# Lambda Heat Pumps - Home Assistant Integration

This integration allows you to connect your Lambda Heat Pump system to Home Assistant, providing comprehensive monitoring and control capabilities for your heating system.

## Documentation Overview

### General Documentation
- [English Documentation](lambda_heat_pumps_en.md) - Comprehensive English documentation about the integration
- [German Documentation (Deutsche Dokumentation)](lambda_heat_pumps_de.md) - Comprehensive German documentation about the integration

### Getting Started
- [Quick Start Guide](lambda_heat_pumps_quick_start.md) - How to install and set up the integration
- [HACS Installation Guide](lambda_heat_pumps_hacs_installation.md) - Install the integration via HACS
- [FAQ](lambda_heat_pumps_faq.md) - Frequently asked questions about the integration
- [Troubleshooting](lambda_heat_pumps_troubleshooting.md) - Solutions to common problems

### Reference Documentation
- [Entity Reference](lambda_heat_pumps_entity_reference.md) - Complete list of all entities provided by the integration
- [English Modbus Register Description](lambda_heat_pumps_modbus_register_en.md) - Detailed information about Modbus registers (English)
- [German Modbus Register Description](lambda_heat_pumps_modbus_register_de.md) - Detailed information about Modbus registers (German)

### For Developers
- [Developer Guide](lambda_heat_pumps_developer_guide.md) - Information for developers who want to extend or modify the integration

## Key Features

- Support for multiple heat pumps, boilers, heating circuits, buffers, and solar systems
- Real-time monitoring of temperature sensors, operational states, and errors
- Climate entities for controlling heating and hot water
- Service for updating room temperature from external sensors
- Configurable polling interval for data updates
- Detailed entity attributes for comprehensive system information

## Component Documentation

The Lambda Heat Pumps integration is comprised of several components:

1. **Configuration:** Easy setup through the Home Assistant UI
2. **Coordinator:** Manages data polling and Modbus communication
3. **Sensor Entities:** Provides temperature, state, and diagnostic readings
4. **Climate Entities:** Controls heating circuits and hot water boilers
5. **Services:** Additional functionality for system control

## System Requirements

- Home Assistant 2024.4.4 or newer
- A Lambda Heat Pump system with Modbus TCP connectivity
- Network connection between your Home Assistant instance and the Lambda controller
