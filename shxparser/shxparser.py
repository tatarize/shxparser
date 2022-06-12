from math import tau, cos, sin, atan2

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


def read_int_8(stream):
    byte = bytearray(stream.read(1))
    if len(byte) == 1:
        return byte[0]
    return None


def read_string(stream):
    bb = bytearray()
    while True:
        b = stream.read(1)
        if b == b'':
            return bb.decode('utf-8')
        if b == b'\r' or b == b'\n' or b == b'\x00':
            return bb.decode('utf-8')
        bb += b


class ShxPath:
    def __init__(self):
        self.path = list()
        self.last_x = None
        self.last_y = None

    def new_path(self):
        self.path.append(None)
        self.last_x = None
        self.last_y = None

    def move(self, x, y):
        self.path.append((x,y))
        self.last_x = x
        self.last_y = y

    def line(self, x, y):
        if self.last_x is not None or self.last_y is not None:
            self.path.append((self.last_x, self.last_y, x, y))
        self.last_x = x
        self.last_y = y

    def arc(self, cx, cy,  x, y):
        if self.last_x is not None or self.last_y is not None:
            self.path.append((self.last_x, self.last_y, cx, cy, x, y))
        self.last_x = x
        self.last_y = y


class ShxFile:
    def __init__(self, filename):
        self.format = None
        self.type = None
        self.version = None
        self.glyph_bytes = dict()
        self.glyphs = dict()
        self.font_name = "unknown"
        self.font_height = None
        self.font_width = None
        self.modes = None
        self.unicode = False
        self.embedded = False
        self._stack = []
        self._parse(filename)

    def __str__(self):
        return f'{self.type}("{self.font_name}", {self.version}, glyphs: {len(self.glyph_bytes)})'

    def render(self, path, text, horizontal=True):
        skip = False
        x = 0
        y = 0
        scale = 1.0
        stack = []
        for letter in text:
            try:
                byte_glyph = self.glyph_bytes[ord(letter)]
            except KeyError:
                # Letter is not found.
                continue
            b_glyph = bytearray(byte_glyph)
            pen = False
            while b_glyph:
                b = b_glyph.pop(0)
                direction = b & 0x0f
                length = (b & 0xf0) >> 4
                if length == 0:
                    if direction == END_OF_SHAPE:
                        path.new_path()
                    elif direction == PEN_DOWN:
                        if not skip:
                            pen = True
                            path.move(x,y)
                    elif direction == PEN_UP:
                        if not skip:
                            pen = False
                    elif direction == DIVIDE_VECTOR:
                        factor = b_glyph.pop(0)
                        if not skip:
                            scale /= factor
                    elif direction == MULTIPLY_VECTOR:
                        factor = b_glyph.pop(0)
                        if not skip:
                            scale *= factor
                    elif direction == PUSH_STACK:
                        if not skip:
                            stack.append((x, y))
                            if len(self._stack) == 4:
                                raise IndexError(f"Position stack overflow in shape {letter}")
                    elif direction == POP_STACK:
                        if not skip:
                            try:
                                x, y = stack.pop()
                            except IndexError:
                                raise IndexError(f"Position stack underflow in shape {letter}")
                            path.move(x, y)
                    elif direction == DRAW_SUBSHAPE:
                        if self.type == "shapes":
                            glyph = b_glyph.pop(0)
                            if not skip:
                                b_glyph = bytearray(self.glyph_bytes[glyph]) + b_glyph
                        elif self.type == "bigfont":
                            glyph = b_glyph.pop(0)
                            if glyph == 0:
                                glyph = int_16le([b_glyph.pop(0), b_glyph.pop(0)])
                                origin_x = b_glyph.pop(0) * scale
                                origin_y = b_glyph.pop(0) * scale
                                width = b_glyph.pop(0) * scale
                                height = b_glyph.pop(0) * scale
                            if not skip:
                                try:
                                    b_glyph = bytearray(self.glyph_bytes[glyph]) + b_glyph
                                except KeyError:
                                    pass  # TODO: Likely some bug here.
                        elif self.type == "unifont":
                            glyph = int_16le([b_glyph.pop(0), b_glyph.pop(0)])
                            if not skip:
                                b_glyph = bytearray(self.glyph_bytes[glyph]) + b_glyph
                    elif direction == XY_DISPLACEMENT:
                        dx = signed8(b_glyph.pop(0)) * scale
                        dy = signed8(b_glyph.pop(0)) * scale
                        if not skip:
                            x += dx
                            y += dy
                            if pen:
                                path.line(x, y)
                            else:
                                path.move(x, y)
                    elif direction == POLY_XY_DISPLACEMENT:
                        while True:
                            dx = signed8(b_glyph.pop(0)) * scale
                            dy = signed8(b_glyph.pop(0)) * scale
                            if dx == 0 and dy == 0:
                                break
                            if not skip:
                                x += dx
                                y += dy
                                if pen:
                                    path.line(x, y)
                                else:
                                    path.move(x, y)
                    elif direction == OCTANT_ARC:
                        radius = b_glyph.pop(0) * scale
                        sc = signed8(b_glyph.pop(0))
                        if not skip:
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
                            cx = x - radius * cos(start_angle)
                            cy = y - radius * sin(start_angle)
                            mx = cx + radius * cos(mid_angle)
                            my = cy + radius * sin(mid_angle)
                            x = cx + radius * cos(end_angle)
                            y = cy + radius * sin(end_angle)
                            if pen:
                                path.arc(mx, my, x, y)
                            else:
                                path.move(x, y)
                    elif direction == FRACTIONAL_ARC:
                        """
                        Fractional Arc.
                        Octant Arc plus fractional bits 0-255 parts of 45°
                        55° -> (55 - 45) * (256 / 45) = 56 (octent 1)
                        45° + (56/256 * 45°) = 55°
                        95° -> (95 - 90) * (256 / 45) = 28 (octent 2)
                        90° + (28/256 * 45°) = 95°
                        """
                        octant = tau / 8.0
                        start_offset = octant * b_glyph.pop(0) / 256.0
                        end_offset = octant * b_glyph.pop(0) / 256.0
                        radius = (256 * b_glyph.pop(0) + b_glyph.pop(0)) * scale
                        sc = signed8(b_glyph.pop(0))
                        if not skip:
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
                            cx = x - radius * cos(start_angle)
                            cy = y - radius * sin(start_angle)
                            mx = cx + radius * cos(mid_angle)
                            my = cy + radius * sin(mid_angle)
                            x = cx + radius * cos(end_angle)
                            y = cy + radius * sin(end_angle)
                            if pen:
                                path.arc(mx, my, x, y)
                            else:
                                path.move(x, y)
                    elif direction == BULGE_ARC:
                        dx = signed8(b_glyph.pop(0)) * scale
                        dy = signed8(b_glyph.pop(0)) * scale
                        h = signed8(b_glyph.pop(0))
                        if not skip:
                            r = abs(complex(dx, dy)) / 2
                            bulge = h / 127.0
                            bx = x + (dx / 2)
                            by = y + (dy / 2)
                            bulge_angle = atan2(dy, dx) - tau / 4
                            mx = bx + r * bulge * cos(bulge_angle)
                            my = by + r * bulge * sin(bulge_angle)
                            x += dx
                            y += dy
                            if pen:
                                if bulge == 0:
                                    path.line(x, y)
                                else:
                                    path.arc(mx, my, x, y)
                            else:
                                path.move(x, y)
                    elif direction == POLY_BULGE_ARC:
                        while True:
                            dx = signed8(b_glyph.pop(0)) * scale
                            dy = signed8(b_glyph.pop(0)) * scale
                            if dx == 0 and dy == 0:
                                break
                            h = signed8(b_glyph.pop(0))
                            if not skip:
                                r = abs(complex(dx, dy)) / 2
                                bulge = h / 127.0
                                bx = x + (dx / 2)
                                by = y + (dy / 2)
                                bulge_angle = atan2(dy, dx) - tau / 4
                                mx = bx + r * bulge * cos(bulge_angle)
                                my = by + r * bulge * sin(bulge_angle)
                                x += dx
                                y += dy
                                if pen:
                                    if bulge == 0:
                                        path.line(x, y)
                                    else:
                                        path.arc(mx, my, x, y)
                                else:
                                    path.move(x, y)
                    elif direction == COND_MODE_2:
                        if self.modes == 2 and horizontal:
                            skip = True
                            continue
                else:
                    if not skip:
                        if direction in (2, 1, 0, 0xf, 0xe):
                            dx = 1.0
                        elif direction in (3, 0xd):
                            dx = 0.5
                        elif direction in (4, 0xc):
                            dx = 0.0
                        elif direction in (5, 0xb):
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
                        x += dx * length * scale
                        y += dy * length * scale
                        if pen:
                            path.line(x, y)
                        else:
                            path.move(x, y)
                skip = False

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
        glyph_ref = list()
        for i in range(count):
            index = read_int_16le(f)
            length = read_int_16le(f)
            glyph_ref.append((index,length))

        for index, length in glyph_ref:
            if index == 0:
                self.font_name = read_string(f)
                self.font_height = read_int_8(f)  # vector lengths above baseline
                self.font_width = read_int_8(f)  # vector lengths below baseline
                self.modes = read_int_8(f)  # 0 - Horizontal, 2 - dual. 0x0E command only when mode=2
                end = read_int_16le(f)
            else:
                self.glyph_bytes[index] = f.read(length)

    def _parse_bigfont(self, f):
        count = read_int_16le(f)
        length = read_int_16le(f)
        changes = list()
        change_count = read_int_16le(f)
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
            f.seek(offset,0)
            if index == 0:
                # self.font_name = read_string(f)
                self.font_height = read_int_8(f)  # vector lengths above baseline
                self.font_width = read_int_8(f)  # vector lengths below baseline
                self.modes = read_int_8(f)  # 0 - Horizontal, 2 - dual. 0x0E command only when mode=2
            else:
                self.glyph_bytes[index] = f.read(length)[1:]

    def _parse_unifont(self, f):
        count = read_int_32le(f)
        length = read_int_16le(f)
        f.seek(5)
        self.font_name = read_string(f)
        self.font_height = read_int_8(f)
        self.font_width = read_int_8(f)
        self.mode = read_int_8(f)
        self.unicode = read_int_8(f)
        self.embedded = read_int_8(f)
        ignore = read_int_8(f)
        for i in range(count-1):
            index = read_int_16le(f)
            length = read_int_16le(f)
            self.glyph_bytes[index] = f.read(length)[1:]

    def _parse(self, filename):
        with open(filename, "br") as f:
            self._parse_header(f)
            if self.type == "shapes":
                self._parse_shapes(f)
            elif self.type == "bigfont":
                self._parse_bigfont(f)
            elif self.type == "unifont":
                self._parse_unifont(f)
