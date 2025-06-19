"""Pytest configuration file."""
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from unittest.mock import MagicMock

from custom_components.lambda_heat_pumps.const import DOMAIN


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.data = {
        "temperature": 20.5,
        "humidity": 45.0,
        "pressure": 1013.0,
    }
    return coordinator


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test"
    entry.data = {
        "host": "192.168.1.100",
        "name": "Test Lambda",
        "slave_id": 1,
    }
    return entry


@pytest.fixture
def hass():
    """Create a Home Assistant instance for testing."""
    hass = MagicMock(spec=HomeAssistant)
    hass.data = {DOMAIN: {}}
    hass.config_entries = MagicMock()
    hass.config_entries.async_entries = AsyncMock(return_value=[])
    hass.config_entries.flow = MagicMock()
    hass.config_entries.flow.async_init = AsyncMock()
    hass.config_entries.flow.async_configure = AsyncMock()
    hass.async_block_till_done = AsyncMock()
    return hass


@pytest.fixture
def mock_hass(hass: HomeAssistant, mock_coordinator):
    """Create a mock hass instance with coordinator."""
    hass.data = {DOMAIN: {"test": {"coordinator": mock_coordinator}}}
    return hass 