import unittest
from glob import glob
from itertools import chain

from shxparser.shxparser import ShxFile


def draw(paths, w, h, below, above, filename="test.png"):
    from PIL import Image, ImageDraw
    im = Image.new('RGBA', (w, h), "white")
    draw = ImageDraw.Draw(im)
    for path in paths:
        last_x = None
        last_y = None
        for x, y in path:
            if last_x is not None:
                draw.line((last_x, last_y, x, y), fill="black")
            last_x, last_y = x+200, y + 200
    im.save(filename)


class TestParser(unittest.TestCase):
    """Tests the parsing functionality."""

    def test_parse(self):
        for f in chain(glob("parse/*.SHX"), glob("parse/*.shx")):
            print(f"Attempt parsing of file: {str(f)}")
            shx = ShxFile(f)
            print(f"Parsed: {str(shx)} @ {str(f)}")
            paths = list()
            for letter in "hello world":
                try:
                    glyph = shx.glyphs[ord(letter)]
                except KeyError:
                    continue
                paths.append(glyph)
            draw(paths, 5000, 1000, shx.below, shx.above, f"{f}.png")


