# Zentralisierte Namensgebung für Lambda Heat Pumps Integration

## Übersicht

Dieses Dokument beschreibt die Implementierung einer zentralisierten Namensgebung für die Lambda Heat Pumps Integration. Das Ziel ist es, die derzeit verstreute Namenslogik in verschiedenen Dateien (`sensor.py`, `template_sensor.py`, `climate.py`) zu zentralisieren und konsistent zu machen.

## Problemstellung

### Aktuelle Probleme

1. **Code-Duplikation**: Namenslogik ist in mehreren Dateien implementiert
2. **Inkonsistenz**: Unterschiedliche Implementierungen für Legacy- und Standard-Modus
3. **Wartungsaufwand**: Änderungen müssen an mehreren Stellen vorgenommen werden
4. **Override-Handling**: Sensor-Name-Overrides werden unterschiedlich behandelt

### Betroffene Dateien

- `custom_components/lambda_heat_pumps/sensor.py` (Zeilen 100-150)
- `custom_components/lambda_heat_pumps/template_sensor.py` (Zeilen 70-90)
- `custom_components/lambda_heat_pumps/climate.py` (Zeilen 30-35)
- `custom_components/lambda_heat_pumps/utils.py` (bestehende Funktionen)

## Lösung: Zentralisierte Device-Konfiguration

### Neue Funktionen in `utils.py`

#### 1. `generate_device_config()` - Mit Error-Handling

```python
from typing import Dict, Any, Optional
import logging

_LOGGER = logging.getLogger(__name__)

def generate_device_config(
    device_type: str, 
    count: int, 
    name_prefix: str = "",
    use_legacy_modbus_names: bool = False,
    sensor_overrides: Optional[Dict[str, str]] = None
) -> Dict[int, Dict[str, Any]]:
    """Generate complete device configuration including addresses and naming.
    
    Args:
        device_type: Type of device (hp, boil, buff, sol, hc)
        count: Number of devices
        name_prefix: Name prefix like "eu08l" (used in legacy mode)
        use_legacy_modbus_names: Whether to use legacy naming convention
        sensor_overrides: Dictionary of sensor name overrides from config
        
    Returns:
        dict: Dictionary with device numbers as keys and config dicts as values
        
    Raises:
        ValueError: If device_type is invalid or count is negative
    """
    # Input validation
    valid_device_types = {'hp', 'boil', 'buff', 'sol', 'hc'}
    if device_type not in valid_device_types:
        raise ValueError(
            f"Invalid device_type '{device_type}'. "
            f"Must be one of: {', '.join(valid_device_types)}"
        )
    
    if count < 0:
        raise ValueError(f"Count must be non-negative, got {count}")
    
    if count == 0:
        _LOGGER.debug("Count is 0 for device_type %s, returning empty config", device_type)
        return {}
    
    base_addresses = BASE_ADDRESSES
    start_address = base_addresses.get(device_type, 0)
    
    if start_address == 0:
        _LOGGER.warning("No base address found for device_type %s", device_type)
        return {}
    
    device_config = {}
    
    for i in range(1, count + 1):
        modbus_base = start_address + (i - 1) * 100
        device_prefix = f"{device_type}{i}"
        
        # Generate entity prefix for templates
        if use_legacy_modbus_names:
            entity_prefix = f"{name_prefix}_{device_prefix}"
        else:
            entity_prefix = device_prefix
        
        device_config[i] = {
            "modbus_base": modbus_base,
            "device_prefix": device_prefix,
            "name_prefix": name_prefix,
            "entity_prefix": entity_prefix,
            "naming_mode": "legacy" if use_legacy_modbus_names else "standard",
            "sensor_overrides": sensor_overrides or {}
        }
    
    _LOGGER.debug(
        "Generated device config for %s: %d devices, legacy_mode=%s",
        device_type, count, use_legacy_modbus_names
    )
    
    return device_config
```

#### 2. `generate_sensor_names_from_config()` - Mit Error-Handling

```python
def generate_sensor_names_from_config(
    device_config: Dict[str, Any],
    sensor_name: str,
    sensor_id: str,
    override_name: Optional[str] = None
) -> Dict[str, str]:
    """Generate sensor names using device configuration.
    
    Args:
        device_config: Device configuration from generate_device_config
        sensor_name: Human readable sensor name
        sensor_id: Sensor identifier
        override_name: Optional override name
        
    Returns:
        dict: Contains 'name', 'entity_id', and 'unique_id'
        
    Raises:
        ValueError: If device_config is invalid or required fields are missing
    """
    # Validate device_config structure
    required_fields = {'device_prefix', 'name_prefix', 'naming_mode'}
    missing_fields = required_fields - set(device_config.keys())
    if missing_fields:
        raise ValueError(
            f"Invalid device_config: missing required fields: {missing_fields}"
        )
    
    device_prefix = device_config["device_prefix"]
    name_prefix = device_config["name_prefix"]
    naming_mode = device_config["naming_mode"]
    
    # Validate naming_mode
    if naming_mode not in {'legacy', 'standard'}:
        raise ValueError(f"Invalid naming_mode: {naming_mode}")
    
    # Handle override name
    if override_name and naming_mode == "legacy":
        display_name = override_name
        entity_id = f"sensor.{name_prefix}_{override_name}"
        unique_id = f"{name_prefix}_{override_name}"
    else:
        # Standard display name
        display_name = f"{device_prefix.upper()} {sensor_name}"
        
        # Entity ID logic
        if naming_mode == "legacy":
            entity_id = f"sensor.{name_prefix}_{device_prefix}_{sensor_id}"
            unique_id = f"{name_prefix}_{device_prefix}_{sensor_id}"
        else:
            entity_id = f"sensor.{device_prefix}_{sensor_id}"
            unique_id = f"{device_prefix}_{sensor_id}"
    
    return {
        "name": display_name,
        "entity_id": entity_id,
        "unique_id": unique_id
    }
```

#### 3. `generate_climate_config()` - Mit Error-Handling

```python
def generate_climate_config(
    climate_type: str,
    device_configs: Dict[str, Dict[int, Dict[str, Any]]],
    name_prefix: str = "",
    use_legacy_modbus_names: bool = False
) -> Dict[int, Dict[str, Any]]:
    """Generate climate configuration based on underlying device configs.
    
    Args:
        climate_type: Climate type ("hot_water" or "heating_circuit")
        device_configs: Device configurations from generate_device_config
        name_prefix: Name prefix like "eu08l"
        use_legacy_modbus_names: Whether to use legacy naming convention
        
    Returns:
        dict: Climate configuration for each device
        
    Raises:
        ValueError: If climate_type is invalid or device_configs is malformed
    """
    # Validate climate_type
    valid_climate_types = {'hot_water', 'heating_circuit'}
    if climate_type not in valid_climate_types:
        raise ValueError(
            f"Invalid climate_type '{climate_type}'. "
            f"Must be one of: {', '.join(valid_climate_types)}"
        )
    
    # Map climate types to device types
    climate_to_device = {
        "hot_water": "boil",
        "heating_circuit": "hc"
    }
    
    device_type = climate_to_device.get(climate_type)
    if not device_type or device_type not in device_configs:
        _LOGGER.warning(
            "No device configs found for climate_type %s (device_type: %s)",
            climate_type, device_type
        )
        return {}
    
    climate_config = {}
    
    for idx, device_config in device_configs[device_type].items():
        # Get template info
        from .const import CLIMATE_TEMPLATES
        template = CLIMATE_TEMPLATES.get(climate_type, {})
        template_name = template.get("name", climate_type.replace("_", " ").title())
        
        # Generate climate-specific names
        display_name = f"{template_name} {idx}"
        
        if use_legacy_modbus_names:
            entity_id = f"climate.{name_prefix}_{climate_type}_{idx}"
            unique_id = f"{name_prefix}_{climate_type}_{idx}"
        else:
            entity_id = f"climate.lambda_heat_pumps_{climate_type}_{idx}"
            unique_id = f"lambda_heat_pumps_{climate_type}_{idx}"
        
        climate_config[idx] = {
            "modbus_base": device_config["modbus_base"],
            "device_prefix": device_config["device_prefix"],
            "climate_type": climate_type,
            "template_name": template_name,
            "name": display_name,
            "entity_id": entity_id,
            "unique_id": unique_id,
            "naming_mode": device_config["naming_mode"],
            "template": template
        }
    
    return climate_config
```

### Performance-Optimierung: Caching im Coordinator

#### Erweiterte Coordinator-Klasse

```python
# In coordinator.py
class LambdaDataUpdateCoordinator(DataUpdateCoordinator):
    """Lambda data update coordinator with device config caching."""
    
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)
        self._entry = entry
        self._device_configs_cache: Optional[Dict[str, Dict[int, Dict[str, Any]]]] = None
        self._climate_configs_cache: Optional[Dict[str, Dict[int, Dict[str, Any]]]] = None
        self._cache_valid = False
    
    def _invalidate_cache(self):
        """Invalidate cached configurations."""
        self._device_configs_cache = None
        self._climate_configs_cache = None
        self._cache_valid = False
    
    def get_device_configs(self) -> Dict[str, Dict[int, Dict[str, Any]]]:
        """Get cached device configurations, creating them if necessary."""
        if not self._cache_valid or self._device_configs_cache is None:
            self._generate_device_configs()
        
        return self._device_configs_cache
    
    def get_climate_configs(self) -> Dict[str, Dict[int, Dict[str, Any]]]:
        """Get cached climate configurations, creating them if necessary."""
        if not self._cache_valid or self._climate_configs_cache is None:
            self._generate_climate_configs()
        
        return self._climate_configs_cache
    
    def _generate_device_configs(self):
        """Generate and cache device configurations."""
        num_hps = self._entry.data.get("num_hps", 1)
        num_boil = self._entry.data.get("num_boil", 1)
        num_buff = self._entry.data.get("num_buff", 0)
        num_sol = self._entry.data.get("num_sol", 0)
        num_hc = self._entry.data.get("num_hc", 1)
        
        use_legacy_modbus_names = self._entry.data.get("use_legacy_modbus_names", False)
        name_prefix = self._entry.data.get("name", "").lower().replace(" ", "")
        sensor_overrides = getattr(self, "sensor_overrides", {})
        
        self._device_configs_cache = {
            "hp": generate_device_config("hp", num_hps, name_prefix, use_legacy_modbus_names, sensor_overrides),
            "boil": generate_device_config("boil", num_boil, name_prefix, use_legacy_modbus_names, sensor_overrides),
            "buff": generate_device_config("buff", num_buff, name_prefix, use_legacy_modbus_names, sensor_overrides),
            "sol": generate_device_config("sol", num_sol, name_prefix, use_legacy_modbus_names, sensor_overrides),
            "hc": generate_device_config("hc", num_hc, name_prefix, use_legacy_modbus_names, sensor_overrides),
        }
        self._cache_valid = True
    
    def _generate_climate_configs(self):
        """Generate and cache climate configurations."""
        device_configs = self.get_device_configs()
        use_legacy_modbus_names = self._entry.data.get("use_legacy_modbus_names", False)
        name_prefix = self._entry.data.get("name", "").lower().replace(" ", "")
        
        self._climate_configs_cache = {
            "hot_water": generate_climate_config("hot_water", device_configs, name_prefix, use_legacy_modbus_names),
            "heating_circuit": generate_climate_config("heating_circuit", device_configs, name_prefix, use_legacy_modbus_names)
        }
    
    async def async_config_entry_updated(self, entry: ConfigEntry):
        """Handle config entry updates by invalidating cache."""
        self._invalidate_cache()
        await super().async_config_entry_updated(entry)
```

### Integration mit Home Assistant Core

#### Verwendung von HA-Konventionen

```python
from homeassistant.helpers.entity_registry import async_generate_entity_id
from homeassistant.helpers.device_registry import DeviceInfo

def generate_sensor_names_from_config(
    device_config: Dict[str, Any],
    sensor_name: str,
    sensor_id: str,
    override_name: Optional[str] = None,
    hass: Optional[HomeAssistant] = None
) -> Dict[str, str]:
    """Generate sensor names using device configuration with HA integration."""
    # ... existing validation code ...
    
    # Use HA's entity ID generation for better compatibility
    if hass and naming_mode == "standard":
        # Let HA generate the entity ID to avoid conflicts
        suggested_entity_id = f"{device_prefix}_{sensor_id}"
        entity_id = async_generate_entity_id(
            hass, "sensor", suggested_entity_id, 
            hass.data.get(DOMAIN, {}).keys()
        )
    else:
        # Manual generation for legacy mode
        if naming_mode == "legacy":
            entity_id = f"sensor.{name_prefix}_{device_prefix}_{sensor_id}"
        else:
            entity_id = f"sensor.{device_prefix}_{sensor_id}"
    
    return {
        "name": display_name,
        "entity_id": entity_id,
        "unique_id": unique_id
    }
```

## Code-Änderungen

### 1. Änderungen in `sensor.py` - Mit Caching

#### Imports erweitern:
```python
from .utils import (
    build_device_info, 
    generate_sensor_names_from_config
)
```

#### Sensor-Erstellung umschreiben:
```python
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Lambda Heat Pumps sensors."""
    # ... existing code bis zur Coordinator-Extraktion ...
    
    # Get cached device configurations from coordinator
    device_configs = coordinator.get_device_configs()
    
    for prefix, count, template in TEMPLATES:
        for idx in range(1, count + 1):
            device_config = device_configs[prefix][idx]
            base_address = device_config["modbus_base"]
            
            for sensor_id, sensor_info in template.items():
                address = base_address + sensor_info["relative_address"]
                
                if coordinator.is_register_disabled(address):
                    _LOGGER.debug(
                        "Skipping sensor %s (address %d) because register is disabled",
                        f"{prefix}{idx}_{sensor_id}",
                        address,
                    )
                    continue
                
                # Check for override name
                override_name = None
                if device_config["naming_mode"] == "legacy":
                    override_key = f"{prefix}{idx}_{sensor_id}"
                    override_name = device_config["sensor_overrides"].get(override_key)
                
                # Generate sensor names using device config
                naming = generate_sensor_names_from_config(
                    device_config=device_config,
                    sensor_name=sensor_info['name'],
                    sensor_id=sensor_id,
                    override_name=override_name,
                    hass=hass  # Pass hass for HA integration
                )
                
                # ... rest of sensor creation logic ...
```

### 2. Änderungen in `template_sensor.py` - Mit Caching

```python
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Lambda Template sensors."""
    # ... existing code bis zur Coordinator-Extraktion ...
    
    # Get cached device configurations from coordinator
    device_configs = coordinator.get_device_configs()

    for device_type, count in DEVICE_COUNTS.items():
        for idx in range(1, count + 1):
            device_config = device_configs[device_type][idx]
            
            for sensor_id, sensor_info in CALCULATED_SENSOR_TEMPLATES.items():
                if sensor_info.get("device_type") == device_type:
                    # Generate sensor names using device config
                    naming = generate_sensor_names_from_config(
                        device_config=device_config,
                        sensor_name=sensor_info['name'],
                        sensor_id=sensor_id,
                        hass=hass
                    )
                    
                    # Use entity prefix from device config
                    template_str = sensor_info["template"].format(
                        full_entity_prefix=device_config["entity_prefix"]
                    )
                    
                    # ... rest of template sensor creation logic ...
```

### 3. Änderungen in `climate.py` - Mit Caching

```python
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Lambda Heat Pumps climate entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    # Get cached climate configurations from coordinator
    climate_configs = coordinator.get_climate_configs()
    
    entities = []
    
    # Hot Water (Boiler-based)
    for idx, climate_config in climate_configs["hot_water"].items():
        entities.append(
            LambdaClimateEntity(
                coordinator,
                entry,
                climate_config
            )
        )
    
    # Heating Circuits
    for idx, climate_config in climate_configs["heating_circuit"].items():
        entity_key = f"room_temperature_entity_{idx}"
        if not entry.options.get(entity_key):
            _LOGGER.debug(
                "No room temperature entity configured for heating circuit %s in entry %s, skipping entity creation.",
                idx, entry.entry_id
            )
            continue
        entities.append(
            LambdaClimateEntity(
                coordinator,
                entry,
                climate_config
            )
        )
    
    async_add_entities(entities)
```

## Erweiterte Tests

### Vollständige Test-Suite

```python
import pytest
from unittest.mock import Mock, patch
from .utils import (
    generate_device_config,
    generate_sensor_names_from_config,
    generate_climate_config
)

class TestDeviceConfigGeneration:
    """Test device configuration generation."""
    
    def test_valid_device_types(self):
        """Test all valid device types."""
        valid_types = ['hp', 'boil', 'buff', 'sol', 'hc']
        for device_type in valid_types:
            result = generate_device_config(device_type, 1)
            assert len(result) == 1
            assert 1 in result
            assert result[1]["device_prefix"] == f"{device_type}1"
    
    def test_invalid_device_type(self):
        """Test invalid device type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid device_type"):
            generate_device_config("invalid", 1)
    
    def test_negative_count(self):
        """Test negative count raises ValueError."""
        with pytest.raises(ValueError, match="Count must be non-negative"):
            generate_device_config("hp", -1)
    
    def test_zero_count(self):
        """Test zero count returns empty dict."""
        result = generate_device_config("hp", 0)
        assert result == {}
    
    def test_legacy_mode_configuration(self):
        """Test legacy mode configuration."""
        result = generate_device_config("hp", 2, "eu08l", True)
        assert result[1]["naming_mode"] == "legacy"
        assert result[1]["entity_prefix"] == "eu08l_hp1"
        assert result[2]["entity_prefix"] == "eu08l_hp2"
    
    def test_standard_mode_configuration(self):
        """Test standard mode configuration."""
        result = generate_device_config("hp", 2, "eu08l", False)
        assert result[1]["naming_mode"] == "standard"
        assert result[1]["entity_prefix"] == "hp1"
        assert result[2]["entity_prefix"] == "hp2"
    
    def test_sensor_overrides_integration(self):
        """Test sensor overrides are properly integrated."""
        overrides = {"hp1_test_sensor": "Custom Name"}
        result = generate_device_config("hp", 1, "eu08l", True, overrides)
        assert result[1]["sensor_overrides"] == overrides

class TestSensorNameGeneration:
    """Test sensor name generation."""
    
    def test_standard_mode_names(self):
        """Test standard mode name generation."""
        device_config = {
            "device_prefix": "hp1",
            "name_prefix": "eu08l",
            "naming_mode": "standard"
        }
        result = generate_sensor_names_from_config(
            device_config, "Flow Temperature", "flow_temp"
        )
        assert result["name"] == "HP1 Flow Temperature"
        assert result["entity_id"] == "sensor.hp1_flow_temp"
        assert result["unique_id"] == "hp1_flow_temp"
    
    def test_legacy_mode_names(self):
        """Test legacy mode name generation."""
        device_config = {
            "device_prefix": "hp1",
            "name_prefix": "eu08l",
            "naming_mode": "legacy"
        }
        result = generate_sensor_names_from_config(
            device_config, "Flow Temperature", "flow_temp"
        )
        assert result["name"] == "HP1 Flow Temperature"
        assert result["entity_id"] == "sensor.eu08l_hp1_flow_temp"
        assert result["unique_id"] == "eu08l_hp1_flow_temp"
    
    def test_override_name_handling(self):
        """Test override name handling in legacy mode."""
        device_config = {
            "device_prefix": "hp1",
            "name_prefix": "eu08l",
            "naming_mode": "legacy"
        }
        result = generate_sensor_names_from_config(
            device_config, "Flow Temperature", "flow_temp", "Custom Name"
        )
        assert result["name"] == "Custom Name"
        assert result["entity_id"] == "sensor.eu08l_Custom Name"
        assert result["unique_id"] == "eu08l_Custom Name"
    
    def test_override_name_ignored_in_standard_mode(self):
        """Test override names are ignored in standard mode."""
        device_config = {
            "device_prefix": "hp1",
            "name_prefix": "eu08l",
            "naming_mode": "standard"
        }
        result = generate_sensor_names_from_config(
            device_config, "Flow Temperature", "flow_temp", "Custom Name"
        )
        assert result["name"] == "HP1 Flow Temperature"  # Override ignored
        assert result["entity_id"] == "sensor.hp1_flow_temp"
    
    def test_invalid_device_config(self):
        """Test invalid device config raises ValueError."""
        with pytest.raises(ValueError, match="missing required fields"):
            generate_sensor_names_from_config({}, "Test", "test")
    
    def test_invalid_naming_mode(self):
        """Test invalid naming mode raises ValueError."""
        device_config = {
            "device_prefix": "hp1",
            "name_prefix": "eu08l",
            "naming_mode": "invalid"
        }
        with pytest.raises(ValueError, match="Invalid naming_mode"):
            generate_sensor_names_from_config(device_config, "Test", "test")

class TestClimateConfigGeneration:
    """Test climate configuration generation."""
    
    def test_hot_water_configuration(self):
        """Test hot water climate configuration."""
        device_configs = {
            "boil": {
                1: {
                    "modbus_base": 2000,
                    "device_prefix": "boil1",
                    "naming_mode": "legacy"
                }
            }
        }
        result = generate_climate_config("hot_water", device_configs, "eu08l", True)
        assert len(result) == 1
        assert result[1]["climate_type"] == "hot_water"
        assert result[1]["device_prefix"] == "boil1"
        assert result[1]["entity_id"] == "climate.eu08l_hot_water_1"
    
    def test_heating_circuit_configuration(self):
        """Test heating circuit climate configuration."""
        device_configs = {
            "hc": {
                1: {
                    "modbus_base": 5000,
                    "device_prefix": "hc1",
                    "naming_mode": "standard"
                }
            }
        }
        result = generate_climate_config("heating_circuit", device_configs, "eu08l", False)
        assert len(result) == 1
        assert result[1]["climate_type"] == "heating_circuit"
        assert result[1]["device_prefix"] == "hc1"
        assert result[1]["entity_id"] == "climate.lambda_heat_pumps_heating_circuit_1"
    
    def test_invalid_climate_type(self):
        """Test invalid climate type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid climate_type"):
            generate_climate_config("invalid", {}, "eu08l", False)
    
    def test_missing_device_configs(self):
        """Test missing device configs returns empty dict."""
        result = generate_climate_config("hot_water", {}, "eu08l", False)
        assert result == {}

class TestPerformanceOptimization:
    """Test performance optimization features."""
    
    @patch('custom_components.lambda_heat_pumps.utils.generate_device_config')
    def test_caching_reduces_function_calls(self, mock_generate):
        """Test that caching reduces function calls."""
        mock_generate.return_value = {1: {"test": "data"}}
        
        # First call should invoke the function
        result1 = generate_device_config("hp", 1)
        assert mock_generate.call_count == 1
        
        # Second call should use cache
        result2 = generate_device_config("hp", 1)
        assert mock_generate.call_count == 1  # No additional call
        
        assert result1 == result2

class TestHomeAssistantIntegration:
    """Test Home Assistant integration features."""
    
    def test_entity_id_generation_with_hass(self):
        """Test entity ID generation using HA's async_generate_entity_id."""
        hass = Mock()
        hass.data = {DOMAIN: {}}
        
        device_config = {
            "device_prefix": "hp1",
            "name_prefix": "eu08l",
            "naming_mode": "standard"
        }
        
        with patch('homeassistant.helpers.entity_registry.async_generate_entity_id') as mock_generate:
            mock_generate.return_value = "sensor.hp1_flow_temp_2"
            
            result = generate_sensor_names_from_config(
                device_config, "Flow Temperature", "flow_temp", hass=hass
            )
            
            mock_generate.assert_called_once()
            assert result["entity_id"] == "sensor.hp1_flow_temp_2"
```

## Migrationsstrategie

### Version X.1.0 - Neue Funktionen hinzufügen
- Neue Funktionen werden hinzugefügt, aber nicht verwendet
- Bestehende Funktionen bleiben unverändert
- Tests für neue Funktionen werden hinzugefügt

### Version X.2.0 - Deprecation Warning
```python
import warnings

def generate_base_addresses(device_type: str, count: int) -> dict:
    """Generate base addresses for a given device type and count.
    
    DEPRECATED: This function will be removed in version X.3.0.
    Use generate_device_config() instead.
    """
    warnings.warn(
        "generate_base_addresses is deprecated and will be removed in version X.3.0. "
        "Use generate_device_config() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    # ... existing implementation ...
```

### Version X.3.0 - Entfernung alter Funktionen
- `generate_base_addresses()` wird entfernt
- Alle Plattformen verwenden die neuen Funktionen
- Vollständige Migration abgeschlossen

### Migration-Guide für Benutzer

```markdown
## Migration von Version X.1.0 zu X.3.0

### Für Entwickler:
1. Ersetze `generate_base_addresses()` durch `generate_device_config()`
2. Verwende `generate_sensor_names_from_config()` für Sensor-Namen
3. Verwende `generate_climate_config()` für Climate-Entities
4. Aktualisiere Tests entsprechend

### Für Benutzer:
- Keine Änderungen an Konfigurationen erforderlich
- Alle bestehenden Entity-IDs bleiben unverändert
- Legacy-Modus wird weiterhin unterstützt
```

## Beispiel-Konfiguration

### Eingabe-Parameter
```python
device_type = "hp"
count = 2
name_prefix = "eu08l"
use_legacy_modbus_names = True
sensor_overrides = {
    "hp1_actual_heating_capacity": "Hp_QP_heating",
    "hp2_actual_heating_capacity": "Hp2_QP_heating"
}
```

### Ausgabe von `generate_device_config()`
```python
{
    1: {
        "modbus_base": 1000,
        "device_prefix": "hp1",
        "name_prefix": "eu08l",
        "entity_prefix": "eu08l_hp1",
        "naming_mode": "legacy",
        "sensor_overrides": {
            "hp1_actual_heating_capacity": "Hp_QP_heating",
            "hp2_actual_heating_capacity": "Hp2_QP_heating"
        }
    },
    2: {
        "modbus_base": 1100,
        "device_prefix": "hp2",
        "name_prefix": "eu08l",
        "entity_prefix": "eu08l_hp2",
        "naming_mode": "legacy",
        "sensor_overrides": {
            "hp1_actual_heating_capacity": "Hp_QP_heating",
            "hp2_actual_heating_capacity": "Hp2_QP_heating"
        }
    }
}
```

### Ausgabe von `generate_sensor_names_from_config()`
```python
# Für HP1, Sensor "flow_line_temperature"
{
    "name": "HP1 Flow Line Temperature",
    "entity_id": "sensor.eu08l_hp1_flow_line_temperature",
    "unique_id": "eu08l_hp1_flow_line_temperature"
}

# Für HP1 mit Override
{
    "name": "Hp_QP_heating",
    "entity_id": "sensor.eu08l_Hp_QP_heating",
    "unique_id": "eu08l_Hp_QP_heating"
}
```

## Vorteile der neuen Lösung

1. **Zentralisierung**: Alle Namenslogik ist in `utils.py` zentralisiert
2. **Konsistenz**: Einheitliche Namensgebung über alle Plattformen
3. **Wartbarkeit**: Änderungen müssen nur an einer Stelle gemacht werden
4. **Erweiterbarkeit**: Neue Plattformen können einfach die zentralen Funktionen nutzen
5. **Legacy-Support**: Die Unterscheidung zwischen Legacy- und Standard-Modus wird beibehalten
6. **Override-Support**: Sensor-Name-Overrides werden automatisch berücksichtigt
7. **Template-Support**: Entity-Prefixe für Templates werden automatisch generiert
8. **Rückwärtskompatibilität**: Bestehende Funktionen bleiben erhalten
9. **Error-Handling**: Robuste Validierung und aussagekräftige Fehlermeldungen
10. **Performance**: Caching reduziert wiederholte Berechnungen
11. **HA-Integration**: Verwendung von HA-Konventionen für bessere Kompatibilität
12. **Testbarkeit**: Umfassende Test-Suite für alle Szenarien

## Implementierungsreihenfolge

1. **Schritt 1**: Neue Funktionen in `utils.py` hinzufügen (mit Error-Handling)
2. **Schritt 2**: Coordinator-Klasse um Caching erweitern
3. **Schritt 3**: `template_sensor.py` umschreiben (einfachster Fall)
4. **Schritt 4**: `sensor.py` umschreiben (komplexester Fall)
5. **Schritt 5**: `climate.py` umschreiben
6. **Schritt 6**: Umfassende Tests implementieren
7. **Schritt 7**: HA-Integration hinzufügen
8. **Schritt 8**: Dokumentation aktualisieren
9. **Schritt 9**: Deprecation-Warnings hinzufügen
10. **Schritt 10**: Alte Funktionen entfernen

## Tests

Die bestehenden Tests für `generate_base_addresses()` sollten erweitert werden:

```python
def test_generate_device_config():
    """Test generate_device_config function."""
    result = generate_device_config("hp", 2, "eu08l", True)
    assert len(result) == 2
    assert result[1]["modbus_base"] == 1000
    assert result[1]["device_prefix"] == "hp1"
    assert result[1]["entity_prefix"] == "eu08l_hp1"
    assert result[1]["naming_mode"] == "legacy"

def test_generate_sensor_names_from_config():
    """Test generate_sensor_names_from_config function."""
    device_config = {
        "device_prefix": "hp1",
        "name_prefix": "eu08l",
        "naming_mode": "legacy"
    }
    result = generate_sensor_names_from_config(
        device_config, "Flow Line Temperature", "flow_line_temperature"
    )
    assert result["name"] == "HP1 Flow Line Temperature"
    assert result["entity_id"] == "sensor.eu08l_hp1_flow_line_temperature"
    assert result["unique_id"] == "eu08l_hp1_flow_line_temperature"
```

## Migration

Die Migration kann schrittweise erfolgen, da die alten Funktionen für Rückwärtskompatibilität beibehalten werden. Alle bestehenden Konfigurationen werden weiterhin funktionieren. 