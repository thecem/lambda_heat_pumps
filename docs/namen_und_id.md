# Namens- und ID-Schema der Lambda Home Assistant Integration

Diese Dokumentation beschreibt, wie die Namen, IDs und Anzeigenamen ("name") für Sensoren und Climate-Entities in der Lambda-Integration generiert werden. Sie erklärt die Auswirkungen der Konfigurationsoption **use_modbus_names** und gibt Beispiele für beide Schemata. Außerdem werden die Felder `entity_id`, `unique_id`, `name` und `original_name` erläutert und Best Practices für Datenkontinuität und Automationen gegeben.

---

## 1. Grundprinzipien

- **entity_id**: Wird von Home Assistant als Primärschlüssel für Historie, Automationen und Dashboards verwendet. Beispiel: `sensor.eu08l_hp1_flow_line_temperature`
- **unique_id**: Wird intern zur eindeutigen Identifikation der Entity verwendet. Beispiel: `hp1_flow_line_temperature`
- **name**: Anzeigename im UI. Kann vom Nutzer überschrieben werden. Wird aus der Konfiguration und dem gewählten Schema generiert.
- **original_name**: Ursprünglicher Anzeigename, bevor der Nutzer ihn ändert (wird von Home Assistant verwaltet).

## 2. Namensschemata

Die Integration unterstützt zwei Schemata, wählbar über die Option `use_modbus_names` in der Konfiguration:

### a) Modbus-Schema (`use_modbus_names: true`)
- **Format:** `<base_name>_<DeviceType><Nummer>_<SensorKey>`
- **Beispiel:**
  - Sensor: `EU08L_Hp1_Flow_Line_Temperature`
  - Climate: `EU08L_Hot_Water_1_Target_High_Temperature`

### b) Neues Schema (`use_modbus_names: false`)
- **Format:** `<base_name>_<device_type>_<nummer>_<sensor_key>` (alles klein)
- **Beispiel:**
  - Sensor: `eu08l_hp_1_flow_line_temperature`
  - Climate: `eu08l_hot_water_1_target_high_temperature`

Das Schema wirkt sich auf den **name**-Wert der Entity aus. Die `entity_id` bleibt unabhängig vom Schema stabil, solange die Konfiguration (z.B. Anzahl der Geräte) gleich bleibt.

## 3. Dynamische Sensoren und Climate-Entities

Die Integration unterstützt mehrere Heat Pumps (HP), Boiler, Heating Circuits (HC), Buffer und Solar-Module. Die Namen werden dynamisch generiert:

- **Heat Pump Sensor:**
  - Modbus: `EU08L_Hp1_Flow_Line_Temperature`
  - Neu:    `eu08l_hp_1_flow_line_temperature`
  - entity_id: `sensor.hp1_flow_line_temperature`
  - unique_id: `hp1_flow_line_temperature`

- **Boiler Sensor:**
  - Modbus: `EU08L_Boil2_Actual_High_Temperature`
  - Neu:    `eu08l_boil_2_actual_high_temperature`
  - entity_id: `sensor.boil2_actual_high_temperature`
  - unique_id: `boil2_actual_high_temperature`

- **Heating Circuit Sensor:**
  - Modbus: `EU08L_Hc1_Target_Room_Temperature`
  - Neu:    `eu08l_hc_1_target_room_temperature`
  - entity_id: `sensor.hc1_target_room_temperature`
  - unique_id: `hc1_target_room_temperature`

- **Buffer Sensor:**
  - Modbus: `EU08L_Buffer1_Temperature_Top`
  - Neu:    `eu08l_buffer_1_temperature_top`
  - entity_id: `sensor.buffer1_temperature_top`
  - unique_id: `buffer1_temperature_top`

- **Solar Sensor:**
  - Modbus: `EU08L_Solar1_Operating_State`
  - Neu:    `eu08l_solar_1_operating_state`
  - entity_id: `sensor.solar1_operating_state`
  - unique_id: `solar1_operating_state`

- **Climate Entity (Warmwasser/Boiler):**
  - Modbus: `EU08L_Hot_Water_1_Target_High_Temperature`
  - Neu:    `eu08l_hot_water_1_target_high_temperature`
  - entity_id: `climate.eu08l_hot_water_1_climate`
  - unique_id: `eu08l_hot_water_1_climate`

- **Climate Entity (Heizkreis):**
  - Modbus: `EU08L_Heating_Circuit_2_Target_Room_Temperature`
  - Neu:    `eu08l_heating_circuit_2_target_room_temperature`
  - entity_id: `climate.eu08l_heating_circuit_2_climate`
  - unique_id: `eu08l_heating_circuit_2_climate`

## 4. Felder im Entity-Registry

| Feld         | Bedeutung                                                                 |
|--------------|---------------------------------------------------------------------------|
| entity_id    | Primärschlüssel für Historie, Automationen, Dashboards                    |
| unique_id    | Eindeutige ID der Entity (intern, für Migration und Zuordnung)            |
| name         | Anzeigename im UI (kann vom Nutzer überschrieben werden)                  |
| original_name| Ursprünglicher Anzeigename (wird von Home Assistant verwaltet)            |

## 5. Auswirkungen auf Historie und Automationen

- **Wichtig:** Die Historie und Automationen werden über die `entity_id` verknüpft. Solange sich diese nicht ändert, bleiben Daten und Automationen erhalten.
- Ein Wechsel des Namensschemas (über `use_modbus_names`) ändert **nur** den Anzeigenamen (`name`), nicht aber die `entity_id` oder `unique_id`.
- Die `entity_id` bleibt stabil, solange die Geräteanzahl und Reihenfolge gleich bleibt.
- Bei Änderung der Geräteanzahl (z.B. weitere HP/Boiler) werden neue Entities mit neuen IDs erzeugt.

## 6. Best Practices

- Für maximale Datenkontinuität sollte die Geräteanzahl und Reihenfolge in der Konfiguration nicht verändert werden.
- Automationen und Dashboards sollten immer auf die `entity_id` referenzieren, nicht auf den Anzeigenamen.
- Nach Änderung des Namensschemas kann es sinnvoll sein, die Anzeigenamen im UI zu prüfen und ggf. anzupassen.

## 7. Beispiele für die wichtigsten Felder

| Entity-Typ   | entity_id                              | unique_id                        | name (Modbus)                      | name (neu)                         |
|--------------|----------------------------------------|----------------------------------|-------------------------------------|-------------------------------------|
| HP-Sensor    | sensor.hp1_flow_line_temperature       | hp1_flow_line_temperature        | EU08L_Hp1_Flow_Line_Temperature     | eu08l_hp_1_flow_line_temperature    |
| Boiler       | sensor.boil2_actual_high_temperature   | boil2_actual_high_temperature    | EU08L_Boil2_Actual_High_Temperature | eu08l_boil_2_actual_high_temperature|
| HC           | sensor.hc1_target_room_temperature     | hc1_target_room_temperature      | EU08L_Hc1_Target_Room_Temperature   | eu08l_hc_1_target_room_temperature  |
| Buffer       | sensor.buffer1_temperature_top         | buffer1_temperature_top          | EU08L_Buffer1_Temperature_Top       | eu08l_buffer_1_temperature_top      |
| Solar        | sensor.solar1_operating_state          | solar1_operating_state           | EU08L_Solar1_Operating_State        | eu08l_solar_1_operating_state       |
| Climate Boil | climate.eu08l_hot_water_1_climate      | eu08l_hot_water_1_climate        | EU08L_Hot_Water_1_Target_High_Temperature | eu08l_hot_water_1_target_high_temperature |
| Climate HC   | climate.eu08l_heating_circuit_2_climate| eu08l_heating_circuit_2_climate  | EU08L_Heating_Circuit_2_Target_Room_Temperature | eu08l_heating_circuit_2_target_room_temperature |

## 8. Übersetzungen und Anzeigename

- Die Namen werden **nicht** automatisch übersetzt. Nur wenn ein `translation_key` gesetzt und in den Übersetzungsdateien gepflegt ist, erscheint eine Lokalisierung im UI.
- Die meisten Entities nutzen den generierten Namen als Anzeigename.

## 9. Wichtige Hinweise zur Namensgebung

- Der Name "lambda" ist in Home Assistant reserviert und darf nicht als Gerätename verwendet werden.
- Der Standard-Name ist daher "lambda_wp" (für "Lambda Wärmepumpe").
- Bei der Konfiguration sollte ein eindeutiger Name gewählt werden, der nicht mit reservierten Namen kollidiert.
- Leerzeichen im Namen werden automatisch entfernt.

## 10. Zusammensetzung des base_name

Der `base_name` wird aus verschiedenen Komponenten zusammengesetzt und ist ein wichtiger Bestandteil der Entity-Namen. Er wird wie folgt aufgebaut:

### 10.1 Grundstruktur
Der `base_name` setzt sich aus dem Gerätenamen (`name_prefix`) und dem spezifischen Sensornamen zusammen:

```
base_name = name_prefix + " " + sensor_specific_name
```

### 10.2 Komponenten

1. **name_prefix**:
   - Wird aus der Konfiguration gelesen (`entry.data.get("name", "lambda_wp")`)
   - Standardwert ist "lambda_wp" (wenn kein Name angegeben wurde)
   - Wird in Kleinbuchstaben umgewandelt und Leerzeichen entfernt
   - Beispiel: "EU08L" → "eu08l"

2. **sensor_specific_name**:
   - Für statische Sensoren: Der Name aus der Sensor-Konfiguration
   - Für dynamische Sensoren: Wird aus Template und Gerätenummer zusammengesetzt

### 10.3 Beispiele für verschiedene Sensortypen

1. **Statische Sensoren**:
   ```
   base_name = name_prefix + " " + sensor_config["name"]
   Beispiel: "eu08l Flow Line Temperature"
   ```

2. **Heat Pump Sensoren**:
   ```
   base_name = name_prefix + " HP" + nummer + " " + template["name"]
   Beispiel: "eu08l HP1 Flow Line Temperature"
   ```

3. **Boiler Sensoren**:
   ```
   base_name = name_prefix + " Boil" + nummer + " " + template["name"]
   Beispiel: "eu08l Boil1 Actual High Temperature"
   ```

4. **Heating Circuit Sensoren**:
   ```
   base_name = name_prefix + " HC" + nummer + " " + template["name"]
   Beispiel: "eu08l HC1 Target Room Temperature"
   ```

5. **Buffer Sensoren**:
   ```
   base_name = name_prefix + " Buffer" + nummer + " " + template["name"]
   Beispiel: "eu08l Buffer1 Temperature Top"
   ```

6. **Solar Sensoren**:
   ```
   base_name = name_prefix + " Solar" + nummer + " " + template["name"]
   Beispiel: "eu08l Solar1 Operating State"
   ```

### 10.4 Verwendung des base_name

Der `base_name` wird in der `get_entity_name` Funktion verwendet, um den finalen Entity-Namen zu generieren. Je nach gewähltem Schema (`use_modbus_names`) wird der `base_name` unterschiedlich formatiert:

- **Modbus-Schema** (`use_modbus_names: true`):
  - `base_name` wird in Großbuchstaben umgewandelt
  - Leerzeichen werden durch Unterstriche ersetzt
  - Beispiel: "EU08L_HP1_FLOW_LINE_TEMPERATURE"

- **Neues Schema** (`use_modbus_names: false`):
  - `base_name` wird in Kleinbuchstaben umgewandelt
  - Leerzeichen werden durch Unterstriche ersetzt
  - Beispiel: "eu08l_hp_1_flow_line_temperature"

---

*Letzte Aktualisierung: [automatisch generiert]* 