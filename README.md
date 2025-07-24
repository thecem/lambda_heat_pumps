# Lambda Heat Pumps Integration

Eine Home Assistant Integration für Lambda Wärmepumpen mit Modbus-Kommunikation.

## 🚀 **Features**

- **Vollständig asynchrone Modbus-Kommunikation** - Keine Konflikte mit anderen Modbus-Integrationen
- **Automatische pymodbus API-Kompatibilität** - Unterstützt Versionen 1.x, 2.x und 3.x
- **Cycling-Counter** - Automatische Zählung der Betriebszyklen
- **Energy-Integration** - Energieverbrauch-Berechnung
- **Climate-Entities** - Temperaturregelung für Warmwasser und Heizkreise
- **Service-API** - Direkter Modbus-Register-Zugriff
- **State-Restoration** - Wiederherstellung der Zählerstände nach Neustart

## 🔧 **Installation**

### HACS (Empfohlen)
1. Fügen Sie dieses Repository zu HACS hinzu
2. Installieren Sie die Integration über HACS
3. Fügen Sie die Integration über die Home Assistant UI hinzu

### Manuelle Installation
1. Kopieren Sie den `custom_components/lambda_heat_pumps` Ordner in Ihren `config/custom_components/` Ordner
2. Starten Sie Home Assistant neu
3. Fügen Sie die Integration über die Home Assistant UI hinzu

## ⚙️ **Konfiguration**

### Grundkonfiguration
```yaml
# configuration.yaml
lambda_heat_pumps:
  host: "192.168.1.100"  # IP-Adresse der Wärmepumpe
  port: 502              # Modbus-Port (Standard: 502)
  name: "eu08l"          # Name-Prefix für Entities
  num_hps: 1             # Anzahl Wärmepumpen
  num_boil: 1            # Anzahl Warmwasser-Speicher
  num_hc: 1              # Anzahl Heizkreise
  use_legacy_modbus_names: false  # Legacy-Namenskonvention
```

### Erweiterte Optionen
```yaml
lambda_heat_pumps:
  # ... Grundkonfiguration ...
  hot_water_min_temp: 30.0    # Minimal-Temperatur Warmwasser
  hot_water_max_temp: 70.0    # Maximal-Temperatur Warmwasser
  heating_circuit_min_temp: 15.0  # Minimal-Temperatur Heizkreis
  heating_circuit_max_temp: 35.0  # Maximal-Temperatur Heizkreis
```

## 📊 **Verfügbare Entities**

### Sensoren
- **Betriebszustand** - Aktueller Betriebsmodus
- **Temperaturen** - Vorlauf, Rücklauf, Außentemperatur
- **Leistung** - Heizleistung, Kälteleistung
- **Cycling-Counter** - Betriebszyklen (total, daily, yesterday)
- **Energy-Counter** - Energieverbrauch (total, daily, yesterday)

### Climate-Entities
- **Warmwasser-Temperatur** - Regelung der Warmwasser-Temperatur
- **Heizkreis-Temperatur** - Regelung der Heizkreis-Temperatur

## 🔌 **Services**

### `lambda_heat_pumps.read_modbus_register`
Liest einen einzelnen Modbus-Register.

```yaml
service: lambda_heat_pumps.read_modbus_register
data:
  address: 1000
  slave_id: 1
```

### `lambda_heat_pumps.write_modbus_register`
Schreibt einen einzelnen Modbus-Register.

```yaml
service: lambda_heat_pumps.write_modbus_register
data:
  address: 1000
  value: 500
  slave_id: 1
```

### `lambda_heat_pumps.write_room_temperatures`
Schreibt Raumtemperaturen für mehrere Heizkreise.

```yaml
service: lambda_heat_pumps.write_room_temperatures
data:
  temperatures:
    - 21.5
    - 20.0
    - 22.0
```

### `lambda_heat_pumps.write_pv_surplus`
Schreibt PV-Überschuss für Wärmepumpen-Boost.

```yaml
service: lambda_heat_pumps.write_pv_surplus
data:
  surplus: 2000  # Watt
```

## 🔄 **Cycling-Counter**

Die Integration zählt automatisch die Betriebszyklen der Wärmepumpe:

- **Heating Cycles** - Heizbetrieb
- **Hot Water Cycles** - Warmwasser-Bereitung
- **Cooling Cycles** - Kühlbetrieb
- **Defrost Cycles** - Abtauzyklen

### Automatische Updates
- **Total Counter** - Wird bei jedem Zyklus-Start inkrementiert
- **Daily Counter** - Wird täglich um Mitternacht zurückgesetzt
- **Yesterday Counter** - Zeigt den Wert des Vortags

## 🛠️ **Technische Details**

### Asynchrone Modbus-Implementierung
Die Integration verwendet vollständig asynchrone Modbus-Clients für:
- **Bessere Performance** - Keine Blocking-Operationen
- **Kompatibilität** - Keine Konflikte mit anderen Modbus-Integrationen
- **Skalierbarkeit** - Unterstützung mehrerer gleichzeitiger Verbindungen

### API-Kompatibilität
Automatische Erkennung und Anpassung an verschiedene `pymodbus` Versionen:
- **pymodbus 1.x**: Keine Slave/Unit-Parameter
- **pymodbus 2.x**: `unit` Parameter
- **pymodbus 3.x**: `slave` Parameter

### State-Restoration
- **Automatische Wiederherstellung** der Zählerstände nach Neustart
- **Persistierung** der Daten in JSON-Dateien
- **Offset-Unterstützung** für manuelle Korrekturen

## 🐛 **Troubleshooting**

### Häufige Probleme

#### Modbus-Verbindung fehlschlägt
- Prüfen Sie die IP-Adresse und den Port
- Stellen Sie sicher, dass die Wärmepumpe erreichbar ist
- Prüfen Sie Firewall-Einstellungen

#### Keine Daten empfangen
- Prüfen Sie die Modbus-Register-Adressen
- Stellen Sie sicher, dass die Slave-ID korrekt ist
- Aktivieren Sie Debug-Logging für detaillierte Informationen

#### Konflikte mit anderen Modbus-Integrationen
- Die Integration ist vollständig asynchron und sollte keine Konflikte verursachen
- Falls Probleme auftreten, prüfen Sie die Modbus-Netzwerk-Konfiguration

### Debug-Logging aktivieren
```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.lambda_heat_pumps: debug
```

## 📝 **Changelog**

Siehe [CHANGELOG.md](CHANGELOG.md) für detaillierte Änderungsprotokolle.

## 🤝 **Beitragen**

Beiträge sind willkommen! Bitte erstellen Sie einen Pull Request oder öffnen Sie ein Issue.

## 📄 **Lizenz**

Dieses Projekt ist unter der MIT-Lizenz lizenziert. Siehe [LICENSE](LICENSE) für Details.

## 🙏 **Danksagungen**

- Home Assistant Community für die großartige Plattform
- pymodbus-Entwickler für die Modbus-Bibliothek
- Lambda für die Wärmepumpen-Technologie
