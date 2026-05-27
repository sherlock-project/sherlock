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


class LocalStorage:
    """Yerel JSON dosya depolama yoneticisi"""

    def __init__(self):
        self.base_dir = Path.home() / '.sherlock'
        self.history_dir = self.base_dir / 'history'
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
        return {
            'site_name': result.site_name,
            'url_user': result.site_url_user,
            'status': result.status.value if result.status else 'unknown',
            'http_status': result.context.get('http_status'),
            'response_time': result.query_time,
            'context': result.context
        }

    async def save_scan(
        self,
        username: str,
        results: List[QueryResult],
        total_sites: int,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Tarama sonuclarini kaydet

        Args:
            username: Aranan kullanici adi
            results: Tarama sonuclari
            total_sites: Toplam site sayisi
            metadata: Ek meta veriler

        Returns:
            Kaydedilen dosya yolu
        """
        scan_id = self._generate_scan_id()
        filename = self._get_filename(username)
        filepath = self.history_dir / filename

        found_count = sum(
            1 for r in results
            if r.status == QueryStatus.CLAIMED
        )

        data = {
            'scan_id': scan_id,
            'username': username,
            'started_at': self._get_timestamp(),
            'completed_at': datetime.now().isoformat(),
            'total_sites': total_sites,
            'found_count': found_count,
            'metadata': metadata or {},
            'results': [self._result_to_dict(r) for r in results]
        }

        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, indent=2, ensure_ascii=False))

        return str(filepath)

    async def load_scan(self, filepath: str) -> Dict[str, Any]:
        """Tarama sonuclarini yukle"""
        async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
            content = await f.read()
            return json.loads(content)

    def get_scan_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Tarama gecmisini listele"""
        scans = []

        if not self.history_dir.exists():
            return scans

        for filepath in sorted(self.history_dir.glob('*.json'), reverse=True):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['_filepath'] = str(filepath)
                    scans.append(data)
            except Exception:
                continue

        if limit:
            scans = scans[:limit]

        return scans

    def delete_scan(self, filepath: str) -> bool:
        """Tarama kaydini sil"""
        try:
            Path(filepath).unlink()
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
