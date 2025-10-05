"""
Sherlock Cache Module

This module handles SQLite-based caching for username lookup results.
"""

import sqlite3
import time
from pathlib import Path
from typing import Optional, Dict, Any
from sherlock_project.result import QueryStatus


class SherlockCache:
    """Manages SQLite cache for Sherlock results."""
    
    def __init__(self, cache_path: Optional[str] = None, cache_duration: int = 86400):
        """
        Initialize the cache.
        
        Args:
            cache_path: Path to SQLite database file. Defaults to ~/.sherlock_cache.db
            cache_duration: Time in seconds to cache results. Default: 86400 (24 hours)
        """
        if cache_path is None:
            cache_dir = Path.home() / ".sherlock"
            cache_dir.mkdir(exist_ok=True)
            cache_path = str(cache_dir / "cache.db")
        
        self.cache_path = cache_path
        self.cache_duration = cache_duration
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database with required tables."""
        conn = sqlite3.connect(self.cache_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                username TEXT NOT NULL,
                site TEXT NOT NULL,
                status TEXT NOT NULL,
                url TEXT,
                timestamp INTEGER NOT NULL,
                PRIMARY KEY (username, site)
            )
        ''')
        
        # Create index for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON results(timestamp)
        ''')
        
        conn.commit()
        conn.close()
    
    def get(self, username: str, site: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached result for a username on a specific site.
        
        Args:
            username: The username to lookup
            site: The site name
            
        Returns:
            Dictionary with cached result or None if not cached/expired
        """
        conn = sqlite3.connect(self.cache_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT status, url, timestamp FROM results
            WHERE username = ? AND site = ?
        ''', (username, site))
        
        result = cursor.fetchone()
        conn.close()
        
        if result is None:
            return None
        
        status, url, timestamp = result
        current_time = int(time.time())
        
        # Check if cache is expired
        if current_time - timestamp > self.cache_duration:
            return None
        
        return {
            'status': QueryStatus[status],
            'url': url,
            'timestamp': timestamp
        }
    
    def set(self, username: str, site: str, status: QueryStatus, 
            url: Optional[str] = None):
        """
        Store result in cache.
        
        Args:
            username: The username
            site: The site name
            status: Query status
            url: URL of the found profile (if applicable)
        """
        conn = sqlite3.connect(self.cache_path)
        cursor = conn.cursor()
        
        current_time = int(time.time())
        
        cursor.execute('''
            INSERT OR REPLACE INTO results (username, site, status, url, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, site, status.name, url, current_time))
        
        conn.commit()
        conn.close()
    
    def clear(self, username: Optional[str] = None, site: Optional[str] = None):
        """
        Clear cache entries.
        
        Args:
            username: Clear specific username (if None, clears all)
            site: Clear specific site (if None, clears all)
        """
        conn = sqlite3.connect(self.cache_path)
        cursor = conn.cursor()
        
        if username and site:
            cursor.execute('DELETE FROM results WHERE username = ? AND site = ?',
                         (username, site))
        elif username:
            cursor.execute('DELETE FROM results WHERE username = ?', (username,))
        elif site:
            cursor.execute('DELETE FROM results WHERE site = ?', (site,))
        else:
            cursor.execute('DELETE FROM results')
        
        conn.commit()
        conn.close()
    
    def cleanup_expired(self):
        """Remove expired entries from cache."""
        conn = sqlite3.connect(self.cache_path)
        cursor = conn.cursor()
        
        current_time = int(time.time())
        expiration_time = current_time - self.cache_duration
        
        cursor.execute('DELETE FROM results WHERE timestamp < ?', 
                      (expiration_time,))
        
        conn.commit()
        conn.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        conn = sqlite3.connect(self.cache_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM results')
        total = cursor.fetchone()[0]
        
        current_time = int(time.time())
        expiration_time = current_time - self.cache_duration
        
        cursor.execute('SELECT COUNT(*) FROM results WHERE timestamp >= ?',
                      (expiration_time,))
        valid = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_entries': total,
            'valid_entries': valid,
            'expired_entries': total - valid,
            'cache_path': self.cache_path
        }
