"""Test the sensor module."""
import pytest
from unittest.mock import patch, MagicMock
from homeassistant.const import UnitOfTemperature

from custom_components.lambda_heat_pumps.sensor import async_setup_entry


@pytest.mark.asyncio
async def test_sensor_setup(hass, mock_config_entry, mock_coordinator):
    """Test sensor entity setup."""
    DOMAIN = "lambda_heat_pumps"
    entry_id = getattr(mock_config_entry, 'entry_id', 'test')
    mock_config_entry.options = {}
    mock_config_entry.data = {"num_hps": 1, "num_boil": 0, "num_hc": 0, "num_buff": 0, "num_sol": 0}
    hass.data = {DOMAIN: {entry_id: {"coordinator": mock_coordinator}}}
    # Koordinator-Daten so setzen, dass ein Sensor erzeugt wird
    mock_coordinator.data = {"hp1_error_state": 0}
    mock_coordinator.is_register_disabled = MagicMock(return_value=False)

    with patch(
        "custom_components.lambda_heat_pumps.sensor.LambdaSensor"
    ) as mock_sensor_class:
        mock_sensor_instance = MagicMock()
        mock_sensor_class.return_value = mock_sensor_instance
        mock_sensor_instance._attr_native_unit_of_measurement = (
            UnitOfTemperature.CELSIUS
        )

        await async_setup_entry(hass, mock_config_entry, mock_coordinator)
        # Überprüfe, dass LambdaSensor mindestens einmal aufgerufen wurde
        assert mock_sensor_class.called