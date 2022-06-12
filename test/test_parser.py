import unittest
from glob import glob
from itertools import chain

from shxparser.shxparser import ShxFile, ShxPath


def draw(paths, w, h, fw, fh, filename="test.png"):
    from PIL import Image, ImageDraw
    im = Image.new('RGBA', (w, h), "white")
    draw = ImageDraw.Draw(im)
    for p in paths.path:
        if p is None:
            continue
        if len(p) == 2:
            continue
        elif len(p) == 4:
            x0 = p[0] + fw
            y0 = p[1] - fh
            x1 = p[2] + fw
            y1 = p[3] - fh
            draw.line((x0, -y0, x1, -y1), fill="black")
        elif len(p) == 6:
            x0 = p[0] + fw
            y0 = p[1] - fh
            x1 = p[2] + fw
            y1 = p[3] - fh
            x2 = p[4] + fw
            y2 = p[5] - fh
            draw.line((x0, -y0, x2, -y2), fill="black")
    im.save(filename)


class TestParser(unittest.TestCase):
    """Tests the parsing functionality."""

    def test_parse(self):
        for f in chain(glob("parse/*.SHX"), glob("parse/*.shx")):
            print(f"Attempt parsing of file: {str(f)}")
            shx = ShxFile(f)
            print(f"Parsed: {str(shx)} @ {str(f)}")
            paths = ShxPath()
            shx.render(paths, "hello world", 0)
            draw(paths, 1000, 100, shx.font_width, shx.font_height, f"{f}.png")


