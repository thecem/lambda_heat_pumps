"""Fixed Modbus utilities for Lambda Heat Pumps integration - HA Compatible."""

import logging
import asyncio
from typing import Any

_LOGGER = logging.getLogger(__name__)


def _detect_pymodbus_api(client, method_name: str) -> str:
    """Detect pymodbus API version compatibility."""
    try:
        import inspect

        method = getattr(client, method_name, None)
        if not method:
            return "none"

        sig = inspect.signature(method)
        params = list(sig.parameters.keys())

        if "slave" in params:
            return "slave"  # pymodbus >= 3.0
        elif "unit" in params:
            return "unit"  # pymodbus 2.x
        else:
            return "none"  # pymodbus < 2.0
    except Exception:
        # Fallback based on version
        try:
            import pymodbus

            version = pymodbus.__version__
            if version.startswith("3"):
                return "slave"
            elif version.startswith("2"):
                return "unit"
            else:
                return "none"
        except ImportError:
            return "none"


async def async_read_holding_registers(
    client, address: int, count: int, slave_id: int = 1
) -> Any:
    """Read holding registers with full API compatibility."""
    try:
        # For pymodbus 3.11.1, use only address as positional, rest as kwargs
        try:
            # Try with slave parameter (most common in 3.x)
            return await client.read_holding_registers(
                address, count=count, slave=slave_id
            )
        except (TypeError, AttributeError):
            try:
                # Try with unit parameter
                return await client.read_holding_registers(
                    address, count=count, unit=slave_id
                )
            except (TypeError, AttributeError):
                try:
                    # Try without slave/unit parameter
                    return await client.read_holding_registers(address, count=count)
                except TypeError:
                    # Last resort: only address and count as positional
                    return await client.read_holding_registers(address, count)

    except Exception as e:
        _LOGGER.exception("Modbus read error at address %d: %s", address, e)
        raise


async def async_read_input_registers(
    client, address: int, count: int, slave_id: int = 1
) -> Any:
    """Read input registers with full API compatibility."""
    try:
        # For pymodbus 3.11.1, use only address as positional, rest as kwargs
        try:
            # Try with slave parameter (most common in 3.x)
            return await client.read_input_registers(
                address, count=count, slave=slave_id
            )
        except (TypeError, AttributeError):
            try:
                # Try with unit parameter
                return await client.read_input_registers(
                    address, count=count, unit=slave_id
                )
            except (TypeError, AttributeError):
                try:
                    # Try without slave/unit parameter
                    return await client.read_input_registers(address, count=count)
                except TypeError:
                    # Last resort: only address and count as positional
                    return await client.read_input_registers(address, count)

    except Exception as e:
        _LOGGER.exception("Modbus read error at address %d", address)
        raise


async def async_write_register(
    client, address: int, value: int, slave_id: int = 1
) -> Any:
    """Write single register with full API compatibility."""
    try:
        # For pymodbus 3.11.1, use address as positional, rest as kwargs
        try:
            # Try with slave parameter (most common in 3.x)
            return await client.write_register(address, value, slave=slave_id)
        except (TypeError, AttributeError):
            try:
                # Try with unit parameter
                return await client.write_register(address, value, unit=slave_id)
            except (TypeError, AttributeError):
                # Try without slave/unit parameter
                return await client.write_register(address, value)

    except Exception as e:
        _LOGGER.exception("Modbus write error at address %d", address)
        raise


async def async_write_registers(
    client, address: int, values: list, slave_id: int = 1
) -> Any:
    """Write multiple registers with full API compatibility."""
    try:
        api_type = _detect_pymodbus_api(client, "write_registers")

        if api_type == "slave":
            return await client.write_registers(address, values, slave=slave_id)
        elif api_type == "unit":
            return await client.write_registers(address, values, unit=slave_id)
        else:
            return await client.write_registers(address, values)

    except Exception as e:
        _LOGGER.error("Modbus write error at address %d: %s", address, e)
        raise


# Synchronous versions for backward compatibility
def read_holding_registers(client, address: int, count: int, slave_id: int = 1) -> Any:
    """Synchronous read holding registers with compatibility."""
    try:
        api_type = _detect_pymodbus_api(client, "read_holding_registers")

        if api_type == "slave":
            try:
                return client.read_holding_registers(
                    address, count=count, slave=slave_id
                )
            except TypeError:
                return client.read_holding_registers(address, count, slave=slave_id)
        elif api_type == "unit":
            return client.read_holding_registers(address, count, unit=slave_id)
        else:
            return client.read_holding_registers(address, count)

    except Exception as e:
        _LOGGER.error("Modbus read error at address %d: %s", address, e)
        raise


def write_register(client, address: int, value: int, slave_id: int = 1) -> Any:
    """Synchronous write register with compatibility."""
    try:
        api_type = _detect_pymodbus_api(client, "write_register")

        if api_type == "slave":
            return client.write_register(address, value, slave=slave_id)
        elif api_type == "unit":
            return client.write_register(address, value, unit=slave_id)
        else:
            return client.write_register(address, value)

    except Exception as e:
        _LOGGER.error("Modbus write error at address %d: %s", address, e)
        raise


def write_registers(client, address: int, values: list, slave_id: int = 1) -> Any:
    """Synchronous write registers with compatibility."""
    try:
        api_type = _detect_pymodbus_api(client, "write_registers")

        if api_type == "slave":
            return client.write_registers(address, values, slave=slave_id)
        elif api_type == "unit":
            return client.write_registers(address, values, unit=slave_id)
        else:
            return client.write_registers(address, values)

    except Exception as e:
        _LOGGER.error("Modbus write error at address %d: %s", address, e)
        raise


def read_input_registers(client, address: int, count: int, slave_id: int = 1) -> Any:
    """Synchronous read input registers with compatibility."""
    try:
        api_type = _detect_pymodbus_api(client, "read_input_registers")

        if api_type == "slave":
            try:
                return client.read_input_registers(address, count=count, slave=slave_id)
            except TypeError:
                return client.read_input_registers(address, count, slave=slave_id)
        elif api_type == "unit":
            return client.read_input_registers(address, count, unit=slave_id)
        else:
            return client.read_input_registers(address, count)

    except Exception as e:
        _LOGGER.error("Modbus read error at address %d: %s", address, e)
        raise
