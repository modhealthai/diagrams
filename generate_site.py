#!/usr/bin/env python3
"""
Script to generate the static site from diagram metadata.

This script can be run manually or as part of the GitHub Actions workflow
to generate the complete static site for GitHub Pages.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from site_generator import SiteGenerator, SiteConfig


def main():
    """Generate the static site."""
    print("Generating static site for pystructurizr diagrams...")
    
    # Configuration
    config = SiteConfig(
        title="Architecture Diagrams",
        description="Explore our system architecture through interactive diagrams generated with pystructurizr",
        base_url=os.environ.get("GITHUB_PAGES_URL", ""),
        theme="default"
    )
    
    # Create site generator
    generator = SiteGenerator(
        templates_dir="templates",
        output_dir="docs",
        diagrams_dir="docs",
        config=config
    )
    
    try:
        # Validate templates first
        print("Validating templates...")
        generator.validate_templates()
        print("✓ Templates validated successfully")
        
        # Generate the site
        print("Generating site...")
        generator.generate_site()
        print("✓ Site generated successfully")
        
        # Generate sitemap if base URL is provided
        if config.base_url:
            print("Generating sitemap...")
            generator.generate_sitemap()
            print("✓ Sitemap generated successfully")
        
        print(f"\nSite generation completed!")
        print(f"Output directory: {generator.output_dir}")
        print(f"Total diagrams processed: {len(generator.diagrams)}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error during site generation: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())