"""
Yerel JSON depolama modulu
Tarama gecmisi ve sonuclari icin dosya yonetimi
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
import aiofiles
import uuid

from sherlock_project.result import QueryResult, QueryStatus


HISTORY_INDEX_FILENAME = "search_history.json"


class LocalStorage:
    """Yerel JSON dosya depolama yoneticisi"""

    def __init__(self):
        self.base_dir = Path.home() / '.sherlock'
        self.history_dir = self.base_dir / 'history'
        self.index_file = self.history_dir / HISTORY_INDEX_FILENAME
        self._ensure_directories()

    def _ensure_directories(self):
        """Gerekli dizinleri olustur"""
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def _generate_scan_id(self) -> str:
        """Benzersiz tarama ID uret"""
        return str(uuid.uuid4())[:8]

    def _get_timestamp(self) -> str:
        """ISO format zaman damgasi"""
        return datetime.now().isoformat()

    def _get_filename(self, username: str) -> str:
        """Tarama dosya adi olustur"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{timestamp}_{username}.json"

    def _result_to_dict(self, result: QueryResult) -> Dict[str, Any]:
        """QueryResult'u dict'e cevir"""
        http_status = None
        if isinstance(result.context, dict):
            http_status = result.context.get('http_status')
        return {
            'site_name': result.site_name,
            'url_user': result.site_url_user,
            'status': result.status.value if result.status else 'unknown',
            'http_status': http_status,
            'response_time': result.query_time,
            'context': result.context
        }

    def _load_index(self) -> List[Dict[str, Any]]:
        """Load the search history index from the index file.

        Returns an empty list if the file is missing or corrupted.
        """
        if not self.index_file.exists():
            return []

        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return []
        except (json.JSONDecodeError, IOError, ValueError):
            # Handle corrupted JSON gracefully: return empty list
            return []

    def _save_index(self, index: List[Dict[str, Any]]) -> None:
        """Persist the search history index to the index file."""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
        except IOError:
            # If we cannot write the index, just skip — scan file itself is saved
            pass

    def load_search_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load search history from the consolidated index file.

        This is the primary method for retrieving previous searches.
        Handles missing and corrupted JSON files gracefully.

        Args:
            limit: Maximum number of history entries to return (most recent first).

        Returns:
            List of dictionaries, each representing a previous search summary.
        """
        index = self._load_index()

        # Sort by timestamp descending (newest first)
        index.sort(key=lambda h: h.get("timestamp", ""), reverse=True)

        if limit:
            return index[:limit]
        return index

    def delete_scan(self, filepath: str) -> bool:
        """Tarama kaydini sil"""
        try:
            Path(filepath).unlink()
            # Also remove from index if present
            index = self._load_index()
            target_path = str(Path(filepath).resolve())
            index = [e for e in index if e.get("_filepath") != target_path]
            self._save_index(index)
            return True
        except Exception:
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Depolama istatistikleri"""
        scans = self.get_scan_history()
        total_scans = len(scans)
        total_found = sum(s.get('found_count', 0) for s in scans)
        unique_usernames = len(set(s.get('username') for s in scans))

        return {
            'total_scans': total_scans,
            'total_found_accounts': total_found,
            'unique_usernames': unique_usernames,
            'storage_path': str(self.history_dir)
        }

    async def save_scan(
        self,
        username: str,
        results: List[QueryResult],
        total_sites: int,
        metadata: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Tarama sonuclarini kaydet.

        Only saves if the search produced at least one claimed result
        (i.e. non-empty search). Returns None for empty searches.

        Args:
            username: Aranan kullanici adi
            results: Tarama sonuclari
            total_sites: Toplam site sayisi
            metadata: Ek meta veriler

        Returns:
            Kaydedilen dosya yolu, or None if search was empty.
        """
        found_count = sum(
            1 for r in results
            if r.status == QueryStatus.CLAIMED
        )

        # Do NOT save empty searches (no claimed results).
        if found_count == 0:
            return None

        scan_id = self._generate_scan_id()
        filename = self._get_filename(username)
        filepath = self.history_dir / filename

        data = {
            'scan_id': scan_id,
            'username': username,
            'started_at': self._get_timestamp(),
            'completed_at': datetime.now().isoformat(),
            'total_sites': total_sites,
            'found_count': found_count,
            'metadata': metadata or {},
            'results': [r.to_dict() for r in results]
        }

        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, indent=2, ensure_ascii=False))

        # Update the consolidated history index (using issue #5 specified field names)
        index = self._load_index()
        index.append({
            "query": username,
            "timestamp": data["completed_at"],
            "resultCount": found_count,
            "scan_id": scan_id,
            "total_sites": total_sites,
            "_filepath": str(filepath.resolve()),
        })
        self._save_index(index)

        return str(filepath)

    async def load_scan(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Tarama sonuclarini yukle.

        Handles missing and corrupted JSON files gracefully by returning None.

        Args:
            filepath: Path to the scan JSON file.

        Returns:
            Dictionary with scan data, or None if file is missing or corrupted.
        """
        path = Path(filepath)
        if not path.exists():
            return None

        try:
            async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
        except (json.JSONDecodeError, IOError):
            # Handle corrupted JSON gracefully
            return None

    def get_scan_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Tarama gecmisini listele (legacy method, scans individual files).

        This is kept for backward compatibility. For new code,
        prefer load_search_history().

        Args:
            limit: Maximum number of history entries to return.

        Returns:
            List of scan data dictionaries.
        """
        scans = []

        if not self.history_dir.exists():
            return scans

        for filepath in sorted(self.history_dir.glob('*.json'), reverse=True):
            # Skip the index file itself
            if filepath.name == HISTORY_INDEX_FILENAME:
                continue
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['_filepath'] = str(filepath)
                    scans.append(data)
            except (json.JSONDecodeError, IOError):
                # Handle corrupted JSON gracefully: skip this file
                continue

        if limit:
            scans = scans[:limit]

        return scans