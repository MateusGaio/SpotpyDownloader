import sys
import os
from typing import Dict, Any, List

from rich.console import Console

from auto_drive_sync.core.drive_detector import get_removable_drives
from auto_drive_sync.core.spotify_client import SpotifyMetadataClient, MissingCredentialsError
from auto_drive_sync.core.ytmusic_client import YTMusicMetadataClient
from auto_drive_sync.core.downloader import AudioDownloader
from auto_drive_sync.core.tagger import AutomotiveTagger
from auto_drive_sync.core.sync_engine import SyncEngine
from auto_drive_sync.utils.sanitizer import sanitize_filename
from auto_drive_sync.cli.interface import (
    display_header, get_playlist_url, select_destination_drive,
    show_sync_summary
)
from auto_drive_sync.cli.progress import render_track_progress
import questionary

console = Console()


AVG_TRACK_SIZE_MB = 8.5


def estimate_space_needed(tracks: List[Dict[str, Any]]) -> float:
    return round(len(tracks) * AVG_TRACK_SIZE_MB / 1024, 2)


def sanitize_track_filename(track: Dict[str, Any]) -> str:
    name = f"{track.get('track_number', '')} - {track.get('title', '')}"
    artists = track.get('primary_artist', '')
    if artists:
        name = f"{artists} - {name}"
    return sanitize_filename(name) + '.mp3'


def main():
    display_header()
    playlist_url = get_playlist_url()
    is_ytmusic = ('music.youtube.com/playlist' in playlist_url.lower()
                  or 'youtube.com/playlist' in playlist_url.lower())

    if is_ytmusic:
        client = YTMusicMetadataClient()
    else:
        try:
            client = SpotifyMetadataClient()
        except MissingCredentialsError as e:
            console.print(f'[red]Erro: {e}[/red]')
            sys.exit(1)

    metadata = client.get_playlist_tracks(playlist_url)
    playlist_name = metadata.get('playlist_name', 'Playlist')
    tracks = metadata.get('tracks', [])

    destination = select_destination_drive()
    drives = get_removable_drives()
    free_gb = 0
    for d in drives:
        if d['mountpoint'] == destination or d['device'] in destination:
            free_gb = d['free_gb']
            break

    needed_gb = estimate_space_needed(tracks)
    sync_info = SyncEngine.load_sync_info(destination)
    new_tracks = [t for t in tracks if t.get('track_id') not in sync_info.get('downloaded_tracks', {})]

    show_sync_summary(playlist_name, len(tracks), len(new_tracks), free_gb, needed_gb)

    if not new_tracks:
        console.print('[yellow]Nenhuma nova faixa para sincronizar.[/yellow]')
        return

    pending = SyncEngine.filter_pending_tracks(new_tracks, sync_info)

    if not pending:
        console.print('[yellow]Todas as faixas já foram sincronizadas.[/yellow]')
        return

    downloader = AudioDownloader()
    tagger = AutomotiveTagger()

    console.print(f'[bold]Iniciando download de {len(pending)} faixas...[/bold]')

    for track in pending:
        file_name = sanitize_track_filename(track)
        result = downloader.download_track(
            track.get('primary_artist', ''),
            track.get('title', ''),
            os.path.join(destination, file_name),
            video_url=track.get('video_url')
        )
        if not result.get('success'):
            console.print(f'[red]Falha ao baixar: {track.get("title", "")} - {result.get("error", "")}[/red]')
            continue

        tagger.apply_tags(result.get('file_path', {}), {
            'title': track.get('title', ''),
            'artists': track.get('artists', ''),
            'album_name': track.get('album_name', ''),
            'release_year': int(track.get('release_year', 2024)) if track.get('release_year') else 2024,
            'track_number': track.get('track_number', 1),
            'cover_url': track.get('cover_url', ''),
        })

        SyncEngine.register_downloaded_track(
            destination, sync_info, track, file_name
        )

    console.print('[green]Sincronização concluída![/green]')


def cli_entrypoint():
    main()


if __name__ == '__main__':
    cli_entrypoint()