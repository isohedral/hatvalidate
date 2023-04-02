import sys

from geom import *
from hat import hat
from kitegrid import *
from patchmap import *

hat_halo = getHalo( hat )

def getLegalNeighbours( allow_holes = False ):
	'''Construct a set of transformation matrices that carry the
	identity hat to a position and orientation that touches it 
	without overlapping'''

	## For every orientation of the hat, translate each of its cells
	## to every halo cell of the identity hat.  If the result is 
	## simply connected and doesn't overlap the identity hat, keep it.

	halo = getHalo( hat )
	ret = set()

	for T in orientations:
		o_hat = set( [T * p for p in hat] )
		for hp in halo:
			for op in o_hat:
				## Not all integer vectors are legal translations in
				## the kite grid.  Check only those that are.
				if canTranslate( op, hp ):
					t_hat = set( [p + (hp-op) for p in o_hat] )

					## t_hat is a candidate neighbour.  If it intersects
					## the identity hat, we throw it away
					if not t_hat.isdisjoint( hat ):
						continue

					## We also optionally need the union of the identity hat 
					## and t_hat to be simply connected.
					if (not allow_holes) and (not isSimplyConnected( hat | t_hat )):
						continue

					## We have a legitimate neighbour!
					ret.add( translate(hp.x-op.x, hp.y-op.y) * T )

	return ret

def getPatchTransforms( n ):
	'''Get a set of transform matrices corresponding to all possible 
	positions of a hat in an n-patch.'''
	ret = set([Transform()])
	ln = getLegalNeighbours()

	for i in range( n ):
		for T in list( ret ):
			for S in ln:
				ret.add( T * S )

	return ret

def surroundFrom( pm, halo, patch, level ):
	'''Try to place a hat that covers the cells listed in the halo, in order.
	Maybe complete a surround, maybe backtrack.'''

	## If there are no halo cells left to cover, we've got a surround.
	if len( halo ) == 0:
		yield patch
		return

	## It's possible that we've already covered the first halo cell, in
	## which case just keep surrounding
	if pm.isOccupied( halo[0] ):
		yield from surroundFrom( pm, halo[1:], patch, level )
		return 

	## If not, we try all ways to place a new tile to cover halo[0],
	## and recurse on each one.

	ts = pm.getUsers( halo[0] )
	for T in ts:
		if not pm.isOccupied( T ):
			## We can try to recurse on T, bracketed by setup and takedown
			## in the map
			pm.setOccupied( T )
			if pm.isValid():
				yield from surroundFrom(
					pm, halo[1:], patch + [(level,T)], level )
			pm.setUnoccupied( T )

def generateSurrounds( pm, patch ):
	'''Given the partially used patch map in pm, generate a sequence
	of all of the ways to surround it with hats.  Note the "generate": 
	use this function as a value to iterate on.'''

	level = patch[-1][0] + 1

	## Get the ordered halo, giving us a plan for how to try to surround
	## the existing patch.
	halo = pm.getHalo()

	## Perform a simple sanity check first: if any halo cell has no 
	## users compatible with the existing patch, then the patch isn't
	## surroundable.

	for p in halo:
		found_compat = False
		for T in pm.getUsers( p ):
			if not pm.isOccupied( T ):
				found_compat = True
				break
		## Nope, didn't find a usable tile in that position
		if not found_compat:
			return

	## Initiate the recursion!
	yield from surroundFrom( pm, halo, patch, level )

def outputPatch( ts ):
	print( len( ts ) )
	for k, T in ts:
		print( '{0} ; {1}'.format( k, T ) )

if __name__ == '__main__':
	count = 0
	saved = 0

	## For our purposes, we'll never try to generate more than a 3-patch,
	## so it suffices to build a PatchMap based on 3-patches.
	pm = PatchMap( getPatchTransforms( 3 ) )

	## Always put the identity hat at the centre of the patch.
	pm.setOccupied( Transform() )

	## Generate all 1-patches
	for tl in generateSurrounds( pm, [(0,Transform())] ):
		## For each 1-patch, generate all 2-patches
		for tl2 in generateSurrounds( pm, tl ):
			count = count + 1
			if count % 100 == 0:
				sys.stderr.write( 
					'Saw {0} 2-patches, {1} surroundable\n'.format( 
						count, saved ) )

			## Need a shallow copy of the patchmap so that we can discard
			## it without reverting
			cpm = pm.copy()

			## Check for the existence of a 3-patch
			for tl3 in generateSurrounds( cpm, tl2 ):
				## We found a 2-patch that was surroundable.  But we don't
				## actually care what 3-patch was generated.  Just output
				## the 2-patch and stop.
				outputPatch( tl2 )
				saved = saved + 1
				## Break here -- we're not trying to compute all 3-patches,
				## one is enough.
				break

	sys.stderr.write( 
		'Total: {0} 2-patches, {1} surroundable\n'.format( count, saved ) )
