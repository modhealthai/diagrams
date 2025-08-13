"""
Utility functions and helpers for diagram generation.

This module provides helper functions for common diagram patterns, styling,
element creation, relationship management, and configuration handling.

The utilities are designed to simplify the creation of architectural diagrams
by providing reusable patterns, consistent styling, and configuration management.

Example:
    Basic usage of utility functions:
    
    >>> from diagrams.utils import ElementFactory, ViewStyler
    >>> person = ElementFactory.create_person("User", "System user")
    >>> system = ElementFactory.create_software_system("App", "Main application")
    >>> ViewStyler.apply_custom_theme(view, "modern")
"""

from typing import Dict, List, Optional, Any, Union
import yaml
import json
from pathlib import Path
from dataclasses import dataclass, field

from pystructurizr.dsl import Person, SoftwareSystem, Container, Component


@dataclass
class StyleConfig:
    """
    Configuration for diagram styling.
    
    This class defines styling options for different types of diagram elements
    including colors, shapes, and fonts. It provides sensible defaults while
    allowing customization for specific design requirements.
    
    Attributes:
        colors: Dictionary mapping element types to color codes
        shapes: Dictionary mapping element types to shape names
        fonts: Dictionary mapping element types to font specifications
    
    Example:
        >>> style = StyleConfig(
        ...     colors={"person": "#2E4057", "system": "#048A81"},
        ...     shapes={"person": "Person", "system": "RoundedBox"}
        ... )
    """
    colors: Dict[str, str] = field(default_factory=dict)
    shapes: Dict[str, str] = field(default_factory=dict)
    fonts: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Initialize default styling if not provided."""
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
    """
    Common diagram pattern configuration.
    
    This class represents a reusable diagram pattern that can be applied
    to create consistent architectural diagrams. It includes element
    definitions and their relationships.
    
    Attributes:
        name: Human-readable name of the pattern
        description: Detailed description of what the pattern represents
        elements: List of element definitions with type, name, and properties
        relationships: List of relationship definitions between elements
    
    Example:
        >>> pattern = DiagramPattern(
        ...     name="Web Application",
        ...     description="Standard web app pattern",
        ...     elements=[
        ...         {"type": "person", "name": "User", "description": "End user"},
        ...         {"type": "system", "name": "Web App", "description": "Main app"}
        ...     ],
        ...     relationships=[
        ...         {"source": "User", "destination": "Web App", "description": "Uses"}
        ...     ]
        ... )
    """
    name: str
    description: str
    elements: List[Dict[str, Any]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)


class ConfigurationLoader:
    """
    Handles loading and validation of diagram configurations.
    
    This class provides static methods for loading configuration data from
    various file formats and validating the structure of configuration data.
    It supports both YAML and JSON formats with comprehensive error handling.
    
    Example:
        >>> config = ConfigurationLoader.load_from_file("diagram_config.yml")
        >>> ConfigurationLoader.validate_config(config)
        >>> print(f"Loaded config: {config['name']}")
    """
    
    @staticmethod
    def load_from_file(file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load configuration from YAML or JSON file.
        
        This method automatically detects the file format based on the file
        extension and loads the configuration data appropriately. It supports
        both .yml/.yaml and .json files.
        
        Args:
            file_path: Path to the configuration file (YAML or JSON)
            
        Returns:
            Dictionary containing parsed configuration data
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            ValueError: If the file format is not supported or contains invalid syntax
            
        Example:
            >>> config = ConfigurationLoader.load_from_file("config.yml")
            >>> print(f"Project: {config['name']}")
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
        
        This method performs comprehensive validation of configuration data
        to ensure it contains all required fields and has valid values.
        It checks for required fields and validates data types.
        
        Args:
            config: Configuration dictionary to validate against expected schema
            
        Returns:
            True if configuration is valid and contains all required fields
            
        Raises:
            ValueError: If configuration is missing required fields or
                       contains invalid data types
            
        Example:
            >>> config = {"name": "My System", "description": "System docs"}
            >>> is_valid = ConfigurationLoader.validate_config(config)
            >>> print(f"Config is valid: {is_valid}")
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
    """
    Factory class for creating diagram elements with consistent patterns.
    
    This class provides static methods for creating different types of
    architectural elements (people, systems, containers, components) with
    consistent configuration and styling. It ensures that elements are
    created with proper defaults and validation.
    
    Example:
        >>> person = ElementFactory.create_person("Customer", "Buys products")
        >>> system = ElementFactory.create_software_system("E-Commerce", "Online store")
        >>> container = ElementFactory.create_container(system, "Web App", "UI", "React")
    """
    
    @staticmethod
    def create_person(
        name: str,
        description: str = "",
        location: str = "External",
        tags: str = ""
    ) -> Person:
        """
        Create a Person element with standard configuration.
        
        This method creates a Person element representing a user, actor, or
        stakeholder in the system. It applies consistent naming and
        configuration patterns.
        
        Args:
            name: Name of the person or role (e.g., "Customer", "Administrator")
            description: Description of the person's role and responsibilities
            location: Location relative to the system (Internal/External)
            tags: Comma-separated tags for categorization and styling
            
        Returns:
            Configured Person instance ready to be added to views
            
        Example:
            >>> customer = ElementFactory.create_person(
            ...     "Customer",
            ...     "A person who purchases products from the online store",
            ...     "External",
            ...     "user,external"
            ... )
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
        
        This method creates a SoftwareSystem element representing a high-level
        software system or application. It can represent both internal systems
        (that you own) and external systems (that you integrate with).
        
        Args:
            name: Name of the software system (e.g., "E-Commerce Platform")
            description: Description of what the system does
            location: Location relative to your organization (Internal/External)
            tags: Comma-separated tags for categorization and styling
            
        Returns:
            Configured SoftwareSystem instance ready to be added to views
            
        Example:
            >>> ecommerce = ElementFactory.create_software_system(
            ...     "E-Commerce Platform",
            ...     "Allows customers to browse and purchase products online",
            ...     "Internal",
            ...     "web,ecommerce"
            ... )
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
        
        This method creates a Container element representing an application,
        database, file system, or other deployable unit within a software
        system. Containers are the building blocks of a system.
        
        Args:
            software_system: Parent software system that contains this container
            name: Name of the container (e.g., "Web Application", "Database")
            description: Description of what the container does
            technology: Technology stack or platform used (e.g., "React", "PostgreSQL")
            tags: Comma-separated tags for categorization and styling
            
        Returns:
            Configured Container instance ready to be added to views
            
        Example:
            >>> web_app = ElementFactory.create_container(
            ...     ecommerce_system,
            ...     "Web Application",
            ...     "Provides the e-commerce functionality via web browser",
            ...     "React/TypeScript",
            ...     "web,frontend"
            ... )
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
        
        This method creates a Component element representing a class, interface,
        object, or other code-level construct within a container. Components
        are the finest-grained elements in the C4 model.
        
        Args:
            container: Parent container that contains this component
            name: Name of the component (e.g., "Order Controller", "User Service")
            description: Description of what the component does
            technology: Technology/framework used (e.g., "Spring Boot", "FastAPI")
            tags: Comma-separated tags for categorization and styling
            
        Returns:
            Configured Component instance ready to be added to views
            
        Example:
            >>> controller = ElementFactory.create_component(
            ...     api_container,
            ...     "Order Controller",
            ...     "Handles HTTP requests for order operations",
            ...     "Spring Boot REST Controller",
            ...     "controller,rest"
            ... )
        """
        # Using pystructurizr DSL API
        component = Component(name, description, technology)
        return component


class RelationshipManager:
    """
    Manages relationships between diagram elements.
    
    This class provides utilities for creating and managing relationships
    between architectural elements. It supports different types of relationships
    and interaction styles, and provides batch operations for common patterns.
    
    Example:
        >>> rel = RelationshipManager.create_relationship(
        ...     user, system, "Uses the application", "HTTPS", "Synchronous"
        ... )
        >>> relationships = RelationshipManager.add_common_relationships(
        ...     elements, patterns
        ... )
    """
    
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
        
        This method creates a relationship definition that describes how
        two architectural elements interact. The relationship includes
        descriptive information and technical details.
        
        Args:
            source: Source element that initiates the relationship
            destination: Destination element that receives the interaction
            description: Human-readable description of the relationship
            technology: Technology or protocol used (e.g., "HTTPS", "SQL", "Message Queue")
            interaction_style: Style of interaction (Synchronous/Asynchronous)
            
        Returns:
            Dictionary representing the relationship with source, destination,
            description, technology, and interaction style information
            
        Example:
            >>> relationship = RelationshipManager.create_relationship(
            ...     customer,
            ...     ecommerce_system,
            ...     "Browses products and places orders",
            ...     "HTTPS",
            ...     "Synchronous"
            ... )
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
        
        This method creates multiple relationships at once based on a list
        of relationship patterns. It's useful for applying common architectural
        patterns or bulk relationship creation.
        
        Args:
            elements: Dictionary mapping element names to element instances
            patterns: List of relationship patterns, each containing source,
                     destination, description, and optionally technology
            
        Returns:
            List of created relationship dictionaries
            
        Example:
            >>> elements = {"User": user, "System": system, "DB": database}
            >>> patterns = [
            ...     {"source": "User", "destination": "System", "description": "Uses"},
            ...     {"source": "System", "destination": "DB", "description": "Stores data"}
            ... ]
            >>> relationships = RelationshipManager.add_common_relationships(
            ...     elements, patterns
            ... )
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
    """
    Applies consistent styling to diagram views.
    
    This class provides methods for applying consistent visual styling
    to diagram views. It supports both default styling and predefined
    themes, ensuring that diagrams have a professional and consistent
    appearance.
    
    Example:
        >>> ViewStyler.apply_default_styles(view, custom_style_config)
        >>> ViewStyler.apply_custom_theme(view, "corporate")
    """
    
    @staticmethod
    def apply_default_styles(
        view: Any,
        style_config: Optional[StyleConfig] = None
    ) -> None:
        """
        Apply default styling to a view.
        
        This method applies consistent default styling to a diagram view
        using either the provided style configuration or sensible defaults.
        The styling includes colors, shapes, and fonts for different element types.
        
        Args:
            view: View instance to apply styling to
            style_config: Optional custom style configuration. If not provided,
                         default styling will be used
            
        Example:
            >>> custom_style = StyleConfig(colors={"person": "#2E4057"})
            >>> ViewStyler.apply_default_styles(view, custom_style)
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
        
        This method applies one of several predefined visual themes to a
        diagram view. Each theme provides a different color palette and
        styling approach suitable for different contexts and preferences.
        
        Args:
            view: View instance to apply the theme to
            theme_name: Name of the theme to apply. Available themes:
                       - "corporate": Professional blue/teal color scheme
                       - "modern": Purple/blue modern color scheme
                       - "minimal": Grayscale minimalist color scheme
            
        Example:
            >>> ViewStyler.apply_custom_theme(view, "corporate")
            >>> ViewStyler.apply_custom_theme(container_view, "modern")
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
    """
    Common diagram patterns and templates.
    
    This class provides predefined architectural patterns that can be used
    as starting points for creating diagrams. Each pattern includes common
    elements and relationships for specific architectural styles.
    
    Example:
        >>> microservices = DiagramPatterns.get_microservices_pattern()
        >>> web_app = DiagramPatterns.get_web_application_pattern()
        >>> print(f"Pattern: {microservices.name}")
    """
    
    @staticmethod
    def get_microservices_pattern() -> DiagramPattern:
        """
        Get a microservices architecture pattern.
        
        This method returns a predefined pattern for microservices architecture
        including common elements like API Gateway, multiple services, and
        shared database components.
        
        Returns:
            DiagramPattern instance configured for microservices architecture
            with typical elements and relationships
            
        Example:
            >>> pattern = DiagramPatterns.get_microservices_pattern()
            >>> elements = create_elements_from_config(pattern.elements, model)
        """
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
        """
        Get a web application architecture pattern.
        
        This method returns a predefined pattern for traditional web application
        architecture including user, web application, database, and external
        services like email systems.
        
        Returns:
            DiagramPattern instance configured for web application architecture
            with typical elements and relationships
            
        Example:
            >>> pattern = DiagramPatterns.get_web_application_pattern()
            >>> elements = create_elements_from_config(pattern.elements, model)
        """
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
    
    This function attempts to load configuration from the specified file
    and falls back to sensible defaults if the file doesn't exist or
    cannot be loaded. This ensures that diagrams can always be generated
    even without explicit configuration.
    
    Args:
        config_path: Path to the configuration file (YAML or JSON)
        
    Returns:
        Configuration dictionary with either loaded data or default values
        
    Example:
        >>> config = load_diagram_config("my_config.yml")
        >>> print(f"Project: {config['name']}")
        >>> # Falls back to defaults if file doesn't exist
        >>> default_config = load_diagram_config("nonexistent.yml")
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
    
    This function validates a list of element definitions to ensure they
    have the required fields and valid values. It checks for required
    fields like 'type' and 'name', and validates that element types are
    from the allowed set.
    
    Args:
        elements: List of element definition dictionaries to validate
        
    Returns:
        True if all elements are valid and contain required fields
        
    Raises:
        ValueError: If any element is missing required fields or has
                   invalid values
        
    Example:
        >>> elements = [
        ...     {"type": "person", "name": "User", "description": "End user"},
        ...     {"type": "system", "name": "App", "description": "Main app"}
        ... ]
        >>> is_valid = validate_diagram_elements(elements)
        >>> print(f"Elements are valid: {is_valid}")
    """
    if not elements:
        raise ValueError("Elements list cannot be empty")
    
    required_fields = ['type', 'name']
    valid_types = ['person', 'system', 'container', 'component']
    
    for i, element in enumerate(elements):
        if not isinstance(element, dict):
            raise ValueError(f"Element {i}: Must be a dictionary")
        
        for field in required_fields:
            if field not in element:
                raise ValueError(f"Element {i}: Missing required field '{field}'")
            
            if not element[field] or not str(element[field]).strip():
                raise ValueError(f"Element {i}: Field '{field}' cannot be empty")
        
        if element['type'] not in valid_types:
            raise ValueError(f"Element {i}: Invalid type '{element['type']}'. Valid types: {valid_types}")
        
        # Validate optional fields
        if 'description' in element and element['description'] is not None:
            if not isinstance(element['description'], str):
                raise ValueError(f"Element {i}: Description must be a string")
    
    return True


def validate_diagram_relationships(
    relationships: List[Dict[str, Any]], 
    element_names: List[str]
) -> bool:
    """
    Validate diagram relationship definitions.
    
    This function validates a list of relationship definitions to ensure they
    reference valid elements and have proper structure.
    
    Args:
        relationships: List of relationship definition dictionaries
        element_names: List of valid element names that can be referenced
        
    Returns:
        True if all relationships are valid
        
    Raises:
        ValueError: If any relationship is invalid or references non-existent elements
        
    Example:
        >>> relationships = [
        ...     {"source": "User", "destination": "System", "description": "Uses"}
        ... ]
        >>> element_names = ["User", "System"]
        >>> is_valid = validate_diagram_relationships(relationships, element_names)
    """
    if not relationships:
        return True  # Empty relationships list is valid
    
    required_fields = ['source', 'destination', 'description']
    
    for i, relationship in enumerate(relationships):
        if not isinstance(relationship, dict):
            raise ValueError(f"Relationship {i}: Must be a dictionary")
        
        for field in required_fields:
            if field not in relationship:
                raise ValueError(f"Relationship {i}: Missing required field '{field}'")
            
            if not relationship[field] or not str(relationship[field]).strip():
                raise ValueError(f"Relationship {i}: Field '{field}' cannot be empty")
        
        # Validate that source and destination reference valid elements
        source = relationship['source']
        destination = relationship['destination']
        
        if source not in element_names:
            raise ValueError(f"Relationship {i}: Source '{source}' not found in elements")
        
        if destination not in element_names:
            raise ValueError(f"Relationship {i}: Destination '{destination}' not found in elements")
        
        if source == destination:
            raise ValueError(f"Relationship {i}: Source and destination cannot be the same element")
        
        # Validate optional fields
        if 'technology' in relationship and relationship['technology'] is not None:
            if not isinstance(relationship['technology'], str):
                raise ValueError(f"Relationship {i}: Technology must be a string")
    
    return True


def validate_diagram_definition(diagram_def: Dict[str, Any]) -> bool:
    """
    Validate a complete diagram definition including elements and relationships.
    
    This function performs comprehensive validation of a diagram definition
    including elements, relationships, and overall structure.
    
    Args:
        diagram_def: Dictionary containing complete diagram definition
        
    Returns:
        True if the diagram definition is valid
        
    Raises:
        ValueError: If the diagram definition is invalid
        
    Example:
        >>> diagram_def = {
        ...     "name": "System Context",
        ...     "description": "High-level view",
        ...     "elements": [{"type": "person", "name": "User"}],
        ...     "relationships": []
        ... }
        >>> is_valid = validate_diagram_definition(diagram_def)
    """
    if not isinstance(diagram_def, dict):
        raise ValueError("Diagram definition must be a dictionary")
    
    # Validate required top-level fields
    required_fields = ['name', 'description', 'elements']
    for field in required_fields:
        if field not in diagram_def:
            raise ValueError(f"Missing required field: {field}")
        
        if not diagram_def[field] or (isinstance(diagram_def[field], str) and not diagram_def[field].strip()):
            raise ValueError(f"Field '{field}' cannot be empty")
    
    # Validate elements
    elements = diagram_def['elements']
    if not isinstance(elements, list):
        raise ValueError("Elements must be a list")
    
    validate_diagram_elements(elements)
    
    # Extract element names for relationship validation
    element_names = [element['name'] for element in elements]
    
    # Validate relationships if present
    if 'relationships' in diagram_def:
        relationships = diagram_def['relationships']
        if not isinstance(relationships, list):
            raise ValueError("Relationships must be a list")
        
        validate_diagram_relationships(relationships, element_names)
    
    # Validate optional fields
    if 'type' in diagram_def:
        valid_diagram_types = ['system_context', 'container', 'component']
        if diagram_def['type'] not in valid_diagram_types:
            raise ValueError(f"Invalid diagram type. Valid types: {valid_diagram_types}")
    
    return True


class DiagramValidator:
    """
    Comprehensive diagram validation with detailed error reporting.
    
    This class provides advanced validation capabilities for diagrams
    including structural validation, semantic checks, and best practice
    recommendations.
    """
    
    def __init__(self):
        """Initialize the diagram validator."""
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_diagram_structure(self, diagram_def: Dict[str, Any]) -> bool:
        """
        Validate diagram structure and collect detailed error information.
        
        Args:
            diagram_def: Dictionary containing diagram definition
            
        Returns:
            True if validation passes, False otherwise
        """
        self.errors.clear()
        self.warnings.clear()
        
        try:
            validate_diagram_definition(diagram_def)
            
            # Additional structural checks
            self._check_diagram_completeness(diagram_def)
            self._check_best_practices(diagram_def)
            
            return len(self.errors) == 0
            
        except ValueError as e:
            self.errors.append(str(e))
            return False
    
    def _check_diagram_completeness(self, diagram_def: Dict[str, Any]) -> None:
        """Check for diagram completeness and common issues."""
        elements = diagram_def.get('elements', [])
        relationships = diagram_def.get('relationships', [])
        
        # Check for isolated elements (no relationships)
        if relationships:
            element_names = {element['name'] for element in elements}
            connected_elements = set()
            
            for rel in relationships:
                connected_elements.add(rel['source'])
                connected_elements.add(rel['destination'])
            
            isolated_elements = element_names - connected_elements
            if isolated_elements:
                self.warnings.append(f"Isolated elements (no relationships): {', '.join(isolated_elements)}")
        
        # Check for missing descriptions
        elements_without_desc = [
            elem['name'] for elem in elements 
            if not elem.get('description', '').strip()
        ]
        if elements_without_desc:
            self.warnings.append(f"Elements missing descriptions: {', '.join(elements_without_desc)}")
    
    def _check_best_practices(self, diagram_def: Dict[str, Any]) -> None:
        """Check for best practice violations."""
        elements = diagram_def.get('elements', [])
        
        # Check for reasonable number of elements
        if len(elements) > 20:
            self.warnings.append(f"Large number of elements ({len(elements)}). Consider breaking into multiple diagrams.")
        
        # Check for consistent naming
        element_names = [elem['name'] for elem in elements]
        if len(set(element_names)) != len(element_names):
            self.errors.append("Duplicate element names found")
        
        # Check for proper element distribution
        element_types = [elem['type'] for elem in elements]
        type_counts = {t: element_types.count(t) for t in set(element_types)}
        
        if 'person' not in type_counts:
            self.warnings.append("No people/actors defined. Consider adding users or stakeholders.")
    
    def get_validation_report(self) -> Dict[str, Any]:
        """
        Get a detailed validation report.
        
        Returns:
            Dictionary containing validation results, errors, and warnings
        """
        return {
            "valid": len(self.errors) == 0,
            "errors": self.errors.copy(),
            "warnings": self.warnings.copy(),
            "error_count": len(self.errors),
            "warning_count": len(self.warnings)
        }


def create_elements_from_config(
    config: List[Dict[str, Any]],
    model: Any
) -> Dict[str, Union[Person, SoftwareSystem, Container, Component]]:
    """
    Create diagram elements from configuration.
    
    This function creates architectural elements from a configuration list,
    automatically determining the element type and creating the appropriate
    instances. It's useful for bulk element creation from configuration files
    or patterns.
    
    Args:
        config: List of element configuration dictionaries, each containing
               'type', 'name', 'description', and optional properties
        model: Structurizr model instance to add elements to
        
    Returns:
        Dictionary mapping element names to their created instances
        
    Example:
        >>> config = [
        ...     {"type": "person", "name": "User", "description": "End user"},
        ...     {"type": "system", "name": "App", "description": "Main app"}
        ... ]
        >>> elements = create_elements_from_config(config, model)
        >>> user = elements["User"]
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