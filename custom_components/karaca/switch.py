"""Platform for Karaca Connect switch integration."""
import asyncio
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import KaracaAPIError
from .const import DOMAIN, LOGGER, CONF_NAME_PREFIX, DEFAULT_NAME
from .sensor import KaracaBaseEntity

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Karaca switches from a config entry."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = data["coordinator"]
    client = data["client"]
    name_prefix = config_entry.data.get(CONF_NAME_PREFIX, DEFAULT_NAME)

    async_add_entities([KaracaPowerSwitch(coordinator, client, config_entry, name_prefix)])


class KaracaPowerSwitch(KaracaBaseEntity, SwitchEntity):
    """Switch entity representing the master power state of the tea maker."""

    _attr_icon = "mdi:power"

    def __init__(self, coordinator, client, entry: ConfigEntry, name_prefix: str):
        """Initialize the power switch entity."""
        super().__init__(coordinator, entry, name_prefix)
        self.client = client
        self._attr_name = f"{self.name_prefix} Güç"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.coordinator.device_udid}_power_switch"

    @property
    def is_on(self) -> bool:
        """Return true if the tea maker is active (not in standby mode)."""
        try:
            detail = self.coordinator.data.get("detail", {})
            mode_id = detail.get("mode", 1)
            mode_state = detail.get("modeState", 0)
            
            # If mode is standby (1), it's considered OFF.
            # If mode is anything else (2, 6, 9, 13) and state is active, it is ON.
            return mode_id != 1
        except Exception:
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the tea maker on (defaults to Boiling Water mode)."""
        LOGGER.info("Turning ON Karaca tea maker (defaulting to Boiling Water mode)...")
        try:
            # Mode 6 = Boiling Water
            path = f"/api/v1/devices/{self.coordinator.device_id}/modes/6"
            await self.client.async_request("PUT", path, json_data={"active": True})
            
            # Clear previous error on success
            self.coordinator.last_error = None
            
            # Force immediate update
            await self.coordinator.async_request_refresh()
        except KaracaAPIError as err:
            LOGGER.warning("Karaca API warning: %s", err)
            self.coordinator.last_error = str(err)
            self.coordinator.async_set_updated_data(self.coordinator.data)
            
            async def clear_error():
                await asyncio.sleep(15)
                if self.coordinator.last_error == str(err):
                    self.coordinator.last_error = None
                    self.coordinator.async_set_updated_data(self.coordinator.data)
            
            self.coordinator.hass.async_create_task(clear_error())
        except Exception as err:
            LOGGER.error("Failed to turn on tea maker: %s", err)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the tea maker off (returns to StandBy mode)."""
        LOGGER.info("Turning OFF Karaca tea maker (switching to StandBy mode)...")
        try:
            # Mode 1 = StandBy
            path = f"/api/v1/devices/{self.coordinator.device_id}/modes/1"
            await self.client.async_request("PUT", path, json_data={"active": True})
            
            # Clear previous error on success
            self.coordinator.last_error = None
            
            # Force immediate update
            await self.coordinator.async_request_refresh()
        except KaracaAPIError as err:
            LOGGER.warning("Karaca API warning: %s", err)
            self.coordinator.last_error = str(err)
            self.coordinator.async_set_updated_data(self.coordinator.data)
            
            async def clear_error():
                await asyncio.sleep(15)
                if self.coordinator.last_error == str(err):
                    self.coordinator.last_error = None
                    self.coordinator.async_set_updated_data(self.coordinator.data)
            
            self.coordinator.hass.async_create_task(clear_error())
        except Exception as err:
            LOGGER.error("Failed to turn off tea maker: %s", err)
