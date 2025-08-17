"""
Modulare Lambda Heat Pump Register-Verwaltung basierend auf CSV-Dokumentation und Hardware-Scan

Dieses Modul implementiert automatische Erkennung und Konfiguration aller verfügbaren
Lambda Heat Pump Module basierend auf:
1. CSV-Dokumentation (lambda_register.csv)
2. Hardware-Scan Ergebnissen (lambda_comprehensive_scan_*.json)
3. Undokumentierte Register-Entdeckungen
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Any
import logging
import json
from pathlib import Path

_LOGGER = logging.getLogger(__name__)


@dataclass
class RegisterTemplate:
    """Template für ein einzelnes Register"""

    register: int
    name: str
    unit: str
    scale: float = 1.0
    precision: int = 1
    data_type: str = "uint16"
    writeable: bool = False
    state_class: Optional[str] = None
    device_class: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    documented: bool = True


@dataclass
class ModuleTemplate:
    """Template für ein komplettes Modul (z.B. Heat Pump, Boiler, etc.)"""

    name: str
    index: int
    subindex_range: range
    base_address: int
    registers: dict[int, RegisterTemplate] = field(default_factory=dict)
    required_registers: list[int] = field(default_factory=list)
    optional_registers: list[int] = field(default_factory=list)

    @property
    def address_range(self) -> range:
        """Berechne Adressbereich für dieses Modul"""
        start = self.base_address
        end = start + (len(self.subindex_range) * 100)
        return range(start, end)


class LambdaModularRegistry:
    """
    Zentrale Registry für alle Lambda Heat Pump Module

    Basiert auf der CSV-Adressierung: Index*1000 + Subindex*100 + Number
    """

    def __init__(self):
        self.modules: dict[str, ModuleTemplate] = {}
        self.discovered_registers: dict[int, Any] = {}
        self.undocumented_registers: dict[int, RegisterTemplate] = {}
        self._setup_module_templates()

    def _setup_module_templates(self):
        """Setup aller Module basierend auf CSV-Dokumentation"""

        # SEKTION 1: General Ambient (Index 0, Subindex 0)
        self.modules["general_ambient"] = ModuleTemplate(
            name="General Ambient",
            index=0,
            subindex_range=range(0, 1),
            base_address=0,
            registers={
                0: RegisterTemplate(
                    0, "Error Number", "", writeable=False, state_class="total"
                ),
                1: RegisterTemplate(
                    1, "Operating State", "", writeable=False, icon="mdi:state-machine"
                ),
                2: RegisterTemplate(
                    2,
                    "Actual Ambient Temp",
                    "°C",
                    scale=0.1,
                    device_class="temperature",
                ),
                3: RegisterTemplate(
                    3,
                    "Average Ambient Temp 1h",
                    "°C",
                    scale=0.1,
                    device_class="temperature",
                ),
                4: RegisterTemplate(
                    4,
                    "Calculated Ambient Temp",
                    "°C",
                    scale=0.1,
                    device_class="temperature",
                ),
            },
            required_registers=[0, 1, 2],
            optional_registers=[3, 4],
        )

        # SEKTION 2: General E-Manager (Index 0, Subindex 1)
        self.modules["general_e_manager"] = ModuleTemplate(
            name="General E-Manager",
            index=0,
            subindex_range=range(1, 2),
            base_address=100,
            registers={
                100: RegisterTemplate(
                    100, "Error Number", "", writeable=False, state_class="total"
                ),
                101: RegisterTemplate(
                    101,
                    "Operating State",
                    "",
                    writeable=False,
                    icon="mdi:state-machine",
                ),
                102: RegisterTemplate(
                    102, "Actual Power", "W", scale=0.1, device_class="power"
                ),
                103: RegisterTemplate(
                    103, "Actual Power Consumption", "W", device_class="power"
                ),
                104: RegisterTemplate(
                    104,
                    "Power Consumption Setpoint",
                    "W",
                    device_class="power",
                    writeable=True,
                ),
            },
            required_registers=[100, 101, 102],
            optional_registers=[103, 104],
        )

        # SEKTION 3: Heat Pump (Index 1, Subindex 0-2)
        self.modules["heat_pump"] = ModuleTemplate(
            name="Heat Pump",
            index=1,
            subindex_range=range(0, 3),
            base_address=1000,
            registers={
                # Dokumentierte Register (1000-1021)
                1000: RegisterTemplate(
                    1000, "HP Error State", "", writeable=False, state_class="total"
                ),
                1001: RegisterTemplate(
                    1001, "HP Error Number", "", writeable=False, state_class="total"
                ),
                1002: RegisterTemplate(
                    1002, "HP State", "", writeable=False, icon="mdi:heat-pump"
                ),
                1003: RegisterTemplate(
                    1003,
                    "Operating State",
                    "",
                    writeable=False,
                    icon="mdi:state-machine",
                ),
                1004: RegisterTemplate(
                    1004, "T-Flow", "°C", scale=0.01, device_class="temperature"
                ),
                1005: RegisterTemplate(
                    1005, "T-Return", "°C", scale=0.01, device_class="temperature"
                ),
                1006: RegisterTemplate(1006, "Vol. Sink", "l/min", scale=0.01),
                1007: RegisterTemplate(
                    1007, "T-EQin", "°C", scale=0.01, device_class="temperature"
                ),
                1008: RegisterTemplate(
                    1008, "T-EQout", "°C", scale=0.01, device_class="temperature"
                ),
                1009: RegisterTemplate(1009, "Vol. Source", "l/min", scale=0.01),
                1010: RegisterTemplate(1010, "Compressor Rating", "%", scale=0.01),
                1011: RegisterTemplate(
                    1011, "Qp Heating", "kW", scale=0.1, device_class="power"
                ),
                1012: RegisterTemplate(
                    1012, "FI Power Consumption", "W", device_class="power"
                ),
                1013: RegisterTemplate(1013, "COP", "", scale=0.01),
                1014: RegisterTemplate(
                    1014, "Modbus Request Release Password", "", writeable=True
                ),
                1015: RegisterTemplate(1015, "Request Type", "", writeable=True),
                1016: RegisterTemplate(
                    1016, "Request Flow Line Temp", "°C", scale=0.1, writeable=True
                ),
                1017: RegisterTemplate(
                    1017, "Request Return Line Temp", "°C", scale=0.1, writeable=True
                ),
                1018: RegisterTemplate(
                    1018, "Request Heat Sink Temp Diff", "K", scale=0.1, writeable=True
                ),
                1019: RegisterTemplate(
                    1019, "Relais State 2nd Stage", "", writeable=False
                ),
                1020: RegisterTemplate(
                    1020,
                    "Statistic VdA E (Teil 1)",
                    "Wh",
                    state_class="total_increasing",
                ),
                1021: RegisterTemplate(
                    1021,
                    "Statistic VdA E (Teil 2)",
                    "Wh",
                    state_class="total_increasing",
                ),
            },
            required_registers=[1000, 1001, 1002, 1003],
            optional_registers=[
                1004,
                1005,
                1006,
                1007,
                1008,
                1009,
                1010,
                1011,
                1012,
                1013,
            ],
        )

        # SEKTION 4: Boiler (Index 2, Subindex 0-4)
        self.modules["boiler"] = ModuleTemplate(
            name="Boiler",
            index=2,
            subindex_range=range(0, 5),
            base_address=2000,
            registers={
                2000: RegisterTemplate(
                    2000, "Error Number", "", writeable=False, state_class="total"
                ),
                2001: RegisterTemplate(
                    2001,
                    "Operating State",
                    "",
                    writeable=False,
                    icon="mdi:state-machine",
                ),
                2002: RegisterTemplate(
                    2002,
                    "Actual High Temp",
                    "°C",
                    scale=0.1,
                    device_class="temperature",
                ),
                2003: RegisterTemplate(
                    2003, "Actual Low Temp", "°C", scale=0.1, device_class="temperature"
                ),
                2004: RegisterTemplate(
                    2004,
                    "Actual Circulation Temp",
                    "°C",
                    scale=0.1,
                    device_class="temperature",
                ),
                2005: RegisterTemplate(
                    2005, "Circulation Pump State", "", icon="mdi:pump"
                ),
                2050: RegisterTemplate(
                    2050, "Max Boiler Temp", "°C", scale=0.1, writeable=True
                ),
            },
            required_registers=[2000, 2001, 2002],
            optional_registers=[2003, 2004, 2005, 2050],
        )

        # SEKTION 5: Buffer (Index 3, Subindex 0-4)
        self.modules["buffer"] = ModuleTemplate(
            name="Buffer",
            index=3,
            subindex_range=range(0, 5),
            base_address=3000,
            registers={
                3000: RegisterTemplate(
                    3000, "Error Number", "", writeable=False, state_class="total"
                ),
                3001: RegisterTemplate(
                    3001,
                    "Operating State",
                    "",
                    writeable=False,
                    icon="mdi:state-machine",
                ),
                3002: RegisterTemplate(
                    3002,
                    "Actual High Temp",
                    "°C",
                    scale=0.1,
                    device_class="temperature",
                ),
                3003: RegisterTemplate(
                    3003, "Actual Low Temp", "°C", scale=0.1, device_class="temperature"
                ),
                3004: RegisterTemplate(
                    3004,
                    "Modbus Buffer Temp High",
                    "°C",
                    scale=0.1,
                    device_class="temperature",
                ),
                3005: RegisterTemplate(3005, "Request Type", "", writeable=True),
                3006: RegisterTemplate(
                    3006,
                    "Request Flow Line Temp Setpoint",
                    "°C",
                    scale=0.1,
                    writeable=True,
                ),
                3007: RegisterTemplate(
                    3007,
                    "Request Return Line Temp Setpoint",
                    "°C",
                    scale=0.1,
                    writeable=True,
                ),
                3008: RegisterTemplate(
                    3008, "Request Heat Sink Temp Diff", "K", scale=0.1, writeable=True
                ),
                3009: RegisterTemplate(
                    3009,
                    "Modbus Request Heating Capacity",
                    "kW",
                    scale=0.1,
                    writeable=True,
                ),
                3050: RegisterTemplate(
                    3050, "Max Buffer Temp", "°C", scale=0.1, writeable=True
                ),
            },
            required_registers=[3000, 3001, 3002],
            optional_registers=[3003, 3004, 3005, 3006, 3007, 3008, 3009, 3050],
        )

        # SEKTION 6: Solar (Index 4, Subindex 0-1)
        self.modules["solar"] = ModuleTemplate(
            name="Solar",
            index=4,
            subindex_range=range(0, 2),
            base_address=4000,
            registers={
                4000: RegisterTemplate(
                    4000, "Error Number", "", writeable=False, state_class="total"
                ),
                4001: RegisterTemplate(
                    4001,
                    "Operating State",
                    "",
                    writeable=False,
                    icon="mdi:state-machine",
                ),
                4002: RegisterTemplate(
                    4002, "Collector Temp", "°C", scale=0.1, device_class="temperature"
                ),
                4003: RegisterTemplate(
                    4003, "Buffer 1 Temp", "°C", scale=0.1, device_class="temperature"
                ),
                4004: RegisterTemplate(
                    4004, "Buffer 2 Temp", "°C", scale=0.1, device_class="temperature"
                ),
                4050: RegisterTemplate(
                    4050, "Max Buffer Temp", "°C", scale=0.1, writeable=True
                ),
                4051: RegisterTemplate(
                    4051, "Buffer Changeover Temp", "°C", scale=0.1, writeable=True
                ),
            },
            required_registers=[4000, 4001, 4002],
            optional_registers=[4003, 4004, 4050, 4051],
        )

        # SEKTION 7: Heating Circuit (Index 5, Subindex 0-11)
        self.modules["heating_circuit"] = ModuleTemplate(
            name="Heating Circuit",
            index=5,
            subindex_range=range(0, 12),
            base_address=5000,
            registers={
                5000: RegisterTemplate(
                    5000, "Error Number", "", writeable=False, state_class="total"
                ),
                5001: RegisterTemplate(
                    5001,
                    "Operating State",
                    "",
                    writeable=False,
                    icon="mdi:state-machine",
                ),
                5002: RegisterTemplate(
                    5002, "Flow Line Temp", "°C", scale=0.1, device_class="temperature"
                ),
                5003: RegisterTemplate(
                    5003,
                    "Return Line Temp",
                    "°C",
                    scale=0.1,
                    device_class="temperature",
                ),
                5004: RegisterTemplate(
                    5004,
                    "Room Device Temp",
                    "°C",
                    scale=0.1,
                    device_class="temperature",
                ),
                5005: RegisterTemplate(
                    5005, "Setpoint Flow Line Temp", "°C", scale=0.1, writeable=True
                ),
                5006: RegisterTemplate(5006, "Operating Mode", "", writeable=True),
                5007: RegisterTemplate(
                    5007, "Target Temp Flow Line", "°C", scale=0.1, writeable=True
                ),
                5050: RegisterTemplate(
                    5050, "Offset Flow Line Setpoint", "K", scale=0.1, writeable=True
                ),
                5051: RegisterTemplate(
                    5051, "Room Heating Temp", "°C", scale=0.1, writeable=True
                ),
                5052: RegisterTemplate(
                    5052, "Room Cooling Temp", "°C", scale=0.1, writeable=True
                ),
            },
            required_registers=[5000, 5001, 5004],
            optional_registers=[5002, 5003, 5005, 5006, 5007, 5050, 5051, 5052],
        )

        # Setup undokumentierte Register (Heat Pump Sektion erweitern)
        self._setup_undocumented_registers()

    def _setup_undocumented_registers(self):
        """Setup der undokumentierten Register basierend auf Hardware-Scan"""

        undocumented_hp_registers = {
            # Erweiterte HP Parameter (1024-1033)
            1024: RegisterTemplate(
                1024, "Extended HP Parameter 1", "", documented=False
            ),
            1025: RegisterTemplate(
                1025,
                "Compressor Outlet Temp",
                "°C",
                scale=0.01,
                device_class="temperature",
                documented=False,
                description="Kompressor-Auslasstemperatur",
            ),
            1026: RegisterTemplate(
                1026,
                "Additional Temp Sensor 1",
                "°C",
                scale=0.01,
                device_class="temperature",
                documented=False,
            ),
            1027: RegisterTemplate(
                1027,
                "Additional Temp Sensor 2",
                "°C",
                scale=0.01,
                device_class="temperature",
                documented=False,
            ),
            1028: RegisterTemplate(
                1028,
                "Additional Temp Sensor 3",
                "°C",
                scale=0.01,
                device_class="temperature",
                documented=False,
            ),
            1029: RegisterTemplate(
                1029,
                "Ambient Temp Sensor 1",
                "°C",
                scale=0.01,
                device_class="temperature",
                documented=False,
            ),
            1030: RegisterTemplate(
                1030,
                "Ambient Temp Sensor 2",
                "°C",
                scale=0.01,
                device_class="temperature",
                documented=False,
            ),
            1031: RegisterTemplate(
                1031, "Extended HP Parameter 7", "", documented=False
            ),
            1032: RegisterTemplate(
                1032, "Extended HP Parameter 8", "", documented=False
            ),
            1033: RegisterTemplate(
                1033, "Extended HP Parameter 9", "", documented=False
            ),
            # Konfigurationsparameter (1050-1060)
            1050: RegisterTemplate(1050, "Config Parameter 1", "", documented=False),
            1051: RegisterTemplate(1051, "Config Parameter 2", "%", documented=False),
            1052: RegisterTemplate(1052, "Config Parameter 3", "%", documented=False),
            1053: RegisterTemplate(1053, "Config Parameter 4", "%", documented=False),
            1054: RegisterTemplate(1054, "Config Parameter 5", "%", documented=False),
            1055: RegisterTemplate(1055, "Config Parameter 6", "%", documented=False),
            1056: RegisterTemplate(1056, "Config Parameter 7", "%", documented=False),
            1057: RegisterTemplate(1057, "Maximum Value", "%", documented=False),
            1058: RegisterTemplate(1058, "Config Parameter 9", "%", documented=False),
            1059: RegisterTemplate(1059, "Config Parameter 10", "%", documented=False),
            1060: RegisterTemplate(1060, "Config Parameter 11", "", documented=False),
        }

        # Zu Heat Pump Modul hinzufügen
        self.modules["heat_pump"].registers.update(undocumented_hp_registers)
        self.undocumented_registers.update(undocumented_hp_registers)

    def load_hardware_scan(self, scan_file_path: str) -> bool:
        """Lade Hardware-Scan Ergebnisse."""
        try:
            with Path(scan_file_path).open() as f:
                scan_data = json.load(f)

            # Die Struktur ist {"responsive_registers": {...}} statt {"registers": {...}}
            self.discovered_registers = scan_data.get("responsive_registers", {})
            _LOGGER.info(
                "Loaded %d discovered registers from %s",
                len(self.discovered_registers),
                scan_file_path,
            )
            return True

        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            _LOGGER.error("Failed to load hardware scan: %s", e)
            return False

    def detect_available_modules(self) -> dict[str, bool]:
        """Erkenne verfügbare Module basierend auf Hardware-Scan"""
        available_modules = {}

        for module_name, module in self.modules.items():
            # Prüfe ob mindestens die required_registers verfügbar sind
            required_found = 0
            for required_reg in module.required_registers:
                if str(required_reg) in self.discovered_registers:
                    required_found += 1

            # Modul ist verfügbar wenn alle required Register gefunden wurden
            if required_found == len(module.required_registers):
                available_modules[module_name] = True
                _LOGGER.info(f"Module '{module_name}' detected as AVAILABLE")
            else:
                available_modules[module_name] = False
                _LOGGER.info(
                    f"Module '{module_name}' detected as NOT AVAILABLE "
                    f"({required_found}/{len(module.required_registers)} required registers found)"
                )

        return available_modules

    def get_module_registers(
        self, module_name: str, *, include_undocumented: bool = True
    ) -> dict[int, RegisterTemplate]:
        """Hole alle Register für ein Modul."""
        if module_name not in self.modules:
            return {}

        module = self.modules[module_name]
        registers = {}

        for reg_addr, register in module.registers.items():
            # Nur verfügbare Register zurückgeben
            if str(reg_addr) in self.discovered_registers:
                # Undokumentierte Register optional ausschließen
                if not include_undocumented and not register.documented:
                    continue
                registers[reg_addr] = register

        return registers

    def get_all_available_registers(
        self, *, include_undocumented: bool = True
    ) -> dict[int, RegisterTemplate]:
        """Hole alle verfügbaren Register aller Module."""
        all_registers = {}

        for module_name in self.modules:
            module_registers = self.get_module_registers(
                module_name, include_undocumented=include_undocumented
            )
            all_registers.update(module_registers)

        return all_registers

    def generate_sensor_config(
        self, module_name: str, device_index: int = 1
    ) -> list[dict[str, Any]]:
        """Generiere Sensor-Konfiguration für ein Modul."""
        registers = self.get_module_registers(module_name)
        sensor_configs = []

        for reg_addr, register in registers.items():
            config = {
                "unique_id": f"lambda_{module_name}_{device_index}_{register.name.lower().replace(' ', '_')}",
                "name": f"{module_name.title()} {device_index} {register.name}",
                "register": reg_addr,
                "unit_of_measurement": register.unit if register.unit else None,
                "scale": register.scale,
                "precision": register.precision,
                "data_type": register.data_type,
                "state_class": register.state_class,
                "device_class": register.device_class,
                "icon": register.icon,
                "entity_registry_enabled_default": register.documented,  # Undokumentierte standardmäßig deaktiviert
            }
            sensor_configs.append(config)

        return sensor_configs

    def get_system_overview(self) -> dict[str, Any]:
        """Generiere System-Übersicht."""
        available_modules = self.detect_available_modules()

        overview = {
            "total_modules": len(self.modules),
            "available_modules": sum(available_modules.values()),
            "total_registers": sum(len(m.registers) for m in self.modules.values()),
            "discovered_registers": len(self.discovered_registers),
            "undocumented_registers": len(self.undocumented_registers),
            "modules": {},
        }

        for module_name, module in self.modules.items():
            available_regs = self.get_module_registers(module_name)
            undoc_regs = {k: v for k, v in available_regs.items() if not v.documented}

            overview["modules"][module_name] = {
                "available": available_modules[module_name],
                "total_registers": len(module.registers),
                "available_registers": len(available_regs),
                "undocumented_registers": len(undoc_regs),
                "address_range": f"{module.base_address}-{module.base_address + 999}",
                "coverage_percentage": round(
                    (len(available_regs) / len(module.registers)) * 100, 1
                )
                if module.registers
                else 0,
            }

        return overview


# Global registry instance
lambda_registry = LambdaModularRegistry()
