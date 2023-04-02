from geom import Point

### The coordinates of the kite cells that make up the hat polykite,
### given in the coordinate system defined in kitegrid.py.
hat = set( [
	Point( 0, -1 ),
	Point( 1, -1 ),
	Point( 1, 0 ),
	Point( 0, 1 ),
	Point( 1, 2 ),
	Point( 2, 1 ),
	Point( 3, -1 ),
	Point( 4, -1 ) ] )

## The hex cells of the *vertices* of the hat's outline. In the rest
## of the implementation of the kite grid we avoid referring explicitly
## to these vertex locations.  In other Laves grids they aren't
## so easily described, but it just so happens that in [3.4.6.4] you can
## easily associate hexagons in the underlying hex tiling with all tiles
## *and* all vertices.
hat_outline = [
	Point(0, 0),
	Point(-1,-1),
	Point(0,-2),
	Point(2,-2),
	Point(2,-1),
	Point(4,-2),
	Point(5,-1),
	Point(4, 0),
	Point(3, 0),
	Point(2, 2),
	Point(0, 3),
	Point(0, 2),
	Point(-1, 2) ]
