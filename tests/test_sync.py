import pytest
import os
import json
import tempfile
from auto_drive_sync.core.sync_engine import SyncEngine


class TestSyncEngine:
    @pytest.fixture
    def temp_dest(self):
        tmp = tempfile.mkdtemp()
        yield tmp
        import shutil
        shutil.rmtree(tmp)

    def test_load_sync_info_empty(self, temp_dest):
        info = SyncEngine.load_sync_info(temp_dest)
        assert info == {
            'playlist_id': '',
            'playlist_name': '',
            'last_sync_timestamp': '',
            'downloaded_tracks': {},
        }

    def test_load_sync_info_with_file(self, temp_dest):
        path = os.path.join(temp_dest, '.sync_info.json')
        with open(path, 'w') as f:
            json.dump({'playlist_id': 'test123', 'downloaded_tracks': {}}, f)
        info = SyncEngine.load_sync_info(temp_dest)
        assert info['playlist_id'] == 'test123'

    def test_register_and_load(self, temp_dest):
        track = {'track_id': 'track_abc', 'title': 'Test', 'primary_artist': 'Artist'}
        SyncEngine.register_downloaded_track(temp_dest, {}, track, '01 - Test.mp3')
        info = SyncEngine.load_sync_info(temp_dest)
        assert 'track_abc' in info['downloaded_tracks']
        assert info['downloaded_tracks']['track_abc']['file_name'] == '01 - Test.mp3'

    def test_filter_pending_tracks_no_existing(self, temp_dest):
        sync_info = {'downloaded_tracks': {}}
        tracks = [
            {'track_id': 't1', 'title': 'Track 1', 'file_name': '01 - T1.mp3'},
            {'track_id': 't2', 'title': 'Track 2', 'file_name': '02 - T2.mp3'},
        ]
        result = SyncEngine.filter_pending_tracks(tracks, sync_info)
        assert len(result) == 2

    def test_filter_pending_tracks_with_existing(self, temp_dest):
        path = os.path.join(temp_dest, '.sync_info.json')
        with open(path, 'w') as f:
            json.dump({
                'playlist_id': 'test123',
                'playlist_name': 'Test Playlist',
                'last_sync_timestamp': '2024-01-01T00:00:00',
                'downloaded_tracks': {
                    't1': {
                        'title': 'Track 1',
                        'artist': 'Artist 1',
                        'file_name': '01 - T1.mp3',
                        'downloaded_at': '2024-01-01T00:00:00'
                    }
                }
            }, f)
        with open(path, 'r') as f:
            sync_info = json.load(f)
        tracks = [
            {'track_id': 't1', 'title': 'Track 1', 'file_name': '01 - T1.mp3'},
            {'track_id': 't2', 'title': 'Track 2', 'file_name': '02 - T2.mp3'},
        ]
        result = SyncEngine.filter_pending_tracks(tracks, sync_info)
        assert len(result) == 1
        assert result[0]['track_id'] == 't2'