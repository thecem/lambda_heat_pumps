"""
Lambda Heat Pumps - Cycling Automations
Handles daily cycling counter updates and automation setup.
"""

import logging
from datetime import datetime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.dispatcher import async_dispatcher_send

_LOGGER = logging.getLogger(__name__)

# Signal für Yesterday-Update
SIGNAL_UPDATE_YESTERDAY = "lambda_heat_pumps_update_yesterday"


def setup_cycling_automations(hass: HomeAssistant, entry_id: str) -> None:
    """Set up cycling-related automations for the integration."""
    _LOGGER.info("Setting up cycling automations for entry %s", entry_id)

    # Tägliche Aktualisierung der Yesterday-Sensoren um Mitternacht
    @callback
    def update_yesterday_sensors(now: datetime) -> None:
        """Update yesterday sensors at midnight."""
        _LOGGER.info("Updating yesterday cycling sensors at midnight")

        # Sende Signal an alle Cycling-Sensoren
        async_dispatcher_send(hass, SIGNAL_UPDATE_YESTERDAY, entry_id)

    # Registriere die Zeit-basierte Automatisierung
    # async_track_time_change ist KEINE Coroutine, daher KEIN await!
    listener = async_track_time_change(
        hass, update_yesterday_sensors, hour=0, minute=0, second=0
    )

    # Speichere den Listener für späteres Cleanup
    if "lambda_heat_pumps" not in hass.data:
        hass.data["lambda_heat_pumps"] = {}
    if entry_id not in hass.data["lambda_heat_pumps"]:
        hass.data["lambda_heat_pumps"][entry_id] = {}
    hass.data["lambda_heat_pumps"][entry_id]["cycling_listener"] = listener

    _LOGGER.info("Cycling automations set up successfully")


def cleanup_cycling_automations(hass: HomeAssistant, entry_id: str) -> None:
    """Clean up cycling-related automations."""
    _LOGGER.info("Cleaning up cycling automations for entry %s", entry_id)

    # Cleanup des Listeners
    if (
        "lambda_heat_pumps" in hass.data
        and entry_id in hass.data["lambda_heat_pumps"]
        and "cycling_listener" in hass.data["lambda_heat_pumps"][entry_id]
    ):
        listener = hass.data["lambda_heat_pumps"][entry_id]["cycling_listener"]
        if listener:
            listener()
            _LOGGER.info("Cleaned up cycling listener for entry %s", entry_id)

        # Entferne den Eintrag
        del hass.data["lambda_heat_pumps"][entry_id]["cycling_listener"]
