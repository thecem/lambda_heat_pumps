"""Test migration logic for Lambda Heat Pumps integration."""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from custom_components.lambda_heat_pumps import async_migrate_entry
from custom_components.lambda_heat_pumps.__init__ import migrate_entity_registry


class TestMigration:
    """Test migration functionality."""

    @pytest.mark.asyncio
    async def test_migrate_entry_version_check(self):
        """Test that migration only runs for old versions."""
        mock_hass = Mock()
        mock_entry = Mock()
        mock_entry.data = {"name": "eu08l", "host": "192.168.1.100"}

        # Test mit Version 1 (sollte migrieren)
        mock_entry.version = 1
        with patch(
            "custom_components.lambda_heat_pumps.migrate_entity_registry"
        ) as mock_migrate:
            mock_migrate.return_value = True
            result = await async_migrate_entry(mock_hass, mock_entry)
            assert result is True
            mock_migrate.assert_called_once_with(mock_hass, mock_entry)

        # Test mit Version 3 (sollte nicht migrieren)
        mock_entry.version = 3
        with patch(
            "custom_components.lambda_heat_pumps.migrate_entity_registry"
        ) as mock_migrate:
            result = await async_migrate_entry(mock_hass, mock_entry)
            assert result is True
            mock_migrate.assert_not_called()

    @pytest.mark.asyncio
    async def test_migrate_entity_registry_duplicate_removal(self):
        """Test removal of duplicate entities with numeric suffixes."""
        mock_hass = Mock()
        mock_entry = Mock()
        mock_entry.entry_id = "test_entry"
        mock_entry.data = {"name": "eu08l"}

        # Mock Entity Registry
        mock_registry = Mock()
        mock_registry.entities.get_entries_for_config_entry_id.return_value = [
            Mock(entity_id="sensor.eu08l_ambient_temp", unique_id="ambient_temp"),
            Mock(
                entity_id="sensor.eu08l_ambient_temp_2", unique_id="eu08l_ambient_temp"
            ),
            Mock(
                entity_id="climate.eu08l_boil1_hot_water",
                unique_id="lambda_heat_pumps_hot_water",
            ),
            Mock(entity_id="climate.hot_water_1", unique_id="old_hot_water"),
        ]

        with patch(
            "homeassistant.helpers.entity_registry.async_get",
            return_value=mock_registry,
        ):
            result = await migrate_entity_registry(mock_hass, mock_entry)

            assert result is True
            # Prüfe, dass _2 Entity entfernt wurde
            mock_registry.async_remove.assert_called_with("sensor.eu08l_ambient_temp_2")

    @pytest.mark.asyncio
    async def test_migrate_entity_registry_general_sensor_migration(self):
        """Test migration of general sensor unique_ids."""
        mock_hass = Mock()
        mock_entry = Mock()
        mock_entry.entry_id = "test_entry"
        mock_entry.data = {"name": "eu08l"}

        # Mock Entity Registry mit General Sensor
        mock_registry = Mock()
        mock_registry.entities.get_entries_for_config_entry_id.return_value = [
            Mock(
                entity_id="sensor.eu08l_ambient_temp",
                unique_id="ambient_temp",  # Ohne name_prefix
            )
        ]

        with patch(
            "homeassistant.helpers.entity_registry.async_get",
            return_value=mock_registry,
        ):
            result = await migrate_entity_registry(mock_hass, mock_entry)

            assert result is True
            # Prüfe, dass unique_id aktualisiert wurde
            mock_registry.async_update_entity.assert_called_with(
                "sensor.eu08l_ambient_temp", new_unique_id="eu08l_ambient_temp"
            )

    @pytest.mark.asyncio
    async def test_migrate_entity_registry_climate_entity_migration(self):
        """Test migration of climate entity unique_ids."""
        mock_hass = Mock()
        mock_entry = Mock()
        mock_entry.entry_id = "test_entry"
        mock_entry.data = {"name": "eu08l"}

        # Mock Entity Registry mit Climate Entity
        mock_registry = Mock()
        mock_registry.entities.get_entries_for_config_entry_id.return_value = [
            Mock(
                entity_id="climate.eu08l_boil1_hot_water",
                unique_id="lambda_heat_pumps_hot_water",  # Altes Format
            )
        ]

        with patch(
            "homeassistant.helpers.entity_registry.async_get",
            return_value=mock_registry,
        ):
            result = await migrate_entity_registry(mock_hass, mock_entry)

            assert result is True
            # Prüfe, dass unique_id aktualisiert wurde
            mock_registry.async_update_entity.assert_called_with(
                "climate.eu08l_boil1_hot_water", new_unique_id="eu08l_boil1_hot_water"
            )

    @pytest.mark.asyncio
    async def test_migrate_entity_registry_old_climate_entity_removal(self):
        """Test removal of old climate entities with incompatible format."""
        mock_hass = Mock()
        mock_entry = Mock()
        mock_entry.entry_id = "test_entry"
        mock_entry.data = {"name": "eu08l"}

        # Mock Entity Registry mit altem Climate Entity
        mock_registry = Mock()
        mock_registry.entities.get_entries_for_config_entry_id.return_value = [
            Mock(
                entity_id="climate.hot_water_1",  # Altes Format
                unique_id="old_hot_water",
            )
        ]

        with patch(
            "homeassistant.helpers.entity_registry.async_get",
            return_value=mock_registry,
        ):
            result = await migrate_entity_registry(mock_hass, mock_entry)

            assert result is True
            # Prüfe, dass altes Climate Entity entfernt wurde
            mock_registry.async_remove.assert_called_with("climate.hot_water_1")

    @pytest.mark.asyncio
    async def test_migrate_entity_registry_cycling_sensor_migration(self):
        """Test migration of cycling sensor unique_ids."""
        mock_hass = Mock()
        mock_entry = Mock()
        mock_entry.entry_id = "test_entry"
        mock_entry.data = {"name": "eu08l"}

        # Mock Entity Registry mit Cycling Sensor
        mock_registry = Mock()
        mock_registry.entities.get_entries_for_config_entry_id.return_value = [
            Mock(
                entity_id="sensor.eu08l_hp1_heating_cycling_total",
                unique_id="hp1_heating_cycling_total",  # Inkonsistent
            )
        ]

        with patch(
            "homeassistant.helpers.entity_registry.async_get",
            return_value=mock_registry,
        ):
            result = await migrate_entity_registry(mock_hass, mock_entry)

            assert result is True
            # Prüfe, dass unique_id aktualisiert wurde
            mock_registry.async_update_entity.assert_called_with(
                "sensor.eu08l_hp1_heating_cycling_total",
                new_unique_id="eu08l_hp1_heating_cycling_total",
            )

    @pytest.mark.asyncio
    async def test_migrate_entity_registry_no_changes_needed(self):
        """Test migration when no changes are needed."""
        mock_hass = Mock()
        mock_entry = Mock()
        mock_entry.entry_id = "test_entry"
        mock_entry.data = {"name": "eu08l"}

        # Mock Entity Registry mit bereits korrekten Entities
        mock_registry = Mock()
        mock_registry.entities.get_entries_for_config_entry_id.return_value = [
            Mock(
                entity_id="sensor.eu08l_ambient_temp",
                unique_id="eu08l_ambient_temp",  # Bereits korrekt
            ),
            Mock(
                entity_id="climate.eu08l_boil1_hot_water",
                unique_id="eu08l_boil1_hot_water",  # Bereits korrekt
            ),
        ]

        with patch(
            "homeassistant.helpers.entity_registry.async_get",
            return_value=mock_registry,
        ):
            result = await migrate_entity_registry(mock_hass, mock_entry)

            assert result is True
            # Prüfe, dass keine Änderungen vorgenommen wurden
            mock_registry.async_update_entity.assert_not_called()
            mock_registry.async_remove.assert_not_called()

    @pytest.mark.asyncio
    async def test_migrate_entity_registry_error_handling(self):
        """Test error handling during migration."""
        mock_hass = Mock()
        mock_entry = Mock()
        mock_entry.entry_id = "test_entry"
        mock_entry.data = {"name": "eu08l"}

        # Mock Entity Registry mit Exception
        mock_registry = Mock()
        mock_registry.entities.get_entries_for_config_entry_id.side_effect = Exception(
            "Test error"
        )

        with patch(
            "homeassistant.helpers.entity_registry.async_get",
            return_value=mock_registry,
        ):
            result = await migrate_entity_registry(mock_hass, mock_entry)

            assert result is False

    @pytest.mark.asyncio
    async def test_migrate_entity_registry_empty_registry(self):
        """Test migration with empty entity registry."""
        mock_hass = Mock()
        mock_entry = Mock()
        mock_entry.entry_id = "test_entry"
        mock_entry.data = {"name": "eu08l"}

        # Mock Entity Registry ohne Entities
        mock_registry = Mock()
        mock_registry.entities.get_entries_for_config_entry_id.return_value = []

        with patch(
            "homeassistant.helpers.entity_registry.async_get",
            return_value=mock_registry,
        ):
            result = await migrate_entity_registry(mock_hass, mock_entry)

            assert result is True
            # Prüfe, dass keine Änderungen vorgenommen wurden
            mock_registry.async_update_entity.assert_not_called()
            mock_registry.async_remove.assert_not_called()

    @pytest.mark.asyncio
    async def test_migrate_entity_registry_multiple_duplicates(self):
        """Test removal of multiple duplicate entities."""
        mock_hass = Mock()
        mock_entry = Mock()
        mock_entry.entry_id = "test_entry"
        mock_entry.data = {"name": "eu08l"}

        # Mock Entity Registry mit mehreren Duplikaten
        mock_registry = Mock()
        mock_registry.entities.get_entries_for_config_entry_id.return_value = [
            Mock(entity_id="sensor.eu08l_ambient_temp", unique_id="eu08l_ambient_temp"),
            Mock(
                entity_id="sensor.eu08l_ambient_temp_2", unique_id="eu08l_ambient_temp"
            ),
            Mock(
                entity_id="sensor.eu08l_ambient_temp_3", unique_id="eu08l_ambient_temp"
            ),
            Mock(
                entity_id="climate.eu08l_boil1_hot_water",
                unique_id="eu08l_boil1_hot_water",
            ),
            Mock(entity_id="climate.hot_water_1", unique_id="old_hot_water"),
            Mock(entity_id="climate.hot_water_2", unique_id="old_hot_water_2"),
        ]

        with patch(
            "homeassistant.helpers.entity_registry.async_get",
            return_value=mock_registry,
        ):
            result = await migrate_entity_registry(mock_hass, mock_entry)

            assert result is True
            # Prüfe, dass alle Duplikate entfernt wurden
            expected_removals = [
                "sensor.eu08l_ambient_temp_2",
                "sensor.eu08l_ambient_temp_3",
                "climate.hot_water_1",
                "climate.hot_water_2",
            ]
            actual_removals = [
                call[0][0] for call in mock_registry.async_remove.call_args_list
            ]
            assert set(actual_removals) == set(expected_removals)

    @pytest.mark.asyncio
    async def test_migrate_entity_registry_name_prefix_case_sensitivity(self):
        """Test migration with different name_prefix cases."""
        mock_hass = Mock()
        mock_entry = Mock()
        mock_entry.entry_id = "test_entry"
        mock_entry.data = {"name": "EU08L"}  # Uppercase

        # Mock Entity Registry
        mock_registry = Mock()
        mock_registry.entities.get_entries_for_config_entry_id.return_value = [
            Mock(
                entity_id="sensor.eu08l_ambient_temp",  # Lowercase in entity_id
                unique_id="ambient_temp",
            )
        ]

        with patch(
            "homeassistant.helpers.entity_registry.async_get",
            return_value=mock_registry,
        ):
            result = await migrate_entity_registry(mock_hass, mock_entry)

            assert result is True
            # Prüfe, dass unique_id mit lowercase name_prefix aktualisiert wurde
            mock_registry.async_update_entity.assert_called_with(
                "sensor.eu08l_ambient_temp", new_unique_id="eu08l_ambient_temp"
            )
