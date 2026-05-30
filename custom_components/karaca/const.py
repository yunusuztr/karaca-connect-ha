"""Constants for the Karaca Connect integration."""
import logging

DOMAIN = "karaca"
LOGGER = logging.getLogger(__package__)

CONF_NAME_PREFIX = "name_prefix"
CONF_REFRESH_TOKEN = "refresh_token"
CONF_DEVICE_ID = "device_id"
CONF_DEVICE_UDID = "device_udid"
CONF_DEVICE_TYPE = "device_type"
CONF_DEVICE_LABEL = "device_label"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_ERROR_CLEAR_SECONDS = "error_clear_seconds"

BASE_URL = "https://karacaconnectapi.krc.com.tr"

DEFAULT_NAME = "Çay sever"
DEFAULT_SCAN_INTERVAL = 30  # seconds
DEFAULT_ERROR_CLEAR_SECONDS = 15

# Mode mappings
MODE_STANDBY = 1
MODE_FILTER_COFFEE = 2
MODE_BOILING_WATER = 6
MODE_TEA_BREWING = 9
MODE_BABY_FOOD = 13

MODES = {
    MODE_STANDBY: "StandBy",
    MODE_FILTER_COFFEE: "FilterCoffee",
    MODE_BOILING_WATER: "BoilingWater",
    MODE_TEA_BREWING: "TeaBrewing",
    MODE_BABY_FOOD: "BabyFood",
}

MODE_LABELS = {
    MODE_STANDBY: "Beklemede",
    MODE_FILTER_COFFEE: "Filtre Kahve",
    MODE_BOILING_WATER: "Su Kaynatma",
    MODE_TEA_BREWING: "Çay Demleme",
    MODE_BABY_FOOD: "Mama Suyu",
}

MODE_ICONS = {
    MODE_FILTER_COFFEE: "mdi:coffee-maker",
    MODE_BOILING_WATER: "mdi:kettle",
    MODE_TEA_BREWING: "mdi:tea",
    MODE_BABY_FOOD: "mdi:baby-bottle",
}

SETTING_TEA_NOTIFICATION = 1
SETTING_FILTER_COFFEE_NOTIFICATION = 2
SETTING_FRESHNESS = 3
SETTING_POWER_OFF = 4
SETTING_NO_WATER = 5
SETTING_REMINDERS = 6
SETTING_VOICE = 7
SETTING_CLEANING = 8


def normalize_key(value) -> str:
    """Normalize Karaca API text keys for matching."""
    if value is None:
        return ""
    return str(value).replace("_", "").replace("-", "").replace(" ", "").casefold()


def normalize_mode_id(value, default: int = MODE_STANDBY) -> int:
    """Return a stable integer mode id from API values that may be str or int."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
