# Lambda Heat Pumps Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![maintainer](https://img.shields.io/badge/maintainer-%40GuidoJeuken--6512-blue.svg)](https://github.com/GuidoJeuken-6512)
[![version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/GuidoJeuken-6512/lambda_wp_hacs/releases)
[![license](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 🚀 Quickstart (English)

**Lambda Heat Pumps** is a Home Assistant custom integration for Lambda heat pumps via Modbus/TCP.

**HACS Installation:**
1. Install HACS (if not already done)
2. Add this repo as a custom repository: `GuidoJeuken-6512/lambda_wp_hacs` (category: Integration)
3. Search for "Lambda Heat Pumps" in HACS, install, and restart Home Assistant
4. Add the integration via Settings → Devices & Services

**Features:**
- Full Modbus/TCP support for Lambda heat pumps
- Dynamic entity and sensor detection
- Room thermostat control, YAML config, debug logging

**Documentation:**
- [English Guide](docs/lambda_heat_pumps_en.md)
- [Troubleshooting](docs/lambda_heat_pumps_troubleshooting.md)

**Support:**
- [GitHub Issues](https://github.com/GuidoJeuken-6512/lambda_wp_hacs/issues)
- [Home Assistant Community](https://community.home-assistant.io/)

---

## 🇩🇪 Schnelleinstieg (Deutsch)

> **HACS Custom Integration**  
> Diese Integration verbindet Lambda Wärmepumpen mit Home Assistant via Modbus/TCP.

### 🚀 Quickstart (HACS)

1. **HACS installieren** (falls noch nicht geschehen)
2. **Custom Repository hinzufügen:**
   - HACS → Integrations → „⋮“ → „Custom repositories“
   - URL: `GuidoJeuken-6512/lambda_wp_hacs` (Kategorie: Integration)
3. **Integration suchen & installieren:**
   - „Lambda Heat Pumps“ auswählen und installieren
   - Home Assistant neu starten
4. **Integration einrichten:**
   - Einstellungen → Geräte & Dienste → Integration hinzufügen → „Lambda Heat Pumps“

---

## ✨ Features
- **Full Modbus/TCP integration** for Lambda heat pumps
- **Dynamic sensor/entity detection** based on firmware
- **Configurable number of devices** (heat pumps, boilers, heating circuits, buffer tanks, solar modules)
- **Room thermostat control** with external sensors
- **Centralized filtering and disabling of registers**
- **Automatic YAML config for advanced options**
- **Debug logging and troubleshooting tools**

---

## ⚙️ Configuration
- **UI-based setup** via Home Assistant
- **Advanced options** (legacy mode, register disabling, sensor name override)
- **YAML config (`lambda_wp_config.yaml`)** for register/sensor customization

---

## 📦 Manual Installation (without HACS)

If you do not use HACS, you can install the integration manually:

1. **Create the folder** `/config/custom_components` on your Home Assistant server if it does not exist.

2. **If you have terminal access to your Home Assistant server:**
   ```bash
   cd /config/custom_components
   # Clone the repository
   git clone https://github.com/GuidoJeuken-6512/lambda_wp_hacs.git lambda_heat_pumps
   ```

3. **If you do not have terminal access:**
   - Download the integration from:  
     https://github.com/GuidoJeuken-6512/lambda_wp_hacs
   - Copy the entire folder `lambda_heat_pumps` into `/config/custom_components/` on your Home Assistant server.

4. **Restart Home Assistant** to activate the integration.

---

## 🛠️ Troubleshooting & Support
- **Log-Analyse:** Aktiviere Debug-Logging für detaillierte Fehlerausgabe
- **Häufige Probleme:** Siehe Abschnitt „Troubleshooting“ unten
- **Support:**
  - [GitHub Issues](https://github.com/GuidoJeuken-6512/lambda_wp_hacs/issues)
  - [Home Assistant Community](https://community.home-assistant.io/)

---

## 📄 Lizenz & Haftung
MIT License. Nutzung auf eigene Gefahr. Siehe [LICENSE](LICENSE).

---

## 📚 Weitere Dokumentation
- [Quick Start (DE)](docs/lambda_heat_pumps_quick_start.md)
- [FAQ (DE)](docs/lambda_heat_pumps_faq.md)
- [Entwickler-Guide](docs/lambda_heat_pumps_developer_guide.md)
- [Modbus Register (DE/EN)](docs/lambda_heat_pumps_modbus_register_de.md), [EN](docs/lambda_heat_pumps_modbus_register_en.md)
- [Troubleshooting](docs/lambda_heat_pumps_troubleshooting.md)
- [HACS Publishing Guide](docs/lambda_heat_pumps_hacs_publishing.md)

---

## 📝 Changelog
Siehe [Releases](https://github.com/GuidoJeuken-6512/lambda_wp_hacs/releases) für Änderungen und Breaking Changes.

---

**Developed with ❤️ for the Home Assistant Community**
