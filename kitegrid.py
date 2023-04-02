### Manage cells in the [3.4.6.4] tiling using integer coordinates.
### First, we give integer coordinates to the hexagons in the regular
### [3^6] tiling, by giving coordinates relative to a basis with axes
### (1,0) and (1/2,sqrt(3)/2).  Then we superimpose a scaled-up kite
### tiling, so that every kite is uniquely associated with a hexagon
### (and a fraction of the hexagons don't have a corresponding kite).
### See the illustration in kitegrid.pdf.

import sys

from geom import Point, Transform

c_offsets = [
	[None, Point(-1,0), None, None, None, Point(1,0)],
	[None, Point(0,1), Point(-1,1), None, Point(1,-1), Point(0,-1)] ]

## Rotate 60 degrees CCW
R60 = Transform( 0, -1, 0, 1, 1, 0 )
## Rotate 60 degrees CW
R300 = Transform( 1, 1, 0, -1, 0, 0 )

def getSixfoldCentre( p ):
	'''Every kite in the kite grid is adjacent to exactly one
	centre of sixfold rotation.  Return that point.'''
	return p + c_offsets[p.y%2][(p.x-p.y)%6]

def canTranslate( p, q ):
	'''Check whether p and q are related by a translation of the
	kite grid.'''
	return (p-getSixfoldCentre(p)) == (q-getSixfoldCentre(q))

def getAdjacents( p ):
	'''Get a set of the four kite cells that share an edge with p'''
	c = getSixfoldCentre( p )
	v = p - c
	left = R60 * v
	right = R300 * v
	return set([c + left, c + right, p + v + left, p + v + right])

def getNeighbours( p ):
	'''Get a cyclic list of the nine kite cells that share an edge or a 
	vertex with p, in cyclic order around the cell'''
	c = getSixfoldCentre( p )
	v = p - c
	left = R60 * v
	right = R300 * v
	return [c + left, c - right, c - v, c - left, c + right,
		p + right * 2, p + v + right, p + v + left, p + left * 2]

def getNeighbourSet( p ):
	return set( getNeighbours( p ) )

def getHalo( sop ):
	'''Get a set of all the kite cells that are neighbours of any
	cell in the set sop, excluding cells in sop itself'''
	hset = set()
	for p in sop:
		ns = getNeighbourSet( p )
		for n in ns:
			hset.add( n )
	return hset - sop

def getRainbow( p, h, sop ):
	'''A helper function for getOrderedHalo().  Given cell p in shape
	sop, get the arc of p's neighbours outside of sop that contains h.
	Return the list of halo cells encountered and the first shape cell 
	after them.'''

	ns = getNeighbours( p )
	i = ns.index( h ) + len(ns)

	## Walk back to the first non-sop cell 
	while ns[(i-1)%len(ns)] not in sop:
		i = i - 1

	ret = []
	while ns[i%len(ns)] not in sop:
		ret.append( ns[i%len(ns)] )
		i = i + 1

	return (ret, ns[i%len(ns)])

def getHaloStart( sop ):
	'''Get a suitable starting cell for an ordered halo.  This is any
	cell in sop that's adjacent to a cell not in sop across one of its
	edges.  Return the cell and the halo neighbour.'''

	start = None

	for p in sop:
		ans = getAdjacents( p )

		for a in ans:
			if a not in sop:
				return (p,a)
				
def getOrderedHalo( sop ):
	'''Given a shape, get a cyclic list of all neighbouring kite cells 
	that circle the border.  The list might omit cells that were
	covered earlier, but that's OK.'''

	used = sop.copy()

	start, h = getHaloStart( sop )

	cur = start
	ret = []

	while True:
		rainbow, next = getRainbow( cur, h, sop )

		## Add the subset of the rainbow that's not already used
		for p in rainbow:
			if not p in used:
				ret.append( p )
				used.add( p )

		cur = next
		h = rainbow[-1]

		if cur == start:
			break

	return ret

def isSimplyConnected( sop ):
	'''Check whether the set of kite cells given by sop is simply
	connected'''

	## This can be computed by checking that sop's halo is a single
	## connected component relative to edge adjacencies.
	halo = getHalo( sop )
	visited = set()

	## Pick a random halo element
	p = next(iter(halo))
	work = [p]
	visited.add( p )

	## Depth first search
	while len( work ) > 0:
		p = work.pop()
		ns = getAdjacents( p )
		for n in ns:
			if (n in halo) and (n not in visited):
				visited.add( n )
				work.append( n )

	## Did you visit the whole halo?
	return len( visited ) == len( halo )

def getAllOrientations():
	'''Produce a list of 12 transformation matrices corresponding to 
	all possible orientations of a shape in the kite grid'''

	## Reflect the hex grid across the X axis
	Fy = Transform( 1, 1, 0, 0, -1, 0 )

	ret = []
	T = Transform()

	for i in range( 6 ):
		ret.append( T )
		ret.append( Fy * T )
		T = R60 * T

	return ret

orientations = getAllOrientations()
