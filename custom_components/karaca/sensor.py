"""Platform for Karaca Connect sensor integration."""
import asyncio
from datetime import timedelta

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import homeassistant.util.dt as dt_util

from .const import (
    CONF_NAME_PREFIX,
    DEFAULT_NAME,
    DOMAIN,
    LOGGER,
    MODE_BABY_FOOD,
    MODE_BOILING_WATER,
    MODE_FILTER_COFFEE,
    MODE_LABELS,
    MODE_STANDBY,
    MODE_TEA_BREWING,
    normalize_key,
    normalize_mode_id,
)

STATUS_OFF = "Kapalı"
STATUS_WATER_BOILING = "Su Kaynatılıyor"
STATUS_WATER_READY = "Su Hazır"
STATUS_TEA_BREWING = "Çay Demleniyor"
STATUS_TEA_READY_FRESH = "Çay Hazır (Taze)"
STATUS_TEA_READY_STALE = "Çay Hazır (Bayat)"
STATUS_FILTER_COFFEE_BREWING = "Filtre Kahve Demleniyor"
STATUS_COFFEE_READY = "Kahve Hazır"
STATUS_BABY_WATER_HEATING = "Mama Suyu Isıtılıyor"
STATUS_BABY_WATER_READY = "Mama Suyu Hazır"
STATUS_UNKNOWN = "Bilinmeyen Durum"

FRESHNESS_FRESH = "Taze"
FRESHNESS_STALE = "Bayat"
FRESHNESS_OFF = "Kapalı"
FRESHNESS_UNKNOWN = "Bilinmiyor"
TEA_FRESHNESS_DURATION = timedelta(minutes=60)

STATUS_BY_STEP_ID = {
    "standbyoff": STATUS_OFF,
    "boilingwaterwaterboiling": STATUS_WATER_BOILING,
    "boilingwaterwaterboiled": STATUS_WATER_READY,
    "teabrewingteabrewing": STATUS_TEA_BREWING,
    "teabrewingteaready": STATUS_TEA_READY_FRESH,
    "teabrewingfresh": STATUS_TEA_READY_FRESH,
    "teabrewingbrewedfresh": STATUS_TEA_READY_FRESH,
    "teabrewingstale": STATUS_TEA_READY_STALE,
    "teabrewingbrewedstale": STATUS_TEA_READY_STALE,
    "filtercoffeefiltercoffeebrewing": STATUS_FILTER_COFFEE_BREWING,
    "filtercoffeefiltercoffeeready": STATUS_COFFEE_READY,
    "filtercoffeecoffeeready": STATUS_COFFEE_READY,
    "babyfoodbabyfoodheating": STATUS_BABY_WATER_HEATING,
    "babyfoodbabyfoodready": STATUS_BABY_WATER_READY,
}

STATUS_BY_MODE_STATE_LABEL = {
    "off": STATUS_OFF,
    "waterboiling": STATUS_WATER_BOILING,
    "waterboiled": STATUS_WATER_READY,
    "teabrewing": STATUS_TEA_BREWING,
    "teaready": STATUS_TEA_READY_FRESH,
    "fresh": STATUS_TEA_READY_FRESH,
    "brewedfresh": STATUS_TEA_READY_FRESH,
    "stale": STATUS_TEA_READY_STALE,
    "brewedstale": STATUS_TEA_READY_STALE,
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
    STATUS_TEA_READY_FRESH,
    STATUS_TEA_READY_STALE,
    STATUS_TEA_BREWING,
    STATUS_COFFEE_READY,
    STATUS_FILTER_COFFEE_BREWING,
    STATUS_BABY_WATER_READY,
    STATUS_BABY_WATER_HEATING,
    STATUS_OFF,
    STATUS_UNKNOWN,
    *ERROR_STATUS_OPTIONS,
]

FRESHNESS_OPTIONS = [
    FRESHNESS_FRESH,
    FRESHNESS_STALE,
    FRESHNESS_OFF,
    FRESHNESS_UNKNOWN,
]

MODE_STATUS_OFF = "Kapalı"
MODE_STATUS_STANDBY = "Beklemede"
MODE_SENSOR_OPTIONS = [
    MODE_STATUS_OFF,
    MODE_STATUS_STANDBY,
    MODE_LABELS[MODE_BOILING_WATER],
    MODE_LABELS[MODE_TEA_BREWING],
    MODE_LABELS[MODE_FILTER_COFFEE],
    MODE_LABELS[MODE_BABY_FOOD],
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


def _parse_api_datetime(value):
    """Parse Karaca API datetime values as local time when timezone is omitted."""
    if not value:
        return None

    parsed = dt_util.parse_datetime(str(value))
    if parsed is None:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)
    return parsed


def _positive_number_from_mapping(data: dict | None, keys: tuple[str, ...]):
    """Return the first positive numeric value in a nested API mapping."""
    if not isinstance(data, dict):
        return None

    for key in keys:
        value = data.get(key)
        if value in (None, ""):
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        return number if number > 0 else 0

    return None


def _is_tea_ready_detail(detail: dict) -> bool:
    """Return if the device detail currently represents a brewed tea ready state."""
    step_view = detail.get("stepView") or {}
    step_id = normalize_key(step_view.get("id"))
    label = normalize_key(step_view.get("label"))
    mode_state_label = normalize_key(detail.get("modeStateLabel"))

    return (
        "teaready" in step_id
        or "brewedfresh" in step_id
        or "brewedstale" in step_id
        or mode_state_label in {"teaready", "fresh", "brewedfresh", "stale", "brewedstale"}
        or "çayhazır" in label
        or "cayhazir" in label
    )


def _freshness_status_from_detail(detail: dict) -> str:
    """Return Taze/Bayat/Kapalı/Bilinmiyor from Karaca freshness data."""
    if not _is_tea_ready_detail(detail):
        return FRESHNESS_OFF

    step_view = detail.get("stepView") or {}
    step_id = normalize_key(step_view.get("id"))
    mode_state_label = normalize_key(detail.get("modeStateLabel"))
    if "stale" in step_id or "bayat" in step_id or mode_state_label in {"stale", "brewedstale"}:
        return FRESHNESS_STALE

    freshness = detail.get("freshness")
    modes = detail.get("modes") or {}
    tea_mode = modes.get("teaBrewing") or modes.get("tea_brewing") or {}
    mode_freshness = tea_mode.get("freshness")
    countdown = step_view.get("countdown")

    freshness_sources = [freshness, mode_freshness, countdown]
    for source in freshness_sources:
        remaining = _positive_number_from_mapping(
            source,
            (
                "remainingSeconds",
                "remaining_seconds",
                "seconds",
                "remainingSecond",
                "remainingMinutes",
                "remaining_minutes",
                "minutes",
                "minute",
                "value",
            ),
        )
        if remaining is not None:
            return FRESHNESS_FRESH if remaining > 0 else FRESHNESS_STALE

    for source in (freshness, mode_freshness):
        if isinstance(source, dict) and source.get("show") is True:
            return FRESHNESS_FRESH

    if isinstance(countdown, dict) and countdown:
        display_text = normalize_key(countdown.get("displayText"))
        if "tazelik" in display_text or "fresh" in display_text:
            return FRESHNESS_FRESH

    updated = _parse_api_datetime(detail.get("updatedDate"))
    if updated is None:
        return FRESHNESS_UNKNOWN

    elapsed = dt_util.now() - dt_util.as_local(updated)
    if elapsed <= TEA_FRESHNESS_DURATION:
        return FRESHNESS_FRESH
    return FRESHNESS_STALE


def _fresh_until_from_detail(detail: dict):
    """Return freshness expiry datetime when it can be inferred."""
    if not _is_tea_ready_detail(detail):
        return None
    updated = _parse_api_datetime(detail.get("updatedDate"))
    if updated is None:
        return None
    return dt_util.as_local(updated) + TEA_FRESHNESS_DURATION


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
        KaracaFreshnessSensor(coordinator, config_entry, name_prefix),
    ]
    async_add_entities(sensors)


class KaracaBaseEntity(CoordinatorEntity):
    """Base class for all Karaca entities."""

    def __init__(self, coordinator, entry: ConfigEntry, name_prefix: str):
        """Initialize the base entity."""
        super().__init__(coordinator)
        self.entry = entry
        self.name_prefix = name_prefix

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

    async def async_refresh_after_command(self) -> None:
        """Refresh immediately, then follow up shortly after a cloud command."""
        try:
            await self.coordinator.async_request_refresh()
        except Exception as err:  # pylint: disable=broad-except
            LOGGER.debug("Immediate Karaca refresh after command failed: %s", err)

        async def delayed_refresh(delay: float) -> None:
            await asyncio.sleep(delay)
            try:
                await self.coordinator.async_request_refresh()
            except Exception as err:  # pylint: disable=broad-except
                LOGGER.debug("Delayed Karaca refresh after command failed: %s", err)

        for delay in (1.5, 4.0):
            self.coordinator.hass.async_create_task(delayed_refresh(delay))

    def set_temporary_error(self, message: str) -> None:
        """Expose a command error briefly through the status sensor."""
        self.coordinator.last_error = str(message)
        self.coordinator.async_set_updated_data(self.coordinator.data)

        async def clear_error(expected_message: str) -> None:
            await asyncio.sleep(self.coordinator.error_clear_seconds)
            if self.coordinator.last_error == expected_message:
                self.coordinator.last_error = None
                self.coordinator.async_set_updated_data(self.coordinator.data)

        self.coordinator.hass.async_create_task(clear_error(str(message)))


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
            step_view = detail.get("stepView") or {}

            if _is_tea_ready_detail(detail):
                freshness_status = _freshness_status_from_detail(detail)
                if freshness_status == FRESHNESS_STALE:
                    return STATUS_TEA_READY_STALE
                return STATUS_TEA_READY_FRESH

            step_id = normalize_key(step_view.get("id"))
            if step_id in STATUS_BY_STEP_ID:
                return STATUS_BY_STEP_ID[step_id]

            mode_state_label = normalize_key(detail.get("modeStateLabel"))
            if mode_state_label in STATUS_BY_MODE_STATE_LABEL:
                return STATUS_BY_MODE_STATE_LABEL[mode_state_label]

            label = step_view.get("label")
            if label in self._attr_options:
                return label

            if label:
                LOGGER.debug(
                    "Unknown Karaca status step_id=%s, mode_state_label=%s, label=%s",
                    step_view.get("id"),
                    detail.get("modeStateLabel"),
                    label,
                )
                return STATUS_UNKNOWN

            if normalize_mode_id(detail.get("mode")) == MODE_STANDBY:
                return STATUS_OFF
            return STATUS_UNKNOWN
        except Exception:  # pylint: disable=broad-except
            return STATUS_UNKNOWN

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes."""
        try:
            detail = self.coordinator.data.get("detail", {})
            meta = self.coordinator.data.get("meta", {})
            fresh_until = _fresh_until_from_detail(detail)
            return {
                "karaca_role": "status",
                "countdown": detail.get("stepView", {}).get("countdown"),
                "freshness": detail.get("freshness"),
                "fresh_until": fresh_until.isoformat() if fresh_until else None,
                "connected": meta.get("connected", True),
                "last_updated": detail.get("updatedDate"),
                "state_code": detail.get("state"),
                "mode_state_code": detail.get("modeState"),
                "step_id": detail.get("stepView", {}).get("id"),
                "mode_state_label": detail.get("modeStateLabel"),
                "last_error": self.coordinator.last_error,
            }
        except Exception:  # pylint: disable=broad-except
            return {}


class KaracaModeSensor(KaracaBaseEntity, SensorEntity):
    """Sensor that shows the active mode of the tea maker."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_icon = "mdi:tune"
    _attr_options = MODE_SENSOR_OPTIONS

    def __init__(self, coordinator, entry: ConfigEntry, name_prefix: str):
        """Initialize the active mode sensor."""
        super().__init__(coordinator, entry, name_prefix)
        self._attr_name = f"{self.name_prefix} Aktif Mod"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.coordinator.device_udid}_mode"

    @property
    def available(self) -> bool:
        """Keep active mode visible so disconnected devices can show Kapalı."""
        return self.coordinator.last_update_success and self.coordinator.data is not None

    @property
    def native_value(self) -> str:
        """Return the native value of the sensor."""
        try:
            detail = self.coordinator.data.get("detail", {})
            meta = self.coordinator.data.get("meta", {})
            if meta.get("connected") is False:
                return MODE_STATUS_OFF

            mode_id = normalize_mode_id(detail.get("mode"))
            if mode_id == MODE_STANDBY:
                return MODE_STATUS_STANDBY

            return MODE_LABELS.get(mode_id, MODE_STATUS_STANDBY)
        except Exception:  # pylint: disable=broad-except
            return MODE_STATUS_STANDBY

    @property
    def extra_state_attributes(self) -> dict:
        """Return mode sensor metadata."""
        return {"karaca_role": "active_mode"}


class KaracaFreshnessSensor(KaracaBaseEntity, SensorEntity):
    """Sensor that shows whether brewed tea is still fresh."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_icon = "mdi:timer-sand"
    _attr_options = FRESHNESS_OPTIONS

    def __init__(self, coordinator, entry: ConfigEntry, name_prefix: str):
        """Initialize the tea freshness sensor."""
        super().__init__(coordinator, entry, name_prefix)
        self._attr_name = f"{self.name_prefix} Çay Tazeliği"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.coordinator.device_udid}_tea_freshness"

    @property
    def native_value(self) -> str:
        """Return the freshness state."""
        try:
            detail = self.coordinator.data.get("detail", {})
            return _freshness_status_from_detail(detail)
        except Exception:  # pylint: disable=broad-except
            return FRESHNESS_UNKNOWN

    @property
    def extra_state_attributes(self) -> dict:
        """Return freshness metadata."""
        try:
            detail = self.coordinator.data.get("detail", {})
            fresh_until = _fresh_until_from_detail(detail)
            remaining_minutes = None
            if fresh_until:
                remaining = (fresh_until - dt_util.now()).total_seconds()
                remaining_minutes = max(0, int(remaining // 60))

            return {
                "karaca_role": "tea_freshness",
                "fresh_for_minutes": int(TEA_FRESHNESS_DURATION.total_seconds() // 60),
                "fresh_until": fresh_until.isoformat() if fresh_until else None,
                "remaining_minutes": remaining_minutes,
                "freshness": detail.get("freshness"),
                "countdown": detail.get("stepView", {}).get("countdown"),
            }
        except Exception:  # pylint: disable=broad-except
            return {}
