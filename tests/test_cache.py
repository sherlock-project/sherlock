"""Tests for cache functionality."""

import pytest
import time
from sherlock_project.cache import SherlockCache
from sherlock_project.result import QueryStatus


@pytest.fixture
def cache(tmp_path):
    """Create temporary cache for testing."""
    cache_path = str(tmp_path / "test_cache.db")
    return SherlockCache(cache_path=cache_path, cache_duration=2)


def test_cache_set_and_get(cache):
    """Test basic cache set and get operations."""
    cache.set("testuser", "GitHub", QueryStatus.CLAIMED, "https://github.com/testuser")
    
    result = cache.get("testuser", "GitHub")
    assert result is not None
    assert result['status'] == QueryStatus.CLAIMED
    assert result['url'] == "https://github.com/testuser"


def test_cache_expiration(cache):
    """Test that cache entries expire correctly."""
    cache.set("testuser", "GitHub", QueryStatus.CLAIMED, "https://github.com/testuser")
    
    # Should be cached
    result = cache.get("testuser", "GitHub")
    assert result is not None
    
    # Wait for expiration (cache_duration is 2 seconds)
    time.sleep(3)
    
    # Should be expired
    result = cache.get("testuser", "GitHub")
    assert result is None


def test_cache_clear_all(cache):
    """Test clearing entire cache."""
    cache.set("user1", "GitHub", QueryStatus.CLAIMED, "https://github.com/user1")
    cache.set("user2", "Twitter", QueryStatus.AVAILABLE, None)
    
    cache.clear()
    
    assert cache.get("user1", "GitHub") is None
    assert cache.get("user2", "Twitter") is None


def test_cache_clear_username(cache):
    """Test clearing cache for specific username."""
    cache.set("user1", "GitHub", QueryStatus.CLAIMED, "https://github.com/user1")
    cache.set("user1", "Twitter", QueryStatus.AVAILABLE, None)
    cache.set("user2", "GitHub", QueryStatus.CLAIMED, "https://github.com/user2")
    
    cache.clear(username="user1")
    
    assert cache.get("user1", "GitHub") is None
    assert cache.get("user1", "Twitter") is None
    assert cache.get("user2", "GitHub") is not None


def test_cache_stats(cache):
    """Test cache statistics."""
    cache.set("user1", "GitHub", QueryStatus.CLAIMED, "https://github.com/user1")
    cache.set("user2", "Twitter", QueryStatus.AVAILABLE, None)
    
    stats = cache.get_stats()
    assert stats['total_entries'] == 2
    assert stats['valid_entries'] == 2
    assert stats['expired_entries'] == 0
