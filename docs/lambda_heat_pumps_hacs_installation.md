# Installing Lambda Heat Pumps via HACS

This guide explains how to install the Lambda Heat Pumps integration for Home Assistant using the Home Assistant Community Store (HACS).

## Prerequisites

1. Home Assistant version 2024.4.4 or newer
2. HACS installed on your Home Assistant instance ([HACS Installation Guide](https://hacs.xyz/docs/setup/download))
3. A Lambda heat pump system with Modbus TCP connectivity

## Installation Steps

### Option 1: Installing from HACS (Once Published)

1. **Open HACS in Home Assistant**
   - Navigate to HACS in your Home Assistant sidebar

2. **Add the Lambda Heat Pumps integration**
   - Click on "Integrations"
   - Click the "+" button in the bottom-right corner
   - Search for "Lambda Heat Pumps"
   - Click on the integration and then click "Download"
   - Follow the installation instructions

3. **Restart Home Assistant**
   - Restart your Home Assistant instance to complete the installation

### Option 2: Manual Installation via HACS Custom Repository

If the integration is not yet available in the HACS store, you can add it as a custom repository:

1. **Open HACS in Home Assistant**
   - Navigate to HACS in your Home Assistant sidebar

2. **Add Custom Repository**
   - Click on the three dots in the top-right corner
   - Select "Custom repositories"
   - Enter the repository URL: `https://github.com/GuidoJeuken-6512/lambda_heat_pumps_hacs`
   - Select "Integration" as the Category
   - Click "Add"

3. **Install the Integration**
   - The Lambda Heat Pumps integration should now appear in your HACS Integrations
   - Click on it and select "Download"
   - Follow the installation instructions

4. **Restart Home Assistant**
   - Restart your Home Assistant instance to complete the installation

## Configuration

After installation and restart, configure the integration:

1. **Add the Integration**
   - Go to Configuration → Integrations
   - Click the "+" button to add a new integration
   - Search for "Lambda Heat Pumps"
   - Follow the configuration wizard to set up your Lambda controller

2. **Required Information**
   - Name for your Lambda system
   - IP address or hostname of your Lambda controller
   - Modbus TCP port (default: 502)
   - Slave ID (default: 1)
   - Number of devices (heat pumps, boilers, heating circuits, etc.)
   - Firmware version of your Lambda controller

## Troubleshooting HACS Installation

If you encounter issues during installation:

1. **Check HACS Logs**
   - Go to Configuration → Logs
   - Filter for "hacs" to see HACS-related log entries

2. **Integration Not Appearing**
   - Make sure Home Assistant has been restarted after HACS installation
   - Check if there are any HACS installation errors in the logs
   - Verify that your Home Assistant version meets the minimum requirements

3. **Manual Installation Alternative**
   - If HACS installation continues to fail, you can manually install the integration by copying the files to your `custom_components` directory
   - See the [Quick Start Guide](lambda_heat_pumps_quick_start.md) for manual installation instructions

## Updating the Integration

To update the integration when new versions are available:

1. Open HACS → Integrations
2. Look for updates in the "Updates" tab
3. Click on Lambda Heat Pumps and select "Update"
4. Restart Home Assistant after updating
