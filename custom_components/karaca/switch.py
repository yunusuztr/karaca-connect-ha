"""Platform for Karaca Connect switch integration."""
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import KaracaAPIError
from .const import (
    CONF_NAME_PREFIX,
    DEFAULT_NAME,
    DOMAIN,
    LOGGER,
    MODE_BABY_FOOD,
    MODE_BOILING_WATER,
    MODE_FILTER_COFFEE,
    MODE_ICONS,
    MODE_LABELS,
    MODE_STANDBY,
    MODE_TEA_BREWING,
    SETTING_CLEANING,
    SETTING_FILTER_COFFEE_NOTIFICATION,
    SETTING_FRESHNESS,
    SETTING_NO_WATER,
    SETTING_POWER_OFF,
    SETTING_REMINDERS,
    SETTING_TEA_NOTIFICATION,
    SETTING_VOICE,
    normalize_mode_id,
)
from .sensor import KaracaBaseEntity

MODE_SWITCHES = [
    (MODE_BOILING_WATER, "Su Kaynatma"),
    (MODE_TEA_BREWING, "Çay Demleme"),
    (MODE_FILTER_COFFEE, "Filtre Kahve"),
    (MODE_BABY_FOOD, "Mama Suyu"),
]

SETTING_SWITCHES = [
    (SETTING_TEA_NOTIFICATION, "Çay Demleme Bildirimi", "mdi:bell-ring"),
    (SETTING_FILTER_COFFEE_NOTIFICATION, "Filtre Kahve Bildirimi", "mdi:bell-ring"),
    (SETTING_FRESHNESS, "Tazelik Bildirimi", "mdi:timer-sand"),
    (SETTING_POWER_OFF, "Kapanma Bildirimi", "mdi:power"),
    (SETTING_NO_WATER, "Su Kalmadı Bildirimi", "mdi:water-alert"),
    (SETTING_REMINDERS, "Anımsatıcı Bildirimler", "mdi:bell-cog"),
    (SETTING_VOICE, "Konuşma Sesi", "mdi:volume-high"),
    (SETTING_CLEANING, "Temizlik Bildirimi", "mdi:spray-bottle"),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Karaca switches from a config entry."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = data["coordinator"]
    client = data["client"]
    name_prefix = config_entry.options.get(
        CONF_NAME_PREFIX,
        config_entry.data.get(CONF_NAME_PREFIX, DEFAULT_NAME),
    )

    entities = [KaracaPowerSwitch(coordinator, client, config_entry, name_prefix)]
    entities.extend(
        KaracaModeSwitch(coordinator, client, config_entry, name_prefix, mode_id, name)
        for mode_id, name in MODE_SWITCHES
    )

    try:
        settings = await client.async_get_settings(coordinator.device_id)
    except Exception as err:  # pylint: disable=broad-except
        LOGGER.warning("Karaca settings could not be loaded: %s", err)
        settings = []

    entities.extend(
        KaracaSettingSwitch(
            coordinator,
            client,
            config_entry,
            name_prefix,
            setting_id,
            name,
            icon,
            settings,
        )
        for setting_id, name, icon in SETTING_SWITCHES
    )

    async_add_entities(entities)


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
        """Return true if the tea maker is active."""
        try:
            detail = self.coordinator.data.get("detail", {})
            return normalize_mode_id(detail.get("mode")) != MODE_STANDBY
        except Exception:  # pylint: disable=broad-except
            return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the tea maker on in boiling water mode."""
        LOGGER.info("Turning on Karaca tea maker in boiling water mode.")
        await self._async_set_mode(MODE_BOILING_WATER)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the tea maker off by returning it to standby."""
        LOGGER.info("Turning off Karaca tea maker.")
        await self._async_set_mode(MODE_STANDBY)

    async def _async_set_mode(self, mode_id: int) -> None:
        """Send a mode command with error handling."""
        if not self.client.command_allowed():
            LOGGER.debug("Karaca command skipped because cooldown is active.")
            await self.async_refresh_after_command()
            return

        try:
            await self.client.async_set_mode(self.coordinator.device_id, mode_id)
            self.coordinator.last_error = None
            await self.async_refresh_after_command()
        except KaracaAPIError as err:
            LOGGER.warning("Karaca API warning: %s", err)
            self.set_temporary_error(str(err))
        except Exception as err:  # pylint: disable=broad-except
            LOGGER.error("Failed to set Karaca power state: %s", err)


class KaracaModeSwitch(KaracaBaseEntity, SwitchEntity):
    """Switch entity for one Karaca cooking mode."""

    def __init__(
        self,
        coordinator,
        client,
        entry: ConfigEntry,
        name_prefix: str,
        mode_id: int,
        mode_name: str,
    ):
        """Initialize a mode switch."""
        super().__init__(coordinator, entry, name_prefix)
        self.client = client
        self.mode_id = mode_id
        self.mode_name = mode_name
        self._attr_name = f"{self.name_prefix} {mode_name}"
        self._attr_icon = MODE_ICONS.get(mode_id, "mdi:kettle")

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.coordinator.device_udid}_mode_{self.mode_id}_switch"

    @property
    def is_on(self) -> bool:
        """Return if this mode is currently active."""
        try:
            detail = self.coordinator.data.get("detail", {})
            return normalize_mode_id(detail.get("mode")) == self.mode_id
        except Exception:  # pylint: disable=broad-except
            return False

    @property
    def extra_state_attributes(self) -> dict:
        """Return mode metadata."""
        detail = self.coordinator.data.get("detail", {}) if self.coordinator.data else {}
        return {
            "mode_id": self.mode_id,
            "mode_name": MODE_LABELS.get(self.mode_id, self.mode_name),
            "current_mode": detail.get("mode"),
            "current_mode_name": detail.get("modeName"),
            "current_state": detail.get("modeStateLabel"),
            "off_sends_standby_only_if_this_mode_is_active": True,
        }

    async def async_turn_on(self, **kwargs) -> None:
        """Activate this mode."""
        if self.is_on:
            await self.async_refresh_after_command()
            return
        await self._async_set_mode(self.mode_id)

    async def async_turn_off(self, **kwargs) -> None:
        """Return to standby only if this exact mode is active."""
        if not self.is_on:
            await self.async_refresh_after_command()
            return
        await self._async_set_mode(MODE_STANDBY)

    async def _async_set_mode(self, mode_id: int) -> None:
        """Send a mode command with cooldown and error handling."""
        if not self.client.command_allowed():
            LOGGER.debug("Karaca mode command skipped because cooldown is active.")
            await self.async_refresh_after_command()
            return

        try:
            await self.client.async_set_mode(self.coordinator.device_id, mode_id)
            self.coordinator.last_error = None
            await self.async_refresh_after_command()
        except KaracaAPIError as err:
            LOGGER.warning("Karaca API warning: %s", err)
            self.set_temporary_error(str(err))
        except Exception as err:  # pylint: disable=broad-except
            LOGGER.error("Failed to set Karaca mode %s: %s", self.mode_name, err)


class KaracaSettingSwitch(KaracaBaseEntity, SwitchEntity):
    """Switch entity for Karaca notification and voice settings."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator,
        client,
        entry: ConfigEntry,
        name_prefix: str,
        setting_id: int,
        setting_name: str,
        icon: str,
        initial_settings: list[dict],
    ):
        """Initialize a device setting switch."""
        super().__init__(coordinator, entry, name_prefix)
        self.client = client
        self.setting_id = setting_id
        self._settings = initial_settings
        self._attr_name = f"{self.name_prefix} {setting_name}"
        self._attr_icon = icon

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.coordinator.device_udid}_setting_{self.setting_id}"

    @property
    def is_on(self):
        """Return if this Karaca setting is enabled."""
        for item in self._settings:
            if item.get("id") == self.setting_id:
                return bool(item.get("value"))
        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return setting metadata."""
        return {"setting_id": self.setting_id}

    async def async_turn_on(self, **kwargs) -> None:
        """Enable this setting."""
        await self._async_set_setting(True)

    async def async_turn_off(self, **kwargs) -> None:
        """Disable this setting."""
        await self._async_set_setting(False)

    async def async_update(self) -> None:
        """Refresh setting values."""
        self._settings = await self.client.async_get_settings(self.coordinator.device_id)

    async def _async_set_setting(self, value: bool) -> None:
        """Update this setting through Karaca API."""
        try:
            await self.client.async_set_setting(self.coordinator.device_id, self.setting_id, value)
            self._settings = await self.client.async_get_settings(self.coordinator.device_id)
            self.async_write_ha_state()
        except Exception as err:  # pylint: disable=broad-except
            LOGGER.warning("Failed to set Karaca setting %s: %s", self.setting_id, err)
