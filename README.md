# shxparser

Pure Python Parser for SHX Hershey font files.

SHX files are an AutoCad format which encodes single line fonts. This format is used for many CNC and laser operations where filled fonts are not as useful or helpful.

For some format descriptions and explanations see:

* https://help.autodesk.com/view/ACD/2020/ENU/?guid=GUID-0A8E12A1-F4AB-44AD-8A9B-2140E0D5FD23

And:

* https://help.autodesk.com/view/ACD/2020/ENU/?guid=GUID-06832147-16BE-4A66-A6D0-3ADF98DC8228

--

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
* OCTANT_ARC - Performs a octant_arc operation. Performing an arc across some octants.
* FRACTIONAL_ARC - Performs a octant_arc operation with fractional value offsets.
* BULGE_ARC - Performs bulge arc operations with dx, dy, and bulge.
* POLY_BULGE_ARC - Performs a sequence of bulge arc operations. 0,0 terminates.
* COND_MODE_2 - Performs the next command conditionally, and only if the current mode is vertical.
