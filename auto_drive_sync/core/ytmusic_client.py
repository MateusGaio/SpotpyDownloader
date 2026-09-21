import re
from typing import Dict, Any
from urllib.parse import urlparse, parse_qs
from ytmusicapi import YTMusic


class YTMusicMetadataClient:
    def __init__(self):
        self._yt = YTMusic()
        self._album_year_cache = {}

    def _extract_playlist_id(self, playlist_url_or_id: str) -> str:
        parsed = urlparse(playlist_url_or_id)
        qs_list = parse_qs(parsed.query).get('list')
        if qs_list:
            return qs_list[0]
        match = re.search(r'playlist/([a-zA-Z0-9_-]+)', playlist_url_or_id)
        if match:
            return match.group(1)
        return playlist_url_or_id

    def _album_release_year(self, album_id: str) -> str:
        if not album_id:
            return ''
        if album_id not in self._album_year_cache:
            try:
                album = self._yt.get_album(album_id)
                self._album_year_cache[album_id] = str(album.get('year', '') or '')
            except Exception:
                self._album_year_cache[album_id] = ''
        return self._album_year_cache[album_id]

    def _best_thumbnail(self, thumbnails) -> str:
        if not thumbnails:
            return ''
        return max(thumbnails, key=lambda t: t.get('width', 0)).get('url', '')

    def get_playlist_tracks(self, playlist_url_or_id: str) -> Dict[str, Any]:
        playlist_id = self._extract_playlist_id(playlist_url_or_id)
        playlist_info = self._yt.get_playlist(playlist_id, limit=None)
        playlist_name = playlist_info.get('title', 'Unknown Playlist')
        tracks = []
        for index, item in enumerate(playlist_info.get('tracks', []), start=1):
            video_id = item.get('videoId')
            if not video_id or not item.get('isAvailable', True):
                continue
            artists = item.get('artists') or []
            primary_artist = artists[0].get('name', '') if artists else ''
            artist_names = ', '.join(a.get('name', '') for a in artists)
            album = item.get('album') or {}
            tracks.append({
                'track_id': video_id,
                'title': item.get('title', ''),
                'artists': artist_names,
                'primary_artist': primary_artist,
                'album_name': album.get('name', ''),
                'release_year': self._album_release_year(album.get('id')),
                'track_number': index,
                'cover_url': self._best_thumbnail(item.get('thumbnails')),
                'video_url': f'https://music.youtube.com/watch?v={video_id}',
            })
        return {
            'playlist_name': playlist_name,
            'tracks': tracks,
        }
