"""Test the utils module."""
import pytest
from unittest.mock import MagicMock
from homeassistant.const import CONF_HOST, CONF_PORT

from custom_components.lambda_heat_pumps.utils import get_compatible_sensors
from custom_components.lambda_heat_pumps.const import CONF_SLAVE_ID


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    entry = MagicMock()
    entry.data = {
        CONF_HOST: "192.168.1.100",
        CONF_PORT: 502,
        CONF_SLAVE_ID: 1,
    }
    entry.options = {}
    return entry


def test_get_compatible_sensors():
    """Test get_compatible_sensors."""
    # Test-Sensoren mit verschiedenen Firmware-Versionen
    test_sensors = {
        "sensor1": {"firmware_version": 1},
        "sensor2": {"firmware_version": 2},
        "sensor3": {"firmware_version": 3},
        "sensor4": {},  # Kein firmware_version Attribut
    }
    
    # Test mit Firmware-Version 2
    compatible_sensors = get_compatible_sensors(test_sensors, 2)
    assert "sensor1" in compatible_sensors
    assert "sensor2" in compatible_sensors
    assert "sensor3" not in compatible_sensors
    # Sollte enthalten sein, da Standard-Version 1
    assert "sensor4" in compatible_sensors