"""Build `<fighter>_bust_circle.png` (circular crop + thin gold ring) from `<fighter>_bust.png`."""
import os
import sys
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PORTRAITS = os.path.join(ROOT, "assets", "portraits")
SS = 4


def make_circle(name):
    src = Image.open(os.path.join(PORTRAITS, f"{name}_bust.png")).convert("RGBA")
    n = src.width
    big = n * SS
    mask = Image.new("L", (big, big), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, big - 1, big - 1), fill=255)
    mask = mask.resize((n, n), Image.LANCZOS)
    out = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    out.paste(src, (0, 0), mask)
    ring = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(ring)
    w = 3 * SS
    d.ellipse((0, 0, big - 1, big - 1), outline=(216, 193, 113, 255), width=w)
    ring = ring.resize((n, n), Image.LANCZOS)
    out = Image.alpha_composite(out, ring)
    out.save(os.path.join(PORTRAITS, f"{name}_bust_circle.png"))


if __name__ == "__main__":
    for fighter in sys.argv[1:]:
        make_circle(fighter)
