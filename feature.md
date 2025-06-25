# Feature: Additional sensors for Lambda heat pump

## Goal
In this branch, additional sensors for the Lambda heat pump are to be integrated. The aim is to make calculated (template) sensor data available in the Home Assistant.

## Background
Currently, the sensors (temperature, operating mode, etc.) offered by the Lambda are read out. Many users would like more sensors for a more detailed evaluation. (JAZ / clocking..)

## Tasks
- [x] Research: Which sensors are useful?
- [ ] Integration of the new sensors into the Python component
- [ ] Adaptation of the documentation
- [ ] Creation of unit tests for the new sensors

## List of sensors
- JAZ (calculation of the annual coefficient of performance)
- COP total (calculates total thermal energy / total primary energy)
- Cycles
- Cycles by type of demand (heating / DHW)
- Electricity consumption by type of demand (heating / DHW)
- daily, monthly / annual electricity consumption / heat end / COP
- ...

## Acceptance criteria
- The new sensors appear in Home Assistant as separate entities.
- All sensors are "dynamic", are generated according to the number of devices, if necessary (several heating circuits)
- All sensors are documented.
- Unit tests exist for each new sensor integration.

## Status
- Feature branch created
- First sensors integrated (see commits)
- Documentation is being updated

## ToDo
- Check and add further sensors
- Write and execute tests
- Start review/code review

Translated with DeepL.com (free version)

# Feature: Zusätzliche Sensoren für Lambda Wärmepumpe

## Ziel
In diesem Branch sollen zusätzliche Sensoren für die Lambda Wärmepumpe integriert werden. Ziel ist es, berechnete (template) Sensordaten im Home Assistant verfügbar zu machen.

## Hintergrund
Aktuell werden die Senoren (Temperatur, Betriebsmodus, etc.) ausgelesen, die die Lambda anbietet. Viele Nutzer:innen wünschen sich weitere Sensoren für eine detailliertere Auswertung. (JAZ / Taktung..)

## Aufgaben
- [x] Recherche: Welche Sensoren sind sinnvoll?
- [ ] Integration der neuen Sensoren in die Python-Komponente
- [ ] Anpassung der Dokumentation
- [ ] Erstellung von Unit-Tests für die neuen Sensoren

## Senorenliste
- JAZ (Berechnugn der Jahresarbeitszahl)
- COP gesamt (berechnet Wärmeenergie gesamt / Primärenergei gesamt)
- Taktungen
- Taktungen nach Anforderungsart (Heizen / WW)
- Stromverbrauch nach Anforderungsart (Heizen / WW)
- täglich, monatliche / jährlicher Stromverbrauch / WärmeMende / COP
- ...

## Akzeptanzkriterien
- Die neuen Sensoren erscheinen in Home Assistant als eigene Entitäten.
- alle Sensoren sind "dynamisch", werden nach Anzahl der Geräte erzeugt, wenn notwendig (mehrere heizkreise)
- Alle Sensoren sind dokumentiert.
- Es existieren Unit-Tests für jede neue Sensor-Integration.

## Status
- Feature-Branch angelegt
- Erste Sensoren integriert (siehe commits)
- Dokumentation wird aktualisiert

## ToDo
- Weitere Sensoren prüfen und ergänzen
- Tests schreiben und ausführen
- Review/Code-Review anfragen
