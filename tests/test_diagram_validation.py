"""
Tests for diagram validation functionality.

This module tests the validation capabilities for diagram definitions,
elements, relationships, and export data to ensure proper error handling
and informative error messages.
"""

import pytest
import json
from datetime import datetime
from unittest.mock import Mock, patch

from src.diagrams.generator import DiagramGenerator, DiagramConfig
from src.diagrams.utils import (
    validate_diagram_elements,
    validate_diagram_relationships,
    validate_diagram_definition,
    DiagramValidator
)


class TestDiagramElementValidation:
    """Test validation of diagram elements."""
    
    def test_valid_elements(self):
        """Test validation of valid element definitions."""
        elements = [
            {"type": "person", "name": "User", "description": "End user"},
            {"type": "system", "name": "App", "description": "Main application"},
            {"type": "container", "name": "Database", "description": "Data storage"},
            {"type": "component", "name": "Controller", "description": "API controller"}
        ]
        
        assert validate_diagram_elements(elements) is True
    
    def test_empty_elements_list(self):
        """Test validation fails for empty elements list."""
        with pytest.raises(ValueError, match="Elements list cannot be empty"):
            validate_diagram_elements([])
    
    def test_missing_required_fields(self):
        """Test validation fails for missing required fields."""
        elements = [{"type": "person"}]  # Missing 'name'
        
        with pytest.raises(ValueError, match="Missing required field 'name'"):
            validate_diagram_elements(elements)
    
    def test_empty_required_fields(self):
        """Test validation fails for empty required fields."""
        elements = [{"type": "person", "name": ""}]  # Empty name
        
        with pytest.raises(ValueError, match="Field 'name' cannot be empty"):
            validate_diagram_elements(elements)
    
    def test_invalid_element_type(self):
        """Test validation fails for invalid element types."""
        elements = [{"type": "invalid", "name": "Test"}]
        
        with pytest.raises(ValueError, match="Invalid type 'invalid'"):
            validate_diagram_elements(elements)
    
    def test_non_dict_element(self):
        """Test validation fails for non-dictionary elements."""
        elements = ["not a dict"]
        
        with pytest.raises(ValueError, match="Must be a dictionary"):
            validate_diagram_elements(elements)
    
    def test_invalid_description_type(self):
        """Test validation fails for non-string descriptions."""
        elements = [{"type": "person", "name": "User", "description": 123}]
        
        with pytest.raises(ValueError, match="Description must be a string"):
            validate_diagram_elements(elements)


class TestDiagramRelationshipValidation:
    """Test validation of diagram relationships."""
    
    def test_valid_relationships(self):
        """Test validation of valid relationship definitions."""
        relationships = [
            {"source": "User", "destination": "System", "description": "Uses"},
            {"source": "System", "destination": "Database", "description": "Stores data", "technology": "SQL"}
        ]
        element_names = ["User", "System", "Database"]
        
        assert validate_diagram_relationships(relationships, element_names) is True
    
    def test_empty_relationships_list(self):
        """Test validation passes for empty relationships list."""
        assert validate_diagram_relationships([], ["User"]) is True
    
    def test_missing_required_fields(self):
        """Test validation fails for missing required fields."""
        relationships = [{"source": "User", "destination": "System"}]  # Missing 'description'
        element_names = ["User", "System"]
        
        with pytest.raises(ValueError, match="Missing required field 'description'"):
            validate_diagram_relationships(relationships, element_names)
    
    def test_empty_required_fields(self):
        """Test validation fails for empty required fields."""
        relationships = [{"source": "User", "destination": "System", "description": ""}]
        element_names = ["User", "System"]
        
        with pytest.raises(ValueError, match="Field 'description' cannot be empty"):
            validate_diagram_relationships(relationships, element_names)
    
    def test_invalid_source_element(self):
        """Test validation fails for invalid source element."""
        relationships = [{"source": "Invalid", "destination": "System", "description": "Uses"}]
        element_names = ["User", "System"]
        
        with pytest.raises(ValueError, match="Source 'Invalid' not found in elements"):
            validate_diagram_relationships(relationships, element_names)
    
    def test_invalid_destination_element(self):
        """Test validation fails for invalid destination element."""
        relationships = [{"source": "User", "destination": "Invalid", "description": "Uses"}]
        element_names = ["User", "System"]
        
        with pytest.raises(ValueError, match="Destination 'Invalid' not found in elements"):
            validate_diagram_relationships(relationships, element_names)
    
    def test_self_referencing_relationship(self):
        """Test validation fails for self-referencing relationships."""
        relationships = [{"source": "User", "destination": "User", "description": "Self-reference"}]
        element_names = ["User"]
        
        with pytest.raises(ValueError, match="Source and destination cannot be the same element"):
            validate_diagram_relationships(relationships, element_names)
    
    def test_non_dict_relationship(self):
        """Test validation fails for non-dictionary relationships."""
        relationships = ["not a dict"]
        element_names = ["User"]
        
        with pytest.raises(ValueError, match="Must be a dictionary"):
            validate_diagram_relationships(relationships, element_names)
    
    def test_invalid_technology_type(self):
        """Test validation fails for non-string technology."""
        relationships = [{"source": "User", "destination": "System", "description": "Uses", "technology": 123}]
        element_names = ["User", "System"]
        
        with pytest.raises(ValueError, match="Technology must be a string"):
            validate_diagram_relationships(relationships, element_names)


class TestDiagramDefinitionValidation:
    """Test validation of complete diagram definitions."""
    
    def test_valid_diagram_definition(self):
        """Test validation of valid diagram definition."""
        diagram_def = {
            "name": "System Context",
            "description": "High-level system view",
            "type": "system_context",
            "elements": [
                {"type": "person", "name": "User", "description": "End user"},
                {"type": "system", "name": "App", "description": "Main app"}
            ],
            "relationships": [
                {"source": "User", "destination": "App", "description": "Uses"}
            ]
        }
        
        assert validate_diagram_definition(diagram_def) is True
    
    def test_non_dict_diagram_definition(self):
        """Test validation fails for non-dictionary diagram definition."""
        with pytest.raises(ValueError, match="Diagram definition must be a dictionary"):
            validate_diagram_definition("not a dict")
    
    def test_missing_required_fields(self):
        """Test validation fails for missing required fields."""
        diagram_def = {"name": "Test"}  # Missing 'description' and 'elements'
        
        with pytest.raises(ValueError, match="Missing required field"):
            validate_diagram_definition(diagram_def)
    
    def test_empty_required_fields(self):
        """Test validation fails for empty required fields."""
        diagram_def = {
            "name": "",
            "description": "Test",
            "elements": []
        }
        
        with pytest.raises(ValueError, match="Field 'name' cannot be empty"):
            validate_diagram_definition(diagram_def)
    
    def test_invalid_elements_type(self):
        """Test validation fails for non-list elements."""
        diagram_def = {
            "name": "Test",
            "description": "Test",
            "elements": "not a list"
        }
        
        with pytest.raises(ValueError, match="Elements must be a list"):
            validate_diagram_definition(diagram_def)
    
    def test_invalid_relationships_type(self):
        """Test validation fails for non-list relationships."""
        diagram_def = {
            "name": "Test",
            "description": "Test",
            "elements": [{"type": "person", "name": "User"}],
            "relationships": "not a list"
        }
        
        with pytest.raises(ValueError, match="Relationships must be a list"):
            validate_diagram_definition(diagram_def)
    
    def test_invalid_diagram_type(self):
        """Test validation fails for invalid diagram type."""
        diagram_def = {
            "name": "Test",
            "description": "Test",
            "type": "invalid_type",
            "elements": [{"type": "person", "name": "User"}]
        }
        
        with pytest.raises(ValueError, match="Invalid diagram type"):
            validate_diagram_definition(diagram_def)


class TestDiagramValidator:
    """Test the comprehensive DiagramValidator class."""
    
    def test_valid_diagram_structure(self):
        """Test validation of valid diagram structure."""
        validator = DiagramValidator()
        diagram_def = {
            "name": "System Context",
            "description": "High-level system view",
            "elements": [
                {"type": "person", "name": "User", "description": "End user"},
                {"type": "system", "name": "App", "description": "Main app"}
            ],
            "relationships": [
                {"source": "User", "destination": "App", "description": "Uses"}
            ]
        }
        
        assert validator.validate_diagram_structure(diagram_def) is True
        assert len(validator.errors) == 0
    
    def test_invalid_diagram_structure(self):
        """Test validation of invalid diagram structure."""
        validator = DiagramValidator()
        diagram_def = {
            "name": "",  # Empty name
            "description": "Test",
            "elements": [{"type": "person", "name": "User"}]
        }
        
        assert validator.validate_diagram_structure(diagram_def) is False
        assert len(validator.errors) > 0
    
    def test_isolated_elements_warning(self):
        """Test warning for isolated elements."""
        validator = DiagramValidator()
        diagram_def = {
            "name": "Test",
            "description": "Test",
            "elements": [
                {"type": "person", "name": "User", "description": "User"},
                {"type": "system", "name": "App", "description": "App"},
                {"type": "system", "name": "Isolated", "description": "Isolated system"}
            ],
            "relationships": [
                {"source": "User", "destination": "App", "description": "Uses"}
            ]
        }
        
        validator.validate_diagram_structure(diagram_def)
        assert any("Isolated elements" in warning for warning in validator.warnings)
    
    def test_missing_descriptions_warning(self):
        """Test warning for missing descriptions."""
        validator = DiagramValidator()
        diagram_def = {
            "name": "Test",
            "description": "Test",
            "elements": [
                {"type": "person", "name": "User"},  # Missing description
                {"type": "system", "name": "App", "description": "App"}
            ]
        }
        
        validator.validate_diagram_structure(diagram_def)
        assert any("missing descriptions" in warning for warning in validator.warnings)
    
    def test_large_diagram_warning(self):
        """Test warning for large number of elements."""
        validator = DiagramValidator()
        elements = [
            {"type": "system", "name": f"System{i}", "description": f"System {i}"}
            for i in range(25)  # More than 20 elements
        ]
        diagram_def = {
            "name": "Large Diagram",
            "description": "Test",
            "elements": elements
        }
        
        validator.validate_diagram_structure(diagram_def)
        assert any("Large number of elements" in warning for warning in validator.warnings)
    
    def test_duplicate_element_names_error(self):
        """Test error for duplicate element names."""
        validator = DiagramValidator()
        diagram_def = {
            "name": "Test",
            "description": "Test",
            "elements": [
                {"type": "person", "name": "User", "description": "User 1"},
                {"type": "system", "name": "User", "description": "User 2"}  # Duplicate name
            ]
        }
        
        validator.validate_diagram_structure(diagram_def)
        assert any("Duplicate element names" in error for error in validator.errors)
    
    def test_no_people_warning(self):
        """Test warning for no people/actors."""
        validator = DiagramValidator()
        diagram_def = {
            "name": "Test",
            "description": "Test",
            "elements": [
                {"type": "system", "name": "App1", "description": "App 1"},
                {"type": "system", "name": "App2", "description": "App 2"}
            ]
        }
        
        validator.validate_diagram_structure(diagram_def)
        assert any("No people/actors defined" in warning for warning in validator.warnings)
    
    def test_validation_report(self):
        """Test validation report generation."""
        validator = DiagramValidator()
        diagram_def = {
            "name": "",  # This will cause an error
            "description": "Test",
            "elements": [
                {"type": "system", "name": "App", "description": "App"}  # No people - warning
            ]
        }
        
        validator.validate_diagram_structure(diagram_def)
        report = validator.get_validation_report()
        
        assert "valid" in report
        assert "errors" in report
        assert "warnings" in report
        assert "error_count" in report
        assert "warning_count" in report
        assert report["valid"] is False
        assert report["error_count"] > 0


class TestDiagramGeneratorValidation:
    """Test validation in DiagramGenerator class."""
    
    def test_workspace_validation_success(self):
        """Test successful workspace validation."""
        config = DiagramConfig(
            name="Test System",
            description="Test system description"
        )
        generator = DiagramGenerator(config)
        generator.create_workspace()
        
        # Add a mock diagram metadata
        from src.diagrams.generator import DiagramMetadata
        metadata = DiagramMetadata(
            title="Test Diagram",
            description="Test description",
            diagram_type="system_context",
            last_updated=datetime.now(),
            file_path="test.json"
        )
        generator._metadata.append(metadata)
        
        # Should not raise an exception
        generator.validate_workspace()
    
    def test_workspace_validation_no_workspace(self):
        """Test workspace validation fails when no workspace created."""
        config = DiagramConfig(name="Test", description="Test")
        generator = DiagramGenerator(config)
        
        with pytest.raises(ValueError, match="Workspace has not been created"):
            generator.validate_workspace()
    
    def test_workspace_validation_empty_name(self):
        """Test workspace validation fails for empty name."""
        config = DiagramConfig(name="", description="Test")
        generator = DiagramGenerator(config)
        generator.create_workspace()
        
        with pytest.raises(ValueError, match="Workspace name cannot be empty"):
            generator.validate_workspace()
    
    def test_workspace_validation_empty_description(self):
        """Test workspace validation fails for empty description."""
        config = DiagramConfig(name="Test", description="")
        generator = DiagramGenerator(config)
        generator.create_workspace()
        
        with pytest.raises(ValueError, match="Workspace description cannot be empty"):
            generator.validate_workspace()
    
    def test_workspace_validation_no_diagrams(self):
        """Test workspace validation fails when no diagrams exist."""
        config = DiagramConfig(name="Test", description="Test")
        generator = DiagramGenerator(config)
        generator.create_workspace()
        
        with pytest.raises(ValueError, match="Workspace must contain at least one diagram"):
            generator.validate_workspace()
    
    def test_json_export_validation_success(self):
        """Test successful JSON export validation."""
        config = DiagramConfig(name="Test", description="Test")
        generator = DiagramGenerator(config)
        
        valid_json = json.dumps({
            "workspace": {
                "name": "Test System",
                "description": "Test description",
                "version": "1.0.0",
                "author": "Test Author",
                "lastUpdated": datetime.now().isoformat()
            },
            "model": {},
            "views": {},
            "metadata": {
                "diagrams": [
                    {
                        "title": "Test Diagram",
                        "description": "Test description",
                        "type": "system_context",
                        "lastUpdated": datetime.now().isoformat(),
                        "filePath": "test.json"
                    }
                ],
                "generatedAt": datetime.now().isoformat()
            },
            "rawWorkspace": {}
        })
        
        # Should not raise an exception
        generator.validate_export_data(valid_json)
    
    def test_json_export_validation_invalid_json(self):
        """Test JSON export validation fails for invalid JSON."""
        config = DiagramConfig(name="Test", description="Test")
        generator = DiagramGenerator(config)
        
        with pytest.raises(ValueError, match="Invalid JSON format"):
            generator.validate_export_data("invalid json")
    
    def test_json_export_validation_missing_sections(self):
        """Test JSON export validation fails for missing sections."""
        config = DiagramConfig(name="Test", description="Test")
        generator = DiagramGenerator(config)
        
        invalid_json = json.dumps({"workspace": {}})  # Missing other sections
        
        with pytest.raises(ValueError, match="Missing required key"):
            generator.validate_export_data(invalid_json)
    
    def test_plantuml_validation_success(self):
        """Test successful PlantUML validation."""
        config = DiagramConfig(name="Test", description="Test")
        generator = DiagramGenerator(config)
        
        valid_plantuml = """@startuml
!title Test Diagram
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml
Person(user, "User", "End user")
System(app, "App", "Main application")
Rel(user, app, "Uses")
@enduml"""
        
        # Should not raise an exception
        generator.validate_plantuml_output(valid_plantuml)
    
    def test_plantuml_validation_empty_output(self):
        """Test PlantUML validation fails for empty output."""
        config = DiagramConfig(name="Test", description="Test")
        generator = DiagramGenerator(config)
        
        with pytest.raises(ValueError, match="PlantUML output is empty"):
            generator.validate_plantuml_output("")
    
    def test_plantuml_validation_missing_start(self):
        """Test PlantUML validation fails for missing @startuml."""
        config = DiagramConfig(name="Test", description="Test")
        generator = DiagramGenerator(config)
        
        invalid_plantuml = "Person(user, 'User')\n@enduml"
        
        with pytest.raises(ValueError, match="Missing @startuml directive"):
            generator.validate_plantuml_output(invalid_plantuml)
    
    def test_plantuml_validation_missing_end(self):
        """Test PlantUML validation fails for missing @enduml."""
        config = DiagramConfig(name="Test", description="Test")
        generator = DiagramGenerator(config)
        
        invalid_plantuml = "@startuml\nPerson(user, 'User')"
        
        with pytest.raises(ValueError, match="Missing @enduml directive"):
            generator.validate_plantuml_output(invalid_plantuml)
    
    def test_plantuml_validation_no_content(self):
        """Test PlantUML validation fails for no content."""
        config = DiagramConfig(name="Test", description="Test")
        generator = DiagramGenerator(config)
        
        empty_plantuml = "@startuml\n!title Test\n@enduml"
        
        with pytest.raises(ValueError, match="PlantUML output appears to have insufficient content"):
            generator.validate_plantuml_output(empty_plantuml)


if __name__ == "__main__":
    pytest.main([__file__])