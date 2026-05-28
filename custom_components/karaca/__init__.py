"""The Karaca Connect integration."""
import asyncio
from datetime import timedelta
import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER, BASE_URL, CONF_NAME_PREFIX, DEFAULT_SCAN_INTERVAL

PLATFORMS = [Platform.SENSOR, Platform.SELECT, Platform.SWITCH]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Karaca Connect from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Create the API Client
    client = KaracaAPIClient(
        hass,
        entry,
        entry.data[CONF_EMAIL],
        entry.data[CONF_PASSWORD],
        entry.data.get("refresh_token"),
    )

    # Initialize the coordinator
    coordinator = KaracaDataUpdateCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

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

    async def async_request(self, method: str, path: str, json_data=None) -> dict:
        """Perform an authorized API request, automatically refreshing tokens if needed."""
        # Ensure we have a valid token
        if not self.jw_token:
            await self.async_ensure_token()

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "ios 26.4.2; version 1.9.13",
            "Authorization": f"Bearer {self.jw_token}",
        }

        async with aiohttp.ClientSession() as session:
            url = f"{BASE_URL}{path}"
            try:
                async with session.request(method, url, headers=headers, json=json_data, timeout=15) as response:
                    if response.status == 401:
                        # Token might have expired, force refresh and retry once
                        LOGGER.warning("JWT Token expired (401), attempting to refresh token...")
                        await self.async_ensure_token(force_refresh=True)
                        headers["Authorization"] = f"Bearer {self.jw_token}"
                        
                        async with session.request(method, url, headers=headers, json=json_data, timeout=15) as retry_response:
                            if retry_response.status != 200:
                                try:
                                    res_json = await retry_response.json()
                                    if isinstance(res_json, dict) and not res_json.get("succeeded", True):
                                        messages = res_json.get("messages", [])
                                        err_msg = messages[0] if messages else f"status {retry_response.status}"
                                        raise HomeAssistantError(f"Karaca Hatası: {err_msg}")
                                except HomeAssistantError:
                                    raise
                                except Exception:
                                    pass
                                raise UpdateFailed(f"API request failed after token refresh: status {retry_response.status}")
                            
                            res_json = await retry_response.json()
                            if isinstance(res_json, dict) and not res_json.get("succeeded", True):
                                messages = res_json.get("messages", [])
                                err_msg = messages[0] if messages else "Bilinmeyen bir hata oluştu."
                                raise HomeAssistantError(f"Karaca Hatası: {err_msg}")
                            return res_json
                    
                    if response.status != 200:
                        try:
                            res_json = await response.json()
                            if isinstance(res_json, dict) and not res_json.get("succeeded", True):
                                messages = res_json.get("messages", [])
                                err_msg = messages[0] if messages else f"returned status {response.status}"
                                raise HomeAssistantError(f"Karaca Hatası: {err_msg}")
                        except HomeAssistantError:
                            raise
                        except Exception:
                            pass
                        raise UpdateFailed(f"API request failed: {method} {path} returned status {response.status}")
                    
                    res_json = await response.json()
                    if isinstance(res_json, dict) and not res_json.get("succeeded", True):
                        messages = res_json.get("messages", [])
                        err_msg = messages[0] if messages else "Bilinmeyen bir hata oluştu."
                        raise HomeAssistantError(f"Karaca Hatası: {err_msg}")
                    return res_json
            except aiohttp.ClientError as err:
                raise UpdateFailed(f"Communication error with Karaca API: {err}")

    async def async_ensure_token(self, force_refresh=False):
        """Ensure we have a valid JWT token, refreshing it if expired or forced."""
        async with self._lock:
            if self.jw_token and not force_refresh:
                return

            async with aiohttp.ClientSession() as session:
                # Try refresh token first if we have one and not forced to do a fresh login
                if self.refresh_token and not force_refresh:
                    try:
                        LOGGER.debug("Attempting to refresh JWT token via refresh token...")
                        refresh_url = f"{BASE_URL}/api/auth/refresh-token"
                        payload = {"refreshToken": self.refresh_token}
                        
                        async with session.post(refresh_url, json=payload, timeout=10) as response:
                            if response.status == 200:
                                res_json = await response.json()
                                if res_json.get("succeeded") and "data" in res_json:
                                    data = res_json["data"]
                                    self.jw_token = data["jwToken"]
                                    new_refresh = data["refreshToken"]
                                    
                                    # Save new tokens
                                    self.refresh_token = new_refresh
                                    new_data = dict(self.entry.data)
                                    new_data["refresh_token"] = new_refresh
                                    self.hass.config_entries.async_update_entry(self.entry, data=new_data)
                                    LOGGER.debug("JWT Token successfully refreshed.")
                                    return
                    except Exception as err:  # pylint: disable=broad-except
                        LOGGER.warning("Refresh token flow failed: %s, falling back to full signin.", err)

                # Fallback or Force: Full signin with password
                LOGGER.info("Performing full password-based login to Karaca API...")
                login_url = f"{BASE_URL}/api/auth/signin"
                payload = {"email": self.email, "password": self.password}
                
                try:
                    async with session.post(login_url, json=payload, timeout=10) as response:
                        if response.status != 200:
                            raise UpdateFailed(f"Login failed: status code {response.status}")
                        
                        res_json = await response.json()
                        if not res_json.get("succeeded") or "data" not in res_json:
                            raise UpdateFailed("Login failed: invalid credentials or failed API status.")
                        
                        data = res_json["data"]
                        self.jw_token = data["jwToken"]
                        new_refresh = data["refreshToken"]
                        
                        # Save new tokens
                        self.refresh_token = new_refresh
                        new_data = dict(self.entry.data)
                        new_data["refresh_token"] = new_refresh
                        self.hass.config_entries.async_update_entry(self.entry, data=new_data)
                        LOGGER.info("Successfully signed in and retrieved new session tokens.")
                except Exception as err:
                    raise UpdateFailed(f"Failed to authenticate with Karaca Connect: {err}")


class KaracaDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Karaca Connect device telemetry."""

    def __init__(self, hass: HomeAssistant, client: KaracaAPIClient):
        """Initialize the coordinator."""
        self.client = client
        self.device_id = None
        self.device_type = None
        self.device_name = None
        self.device_udid = None

        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
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

                self.device_id = tea_maker["id"]
                self.device_type = tea_maker["type"]
                self.device_name = tea_maker["label"]
                self.device_udid = tea_maker["udid"]
                LOGGER.info("Discovered Karaca device: ID=%s, Name=%s", self.device_id, self.device_name)

            # Fetch detailed state
            state_data = await self.client.async_request("GET", f"/api/v1/devices/{self.device_id}")
            device_state = state_data.get("data", {})
            
            if not device_state or "detail" not in device_state:
                raise UpdateFailed("Failed to fetch detailed device telemetry.")

            return device_state
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}")
