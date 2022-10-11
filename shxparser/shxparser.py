from math import tau, cos, sin, atan2

SHXPARSER_VERSION = "0.0.1"


END_OF_SHAPE = 0
PEN_DOWN = 1
PEN_UP = 2
DIVIDE_VECTOR = 3
MULTIPLY_VECTOR = 4
PUSH_STACK = 5
POP_STACK = 6
DRAW_SUBSHAPE = 7
XY_DISPLACEMENT = 8
POLY_XY_DISPLACEMENT = 9  # 0,0 terminated
OCTANT_ARC = 0xA
FRACTIONAL_ARC = 0xB  # 5 bytes, start, end, high radius, radius, ±0SC
BULGE_ARC = 0xC  # dx, dy, bulge
POLY_BULGE_ARC = 0xD  # 0,0 terminated BULGE_ARC
COND_MODE_2 = 0x0E  # PROCESS this command *only if mode=2*


def signed8(b):
    if b > 127:
        return -256 + b
    else:
        return b


def int_16le(byte):
    return (byte[0] & 0xFF) + ((byte[1] & 0xFF) << 8)


def int_32le(b):
    return (
        (b[0] & 0xFF)
        + ((b[1] & 0xFF) << 8)
        + ((b[2] & 0xFF) << 16)
        + ((b[3] & 0xFF) << 24)
    )


def read_int_8(stream):
    byte = bytearray(stream.read(1))
    if len(byte) == 1:
        return byte[0]
    return None


def read_int_16le(stream):
    byte = bytearray(stream.read(2))
    if len(byte) == 2:
        return int_16le(byte)
    return None


def read_int_32le(stream):
    b = bytearray(stream.read(4))
    if len(b) == 4:
        return int_32le(b)
    return None


def read_string(stream):
    bb = bytearray()
    while True:
        b = stream.read(1)
        if b == b"":
            return bb.decode("utf-8")
        if b == b"\r" or b == b"\n" or b == b"\x00":
            return bb.decode("utf-8")
        bb += b


class ShxPath:
    """
    Example path code. Any class with these functions would work as well. When render is called on the ShxFont class
    the path is given particular useful segments.
    """

    def __init__(self):
        self.path = list()

    def new_path(self):
        """
        Start of a new path.
        """
        self.path.append(None)

    def move(self, x, y):
        """
        Move current point to the point specified.
        """
        self.path.append((x, y))

    def line(self, x0, y0, x1, y1):
        """
        Draw a line from the current point to the specified point.
        """
        self.path.append((x0, y0, x1, y1))

    def arc(self, x0, y0, cx, cy, x1, y1):
        """
        Draw an arc from the current point to specified point going through the control point.

        3 Points define a circular arc, there is only one arc which travels from start to end going through a given
        control point. The exceptions are when the arc points are collinear or two arc points are coincident. In some
        cases the start and end points will be equal and the control point will be located the circle diameter away.
        """
        self.path.append((x0, y0, cx, cy, x1, y1))


class ShxFontParseError(Exception):
    """
    Exception thrown if unable to pop a value from the given codes or other suspected parsing errors.
    """


class ShxFont:
    """
    This class performs the parsing of the three major types of .SHX fonts. Composing them into specific glyphs which
    consist of commands in a vector-shape language. When .render() is called on some text, vector actions are performed
    on the font which create the vector path.
    """

    def __init__(self, filename, debug=False):
        self.format = None  # format (usually AutoCAD-86)
        self.type = None  # Font type: shapes, bigfont, unifont
        self.version = None  # Font file version (usually 1.0).
        self.glyphs = dict()  # Glyph dictionary
        self.font_name = "unknown"  # Parsed font name.
        self.above = None  # Distance above baseline for capital letters.
        self.below = None  # Distance below baseline for lowercase letters
        self.modes = None  # 0 Horizontal Only, 2 Dual mode (Horizontal or Vertical)
        self.encoding = False  # 0 unicode, 1 packed multibyte, 2 shape file
        self.embedded = False  # 0 font can be embedded, 1 font cannot be embedded, 2 embedding is read-only
        self._debug = debug
        self._parse(filename)
        self._code = None
        self._path = None
        self._skip = False
        self._pen = False
        self._horizontal = True
        self._letter = None
        self._x = 0
        self._y = 0
        self._last_x = 0
        self._last_y = 0
        self._scale = 1
        self._stack = []

    def __str__(self):
        return f'{self.type}("{self.font_name}", {self.version}, glyphs: {len(self.glyphs)})'

    def _parse(self, filename):
        with open(filename, "br") as f:
            self._parse_header(f)
            if self._debug:
                print(f"Font header indicates font type is {self.type}")
            if self.type == "shapes":
                self._parse_shapes(f)
            elif self.type == "bigfont":
                self._parse_bigfont(f)
            elif self.type == "unifont":
                self._parse_unifont(f)

    def _parse_header(self, f):
        header = read_string(f)
        parts = header.split(" ")
        self.format = parts[0]
        self.type = parts[1]
        self.version = parts[2]
        f.read(2)

    def _parse_shapes(self, f):
        start = read_int_16le(f)
        end = read_int_16le(f)
        count = read_int_16le(f)
        if self._debug:
            print(f"Parsing shape: start={start}, end={end}, count={count}")
        glyph_ref = list()
        for i in range(count):
            index = read_int_16le(f)
            length = read_int_16le(f)
            glyph_ref.append((index, length))

        for index, length in glyph_ref:
            if index == 0:
                self.font_name = read_string(f)
                self.above = read_int_8(f)  # vector lengths above baseline
                self.below = read_int_8(f)  # vector lengths below baseline
                # 0 - Horizontal, 2 - dual. 0x0E command only when mode=2
                self.modes = read_int_8(f)
                # end = read_int_16le(f)
            else:
                self.glyphs[index] = f.read(length)

    def _parse_bigfont(self, f):
        count = read_int_16le(f)
        length = read_int_16le(f)
        changes = list()
        change_count = read_int_16le(f)
        if self._debug:
            print(f"Parsing bigfont: count={count}, length={length}, change_count={change_count}")
        for i in range(change_count):
            start = read_int_16le(f)
            end = read_int_16le(f)
            changes.append((start, end))

        glyph_ref = list()
        for i in range(count):
            index = read_int_16le(f)
            length = read_int_16le(f)
            offset = read_int_32le(f)
            glyph_ref.append((index, length, offset))

        for index, length, offset in glyph_ref:
            f.seek(offset, 0)
            if index == 0:
                # self.font_name = read_string(f)
                self.above = read_int_8(f)  # vector lengths above baseline
                self.below = read_int_8(f)  # vector lengths below baseline
                # 0 - Horizontal, 2 - dual. 0x0E command only when mode=2
                self.modes = read_int_8(f)

            else:
                self.glyphs[index] = f.read(length)

    def _parse_unifont(self, f):
        count = read_int_32le(f)
        length = read_int_16le(f)
        f.seek(5)
        self.font_name = read_string(f)
        self.above = read_int_8(f)
        self.below = read_int_8(f)
        self.mode = read_int_8(f)
        self.encoding = read_int_8(f)
        self.embedded = read_int_8(f)
        ignore = read_int_8(f)
        if self._debug:
            print(f"Parsing unifont: name={self.font_name}, count={count}, length={length}")
        for i in range(count - 1):
            index = read_int_16le(f)
            length = read_int_16le(f)
            self.glyphs[index] = f.read(length)

    def pop(self):
        try:
            code_pop = self._code.pop()
            if self._debug:
                print(f"{code_pop} popped {len(self._code)}")
            return code_pop
        except IndexError as e:
            raise ShxFontParseError("No codes to pop()") from e

    def render(self, path, text, horizontal=True, font_size=12.0):
        self._scale = font_size / self.above
        self._horizontal = horizontal
        self._path = path
        for letter in text:
            self._letter = letter
            try:
                self._code = bytearray(reversed(self.glyphs[ord(letter)]))
            except KeyError:
                # Letter is not found.
                continue
            self._pen = True
            while self._code:
                self._parse_code()
            self._skip = False
        if self._debug:
            print(f"Render Complete.\n\n\n")

    def _parse_code(self):
        b = self.pop()
        direction = b & 0x0F
        length = (b & 0xF0) >> 4
        if length == 0:
            self._parse_code_special(direction)
        else:
            self._parse_code_length(direction, length)

    def _parse_code_length(self, direction, length):
        if self._skip:
            return
        if self._debug:
            print(f"MOVE DIRECTION {direction}")
        if direction in (2, 1, 0, 0xF, 0xE):
            dx = 1.0
        elif direction in (3, 0xD):
            dx = 0.5
        elif direction in (4, 0xC):
            dx = 0.0
        elif direction in (5, 0xB):
            dx = -0.5
        else:  # (6, 7, 8, 9, 0xa):
            dx = -1.0
        if direction in (6, 5, 4, 3, 2):
            dy = 1.0
        elif direction in (7, 1):
            dy = 0.5
        elif direction in (8, 0):
            dy = 0.0
        elif direction in (9, 0xF):
            dy = -0.5
        else:  # (0xa, 0xb, 0xc, 0xd, 0xe, 0xf):
            dy = -1.0
        self._x += dx * length * self._scale
        self._y += dy * length * self._scale
        if self._pen:
            self._path.line(self._last_x, self._last_y, self._x, self._y)
        else:
            self._path.move(self._x, self._y)
        self._last_x, self._last_y = self._x, self._y

    def _parse_code_special(self, special):
        if special == END_OF_SHAPE:
            self._end_of_shape()
        elif special == PEN_DOWN:
            self._pen_down()
        elif special == PEN_UP:
            self._pen_up()
        elif special == DIVIDE_VECTOR:
            self._divide_vector()
        elif special == MULTIPLY_VECTOR:
            self._multiply_vector()
        elif special == PUSH_STACK:
            self._push_stack()
        elif special == POP_STACK:
            self._pop_stack()
        elif special == DRAW_SUBSHAPE:
            self._draw_subshape()
        elif special == XY_DISPLACEMENT:
            self._xy_displacement()
        elif special == POLY_XY_DISPLACEMENT:
            self._poly_xy_displacement()
        elif special == OCTANT_ARC:
            self._octant_arc()
        elif special == FRACTIONAL_ARC:
            self._fractional_arc()
        elif special == BULGE_ARC:
            self._bulge_arc()
        elif special == POLY_BULGE_ARC:
            self._poly_bulge_arc()
        elif special == COND_MODE_2:
            self._cond_mode_2()

    def _end_of_shape(self):
        if self._debug:
            print("END_OF_SHAPE")
        self._path.new_path()

    def _pen_down(self):
        if self._debug:
            print(f"PEN_DOWN {self._x}, {self._y}")
        if not self._skip:
            self._pen = True
            self._path.move(self._x, self._y)
        elif self._debug:
            print(f"Skipped.")

    def _pen_up(self):
        if self._debug:
            print("PEN_UP")
        if not self._skip:
            self._pen = False
        elif self._debug:
            print(f"Skipped.")

    def _divide_vector(self):
        factor = self.pop()
        if not self._skip:
            self._scale /= factor
        elif self._debug:
            print(f"Skipped.")
        if self._debug:
            print(f"DIVIDE_VECTOR {factor} changes scale to {self._scale}")

    def _multiply_vector(self):
        factor = self.pop()
        if not self._skip:
            self._scale *= factor
        elif self._debug:
            print(f"Skipped.")
        if self._debug:
            print(f"DIVIDE_VECTOR {factor} changes scale to {self._scale}")

    def _push_stack(self):
        if not self._skip:
            if self._debug:
                print(f"PUSH_STACK {self._x}, {self._y}")
            self._stack.append((self._x, self._y))
            if len(self._stack) == 4:
                raise IndexError(
                    f"Position stack overflow in shape {self._letter}"
                )
        elif self._debug:
            print(f"Skipped.")

    def _pop_stack(self):
        if self._debug:
            print(f"POP_STACK {self._x}, {self._y}")
        if not self._skip:
            try:
                x, y = self._stack.pop()
                if self._debug:
                    print(f"Popped value: {x}, {y}: {len(self._stack)}")
            except IndexError:
                raise IndexError(
                    f"Position stack underflow in shape {self._letter}"
                )
            self._path.move(x, y)
            self._last_x, self._last_y = self._x, self._y
        elif self._debug:
            print(f"Skipped.")

    def _draw_subshape_shapes(self):
        if self._debug:
            print("subshape within shapes")
        subshape = self.pop()
        if not self._skip:
            self._code += bytearray(reversed(self.glyphs[subshape]))
            if self._debug:
                print(f"Appending glyph {subshape}.")

    def _draw_subshape_bigfont(self):
        if self._debug:
            print("subshape within bigfont")
        subshape = self.pop()
        if subshape == 0:
            subshape = int_16le([self.pop(), self.pop()])
            origin_x = self.pop() * self._scale
            origin_y = self.pop() * self._scale
            width = self.pop() * self._scale
            height = self.pop() * self._scale
        if not self._skip:
            try:
                self._code += bytearray(
                    reversed(self.glyphs[subshape])
                )
                if self._debug:
                    print(f"Appending glyph {subshape}.")
            except KeyError as e:
                raise ShxFontParseError from e
        elif self._debug:
            print(f"Skipped.")

    def _draw_subshape_unifont(self):
        if self._debug:
            print("subshape within unifont")
        subshape = int_16le([self.pop(), self.pop()])
        if not self._skip:
            self._code += bytearray(reversed(self.glyphs[subshape]))
            if self._debug:
                print(f"Appending glyph {subshape}.")
        elif self._debug:
            print(f"Skipped.")

    def _draw_subshape(self):
        if self._debug:
            print("DRAW_SUBSHAPE")
        if self.type == "shapes":
            self._draw_subshape_shapes()
        elif self.type == "bigfont":
            self._draw_subshape_bigfont()
        elif self.type == "unifont":
            self._draw_subshape_unifont()

    def _xy_displacement(self):
        dx = signed8(self.pop()) * self._scale
        dy = signed8(self.pop()) * self._scale
        if self._debug:
            print(f"XY_DISPLACEMENT {dx} {dy}")
        if not self._skip:
            self._x += dx
            self._y += dy
            if self._pen:
                self._path.line(self._last_x, self._last_y, self._x, self._y)
            else:
                self._path.move(self._x, self._y)
            self._last_x, self._last_y = self._x, self._y
        elif self._debug:
            print(f"Skipped.")

    def _poly_xy_displacement(self):
        while True:
            dx = signed8(self.pop()) * self._scale
            dy = signed8(self.pop()) * self._scale
            if self._debug:
                print(f"POLY_XY_DISPLACEMENT {dx} {dy}")
            if dx == 0 and dy == 0:
                break
            if not self._skip:
                self._x += dx
                self._y += dy
                if self._pen:
                    self._path.line(self._last_x, self._last_y, self._x, self._y)
                else:
                    self._path.move(self._x, self._y)
                self._last_x, self._last_y = self._x, self._y
            elif self._debug:
                print(f"Skipped.")

    def _octant_arc(self):
        if self._debug:
            print("OCTANT_ARC")
        radius = self.pop() * self._scale
        sc = signed8(self.pop())
        if not self._skip:
            octant = tau / 8.0
            ccw = (sc >> 7) & 1
            s = (sc >> 4) & 0x7
            c = sc & 0x7
            if c == 0:
                c = 8
            if ccw:
                s = -s
            start_angle = s * octant
            end_angle = (c + s) * octant
            mid_angle = (start_angle + end_angle) / 2
            # negative radius in the direction of start_octent finds center.
            cx = self._x - radius * cos(start_angle)
            cy = self._y - radius * sin(start_angle)
            mx = cx + radius * cos(mid_angle)
            my = cy + radius * sin(mid_angle)
            self._x = cx + radius * cos(end_angle)
            self._y = cy + radius * sin(end_angle)
            if self._pen:
                self._path.arc(self._last_x, self._last_y, mx, my, self._x, self._y)
            else:
                self._path.move(self._x, self._y)
            self._last_x, self._last_y = self._x, self._y

    def _fractional_arc(self):
        """
        Fractional Arc.
        Octant Arc plus fractional bits 0-255 parts of 45°
        55° -> (55 - 45) * (256 / 45) = 56 (octent 1)
        45° + (56/256 * 45°) = 55°
        95° -> (95 - 90) * (256 / 45) = 28 (octent 2)
        90° + (28/256 * 45°) = 95°
        """
        if self._debug:
            print("FRACTION_ARC")
        octant = tau / 8.0
        start_offset = octant * self.pop() / 256.0
        end_offset = octant * self.pop() / 256.0
        radius = (256 * self.pop() + self.pop()) * self._scale
        sc = signed8(self.pop())
        if not self._skip:
            ccw = (sc >> 7) & 1
            s = (sc >> 4) & 0x7
            c = sc & 0x7
            if c == 0:
                c = 8
            if ccw:
                s = -s
            start_angle = start_offset + (s * octant)
            end_angle = (c + s) * octant + end_offset
            mid_angle = (start_angle + end_angle) / 2
            cx = self._x - radius * cos(start_angle)
            cy = self._y - radius * sin(start_angle)
            mx = cx + radius * cos(mid_angle)
            my = cy + radius * sin(mid_angle)
            self._x = cx + radius * cos(end_angle)
            self._y = cy + radius * sin(end_angle)
            if self._pen:
                self._path.arc(self._last_x, self._last_y, mx, my, self._x, self._y)
            else:
                self._path.move(self._x, self._y)
            self._last_x, self._last_y = self._x, self._y

    def _bulge_arc(self):
        if self._debug:
            print("BULGE_ARC")
        dx = signed8(self.pop()) * self._scale
        dy = signed8(self.pop()) * self._scale
        h = signed8(self.pop())
        if not self._skip:
            r = abs(complex(dx, dy)) / 2
            bulge = h / 127.0
            bx = self._x + (dx / 2)
            by = self._y + (dy / 2)
            bulge_angle = atan2(dy, dx) - tau / 4
            mx = bx + r * bulge * cos(bulge_angle)
            my = by + r * bulge * sin(bulge_angle)
            self._x += dx
            self._y += dy
            if self._pen:
                if bulge == 0:
                    self._path.line(self._x, self._y)
                else:
                    self._path.arc(self._last_x, self._last_y, mx, my, self._x, self._y)
            else:
                self._path.move(self._x, self._y)
            self._last_x, self._last_y = self._x, self._y

    def _poly_bulge_arc(self):
        while True:
            if self._debug:
                print("POLY_BULGE_ARC")
            dx = signed8(self.pop()) * self._scale
            dy = signed8(self.pop()) * self._scale
            if dx == 0 and dy == 0:
                break
            h = signed8(self.pop())
            if not self._skip:
                r = abs(complex(dx, dy)) / 2
                bulge = h / 127.0
                bx = self._x + (dx / 2)
                by = self._y + (dy / 2)
                bulge_angle = atan2(dy, dx) - tau / 4
                mx = bx + r * bulge * cos(bulge_angle)
                my = by + r * bulge * sin(bulge_angle)
                self._x += dx
                self._y += dy
                if self._pen:
                    if bulge == 0:
                        self._path.line(self._last_x, self._last_y, self._x, self._y)
                    else:
                        self._path.arc(self._last_x, self._last_y, mx, my, self._x, self._y)
                else:
                    self._path.move(self._x, self._y)
                self._last_x, self._last_y = self._x, self._y

    def _cond_mode_2(self):
        if self._debug:
            print("COND_MODE_2")
        if self.modes == 2 and self._horizontal:
            if self._debug:
                print("SKIP NEXT")
            self._skip = True
            return
