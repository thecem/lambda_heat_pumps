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
    
    if config_entry.version < 3:
        # Migration von Version 1 auf 2: Entity Registry Migration
        _LOGGER.info(
            "Starting Entity Registry migration from version %s to 3",
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
                version=3
            )
            _LOGGER.info("Successfully migrated config entry to version 3")
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
        # Warte auf die erste Datenabfrage
        await coordinator.async_refresh()
        if not coordinator.data:
            _LOGGER.error("Failed to fetch initial data from Lambda device")
            return False

        # Store coordinator in hass.data
        if DOMAIN not in hass.data:
            hass.data[DOMAIN] = {}
        hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator}

        # Set up platforms
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

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
        _LOGGER.error("Failed to setup Lambda integration: %s", ex)
        return False


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading Lambda integration for entry: %s", entry.entry_id)

    # Clean up cycling automations
    cleanup_cycling_automations(hass, entry.entry_id)

    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Remove coordinator from hass.data
        if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
            coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
            await coordinator.async_shutdown()
            del hass.data[DOMAIN][entry.entry_id]

        # If this was the last entry, unload services
        if DOMAIN in hass.data and not hass.data[DOMAIN]:
            await async_unload_services(hass)
            del hass.data[DOMAIN]

        _LOGGER.info("Lambda Heat Pumps integration unloaded successfully")
    else:
        _LOGGER.error("Failed to unload Lambda Heat Pumps integration")

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    _LOGGER.debug("Reloading Lambda integration for entry: %s", entry.entry_id)

    async with _reload_lock:
        # Unload current entry
        await async_unload_entry(hass, entry)

        # Reload entry
        await hass.config_entries.async_reload(entry.entry_id)

        _LOGGER.info("Lambda Heat Pumps integration reloaded successfully")
