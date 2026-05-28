"""Platform for Karaca Connect sensor integration."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, LOGGER, CONF_NAME_PREFIX, DEFAULT_NAME, MODES, MODE_LABELS

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Karaca sensors from a config entry."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = data["coordinator"]
    name_prefix = config_entry.data.get(CONF_NAME_PREFIX, DEFAULT_NAME)

    sensors = [
        KaracaStatusSensor(coordinator, config_entry, name_prefix),
        KaracaModeSensor(coordinator, config_entry, name_prefix),
    ]
    async_add_entities(sensors)


class KaracaBaseEntity(CoordinatorEntity):
    """Base class for all Karaca entities."""

    def __init__(self, coordinator, entry: ConfigEntry, name_prefix: str):
        """Initialize the base entity."""
        super().__init__(coordinator)
        self.entry = entry
        self.name_prefix = name_prefix
        
        # Device Registry linking
        self._attr_device_info = {
            "identifiers": {(DOMAIN, str(coordinator.device_udid))},
            "name": f"Karaca {self.name_prefix}",
            "manufacturer": "Karaca",
            "model": "Çaysever Robotea Pro",
            "sw_version": coordinator.device_type,
        }

    @property
    def unique_id(self) -> str:
        """Return a unique ID for this entity."""
        raise NotImplementedError


class KaracaStatusSensor(KaracaBaseEntity, SensorEntity):
    """Sensor that shows the human-readable status of the tea maker."""

    _attr_icon = "mdi:kettle"

    def __init__(self, coordinator, entry: ConfigEntry, name_prefix: str):
        """Initialize the status sensor."""
        super().__init__(coordinator, entry, name_prefix)
        self._attr_name = f"{self.name_prefix} Durumu"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.coordinator.device_udid}_status"

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        if self.coordinator.last_error:
            return f"Hata: {self.coordinator.last_error}"

        try:
            # Parse localized status label e.g., "Su Kaynatılıyor", "Su Hazır", "Kapalı"
            detail = self.coordinator.data.get("detail", {})
            step_view = detail.get("stepView", {})
            label = step_view.get("label")
            if label:
                return label
            
            # Fallback
            mode_state_label = detail.get("modeStateLabel", "off")
            return mode_state_label
        except Exception:
            return "Kapalı"

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes."""
        try:
            detail = self.coordinator.data.get("detail", {})
            meta = self.coordinator.data.get("meta", {})
            return {
                "countdown": detail.get("stepView", {}).get("countdown"),
                "freshness": detail.get("freshness"),
                "connected": meta.get("connected", True),
                "last_updated": detail.get("updatedDate"),
                "state_code": detail.get("state"),
                "mode_state_code": detail.get("modeState"),
                "last_error": self.coordinator.last_error,
            }
        except Exception:
            return {}


class KaracaModeSensor(KaracaBaseEntity, SensorEntity):
    """Sensor that shows the active mode of the tea maker."""

    _attr_icon = "mdi:tune"

    def __init__(self, coordinator, entry: ConfigEntry, name_prefix: str):
        """Initialize the active mode sensor."""
        super().__init__(coordinator, entry, name_prefix)
        self._attr_name = f"{self.name_prefix} Aktif Mod"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.coordinator.device_udid}_mode"

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        try:
            detail = self.coordinator.data.get("detail", {})
            mode_id = detail.get("mode", 1)
            # Map mode ID to friendly label (e.g. 6 -> "Su Kaynatma")
            return MODE_LABELS.get(mode_id, f"Bilinmeyen Mod ({mode_id})")
        except Exception:
            return "Beklemede (Kapalı)"
