"""
Base diagram generator class for creating pystructurizr diagrams.

This module provides the core DiagramGenerator class that handles workspace creation,
view management, and export functionality for architectural diagrams.
"""

from typing import Dict, List, Optional, Any
import json
from datetime import datetime
from dataclasses import dataclass

from pystructurizr.dsl import Workspace, Model, Person, SoftwareSystem, Container, Component, View


@dataclass
class DiagramConfig:
    """Configuration for diagram generation."""
    name: str
    description: str
    version: str = "1.0.0"
    author: str = "Architecture Team"
    output_formats: List[str] = None

    def __post_init__(self) -> None:
        if self.output_formats is None:
            self.output_formats = ['json', 'plantuml']


@dataclass
class DiagramMetadata:
    """Metadata for generated diagrams."""
    title: str
    description: str
    diagram_type: str
    last_updated: datetime
    file_path: str
    output_files: Dict[str, str] = None

    def __post_init__(self) -> None:
        if self.output_files is None:
            self.output_files = {}


class DiagramGenerator:
    """
    Base class for generating architectural diagrams using pystructurizr.
    
    This class provides methods for creating workspaces, adding different types of views,
    and exporting diagrams to various formats.
    """

    def __init__(self, config: DiagramConfig) -> None:
        """
        Initialize the diagram generator with configuration.
        
        Args:
            config: Configuration object containing diagram settings
        """
        self.config = config
        self.workspace: Optional[Workspace] = None
        self._metadata: List[DiagramMetadata] = []

    def create_workspace(self) -> Workspace:
        """
        Create and configure a new pystructurizr workspace.
        
        Returns:
            Configured Workspace instance
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
        
        Args:
            software_system: The software system to create the view for
            title: Title of the view
            description: Description of the view
            key: Optional key for the view (auto-generated if not provided)
            
        Returns:
            Created SystemContextView instance
        """
        if not self.workspace:
            raise ValueError("Workspace must be created before adding views")
            
        if key is None:
            key = f"SystemContext-{software_system.name.replace(' ', '')}"
            
        # Create system context view using pystructurizr DSL
        view = self.workspace.SystemContextView(
            software_system=software_system,
            key=key,
            title=title,
            description=description
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
        
        Args:
            software_system: The software system to create the view for
            title: Title of the view
            description: Description of the view
            key: Optional key for the view (auto-generated if not provided)
            
        Returns:
            Created ContainerView instance
        """
        if not self.workspace:
            raise ValueError("Workspace must be created before adding views")
            
        if key is None:
            key = f"Container-{software_system.name.replace(' ', '')}"
            
        # Create container view using pystructurizr DSL
        view = self.workspace.ContainerView(
            software_system=software_system,
            key=key,
            title=title,
            description=description
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
        
        Args:
            container: The container to create the view for
            title: Title of the view
            description: Description of the view
            key: Optional key for the view (auto-generated if not provided)
            
        Returns:
            Created ComponentView instance
        """
        if not self.workspace:
            raise ValueError("Workspace must be created before adding views")
            
        if key is None:
            key = f"Component-{container.name.replace(' ', '')}"
            
        # Create component view using pystructurizr DSL
        view = self.workspace.ComponentView(
            container=container,
            key=key,
            title=title,
            description=description
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
        Export the workspace to JSON format.
        
        Returns:
            JSON string representation of the workspace
            
        Raises:
            ValueError: If workspace has not been created
        """
        if not self.workspace:
            raise ValueError("Workspace must be created before export")
            
        # Use pystructurizr's built-in dump functionality
        workspace_data = self.workspace.dump()
        
        # Add our custom metadata
        if isinstance(workspace_data, dict):
            workspace_data["metadata"] = [
                {
                    "title": meta.title,
                    "description": meta.description,
                    "type": meta.diagram_type,
                    "lastUpdated": meta.last_updated.isoformat(),
                    "filePath": meta.file_path
                }
                for meta in self._metadata
            ]
        
        return json.dumps(workspace_data, indent=2)

    def export_to_plantuml(self) -> str:
        """
        Export the workspace to PlantUML format.
        
        Returns:
            PlantUML string representation of all views
            
        Raises:
            ValueError: If workspace has not been created
        """
        if not self.workspace:
            raise ValueError("Workspace must be created before export")
            
        # Basic PlantUML export - this would need to be enhanced
        # based on the actual pystructurizr DSL capabilities
        plantuml_output = []
        
        # Add header
        plantuml_output.append("@startuml")
        plantuml_output.append(f"!title {self.config.name}")
        plantuml_output.append("")
        
        # Add basic structure
        plantuml_output.append("' Generated from pystructurizr workspace")
        plantuml_output.append("' This is a simplified PlantUML export")
        plantuml_output.append("")
        
        # Add metadata as comments
        for meta in self._metadata:
            plantuml_output.append(f"' View: {meta.title}")
            plantuml_output.append(f"' Type: {meta.diagram_type}")
            plantuml_output.append(f"' Description: {meta.description}")
            plantuml_output.append("")
        
        plantuml_output.append("@enduml")
        
        return "\n".join(plantuml_output)

    def get_metadata(self) -> List[DiagramMetadata]:
        """
        Get metadata for all generated diagrams.
        
        Returns:
            List of DiagramMetadata objects
        """
        return self._metadata.copy()