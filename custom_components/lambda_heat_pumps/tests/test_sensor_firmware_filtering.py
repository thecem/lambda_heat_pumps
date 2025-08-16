"""Test sensor firmware filtering functionality."""

from unittest.mock import Mock

from custom_components.lambda_heat_pumps.utils import (
    get_compatible_sensors,
    get_firmware_version_int,
)
from custom_components.lambda_heat_pumps.const import (
    HP_SENSOR_TEMPLATES,
    BOIL_SENSOR_TEMPLATES,
    HC_SENSOR_TEMPLATES,
    BUFF_SENSOR_TEMPLATES,
    SOL_SENSOR_TEMPLATES,
    FIRMWARE_VERSION,
)


class TestSensorFirmwareFiltering:
    """Test class for sensor firmware filtering functionality."""

    def test_get_compatible_sensors_basic_functionality(self):
        """Test basic functionality of get_compatible_sensors."""
        # Test sensors with different firmware versions
        test_sensors = {
            "sensor_v1": {
                "name": "Sensor V1",
                "firmware_version": 1,
                "address": 1000,
            },
            "sensor_v2": {
                "name": "Sensor V2",
                "firmware_version": 2,
                "address": 2000,
            },
            "sensor_v3": {
                "name": "Sensor V3",
                "firmware_version": 3,
                "address": 3000,
            },
            "sensor_no_fw": {
                "name": "Sensor No FW",
                "address": 4000,
            },  # No firmware version
        }

        # Test with firmware version 2
        result = get_compatible_sensors(test_sensors, 2)
        
        assert len(result) == 3
        assert "sensor_v1" in result
        assert "sensor_v2" in result
        assert "sensor_no_fw" in result
        assert "sensor_v3" not in result

    def test_get_compatible_sensors_firmware_version_1(self):
        """Test filtering with firmware version 1."""
        test_sensors = {
            "sensor_v1": {"name": "Sensor V1", "firmware_version": 1, "address": 1000},
            "sensor_v2": {"name": "Sensor V2", "firmware_version": 2, "address": 2000},
            "sensor_v3": {"name": "Sensor V3", "firmware_version": 3, "address": 3000},
            "sensor_no_fw": {"name": "Sensor No FW", "address": 4000},
        }

        result = get_compatible_sensors(test_sensors, 1)
        
        assert len(result) == 2
        assert "sensor_v1" in result
        assert "sensor_no_fw" in result
        assert "sensor_v2" not in result
        assert "sensor_v3" not in result

    def test_get_compatible_sensors_firmware_version_3(self):
        """Test filtering with firmware version 3 (should include all)."""
        test_sensors = {
            "sensor_v1": {"name": "Sensor V1", "firmware_version": 1, "address": 1000},
            "sensor_v2": {"name": "Sensor V2", "firmware_version": 2, "address": 2000},
            "sensor_v3": {"name": "Sensor V3", "firmware_version": 3, "address": 3000},
            "sensor_no_fw": {"name": "Sensor No FW", "address": 4000},
        }

        result = get_compatible_sensors(test_sensors, 3)
        
        assert len(result) == 4
        assert "sensor_v1" in result
        assert "sensor_v2" in result
        assert "sensor_v3" in result
        assert "sensor_no_fw" in result

    def test_get_compatible_sensors_float_firmware_versions(self):
        """Test filtering with float firmware versions."""
        test_sensors = {
            "sensor_v1_5": {
                "name": "Sensor V1.5",
                "firmware_version": 1.5,
                "address": 1500,
            },
            "sensor_v2_7": {
                "name": "Sensor V2.7",
                "firmware_version": 2.7,
                "address": 2700,
            },
            "sensor_v3_0": {
                "name": "Sensor V3.0",
                "firmware_version": 3.0,
                "address": 3000,
            },
        }

        # Test with firmware version 2.5
        result = get_compatible_sensors(test_sensors, 2.5)
        
        # Float comparison: 1.5 <= 2.5 (True), 2.7 <= 2.5 (False), 3.0 <= 2.5 (False)
        assert len(result) == 1
        assert "sensor_v1_5" in result
        assert "sensor_v2_7" not in result
        assert "sensor_v3_0" not in result

    def test_get_compatible_sensors_mixed_data_types(self):
        """Test filtering with mixed data types in firmware_version field."""
        test_sensors = {
            "sensor_int": {
                "name": "Sensor Int",
                "firmware_version": 2,
                "address": 2000,
            },
            "sensor_float": {
                "name": "Sensor Float",
                "firmware_version": 2.5,
                "address": 2500,
            },
            "sensor_string": {
                "name": "Sensor String",
                "firmware_version": "2.0",
                "address": 2000,
            },
            "sensor_none": {
                "name": "Sensor None",
                "firmware_version": None,
                "address": 3000,
            },
            "sensor_no_key": {
                "name": "Sensor No Key",
                "address": 4000,
            },
        }

        result = get_compatible_sensors(test_sensors, 2)
        
        # Should include int (2 <= 2), and sensors without valid firmware_version
        # Float 2.5 > 2, so excluded
        assert len(result) == 4
        assert "sensor_int" in result
        assert "sensor_float" not in result  # 2.5 > 2
        # String is not int/float, so included
        assert "sensor_string" in result
        # None is not int/float, so included
        assert "sensor_none" in result
        # No key, so included
        assert "sensor_no_key" in result

    def test_get_compatible_sensors_empty_input(self):
        """Test filtering with empty sensor dictionary."""
        result = get_compatible_sensors({}, 2)
        assert result == {}

    def test_get_compatible_sensors_zero_firmware_version(self):
        """Test filtering with firmware version 0."""
        test_sensors = {
            "sensor_v0": {
                "name": "Sensor V0",
                "firmware_version": 0,
                "address": 0,
            },
            "sensor_v1": {
                "name": "Sensor V1",
                "firmware_version": 1,
                "address": 1000,
            },
            "sensor_no_fw": {
                "name": "Sensor No FW",
                "address": 2000,
            },
        }

        result = get_compatible_sensors(test_sensors, 0)
        
        assert len(result) == 2
        assert "sensor_v0" in result
        assert "sensor_no_fw" in result
        assert "sensor_v1" not in result

    def test_get_compatible_sensors_negative_firmware_version(self):
        """Test filtering with negative firmware version."""
        test_sensors = {
            "sensor_neg": {
                "name": "Sensor Neg",
                "firmware_version": -1,
                "address": -1000,
            },
            "sensor_v0": {
                "name": "Sensor V0",
                "firmware_version": 0,
                "address": 0,
            },
            "sensor_v1": {
                "name": "Sensor V1",
                "firmware_version": 1,
                "address": 1000,
            },
        }

        result = get_compatible_sensors(test_sensors, -1)
        
        assert len(result) == 1
        assert "sensor_neg" in result
        assert "sensor_v0" not in result
        assert "sensor_v1" not in result

    def test_get_compatible_sensors_preserves_sensor_data(self):
        """Test that filtering preserves all sensor data."""
        test_sensors = {
            "sensor_v1": {
                "name": "Test Sensor",
                "firmware_version": 1,
                "address": 1000,
                "unit_of_measurement": "°C",
                "device_class": "temperature",
                "state_class": "measurement",
            }
        }

        result = get_compatible_sensors(test_sensors, 1)
        
        assert "sensor_v1" in result
        assert result["sensor_v1"]["name"] == "Test Sensor"
        assert result["sensor_v1"]["address"] == 1000
        assert result["sensor_v1"]["unit_of_measurement"] == "°C"
        assert result["sensor_v1"]["device_class"] == "temperature"
        assert result["sensor_v1"]["state_class"] == "measurement"

    def test_get_firmware_version_int_from_options(self):
        """Test get_firmware_version_int with firmware version in options."""
        mock_entry = Mock()
        mock_entry.options = {"firmware_version": "V0.0.3-3K"}
        # Should be ignored
        mock_entry.data = {"firmware_version": "V1.0.0"}
        
        result = get_firmware_version_int(mock_entry)
        
        # V0.0.3-3K should map to version 1
        assert result == 1

    def test_get_firmware_version_int_from_data_fallback(self):
        """Test get_firmware_version_int with firmware version in data (fallback)."""
        mock_entry = Mock()
        mock_entry.options = {}  # No options
        mock_entry.data = {"firmware_version": "V0.0.4-3K"}
        
        result = get_firmware_version_int(mock_entry)
        
        # V0.0.4-3K should map to version 2
        assert result == 2

    def test_get_firmware_version_int_default_fallback(self):
        """Test get_firmware_version_int with no firmware version specified."""
        mock_entry = Mock()
        mock_entry.options = {}
        mock_entry.data = {}
        
        result = get_firmware_version_int(mock_entry)
        
        # Should return default version (1)
        assert result == 1

    def test_get_firmware_version_int_unknown_version(self):
        """Test get_firmware_version_int with unknown firmware version."""
        mock_entry = Mock()
        mock_entry.options = {"firmware_version": "UNKNOWN_VERSION"}
        mock_entry.data = {}
        
        result = get_firmware_version_int(mock_entry)
        
        # Unknown version should default to 1
        assert result == 1

    def test_real_sensor_templates_filtering(self):
        """Test filtering with real sensor templates from the codebase."""
        # Test HP sensor templates
        hp_sensors = get_compatible_sensors(HP_SENSOR_TEMPLATES, 1)
        assert isinstance(hp_sensors, dict)
        
        # Test BOIL sensor templates
        boil_sensors = get_compatible_sensors(BOIL_SENSOR_TEMPLATES, 1)
        assert isinstance(boil_sensors, dict)
        
        # Test HC sensor templates
        hc_sensors = get_compatible_sensors(HC_SENSOR_TEMPLATES, 1)
        assert isinstance(hc_sensors, dict)
        
        # Test BUFF sensor templates
        buff_sensors = get_compatible_sensors(BUFF_SENSOR_TEMPLATES, 1)
        assert isinstance(buff_sensors, dict)
        
        # Test SOL sensor templates
        sol_sensors = get_compatible_sensors(SOL_SENSOR_TEMPLATES, 1)
        assert isinstance(sol_sensors, dict)

    def test_firmware_version_mapping_consistency(self):
        """Test that firmware version mapping is consistent."""
        # Test that all known firmware versions map to integers
        for fw_name, fw_version in FIRMWARE_VERSION.items():
            assert isinstance(fw_version, int)
            assert fw_version > 0

    def test_sensor_filtering_edge_cases(self):
        """Test edge cases in sensor filtering."""
        test_sensors = {
            "sensor_exact_match": {"firmware_version": 2, "address": 2000},
            "sensor_just_below": {"firmware_version": 1.999, "address": 1999},
            "sensor_just_above": {"firmware_version": 2.001, "address": 2001},
        }

        # Test exact match
        result = get_compatible_sensors(test_sensors, 2)
        assert "sensor_exact_match" in result
        assert "sensor_just_below" in result
        assert "sensor_just_above" not in result

    def test_sensor_filtering_with_complex_data(self):
        """Test filtering with complex sensor data structures."""
        test_sensors = {
            "complex_sensor": {
                "name": "Complex Sensor",
                "firmware_version": 2,
                "address": 2000,
                "registers": [2000, 2001],
                "scale": 0.1,
                "offset": 0,
                "precision": 1,
                "txt_mapping": {"0": "Off", "1": "On"},
                "unit_of_measurement": "°C",
                "device_class": "temperature",
                "state_class": "measurement",
            }
        }

        result = get_compatible_sensors(test_sensors, 2)
        
        assert "complex_sensor" in result
        sensor = result["complex_sensor"]
        assert sensor["name"] == "Complex Sensor"
        assert sensor["registers"] == [2000, 2001]
        assert sensor["scale"] == 0.1
        assert sensor["txt_mapping"] == {"0": "Off", "1": "On"}
        assert sensor["unit_of_measurement"] == "°C" 