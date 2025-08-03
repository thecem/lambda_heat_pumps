# TODO: Option C Migration Implementation

## Übersicht
Implementierung einer intelligenten Migration (Option C), die basierend auf der ursprünglichen `use_legacy_names` Einstellung unterschiedliche Migrationsstrategien anwendet und alle Konfigurationen einzeln abarbeitet.

## Ziel
- Historische Daten erhalten
- Konsistenz zwischen Entity-ID und unique_id herstellen
- Alle Konfigurationen korrekt migrieren
- Zukunftssicherheit durch einheitliches Legacy-Format

---

## Phase 1: Analyse und Vorbereitung

### 1.1 Bestehende Migration analysieren
- [ ] Aktuelle `migration.py` verstehen
- [ ] Identifizieren, wo `use_legacy_names` Einstellung gelesen wird
- [ ] Mapping zwischen Entity-ID und unique_id Logik verstehen
- [ ] Duplikat-Erkennung Logik verstehen

### 1.2 Test-Szenarien definieren
- [ ] Test für `use_legacy_names = True` (Version 1)
- [ ] Test für `use_legacy_names = False` (Version 1)
- [ ] Test für mehrere Konfigurationen
- [ ] Test für gemischte Szenarien (einige True, einige False)

### 1.3 Backup-Strategie planen
- [ ] Entity Registry Backup vor Migration
- [ ] Config Entry Backup vor Migration
- [ ] Rollback-Mechanismus definieren

---

## Phase 2: Migration Logic erweitern

### 2.1 Config Entry Analyse
- [ ] Funktion zum Lesen aller Config Entries für Lambda Heat Pumps
- [ ] Funktion zum Identifizieren der `use_legacy_names` Einstellung
- [ ] Funktion zum Gruppieren von Configs nach Legacy-Status

### 2.2 Intelligente Migration implementieren
- [ ] `_perform_migration` erweitern um Legacy-Erkennung
- [ ] Separate Funktionen für Legacy- und Non-Legacy-Migration
- [ ] Entity-ID vs unique_id Konsistenz-Logik

#### 2.2.1 Legacy Migration (`use_legacy_names = True`)
- [ ] Entity-IDs bleiben im Legacy-Format
- [ ] Unique-IDs bleiben im Legacy-Format
- [ ] Keine Änderungen an bestehenden Entities

#### 2.2.2 Non-Legacy Migration (`use_legacy_names = False`)
- [ ] Entity-IDs bleiben unverändert (für Daten-Erhaltung)
- [ ] Unique-IDs werden korrigiert (ohne name_prefix)
- [ ] Konsistenz zwischen Entity-ID und unique_id herstellen

### 2.3 Config Entry Update
- [ ] Alle Config Entries auf `use_legacy_names = True` setzen
- [ ] Version auf 2 aktualisieren
- [ ] Backup der ursprünglichen Einstellungen

---

## Phase 3: Multi-Config Support

### 3.1 Config Discovery
- [ ] Funktion zum Finden aller Lambda Heat Pump Configs
- [ ] Funktion zum Gruppieren nach Legacy-Status
- [ ] Funktion zum Validieren der Config-Integrität

### 3.2 Sequenzielle Migration
- [ ] Migration pro Config Entry
- [ ] Fehlerbehandlung pro Config
- [ ] Fortschritts-Tracking
- [ ] Rollback bei Fehlern

### 3.3 Batch-Processing
- [ ] Alle Configs in einem Durchgang migrieren
- [ ] Atomic-Operation für alle Configs
- [ ] Teilweise Migration verhindern

---

## Phase 4: Entity Registry Migration

### 4.1 Entity Analysis
- [ ] Funktion zum Analysieren aller Entities pro Config
- [ ] Identifizierung von Inkonsistenzen
- [ ] Duplikat-Erkennung verbessern

### 4.2 Migration Rules
- [ ] **Legacy Entities** (`use_legacy_names = True`):
  - Entity-ID: `sensor.eu08l_ambient_temp` → bleibt gleich
  - Unique-ID: `eu08l_ambient_temp` → bleibt gleich
  - Aktion: Keine Änderung

- [ ] **Non-Legacy Entities** (`use_legacy_names = False`):
  - Entity-ID: `sensor.ambient_temp` → bleibt gleich (Daten-Erhaltung)
  - Unique-ID: `ambient_temp` → bleibt gleich (Konsistenz)
  - Aktion: Nur korrigieren wenn inkonsistent

### 4.3 Climate Entity Handling
- [ ] Separate Logik für Climate-Entities
- [ ] Legacy Climate-Entities: `climate.eu08l_boil1_hot_water`
- [ ] Non-Legacy Climate-Entities: `climate.hot_water_1`
- [ ] Entfernung inkompatibler Climate-Entities

---

## Phase 5: Error Handling und Logging

### 5.1 Migration Status Tracking
- [ ] Migration-Status pro Config Entry
- [ ] Erfolg/Fehler-Tracking
- [ ] Rollback-Informationen

### 5.2 Error Recovery
- [ ] Timeout-Handling (30 Sekunden)
- [ ] Entity Registry Fehler
- [ ] Config Entry Fehler
- [ ] Teilweise Migration Recovery

### 5.3 Logging
- [ ] Detaillierte Logs für jede Migration
- [ ] Erfolgs-/Fehler-Statistiken
- [ ] Benutzer-freundliche Meldungen

---

## Phase 6: Testing

### 6.1 Unit Tests
- [ ] Test für Legacy Migration
- [ ] Test für Non-Legacy Migration
- [ ] Test für Multi-Config Migration
- [ ] Test für Error Cases

### 6.2 Integration Tests
- [ ] Test mit echten Entity Registry Daten
- [ ] Test mit verschiedenen Config-Szenarien
- [ ] Test für Rollback-Mechanismus

### 6.3 Edge Cases
- [ ] Test mit leeren Configs
- [ ] Test mit beschädigten Configs
- [ ] Test mit gemischten Entity-Formaten

---

## Phase 7: Dokumentation

### 7.1 Migration Guide
- [ ] Dokumentation der Migration-Logik
- [ ] Benutzer-Anleitung für Migration
- [ ] Troubleshooting Guide

### 7.2 Changelog Updates
- [ ] Migration-Details im CHANGELOG
- [ ] Breaking Changes dokumentieren
- [ ] Upgrade-Anweisungen

---

## Implementierungsreihenfolge

1. **Phase 1**: Analyse und Vorbereitung
2. **Phase 2**: Grundlegende Migration Logic
3. **Phase 3**: Multi-Config Support
4. **Phase 4**: Entity Registry Migration
5. **Phase 5**: Error Handling
6. **Phase 6**: Testing
7. **Phase 7**: Dokumentation

---

## Risiken und Mitigation

### Risiko: Datenverlust
- **Mitigation**: Entity-IDs bleiben unverändert, Backup vor Migration

### Risiko: Inkonsistente States
- **Mitigation**: Atomic-Operationen, Rollback-Mechanismus

### Risiko: Timeout bei großen Installationen
- **Mitigation**: Timeout-Handling, Fortschritts-Tracking

### Risiko: Automatisierungen brechen
- **Mitigation**: Entity-IDs bleiben gleich, nur unique_ids werden korrigiert

---

## Erfolgskriterien

- [ ] Alle Configs werden korrekt migriert
- [ ] Historische Daten bleiben erhalten
- [ ] Entity-ID und unique_id sind konsistent
- [ ] Keine Datenverluste
- [ ] Automatisierungen funktionieren weiter
- [ ] Alle Tests bestehen
- [ ] Dokumentation ist vollständig 