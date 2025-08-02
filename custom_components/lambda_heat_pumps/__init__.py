"""The Lambda Heat Pumps integration."""
from __future__ import annotations
from datetime import timedelta

import logging
import asyncio
import os
import aiofiles

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_registry import (
    async_get as async_get_entity_registry
)

from .const import (
    DOMAIN,
    DEBUG_PREFIX,
    LAMBDA_WP_CONFIG_TEMPLATE  # Import template from const
)
from .coordinator import LambdaDataUpdateCoordinator
from .services import async_setup_services, async_unload_services
from .utils import generate_base_addresses
from .automations import setup_cycling_automations, cleanup_cycling_automations

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=30)
VERSION = "1.1.0"  # Updated version for cycling sensors feature

# Diese Konstante teilt Home Assistant mit, dass die Integration
# Übersetzungen hat
TRANSLATION_SOURCES = {DOMAIN: "translations"}

# Lock für das Reloading
_reload_lock = asyncio.Lock()

PLATFORMS = [
    Platform.SENSOR,
    Platform.CLIMATE,
]

# Config schema - only config entries are supported
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


def setup_debug_logging(hass: HomeAssistant, config: ConfigType) -> None:
    """Set up debug logging for the integration."""
    if config.get("debug", False):
        logging.getLogger(DEBUG_PREFIX).setLevel(logging.DEBUG)
        _LOGGER.info("Debug logging enabled for %s", DEBUG_PREFIX)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Lambda integration."""
    setup_debug_logging(hass, config)
    return True


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate config entry to new version."""
    _LOGGER.debug("Migrating config entry from version %s", config_entry.version)
    
    # Prüfe, ob Migration bereits läuft
    migration_key = f"{DOMAIN}_migration_{config_entry.entry_id}"
    if migration_key in hass.data:
        _LOGGER.warning("Migration already in progress for entry %s", config_entry.entry_id)
        return True
    
    if config_entry.version < 2:
        # Migration von Version 1 auf 2: Entity Registry Migration
        _LOGGER.info(
            "Starting Entity Registry migration from version %s to 2",
            config_entry.version
        )
        
        # Setze Migration-Flag
        hass.data[migration_key] = True
        
        # Führe Entity Registry Migration durch
        migration_success = await migrate_entity_registry(hass, config_entry)
        
        if migration_success:
            # Aktualisiere Config Entry Version
            new_data = {**config_entry.data}
            hass.config_entries.async_update_entry(
                config_entry,
                data=new_data,
                version=2
            )
            _LOGGER.info("Successfully migrated config entry to version 2")
            # Entferne Migration-Flag
            if migration_key in hass.data:
                del hass.data[migration_key]
            return True
        else:
            _LOGGER.error("Entity Registry migration failed")
            # Entferne Migration-Flag auch bei Fehler
            if migration_key in hass.data:
                del hass.data[migration_key]
            return False
    
    return True


async def migrate_entity_registry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate Entity Registry entries for unique_id consistency."""
    try:
        # Timeout-Schutz für Migration
        import asyncio
        migration_task = asyncio.create_task(_perform_migration(hass, entry))
        
        # Timeout nach 30 Sekunden
        try:
            await asyncio.wait_for(migration_task, timeout=30.0)
            return True
        except asyncio.TimeoutError:
            _LOGGER.error("Entity Registry migration timed out after 30 seconds")
            return False
            
    except Exception as e:
        _LOGGER.error("Error during Entity Registry migration: %s", e)
        return False


async def _perform_migration(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Perform the actual migration with timeout protection."""
    entity_registry = async_get_entity_registry(hass)
    registry_entries = entity_registry.entities.get_entries_for_config_entry_id(entry.entry_id)
    
    # Hole Config-Informationen für Migration
    name_prefix = entry.data.get("name", "").lower().replace(" ", "")
    
    migration_count = 0
    removed_count = 0

    try:
        # Sammle alle Entity-IDs für Duplikat-Erkennung
        existing_entities = {}
        for registry_entry in registry_entries:
            entity_id = registry_entry.entity_id
            if entity_id.startswith("sensor.") or entity_id.startswith("climate."):
                base_name = entity_id.replace("sensor.", "").replace("climate.", "")
                
                if base_name not in existing_entities:
                    existing_entities[base_name] = []
                existing_entities[base_name].append(registry_entry)
        
        # Entferne Duplikate
        for base_name, entries in existing_entities.items():
            if len(entries) > 1:
                for registry_entry in entries:
                    entity_id = registry_entry.entity_id
                    if any(suffix in entity_id for suffix in ["_2", "_3", "_4", "_5"]):
                        _LOGGER.info(
                            "Removing duplicate entity with numeric suffix: %s",
                            entity_id
                        )
                        entity_registry.async_remove(entity_id)
                        removed_count += 1

        # Migration für General-Sensoren
        for registry_entry in registry_entries:
            entity_id = registry_entry.entity_id
            if (entity_id.startswith("sensor.") and 
                not any(suffix in entity_id for suffix in ["_2", "_3", "_4", "_5"])):
                
                entity_parts = entity_id.replace("sensor.", "").split("_")
                
                # General-Sensor Migration
                if (len(entity_parts) >= 2 and 
                    entity_parts[0] == name_prefix and 
                    registry_entry.unique_id and 
                    not registry_entry.unique_id.startswith(name_prefix)):
                    
                    new_unique_id = f"{name_prefix}_{registry_entry.unique_id}"
                    _LOGGER.info(
                        "Migrating general sensor unique_id from '%s' to '%s' for entity: %s",
                        registry_entry.unique_id,
                        new_unique_id,
                        entity_id
                    )
                    
                    entity_registry.async_update_entity(
                        entity_id,
                        new_unique_id=new_unique_id
                    )
                    migration_count += 1

        # Migration für Climate-Entities
        for registry_entry in registry_entries:
            entity_id = registry_entry.entity_id
            if (entity_id.startswith("climate.") and 
                not any(suffix in entity_id 
                       for suffix in ["_2", "_3", "_4", "_5"])):
                
                entity_parts = entity_id.replace("climate.", "").split("_")

                # Prüfe, ob es ein neues Format ist
                # (name_prefix_device_type_idx_climate_type)
                if (len(entity_parts) >= 4 and 
                    entity_parts[0] == name_prefix and
                    entity_parts[1] in ["boil", "hc"] and
                    entity_parts[3] in ["hot_water", "heating_circuit"]):
                    
                    # Neues Format - unique_id aktualisieren falls nötig
                    if (registry_entry.unique_id and 
                        registry_entry.unique_id.startswith(
                            "lambda_heat_pumps_")):
                        
                        new_unique_id = "_".join(entity_parts)
                        _LOGGER.info(
                            "Migrating climate entity unique_id from '%s' to '%s' for entity: %s",
                            registry_entry.unique_id,
                            new_unique_id,
                            entity_id
                        )
                        
                        entity_registry.async_update_entity(
                            entity_id,
                            new_unique_id=new_unique_id
                        )
                        migration_count += 1

                else:
                    # Altes Format - Entity entfernen
                    _LOGGER.info(
                        "Removing old climate entity with incompatible format: %s (unique_id: %s)",
                        entity_id,
                        registry_entry.unique_id
                    )
                    entity_registry.async_remove(entity_id)
                    removed_count += 1

        # Migration für Cycling-Sensoren
        for registry_entry in registry_entries:
            entity_id = registry_entry.entity_id
            if (entity_id.startswith("sensor.") and 
                "cycling" in entity_id and 
                not any(suffix in entity_id for suffix in ["_2", "_3", "_4", "_5"])):
                
                entity_parts = entity_id.replace("sensor.", "").split("_")
                if (len(entity_parts) >= 4 and 
                    entity_parts[0] == name_prefix and
                    registry_entry.unique_id and
                    registry_entry.unique_id != "_".join(entity_parts)):
                    
                    new_unique_id = "_".join(entity_parts)
                    _LOGGER.info(
                        "Migrating cycling sensor unique_id from '%s' to '%s' for entity: %s",
                        registry_entry.unique_id,
                        new_unique_id,
                        entity_id
                    )
                    
                    entity_registry.async_update_entity(
                        entity_id,
                        new_unique_id=new_unique_id
                    )
                    migration_count += 1

        if removed_count > 0:
            _LOGGER.info("Entity Registry migration completed: removed %d duplicate entities", removed_count)
        
        if migration_count > 0:
            _LOGGER.info("Entity Registry migration completed: updated %d unique_ids", migration_count)
        
        return True

    except Exception as e:
        _LOGGER.error("Error during Entity Registry migration: %s", e)
        return False


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Lambda Heat Pumps from a config entry."""
    # Check if already set up
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        _LOGGER.debug("Entry %s already loaded, skipping setup", entry.entry_id)
        return True

    _LOGGER.debug("Setting up Lambda integration with config: %s", entry.data)

    # Prüfe, ob lambda_wp_config.yaml existiert, sonst anlegen
    config_dir = hass.config.config_dir
    lambda_config_path = os.path.join(config_dir, "lambda_wp_config.yaml")
    if not os.path.exists(lambda_config_path):
        async with aiofiles.open(lambda_config_path, "w") as f:
            await f.write(LAMBDA_WP_CONFIG_TEMPLATE)  # Use template from const
        _LOGGER.info("Created lambda_wp_config.yaml with default template")

    # Generate base addresses based on configured device counts
    num_hps = entry.data.get("num_hps", 1)
    num_boil = entry.data.get("num_boil", 1)
    num_buff = entry.data.get("num_buff", 0)
    num_sol = entry.data.get("num_sol", 0)
    num_hc = entry.data.get("num_hc", 1)
    _LOGGER.debug(
        "Device counts - HPs: %d, Boilers: %d, Buffers: %d, Solar: %d, "
        "HCs: %d",
        num_hps, num_boil, num_buff, num_sol, num_hc
    )
    

    
    # Log generated base addresses direkt ohne Variablen
    _LOGGER.debug(
        "Generated base addresses - HP: %s, Boil: %s, Buff: %s, Sol: %s, "
        "HC: %s",
        generate_base_addresses('hp', num_hps),
        generate_base_addresses('boil', num_boil),
        generate_base_addresses('buff', num_buff),
        generate_base_addresses('sol', num_sol),
        generate_base_addresses('hc', num_hc)
    )
    # Create coordinator
    coordinator = LambdaDataUpdateCoordinator(hass, entry)
    try:
        await coordinator.async_init()
        # Warte auf die erste Datenabfrage mit Retry-Logik
        max_retries = 3
        for attempt in range(max_retries):
            try:
                await coordinator.async_refresh()
                if coordinator.data:
                    break
                else:
                    _LOGGER.warning(
                        "Attempt %d/%d: No data received from Lambda device",
                        attempt + 1, max_retries
                    )
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1)
            except Exception as ex:
                _LOGGER.warning(
                    "Attempt %d/%d: Error refreshing coordinator: %s",
                    attempt + 1, max_retries, ex
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
        
        if not coordinator.data:
            _LOGGER.error("Failed to fetch initial data from Lambda device after %d attempts", max_retries)
            return False

        # Store coordinator in hass.data (always overwrite to ensure fresh coordinator)
        if DOMAIN not in hass.data:
            hass.data[DOMAIN] = {}
        hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator}

        # Set up platforms with error handling
        try:
            await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        except Exception as platform_ex:
            _LOGGER.error("Error setting up platforms: %s", platform_ex, exc_info=True)
            # Clean up partially setup platforms
            try:
                await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
            except Exception as unload_ex:
                _LOGGER.error("Error cleaning up platforms: %s", unload_ex, exc_info=True)
            return False

        # Set up services only for the first entry
        if len(hass.data[DOMAIN]) == 1:
            await async_setup_services(hass)

        # Set up cycling automations
        setup_cycling_automations(hass, entry.entry_id)

        # Add update listener
        entry.async_on_unload(entry.add_update_listener(async_reload_entry))

        _LOGGER.info("Lambda Heat Pumps integration setup completed")
        return True

    except Exception as ex:
        _LOGGER.error("Failed to setup Lambda integration: %s", ex, exc_info=True)
        
        # Clean up any partial setup
        try:
            if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
                if "coordinator" in hass.data[DOMAIN][entry.entry_id]:
                    await hass.data[DOMAIN][entry.entry_id]["coordinator"].async_shutdown()
                hass.data[DOMAIN].pop(entry.entry_id, None)
        except Exception as cleanup_ex:
            _LOGGER.error("Error during cleanup after failed setup: %s", cleanup_ex, exc_info=True)
        
        return False


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading Lambda integration for entry: %s", entry.entry_id)
    
    unload_ok = True
    
    try:
        # Clean up cycling automations first
        cleanup_cycling_automations(hass, entry.entry_id)
        
        # Unload platforms - handle case where platforms might not be loaded
        platforms_unloaded = True
        try:
            # Check if platforms are actually loaded before trying to unload
            loaded_platforms = []
            for p in PLATFORMS:
                for e in hass.data.get("entity_registry", {}).entities.values():
                    if (e.config_entry_id == entry.entry_id and 
                        e.entity_id.startswith(f"{p}.")):
                        loaded_platforms.append(p)
                        break
            
            if loaded_platforms:
                platforms_unloaded = await hass.config_entries.async_unload_platforms(entry, loaded_platforms)
            else:
                _LOGGER.debug("No platforms found to unload for entry %s", entry.entry_id)
                platforms_unloaded = True
                
        except Exception as platform_ex:
            _LOGGER.error("Error unloading platforms: %s", platform_ex, exc_info=True)
            platforms_unloaded = False
        
        unload_ok = unload_ok and platforms_unloaded

        # Remove coordinator
        if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
            try:
                coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
                await coordinator.async_shutdown()
            except Exception as coord_ex:
                _LOGGER.error("Error during coordinator shutdown: %s", coord_ex, exc_info=True)
                unload_ok = False
            finally:
                hass.data[DOMAIN].pop(entry.entry_id, None)

        # If this was the last entry, unload services
        if DOMAIN in hass.data and not hass.data[DOMAIN]:
            try:
                await async_unload_services(hass)
            except Exception as service_ex:
                _LOGGER.error("Error unloading services: %s", service_ex, exc_info=True)
                unload_ok = False
            finally:
                hass.data.pop(DOMAIN, None)

        if not unload_ok:
            _LOGGER.error("Failed to fully unload Lambda Heat Pumps integration")
        else:
            _LOGGER.info("Lambda Heat Pumps integration unloaded successfully")
            
        return unload_ok
        
    except Exception as ex:
        _LOGGER.error("Unexpected error during unload: %s", ex, exc_info=True)
        return False


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    _LOGGER.debug("Reloading Lambda integration for entry: %s", entry.entry_id)

    async with _reload_lock:
        try:
            # First check if entry is still valid
            if entry.entry_id not in hass.config_entries.async_entry_ids():
                _LOGGER.error("Entry not found in config entries, cannot reload")
                return

            # Unload current entry
            if not await async_unload_entry(hass, entry):
                _LOGGER.error("Failed to unload entry during reload")
                # Try to continue anyway to avoid getting stuck

            # Ensure all platforms are properly unloaded
            await asyncio.sleep(1)

            # Double check entry still exists
            if entry.entry_id not in hass.config_entries.async_entry_ids():
                _LOGGER.error("Entry disappeared during reload")
                return

            # Reload entry using fresh setup
            try:
                await async_setup_entry(hass, entry)
                _LOGGER.info("Lambda Heat Pumps integration reloaded successfully")
            except Exception as setup_ex:
                _LOGGER.error("Failed to setup after reload: %s", setup_ex, exc_info=True)
                # Try standard reload as last resort
                try:
                    await hass.config_entries.async_reload(entry.entry_id)
                except Exception as std_reload_ex:
                    _LOGGER.error("Standard reload also failed: %s", std_reload_ex, exc_info=True)
                    raise
                
        except Exception as ex:
            _LOGGER.error("Critical error during reload: %s", ex, exc_info=True)
            raise
