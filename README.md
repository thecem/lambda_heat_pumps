# Lambda Wärmepumpe Integration für Home Assistant / Lambda Heat Pump Integration for Home Assistant

---

## Deutsch

Diese benutzerdefinierte Integration ermöglicht die Einbindung von Lambda Wärmepumpen in Home Assistant über das Modbus/TCP Protokoll. Sie liest Sensordaten aus und ermöglicht die Steuerung von Klima-Entitäten (z.B. Warmwasser, Heizkreis).

**Features:**
- Auslesen diverser Sensoren der Wärmepumpe (Temperaturen, Zustände, Energieverbrauch etc.)
- Steuerung der Zieltemperatur für Warmwasser und Heizkreise über `climate`-Entitäten
- Dynamische Anpassung der Sensoren und Entitäten basierend auf der Firmware-Version und der konfigurierten Anzahl von Wärmepumpen, Boilern, Heizkreisen, Pufferspeichern und Solarmodulen
- Zentrale, konsistente Filterung aller Sensoren/Entitäten nach Firmware-Version (utils.py)
- Raumthermostatsteuerung: Verwendung externer Temperatursensoren für jeden Heizkreis
- Konfigurierbarer Update-Intervall
- **Firmware-Version, Temperaturbereiche und Schritte sind jederzeit im Options-Dialog änderbar**
- **Debug-Logging beim Speichern der Konfiguration/Optionen**
- Konfiguration vollständig über die Home Assistant UI (Integrations)

**manuelle Installation:**
1. Kopieren Sie den gesamten Ordner `custom_components/lambda_heat_pumps` in Ihren `custom_components` Ordner innerhalb Ihres Home Assistant Konfigurationsverzeichnisses.
2. Starten Sie Home Assistant neu.

Eine weitergehende Beschreibung der Installation und Konfiguration ist hier zu finden: https://homeassistant.com.de/homeassistant/lambda-waermepumpe-integration-fuer-home-assistant/


**Konfiguration:**
- Integration über die Home Assistant UI hinzufügen (`Einstellungen` → `Geräte & Dienste` → `Integration hinzufügen` → "Lambda Heat Pumps")
- Geben Sie Name, Host, Port, Slave ID, Firmware-Version und die Anzahl der Wärmepumpen, Boiler, Heizkreise, Pufferspeicher und Solarmodule an
- **Für Wärmepumpen kann die Anzahl flexibel zwischen 1 und 3 gewählt werden.**
- **Für Boiler zwischen 0 und 5, für Heizkreise zwischen 0 und 12, für Puffer zwischen 0 und 5, für Solarmodule zwischen 0 und 2.**
- Optional: Aktivieren Sie die Raumthermostatsteuerung, um externe Temperatursensoren für jeden Heizkreis zu verwenden
- Die Option **"Modbus-Namen verwenden"** (`use_legacy_modbus_names`): Wenn aktiviert, werden die originalen Modbus-Namen für Sensoren und Entitäten verwendet. Dies ist nützlich, wenn Sie eigene Namenszuweisungen in der `lambda_wp_config.yaml` nutzen möchten oder Kompatibilität zu älteren Setups benötigen. Ist die Option deaktiviert, werden die standardisierten Namen der Integration verwendet. Die alte Lösung und Beispiele finden Sie unter: https://github.com/GuidoJeuken-6512/HomeAssistant/tree/main
- **Wichtig:** Wenn Sie zuvor die alte Lösung genutzt haben und Ihre historischen Werte (Entity-IDs) behalten möchten, müssen Sie diese Option aktivieren, damit die alten Namen weiterverwendet werden und Ihre Daten erhalten bleiben.
- Nach der Einrichtung können Temperaturbereiche, Firmware-Version und Update-Intervall **jederzeit** über die Optionen angepasst werden

**Hinweis zu Temperatur-Min/Max-Werten und Schritten:**
Die Minimal- und Maximalwerte für Warmwasser und Heizkreis sowie die Schrittweite werden direkt im Options-Dialog der Integration (über die Home Assistant UI) gesetzt. Diese Werte sind **nicht** in der `lambda_wp_config.yaml` zu konfigurieren, sondern werden im Dialog der Integration (config_flow) gepflegt und können dort jederzeit geändert werden.

**Deaktivierte Register (ab Version 2025.x):**

Das gezielte Deaktivieren von Modbus-Registern erfolgt jetzt komfortabel über die Datei `lambda_wp_config.yaml` im Home Assistant Konfigurationsverzeichnis. Dies ist nützlich, wenn bestimmte Sensoren in Ihrer Wärmepumpen-Konfiguration nicht vorhanden sind oder Fehler verursachen.

**Vorgehen:**
1. Beobachten Sie die Home Assistant Logs auf Modbus-Fehler (z.B. "Modbus error for ... (address: 1234)")
2. Öffnen Sie die Datei `lambda_wp_config.yaml` (wird beim ersten Start der Integration automatisch angelegt)
3. Tragen Sie die zu deaktivierenden Register-Adressen in die Liste `disabled_registers` ein:

```yaml
disabled_registers:
  - 1234  # sensor_name
  - 1235  # another_sensor_name
```

4. Speichern Sie die Datei und starten Sie Home Assistant neu, oder laden Sie die Integration neu.

**Hinweis:**
- Die Datei kann auch genutzt werden, um Sensor-Namen gezielt zu überschreiben (siehe Kommentare in der Datei).


**Raumthermostatsteuerung & Modbus-Schreibvorgang (Kurzfassung):**
- Externe Temperatursensoren können für jeden Heizkreis ausgewählt werden (Dropdown, nur Fremdsensoren mit device_class 'temperature').
- Die Integration schreibt die gemessenen Werte automatisch und regelmäßig in die Modbus-Register der Heizkreise.
- Das Schreiben erfolgt über die Service-Funktion in `services.py` und kann auch manuell per Service-Aufruf ausgelöst werden.

**Firmware- und Sensor-Handling:**
- Die Firmware-Version kann nachträglich im Options-Dialog geändert werden und triggert ein vollständiges Reload (inkl. Filterung der Sensoren)
- Sensoren und Entitäten werden **zentral** nach Firmware gefiltert (siehe `utils.py`)
- Initialwerte für Sensoren (z.B. Dummy) können in const.py gesetzt werden

**Hinweise für Home Assistant 2025.3:**
- Diese Integration ist vollständig kompatibel mit Home Assistant 2025.3 ff
- Verwendet den neuen DataUpdateCoordinator für optimale Leistung
- Typisierung und async/await nach den neuesten Standards
- Verbesserte Fehlerbehandlung und Logging
- Moderne Konfigurations- und Options-Flows

**Debugging:**
- Im Debug-Mode werden die geschriebenen Werte im Home Assistant Log (DEBUG) ausgegeben

**Bekannte Probleme:**
- Die Übersetzung in andere Sprachen (außer Deutsch und Englisch)
- Die Zuordnung von Sensoren zu Firmware-Ständen ist nicht korrekt

**Haftungsausschluss/Disclaimer:**

Die Nutzung dieser Software erfolgt auf eigene Gefahr. Es wird keine Haftung für Schäden, Datenverluste oder sonstige Folgen übernommen, die durch die Verwendung der Software entstehen. Jeglicher Regressanspruch ist ausgeschlossen.

---

## English

This custom integration allows you to connect Lambda heat pumps to Home Assistant via the Modbus/TCP protocol. It reads sensor data and enables control of climate entities (e.g., hot water, heating circuit).

**Features:**
- Reads various heat pump sensors (temperatures, states, energy consumption, etc.)
- Control of target temperature for hot water and heating circuits via `climate` entities
- Dynamic adaptation of sensors and entities based on firmware version and configured number of heat pumps, boilers, heating circuits, buffer tanks, and solar modules
- Central, consistent filtering of all sensors/entities by firmware version (utils.py)
- Room thermostat control: Use external temperature sensors for each heating circuit
- Configurable update interval
- **Firmware version, temperature ranges and steps can be changed at any time in the options dialog**
- **Debug logging when saving configuration/options**
- Configuration fully via the Home Assistant UI (Integrations)

**Installation:**
1. Copy the entire `custom_components/lambda_heat_pumps` folder into your `custom_components` directory inside your Home Assistant configuration folder.
2. Restart Home Assistant.
A more detailed description of the installation and configuration can be found here: https://homeassistant.com.de/homeassistant/lambda-waermepumpe-integration-fuer-home-assistant/

**Configuration:**
- Add the integration via the Home Assistant UI (`Settings` → `Devices & Services` → `Add Integration` → "Lambda WP")
- Enter name, host, port, slave ID, firmware version, and the number of heat pumps, boilers, heating circuits, buffer tanks, and solar modules
- **For heat pumps, the number can be set flexibly between 1 and 3.**
- **For boilers between 0 and 5, for heating circuits between 0 and 12, for buffers between 0 and 5, and for solar modules between 0 and 2.**
- Optional: Enable room thermostat control to use external temperature sensors for each heating circuit
- The option **"Use legacy Modbus names"** (`use_legacy_modbus_names`): If enabled, the original Modbus names are used for sensors and entities. This is useful if you want to use your own name assignments in `lambda_wp_config.yaml` or need compatibility with older setups. If disabled, the integration's standardized names are used. The old solution and examples can be found at: https://github.com/GuidoJeuken-6512/HomeAssistant/tree/main
- **Important:** If you previously used the old solution and want to keep your historical values (entity IDs), you must enable this option so that the old names are used and your data is preserved.
- After setup, temperature ranges, firmware version and update interval can be **changed at any time** via the options

**Note on temperature min/max values and steps:**
The minimum and maximum values for hot water and heating circuit, as well as the step size, are set directly in the options dialog of the integration (via the Home Assistant UI). These values are **not** to be configured in the `lambda_wp_config.yaml`, but are maintained in the integration dialog (config_flow) and can be changed there at any time.

**Disabled Registers (since version 2025.x):**

You can now conveniently disable specific Modbus registers via the `lambda_wp_config.yaml` file in your Home Assistant configuration directory. This is useful if certain sensors are not present in your heat pump configuration or cause errors.

**How to:**
1. Watch the Home Assistant logs for Modbus errors (e.g. "Modbus error for ... (address: 1234)")
2. Open the file `lambda_wp_config.yaml` (it is created automatically on first start of the integration)
3. Add the register addresses to be disabled to the `disabled_registers` list:

```yaml
disabled_registers:
  - 1234  # sensor_name
  - 1235  # another_sensor_name
```

4. Save the file and restart Home Assistant or reload the integration.

**Note:**
- The file can also be used to override sensor names (see comments in the file).
- The old method with a separate `disabled_registers.yaml` is deprecated and no longer supported.

**Room thermostat control & Modbus write process (short version):**
- External temperature sensors can be selected for each heating circuit (dropdown, only non-integration sensors with device_class 'temperature').
- The integration automatically and regularly writes the measured values to the Modbus registers of the heating circuits.
- Writing is handled by the service function in `services.py` and can also be triggered manually via a service call.

**Firmware and Sensor Handling:**
- The firmware version can be changed later in the options dialog and triggers a full reload (including filtering of sensors)
- Sensors and entities are **centrally** filtered by firmware (see `utils.py`)
- Initial values for sensors (e.g. dummy) can be set in const.py

**Notes for Home Assistant 2025.3:**
- This integration is fully compatible with Home Assistant 2025.3 ff
- Uses the new DataUpdateCoordinator for optimal performance
- Typing and async/await according to the latest standards
- Improved error handling and logging
- Modern configuration and options flows

**Debugging:**
- in debug mode the written values are output to the Home Assistant log (DEBUG)

**Known Issues:**
- Translation to other languages (besides German and English)
- the assignment of sensors to firmware stands is not correct

---

*Diese Integration wird nicht offiziell von Lambda unterstützt. / This integration is not officially supported by Lambda.*

---

## Modbus Test-Tools (Server & Client)

Für Entwicklung und Test der Integration steht ein separates Repository mit Modbus-Testtools zur Verfügung:

**GitHub:** [https://github.com/GuidoJeuken-6512/modbus_tools](https://github.com/GuidoJeuken-6512/modbus_tools)

**Enthalten:**
- Ein einfacher Modbus TCP Server (`server.py`), der Register aus einer YAML-Datei bereitstellt (ideal zum Mocken der Wärmepumpe)
- Ein grafischer Modbus TCP Client (`modbus_client.py`) zum Testen und Debuggen von Registerzugriffen

**Kurzanleitung:**
1. Repository klonen: `git clone https://github.com/GuidoJeuken-6512/modbus_tools`
2. In das Verzeichnis wechseln: `cd modbus_tools`
3. Server starten: `python server.py` (Register werden aus `config/registers.yaml` geladen)
4. Client starten: `python modbus_client.py` (GUI zum Lesen/Schreiben von Registern)

Weitere Details und Konfigurationsmöglichkeiten finden sich im README des Repositories und in den jeweiligen Python-Dateien.

---

**Haftungsausschluss/Disclaimer:**

Use of this software is at your own risk. No liability is accepted for any damages, data loss, or other consequences resulting from the use of this software. Any claims for compensation are excluded.

---
