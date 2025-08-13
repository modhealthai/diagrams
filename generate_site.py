#!/usr/bin/env python3
"""
Optimized site generation script with caching support.

This script generates the static site with performance optimizations including
diagram caching, image optimization, and incremental builds.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from src.site_generator import SiteGenerator, SiteConfig
from src.diagrams.cache import DiagramCache, ImageOptimizer


def main():
    """Main entry point for the site generation script."""
    parser = argparse.ArgumentParser(
        description="Generate static site with diagram caching and optimization"
    )
    
    parser.add_argument(
        "--templates-dir",
        default="templates",
        help="Directory containing HTML templates"
    )
    
    parser.add_argument(
        "--output-dir", 
        default="docs",
        help="Output directory for generated site"
    )
    
    parser.add_argument(
        "--diagrams-dir",
        default="docs",
        help="Directory containing diagram files"
    )
    
    parser.add_argument(
        "--base-url",
        help="Base URL for the site (for sitemap generation)"
    )
    
    parser.add_argument(
        "--title",
        default="Architecture Documentation",
        help="Site title"
    )
    
    parser.add_argument(
        "--description", 
        default="System architecture documentation",
        help="Site description"
    )
    
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching for this run"
    )
    
    parser.add_argument(
        "--clear-cache",
        action="store_true", 
        help="Clear cache before generation"
    )
    
    parser.add_argument(
        "--optimize-images",
        action="store_true",
        help="Optimize images for web display"
    )
    
    parser.add_argument(
        "--cache-stats",
        action="store_true",
        help="Show cache statistics"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize cache if enabled
        cache = None
        if not args.no_cache:
            cache = DiagramCache()
            
            if args.clear_cache:
                print("Clearing cache...")
                cache.clear()
                print("✓ Cache cleared")
            
            if args.cache_stats:
                stats = cache.get_cache_stats()
                print(f"Cache statistics:")
                print(f"  Total entries: {stats['total_entries']}")
                print(f"  Total outputs: {stats['total_outputs']}")
                print(f"  Cache file size: {stats['cache_file_size']} bytes")
                print(f"  Cache file: {stats['cache_file_path']}")
                print()
        
        # Create site configuration
        config = SiteConfig(
            title=args.title,
            description=args.description,
            base_url=args.base_url or ""
        )
        
        # Initialize site generator
        generator = SiteGenerator(
            templates_dir=args.templates_dir,
            output_dir=args.output_dir,
            diagrams_dir=args.diagrams_dir,
            config=config
        )
        
        # Validate templates
        print("Validating templates...")
        if not generator.validate_templates():
            print("✗ Template validation failed")
            return 1
        print("✓ Templates validated")
        
        # Generate site
        print("Generating site...")
        generator.generate_site()
        
        # Generate sitemap if base URL provided
        if args.base_url:
            print("Generating sitemap...")
            generator.generate_sitemap()
            print("✓ Sitemap generated")
        
        # Optimize images if requested
        if args.optimize_images:
            print("Optimizing images...")
            optimizer = ImageOptimizer()
            
            images_dir = Path(args.output_dir) / "images"
            if images_dir.exists():
                optimized = optimizer.optimize_directory(str(images_dir))
                print(f"✓ Optimized {len(optimized)} images")
            else:
                print("No images directory found to optimize")
        
        # Show final statistics
        stats = generator.stats
        print(f"\n✓ Site generation complete!")
        print(f"  Total diagrams: {stats.total_diagrams}")
        print(f"  System contexts: {stats.system_contexts}")
        print(f"  Containers: {stats.containers}")
        print(f"  Components: {stats.components}")
        
        if cache:
            # Clean up stale cache entries
            removed = cache.cleanup_stale_entries()
            if removed > 0:
                print(f"  Cleaned up {removed} stale cache entries")
            
            # Show final cache stats
            if args.cache_stats:
                final_stats = cache.get_cache_stats()
                print(f"  Final cache entries: {final_stats['total_entries']}")
        
        return 0
        
    except Exception as e:
        print(f"✗ Error generating site: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())