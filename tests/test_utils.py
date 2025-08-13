"""
Unit tests for diagram utility functions and helper classes.

Tests cover configuration loading, element factories, relationship management,
styling utilities, and diagram patterns.
"""

import pytest
import json
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from tempfile import NamedTemporaryFile
import os

from src.diagrams.utils import (
    StyleConfig,
    DiagramPattern,
    ConfigurationLoader,
    ElementFactory,
    RelationshipManager,
    ViewStyler,
    DiagramPatterns,
    load_diagram_config,
    validate_diagram_elements,
    create_elements_from_config
)


class TestStyleConfig:
    """Test cases for StyleConfig dataclass."""
    
    def test_style_config_creation_with_defaults(self):
        """Test creating StyleConfig with default values."""
        config = StyleConfig()
        
        # Check default colors are set
        assert config.colors["person"] == "#08427b"
        assert config.colors["software_system"] == "#1168bd"
        assert config.colors["container"] == "#438dd5"
        assert config.colors["component"] == "#85bbf0"
        assert config.colors["external"] == "#999999"
        
        # Check default shapes are set
        assert config.shapes["person"] == "Person"
        assert config.shapes["software_system"] == "RoundedBox"
        assert config.shapes["container"] == "RoundedBox"
        assert config.shapes["component"] == "Component"
    
    def test_style_config_creation_with_custom_values(self):
        """Test creating StyleConfig with custom values."""
        custom_colors = {"person": "#FF0000", "system": "#00FF00"}
        custom_shapes = {"person": "Circle", "system": "Square"}
        custom_fonts = {"default": "Arial", "title": "Helvetica"}
        
        config = StyleConfig(
            colors=custom_colors,
            shapes=custom_shapes,
            fonts=custom_fonts
        )
        
        assert config.colors == custom_colors
        assert config.shapes == custom_shapes
        assert config.fonts == custom_fonts


class TestDiagramPattern:
    """Test cases for DiagramPattern dataclass."""
    
    def test_diagram_pattern_creation(self):
        """Test creating DiagramPattern with all fields."""
        elements = [
            {"type": "person", "name": "User"},
            {"type": "system", "name": "System"}
        ]
        relationships = [
            {"source": "User", "destination": "System", "description": "Uses"}
        ]
        
        pattern = DiagramPattern(
            name="Test Pattern",
            description="Test pattern description",
            elements=elements,
            relationships=relationships
        )
        
        assert pattern.name == "Test Pattern"
        assert pattern.description == "Test pattern description"
        assert pattern.elements == elements
        assert pattern.relationships == relationships
    
    def test_diagram_pattern_creation_with_defaults(self):
        """Test creating DiagramPattern with default values."""
        pattern = DiagramPattern(
            name="Test Pattern",
            description="Test description"
        )
        
        assert pattern.elements == []
        assert pattern.relationships == []


class TestConfigurationLoader:
    """Test cases for ConfigurationLoader class."""
    
    def test_load_from_yaml_file(self):
        """Test loading configuration from YAML file."""
        yaml_content = """
        name: Test System
        description: Test description
        version: 1.0.0
        author: Test Author
        """
        
        with NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            
            try:
                result = ConfigurationLoader.load_from_file(f.name)
                
                assert result["name"] == "Test System"
                assert result["description"] == "Test description"
                assert result["version"] == "1.0.0"
                assert result["author"] == "Test Author"
            finally:
                os.unlink(f.name)
    
    def test_load_from_json_file(self):
        """Test loading configuration from JSON file."""
        json_content = {
            "name": "Test System",
            "description": "Test description",
            "version": "1.0.0",
            "author": "Test Author"
        }
        
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(json_content, f)
            f.flush()
            
            try:
                result = ConfigurationLoader.load_from_file(f.name)
                
                assert result["name"] == "Test System"
                assert result["description"] == "Test description"
                assert result["version"] == "1.0.0"
                assert result["author"] == "Test Author"
            finally:
                os.unlink(f.name)
    
    def test_load_from_nonexistent_file(self):
        """Test loading from non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            ConfigurationLoader.load_from_file("nonexistent.yml")
    
    def test_load_from_unsupported_format(self):
        """Test loading from unsupported file format raises ValueError."""
        with NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test content")
            f.flush()
            
            try:
                with pytest.raises(ValueError, match="Unsupported file format"):
                    ConfigurationLoader.load_from_file(f.name)
            finally:
                os.unlink(f.name)
    
    def test_load_from_invalid_yaml(self):
        """Test loading invalid YAML raises ValueError."""
        invalid_yaml = """
        name: Test System
        description: Test description
        invalid: [unclosed list
        """
        
        with NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(invalid_yaml)
            f.flush()
            
            try:
                with pytest.raises(ValueError, match="Invalid configuration file format"):
                    ConfigurationLoader.load_from_file(f.name)
            finally:
                os.unlink(f.name)
    
    def test_load_from_invalid_json(self):
        """Test loading invalid JSON raises ValueError."""
        invalid_json = '{"name": "Test", "invalid": json}'
        
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(invalid_json)
            f.flush()
            
            try:
                with pytest.raises(ValueError, match="Invalid configuration file format"):
                    ConfigurationLoader.load_from_file(f.name)
            finally:
                os.unlink(f.name)
    
    def test_validate_config_valid(self):
        """Test validation of valid configuration."""
        valid_config = {
            "name": "Test System",
            "description": "Test description",
            "version": "1.0.0",
            "author": "Test Author"
        }
        
        result = ConfigurationLoader.validate_config(valid_config)
        assert result is True
    
    def test_validate_config_missing_required_field(self):
        """Test validation with missing required field."""
        invalid_config = {
            "description": "Test description"
            # Missing 'name' field
        }
        
        with pytest.raises(ValueError, match="Missing required field: name"):
            ConfigurationLoader.validate_config(invalid_config)
    
    def test_validate_config_invalid_version_type(self):
        """Test validation with invalid version type."""
        invalid_config = {
            "name": "Test System",
            "description": "Test description",
            "version": 1.0  # Should be string
        }
        
        with pytest.raises(ValueError, match="Version must be a string"):
            ConfigurationLoader.validate_config(invalid_config)
    
    def test_validate_config_invalid_author_type(self):
        """Test validation with invalid author type."""
        invalid_config = {
            "name": "Test System",
            "description": "Test description",
            "author": 123  # Should be string
        }
        
        with pytest.raises(ValueError, match="Author must be a string"):
            ConfigurationLoader.validate_config(invalid_config)


class TestElementFactory:
    """Test cases for ElementFactory class."""
    
    @patch('src.diagrams.utils.Person')
    def test_create_person(self, mock_person):
        """Test creating a Person element."""
        mock_person_instance = Mock()
        mock_person.return_value = mock_person_instance
        
        result = ElementFactory.create_person(
            "Test User",
            "A test user",
            "External",
            "user,external"
        )
        
        mock_person.assert_called_once_with("Test User", "A test user")
        assert result == mock_person_instance
    
    @patch('src.diagrams.utils.SoftwareSystem')
    def test_create_software_system(self, mock_system):
        """Test creating a SoftwareSystem element."""
        mock_system_instance = Mock()
        mock_system.return_value = mock_system_instance
        
        result = ElementFactory.create_software_system(
            "Test System",
            "A test system",
            "Internal",
            "system,internal"
        )
        
        mock_system.assert_called_once_with("Test System", "A test system")
        assert result == mock_system_instance
    
    @patch('src.diagrams.utils.Container')
    def test_create_container(self, mock_container):
        """Test creating a Container element."""
        mock_container_instance = Mock()
        mock_container.return_value = mock_container_instance
        mock_system = Mock()
        
        result = ElementFactory.create_container(
            mock_system,
            "Test Container",
            "A test container",
            "Python/Django",
            "container,web"
        )
        
        mock_container.assert_called_once_with("Test Container", "A test container", "Python/Django")
        assert result == mock_container_instance
    
    @patch('src.diagrams.utils.Component')
    def test_create_component(self, mock_component):
        """Test creating a Component element."""
        mock_component_instance = Mock()
        mock_component.return_value = mock_component_instance
        mock_container = Mock()
        
        result = ElementFactory.create_component(
            mock_container,
            "Test Component",
            "A test component",
            "Spring Boot",
            "component,service"
        )
        
        mock_component.assert_called_once_with("Test Component", "A test component", "Spring Boot")
        assert result == mock_component_instance


class TestRelationshipManager:
    """Test cases for RelationshipManager class."""
    
    def test_create_relationship(self):
        """Test creating a relationship between elements."""
        source = Mock()
        source.name = "Source"
        destination = Mock()
        destination.name = "Destination"
        
        result = RelationshipManager.create_relationship(
            source,
            destination,
            "Uses",
            "HTTPS",
            "Synchronous"
        )
        
        assert result["source"] == "Source"
        assert result["destination"] == "Destination"
        assert result["description"] == "Uses"
        assert result["technology"] == "HTTPS"
        assert result["interaction_style"] == "Synchronous"
    
    def test_create_relationship_with_defaults(self):
        """Test creating a relationship with default values."""
        source = Mock()
        source.name = "Source"
        destination = Mock()
        destination.name = "Destination"
        
        result = RelationshipManager.create_relationship(
            source,
            destination,
            "Uses"
        )
        
        assert result["source"] == "Source"
        assert result["destination"] == "Destination"
        assert result["description"] == "Uses"
        assert result["technology"] == ""
        assert result["interaction_style"] == "Synchronous"
    
    def test_add_common_relationships(self):
        """Test adding multiple relationships from patterns."""
        # Create mock elements
        user = Mock()
        user.name = "User"
        system = Mock()
        system.name = "System"
        
        elements = {
            "User": user,
            "System": system
        }
        
        patterns = [
            {
                "source": "User",
                "destination": "System",
                "description": "Uses",
                "technology": "HTTPS"
            },
            {
                "source": "System",
                "destination": "User",
                "description": "Responds to"
            }
        ]
        
        result = RelationshipManager.add_common_relationships(elements, patterns)
        
        assert len(result) == 2
        assert result[0]["source"] == "User"
        assert result[0]["destination"] == "System"
        assert result[0]["description"] == "Uses"
        assert result[0]["technology"] == "HTTPS"
        
        assert result[1]["source"] == "System"
        assert result[1]["destination"] == "User"
        assert result[1]["description"] == "Responds to"
    
    def test_add_common_relationships_missing_elements(self):
        """Test adding relationships when some elements are missing."""
        elements = {"User": Mock()}
        
        patterns = [
            {
                "source": "User",
                "destination": "NonExistentSystem",
                "description": "Uses"
            }
        ]
        
        result = RelationshipManager.add_common_relationships(elements, patterns)
        
        assert len(result) == 0  # No relationships created due to missing element


class TestViewStyler:
    """Test cases for ViewStyler class."""
    
    def test_apply_default_styles(self):
        """Test applying default styles to a view."""
        mock_view = Mock()
        
        ViewStyler.apply_default_styles(mock_view)
        
        # Check that style config was stored
        assert hasattr(mock_view, '_style_config')
        assert isinstance(mock_view._style_config, StyleConfig)
    
    def test_apply_default_styles_with_custom_config(self):
        """Test applying custom style config to a view."""
        mock_view = Mock()
        custom_config = StyleConfig(colors={"person": "#FF0000"})
        
        ViewStyler.apply_default_styles(mock_view, custom_config)
        
        assert mock_view._style_config == custom_config
    
    def test_apply_custom_theme_corporate(self):
        """Test applying corporate theme."""
        mock_view = Mock()
        
        ViewStyler.apply_custom_theme(mock_view, "corporate")
        
        assert hasattr(mock_view, '_style_config')
        assert mock_view._style_config.colors["person"] == "#2E4057"
        assert mock_view._style_config.colors["software_system"] == "#048A81"
    
    def test_apply_custom_theme_modern(self):
        """Test applying modern theme."""
        mock_view = Mock()
        
        ViewStyler.apply_custom_theme(mock_view, "modern")
        
        assert hasattr(mock_view, '_style_config')
        assert mock_view._style_config.colors["person"] == "#6C5CE7"
        assert mock_view._style_config.colors["software_system"] == "#A29BFE"
    
    def test_apply_custom_theme_minimal(self):
        """Test applying minimal theme."""
        mock_view = Mock()
        
        ViewStyler.apply_custom_theme(mock_view, "minimal")
        
        assert hasattr(mock_view, '_style_config')
        assert mock_view._style_config.colors["person"] == "#2D3436"
        assert mock_view._style_config.colors["software_system"] == "#636E72"
    
    def test_apply_unknown_theme(self):
        """Test applying unknown theme does nothing."""
        mock_view = Mock()
        
        # Remove any existing _style_config attribute
        if hasattr(mock_view, '_style_config'):
            delattr(mock_view, '_style_config')
        
        ViewStyler.apply_custom_theme(mock_view, "unknown_theme")
        
        # Should not have style config since theme doesn't exist
        assert not hasattr(mock_view, '_style_config')


class TestDiagramPatterns:
    """Test cases for DiagramPatterns class."""
    
    def test_get_microservices_pattern(self):
        """Test getting microservices pattern."""
        pattern = DiagramPatterns.get_microservices_pattern()
        
        assert pattern.name == "Microservices"
        assert pattern.description == "Common microservices architecture pattern"
        assert len(pattern.elements) == 5
        assert len(pattern.relationships) == 5
        
        # Check specific elements
        element_names = [e["name"] for e in pattern.elements]
        assert "User" in element_names
        assert "API Gateway" in element_names
        assert "Service A" in element_names
        assert "Service B" in element_names
        assert "Database" in element_names
    
    def test_get_web_application_pattern(self):
        """Test getting web application pattern."""
        pattern = DiagramPatterns.get_web_application_pattern()
        
        assert pattern.name == "Web Application"
        assert pattern.description == "Traditional web application pattern"
        assert len(pattern.elements) == 4
        assert len(pattern.relationships) == 3
        
        # Check specific elements
        element_names = [e["name"] for e in pattern.elements]
        assert "User" in element_names
        assert "Web Application" in element_names
        assert "Database" in element_names
        assert "Email System" in element_names


class TestUtilityFunctions:
    """Test cases for utility functions."""
    
    @patch('src.diagrams.utils.ConfigurationLoader.load_from_file')
    def test_load_diagram_config_success(self, mock_load):
        """Test successful loading of diagram configuration."""
        expected_config = {
            "name": "Test System",
            "description": "Test description"
        }
        mock_load.return_value = expected_config
        
        result = load_diagram_config("test_config.yml")
        
        mock_load.assert_called_once_with("test_config.yml")
        assert result == expected_config
    
    @patch('src.diagrams.utils.ConfigurationLoader.load_from_file')
    def test_load_diagram_config_file_not_found(self, mock_load):
        """Test loading diagram config when file not found returns defaults."""
        mock_load.side_effect = FileNotFoundError()
        
        result = load_diagram_config("nonexistent.yml")
        
        # Should return default configuration
        assert result["name"] == "Architecture Diagrams"
        assert result["description"] == "System architecture documentation"
        assert result["version"] == "1.0.0"
        assert result["author"] == "Architecture Team"
        assert result["output_formats"] == ["json", "plantuml"]
    
    def test_validate_diagram_elements_valid(self):
        """Test validation of valid diagram elements."""
        valid_elements = [
            {"type": "person", "name": "User", "description": "System user"},
            {"type": "system", "name": "System", "description": "Main system"},
            {"type": "container", "name": "Web App", "description": "Web application"},
            {"type": "component", "name": "Controller", "description": "REST controller"}
        ]
        
        result = validate_diagram_elements(valid_elements)
        assert result is True
    
    def test_validate_diagram_elements_missing_type(self):
        """Test validation with missing type field."""
        invalid_elements = [
            {"name": "User", "description": "System user"}  # Missing 'type'
        ]
        
        with pytest.raises(ValueError, match="Element 0: Missing required field 'type'"):
            validate_diagram_elements(invalid_elements)
    
    def test_validate_diagram_elements_missing_name(self):
        """Test validation with missing name field."""
        invalid_elements = [
            {"type": "person", "description": "System user"}  # Missing 'name'
        ]
        
        with pytest.raises(ValueError, match="Element 0: Missing required field 'name'"):
            validate_diagram_elements(invalid_elements)
    
    def test_validate_diagram_elements_invalid_type(self):
        """Test validation with invalid element type."""
        invalid_elements = [
            {"type": "invalid_type", "name": "User"}
        ]
        
        with pytest.raises(ValueError, match="Element 0: Invalid type 'invalid_type'"):
            validate_diagram_elements(invalid_elements)
    
    def test_create_elements_from_config(self):
        """Test creating elements from configuration."""
        mock_model = Mock()
        mock_person = Mock()
        mock_system = Mock()
        mock_model.add_person.return_value = mock_person
        mock_model.add_software_system.return_value = mock_system
        
        config = [
            {
                "type": "person",
                "name": "User",
                "description": "System user",
                "location": "External",
                "tags": "user,external"
            },
            {
                "type": "system",
                "name": "System",
                "description": "Main system",
                "location": "Internal",
                "tags": "system,internal"
            },
            {
                "type": "container",  # Should be skipped
                "name": "Container",
                "description": "Container"
            }
        ]
        
        result = create_elements_from_config(config, mock_model)
        
        # Should create person and system, skip container
        assert len(result) == 2
        assert "User" in result
        assert "System" in result
        assert result["User"] == mock_person
        assert result["System"] == mock_system
        
        # Verify model calls
        mock_model.add_person.assert_called_once_with("User", "System user")
        mock_model.add_software_system.assert_called_once_with("System", "Main system")
        
        # Verify attributes were set
        assert mock_person.location == "External"
        assert mock_person.tags == "user,external"
        assert mock_system.location == "Internal"
        assert mock_system.tags == "system,internal"
    
    def test_create_elements_from_config_empty(self):
        """Test creating elements from empty configuration."""
        mock_model = Mock()
        
        result = create_elements_from_config([], mock_model)
        
        assert result == {}
        mock_model.add_person.assert_not_called()
        mock_model.add_software_system.assert_not_called()