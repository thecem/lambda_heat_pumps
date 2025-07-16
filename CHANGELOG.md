# Changelog

**Deutsche Version siehe unten / German version see below**

## [1.1.0] - 2024-12-19

### Added
- Compatibility with pymodbus >= 3.6.0
- Counters for heat pump cycling by operating mode
- Extended statistics for different operating modes

### Changed
- Updated to new pymodbus API (3.x)
- Removed redundant parameters in `read_holding_registers` calls
- Synchronous `connect()` calls instead of asynchronous
- Code style improvements (flake8-compatible)

### Fixed
- Import errors in all modules fixed
- Whitespace issues resolved
- HACS validation errors corrected
- Manifest keys properly sorted

## [1.0.9] - 2024-12-19

### Added
- PV surplus control for heat pumps
- Modbus register 102 support for E-Manager Actual Power
- Configurable PV sensors (Watt/kW)
- Automatic unit conversion
- Write interval configuration for PV data
- YAML configuration file `lambda_wp_config.yaml` for advanced settings
- Calculated COP sensor based on thermal energy output and power consumption

### Changed
- Improved error handling for Modbus connections
- Extended integration options for PV control

## [1.0.0] - Initial Release

### Added
- First version of Lambda Heat Pumps Integration
- Modbus communication for heat pumps
- Cycle counter detection
- Climate entity for heat pump control

---

# Changelog (Deutsch)

## [1.1.0] - 2024-12-19

### Added
- Kompatibilität mit pymodbus >= 3.6.0
- Zähler für Wärmepumpen-Taktung nach Betriebsart
- Erweiterte Statistiken für verschiedene Betriebsmodi

### Changed
- Aktualisiert auf neue pymodbus API (3.x)
- Entfernt überflüssige Parameter bei `read_holding_registers` Aufrufen
- Synchroner Aufruf von `connect()` statt asynchron
- Code-Style Verbesserungen (flake8-kompatibel)

### Fixed
- Import-Fehler in allen Modulen behoben
- Whitespace-Probleme bereinigt
- HACS-Validierungsfehler korrigiert
- Manifest-Schlüssel korrekt sortiert

## [1.0.9] - 2024-12-19

### Added
- PV-Überschuss-Steuerung für Wärmepumpen
- Modbus-Register 102 Unterstützung für E-Manager Actual Power
- Konfigurierbare PV-Sensoren (Watt/kW)
- Automatische Einheitenkonvertierung
- Schreibintervall-Konfiguration für PV-Daten
- YAML-Konfigurationsdatei `lambda_wp_config.yaml` für erweiterte Einstellungen
- Berechneter COP-Sensor basierend auf thermischer Energieausgabe und Stromverbrauch

### Changed
- Verbesserte Fehlerbehandlung für Modbus-Verbindungen
- Erweiterte Integration-Optionen für PV-Steuerung

## [1.0.0] - Initial Release

### Added
- Erste Version der Lambda Heat Pumps Integration
- Modbus-Kommunikation für Wärmepumpen
- Zyklenzähler-Erfassung
- Climate-Entity für Wärmepumpensteuerung 