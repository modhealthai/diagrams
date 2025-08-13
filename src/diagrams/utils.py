"""
Utility functions and helpers for diagram generation.

This module provides helper functions for common diagram patterns, styling,
element creation, relationship management, and configuration handling.
"""

from typing import Dict, List, Optional, Any, Union
import yaml
import json
from pathlib import Path
from dataclasses import dataclass, field

from pystructurizr.dsl import Person, SoftwareSystem, Container, Component


@dataclass
class StyleConfig:
    """Configuration for diagram styling."""
    colors: Dict[str, str] = field(default_factory=dict)
    shapes: Dict[str, str] = field(default_factory=dict)
    fonts: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        # Set default colors if not provided
        if not self.colors:
            self.colors = {
                "person": "#08427b",
                "software_system": "#1168bd",
                "container": "#438dd5",
                "component": "#85bbf0",
                "external": "#999999"
            }
        
        # Set default shapes if not provided
        if not self.shapes:
            self.shapes = {
                "person": "Person",
                "software_system": "RoundedBox",
                "container": "RoundedBox",
                "component": "Component"
            }


@dataclass
class DiagramPattern:
    """Common diagram pattern configuration."""
    name: str
    description: str
    elements: List[Dict[str, Any]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)


class ConfigurationLoader:
    """Handles loading and validation of diagram configurations."""
    
    @staticmethod
    def load_from_file(file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load configuration from YAML or JSON file.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            Dictionary containing configuration data
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            ValueError: If the file format is not supported or invalid
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                if path.suffix.lower() in ['.yml', '.yaml']:
                    return yaml.safe_load(f) or {}
                elif path.suffix.lower() == '.json':
                    return json.load(f)
                else:
                    raise ValueError(f"Unsupported file format: {path.suffix}")
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid configuration file format: {e}")
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> bool:
        """
        Validate configuration structure.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        required_fields = ['name', 'description']
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate optional fields
        if 'version' in config and not isinstance(config['version'], str):
            raise ValueError("Version must be a string")
        
        if 'author' in config and not isinstance(config['author'], str):
            raise ValueError("Author must be a string")
        
        return True


class ElementFactory:
    """Factory class for creating diagram elements with consistent patterns."""
    
    @staticmethod
    def create_person(
        name: str,
        description: str = "",
        location: str = "External",
        tags: str = ""
    ) -> Person:
        """
        Create a Person element with standard configuration.
        
        Args:
            name: Name of the person
            description: Description of the person's role
            location: Location (Internal/External)
            tags: Comma-separated tags
            
        Returns:
            Configured Person instance
        """
        # Using pystructurizr DSL API
        person = Person(name, description)
        return person
    
    @staticmethod
    def create_software_system(
        name: str,
        description: str = "",
        location: str = "Internal",
        tags: str = ""
    ) -> SoftwareSystem:
        """
        Create a SoftwareSystem element with standard configuration.
        
        Args:
            name: Name of the software system
            description: Description of the system
            location: Location (Internal/External)
            tags: Comma-separated tags
            
        Returns:
            Configured SoftwareSystem instance
        """
        # Using pystructurizr DSL API
        system = SoftwareSystem(name, description)
        return system
    
    @staticmethod
    def create_container(
        software_system: SoftwareSystem,
        name: str,
        description: str = "",
        technology: str = "",
        tags: str = ""
    ) -> Container:
        """
        Create a Container element with standard configuration.
        
        Args:
            software_system: Parent software system
            name: Name of the container
            description: Description of the container
            technology: Technology stack used
            tags: Comma-separated tags
            
        Returns:
            Configured Container instance
        """
        # Using pystructurizr DSL API
        container = Container(name, description, technology)
        return container
    
    @staticmethod
    def create_component(
        container: Container,
        name: str,
        description: str = "",
        technology: str = "",
        tags: str = ""
    ) -> Component:
        """
        Create a Component element with standard configuration.
        
        Args:
            container: Parent container
            name: Name of the component
            description: Description of the component
            technology: Technology/framework used
            tags: Comma-separated tags
            
        Returns:
            Configured Component instance
        """
        # Using pystructurizr DSL API
        component = Component(name, description, technology)
        return component


class RelationshipManager:
    """Manages relationships between diagram elements."""
    
    @staticmethod
    def create_relationship(
        source: Union[Person, SoftwareSystem, Container, Component],
        destination: Union[Person, SoftwareSystem, Container, Component],
        description: str,
        technology: str = "",
        interaction_style: str = "Synchronous"
    ) -> Dict[str, Any]:
        """
        Create a relationship between two elements.
        
        Args:
            source: Source element
            destination: Destination element
            description: Description of the relationship
            technology: Technology used for the relationship
            interaction_style: Style of interaction (Synchronous/Asynchronous)
            
        Returns:
            Dictionary representing the relationship
        """
        # Return a simple relationship representation
        # The actual implementation would depend on pystructurizr DSL capabilities
        return {
            "source": source.name if hasattr(source, 'name') else str(source),
            "destination": destination.name if hasattr(destination, 'name') else str(destination),
            "description": description,
            "technology": technology,
            "interaction_style": interaction_style
        }
    
    @staticmethod
    def add_common_relationships(
        elements: Dict[str, Union[Person, SoftwareSystem, Container, Component]],
        patterns: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Add multiple relationships based on common patterns.
        
        Args:
            elements: Dictionary of element names to element instances
            patterns: List of relationship patterns with source, destination, description
            
        Returns:
            List of created relationships
        """
        relationships = []
        
        for pattern in patterns:
            source_name = pattern.get('source')
            dest_name = pattern.get('destination')
            description = pattern.get('description', '')
            technology = pattern.get('technology', '')
            
            if source_name in elements and dest_name in elements:
                relationship = RelationshipManager.create_relationship(
                    source=elements[source_name],
                    destination=elements[dest_name],
                    description=description,
                    technology=technology
                )
                relationships.append(relationship)
        
        return relationships


class ViewStyler:
    """Applies consistent styling to diagram views."""
    
    @staticmethod
    def apply_default_styles(
        view: Any,
        style_config: Optional[StyleConfig] = None
    ) -> None:
        """
        Apply default styling to a view.
        
        Args:
            view: View to style
            style_config: Optional custom style configuration
        """
        if style_config is None:
            style_config = StyleConfig()
        
        # Store style configuration for later use
        # The actual styling implementation would depend on pystructurizr DSL capabilities
        view._style_config = style_config
    
    @staticmethod
    def apply_custom_theme(
        view: Any,
        theme_name: str
    ) -> None:
        """
        Apply a predefined theme to a view.
        
        Args:
            view: View to style
            theme_name: Name of the theme to apply
        """
        themes = {
            "corporate": StyleConfig(
                colors={
                    "person": "#2E4057",
                    "software_system": "#048A81",
                    "container": "#54C6EB",
                    "component": "#A8E6CF",
                    "external": "#8B8B8B"
                }
            ),
            "modern": StyleConfig(
                colors={
                    "person": "#6C5CE7",
                    "software_system": "#A29BFE",
                    "container": "#74B9FF",
                    "component": "#81ECEC",
                    "external": "#B2BEC3"
                }
            ),
            "minimal": StyleConfig(
                colors={
                    "person": "#2D3436",
                    "software_system": "#636E72",
                    "container": "#B2BEC3",
                    "component": "#DDD",
                    "external": "#74B9FF"
                }
            )
        }
        
        if theme_name in themes:
            ViewStyler.apply_default_styles(view, themes[theme_name])


class DiagramPatterns:
    """Common diagram patterns and templates."""
    
    @staticmethod
    def get_microservices_pattern() -> DiagramPattern:
        """Get a microservices architecture pattern."""
        return DiagramPattern(
            name="Microservices",
            description="Common microservices architecture pattern",
            elements=[
                {"type": "person", "name": "User", "description": "System user"},
                {"type": "system", "name": "API Gateway", "description": "Routes requests"},
                {"type": "system", "name": "Service A", "description": "Business service"},
                {"type": "system", "name": "Service B", "description": "Business service"},
                {"type": "system", "name": "Database", "description": "Data storage", "location": "External"}
            ],
            relationships=[
                {"source": "User", "destination": "API Gateway", "description": "Makes requests"},
                {"source": "API Gateway", "destination": "Service A", "description": "Routes to"},
                {"source": "API Gateway", "destination": "Service B", "description": "Routes to"},
                {"source": "Service A", "destination": "Database", "description": "Reads/writes"},
                {"source": "Service B", "destination": "Database", "description": "Reads/writes"}
            ]
        )
    
    @staticmethod
    def get_web_application_pattern() -> DiagramPattern:
        """Get a web application architecture pattern."""
        return DiagramPattern(
            name="Web Application",
            description="Traditional web application pattern",
            elements=[
                {"type": "person", "name": "User", "description": "Web user"},
                {"type": "system", "name": "Web Application", "description": "Main application"},
                {"type": "system", "name": "Database", "description": "Data storage"},
                {"type": "system", "name": "Email System", "description": "Email service", "location": "External"}
            ],
            relationships=[
                {"source": "User", "destination": "Web Application", "description": "Uses"},
                {"source": "Web Application", "destination": "Database", "description": "Stores data"},
                {"source": "Web Application", "destination": "Email System", "description": "Sends emails"}
            ]
        )


def load_diagram_config(config_path: str = "diagram_config.yml") -> Dict[str, Any]:
    """
    Load diagram configuration from file with fallback to defaults.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        return ConfigurationLoader.load_from_file(config_path)
    except FileNotFoundError:
        # Return default configuration
        return {
            "name": "Architecture Diagrams",
            "description": "System architecture documentation",
            "version": "1.0.0",
            "author": "Architecture Team",
            "output_formats": ["json", "plantuml"]
        }


def validate_diagram_elements(elements: List[Dict[str, Any]]) -> bool:
    """
    Validate diagram element definitions.
    
    Args:
        elements: List of element definitions
        
    Returns:
        True if all elements are valid
        
    Raises:
        ValueError: If any element is invalid
    """
    required_fields = ['type', 'name']
    valid_types = ['person', 'system', 'container', 'component']
    
    for i, element in enumerate(elements):
        for field in required_fields:
            if field not in element:
                raise ValueError(f"Element {i}: Missing required field '{field}'")
        
        if element['type'] not in valid_types:
            raise ValueError(f"Element {i}: Invalid type '{element['type']}'")
    
    return True


def create_elements_from_config(
    config: List[Dict[str, Any]],
    model: Any
) -> Dict[str, Union[Person, SoftwareSystem, Container, Component]]:
    """
    Create diagram elements from configuration.
    
    Args:
        config: List of element configurations
        model: Structurizr model instance
        
    Returns:
        Dictionary mapping element names to instances
    """
    elements = {}
    
    for element_config in config:
        element_type = element_config['type']
        name = element_config['name']
        description = element_config.get('description', '')
        location = element_config.get('location', 'Internal')
        tags = element_config.get('tags', '')
        
        if element_type == 'person':
            element = model.add_person(name, description)
        elif element_type == 'system':
            element = model.add_software_system(name, description)
        else:
            continue  # Skip containers and components for now
        
        if location:
            element.location = location
        if tags:
            element.tags = tags
            
        elements[name] = element
    
    return elements