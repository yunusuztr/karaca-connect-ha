"""Config flow for Karaca Connect integration."""
import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, LOGGER, BASE_URL, CONF_NAME_PREFIX, DEFAULT_NAME

class KaracaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Karaca Connect."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            email = user_input[CONF_EMAIL]
            password = user_input[CONF_PASSWORD]
            name_prefix = user_input.get(CONF_NAME_PREFIX, DEFAULT_NAME)

            # Validate credentials and fetch first refresh token
            try:
                async with aiohttp.ClientSession() as session:
                    # Step 1: Signin
                    login_url = f"{BASE_URL}/api/auth/signin"
                    payload = {"email": email, "password": password}
                    
                    async with session.post(login_url, json=payload, timeout=10) as response:
                        if response.status != 200:
                            errors["base"] = "invalid_auth"
                        else:
                            res_json = await response.json()
                            if not res_json.get("succeeded") or "data" not in res_json:
                                errors["base"] = "invalid_auth"
                            else:
                                data = res_json["data"]
                                jw_token = data.get("jwToken")
                                refresh_token = data.get("refreshToken")
                                
                                # Step 2: Fetch devices to verify ownership
                                devices_url = f"{BASE_URL}/api/v1/devices/me"
                                headers = {"Authorization": f"Bearer {jw_token}"}
                                
                                async with session.get(devices_url, headers=headers, timeout=10) as dev_response:
                                    if dev_response.status == 200:
                                        dev_json = await dev_response.json()
                                        devices = dev_json.get("data", [])
                                        
                                        if not devices:
                                            errors["base"] = "no_devices"
                                        else:
                                            # Successfully authenticated and found devices!
                                            await self.async_set_unique_id(email.lower())
                                            self._abort_if_unique_id_configured()
                                            
                                            return self.async_create_entry(
                                                title=name_prefix,
                                                data={
                                                    CONF_EMAIL: email,
                                                    CONF_PASSWORD: password,
                                                    "refresh_token": refresh_token,
                                                    CONF_NAME_PREFIX: name_prefix,
                                                },
                                            )
                                    else:
                                        errors["base"] = "cannot_connect"
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except Exception as err:  # pylint: disable=broad-except
                LOGGER.exception("Unexpected exception in config flow: %s", err)
                errors["base"] = "unknown"

        # Show input form
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
