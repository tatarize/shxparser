import unittest
from glob import glob
from itertools import chain

from shxparser.shxparser import ShxFile


def draw(paths, w, h, below, above, filename="test.png"):
    from PIL import Image, ImageDraw
    im = Image.new('RGBA', (w, h), "white")
    draw = ImageDraw.Draw(im)
    dx = 100
    dy = -above+below
    for path in paths:
        x = 0
        y = 0
        for p in path:
            if len(p) == 2:
                x = p[0]
                y = p[1]
            if len(p) == 4:
                draw.line((p[0] + dx, -p[1] - dy, p[2] + dx, -p[3] - dy), fill="black")
                x = p[2]
                y = p[3]
        dx += x
        dy += y
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
            draw(paths, 1000, 100, shx.below, shx.above, f"{f}.png")


