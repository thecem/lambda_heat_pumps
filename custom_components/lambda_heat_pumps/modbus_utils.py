"""Modbus utilities for Lambda Heat Pumps integration."""

import logging
from pymodbus.client import ModbusTcpClient, AsyncModbusTcpClient

_LOGGER = logging.getLogger(__name__)


def _test_api_compatibility(client, method_name):
    """Test which API version is available."""
    method = getattr(client, method_name, None)
    if not method:
        return None

    # Test if method accepts keyword arguments (pymodbus >= 3.0)
    import inspect

    try:
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())

        # Check if method accepts 'slave' parameter (pymodbus >= 3.0)
        if "slave" in params:
            return "slave"
        # Check if method accepts 'unit' parameter (pymodbus 2.x)
        elif "unit" in params:
            return "unit"
        # Otherwise, no slave parameter (pymodbus < 2.0)
        else:
            return "none"
    except (ValueError, TypeError):
        # Fallback: try to determine by pymodbus version
        try:
            import pymodbus

            version = pymodbus.__version__
            if version.startswith("3"):
                return "slave"
            elif version.startswith("2"):
                return "unit"
            else:
                return "none"
        except (ImportError, AttributeError):
            # Last resort: assume older version
            return "none"


def read_holding_registers(client: ModbusTcpClient, address, count, slave_id=1):
    """Read holding registers with compatibility."""
    try:
        api_type = _test_api_compatibility(client, "read_holding_registers")
        _LOGGER.debug("API type detected: %s for read_holding_registers", api_type)

        if api_type == "slave":
            # pymodbus >= 3.0
            return client.read_holding_registers(address, count=count, slave=slave_id)
        elif api_type == "unit":
            # pymodbus 2.x
            return client.read_holding_registers(address, count, unit=slave_id)
        else:
            # pymodbus < 2.0
            return client.read_holding_registers(address, count)
    except Exception as e:
        _LOGGER.error("Modbus error in read_holding_registers: %s", str(e))
        _LOGGER.error(
            "API type was: %s, address: %s, count: %s, slave_id: %s",
            _test_api_compatibility(client, "read_holding_registers"),
            address,
            count,
            slave_id,
        )
        raise


def write_register(client: ModbusTcpClient, address, value, slave_id=1):
    """Write single register with compatibility."""
    try:
        api_type = _test_api_compatibility(client, "write_register")

        if api_type == "slave":
            # pymodbus >= 3.0
            return client.write_register(address, value, slave=slave_id)
        elif api_type == "unit":
            # pymodbus 2.x
            return client.write_register(address, value, unit=slave_id)
        else:
            # pymodbus < 2.0
            return client.write_register(address, value)
    except Exception as e:
        _LOGGER.error("Modbus error in write_register: %s", str(e))
        raise


def write_registers(client: ModbusTcpClient, address, values, slave_id=1):
    """Write multiple registers with compatibility."""
    try:
        api_type = _test_api_compatibility(client, "write_registers")

        if api_type == "slave":
            # pymodbus >= 3.0
            return client.write_registers(address, values, slave=slave_id)
        elif api_type == "unit":
            # pymodbus 2.x
            return client.write_registers(address, values, unit=slave_id)
        else:
            # pymodbus < 2.0
            return client.write_registers(address, values)
    except Exception as e:
        _LOGGER.error("Modbus error in write_registers: %s", str(e))
        raise


def read_input_registers(client: ModbusTcpClient, address, count, slave_id=1):
    """Read input registers with compatibility."""
    try:
        api_type = _test_api_compatibility(client, "read_input_registers")

        if api_type == "slave":
            # pymodbus >= 3.0
            return client.read_input_registers(address, count=count, slave=slave_id)
        elif api_type == "unit":
            # pymodbus 2.x
            return client.read_input_registers(address, count, unit=slave_id)
        else:
            # pymodbus < 2.0
            return client.read_input_registers(address, count)
    except Exception as e:
        _LOGGER.error("Modbus error in read_input_registers: %s", str(e))
        raise


# ==================== ASYNCHRONOUS WRAPPERS ====================


def _test_async_api_compatibility(client, method_name):
    """Test which async API version is available."""
    method = getattr(client, method_name, None)
    if not method:
        return None

    # Test if method accepts keyword arguments (pymodbus >= 3.0)
    import inspect

    try:
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())

        # Check if method accepts 'slave' parameter (pymodbus >= 3.0)
        if "slave" in params:
            return "slave"
        # Check if method accepts 'unit' parameter (pymodbus 2.x)
        elif "unit" in params:
            return "unit"
        # Otherwise, no slave parameter (pymodbus < 2.0)
        else:
            return "none"
    except (ValueError, TypeError):
        # Fallback: try to determine by pymodbus version
        try:
            import pymodbus

            version = pymodbus.__version__
            if version.startswith("3"):
                return "slave"
            elif version.startswith("2"):
                return "unit"
            else:
                return "none"
        except (ImportError, AttributeError):
            # Last resort: assume older version
            return "none"


async def async_read_holding_registers(
    client: AsyncModbusTcpClient, address, count, slave_id=1
):
    """Read holding registers with async compatibility."""
    try:
        api_type = _test_async_api_compatibility(client, "read_holding_registers")
        _LOGGER.debug(
            "Async API type detected: %s for read_holding_registers", api_type
        )

        if api_type == "slave":
            # pymodbus >= 3.0
            return await client.read_holding_registers(
                address, count=count, slave=slave_id
            )
        elif api_type == "unit":
            # pymodbus 2.x
            return await client.read_holding_registers(address, count, unit=slave_id)
        else:
            # pymodbus < 2.0
            return await client.read_holding_registers(address, count)
    except Exception as e:
        _LOGGER.error("Modbus error in async_read_holding_registers: %s", str(e))
        _LOGGER.error(
            "Async API type was: %s, address: %s, count: %s, slave_id: %s",
            _test_async_api_compatibility(client, "read_holding_registers"),
            address,
            count,
            slave_id,
        )
        raise


async def async_write_register(
    client: AsyncModbusTcpClient, address, value, slave_id=1
):
    """Write single register with async compatibility."""
    try:
        api_type = _test_async_api_compatibility(client, "write_register")

        if api_type == "slave":
            # pymodbus >= 3.0
            return await client.write_register(address, value, slave=slave_id)
        elif api_type == "unit":
            # pymodbus 2.x
            return await client.write_register(address, value, unit=slave_id)
        else:
            # pymodbus < 2.0
            return await client.write_register(address, value)
    except Exception as e:
        _LOGGER.error("Modbus error in async_write_register: %s", str(e))
        raise


async def async_write_registers(
    client: AsyncModbusTcpClient, address, values, slave_id=1
):
    """Write multiple registers with async compatibility."""
    try:
        api_type = _test_async_api_compatibility(client, "write_registers")

        if api_type == "slave":
            # pymodbus >= 3.0
            return await client.write_registers(address, values, slave=slave_id)
        elif api_type == "unit":
            # pymodbus 2.x
            return await client.write_registers(address, values, unit=slave_id)
        else:
            # pymodbus < 2.0
            return await client.write_registers(address, values)
    except Exception as e:
        _LOGGER.error("Modbus error in async_write_registers: %s", str(e))
        raise


async def async_read_input_registers(
    client: AsyncModbusTcpClient, address, count, slave_id=1
):
    """Read input registers with async compatibility."""
    try:
        api_type = _test_async_api_compatibility(client, "read_input_registers")

        if api_type == "slave":
            # pymodbus >= 3.0
            return await client.read_input_registers(
                address, count=count, slave=slave_id
            )
        elif api_type == "unit":
            # pymodbus 2.x
            return await client.read_input_registers(address, count, unit=slave_id)
        else:
            # pymodbus < 2.0
            return await client.read_input_registers(address, count)
    except Exception as e:
        _LOGGER.error("Modbus error in async_read_input_registers: %s", str(e))
        raise
