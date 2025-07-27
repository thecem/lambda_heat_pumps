# Lambda Heat Pumps Migration Guide

## Übersicht

Nach dem Update der Lambda Heat Pumps Integration können doppelte Sensoren mit "_2" Suffix auftreten. Diese Anleitung bietet verschiedene Lösungsansätze.

## Problem

Die Integration verwendet jetzt konsistente `unique_id`-Generierung, was zu Duplikaten führen kann:
- **Alte General-Sensoren**: `unique_id` ohne Config-Name
- **Neue General-Sensoren**: `unique_id` mit Config-Name
- **Climate-Entities**: Verschiedene `unique_id`-Formate
- **Cycling-Sensoren**: Inkonsistente Formate

## Lösungsoptionen

### Option 1: Automatische Migration (Empfohlen für bestehende Installationen)

**Vorteile:**
- ✅ Behält alle historischen Daten
- ✅ Automatisierungen bleiben erhalten
- ✅ Dashboards funktionieren weiter
- ✅ Minimaler Aufwand

**Schritte:**
1. Update der Integration installieren
2. Home Assistant neu starten
3. Die Integration führt automatische Migration durch
4. Überprüfe die Logs für Migration-Nachrichten

**Erwartete Log-Nachrichten:**
```
General sensor migration completed: updated X unique_ids
Climate entity migration completed: updated X unique_ids
Cycling sensor migration completed: updated X unique_ids
Migration completed: removed X duplicate entities
```

### Option 2: Manuelle Bereinigung (Für fortgeschrittene Benutzer)

**Vorteile:**
- ✅ Vollständige Kontrolle über den Prozess
- ✅ Backup vor jeder Änderung
- ✅ Detaillierte Protokollierung

**Schritte:**
1. Führe das Bereinigungsskript aus:
   ```bash
   python3 cleanup_entity_registry.py
   ```
2. Starte Home Assistant neu
3. Überprüfe die Ergebnisse

### Option 3: Sauberer Neustart (Für neue Installationen oder bei Problemen)

**Vorteile:**
- ✅ Garantiert keine Duplikate
- ✅ Einfachster Ansatz
- ✅ Keine komplexe Migration

**Nachteile:**
- ❌ Verlust aller historischen Daten
- ❌ Automatisierungen müssen neu erstellt werden
- ❌ Dashboards müssen neu konfiguriert werden

**Schritte:**
1. **Backup erstellen** (wichtig!)
2. Integration aus der Konfiguration entfernen
3. Home Assistant neu starten
4. Integration neu hinzufügen
5. Automatisierungen und Dashboards neu konfigurieren

## Empfehlung nach Benutzertyp

### Für bestehende Installationen mit wichtigen Daten:
**Option 1: Automatische Migration**

### Für Installationen mit Problemen:
**Option 2: Manuelle Bereinigung**

### Für neue Installationen oder Testumgebungen:
**Option 3: Sauberer Neustart**

## Troubleshooting

### Migration schlägt fehl
1. Überprüfe die Logs auf Fehlermeldungen
2. Verwende Option 2 (Manuelle Bereinigung)
3. Bei anhaltenden Problemen: Option 3 (Sauberer Neustart)

### Duplikate bleiben bestehen
1. Starte Home Assistant neu
2. Überprüfe, ob die Migration in den Logs aufgeführt ist
3. Verwende das manuelle Bereinigungsskript

### Performance-Probleme
1. Überprüfe die Anzahl der Entities in der Registry
2. Entferne nicht verwendete Entities
3. Verwende Option 3 bei schwerwiegenden Problemen

## Backup-Strategie

**Vor jeder Migration:**
1. Backup der Konfiguration erstellen
2. Backup der Entity Registry erstellen
3. Screenshots von wichtigen Dashboards machen

**Backup-Befehle:**
```bash
# Konfiguration
cp -r /path/to/config /path/to/backup/config_$(date +%Y%m%d_%H%M%S)

# Entity Registry
cp /path/to/config/.storage/core.entity_registry /path/to/backup/core.entity_registry_$(date +%Y%m%d_%H%M%S)
```

## Support

Bei Problemen mit der Migration:
1. Überprüfe die Logs auf Fehlermeldungen
2. Erstelle ein Issue im GitHub Repository
3. Füge Logs und Entity Registry Ausschnitte hinzu 