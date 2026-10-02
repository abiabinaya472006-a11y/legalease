"""Create a simple LegalEase logo PNG without external image libraries."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path


def _chunk(tag: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def create_logo(path: Path, size: int = 256) -> None:
    """Generate a navy rounded-square logo with a teal accent bar."""
    # Colors
    navy = (26, 43, 74)
    teal = (15, 107, 92)
    paper = (247, 245, 241)

    rows = []
    margin = size // 10
    accent_y0 = size // 2 - size // 12
    accent_y1 = size // 2 + size // 12

    for y in range(size):
        row = bytearray()
        row.append(0)  # filter none
        for x in range(size):
            # Soft rounded square mask
            dx = min(x, size - 1 - x)
            dy = min(y, size - 1 - y)
            inside = dx >= margin // 4 and dy >= margin // 4
            if not inside:
                r, g, b = paper
            elif accent_y0 <= y <= accent_y1 and margin <= x <= size - margin:
                r, g, b = teal
            elif margin <= x <= size - margin and margin <= y <= size - margin:
                # vertical panel
                if x < size // 3:
                    r, g, b = navy
                else:
                    r, g, b = paper if (x + y) % 17 != 0 else (230, 234, 240)
            else:
                r, g, b = paper
            row.extend((r, g, b))
        rows.append(bytes(row))

    raw = b"".join(rows)
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", zlib.compress(raw, 9)) + _chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    create_logo(root / "assets" / "logo.png")
    print("Created assets/logo.png")
