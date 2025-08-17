"""Migration for Lambda Heat Pumps integration."""

from __future__ import annotations
import logging
import os
import shutil
from datetime import datetime
from typing import Any, Dict, List

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.const import CONF_NAME

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Migration Version
MIGRATION_VERSION = 2


async def create_registry_file_backup(hass: HomeAssistant) -> bool:
    """Create backup of registry files in the lambda_heat_pumps directory."""
    try:
        # Get Home Assistant config directory
        config_dir = hass.config.config_dir
        _LOGGER.debug("Config directory: %s", config_dir)
        
        # Define source and destination paths
        registry_files = [
            "core.entity_registry",
            "core.device_registry", 
            "core.config_entries"
        ]
        
        # Create backup directory with proper path handling
        backup_dir = os.path.join(
            config_dir, 
            "lambda_heat_pumps", 
            "backup"
        )
        
        _LOGGER.debug("Backup directory: %s", backup_dir)
        
        # Ensure backup directory exists using async executor
        try:
            await hass.async_add_executor_job(
                lambda: os.makedirs(backup_dir, exist_ok=True)
            )
            _LOGGER.debug("Backup directory created/verified: %s", backup_dir)
        except OSError as e:
            _LOGGER.error("Failed to create backup directory %s: %s", backup_dir, e)
            return False
        
        # Create timestamp for backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        copied_files = []
        missing_files = []
        error_files = []
        
        for registry_file in registry_files:
            source_path = os.path.join(config_dir, ".storage", registry_file)
            dest_path = os.path.join(backup_dir, f"{registry_file}.{timestamp}")
            
            _LOGGER.debug("Processing registry file: %s", registry_file)
            
            # Check if source file exists and is readable using async executor
            try:
                exists = await hass.async_add_executor_job(
                    lambda: os.path.exists(source_path)
                )
                if not exists:
                    _LOGGER.warning(
                        "Registry file not found: %s",
                        source_path
                    )
                    missing_files.append(registry_file)
                    continue
                
                # Check if source file is readable
                readable = await hass.async_add_executor_job(
                    lambda: os.access(source_path, os.R_OK)
                )
                if not readable:
                    _LOGGER.error(
                        "Registry file not readable: %s",
                        source_path
                    )
                    error_files.append(registry_file)
                    continue
                
                # Create backup with proper error handling using async executor
                await hass.async_add_executor_job(
                    lambda: shutil.copy2(source_path, dest_path)
                )
                copied_files.append(registry_file)
                _LOGGER.info(
                    "Registry backup created: %s -> %s",
                    registry_file, dest_path
                )
            except (OSError, IOError) as e:
                _LOGGER.error(
                    "Failed to copy registry file %s: %s",
                    registry_file, e
                )
                error_files.append(registry_file)
                continue
        
        # Log summary
        _LOGGER.info(
            "Registry backup summary: %d copied, %d missing, %d errors",
            len(copied_files), len(missing_files), len(error_files)
        )
        
        # Return True if at least one file was copied successfully
        # or if all files were missing (which might be normal for new installations)
        if copied_files:
            _LOGGER.info(
                "Registry backup completed: %d files copied to %s",
                len(copied_files), backup_dir
            )
            return True
        elif missing_files and not error_files:
            # All files were missing but no errors occurred - this might be normal
            _LOGGER.info(
                "Registry backup completed: No files to backup (all files missing: %s)",
                missing_files
            )
            return True
        else:
            _LOGGER.warning(
                "Registry backup failed: %d errors, %d missing",
                len(error_files), len(missing_files)
            )
            return False
            
    except Exception as e:
        _LOGGER.error("Error creating registry backup: %s", e)
        return False


async def create_migration_backup(hass: HomeAssistant) -> Dict[str, Any]:
    """Erstelle vollständiges Backup vor Migration."""
    backup_data = {
        "timestamp": datetime.now().isoformat(),
        "version": MIGRATION_VERSION,
        "entity_registry": {},
        "config_entries": {},
    }
    
    try:
        # Entity Registry Backup
        entity_registry = async_get_entity_registry(hass)
        lambda_entities = [
            entity for entity in entity_registry.entities.values()
            if entity.config_entry_id and entity.platform == DOMAIN
        ]
        
        for entity in lambda_entities:
            backup_data["entity_registry"][entity.entity_id] = {
                "unique_id": entity.unique_id,
                "name": entity.name,
                "config_entry_id": entity.config_entry_id,
                "platform": entity.platform,
            }
        
        # Config Entries Backup
        config_entries = hass.config_entries.async_entries(DOMAIN)
        for entry in config_entries:
            backup_data["config_entries"][entry.entry_id] = {
                "data": dict(entry.data),
                "options": dict(entry.options) if entry.options else {},
                "title": entry.title,
                "version": entry.version,
            }
        
        _LOGGER.info(
            "Migration backup created: %d entities, %d config entries",
            len(backup_data["entity_registry"]),
            len(backup_data["config_entries"]),
        )
        
        return backup_data
        
    except Exception as e:
        _LOGGER.error("Error creating migration backup: %s", e)
        raise


async def discover_lambda_configs(hass: HomeAssistant) -> Dict[str, List[str]]:
    """Finde alle Lambda Heat Pump Konfigurationen."""
    lambda_configs = {
        "legacy": [],      # use_legacy_names = True
        "non_legacy": [],  # use_legacy_names = False
        "unknown": []      # Keine Einstellung gefunden
    }
    
    config_entries = hass.config_entries.async_entries(DOMAIN)
    
    for entry in config_entries:
        use_legacy = entry.data.get("use_legacy_modbus_names")
        
        if use_legacy is True:
            lambda_configs["legacy"].append(entry.entry_id)
        elif use_legacy is False:
            lambda_configs["non_legacy"].append(entry.entry_id)
        else:
            lambda_configs["unknown"].append(entry.entry_id)
    
    _LOGGER.info(
        "Lambda configs discovered: %d legacy, %d non-legacy, %d unknown",
        len(lambda_configs["legacy"]),
        len(lambda_configs["non_legacy"]),
        len(lambda_configs["unknown"]),
    )
    
    return lambda_configs


async def migrate_config_intelligent(
    hass: HomeAssistant, 
    entry_id: str, 
    backup_data: Dict[str, Any]
) -> bool:
    """Intelligente Migration für eine einzelne Config."""
    try:
        entry = hass.config_entries.async_get_entry(entry_id)
        if not entry:
            _LOGGER.error("Config entry %s not found", entry_id)
            return False
        
        original_use_legacy = entry.data.get("use_legacy_modbus_names")
        name_prefix = entry.data.get(CONF_NAME, "eu08l")
        
        _LOGGER.info(
            "Migrating config %s: use_legacy=%s, name_prefix=%s",
            entry_id, original_use_legacy, name_prefix
        )
        
        # Migrate entities based on original setting
        if original_use_legacy is False:
            # Non-Legacy: Keep entity IDs, fix unique IDs
            success = await _migrate_non_legacy_entities(hass, entry_id, name_prefix)
        else:
            # Legacy or Unknown: Full migration
            success = await _migrate_legacy_entities(hass, entry_id, name_prefix)
        
        # Update config entry AFTER successful migration
        if success:
            new_data = dict(entry.data)
            new_data["use_legacy_modbus_names"] = True
            
            hass.config_entries.async_update_entry(
                entry, 
                data=new_data,
                version=MIGRATION_VERSION
            )
            
            # Clean up orphaned entities after successful migration
            await _cleanup_orphaned_entities(hass, entry_id, name_prefix)
            
            _LOGGER.info("Successfully migrated config %s", entry_id)
        else:
            _LOGGER.error("Failed to migrate config %s", entry_id)
        
        return success
        
    except Exception as e:
        _LOGGER.error("Error migrating config %s: %s", entry_id, e)
        return False


async def _migrate_non_legacy_entities(
    hass: HomeAssistant, 
    entry_id: str, 
    name_prefix: str
) -> bool:
    """Migrate non-legacy entities: keep entity IDs, fix unique IDs."""
    entity_registry = async_get_entity_registry(hass)
    migrated_count = 0
    
    try:
        # Find all entities for this config entry
        entities = [
            entity for entity in entity_registry.entities.values()
            if entity.config_entry_id == entry_id and entity.platform == DOMAIN
        ]
        
        for entity in entities:
            # Check if unique ID already has name_prefix
            if entity.unique_id.startswith(f"{name_prefix}_"):
                _LOGGER.debug(
                    "Entity %s already has legacy unique ID format, skipping",
                    entity.entity_id
                )
                continue
            
            # Keep entity ID, update unique ID to include name_prefix
            new_unique_id = f"{name_prefix}_{entity.unique_id}"
            
            # Check if new unique ID already exists
            existing_entity = entity_registry.async_get_entity_id(
                entity.domain, entity.platform, new_unique_id
            )
            
            if existing_entity and existing_entity != entity.entity_id:
                _LOGGER.info(
                    "Unique ID %s already exists for entity %s, skipping %s",
                    new_unique_id, existing_entity, entity.entity_id
                )
                continue
            
            # Update unique ID
            entity_registry.async_update_entity(
                entity.entity_id,
                new_unique_id=new_unique_id
            )
            migrated_count += 1
        
        _LOGGER.info(
            "Non-legacy migration: %d entities updated for config %s",
            migrated_count, entry_id
        )
        return True
        
    except Exception as e:
        _LOGGER.error("Error in non-legacy migration: %s", e)
        return False


async def _migrate_legacy_entities(
    hass: HomeAssistant, 
    entry_id: str, 
    name_prefix: str
) -> bool:
    """Migrate legacy entities: full entity ID and unique ID migration."""
    entity_registry = async_get_entity_registry(hass)
    migrated_count = 0
    
    try:
        # Find all entities for this config entry
        entities = [
            entity for entity in entity_registry.entities.values()
            if entity.config_entry_id == entry_id and entity.platform == DOMAIN
        ]
        
        for entity in entities:
            # Check if entity already has legacy format (sensor or climate)
            if (entity.entity_id.startswith(f"sensor.{name_prefix}_") or 
                entity.entity_id.startswith(f"climate.{name_prefix}_")):
                _LOGGER.debug(
                    "Entity %s already has legacy format, skipping",
                    entity.entity_id
                )
                continue
            
            # Check if unique ID already has name_prefix
            if entity.unique_id.startswith(f"{name_prefix}_"):
                _LOGGER.debug(
                    "Entity %s already has legacy unique ID format, skipping",
                    entity.entity_id
                )
                continue
            
            # Create new entity ID with name_prefix
            if entity.entity_id.startswith("sensor."):
                new_entity_id = entity.entity_id.replace(
                    "sensor.", f"sensor.{name_prefix}_"
                )
            elif entity.entity_id.startswith("climate."):
                new_entity_id = entity.entity_id.replace(
                    "climate.", f"climate.{name_prefix}_"
                )
            else:
                _LOGGER.warning(
                    "Unknown entity domain %s, skipping %s",
                    entity.entity_id.split(".")[0], entity.entity_id
                )
                continue
            
            # Validate entity ID format
            if not new_entity_id or "." not in new_entity_id:
                _LOGGER.warning(
                    "Invalid entity ID format %s, skipping %s",
                    new_entity_id, entity.entity_id
                )
                continue
            
            # Check if new entity ID already exists
            if entity_registry.async_get(new_entity_id):
                _LOGGER.info(
                    "Entity ID %s already exists, skipping %s",
                    new_entity_id, entity.entity_id
                )
                continue
            
            # Update unique ID to match new entity ID
            if new_entity_id.startswith("sensor."):
                new_unique_id = new_entity_id.replace("sensor.", "")
            elif new_entity_id.startswith("climate."):
                new_unique_id = new_entity_id.replace("climate.", "")
            else:
                _LOGGER.warning(
                    "Unknown entity domain for unique ID %s, skipping",
                    new_entity_id
                )
                continue
            
            # Validate unique ID format
            if not new_unique_id or len(new_unique_id) > 255:
                _LOGGER.warning(
                    "Invalid unique ID format %s, skipping %s",
                    new_unique_id, entity.entity_id
                )
                continue
            
            try:
                # Update entity
                entity_registry.async_update_entity(
                    entity.entity_id,
                    new_entity_id=new_entity_id,
                    new_unique_id=new_unique_id
                )
            except Exception as update_ex:
                _LOGGER.info(
                    "Entity %s already has correct format, skipping: %s",
                    entity.entity_id, update_ex
                )
                continue
            migrated_count += 1
        
        _LOGGER.info(
            "Legacy migration: %d entities updated for config %s",
            migrated_count, entry_id
        )
        return True
        
    except Exception as e:
        _LOGGER.error("Error in legacy migration: %s", e)
        return False


async def _cleanup_orphaned_entities(
    hass: HomeAssistant, 
    entry_id: str, 
    name_prefix: str
) -> None:
    """Clean up orphaned entities after migration."""
    entity_registry = async_get_entity_registry(hass)
    removed_count = 0
    
    try:
        # Find all entities for this config entry
        entities = [
            entity for entity in entity_registry.entities.values()
            if entity.config_entry_id == entry_id and entity.platform == DOMAIN
        ]
        
        for entity in entities:
            # Check if this is an orphaned entity (old format)
            # Old entities have the name_prefix in their unique_id but may not have the correct format
            if entity.entity_id.startswith("sensor."):
                # Case 1: Entity ID doesn't start with name_prefix (old format)
                if not entity.entity_id.startswith(f"sensor.{name_prefix}_"):
                    _LOGGER.info(
                        "Removing orphaned sensor entity (old format): %s "
                        "(unique_id: %s)",
                        entity.entity_id, entity.unique_id
                    )
                    
                    try:
                        entity_registry.async_remove(entity.entity_id)
                        removed_count += 1
                    except Exception as e:
                        _LOGGER.warning(
                            "Failed to remove orphaned entity %s: %s",
                            entity.entity_id, e
                        )
                
                # Case 2: Entity ID starts with name_prefix but unique_id doesn't have the correct format
                elif (entity.entity_id.startswith(f"sensor.{name_prefix}_") and 
                      not entity.unique_id.startswith(f"{name_prefix}_")):
                    _LOGGER.info(
                        "Removing orphaned sensor entity (mismatched format): "
                        "%s (unique_id: %s)",
                        entity.entity_id, entity.unique_id
                    )
                    
                    try:
                        entity_registry.async_remove(entity.entity_id)
                        removed_count += 1
                    except Exception as e:
                        _LOGGER.warning(
                            "Failed to remove orphaned entity %s: %s",
                            entity.entity_id, e
                        )
            
            elif entity.entity_id.startswith("climate."):
                # Case 1: Entity ID doesn't start with name_prefix (old format)
                if not entity.entity_id.startswith(f"climate.{name_prefix}_"):
                    _LOGGER.info(
                        "Removing orphaned climate entity (old format): %s "
                        "(unique_id: %s)",
                        entity.entity_id, entity.unique_id
                    )
                    
                    try:
                        entity_registry.async_remove(entity.entity_id)
                        removed_count += 1
                    except Exception as e:
                        _LOGGER.warning(
                            "Failed to remove orphaned climate entity %s: %s",
                            entity.entity_id, e
                        )
                
                # Case 2: Entity ID starts with name_prefix but unique_id doesn't have the correct format
                elif (entity.entity_id.startswith(f"climate.{name_prefix}_") and 
                      not entity.unique_id.startswith(f"{name_prefix}_")):
                    _LOGGER.info(
                        "Removing orphaned climate entity (mismatched format): "
                        "%s (unique_id: %s)",
                        entity.entity_id, entity.unique_id
                    )
                    
                    try:
                        entity_registry.async_remove(entity.entity_id)
                        removed_count += 1
                    except Exception as e:
                        _LOGGER.warning(
                            "Failed to remove orphaned climate entity %s: %s",
                            entity.entity_id, e
                        )
        
        if removed_count > 0:
            _LOGGER.info(
                "Cleanup completed: %d orphaned entities removed for config %s",
                removed_count, entry_id
            )
        else:
            _LOGGER.debug("No orphaned entities found for config %s", entry_id)
            
    except Exception as e:
        _LOGGER.error("Error during orphaned entity cleanup: %s", e)


async def restore_registry_file_backup(hass: HomeAssistant, timestamp: str = None) -> bool:
    """Restore registry files from backup."""
    try:
        # Get Home Assistant config directory
        config_dir = hass.config.config_dir
        backup_dir = os.path.join(
            config_dir, "lambda_heat_pumps", "backup"
        )
        
        # Check if backup directory exists using async executor
        exists = await hass.async_add_executor_job(
            lambda: os.path.exists(backup_dir)
        )
        if not exists:
            _LOGGER.error("Backup directory not found: %s", backup_dir)
            return False
        
        # Find latest backup if timestamp not specified
        if timestamp is None:
            try:
                backup_files = await hass.async_add_executor_job(
                    lambda: os.listdir(backup_dir)
                )
                registry_backup_files = [
                    f for f in backup_files 
                    if f.endswith((".entity_registry", ".device_registry", ".config_entries"))
                ]
                
                if not registry_backup_files:
                    _LOGGER.error("No backup files found in %s", backup_dir)
                    return False
                
                # Get latest backup by timestamp
                registry_backup_files.sort()
                latest_backup = registry_backup_files[-1]
                timestamp = latest_backup.split(".")[-1]
                _LOGGER.info("Using latest backup timestamp: %s", timestamp)
            except OSError as e:
                _LOGGER.error("Failed to list backup directory: %s", e)
                return False
        
        # Restore registry files
        registry_files = [
            "core.entity_registry",
            "core.device_registry", 
            "core.config_entries"
        ]
        
        restored_files = []
        for registry_file in registry_files:
            backup_path = os.path.join(backup_dir, f"{registry_file}.{timestamp}")
            restore_path = os.path.join(config_dir, ".storage", registry_file)
            
            try:
                # Check if backup file exists
                exists = await hass.async_add_executor_job(
                    lambda: os.path.exists(backup_path)
                )
                if exists:
                    # Restore file using async executor
                    await hass.async_add_executor_job(
                        lambda: shutil.copy2(backup_path, restore_path)
                    )
                    restored_files.append(registry_file)
                    _LOGGER.info(
                        "Registry restored: %s -> %s",
                        backup_path, restore_path
                    )
                else:
                    _LOGGER.warning(
                        "Backup file not found: %s",
                        backup_path
                    )
            except (OSError, IOError) as e:
                _LOGGER.error(
                    "Failed to restore registry file %s: %s",
                    registry_file, e
                )
                continue
        
        if restored_files:
            _LOGGER.info(
                "Registry restore completed: %d files restored",
                len(restored_files)
            )
            return True
        else:
            _LOGGER.warning("No registry files were restored")
            return False
            
    except Exception as e:
        _LOGGER.error("Error restoring registry backup: %s", e)
        return False


async def rollback_migration(
    hass: HomeAssistant, 
    backup_data: Dict[str, Any]
) -> bool:
    """Rollback zur Backup-Version bei Fehlern."""
    try:
        _LOGGER.info("Starting migration rollback")
        
        # Step 1: Restore registry files from backup
        _LOGGER.info("Restoring registry files from backup")
        registry_restore_success = await restore_registry_file_backup(hass)
        if not registry_restore_success:
            _LOGGER.warning("Registry file restore failed, continuing with in-memory rollback")
        
        # Step 2: Restore config entries
        for entry_id, entry_data in backup_data["config_entries"].items():
            entry = hass.config_entries.async_get_entry(entry_id)
            if entry:
                hass.config_entries.async_update_entry(
                    entry,
                    data=entry_data["data"],
                    options=entry_data["options"],
                    version=entry_data.get("version", 1)
                )
        
        # Step 3: Restore entity registry
        entity_registry = async_get_entity_registry(hass)
        for entity_id, entity_data in backup_data["entity_registry"].items():
            entity = entity_registry.async_get(entity_id)
            if entity:
                entity_registry.async_update_entity(
                    entity_id,
                    new_unique_id=entity_data["unique_id"],
                    name=entity_data["name"]
                )
        
        _LOGGER.info("Migration rollback completed successfully")
        return True
        
    except Exception as e:
        _LOGGER.error("Error during migration rollback: %s", e)
        return False


async def perform_option_c_migration(hass: HomeAssistant) -> Dict[str, Any]:
    """Haupt-Migrationsfunktion mit Backup und Multi-Config Support."""
    migration_result = {
        "success": False,
        "backup_created": False,
        "configs_migrated": 0,
        "entities_migrated": 0,
        "errors": [],
        "backup_data": None,
    }
    
    try:
        # Step 1: Create registry file backup (try to create, but don't abort if it fails)
        _LOGGER.info("Creating registry file backup")
        registry_backup_success = await create_registry_file_backup(hass)
        if not registry_backup_success:
            _LOGGER.warning(
                "Registry file backup failed, but continuing with migration"
            )
            migration_result["errors"].append("Registry file backup failed")
        else:
            _LOGGER.info("Registry file backup completed successfully")
            migration_result["backup_created"] = True
        
        # Step 2: Create in-memory backup
        _LOGGER.info("Creating migration backup")
        try:
            backup_data = await create_migration_backup(hass)
            migration_result["backup_data"] = backup_data
        except Exception as e:
            error_msg = f"Failed to create migration backup: {e}"
            migration_result["errors"].append(error_msg)
            _LOGGER.error(error_msg)
            return migration_result
        
        # Step 3: Discover configs
        _LOGGER.info("Discovering Lambda configurations")
        lambda_configs = await discover_lambda_configs(hass)
        
        # Step 4: Migrate each config
        all_configs = (
            lambda_configs["legacy"] + 
            lambda_configs["non_legacy"] + 
            lambda_configs["unknown"]
        )
        
        if not all_configs:
            _LOGGER.info("No Lambda configurations found to migrate")
            migration_result["success"] = True
            return migration_result
        
        for entry_id in all_configs:
            try:
                success = await migrate_config_intelligent(
                    hass, entry_id, backup_data
                )
                if success:
                    migration_result["configs_migrated"] += 1
                else:
                    migration_result["errors"].append(
                        f"Failed to migrate config {entry_id}"
                    )
            except Exception as e:
                error_msg = f"Error migrating config {entry_id}: {e}"
                migration_result["errors"].append(error_msg)
                _LOGGER.error(error_msg)
        
        # Step 5: Check success
        if migration_result["configs_migrated"] == len(all_configs):
            migration_result["success"] = True
            _LOGGER.info(
                "Migration completed successfully: %d configs migrated",
                migration_result["configs_migrated"]
            )
        else:
            _LOGGER.warning(
                "Migration completed with errors: %d/%d configs migrated",
                migration_result["configs_migrated"], len(all_configs)
            )
            # Rollback on critical errors (more than 50% failed)
            if len(migration_result["errors"]) > len(all_configs) // 2:
                _LOGGER.error("Too many errors, performing rollback")
                await rollback_migration(hass, backup_data)
                migration_result["success"] = False
        
        return migration_result
        
    except Exception as e:
        error_msg = f"Critical migration error: {e}"
        migration_result["errors"].append(error_msg)
        _LOGGER.error(error_msg)
        
        # Rollback on critical error
        if migration_result["backup_data"]:
            _LOGGER.info("Performing rollback due to critical error")
            await rollback_migration(hass, migration_result["backup_data"])
        
        return migration_result


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate config entry to new version."""
    _LOGGER.info(
        "Starting migration for config entry %s (version %s)",
        config_entry.entry_id, config_entry.version
    )
    
    # Check if migration is needed
    if config_entry.version >= MIGRATION_VERSION:
        _LOGGER.info(
            "Config entry already at version %d or higher, performing cleanup only",
            MIGRATION_VERSION
        )
        # Even if already migrated, perform cleanup of orphaned entities
        try:
            await cleanup_orphaned_entities_auto(hass)
            _LOGGER.info("Cleanup completed for already migrated config")
            return True
        except Exception as e:
            _LOGGER.error("Error during cleanup: %s", e)
            return False
    
    # Perform the migration
    result = await perform_option_c_migration(hass)
    
    if result["success"]:
        _LOGGER.info("Migration completed successfully")
        return True
    else:
        _LOGGER.error("Migration failed: %s", result["errors"])
        return False 


async def cleanup_orphaned_entities_auto(hass: HomeAssistant) -> None:
    """Automatische Bereinigung verwaister Entities bei jedem Setup."""
    try:
        # Finde alle Lambda Config Entries
        lambda_configs = await discover_lambda_configs(hass)
        all_configs = (
            lambda_configs["legacy"] + 
            lambda_configs["non_legacy"] + 
            lambda_configs["unknown"]
        )
        
        if not all_configs:
            _LOGGER.debug("No Lambda configs found for orphaned entity cleanup")
            return
        
        _LOGGER.info("Starting automatic orphaned entity cleanup for %d configs", len(all_configs))
        
        total_removed = 0
        for entry_id in all_configs:
            try:
                entry = hass.config_entries.async_get_entry(entry_id)
                if not entry:
                    continue
                
                name_prefix = entry.data.get(CONF_NAME, "eu08l")
                removed_count = await _cleanup_orphaned_entities_single_config(
                    hass, entry_id, name_prefix
                )
                total_removed += removed_count
                
            except Exception as e:
                _LOGGER.error("Error during cleanup for config %s: %s", entry_id, e)
        
        if total_removed > 0:
            _LOGGER.info("Automatic cleanup completed: %d orphaned entities removed", total_removed)
        else:
            _LOGGER.debug("No orphaned entities found during automatic cleanup")
            
    except Exception as e:
        _LOGGER.error("Error during automatic orphaned entity cleanup: %s", e)


async def _cleanup_orphaned_entities_single_config(
    hass: HomeAssistant, 
    entry_id: str, 
    name_prefix: str
) -> int:
    """Clean up orphaned entities for a single config entry."""
    entity_registry = async_get_entity_registry(hass)
    removed_count = 0
    
    try:
        # Find all entities for this config entry
        entities = [
            entity for entity in entity_registry.entities.values()
            if entity.config_entry_id == entry_id and entity.platform == DOMAIN
        ]
        
        for entity in entities:
            # Check if this is an orphaned entity (old format without prefix)
            if (entity.entity_id.startswith("sensor.") and 
                not entity.entity_id.startswith(f"sensor.{name_prefix}_") and
                not entity.unique_id.startswith(f"{name_prefix}_")):
                
                _LOGGER.info(
                    "Removing orphaned entity: %s (unique_id: %s)",
                    entity.entity_id, entity.unique_id
                )
                
                try:
                    entity_registry.async_remove(entity.entity_id)
                    removed_count += 1
                except Exception as e:
                    _LOGGER.warning(
                        "Failed to remove orphaned entity %s: %s",
                        entity.entity_id, e
                    )
            
            elif (entity.entity_id.startswith("climate.") and 
                  not entity.entity_id.startswith(f"climate.{name_prefix}_") and
                  not entity.unique_id.startswith(f"{name_prefix}_")):
                
                _LOGGER.info(
                    "Removing orphaned climate entity: %s (unique_id: %s)",
                    entity.entity_id, entity.unique_id
                )
                
                try:
                    entity_registry.async_remove(entity.entity_id)
                    removed_count += 1
                except Exception as e:
                    _LOGGER.warning(
                        "Failed to remove orphaned climate entity %s: %s",
                        entity.entity_id, e
                    )
        
        if removed_count > 0:
            _LOGGER.info(
                "Cleanup completed for config %s: %d orphaned entities removed",
                entry_id, removed_count
            )
        
        return removed_count
            
    except Exception as e:
        _LOGGER.error("Error during orphaned entity cleanup for config %s: %s", entry_id, e)
        return 0 
