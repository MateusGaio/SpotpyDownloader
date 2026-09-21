import json
import os
from typing import Dict, Any, List
from datetime import datetime, timezone


class SyncEngine:
    SYNC_INFO_FILE = '.sync_info.json'

    @classmethod
    def load_sync_info(cls, destination_path: str) -> Dict[str, Any]:
        path = os.path.join(destination_path, cls.SYNC_INFO_FILE)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'playlist_id': '',
            'playlist_name': '',
            'last_sync_timestamp': '',
            'downloaded_tracks': {},
        }

    @classmethod
    def save_sync_info(cls, destination_path: str, sync_info: Dict[str, Any]) -> None:
        path = os.path.join(destination_path, cls.SYNC_INFO_FILE)
        tmp_path = path + '.tmp'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(sync_info, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, path)

    @classmethod
    def filter_pending_tracks(
        cls, tracks: List[Dict[str, Any]], sync_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        downloaded_ids = set(
            sync_info.get('downloaded_tracks', {}).keys()
        )
        pending = []
        for track in tracks:
            if track.get('track_id') not in downloaded_ids:
                pending.append(track)
        return pending

    @classmethod
    def register_downloaded_track(
        cls, destination_path: str, sync_info: Dict[str, Any],
        track: Dict[str, Any], file_name: str
    ) -> None:
        destination = sync_info.get('destination_path', destination_path)
        if 'downloaded_tracks' not in sync_info:
            sync_info['downloaded_tracks'] = {}
        sync_info['downloaded_tracks'][track['track_id']] = {
            'title': track['title'],
            'artist': track['primary_artist'],
            'file_name': file_name,
            'downloaded_at': datetime.now(timezone.utc).isoformat(),
        }
        sync_info['playlist_id'] = track.get('playlist_id', sync_info.get('playlist_id', ''))
        sync_info['playlist_name'] = track.get('playlist_name', sync_info.get('playlist_name', ''))
        sync_info['last_sync_timestamp'] = datetime.now(timezone.utc).isoformat()
        cls.save_sync_info(destination, sync_info)