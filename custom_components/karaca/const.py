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
MODES = {
    1: "StandBy",
    2: "FilterCoffee",
    6: "BoilingWater",
    9: "TeaBrewing",
    13: "BabyFood",
}

MODE_LABELS = {
    1: "Beklemede (Kapalı)",
    2: "Filtre Kahve",
    6: "Su Kaynatma",
    9: "Çay Demleme",
    13: "Mama Suyu",
}
