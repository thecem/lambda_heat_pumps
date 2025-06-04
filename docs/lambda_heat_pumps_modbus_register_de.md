# Lambda Wärmepumpen - Modbus Registerbeschreibung

Diese Dokumentation beschreibt die Modbus-Register und -Adressen, die von der Lambda Wärmepumpen Integration verwendet werden, basierend auf dem Modbus-Protokoll.

## Register-Struktur

Die Modbus-Register-Adresse ist wie folgt strukturiert:
```
X _ _ _ ->  Erste Stelle:    Index (wird vom Modultyp vorgegeben)
_ X _ _ ->  Zweite Stelle:   Subindex (wird von Modulnummer vorgegeben)
_ _ X X ->  Letzten 2 Stellen: Number (wird von Datenpunkt vorgegeben)
```

### Index (Module)
- General = 0
- Heatpump = 1
- Boiler = 2
- Buffer = 3
- Solar = 4
- Heating circuit = 5

### Subindex (Gerätenummer)
- Die Modulnummer ergibt sich aus der Reihenfolge der Module im Konfigurationsmodul
- Module mit niedrigerer Nummer haben einen niedrigeren Subindex

### Beispiel
Register zum Auslesen der Vorlauftemperatur der Wärmepumpe 2:
```
1    1    04
│    │    │
Index Subindex Number
```
= 1104 (Modbus-Adresse)

## Modul: General Ambient (Index 0, Subindex 0)

| Number | Name | R/W | Datentyp | Einheit | Beschreibung |
|--------|------|-----|----------|---------|-------------|
| 00 | Error number | RO | INT16 | [Nr] | 0 = Kein Fehler |
| 01 | Operating state | RO | UINT16 | [Nr] | 0 = AUS, 1 = AUTOMATIK, 2 = MANUELL, 3 = FEHLER |
| 02 | Actual ambient temp. | RW | INT16 | [0.1°C] | Aktuelle Umgebungstemperatur (min = -50,0°C; max = 80,0°C) |
| 03 | Average ambient temp. 1h | RO | INT16 | [0.1°C] | Durchschnittliche Temperatur der letzten 60 Minuten |
| 04 | Calculated ambient temp. | RO | INT16 | [0.1°C] | Für Wärmeverteilungsmodule berechnete Temperatur |

## Modul: General E-Manager (Index 0, Subindex 1)

| Number | Name | R/W | Datentyp | Einheit | Beschreibung |
|--------|------|-----|----------|---------|-------------|
| 00 | Error number | RO | INT16 | [Nr] | 0 = Kein Fehler |
| 01 | Operating state | RO | UINT16 | [Nr] | 0 = AUS, 1 = AUTOMATIK, 2 = MANUELL, 3 = FEHLER, 4 = OFFLINE |
| 02 | Actual power | RW | UINT16/INT16 | [Watt] | Aktuelle Eingangsleistung oder Überschussleistung |
| 03 | Actual power consumption | RO | INT16 | [Watt] | Aktuelle Leistungsaufnahme aller Wärmepumpen |
| 04 | Power consumption setpoint | RO | INT16 | [Watt] | Sollwert für die Gesamtleistungsaufnahme aller Wärmepumpen |

## Modul: Heat Pump (Index 1, Subindex 0-2)

| Number | Name | R/W | Datentyp | Einheit | Beschreibung |
|--------|------|-----|----------|---------|-------------|
| 00 | Hp Error state | RO | UINT16 | [Nr] | 0=NONE, 1=MESSAGE, 2=WARNING, 3=ALARM, 4=FAULT |
| 01 | Hp Error number | RO | INT16 | [Nr] | Fehlernummer |
| 02 | Hp State | RO | UINT16 | [Nr] | 0=INIT, 1=REFERENCE, 2=RESTART-BLOCK, ... |
| 03 | Operating state | RO | UINT16 | [Nr] | 0=STBY, 1=CH, 2=DHW, 3=CC, ... |
| 04 | T-flow | RO | INT16 | [0.01°C] | Vorlauftemperatur |
| 05 | T-return | RO | INT16 | [0.01°C] | Rücklauftemperatur |
| 06 | Vol. sink | RO | INT16 | [0.01l/min] | Volumenstrom Wärmesenke |
| 07 | T-EQin | RO | INT16 | [0.01°C] | Energiequellen-Einlasstemperatur |
| 08 | T-EQout | RO | INT16 | [0.01°C] | Energiequellen-Auslasstemperatur |
| 09 | Vol. source | RO | INT16 | [0.01l/min] | Volumenstrom Energiequelle |
| 10 | Compressor-Rating | RO | UINT16 | [0.01%] | Kompressor-Leistungsbewertung |
| 11 | Qp heating | RO | INT16 | [0.1kW] | Aktuelle Heizleistung |
| 12 | FI power consumption | RO | INT16 | [Watt] | Frequenzumrichter-Leistungsaufnahme |
| 13 | COP | RO | INT16 | [0.01] | Leistungszahl (Coefficient of Performance) |
| 14 | Modbus request release password | RW | UINT16 | [Nr] | Passwort-Register für Modbus-Anfragen |
| 15 | Request type | RW | INT16 | [Nr] | 0=KEINE ANFRAGE, 1=UMWÄLZPUMPE, 2=HEIZUNG, ... |
| 16 | Request flow line temp | RW | INT16 | [0.1°C] | Angeforderte Vorlauftemperatur (min=0,0°C, max=70,0°C) |
| 17 | Request return line temp | RW | INT16 | [0.1°C] | Angeforderte Rücklauftemperatur (min=0,0°C, max=65,0°C) |
| 18 | Request heat sink temp. diff | RW | INT16 | [0.1K] | Angeforderte Temperaturdifferenz (min=0,0K, max=35,0K) |
| 19 | Relais state for 2nd heating stage | RO | INT16 | 0/1 | 1 = NO-Relais für 2. Heizstufe ist aktiviert |
| 20-21 | Statistic VdA E since last reset | RO | INT32 | [Wh] | Elektrische Energieaufnahme des Kompressors seit letztem Reset |
| 22-23 | Statistic VdA Q since last reset | RO | INT32 | [Wh] | Thermische Energieabgabe des Kompressors seit letztem Reset |

## Modul: Boiler (Index 2, Subindex 0-4)

| Number | Name | R/W | Datentyp | Einheit | Beschreibung |
|--------|------|-----|----------|---------|-------------|
| 00 | Error number | RO | INT16 | [Nr] | 0 = Kein Fehler |
| 01 | Operating state | RO | UINT16 | [Nr] | 0=STBY, 1=DHW, 2=LEGIO, 3=SUMMER, ... |
| 02 | Actual high temp. | RO | INT16 | [0.1°C] | Aktuelle Temperatur oberer Sensor |
| 03 | Actual low temp. | RO | INT16 | [0.1°C] | Aktuelle Temperatur unterer Sensor |
| 04 | Actual circulation temp. | RO | INT16 | [0.1°C] | Aktuelle Temperatur Zirkulationssensor |
| 05 | Actual circulation pump state | RO | INT16 | 0/1 | Aktueller Zustand der Zirkulationspumpe [0=AUS, 1=EIN] |
| 50 | Set.: Maximum boiler temp. | RW | INT16 | [0.1°C] | Einstellung für maximale Boilertemperatur (min=25,0°C, max=65,0°C) |

## Modul: Buffer (Index 3, Subindex 0-4)

| Number | Name | R/W | Datentyp | Einheit | Beschreibung |
|--------|------|-----|----------|---------|-------------|
| 00 | Error number | RO | INT16 | [Nr] | 0 = Kein Fehler |
| 01 | Operating state | RO | UINT16 | [Nr] | 0=STBY, 1=HEATING, 2=COOLING, 3=SUMMER, ... |
| 02 | Actual high temp. | RO | INT16 | [0.1°C] | Aktuelle Temperatur oberer Sensor |
| 03 | Actual low temp. | RO | INT16 | [0.1°C] | Aktuelle Temperatur unterer Sensor |
| 04 | Modbus buffer temp. High | RW | INT16 | [0.1°C] | Per Modbus gesetzte Puffertemperatur (min=0°C, max=90°C) |
| 05 | Request type | RW | INT16 | [Enum] | -1=UNGÜLTIGE ANFRAGE, 0=KEINE ANFRAGE, ... |
| 06 | Request flow line temp. setpoint | RW | INT16 | [0.1°C] | Angeforderte Vorlauftemperatur (min=0,0°C, max=65,0°C) |
| 07 | Request return line temp. Setpoint | RW | INT16 | [0.1°C] | Angeforderte Rücklauftemperatur (min=0,0°C, max=60,0°C) |
| 08 | Request heat sink temp. Diff setpoint | RW | INT16 | [0.1°K] | Angeforderte Temperaturdifferenz (min=0,0K, max=35,0K) |
| 09 | Modbus request heating capacity | RW | INT16 | [0.1kW] | Angeforderte Leistung (min=0,0kW, max=25,5kW) |
| 50 | Set.: Maximum buffer temp. | RW | INT16 | [0.1°C] | Einstellung für maximale Puffertemperatur (min=25,0°C, max=65,0°C) |

## Modul: Solar (Index 4, Subindex 0-1)

| Number | Name | R/W | Datentyp | Einheit | Beschreibung |
|--------|------|-----|----------|---------|-------------|
| 00 | Error number | RO | INT16 | [Nr] | 0 = Kein Fehler |
| 01 | Operating state | RO | UINT16 | [Nr] | 0=STBY, 1=HEATING, 2=ERROR, 3=OFF |
| 02 | Collector temp. | RO | INT16 | [0.1°C] | Aktuelle Temperatur Kollektorsensor |
| 03 | Buffer 1 temp. | RO | INT16 | [0.1°C] | Aktuelle Temperatur Puffer 1 Sensor |
| 04 | Buffer 2 temp. | RO | INT16 | [0.1°C] | Aktuelle Temperatur Puffer 2 Sensor |
| 50 | Set.: Maximum buffer temp. | RW | INT16 | [0.1°C] | Einstellung für maximale Puffertemperatur (min=25,0°C, max=90,0°C) |
| 51 | Set.: Buffer changeover temp. | RW | INT16 | [0.1°C] | Einstellung für Pufferumschalttemperatur (min=25,0°C, max=90,0°C) |

## Modul: Heating Circuit (Index 5, Subindex 0-11)

| Number | Name | R/W | Datentyp | Einheit | Beschreibung |
|--------|------|-----|----------|---------|-------------|
| 00 | Error number | RO | INT16 | [Nr] | 0 = Kein Fehler |
| 01 | Operating state | RO | UINT16 | [Nr] | 0=HEATING, 1=ECO, 2=COOLING, ... |
| 02 | Flow line temp. | RO | INT16 | [0.1°C] | Aktuelle Temperatur Vorlaufsensor |
| 03 | Return line temp. | RO | INT16 | [0.1°C] | Aktuelle Temperatur Rücklaufsensor |
| 04 | Room device temp. | RW | INT16 | [0.1°C] | Aktuelle Temperatur Raumgerätesensor (min=-29,9°C, max=99,9°C) |
| 05 | Setpoint flow line temp. | RW | INT16 | [0.1°C] | Solltemperatur Vorlauf (min=15,0°C, max=65,0°C) |
| 06 | Operating mode | RW | INT16 | [Nr] | 0=AUS(RW), 1=MANUAL(R), 2=AUTOMATIK(RW), ... |
| 07 | Target temp. flow line | RO | INT16 | [0.1°C] | Zieltemperatur Vorlauf |
| 50 | Set.: Offset flow line temp. setpoint | RW | INT16 | [0.1°C] | Einstellung für Vorlauf-Temperatursollwert-Offset (min=-10,0K, max=10,0K) |
| 51 | Set.: Setpoint room heating temp. | RW | INT16 | [0.1°C] | Einstellung für Raumtemperatursollwert Heizbetrieb (min=15,0°C, max=40,0°C) |
| 52 | Set.: Setpoint room cooling temp. | RW | INT16 | [0.1°C] | Einstellung für Raumtemperatursollwert Kühlbetrieb (min=15,0°C, max=40,0°C) |

## Hinweise zur Kommunikation

- Kommunikation erfolgt über Modbus TCP und/oder RTU
- Die Zeit eines Kommunikations-Timeouts beträgt 1 Minute
- Lesefunktion erfolgt über den Modbus-Funktionscode 0x03 (read multiple holding registers)
- Schreibfunktion erfolgt über den Modbus-Funktionscode 0x10 (write multiple holding registers)
- Unit ID ist standardmäßig 1
- TCP-Kommunikation erfolgt über Port 502
- Es können bis zu 16 Kommunikationskanäle (16 Master) bedient werden

### Besonderheiten für Schreibzugriffe

- Datenpunkte zwischen 00-49, die beschrieben werden, müssen regelmäßig aktualisiert werden (Timeout nach 5 Minuten)
- Datenpunkte über 50 können einmalig beschrieben werden und werden dauerhaft gespeichert
- Die Verbindung sollte nicht bei jeder Modbus-Anforderung auf- und abgebaut werden, da dies zu Störungen führen kann
