"""
Sherlock Cache Module

This module handles SQLite-based caching for username lookup results.
Uses platform-specific cache directories following XDG Base Directory spec.
"""

import os
import sqlite3
import time
from pathlib import Path
from typing import Optional

from platformdirs import user_cache_dir

from sherlock_project.result import QueryStatus


# Database schema version (increment when schema changes)
SCHEMA_VERSION = 1


class SherlockCache:
    """
    Manages SQLite cache for Sherlock results.
    
    Uses platform-specific cache directories:
    - Linux/macOS: ~/.cache/sherlock/cache.sqlite3
    - Windows: %LOCALAPPDATA%\\sherlock\\cache.sqlite3
    
    Implements parameterized queries to prevent SQL injection.
    """
    
    def __init__(
        self,
        cache_path: Optional[str] = None,
        cache_duration: int = 86400
    ) -> None:
        """
        Initialize the cache.
        
        Args:
            cache_path: Custom path to SQLite database. If None, uses platform default.
                       Can be full path with filename or directory (will add cache.sqlite3)
            cache_duration: Cache TTL in seconds (default: 86400 = 24 hours)
        
        Raises:
            ValueError: If cache_duration <= 0 or cache_path is invalid
            RuntimeError: If database initialization fails
        """
        if cache_duration <= 0:
            raise ValueError("cache_duration must be positive")
        
        self.cache_duration = cache_duration
        
        # Determine cache path
        if cache_path is None:
            # Use environment variable if set, otherwise platform default
            cache_path = os.environ.get('SHERLOCK_CACHE_PATH')
        
        if cache_path is None:
            # Use platform-specific cache directory
            cache_dir = Path(user_cache_dir("sherlock", "sherlock_project"))
            cache_path = str(cache_dir / "cache.sqlite3")
        else:
            # User provided path - check if it's a directory or full path
            cache_path_obj = Path(cache_path)
            if cache_path_obj.is_dir() or (not cache_path_obj.suffix):
                # It's a directory, add filename
                cache_path = str(cache_path_obj / "cache.sqlite3")
        
        # Validate and create directory
        cache_path_obj = Path(cache_path).resolve()
        
        try:
            cache_path_obj.parent.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            raise RuntimeError(f"Cannot create cache directory: {e}") from e
        
        self.cache_path = str(cache_path_obj)
        self._init_database()
    
    def _init_database(self) -> None:
        """
        Initialize the SQLite database with required tables.
        Runs migrations if needed.
        
        Raises:
            RuntimeError: If database initialization fails
        """
        try:
            with sqlite3.connect(self.cache_path) as conn:
                cursor = conn.cursor()
                
                # Create results table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS results (
                        username TEXT NOT NULL,
                        site TEXT NOT NULL,
                        status TEXT NOT NULL,
                        url TEXT,
                        timestamp INTEGER NOT NULL,
                        cache_duration INTEGER NOT NULL DEFAULT 86400,
                        PRIMARY KEY (username, site)
                    )
                ''')
                
                # Create index for faster timestamp queries
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_timestamp 
                    ON results(timestamp)
                ''')
                
                conn.commit()
                
                # Run migrations
                self._migrate_schema(conn)
                
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to initialize cache database: {e}") from e
    
    def _migrate_schema(self, conn: sqlite3.Connection) -> None:
        """
        Handle database schema migrations using PRAGMA user_version.
        
        Args:
            conn: Active database connection
            
        Raises:
            RuntimeError: If migration fails
        """
        cursor = conn.cursor()
        
        # Get current schema version
        cursor.execute("PRAGMA user_version")
        current_version = cursor.fetchone()[0]
        
        if current_version == SCHEMA_VERSION:
            # Already up to date
            return
        
        if current_version == 0:
            # Fresh database or pre-versioning database
            # Check if cache_duration column exists (migration from v0)
            cursor.execute("PRAGMA table_info(results)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'cache_duration' not in columns:
                # Migrate from v0: Add cache_duration column
                try:
                    cursor.execute('''
                        ALTER TABLE results 
                        ADD COLUMN cache_duration INTEGER NOT NULL DEFAULT 86400
                    ''')
                    conn.commit()
                except sqlite3.OperationalError:
                    # Column already exists (shouldn't happen, but be safe)
                    pass
        
        # Add future migrations here as elif current_version == X:
        
        # Update schema version
        cursor.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        conn.commit()
    
    def get(
        self,
        username: str,
        site: str
    ) -> Optional[dict[str, QueryStatus | str | int]]:
        """
        Retrieve cached result if not expired.
        
        Args:
            username: Username to lookup
            site: Site name
            
        Returns:
            Dictionary with status, url, timestamp or None if expired/missing
        """
        # Validate inputs
        self._validate_input(username, "username")
        self._validate_input(site, "site")
        
        with sqlite3.connect(self.cache_path) as conn:
            cursor = conn.cursor()
            
            # Parameterized query prevents SQL injection
            cursor.execute(
                '''
                SELECT status, url, timestamp, cache_duration 
                FROM results
                WHERE username = ? AND site = ?
                ''',
                (username, site)
            )
            
            result = cursor.fetchone()
        
        if result is None:
            return None
        
        status_str, url, timestamp, cached_duration = result
        current_time = int(time.time())
        
        # Check expiration using ORIGINAL cache_duration
        if current_time - timestamp > cached_duration:
            return None
        
        # Validate status enum
        try:
            status = QueryStatus[status_str]
        except KeyError:
            return None
        
        return {
            'status': status,
            'url': url,
            'timestamp': timestamp
        }
    
    def set(
        self,
        username: str,
        site: str,
        status: QueryStatus,
        url: Optional[str] = None
    ) -> None:
        """
        Store result in cache.
        
        Args:
            username: Username
            site: Site name
            status: Query status
            url: Profile URL if found
        """
        # Validate inputs
        self._validate_input(username, "username")
        self._validate_input(site, "site")
        
        if url is not None:
            if len(url) > 2048:
                raise ValueError("URL exceeds maximum length (2048)")
            if '\x00' in url:
                raise ValueError("URL contains null byte")
        
        current_time = int(time.time())
        
        with sqlite3.connect(self.cache_path) as conn:
            cursor = conn.cursor()
            
            # Parameterized query prevents SQL injection
            cursor.execute(
                '''
                INSERT OR REPLACE INTO results 
                (username, site, status, url, timestamp, cache_duration)
                VALUES (?, ?, ?, ?, ?, ?)
                ''',
                (username, site, status.name, url, current_time, self.cache_duration)
            )
            
            conn.commit()
    
    def set_batch(
        self,
        results: list[tuple[str, str, QueryStatus, Optional[str]]]
    ) -> None:
        """
        Store multiple results in cache (for post-run bulk insert).
        
        Args:
            results: List of (username, site, status, url) tuples
        """
        if not results:
            return
        
        current_time = int(time.time())
        
        with sqlite3.connect(self.cache_path) as conn:
            cursor = conn.cursor()
            
            # Prepare batch data
            batch_data = [
                (username, site, status.name, url, current_time, self.cache_duration)
                for username, site, status, url in results
            ]
            
            # Batch insert
            cursor.executemany(
                '''
                INSERT OR REPLACE INTO results 
                (username, site, status, url, timestamp, cache_duration)
                VALUES (?, ?, ?, ?, ?, ?)
                ''',
                batch_data
            )
            
            conn.commit()
    
    def clear(
        self,
        username: Optional[str] = None,
        site: Optional[str] = None
    ) -> None:
        """
        Clear cache entries.
        
        Args:
            username: Clear specific username (None = all)
            site: Clear specific site (None = all)
        """
        # Validate if provided
        if username is not None:
            self._validate_input(username, "username")
        if site is not None:
            self._validate_input(site, "site")
        
        with sqlite3.connect(self.cache_path) as conn:
            cursor = conn.cursor()
            
            # Parameterized queries
            if username and site:
                cursor.execute(
                    'DELETE FROM results WHERE username = ? AND site = ?',
                    (username, site)
                )
            elif username:
                cursor.execute(
                    'DELETE FROM results WHERE username = ?',
                    (username,)
                )
            elif site:
                cursor.execute(
                    'DELETE FROM results WHERE site = ?',
                    (site,)
                )
            else:
                cursor.execute('DELETE FROM results')
            
            conn.commit()
    
    def cleanup_expired(self) -> None:
        """Remove expired entries based on their original TTL."""
        current_time = int(time.time())
        
        with sqlite3.connect(self.cache_path) as conn:
            cursor = conn.cursor()
            
            # Delete where (now - timestamp) > original cache_duration
            cursor.execute(
                '''
                DELETE FROM results 
                WHERE (? - timestamp) > cache_duration
                ''',
                (current_time,)
            )
            
            conn.commit()
    
    def get_stats(self) -> dict[str, str | int]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with total_entries, valid_entries, expired_entries, cache_path
        """
        with sqlite3.connect(self.cache_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM results')
            total = cursor.fetchone()[0]
            
            current_time = int(time.time())
            
            # Count valid (non-expired) entries
            cursor.execute(
                '''
                SELECT COUNT(*) FROM results 
                WHERE (? - timestamp) <= cache_duration
                ''',
                (current_time,)
            )
            valid = cursor.fetchone()[0]
        
        return {
            'total_entries': total,
            'valid_entries': valid,
            'expired_entries': total - valid,
            'cache_path': self.cache_path
        }
    
    @staticmethod
    def _validate_input(value: str, field_name: str) -> None:
        """
        Validate username/site input.
        
        Args:
            value: Input to validate
            field_name: Name for error messages
            
        Raises:
            ValueError: If input is invalid
        """
        if not value:
            raise ValueError(f"{field_name} cannot be empty")
        
        if len(value) > 255:
            raise ValueError(f"{field_name} exceeds maximum length (255)")
        
        # Reject null bytes and control characters (except whitespace)
        if '\x00' in value:
            raise ValueError(f"{field_name} contains null byte")
        
        # Check for other dangerous control characters
        for char in value:
            if ord(char) < 32 and char not in '\t\n\r':
                raise ValueError(f"{field_name} contains invalid control characters")
