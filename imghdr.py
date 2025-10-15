import os
import struct

def what(file, h=None):
    """Detecta tipo de imagen por encabezado (sustituto de imghdr original)."""
    if h is None:
        if isinstance(file, str):
            with open(file, 'rb') as f:
                h = f.read(32)
        else:
            h = file.read(32)

    for name, test in tests:
        res = test(h)
        if res:
            return res
    return None


def test_jpeg(h):
    return h.startswith(b'\xff\xd8')


def test_png(h):
    return h.startswith(b'\211PNG\r\n\032\n')


def test_gif(h):
    return h[:6] in (b'GIF87a', b'GIF89a')


def test_tiff(h):
    return h[:2] in (b'MM', b'II')


def test_bmp(h):
    return h[:2] == b'BM'


def test_webp(h):
    return h[:4] == b'RIFF' and h[8:12] == b'WEBP'


tests = [
    ('jpeg', test_jpeg),
    ('png', test_png),
    ('gif', test_gif),
    ('tiff', test_tiff),
    ('bmp', test_bmp),
    ('webp', test_webp),
]

__all__ = ['what']

