# Sensor Migration Fix - Lösung für doppelte Sensoren

## Problem

Beim Update der Integration wurden Sensoren neu angelegt, weil sich die `unique_id`-Generierung geändert hatte. Home Assistant identifiziert Entitäten anhand der `unique_id`, und wenn sich diese ändert, denkt HA, es sind komplett neue Geräte. Die alten Entitäten bleiben erhalten, neue werden mit "_2" Suffix erstellt.

## Ursache

- Home Assistant identifiziert Entitäten anhand von `unique_id`
- Nach dem Update hatten alle Sensoren neue `unique_id`-Werte
- HA dachte, es sind komplett neue Geräte
- Die alten Entitäten blieben erhalten, neue wurden mit "_2" Suffix erstellt

## Lösung

### 1. Anpassung der `generate_sensor_names` Funktion

Die `generate_sensor_names` Funktion in `utils.py` wurde angepasst, um die `unique_id`-Generierung an die alte Logik anzupassen:

```python
def generate_sensor_names(
    device_prefix: str,
    sensor_name: str,
    sensor_id: str,
    name_prefix: str,
    use_legacy_modbus_names: bool
) -> dict:
    """Generate consistent sensor names, entity IDs, and unique IDs."""
    
    # Display name logic - identical to sensor.py
    if device_prefix == sensor_id:
        display_name = sensor_name
    else:
        display_name = f"{device_prefix.upper()} {sensor_name}"

    # Always use lowercase for name_prefix to unify entity_id generation
    name_prefix_lc = name_prefix.lower() if name_prefix else ""

    # Entity ID und unique_id wie in der alten Version generieren
    if use_legacy_modbus_names:
        if device_prefix == sensor_id:
            entity_id = f"sensor.{name_prefix_lc}_{sensor_id}"
            unique_id = f"{name_prefix_lc}_{sensor_id}"
        else:
            entity_id = f"sensor.{name_prefix_lc}_{device_prefix}_{sensor_id}"
            unique_id = f"{name_prefix_lc}_{device_prefix}_{sensor_id}"
    else:
        if device_prefix == sensor_id:
            entity_id = f"sensor.{sensor_id}"
            unique_id = f"{sensor_id}"
        else:
            entity_id = f"sensor.{device_prefix}_{sensor_id}"
            unique_id = f"{device_prefix}_{sensor_id}"

    return {
        "name": display_name,
        "entity_id": entity_id,
        "unique_id": unique_id
    }
```

### 2. Migration bestehender Entitäten

In `sensor.py` wurde eine Migration bestehender Entitäten hinzugefügt:

```python
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Lambda Heat Pumps sensors."""
    _LOGGER.debug("Setting up Lambda sensors for entry %s", entry.entry_id)

    # Migration bestehender Entitäten - entferne doppelte Sensoren mit "_2" Suffix
    entity_registry = async_get_entity_registry(hass)
    registry_entries = entity_registry.entities.get_entries_for_config_entry_id(entry.entry_id)
    
    for registry_entry in registry_entries:
        if "_2" in registry_entry.entity_id:
            _LOGGER.info(
                "Removing duplicate entity with '_2' suffix: %s",
                registry_entry.entity_id
            )
            entity_registry.async_remove(registry_entry.entity_id)

    # ... restlicher Code
```

### 3. Anpassung der LambdaSensor-Klasse

Die `LambdaSensor`-Klasse wurde angepasst, um die `unique_id`-Logik zu korrigieren:

```python
class LambdaSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, ...):
        # ...
        self._attr_unique_id = unique_id  # Immer die generierte ID verwenden
        # ...
```

## Vorteile der Lösung

1. **Konsistente unique_id**: Zwischen alten und neuen Versionen
2. **Migration bestehender Entitäten**: Entfernt doppelte "_2"-Sensoren
3. **Keine neuen Duplikate**: Bei zukünftigen Updates
4. **Historische Daten bleiben erhalten**: Sensoren werden nicht neu erkannt
5. **Rückwärtskompatibilität**: Funktioniert mit bestehenden Installationen

## Implementierte Dateien

- `custom_components/lambda_heat_pumps/utils.py` - Angepasste `generate_sensor_names` Funktion
- `custom_components/lambda_heat_pumps/sensor.py` - Migration bestehender Entitäten und angepasste `LambdaSensor`-Klasse

## Ergebnis

Nach der Implementierung dieser Lösung:
- Bestehende Sensoren behalten ihre `unique_id`
- Doppelte "_2"-Sensoren werden automatisch entfernt
- Historische Daten bleiben erhalten
- Zukünftige Updates erzeugen keine neuen Duplikate

Die Lösung stellt sicher, dass die Sensoren nicht neu erkannt werden und die historischen Daten erhalten bleiben. 