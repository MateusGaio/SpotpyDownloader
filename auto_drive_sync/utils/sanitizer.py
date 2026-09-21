import unicodedata
import re


def sanitize_filename(text: str) -> str:
    normalized = unicodedata.normalize("NFC", text)
    prohibited = r'\\/:*?"<>|'
    cleaned = re.sub(f'[{re.escape(prohibited)}]', '', normalized)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    if len(cleaned) > 90:
        cleaned = cleaned[:90]
    return cleaned


def ensure_safe_path(base_path: str, filename: str) -> str:
    combined = base_path.rstrip('/') + '/' + filename
    if len(combined) <= 230:
        return filename
    name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
    if ext:
        safe_name = sanitize_filename(name)
        candidate = f"{safe_name}.{ext}"
    else:
        candidate = sanitize_filename(filename)
    while len(base_path.rstrip('/') + '/' + candidate) > 230 and len(candidate) > 10:
        candidate = sanitize_filename(candidate[:-len(ext) - 1]) + ext if ext else sanitize_filename(candidate[:-1])
    return candidate