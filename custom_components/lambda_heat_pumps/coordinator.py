"""Data update coordinator for Lambda."""

from __future__ import annotations
from datetime import timedelta
import logging
import os
import yaml
import aiofiles
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from .const import (
    SENSOR_TYPES,
    HP_SENSOR_TEMPLATES,
    BOIL_SENSOR_TEMPLATES,
    BUFF_SENSOR_TEMPLATES,
    SOL_SENSOR_TEMPLATES,
    HC_SENSOR_TEMPLATES,
    DEFAULT_UPDATE_INTERVAL,
)
from .utils import (
    load_disabled_registers,
    is_register_disabled,
    generate_base_addresses,
    to_signed_16bit,
    to_signed_32bit,
)

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=30)


class LambdaDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Lambda data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize."""
        # Lese update_interval aus den Optionen, falls vorhanden
        update_interval = entry.options.get(
            "update_interval", DEFAULT_UPDATE_INTERVAL
        )
        _LOGGER.debug(
            "Update interval from options: %s seconds", update_interval
        )
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
        self._config_dir = hass.config.config_dir
        self._config_path = os.path.join(self._config_dir, "lambda_heat_pumps")
        self.hass = hass
        self.entry = entry

    async def async_init(self):
        """Async initialization."""
        _LOGGER.debug("Initializing Lambda coordinator")
        _LOGGER.debug("Config directory: %s", self._config_dir)
        _LOGGER.debug("Config path: %s", self._config_path)

        try:
            await self._ensure_config_dir()
            _LOGGER.debug("Config directory ensured")

            self.disabled_registers = await load_disabled_registers(self.hass)
            _LOGGER.debug(
                "Loaded disabled registers: %s", self.disabled_registers
            )

            # Lade sensor_overrides direkt beim Init
            self.sensor_overrides = await self._load_sensor_overrides()
            _LOGGER.debug(
                "Loaded sensor name overrides: %s", self.sensor_overrides
            )

            # Initialize HA started flag
            self._ha_started = False

            # Register event listener for Home Assistant started
            self.hass.bus.async_listen_once(
                "homeassistant_started", self._on_ha_started
            )

            if not self.disabled_registers:
                _LOGGER.debug(
                    "No disabled registers configured - this is normal if you "
                    "haven't disabled any registers"
                )
        except Exception as e:
            _LOGGER.error("Failed to initialize coordinator: %s", str(e))
            self.disabled_registers = set()
            self.sensor_overrides = {}
            raise

    async def _ensure_config_dir(self):
        """Ensure config directory exists."""
        try:

            def _create_dirs():
                os.makedirs(self._config_dir, exist_ok=True)
                os.makedirs(self._config_path, exist_ok=True)
                _LOGGER.debug(
                    "Created directories: %s and %s",
                    self._config_dir,
                    self._config_path,
                )

            await self.hass.async_add_executor_job(_create_dirs)
        except Exception as e:
            _LOGGER.error("Failed to create config directories: %s", str(e))
            raise

    def is_register_disabled(self, address: int) -> bool:
        """Check if a register is disabled."""
        if not hasattr(self, "disabled_registers"):
            _LOGGER.error("disabled_registers not initialized")
            return False

        # Debug: Ausgabe der Typen und Inhalte
        _LOGGER.debug(
            "Check if address %r (type: %s) is in disabled_registers: %r "
            "(types: %r)",
            address,
            type(address),
            self.disabled_registers,
            {type(x) for x in self.disabled_registers},
        )

        is_disabled = is_register_disabled(address, self.disabled_registers)
        if is_disabled:
            _LOGGER.debug(
                "Register %d is disabled (in set: %s)",
                address,
                self.disabled_registers,
            )
        else:
            _LOGGER.debug(
                "Register %d is not disabled (checked against set: %s)",
                address,
                self.disabled_registers,
            )
        return is_disabled

    async def _async_update_data(self):
        """Fetch data from Lambda device."""
        try:
            if not self.client:
                await self._connect()

            data = {}

            # Read general sensors
            for sensor_id, sensor_info in SENSOR_TYPES.items():
                if self.is_register_disabled(sensor_info["address"]):
                    continue
                try:
                    address = sensor_info["address"]
                    count = (
                        2 if sensor_info.get("data_type") == "int32" else 1
                    )
                    result = await self.hass.async_add_executor_job(
                        self.client.read_holding_registers,
                        address,
                        count,
                        self.entry.data.get("slave_id", 1),
                    )
                    if hasattr(result, "isError") and result.isError():
                        _LOGGER.error(
                            "Error reading register %d: %s",
                            address,
                            result,
                        )
                        continue
                    if count == 2:
                        value = (
                            result.registers[0] << 16
                        ) | result.registers[1]
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
                    _LOGGER.error(
                        "Error reading register %d: %s",
                        address,
                        ex,
                    )

            # Read heat pump sensors
            num_hps = self.entry.data.get("num_hps", 1)
            for hp_idx in range(1, num_hps + 1):
                base_address = generate_base_addresses("hp", num_hps)[hp_idx]
                for sensor_id, sensor_info in HP_SENSOR_TEMPLATES.items():
                    if self.is_register_disabled(
                        base_address + sensor_info["relative_address"]
                    ):
                        continue
                    try:
                        address = (
                            base_address + sensor_info["relative_address"]
                        )
                        count = (
                            2 if sensor_info.get("data_type") == "int32" else 1
                        )
                        result = await self.hass.async_add_executor_job(
                            self.client.read_holding_registers,
                            address,
                            count,
                            self.entry.data.get("slave_id", 1),
                        )
                        if hasattr(result, "isError") and result.isError():
                            _LOGGER.error(
                                "Error reading register %d: %s",
                                address,
                                result,
                            )
                            continue
                        if count == 2:
                            value = (
                                result.registers[0] << 16
                            ) | result.registers[1]
                            if sensor_info.get("data_type") == "int32":
                                value = to_signed_32bit(value)
                        else:
                            value = result.registers[0]
                            if sensor_info.get("data_type") == "int16":
                                value = to_signed_16bit(value)
                        if "scale" in sensor_info:
                            value = value * sensor_info["scale"]
                        # Prüfe auf Override-Name
                        override_name = None
                        if hasattr(self, "sensor_overrides"):
                            override_name = self.sensor_overrides.get(
                                f"hp{hp_idx}_{sensor_id}"
                            )
                        key = (
                            override_name
                            if override_name
                            else f"hp{hp_idx}_{sensor_id}"
                        )
                        data[key] = value
                    except Exception as ex:
                        _LOGGER.error(
                            "Error reading register %d: %s",
                            address,
                            ex,
                        )

            # Read boiler sensors
            num_boil = self.entry.data.get("num_boil", 1)
            for boil_idx in range(1, num_boil + 1):
                base_address = generate_base_addresses("boil", num_boil)[
                    boil_idx
                ]
                for sensor_id, sensor_info in BOIL_SENSOR_TEMPLATES.items():
                    if self.is_register_disabled(
                        base_address + sensor_info["relative_address"]
                    ):
                        continue
                    try:
                        address = (
                            base_address + sensor_info["relative_address"]
                        )
                        count = (
                            2 if sensor_info.get("data_type") == "int32" else 1
                        )
                        result = await self.hass.async_add_executor_job(
                            self.client.read_holding_registers,
                            address,
                            count,
                            self.entry.data.get("slave_id", 1),
                        )
                        if hasattr(result, "isError") and result.isError():
                            _LOGGER.error(
                                "Error reading register %d: %s",
                                address,
                                result,
                            )
                            continue
                        if count == 2:
                            value = (
                                result.registers[0] << 16
                            ) | result.registers[1]
                            if sensor_info.get("data_type") == "int32":
                                value = to_signed_32bit(value)
                        else:
                            value = result.registers[0]
                            if sensor_info.get("data_type") == "int16":
                                value = to_signed_16bit(value)
                        if "scale" in sensor_info:
                            value = value * sensor_info["scale"]
                        # Prüfe auf Override-Name
                        override_name = None
                        if hasattr(self, "sensor_overrides"):
                            override_name = self.sensor_overrides.get(
                                f"boil{boil_idx}_{sensor_id}"
                            )
                        key = (
                            override_name
                            if override_name
                            else f"boil{boil_idx}_{sensor_id}"
                        )
                        data[key] = value
                    except Exception as ex:
                        _LOGGER.error(
                            "Error reading register %d: %s",
                            address,
                            ex,
                        )

            # Read buffer sensors
            num_buff = self.entry.data.get("num_buff", 0)
            for buff_idx in range(1, num_buff + 1):
                base_address = generate_base_addresses("buff", num_buff)[
                    buff_idx
                ]
                for sensor_id, sensor_info in BUFF_SENSOR_TEMPLATES.items():
                    if self.is_register_disabled(
                        base_address + sensor_info["relative_address"]
                    ):
                        continue
                    try:
                        address = (
                            base_address + sensor_info["relative_address"]
                        )
                        count = (
                            2 if sensor_info.get("data_type") == "int32" else 1
                        )
                        result = await self.hass.async_add_executor_job(
                            self.client.read_holding_registers,
                            address,
                            count,
                            self.entry.data.get("slave_id", 1),
                        )
                        if hasattr(result, "isError") and result.isError():
                            _LOGGER.error(
                                "Error reading register %d: %s",
                                address,
                                result,
                            )
                            continue
                        if count == 2:
                            value = (
                                result.registers[0] << 16
                            ) | result.registers[1]
                            if sensor_info.get("data_type") == "int32":
                                value = to_signed_32bit(value)
                        else:
                            value = result.registers[0]
                            if sensor_info.get("data_type") == "int16":
                                value = to_signed_16bit(value)
                        if "scale" in sensor_info:
                            value = value * sensor_info["scale"]
                        # Prüfe auf Override-Name
                        override_name = None
                        if hasattr(self, "sensor_overrides"):
                            override_name = self.sensor_overrides.get(
                                f"buff{buff_idx}_{sensor_id}"
                            )
                        key = (
                            override_name
                            if override_name
                            else f"buff{buff_idx}_{sensor_id}"
                        )
                        data[key] = value
                    except Exception as ex:
                        _LOGGER.error(
                            "Error reading register %d: %s",
                            address,
                            ex,
                        )

            # Read solar sensors
            num_sol = self.entry.data.get("num_sol", 0)
            for sol_idx in range(1, num_sol + 1):
                base_address = generate_base_addresses("sol", num_sol)[sol_idx]
                for sensor_id, sensor_info in SOL_SENSOR_TEMPLATES.items():
                    if self.is_register_disabled(
                        base_address + sensor_info["relative_address"]
                    ):
                        continue
                    try:
                        address = (
                            base_address + sensor_info["relative_address"]
                        )
                        count = (
                            2 if sensor_info.get("data_type") == "int32" else 1
                        )
                        result = await self.hass.async_add_executor_job(
                            self.client.read_holding_registers,
                            address,
                            count,
                            self.entry.data.get("slave_id", 1),
                        )
                        if hasattr(result, "isError") and result.isError():
                            _LOGGER.error(
                                "Error reading register %d: %s",
                                address,
                                result,
                            )
                            continue
                        if count == 2:
                            value = (
                                result.registers[0] << 16
                            ) | result.registers[1]
                            if sensor_info.get("data_type") == "int32":
                                value = to_signed_32bit(value)
                        else:
                            value = result.registers[0]
                            if sensor_info.get("data_type") == "int16":
                                value = to_signed_16bit(value)
                        if "scale" in sensor_info:
                            value = value * sensor_info["scale"]
                        # Prüfe auf Override-Name
                        override_name = None
                        if hasattr(self, "sensor_overrides"):
                            override_name = self.sensor_overrides.get(
                                f"sol{sol_idx}_{sensor_id}"
                            )
                        key = (
                            override_name
                            if override_name
                            else f"sol{sol_idx}_{sensor_id}"
                        )
                        data[key] = value
                    except Exception as ex:
                        _LOGGER.error(
                            "Error reading register %d: %s",
                            address,
                            ex,
                        )

            # Read heating circuit sensors
            num_hc = self.entry.data.get("num_hc", 1)
            for hc_idx in range(1, num_hc + 1):
                base_address = generate_base_addresses("hc", num_hc)[hc_idx]
                for sensor_id, sensor_info in HC_SENSOR_TEMPLATES.items():
                    if self.is_register_disabled(
                        base_address + sensor_info["relative_address"]
                    ):
                        continue
                    try:
                        address = (
                            base_address + sensor_info["relative_address"]
                        )
                        count = (
                            2 if sensor_info.get("data_type") == "int32" else 1
                        )
                        result = await self.hass.async_add_executor_job(
                            self.client.read_holding_registers,
                            address,
                            count,
                            self.entry.data.get("slave_id", 1),
                        )
                        if hasattr(result, "isError") and result.isError():
                            _LOGGER.error(
                                "Error reading register %d: %s",
                                address,
                                result,
                            )
                            continue
                        if count == 2:
                            value = (
                                result.registers[0] << 16
                            ) | result.registers[1]
                            if sensor_info.get("data_type") == "int32":
                                value = to_signed_32bit(value)
                        else:
                            value = result.registers[0]
                            if sensor_info.get("data_type") == "int16":
                                value = to_signed_16bit(value)
                        if "scale" in sensor_info:
                            value = value * sensor_info["scale"]
                        # Prüfe auf Override-Name
                        override_name = None
                        if hasattr(self, "sensor_overrides"):
                            override_name = self.sensor_overrides.get(
                                f"hc{hc_idx}_{sensor_id}"
                            )
                        key = (
                            override_name
                            if override_name
                            else f"hc{hc_idx}_{sensor_id}"
                        )
                        data[key] = value
                    except Exception as ex:
                        _LOGGER.error(
                            "Error reading register %d: %s",
                            address,
                            ex,
                        )

            # Update room temperature and PV surplus only after Home Assistant
            # has started. This prevents timing issues with template sensors
            if hasattr(self, '_ha_started') and self._ha_started:
                # Note: Writing operations moved to services.py
                pass

            return data

        except Exception as ex:
            _LOGGER.error("Error updating data: %s", ex)
            if self.client:
                self.client.close()
                self.client = None
            raise UpdateFailed(f"Error fetching Lambda data: {ex}")

    def _on_ha_started(self, event):
        """Handle Home Assistant started event."""
        self._ha_started = True
        _LOGGER.debug(
            "Home Assistant started - enabling room temperature and PV "
            "surplus updates"
        )

    async def _connect(self):
        """Connect to the Modbus device."""
        from pymodbus.client import ModbusTcpClient

        self.client = ModbusTcpClient(self.host, port=self.port)
        try:
            connected = await self.hass.async_add_executor_job(
                self.client.connect
            )
            if not connected:
                raise ConnectionError(
                    "Could not connect to Modbus TCP at "
                    f"{self.host}:{self.port}"
                )
        except Exception as ex:
            _LOGGER.error("Failed to connect to Modbus TCP: %s", ex)
            self.client = None
            raise UpdateFailed(f"Failed to connect to Modbus TCP: {ex}")

    async def _load_sensor_overrides(self) -> dict[str, str]:
        """Load sensor name overrides from YAML config file."""
        config_path = os.path.join(self._config_dir, "lambda_wp_config.yaml")
        if not os.path.exists(config_path):
            return {}
        try:
            async with aiofiles.open(config_path, "r") as f:
                content = await f.read()
                config = yaml.safe_load(content) or {}
                overrides = {}
                for sensor in config.get("sensors_names_override", []):
                    if "id" in sensor and "override_name" in sensor:
                        overrides[sensor["id"]] = sensor["override_name"]
                return overrides
        except Exception as e:
            _LOGGER.error(
                f"Fehler beim Laden der Sensor-Namen-Überschreibungen: {e}"
            )
            return {}
