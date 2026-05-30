"""Platform for Karaca Connect select integration."""
from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import KaracaAPIError
from .const import (
    CONF_NAME_PREFIX,
    DEFAULT_NAME,
    DOMAIN,
    LOGGER,
    MODE_LABELS,
    normalize_mode_id,
)
from .sensor import KaracaBaseEntity

# Reverse mapping for setting modes
FRIENDLY_TO_MODE_ID = {v: k for k, v in MODE_LABELS.items()}

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Karaca selects from a config entry."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = data["coordinator"]
    client = data["client"]
    name_prefix = config_entry.options.get(
        CONF_NAME_PREFIX,
        config_entry.data.get(CONF_NAME_PREFIX, DEFAULT_NAME),
    )

    async_add_entities([KaracaModeSelect(coordinator, client, config_entry, name_prefix)])


class KaracaModeSelect(KaracaBaseEntity, SelectEntity):
    """Select entity to control the tea maker cooking modes."""

    _attr_icon = "mdi:coffee-maker"

    def __init__(self, coordinator, client, entry: ConfigEntry, name_prefix: str):
        """Initialize the mode select entity."""
        super().__init__(coordinator, entry, name_prefix)
        self.client = client
        self._attr_name = f"{self.name_prefix} Mod Seçimi"
        self._attr_options = list(MODE_LABELS.values())

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.coordinator.device_udid}_mode_select"

    @property
    def current_option(self) -> str:
        """Return the currently selected option."""
        try:
            detail = self.coordinator.data.get("detail", {})
            mode_id = normalize_mode_id(detail.get("mode"))
            return MODE_LABELS.get(mode_id, "Beklemede (Kapalı)")
        except Exception:
            return "Beklemede (Kapalı)"

    async def async_select_option(self, option: str) -> None:
        """Change the active cooking mode."""
        mode_id = FRIENDLY_TO_MODE_ID.get(option)
        if mode_id is None:
            LOGGER.error("Invalid option selected: %s", option)
            return

        LOGGER.info("Setting Karaca mode to: %s (ID=%s)", option, mode_id)

        if not self.client.command_allowed():
            LOGGER.debug("Karaca select command skipped because cooldown is active.")
            await self.async_refresh_after_command()
            return

        try:
            await self.client.async_set_mode(self.coordinator.device_id, mode_id)
            self.coordinator.last_error = None
            await self.async_refresh_after_command()
        except KaracaAPIError as err:
            LOGGER.warning("Karaca API warning: %s", err)
            self.set_temporary_error(str(err))
        except Exception as err:
            LOGGER.error("Failed to set mode: %s", err)
