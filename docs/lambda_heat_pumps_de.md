# Lambda Wärmepumpen Integration für Home Assistant

Die Lambda Wärmepumpen Integration ist eine benutzerdefinierte Komponente für Home Assistant, die eine Verbindung zu Lambda Wärmepumpen über das Modbus TCP/RTU-Protokoll herstellt. Diese Dokumentation beschreibt den Aufbau und die Funktionsweise der Integration.

## Inhaltsverzeichnis

1. [Aufbau der Integration](#aufbau-der-integration)
2. [Typen von Sensoren](#typen-von-sensoren)
3. [Sensor-Initialisierung](#sensor-initialisierung)
4. [Sensor-Abruf](#sensor-abruf)
5. [Konfiguration](#konfiguration)
6. [Funktionsübersicht](#funktionsübersicht)
7. [Modbus-Register-Services](#modbus-register-services)
8. [Dynamische Entity-Erstellung](#dynamische-entity-erstellung)
9. [Template-basierte Climate-Entities](#template-basierte-climate-entities)

## Aufbau der Integration

Die Integration besteht aus folgenden Hauptkomponenten:

- **__init__.py**: Haupteinstiegspunkt der Integration, registriert die Komponente bei Home Assistant
- **config_flow.py**: Benutzeroberfläche für die Konfiguration der Integration
- **const.py**: Konstanten und Konfigurationswerte, einschließlich Sensortypen und Register-Adressen
- **coordinator.py**: Datenkoordinator, der den Datenaustausch mit der Wärmepumpe verwaltet
- **sensor.py**: Implementierung der Sensoren für verschiedene Wärmepumpen-Parameter
- **climate.py**: Implementierung der Klima-Entitäten für Heizung und Warmwasser
- **services.py**: Servicefunktionen, z.B. für den Raumtemperatur-Abruf
- **utils.py**: Hilfsfunktionen für die gesamte Integration

Die Integration unterstützt verschiedene Geräte:
- Bis zu 3 Wärmepumpen (Heat Pumps)
- Bis zu 5 Warmwasserspeicher (Boiler)
- Bis zu 12 Heizkreise (Heating Circuits)
- Bis zu 5 Pufferspeicher (Buffer)
- Bis zu 2 Solaranlagen (Solar)

## Typen von Sensoren

Die Integration unterstützt verschiedene Sensortypen, die in `const.py` definiert sind:

### Allgemeine Sensoren (SENSOR_TYPES)
- Umgebungstemperatur
- Fehler-Nummern
- Betriebszustände
- E-Manager-Werte (Leistungsaufnahme, Sollwerte)

### Wärmepumpen-Sensoren (HP_SENSOR_TEMPLATES)
- Vorlauf- und Rücklauftemperaturen
- Volumenstrom
- Energiequellen-Temperaturen
- Kompressorleistung
- COP (Coefficient of Performance)
- Leistungsaufnahme
- Energieverbrauch

### Warmwasserspeicher-Sensoren (BOIL_SENSOR_TEMPLATES)
- Temperaturen (oben/unten)
- Betriebszustände
- Zirkulation

### Heizkreis-Sensoren (HC_SENSOR_TEMPLATES)
- Vorlauf- und Rücklauftemperaturen
- Raumtemperaturen
- Betriebsmodi
- Sollwerte

### Pufferspeicher-Sensoren (BUFFER_SENSOR_TEMPLATES)
- Temperaturen (oben/unten)
- Betriebszustände
- Anforderungstypen

### Solar-Sensoren (SOLAR_SENSOR_TEMPLATES)
- Kollektortemperaturen
- Speichertemperaturen
- Leistung und Energieertrag

## Sensor-Initialisierung

Die Sensoren werden beim Start der Integration in `sensor.py` initialisiert:

1. Der Datenkoordinator wird geladen
2. Die konfigurierte Firmware-Version wird bestimmt
3. Sensoren werden basierend auf ihrer Kompatibilität mit der Firmware gefiltert
4. Für jede Sensor-Kategorie werden entsprechende Objekte erstellt und registriert
5. Jeder Sensor erhält eine eindeutige ID und wird mit dem Datenkoordinator verbunden

Beispiel aus `sensor.py`:
```python
entities = []
name_prefix = entry.data.get("name", "lambda_wp").lower().replace(" ", "")
prefix = f"{name_prefix}_"

compatible_static_sensors = get_compatible_sensors(SENSOR_TYPES, fw_version)
for sensor_id, sensor_config in compatible_static_sensors.items():
    # Prüfung auf deaktivierte Register
    if coordinator.is_register_disabled(sensor_config["address"]):
        continue
    
    # Entitäten erstellen und hinzufügen
    entities.append(
        LambdaSensor(
            coordinator=coordinator,
            config_entry=entry,
            sensor_id=sensor_id,
            sensor_config=sensor_config_with_name,
            unique_id=f"{entry.entry_id}_{sensor_id}",
        )
    )
```

## Sensor-Abruf

Der Datenabruf erfolgt über den `LambdaDataUpdateCoordinator` in `coordinator.py`:

1. Eine Modbus-TCP/RTU-Verbindung wird zur Wärmepumpe hergestellt
2. Die Register werden entsprechend der Konfiguration abgefragt
3. Die Daten werden verarbeitet und in ein strukturiertes Format umgewandelt
4. Die Sensoren werden mit den neuen Daten aktualisiert

Der Abruf erfolgt regelmäßig nach dem konfigurierten Intervall (Standard: 30 Sekunden).

```python
async def _async_update_data(self):
    """Fetch data from Lambda device."""
    from pymodbus.client import ModbusTcpClient
    
    # Verbindung aufbauen
    if not self.client:
        self.client = ModbusTcpClient(self.host, port=self.port)
        if not await self.hass.async_add_executor_job(self.client.connect):
            raise ConnectionError("Could not connect to Modbus TCP")
    
    # Daten abrufen (Statische Sensoren, HP, Boiler, HC, etc.)
    try:
        data = {}
        # 1. Statische Sensoren abfragen
        for sensor_id, sensor_config in compatible_static_sensors.items():
            if self.is_register_disabled(sensor_config["address"]):
                continue
                
            result = await self.hass.async_add_executor_job(
                self.client.read_holding_registers,
                sensor_config["address"],
                count,
                self.slave_id,
            )
            
            # Daten verarbeiten und speichern
            # ...
    except Exception as ex:
        _LOGGER.error("Exception during data update: %s", ex)
    
    return data
```

## Konfiguration

Die Konfiguration erfolgt über die Home Assistant Benutzeroberfläche mit dem `config_flow.py`:

### Grundeinstellungen
- **Name**: Name der Installation
- **Host**: IP-Adresse oder Hostname der Wärmepumpe
- **Port**: Modbus-TCP-Port (Standard: 502)
- **Slave-ID**: Modbus-Slave-ID (Standard: 1)
- **Firmware-Version**: Firmware der Wärmepumpe (bestimmt verfügbare Sensoren)

### Geräteanzahl
- Anzahl der Wärmepumpen (1-3)
- Anzahl der Warmwasserspeicher (0-5)
- Anzahl der Heizkreise (0-12)
- Anzahl der Pufferspeicher (0-5)
- Anzahl der Solaranlagen (0-2)

### Temperatureinstellungen
- Warmwasser-Temperaturbereich (Min/Max)
- Heizkreis-Temperaturbereich (Min/Max)
- Temperaturschrittweite für Heizkreise

### Raumtemperatursteuerung
- Option zur Nutzung externer Temperatursensoren für Heizkreise

## Funktionsübersicht

### __init__.py
- **async_setup**: Initialisiert die Integration in Home Assistant
- **async_setup_entry**: Richtet eine konfigurierte Integration ein
- **async_unload_entry**: Entlädt eine Integration
- **async_reload_entry**: Lädt eine Integration neu nach Konfigurationsänderungen

### config_flow.py
- **LambdaConfigFlow**: Konfigurationsfluss für die Ersteinrichtung
- **LambdaOptionsFlow**: Konfigurationsfluss für die Optionen (z.B. Temperatureinstellungen)
- **async_step_user**: Erster Schritt der Konfiguration
- **async_step_init**: Verwaltung der Optionen
- **async_step_room_sensor**: Konfiguration von Raumtemperatursensoren

### coordinator.py
- **LambdaDataUpdateCoordinator**: Koordiniert Datenabrufe von der Wärmepumpe
- **async_init**: Initialisiert den Koordinator
- **_async_update_data**: Ruft Daten von der Wärmepumpe ab
- **is_register_disabled**: Prüft, ob ein Register deaktiviert ist

### sensor.py
- **async_setup_entry**: Richtet Sensoren basierend auf der Konfiguration ein
- **LambdaSensor**: Sensorklasse für Lambda-Wärmepumpen-Daten

### climate.py
- **async_setup_entry**: Richtet Klima-Entitäten ein
- **LambdaClimateBoiler**: Klasse für Warmwasserspeicher als Klima-Entität
- **LambdaClimateHC**: Klasse für Heizkreise als Klima-Entität

### services.py
- **async_setup_services**: Registriert Services für die Integration
- **async_update_room_temperature**: Service zum Aktualisieren der Raumtemperatur

### utils.py
- **get_compatible_sensors**: Filtert Sensoren nach Firmware-Kompatibilität
- **build_device_info**: Erstellt Geräteinformationen für das HA-Geräteregister
- **load_disabled_registers**: Lädt deaktivierte Register aus YAML-Datei
- **is_register_disabled**: Prüft, ob ein Register deaktiviert ist

## Firmware-Filterung

Die Integration unterstützt verschiedene Firmware-Versionen und filtert verfügbare Sensoren entsprechend:

```python
def get_compatible_sensors(sensor_templates: dict, fw_version: int) -> dict:
    """Return only sensors compatible with the given firmware version."""
    return {
        k: v
        for k, v in sensor_templates.items()
        if v.get("firmware_version", 1) <= fw_version
    }
```

Jeder Sensor hat ein `firmware_version`-Attribut, das die Mindestversion angibt, ab der der Sensor verfügbar ist.

## Modbus-Register-Services

Die Integration stellt zwei Home Assistant-Services für den direkten Zugriff auf Modbus-Register bereit:
- `lambda_heat_pumps.read_modbus_register`: Liest einen beliebigen Modbus-Registerwert aus.
- `lambda_heat_pumps.write_modbus_register`: Schreibt einen Wert in ein beliebiges Modbus-Register.

Diese Services können über die Entwicklerwerkzeuge genutzt werden. Die Registeradressen werden dynamisch berechnet und müssen entsprechend der Modbus-Dokumentation angegeben werden.

## Dynamische Entity-Erstellung

- Heizkreis-Klima-Entitäten werden nur erstellt, wenn für den jeweiligen Heizkreis ein Raumthermostat-Sensor in den Integrationsoptionen konfiguriert ist.
- Boiler- und andere Geräte-Entitäten werden entsprechend der konfigurierten Geräteanzahl erstellt.

## Template-basierte Climate-Entities

- Alle Climate-Entities (Boiler, Heizkreis) sind jetzt zentral in `const.py` als Templates definiert.
- Dadurch können Eigenschaften zentral gepflegt und erweitert werden.
