"""Test Modbus API compatibility for different pymodbus versions."""

import pytest
from unittest.mock import Mock, patch

from custom_components.lambda_heat_pumps.modbus_utils import (
    _test_api_compatibility,
    _test_async_api_compatibility,
    read_holding_registers,
    write_register,
    write_registers,
    read_input_registers,
    async_read_holding_registers,
    async_write_register,
    async_write_registers,
    async_read_input_registers,
)


class MockModbusClient:
    """Mock Modbus client for testing different API versions."""

    def __init__(self, api_version: str):
        """Initialize with specific API version."""
        self.api_version = api_version
        self._setup_methods()

    def _setup_methods(self):
        """Setup methods with correct signatures based on API version."""
        if self.api_version == "slave":
            # pymodbus 3.x: count=count, slave=slave_id
            self.read_holding_registers = Mock(
                side_effect=self._read_holding_registers_slave
            )
            self.write_register = Mock(
                side_effect=self._write_register_slave
            )
            self.write_registers = Mock(
                side_effect=self._write_registers_slave
            )
            self.read_input_registers = Mock(
                side_effect=self._read_input_registers_slave
            )
        elif self.api_version == "unit":
            # pymodbus 2.x: count, unit=slave_id
            self.read_holding_registers = Mock(
                side_effect=self._read_holding_registers_unit
            )
            self.write_register = Mock(
                side_effect=self._write_register_unit
            )
            self.write_registers = Mock(
                side_effect=self._write_registers_unit
            )
            self.read_input_registers = Mock(
                side_effect=self._read_input_registers_unit
            )
        else:
            # pymodbus 1.x: address, count (no slave/unit)
            self.read_holding_registers = Mock(
                side_effect=self._read_holding_registers_none
            )
            self.write_register = Mock(
                side_effect=self._write_register_none
            )
            self.write_registers = Mock(
                side_effect=self._write_registers_none
            )
            self.read_input_registers = Mock(
                side_effect=self._read_input_registers_none
            )

    def _read_holding_registers_slave(self, address, count=1, slave=1):
        """Mock read_holding_registers for pymodbus 3.x."""
        return Mock(isError=lambda: False, registers=[100])

    def _write_register_slave(self, address, value, slave=1):
        """Mock write_register for pymodbus 3.x."""
        return Mock(isError=lambda: False)

    def _write_registers_slave(self, address, values, slave=1):
        """Mock write_registers for pymodbus 3.x."""
        return Mock(isError=lambda: False)

    def _read_input_registers_slave(self, address, count=1, slave=1):
        """Mock read_input_registers for pymodbus 3.x."""
        return Mock(isError=lambda: False, registers=[100])

    def _read_holding_registers_unit(self, address, count, unit=1):
        """Mock read_holding_registers for pymodbus 2.x."""
        return Mock(isError=lambda: False, registers=[100])

    def _write_register_unit(self, address, value, unit=1):
        """Mock write_register for pymodbus 2.x."""
        return Mock(isError=lambda: False)

    def _write_registers_unit(self, address, values, unit=1):
        """Mock write_registers for pymodbus 2.x."""
        return Mock(isError=lambda: False)

    def _read_input_registers_unit(self, address, count, unit=1):
        """Mock read_input_registers for pymodbus 2.x."""
        return Mock(isError=lambda: False, registers=[100])

    def _read_holding_registers_none(self, address, count):
        """Mock read_holding_registers for pymodbus 1.x."""
        return Mock(isError=lambda: False, registers=[100])

    def _write_register_none(self, address, value):
        """Mock write_register for pymodbus 1.x."""
        return Mock(isError=lambda: False)

    def _write_registers_none(self, address, values):
        """Mock write_registers for pymodbus 1.x."""
        return Mock(isError=lambda: False)

    def _read_input_registers_none(self, address, count):
        """Mock read_input_registers for pymodbus 1.x."""
        return Mock(isError=lambda: False, registers=[100])


class MockAsyncModbusClient:
    """Mock Async Modbus client for testing different API versions."""

    def __init__(self, api_version: str):
        """Initialize with specific API version."""
        self.api_version = api_version
        self._setup_methods()

    def _setup_methods(self):
        """Setup methods with correct signatures based on API version."""
        if self.api_version == "slave":
            # pymodbus 3.x: count=count, slave=slave_id
            self.read_holding_registers = Mock(side_effect=self._read_holding_registers_slave)
            self.write_register = Mock(side_effect=self._write_register_slave)
            self.write_registers = Mock(side_effect=self._write_registers_slave)
            self.read_input_registers = Mock(side_effect=self._read_input_registers_slave)
        elif self.api_version == "unit":
            # pymodbus 2.x: count, unit=slave_id
            self.read_holding_registers = Mock(side_effect=self._read_holding_registers_unit)
            self.write_register = Mock(side_effect=self._write_register_unit)
            self.write_registers = Mock(side_effect=self._write_registers_unit)
            self.read_input_registers = Mock(side_effect=self._read_input_registers_unit)
        else:
            # pymodbus 1.x: address, count (no slave/unit)
            self.read_holding_registers = Mock(side_effect=self._read_holding_registers_none)
            self.write_register = Mock(side_effect=self._write_register_none)
            self.write_registers = Mock(side_effect=self._write_registers_none)
            self.read_input_registers = Mock(side_effect=self._read_input_registers_none)

    async def _read_holding_registers_slave(self, address, count=1, slave=1):
        """Mock async read_holding_registers for pymodbus 3.x."""
        return Mock(isError=lambda: False, registers=[100])

    async def _write_register_slave(self, address, value, slave=1):
        """Mock async write_register for pymodbus 3.x."""
        return Mock(isError=lambda: False)

    async def _write_registers_slave(self, address, values, slave=1):
        """Mock async write_registers for pymodbus 3.x."""
        return Mock(isError=lambda: False)

    async def _read_input_registers_slave(self, address, count=1, slave=1):
        """Mock async read_input_registers for pymodbus 3.x."""
        return Mock(isError=lambda: False, registers=[100])

    async def _read_holding_registers_unit(self, address, count, unit=1):
        """Mock async read_holding_registers for pymodbus 2.x."""
        return Mock(isError=lambda: False, registers=[100])

    async def _write_register_unit(self, address, value, unit=1):
        """Mock async write_register for pymodbus 2.x."""
        return Mock(isError=lambda: False)

    async def _write_registers_unit(self, address, values, unit=1):
        """Mock async write_registers for pymodbus 2.x."""
        return Mock(isError=lambda: False)

    async def _read_input_registers_unit(self, address, count, unit=1):
        """Mock async read_input_registers for pymodbus 2.x."""
        return Mock(isError=lambda: False, registers=[100])

    async def _read_holding_registers_none(self, address, count):
        """Mock async read_holding_registers for pymodbus 1.x."""
        return Mock(isError=lambda: False, registers=[100])

    async def _write_register_none(self, address, value):
        """Mock async write_register for pymodbus 1.x."""
        return Mock(isError=lambda: False)

    async def _write_registers_none(self, address, values):
        """Mock async write_registers for pymodbus 1.x."""
        return Mock(isError=lambda: False)

    async def _read_input_registers_none(self, address, count):
        """Mock async read_input_registers for pymodbus 1.x."""
        return Mock(isError=lambda: False, registers=[100])


class TestModbusAPICompatibility:
    """Test Modbus API compatibility detection and function calls."""

    @pytest.mark.parametrize("api_version", ["slave", "unit", "none"])
    def test_api_compatibility_detection_sync(self, api_version):
        """Test API compatibility detection for synchronous clients."""
        client = MockModbusClient(api_version)
        
        # Test detection
        detected = _test_api_compatibility(client, 'read_holding_registers')
        assert detected == api_version

    @pytest.mark.parametrize("api_version", ["slave", "unit", "none"])
    def test_api_compatibility_detection_async(self, api_version):
        """Test API compatibility detection for asynchronous clients."""
        client = MockAsyncModbusClient(api_version)
        
        # Test detection
        detected = _test_async_api_compatibility(client, 'read_holding_registers')
        assert detected == api_version

    @pytest.mark.parametrize("api_version", ["slave", "unit", "none"])
    def test_read_holding_registers_sync(self, api_version):
        """Test read_holding_registers with different API versions."""
        client = MockModbusClient(api_version)
        
        # Test function call
        result = read_holding_registers(client, 1000, 10, 1)
        assert result is not None
        assert not result.isError()

    @pytest.mark.parametrize("api_version", ["slave", "unit", "none"])
    def test_write_register_sync(self, api_version):
        """Test write_register with different API versions."""
        client = MockModbusClient(api_version)
        
        # Test function call
        result = write_register(client, 1000, 500, 1)
        assert result is not None
        assert not result.isError()

    @pytest.mark.parametrize("api_version", ["slave", "unit", "none"])
    def test_write_registers_sync(self, api_version):
        """Test write_registers with different API versions."""
        client = MockModbusClient(api_version)
        
        # Test function call
        result = write_registers(client, 1000, [500, 600], 1)
        assert result is not None
        assert not result.isError()

    @pytest.mark.parametrize("api_version", ["slave", "unit", "none"])
    def test_read_input_registers_sync(self, api_version):
        """Test read_input_registers with different API versions."""
        client = MockModbusClient(api_version)
        
        # Test function call
        result = read_input_registers(client, 1000, 10, 1)
        assert result is not None
        assert not result.isError()

    @pytest.mark.parametrize("api_version", ["slave", "unit", "none"])
    async def test_read_holding_registers_async(self, api_version):
        """Test async_read_holding_registers with different API versions."""
        client = MockAsyncModbusClient(api_version)
        
        # Test function call
        result = await async_read_holding_registers(client, 1000, 10, 1)
        assert result is not None
        assert not result.isError()

    @pytest.mark.parametrize("api_version", ["slave", "unit", "none"])
    async def test_write_register_async(self, api_version):
        """Test async_write_register with different API versions."""
        client = MockAsyncModbusClient(api_version)
        
        # Test function call
        result = await async_write_register(client, 1000, 500, 1)
        assert result is not None
        assert not result.isError()

    @pytest.mark.parametrize("api_version", ["slave", "unit", "none"])
    async def test_write_registers_async(self, api_version):
        """Test async_write_registers with different API versions."""
        client = MockAsyncModbusClient(api_version)
        
        # Test function call
        result = await async_write_registers(client, 1000, [500, 600], 1)
        assert result is not None
        assert not result.isError()

    @pytest.mark.parametrize("api_version", ["slave", "unit", "none"])
    async def test_read_input_registers_async(self, api_version):
        """Test async_read_input_registers with different API versions."""
        client = MockAsyncModbusClient(api_version)
        
        # Test function call
        result = await async_read_input_registers(client, 1000, 10, 1)
        assert result is not None
        assert not result.isError()

    def test_api_compatibility_with_invalid_method(self):
        """Test API compatibility detection with invalid method."""
        client = MockModbusClient("slave")
        
        # Test with non-existent method
        result = _test_api_compatibility(client, 'non_existent_method')
        assert result is None

    def test_async_api_compatibility_with_invalid_method(self):
        """Test async API compatibility detection with invalid method."""
        client = MockAsyncModbusClient("slave")
        
        # Test with non-existent method
        result = _test_async_api_compatibility(client, 'non_existent_method')
        assert result is None

    @patch('inspect.signature')
    def test_api_compatibility_inspect_error(self, mock_signature):
        """Test API compatibility detection when inspect.signature fails."""
        mock_signature.side_effect = ValueError("Inspect error")
        
        client = MockModbusClient("slave")
        
        # Should fall back to version-based detection
        result = _test_api_compatibility(client, 'read_holding_registers')
        # Result depends on pymodbus version, but should not be None
        assert result in ["slave", "unit", "none"]

    @patch('inspect.signature')
    def test_async_api_compatibility_inspect_error(self, mock_signature):
        """Test async API compatibility detection when inspect.signature fails."""
        mock_signature.side_effect = ValueError("Inspect error")
        
        client = MockAsyncModbusClient("slave")
        
        # Should fall back to version-based detection
        result = _test_async_api_compatibility(client, 'read_holding_registers')
        # Result depends on pymodbus version, but should not be None
        assert result in ["slave", "unit", "none"]

    @patch('inspect.signature')
    @patch('pymodbus.__version__', '3.0.0')
    def test_api_compatibility_pymodbus_3_fallback(self, mock_signature):
        """Test API compatibility detection with pymodbus 3.x fallback."""
        mock_signature.side_effect = ValueError("Inspect error")
        
        client = MockModbusClient("slave")
        
        result = _test_api_compatibility(client, 'read_holding_registers')
        assert result == "slave"

    @patch('inspect.signature')
    @patch('pymodbus.__version__', '2.5.0')
    def test_api_compatibility_pymodbus_2_fallback(self, mock_signature):
        """Test API compatibility detection with pymodbus 2.x fallback."""
        mock_signature.side_effect = ValueError("Inspect error")
        
        client = MockModbusClient("unit")
        
        result = _test_api_compatibility(client, 'read_holding_registers')
        assert result == "unit"

    @patch('inspect.signature')
    @patch('pymodbus.__version__', '1.5.0')
    def test_api_compatibility_pymodbus_1_fallback(self, mock_signature):
        """Test API compatibility detection with pymodbus 1.x fallback."""
        mock_signature.side_effect = ValueError("Inspect error")
        
        client = MockModbusClient("none")
        
        result = _test_api_compatibility(client, 'read_holding_registers')
        assert result == "none"

    def test_error_handling_in_sync_functions(self):
        """Test error handling in synchronous functions."""
        client = MockModbusClient("slave")
        
        # Mock client to raise an exception
        client.read_holding_registers = Mock(side_effect=Exception("Test error"))
        
        # Should raise the exception
        with pytest.raises(Exception, match="Test error"):
            read_holding_registers(client, 1000, 10, 1)

    async def test_error_handling_in_async_functions(self):
        """Test error handling in asynchronous functions."""
        client = MockAsyncModbusClient("slave")
        
        # Mock client to raise an exception
        client.read_holding_registers = Mock(side_effect=Exception("Test error"))
        
        # Should raise the exception
        with pytest.raises(Exception, match="Test error"):
            await async_read_holding_registers(client, 1000, 10, 1)

    def test_default_slave_id_parameter(self):
        """Test that default slave_id parameter works correctly."""
        client = MockModbusClient("slave")
        
        # Test without explicit slave_id (should use default 1)
        result = read_holding_registers(client, 1000, 10)
        assert result is not None
        assert not result.isError()

    async def test_default_slave_id_parameter_async(self):
        """Test that default slave_id parameter works correctly in async functions."""
        client = MockAsyncModbusClient("slave")
        
        # Test without explicit slave_id (should use default 1)
        result = await async_read_holding_registers(client, 1000, 10)
        assert result is not None
        assert not result.isError()


class TestModbusIntegrationCompatibility:
    """Test integration compatibility with real-world scenarios."""

    def test_multiple_api_versions_same_session(self):
        """Test handling multiple API versions in the same session."""
        # Test that we can handle different client types
        clients = [
            MockModbusClient("slave"),
            MockModbusClient("unit"),
            MockModbusClient("none"),
        ]
        
        for client in clients:
            result = read_holding_registers(client, 1000, 10, 1)
            assert result is not None
            assert not result.isError()

    async def test_multiple_api_versions_same_session_async(self):
        """Test handling multiple API versions in the same async session."""
        # Test that we can handle different client types
        clients = [
            MockAsyncModbusClient("slave"),
            MockAsyncModbusClient("unit"),
            MockAsyncModbusClient("none"),
        ]
        
        for client in clients:
            result = await async_read_holding_registers(client, 1000, 10, 1)
            assert result is not None
            assert not result.isError()

    def test_edge_case_parameters(self):
        """Test edge cases with different parameter combinations."""
        client = MockModbusClient("slave")
        
        # Test with zero count
        result = read_holding_registers(client, 1000, 0, 1)
        assert result is not None
        
        # Test with large address
        result = read_holding_registers(client, 65535, 1, 1)
        assert result is not None
        
        # Test with large slave_id
        result = read_holding_registers(client, 1000, 1, 255)
        assert result is not None

    async def test_edge_case_parameters_async(self):
        """Test edge cases with different parameter combinations in async."""
        client = MockAsyncModbusClient("slave")
        
        # Test with zero count
        result = await async_read_holding_registers(client, 1000, 0, 1)
        assert result is not None
        
        # Test with large address
        result = await async_read_holding_registers(client, 65535, 1, 1)
        assert result is not None
        
        # Test with large slave_id
        result = await async_read_holding_registers(client, 1000, 1, 255)
        assert result is not None 