"""Test the __init__ module."""
import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, Mock, mock_open, patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from custom_components.lambda_heat_pumps import (DOMAIN, PLATFORMS,
                                                 TRANSLATION_SOURCES, VERSION,
                                                 async_reload_entry,
                                                 async_setup,
                                                 async_setup_entry,
                                                 async_unload_entry,
                                                 setup_debug_logging)
from custom_components.lambda_heat_pumps.const import DEBUG_PREFIX
from custom_components.lambda_heat_pumps.coordinator import \
    LambdaDataUpdateCoordinator


@pytest.fixture
def mock_hass():
    """Create a mock hass object."""
    hass = Mock()
    hass.config = Mock()
    hass.config.config_dir = "/tmp/test_config"
    hass.config_entries = Mock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    hass.config_entries.async_forward_entry_setups = AsyncMock()
    hass.config_entries.async_get_entry = Mock()
    hass.data = {}
    hass.data[DOMAIN] = {}
    hass.services = Mock()
    hass.services.async_register = Mock()
    hass.bus = Mock()
    hass.bus.async_listen = Mock()
    hass.states = Mock()
    hass.states.get = Mock(return_value=Mock(state="20.0"))
    return hass


@pytest.fixture
def mock_entry():
    """Create a mock config entry."""
    entry = Mock()
    entry.entry_id = "test_entry"
    entry.data = {
        "host": "192.168.1.100",
        "port": 502,
        "slave_id": 1,
        "firmware_version": "V0.0.3-3K",
        "num_hps": 1,
        "num_boil": 1,
        "num_hc": 1,
        "num_buffer": 0,
        "num_solar": 0,
        "update_interval": 30,
        "write_interval": 30,
        "heating_circuit_min_temp": 15,
        "heating_circuit_max_temp": 35,
        "heating_circuit_temp_step": 0.5,
        "room_thermostat_control": False,
        "pv_surplus": False,
        "room_temperature_entity_1": "sensor.room_temp",
        "pv_power_sensor_entity": "sensor.pv_power"
    }
    entry.options = {
        "update_interval": 30,
        "write_interval": 30
    }
    entry.async_on_unload = Mock()
    entry.add_update_listener = Mock()
    return entry


def test_setup_debug_logging_enabled():
    """Test setup_debug_logging with debug enabled."""
    mock_hass = MagicMock()
    config = {"debug": True}
    
    with patch("logging.getLogger") as mock_get_logger:
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        setup_debug_logging(mock_hass, config)
        
        mock_get_logger.assert_called_with(DEBUG_PREFIX)
        mock_logger.setLevel.assert_called_once()


def test_setup_debug_logging_disabled():
    """Test setup_debug_logging with debug disabled."""
    mock_hass = MagicMock()
    config = {"debug": False}
    
    with patch("logging.getLogger") as mock_get_logger:
        setup_debug_logging(mock_hass, config)
        
        # Should not call setLevel when debug is False
        mock_get_logger.assert_not_called()


def test_setup_debug_logging_no_debug_key():
    """Test setup_debug_logging without debug key."""
    mock_hass = MagicMock()
    config = {}
    
    with patch("logging.getLogger") as mock_get_logger:
        setup_debug_logging(mock_hass, config)
        
        # Should not call setLevel when no debug key
        mock_get_logger.assert_not_called()


@pytest.mark.asyncio
async def test_async_setup_success(mock_hass):
    """Test successful async_setup."""
    mock_hass = MagicMock()
    config = {"debug": False}
    
    with patch("custom_components.lambda_heat_pumps.setup_debug_logging") as mock_setup_debug:
        result = await async_setup(mock_hass, config)
        
        assert result is True
        mock_setup_debug.assert_called_once_with(mock_hass, config)


@pytest.mark.asyncio
async def test_async_setup_entry_success(mock_hass, mock_entry):
    """Test successful async_setup_entry."""
    mock_coordinator = Mock()
    mock_coordinator.async_init = AsyncMock()
    mock_coordinator.async_refresh = AsyncMock()
    mock_coordinator.data = {"test": "data"}
    
    with patch("custom_components.lambda_heat_pumps.LambdaDataUpdateCoordinator", return_value=mock_coordinator):
        with patch("custom_components.lambda_heat_pumps.async_setup_services") as mock_setup_services:
            with patch("custom_components.lambda_heat_pumps.os.path.exists", return_value=True):
                result = await async_setup_entry(mock_hass, mock_entry)
                
                assert result is True
                mock_coordinator.async_init.assert_called_once()
                mock_coordinator.async_refresh.assert_called_once()
                mock_setup_services.assert_called_once_with(mock_hass)
                assert mock_hass.data[DOMAIN][mock_entry.entry_id]["coordinator"] == mock_coordinator


@pytest.mark.asyncio
async def test_async_setup_entry_coordinator_init_failure(mock_hass, mock_entry):
    """Test async_setup_entry with coordinator init failure."""
    mock_coordinator = Mock()
    mock_coordinator.async_init = AsyncMock(side_effect=Exception("Init failed"))
    
    with patch("custom_components.lambda_heat_pumps.LambdaDataUpdateCoordinator", return_value=mock_coordinator):
        with patch("custom_components.lambda_heat_pumps.os.path.exists", return_value=True):
            result = await async_setup_entry(mock_hass, mock_entry)
            
            assert result is False


@pytest.mark.asyncio
async def test_async_setup_entry_services_setup_failure(mock_hass, mock_entry):
    """Test async_setup_entry with services setup failure."""
    mock_coordinator = Mock()
    mock_coordinator.async_init = AsyncMock()
    mock_coordinator.async_refresh = AsyncMock()
    mock_coordinator.data = {"test": "data"}
    
    with patch("custom_components.lambda_heat_pumps.LambdaDataUpdateCoordinator", return_value=mock_coordinator):
        with patch("custom_components.lambda_heat_pumps.async_setup_services", side_effect=Exception("Service setup failed")):
            with patch("custom_components.lambda_heat_pumps.os.path.exists", return_value=True):
                result = await async_setup_entry(mock_hass, mock_entry)
                
                assert result is False


@pytest.mark.asyncio
async def test_async_setup_entry_create_config_file(mock_hass, mock_entry):
    """Test async setup entry creates config file."""
    mock_coordinator = Mock()
    mock_coordinator.async_init = AsyncMock()
    mock_coordinator.async_refresh = AsyncMock()
    mock_coordinator.data = {"test": "data"}
    
    with patch("custom_components.lambda_heat_pumps.LambdaDataUpdateCoordinator", return_value=mock_coordinator):
        with patch("custom_components.lambda_heat_pumps.async_setup_services"):
            with patch("custom_components.lambda_heat_pumps.os.path.exists", return_value=False):
                with patch("custom_components.lambda_heat_pumps.aiofiles.open", mock_open()) as mock_file:
                    result = await async_setup_entry(mock_hass, mock_entry)
                    
                    assert result is True
                    mock_file.assert_called_once()


@pytest.mark.asyncio
async def test_async_setup_entry_coordinator_no_data(mock_hass, mock_entry):
    """Test async setup entry when coordinator has no data."""
    mock_coordinator = Mock()
    mock_coordinator.async_init = AsyncMock()
    mock_coordinator.async_refresh = AsyncMock()
    mock_coordinator.data = None
    
    with patch("custom_components.lambda_heat_pumps.LambdaDataUpdateCoordinator", return_value=mock_coordinator):
        with patch("custom_components.lambda_heat_pumps.os.path.exists", return_value=True):
            result = await async_setup_entry(mock_hass, mock_entry)
            
            assert result is False


@pytest.mark.asyncio
async def test_async_setup_entry_exception(mock_hass, mock_entry):
    """Test async setup entry with exception."""
    with patch("custom_components.lambda_heat_pumps.LambdaDataUpdateCoordinator", side_effect=Exception("Test error")):
        with patch("custom_components.lambda_heat_pumps.os.path.exists", return_value=True):
            result = await async_setup_entry(mock_hass, mock_entry)
            
            assert result is False


@pytest.mark.asyncio
async def test_async_setup_entry_not_first_entry(mock_hass, mock_entry):
    """Test async setup entry when not the first entry."""
    mock_hass.data[DOMAIN] = {"existing_entry": Mock()}
    
    mock_coordinator = Mock()
    mock_coordinator.async_init = AsyncMock()
    mock_coordinator.async_refresh = AsyncMock()
    mock_coordinator.data = {"test": "data"}
    
    with patch("custom_components.lambda_heat_pumps.LambdaDataUpdateCoordinator", return_value=mock_coordinator):
        with patch("custom_components.lambda_heat_pumps.async_setup_services") as mock_setup_services:
            with patch("custom_components.lambda_heat_pumps.os.path.exists", return_value=True):
                result = await async_setup_entry(mock_hass, mock_entry)
                
                assert result is True
                # Should not call setup_services when not first entry
                mock_setup_services.assert_not_called()


@pytest.mark.asyncio
async def test_async_unload_entry_success(mock_hass, mock_entry):
    """Test successful async_unload_entry."""
    mock_hass.data[DOMAIN][mock_entry.entry_id] = {"coordinator": Mock()}
    
    result = await async_unload_entry(mock_hass, mock_entry)
    
    assert result is True
    assert mock_entry.entry_id not in mock_hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_async_unload_entry_no_coordinator(mock_hass, mock_entry):
    """Test async_unload_entry with no coordinator."""
    # Ensure DOMAIN exists but entry_id doesn't
    mock_hass.data[DOMAIN] = {}
    
    result = await async_unload_entry(mock_hass, mock_entry)
    
    assert result is True


@pytest.mark.asyncio
async def test_async_unload_entry_services_unload_failure(mock_hass, mock_entry):
    """Test async_unload_entry with services unload failure."""
    mock_hass.data[DOMAIN][mock_entry.entry_id] = {"coordinator": Mock()}
    mock_hass.config_entries.async_unload_platforms.return_value = False
    
    result = await async_unload_entry(mock_hass, mock_entry)
    
    assert result is False
    assert mock_entry.entry_id in mock_hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_async_reload_entry_success(mock_hass, mock_entry):
    """Test successful async_reload_entry."""
    mock_coordinator = Mock()
    mock_coordinator.async_init = AsyncMock()
    mock_coordinator.async_refresh = AsyncMock()
    mock_coordinator.data = {"test": "data"}
    
    with patch("custom_components.lambda_heat_pumps.LambdaDataUpdateCoordinator", return_value=mock_coordinator):
        with patch("custom_components.lambda_heat_pumps.async_setup_services"):
            with patch("custom_components.lambda_heat_pumps.os.path.exists", return_value=True):
                await async_reload_entry(mock_hass, mock_entry)
                
                mock_coordinator.async_init.assert_called_once()
                mock_coordinator.async_refresh.assert_called_once()
                assert mock_hass.data[DOMAIN][mock_entry.entry_id]["coordinator"] == mock_coordinator


@pytest.mark.asyncio
async def test_async_reload_entry_unload_exception(mock_hass, mock_entry):
    """Test async_reload_entry with unload exception."""
    mock_coordinator = Mock()
    mock_coordinator.async_init = AsyncMock()
    mock_coordinator.async_refresh = AsyncMock()
    mock_coordinator.data = {"test": "data"}
    
    with patch("custom_components.lambda_heat_pumps.async_unload_entry", side_effect=Exception("Unload failed")):
        with patch("custom_components.lambda_heat_pumps.LambdaDataUpdateCoordinator", return_value=mock_coordinator):
            with patch("custom_components.lambda_heat_pumps.async_setup_services"):
                with patch("custom_components.lambda_heat_pumps.os.path.exists", return_value=True):
                    await async_reload_entry(mock_hass, mock_entry)
                    
                    # Should continue and setup new coordinator
                    mock_coordinator.async_init.assert_called_once()


@pytest.mark.asyncio
async def test_async_reload_entry_setup_exception(mock_hass, mock_entry):
    """Test async_reload_entry with setup exception."""
    with patch("custom_components.lambda_heat_pumps.async_unload_entry"):
        with patch("custom_components.lambda_heat_pumps.LambdaDataUpdateCoordinator", side_effect=Exception("Setup failed")):
            with patch("custom_components.lambda_heat_pumps.os.path.exists", return_value=True):
                await async_reload_entry(mock_hass, mock_entry)
                
                # Should clean up on failure
                if DOMAIN in mock_hass.data and mock_entry.entry_id in mock_hass.data[DOMAIN]:
                    assert False, "Should have cleaned up on failure"


@pytest.mark.asyncio
async def test_async_reload_entry_coordinator_no_data(mock_hass, mock_entry):
    """Test async_reload_entry when coordinator has no data."""
    mock_coordinator = Mock()
    mock_coordinator.async_init = AsyncMock()
    mock_coordinator.async_refresh = AsyncMock()
    mock_coordinator.data = None
    
    with patch("custom_components.lambda_heat_pumps.async_unload_entry"):
        with patch("custom_components.lambda_heat_pumps.LambdaDataUpdateCoordinator", return_value=mock_coordinator):
            with patch("custom_components.lambda_heat_pumps.os.path.exists", return_value=True):
                await async_reload_entry(mock_hass, mock_entry)
                
                # Should not store coordinator if no data
                if DOMAIN in mock_hass.data and mock_entry.entry_id in mock_hass.data[DOMAIN]:
                    assert False, "Should not store coordinator with no data"


@pytest.mark.asyncio
async def test_async_reload_entry_cleanup_on_failure(mock_hass, mock_entry):
    """Test async_reload_entry cleanup on failure."""
    mock_hass.data[DOMAIN][mock_entry.entry_id] = {"old_coordinator": Mock()}
    
    with patch("custom_components.lambda_heat_pumps.async_unload_entry"):
        with patch("custom_components.lambda_heat_pumps.LambdaDataUpdateCoordinator", side_effect=Exception("Setup failed")):
            with patch("custom_components.lambda_heat_pumps.os.path.exists", return_value=True):
                await async_reload_entry(mock_hass, mock_entry)
                
                # Should clean up old coordinator
                assert mock_entry.entry_id not in mock_hass.data[DOMAIN]


def test_constants():
    """Test that constants are properly defined."""
    assert PLATFORMS == [Platform.SENSOR, Platform.CLIMATE]
    assert VERSION == "1.0.0"
    assert TRANSLATION_SOURCES == {DOMAIN: "translations"}


@pytest.mark.asyncio
async def test_async_reload_entry_lock_prevents_multiple_reloads(mock_hass, mock_entry):
    """Test that reload lock prevents multiple simultaneous reloads."""
    mock_coordinator = Mock()
    mock_coordinator.async_init = AsyncMock()
    mock_coordinator.async_refresh = AsyncMock()
    mock_coordinator.data = {"test": "data"}
    
    with patch("custom_components.lambda_heat_pumps.async_unload_entry"):
        with patch("custom_components.lambda_heat_pumps.LambdaDataUpdateCoordinator", return_value=mock_coordinator):
            with patch("custom_components.lambda_heat_pumps.async_setup_services"):
                with patch("custom_components.lambda_heat_pumps.os.path.exists", return_value=True):
                    # Start two reloads simultaneously
                    task1 = asyncio.create_task(async_reload_entry(mock_hass, mock_entry))
                    task2 = asyncio.create_task(async_reload_entry(mock_hass, mock_entry))
                    
                    await asyncio.gather(task1, task2)
                    
                    # Both should complete successfully
                    mock_coordinator.async_init.assert_called()


@pytest.mark.asyncio
async def test_async_setup_with_config(mock_hass):
    """Test async_setup with config."""
    config = {"lambda_heat_pumps": {"debug": True}}
    
    with patch("custom_components.lambda_heat_pumps.setup_debug_logging") as mock_setup_debug:
        result = await async_setup(mock_hass, config)
        
        assert result is True
        mock_setup_debug.assert_called_once_with(mock_hass, config)


@pytest.mark.asyncio
async def test_async_setup_entry_with_platforms(mock_hass, mock_entry):
    """Test async_setup_entry sets up platforms correctly."""
    mock_coordinator = Mock()
    mock_coordinator.async_init = AsyncMock()
    mock_coordinator.async_refresh = AsyncMock()
    mock_coordinator.data = {"test": "data"}
    
    with patch("custom_components.lambda_heat_pumps.LambdaDataUpdateCoordinator", return_value=mock_coordinator):
        with patch("custom_components.lambda_heat_pumps.async_setup_services"):
            with patch("custom_components.lambda_heat_pumps.os.path.exists", return_value=True):
                result = await async_setup_entry(mock_hass, mock_entry)
                
                assert result is True
                mock_hass.config_entries.async_forward_entry_setups.assert_called_once_with(mock_entry, PLATFORMS)


@pytest.mark.asyncio
async def test_async_setup_entry_coordinator_cleanup(mock_hass, mock_entry):
    """Test async_setup_entry cleans up coordinator on failure."""
    mock_coordinator = Mock()
    mock_coordinator.async_init = AsyncMock(side_effect=Exception("Init failed"))
    
    with patch("custom_components.lambda_heat_pumps.LambdaDataUpdateCoordinator", return_value=mock_coordinator):
        with patch("custom_components.lambda_heat_pumps.os.path.exists", return_value=True):
            result = await async_setup_entry(mock_hass, mock_entry)
            
            assert result is False
            # Should not store coordinator on failure
            assert mock_entry.entry_id not in mock_hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_async_unload_entry_coordinator_cleanup(mock_hass, mock_entry):
    """Test async_unload_entry cleans up coordinator."""
    mock_coordinator = Mock()
    mock_hass.data[DOMAIN][mock_entry.entry_id] = {"coordinator": mock_coordinator}
    
    result = await async_unload_entry(mock_hass, mock_entry)
    
    assert result is True
    assert mock_entry.entry_id not in mock_hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_async_setup_entry_multiple_entries(mock_hass):
    """Test async_setup_entry with multiple entries."""
    entry1 = Mock()
    entry1.entry_id = "entry1"
    entry1.data = {"host": "192.168.1.100", "port": 502, "slave_id": 1, "num_hps": 1, "num_boil": 1, "num_hc": 1, "num_buffer": 0, "num_solar": 0}
    entry1.options = {}
    entry1.async_on_unload = Mock()
    entry1.add_update_listener = Mock()
    
    entry2 = Mock()
    entry2.entry_id = "entry2"
    entry2.data = {"host": "192.168.1.101", "port": 502, "slave_id": 1, "num_hps": 1, "num_boil": 1, "num_hc": 1, "num_buffer": 0, "num_solar": 0}
    entry2.options = {}
    entry2.async_on_unload = Mock()
    entry2.add_update_listener = Mock()
    
    mock_coordinator1 = Mock()
    mock_coordinator1.async_init = AsyncMock()
    mock_coordinator1.async_refresh = AsyncMock()
    mock_coordinator1.data = {"test": "data"}
    
    mock_coordinator2 = Mock()
    mock_coordinator2.async_init = AsyncMock()
    mock_coordinator2.async_refresh = AsyncMock()
    mock_coordinator2.data = {"test": "data"}
    
    with patch("custom_components.lambda_heat_pumps.LambdaDataUpdateCoordinator", side_effect=[mock_coordinator1, mock_coordinator2]):
        with patch("custom_components.lambda_heat_pumps.async_setup_services") as mock_setup_services:
            with patch("custom_components.lambda_heat_pumps.os.path.exists", return_value=True):
                result1 = await async_setup_entry(mock_hass, entry1)
                result2 = await async_setup_entry(mock_hass, entry2)
                
                assert result1 is True
                assert result2 is True
                # Should call setup_services only once (for first entry)
                assert mock_setup_services.call_count == 1
