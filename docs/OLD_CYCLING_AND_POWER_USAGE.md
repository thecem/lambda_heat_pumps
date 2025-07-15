# Lambda Heat Pumps: Cycling- und Power-Usage-Zähler pro Betriebsart

## Übersicht
Diese Dokumentation beschreibt die Funktionsweise der generischen Flankenerkennung und Energieintegration in der Lambda Heat Pumps Integration. Sie erklärt, wie Statuswechsel am `operating_state` erkannt werden, wie die Zuordnung zu den jeweiligen Zählern/Sensoren erfolgt und wie die Sensorwerte für **Cycling** und **Power Usage** pro Betriebsart bereitgestellt werden.

---

## 1. Zielsetzung
- **Cycling-Zähler**: Zählen, wie oft eine Wärmepumpe in einen bestimmten Betriebsmodus (Heizen, Warmwasser, Kühlen, Defrost) gewechselt ist.
- **Power Usage**: Ermitteln, wie viel Energie (kWh) pro Tag und Modus verbraucht wurde.
- **Generisch & Erweiterbar**: Die Lösung ist für beliebig viele Betriebsarten und Wärmepumpen-Instanzen ausgelegt.
- **Robust**: Die Erkennung erfolgt unabhängig vom Sensornamen, nur anhand des Modbus-Registers und Index.
- **Offsets**: Ermöglichen das Setzen von Startwerten (z. B. bei Gerätewechsel).

---

## 2. Funktionsweise der Flankenerkennung

### 2.1. Was ist eine Flanke?
Eine Flanke ist der Übergang eines Sensors von einem Zustand in einen anderen. Für die Zählung interessiert uns die **positive Flanke**: Der Wechsel von "nicht aktiv" auf "aktiv" für einen bestimmten Modus.

### 2.2. Wie wird die Flanke erkannt?
- Für jeden Modus (z. B. Heizen = 1, Warmwasser = 2, Kühlen = 3, Defrost = 5) und jede Wärmepumpe wird der letzte bekannte Wert des `operating_state` gespeichert:  
  `self._last_mode_state[mode][hp_idx]`
- Bei jedem Polling wird der aktuelle Wert des `operating_state` ausgelesen.
- **Nur wenn** der vorherige Wert (`last_mode_state`) **ungleich** dem Zielwert (`mode_val`) war **und** der aktuelle Wert **gleich** dem Zielwert ist, wird der Zähler erhöht:

```python
if last_mode_state != mode_val and op_state_val == mode_val:
    cycles[hp_idx] = cycles.get(hp_idx, 0) + 1
```
- Nach der Prüfung wird der aktuelle Wert als neuer letzter Wert gespeichert:

```python
self._last_mode_state[mode][hp_idx] = op_state_val
```

### 2.3. Debugging und Monitoring
- **Info-Meldungen**: Bei jeder Änderung des `operating_state` wird eine Info-Meldung ausgegeben:
  ```
  Wärmepumpe 1: operating_state geändert von 0 auf 1
  ```
- **Cycling-Meldungen**: Bei jeder erkannten Flanke (Modus-Aktivierung) wird eine Info-Meldung ausgegeben:
  ```
  Wärmepumpe 1: heating Modus aktiviert (Cycling: 5)
  ```
- Diese Meldungen helfen bei der Diagnose von Problemen mit der Flankenerkennung.

### 2.4. Vorteile
- **Keine Mehrfachzählung**: Der Zähler erhöht sich nur bei echten Statuswechseln.
- **Unabhängig vom Sensornamen**: Die Zuordnung erfolgt über Modbus-Register und Index.
- **Erweiterbar**: Neue Modi können einfach ergänzt werden.

---

## 3. Energieintegration (Power Usage)

### 3.1. Prinzip
- Für jeden Modus und jede Wärmepumpe wird ein eigener Energiezähler geführt:  
  `self.<mode>_energy[hp_idx]`
- Bei jedem Polling wird geprüft, ob der aktuelle Modus aktiv ist (`op_state_val == mode_val`).
- Ist der Modus aktiv, wird die aktuelle Leistung (z. B. `actual_heating_capacity`) mit dem Zeitintervall multipliziert und zum Tageszähler addiert:

```python
if op_state_val == mode_val:
    energy[hp_idx] = energy.get(hp_idx, 0.0) + power_val * interval
```
- Das Zeitintervall ist dynamisch und entspricht dem Polling-Intervall (z. B. 30 Sekunden).

### 3.2. Vorteile
- **Tagesgenaue Verbrauchswerte pro Modus**
- **Unabhängig von der Namensgebung**
- **Offset-fähig**

---

## 4. Sensorbereitstellung

### 4.1. Dynamische Entity-IDs
- Die Sensoren werden für jeden Modus und jede Wärmepumpe dynamisch erzeugt, z. B.:
  - `sensor.eu08l_hp1_heating_cycling_daily`
  - `sensor.eu08l_hp1_heating_energy_daily`
  - `sensor.eu08l_hp1_hot_water_cycling_daily`
  - `sensor.eu08l_hp1_hot_water_energy_daily`
- Das Namensschema richtet sich nach der Konfiguration (`use_legacy_names`).

### 4.2. Offsets
- Offsets für Cycling und Energy können in der `lambda_wp_config.yaml` gesetzt werden:

```yaml
cycling_offsets:
  hp1: 0
  hp2: 0
energy_offsets:
  hp1: 0.0
  hp2: 0.0
```
- Die Sensorwerte werden immer als Summe aus internem Zähler und Offset bereitgestellt.

---

## 5. Erweiterbarkeit
- Neue Betriebsmodi können einfach im `MODES`-Dict ergänzt werden.
- Die Flankenerkennung und Energieintegration funktionieren automatisch für alle eingetragenen Modi.
- Die Lösung ist für beliebig viele Wärmepumpen-Instanzen ausgelegt.

---

## 6. Persistenz
- Die aktuellen Zählerstände werden nach jedem Polling asynchron gespeichert.
- Beim Neustart werden die Werte wieder geladen und fortgeführt.

---

## 7. Beispielablauf
1. **Polling:** Die Integration liest alle relevanten Register aus.
2. **Flankenerkennung:** Für jeden Modus und jede HP wird geprüft, ob ein Statuswechsel vorliegt.
3. **Zähler erhöhen:** Bei Flanke wird der entsprechende Cycling-Zähler erhöht.
4. **Energieintegration:** Ist ein Modus aktiv, wird die aktuelle Leistung zum Tagesverbrauch addiert.
5. **Sensorwerte:** Die aktuellen Werte (inkl. Offsets) werden als Sensoren bereitgestellt.
6. **Persistenz:** Die Werte werden gespeichert.

---

## 8. Vorteile der Lösung
- **Robust gegen Namensänderungen**
- **Keine Mehrfachzählung**
- **Tagesgenaue Verbrauchswerte pro Modus**
- **Offset-fähig und persistent**
- **Leicht erweiterbar für neue Modi**

---

## 9. Hinweise
- Die Lösung funktioniert für alle unterstützten Wärmepumpen und ist unabhängig vom Namensschema.
- Die Zuordnung erfolgt ausschließlich über Modbus-Register und Index.
- Die Sensoren sind nach Home Assistant-Konventionen benannt und können in Automationen, Dashboards und Auswertungen verwendet werden.

---

## 10. Troubleshooting

### 10.1. Flankenerkennung funktioniert nicht
Wenn die Flankenerkennung nicht richtig funktioniert, können folgende Schritte helfen:

1. **Logs überprüfen**: Schauen Sie in die Home Assistant Logs nach Info-Meldungen:
   ```
   Wärmepumpe 1: operating_state geändert von 0 auf 1
   Wärmepumpe 1: heating Modus aktiviert (Cycling: 5)
   ```

2. **Sensor-Werte prüfen**: Überprüfen Sie, ob der `operating_state` Sensor korrekte Werte liefert:
   - Heizen: 1
   - Warmwasser: 2  
   - Kühlen: 3
   - Defrost: 5

3. **Polling-Intervall**: Ein zu kurzes Polling-Intervall kann zu Problemen führen. Empfohlen: 30 Sekunden oder mehr.

4. **Register-Konfiguration**: Stellen Sie sicher, dass das `operating_state` Register korrekt konfiguriert ist.

### 10.2. Häufige Probleme
- **Keine Info-Meldungen**: Der `operating_state` Sensor wird nicht korrekt ausgelesen
- **Falsche Cycling-Werte**: Die Flankenerkennung zählt zu oft oder zu selten
- **Fehlende Energie-Werte**: Der `actual_heating_capacity` Sensor ist nicht verfügbar

---

**Fragen oder Erweiterungswünsche?** Bitte im Projekt melden! 