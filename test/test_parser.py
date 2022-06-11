import unittest
from glob import glob
from itertools import chain

from shxparser.shxparser import ShxFile


def draw(paths, w, h, below, above, filename="test.png"):
    from PIL import Image, ImageDraw
    im = Image.new('RGBA', (w, h), "white")
    draw = ImageDraw.Draw(im)
    dx = below + above
    for path in paths:
        for p in path:
            if len(p) == 2:
                pass
            if len(p) == 4:
                draw.line((p[0] + dx, -p[1], p[2] + dx, -p[3]), fill="black")
        dx += above
    im.save(filename)


class TestParser(unittest.TestCase):
    """Tests the parsing functionality."""

    def test_parse(self):
        for f in chain(glob("parse/*.SHX"), glob("parse/*.shx")):
            print(f"Attempt parsing of file: {str(f)}")
            shx = ShxFile(f)
            print(f"Parsed: {str(shx)} @ {str(f)}")
            paths = list()
            txt = "hello world"
            for letter in txt:
                try:
                    glyph = shx.glyphs[ord(letter)]
                except KeyError:
                    continue
                paths.append(glyph)
                print(glyph)
            draw(paths, shx.above * (len(txt) + 1), shx.above, shx.below, shx.above, f"{f}.png")


