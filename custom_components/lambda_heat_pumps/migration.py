"""Migration logic for Lambda Heat Pumps integration."""

import logging
import asyncio
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


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
        
        # Aktualisiere unique_id für alle verbleibenden Entities
        for registry_entry in registry_entries:
            entity_id = registry_entry.entity_id
            
            # Überspringe bereits entfernte Entities
            if not entity_registry.async_get(entity_id):
                continue
            
            # Aktualisiere unique_id für Sensor-Entities
            if entity_id.startswith("sensor."):
                base_name = entity_id.replace("sensor.", "")
                new_unique_id = f"{name_prefix}_{base_name}"
                
                if registry_entry.unique_id != new_unique_id:
                    _LOGGER.info(
                        "Updating unique_id for %s: %s -> %s",
                        entity_id,
                        registry_entry.unique_id,
                        new_unique_id
                    )
                    entity_registry.async_update_entity(
                        entity_id,
                        new_unique_id=new_unique_id
                    )
                    migration_count += 1
            
            # Aktualisiere unique_id für Climate-Entities
            elif entity_id.startswith("climate."):
                base_name = entity_id.replace("climate.", "")
                new_unique_id = f"{name_prefix}_{base_name}"
                
                if registry_entry.unique_id != new_unique_id:
                    _LOGGER.info(
                        "Updating unique_id for %s: %s -> %s",
                        entity_id,
                        registry_entry.unique_id,
                        new_unique_id
                    )
                    entity_registry.async_update_entity(
                        entity_id,
                        new_unique_id=new_unique_id
                    )
                    migration_count += 1
        
        _LOGGER.info(
            "Entity Registry migration completed: %d entities updated, %d duplicates removed",
            migration_count,
            removed_count
        )
        return True
        
    except Exception as e:
        _LOGGER.error("Error during Entity Registry migration: %s", e)
        return False 