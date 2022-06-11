from math import tau, cos, sin

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


def read_int_16le(stream):
    byte = bytearray(stream.read(2))
    if len(byte) == 2:
        return int_16le(byte)
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
            return bb.decode('utf8')
        if b == b'\r' or b == b'\n' or b == b'\x00':
            return bb.decode('utf8')
        bb += b


class ShxFile:
    def __init__(self, filename):
        self.format = None
        self.type = None
        self.version = None
        self.glyph_bytes = dict()
        self.glyphs = dict()
        self.font_name = "unknown"
        self.above = None
        self.below = None
        self.modes = None
        self._parse(filename)

    def __str__(self):
        return f'ShxFile for {self.font_name}'

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
                self.above = read_int_8(f)  # vector lengths above baseline
                self.below = read_int_8(f)  # vector lengths below baseline
                self.modes = read_int_8(f)  # 0 - Horizontal, 2 - dual. 0x0E command only when mode=2
                end = read_int_16le(f)
            else:
                self.glyph_bytes[index] = f.read(length)
        for b in self.glyph_bytes:
            self.glyphs[b] = self._parse_glyph(self.glyph_bytes[b], b)

    def _parse_bigfont(self, f):
        pass

    def _parse_unifont(self, f):
        pass

    def _parse_glyph(self, byte_glyph, glyph_index):
        b_glyph = bytearray(byte_glyph)
        stack = list()
        x = 0
        y = 0
        scale = 1.0
        points = list()
        pen = True
        while b_glyph:
            b = b_glyph.pop(0)
            direction = b & 0x0f
            length = (b & 0xf0) >> 4
            if length == 0:
                if direction == END_OF_SHAPE:
                    return points
                elif direction == PEN_DOWN:
                    pen = True
                elif direction == PEN_UP:
                    pen = False
                elif direction == DIVIDE_VECTOR:
                    scale /= b_glyph.pop(0)
                    continue
                elif direction == MULTIPLY_VECTOR:
                    scale *= b_glyph.pop(0)
                    continue
                elif direction == PUSH_STACK:
                    stack.append((x, y))
                    if len(stack) == 4:
                        raise IndexError(f"Position stack overflow in shape {chr(glyph_index)}")
                    continue
                elif direction == POP_STACK:
                    try:
                        x, y = stack.pop()
                    except IndexError:
                        raise IndexError(f"Position stack underflow in shape {chr(glyph_index)}")
                    if pen:
                        points.append((x, y))
                elif direction == DRAW_SUBSHAPE:
                    if self.type == "shapes":
                        glyph = b_glyph.pop(0)
                        b_glyph = bytearray(self.glyph_bytes[glyph]) + b_glyph
                    elif self.type == "bigfont":
                        # TODO: Requires some different scaling?
                        glyph = int_16le([b_glyph.pop(0), b_glyph.pop(0)])
                        b_glyph = bytearray(self.glyph_bytes[glyph]) + b_glyph
                    elif self.type == "unifont":
                        glyph = int_16le([b_glyph.pop(0), b_glyph.pop(0)])
                        b_glyph = bytearray(self.glyph_bytes[glyph]) + b_glyph
                    continue
                elif direction == XY_DISPLACEMENT:
                    dx = signed8(b_glyph.pop(0))
                    dy = signed8(b_glyph.pop(0))
                    y += dx * scale
                    x += dy * scale
                    if pen:
                        points.append((x, y))
                    continue
                elif direction == POLY_XY_DISPLACEMENT:
                    while True:
                        dx = signed8(b_glyph.pop(0))
                        dy = signed8(b_glyph.pop(0))
                        if dx == 0 and dy == 0:
                            break
                        y += dx * scale
                        x += dy * scale
                        if pen:
                            points.append((x, y))
                    continue
                elif direction == OCTANT_ARC:
                    octant = tau / 8.0
                    radius = b_glyph.pop(0)
                    sc = signed8(b_glyph.pop(0))
                    ccw = (sc >> 7) & 1
                    start = (sc >> 4) & 0x7
                    span = sc & 0x7
                    if span == 0:
                        span = 8
                    if ccw:
                        start = -start
                    start_octent = span * tau / 8.0
                    end_octent = start_octent + start
                    cx = -radius * cos(start_octent)
                    cy = -radius * sin(start_octent)
                    dx = cx + radius * cos(end_octent)
                    dy = cy + radius * sin(end_octent)
                    y += dx * scale
                    x += dy * scale
                    if pen:
                        points.append((x, y))
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
                    radius = 256 * b_glyph.pop(0) + b_glyph.pop(0)
                    sc = signed8(b_glyph.pop(0))
                    ccw = sc >= 0
                    sweep = (sc >> 4) & 0x7
                    sweep *= octant
                    c = sc & 0x7
                    if c == 0:
                        c = 8
                    if ccw:
                        sweep = -sweep
                    start_angle = start_offset + (c * octant)
                    end_angle = start_angle + sweep + end_offset
                    cx = -radius * cos(start_angle)
                    cy = -radius * sin(start_angle)
                    dx = cx + radius * cos(end_angle)
                    dy = cy + radius * sin(end_angle)
                    y += dx * scale
                    x += dy * scale
                    if pen:
                        points.append((x, y))
                elif direction == BULGE_ARC:
                    dx = signed8(b_glyph.pop(0))
                    dy = signed8(b_glyph.pop(0))
                    h = signed8(b_glyph.pop(0))
                    bulge = h / 127.0
                    y += dx * scale
                    x += dy * scale
                    if pen:
                        points.append((x, y))
                elif direction == POLY_BULGE_ARC:
                    while True:
                        dx = signed8(b_glyph.pop(0))
                        dy = signed8(b_glyph.pop(0))
                        if dx == 0 and dy == 0:
                            break
                        h = signed8(b_glyph.pop(0))
                        bulge = h / 127.0
                        y += dx * scale
                        x += dy * scale
                        if pen:
                            points.append((x, y))
                elif direction == COND_MODE_2:
                    pass
            else:
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
                    points.append((x, y))
        return points

    def _parse(self, filename):
        with open(filename, "br") as f:
            self._parse_header(f)
            if self.type == "shapes":
                self._parse_shapes(f)
            elif self.type == "bigfont":
                self._parse_bigfont(f)
            elif self.type == "unifont":
                self._parse_unifont(f)
