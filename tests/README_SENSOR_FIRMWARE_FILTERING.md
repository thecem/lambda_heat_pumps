# Sensor Firmware Filtering Tests

Diese Dokumentation beschreibt die umfassenden Tests für die Sensor-Filterung nach Firmware-Version in der Lambda Heat Pumps Integration.

## Übersicht

Die Tests in `tests/test_sensor_firmware_filtering.py` überprüfen die Funktionalität der `get_compatible_sensors()` und `get_firmware_version_int()` Funktionen, die für die korrekte Filterung von Sensoren basierend auf der Firmware-Version der Lambda Wärmepumpe verantwortlich sind.

## Test-Klasse: `TestSensorFirmwareFiltering`

### 1. Grundlegende Funktionalität

#### `test_get_compatible_sensors_basic_functionality()`
**Zweck:** Testet die grundlegende Funktionalität der Sensor-Filterung
**Getestet:**
- Filterung von Sensoren mit verschiedenen Firmware-Versionen (1, 2, 3)
- Sensoren ohne Firmware-Version werden immer eingeschlossen
- Korrekte Auswahl bei Firmware-Version 2 (sollte Sensoren mit Version ≤ 2 einschließen)

**Erwartetes Verhalten:**
- 3 Sensoren sollten zurückgegeben werden (Version 1, 2 und ohne Firmware)
- Sensor mit Version 3 sollte ausgeschlossen werden

### 2. Spezifische Firmware-Versionen

#### `test_get_compatible_sensors_firmware_version_1()`
**Zweck:** Testet Filterung mit Firmware-Version 1
**Getestet:**
- Nur Sensoren mit Version ≤ 1 werden eingeschlossen
- Sensoren ohne Firmware-Version werden eingeschlossen

#### `test_get_compatible_sensors_firmware_version_3()`
**Zweck:** Testet Filterung mit Firmware-Version 3 (höchste Version)
**Getestet:**
- Alle Sensoren sollten eingeschlossen werden
- Vollständige Kompatibilität mit allen verfügbaren Sensoren

### 3. Float-Firmware-Versionen

#### `test_get_compatible_sensors_float_firmware_versions()`
**Zweck:** Testet die Behandlung von Dezimal-Firmware-Versionen
**Getestet:**
- Float-Vergleiche (1.5, 2.7, 3.0)
- Präzise mathematische Vergleiche
- Korrekte Ausgrenzung von Sensoren mit höheren Versionen

**Beispiel:**
- Bei Firmware-Version 2.5: Nur Sensor mit Version 1.5 wird eingeschlossen
- Sensoren mit Version 2.7 und 3.0 werden ausgeschlossen

### 4. Gemischte Datentypen

#### `test_get_compatible_sensors_mixed_data_types()`
**Zweck:** Testet die Behandlung verschiedener Datentypen im `firmware_version` Feld
**Getestet:**
- **Integer-Werte:** Korrekte numerische Vergleiche
- **Float-Werte:** Präzise Dezimalvergleiche
- **String-Werte:** Werden als nicht-numerisch behandelt und eingeschlossen
- **None-Werte:** Werden als nicht-numerisch behandelt und eingeschlossen
- **Fehlende Schlüssel:** Sensoren ohne `firmware_version` werden eingeschlossen

### 5. Edge Cases

#### `test_get_compatible_sensors_empty_input()`
**Zweck:** Testet das Verhalten bei leerer Eingabe
**Getestet:**
- Leeres Sensor-Dictionary
- Rückgabe eines leeren Dictionaries

#### `test_get_compatible_sensors_zero_firmware_version()`
**Zweck:** Testet Firmware-Version 0
**Getestet:**
- Nur Sensoren mit Version 0 werden eingeschlossen
- Sensoren ohne Firmware-Version werden eingeschlossen

#### `test_get_compatible_sensors_negative_firmware_version()`
**Zweck:** Testet negative Firmware-Versionen
**Getestet:**
- Nur Sensoren mit negativer Version werden eingeschlossen
- Sehr restriktive Filterung

### 6. Datenintegrität

#### `test_get_compatible_sensors_preserves_sensor_data()`
**Zweck:** Stellt sicher, dass alle Sensor-Daten erhalten bleiben
**Getestet:**
- Vollständige Erhaltung aller Sensor-Eigenschaften
- Keine Datenverluste durch Filterung
- Korrekte Werte für alle Felder (name, address, unit_of_measurement, etc.)

### 7. Firmware-Version-Mapping

#### `test_get_firmware_version_int_from_options()`
**Zweck:** Testet die Konvertierung von String- zu Integer-Firmware-Versionen aus Options
**Getestet:**
- Priorität der Options über Data
- Korrekte Mapping von "V0.0.3-3K" → 1

#### `test_get_firmware_version_int_from_data_fallback()`
**Zweck:** Testet Fallback auf Data wenn keine Options vorhanden
**Getestet:**
- Fallback-Mechanismus
- Korrekte Mapping von "V0.0.4-3K" → 2

#### `test_get_firmware_version_int_default_fallback()`
**Zweck:** Testet Standard-Fallback bei fehlenden Firmware-Informationen
**Getestet:**
- Standardwert 1 bei komplett fehlenden Daten
- Robuste Behandlung von unvollständigen Konfigurationen

#### `test_get_firmware_version_int_unknown_version()`
**Zweck:** Testet Behandlung unbekannter Firmware-Versionen
**Getestet:**
- Fallback auf Standardwert 1
- Robuste Fehlerbehandlung

### 8. Echte Sensor-Templates

#### `test_real_sensor_templates_filtering()`
**Zweck:** Testet mit den tatsächlichen Sensor-Templates aus dem Codebase
**Getestet:**
- HP_SENSOR_TEMPLATES (Wärmepumpen-Sensoren)
- BOIL_SENSOR_TEMPLATES (Kessel-Sensoren)
- HC_SENSOR_TEMPLATES (Heizkreise-Sensoren)
- BUFF_SENSOR_TEMPLATES (Puffer-Sensoren)
- SOL_SENSOR_TEMPLATES (Solar-Sensoren)

**Validierung:**
- Alle Templates werden korrekt gefiltert
- Rückgabe von Dictionary-Objekten
- Keine Runtime-Fehler

### 9. Konsistenz-Prüfungen

#### `test_firmware_version_mapping_consistency()`
**Zweck:** Überprüft die Konsistenz der Firmware-Version-Mappings
**Getestet:**
- Alle Mappings sind Integer-Werte
- Alle Werte sind positiv (> 0)
- Keine ungültigen Datentypen

### 10. Präzise Edge Cases

#### `test_sensor_filtering_edge_cases()`
**Zweck:** Testet sehr präzise Vergleiche
**Getestet:**
- Exakte Matches (2.0 == 2.0)
- Werte knapp unter der Grenze (1.999 < 2.0)
- Werte knapp über der Grenze (2.001 > 2.0)

### 11. Komplexe Datenstrukturen

#### `test_sensor_filtering_with_complex_data()`
**Zweck:** Testet Sensoren mit erweiterten Eigenschaften
**Getestet:**
- Sensoren mit Registern-Arrays
- Skalierungs- und Offset-Werte
- Text-Mappings
- Erweiterte Metadaten (device_class, state_class, etc.)

## Test-Ausführung

### Einzelne Tests ausführen:
```bash
# Virtuelle Umgebung aktivieren
.venv\Scripts\Activate.ps1

# Alle Firmware-Filtering Tests
python -m pytest tests/test_sensor_firmware_filtering.py -v

# Spezifischen Test ausführen
python -m pytest tests/test_sensor_firmware_filtering.py::TestSensorFirmwareFiltering::test_get_compatible_sensors_basic_functionality -v
```

### Test-Coverage:
```bash
python -m pytest tests/test_sensor_firmware_filtering.py --cov=custom_components.lambda_heat_pumps.utils --cov-report=html
```

## Erwartete Ergebnisse

Bei erfolgreicher Ausführung sollten alle 17 Tests durchlaufen:

```
==================== 17 passed, 1 warning in 4.88s =====================
```

## Wichtige Erkenntnisse

1. **Float-Vergleiche:** Die Implementierung führt präzise mathematische Vergleiche durch
2. **Datentyp-Behandlung:** Nicht-numerische Werte werden als kompatibel behandelt
3. **Fallback-Mechanismus:** Robuste Behandlung fehlender Firmware-Informationen
4. **Datenintegrität:** Alle Sensor-Daten bleiben bei der Filterung erhalten
5. **Edge Cases:** Umfassende Behandlung von Grenzfällen

## Integration mit bestehenden Tests

Diese Tests ergänzen die bereits vorhandenen Tests in `tests/test_utils.py`:
- `test_get_compatible_sensors_with_firmware_version()`
- `test_get_compatible_sensors_no_firmware_version()`

Die neuen Tests bieten eine deutlich umfassendere Abdeckung und testen auch Edge Cases, die in den ursprünglichen Tests nicht abgedeckt waren. 