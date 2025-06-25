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
