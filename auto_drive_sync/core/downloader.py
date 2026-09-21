import yt_dlp
from yt_dlp.utils import DownloadError
from typing import Dict, Any


class AudioDownloader:
    def __init__(self):
        self._ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'js_runtimes': {'node': {'path': None}},
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
        }

    def download_track(self, artist: str, title: str, output_path: str, video_url: str = None) -> Dict[str, Any]:
        query = video_url or f"ytsearch1:{artist} - {title} Audio"
        try:
            with yt_dlp.YoutubeDL(self._ydl_opts) as ydl:
                info = ydl.extract_info(query, download=True)
                if 'entries' in info:
                    info = info['entries'][0]
                filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
                # Move to final output_path if needed
                final_path = output_path if output_path else filename
                import shutil
                if filename != final_path:
                    shutil.move(filename, final_path)
                return {'success': True, 'file_path': final_path}
        except DownloadError as e:
            return {'success': False, 'error': str(e)}
        except Exception as e:
            return {'success': False, 'error': str(e)}