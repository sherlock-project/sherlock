"""Tests for search history persistence (Issue #5).

Tests save, load, empty input, and invalid file scenarios
for the local JSON storage of search history.
"""
import json
import os
import asyncio
from pathlib import Path
from unittest.mock import patch

import pytest

from sherlock_project.result import QueryResult, QueryStatus
from sherlock_project.storage.local_store import LocalStorage, HISTORY_INDEX_FILENAME


class TestSearchHistory:
    """Test suite for search history persistence."""

    @pytest.fixture
    def storage(self, tmp_path):
        """Create a LocalStorage instance with a temp home directory."""
        with patch.object(Path, "home", return_value=tmp_path):
            storage = LocalStorage()
            yield storage

    @pytest.fixture
    def claimed_result(self):
        """Create a claimed (successful) query result."""
        return QueryResult(
            username="testuser",
            site_name="github",
            site_url_user="https://github.com/testuser",
            status=QueryStatus.CLAIMED,
            query_time=0.123,
        )

    @pytest.fixture
    def available_result(self):
        """Create an available (not found) query result."""
        return QueryResult(
            username="testuser",
            site_name="twitter",
            site_url_user="https://twitter.com/testuser",
            status=QueryStatus.AVAILABLE,
        )

    def test_save_successful_search(self, storage, claimed_result, available_result):
        """Test that a successful (non-empty) search is saved to JSON."""
        results = [claimed_result, available_result]

        saved = asyncio.run(storage.save_scan("testuser", results, 2))
        assert saved is not None, "Non-empty search should be saved"
        assert os.path.exists(saved), "JSON file should exist on disk"

        # Verify the index file was created
        index_file = storage.history_dir / HISTORY_INDEX_FILENAME
        assert index_file.exists(), "Index file should exist"

        with open(index_file, "r") as f:
            index = json.load(f)

        assert len(index) == 1, "Index should have one entry"
        entry = index[0]
        assert entry["query"] == "testuser", "Field should be 'query'"
        assert "timestamp" in entry, "Field 'timestamp' should exist"
        assert entry["resultCount"] == 1, "Field 'resultCount' should be 1"

    def test_do_not_save_empty_search(self, storage, available_result):
        """Test that empty searches (0 claimed results) are NOT saved."""
        results = [available_result]

        saved = asyncio.run(storage.save_scan("testuser", results, 2))
        assert saved is None, "Empty search should not be saved"

        # Load history and verify it's empty
        history = storage.load_search_history()
        assert len(history) == 0, "History should be empty after empty search"

    def test_do_not_save_whitespace_only_search(self, storage):
        """Test that searches with no results (whitespace/empty input) are not saved."""
        saved = asyncio.run(storage.save_scan(" ", [], 0))
        assert saved is None, "Whitespace query with no results should not be saved"

    def test_load_history_on_startup(self, storage, claimed_result):
        """Test that saved history is loaded on startup."""
        results = [claimed_result]

        asyncio.run(storage.save_scan("alice", results, 100))
        asyncio.run(storage.save_scan("bob", results, 100))

        # Create a new storage instance (simulating app restart)
        new_storage = LocalStorage()
        history = new_storage.load_search_history()

        assert len(history) == 2, "Should load 2 history entries"
        queries = [h["query"] for h in history]
        assert "alice" in queries
        assert "bob" in queries

    def test_load_history_returns_empty_list_when_missing(self, storage):
        """Test that missing JSON file returns empty list (no crash)."""
        # Ensure no index file exists
        index_file = storage.index_file
        if index_file.exists():
            index_file.unlink()

        history = storage.load_search_history()
        assert history == [], "Missing file should return empty list"

    def test_load_history_handles_corrupted_json(self, storage):
        """Test that corrupted JSON file returns empty list (no crash)."""
        # Write invalid JSON to the index file
        index_file = storage.index_file
        index_file.parent.mkdir(parents=True, exist_ok=True)
        with open(index_file, "w") as f:
            f.write("{invalid json!!!}")

        # Should not crash, should return empty list
        history = storage.load_search_history()
        assert history == [], "Corrupted file should return empty list"

    def test_load_history_handles_empty_json_file(self, storage):
        """Test that an empty JSON file returns empty list (no crash)."""
        index_file = storage.index_file
        index_file.parent.mkdir(parents=True, exist_ok=True)
        with open(index_file, "w") as f:
            f.write("")

        history = storage.load_search_history()
        assert history == [], "Empty file should return empty list"

    def test_json_structure_matches_issue_spec(self, storage, claimed_result):
        """Verify JSON structure exactly matches issue #5 specification.

        Expected: [{"query": "...", "timestamp": "...", "resultCount": N}]
        """
        results = [claimed_result]
        asyncio.run(storage.save_scan("example search", results, 50))

        index_file = storage.history_dir / HISTORY_INDEX_FILENAME
        with open(index_file, "r") as f:
            data = json.load(f)

        assert isinstance(data, list), "Root should be a list"
        assert len(data) == 1, "Should have one entry"
        entry = data[0]

        # Issue #5 specified fields (no extra required fields for the API)
        assert "query" in entry, "Must have 'query' field"
        assert "timestamp" in entry, "Must have 'timestamp' field"
        assert "resultCount" in entry, "Must have 'resultCount' field"

        assert entry["query"] == "example search"
        assert isinstance(entry["resultCount"], int)
        assert entry["resultCount"] == 1

    def test_timestamp_format(self, storage, claimed_result):
        """Test that timestamp uses ISO 8601 format."""
        results = [claimed_result]
        asyncio.run(storage.save_scan("testuser", results, 5))

        history = storage.load_search_history()
        assert len(history) == 1
        timestamp = history[0]["timestamp"]
        # ISO 8601 contains 'T' separator e.g. "2026-05-05T12:30:00"
        assert "T" in timestamp, "Timestamp should be ISO 8601 format with 'T' separator"

    def test_multiple_searches_sorted_by_time(self, storage, claimed_result):
        """Test that history is sorted newest-first."""
        results = [claimed_result]
        asyncio.run(storage.save_scan("first", results, 5))
        asyncio.run(storage.save_scan("second", results, 5))
        asyncio.run(storage.save_scan("third", results, 5))

        history = storage.load_search_history()
        assert len(history) == 3
        # Should be newest first (third, second, first)
        timestamps = [h["timestamp"] for h in history]
        assert timestamps == sorted(timestamps, reverse=True), \
            "Should be sorted newest first"

    def test_load_scan_handles_missing_file(self, storage):
        """Test load_scan returns None for non-existent files."""
        result = asyncio.run(storage.load_scan("/nonexistent/path.json"))
        assert result is None, "Missing file should return None"

    def test_load_scan_handles_corrupted_file(self, storage, claimed_result):
        """Test load_scan returns None for corrupted JSON files."""
        results = [claimed_result]
        path = asyncio.run(storage.save_scan("testuser", results, 5))

        # Corrupt the file
        with open(path, "w") as f:
            f.write("not valid json{{{")

        result = asyncio.run(storage.load_scan(path))
        assert result is None, "Corrupted file should return None"