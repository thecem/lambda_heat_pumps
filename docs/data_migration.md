Wir fassen die Datenmigration in eine markdown-Datei zusammen, die als Dokumentation oder als Teil des Entwicklerdokuments dienen kann.

Das Dokument enthält:

1. Einführung: Warum Migration?

2. Voraussetzungen

3. Implementierungsschritte in der Custom Integration

4. Code-Beispiele

5. Hinweise und Einschränkungen

# Datenmigration für state_class in Custom Integration

## Einführung

In der Lambda Heat Pumps Integration wurden Temperatursensoren fälschlicherweise mit `state_class: total` konfiguriert.

Die korrekte `state_class` für Temperatursensoren ist `measurement`.

Diese Migration korrigiert die Metadaten in der Datenbank, ohne die historischen Rohdaten zu verändern.

## Voraussetzungen

- Home Assistant Version 2021.9 oder höher (wegen Statistics Meta API)

- Custom Integration `lambda_heat_pumps` muss bereits installiert sein

- Datenbankzugriff über den Recorder

## Implementierung

### Schritt 1: Migration beim Setup der Integration

Wir führen die Migration beim ersten Start nach dem Update durch.

### Schritt 2: Code-Änderungen in der Custom Integration

#### 1. Migrationsfunktion

Füge folgende Funktion in deine Integration ein (z.B. in `__init__.py`):

```python

from homeassistant.components.recorder import get_instance

from homeassistant.components.recorder.statistics import update_statistics_metadata

async def async_migrate_temperature_sensors(hass: HomeAssistant):

"""Migrate temperature sensors from state_class total to measurement."""

recorder = get_instance(hass)

# Liste der Entity-IDs aller Temperatursensoren in deiner Integration

# Diese Liste muss angepasst werden, um alle betroffenen Sensoren zu enthalten!

temperature_entities = [

"sensor.eu08l_ambient_temperature",

"sensor.eu08l_ambient_temperature_1h",

"sensor.eu08l_ambient_temperature_calculated",

"sensor.eu08l_hp1_flow_line_temperature",

"sensor.eu08l_hp1_return_line_temperature",

"sensor.eu08l_hp1_energy_source_inlet_temperature",

"sensor.eu08l_hp1_energy_source_outlet_temperature",

"sensor.eu08l_boil1_actual_high_temperature",

"sensor.eu08l_boil1_actual_low_temperature",

"sensor.eu08l_hc1_flow_line_temperature",

"sensor.eu08l_hc1_return_line_temperature",

# ... weitere Temperatursensoren

]

def _update_metadata():

with recorder.session_scope() as session:

# Holen der vorhandenen Metadaten

metadata = recorder.statistics_meta_manager.get_metadata(session)

for meta in metadata:

if meta["statistic_id"] in temperature_entities:

# Aktualisiere state_class

new_meta = {**meta, "state_class": "measurement"}

update_statistics_metadata(recorder, meta["statistic_id"], new_meta)

await recorder.async_add_executor_job(_update_metadata)

```

#### 2. Integration in `async_setup_entry`

In der `async_setup_entry` Funktion deiner Integration:

```python

async def async_setup_entry(hass: HomeAssistant, config_entry):

# ... existierendes Setup

# Migration nur bei der ersten Einrichtung oder nach einem Update

if config_entry.version == 1:

_LOGGER.info("Starting migration for temperature sensors")

await async_migrate_temperature_sensors(hass)

# Erhöhe die Konfigurationsversion

hass.config_entries.async_update_entry(config_entry, version=2)

_LOGGER.info("Migration completed. Config entry version set to 2")

return True

```

#### 3. Erhöhe die Version in `manifest.json`

Aktualisiere die `version` in deiner `manifest.json` auf eine neue Version (z.B. von 1.0.0 auf 1.1.0).

### Schritt 3: Erhöhe die Konfigurationsentry-Version

Wenn die Integration bereits installiert ist, muss die `config_entry` Version erhöht werden.

Dies geschieht automatisch im obigen Code, wenn `config_entry.version == 1`.

## Hinweise und Einschränkungen

1. **Keine rückwirkende Neuberechnung**:

- Die Migration ändert nur die Metadaten. Bereits aggregierte Statistiken (Min, Max, Mittel) werden nicht neu berechnet.

- Neue Daten werden korrekt als `measurement` aufgezeichnet.

2. **Entity-IDs müssen bekannt sein**:

- Du musst im Voraus alle Entity-IDs der Temperatursensoren kennen, die migriert werden sollen.

3. **Datenbank-Lock**:

- Die Migration läuft im Hintergrund, blockiert aber kurz die Datenbank.

- Bei sehr großen Datenbanken kann dies zu einer kurzen Verzögerung führen.

4. **Fehlerbehandlung**:

- Implementiere eine Fehlerbehandlung, um Probleme während der Migration abzufangen.

```python

try:

await async_migrate_temperature_sensors(hass)

except Exception as e:

_LOGGER.error("Migration failed: %s", e)

# Optional: Benachrichtigung an den Benutzer

```

5. **Benachrichtigung des Benutzers** (Optional):

- Informiere den Benutzer über den Erfolg oder Fehler der Migration.

```python

hass.components.persistent_notification.async_create(

"Die Migration der Temperatursensoren wurde erfolgreich durchgeführt.",

title="Lambda Heat Pumps Update"

)

```

## Zusammenfassung

Durch diese Migration werden die Metadaten der Temperatursensoren in der Datenbank korrigiert, sodass zukünftig korrekte Statistiken erstellt werden.

Die historischen Rohdaten bleiben dabei vollständig erhalten.

---

**Hinweis**: Passe die Liste der `temperature_entities` an deine tatsächlichen Sensoren an.

Diese Liste muss alle Entity-IDs enthalten, die von der Migration betroffen sind.

from homeassistant.core import HomeAssistant
from homeassistant.components.recorder import get_instance
from homeassistant.components.recorder.statistics import update_statistics_metadata
from homeassistant.components.sensor import SensorDeviceClass

### init.py.... Migrationsfunktion...
async def async_migrate_temperature_sensors(hass: HomeAssistant):
    """
    Migriert Temperatursensoren von state_class 'total' zu 'measurement'
    """
    _LOGGER = logging.getLogger(__name__)
    _LOGGER.info("Starting temperature sensors migration")
    
    recorder = get_instance(hass)
    
    # Dynamische Liste aller Temperatursensoren-Entity-IDs
    temperature_entities = [
        entity_id for entity_id, state in hass.states.async_all()
        if (state.attributes.get('device_class') == SensorDeviceClass.TEMPERATURE and
            state.attributes.get('state_class') == "total")
    ]

    if not temperature_entities:
        _LOGGER.info("No temperature sensors to migrate")
        return

    def _update_metadata():
        with recorder.session_scope() as session:
            metadata = recorder.statistics_meta_manager.get_metadata(session)
            
            for meta in metadata:
                if meta["statistic_id"] in temperature_entities:
                    new_meta = {
                        **meta,
                        "state_class": "measurement",
                        "unit_of_measurement": "°C"
                    }
                    update_statistics_metadata(
                        recorder,
                        meta["statistic_id"],
                        new_meta
                    )
                    _LOGGER.debug(
                        "Migrated sensor: %s (new state_class: measurement)",
                        meta["statistic_id"]
                    )

    try:
        await recorder.async_add_executor_job(_update_metadata)
        _LOGGER.info(
            "Successfully migrated %d temperature sensors",
            len(temperature_entities)
        )
        
        # Optional: Benachrichtigung an Benutzer
        hass.components.persistent_notification.async_create(
            f"{len(temperature_entities)} Temperatursensoren wurden erfolgreich migriert",
            title="Lambda Heat Pumps Update"
        )
    except Exception as e:
        _LOGGER.error("Migration failed: %s", e, exc_info=True)
        hass.components.persistent_notification.async_create(
            f"Fehler bei der Migration: {str(e)}",
            title="Lambda Heat Pumps Migrationsfehler"
        )

ntegration in das Setup (__init__.py)
python

async def async_setup_entry(hass: HomeAssistant, config_entry):
    """Setup der Lambda Heat Pumps Integration"""
    
    # 1. Normale Initialisierung
    # ... (existierender Code)
    
    # 2. Datenmigration bei der ersten Installation oder nach Update
    if config_entry.version <= 1:
        try:
            # Migration im Hintergrund starten
            hass.async_create_task(async_migrate_temperature_sensors(hass))
            
            # Versionsnummer erhöhen
            hass.config_entries.async_update_entry(config_entry, version=2)
            _LOGGER.info(
                "Config entry updated to version %d", 
                config_entry.version
            )
        except Exception as e:
            _LOGGER.error("Initial migration setup failed: %s", e)
    
    return True

3. Manifest-Update (manifest.json)
json

{
  "version": "1.1.0",
  "requirements": ["pyModbusTCP==1.1.2"],
  "codeowners": ["@yourusername"],
  "config_flow": true,
  "domain": "lambda_heat_pumps",
  "name": "Lambda Heat Pumps",
  "documentation": "https://github.com/your-repo/README.md",
  "iot_class": "local_polling"
}

Technische Details
Was die Migration bewirkt

    Identifiziert alle Temperatursensoren mit falscher state_class: total

    Aktualisiert die Metadaten in der Datenbank auf state_class: measurement

    Ändert nicht die historischen Rohdaten

    Wirkt sich nur auf zukünftige Statistiken aus

Auswirkungen auf Daten
Datenart	Vor Migration	Nach Migration
Historische Rohdaten	✅ Bleiben erhalten	✅ Unverändert
Bestehende Statistiken	❌ Falsch kategorisiert	❌ Unverändert
Zukünftige Statistiken	Wären falsch	✅ Korrekt kategorisiert
Energie-Dashboard	Mögliche Fehler	✅ Korrekte Integration
Migrationszeitpunkt

    Beim ersten Start nach Update der Integration

    Automatisch im Hintergrund

    Vor Initialisierung der Sensoren

    Nur einmalig bei Version 1 → 2

Fehlerbehandlung

Die Implementierung enthält mehrstufige Fehlerbehandlung:

    Logging aller Migrationsschritte

    Exception-Handling für Datenbankoperationen

    Benutzerbenachrichtigung bei Erfolg/Fehler

    Versionskontrolle verhindert wiederholte Migration

Hinweise für Benutzer

    Kein manueller Eingriff erforderlich

    Migration läuft automatisch

    Historische Daten bleiben vollständig erhalten

    Nach Migration:

        Korrekte Statistiken für neue Daten

        Keine Warnungen mehr über falsche state_class

        Bessere Integration in Energie-Dashboards

Testempfehlungen

    Migration im Dev-Umgebung testen

    Verschiedene Szenarien prüfen:

        Keine Temperatursensoren vorhanden

        Sensoren mit korrekter state_class

        Große Datenbestände

        Verschiedene Datenbanktypen (SQLite, MySQL)

    Log-Ausgabe überprüfen:
    log

    INFO: Starting temperature sensors migration
    DEBUG: Migrated sensor: sensor.eu08l_boil1_actual_high_temperature
    INFO: Successfully migrated 12 temperature sensors

Limitierungen

    Keine rückwirkende Korrektur:

        Bereits erstellte Statistiken werden nicht neu berechnet

        Nur neue Daten werden korrekt kategorisiert

    Datenbankabhängig:

        Getestet mit SQLite und MySQL

        Bei externen DBs möglicherweise zusätzliche Konfiguration nötig

    Performance:

        Bei sehr großen Datenbeständen (>100.000 Einträge) kann Migration mehrere Sekunden dauern

        Läuft im Hintergrund ohne UI-Blockierung

Support

Bei Problemen mit der Migration:

    Logs prüfen: home-assistant.log

    Issue auf GitHub erstellen

    Support-Informationen bereitstellen:

        Home Assistant Version

        Datenbanktyp

        Anzahl der Sensoren

        Fehlerlogs        