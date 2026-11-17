"""Builds the website's phone screenshots from the Play Store raw captures.

The emulator draws the clock and status icons 12px from the screen edge, which the
rounded phone frame on the site clips. This moves them inward (and down a little)
so they sit clear of the corner radius, then writes 720px WebP files to img/.

The raw 1080x2400 captures live in the app repo, under docs/launch/play-store/src/raw.
Run from this repo's root, passing that folder:

    python tools/make-screens.py ../Finorvia/docs/launch/play-store/src/raw
"""
import sys
from pathlib import Path
from PIL import Image

if len(sys.argv) != 2:
    sys.exit(__doc__)
RAW = Path(sys.argv[1])
OUT = Path(__file__).resolve().parents[1] / "img"
NAMES = ["home", "home_dark", "subs", "add", "analytics2", "goals", "widgets"]

BAR_H = 64          # rows the original status bar content lives in (content is y 13-47)
CLEAR_H = 82        # rows repainted with the background before pasting back
LEFT = (0, 0, 130, BAR_H)       # clock
RIGHT = (840, 0, 1080, BAR_H)   # wifi + battery
INSET_X = 88        # clock moves right / icons move left by roughly this much
DROP_Y = 20         # and both move down a touch


def repaint(im, box, sample_x):
    """Fill box row by row with the colour at sample_x, which keeps wallpaper gradients."""
    x0, y0, x1, y1 = box
    px = im.load()
    for y in range(y0, y1):
        c = px[sample_x, y]
        for x in range(x0, x1):
            px[x, y] = c


def fix(im):
    im = im.convert("RGB")
    clock = im.crop(LEFT)
    icons = im.crop(RIGHT)
    repaint(im, (0, 0, 140, CLEAR_H), 200)
    repaint(im, (830, 0, 1080, CLEAR_H), 780)
    # Paste only the glyphs, not their background, so the repainted rows show through.
    for part, box, dx in ((clock, LEFT, INSET_X), (icons, RIGHT, -(INSET_X - 64))):
        bg = part.getpixel((part.width - 1, BAR_H - 2))
        mask = Image.new("L", part.size, 0)
        mp, pp = mask.load(), part.load()
        for y in range(part.height):
            for x in range(part.width):
                d = sum(abs(a - b) for a, b in zip(pp[x, y], bg))
                mp[x, y] = min(255, d * 2)  # soft edge keeps the glyphs' anti-aliasing
        im.paste(part, (box[0] + dx, box[1] + DROP_Y), mask)
    return im


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for n in NAMES:
        im = fix(Image.open(RAW / f"{n}.png"))
        im.resize((720, 1600), Image.LANCZOS).save(OUT / f"{n}.webp", "WEBP", quality=84)
        print("wrote", OUT / f"{n}.webp")


if __name__ == "__main__":
    main()
