# Lambda Heat Pumps - Quick Start Guide

This quick start guide will help you get up and running with the Lambda Heat Pumps integration for Home Assistant.

## Installation

1. Copy the `lambda_heat_pumps` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Navigate to Configuration → Integrations → Add Integration
4. Search for "Lambda Heat Pumps" and select it

## Initial Configuration

When setting up the integration, you will need to provide:

- **Name**: A name for your Lambda Heat Pump installation (e.g., "Main Heat Pump")
- **Host**: IP address or hostname of your Lambda controller
- **Port**: Modbus TCP port (default: 502)
- **Slave ID**: Modbus Slave ID (default: 1)
- **Number of devices**: Configure how many of each device type you have:
  - Heat Pumps (1-3)
  - Boilers (0-5)
  - Heating Circuits (0-12)
  - Buffers (0-5)
  - Solar Systems (0-2)
- **Firmware Version**: Select your Lambda controller's firmware version

## Integration Options

After initial setup, you can modify additional settings in the integration options:

1. Go to Configuration → Integrations
2. Find your Lambda Heat Pump integration and click "Configure"
3. Here you can adjust:
   - Hot water temperature range (min/max)
   - Heating circuit temperature range (min/max)
   - Temperature step size
   - Room thermostat control (using external sensors)

## Using Room Temperature Sensors

If you want to use external temperature sensors for your heating circuits:

1. In integration options, enable "Room thermostat control"
2. Select temperature sensors for each heating circuit
3. The integration will periodically update your Lambda controller with the measured room temperatures

## Disabling Problematic Registers / Deaktivieren problematischer Register

If certain Modbus registers cause issues or errors, you can disable them:

1. Edit the `disabled_registers.yaml` file in the integration directory
2. Add the register addresses you want to disable in the `disabled_registers:` list:
   ```yaml
   disabled_registers:
     - 2004  # boil1_actual_circulation_temp
     - 2005  # boil1_actual_circulation_pump_state
     - 5204  # hc3_flow_line_temp
   ```
3. Add comments after each register to help identify them later
4. Restart Home Assistant or reload the integration

The disabled registers will be skipped during communication with the Lambda controller. This is useful when certain registers are not supported or cause errors.

### Warum Register deaktivieren?

Die Deaktivierung bestimmter Register kann in folgenden Fällen sinnvoll sein:

- Wenn bestimmte Sensoren nicht an Ihren Lambda Controller angeschlossen sind
- Bei Kommunikationsfehlern mit einzelnen Registern
- Wenn bestimmte Register in Ihrer Firmware-Version nicht unterstützt werden
- Um den Netzwerkverkehr zu reduzieren, wenn Sie bestimmte Informationen nicht benötigen

Dies erhöht die Stabilität der Integration und reduziert unnötige Kommunikation mit der Wärmepumpe.

## Dynamische Geräteverwaltung / Dynamic Device Management

Bei der Konfiguration der Integration werden die Anzahl der vorhandenen Geräte jedes Typs angegeben. Die Integration erstellt dann automatisch die entsprechenden Entitäten für jedes konfigurierte Gerät:

### Multiple Heat Pumps (Wärmepumpen)

Wenn Sie mehrere Wärmepumpen konfiguriert haben (bis zu 3):
- Für jede Wärmepumpe werden separate Sensoren erstellt
- Die Entitäts-IDs enthalten den Index der Wärmepumpe (z.B. `sensor.lambda_hp1_flow_line_temperature`, `sensor.lambda_hp2_flow_line_temperature`)
- Jede Wärmepumpe hat ihre eigenen Betriebszustände und Fehlerstatusanzeigen
- Die Register-Adressen werden automatisch entsprechend dem Index berechnet (z.B. 1004, 1104, 1204)

### Multiple Heating Circuits (Heizkreise)

Wenn Sie mehrere Heizkreise konfiguriert haben (bis zu 12):
- Jeder Heizkreis wird als separate Climate-Entität erstellt
- Die Entitäts-IDs enthalten den Index des Heizkreises (z.B. `climate.lambda_hc1`, `climate.lambda_hc2`)
- Jeder Heizkreis kann individuell gesteuert werden (Temperaturregelung, Betriebsmodus)
- Zusätzliche Sensoren werden für Vorlauf- und Rücklauftemperatur jedes Heizkreises erstellt

### Multiple Boilers (Warmwasserboiler)

Wenn Sie mehrere Boiler konfiguriert haben (bis zu 5):
- Jeder Boiler wird als separate Climate-Entität erstellt
- Die Entitäts-IDs enthalten den Index des Boilers (z.B. `climate.lambda_boil1`, `climate.lambda_boil2`)
- Für jeden Boiler werden Sensoren für obere und untere Temperatur, sowie Zirkulation erstellt (sofern nicht deaktiviert)
- Die Warmwassertemperatur kann für jeden Boiler individuell eingestellt werden

### Multiple Buffer Tanks (Pufferspeicher)

Wenn Sie mehrere Pufferspeicher konfiguriert haben (bis zu 5):
- Für jeden Pufferspeicher werden separate Sensoren erstellt
- Die Entitäts-IDs enthalten den Index des Pufferspeichers (z.B. `sensor.lambda_buffer1_high_temp`, `sensor.lambda_buffer2_high_temp`)

### Multiple Solar Systems (Solaranlagen)

Wenn Sie mehrere Solaranlagen konfiguriert haben (bis zu 2):
- Für jede Solaranlage werden separate Sensoren erstellt
- Die Entitäts-IDs enthalten den Index der Solaranlage (z.B. `sensor.lambda_solar1_collector_temp`, `sensor.lambda_solar2_collector_temp`)

Die Integration passt die Modbus-Register-Adressen automatisch an die konfigurierten Geräte an. Die Register-Struktur folgt dem in der Modbus-Dokumentation beschriebenen Schema.

### Register-Struktur und Geräteindizes

Die Register-Adressen für die verschiedenen Geräte werden nach folgendem Schema berechnet:

```
XYYZ
```

Dabei ist:
- **X**: Der Gerätetyp (1 = Wärmepumpe, 2 = Boiler, 3 = Pufferspeicher, 4 = Solar, 5 = Heizkreis)
- **YY**: Der Geräteindex (0-basiert) innerhalb des Typs
- **Z**: Die Registeradresse innerhalb des Geräts

Beispiele:
- Register `1004`: Vorlauftemperatur der ersten Wärmepumpe (HP0)
- Register `1104`: Vorlauftemperatur der zweiten Wärmepumpe (HP1)
- Register `5002`: Vorlauftemperatur des ersten Heizkreises (HC0)
- Register `5102`: Vorlauftemperatur des zweiten Heizkreises (HC1)

Wichtig: In der Benutzeroberfläche werden die Geräte mit 1-basierten Indizes angezeigt (HP1, HC1), während die Register-Adressen 0-basierte Indizes verwenden!

Wenn Sie problematische Register in `lambda_wp_config.yaml` deaktivieren, achten Sie darauf, die korrekte Register-Adresse zu verwenden.

## Troubleshooting / Fehlerbehebung

If you encounter issues:

- Check your network connection to the Lambda controller
- Verify that the Modbus TCP port is accessible (default: 502)
- Check the Home Assistant logs for specific error messages
- Ensure your firmware version is correctly selected
- Try disabling problematic registers if you see consistent errors

### Typische Fehler bei der Modbus-Kommunikation

Bei Problemen mit der Modbus-Kommunikation können folgende Fehler in den Logs erscheinen:

```
ModbusIOException: [Input/Output] Error/Exception communicating with Tcp
Failed to update data from Lambda controller: [Input/Output] Connection Error
Read error: [Input/Output] Exception communicating with Tcp
```

Diese Fehler können auftreten, wenn:
- Der Lambda Controller nicht erreichbar ist
- Die Netzwerkverbindung unterbrochen wurde
- Ein oder mehrere Register nicht verfügbar sind (diese können deaktiviert werden)
- Der Lambda Controller zu viele gleichzeitige Anfragen erhält

## Optimierung der Performance / Performance Optimization

### Optimierung der Abfrageintervalle

Die Anzahl der konfigurierten Geräte beeinflusst direkt die Menge der Modbus-Register, die abgefragt werden müssen:

- Jede Wärmepumpe fügt etwa 20 Register hinzu
- Jeder Heizkreis fügt etwa 10 Register hinzu
- Jeder Boiler fügt etwa 6 Register hinzu
- Jeder Pufferspeicher fügt etwa 10 Register hinzu
- Jede Solaranlage fügt etwa 6 Register hinzu

Bei größeren Installationen mit vielen Geräten kann es sinnvoll sein, das Scan-Intervall zu erhöhen (z.B. auf 45 oder 60 Sekunden), um die Netzwerkbelastung zu reduzieren und Timeouts zu vermeiden. Dies kann in der `configuration.yaml` eingestellt werden:

```yaml
lambda_heat_pumps:
  scan_interval: 45  # Abfrageintervall in Sekunden (Standard: 30)
```

Für viele Heizkreise (z.B. 8 oder mehr) empfehlen wir ein Scan-Intervall von mindestens 45 Sekunden.

Tipp: Deaktivieren Sie Register von Sensoren, die Sie nicht benötigen, um die Anzahl der Modbus-Abfragen zu reduzieren.

## Modbus Register Services

The integration provides two additional Home Assistant services for advanced users:
- `lambda_heat_pumps.read_modbus_register`: Read any Modbus register from the Lambda controller.
- `lambda_heat_pumps.write_modbus_register`: Write a value to any Modbus register of the Lambda controller.

You can use these services via the Developer Tools → Services UI. See the main documentation for details and examples.

## Dynamic Entity Creation

- Heating circuit climate entities are only created if a room thermostat sensor is configured for the respective circuit in the integration options.
- Boiler and other device entities are created based on the configured device count.

## Template-based Climate Entities

- All climate entities (boiler, heating circuit) are now defined by templates in `const.py`.
- This makes it easy to extend or adjust entity properties centrally.

## Next Steps

Once your integration is running:
- Create automations based on temperature readings
- Set up notifications for error states
- Use the climate entities to control your heating and hot water
- Create dashboards with temperature graphs and status information

For advanced configuration and complete entity reference, see the full documentation.
