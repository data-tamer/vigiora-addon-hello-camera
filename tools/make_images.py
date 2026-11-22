"""Draws images/icon.png (256 x 256) and images/screenshot-1.png (a placeholder) with the standard library only.

Run it again after you change a colour:  python tools/make_images.py
Replace both images with your own before you submit. The icon must be a square PNG of 128 to 512 pixels,
at most 200 KB. The placeholder is deliberately plain and says so, so nobody mistakes it for a real screenshot.
"""
import struct
import zlib
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "images"
SS = 3  # supersampling for smooth edges

NAVY, TEAL, WHITE, SAND, GREY = (23, 37, 84), (20, 184, 166), (255, 255, 255), (245, 241, 232), (120, 120, 130)


def write_png(path: Path, w: int, h: int, rows: list[bytes]) -> None:
    def chunk(kind: bytes, data: bytes) -> bytes:
        c = struct.pack(">I", len(data)) + kind + data
        return c + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    raw = b"".join(b"\x00" + r for r in rows)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    path.write_bytes(png)


def render(w: int, h: int, shade) -> list[bytes]:
    """shade(x, y) -> (r, g, b) for a point in 0..w, 0..h; each pixel averages SS x SS samples."""
    rows = []
    for y in range(h):
        row = bytearray()
        for x in range(w):
            r = g = b = 0
            for sy in range(SS):
                for sx in range(SS):
                    c = shade(x + (sx + 0.5) / SS, y + (sy + 0.5) / SS)
                    r, g, b = r + c[0], g + c[1], b + c[2]
            n = SS * SS
            row += bytes((r // n, g // n, b // n))
        rows.append(bytes(row))
    return rows


def icon_shade(x: float, y: float):
    """A rounded navy square with a teal ring and a white dot: a lens, nothing more."""
    s = 256.0
    cx = cy = s / 2
    # rounded square, corner radius 48
    dx, dy = abs(x - cx) - (s / 2 - 48), abs(y - cy) - (s / 2 - 48)
    if max(dx, 0) ** 2 + max(dy, 0) ** 2 > 48 ** 2:
        return WHITE
    d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
    if 62 <= d <= 86:
        return TEAL
    if d <= 26:
        return WHITE
    return NAVY


# A 5 x 7 pixel font for the letters of the placeholder text.
FONT = {
    "P": ["XXXX.", "X...X", "X...X", "XXXX.", "X....", "X....", "X...."],
    "L": ["X....", "X....", "X....", "X....", "X....", "X....", "XXXXX"],
    "A": [".XXX.", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"],
    "C": [".XXXX", "X....", "X....", "X....", "X....", "X....", ".XXXX"],
    "E": ["XXXXX", "X....", "X....", "XXXX.", "X....", "X....", "XXXXX"],
    "H": ["X...X", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"],
    "O": [".XXX.", "X...X", "X...X", "X...X", "X...X", "X...X", ".XXX."],
    "D": ["XXXX.", "X...X", "X...X", "X...X", "X...X", "X...X", "XXXX."],
    "R": ["XXXX.", "X...X", "X...X", "XXXX.", "X.X..", "X..X.", "X...X"],
    "S": [".XXXX", "X....", "X....", ".XXX.", "....X", "....X", "XXXX."],
    "N": ["X...X", "XX..X", "X.X.X", "X..XX", "X...X", "X...X", "X...X"],
    "T": ["XXXXX", "..X..", "..X..", "..X..", "..X..", "..X..", "..X.."],
    " ": ["....."] * 7,
}


def text_mask(text: str, scale: int):
    """Set of (x, y) pixels of the text, and its width and height."""
    pts = set()
    for i, ch in enumerate(text):
        for ry, line in enumerate(FONT[ch]):
            for rx, c in enumerate(line):
                if c == "X":
                    for a in range(scale):
                        for b in range(scale):
                            pts.add(((i * 6 + rx) * scale + a, ry * scale + b))
    return pts, len(text) * 6 * scale - scale, 7 * scale


W, H = 800, 450
BIG, SMALL = text_mask("PLACEHOLDER", 10), text_mask("SCREENSHOT", 5)


def shot_shade(x: float, y: float):
    if x < 6 or y < 6 or x > W - 6 or y > H - 6:
        return GREY
    for (pts, tw, th), top in ((BIG, 150), (SMALL, 270)):
        left = (W - tw) // 2
        if (int(x) - left, int(y) - top) in pts:
            return NAVY
    if ((x + y) // 40) % 2 == 0:
        return SAND
    return (236, 231, 218)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    write_png(OUT / "icon.png", 256, 256, render(256, 256, icon_shade))
    write_png(OUT / "screenshot-1.png", W, H, render(W, H, shot_shade))
    print("wrote", OUT / "icon.png", "and", OUT / "screenshot-1.png")
