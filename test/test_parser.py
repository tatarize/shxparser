import unittest
from glob import glob

from shxparser.shxparser import ShxFile


class TestParser(unittest.TestCase):
    """Tests the parsing functionality."""

    def test_parse(self):
        for f in glob("parse/*"):
            print(f"Attempt parsing of file: {str(f)}")
            shx = ShxFile(f)
            print(f"Parsed: {str(shx)} @ {str(f)}")


