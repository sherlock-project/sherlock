"""Tests for cache functionality using mocks."""

import time
import unittest
from unittest.mock import MagicMock, Mock, patch

from sherlock_project.cache import SherlockCache
from sherlock_project.result import QueryStatus


class TestCacheInitialization(unittest.TestCase):
    """Test cache initialization and security."""
    
    @patch('sherlock_project.cache.Path.mkdir')
    @patch('sherlock_project.cache.sqlite3')
    @patch('sherlock_project.cache.user_cache_dir')
    def test_init_creates_database(
        self,
        mock_cache_dir: Mock,
        mock_sqlite: Mock,
        mock_mkdir: Mock
    ) -> None:
        """Test database initialization."""
        mock_cache_dir.return_value = "/home/user/.cache/sherlock"
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__.return_value = mock_conn
        mock_sqlite.connect.return_value = mock_conn
        
        cache = SherlockCache()
        
        assert cache is not None

        # Verify database operations
        assert mock_cursor.execute.call_count >= 2
        calls = [str(call) for call in mock_cursor.execute.call_args_list]
        assert any('CREATE TABLE' in str(call) for call in calls)
        assert any('CREATE INDEX' in str(call) for call in calls)
    
    def test_init_rejects_negative_duration(self) -> None:
        """Test cache_duration validation."""
        with self.assertRaises(ValueError) as cm:
            SherlockCache(cache_duration=0)
        self.assertIn("positive", str(cm.exception))
        
        with self.assertRaises(ValueError) as cm:
            SherlockCache(cache_duration=-100)
        self.assertIn("positive", str(cm.exception))
    
    @patch('sherlock_project.cache.Path.mkdir')
    @patch('sherlock_project.cache.sqlite3')
    @patch('sherlock_project.cache.user_cache_dir')
    def test_uses_platform_cache_dir(
        self,
        mock_cache_dir: Mock,
        mock_sqlite: Mock,
        mock_mkdir: Mock
    ) -> None:
        """Test platform-specific cache directory usage."""
        mock_cache_dir.return_value = "/home/user/.cache/sherlock"
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__.return_value = mock_conn
        mock_sqlite.connect.return_value = mock_conn
        
        cache = SherlockCache()
        
        # Verify platformdirs was called
        mock_cache_dir.assert_called_once_with("sherlock", "sherlock_project")
        
        # Verify cache path ends with cache.sqlite3
        assert cache.cache_path.endswith("cache.sqlite3")
        assert cache is not None


@patch('sherlock_project.cache.sqlite3')
@patch('sherlock_project.cache.Path.mkdir')
@patch('sherlock_project.cache.user_cache_dir')
class TestCacheOperations(unittest.TestCase):
    """Test cache get/set operations."""
    
    def test_set_uses_parameterized_query(
        self,
        mock_cache_dir: Mock,
        mock_mkdir: Mock,
        mock_sqlite: Mock
    ) -> None:
        """Test SQL injection protection via parameterized queries."""
        mock_cache_dir.return_value = "/home/user/.cache/sherlock"
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = None
        mock_sqlite.connect.return_value = mock_conn
        
        cache = SherlockCache(cache_duration=86400)
        cache.set("testuser", "GitHub", QueryStatus.CLAIMED, "https://github.com/testuser")
        
        # Verify parameterized query was used (prevents SQL injection)
        call_args = mock_cursor.execute.call_args
        self.assertIn("INSERT OR REPLACE", call_args[0][0])
        self.assertEqual(
            call_args[0][1][:4],
            ("testuser", "GitHub", "CLAIMED", "https://github.com/testuser")
        )
    
    def test_set_rejects_control_characters(
        self,
        mock_cache_dir: Mock,
        mock_mkdir: Mock,
        mock_sqlite: Mock
    ) -> None:
        """Test rejection of control characters in username."""
        mock_cache_dir.return_value = "/home/user/.cache/sherlock"
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__.return_value = mock_conn
        mock_sqlite.connect.return_value = mock_conn
        
        cache = SherlockCache(cache_duration=86400)
        
        # Test various control characters
        with self.assertRaises(ValueError) as cm:
            cache.set("user\x00name", "GitHub", QueryStatus.CLAIMED, "https://example.com")
        self.assertIn("null byte", str(cm.exception))
        
        with self.assertRaises(ValueError) as cm:
            cache.set("user\x01name", "GitHub", QueryStatus.CLAIMED, "https://example.com")
        self.assertIn("control characters", str(cm.exception))
    
    def test_set_rejects_null_bytes(
        self,
        mock_cache_dir: Mock,
        mock_mkdir: Mock,
        mock_sqlite: Mock
    ) -> None:
        """Test null byte rejection."""
        mock_cache_dir.return_value = "/home/user/.cache/sherlock"
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__.return_value = mock_conn
        mock_sqlite.connect.return_value = mock_conn
        
        cache = SherlockCache(cache_duration=86400)
        
        with self.assertRaises(ValueError) as cm:
            cache.set("user\x00injection", "GitHub", QueryStatus.CLAIMED, "https://example.com")
        self.assertIn("null byte", str(cm.exception))
    
    def test_set_validates_url_length(
        self,
        mock_cache_dir: Mock,
        mock_mkdir: Mock,
        mock_sqlite: Mock
    ) -> None:
        """Test URL length validation."""
        mock_cache_dir.return_value = "/home/user/.cache/sherlock"
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__.return_value = mock_conn
        mock_sqlite.connect.return_value = mock_conn
        
        cache = SherlockCache(cache_duration=86400)
        
        long_url = "https://example.com/" + ("a" * 3000)
        
        with self.assertRaises(ValueError) as cm:
            cache.set("user", "Site", QueryStatus.CLAIMED, long_url)
        self.assertIn("maximum length", str(cm.exception))
    
    def test_get_uses_parameterized_query(
        self,
        mock_cache_dir: Mock,
        mock_mkdir: Mock,
        mock_sqlite: Mock
    ) -> None:
        """Test SQL injection protection in get() via parameterized queries."""
        mock_cache_dir.return_value = "/home/user/.cache/sherlock"
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        current_time = int(time.time())
        mock_cursor.fetchone.return_value = (
            "CLAIMED",
            "https://github.com/testuser",
            current_time,
            86400
        )
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = None
        mock_sqlite.connect.return_value = mock_conn
        
        cache = SherlockCache(cache_duration=86400)
        result = cache.get("testuser", "GitHub")
        
        assert result is not None

        # Verify parameterized query (prevents SQL injection)
        call_args = mock_cursor.execute.call_args
        self.assertIn("SELECT", call_args[0][0])
        self.assertIn("WHERE username = ? AND site = ?", call_args[0][0])
        self.assertEqual(call_args[0][1], ("testuser", "GitHub"))
    
    def test_get_returns_none_for_expired(
        self,
        mock_cache_dir: Mock,
        mock_mkdir: Mock,
        mock_sqlite: Mock
    ) -> None:
        """Test expired entries return None."""
        mock_cache_dir.return_value = "/home/user/.cache/sherlock"
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        old_timestamp = int(time.time()) - (2 * 86400)
        mock_cursor.fetchone.return_value = (
            "CLAIMED",
            "https://github.com/testuser",
            old_timestamp,
            86400
        )
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = None
        mock_sqlite.connect.return_value = mock_conn
        
        cache = SherlockCache(cache_duration=86400)
        result = cache.get("testuser", "GitHub")
        
        self.assertIsNone(result)
    
    def test_get_returns_valid_entry(
        self,
        mock_cache_dir: Mock,
        mock_mkdir: Mock,
        mock_sqlite: Mock
    ) -> None:
        """Test valid entry is returned correctly."""
        mock_cache_dir.return_value = "/home/user/.cache/sherlock"
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        current_time = int(time.time())
        mock_cursor.fetchone.return_value = (
            "CLAIMED",
            "https://github.com/testuser",
            current_time - 1000,
            86400
        )
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = None
        mock_sqlite.connect.return_value = mock_conn
        
        cache = SherlockCache(cache_duration=86400)
        result = cache.get("testuser", "GitHub")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['status'], QueryStatus.CLAIMED)
        self.assertEqual(result['url'], "https://github.com/testuser")


@patch('sherlock_project.cache.sqlite3')
@patch('sherlock_project.cache.Path.mkdir')
@patch('sherlock_project.cache.user_cache_dir')
class TestCacheClear(unittest.TestCase):
    """Test cache clearing functionality."""
    
    def test_clear_all(
        self,
        mock_cache_dir: Mock,
        mock_mkdir: Mock,
        mock_sqlite: Mock
    ) -> None:
        """Test clearing entire cache."""
        mock_cache_dir.return_value = "/home/user/.cache/sherlock"
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = None
        mock_sqlite.connect.return_value = mock_conn
        
        cache = SherlockCache()
        cache.clear()
        
        call_args = mock_cursor.execute.call_args
        self.assertEqual(call_args[0][0], 'DELETE FROM results')
    
    def test_clear_by_username(
        self,
        mock_cache_dir: Mock,
        mock_mkdir: Mock,
        mock_sqlite: Mock
    ) -> None:
        """Test clearing by username."""
        mock_cache_dir.return_value = "/home/user/.cache/sherlock"
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = None
        mock_sqlite.connect.return_value = mock_conn
        
        cache = SherlockCache()
        cache.clear(username="testuser")
        
        call_args = mock_cursor.execute.call_args
        self.assertIn("WHERE username = ?", call_args[0][0])
        self.assertEqual(call_args[0][1], ("testuser",))
    
    def test_clear_validates_input(
        self,
        mock_cache_dir: Mock,
        mock_mkdir: Mock,
        mock_sqlite: Mock
    ) -> None:
        """Test input validation in clear()."""
        mock_cache_dir.return_value = "/home/user/.cache/sherlock"
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__.return_value = mock_conn
        mock_sqlite.connect.return_value = mock_conn
        
        cache = SherlockCache()
        
        with self.assertRaises(ValueError):
            cache.clear(username="user\x00injection")


@patch('sherlock_project.cache.sqlite3')
@patch('sherlock_project.cache.Path.mkdir')
@patch('sherlock_project.cache.user_cache_dir')
class TestCacheStats(unittest.TestCase):
    """Test cache statistics."""
    
    def test_stats_calculation(
        self,
        mock_cache_dir: Mock,
        mock_mkdir: Mock,
        mock_sqlite: Mock
    ) -> None:
        """Test statistics calculation."""
        mock_cache_dir.return_value = "/home/user/.cache/sherlock"
        
        # Create separate cursors for init and stats
        init_cursor = MagicMock()
        stats_cursor = MagicMock()
        
        # Stats cursor should return values for the two SELECT COUNT queries
        stats_cursor.fetchone.side_effect = [(10,), (7,)]
        
        mock_conn = MagicMock()
        # Return different cursor for stats call
        mock_conn.cursor.return_value = init_cursor
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = None
        mock_sqlite.connect.return_value = mock_conn
        
        cache = SherlockCache()
        
        # Now set up for the stats call
        mock_conn.cursor.return_value = stats_cursor
        stats = cache.get_stats()
        
        self.assertEqual(stats['total_entries'], 10)
        self.assertEqual(stats['valid_entries'], 7)
        self.assertEqual(stats['expired_entries'], 3)
        self.assertIn('cache_path', stats)

