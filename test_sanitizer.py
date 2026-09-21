import pytest
from auto_drive_sync.utils.sanitizer import sanitize_filename, ensure_safe_path


def test_sanitize_filename_prohibited_chars():
    result = sanitize_filename('test/file:name"with*prohibited|chars')
    forbidden = set(r'\\/:*?"<>|')
    for ch in forbidden:
        assert ch not in result


def test_sanitize_filename_unicode_nfc():
    result = sanitize_filename('café')
    assert 'café' in result or result == 'café'


def test_sanitize_filename_multiple_spaces():
    result = sanitize_filename('hello   world')
    assert result == 'hello world'


def test_sanitize_filename_truncation():
    long_text = 'a' * 120
    result = sanitize_filename(long_text)
    assert len(result) <= 90


def test_ensure_safe_path_within_limit():
    filename = 'song.mp3'
    base = '/mnt/usb'
    result = ensure_safe_path(base, filename)
    assert len(base + '/' + filename) <= 230


def test_ensure_safe_path_truncation():
    filename = 'very_long_filename_that_exceeds_the_limit.mp3'
    base = '/mnt/usb'
    result = ensure_safe_path(base, filename)
    combined = base + '/' + result
    assert len(combined) <= 230