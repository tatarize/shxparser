# shxparser

Pure Python Parser for SHX Hershey font files.

SHX files are an AutoCad format which can encode single line fonts.

This format is used for many CNC and laser operations.

---

# Progress (Planning)

Things currently parse but, do not actually produce correct results. Also, very little has been done to check the `bigfont` and `unifont` types.

# Encoding
Calling the parser on a `SHX` file will parse the file. The glyph data is accessed via the `ShxFile.glyphs` dictionary which stores the particular commands.
These positions are stored (or will be) in segments. Each segment is:
* `(x0,y0)` -- Move to Position.
* `((x0,y0), (x1, y1))` --- Straight Line start->end
* `((x0,y0), (cx, cy), (x1, y1))` --- Arc start->control->end where control is a point on the arc that starts at start and ends at end.

Or something like that, I haven't really decided or figured it out yet.

# Format

For some format descriptions and explanations see:

* https://help.autodesk.com/view/ACD/2020/ENU/?guid=GUID-0A8E12A1-F4AB-44AD-8A9B-2140E0D5FD23

And:

* https://help.autodesk.com/view/ACD/2020/ENU/?guid=GUID-06832147-16BE-4A66-A6D0-3ADF98DC8228


Primarily the format performs regular (octant direction, distance) and 15 speciality operations.

## Regular Command
* Direction, Length pair. If Length is 0 then direction is special command.

## Special Commands
* END_OF_SHAPE - Ends the shape.
* PEN_DOWN - Puts the pen down into drawing mode.
* PEN_UP - Puts the pen up into move mode.
* DIVIDE_VECTOR - Applies a vector 1/scale
* MULTIPLY_VECTOR - Applies a vector scale
* PUSH_STACK - Pushes current position to the stack.
* POP_STACK - Pops current position from the stack.
* DRAW_SUBSHAPE - References the glyph data of another glyph.
* XY_DISPLACEMENT - Moves to a long dx, dy position.
* POLY_XY_DISPLACEMENT - Performs a sequence of long dx, dy position changes. 0,0 terminates.
* OCTANT_ARC - Performs an octant_arc operation. Performing an arc across some octants.
* FRACTIONAL_ARC - Performs an octant_arc operation with fractional value offsets.
* BULGE_ARC - Performs bulge arc operations with dx, dy, and bulge.
* POLY_BULGE_ARC - Performs a sequence of bulge arc operations. 0,0 terminates.
* COND_MODE_2 - Performs the next command conditionally, and only if the current mode is vertical.
