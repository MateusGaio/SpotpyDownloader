import questionary
from rich.panel import Panel
from rich.console import Console
from rich.text import Text
from rich.progress import Progress, TextColumn, BarColumn, TaskID
from auto_drive_sync.core.drive_detector import get_removable_drives
from auto_drive_sync.core.spotify_client import SpotifyMetadataClient, MissingCredentialsError
from auto_drive_sync.core.sync_engine import SyncEngine
from auto_drive_sync.utils.sanitizer import sanitize_filename
import os
import sys

console = Console()


def display_header():
    panel = Panel(
        Text('AutoDrive-Sync', style='bold blue'),
        subtitle='Sincronizador de playlists Spotify e YT Music para USB automotiva',
        style='blue',
    )
    console.print(panel)


def get_playlist_url() -> str:
    while True:
        url = questionary.text('URL da playlist (Spotify ou YT Music): ').unsafe_ask()
        if not url:
            continue
        lowered = url.lower()
        is_spotify = 'open.spotify.com/playlist' in lowered
        is_ytmusic = ('music.youtube.com/playlist' in lowered or 'youtube.com/playlist' in lowered) and 'list=' in lowered
        if is_spotify or is_ytmusic:
            return url
        console.print('[red]Por favor, envie um link válido de playlist do Spotify ou YT Music.[/red]')


def select_destination_drive():
    drives = get_removable_drives()
    if not drives:
        path = questionary.text(
            'Nenhuma unidade removível encontrada. Digite o caminho manualmente: '
        ).unsafe_ask()
        if path and os.path.isdir(path):
            return path
        console.print('[red]Caminho inválido. Tente novamente.[/red]')
        return select_destination_drive()
    choices = []
    for d in drives:
        label = f"{d['device']} ({d['fstype']}) - Livre: {d['free_gb']:.2f} GB"
        choices.append({
            'value': d['mountpoint'],
            'name': label,
        })
    selected = questionary.select(
        'Selecione o destino (pendrive):',
        choices=choices,
    ).unsafe_ask()
    if selected and os.path.isdir(selected):
        return selected
    console.print('[red]Destino inválido.[/red]')
    return select_destination_drive()


def show_sync_summary(playlist_name, total_tracks, new_tracks, free_gb, needed_gb):
    panel = Panel(
        f'Playlist: [bold]{playlist_name}[/bold]\n'
        f'Total de faixas: [bold]{total_tracks}[/bold]\n'
        f'Novas para baixar: [bold]{new_tracks}[/bold]\n'
        f'Espaço livre no pendrive: [bold]{free_gb:.2f} GB[/bold]\n'
        f'Espaço estimado necessário: [bold]{needed_gb:.2f} GB[/bold]',
        title='Resumo da Sincronização',
        style='green',
    )
    console.print(panel)


def run_progress_bar(total_tracks, track_callbacks):
    with Progress(
        TextColumn('[progress.description]{task.description}'),
        BarColumn(),
        TextColumn('[progress.percentage]{task.percentage:>3.0f}%'),
    ) as progress:
        task = progress.add_task('Playlist progresso', total=total_tracks)
        for i in range(total_tracks):
            track_callbacks(i)
            progress.update(task, advance=1)