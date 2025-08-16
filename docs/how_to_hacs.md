# Wichtige Vorgaben und Guidelines für HACS und brands

Damit dein PR schnell akzeptiert wird, halte dich an folgende Vorgaben:

- Das Repository muss öffentlich sein und die Integration im Verzeichnis `custom_components/<domain>` liegen.
- Pflichtdateien: `manifest.json`, `__init__.py`, ggf. `config_flow.py`, `translations/`, `README.md` (englisch), evtl. weitere Python-Dateien.
- `manifest.json` muss alle Pflichtfelder enthalten: `domain`, `name`, `version`, `documentation`, `requirements`, `dependencies`, `codeowners` (dein GitHub-Handle).
- Die Domain in `manifest.json` muss mit dem Verzeichnisnamen übereinstimmen.
- README.md: Englische Anleitung, Installations- und Konfigurationshinweise.
- Brand-Logo: PNG, 256x256px, transparent, quadratisch, im brands-Repo unter `custom_integrations/<domain>/icon.png` per PR einreichen.
- Code sollte PEP8-konform und fehlerfrei sein (nutze z.B. flake8/pylint).
- Jede Änderung am Code erfordert eine neue Version in `manifest.json` (semantische Versionierung).
- Tests sind empfohlen, aber nicht zwingend. Wenn vorhanden, im Verzeichnis `tests/` und pytest-kompatibel.
- Keine privaten/sensiblen Daten, keine Werbung oder Tracking im Code.
- Die Integration darf keine Abhängigkeiten enthalten, die gegen Home Assistant- oder HACS-Richtlinien verstoßen.

**Offizielle Quellen:**
- [HACS Publish Guide](https://hacs.xyz/docs/publish/start)
- [HACS include checklist](https://hacs.xyz/docs/publish/include)
- [brands-Repo (Logo)](https://github.com/home-assistant/brands)
- [HACS Integration Repo](https://github.com/hacs/integration)

--- 

# Schritt-für-Schritt-Anleitung: Integration in den offiziellen HACS Store

## 1. Repository vorbereiten
- Stelle sicher, dass dein GitHub-Repository öffentlich ist.
- Die Integration muss im Verzeichnis `custom_components/<dein_domain_name>` liegen (z.B. `custom_components/lambda_heat_pumps`).
- Die wichtigsten Dateien:
  - `manifest.json`
  - `__init__.py`
  - `config_flow.py`
  - `translations/`
  - `README.md`
  - ggf. weitere Python-Dateien

## 2. manifest.json prüfen
- Die Datei muss ein valides JSON sein und alle Pflichtfelder enthalten (siehe [HACS Doku](https://hacs.xyz/docs/publish/include#manifestjson)).
- Beispiel:
  ```json
  {
    "domain": "lambda_heat_pumps",
    "name": "Lambda Heat Pumps",
    "version": "1.0.0",
    "documentation": "https://github.com/DEIN_GITHUB/lambda_heat_pumps",
    "requirements": [],
    "dependencies": [],
    "codeowners": ["@DEIN_GITHUB_USERNAME"]
  }
  ```

## 3. README.md und Doku
- Die README sollte eine englische Anleitung enthalten (deutsche Sektion ist optional).
- Installationsanleitung für HACS und Home Assistant beilegen.

## 4. Brand-Logo einreichen
- Erstelle ein PNG-Logo (256x256 Pixel, transparent, quadratisch).
- Forke das [brands-Repository](https://github.com/home-assistant/brands).
- Lege das Logo unter `custom_integrations/lambda_heat_pumps/icon.png` ab.
- Erstelle einen Pull Request im brands-Repo mit deinem Logo.

## 5. HACS-Repository einreichen
- Forke das [hacs/integration-Repository](https://github.com/hacs/integration).
- Öffne ein Issue oder einen Pull Request, um deine Integration hinzuzufügen:
  - Folge der Anleitung: https://hacs.xyz/docs/publish/include
  - Trage dein Repository in die Datei `default.json` ein (über einen PR).

## 6. Warten auf Review
- Die HACS-Maintainer prüfen deinen PR.
- Es kann sein, dass du noch kleine Änderungen vornehmen musst (Code, Manifest, Logo, Doku).

## 7. Nach Freigabe
- Deine Integration erscheint im offiziellen HACS Store unter "Integrationen".
- Nutzer können sie direkt über HACS suchen und installieren.

---

**Wichtige Links:**
- [HACS Publish Guide](https://hacs.xyz/docs/publish/start)
- [brands-Repo (Logo)](https://github.com/home-assistant/brands)
- [HACS Integration Repo](https://github.com/hacs/integration)

---

**Tipp:**
Halte dich genau an die Formatvorgaben und Guidelines von HACS und brands, damit dein PR schnell akzeptiert wird.


