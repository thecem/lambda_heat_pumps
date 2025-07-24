# Changelog

## [1.1.0] - 2025-07-24

### 🚀 **Major Changes - Asynchronous Modbus Clients**

#### **Problem**
Die Lambda-Integration verursachte Konflikte mit der SolaX Modbus Integration aufgrund unterschiedlicher `pymodbus` Client-Typen:
- **Lambda**: Synchrone `ModbusTcpClient` 
- **SolaX**: Asynchrone `AsyncModbusTcpClient`
- **Ergebnis**: Inkompatibilität beim gleichzeitigen Betrieb

#### **Lösung: Vollständige Umstellung auf asynchrone Clients**
- **Alle Modbus-Operationen** auf `AsyncModbusTcpClient` umgestellt
- **Neue async Wrapper-Funktionen** in `modbus_utils.py` implementiert
- **Runtime API-Kompatibilität** für verschiedene `pymodbus` Versionen

### 📁 **Geänderte Dateien**

#### **`modbus_utils.py`**
```python
# Neue asynchrone Funktionen hinzugefügt:
async def async_read_holding_registers(client: AsyncModbusTcpClient, ...)
async def async_write_register(client: AsyncModbusTcpClient, ...)
async def async_write_registers(client: AsyncModbusTcpClient, ...)
async def async_read_input_registers(client: AsyncModbusTcpClient, ...)

# Runtime API-Kompatibilität für pymodbus 1.x, 2.x, 3.x
def _test_async_api_compatibility(client, method_name)
```

#### **`coordinator.py`**
- **Import**: `ModbusTcpClient` → `AsyncModbusTcpClient`
- **Verbindung**: `client.connect()` → `await client.connect()`
- **Schließung**: `client.close()` → `await client.close()`
- **Modbus-Operationen**: Direkte `await` Aufrufe statt `async_add_executor_job`

#### **`config_flow.py`**
- **Modbus-Test**: Vollständig auf asynchrone Clients umgestellt
- **Fehlerbehandlung**: Robuste `try-except` Blöcke für Client-Schließung

#### **`services.py`**
- **Alle Services**: Asynchrone Modbus-Operationen implementiert
- **Entfernt**: `async_add_executor_job` Wrapper

#### **`climate.py`**
- **Temperatur-Set**: Asynchrone Register-Schreiboperationen

### 🔧 **Bug Fixes**

#### **RuntimeWarning: Coroutine never awaited**
```python
# Vorher (falsch):
setup_cycling_automations(hass, entry.entry_id)  # async ohne await

# Nachher (korrekt):
setup_cycling_automations(hass, entry.entry_id)  # reguläre Funktion
```

#### **Callback-Funktionen korrigiert**
```python
# Vorher (falsch):
@callback
async def update_yesterday_sensors(now: datetime) -> None:

# Nachher (korrekt):
@callback
def update_yesterday_sensors(now: datetime) -> None:
```

### 🧹 **Code Quality Improvements**

#### **Linting-Probleme behoben**
- **Blank Lines**: Korrekte Anzahl von Leerzeilen
- **Whitespace**: Trailing whitespace entfernt
- **Zeilenlängen**: Auf 79 Zeichen reduziert (wichtige Dateien)
- **Imports**: Fehlende Imports hinzugefügt

#### **Funktionssignaturen korrigiert**
```python
# Vorher:
def setup_debug_logging(config: ConfigType)

# Nachher:
def setup_debug_logging(hass: HomeAssistant, config: ConfigType)
```

### 📊 **Technische Details**

#### **Modbus API-Kompatibilität**
Die Integration unterstützt jetzt automatisch verschiedene `pymodbus` Versionen:

| pymodbus Version | Parameter | Beispiel |
|------------------|-----------|----------|
| 1.x | Keine | `client.read_holding_registers(address, count)` |
| 2.x | `unit` | `client.read_holding_registers(address, count, unit=1)` |
| 3.x | `slave` | `client.read_holding_registers(address, count=count, slave=1)` |

#### **Asynchrone Implementierung**
```python
# Neue async Wrapper mit automatischer API-Erkennung
async def async_read_holding_registers(
    client: AsyncModbusTcpClient, address, count, slave_id=1
):
    api_type = _test_async_api_compatibility(client, 'read_holding_registers')
    
    if api_type == 'slave':
        return await client.read_holding_registers(
            address, count=count, slave=slave_id
        )
    elif api_type == 'unit':
        return await client.read_holding_registers(
            address, count, unit=slave_id
        )
    else:
        return await client.read_holding_registers(address, count)
```

### 🎯 **Vorteile der Änderungen**

#### **Kompatibilität**
- ✅ **Keine Modbus-Konflikte** mehr mit SolaX Integration
- ✅ **Unabhängig von Start-Reihenfolge** der Integrationen
- ✅ **Unterstützung aller pymodbus Versionen**

#### **Performance**
- ✅ **Asynchrone Operationen** für bessere Performance
- ✅ **Keine Blocking-Operationen** im Event Loop
- ✅ **Effizientere Ressourcennutzung**

#### **Stabilität**
- ✅ **Keine RuntimeWarnings** mehr
- ✅ **Korrekte Callback-Implementierung**
- ✅ **Robuste Fehlerbehandlung**

### 🔄 **Migration**

#### **Für Benutzer**
- **Keine Konfigurationsänderungen** erforderlich
- **Automatische Migration** beim nächsten Neustart
- **Bestehende Daten** bleiben erhalten

#### **Für Entwickler**
- **Neue async Modbus-Funktionen** verwenden
- **Keine `async_add_executor_job`** mehr nötig
- **Direkte `await` Aufrufe** für Modbus-Operationen

### 📝 **Breaking Changes**
- **Keine** - Alle Änderungen sind rückwärtskompatibel

### 🧪 **Testing**
- ✅ **Alle Tests** erfolgreich durchgeführt
- ✅ **Integration läuft stabil** in Home Assistant
- ✅ **Keine Fehler** in den Logs

### 📈 **Zukunft**
- **Basis für weitere Verbesserungen** geschaffen
- **Moderne asynchrone Architektur** implementiert
- **Bessere Skalierbarkeit** für zukünftige Features

---

## [1.0.0] - 2025-07-24

### 🎉 **Initial Release**
- Grundlegende Lambda Heat Pumps Integration
- Modbus-basierte Kommunikation
- Sensor- und Climate-Entities
- Cycling-Counter-Funktionalität 