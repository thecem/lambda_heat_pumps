"""Data update coordinator for Lambda."""
from __future__ import annotations
from datetime import timedelta
import logging
import os
import yaml
import aiofiles
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import (
    SENSOR_TYPES,
    HP_SENSOR_TEMPLATES,
    BOIL_SENSOR_TEMPLATES,
    BUFF_SENSOR_TEMPLATES,
    SOL_SENSOR_TEMPLATES,
    FIRMWARE_VERSION,
    DEFAULT_FIRMWARE,
    HC_SENSOR_TEMPLATES,
)
from .utils import get_compatible_sensors, load_disabled_registers, is_register_disabled, generate_base_addresses, to_signed_16bit, to_signed_32bit

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=30)


class LambdaDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Lambda data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize."""
        # Lese update_interval aus den Optionen, falls vorhanden
        update_interval = entry.options.get("update_interval", 30)
        _LOGGER.debug("Update interval from options: %s seconds", update_interval)
        _LOGGER.debug("Entry options: %s", entry.options)
        _LOGGER.debug(
            "Room thermostat control: %s",
            entry.options.get("room_thermostat_control", "nicht gefunden"),
        )

        super().__init__(
            hass,
            _LOGGER,
            name="Lambda Coordinator",
            update_interval=timedelta(seconds=update_interval),
        )
        self.host = entry.data["host"]
        self.port = entry.data["port"]
        self.slave_id = entry.data.get("slave_id", 1)
        self.debug_mode = entry.data.get("debug_mode", False)
        if self.debug_mode:
            _LOGGER.setLevel(logging.DEBUG)
        self.client = None
        self.config_entry_id = entry.entry_id
        self.disabled_registers = set()
        self._config_dir = hass.config.config_dir
        self._config_path = os.path.join(self._config_dir, "lambda_heat_pumps")
        # Nutze die lokale Datei im Custom Component-Ordner
        self._disabled_registers_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "disabled_registers.yaml"
        )
        self.hass = hass
        self.entry = entry

    async def async_init(self):
        """Async initialization."""
        _LOGGER.debug("Initializing Lambda coordinator")
        _LOGGER.debug("Config directory: %s", self._config_dir)
        _LOGGER.debug("Config path: %s", self._config_path)
        _LOGGER.debug("Disabled registers path: %s", self._disabled_registers_path)

        try:
            await self._ensure_config_dir()
            _LOGGER.debug("Config directory ensured")

            self.disabled_registers = await load_disabled_registers(self.hass, self._disabled_registers_path)
            _LOGGER.debug("Loaded disabled registers: %s", self.disabled_registers)

            if not self.disabled_registers:
                _LOGGER.debug("No disabled registers configured - this is normal if you haven't disabled any registers")
        except Exception as e:
            _LOGGER.error("Failed to initialize coordinator: %s", str(e))
            self.disabled_registers = set()
            raise

    async def _ensure_config_dir(self):
        """Ensure config directory exists."""
        try:
            def _create_dirs():
                os.makedirs(self._config_dir, exist_ok=True)
                os.makedirs(self._config_path, exist_ok=True)
                _LOGGER.debug("Created directories: %s and %s", self._config_dir, self._config_path)

            await self.hass.async_add_executor_job(_create_dirs)
        except Exception as e:
            _LOGGER.error("Failed to create config directories: %s", str(e))
            raise

    def is_register_disabled(self, address: int) -> bool:
        """Check if a register is disabled."""
        if not hasattr(self, 'disabled_registers'):
            _LOGGER.error("disabled_registers not initialized")
            return False

        # Debug: Ausgabe der Typen und Inhalte
        _LOGGER.debug(
            "Check if address %r (type: %s) is in disabled_registers: %r (types: %r)",
            address, type(address), self.disabled_registers, {type(x) for x in self.disabled_registers}
        )

        is_disabled = is_register_disabled(address, self.disabled_registers)
        if is_disabled:
            _LOGGER.debug("Register %d is disabled (in set: %s)", address, self.disabled_registers)
        else:
            _LOGGER.debug("Register %d is not disabled (checked against set: %s)", address, self.disabled_registers)
        return is_disabled

    async def _async_update_data(self):
        """Fetch data from Lambda device."""
        # Ensure Modbus client is initialized
        if self.client is None:
            from pymodbus.client import ModbusTcpClient
            self.client = ModbusTcpClient(self.host, port=self.port)
            try:
                connected = await self.hass.async_add_executor_job(self.client.connect)
                if not connected:
                    raise ConnectionError(f"Could not connect to Modbus TCP at {self.host}:{self.port}")
            except Exception as ex:
                _LOGGER.error("Failed to connect to Modbus TCP: %s", ex)
                self.client = None
                raise UpdateFailed(f"Failed to connect to Modbus TCP: {ex}")

        try:
            # Get device counts from config
            num_hps = self.entry.data.get("num_hps", 1)
            num_boil = self.entry.data.get("num_boil", 1)
            num_buff = self.entry.data.get("num_buff", 0)  # Default to 0 if not configured
            num_sol = self.entry.data.get("num_sol", 0)    # Default to 0 if not configured
            num_hc = self.entry.data.get("num_hc", 1)

            _LOGGER.debug(
                "Reading data for devices: %d HPs, %d boilers, %d buffers, %d solar, %d heating circuits",
                num_hps, num_boil, num_buff, num_sol, num_hc
            )

            # Initialize data dictionary
            data = {}

            # Check if client is still connected
            if not self.client.connected:
                _LOGGER.warning("Modbus client disconnected, attempting to reconnect")
                connected = await self.hass.async_add_executor_job(self.client.connect)
                if not connected:
                    raise ConnectionError("Failed to reconnect to Modbus TCP")

            # General/Ambient data
            for sensor_id, sensor_info in SENSOR_TYPES.items():
                address = sensor_info["address"]
                if is_register_disabled(address, self.disabled_registers):
                    continue
                try:
                    count = 2 if sensor_info.get("data_type") == "int32" else 1
                    result = await self.hass.async_add_executor_job(
                        self.client.read_holding_registers,
                        address,
                        count,
                        self.entry.data.get("slave_id", 1)
                    )
                    if hasattr(result, "isError") and result.isError():
                        _LOGGER.error("Error reading register %d: %s", address, result)
                        continue
                    if not hasattr(result, "registers") or not result.registers:
                        _LOGGER.error("Invalid response for register %d: %s", address, result)
                        continue
                    if count == 2:
                        value = (result.registers[0] << 16) | result.registers[1]
                        if sensor_info.get("data_type") == "int32":
                            value = to_signed_32bit(value)
                    else:
                        value = result.registers[0]
                        if sensor_info.get("data_type") == "int16":
                            value = to_signed_16bit(value)
                    if "scale" in sensor_info:
                        value = value * sensor_info["scale"]
                    data[sensor_id] = value
                except Exception as ex:
                    _LOGGER.error("Error reading register %d: %s", address, ex)

            # Heat Pump data
            for hp_idx in range(1, num_hps + 1):
                base_address = generate_base_addresses('hp', num_hps)[hp_idx]
                for sensor_id, sensor_info in HP_SENSOR_TEMPLATES.items():
                    address = base_address + sensor_info["relative_address"]
                    if is_register_disabled(address, self.disabled_registers):
                        _LOGGER.debug("Register %d is disabled, skipping", address)
                        continue
                    try:
                        _LOGGER.debug("Reading register %d for sensor %s", address, sensor_id)
                        count = 2 if sensor_info.get("data_type") == "int32" else 1
                        result = await self.hass.async_add_executor_job(
                            self.client.read_holding_registers,
                            address,
                            count,
                            self.entry.data.get("slave_id", 1)
                        )
                        if hasattr(result, "isError") and result.isError():
                            error_msg = f"Modbus error {result.exception_code}: {result.message}"
                            _LOGGER.error(
                                "Error reading register %d: %s",
                                address,
                                error_msg,
                            )
                            if result.exception_code == 1:  # Illegal Function
                                raise UpdateFailed(f"Modbus error: {error_msg}")
                            continue
                        if not hasattr(result, "registers") or not result.registers:
                            _LOGGER.error(
                                "Invalid response for register %d: %s",
                                address,
                                result,
                            )
                            continue
                        if count == 2:
                            value = (result.registers[0] << 16) | result.registers[1]
                            if sensor_info.get("data_type") == "int32":
                                value = to_signed_32bit(value)
                        else:
                            value = result.registers[0]
                            if sensor_info.get("data_type") == "int16":
                                value = to_signed_16bit(value)
                        if "scale" in sensor_info:
                            value = value * sensor_info["scale"]
                        # override_name-Mechanismus
                        use_legacy_modbus_names = self.entry.data.get("use_legacy_modbus_names", False)
                        if use_legacy_modbus_names and "override_name" in sensor_info:
                            sensor_id_final = sensor_info["override_name"]
                        else:
                            sensor_id_final = f"hp{hp_idx}_{sensor_id}"
                        data[sensor_id_final] = value
                        _LOGGER.debug("Successfully read register %d: %s", address, value)
                    except Exception as ex:
                        _LOGGER.error(
                            "Error reading register %d: %s",
                            address,
                            ex,
                        )
                        # If we get a connection error, try to reconnect
                        if isinstance(ex, (ConnectionError, TimeoutError)):
                            self.client = None
                            raise UpdateFailed(f"Connection error: {ex}")

            # Boiler data
            for boil_idx in range(1, num_boil + 1):
                base_address = generate_base_addresses('boil', num_boil)[boil_idx]
                for sensor_id, sensor_info in BOIL_SENSOR_TEMPLATES.items():
                    address = base_address + sensor_info["relative_address"]
                    if is_register_disabled(address, self.disabled_registers):
                        continue
                    try:
                        count = 2 if sensor_info.get("data_type") == "int32" else 1
                        result = await self.hass.async_add_executor_job(
                            self.client.read_holding_registers,
                            address,
                            count,
                            self.entry.data.get("slave_id", 1)
                        )
                        if hasattr(result, "isError") and result.isError():
                            _LOGGER.error(
                                "Error reading register %d: %s",
                                address,
                                result,
                            )
                            continue
                        if count == 2:
                            value = (result.registers[0] << 16) | result.registers[1]
                            if sensor_info.get("data_type") == "int32":
                                value = to_signed_32bit(value)
                        else:
                            value = result.registers[0]
                            if sensor_info.get("data_type") == "int16":
                                value = to_signed_16bit(value)
                        if "scale" in sensor_info:
                            value = value * sensor_info["scale"]
                        use_legacy_modbus_names = self.entry.data.get("use_legacy_modbus_names", False)
                        if use_legacy_modbus_names and "override_name" in sensor_info:
                            sensor_id_final = sensor_info["override_name"]
                        else:
                            sensor_id_final = f"boil{boil_idx}_{sensor_id}"
                        data[sensor_id_final] = value
                    except Exception as ex:
                        _LOGGER.error(
                            "Error reading register %d: %s",
                            address,
                            ex,
                        )

            # Buffer data - only if configured
            if num_buff > 0:
                for buff_idx in range(1, num_buff + 1):
                    base_address = generate_base_addresses('buff', num_buff)[buff_idx]
                    for sensor_id, sensor_info in BUFF_SENSOR_TEMPLATES.items():
                        address = base_address + sensor_info["relative_address"]
                        if is_register_disabled(address, self.disabled_registers):
                            continue
                        try:
                            count = 2 if sensor_info.get("data_type") == "int32" else 1
                            result = await self.hass.async_add_executor_job(
                                self.client.read_holding_registers,
                                address,
                                count,
                                self.entry.data.get("slave_id", 1)
                            )
                            if hasattr(result, "isError") and result.isError():
                                _LOGGER.error(
                                    "Error reading register %d: %s",
                                    address,
                                    result,
                                )
                                continue
                            if count == 2:
                                value = (result.registers[0] << 16) | result.registers[1]
                                if sensor_info.get("data_type") == "int32":
                                    value = to_signed_32bit(value)
                            else:
                                value = result.registers[0]
                                if sensor_info.get("data_type") == "int16":
                                    value = to_signed_16bit(value)
                            if "scale" in sensor_info:
                                value = value * sensor_info["scale"]
                            use_legacy_modbus_names = self.entry.data.get("use_legacy_modbus_names", False)
                            if use_legacy_modbus_names and "override_name" in sensor_info:
                                sensor_id_final = sensor_info["override_name"]
                            else:
                                sensor_id_final = f"buff{buff_idx}_{sensor_id}"
                            data[sensor_id_final] = value
                        except Exception as ex:
                            _LOGGER.error(
                                "Error reading register %d: %s",
                                address,
                                ex,
                            )

            # Solar data - only if configured
            if num_sol > 0:
                for sol_idx in range(1, num_sol + 1):
                    base_address = generate_base_addresses('sol', num_sol)[sol_idx]
                    for sensor_id, sensor_info in SOL_SENSOR_TEMPLATES.items():
                        address = base_address + sensor_info["relative_address"]
                        if is_register_disabled(address, self.disabled_registers):
                            continue
                        try:
                            count = 2 if sensor_info.get("data_type") == "int32" else 1
                            result = await self.hass.async_add_executor_job(
                                self.client.read_holding_registers,
                                address,
                                count,
                                self.entry.data.get("slave_id", 1)
                            )
                            if hasattr(result, "isError") and result.isError():
                                _LOGGER.error(
                                    "Error reading register %d: %s",
                                    address,
                                    result,
                                )
                                continue
                            if count == 2:
                                value = (result.registers[0] << 16) | result.registers[1]
                                if sensor_info.get("data_type") == "int32":
                                    value = to_signed_32bit(value)
                            else:
                                value = result.registers[0]
                                if sensor_info.get("data_type") == "int16":
                                    value = to_signed_16bit(value)
                            if "scale" in sensor_info:
                                value = value * sensor_info["scale"]
                            use_legacy_modbus_names = self.entry.data.get("use_legacy_modbus_names", False)
                            if use_legacy_modbus_names and "override_name" in sensor_info:
                                sensor_id_final = sensor_info["override_name"]
                            else:
                                sensor_id_final = f"sol{sol_idx}_{sensor_id}"
                            data[sensor_id_final] = value
                        except Exception as ex:
                            _LOGGER.error(
                                "Error reading register %d: %s",
                                address,
                                ex,
                            )

            # Heating Circuit data
            for hc_idx in range(1, num_hc + 1):
                base_address = generate_base_addresses('hc', num_hc)[hc_idx]
                for sensor_id, sensor_info in HC_SENSOR_TEMPLATES.items():
                    address = base_address + sensor_info["relative_address"]
                    if is_register_disabled(address, self.disabled_registers):
                        continue
                    try:
                        count = 2 if sensor_info.get("data_type") == "int32" else 1
                        result = await self.hass.async_add_executor_job(
                            self.client.read_holding_registers,
                            address,
                            count,
                            self.entry.data.get("slave_id", 1)
                        )
                        if hasattr(result, "isError") and result.isError():
                            _LOGGER.error(
                                "Error reading register %d: %s",
                                address,
                                result,
                            )
                            continue
                        if count == 2:
                            value = (result.registers[0] << 16) | result.registers[1]
                            if sensor_info.get("data_type") == "int32":
                                value = to_signed_32bit(value)
                        else:
                            value = result.registers[0]
                            if sensor_info.get("data_type") == "int16":
                                value = to_signed_16bit(value)
                        if "scale" in sensor_info:
                            value = value * sensor_info["scale"]
                        use_legacy_modbus_names = self.entry.data.get("use_legacy_modbus_names", False)
                        if use_legacy_modbus_names and "override_name" in sensor_info:
                            sensor_id_final = sensor_info["override_name"]
                        else:
                            sensor_id_final = f"hc{hc_idx}_{sensor_id}"
                        data[sensor_id_final] = value
                    except Exception as ex:
                        _LOGGER.error(
                            "Error reading register %d: %s",
                            address,
                            ex,
                        )

            return data

        except Exception as ex:
            _LOGGER.error("Error updating data: %s", ex)
            raise UpdateFailed(f"Error updating data: {ex}")
