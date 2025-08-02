# TODO - Lambda Heat Pumps Integration

## 🔧 **Code Quality & Architecture**

### **Device Class Refactoring** ⭐ **HIGH PRIORITY**
**Problem**: Aktuelle automatische `device_class`-Zuweisung in `sensor.py` ist inkonsistent und wartungsintensiv.

**Aktuelle Lösung**:
```python
# In sensor.py - automatische Zuweisung
elif not device_class and sensor_info.get("unit") == "Wh":
    device_class = SensorDeviceClass.ENERGY
elif not device_class and sensor_info.get("unit") == "kWh":
    device_class = SensorDeviceClass.ENERGY
```

**⚠️ AKTUELLER STATUS**: 
- `LambdaSensor`-Klasse: ✅ `device_class`-Property implementiert (Zeilen 904-915)
- `LambdaTemplateSensor`-Klasse: ✅ `device_class`-Property implementiert (Zeilen 982-992)
- Automatische Zuweisung: ✅ Funktioniert für Standard-Sensoren
- Explizite Definitionen: ❌ Noch nicht in `const.py` implementiert

**Bessere Lösung**: Explizite `device_class`-Definition in `const.py`

**Vorteile**:
- ✅ Klarheit: Jeder Sensor hat eine eindeutige, dokumentierte `device_class`
- ✅ Wartbarkeit: Einfacher zu verstehen und zu ändern
- ✅ Konsistenz: Keine versteckten Regeln oder Ausnahmen
- ✅ Vollständigkeit: Alle Sensoren werden explizit definiert
- ✅ IDE-Support: Bessere Autocomplete und Typprüfung

**Implementierung**:
```python
# In const.py - explizite Definition
"energy_total": {
    "relative_address": 5,
    "name": "Energy Total",
    "unit": "kWh",
    "scale": 1,
    "precision": 0,
    "data_type": "int32",
    "firmware_version": 1,
    "device_type": "sol",
    "writeable": False,
    "device_class": "energy",  # ← EXPLIZIT
    "state_class": "total_increasing",
},
```

**Zu definierende `device_class`-Werte**:
- `"energy"` für kWh, Wh
- `"temperature"` für °C
- `"power"` für W, kW
- `"pressure"` für bar, Pa
- `"frequency"` für Hz
- `"voltage"` für V
- `"current"` für A
- `"duration"` für s, min, h
- `"speed"` für rpm, m/s
- `"volume"` für l, m³
- `"mass"` für kg, g
- `"humidity"` für %
- `"illuminance"` für lx
- `"concentration"` für ppm, mg/m³

**Vereinfachte sensor.py**:
```python
# In sensor.py - viel einfacher!
device_class = sensor_info.get("device_class")
if device_class:
    device_class = SensorDeviceClass(device_class)
```

**Betroffene Dateien**:
- `custom_components/lambda_heat_pumps/const.py` - Alle Sensor-Definitionen
- `custom_components/lambda_heat_pumps/sensor.py` - Vereinfachte Logik
- `custom_components/lambda_heat_pumps/template_sensor.py` - Anpassung falls nötig

### **Device Class Properties Implementation** ✅ **COMPLETED**
**Problem**: `LambdaSensor`-Klasse hatte keine `device_class`-Property implementiert.

**Gelöste Probleme**:
- ✅ `LambdaSensor`-Klasse: `device_class`-Property hinzugefügt (Zeilen 904-915)
- ✅ `LambdaSensor`-Klasse: `native_unit_of_measurement`-Property hinzugefügt (Zeilen 895-898)
- ✅ `LambdaSensor`-Klasse: `state_class`-Property hinzugefügt (Zeilen 900-908)
- ✅ `LambdaTemplateSensor`-Klasse: Hatte bereits alle Properties implementiert

**Ergebnis**: 
- Sensoren mit `kWh`/`Wh` Einheit bekommen jetzt automatisch `device_class: "energy"`
- Alle Standard-Sensoren haben jetzt korrekte `device_class`-Zuweisung
- Template-Sensoren funktionieren bereits korrekt

### **Alle Sensor-Klassen Device Class Überprüfung** ✅ **COMPLETED**
**Überprüfung aller Sensor-Klassen in der Integration:**

#### **1. LambdaSensor** ✅ **IMPLEMENTIERT**
- **Datei**: `custom_components/lambda_heat_pumps/sensor.py` (Zeilen 745-936)
- **device_class-Property**: ✅ Implementiert (Zeilen 920-930)
- **native_unit_of_measurement-Property**: ✅ Implementiert (Zeilen 904-907)
- **state_class-Property**: ✅ Implementiert (Zeilen 909-918)
- **Status**: ✅ **VOLLSTÄNDIG**

#### **2. LambdaTemplateSensor** ✅ **IMPLEMENTIERT**
- **Datei**: `custom_components/lambda_heat_pumps/sensor.py` (Zeilen 937-1076)
- **device_class-Property**: ✅ Implementiert (Zeilen 1008-1018)
- **native_unit_of_measurement-Property**: ✅ Implementiert (Zeilen 992-995)
- **state_class-Property**: ✅ Implementiert (Zeilen 997-1006)
- **Status**: ✅ **VOLLSTÄNDIG**

#### **3. LambdaTemplateSensor (template_sensor.py)** ✅ **IMPLEMENTIERT**
- **Datei**: `custom_components/lambda_heat_pumps/template_sensor.py` (Zeilen 154-318)
- **device_class-Property**: ✅ Implementiert (Zeilen 218-228)
- **native_unit_of_measurement-Property**: ✅ Implementiert (Zeilen 202-205)
- **state_class-Property**: ✅ Implementiert (Zeilen 207-216)
- **Status**: ✅ **VOLLSTÄNDIG**

#### **4. LambdaCyclingSensor** ✅ **IMPLEMENTIERT**
- **Datei**: `custom_components/lambda_heat_pumps/sensor.py` (Zeilen 383-554)
- **device_class-Property**: ✅ Implementiert (Zeilen 528-530)
- **native_unit_of_measurement-Property**: ✅ Implementiert (Zeilen 520-523)
- **state_class-Property**: ✅ Implementiert (Zeilen 524-527)
- **Status**: ✅ **VOLLSTÄNDIG**

#### **5. LambdaYesterdaySensor** ✅ **IMPLEMENTIERT**
- **Datei**: `custom_components/lambda_heat_pumps/sensor.py` (Zeilen 555-744)
- **device_class-Property**: ✅ Implementiert (Zeilen 718-720)
- **native_unit_of_measurement-Property**: ✅ Implementiert (Zeilen 710-713)
- **state_class-Property**: ✅ Implementiert (Zeilen 714-717)
- **Status**: ✅ **VOLLSTÄNDIG**

#### **6. LambdaClimateEntity** ❌ **FEHLT**
- **Datei**: `custom_components/lambda_heat_pumps/climate.py` (Zeilen 35-156)
- **device_class-Property**: ❌ **NICHT IMPLEMENTIERT**
- **Begründung**: Climate-Entities erben von `ClimateEntity`, nicht von `SensorEntity`
- **Empfehlung**: `device_class: "temperature"` hinzufügen für bessere Kategorisierung
- **Status**: ❌ **MUSS IMPLEMENTIERT WERDEN**

**Zusammenfassung**:
- ✅ **5 von 6 Sensor-Klassen** haben vollständige `device_class`-Implementierung
- ❌ **1 von 6 Sensor-Klassen** (`LambdaClimateEntity`) fehlt `device_class`-Property
- **Gesamtstatus**: 83% **ABGESCHLOSSEN**

### **Climate Entities Device Class** ⭐ **MEDIUM PRIORITY**
**Problem**: Climate-Entities haben keine `device_class`-Verarbeitung implementiert.

**Aktuelle Situation**:
- Climate-Entities erben von `ClimateEntity`, nicht von `SensorEntity`
- Keine `device_class`-Property implementiert
- Keine automatische Zuweisung basierend auf Einheiten

**Betroffene Entities**:
- `hot_water` Climate-Entities
- `heating_circuit` Climate-Entities

**Spezifische Details**:
- **Datei**: `custom_components/lambda_heat_pumps/climate.py` (Zeilen 35-156)
- **Klasse**: `LambdaClimateEntity(CoordinatorEntity, ClimateEntity)`
- **Fehlende Property**: `device_class`
- **Empfohlener Wert**: `SensorDeviceClass.TEMPERATURE`

**Implementierung**:
```python
# In climate.py - device_class hinzufügen
@property
def device_class(self) -> SensorDeviceClass | None:
    """Return the device class of the climate entity."""
    # Climate-Entities sind immer Temperatur-basiert
    return SensorDeviceClass.TEMPERATURE
```

**Vorteile**:
- ✅ Bessere Kategorisierung in Home Assistant
- ✅ Korrekte Anzeige in Dashboards
- ✅ Konsistenz mit anderen Sensor-Klassen
- ✅ Verbesserte Suchfunktionalität

### **Template Sensor Definitions** ⭐ **MEDIUM PRIORITY**
**Problem**: Alle Template-Sensor-Definitionen haben `"device_class": None`.

**Aktuelle Situation**:
```python
# In const.py - alle Template-Sensoren
"cop_calc": {
    # ...
    "device_class": None,  # ← Sollte "measurement" oder spezifischer sein
},
"heating_cycling_total": {
    # ...
    "device_class": None,  # ← Sollte "total" oder "measurement" sein
},
```

**Bessere Lösung**: Explizite `device_class`-Werte für Template-Sensoren

**Implementierung**:
```python
# In const.py - explizite device_class
"cop_calc": {
    # ...
    "device_class": "measurement",  # ← EXPLIZIT
},
"heating_cycling_total": {
    # ...
    "device_class": "total",  # ← EXPLIZIT
},
"energy_calculated": {
    # ...
    "device_class": "energy",  # ← EXPLIZIT
},
```

**Automatische Fallback-Logik für Template-Sensoren**:
```python
# In template_sensor.py - ähnlich wie in sensor.py
device_class = sensor_info.get("device_class")
if not device_class and sensor_info.get("unit") == "°C":
    device_class = "temperature"
elif not device_class and sensor_info.get("unit") == "cycles":
    device_class = "total"
elif not device_class and sensor_info.get("unit") in ["Wh", "kWh"]:
    device_class = "energy"
```

**Betroffene Dateien**:
- `custom_components/lambda_heat_pumps/const.py` - Template-Sensor-Definitionen
- `custom_components/lambda_heat_pumps/climate.py` - Climate-Entities
- `custom_components/lambda_heat_pumps/template_sensor.py` - Fallback-Logik

### **Cycling Sensors Device Class** ⭐ **MEDIUM PRIORITY**
**Problem**: Cycling-Sensoren haben `"device_class": None`, obwohl sie historische Werte erzeugen.

**Aktuelle Situation**:
```python
# Total-Sensoren (akkumulativ)
"heating_cycling_total": {
    "unit": "cycles",
    "state_class": "total_increasing",  # ✅ KORREKT
    "device_class": None,  # ❌ FEHLT
},

# Daily-Sensoren (tägliche Differenz)
"heating_cycling_daily": {
    "unit": "cycles", 
    "state_class": "total",  # ✅ KORREKT
    "device_class": None,  # ❌ FEHLT
},
```

**Historische Werte**: 
- **Total-Sensoren** (`state_class: "total_increasing"`): Akkumulieren kontinuierlich, Home Assistant speichert historische Werte automatisch
- **Daily-Sensoren** (`state_class: "total"`): Berechnen tägliche Differenzen, Home Assistant speichert historische Werte für tägliche Statistiken

**Beste Lösung**: `device_class: "total"` für alle Cycling-Sensoren

**Begründung**:
- Cycling-Sensoren sind **Zähler** (Anzahl von Zyklen)
- `state_class: "total_increasing"` zeigt bereits akkumulative Werte
- `device_class: "total"` vervollständigt die Kategorisierung
- Home Assistant behandelt sie dann korrekt als Zähler mit historischen Werten

**Implementierung**:
```python
# Total-Sensoren
"heating_cycling_total": {
    "device_class": "total",  # ← BESTE WAHL
    "state_class": "total_increasing",
},
"hot_water_cycling_total": {
    "device_class": "total", 
    "state_class": "total_increasing",
},
"cooling_cycling_total": {
    "device_class": "total",
    "state_class": "total_increasing", 
},
"defrost_cycling_total": {
    "device_class": "total",
    "state_class": "total_increasing",
},

# Daily-Sensoren  
"heating_cycling_daily": {
    "device_class": "total",
    "state_class": "total",
},
"hot_water_cycling_daily": {
    "device_class": "total",
    "state_class": "total", 
},
"cooling_cycling_daily": {
    "device_class": "total",
    "state_class": "total",
},
"defrost_cycling_daily": {
    "device_class": "total", 
    "state_class": "total",
},

# Yesterday-Sensoren (Speicher für Daily-Berechnung)
"heating_cycling_yesterday": {
    "device_class": "total",
    "state_class": "total",
},
"hot_water_cycling_yesterday": {
    "device_class": "total",
    "state_class": "total",
},
"cooling_cycling_yesterday": {
    "device_class": "total",
    "state_class": "total",
},
"defrost_cycling_yesterday": {
    "device_class": "total",
    "state_class": "total",
},
```

**Vorteile**:
- ✅ Home Assistant erkennt sie als Zähler
- ✅ Automatische Historien-Speicherung
- ✅ Korrekte Visualisierung in Dashboards
- ✅ Energie-Management-Integration
- ✅ Bessere Kategorisierung für Wartungsplanung

**Betroffene Dateien**:
- `custom_components/lambda_heat_pumps/const.py` - Cycling-Sensor-Definitionen

---

## 🚀 **Performance & Features**

### **Caching-System für Modbus-Daten**
- Implementierung eines intelligenten Caching-Systems
- Reduzierung von Modbus-Anfragen für statische Daten
- Optimierung der Update-Intervalle basierend auf Datenänderungen

### **Erweiterte Fehlerbehandlung**
- Retry-Mechanismus für Modbus-Verbindungen
- Graceful Degradation bei Teilausfällen
- Detaillierte Fehlerdiagnose und -berichterstattung

---

## 📊 **Monitoring & Analytics**

### **Erweiterte Statistiken**
- Tägliche, wöchentliche, monatliche Energieverbrauchsstatistiken
- Effizienz-Berechnungen (COP, SCOP)
- Trend-Analysen und Vorhersagen

### **Dashboard-Integration**
- Vordefinierte Lovelace-Dashboards
- Automatische Gruppierung von verwandten Sensoren
- Responsive Design für mobile Geräte

---

## 🔌 **Integration & Compatibility**

### **Erweiterte Home Assistant Integration**
- Energie-Management-Integration
- Automatisierungs-Templates
- Blueprint-Integration für häufige Szenarien

### **Externe API-Support**
- REST-API für externe Systeme
- MQTT-Integration für IoT-Devices
- Webhook-Support für Benachrichtigungen

---

## 📚 **Documentation & Testing**

### **Erweiterte Dokumentation**
- API-Referenz für Entwickler
- Troubleshooting-Guide erweitern
- Video-Tutorials für Einrichtung

### **Test-Suite**
- Unit-Tests für alle Komponenten
- Integration-Tests für Modbus-Kommunikation
- Performance-Tests für große Installationen

---

## 🎯 **User Experience**

### **Konfigurations-Assistent**
- Schritt-für-Schritt Einrichtung
- Automatische Geräteerkennung
- Validierung der Konfiguration

### **Erweiterte Benutzeroberfläche**
- Inline-Konfiguration von Sensoren
- Drag-and-Drop Dashboard-Erstellung
- Mobile-optimierte Bedienung

---

## 🔒 **Security & Privacy**

### **Sicherheitsverbesserungen**
- Verschlüsselte Modbus-Kommunikation (falls unterstützt)
- Authentifizierung für externe APIs
- Audit-Logs für alle Änderungen

---

## 📋 **Maintenance & Updates**

### **Automatische Updates**
- Update-Benachrichtigungen
- Automatische Backup vor Updates
- Rollback-Mechanismus

### **Monitoring & Health Checks**
- System-Gesundheitsüberwachung
- Proaktive Fehlererkennung
- Performance-Monitoring

---

*Letzte Aktualisierung: 2025-08-02*
*Status: In Bearbeitung* 