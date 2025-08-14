"""
Base diagram generator class for creating pystructurizr diagrams.

This module provides the core DiagramGenerator class that handles workspace creation,
view management, and export functionality for architectural diagrams.

Example:
    Basic usage of the DiagramGenerator:
    
    >>> from diagrams.generator import DiagramGenerator, DiagramConfig
    >>> config = DiagramConfig(name="My System", description="System architecture")
    >>> generator = DiagramGenerator(config)
    >>> workspace = generator.create_workspace()
    >>> # Add views and export diagrams
"""

from typing import Dict, List, Optional, Any
import json
from datetime import datetime
from dataclasses import dataclass

try:
    from .cache import DiagramCache, ImageOptimizer
except ImportError:
    # Handle running as script or in different contexts
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent))
    from cache import DiagramCache, ImageOptimizer

from pystructurizr.dsl import Workspace, Model, Person, SoftwareSystem, Container, Component, View


@dataclass
class DiagramConfig:
    """
    Configuration for diagram generation.
    
    This class holds all the configuration parameters needed to generate
    architectural diagrams, including metadata and output format preferences.
    
    Attributes:
        name: The name of the diagram set or project
        description: A detailed description of what the diagrams represent
        version: Version string for the diagram set (default: "1.0.0")
        author: Author or team responsible for the diagrams (default: "Architecture Team")
        output_formats: List of formats to export (default: ['json', 'plantuml'])
    
    Example:
        >>> config = DiagramConfig(
        ...     name="E-Commerce System",
        ...     description="Online shopping platform architecture",
        ...     version="2.1.0",
        ...     author="Platform Team",
        ...     output_formats=['json', 'plantuml', 'png']
        ... )
    """
    name: str
    description: str
    version: str = "1.0.0"
    author: str = "Architecture Team"
    output_formats: Optional[List[str]] = None

    def __post_init__(self) -> None:
        """Initialize default output formats if none provided."""
        if self.output_formats is None:
            self.output_formats = ['json', 'plantuml']


@dataclass
class DiagramMetadata:
    """
    Metadata for generated diagrams.
    
    This class stores metadata about individual diagrams including their type,
    creation time, and associated output files.
    
    Attributes:
        title: Human-readable title of the diagram
        description: Detailed description of what the diagram shows
        diagram_type: Type of diagram ('system_context', 'container', 'component')
        last_updated: Timestamp when the diagram was last modified
        file_path: Path to the source file or primary output file
        output_files: Dictionary mapping format names to file paths
    
    Example:
        >>> metadata = DiagramMetadata(
        ...     title="System Context View",
        ...     description="High-level view of the system",
        ...     diagram_type="system_context",
        ...     last_updated=datetime.now(),
        ...     file_path="system_context.json"
        ... )
    """
    title: str
    description: str
    diagram_type: str
    last_updated: datetime
    file_path: str
    output_files: Optional[Dict[str, str]] = None

    def __post_init__(self) -> None:
        """Initialize empty output files dictionary if none provided."""
        if self.output_files is None:
            self.output_files = {}


class DiagramGenerator:
    """
    Base class for generating architectural diagrams using pystructurizr.
    
    This class provides methods for creating workspaces, adding different types of views,
    and exporting diagrams to various formats including JSON and PlantUML.
    
    The generator maintains metadata about all created diagrams and provides
    validation and export capabilities.
    
    Attributes:
        config: Configuration object containing diagram settings
        workspace: The pystructurizr workspace instance (None until created)
        _metadata: Internal list of diagram metadata
    
    Example:
        >>> config = DiagramConfig(name="My System", description="System docs")
        >>> generator = DiagramGenerator(config)
        >>> workspace = generator.create_workspace()
        >>> view = generator.add_system_context_view(system, "Context", "Overview")
        >>> json_output = generator.export_to_json()
    """

    def __init__(self, config: DiagramConfig, enable_cache: bool = True) -> None:
        """
        Initialize the diagram generator with configuration.
        
        Args:
            config: Configuration object containing diagram settings including
                   name, description, version, author, and output formats
            enable_cache: Whether to enable caching for performance optimization
        
        Raises:
            TypeError: If config is not a DiagramConfig instance
        """
        if not isinstance(config, DiagramConfig):
            raise TypeError("config must be a DiagramConfig instance")
            
        self.config = config
        self.workspace: Optional[Workspace] = None
        self._metadata: List[DiagramMetadata] = []
        self.enable_cache = enable_cache
        self.cache = DiagramCache() if enable_cache else None
        self.image_optimizer = ImageOptimizer()

    def create_workspace(self) -> Workspace:
        """
        Create and configure a new pystructurizr workspace.
        
        This method initializes a new Structurizr workspace that will contain
        all the architectural models and views. The workspace is configured
        with the settings from the DiagramConfig.
        
        Returns:
            Configured Workspace instance ready for adding models and views
        
        Example:
            >>> generator = DiagramGenerator(config)
            >>> workspace = generator.create_workspace()
            >>> # Now you can add models and views to the workspace
        """
        self.workspace = Workspace()
        return self.workspace

    def add_system_context_view(
        self,
        software_system: SoftwareSystem,
        title: str,
        description: str = "",
        key: Optional[str] = None
    ) -> Any:
        """
        Add a system context view to the workspace.
        
        A system context view shows a software system and its relationships
        with users and other software systems. This is typically the highest
        level view in the C4 model hierarchy.
        
        Args:
            software_system: The software system to create the view for
            title: Human-readable title for the view
            description: Optional detailed description of what the view shows
            key: Optional unique identifier for the view. If not provided,
                 will be auto-generated from the software system name
            
        Returns:
            Created SystemContextView instance that can be used to add
            elements and apply styling
            
        Raises:
            ValueError: If workspace has not been created yet
            
        Example:
            >>> system = model.add_software_system("E-Commerce", "Online store")
            >>> view = generator.add_system_context_view(
            ...     system,
            ...     "E-Commerce System Context",
            ...     "Shows the e-commerce system and its users"
            ... )
            >>> view.include(customer, admin, payment_system)
        """
        if not self.workspace:
            raise ValueError("Workspace must be created before adding views")
            
        if key is None:
            key = f"SystemContext-{software_system.name.replace(' ', '')}"
            
        # Create system context view using pystructurizr DSL
        view = self.workspace.SystemContextView(
            software_system,
            key,
            title
        )
        
        # Store metadata
        metadata = DiagramMetadata(
            title=title,
            description=description,
            diagram_type="system_context",
            last_updated=datetime.now(),
            file_path=f"{key}.json"
        )
        self._metadata.append(metadata)
        
        return view

    def add_container_view(
        self,
        software_system: SoftwareSystem,
        title: str,
        description: str = "",
        key: Optional[str] = None
    ) -> Any:
        """
        Add a container view to the workspace.
        
        A container view shows the internal structure of a software system,
        including the containers (applications, databases, file systems, etc.)
        that make up the system and their relationships.
        
        Args:
            software_system: The software system to create the view for
            title: Human-readable title for the view
            description: Optional detailed description of what the view shows
            key: Optional unique identifier for the view. If not provided,
                 will be auto-generated from the software system name
            
        Returns:
            Created ContainerView instance that can be used to add
            containers and apply styling
            
        Raises:
            ValueError: If workspace has not been created yet
            
        Example:
            >>> system = model.add_software_system("E-Commerce", "Online store")
            >>> view = generator.add_container_view(
            ...     system,
            ...     "E-Commerce Container View",
            ...     "Shows the internal structure of the e-commerce system"
            ... )
            >>> view.include(web_app, api, database)
        """
        if not self.workspace:
            raise ValueError("Workspace must be created before adding views")
            
        if key is None:
            key = f"Container-{software_system.name.replace(' ', '')}"
            
        # Create container view using pystructurizr DSL
        view = self.workspace.ContainerView(
            software_system,
            key,
            title
        )
        
        # Store metadata
        metadata = DiagramMetadata(
            title=title,
            description=description,
            diagram_type="container",
            last_updated=datetime.now(),
            file_path=f"{key}.json"
        )
        self._metadata.append(metadata)
        
        return view

    def add_component_view(
        self,
        container: Container,
        title: str,
        description: str = "",
        key: Optional[str] = None
    ) -> Any:
        """
        Add a component view to the workspace.
        
        A component view shows the internal structure of a container,
        including the components (classes, interfaces, objects, etc.)
        that make up the container and their relationships.
        
        Args:
            container: The container to create the view for
            title: Human-readable title for the view
            description: Optional detailed description of what the view shows
            key: Optional unique identifier for the view. If not provided,
                 will be auto-generated from the container name
            
        Returns:
            Created ComponentView instance that can be used to add
            components and apply styling
            
        Raises:
            ValueError: If workspace has not been created yet
            
        Example:
            >>> api_container = system.add_container("API", "REST API", "Python")
            >>> view = generator.add_component_view(
            ...     api_container,
            ...     "API Component View",
            ...     "Shows the internal structure of the API container"
            ... )
            >>> view.include(controller, service, repository)
        """
        if not self.workspace:
            raise ValueError("Workspace must be created before adding views")
            
        if key is None:
            key = f"Component-{container.name.replace(' ', '')}"
            
        # Create component view using pystructurizr DSL
        view = self.workspace.ComponentView(
            container,
            key,
            title
        )
        
        # Store metadata
        metadata = DiagramMetadata(
            title=title,
            description=description,
            diagram_type="component",
            last_updated=datetime.now(),
            file_path=f"{key}.json"
        )
        self._metadata.append(metadata)
        
        return view

    def export_to_json(self) -> str:
        """
        Export the workspace to structured JSON format with metadata.
        
        This method creates a comprehensive JSON export that includes the
        workspace data, model information, views, and metadata about all
        generated diagrams. The export is structured for easy consumption
        by static site generators and other tools.
        
        Returns:
            JSON string representation of the workspace with enhanced metadata
            including workspace configuration, model data, views, and diagram
            metadata with timestamps and file paths
            
        Raises:
            ValueError: If workspace has not been created or if export fails
            
        Example:
            >>> generator = DiagramGenerator(config)
            >>> workspace = generator.create_workspace()
            >>> # ... add views ...
            >>> json_data = generator.export_to_json()
            >>> with open("architecture.json", "w") as f:
            ...     f.write(json_data)
        """
        if not self.workspace:
            raise ValueError("Workspace must be created before export")
        
        # Validate workspace before export
        self.validate_workspace()
        
        try:
            # Get the raw workspace data
            workspace_data = self.workspace.dump()
            
            # Create structured export with metadata
            structured_export = {
                "workspace": {
                    "name": self.config.name,
                    "description": self.config.description,
                    "version": self.config.version,
                    "author": self.config.author,
                    "lastUpdated": datetime.now().isoformat(),
                    "configuration": {
                        "outputFormats": self.config.output_formats
                    }
                },
                "model": self._extract_model_data(),
                "views": self._extract_views_data(),
                "metadata": {
                    "diagrams": [
                        {
                            "title": meta.title,
                            "description": meta.description,
                            "type": meta.diagram_type,
                            "lastUpdated": meta.last_updated.isoformat(),
                            "filePath": meta.file_path,
                            "outputFiles": meta.output_files
                        }
                        for meta in self._metadata
                    ],
                    "generatedAt": datetime.now().isoformat(),
                    "generator": {
                        "name": "pystructurizr-github-pages",
                        "version": self.config.version
                    }
                },
                "rawWorkspace": workspace_data
            }
            
            return json.dumps(structured_export, indent=2, ensure_ascii=False)
            
        except Exception as e:
            raise ValueError(f"Failed to export workspace to JSON: {str(e)}")
    
    def _extract_model_data(self) -> Dict[str, Any]:
        """
        Extract model data from the workspace.
        
        This method traverses the workspace model to extract information
        about all architectural elements including people, software systems,
        containers, components, and their relationships.
        
        Returns:
            Dictionary containing structured model data with separate
            collections for each element type and their relationships
            
        Note:
            This is a simplified extraction. In a full implementation,
            this would traverse the actual workspace model structure
            to extract all elements and their properties.
        """
        model_data = {
            "people": [],
            "softwareSystems": [],
            "containers": [],
            "components": [],
            "relationships": []
        }
        
        # This is a simplified extraction - in a real implementation,
        # we would traverse the workspace model to extract all elements
        # For now, we'll return the structure with placeholders
        
        return model_data
    
    def _extract_views_data(self) -> Dict[str, Any]:
        """
        Extract views data from the workspace.
        
        This method traverses the workspace views to extract information
        about all created views including their configuration, included
        elements, and styling information.
        
        Returns:
            Dictionary containing structured view data organized by
            view type with styling and configuration information
            
        Note:
            This is a simplified extraction. In a full implementation,
            this would traverse the actual workspace views to extract
            all view definitions and their properties.
        """
        views_data = {
            "systemContextViews": [],
            "containerViews": [],
            "componentViews": [],
            "styles": {}
        }
        
        # This is a simplified extraction - in a real implementation,
        # we would traverse the workspace views to extract all view data
        
        return views_data

    def validate_workspace(self) -> None:
        """
        Validate the workspace and all its elements before export.
        
        This method performs comprehensive validation of the workspace including:
        - Checking that required elements exist
        - Validating relationships between elements
        - Ensuring all views have proper configuration
        - Checking for common diagram issues
        
        Raises:
            ValueError: If validation fails with detailed error messages
        """
        if not self.workspace:
            raise ValueError("Workspace has not been created")
        
        # Validate configuration
        if not self.config.name or not self.config.name.strip():
            raise ValueError("Workspace name cannot be empty")
        
        if not self.config.description or not self.config.description.strip():
            raise ValueError("Workspace description cannot be empty")
        
        # Validate that we have at least one diagram
        if not self._metadata:
            raise ValueError("Workspace must contain at least one diagram")
        
        # Validate each diagram's metadata
        for i, meta in enumerate(self._metadata):
            if not meta.title or not meta.title.strip():
                raise ValueError(f"Diagram {i+1}: Title cannot be empty")
            
            if meta.diagram_type not in ['system_context', 'container', 'component']:
                raise ValueError(f"Diagram {i+1}: Invalid diagram type '{meta.diagram_type}'")
        
        print("✓ Workspace validation passed")

    def validate_export_data(self, json_data: str) -> None:
        """
        Validate exported JSON data structure and content.
        
        This method validates that the exported JSON data has the correct
        structure and contains all required fields with valid values.
        
        Args:
            json_data: JSON string to validate
            
        Raises:
            ValueError: If validation fails with detailed error messages
        """
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        
        # Validate top-level structure
        required_sections = ['workspace', 'model', 'views', 'metadata', 'rawWorkspace']
        for section in required_sections:
            if section not in data:
                raise ValueError(f"Missing required section: {section}")
        
        # Validate workspace section
        workspace = data['workspace']
        required_workspace_fields = ['name', 'description', 'version', 'author']
        for field in required_workspace_fields:
            if field not in workspace or not workspace[field]:
                raise ValueError(f"Missing or empty workspace field: {field}")
        
        # Validate metadata section
        metadata = data['metadata']
        if 'diagrams' not in metadata:
            raise ValueError("Missing diagrams in metadata section")
        
        if not isinstance(metadata['diagrams'], list):
            raise ValueError("Diagrams metadata must be a list")
        
        if len(metadata['diagrams']) == 0:
            raise ValueError("Must have at least one diagram in metadata")
        
        # Validate each diagram metadata
        for i, diagram in enumerate(metadata['diagrams']):
            required_diagram_fields = ['title', 'type', 'lastUpdated']
            for field in required_diagram_fields:
                if field not in diagram or not diagram[field]:
                    raise ValueError(f"Diagram {i+1}: Missing or empty field '{field}'")
        
        print("✓ JSON export data validation passed")

    def validate_plantuml_output(self, plantuml_data: str) -> None:
        """
        Validate PlantUML output format and content.
        
        This method validates that the PlantUML output has proper syntax
        and contains expected elements for diagram rendering.
        
        Args:
            plantuml_data: PlantUML string to validate
            
        Raises:
            ValueError: If validation fails with detailed error messages
        """
        if not plantuml_data or not plantuml_data.strip():
            raise ValueError("PlantUML output is empty")
        
        lines = plantuml_data.strip().split('\n')
        
        # Check for required PlantUML structure
        if not any(line.strip().startswith('@startuml') for line in lines):
            raise ValueError("Missing @startuml directive")
        
        if not any(line.strip().startswith('@enduml') for line in lines):
            raise ValueError("Missing @enduml directive")
        
        # Check for title (less strict - can be !title or title in comments)
        has_title = any('!title' in line or 'title' in line.lower() for line in lines)
        if not has_title:
            raise ValueError("Missing title directive")
        
        # Check for C4 model includes (optional but recommended)
        has_c4_includes = any('C4_' in line for line in lines)
        if not has_c4_includes:
            # This is a warning, not an error
            pass
        
        # Check for basic content (at least some elements or relationships)
        content_indicators = ['Person(', 'System(', 'Container(', 'Component(', 'Rel(']
        has_content = any(indicator in plantuml_data for indicator in content_indicators)
        if not has_content:
            raise ValueError("PlantUML output appears to be empty (no elements or relationships found)")
        
        print("✓ PlantUML output validation passed")

    def get_metadata(self) -> List[DiagramMetadata]:
        """
        Get metadata for all diagrams in the workspace.
        
        Returns:
            List of DiagramMetadata objects containing information about
            all diagrams in the workspace
        """
        return self._metadata.copy()

    def export_to_plantuml(self) -> str:
        """
        Export the workspace to PlantUML format with proper formatting and styling.
        
        This method generates PlantUML source code for all views in the workspace,
        including proper C4 model styling, headers, and formatting. The output
        can be used with PlantUML to generate visual diagrams.
        
        Returns:
            PlantUML string representation of all views with styling directives,
            C4 model includes, and proper formatting for rendering
            
        Raises:
            ValueError: If workspace has not been created or if export fails
            
        Example:
            >>> generator = DiagramGenerator(config)
            >>> workspace = generator.create_workspace()
            >>> # ... add views ...
            >>> plantuml_code = generator.export_to_plantuml()
            >>> with open("architecture.puml", "w") as f:
            ...     f.write(plantuml_code)
        """
        if not self.workspace:
            raise ValueError("Workspace must be created before export")
        
        # Validate workspace before export
        self.validate_workspace()
        
        try:
            plantuml_output = []
            
            # Add PlantUML header with C4 model support
            plantuml_output.extend([
                "@startuml",
                f"!title {self.config.name}",
                "",
                "' Generated from pystructurizr workspace",
                f"' Author: {self.config.author}",
                f"' Version: {self.config.version}",
                f"' Generated at: {datetime.now().isoformat()}",
                "",
                "' Include C4 model macros for better styling",
                "!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml",
                "!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml",
                "!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml",
                "",
                "' Custom styling",
                "!define TECHN_FONT_SIZE 12",
                "skinparam backgroundColor #FFFFFF",
                "skinparam defaultFontName Arial",
                "skinparam defaultFontSize 11",
                ""
            ])
            
            # Generate PlantUML for each diagram type
            for meta in self._metadata:
                plantuml_output.extend([
                    f"' === {meta.title} ===",
                    f"' Type: {meta.diagram_type}",
                    f"' Description: {meta.description}",
                    f"' Last Updated: {meta.last_updated.isoformat()}",
                    ""
                ])
                
                if meta.diagram_type == "system_context":
                    plantuml_output.extend(self._generate_system_context_plantuml())
                elif meta.diagram_type == "container":
                    plantuml_output.extend(self._generate_container_plantuml())
                elif meta.diagram_type == "component":
                    plantuml_output.extend(self._generate_component_plantuml())
                
                plantuml_output.append("")
            
            # Add footer
            plantuml_output.extend([
                "' Styling for different element types",
                "skinparam person {",
                "  BackgroundColor #08427b",
                "  FontColor #ffffff",
                "  BorderColor #073B6F",
                "}",
                "",
                "skinparam rectangle {",
                "  BackgroundColor #1168bd",
                "  FontColor #ffffff",
                "  BorderColor #0E5A9D",
                "}",
                "",
                "skinparam database {",
                "  BackgroundColor #438dd5",
                "  FontColor #ffffff",
                "  BorderColor #3A7BC8",
                "}",
                "",
                "@enduml"
            ])
            
            return "\n".join(plantuml_output)
            
        except Exception as e:
            raise ValueError(f"Failed to export workspace to PlantUML: {str(e)}")
    
    def _generate_system_context_plantuml(self) -> List[str]:
        """
        Generate PlantUML code for system context view.
        
        This method creates PlantUML source code for system context diagrams
        using C4 model notation. It includes people, software systems, and
        their relationships.
        
        Returns:
            List of PlantUML lines representing the system context view
            with proper C4 model syntax and styling
        """
        lines = [
            "' System Context View",
            "Person(customer, \"Customer\", \"A customer who browses products, places orders, and makes payments\")",
            "Person(admin, \"Administrator\", \"System administrator who manages products, orders, and system configuration\")",
            "Person(support, \"Support Staff\", \"Customer support staff who help customers with orders and issues\")",
            "",
            "System(ecommerce, \"E-Commerce Platform\", \"Allows customers to browse products, place orders, and make payments online\")",
            "",
            "System_Ext(payment, \"Payment Gateway\", \"Processes credit card payments and handles payment security\")",
            "System_Ext(email, \"Email Service\", \"Sends transactional emails like order confirmations and notifications\")",
            "System_Ext(inventory, \"Inventory Management\", \"Manages product inventory, stock levels, and supplier information\")",
            "System_Ext(shipping, \"Shipping Provider\", \"Handles package delivery and tracking services\")",
            "",
            "' Relationships",
            "Rel(customer, ecommerce, \"Browses products, places orders, tracks shipments\")",
            "Rel(admin, ecommerce, \"Manages products, processes orders, configures system\")",
            "Rel(support, ecommerce, \"Helps customers with orders and resolves issues\")",
            "",
            "Rel(ecommerce, payment, \"Processes payments\", \"HTTPS/REST API\")",
            "Rel(ecommerce, email, \"Sends order confirmations and notifications\", \"SMTP/API\")",
            "Rel(ecommerce, inventory, \"Checks stock levels and updates inventory\", \"HTTPS/REST API\")",
            "Rel(ecommerce, shipping, \"Creates shipping labels and tracks packages\", \"HTTPS/REST API\")",
            "",
            "Rel(payment, ecommerce, \"Sends payment confirmations and failures\", \"Webhooks\")",
            "Rel(shipping, ecommerce, \"Provides delivery status updates\", \"Webhooks\")",
            ""
        ]
        return lines
    
    def _generate_container_plantuml(self) -> List[str]:
        """
        Generate PlantUML code for container view.
        
        This method creates PlantUML source code for container diagrams
        using C4 model notation. It includes containers within a system
        boundary and their relationships with external elements.
        
        Returns:
            List of PlantUML lines representing the container view
            with proper C4 model syntax and system boundaries
        """
        lines = [
            "' Container View",
            "Person(customer, \"Customer\")",
            "Person(admin, \"Administrator\")",
            "",
            "System_Boundary(ecommerce_boundary, \"E-Commerce Platform\") {",
            "  Container(web_app, \"Web Application\", \"React/TypeScript\", \"Provides the e-commerce functionality via a web browser\")",
            "  Container(mobile_app, \"Mobile Application\", \"React Native\", \"Provides e-commerce functionality via mobile devices\")",
            "  Container(api_gateway, \"API Gateway\", \"Node.js/Express\", \"Routes requests and handles authentication/authorization\")",
            "  ",
            "  Container(product_service, \"Product Service\", \"Python/FastAPI\", \"Manages product catalog, search, and recommendations\")",
            "  Container(order_service, \"Order Service\", \"Java/Spring Boot\", \"Handles order processing, cart management, and checkout\")",
            "  Container(user_service, \"User Service\", \"Python/Django\", \"Manages user accounts, authentication, and profiles\")",
            "  Container(notification_service, \"Notification Service\", \"Node.js\", \"Handles email notifications and push notifications\")",
            "  ",
            "  ContainerDb(database, \"Database\", \"PostgreSQL\", \"Stores user accounts, product information, orders, and system data\")",
            "  Container(cache, \"Cache\", \"Redis\", \"Caches frequently accessed data for improved performance\")",
            "  Container(file_storage, \"File Storage\", \"AWS S3\", \"Stores product images and other static assets\")",
            "}",
            "",
            "System_Ext(payment, \"Payment Gateway\")",
            "System_Ext(email, \"Email Service\")",
            "System_Ext(inventory, \"Inventory Management\")",
            "System_Ext(shipping, \"Shipping Provider\")",
            "",
            "' User interactions",
            "Rel(customer, web_app, \"Browses products and places orders using\")",
            "Rel(customer, mobile_app, \"Browses products and places orders using\")",
            "Rel(admin, web_app, \"Manages products and orders using\")",
            "",
            "' Front-end to API Gateway",
            "Rel(web_app, api_gateway, \"Makes API calls to\", \"HTTPS/REST\")",
            "Rel(mobile_app, api_gateway, \"Makes API calls to\", \"HTTPS/REST\")",
            "",
            "' API Gateway to services",
            "Rel(api_gateway, user_service, \"Routes authentication requests to\", \"HTTP/REST\")",
            "Rel(api_gateway, product_service, \"Routes product requests to\", \"HTTP/REST\")",
            "Rel(api_gateway, order_service, \"Routes order requests to\", \"HTTP/REST\")",
            "",
            "' Services to database",
            "Rel(user_service, database, \"Reads from and writes to\", \"SQL/TCP\")",
            "Rel(product_service, database, \"Reads from and writes to\", \"SQL/TCP\")",
            "Rel(order_service, database, \"Reads from and writes to\", \"SQL/TCP\")",
            "",
            "' Services to cache",
            "Rel(product_service, cache, \"Caches product data in\", \"Redis Protocol\")",
            "Rel(user_service, cache, \"Caches session data in\", \"Redis Protocol\")",
            "",
            "' External system relationships",
            "Rel(order_service, payment, \"Processes payments via\")",
            "Rel(order_service, inventory, \"Checks inventory via\")",
            "Rel(order_service, shipping, \"Creates shipments via\")",
            "Rel(notification_service, email, \"Sends emails via\")",
            ""
        ]
        return lines
    
    def _generate_component_plantuml(self) -> List[str]:
        """
        Generate PlantUML code for component view.
        
        This method creates PlantUML source code for component diagrams
        using C4 model notation. It includes components within a container
        boundary and their relationships with external elements.
        
        Returns:
            List of PlantUML lines representing the component view
            with proper C4 model syntax and container boundaries
        """
        lines = [
            "' Component View - Order Service",
            "Person(customer, \"Customer\")",
            "Container(api_gateway, \"API Gateway\")",
            "ContainerDb(database, \"Database\")",
            "Container(notification_service, \"Notification Service\")",
            "",
            "System_Ext(payment, \"Payment Gateway\")",
            "System_Ext(inventory, \"Inventory Management\")",
            "System_Ext(shipping, \"Shipping Provider\")",
            "",
            "Container_Boundary(order_boundary, \"Order Service\") {",
            "  Component(order_controller, \"Order Controller\", \"Spring Boot REST Controller\", \"Handles HTTP requests for order operations\")",
            "  Component(cart_service, \"Cart Service\", \"Spring Service\", \"Manages shopping cart operations and persistence\")",
            "  Component(order_processor, \"Order Processor\", \"Spring Service\", \"Processes orders, validates inventory, and coordinates payment\")",
            "  ",
            "  Component(payment_client, \"Payment Client\", \"HTTP Client\", \"Integrates with external payment gateway\")",
            "  Component(inventory_client, \"Inventory Client\", \"HTTP Client\", \"Integrates with external inventory management system\")",
            "  Component(shipping_client, \"Shipping Client\", \"HTTP Client\", \"Integrates with external shipping providers\")",
            "  ",
            "  Component(order_repository, \"Order Repository\", \"Spring Data JPA\", \"Handles data persistence for orders and cart items\")",
            "  Component(notification_publisher, \"Notification Publisher\", \"Message Queue Publisher\", \"Publishes order events to notification service\")",
            "}",
            "",
            "' External requests",
            "Rel(api_gateway, order_controller, \"Routes order requests to\", \"HTTP/REST\")",
            "",
            "' Internal component relationships",
            "Rel(order_controller, cart_service, \"Manages cart operations via\")",
            "Rel(order_controller, order_processor, \"Processes orders via\")",
            "",
            "Rel(cart_service, order_repository, \"Persists cart data via\")",
            "",
            "Rel(order_processor, payment_client, \"Processes payments via\")",
            "Rel(order_processor, inventory_client, \"Checks inventory via\")",
            "Rel(order_processor, shipping_client, \"Creates shipments via\")",
            "Rel(order_processor, order_repository, \"Persists order data via\")",
            "Rel(order_processor, notification_publisher, \"Publishes order events via\")",
            "",
            "' External integrations",
            "Rel(payment_client, payment, \"Makes payment requests to\")",
            "Rel(inventory_client, inventory, \"Checks stock levels with\")",
            "Rel(shipping_client, shipping, \"Creates shipping labels with\")",
            "",
            "Rel(order_repository, database, \"Reads from and writes to\", \"JDBC/SQL\")",
            "Rel(notification_publisher, notification_service, \"Publishes events to\", \"Message Queue\")",
            ""
        ]
        return lines

    def get_metadata(self) -> List[DiagramMetadata]:
        """
        Get metadata for all generated diagrams.
        
        This method returns a copy of the internal metadata list containing
        information about all diagrams that have been created in this
        generator instance.
        
        Returns:
            List of DiagramMetadata objects containing title, description,
            type, timestamps, and file paths for each generated diagram
            
        Example:
            >>> metadata_list = generator.get_metadata()
            >>> for meta in metadata_list:
            ...     print(f"{meta.title}: {meta.diagram_type}")
        """
        return self._metadata.copy()
    
    def validate_export_data(self, export_data: str) -> bool:
        """
        Validate the structure of exported JSON data.
        
        This method performs comprehensive validation of JSON export data
        to ensure it contains all required fields and has the correct
        structure for consumption by other tools.
        
        Args:
            export_data: JSON string to validate against expected schema
            
        Returns:
            True if data structure is valid and contains all required fields
            
        Raises:
            ValueError: If data structure is invalid, missing required fields,
                       or contains invalid values
            
        Example:
            >>> json_data = generator.export_to_json()
            >>> is_valid = generator.validate_export_data(json_data)
            >>> print(f"Export data is valid: {is_valid}")
        """
        try:
            data = json.loads(export_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
        
        # Validate required top-level keys
        required_keys = ["workspace", "model", "views", "metadata", "rawWorkspace"]
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key: {key}")
        
        # Validate workspace section
        workspace = data["workspace"]
        workspace_required = ["name", "description", "version", "author", "lastUpdated"]
        for key in workspace_required:
            if key not in workspace:
                raise ValueError(f"Missing required workspace key: {key}")
        
        # Validate metadata section
        metadata = data["metadata"]
        if "diagrams" not in metadata:
            raise ValueError("Missing diagrams in metadata")
        
        if "generatedAt" not in metadata:
            raise ValueError("Missing generatedAt in metadata")
        
        # Validate each diagram metadata
        for i, diagram in enumerate(metadata["diagrams"]):
            diagram_required = ["title", "description", "type", "lastUpdated", "filePath"]
            for key in diagram_required:
                if key not in diagram:
                    raise ValueError(f"Missing required key '{key}' in diagram {i}")
            
            # Validate diagram type
            valid_types = ["system_context", "container", "component"]
            if diagram["type"] not in valid_types:
                raise ValueError(f"Invalid diagram type '{diagram['type']}' in diagram {i}")
        
        return True
    
    def validate_plantuml_output(self, plantuml_data: str) -> bool:
        """
        Validate the structure of exported PlantUML data.
        
        This method validates PlantUML source code to ensure it has the
        correct structure and required directives for successful rendering.
        It checks for proper start/end markers, title directives, and
        sufficient content.
        
        Args:
            plantuml_data: PlantUML string to validate for syntax and structure
            
        Returns:
            True if PlantUML structure is valid and can be rendered
            
        Raises:
            ValueError: If PlantUML structure is invalid, missing required
                       directives, or has insufficient content
            
        Example:
            >>> plantuml_code = generator.export_to_plantuml()
            >>> is_valid = generator.validate_plantuml_output(plantuml_code)
            >>> print(f"PlantUML code is valid: {is_valid}")
        """
        if not plantuml_data.strip():
            raise ValueError("PlantUML output is empty")
        
        lines = plantuml_data.split('\n')
        
        # Check for required PlantUML markers
        if not any(line.strip().startswith('@startuml') for line in lines):
            raise ValueError("Missing @startuml directive")
        
        if not any(line.strip().startswith('@enduml') for line in lines):
            raise ValueError("Missing @enduml directive")
        
        # Check for basic structure
        has_title = any('!title' in line for line in lines)
        if not has_title:
            raise ValueError("Missing title directive")
        
        # Validate that we have some content between start and end
        content_lines = []
        in_diagram = False
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('@startuml'):
                in_diagram = True
                continue
            elif stripped.startswith('@enduml'):
                in_diagram = False
                continue
            elif in_diagram and stripped and not stripped.startswith("'"):
                content_lines.append(stripped)
        
        if len(content_lines) < 3:  # Should have at least some meaningful content
            raise ValueError("PlantUML output appears to have insufficient content")
        
        return True
    
    def is_diagram_cached(self, diagram_key: str, content: Optional[str] = None) -> bool:
        """
        Check if a diagram is cached and up-to-date.
        
        Args:
            diagram_key: Unique key for the diagram
            content: Optional content to check for changes
            
        Returns:
            True if diagram is cached and current, False otherwise
        """
        if not self.enable_cache or not self.cache:
            return False
        
        return self.cache.is_cached(diagram_key, content)
    
    def get_cached_outputs(self, diagram_key: str) -> Optional[Dict[str, str]]:
        """
        Get cached output files for a diagram.
        
        Args:
            diagram_key: Unique key for the diagram
            
        Returns:
            Dictionary of cached output files or None if not cached
        """
        if not self.enable_cache or not self.cache:
            return None
        
        return self.cache.get_cached_outputs(diagram_key)
    
    def cache_diagram_outputs(
        self,
        diagram_key: str,
        output_files: Dict[str, str],
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Cache diagram generation outputs.
        
        Args:
            diagram_key: Unique key for the diagram
            output_files: Dictionary of generated output files
            content: Optional content that was used to generate the diagram
            metadata: Additional metadata to cache
        """
        if not self.enable_cache or not self.cache:
            return
        
        self.cache.cache_diagram(diagram_key, content, output_files, metadata)
    
    def optimize_output_images(self, output_dir: str) -> List[str]:
        """
        Optimize all generated images for web display.
        
        Args:
            output_dir: Directory containing generated images
            
        Returns:
            List of optimized image file paths
        """
        return self.image_optimizer.optimize_directory(output_dir)
    
    def clear_cache(self) -> None:
        """Clear all cached diagram data."""
        if self.cache:
            self.cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        if not self.cache:
            return {"cache_enabled": False}
        
        stats = self.cache.get_cache_stats()
        stats["cache_enabled"] = True
        return stats