"""
Unit tests for the DiagramGenerator class.

Tests cover workspace creation, view management, export functionality,
and validation methods for the core diagram generation functionality.
"""

import pytest
import json
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.diagrams.generator import (
    DiagramGenerator,
    DiagramConfig,
    DiagramMetadata
)


class TestDiagramConfig:
    """Test cases for DiagramConfig dataclass."""
    
    def test_diagram_config_creation_with_defaults(self):
        """Test creating DiagramConfig with default values."""
        config = DiagramConfig(
            name="Test Diagram",
            description="Test description"
        )
        
        assert config.name == "Test Diagram"
        assert config.description == "Test description"
        assert config.version == "1.0.0"
        assert config.author == "Architecture Team"
        assert config.output_formats == ['json', 'plantuml']
    
    def test_diagram_config_creation_with_custom_values(self):
        """Test creating DiagramConfig with custom values."""
        config = DiagramConfig(
            name="Custom Diagram",
            description="Custom description",
            version="2.0.0",
            author="Custom Author",
            output_formats=['json', 'svg']
        )
        
        assert config.name == "Custom Diagram"
        assert config.description == "Custom description"
        assert config.version == "2.0.0"
        assert config.author == "Custom Author"
        assert config.output_formats == ['json', 'svg']


class TestDiagramMetadata:
    """Test cases for DiagramMetadata dataclass."""
    
    def test_diagram_metadata_creation_with_defaults(self):
        """Test creating DiagramMetadata with default values."""
        now = datetime.now()
        metadata = DiagramMetadata(
            title="Test Diagram",
            description="Test description",
            diagram_type="system_context",
            last_updated=now,
            file_path="test.json"
        )
        
        assert metadata.title == "Test Diagram"
        assert metadata.description == "Test description"
        assert metadata.diagram_type == "system_context"
        assert metadata.last_updated == now
        assert metadata.file_path == "test.json"
        assert metadata.output_files == {}
    
    def test_diagram_metadata_creation_with_output_files(self):
        """Test creating DiagramMetadata with output files."""
        now = datetime.now()
        output_files = {"png": "test.png", "svg": "test.svg"}
        
        metadata = DiagramMetadata(
            title="Test Diagram",
            description="Test description",
            diagram_type="container",
            last_updated=now,
            file_path="test.json",
            output_files=output_files
        )
        
        assert metadata.output_files == output_files


class TestDiagramGenerator:
    """Test cases for DiagramGenerator class."""
    
    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return DiagramConfig(
            name="Test System",
            description="Test system description",
            version="1.0.0",
            author="Test Author"
        )
    
    @pytest.fixture
    def generator(self, config):
        """Create a DiagramGenerator instance for testing."""
        return DiagramGenerator(config)
    
    def test_generator_initialization(self, config):
        """Test DiagramGenerator initialization."""
        generator = DiagramGenerator(config)
        
        assert generator.config == config
        assert generator.workspace is None
        assert generator._metadata == []
    
    @patch('src.diagrams.generator.Workspace')
    def test_create_workspace(self, mock_workspace, generator):
        """Test workspace creation."""
        mock_workspace_instance = Mock()
        mock_workspace.return_value = mock_workspace_instance
        
        result = generator.create_workspace()
        
        mock_workspace.assert_called_once()
        assert generator.workspace == mock_workspace_instance
        assert result == mock_workspace_instance
    
    def test_add_system_context_view_without_workspace(self, generator):
        """Test adding system context view without workspace raises error."""
        mock_system = Mock()
        mock_system.name = "Test System"
        
        with pytest.raises(ValueError, match="Workspace must be created before adding views"):
            generator.add_system_context_view(
                mock_system,
                "Test View",
                "Test description"
            )
    
    @patch('src.diagrams.generator.Workspace')
    def test_add_system_context_view_success(self, mock_workspace, generator):
        """Test successful addition of system context view."""
        # Setup workspace
        mock_workspace_instance = Mock()
        mock_workspace.return_value = mock_workspace_instance
        mock_view = Mock()
        mock_workspace_instance.SystemContextView.return_value = mock_view
        
        generator.create_workspace()
        
        # Setup software system
        mock_system = Mock()
        mock_system.name = "Test System"
        
        # Add view
        result = generator.add_system_context_view(
            mock_system,
            "Test System Context",
            "Test description"
        )
        
        # Verify view creation
        mock_workspace_instance.SystemContextView.assert_called_once_with(
            mock_system,
            "SystemContext-TestSystem",
            "Test System Context"
        )
        
        assert result == mock_view
        assert len(generator._metadata) == 1
        
        metadata = generator._metadata[0]
        assert metadata.title == "Test System Context"
        assert metadata.description == "Test description"
        assert metadata.diagram_type == "system_context"
        assert metadata.file_path == "SystemContext-TestSystem.json"
    
    @patch('src.diagrams.generator.Workspace')
    def test_add_container_view_success(self, mock_workspace, generator):
        """Test successful addition of container view."""
        # Setup workspace
        mock_workspace_instance = Mock()
        mock_workspace.return_value = mock_workspace_instance
        mock_view = Mock()
        mock_workspace_instance.ContainerView.return_value = mock_view
        
        generator.create_workspace()
        
        # Setup software system
        mock_system = Mock()
        mock_system.name = "Test System"
        
        # Add view
        result = generator.add_container_view(
            mock_system,
            "Test Container View",
            "Container description"
        )
        
        # Verify view creation
        mock_workspace_instance.ContainerView.assert_called_once_with(
            mock_system,
            "Container-TestSystem",
            "Test Container View"
        )
        
        assert result == mock_view
        assert len(generator._metadata) == 1
        
        metadata = generator._metadata[0]
        assert metadata.title == "Test Container View"
        assert metadata.description == "Container description"
        assert metadata.diagram_type == "container"
    
    @patch('src.diagrams.generator.Workspace')
    def test_add_component_view_success(self, mock_workspace, generator):
        """Test successful addition of component view."""
        # Setup workspace
        mock_workspace_instance = Mock()
        mock_workspace.return_value = mock_workspace_instance
        mock_view = Mock()
        mock_workspace_instance.ComponentView.return_value = mock_view
        
        generator.create_workspace()
        
        # Setup container
        mock_container = Mock()
        mock_container.name = "Test Container"
        
        # Add view
        result = generator.add_component_view(
            mock_container,
            "Test Component View",
            "Component description"
        )
        
        # Verify view creation
        mock_workspace_instance.ComponentView.assert_called_once_with(
            mock_container,
            "Component-TestContainer",
            "Test Component View"
        )
        
        assert result == mock_view
        assert len(generator._metadata) == 1
        
        metadata = generator._metadata[0]
        assert metadata.title == "Test Component View"
        assert metadata.description == "Component description"
        assert metadata.diagram_type == "component"
    
    def test_export_to_json_without_workspace(self, generator):
        """Test JSON export without workspace raises error."""
        with pytest.raises(ValueError, match="Workspace must be created before export"):
            generator.export_to_json()
    
    @patch('src.diagrams.generator.Workspace')
    def test_export_to_json_success(self, mock_workspace, generator):
        """Test successful JSON export."""
        # Setup workspace
        mock_workspace_instance = Mock()
        mock_workspace.return_value = mock_workspace_instance
        mock_workspace_instance.dump.return_value = {"test": "data"}
        
        generator.create_workspace()
        
        # Add some metadata
        metadata = DiagramMetadata(
            title="Test Diagram",
            description="Test description",
            diagram_type="system_context",
            last_updated=datetime(2023, 1, 1, 12, 0, 0),
            file_path="test.json"
        )
        generator._metadata.append(metadata)
        
        # Export to JSON
        result = generator.export_to_json()
        
        # Verify result is valid JSON
        data = json.loads(result)
        
        assert "workspace" in data
        assert "model" in data
        assert "views" in data
        assert "metadata" in data
        assert "rawWorkspace" in data
        
        # Check workspace section
        workspace = data["workspace"]
        assert workspace["name"] == generator.config.name
        assert workspace["description"] == generator.config.description
        assert workspace["version"] == generator.config.version
        assert workspace["author"] == generator.config.author
        
        # Check metadata section
        metadata_section = data["metadata"]
        assert "diagrams" in metadata_section
        assert "generatedAt" in metadata_section
        assert "generator" in metadata_section
        
        diagrams = metadata_section["diagrams"]
        assert len(diagrams) == 1
        assert diagrams[0]["title"] == "Test Diagram"
        assert diagrams[0]["type"] == "system_context"
    
    def test_export_to_plantuml_without_workspace(self, generator):
        """Test PlantUML export without workspace raises error."""
        with pytest.raises(ValueError, match="Workspace must be created before export"):
            generator.export_to_plantuml()
    
    @patch('src.diagrams.generator.Workspace')
    def test_export_to_plantuml_success(self, mock_workspace, generator):
        """Test successful PlantUML export."""
        # Setup workspace
        mock_workspace_instance = Mock()
        mock_workspace.return_value = mock_workspace_instance
        
        generator.create_workspace()
        
        # Add some metadata
        metadata = DiagramMetadata(
            title="Test Diagram",
            description="Test description",
            diagram_type="system_context",
            last_updated=datetime(2023, 1, 1, 12, 0, 0),
            file_path="test.json"
        )
        generator._metadata.append(metadata)
        
        # Export to PlantUML
        result = generator.export_to_plantuml()
        
        # Verify PlantUML structure
        assert "@startuml" in result
        assert "@enduml" in result
        assert f"!title {generator.config.name}" in result
        assert f"' Author: {generator.config.author}" in result
        assert f"' Version: {generator.config.version}" in result
        assert "Test Diagram" in result
        assert "system_context" in result
    
    def test_get_metadata(self, generator):
        """Test getting metadata returns a copy."""
        # Add some metadata
        metadata = DiagramMetadata(
            title="Test Diagram",
            description="Test description",
            diagram_type="system_context",
            last_updated=datetime.now(),
            file_path="test.json"
        )
        generator._metadata.append(metadata)
        
        result = generator.get_metadata()
        
        assert len(result) == 1
        assert result[0] == metadata
        assert result is not generator._metadata  # Should be a copy
    
    def test_validate_export_data_valid_json(self, generator):
        """Test validation of valid JSON export data."""
        valid_data = {
            "workspace": {
                "name": "Test",
                "description": "Test desc",
                "version": "1.0.0",
                "author": "Test Author",
                "lastUpdated": "2023-01-01T12:00:00"
            },
            "model": {},
            "views": {},
            "metadata": {
                "diagrams": [
                    {
                        "title": "Test Diagram",
                        "description": "Test desc",
                        "type": "system_context",
                        "lastUpdated": "2023-01-01T12:00:00",
                        "filePath": "test.json"
                    }
                ],
                "generatedAt": "2023-01-01T12:00:00"
            },
            "rawWorkspace": {}
        }
        
        json_data = json.dumps(valid_data)
        result = generator.validate_export_data(json_data)
        
        assert result is True
    
    def test_validate_export_data_invalid_json(self, generator):
        """Test validation of invalid JSON format."""
        invalid_json = "{ invalid json"
        
        with pytest.raises(ValueError, match="Invalid JSON format"):
            generator.validate_export_data(invalid_json)
    
    def test_validate_export_data_missing_keys(self, generator):
        """Test validation with missing required keys."""
        incomplete_data = {
            "workspace": {},
            "model": {}
            # Missing required keys
        }
        
        json_data = json.dumps(incomplete_data)
        
        with pytest.raises(ValueError, match="Missing required key"):
            generator.validate_export_data(json_data)
    
    def test_validate_export_data_invalid_diagram_type(self, generator):
        """Test validation with invalid diagram type."""
        invalid_data = {
            "workspace": {
                "name": "Test",
                "description": "Test desc",
                "version": "1.0.0",
                "author": "Test Author",
                "lastUpdated": "2023-01-01T12:00:00"
            },
            "model": {},
            "views": {},
            "metadata": {
                "diagrams": [
                    {
                        "title": "Test Diagram",
                        "description": "Test desc",
                        "type": "invalid_type",  # Invalid type
                        "lastUpdated": "2023-01-01T12:00:00",
                        "filePath": "test.json"
                    }
                ],
                "generatedAt": "2023-01-01T12:00:00"
            },
            "rawWorkspace": {}
        }
        
        json_data = json.dumps(invalid_data)
        
        with pytest.raises(ValueError, match="Invalid diagram type"):
            generator.validate_export_data(json_data)
    
    def test_validate_plantuml_output_valid(self, generator):
        """Test validation of valid PlantUML output."""
        valid_plantuml = """
        @startuml
        !title Test Diagram
        Person(user, "User")
        System(system, "System")
        @enduml
        """
        
        result = generator.validate_plantuml_output(valid_plantuml)
        assert result is True
    
    def test_validate_plantuml_output_empty(self, generator):
        """Test validation of empty PlantUML output."""
        with pytest.raises(ValueError, match="PlantUML output is empty"):
            generator.validate_plantuml_output("")
    
    def test_validate_plantuml_output_missing_startuml(self, generator):
        """Test validation of PlantUML output missing @startuml."""
        invalid_plantuml = """
        !title Test Diagram
        Person(user, "User")
        @enduml
        """
        
        with pytest.raises(ValueError, match="Missing @startuml directive"):
            generator.validate_plantuml_output(invalid_plantuml)
    
    def test_validate_plantuml_output_missing_enduml(self, generator):
        """Test validation of PlantUML output missing @enduml."""
        invalid_plantuml = """
        @startuml
        !title Test Diagram
        Person(user, "User")
        """
        
        with pytest.raises(ValueError, match="Missing @enduml directive"):
            generator.validate_plantuml_output(invalid_plantuml)
    
    def test_validate_plantuml_output_insufficient_content(self, generator):
        """Test validation of PlantUML output with insufficient content."""
        minimal_plantuml = """
        @startuml
        !title Test
        @enduml
        """
        
        with pytest.raises(ValueError, match="insufficient content"):
            generator.validate_plantuml_output(minimal_plantuml)
    
    @patch('src.diagrams.generator.Workspace')
    def test_export_json_with_validation_error(self, mock_workspace, generator):
        """Test JSON export that fails validation."""
        # Setup workspace that returns invalid data
        mock_workspace_instance = Mock()
        mock_workspace.return_value = mock_workspace_instance
        mock_workspace_instance.dump.side_effect = Exception("Workspace dump failed")
        
        generator.create_workspace()
        
        with pytest.raises(ValueError, match="Failed to export workspace to JSON"):
            generator.export_to_json()
    
    @patch('src.diagrams.generator.Workspace')
    def test_export_plantuml_with_validation_error(self, mock_workspace, generator):
        """Test PlantUML export that fails validation."""
        # Setup workspace
        mock_workspace_instance = Mock()
        mock_workspace.return_value = mock_workspace_instance
        
        generator.create_workspace()
        
        # Mock datetime to cause an error
        with patch('src.diagrams.generator.datetime') as mock_datetime:
            mock_datetime.now.side_effect = Exception("DateTime error")
            
            with pytest.raises(ValueError, match="Failed to export workspace to PlantUML"):
                generator.export_to_plantuml()
    
    def test_custom_view_keys(self, generator):
        """Test that custom view keys are used when provided."""
        # This test would require mocking the workspace creation
        # and verifying that custom keys are passed correctly
        pass  # Implementation depends on pystructurizr API details
    
    @patch('src.diagrams.generator.Workspace')
    def test_multiple_views_metadata(self, mock_workspace, generator):
        """Test that multiple views create separate metadata entries."""
        # Setup workspace
        mock_workspace_instance = Mock()
        mock_workspace.return_value = mock_workspace_instance
        mock_workspace_instance.SystemContextView.return_value = Mock()
        mock_workspace_instance.ContainerView.return_value = Mock()
        
        generator.create_workspace()
        
        # Setup mocks
        mock_system = Mock()
        mock_system.name = "Test System"
        
        # Add multiple views
        generator.add_system_context_view(mock_system, "Context View", "Context desc")
        generator.add_container_view(mock_system, "Container View", "Container desc")
        
        # Verify metadata
        assert len(generator._metadata) == 2
        assert generator._metadata[0].diagram_type == "system_context"
        assert generator._metadata[1].diagram_type == "container"
        assert generator._metadata[0].title == "Context View"
        assert generator._metadata[1].title == "Container View"