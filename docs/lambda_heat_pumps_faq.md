# Lambda Heat Pumps - Frequently Asked Questions

## General Questions

### What is the Lambda Heat Pumps integration?
The Lambda Heat Pumps integration is a custom component for Home Assistant that allows you to monitor and control Lambda heat pump systems via Modbus TCP.

### Which Lambda models are supported?
The integration supports all Lambda heat pump systems that provide Modbus TCP access, including systems with multiple heat pumps, boilers, heating circuits, buffers, and solar components.

### How often is data updated from my Lambda system?
By default, the integration polls data every 30 seconds. You can adjust this interval in the integration options if needed.

### Do I need any additional hardware?
No additional hardware is required if your Lambda controller already has network connectivity and Modbus TCP enabled. The integration communicates directly with the controller over your local network.

## Setup and Configuration

### How do I install the integration?
Copy the `lambda_heat_pumps` folder to your Home Assistant `custom_components` directory, restart Home Assistant, then add the integration through the UI under Configuration → Integrations.

### How do I know how many heating circuits, boilers, etc. to configure?
Configure the number of devices based on your actual Lambda system setup. You can find this information in your Lambda controller configuration or installation documentation. Setting incorrect device counts may result in missing entities or errors.

### Which firmware version should I select?
Select the firmware version that matches your Lambda controller. If unsure, check the controller's system information screen or contact your installer.

### Can I change the configuration after initial setup?
Yes, most settings can be adjusted through the integration options after setup. You can access these by clicking on the "Configure" button for the integration in the Integrations page.

## Features and Functionality

### Can I control room temperature with the integration?
Yes, the integration provides climate entities for heating circuits that allow you to set target temperatures and operating modes.

### How do I use my own room temperature sensors instead of the built-in ones?
Use the `lambda_heat_pumps.update_room_temperature` service to periodically update room temperature readings from your preferred temperature sensors to the Lambda controller.

### Can I control hot water temperature?
Yes, boilers are exposed as climate entities that allow you to set the target hot water temperature within the allowed range.

### Do all sensors update in real-time?
The integration polls data at regular intervals (default: 30 seconds), so there may be a small delay between a change in the system and the update in Home Assistant.

### Can I use this integration in automations?
Yes, all entities and services provided by the integration can be used in Home Assistant automations, scripts, and scenes.

### Can I read or write arbitrary Modbus registers?
Yes, the integration provides two services: `read_modbus_register` and `write_modbus_register`. You can use these via the Home Assistant Developer Tools to read or write any Modbus register address. See the documentation for details.

### Why is my heating circuit climate entity missing?
Heating circuit climate entities are only created if a room thermostat sensor is configured for that circuit in the integration options.

### How are climate entities defined?
All climate entities are now defined by templates in `const.py`, making it easy to adjust or extend their properties centrally.

## Troubleshooting

### Why do some entities show "unavailable"?
Entities may show as unavailable if:
- The corresponding device doesn't exist in your system
- There's a communication issue with the Lambda controller
- The data for that entity is not available in the current system state

### Why do climate entities show incorrect modes?
The available modes depend on the operating state of the device and the firmware version. Make sure you've selected the correct firmware version during setup.

### How can I debug communication issues?
Enable debug logging for the integration by adding the following to your `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.lambda_heat_pumps: debug
```

### What should I do if I get timeout errors?
Network timeouts can occur if there are connectivity issues between Home Assistant and the Lambda controller. Check your network setup and try increasing the polling interval in the integration options.

## Advanced Topics

### Can I extend the integration to support additional features?
Yes, the integration is designed to be extensible. See the developer guide for information on how to modify or extend the integration.

### How can I contribute to the integration?
Contributions are welcome! You can contribute by submitting pull requests to the GitHub repository with bug fixes, enhancements, or documentation improvements.

### Is the integration compatible with Home Assistant Energy Dashboard?
The integration provides power consumption sensors that can be used in the Energy Dashboard. Look for sensors with names like `sensor.[name]_hpX_fi_power_consumption` which represent the power consumption of individual heat pumps.
