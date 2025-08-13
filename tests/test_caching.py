"""
Tests for diagram caching and performance optimization functionality.

This module tests the caching system, image optimization, and performance
improvements for the diagram generation workflow.
"""

import pytest
import json
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

from src.diagrams.cache import DiagramCache, CacheEntry, ImageOptimizer, create_github_actions_cache_config
from src.diagrams.generator import DiagramGenerator, DiagramConfig


class TestDiagramCache:
    """Test the diagram caching system."""
    
    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary cache directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def cache(self, temp_cache_dir):
        """Create a DiagramCache instance with temporary directory."""
        return DiagramCache(temp_cache_dir)
    
    def test_cache_initialization(self, temp_cache_dir):
        """Test cache initialization and directory creation."""
        cache = DiagramCache(temp_cache_dir)
        
        assert cache.cache_dir.exists()
        assert cache.cache_dir.is_dir()
        assert cache.cache_file == cache.cache_dir / "diagram_cache.json"
        assert isinstance(cache.cache_data, dict)
    
    def test_cache_entry_serialization(self):
        """Test CacheEntry serialization and deserialization."""
        entry = CacheEntry(
            file_path="test.py",
            content_hash="abc123",
            last_modified=datetime(2023, 1, 1, 12, 0, 0),
            output_files={"png": "test.png"},
            metadata={"type": "system_context"}
        )
        
        # Test to_dict
        data = entry.to_dict()
        assert data["file_path"] == "test.py"
        assert data["content_hash"] == "abc123"
        assert data["last_modified"] == "2023-01-01T12:00:00"
        assert data["output_files"] == {"png": "test.png"}
        assert data["metadata"] == {"type": "system_context"}
        
        # Test from_dict
        restored = CacheEntry.from_dict(data)
        assert restored.file_path == entry.file_path
        assert restored.content_hash == entry.content_hash
        assert restored.last_modified == entry.last_modified
        assert restored.output_files == entry.output_files
        assert restored.metadata == entry.metadata
    
    def test_content_hash_calculation(self, cache):
        """Test content hash calculation."""
        content1 = "test content"
        content2 = "different content"
        content3 = "test content"  # Same as content1
        
        hash1 = cache._calculate_content_hash(content1)
        hash2 = cache._calculate_content_hash(content2)
        hash3 = cache._calculate_content_hash(content3)
        
        assert hash1 != hash2  # Different content should have different hashes
        assert hash1 == hash3  # Same content should have same hash
        assert len(hash1) == 64  # SHA-256 produces 64-character hex string
    
    def test_file_hash_calculation(self, cache, temp_cache_dir):
        """Test file hash calculation."""
        test_file = Path(temp_cache_dir) / "test.txt"
        test_file.write_text("test content")
        
        hash1 = cache._calculate_file_hash(test_file)
        assert len(hash1) == 64
        
        # Same file should produce same hash
        hash2 = cache._calculate_file_hash(test_file)
        assert hash1 == hash2
        
        # Different content should produce different hash
        test_file.write_text("different content")
        hash3 = cache._calculate_file_hash(test_file)
        assert hash1 != hash3
        
        # Non-existent file should return empty string
        non_existent = Path(temp_cache_dir) / "nonexistent.txt"
        hash4 = cache._calculate_file_hash(non_existent)
        assert hash4 == ""
    
    def test_cache_diagram(self, cache, temp_cache_dir):
        """Test caching a diagram."""
        test_file = Path(temp_cache_dir) / "test.py"
        test_file.write_text("diagram content")
        
        output_files = {"json": "test.json", "png": "test.png"}
        metadata = {"type": "system_context", "title": "Test Diagram"}
        
        cache.cache_diagram(
            str(test_file),
            output_files=output_files,
            metadata=metadata
        )
        
        # Check that cache entry was created
        cache_key = str(test_file.resolve())
        assert cache_key in cache.cache_data
        
        entry = cache.cache_data[cache_key]
        assert entry.file_path == str(test_file)
        assert entry.output_files == output_files
        assert entry.metadata == metadata
        assert len(entry.content_hash) == 64
    
    def test_is_cached_with_file(self, cache, temp_cache_dir):
        """Test cache checking with file."""
        test_file = Path(temp_cache_dir) / "test.py"
        test_file.write_text("original content")
        
        # Initially not cached
        assert not cache.is_cached(str(test_file))
        
        # Cache the file
        cache.cache_diagram(str(test_file), output_files={"json": "test.json"})
        
        # Now should be cached
        assert cache.is_cached(str(test_file))
        
        # Modify file - should no longer be cached
        time.sleep(0.1)  # Ensure different modification time
        test_file.write_text("modified content")
        assert not cache.is_cached(str(test_file))
    
    def test_is_cached_with_content(self, cache, temp_cache_dir):
        """Test cache checking with content string."""
        test_file = Path(temp_cache_dir) / "test.py"
        content = "test content"
        
        # Initially not cached
        assert not cache.is_cached(str(test_file), content)
        
        # Cache with content
        cache.cache_diagram(str(test_file), content=content, output_files={"json": "test.json"})
        
        # Should be cached with same content
        assert cache.is_cached(str(test_file), content)
        
        # Should not be cached with different content
        assert not cache.is_cached(str(test_file), "different content")
    
    def test_get_cached_outputs(self, cache, temp_cache_dir):
        """Test retrieving cached outputs."""
        test_file = Path(temp_cache_dir) / "test.py"
        test_file.write_text("content")
        
        output_files = {"json": "test.json", "png": "test.png"}
        
        # Initially no cached outputs
        assert cache.get_cached_outputs(str(test_file)) is None
        
        # Cache the diagram
        cache.cache_diagram(str(test_file), output_files=output_files)
        
        # Should return cached outputs
        cached = cache.get_cached_outputs(str(test_file))
        assert cached == output_files
    
    def test_cache_persistence(self, temp_cache_dir):
        """Test that cache persists across instances."""
        # Create first cache instance and add entry
        cache1 = DiagramCache(temp_cache_dir)
        test_file = Path(temp_cache_dir) / "test.py"
        test_file.write_text("content")
        
        cache1.cache_diagram(str(test_file), output_files={"json": "test.json"})
        
        # Create second cache instance - should load existing data
        cache2 = DiagramCache(temp_cache_dir)
        
        assert cache2.is_cached(str(test_file))
        assert cache2.get_cached_outputs(str(test_file)) == {"json": "test.json"}
    
    def test_invalidate_cache(self, cache, temp_cache_dir):
        """Test cache invalidation."""
        test_file = Path(temp_cache_dir) / "test.py"
        test_file.write_text("content")
        
        # Cache the file
        cache.cache_diagram(str(test_file), output_files={"json": "test.json"})
        assert cache.is_cached(str(test_file))
        
        # Invalidate cache
        cache.invalidate(str(test_file))
        assert not cache.is_cached(str(test_file))
    
    def test_clear_cache(self, cache, temp_cache_dir):
        """Test clearing all cache entries."""
        test_file1 = Path(temp_cache_dir) / "test1.py"
        test_file2 = Path(temp_cache_dir) / "test2.py"
        test_file1.write_text("content1")
        test_file2.write_text("content2")
        
        # Cache multiple files
        cache.cache_diagram(str(test_file1), output_files={"json": "test1.json"})
        cache.cache_diagram(str(test_file2), output_files={"json": "test2.json"})
        
        assert cache.is_cached(str(test_file1))
        assert cache.is_cached(str(test_file2))
        
        # Clear cache
        cache.clear()
        
        assert not cache.is_cached(str(test_file1))
        assert not cache.is_cached(str(test_file2))
        assert len(cache.cache_data) == 0
    
    def test_cleanup_stale_entries(self, cache, temp_cache_dir):
        """Test cleanup of stale cache entries."""
        test_file1 = Path(temp_cache_dir) / "test1.py"
        test_file2 = Path(temp_cache_dir) / "test2.py"
        test_file1.write_text("content1")
        test_file2.write_text("content2")
        
        # Cache both files
        cache.cache_diagram(str(test_file1), output_files={"json": "test1.json"})
        cache.cache_diagram(str(test_file2), output_files={"json": "test2.json"})
        
        assert len(cache.cache_data) == 2
        
        # Delete one file
        test_file1.unlink()
        
        # Cleanup should remove the stale entry
        removed = cache.cleanup_stale_entries()
        assert removed == 1
        assert len(cache.cache_data) == 1
        assert cache.is_cached(str(test_file2))
    
    def test_cache_stats(self, cache, temp_cache_dir):
        """Test cache statistics."""
        stats = cache.get_cache_stats()
        
        assert "total_entries" in stats
        assert "total_outputs" in stats
        assert "cache_file_size" in stats
        assert "cache_file_path" in stats
        
        assert stats["total_entries"] == 0
        assert stats["total_outputs"] == 0
        
        # Add some cache entries
        test_file = Path(temp_cache_dir) / "test.py"
        test_file.write_text("content")
        
        cache.cache_diagram(str(test_file), output_files={"json": "test.json", "png": "test.png"})
        
        stats = cache.get_cache_stats()
        assert stats["total_entries"] == 1
        assert stats["total_outputs"] == 2


class TestImageOptimizer:
    """Test the image optimization functionality."""
    
    @pytest.fixture
    def optimizer(self):
        """Create an ImageOptimizer instance."""
        return ImageOptimizer()
    
    @pytest.fixture
    def temp_images_dir(self):
        """Create a temporary directory with test images."""
        with tempfile.TemporaryDirectory() as temp_dir:
            images_dir = Path(temp_dir)
            
            # Create test files
            (images_dir / "test.png").write_text("fake png content")
            (images_dir / "test.jpg").write_text("fake jpg content")
            (images_dir / "test.svg").write_text("<svg>fake svg</svg>")
            (images_dir / "test.txt").write_text("not an image")
            
            yield images_dir
    
    def test_optimizer_initialization(self, optimizer):
        """Test optimizer initialization."""
        assert optimizer.supported_formats == {'.png', '.jpg', '.jpeg', '.svg'}
    
    def test_optimize_image_svg(self, optimizer, temp_images_dir):
        """Test SVG image optimization (should just copy)."""
        svg_file = temp_images_dir / "test.svg"
        result = optimizer.optimize_image(str(svg_file))
        
        assert result == str(svg_file)
        assert svg_file.exists()
    
    def test_optimize_image_nonexistent(self, optimizer):
        """Test optimization of non-existent image."""
        result = optimizer.optimize_image("nonexistent.png")
        assert result is None
    
    def test_optimize_image_unsupported_format(self, optimizer, temp_images_dir):
        """Test optimization of unsupported format."""
        txt_file = temp_images_dir / "test.txt"
        result = optimizer.optimize_image(str(txt_file))
        
        assert result == str(txt_file)  # Should return original path
    
    def test_optimize_directory(self, optimizer, temp_images_dir):
        """Test optimizing all images in a directory."""
        results = optimizer.optimize_directory(str(temp_images_dir))
        
        # Should process PNG, JPG, and SVG files
        assert len(results) == 3
        
        # All results should be valid paths
        for result in results:
            assert Path(result).exists()
    
    def test_optimize_directory_nonexistent(self, optimizer):
        """Test optimizing non-existent directory."""
        results = optimizer.optimize_directory("nonexistent")
        assert results == []


class TestDiagramGeneratorCaching:
    """Test caching integration with DiagramGenerator."""
    
    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return DiagramConfig(
            name="Test System",
            description="Test system for caching",
            version="1.0.0",
            author="Test Suite"
        )
    
    def test_generator_with_caching_enabled(self, config):
        """Test generator with caching enabled."""
        generator = DiagramGenerator(config, enable_cache=True)
        
        assert generator.enable_cache is True
        assert generator.cache is not None
        assert generator.image_optimizer is not None
    
    def test_generator_with_caching_disabled(self, config):
        """Test generator with caching disabled."""
        generator = DiagramGenerator(config, enable_cache=False)
        
        assert generator.enable_cache is False
        assert generator.cache is None
        assert generator.image_optimizer is not None
    
    def test_cache_methods_with_caching_disabled(self, config):
        """Test cache methods when caching is disabled."""
        generator = DiagramGenerator(config, enable_cache=False)
        
        # All cache methods should handle disabled cache gracefully
        assert not generator.is_diagram_cached("test")
        assert generator.get_cached_outputs("test") is None
        
        # These should not raise errors
        generator.cache_diagram_outputs("test", {})
        generator.clear_cache()
        
        stats = generator.get_cache_stats()
        assert stats == {"cache_enabled": False}
    
    def test_cache_methods_with_caching_enabled(self, config):
        """Test cache methods when caching is enabled."""
        generator = DiagramGenerator(config, enable_cache=True)
        
        # Clear any existing cache
        generator.clear_cache()
        
        # Initially nothing cached
        assert not generator.is_diagram_cached("test")
        assert generator.get_cached_outputs("test") is None
        
        # Cache something
        output_files = {"json": "test.json"}
        generator.cache_diagram_outputs("test", output_files, content="test content")
        
        # Should now be cached
        assert generator.is_diagram_cached("test", "test content")
        assert generator.get_cached_outputs("test") == output_files
        
        # Get stats
        stats = generator.get_cache_stats()
        assert stats["cache_enabled"] is True
        assert stats["total_entries"] == 1
    
    def test_image_optimization(self, config):
        """Test image optimization functionality."""
        generator = DiagramGenerator(config)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            images_dir = Path(temp_dir)
            (images_dir / "test.svg").write_text("<svg>test</svg>")
            
            results = generator.optimize_output_images(str(images_dir))
            assert len(results) == 1
            assert results[0] == str(images_dir / "test.svg")


class TestGitHubActionsCacheConfig:
    """Test GitHub Actions cache configuration."""
    
    def test_cache_config_structure(self):
        """Test that cache config has correct structure."""
        config = create_github_actions_cache_config()
        
        assert "cache_paths" in config
        assert "cache_key_prefix" in config
        assert "restore_keys" in config
        
        assert isinstance(config["cache_paths"], list)
        assert isinstance(config["restore_keys"], list)
        assert isinstance(config["cache_key_prefix"], str)
    
    def test_cache_config_paths(self):
        """Test that cache config includes expected paths."""
        config = create_github_actions_cache_config()
        
        expected_paths = ["~/.cache/uv", ".cache/", "docs/images/", "plantuml.jar"]
        
        for path in expected_paths:
            assert path in config["cache_paths"]
    
    def test_cache_config_keys(self):
        """Test cache key configuration."""
        config = create_github_actions_cache_config()
        
        assert config["cache_key_prefix"] == "pystructurizr-diagrams"
        assert "pystructurizr-diagrams-" in config["restore_keys"]
        assert "pystructurizr-" in config["restore_keys"]


class TestCachingPerformance:
    """Test performance improvements from caching."""
    
    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return DiagramConfig(
            name="Performance Test",
            description="Testing caching performance",
            version="1.0.0",
            author="Test Suite"
        )
    
    def test_cache_hit_performance(self, config):
        """Test that cache hits are faster than cache misses."""
        generator = DiagramGenerator(config, enable_cache=True)
        
        # Simulate expensive operation
        def expensive_operation():
            time.sleep(0.01)  # Simulate work
            return {"json": "output.json"}
        
        diagram_key = "performance_test"
        content = "test content for performance"
        
        # First call - cache miss (should be slower)
        start_time = time.time()
        
        if not generator.is_diagram_cached(diagram_key, content):
            outputs = expensive_operation()
            generator.cache_diagram_outputs(diagram_key, outputs, content)
        else:
            outputs = generator.get_cached_outputs(diagram_key)
        
        first_call_time = time.time() - start_time
        
        # Second call - cache hit (should be faster)
        start_time = time.time()
        
        if not generator.is_diagram_cached(diagram_key, content):
            outputs = expensive_operation()
            generator.cache_diagram_outputs(diagram_key, outputs, content)
        else:
            outputs = generator.get_cached_outputs(diagram_key)
        
        second_call_time = time.time() - start_time
        
        # Cache hit should be significantly faster
        assert second_call_time < first_call_time
        assert outputs == {"json": "output.json"}
    
    def test_cache_memory_efficiency(self, config):
        """Test that cache doesn't consume excessive memory."""
        generator = DiagramGenerator(config, enable_cache=True)
        
        # Clear any existing cache
        generator.clear_cache()
        
        # Add many cache entries
        for i in range(100):
            generator.cache_diagram_outputs(
                f"diagram_{i}",
                {"json": f"output_{i}.json"},
                content=f"content_{i}"
            )
        
        stats = generator.get_cache_stats()
        assert stats["total_entries"] == 100
        
        # Cache file should exist and be reasonable size
        cache_file_size = stats["cache_file_size"]
        assert cache_file_size > 0
        assert cache_file_size < 1024 * 1024  # Should be less than 1MB for 100 entries