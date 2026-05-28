"""Platform for Karaca Connect sensor integration."""
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, LOGGER, CONF_NAME_PREFIX, DEFAULT_NAME, MODE_LABELS

STATUS_OFF = "Kapalı"
STATUS_WATER_BOILING = "Su Kaynatılıyor"
STATUS_WATER_READY = "Su Hazır"
STATUS_TEA_BREWING = "Çay Demleniyor"
STATUS_TEA_READY = "Çay Hazır (Taze)"
STATUS_FILTER_COFFEE_BREWING = "Filtre Kahve Demleniyor"
STATUS_COFFEE_READY = "Kahve Hazır"
STATUS_BABY_WATER_HEATING = "Mama Suyu Isıtılıyor"
STATUS_BABY_WATER_READY = "Mama Suyu Hazır"

STATUS_BY_STEP_ID = {
    "standby_off": STATUS_OFF,
    "boilingwater_waterboiling": STATUS_WATER_BOILING,
    "boilingwater_waterboiled": STATUS_WATER_READY,
    "teabrewing_teabrewing": STATUS_TEA_BREWING,
    "teabrewing_teaready": STATUS_TEA_READY,
    "teabrewing_fresh": STATUS_TEA_READY,
    "filtercoffee_filtercoffeebrewing": STATUS_FILTER_COFFEE_BREWING,
    "filtercoffee_filtercoffeeready": STATUS_COFFEE_READY,
    "filtercoffee_coffeeready": STATUS_COFFEE_READY,
    "babyfood_babyfoodheating": STATUS_BABY_WATER_HEATING,
    "babyfood_babyfoodready": STATUS_BABY_WATER_READY,
}

STATUS_BY_MODE_STATE_LABEL = {
    "off": STATUS_OFF,
    "waterboiling": STATUS_WATER_BOILING,
    "waterboiled": STATUS_WATER_READY,
    "teabrewing": STATUS_TEA_BREWING,
    "teaready": STATUS_TEA_READY,
    "filtercoffeebrewing": STATUS_FILTER_COFFEE_BREWING,
    "coffeebrewing": STATUS_FILTER_COFFEE_BREWING,
    "filtercoffeeready": STATUS_COFFEE_READY,
    "coffeeready": STATUS_COFFEE_READY,
    "babyfoodheating": STATUS_BABY_WATER_HEATING,
    "babyfoodwarming": STATUS_BABY_WATER_HEATING,
    "babyfoodready": STATUS_BABY_WATER_READY,
}

ERROR_STATUS_WATER_EMPTY = "Hata: Su Kalmadı"
ERROR_STATUS_TARGET_TEMPERATURE = "Hata: Hedef Sıcaklık Uygun Değil"
ERROR_STATUS_CLEANING = "Hata: Temizlik Gerekli"
ERROR_STATUS_GENERIC = "Hata: Cihaz Uyarısı"
ERROR_STATUS_OPTIONS = [
    ERROR_STATUS_WATER_EMPTY,
    ERROR_STATUS_TARGET_TEMPERATURE,
    ERROR_STATUS_CLEANING,
    ERROR_STATUS_GENERIC,
]

STATUS_OPTIONS = [
    STATUS_WATER_READY,
    STATUS_WATER_BOILING,
    STATUS_TEA_READY,
    STATUS_TEA_BREWING,
    STATUS_COFFEE_READY,
    STATUS_FILTER_COFFEE_BREWING,
    STATUS_BABY_WATER_READY,
    STATUS_BABY_WATER_HEATING,
    STATUS_OFF,
    *ERROR_STATUS_OPTIONS,
]


def _error_status_from_message(message: str) -> str:
    """Map dynamic Karaca API messages to stable enum states."""
    text = message.casefold()

    if "temizlik" in text or "clean" in text:
        return ERROR_STATUS_CLEANING

    if "su" in text and any(
        keyword in text
        for keyword in ("kalmad", "yok", "eksik", "boş", "bos", "hazne")
    ):
        return ERROR_STATUS_WATER_EMPTY

    if (
        "hedef" in text
        and ("sıcak" in text or "sicak" in text or "temperature" in text)
    ) or "mevcut su sıcak" in text or "mevcut su sicak" in text:
        return ERROR_STATUS_TARGET_TEMPERATURE

    return ERROR_STATUS_GENERIC


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Karaca sensors from a config entry."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = data["coordinator"]
    name_prefix = config_entry.options.get(
        CONF_NAME_PREFIX,
        config_entry.data.get(CONF_NAME_PREFIX, DEFAULT_NAME),
    )

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

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        if not super().available:
            return False

        data = self.coordinator.data or {}
        meta = data.get("meta", {})
        return meta.get("connected", True)


class KaracaStatusSensor(KaracaBaseEntity, SensorEntity):
    """Sensor that shows the human-readable status of the tea maker."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_icon = "mdi:kettle"
    _attr_options = STATUS_OPTIONS

    def __init__(self, coordinator, entry: ConfigEntry, name_prefix: str):
        """Initialize the status sensor."""
        super().__init__(coordinator, entry, name_prefix)
        self._attr_name = f"{self.name_prefix} Durumu"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.coordinator.device_udid}_status"

    @property
    def native_value(self) -> str:
        """Return the native value of the sensor."""
        if self.coordinator.last_error:
            return _error_status_from_message(self.coordinator.last_error)

        try:
            detail = self.coordinator.data.get("detail", {})
            step_view = detail.get("stepView", {})
            freshness = detail.get("freshness") or {}
            countdown = step_view.get("countdown") or {}

            if freshness.get("show") or countdown.get("displayText") == "Kalan Tazelik Süresi":
                return STATUS_TEA_READY

            step_id = step_view.get("id")
            if step_id in STATUS_BY_STEP_ID:
                return STATUS_BY_STEP_ID[step_id]

            mode_state_label = detail.get("modeStateLabel")
            if mode_state_label in STATUS_BY_MODE_STATE_LABEL:
                return STATUS_BY_MODE_STATE_LABEL[mode_state_label]

            label = step_view.get("label")
            if label in self._attr_options:
                return label
            
            # Fallback mappings if any slightly different API responses are received
            if label:
                LOGGER.debug(
                    "Unknown Karaca status step_id=%s, mode_state_label=%s, label=%s",
                    step_id,
                    mode_state_label,
                    label,
                )
                return "Kapalı"
            
            if mode_state_label == "off":
                return "Kapalı"
            return "Kapalı"
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
                "step_id": detail.get("stepView", {}).get("id"),
                "mode_state_label": detail.get("modeStateLabel"),
                "last_error": self.coordinator.last_error,
            }
        except Exception:
            return {}


class KaracaModeSensor(KaracaBaseEntity, SensorEntity):
    """Sensor that shows the active mode of the tea maker."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_icon = "mdi:tune"
    _attr_options = [
        "Beklemede (Kapalı)",
        "Filtre Kahve",
        "Su Kaynatma",
        "Çay Demleme",
        "Mama Suyu",
    ]

    def __init__(self, coordinator, entry: ConfigEntry, name_prefix: str):
        """Initialize the active mode sensor."""
        super().__init__(coordinator, entry, name_prefix)
        self._attr_name = f"{self.name_prefix} Aktif Mod"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.coordinator.device_udid}_mode"

    @property
    def native_value(self) -> str:
        """Return the native value of the sensor."""
        try:
            detail = self.coordinator.data.get("detail", {})
            mode_id = detail.get("mode", 1)
            # Map mode ID to friendly label (e.g. 6 -> "Su Kaynatma")
            val = MODE_LABELS.get(mode_id, "Beklemede (Kapalı)")
            if val in self._attr_options:
                return val
            return "Beklemede (Kapalı)"
        except Exception:
            return "Beklemede (Kapalı)"
