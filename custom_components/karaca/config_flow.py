"""Config flow for Karaca Connect integration."""
import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .const import (
    BASE_URL,
    CONF_DEVICE_ID,
    CONF_DEVICE_LABEL,
    CONF_DEVICE_TYPE,
    CONF_DEVICE_UDID,
    CONF_ERROR_CLEAR_SECONDS,
    CONF_NAME_PREFIX,
    CONF_REFRESH_TOKEN,
    CONF_SCAN_INTERVAL,
    DEFAULT_ERROR_CLEAR_SECONDS,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LOGGER,
)


def _is_supported_device(device: dict) -> bool:
    """Return if the device looks like a supported Karaca tea maker."""
    device_type = device.get("type", "")
    return device_type == "robotea4in1" or "robotea" in device_type


def _device_title(device: dict) -> str:
    """Return a readable device title."""
    product = device.get("product") or {}
    label = device.get("label") or product.get("name") or "Karaca cihaz"
    return f"{label} ({device.get('id')})"


async def _async_login_and_get_devices(
    hass: HomeAssistant,
    email: str,
    password: str,
) -> tuple[str, list[dict]]:
    """Login to Karaca Connect and return refresh token plus devices."""
    session = async_get_clientsession(hass)
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "ios 26.4.2; version 1.9.13",
    }

    login_url = f"{BASE_URL}/api/auth/signin"
    payload = {"email": email, "password": password}

    async with session.post(login_url, headers=headers, json=payload, timeout=10) as response:
        if response.status != 200:
            raise ValueError("invalid_auth")

        res_json = await response.json()
        if not res_json.get("succeeded") or "data" not in res_json:
            raise ValueError("invalid_auth")

        data = res_json["data"]
        jw_token = data.get("jwToken")
        refresh_token = data.get("refreshToken")

    if not jw_token or not refresh_token:
        raise ValueError("invalid_auth")

    devices_url = f"{BASE_URL}/api/v1/devices/me"
    device_headers = {**headers, "Authorization": f"Bearer {jw_token}"}

    async with session.get(devices_url, headers=device_headers, timeout=10) as response:
        if response.status != 200:
            raise ValueError("cannot_connect")

        devices_json = await response.json()
        devices = devices_json.get("data", [])

    return refresh_token, [device for device in devices if _is_supported_device(device)]


class KaracaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Karaca Connect."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize flow data."""
        self._email = None
        self._password = None
        self._refresh_token = None
        self._name_prefix = DEFAULT_NAME
        self._devices = []
        self._reauth_entry = None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return options flow handler."""
        return KaracaOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            self._email = user_input[CONF_EMAIL]
            self._password = user_input[CONF_PASSWORD]
            self._name_prefix = user_input.get(CONF_NAME_PREFIX, DEFAULT_NAME)

            try:
                self._refresh_token, self._devices = await _async_login_and_get_devices(
                    self.hass,
                    self._email,
                    self._password,
                )
            except ValueError as err:
                errors["base"] = str(err)
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except Exception as err:  # pylint: disable=broad-except
                LOGGER.exception("Unexpected exception in config flow: %s", err)
                errors["base"] = "unknown"
            else:
                if not self._devices:
                    errors["base"] = "no_devices"
                elif len(self._devices) == 1:
                    return await self._async_create_entry_for_device(self._devices[0])
                else:
                    return await self.async_step_device()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL): cv.string,
                    vol.Required(CONF_PASSWORD): cv.string,
                    vol.Optional(CONF_NAME_PREFIX, default=DEFAULT_NAME): cv.string,
                }
            ),
            errors=errors,
        )

    async def async_step_device(self, user_input=None):
        """Let user select the Karaca device to add."""
        errors = {}
        device_options = {str(device["id"]): _device_title(device) for device in self._devices}

        if user_input is not None:
            selected_id = user_input[CONF_DEVICE_ID]
            selected = next(
                (device for device in self._devices if str(device.get("id")) == selected_id),
                None,
            )
            if selected is None:
                errors["base"] = "unknown"
            else:
                return await self._async_create_entry_for_device(selected)

        return self.async_show_form(
            step_id="device",
            data_schema=vol.Schema({vol.Required(CONF_DEVICE_ID): vol.In(device_options)}),
            errors=errors,
        )

    async def async_step_reauth(self, entry_data):
        """Handle reauthentication request."""
        self._reauth_entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        self._email = entry_data.get(CONF_EMAIL)
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        """Ask for credentials again when token/login fails."""
        errors = {}

        if user_input is not None:
            email = user_input.get(CONF_EMAIL, self._email)
            password = user_input[CONF_PASSWORD]

            try:
                refresh_token, _devices = await _async_login_and_get_devices(
                    self.hass,
                    email,
                    password,
                )
            except ValueError as err:
                errors["base"] = str(err)
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            else:
                data = dict(self._reauth_entry.data)
                data[CONF_EMAIL] = email
                data[CONF_PASSWORD] = password
                data[CONF_REFRESH_TOKEN] = refresh_token
                self.hass.config_entries.async_update_entry(self._reauth_entry, data=data)
                await self.hass.config_entries.async_reload(self._reauth_entry.entry_id)
                return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL, default=self._email or ""): cv.string,
                    vol.Required(CONF_PASSWORD): cv.string,
                }
            ),
            errors=errors,
        )

    async def _async_create_entry_for_device(self, device: dict):
        """Create config entry for one selected Karaca device."""
        device_udid = device.get("udid") or str(device["id"])
        await self.async_set_unique_id(f"{self._email.lower()}_{device_udid}")
        self._abort_if_unique_id_configured()

        device_label = device.get("label") or _device_title(device)
        return self.async_create_entry(
            title=f"{self._name_prefix} - {device_label}",
            data={
                CONF_EMAIL: self._email,
                CONF_PASSWORD: self._password,
                CONF_REFRESH_TOKEN: self._refresh_token,
                CONF_NAME_PREFIX: self._name_prefix,
                CONF_DEVICE_ID: str(device["id"]),
                CONF_DEVICE_UDID: device_udid,
                CONF_DEVICE_TYPE: device.get("type"),
                CONF_DEVICE_LABEL: device_label,
            },
        )


class KaracaOptionsFlow(config_entries.OptionsFlow):
    """Handle Karaca Connect options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage Karaca Connect options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self._config_entry.options
        data = self._config_entry.data

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_NAME_PREFIX,
                        default=options.get(CONF_NAME_PREFIX, data.get(CONF_NAME_PREFIX, DEFAULT_NAME)),
                    ): cv.string,
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                    ): vol.All(vol.Coerce(int), vol.Range(min=15, max=3600)),
                    vol.Optional(
                        CONF_ERROR_CLEAR_SECONDS,
                        default=options.get(
                            CONF_ERROR_CLEAR_SECONDS,
                            DEFAULT_ERROR_CLEAR_SECONDS,
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=3, max=300)),
                }
            ),
        )
