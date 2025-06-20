# Lambda Heat Pumps Integration für Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![maintainer](https://img.shields.io/badge/maintainer-%40GuidoJeuken--6512-blue.svg)](https://github.com/GuidoJeuken-6512)
[![version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/GuidoJeuken-6512/lambda_wp_hacs)
[![license](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Eine benutzerdefinierte Home Assistant Integration für Lambda Wärmepumpen über Modbus/TCP Protokoll.

## 📋 Inhaltsverzeichnis

- [Überblick](#überblick)
- [Features](#features)
- [Installation](#installation)
- [Konfiguration](#konfiguration)
- [Verwendung](#verwendung)
- [Troubleshooting](#troubleshooting)
- [Entwicklung](#entwicklung)
- [Lizenz](#lizenz)

## 🔍 Überblick

Diese Integration ermöglicht die vollständige Einbindung von Lambda Wärmepumpen in Home Assistant. Sie liest Sensordaten aus und ermöglicht die Steuerung von Klima-Entitäten über das Modbus/TCP Protokoll.

### Unterstützte Geräte

- **Wärmepumpen**: 1-3 Geräte
- **Boiler**: 0-5 Geräte  
- **Heizkreise**: 0-12 Kreise
- **Pufferspeicher**: 0-5 Speicher
- **Solarmodule**: 0-2 Module

### Firmware-Versionen

- V0.0.3-3K
- V0.0.4-3K
- V0.0.5-3K
- V0.0.6-3K
- V0.0.7-3K

## ✨ Features

### 🔧 Kernfunktionen
- **Vollständige Modbus/TCP Integration** für Lambda Wärmepumpen
- **Dynamische Sensor-Erkennung** basierend auf Firmware-Version
- **Konfigurierbare Geräteanzahl** für alle Komponenten
- **Raumthermostat-Steuerung** mit externen Temperatursensoren
- **Zentrale Firmware-Filterung** aller Sensoren und Entitäten

### 🌡️ Temperatursteuerung
- **Warmwasser-Steuerung** mit konfigurierbaren Temperaturbereichen
- **Heizkreis-Steuerung** mit individuellen Einstellungen
- **Externe Temperatursensoren** für jeden Heizkreis
- **Automatische Modbus-Schreibvorgänge** für Raumthermostate

### 📊 Monitoring & Daten
- **Umfassende Sensordaten**: Temperaturen, Zustände, Energieverbrauch
- **Echtzeit-Updates** mit konfigurierbarem Intervall
- **Debug-Logging** für Entwickler und Troubleshooting
- **Historische Daten** für Trend-Analysen

### ⚙️ Konfiguration
- **Vollständige UI-Integration** über Home Assistant Einstellungen
- **Dynamische Options-Dialoge** für alle Einstellungen
- **Legacy-Modus** für Kompatibilität mit bestehenden Setups
- **Deaktivierung problematischer Register** über YAML-Konfiguration

## 🚀 Installation

### Voraussetzungen

- Home Assistant 2024.4.4 oder höher
- HACS (Home Assistant Community Store)
- Modbus/TCP-fähige Lambda Wärmepumpe

### HACS Installation (Empfohlen)

1. **HACS installieren** (falls noch nicht geschehen):
   ```bash
   # Über Home Assistant Supervisor → Add-on Store → HACS
   ```

2. **Repository hinzufügen**:
   - Öffnen Sie HACS → Integrations
   - Klicken Sie auf "⋮" → "Custom repositories"
   - Fügen Sie hinzu: `GuidoJeuken-6512/lambda_wp_hacs`
   - Kategorie: Integration

3. **Integration installieren**:
   - Suchen Sie nach "Lambda Heat Pumps"
   - Klicken Sie auf "Download"
   - Starten Sie Home Assistant neu

### Manuelle Installation

1. **Repository klonen**:
   ```bash
   cd /config/custom_components
   git clone https://github.com/GuidoJeuken-6512/lambda_wp_hacs.git lambda_heat_pumps
   ```

2. **Home Assistant neu starten**

## ⚙️ Konfiguration

### Erste Einrichtung

1. **Integration hinzufügen**:
   - `Einstellungen` → `Geräte & Dienste` → `Integration hinzufügen`
   - Suchen Sie nach "Lambda Heat Pumps"

2. **Grundkonfiguration**:
   ```yaml
   Name: "Meine Lambda WP"
   Host: "192.168.1.100"  # IP-Adresse Ihrer Wärmepumpe
   Port: 5020             # Standard Modbus-Port
   Slave ID: 1            # Modbus Slave-ID
   Firmware Version: "V0.0.3-3K"
   ```

3. **Geräteanzahl konfigurieren**:
   - Wärmepumpen: 1-3
   - Boiler: 0-5
   - Heizkreise: 0-12
   - Pufferspeicher: 0-5
   - Solarmodule: 0-2

### Erweiterte Einstellungen

#### Raumthermostat-Steuerung
- Aktivieren Sie "Room thermostat control"
- Wählen Sie externe Temperatursensoren für jeden Heizkreis
- Die Integration schreibt automatisch die Werte in die Modbus-Register

#### Legacy-Modus
- Aktivieren Sie "Use legacy Modbus names" für Kompatibilität
- Wichtig für bestehende Setups mit historischen Daten

#### Temperaturbereiche
- Warmwasser: 40-60°C (konfigurierbar)
- Heizkreise: 15-35°C (konfigurierbar)
- Schrittweite: 0.5°C (konfigurierbar)

### YAML-Konfiguration

Die Integration erstellt automatisch eine `lambda_wp_config.yaml` Datei:

```yaml
# Lambda WP configuration
# Deaktivierung problematischer Register
disabled_registers:
  - 2004  # Beispiel: boil1_actual_circulation_temp

# Sensor-Namen überschreiben (nur im Legacy-Modus)
sensors_names_override:
  - id: actual_heating_capacity
    override_name: Hp_QP_heating
```

## 📱 Verwendung

### Automatisierungen

```yaml
# Beispiel: Warmwasser-Temperatur basierend auf Tageszeit
automation:
  - alias: "Warmwasser Nachtmodus"
    trigger:
      platform: time
      at: "22:00:00"
    action:
      service: climate.set_temperature
      target:
        entity_id: climate.lambda_wp_hot_water_1
      data:
        temperature: 45
```

### Services

```yaml
# Manueller Service-Aufruf für Raumthermostat
service: lambda_heat_pumps.write_room_temperature
data:
  heating_circuit: 1
  temperature: 22.5
```

### Lovelace Dashboard

```yaml
# Beispiel-Card für Wärmepumpe
type: vertical-stack
cards:
  - type: entities
    title: Lambda Wärmepumpe
    entities:
      - entity: sensor.lambda_wp_hp1_flow_line_temperature
      - entity: sensor.lambda_wp_hp1_state
      - entity: climate.lambda_wp_hot_water_1
      - entity: climate.lambda_wp_heating_circuit_1
```

## 🔧 Troubleshooting

### Häufige Probleme

#### Verbindungsfehler
```yaml
# Prüfen Sie:
- IP-Adresse und Port der Wärmepumpe
- Netzwerkverbindung
- Firewall-Einstellungen
- Modbus Slave-ID
```

#### Fehlende Sensoren
```yaml
# Lösung:
1. Firmware-Version in den Optionen prüfen
2. Register in lambda_wp_config.yaml deaktivieren
3. Integration neu laden
```

#### Debug-Logging aktivieren

```yaml
# In configuration.yaml
logger:
  default: info
  logs:
    custom_components.lambda_heat_pumps: debug
```

### Log-Analyse

Suchen Sie nach diesen Log-Einträgen:
- `Modbus error for ... (address: 1234)` → Register deaktivieren
- `Failed to connect` → Netzwerk/Modbus-Konfiguration prüfen
- `Firmware version mismatch` → Firmware-Version anpassen

## 🛠️ Entwicklung

### Projektstruktur

```
lambda_heat_pumps/
├── __init__.py          # Hauptintegration
├── config_flow.py       # Konfigurations-UI
├── const.py            # Konstanten und Sensor-Definitionen
├── coordinator.py      # Datenkoordination
├── sensor.py          # Sensor-Entitäten
├── climate.py         # Klima-Entitäten
├── services.py        # Service-Funktionen
├── utils.py           # Hilfsfunktionen
├── const_mapping.py   # Zustands-Mappings
├── translations/      # Übersetzungen
└── manifest.json      # HACS-Manifest
```

### Modbus-Test-Tools

Für Entwicklung und Testing steht ein separates Repository zur Verfügung:

**GitHub:** [modbus_tools](https://github.com/GuidoJeuken-6512/modbus_tools)

Enthält:
- Modbus TCP Server zum Mocken der Wärmepumpe
- Grafischer Modbus TCP Client für Debugging

### Beitragen

1. Fork des Repositories
2. Feature-Branch erstellen
3. Änderungen committen
4. Pull Request erstellen

## 📄 Lizenz

Diese Software wird unter der MIT-Lizenz veröffentlicht. Siehe [LICENSE](LICENSE) für Details.

## ⚠️ Haftungsausschluss

Die Nutzung dieser Software erfolgt auf eigene Gefahr. Es wird keine Haftung für Schäden, Datenverluste oder sonstige Folgen übernommen, die durch die Verwendung der Software entstehen.

---

## 🌍 International

### English

This integration provides full Lambda heat pump integration for Home Assistant via Modbus/TCP protocol. For English documentation, please refer to the [English README](README_EN.md).

### Support

- **GitHub Issues:** [Report a Bug](https://github.com/GuidoJeuken-6512/lambda_wp_hacs/issues)
- **Community:** [Home Assistant Community](https://community.home-assistant.io/)
- **Documentation:** [Detailed Guide](https://homeassistant.com.de/homeassistant/lambda-waermepumpe-integration-fuer-home-assistant/)

---

**Entwickelt mit ❤️ für die Home Assistant Community**
