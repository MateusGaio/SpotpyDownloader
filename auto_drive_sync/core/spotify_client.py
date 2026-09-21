import os
import re
from typing import Dict, Any, List
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException

SPOTIFY_SCOPE = 'playlist-read-private playlist-read-collaborative'


class MissingCredentialsError(Exception):
    pass


class SpotifyMetadataClient:
    def __init__(self):
        client_id = os.environ.get('SPOTIPY_CLIENT_ID')
        client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
        redirect_uri = os.environ.get('SPOTIPY_REDIRECT_URI', 'http://127.0.0.1:8888/callback')
        if not client_id or not client_secret:
            raise MissingCredentialsError(
                'SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET environment variables are required.'
            )
        cache_path = os.path.expanduser('~/.cache/auto_drive_sync/spotify_token.json')
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        self._sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=SPOTIFY_SCOPE,
            cache_path=cache_path,
        ))

    def _extract_playlist_id(self, playlist_url_or_id: str) -> str:
        match = re.search(r'playlist/([a-zA-Z0-9]+)', playlist_url_or_id)
        if match:
            return match.group(1)
        return playlist_url_or_id

    def get_playlist_tracks(self, playlist_url_or_id: str) -> Dict[str, Any]:
        playlist_id = self._extract_playlist_id(playlist_url_or_id)
        playlist_info = self._sp.playlist(playlist_id)
        playlist_name = playlist_info.get('name', 'Unknown Playlist')
        tracks = []
        offset = 0
        limit = 100
        total = 1
        while offset < total:
            page = self._sp.playlist_items(playlist_id, offset=offset, limit=limit)
            total = page.get('total', 0)
            for item in page.get('items', []):
                track = item.get('item') or item.get('track')
                if track is None:
                    continue
                track_id = track.get('id')
                if not track_id:
                    continue
                artists = track.get('artists', [])
                primary_artist = artists[0].get('name', '') if artists else ''
                artist_names = ', '.join(a.get('name', '') for a in artists)
                album_name = track.get('album', {}).get('name', '')
                release_date = track.get('album', {}).get('release_date', '')
                release_year = release_date[:4] if release_date else ''
                track_number = track.get('track_number', 0)
                cover_url = track.get('album', {}).get('images', [{}])[0].get('url', '')
                tracks.append({
                    'track_id': track_id,
                    'title': track.get('name', ''),
                    'artists': artist_names,
                    'primary_artist': primary_artist,
                    'album_name': album_name,
                    'release_year': release_year,
                    'track_number': track_number,
                    'cover_url': cover_url,
                })
            offset += limit
        return {
            'playlist_name': playlist_name,
            'tracks': tracks,
        }