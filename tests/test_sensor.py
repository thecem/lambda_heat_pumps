"""Test the sensor module."""
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant

from custom_components.lambda_heat_pumps.const import (BOIL_SENSOR_TEMPLATES,
                                                       BUFF_SENSOR_TEMPLATES,
                                                       DOMAIN,
                                                       HC_SENSOR_TEMPLATES,
                                                       HP_SENSOR_TEMPLATES,
                                                       SENSOR_TYPES,
                                                       SOL_SENSOR_TEMPLATES)
from custom_components.lambda_heat_pumps.sensor import (LambdaSensor,
                                                        async_setup_entry)


@pytest.fixture
def mock_hass():
    """Create a mock hass object."""
    hass = Mock()
    hass.config = Mock()
    hass.config.config_dir = "/tmp/test_config"
    hass.config_entries = Mock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    hass.data = {}
    hass.states = Mock()
    hass.states.async_all = AsyncMock(return_value=[])
    return hass


@pytest.fixture
def mock_entry():
    """Create a mock config entry."""
    entry = Mock()
    entry.entry_id = "test_entry"
    entry.data = {
        "host": "192.168.1.100",
        "port": 502,
        "slave_id": 1,
        "firmware_version": "V0.0.3-3K",
        "num_hps": 1,
        "num_boil": 1,
        "num_hc": 1,
        "num_buffer": 0,
        "num_solar": 0,
        "update_interval": 30,
        "write_interval": 30,
        "heating_circuit_min_temp": 15,
        "heating_circuit_max_temp": 35,
        "heating_circuit_temp_step": 0.5,
        "room_thermostat_control": False,
        "pv_surplus": False,
        "room_temperature_entity_1": "sensor.room_temp",
        "pv_power_sensor_entity": "sensor.pv_power"
    }
    return entry


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = Mock()
    coordinator.data = {
        "hp1_temperature": 20.5,
        "hp1_state": 1,
        "hp1_operating_state": 2
    }
    coordinator.sensor_overrides = {}
    return coordinator


@pytest.mark.asyncio
async def test_async_setup_entry_no_coordinator(mock_hass, mock_entry):
    """Test async setup entry when no coordinator exists."""
    mock_add_entities = AsyncMock()
    
    # Don't set up coordinator in hass.data
    mock_hass.data[DOMAIN] = {}
    
    # This should raise a KeyError, which is expected behavior
    with pytest.raises(KeyError):
        await async_setup_entry(mock_hass, mock_entry, mock_add_entities)


@pytest.mark.asyncio
async def test_async_setup_entry_with_coordinator(mock_hass, mock_entry, mock_coordinator):
    """Test async setup entry with coordinator."""
    mock_add_entities = AsyncMock()
    mock_hass.data[DOMAIN] = {mock_entry.entry_id: {"coordinator": mock_coordinator}}
    
    with patch("custom_components.lambda_heat_pumps.sensor.LambdaSensor") as mock_sensor_class:
        mock_sensor = Mock()
        mock_sensor_class.return_value = mock_sensor
        
        result = await async_setup_entry(mock_hass, mock_entry, mock_add_entities)
        
        # Should call add_entities
        mock_add_entities.assert_called()


@pytest.mark.asyncio
async def test_async_setup_entry_with_disabled_registers(mock_hass, mock_entry, mock_coordinator):
    """Test async setup entry with disabled registers."""
    mock_add_entities = AsyncMock()
    mock_hass.data[DOMAIN] = {mock_entry.entry_id: {"coordinator": mock_coordinator}}
    mock_coordinator.is_register_disabled.return_value = True
    
    with patch("custom_components.lambda_heat_pumps.sensor.LambdaSensor") as mock_sensor_class:
        mock_sensor = Mock()
        mock_sensor_class.return_value = mock_sensor
        
        result = await async_setup_entry(mock_hass, mock_entry, mock_add_entities)
        
        # Should call add_entities but skip disabled registers
        mock_add_entities.assert_called()


@pytest.mark.asyncio
async def test_async_setup_entry_with_legacy_names(mock_hass, mock_entry, mock_coordinator):
    """Test async setup entry with legacy names."""
    mock_add_entities = AsyncMock()
    mock_hass.data[DOMAIN] = {mock_entry.entry_id: {"coordinator": mock_coordinator}}
    mock_entry.data["use_legacy_modbus_names"] = True
    
    with patch("custom_components.lambda_heat_pumps.sensor.LambdaSensor") as mock_sensor_class:
        mock_sensor = Mock()
        mock_sensor_class.return_value = mock_sensor
        
        result = await async_setup_entry(mock_hass, mock_entry, mock_add_entities)
        
        # Should call add_entities
        mock_add_entities.assert_called()


def test_lambda_sensor_init(mock_entry, mock_coordinator):
    """Test LambdaSensor initialization."""
    sensor = LambdaSensor(
        coordinator=mock_coordinator,
        entry=mock_entry,
        sensor_id="hp1_temperature",
        name="Test Sensor",
        unit="°C",
        address=1000,
        scale=1.0,
        state_class="measurement",
        device_class="temperature",
        relative_address=0,
        data_type="int16",
        device_type="HP",
        txt_mapping=False,
        precision=1,
        entity_id="sensor.hp1_temperature",
        unique_id="hp1_temperature"
    )
    
    assert sensor.coordinator == mock_coordinator
    assert sensor._entry == mock_entry
    assert sensor._sensor_id == "hp1_temperature"
    assert sensor._attr_name == "Test Sensor"
    assert sensor._unit == "°C"
    assert sensor._address == 1000
    assert sensor._scale == 1.0
    assert sensor._state_class == "measurement"
    assert sensor._device_class == "temperature"
    assert sensor._relative_address == 0
    assert sensor._data_type == "int16"
    assert sensor._device_type == "HP"
    assert sensor._txt_mapping is False
    assert sensor._precision == 1
    assert sensor.entity_id == "sensor.hp1_temperature"
    assert sensor._attr_unique_id == "hp1_temperature"


def test_lambda_sensor_name_property(mock_entry, mock_coordinator):
    """Test LambdaSensor name property."""
    sensor = LambdaSensor(
        coordinator=mock_coordinator,
        entry=mock_entry,
        sensor_id="hp1_temperature",
        name="Test Sensor",
        unit="°C",
        address=1000,
        scale=1.0,
        state_class="measurement",
        device_class="temperature",
        relative_address=0,
        data_type="int16",
        device_type="HP",
        txt_mapping=False,
        precision=1,
        entity_id="sensor.hp1_temperature",
        unique_id="hp1_temperature"
    )
    
    # Test with sensor_overrides
    mock_coordinator.sensor_overrides = {"hp1_temperature": "Custom Name"}
    mock_entry.data = {"use_legacy_modbus_names": True}
    assert sensor.name == "Custom Name"
    
    # Test without sensor_overrides
    mock_coordinator.sensor_overrides = {}
    assert sensor.name == "Test Sensor"


def test_lambda_sensor_native_value_none(mock_entry, mock_coordinator):
    """Test LambdaSensor native_value when data is None."""
    sensor = LambdaSensor(
        coordinator=mock_coordinator,
        entry=mock_entry,
        sensor_id="hp1_temperature",
        name="Test Sensor",
        unit="°C",
        address=1000,
        scale=1.0,
        state_class="measurement",
        device_class="temperature",
        relative_address=0,
        data_type="int16",
        device_type="HP",
        txt_mapping=False,
        precision=1,
        entity_id="sensor.hp1_temperature",
        unique_id="hp1_temperature"
    )
    mock_coordinator.data = {}
    
    assert sensor.native_value is None


def test_lambda_sensor_native_value_with_data(mock_entry, mock_coordinator):
    """Test LambdaSensor native_value with data."""
    sensor = LambdaSensor(
        coordinator=mock_coordinator,
        entry=mock_entry,
        sensor_id="hp1_temperature",
        name="Test Sensor",
        unit="°C",
        address=1000,
        scale=1.0,
        state_class="measurement",
        device_class="temperature",
        relative_address=0,
        data_type="int16",
        device_type="HP",
        txt_mapping=False,
        precision=1,
        entity_id="sensor.hp1_temperature",
        unique_id="hp1_temperature"
    )
    mock_coordinator.data = {"hp1_temperature": 20.5}
    
    assert sensor.native_value == 20.5


def test_lambda_sensor_native_value_with_txt_mapping(mock_entry, mock_coordinator):
    """Test LambdaSensor native_value with text mapping."""
    sensor = LambdaSensor(
        coordinator=mock_coordinator,
        entry=mock_entry,
        sensor_id="hp1_state",
        name="HP1 Operating State",
        unit="",
        address=1000,
        scale=1.0,
        state_class="",
        device_class=None,
        relative_address=0,
        data_type="int16",
        device_type="HP",
        txt_mapping=True,
        precision=None,
        entity_id="sensor.hp1_state",
        unique_id="hp1_state"
    )
    mock_coordinator.data = {"hp1_state": 1}
    
    # Mock the text mapping
    with patch("custom_components.lambda_heat_pumps.sensor.HP_OPERATING_STATE", {1: "Running"}):
        assert sensor.native_value == "Running"


def test_lambda_sensor_native_value_with_precision(mock_entry, mock_coordinator):
    """Test LambdaSensor native_value with precision."""
    sensor = LambdaSensor(
        coordinator=mock_coordinator,
        entry=mock_entry,
        sensor_id="hp1_temperature",
        name="Test Sensor",
        unit="°C",
        address=1000,
        scale=0.01,
        state_class="measurement",
        device_class="temperature",
        relative_address=0,
        data_type="int16",
        device_type="HP",
        txt_mapping=False,
        precision=2,
        entity_id="sensor.hp1_temperature",
        unique_id="hp1_temperature"
    )
    mock_coordinator.data = {"hp1_temperature": 20.57}
    
    assert sensor.native_value == 20.57


def test_lambda_sensor_device_info(mock_entry, mock_coordinator):
    """Test LambdaSensor device_info."""
    sensor = LambdaSensor(
        coordinator=mock_coordinator,
        entry=mock_entry,
        sensor_id="hp1_temperature",
        name="Test Sensor",
        unit="°C",
        address=1000,
        scale=1.0,
        state_class="measurement",
        device_class="temperature",
        relative_address=0,
        data_type="int16",
        device_type="HP",
        txt_mapping=False,
        precision=1,
        entity_id="sensor.hp1_temperature",
        unique_id="hp1_temperature"
    )
    
    device_info = sensor.device_info
    assert device_info is not None
    assert "identifiers" in device_info
    assert "name" in device_info


def test_lambda_sensor_unique_id(mock_entry, mock_coordinator):
    """Test LambdaSensor unique_id."""
    sensor = LambdaSensor(
        coordinator=mock_coordinator,
        entry=mock_entry,
        sensor_id="hp1_temperature",
        name="Test Sensor",
        unit="°C",
        address=1000,
        scale=1.0,
        state_class="measurement",
        device_class="temperature",
        relative_address=0,
        data_type="int16",
        device_type="HP",
        txt_mapping=False,
        precision=1,
        entity_id="sensor.hp1_temperature",
        unique_id="hp1_temperature"
    )
    
    assert sensor.unique_id == "hp1_temperature"


def test_lambda_sensor_entity_id(mock_entry, mock_coordinator):
    """Test LambdaSensor entity_id."""
    sensor = LambdaSensor(
        coordinator=mock_coordinator,
        entry=mock_entry,
        sensor_id="hp1_temperature",
        name="Test Sensor",
        unit="°C",
        address=1000,
        scale=1.0,
        state_class="measurement",
        device_class="temperature",
        relative_address=0,
        data_type="int16",
        device_type="HP",
        txt_mapping=False,
        precision=1,
        entity_id="sensor.hp1_temperature",
        unique_id="hp1_temperature"
    )
    
    assert sensor.entity_id == "sensor.hp1_temperature"


def test_lambda_sensor_native_unit_of_measurement(mock_entry, mock_coordinator):
    """Test LambdaSensor native_unit_of_measurement."""
    sensor = LambdaSensor(
        coordinator=mock_coordinator,
        entry=mock_entry,
        sensor_id="hp1_temperature",
        name="Test Sensor",
        unit="°C",
        address=1000,
        scale=1.0,
        state_class="measurement",
        device_class="temperature",
        relative_address=0,
        data_type="int16",
        device_type="HP",
        txt_mapping=False,
        precision=1,
        entity_id="sensor.hp1_temperature",
        unique_id="hp1_temperature"
    )
    
    assert sensor.native_unit_of_measurement == "°C"


def test_lambda_sensor_state_class(mock_entry, mock_coordinator):
    """Test LambdaSensor state_class."""
    sensor = LambdaSensor(
        coordinator=mock_coordinator,
        entry=mock_entry,
        sensor_id="hp1_temperature",
        name="Test Sensor",
        unit="°C",
        address=1000,
        scale=1.0,
        state_class="measurement",
        device_class="temperature",
        relative_address=0,
        data_type="int16",
        device_type="HP",
        txt_mapping=False,
        precision=1,
        entity_id="sensor.hp1_temperature",
        unique_id="hp1_temperature"
    )
    
    assert sensor.state_class == "measurement"


def test_lambda_sensor_device_class(mock_entry, mock_coordinator):
    """Test LambdaSensor device_class."""
    sensor = LambdaSensor(
        coordinator=mock_coordinator,
        entry=mock_entry,
        sensor_id="hp1_temperature",
        name="Test Sensor",
        unit="°C",
        address=1000,
        scale=1.0,
        state_class="measurement",
        device_class="temperature",
        relative_address=0,
        data_type="int16",
        device_type="HP",
        txt_mapping=False,
        precision=1,
        entity_id="sensor.hp1_temperature",
        unique_id="hp1_temperature"
    )
    
    assert sensor.device_class == "temperature"


def test_lambda_sensor_should_poll(mock_entry, mock_coordinator):
    """Test LambdaSensor should_poll."""
    sensor = LambdaSensor(
        coordinator=mock_coordinator,
        entry=mock_entry,
        sensor_id="hp1_temperature",
        name="Test Sensor",
        unit="°C",
        address=1000,
        scale=1.0,
        state_class="measurement",
        device_class="temperature",
        relative_address=0,
        data_type="int16",
        device_type="HP",
        txt_mapping=False,
        precision=1,
        entity_id="sensor.hp1_temperature",
        unique_id="hp1_temperature"
    )
    
    assert sensor.should_poll is False


def test_lambda_sensor_has_entity_name(mock_entry, mock_coordinator):
    """Test LambdaSensor has_entity_name."""
    sensor = LambdaSensor(
        coordinator=mock_coordinator,
        entry=mock_entry,
        sensor_id="hp1_temperature",
        name="Test Sensor",
        unit="°C",
        address=1000,
        scale=1.0,
        state_class="measurement",
        device_class="temperature",
        relative_address=0,
        data_type="int16",
        device_type="HP",
        txt_mapping=False,
        precision=1,
        entity_id="sensor.hp1_temperature",
        unique_id="hp1_temperature"
    )
    
    assert sensor.has_entity_name is True
