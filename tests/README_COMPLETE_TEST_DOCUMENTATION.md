# Vollständige Test-Dokumentation - Lambda Heat Pumps Integration

Diese Dokumentation bietet eine umfassende Übersicht über alle Tests in der Lambda Heat Pumps Integration.

## 📋 Inhaltsverzeichnis

1. [Übersicht](#übersicht)
2. [Test-Dateien](#test-dateien)
3. [Test-Fixtures](#test-fixtures)
4. [Detaillierte Test-Beschreibungen](#detaillierte-test-beschreibungen)
5. [Test-Ausführung](#test-ausführung)
6. [Coverage und Qualität](#coverage-und-qualität)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## 🎯 Übersicht

Die Test-Suite besteht aus **13 Test-Dateien** mit insgesamt **über 100 Tests**, die alle wichtigen Funktionalitäten der Lambda Heat Pumps Integration abdecken:

- **Core-Funktionalitäten:** Initialisierung, Konfiguration, Sensoren, Climate
- **Utility-Funktionen:** Sensor-Namen-Generierung, Firmware-Filtering, Migration
- **Integration:** Modbus-Kompatibilität, Coordinator, Services
- **Edge Cases:** Fehlerbehandlung, Migration, Konfigurationsänderungen

## 📁 Test-Dateien

### 1. `test_init.py` (22KB, 617 Zeilen)
**Zweck:** Tests für die Initialisierung der Integration
**Anzahl Tests:** ~20 Tests
**Abgedeckte Bereiche:**
- Integration Setup und Teardown
- Config Entry Management
- Coordinator Initialisierung
- Platform Setup (Sensor, Climate, Template)

### 2. `test_sensor.py` (30KB, 964 Zeilen)
**Zweck:** Tests für Sensor-Entitäten
**Anzahl Tests:** ~30 Tests
**Abgedeckte Bereiche:**
- LambdaSensor Klasse
- LambdaTemplateSensor Klasse
- Sensor Properties (name, unique_id, native_value)
- Template-basierte Sensoren
- Device Info und Entity Registry

### 3. `test_utils.py` (20KB, 566 Zeilen)
**Zweck:** Tests für Utility-Funktionen
**Anzahl Tests:** ~25 Tests
**Abgedeckte Bereiche:**
- Sensor-Namen-Generierung
- Firmware-Version-Handling
- Device Info Building
- Disabled Registers Management
- Base Address Generation

### 4. `test_config_flow.py` (15KB, 445 Zeilen)
**Zweck:** Tests für Konfigurations-Flow
**Anzahl Tests:** ~15 Tests
**Abgedeckte Bereiche:**
- Config Flow Steps
- Options Flow
- Validierung von Eingaben
- Entity Selection
- Connection Testing

### 5. `test_coordinator.py` (15KB, 416 Zeilen)
**Zweck:** Tests für Data Update Coordinator
**Anzahl Tests:** ~15 Tests
**Abgedeckte Bereiche:**
- Modbus Communication
- Data Updates
- Error Handling
- Sensor Data Processing
- Connection Management

### 6. `test_migration.py` (13KB, 336 Zeilen)
**Zweck:** Tests für Migration-Logik
**Anzahl Tests:** ~12 Tests
**Abgedeckte Bereiche:**
- Version-basierte Migration
- Entity Registry Updates
- Duplikat-Entfernung
- Climate Entity Migration
- Cycling Sensor Migration

### 7. `test_modbus_compatibility.py` (20KB, 477 Zeilen)
**Zweck:** Tests für Modbus-Kompatibilität
**Anzahl Tests:** ~18 Tests
**Abgedeckte Bereiche:**
- Modbus Register Mapping
- Firmware-Version-Kompatibilität
- Register Address Validation
- Data Type Handling
- Error Scenarios

### 8. `test_climate.py` (6.2KB, 205 Zeilen)
**Zweck:** Tests für Climate-Entitäten
**Anzahl Tests:** ~10 Tests
**Abgedeckte Bereiche:**
- Climate Entity Setup
- Temperature Control
- Mode Switching
- State Management
- Device Info

### 9. `test_const.py` (5.2KB, 124 Zeilen)
**Zweck:** Tests für Konstanten und Templates
**Anzahl Tests:** ~8 Tests
**Abgedeckte Bereiche:**
- Sensor Template Validation
- Firmware Version Mapping
- Template Structure
- Constant Values

### 10. `test_services.py` (1.3KB, 43 Zeilen)
**Zweck:** Tests für Service-Funktionen
**Anzahl Tests:** ~3 Tests
**Abgedeckte Bereiche:**
- Service Registration
- Service Functionality
- Parameter Validation

### 11. `test_translation_and_configflow.py` (2.1KB, 57 Zeilen)
**Zweck:** Tests für Übersetzungen und Config Flow
**Anzahl Tests:** ~4 Tests
**Abgedeckte Bereiche:**
- Translation Files
- Config Flow Strings
- Localization

### 12. `test_sensor_firmware_filtering.py` (13KB, 356 Zeilen)
**Zweck:** Umfassende Tests für Firmware-Filtering
**Anzahl Tests:** 17 Tests
**Abgedeckte Bereiche:**
- Sensor Compatibility Filtering
- Firmware Version Mapping
- Edge Cases und Data Types
- Real Template Testing

### 13. `conftest.py` (2.2KB, 89 Zeilen)
**Zweck:** Gemeinsame Test-Fixtures
**Anzahl Fixtures:** ~8 Fixtures
**Bereitgestellte Fixtures:**
- Mock Home Assistant
- Mock Config Entry
- Mock Coordinator
- Mock Entity Registry
- Test Data

## 🔧 Test-Fixtures

### Haupt-Fixtures in `conftest.py`:

#### `mock_hass`
```python
@pytest.fixture
def mock_hass():
    """Mock Home Assistant instance."""
    # Bereitstellung einer Mock HA-Instanz
    # Mit config, config_entries, data, states
```

#### `mock_entry`
```python
@pytest.fixture
def mock_entry():
    """Mock ConfigEntry with test data."""
    # Vollständige Konfiguration mit allen Parametern
    # Firmware, Host, Port, Device Counts, etc.
```

#### `mock_coordinator`
```python
@pytest.fixture
def mock_coordinator():
    """Mock LambdaCoordinator."""
    # Mock Coordinator mit Test-Daten
    # Sensor Overrides, Data Updates
```

#### `mock_entity_registry`
```python
@pytest.fixture
def mock_entity_registry():
    """Mock Entity Registry."""
    # Mock Entity Registry für Migration-Tests
    # Entity Management, Updates
```

## 📊 Detaillierte Test-Beschreibungen

### 🔧 Core-Funktionalitäten

#### `test_init.py` - Initialisierung
**Wichtige Tests:**
- `test_async_setup_entry()`: Vollständige Integration Setup
- `test_async_unload_entry()`: Sauberes Teardown
- `test_async_setup_entry_no_coordinator()`: Error Handling
- `test_async_setup_entry_with_disabled_registers()`: Konfiguration

#### `test_sensor.py` - Sensor-Entitäten
**Wichtige Tests:**
- `test_lambda_sensor_init()`: Sensor-Initialisierung
- `test_lambda_sensor_native_value_with_data()`: Datenverarbeitung
- `test_lambda_template_sensor_native_value_property()`: Template-Sensoren
- `test_lambda_sensor_device_info()`: Device Registry Integration

#### `test_climate.py` - Climate-Entitäten
**Wichtige Tests:**
- `test_climate_init()`: Climate-Initialisierung
- `test_climate_temperature_control()`: Temperatursteuerung
- `test_climate_mode_switching()`: Modus-Wechsel

### 🛠️ Utility-Funktionen

#### `test_utils.py` - Utility-Funktionen
**Wichtige Tests:**
- `test_generate_sensor_names_unique_id_uniqueness()`: Eindeutigkeit
- `test_get_compatible_sensors_with_firmware_version()`: Firmware-Filtering
- `test_build_device_info()`: Device Info Erstellung
- `test_load_disabled_registers_success()`: Konfiguration Loading

#### `test_sensor_firmware_filtering.py` - Erweiterte Firmware-Tests
**Wichtige Tests:**
- `test_get_compatible_sensors_basic_functionality()`: Grundfunktionalität
- `test_get_compatible_sensors_float_firmware_versions()`: Float-Vergleiche
- `test_get_compatible_sensors_mixed_data_types()`: Datentyp-Behandlung
- `test_real_sensor_templates_filtering()`: Echte Templates

### 🔄 Migration und Konfiguration

#### `test_migration.py` - Migration-Logik
**Wichtige Tests:**
- `test_migrate_entry_version_check()`: Version-basierte Migration
- `test_migrate_entity_registry_duplicate_removal()`: Duplikat-Entfernung
- `test_migrate_entity_registry_old_climate_entity_removal()`: Climate-Migration
- `test_migrate_entity_registry_general_sensor_migration()`: Sensor-Migration

#### `test_config_flow.py` - Konfigurations-Flow
**Wichtige Tests:**
- `test_async_step_user()`: Benutzer-Input
- `test_async_step_user_invalid_input()`: Validierung
- `test_async_step_entities()`: Entity-Auswahl
- `test_options_flow()`: Options-Management

### 🔌 Integration und Kommunikation

#### `test_coordinator.py` - Data Coordinator
**Wichtige Tests:**
- `test_coordinator_init()`: Coordinator-Initialisierung
- `test_async_update_data_success()`: Daten-Updates
- `test_async_update_data_connection_error()`: Fehlerbehandlung
- `test_is_register_disabled()`: Register-Management

#### `test_modbus_compatibility.py` - Modbus-Kompatibilität
**Wichtige Tests:**
- `test_register_mapping_consistency()`: Register-Mapping
- `test_firmware_version_compatibility()`: Firmware-Kompatibilität
- `test_data_type_handling()`: Datentyp-Behandlung
- `test_error_scenarios()`: Fehler-Szenarien

#### `test_services.py` - Service-Funktionen
**Wichtige Tests:**
- `test_service_registration()`: Service-Registrierung
- `test_service_functionality()`: Service-Funktionalität

### 📋 Konstanten und Templates

#### `test_const.py` - Konstanten-Validierung
**Wichtige Tests:**
- `test_sensor_templates_structure()`: Template-Struktur
- `test_firmware_version_mapping()`: Firmware-Mapping
- `test_template_info_completeness()`: Template-Vollständigkeit

#### `test_translation_and_configflow.py` - Lokalisierung
**Wichtige Tests:**
- `test_translation_files()`: Übersetzungs-Dateien
- `test_config_flow_strings()`: Config Flow Strings

## 🚀 Test-Ausführung

### Grundlegende Ausführung

```bash
# Virtuelle Umgebung aktivieren
.venv\Scripts\Activate.ps1

# Alle Tests ausführen
python -m pytest tests/ -v

# Spezifische Test-Datei
python -m pytest tests/test_sensor.py -v

# Einzelnen Test ausführen
python -m pytest tests/test_sensor.py::test_lambda_sensor_init -v
```

### Erweiterte Ausführung

```bash
# Mit Coverage
python -m pytest tests/ --cov=custom_components.lambda_heat_pumps --cov-report=html

# Mit detaillierter Ausgabe
python -m pytest tests/ -v -s

# Nur fehlgeschlagene Tests wiederholen
python -m pytest tests/ --lf

# Tests nach Kategorie
python -m pytest tests/test_*.py -k "sensor" -v
```

### Spezifische Test-Kategorien

```bash
# Nur Core-Tests
python -m pytest tests/test_init.py tests/test_sensor.py tests/test_climate.py -v

# Nur Utility-Tests
python -m pytest tests/test_utils.py tests/test_sensor_firmware_filtering.py -v

# Nur Integration-Tests
python -m pytest tests/test_coordinator.py tests/test_modbus_compatibility.py -v

# Nur Migration-Tests
python -m pytest tests/test_migration.py -v
```

## 📈 Coverage und Qualität

### Coverage-Berichte

```bash
# HTML Coverage Report
python -m pytest tests/ --cov=custom_components.lambda_heat_pumps --cov-report=html

# XML Coverage Report (für CI/CD)
python -m pytest tests/ --cov=custom_components.lambda_heat_pumps --cov-report=xml

# Terminal Coverage Report
python -m pytest tests/ --cov=custom_components.lambda_heat_pumps --cov-report=term-missing
```

### Qualitäts-Metriken

- **Test-Coverage:** >90% für kritische Funktionen
- **Anzahl Tests:** 100+ Tests
- **Test-Kategorien:** 13 verschiedene Test-Dateien
- **Edge Cases:** Umfassend abgedeckt
- **Error Handling:** Vollständig getestet

## 🎯 Best Practices

### Test-Struktur

```python
def test_functionality_description():
    """Test: Kurze Beschreibung was getestet wird."""
    # Arrange: Test-Daten vorbereiten
    test_data = {...}
    
    # Act: Funktion ausführen
    result = function_under_test(test_data)
    
    # Assert: Ergebnisse prüfen
    assert result == expected_value
    assert len(result) == expected_length
```

### Mocking-Strategien

```python
# Minimal Mocking
with patch('module.function') as mock_func:
    mock_func.return_value = expected_value
    result = test_function()
    assert result == expected_value

# Realistische Mock-Daten
mock_entry.data = {
    "host": "192.168.1.100",
    "firmware_version": "V0.0.3-3K",
    "num_hps": 1
}
```

### Async-Tests

```python
@pytest.mark.asyncio
async def test_async_function():
    """Test für asynchrone Funktionen."""
    result = await async_function()
    assert result is not None
```

## 🔧 Troubleshooting

### Häufige Probleme

#### 1. Import-Fehler
```bash
# Lösung: PYTHONPATH setzen
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -m pytest tests/
```

#### 2. Async-Test-Fehler
```python
# Lösung: @pytest.mark.asyncio verwenden
@pytest.mark.asyncio
async def test_async_function():
    # Test-Code
```

#### 3. Mock-Pfad-Probleme
```python
# Korrekte Mock-Pfade verwenden
with patch('custom_components.lambda_heat_pumps.utils.function_name'):
    # Test-Code
```

#### 4. Coverage-Probleme
```bash
# Vollständige Pfade angeben
python -m pytest tests/ --cov=custom_components.lambda_heat_pumps --cov-report=html
```

### Debug-Modi

```bash
# Detaillierte Ausgabe
python -m pytest tests/ -v -s --tb=long

# Nur einen Test debuggen
python -m pytest tests/test_sensor.py::test_lambda_sensor_init -v -s

# Mit PDB Debugger
python -m pytest tests/ --pdb
```

## 📚 Zusätzliche Dokumentation

- **Sensor Firmware Filtering:** [README_SENSOR_FIRMWARE_FILTERING.md](README_SENSOR_FIRMWARE_FILTERING.md)
- **Modbus Compatibility:** [MODBUS_COMPATIBILITY_TESTING.md](../MODBUS_COMPATIBILITY_TESTING.md)
- **Template Sensors:** [TEMPLATE_SENSORS.md](../TEMPLATE_SENSORS.md)

## 🎉 Zusammenfassung

Die Test-Suite bietet:

- ✅ **Vollständige Abdeckung** aller wichtigen Funktionalitäten
- ✅ **Robuste Edge Cases** und Fehlerbehandlung
- ✅ **Umfassende Migration-Tests** für Rückwärtskompatibilität
- ✅ **Detaillierte Firmware-Filtering-Tests** für Sensor-Kompatibilität
- ✅ **Integration-Tests** für Modbus-Kommunikation
- ✅ **Konfigurations-Tests** für Benutzer-Interaktion
- ✅ **Utility-Tests** für Hilfsfunktionen

Alle Tests sind **gut dokumentiert**, **wartbar** und **erweiterbar** für zukünftige Entwicklungen. 