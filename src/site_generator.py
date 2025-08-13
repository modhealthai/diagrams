"""
Static site generator for pystructurizr diagrams.

This module generates HTML pages from diagram metadata and templates,
creating a complete static site for GitHub Pages deployment. It provides
a comprehensive site generation system with navigation, responsive design,
and automatic content organization.

The generator processes diagram metadata and creates:
- Homepage with featured and recent diagrams
- Diagram listing pages with categorization
- Individual diagram pages with related content
- Navigation structure and sitemap

Example:
    Basic usage of the site generator:
    
    >>> from site_generator import SiteGenerator, SiteConfig
    >>> config = SiteConfig(title="My Architecture", base_url="https://example.com")
    >>> generator = SiteGenerator(config=config)
    >>> generator.generate_site()
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from jinja2 import Environment, FileSystemLoader, select_autoescape

from diagrams.generator import DiagramMetadata


@dataclass
class SiteConfig:
    """
    Configuration for static site generation.
    
    This class holds all configuration parameters needed to generate
    the static site including site metadata, URLs, theming, and navigation.
    
    Attributes:
        title: The title of the website
        description: A description of the site for SEO and display
        base_url: Base URL for the site (used for sitemap and absolute links)
        theme: Theme name for styling (currently supports "default")
        navigation: List of navigation items with name and url
    
    Example:
        >>> config = SiteConfig(
        ...     title="My Architecture Documentation",
        ...     description="Comprehensive system architecture diagrams",
        ...     base_url="https://mycompany.github.io/architecture",
        ...     theme="corporate"
        ... )
    """
    title: str = "Architecture Diagrams"
    description: str = "Explore our system architecture through interactive diagrams"
    base_url: str = ""
    theme: str = "default"
    navigation: Optional[List[Dict[str, str]]] = None

    def __post_init__(self) -> None:
        """Initialize default navigation if none provided."""
        if self.navigation is None:
            self.navigation = [
                {"name": "Home", "url": "/"},
                {"name": "All Diagrams", "url": "/diagrams/"}
            ]


@dataclass
class SiteStats:
    """
    Statistics about the generated site.
    
    This class holds statistical information about the generated site
    including counts of different diagram types and last update times.
    
    Attributes:
        total_diagrams: Total number of diagrams in the site
        system_contexts: Number of system context diagrams
        containers: Number of container diagrams
        components: Number of component diagrams
        last_updated: Timestamp of the most recently updated diagram
    
    Example:
        >>> stats = SiteStats(
        ...     total_diagrams=15,
        ...     system_contexts=3,
        ...     containers=7,
        ...     components=5,
        ...     last_updated=datetime.now()
        ... )
    """
    total_diagrams: int = 0
    system_contexts: int = 0
    containers: int = 0
    components: int = 0
    last_updated: Optional[datetime] = None


class SiteGenerator:
    """
    Generates static HTML site from diagram metadata and templates.
    
    This class handles the complete site generation process including:
    - Loading diagram metadata from JSON files
    - Processing templates with Jinja2
    - Creating navigation structure
    - Generating individual diagram pages
    - Creating index and listing pages
    - Copying static assets
    - Generating sitemaps
    
    The generator uses Jinja2 templates for flexible HTML generation and
    supports responsive design, SEO optimization, and accessibility features.
    
    Attributes:
        templates_dir: Path to directory containing Jinja2 templates
        output_dir: Path to directory where generated HTML will be written
        diagrams_dir: Path to directory containing diagram metadata and outputs
        config: Site configuration object
        jinja_env: Jinja2 environment for template processing
        diagrams: List of loaded diagram metadata
        stats: Site statistics
    
    Example:
        >>> config = SiteConfig(title="My Docs", base_url="https://example.com")
        >>> generator = SiteGenerator(
        ...     templates_dir="templates",
        ...     output_dir="site",
        ...     config=config
        ... )
        >>> generator.generate_site()
    """

    def __init__(
        self,
        templates_dir: str = "templates",
        output_dir: str = "docs",
        diagrams_dir: str = "docs",
        config: Optional[SiteConfig] = None
    ) -> None:
        """
        Initialize the site generator.
        
        Sets up the site generator with the specified directories and configuration.
        Initializes the Jinja2 environment with appropriate settings for HTML
        generation and sets up custom filters.
        
        Args:
            templates_dir: Directory containing Jinja2 templates (base.html, index.html, etc.)
            output_dir: Directory where generated HTML will be written
            diagrams_dir: Directory containing diagram metadata and output files
            config: Site configuration object. If None, default config will be used
            
        Example:
            >>> generator = SiteGenerator(
            ...     templates_dir="my_templates",
            ...     output_dir="public",
            ...     diagrams_dir="diagrams",
            ...     config=SiteConfig(title="My Architecture")
            ... )
        """
        self.templates_dir = Path(templates_dir)
        self.output_dir = Path(output_dir)
        self.diagrams_dir = Path(diagrams_dir)
        self.config = config or SiteConfig()
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Add custom filters
        self.jinja_env.filters['replace'] = lambda s, old, new: s.replace(old, new)
        
        self.diagrams: List[DiagramMetadata] = []
        self.stats = SiteStats()

    def load_diagram_metadata(self) -> None:
        """
        Load diagram metadata from JSON files in the diagrams directory.
        
        Scans for diagram_metadata.json files and individual diagram JSON exports
        to build a complete list of available diagrams with their metadata.
        """
        self.diagrams = []
        
        # Look for diagram metadata file
        metadata_file = self.diagrams_dir / "diagram_metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata_data = json.load(f)
                    
                # Process metadata from the structured format
                if "metadata" in metadata_data and "diagrams" in metadata_data["metadata"]:
                    for diagram_data in metadata_data["metadata"]["diagrams"]:
                        diagram = DiagramMetadata(
                            title=diagram_data["title"],
                            description=diagram_data["description"],
                            diagram_type=diagram_data["type"],
                            last_updated=datetime.fromisoformat(diagram_data["lastUpdated"]),
                            file_path=diagram_data["filePath"],
                            output_files=diagram_data.get("outputFiles", {})
                        )
                        self.diagrams.append(diagram)
                        
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Warning: Could not load diagram metadata: {e}")
        
        # Also scan for individual JSON files
        for json_file in self.diagrams_dir.glob("*.json"):
            if json_file.name == "diagram_metadata.json":
                continue
                
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Check if this is a diagram export file
                if "workspace" in data and "metadata" in data:
                    workspace = data["workspace"]
                    metadata = data["metadata"]
                    
                    if "diagrams" in metadata:
                        for diagram_data in metadata["diagrams"]:
                            # Check if we already have this diagram
                            existing = next(
                                (d for d in self.diagrams if d.file_path == diagram_data["filePath"]),
                                None
                            )
                            
                            if not existing:
                                diagram = DiagramMetadata(
                                    title=diagram_data["title"],
                                    description=diagram_data["description"],
                                    diagram_type=diagram_data["type"],
                                    last_updated=datetime.fromisoformat(diagram_data["lastUpdated"]),
                                    file_path=diagram_data["filePath"],
                                    output_files=diagram_data.get("outputFiles", {})
                                )
                                self.diagrams.append(diagram)
                                
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Warning: Could not process {json_file}: {e}")
        
        # Update statistics
        self._calculate_stats()
        
        print(f"Loaded {len(self.diagrams)} diagrams")

    def _calculate_stats(self) -> None:
        """Calculate site statistics from loaded diagrams."""
        self.stats = SiteStats(
            total_diagrams=len(self.diagrams),
            system_contexts=len([d for d in self.diagrams if d.diagram_type == "system_context"]),
            containers=len([d for d in self.diagrams if d.diagram_type == "container"]),
            components=len([d for d in self.diagrams if d.diagram_type == "component"]),
            last_updated=max([d.last_updated for d in self.diagrams]) if self.diagrams else None
        )

    def generate_site(self) -> None:
        """
        Generate the complete static site.
        
        This method orchestrates the entire site generation process:
        1. Load diagram metadata
        2. Create output directory structure
        3. Generate index page
        4. Generate diagram listing page
        5. Generate individual diagram pages
        6. Copy static assets
        """
        print("Starting site generation...")
        
        # Load diagram data
        self.load_diagram_metadata()
        
        # Create output directory structure
        self._create_output_structure()
        
        # Generate pages
        self._generate_index_page()
        self._generate_diagrams_listing_page()
        self._generate_individual_diagram_pages()
        
        # Copy static assets if they exist
        self._copy_static_assets()
        
        print(f"Site generation complete. Generated {len(self.diagrams)} diagram pages.")

    def _create_output_structure(self) -> None:
        """Create the output directory structure."""
        # Create main output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create diagrams subdirectory
        diagrams_output_dir = self.output_dir / "diagrams"
        diagrams_output_dir.mkdir(exist_ok=True)
        
        print(f"Created output directory structure at {self.output_dir}")

    def _generate_index_page(self) -> None:
        """Generate the main index page."""
        template = self.jinja_env.get_template("index.html")
        
        # Get recent diagrams (last 6, sorted by date)
        recent_diagrams = sorted(
            self.diagrams,
            key=lambda d: d.last_updated,
            reverse=True
        )[:6]
        
        # Get featured diagrams (system context diagrams)
        featured_diagrams = [
            d for d in self.diagrams 
            if d.diagram_type == "system_context"
        ][:3]
        
        context = {
            "config": self.config,
            "stats": asdict(self.stats),
            "recent_diagrams": recent_diagrams,
            "featured_diagrams": featured_diagrams,
            "current_year": datetime.now().year
        }
        
        html_content = template.render(**context)
        
        output_file = self.output_dir / "index.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Generated index page: {output_file}")

    def _generate_diagrams_listing_page(self) -> None:
        """Generate the diagrams listing page."""
        template = self.jinja_env.get_template("diagrams.html")
        
        # Sort diagrams by name for the listing
        sorted_diagrams = sorted(self.diagrams, key=lambda d: d.title.lower())
        
        context = {
            "config": self.config,
            "diagrams": sorted_diagrams,
            "stats": asdict(self.stats),
            "current_year": datetime.now().year
        }
        
        html_content = template.render(**context)
        
        # Create diagrams directory and index
        diagrams_dir = self.output_dir / "diagrams"
        diagrams_dir.mkdir(exist_ok=True)
        
        output_file = diagrams_dir / "index.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Generated diagrams listing page: {output_file}")

    def _generate_individual_diagram_pages(self) -> None:
        """Generate individual pages for each diagram."""
        template = self.jinja_env.get_template("diagram.html")
        
        diagrams_dir = self.output_dir / "diagrams"
        
        for diagram in self.diagrams:
            # Find related diagrams (same type or from same source file)
            related_diagrams = self._find_related_diagrams(diagram)
            
            # Load PlantUML source if available
            plantuml_source = self._load_plantuml_source(diagram)
            
            context = {
                "config": self.config,
                "diagram": diagram,
                "related_diagrams": related_diagrams,
                "plantuml_source": plantuml_source,
                "current_year": datetime.now().year
            }
            
            html_content = template.render(**context)
            
            # Generate filename from diagram file path
            html_filename = diagram.file_path.replace('.py', '.html').replace('.json', '.html')
            if not html_filename.endswith('.html'):
                html_filename += '.html'
            
            output_file = diagrams_dir / html_filename
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"Generated diagram page: {output_file}")

    def _find_related_diagrams(self, current_diagram: DiagramMetadata) -> List[DiagramMetadata]:
        """
        Find diagrams related to the current one.
        
        Args:
            current_diagram: The diagram to find related diagrams for
            
        Returns:
            List of related diagrams (excluding the current one)
        """
        related = []
        
        # Find diagrams of the same type
        same_type = [
            d for d in self.diagrams 
            if d.diagram_type == current_diagram.diagram_type and d != current_diagram
        ]
        related.extend(same_type[:2])  # Limit to 2 of same type
        
        # Find diagrams from the same source file (if applicable)
        if hasattr(current_diagram, 'source_file'):
            same_source = [
                d for d in self.diagrams 
                if getattr(d, 'source_file', None) == getattr(current_diagram, 'source_file', None)
                and d != current_diagram
                and d not in related
            ]
            related.extend(same_source[:2])  # Limit to 2 from same source
        
        # Fill remaining slots with other diagrams
        if len(related) < 4:
            others = [
                d for d in self.diagrams 
                if d != current_diagram and d not in related
            ]
            # Sort by last updated, most recent first
            others.sort(key=lambda d: d.last_updated, reverse=True)
            related.extend(others[:4 - len(related)])
        
        return related

    def _load_plantuml_source(self, diagram: DiagramMetadata) -> Optional[str]:
        """
        Load PlantUML source code for a diagram if available.
        
        Args:
            diagram: The diagram to load PlantUML source for
            
        Returns:
            PlantUML source code or None if not available
        """
        if 'plantuml' in diagram.output_files:
            plantuml_file = Path(diagram.output_files['plantuml'])
            if plantuml_file.exists():
                try:
                    with open(plantuml_file, 'r', encoding='utf-8') as f:
                        return f.read()
                except Exception as e:
                    print(f"Warning: Could not load PlantUML source from {plantuml_file}: {e}")
        
        return None

    def _copy_static_assets(self) -> None:
        """Copy static assets like images and CSS files to the output directory."""
        # Copy diagram images and other outputs
        for diagram in self.diagrams:
            for format_type, file_path in diagram.output_files.items():
                source_file = Path(file_path)
                if source_file.exists():
                    # Determine destination path
                    if source_file.is_absolute():
                        # If absolute path, try to make it relative to diagrams_dir
                        try:
                            relative_path = source_file.relative_to(self.diagrams_dir)
                        except ValueError:
                            # If not under diagrams_dir, use just the filename
                            relative_path = source_file.name
                    else:
                        relative_path = source_file
                    
                    dest_file = self.output_dir / relative_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    try:
                        shutil.copy2(source_file, dest_file)
                        print(f"Copied asset: {source_file} -> {dest_file}")
                    except Exception as e:
                        print(f"Warning: Could not copy {source_file}: {e}")

    def create_navigation_structure(self) -> Dict[str, Any]:
        """
        Create navigation structure based on available diagrams.
        
        Returns:
            Dictionary containing navigation structure with categories and links
        """
        navigation = {
            "main": [
                {"name": "Home", "url": "/", "active": False},
                {"name": "All Diagrams", "url": "/diagrams/", "active": False}
            ],
            "categories": {}
        }
        
        # Group diagrams by type
        by_type = {}
        for diagram in self.diagrams:
            diagram_type = diagram.diagram_type
            if diagram_type not in by_type:
                by_type[diagram_type] = []
            by_type[diagram_type].append(diagram)
        
        # Create category navigation
        for diagram_type, diagrams in by_type.items():
            type_name = diagram_type.replace('_', ' ').title()
            navigation["categories"][diagram_type] = {
                "name": type_name,
                "count": len(diagrams),
                "diagrams": [
                    {
                        "name": d.title,
                        "url": f"/diagrams/{d.file_path.replace('.py', '.html').replace('.json', '.html')}",
                        "description": d.description[:100] + "..." if len(d.description) > 100 else d.description
                    }
                    for d in sorted(diagrams, key=lambda x: x.title)
                ]
            }
        
        return navigation

    def validate_templates(self) -> bool:
        """
        Validate that all required templates exist and are valid.
        
        Returns:
            True if all templates are valid
            
        Raises:
            FileNotFoundError: If required templates are missing
            Exception: If templates have syntax errors
        """
        required_templates = ["base.html", "index.html", "diagrams.html", "diagram.html"]
        
        for template_name in required_templates:
            template_path = self.templates_dir / template_name
            if not template_path.exists():
                raise FileNotFoundError(f"Required template not found: {template_path}")
            
            try:
                # Try to load the template to check for syntax errors
                self.jinja_env.get_template(template_name)
            except Exception as e:
                raise Exception(f"Template syntax error in {template_name}: {e}")
        
        print("All templates validated successfully")
        return True

    def generate_sitemap(self) -> None:
        """Generate a sitemap.xml file for the static site."""
        sitemap_content = ['<?xml version="1.0" encoding="UTF-8"?>']
        sitemap_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        
        base_url = self.config.base_url.rstrip('/')
        
        # Add main pages
        sitemap_content.extend([
            '  <url>',
            f'    <loc>{base_url}/</loc>',
            f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>',
            '    <changefreq>weekly</changefreq>',
            '    <priority>1.0</priority>',
            '  </url>',
            '  <url>',
            f'    <loc>{base_url}/diagrams/</loc>',
            f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>',
            '    <changefreq>weekly</changefreq>',
            '    <priority>0.8</priority>',
            '  </url>'
        ])
        
        # Add diagram pages
        for diagram in self.diagrams:
            html_filename = diagram.file_path.replace('.py', '.html').replace('.json', '.html')
            sitemap_content.extend([
                '  <url>',
                f'    <loc>{base_url}/diagrams/{html_filename}</loc>',
                f'    <lastmod>{diagram.last_updated.strftime("%Y-%m-%d")}</lastmod>',
                '    <changefreq>monthly</changefreq>',
                '    <priority>0.6</priority>',
                '  </url>'
            ])
        
        sitemap_content.append('</urlset>')
        
        sitemap_file = self.output_dir / "sitemap.xml"
        with open(sitemap_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sitemap_content))
        
        print(f"Generated sitemap: {sitemap_file}")


def main():
    """Main function to run the site generator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate static site from pystructurizr diagrams")
    parser.add_argument("--templates-dir", default="templates", help="Templates directory")
    parser.add_argument("--output-dir", default="docs", help="Output directory")
    parser.add_argument("--diagrams-dir", default="docs", help="Diagrams directory")
    parser.add_argument("--base-url", default="", help="Base URL for the site")
    parser.add_argument("--title", default="Architecture Diagrams", help="Site title")
    parser.add_argument("--description", default="Explore our system architecture through interactive diagrams", help="Site description")
    parser.add_argument("--validate-only", action="store_true", help="Only validate templates, don't generate site")
    
    args = parser.parse_args()
    
    # Create site configuration
    config = SiteConfig(
        title=args.title,
        description=args.description,
        base_url=args.base_url
    )
    
    # Create site generator
    generator = SiteGenerator(
        templates_dir=args.templates_dir,
        output_dir=args.output_dir,
        diagrams_dir=args.diagrams_dir,
        config=config
    )
    
    try:
        # Validate templates
        generator.validate_templates()
        
        if args.validate_only:
            print("Template validation completed successfully")
            return
        
        # Generate the site
        generator.generate_site()
        
        # Generate sitemap
        if config.base_url:
            generator.generate_sitemap()
        
        print("Site generation completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())