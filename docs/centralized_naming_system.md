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

#### 1. `generate_device_config()`

```python
def generate_device_config(
    device_type: str, 
    count: int, 
    name_prefix: str = "",
    use_legacy_modbus_names: bool = False,
    sensor_overrides: dict = None
) -> dict:
    """Generate complete device configuration including addresses and naming.
    
    Args:
        device_type: Type of device (hp, boil, buff, sol, hc)
        count: Number of devices
        name_prefix: Name prefix like "eu08l" (used in legacy mode)
        use_legacy_modbus_names: Whether to use legacy naming convention
        sensor_overrides: Dictionary of sensor name overrides from config
        
    Returns:
        dict: Dictionary with device numbers as keys and config dicts as values
        Each config dict contains:
        - modbus_base: Base Modbus address
        - device_prefix: Device prefix like "hp1", "boil1"
        - name_prefix: Name prefix for legacy mode
        - entity_prefix: Entity prefix for templates
        - naming_mode: "legacy" or "standard"
        - sensor_overrides: Override names from lambda_wp_config.yaml
    """
    base_addresses = BASE_ADDRESSES
    start_address = base_addresses.get(device_type, 0)
    
    if start_address == 0:
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
    
    return device_config
```

#### 2. `generate_sensor_names_from_config()`

```python
def generate_sensor_names_from_config(
    device_config: dict,
    sensor_name: str,
    sensor_id: str,
    override_name: str = None
) -> dict:
    """Generate sensor names using device configuration.
    
    Args:
        device_config: Device configuration from generate_device_config
        sensor_name: Human readable sensor name
        sensor_id: Sensor identifier
        override_name: Optional override name
        
    Returns:
        dict: Contains 'name', 'entity_id', and 'unique_id'
    """
    device_prefix = device_config["device_prefix"]
    name_prefix = device_config["name_prefix"]
    naming_mode = device_config["naming_mode"]
    
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

#### 3. `generate_climate_config()`

```python
def generate_climate_config(
    climate_type: str,
    device_configs: dict,
    name_prefix: str = "",
    use_legacy_modbus_names: bool = False
) -> dict:
    """Generate climate configuration based on underlying device configs.
    
    Args:
        climate_type: Climate type ("hot_water" or "heating_circuit")
        device_configs: Device configurations from generate_device_config
        name_prefix: Name prefix like "eu08l"
        use_legacy_modbus_names: Whether to use legacy naming convention
        
    Returns:
        dict: Climate configuration for each device
    """
    # Map climate types to device types
    climate_to_device = {
        "hot_water": "boil",
        "heating_circuit": "hc"
    }
    
    device_type = climate_to_device.get(climate_type)
    if not device_type or device_type not in device_configs:
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

#### 4. Backward Compatibility

```python
# Keep existing function for backward compatibility
def generate_base_addresses(device_type: str, count: int) -> dict:
    """Generate base addresses for a given device type and count.
    
    Args:
        device_type: Type of device (hp, boil, buff, sol, hc)
        count: Number of devices

    Returns:
        dict: Dictionary with device numbers as keys
        and base addresses as values
    """
    base_addresses = BASE_ADDRESSES
    start_address = base_addresses.get(device_type, 0)
    if start_address == 0:
        return {}

    return {i: start_address + (i - 1) * 100 for i in range(1, count + 1)}
```

## Code-Änderungen

### 1. Änderungen in `sensor.py`

#### Imports erweitern:
```python
from .utils import (
    build_device_info, 
    generate_device_config,
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
    # ... existing code bis zur Device-Count-Extraktion ...
    
    # Get sensor overrides from coordinator
    sensor_overrides = getattr(coordinator, "sensor_overrides", {})
    
    # Generate device configurations
    device_configs = {
        "hp": generate_device_config("hp", num_hps, name_prefix, use_legacy_modbus_names, sensor_overrides),
        "boil": generate_device_config("boil", num_boil, name_prefix, use_legacy_modbus_names, sensor_overrides),
        "buff": generate_device_config("buff", num_buff, name_prefix, use_legacy_modbus_names, sensor_overrides),
        "sol": generate_device_config("sol", num_sol, name_prefix, use_legacy_modbus_names, sensor_overrides),
        "hc": generate_device_config("hc", num_hc, name_prefix, use_legacy_modbus_names, sensor_overrides),
    }

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
                if use_legacy_modbus_names:
                    override_key = f"{prefix}{idx}_{sensor_id}"
                    override_name = sensor_overrides.get(override_key)
                
                # Generate sensor names using device config
                naming = generate_sensor_names_from_config(
                    device_config=device_config,
                    sensor_name=sensor_info['name'],
                    sensor_id=sensor_id,
                    override_name=override_name
                )
                
                # ... rest of sensor creation logic using naming dict ...
                sensors.append(
                    LambdaSensor(
                        coordinator=coordinator,
                        entry=entry,
                        sensor_id=naming["unique_id"].replace("sensor.", ""),
                        name=naming["name"],
                        unit=sensor_info.get("unit", ""),
                        address=address,
                        scale=sensor_info.get("scale", 1.0),
                        state_class=sensor_info.get("state_class", ""),
                        device_class=device_class,
                        relative_address=sensor_info.get("relative_address", 0),
                        data_type=sensor_info.get("data_type", None),
                        device_type=device_type,
                        txt_mapping=sensor_info.get("txt_mapping", False),
                        precision=sensor_info.get("precision", None),
                        entity_id=naming["entity_id"],
                        unique_id=naming["unique_id"],
                    )
                )
```

### 2. Änderungen in `template_sensor.py`

#### Imports erweitern:
```python
from .utils import (
    build_device_info, 
    generate_device_config,
    generate_sensor_names_from_config
)
```

#### Template-Sensor-Erstellung umschreiben:
```python
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Lambda Template sensors."""
    # ... existing code bis zur Device-Count-Extraktion ...
    
    # Generate device configurations
    device_configs = {
        "hp": generate_device_config("hp", num_hps, name_prefix, use_legacy_modbus_names),
        "boil": generate_device_config("boil", num_boil, name_prefix, use_legacy_modbus_names),
        "buff": generate_device_config("buff", num_buff, name_prefix, use_legacy_modbus_names),
        "sol": generate_device_config("sol", num_sol, name_prefix, use_legacy_modbus_names),
        "hc": generate_device_config("hc", num_hc, name_prefix, use_legacy_modbus_names),
    }

    for device_type, count in DEVICE_COUNTS.items():
        for idx in range(1, count + 1):
            device_config = device_configs[device_type][idx]
            
            for sensor_id, sensor_info in CALCULATED_SENSOR_TEMPLATES.items():
                if sensor_info.get("device_type") == device_type:
                    # Generate sensor names using device config
                    naming = generate_sensor_names_from_config(
                        device_config=device_config,
                        sensor_name=sensor_info['name'],
                        sensor_id=sensor_id
                    )
                    
                    # Use entity prefix from device config
                    template_str = sensor_info["template"].format(
                        full_entity_prefix=device_config["entity_prefix"]
                    )
                    
                    template_sensors.append(
                        LambdaTemplateSensor(
                            coordinator=coordinator,
                            entry=entry,
                            sensor_id=f"{device_config['device_prefix']}_{sensor_id}",
                            name=naming["name"],
                            unit=sensor_info.get("unit", ""),
                            state_class=sensor_info.get("state_class", ""),
                            device_class=sensor_info.get("device_class"),
                            device_type=device_type.upper(),
                            precision=sensor_info.get("precision"),
                            entity_id=naming["entity_id"],
                            unique_id=naming["unique_id"],
                            template_str=template_str,
                        )
                    )
```

### 3. Änderungen in `climate.py`

#### Imports erweitern:
```python
from .utils import (
    generate_device_config,
    generate_climate_config,
    build_device_info
)
```

#### Climate-Entity-Klasse umschreiben:
```python
class LambdaClimateEntity(CoordinatorEntity, ClimateEntity):
    """Template-basierte Lambda Climate Entity."""

    _attr_should_poll = False
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE

    def __init__(self, coordinator, entry, climate_config):
        super().__init__(coordinator)
        self._entry = entry
        self._climate_config = climate_config
        
        # Verwende Konfiguration für Namen und IDs
        self._attr_name = climate_config["name"]
        self._attr_unique_id = climate_config["unique_id"]
        self.entity_id = climate_config["entity_id"]
        
        # Verwende Template für andere Eigenschaften
        template = climate_config["template"]
        self._attr_min_temp = 40 if climate_config["climate_type"] == "hot_water" else 20
        self._attr_max_temp = 60 if climate_config["climate_type"] == "hot_water" else 45
        self._attr_target_temperature_step = template.get("precision", 0.5)
        self._attr_temperature_unit = template.get("unit", "°C")
        self._attr_hvac_modes = [HVACMode.HEAT]
        self._attr_hvac_mode = HVACMode.HEAT

    @property
    def current_temperature(self):
        key = (
            f"{self._climate_config['device_prefix']}_actual_high_temperature"
            if self._climate_config["climate_type"] == "hot_water"
            else f"{self._climate_config['device_prefix']}_room_device_temperature"
        )
        return self.coordinator.data.get(key)

    @property
    def target_temperature(self):
        key = (
            f"{self._climate_config['device_prefix']}_target_high_temperature"
            if self._climate_config["climate_type"] == "hot_water"
            else f"{self._climate_config['device_prefix']}_target_room_temperature"
        )
        return self.coordinator.data.get(key)

    async def async_set_temperature(self, **kwargs):
        temperature = kwargs.get("temperature")
        if temperature is None:
            return
        reg_addr = self._climate_config["modbus_base"] + self._climate_config["template"]["relative_set_address"]
        scale = self._climate_config["template"]["scale"]
        raw_value = int(temperature / scale)
        
        # ... rest of existing method ...
```

#### Setup-Funktion umschreiben:
```python
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Lambda Heat Pumps climate entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    num_boil = entry.data.get("num_boil", 1)
    num_hc = entry.data.get("num_hc", 1)
    
    # Get naming configuration
    use_legacy_modbus_names = entry.data.get("use_legacy_modbus_names", False)
    name_prefix = entry.data.get("name", "").lower().replace(" ", "")
    
    # Generate device configurations
    device_configs = {
        "boil": generate_device_config("boil", num_boil, name_prefix, use_legacy_modbus_names),
        "hc": generate_device_config("hc", num_hc, name_prefix, use_legacy_modbus_names)
    }
    
    # Generate climate configurations
    hot_water_configs = generate_climate_config("hot_water", device_configs, name_prefix, use_legacy_modbus_names)
    heating_circuit_configs = generate_climate_config("heating_circuit", device_configs, name_prefix, use_legacy_modbus_names)
    
    entities = []
    
    # Hot Water (Boiler-based)
    for idx, climate_config in hot_water_configs.items():
        entities.append(
            LambdaClimateEntity(
                coordinator,
                entry,
                climate_config
            )
        )
    
    # Heating Circuits
    for idx, climate_config in heating_circuit_configs.items():
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

## Implementierungsreihenfolge

1. **Schritt 1**: Neue Funktionen in `utils.py` hinzufügen
2. **Schritt 2**: `template_sensor.py` umschreiben (einfachster Fall)
3. **Schritt 3**: `sensor.py` umschreiben (komplexester Fall)
4. **Schritt 4**: `climate.py` umschreiben
5. **Schritt 5**: Tests aktualisieren
6. **Schritt 6**: Dokumentation aktualisieren

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