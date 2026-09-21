import io
import requests
from typing import Dict, Any
from PIL import Image
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TYER, TRCK
from mutagen.id3 import ID3NoHeaderError


class AutomotiveTagger:
    @staticmethod
    def apply_tags(file_path: str, metadata: Dict[str, Any]) -> None:
        try:
            tags = ID3(file_path)
        except ID3NoHeaderError:
            tags = ID3()
        tags.delall('APIC')
        title_frame = TIT2(encoding=1, text=[metadata['title']])
        artist_frame = TPE1(encoding=1, text=[metadata['artists']])
        album_frame = TALB(encoding=1, text=[metadata['album_name']])
        year_frame = TYER(encoding=1, text=[str(metadata['release_year'])])
        track_frame = TRCK(encoding=1, text=[str(metadata['track_number'])])
        tags.add(title_frame)
        tags.add(artist_frame)
        tags.add(album_frame)
        tags.add(year_frame)
        tags.add(track_frame)
        cover_url = metadata.get('cover_url')
        if cover_url:
            try:
                resp = requests.get(cover_url, timeout=15)
                resp.raise_for_status()
                img = Image.open(io.BytesIO(resp.content)).convert('RGB')
                img = img.resize((500, 500), Image.Resampling.LANCZOS)
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG')
                apiq = APIC(
                    encoding=1,
                    mime='image/jpeg',
                    type=3,
                    desc='Cover',
                    data=buffer.getvalue()
                )
                tags.add(apiq)
            except Exception:
                pass
        tags.save(file_path, v2_version=3)