"""The Karaca Connect integration."""
import asyncio
from datetime import timedelta
import time
import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    LOGGER,
    BASE_URL,
    CONF_DEVICE_ID,
    CONF_DEVICE_LABEL,
    CONF_DEVICE_TYPE,
    CONF_DEVICE_UDID,
    CONF_ERROR_CLEAR_SECONDS,
    CONF_REFRESH_TOKEN,
    CONF_SCAN_INTERVAL,
    DEFAULT_ERROR_CLEAR_SECONDS,
    DEFAULT_SCAN_INTERVAL,
)

class KaracaAPIError(Exception):
    """Exception raised when Karaca API returns a business validation error."""

PLATFORMS = [Platform.SENSOR, Platform.SWITCH]
_INTERNAL_UPDATE_SKIP = "_internal_update_skip"


def _mark_entry_internal_update(hass: HomeAssistant, entry_id: str) -> None:
    """Mark a config entry update that should not trigger an integration reload."""
    skips = hass.data.setdefault(DOMAIN, {}).setdefault(_INTERNAL_UPDATE_SKIP, {})
    skips[entry_id] = skips.get(entry_id, 0) + 1


def _consume_entry_internal_update(hass: HomeAssistant, entry_id: str) -> bool:
    """Return True when a config entry update was made internally by this integration."""
    skips = hass.data.get(DOMAIN, {}).get(_INTERNAL_UPDATE_SKIP, {})
    count = skips.get(entry_id, 0)
    if count <= 0:
        return False

    if count == 1:
        skips.pop(entry_id, None)
    else:
        skips[entry_id] = count - 1
    return True


def _clear_entry_internal_update(hass: HomeAssistant, entry_id: str) -> None:
    """Clear any setup-time internal update markers before attaching listeners."""
    skips = hass.data.get(DOMAIN, {}).get(_INTERNAL_UPDATE_SKIP, {})
    skips.pop(entry_id, None)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Karaca Connect from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Create the API Client
    client = KaracaAPIClient(
        hass,
        entry,
        entry.data[CONF_EMAIL],
        entry.data[CONF_PASSWORD],
        entry.data.get(CONF_REFRESH_TOKEN),
    )

    # Initialize the coordinator
    coordinator = KaracaDataUpdateCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _clear_entry_internal_update(hass, entry.entry_id)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload Karaca Connect when options change."""
    if _consume_entry_internal_update(hass, entry.entry_id):
        LOGGER.debug("Skipping Karaca reload after internal config entry data update.")
        return

    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class KaracaAPIClient:
    """API client wrapper for Karaca Connect REST API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, email: str, password: str, refresh_token: str):
        """Initialize the client."""
        self.hass = hass
        self.entry = entry
        self.email = email
        self.password = password
        self.refresh_token = refresh_token
        self.jw_token = None
        self._lock = asyncio.Lock()
        self._last_command_at = 0.0
        self.session = async_get_clientsession(hass)

    def command_allowed(self, cooldown_seconds: float = 3.0) -> bool:
        """Return if a cloud command may be sent without hitting cooldown."""
        now = time.monotonic()
        if now - self._last_command_at < cooldown_seconds:
            return False
        self._last_command_at = now
        return True

    async def async_request(self, method: str, path: str, json_data=None) -> dict:
        """Perform an authorized API request, automatically refreshing tokens if needed."""
        if not self.jw_token:
            await self.async_ensure_token()

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "ios 26.4.2; version 1.9.13",
            "Authorization": f"Bearer {self.jw_token}",
        }

        url = f"{BASE_URL}{path}"
        try:
            async with self.session.request(method, url, headers=headers, json=json_data, timeout=15) as response:
                if response.status == 401:
                    LOGGER.warning("JWT Token expired (401), attempting to refresh token...")
                    await self.async_ensure_token(force_refresh=True)
                    headers["Authorization"] = f"Bearer {self.jw_token}"

                    async with self.session.request(method, url, headers=headers, json=json_data, timeout=15) as retry_response:
                        if retry_response.status in (401, 403):
                            raise ConfigEntryAuthFailed("Karaca Connect credentials are no longer valid.")
                        if retry_response.status != 200:
                            try:
                                res_json = await retry_response.json()
                                if isinstance(res_json, dict) and not res_json.get("succeeded", True):
                                    messages = res_json.get("messages", [])
                                    err_msg = messages[0] if messages else f"status {retry_response.status}"
                                    raise KaracaAPIError(err_msg)
                            except KaracaAPIError:
                                raise
                            except Exception:
                                pass
                            raise UpdateFailed(
                                f"API request failed after token refresh: status {retry_response.status}"
                            )

                        res_json = await retry_response.json()
                        if isinstance(res_json, dict) and not res_json.get("succeeded", True):
                            messages = res_json.get("messages", [])
                            err_msg = messages[0] if messages else "Bilinmeyen bir hata oluştu."
                            raise KaracaAPIError(err_msg)
                        return res_json

                if response.status in (401, 403):
                    raise ConfigEntryAuthFailed("Karaca Connect credentials are no longer valid.")

                if response.status != 200:
                    try:
                        res_json = await response.json()
                        if isinstance(res_json, dict) and not res_json.get("succeeded", True):
                            messages = res_json.get("messages", [])
                            err_msg = messages[0] if messages else f"returned status {response.status}"
                            raise KaracaAPIError(err_msg)
                    except KaracaAPIError:
                        raise
                    except Exception:
                        pass
                    raise UpdateFailed(f"API request failed: {method} {path} returned status {response.status}")

                res_json = await response.json()
                if isinstance(res_json, dict) and not res_json.get("succeeded", True):
                    messages = res_json.get("messages", [])
                    err_msg = messages[0] if messages else "Bilinmeyen bir hata oluştu."
                    raise KaracaAPIError(err_msg)
                return res_json
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Communication error with Karaca API: {err}")

    async def async_set_mode(self, device_id: str, mode_id: int, active: bool = True) -> dict:
        """Activate a Karaca device mode."""
        return await self.async_request(
            "PUT",
            f"/api/v1/devices/{device_id}/modes/{mode_id}",
            json_data={"active": active},
        )

    async def async_get_settings(self, device_id: str) -> list[dict]:
        """Return device notification and voice settings."""
        data = await self.async_request("GET", f"/api/v1/devices/{device_id}/settings")
        settings_data = data.get("data", {})
        if isinstance(settings_data, dict):
            return settings_data.get("notifications", [])
        return []

    async def async_set_setting(self, device_id: str, setting_id: int, value: bool) -> dict:
        """Update a Karaca device setting."""
        path = f"/api/v1/devices/{device_id}/settings/{setting_id}"
        try:
            return await self.async_request("PUT", path, json_data={"value": value})
        except KaracaAPIError:
            return await self.async_request("PUT", path, json_data={"active": value})

    async def async_ensure_token(self, force_refresh=False):
        """Ensure we have a valid JWT token, refreshing it if expired or forced."""
        async with self._lock:
            if self.jw_token and not force_refresh:
                return

            if self.refresh_token and not force_refresh:
                try:
                    LOGGER.debug("Attempting to refresh JWT token via refresh token...")
                    refresh_url = f"{BASE_URL}/api/auth/refresh-token"
                    payload = {"refreshToken": self.refresh_token}

                    async with self.session.post(refresh_url, json=payload, timeout=10) as response:
                        if response.status == 200:
                            res_json = await response.json()
                            if res_json.get("succeeded") and "data" in res_json:
                                data = res_json["data"]
                                self.jw_token = data["jwToken"]
                                new_refresh = data["refreshToken"]

                                self.refresh_token = new_refresh
                                new_data = dict(self.entry.data)
                                new_data[CONF_REFRESH_TOKEN] = new_refresh
                                _mark_entry_internal_update(self.hass, self.entry.entry_id)
                                self.hass.config_entries.async_update_entry(self.entry, data=new_data)
                                LOGGER.debug("JWT Token successfully refreshed.")
                                return
                except Exception as err:  # pylint: disable=broad-except
                    LOGGER.warning("Refresh token flow failed: %s, falling back to full signin.", err)

            LOGGER.info("Performing full password-based login to Karaca API...")
            login_url = f"{BASE_URL}/api/auth/signin"
            payload = {"email": self.email, "password": self.password}

            try:
                async with self.session.post(login_url, json=payload, timeout=10) as response:
                    if response.status in (401, 403):
                        raise ConfigEntryAuthFailed("Karaca Connect credentials are no longer valid.")
                    if response.status != 200:
                        raise UpdateFailed(f"Login failed: status code {response.status}")

                    res_json = await response.json()
                    if not res_json.get("succeeded") or "data" not in res_json:
                        raise ConfigEntryAuthFailed("Karaca Connect credentials are no longer valid.")

                    data = res_json["data"]
                    self.jw_token = data["jwToken"]
                    new_refresh = data["refreshToken"]

                    self.refresh_token = new_refresh
                    new_data = dict(self.entry.data)
                    new_data[CONF_REFRESH_TOKEN] = new_refresh
                    _mark_entry_internal_update(self.hass, self.entry.entry_id)
                    self.hass.config_entries.async_update_entry(self.entry, data=new_data)
                    LOGGER.info("Successfully signed in and retrieved new session tokens.")
            except ConfigEntryAuthFailed:
                raise
            except Exception as err:
                raise UpdateFailed(f"Failed to authenticate with Karaca Connect: {err}")


class KaracaDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Karaca Connect device telemetry."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client: KaracaAPIClient):
        """Initialize the coordinator."""
        self.entry = entry
        self.client = client
        self.device_id = entry.data.get(CONF_DEVICE_ID)
        self.device_type = entry.data.get(CONF_DEVICE_TYPE)
        self.device_name = entry.data.get(CONF_DEVICE_LABEL)
        self.device_udid = entry.data.get(CONF_DEVICE_UDID)
        self.last_error = None
        self.error_clear_seconds = entry.options.get(
            CONF_ERROR_CLEAR_SECONDS,
            DEFAULT_ERROR_CLEAR_SECONDS,
        )
        scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self):
        """Fetch data from Karaca Connect API."""
        try:
            # Discovery device ID if not already discovered
            if not self.device_id:
                devices_data = await self.client.async_request("GET", "/api/v1/devices/me")
                devices = devices_data.get("data", [])
                
                if not devices:
                    raise UpdateFailed("No Karaca smart devices found linked to this account.")
                
                # We prioritize Çaysever Robotea, or take the first device
                tea_maker = None
                for d in devices:
                    if d.get("type") == "robotea4in1" or "robotea" in d.get("type", ""):
                        tea_maker = d
                        break
                
                if not tea_maker:
                    tea_maker = devices[0]

                self.device_id = str(tea_maker["id"])
                self.device_type = tea_maker.get("type")
                self.device_name = tea_maker.get("label") or "Karaca cihaz"
                self.device_udid = tea_maker.get("udid") or self.device_id
                new_data = dict(self.entry.data)
                new_data.update(
                    {
                        CONF_DEVICE_ID: str(self.device_id),
                        CONF_DEVICE_TYPE: self.device_type,
                        CONF_DEVICE_LABEL: self.device_name,
                        CONF_DEVICE_UDID: self.device_udid,
                    }
                )
                _mark_entry_internal_update(self.client.hass, self.entry.entry_id)
                self.client.hass.config_entries.async_update_entry(
                    self.entry,
                    data=new_data,
                )
                LOGGER.info("Discovered Karaca device: ID=%s, Name=%s", self.device_id, self.device_name)

            # Fetch detailed state
            state_data = await self.client.async_request("GET", f"/api/v1/devices/{self.device_id}")
            device_state = state_data.get("data", {})
            
            if not device_state or "detail" not in device_state:
                raise UpdateFailed("Failed to fetch detailed device telemetry.")

            return device_state
        except ConfigEntryAuthFailed:
            raise
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}")
