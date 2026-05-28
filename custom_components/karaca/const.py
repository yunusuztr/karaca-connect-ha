"""Constants for the Karaca Connect integration."""
import logging

DOMAIN = "karaca"
LOGGER = logging.getLogger(__package__)

CONF_NAME_PREFIX = "name_prefix"
CONF_REFRESH_TOKEN = "refresh_token"

BASE_URL = "https://karacaconnectapi.krc.com.tr"

DEFAULT_NAME = "Çay sever"
DEFAULT_SCAN_INTERVAL = 30  # seconds

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
