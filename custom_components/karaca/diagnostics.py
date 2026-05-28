"""Diagnostics support for Karaca Connect."""
from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

TO_REDACT = {
    "email",
    "password",
    "refresh_token",
    "jw_token",
    "Authorization",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict:
    """Return diagnostics for a config entry."""
    runtime_data = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    coordinator = runtime_data.get("coordinator")

    diagnostics = {
        "entry": {
            "title": entry.title,
            "data": dict(entry.data),
            "options": dict(entry.options),
        },
        "coordinator": {
            "device_id": getattr(coordinator, "device_id", None),
            "device_type": getattr(coordinator, "device_type", None),
            "device_name": getattr(coordinator, "device_name", None),
            "device_udid": getattr(coordinator, "device_udid", None),
            "last_error": getattr(coordinator, "last_error", None),
            "last_update_success": getattr(coordinator, "last_update_success", None),
        },
        "latest_data": getattr(coordinator, "data", None),
    }

    return async_redact_data(diagnostics, TO_REDACT)
