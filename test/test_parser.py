import unittest
from glob import glob
from itertools import chain

from shxparser.shxparser import ShxFile


def draw(paths, w, h, fw, fh, filename="test.png"):
    from PIL import Image, ImageDraw
    im = Image.new('RGBA', (w, h), "white")
    draw = ImageDraw.Draw(im)
    dx = 0
    dy = 0
    for path in paths:
        x = 0
        y = 0
        for p in path:
            if len(p) == 2:
                x = p[0]
                y = p[1]
            if len(p) == 4:
                x0 = p[0] + dx + fw
                y0 = p[1] + dy - fh
                x1 = p[2] + dx + fw
                y1 = p[3] + dy - fh
                draw.line((x0, -y0, x1, -y1), fill="black")
                x = p[2]
                y = p[3]
        dx += x
        dy += y
        print(dx)
        print(dy)
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
            draw(paths, 1000, 100, shx.font_width, shx.font_height, f"{f}.png")


