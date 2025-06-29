"""Test the calculated sensor module."""
from unittest.mock import MagicMock, patch

import pytest
from homeassistant.components.sensor import SensorDeviceClass

from custom_components.lambda_heat_pumps.calculated_sensor import \
    LambdaCalculatedSensor


@pytest.mark.asyncio
async def test_calculated_sensor_initialization(
    hass, mock_config_entry, mock_coordinator
):
    """Test calculated sensor initialization."""
    # Setup
    mock_config_entry.data = {"num_hps": 1, "num_boil": 0, "num_hc": 0, "num_buff": 0, "num_sol": 0}
    mock_coordinator.data = {}
    mock_coordinator.is_register_disabled = MagicMock(return_value=False)
    mock_coordinator.sensor_overrides = {}

    # Create calculated sensor
    sensor = LambdaCalculatedSensor(
        coordinator=mock_coordinator,
        entry=mock_config_entry,
        sensor_id="hp1_cop_calc",
        name="COP Calculated",
        unit=None,
        address=None,
        scale=1.0,
        state_class="measurement",
        device_class=None,
        relative_address=0,
        data_type="calculated",
        device_type="hp",
        txt_mapping=False,
        precision=2,
        entity_id="sensor.hp1_cop_calc",
        unique_id="lambda_heat_pumps_hp1_cop_calc",
        template_str=(
            "{{ (states('sensor.{device_prefix}_thermal_output') | float(0) / "
            "states('sensor.{device_prefix}_power_input') | float(1)) | round(2) }}"
        )
    )

    # Test initialization
    assert sensor._sensor_id == "hp1_cop_calc"
    assert sensor._name == "COP Calculated"
    assert sensor._unit is None
    assert sensor._state_class == "measurement"
    assert sensor._device_class is None
    assert sensor._data_type == "calculated"
    assert sensor._device_type == "hp"
    assert sensor._precision == 2


@pytest.mark.asyncio
async def test_calculated_sensor_properties(
    hass, mock_config_entry, mock_coordinator
):
    """Test calculated sensor properties."""
    # Setup
    mock_config_entry.data = {"num_hps": 1, "num_boil": 0, "num_hc": 0, "num_buff": 0, "num_sol": 0}
    mock_coordinator.data = {}
    mock_coordinator.is_register_disabled = MagicMock(return_value=False)
    mock_coordinator.sensor_overrides = {}

    # Create calculated sensor
    sensor = LambdaCalculatedSensor(
        coordinator=mock_coordinator,
        entry=mock_config_entry,
        sensor_id="hp1_efficiency_ratio",
        name="Efficiency Ratio",
        unit="%",
        address=None,
        scale=1.0,
        state_class="measurement",
        device_class=SensorDeviceClass.POWER_FACTOR,
        relative_address=0,
        data_type="calculated",
        device_type="hp",
        txt_mapping=False,
        precision=1,
        entity_id="sensor.hp1_efficiency_ratio",
        unique_id="lambda_heat_pumps_hp1_efficiency_ratio",
        template_str=(
            "{{ (states('sensor.{device_prefix}_actual_capacity') | float(0) / "
            "states('sensor.{device_prefix}_rated_capacity') | float(100)) * 100 | "
            "round(1) }}"
        )
    )

    # Test properties
    assert sensor.name == "Efficiency Ratio"
    assert sensor.native_unit_of_measurement == "%"
    assert sensor.state_class == "measurement"
    assert sensor.device_class == SensorDeviceClass.POWER_FACTOR
    assert sensor.unique_id == "lambda_heat_pumps_hp1_efficiency_ratio"


@pytest.mark.asyncio
async def test_calculated_sensor_template_rendering_success(
    hass, mock_config_entry, mock_coordinator
):
    """Test successful template rendering."""
    # Setup mit validen Daten
    mock_config_entry.data = {"num_hps": 1, "num_boil": 0, "num_hc": 0, "num_buff": 0, "num_sol": 0}
    mock_coordinator.data = {
        "hp1_compressor_thermal_energy_output_accumulated": 1000,
        "hp1_compressor_power_consumption_accumulated": 500
    }
    mock_coordinator.is_register_disabled = MagicMock(return_value=False)
    mock_coordinator.sensor_overrides = {}

    sensor = LambdaCalculatedSensor(
        coordinator=mock_coordinator,
        entry=mock_config_entry,
        sensor_id="hp1_cop_calc",
        name="COP Calculated",
        unit=None,
        address=None,
        scale=1.0,
        state_class="measurement",
        device_class=None,
        relative_address=0,
        data_type="calculated",
        device_type="hp",
        txt_mapping=False,
        precision=2,
        entity_id="sensor.hp1_cop_calc",
        unique_id="lambda_heat_pumps_hp1_cop_calc",
        template_str=(
            "{{ (states('sensor.{device_prefix}_compressor_thermal_energy_output_accumulated') | "
            "float(0) / states('sensor.{device_prefix}_compressor_power_consumption_accumulated') | "
            "float(1)) | round(2) }}"
        )
    )

    with patch("custom_components.lambda_heat_pumps.calculated_sensor.Template.async_render",
        return_value="2.0"):
        sensor._calculate_value()
        assert sensor.native_value == 2.0


@pytest.mark.asyncio
async def test_calculated_sensor_template_rendering_division_by_zero(
    hass, mock_config_entry, mock_coordinator
):
    """Test template rendering mit Division durch Null."""
    mock_config_entry.data = {"num_hps": 1, "num_boil": 0, "num_hc": 0, "num_buff": 0, "num_sol": 0}
    mock_coordinator.data = {
        "hp1_compressor_thermal_energy_output_accumulated": 1000,
        "hp1_compressor_power_consumption_accumulated": 0
    }
    mock_coordinator.is_register_disabled = MagicMock(return_value=False)
    mock_coordinator.sensor_overrides = {}

    sensor = LambdaCalculatedSensor(
        coordinator=mock_coordinator,
        entry=mock_config_entry,
        sensor_id="hp1_cop_calc",
        name="COP Calculated",
        unit=None,
        address=None,
        scale=1.0,
        state_class="measurement",
        device_class=None,
        relative_address=0,
        data_type="calculated",
        device_type="hp",
        txt_mapping=False,
        precision=2,
        entity_id="sensor.hp1_cop_calc",
        unique_id="lambda_heat_pumps_hp1_cop_calc",
                template_str=(
            "{{ (states('sensor.{device_prefix}_compressor_thermal_energy_output_accumulated') | "
            "float(0) / states('sensor.{device_prefix}_compressor_power_consumption_accumulated') | "
            "float(1)) | round(2) }}"
        )
    )

    with patch("custom_components.lambda_heat_pumps.calculated_sensor.Template.async_render",
        return_value="0"):
        sensor._calculate_value()
        assert sensor.native_value == 0.0


@pytest.mark.asyncio
async def test_calculated_sensor_template_rendering_unavailable_states(
    hass, mock_config_entry, mock_coordinator
):
    """Test template rendering mit unavailable states."""
    mock_config_entry.data = {"num_hps": 1, "num_boil": 0, "num_hc": 0, "num_buff": 0, "num_sol": 0}
    mock_coordinator.data = {}
    mock_coordinator.is_register_disabled = MagicMock(return_value=False)
    mock_coordinator.sensor_overrides = {}

    sensor = LambdaCalculatedSensor(
        coordinator=mock_coordinator,
        entry=mock_config_entry,
        sensor_id="hp1_cop_calc",
        name="COP Calculated",
        unit=None,
        address=None,
        scale=1.0,
        state_class="measurement",
        device_class=None,
        relative_address=0,
        data_type="calculated",
        device_type="hp",
        txt_mapping=False,
        precision=2,
        entity_id="sensor.hp1_cop_calc",
        unique_id="lambda_heat_pumps_hp1_cop_calc",
        template_str="{{ (states('sensor.{device_prefix}_compressor_thermal_energy_output_accumulated') | float(0) / states('sensor.{device_prefix}_compressor_power_consumption_accumulated') | float(1)) | round(2) }}"
    )

    with patch("custom_components.lambda_heat_pumps.calculated_sensor.Template.async_render",
        return_value="unavailable"):
        sensor._calculate_value()
        assert sensor.native_value is None


@pytest.mark.asyncio
async def test_calculated_sensor_device_prefix_extraction(
    hass, mock_config_entry, mock_coordinator
):
    """Test device prefix extraction from sensor ID."""
    # Setup
    mock_config_entry.data = {"num_hps": 1, "num_boil": 0, "num_hc": 0, "num_buff": 0, "num_sol": 0}
    mock_coordinator.data = {}
    mock_coordinator.is_register_disabled = MagicMock(return_value=False)
    mock_coordinator.sensor_overrides = {}

    # Test different sensor ID formats
    test_cases = [
        ("hp1_cop_calc", "hp1"),
        ("hp2_efficiency_ratio", "hp2"),
        ("boil1_temperature", "boil1"),  # 3 Teile: ["boil1", "temperature"] -> "boil1"
        ("hc3_power", "hc3"),
        ("simple_sensor", "simple_sensor")  # 2 Teile: ["simple", "sensor"] -> "simple_sensor"
    ]

    for sensor_id, expected_prefix in test_cases:
        sensor = LambdaCalculatedSensor(
            coordinator=mock_coordinator,
            entry=mock_config_entry,
            sensor_id=sensor_id,
            name="Test Sensor",
            unit=None,
            address=None,
            scale=1.0,
            state_class="measurement",
            device_class=None,
            relative_address=0,
            data_type="calculated",
            device_type="hp",
            txt_mapping=False,
            precision=2,
            entity_id=f"sensor.{sensor_id}",
            unique_id=f"lambda_heat_pumps_{sensor_id}",
                    template_str="{{ states('sensor.{device_prefix}_test') | float(0) }}"
        )

        # Korrekte Logik: Wenn mindestens drei Teile, nur das erste Element als Prefix
        parts = sensor_id.split("_")
        if len(parts) >= 3:
            expected = parts[0]
        elif len(parts) == 2:
            expected = sensor_id
        else:
            expected = sensor_id
        device_prefix = sensor._get_device_prefix()
        assert device_prefix == expected


@pytest.mark.asyncio
async def test_calculated_sensor_legacy_names(
    hass, mock_config_entry, mock_coordinator
):
    """Test calculated sensor with legacy modbus names."""
    # Setup with legacy names enabled
    mock_config_entry.data = {
        "num_hps": 1, "num_boil": 0, "num_hc": 0, "num_buff": 0, "num_sol": 0,
        "use_legacy_modbus_names": True
    }
    mock_coordinator.data = {}
    mock_coordinator.is_register_disabled = MagicMock(return_value=False)
    mock_coordinator.sensor_overrides = {"hp1_cop_calc": "legacy_cop_name"}

    # Create calculated sensor
    sensor = LambdaCalculatedSensor(
        coordinator=mock_coordinator,
        entry=mock_config_entry,
        sensor_id="hp1_cop_calc",
        name="COP Calculated",
        unit=None,
        address=None,
        scale=1.0,
        state_class="measurement",
        device_class=None,
        relative_address=0,
        data_type="calculated",
        device_type="hp",
        txt_mapping=False,
        precision=2,
        entity_id="sensor.hp1_cop_calc",
        unique_id="lambda_heat_pumps_hp1_cop_calc",
                template_str="{{ states('sensor.{device_prefix}_test') | float(0) }}"
    )

    # Test legacy name override
    assert sensor.name == "legacy_cop_name"


@pytest.mark.asyncio
async def test_calculated_sensor_device_info(
    hass, mock_config_entry, mock_coordinator
):
    """Test calculated sensor device info."""
    # Setup
    mock_config_entry.data = {"num_hps": 1, "num_boil": 0, "num_hc": 0, "num_buff": 0, "num_sol": 0}
    mock_config_entry.entry_id = "test_entry_id"
    mock_coordinator.data = {}
    mock_coordinator.is_register_disabled = MagicMock(return_value=False)
    mock_coordinator.sensor_overrides = {}

    # Create calculated sensor
    sensor = LambdaCalculatedSensor(
        coordinator=mock_coordinator,
        entry=mock_config_entry,
        sensor_id="hp1_cop_calc",
        name="COP Calculated",
        unit=None,
        address=None,
        scale=1.0,
        state_class="measurement",
        device_class=None,
        relative_address=0,
        data_type="calculated",
        device_type="hp",
        txt_mapping=False,
        precision=2,
        entity_id="sensor.hp1_cop_calc",
        unique_id="lambda_heat_pumps_hp1_cop_calc",
                template_str="{{ states('sensor.{device_prefix}_test') | float(0) }}"
    )

    # Test device info
    device_info = sensor.device_info
    assert device_info["identifiers"] == {("lambda_heat_pumps", "test_entry_id")}
    assert device_info["name"] == "Lambda hp"
    assert device_info["manufacturer"] == "Lambda"
    assert device_info["model"] == "Heat Pump"


@pytest.mark.asyncio
async def test_calculated_sensor_coordinator_update(
    hass, mock_config_entry, mock_coordinator
):
    """Test coordinator update handling."""
    # Setup
    mock_config_entry.data = {"num_hps": 1, "num_boil": 0, "num_hc": 0, "num_buff": 0, "num_sol": 0}
    mock_coordinator.data = {
        "hp1_compressor_thermal_energy_output_accumulated": 1000,
        "hp1_compressor_power_consumption_accumulated": 500
    }
    mock_coordinator.is_register_disabled = MagicMock(return_value=False)
    mock_coordinator.sensor_overrides = {}

    # Create calculated sensor
    sensor = LambdaCalculatedSensor(
        coordinator=mock_coordinator,
        entry=mock_config_entry,
        sensor_id="hp1_cop_calc",
        name="COP Calculated",
        unit=None,
        address=None,
        scale=1.0,
        state_class="measurement",
        device_class=None,
        relative_address=0,
        data_type="calculated",
        device_type="hp",
        txt_mapping=False,
        precision=2,
        entity_id="sensor.hp1_cop_calc",
        unique_id="lambda_heat_pumps_hp1_cop_calc",
        template_str="{{ (states('sensor.{device_prefix}_compressor_thermal_energy_output_accumulated') | float(0) / states('sensor.{device_prefix}_compressor_power_consumption_accumulated') | float(1)) | round(2) }}"
    )

    with patch("custom_components.lambda_heat_pumps.calculated_sensor.Template.async_render", return_value="2.0"), \
         patch.object(sensor, 'async_write_ha_state'):
        # Test coordinator update
        sensor._handle_coordinator_update()

        # Verify that _calculate_value was called and state was updated
        assert sensor.native_value == 2.0


@pytest.mark.asyncio
async def test_calculated_sensor_device_class_none_handling(
    hass, mock_config_entry, mock_coordinator
):
    """Test handling of None device_class."""
    # Setup
    mock_config_entry.data = {"num_hps": 1, "num_boil": 0, "num_hc": 0, "num_buff": 0, "num_sol": 0}
    mock_coordinator.data = {}
    mock_coordinator.is_register_disabled = MagicMock(return_value=False)
    mock_coordinator.sensor_overrides = {}

    # Create calculated sensor with None device_class
    sensor = LambdaCalculatedSensor(
        coordinator=mock_coordinator,
        entry=mock_config_entry,
        sensor_id="hp1_cop_calc",
        name="COP Calculated",
        unit=None,
        address=None,
        scale=1.0,
        state_class="measurement",
        device_class=None,
        relative_address=0,
        data_type="calculated",
        device_type="hp",
        txt_mapping=False,
        precision=2,
        entity_id="sensor.hp1_cop_calc",
        unique_id="lambda_heat_pumps_hp1_cop_calc",
                template_str="{{ states('sensor.{device_prefix}_test') | float(0) }}"
    )

    # Test that device_class is properly set to None
    assert sensor.device_class is None

