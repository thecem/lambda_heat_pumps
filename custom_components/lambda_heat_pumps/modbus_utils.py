"""Modbus utilities for Lambda Heat Pumps integration."""
import logging

_LOGGER = logging.getLogger(__name__)


def modbus_call(client, method, *args, **kwargs):
    """Universal Modbus compatibility wrapper."""
    slave_id = kwargs.pop('slave_id', 1)  # Default slave_id = 1

    # Prüfe ob die Methode existiert
    if not hasattr(client, method):
        raise AttributeError(f"Modbus client missing method: {method}")

    _LOGGER.debug(
        f"Modbus call: {method}(address={args[0] if args else 'N/A'}, "
        f"slave_id={slave_id})"
    )

    try:
        # Neue API (pymodbus >= 3.0) - slave=
        result = getattr(client, method)(*args, **kwargs, slave=slave_id)
        _LOGGER.debug("Modbus call successful with new API (slave=)")
        return result
    except (TypeError, AttributeError):
        try:
            # Mittlere API (pymodbus 2.x) - unit=
            result = getattr(client, method)(*args, **kwargs, unit=slave_id)
            _LOGGER.debug("Modbus call successful with legacy API (unit=)")
            return result
        except TypeError:
            try:
                # Sehr alte API (pymodbus < 2.0) - kein Parameter
                result = getattr(client, method)(*args, **kwargs)
                _LOGGER.debug(
                    "Modbus call successful with very old API (no parameter)"
                )
                return result
            except Exception as e:
                _LOGGER.error("Modbus error in %s: %s", method, str(e))
                raise


def read_holding_registers(client, address, count, slave_id=1):
    """Read holding registers with compatibility."""
    return modbus_call(
        client, "read_holding_registers", address, count, slave_id=slave_id
    )


def write_register(client, address, value, slave_id=1):
    """Write single register with compatibility."""
    return modbus_call(
        client, "write_register", address, value, slave_id=slave_id
    )


def write_registers(client, address, values, slave_id=1):
    """Write multiple registers with compatibility."""
    return modbus_call(
        client, "write_registers", address, values, slave_id=slave_id
    )


def read_input_registers(client, address, count, slave_id=1):
    """Read input registers with compatibility."""
    return modbus_call(
        client, "read_input_registers", address, count, slave_id=slave_id
    )
