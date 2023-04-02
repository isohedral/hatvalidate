### A data structure that keeps track of a set of transformations which
### might be used as part of an n-patch, and a set of cells that make up 
### a current patch.  We also track, for all possible patch cells, which
### transformed tiles could potentially occupy those cells.  Used as part
### of recursively surrounding (n-1)-patches to construct n-patches.

from geom import *
from hat import *
from kitegrid import *

class PatchMap:
	def __init__( self, ts ):
		self.shapes = {}
		self.users = {}
		self.occupied = set()

		for T in ts:
			ps = set([T * p for p in hat])
			self.shapes[T] = ps

			for P in ps:
				self.users.setdefault( P, [] ).append( T )

	def copy( self ):
		## Based on the recursive computation in surround.py, we need 
		## a deep copy of the occupancy map, but we can keep the other
		## information as-is (it won't be modified)
		ret = PatchMap( [] )
		ret.shapes = self.shapes
		ret.users = self.users
		ret.occupied = self.occupied.copy()
		return ret

	def isOccupied( self, tp ):
		'''Check if an individual cell, or if any of a list of cells, is
		currently occupied.'''

		if isinstance( tp, Point ):
			return tp in self.occupied
		else:
			ps = self.shapes[tp]
			for P in ps:
				if P in self.occupied:
					return True
			return False

	def setOccupied( self, tp ):
		if isinstance( tp, Point ):
			self.occupied.add( tp )
		else:
			ps = self.shapes[tp]
			for P in ps:
				self.occupied.add( P )

	def setUnoccupied( self, tp ):
		if isinstance( tp, Point ):
			self.occupied.remove( tp )
		else:
			ps = self.shapes[tp]
			for P in ps:
				self.occupied.remove( P )

	def isValid( self ):
		'''Verify that a patch is legitimate.'''

		## Must be simply connected.  That's basically it.
		return isSimplyConnected( self.occupied )

	def getCells( self, T ):
		return self.shapes[T]

	def getUsers( self, P ):
		return self.users[P]

	def getHalo( self ):
		return getOrderedHalo( self.occupied )
