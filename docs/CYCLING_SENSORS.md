# Lambda Heat Pumps: Cycling Sensoren (Total, Daily, Yesterday)

## Übersicht
Die Cycling-Sensoren sind eine umfassende Lösung zur Verfolgung von Betriebsmodus-Wechseln der Lambda Wärmepumpen. Sie umfassen **Total-Sensoren** (Gesamtanzahl), **Daily-Sensoren** (tägliche Werte) und **Yesterday-Sensoren** (Referenzwerte für Daily-Berechnung). Die Flankenerkennung erfolgt zentral im Coordinator für maximale Robustheit und Performance.

## Architektur

### 1. Sensor-Typen

#### Total Cycling Sensoren (echte Entities)
- **Zweck**: Zählen die Gesamtanzahl der Cycling-Ereignisse seit Installation
- **Typ**: Echte Python-Entities (`LambdaCyclingSensor`)
- **Persistenz**: Werte werden direkt in den Entities gespeichert
- **Update**: Bei jeder Flankenerkennung durch `increment_cycling_counter`
- **Beispiele**: 
  - `sensor.eu08l_hp1_heating_cycling_total`
  - `sensor.eu08l_hp1_hot_water_cycling_total`
  - `sensor.eu08l_hp1_cooling_cycling_total`
  - `sensor.eu08l_hp1_defrost_cycling_total`

#### Yesterday Cycling Sensoren (echte Entities)
- **Zweck**: Speichern die Total-Werte von gestern für Daily-Berechnung
- **Typ**: Echte Python-Entities (`LambdaYesterdaySensor`)
- **Update**: Täglich um Mitternacht automatisch aktualisiert
- **Beispiele**:
  - `sensor.eu08l_hp1_heating_cycling_yesterday`
  - `sensor.eu08l_hp1_hot_water_cycling_yesterday`
  - `sensor.eu08l_hp1_cooling_cycling_yesterday`
  - `sensor.eu08l_hp1_defrost_cycling_yesterday`

#### Daily Cycling Sensoren (Template-Sensoren)
- **Zweck**: Berechnen die täglichen Cycling-Werte
- **Typ**: Template-Sensoren (`LambdaTemplateSensor`)
- **Formel**: `Total - Yesterday`
- **Update**: Automatisch bei Änderungen der Total- oder Yesterday-Sensoren
- **Beispiele**:
  - `sensor.eu08l_hp1_heating_cycling_daily`
  - `sensor.eu08l_hp1_hot_water_cycling_daily`
  - `sensor.eu08l_hp1_cooling_cycling_daily`
  - `sensor.eu08l_hp1_defrost_cycling_daily`

## 2. Flankenerkennung

### 2.1. Was ist eine Flanke?
Eine Flanke ist der Übergang eines Sensors von einem Zustand in einen anderen. Für die Cycling-Zählung interessiert uns die **positive Flanke**: Der Wechsel von "nicht aktiv" auf "aktiv" für einen bestimmten Betriebsmodus.

### 2.2. Implementierung im Coordinator
Die Flankenerkennung erfolgt zentral im `LambdaDataUpdateCoordinator` in `coordinator.py`:

```python
# Betriebsmodi-Mapping
MODES = {
    "heating": 1,      # CH (Central Heating)
    "hot_water": 2,    # DHW (Domestic Hot Water)
    "cooling": 3,      # CC (Cooling)
    "defrost": 5,      # DEFROST
}

# Flankenerkennung für jeden Modus und jede HP
for mode, mode_val in MODES.items():
    last_mode_state = self._last_mode_state[mode].get(hp_idx)
    
    # Flanke: operating_state wechselt von etwas anderem auf mode_val
    if last_mode_state != mode_val and op_state_val == mode_val:
        # Prüfe, ob die Cycling-Entities bereits registriert sind
        cycling_entities_ready = False
        try:
            # Prüfe, ob die Cycling-Entities in hass.data verfügbar sind
            if ("lambda_heat_pumps" in self.hass.data and 
                self.entry.entry_id in self.hass.data["lambda_heat_pumps"] and
                "cycling_entities" in self.hass.data["lambda_heat_pumps"][self.entry.entry_id]):
                cycling_entities_ready = True
        except Exception:
            pass
        
        if cycling_entities_ready:
            # Zentrale Funktion für total-Zähler aufrufen
            await increment_cycling_counter(
                self.hass,
                mode=mode,
                hp_index=hp_idx,
                name_prefix=self.entry.data.get("name", "eu08l"),
                use_legacy_modbus_names=self._use_legacy_names,
                cycling_offsets=self._cycling_offsets
            )
            _LOGGER.info(
                "Wärmepumpe %d: %s Modus aktiviert (Cycling total inkrementiert)",
                hp_idx, mode
            )
        else:
            _LOGGER.debug(
                "Wärmepumpe %d: %s Modus aktiviert (Cycling-Entities noch nicht bereit)",
                hp_idx, mode
            )
    
    # Aktuellen Wert als neuen letzten Wert speichern
    self._last_mode_state[mode][hp_idx] = op_state_val
```

### 2.3. Timing-Schutzmaßnahmen

#### Problem
Beim Neustart von Home Assistant kann es zu Timing-Problemen kommen:
- Die Integration wird geladen
- Der Coordinator startet und versucht, Flankenerkennung durchzuführen
- Die Cycling-Entities sind noch nicht vollständig registriert
- Dies führt zu Fehlern wie "Entity not found" oder doppelten Unique IDs

#### Lösung
**Zweistufige Prüfung im Coordinator:**
1. **Entity-Registry-Prüfung**: Ist die Entity bereits registriert?
2. **State-Verfügbarkeits-Prüfung**: Ist der State der Entity verfügbar?

**Robuste Increment-Funktion:**
```python
async def increment_cycling_counter(...):
    # 1. Prüfe Entity Registry
    entity_entry = entity_registry.async_get(entity_id)
    if entity_entry is None:
        _LOGGER.warning(f"Skipping cycling counter increment: {entity_id} not yet registered")
        return

    # 2. Prüfe State-Verfügbarkeit
    state_obj = hass.states.get(entity_id)
    if state_obj is None:
        _LOGGER.warning(f"Skipping cycling counter increment: {entity_id} state not available yet")
        return

    # 3. Führe Update durch
    # ... Rest der Funktion
```

### 2.4. Vorteile der zentralen Flankenerkennung

#### Robustheit
- **Zentrale Logik**: Alle Flankenerkennung an einem Ort
- **Keine Mehrfachzählung**: Nur echte Statuswechsel werden gezählt
- **Unabhängig vom Sensornamen**: Zuordnung über Modbus-Register und Index
- **Timing-Schutz**: Robuste Behandlung von Startup-Sequenzen

#### Performance
- **Effizient**: Nur bei echten Änderungen wird der Zähler erhöht
- **Keine Template-Abhängigkeiten**: Direkte Entity-Updates
- **Minimaler Ressourcenverbrauch**: Keine kontinuierlichen Berechnungen

#### Wartbarkeit
- **Klare Trennung**: Flankenerkennung im Coordinator, Sensor-Logik in Entities
- **Debugging**: Umfassende Logging bei Statuswechseln
- **Erweiterbar**: Neue Modi können einfach hinzugefügt werden

### 2.5. Debugging der Flankenerkennung

#### Log-Meldungen
```
# Bei Statuswechsel
INFO: Wärmepumpe 1: operating_state geändert von 1 auf 5

# Bei Flankenerkennung (Entities bereit)
INFO: Wärmepumpe 1: defrost Modus aktiviert (Cycling total inkrementiert)
INFO: Cycling counter incremented: sensor.eu08l_hp1_defrost_cycling_total = 1 (was 0, offset 0) [entity updated]

# Bei Flankenerkennung (Entities noch nicht bereit)
DEBUG: Wärmepumpe 1: defrost Modus aktiviert (Cycling-Entities noch nicht bereit)

# Bei Entity-Problemen
WARNING: Skipping cycling counter increment: sensor.eu08l_hp1_heating_cycling_total not yet registered
WARNING: Skipping cycling counter increment: sensor.eu08l_hp1_heating_cycling_total state not available yet
```

#### State-Tracking
```python
# Interner State für jede HP und jeden Modus
self._last_mode_state = {
    "heating": {1: 0, 2: 0},      # HP1: 0, HP2: 0
    "hot_water": {1: 0, 2: 0},   # HP1: 0, HP2: 0
    "cooling": {1: 0, 2: 0},     # HP1: 0, HP2: 0
    "defrost": {1: 0, 2: 0},     # HP1: 0, HP2: 0
}
```

## 3. Funktionsweise der Total-Sensoren

### 3.1. Persistente Werte
Total-Sensoren sind echte Python-Entities, die ihre Werte direkt speichern:

```python
class LambdaCyclingSensor(SensorEntity):
    def __init__(self, ...):
        self._cycling_value = 0  # Persistenter Wert
    
    def set_cycling_value(self, value):
        """Set the cycling value and update state."""
        self._cycling_value = int(value)
        self.async_write_ha_state()
    
    @property
    def native_value(self):
        """Return the current cycling value."""
        return int(getattr(self, '_cycling_value', 0))
```

### 3.2. Increment-Funktion
Die `increment_cycling_counter` Funktion in `utils.py` erhöht die Total-Sensoren:

```python
async def increment_cycling_counter(
    hass: HomeAssistant,
    mode: str,
    hp_index: int,
    name_prefix: str,
    use_legacy_modbus_names: bool = False,
    cycling_offsets: dict = None,
):
    # Entity-ID generieren
    sensor_id = f"{mode}_cycling_total"
    device_prefix = f"hp{hp_index}"
    names = generate_sensor_names(...)
    entity_id = names["entity_id"]
    
    # 1. Prüfe Entity Registry
    entity_registry = async_get_entity_registry(hass)
    entity_entry = entity_registry.async_get(entity_id)
    if entity_entry is None:
        _LOGGER.warning(f"Skipping cycling counter increment: {entity_id} not yet registered")
        return

    # 2. Prüfe State-Verfügbarkeit
    state_obj = hass.states.get(entity_id)
    if state_obj is None:
        _LOGGER.warning(f"Skipping cycling counter increment: {entity_id} state not available yet")
        return

    # 3. Aktuellen Wert holen
    current = int(float(state_obj.state)) if state_obj.state not in (None, "unknown", "unavailable") else 0
    
    # 4. Offset anwenden
    offset = cycling_offsets.get(device_prefix, {}).get(sensor_id, 0)
    new_value = current + 1 + offset
    
    # 5. Entity-Update
    cycling_entity = find_cycling_entity(hass, entity_id)
    if cycling_entity:
        cycling_entity.set_cycling_value(new_value)
```

### 3.3. Offset-Unterstützung
Total-Sensoren unterstützen Offsets für Gerätewechsel oder Reset-Szenarien:

```yaml
# In lambda_wp_config.yaml
cycling_offsets:
  hp1:
    heating_cycling_total: 1500   # HP1 hatte bereits 1500 Heizzyklen
    hot_water_cycling_total: 800  # HP1 hatte bereits 800 Warmwasserzyklen
  hp2:
    heating_cycling_total: 0      # HP2 ist neu
    hot_water_cycling_total: 0    # HP2 ist neu
```

## 4. Funktionsweise der Daily-Sensoren

### 4.1. Täglicher Update-Zyklus
1. **Um Mitternacht**: Automatisierung sendet Signal `SIGNAL_UPDATE_YESTERDAY`
2. **Yesterday-Sensoren**: Übernehmen aktuelle Total-Werte
3. **Daily-Sensoren**: Berechnen sich automatisch neu (Total - Yesterday)

### 4.2. Template-Berechnung
```yaml
# Beispiel für heating_cycling_daily
template: |
  {% set total = states('sensor.eu08l_hp1_heating_cycling_total') | float(0) %}
  {% set yesterday = states('sensor.eu08l_hp1_heating_cycling_yesterday') | float(0) %}
  {{ (total - yesterday) | round(0) }}
```

### 4.3. Automatisierung
```python
# In automations.py
@callback
def update_yesterday_sensors(now: datetime) -> None:
    """Update yesterday sensors at midnight."""
    async_dispatcher_send(hass, SIGNAL_UPDATE_YESTERDAY, entry_id)

# Registrierung
listener = async_track_time_change(
    hass, 
    update_yesterday_sensors, 
    hour=0, 
    minute=0, 
    second=0
)
```

## 5. Automatische Erstellung

### 5.1. Basierend auf HP-Konfiguration
Alle Cycling-Sensoren werden automatisch basierend auf der HP-Konfiguration erstellt:

```python
# Aus der Config
num_hps = entry.data.get("num_hps", 1)  # z.B. 2 HPs

# Automatische Erstellung für jede HP
for hp_idx in range(1, num_hps + 1):  # 1, 2
    for mode, template_id in cycling_modes:  # heating, hot_water, cooling, defrost
        # Erstellt Total-, Yesterday- und Daily-Sensoren
```

### 5.2. Konsistente Namensgebung
Alle Sensoren verwenden die zentrale `generate_sensor_names` Funktion:

```python
# Für alle Sensor-Typen
names = generate_sensor_names(
    device_prefix,        # "hp1"
    template["name"],     # "Heating Cycling Total"
    template_id,          # "heating_cycling_total"
    name_prefix,          # "eu08l"
    use_legacy_modbus_names  # False
)
```

### 5.3. Beispiel-Output (2 HPs)
**Total-Sensoren (8 Stück):**
- `sensor.eu08l_hp1_heating_cycling_total`
- `sensor.eu08l_hp1_hot_water_cycling_total`
- `sensor.eu08l_hp1_cooling_cycling_total`
- `sensor.eu08l_hp1_defrost_cycling_total`
- `sensor.eu08l_hp2_heating_cycling_total`
- `sensor.eu08l_hp2_hot_water_cycling_total`
- `sensor.eu08l_hp2_cooling_cycling_total`
- `sensor.eu08l_hp2_defrost_cycling_total`

**Yesterday-Sensoren (8 Stück):**
- `sensor.eu08l_hp1_heating_cycling_yesterday`
- `sensor.eu08l_hp1_hot_water_cycling_yesterday`
- `sensor.eu08l_hp1_cooling_cycling_yesterday`
- `sensor.eu08l_hp1_defrost_cycling_yesterday`
- `sensor.eu08l_hp2_heating_cycling_yesterday`
- `sensor.eu08l_hp2_hot_water_cycling_yesterday`
- `sensor.eu08l_hp2_cooling_cycling_yesterday`
- `sensor.eu08l_hp2_defrost_cycling_yesterday`

**Daily-Sensoren (8 Stück):**
- `sensor.eu08l_hp1_heating_cycling_daily`
- `sensor.eu08l_hp1_hot_water_cycling_daily`
- `sensor.eu08l_hp1_cooling_cycling_daily`
- `sensor.eu08l_hp1_defrost_cycling_daily`
- `sensor.eu08l_hp2_heating_cycling_daily`
- `sensor.eu08l_hp2_hot_water_cycling_daily`
- `sensor.eu08l_hp2_cooling_cycling_daily`
- `sensor.eu08l_hp2_defrost_cycling_daily`

## 6. Vorteile der Gesamtlösung

### 6.1. Robustheit
- **Zentrale Flankenerkennung**: Alle Logik im Coordinator
- **Unabhängige Entities**: Total- und Yesterday-Sensoren sind echte Entities
- **Signal-basiert**: Keine direkten Abhängigkeiten zwischen Sensoren
- **Fehlerbehandlung**: Graceful handling bei fehlenden Werten
- **Timing-Schutz**: Robuste Behandlung von Startup-Sequenzen

### 6.2. Performance
- **Effiziente Flankenerkennung**: Nur bei echten Statuswechseln
- **Template-basiert**: Daily-Sensoren werden nur bei Änderungen neu berechnet
- **Minimaler Ressourcenverbrauch**: Keine kontinuierlichen Polling-Operationen

### 6.3. Wartbarkeit
- **Zentrale Definition**: Alle Sensoren in `const.py` definiert
- **Konsistente Namensgebung**: Verwendet `generate_sensor_names`
- **Klare Trennung**: Flankenerkennung, Total, Yesterday und Daily sind getrennt implementiert

### 6.4. Erweiterbarkeit
- **Neue Modi**: Einfach in `const.py` hinzufügen
- **Mehr HPs**: Automatische Skalierung basierend auf Config
- **Offsets**: Flexible Konfiguration für Gerätewechsel

## 7. Konfiguration

### 7.1. Automatische Einrichtung
- **Setup**: Automatisch bei Integration-Start
- **Cleanup**: Automatisch bei Integration-Entfernung
- **Reload**: Automatisch bei Konfigurationsänderungen

### 7.2. Manuelle Anpassungen
```yaml
# In lambda_wp_config.yaml
cycling_offsets:
  hp1:
    heating_cycling_total: 1500   # Offset für Total-Sensor
    hot_water_cycling_total: 800  # Yesterday wird automatisch angepasst
    cooling_cycling_total: 200
    defrost_cycling_total: 50
  hp2:
    heating_cycling_total: 0      # Neue HP
    hot_water_cycling_total: 0
    cooling_cycling_total: 0
    defrost_cycling_total: 0
```

## 8. Debugging

### 8.1. Log-Meldungen
```
# Flankenerkennung (Entities bereit)
INFO: Wärmepumpe 1: operating_state geändert von 1 auf 5
INFO: Wärmepumpe 1: defrost Modus aktiviert (Cycling total inkrementiert)
INFO: Cycling counter incremented: sensor.eu08l_hp1_defrost_cycling_total = 1 (was 0, offset 0) [entity updated]

# Flankenerkennung (Entities noch nicht bereit)
DEBUG: Wärmepumpe 1: defrost Modus aktiviert (Cycling-Entities noch nicht bereit)

# Entity-Probleme
WARNING: Skipping cycling counter increment: sensor.eu08l_hp1_heating_cycling_total not yet registered
WARNING: Skipping cycling counter increment: sensor.eu08l_hp1_heating_cycling_total state not available yet

# Mitternacht-Update
INFO: Yesterday value updated for sensor.eu08l_hp1_heating_cycling_total: 0 -> 5

# Template-Berechnung
INFO: Template-Sensor berechnet: Heating Cycling Daily = 3
```

### 8.2. State-Attribute
```yaml
# Total-Sensor
yesterday_value: 5
hp_index: 1
sensor_type: cycling_total

# Yesterday-Sensor
mode: heating
hp_index: 1
sensor_type: cycling_yesterday
```

## 9. Erweiterbarkeit

### 9.1. Neue Modi hinzufügen
1. **Modus in `const.py` definieren**:
```python
MODES = {
    "heating": 1,
    "hot_water": 2,
    "cooling": 3,
    "defrost": 5,
    "standby": 0,  # Neuer Modus
}
```

2. **Total-Sensor in `const.py` definieren**:
```python
"standby_cycling_total": {
    "name": "Standby Cycling Total",
    "unit": "cycles",
    "device_type": "hp",
    "state_class": "total_increasing",
    # ... weitere Konfiguration
}
```

3. **Yesterday-Sensor in `const.py` definieren**:
```python
"standby_cycling_yesterday": {
    "name": "Standby Cycling Yesterday",
    "unit": "cycles",
    "device_type": "hp",
    "template": "{% set total = states('sensor.{full_entity_prefix}_standby_cycling_total') | float(0) %}{{ total }}"
}
```

4. **Daily-Sensor in `const.py` definieren**:
```python
"standby_cycling_daily": {
    "name": "Standby Cycling Daily",
    "unit": "cycles",
    "device_type": "hp",
    "template": "{% set total = states('sensor.{full_entity_prefix}_standby_cycling_total') | float(0) %}{% set yesterday = states('sensor.{full_entity_prefix}_standby_cycling_yesterday') | float(0) %}{{ (total - yesterday) | round(0) }}"
}
```

5. **Entity-Erstellung erweitern** (automatisch durch Template-System)

## 10. Troubleshooting

### 10.1. Häufige Probleme

#### Doppelte Unique IDs beim Neustart
**Symptom**: `Platform lambda_heat_pumps does not generate unique IDs. ID eu08l_hp1_heating_cycling_total is already used`

**Ursache**: Timing-Problem beim Neustart - Entities werden erneut registriert, bevor alte entfernt sind

**Lösung**: 
- Entity Registry bereinigen (siehe Abschnitt 2.3)
- Integration neu starten
- Timing-Schutzmaßnahmen sind bereits implementiert

#### Cycling-Entities nicht gefunden
**Symptom**: `Cycling entity sensor.eu08l_hp1_heating_cycling_total not found, using fallback state update`

**Ursache**: Entities sind noch nicht vollständig registriert

**Lösung**: 
- Warten bis Integration vollständig geladen ist
- Log zeigt automatisch, wenn Entities bereit sind

#### Yesterday-Sensoren werden nicht aktualisiert
**Symptom**: Daily-Sensoren zeigen 0 oder falsche Werte

**Ursache**: Mitternacht-Automatisierung funktioniert nicht

**Lösung**:
- Prüfe Log auf Mitternacht-Updates
- Manuell Signal senden: `hass.bus.async_fire("lambda_heat_pumps_update_yesterday")`

### 10.2. Debugging-Schritte
1. **Log-Level auf DEBUG setzen** für detaillierte Meldungen
2. **Entity Registry prüfen** auf doppelte Einträge
3. **State-Objekte prüfen** mit Developer Tools
4. **Template-Sensoren testen** mit Template-Editor

## Fazit

Die Cycling-Sensoren bieten eine **umfassende, robuste und performante Lösung** für die Verfolgung von Betriebsmodus-Wechseln. Die Kombination aus:

- **Zentraler Flankenerkennung** im Coordinator mit Timing-Schutz
- **Echten Entities** für Total- und Yesterday-Sensoren
- **Template-Sensoren** für Daily-Berechnungen
- **Automatischer Erstellung** basierend auf HP-Konfiguration
- **Konsistenter Namensgebung** mit `generate_sensor_names`
- **Robuster Fehlerbehandlung** für Startup-Sequenzen

ermöglicht maximale Flexibilität bei minimalem Ressourcenverbrauch und höchster Wartbarkeit. Die Timing-Schutzmaßnahmen stellen sicher, dass die Integration auch nach Neustarts zuverlässig funktioniert. 