### Basic geometry classes: points and affine transformations with
### integer coordinates.

import math
from functools import total_ordering

@total_ordering
class Point:
	def __init__( self, x = 0, y = 0 ):
		self.x = x
		self.y = y

	def __repr__( self ):
		return '<{0} {1}>'.format( self.x, self.y )

	def __add__( self, other ):
		return Point( self.x + other.x, self.y + other.y )
	
	def __sub__( self, other ):
		return Point( self.x - other.x, self.y - other.y )

	def __mul__( self, d ):
		return Point( self.x * d, self.y * d )

	def __eq__( self, other ):
		return (self.x == other.x) and (self.y == other.y)

	def __lt__( self, other ):
		if self.y < other.y:
			return True
		else:
			return (self.y == other.y) and (self.x < other.x)

	## Allow points to be stored in sets or used as keys in dictionaries
	def __hash__( self ):
		return hash( (self.x, self.y) )

### The first two rows of a 3x3 2D affine transformation matrix, in
### row-major order (with 0 0 1 as the implicit third row).
class Transform:
	def __init__( self, a = 1, b = 0, c = 0, d = 0, e = 1, f = 0 ):
		self.m = (a,b,c,d,e,f)

	def __repr__( self ):
		return '<{0},{1},{2},{3},{4},{5}>'.format( *self.m )

	def __mul__( self, other ):
		if isinstance( other, Transform ):
			return Transform(
				self.m[0] * other.m[0] + self.m[1] * other.m[3],
				self.m[0] * other.m[1] + self.m[1] * other.m[4],
				self.m[0] * other.m[2] + self.m[1] * other.m[5] + self.m[2],
				self.m[3] * other.m[0] + self.m[4] * other.m[3],
				self.m[3] * other.m[1] + self.m[4] * other.m[4],
				self.m[3] * other.m[2] + self.m[4] * other.m[5] + self.m[5] )
		else:
			return Point( 
				self.m[0] * other.x + self.m[1] * other.y + self.m[2],
				self.m[3] * other.x + self.m[4] * other.y + self.m[5] )
	
	def invert( self ):
		det = self.m[0] * self.m[4] - self.m[1] * self.m[3]
		return Transform(
			self.m[4] // det, -self.m[1] // det, 
			(self.m[1] * self.m[5] - self.m[2] * self.m[4]) // det,
			-self.m[3] // det, self.m[0] // det, 
			(self.m[2] * self.m[3] - self.m[0] * self.m[5]) // det )

	def __eq__( self, other ):
		return self.m == other.m

	def __hash__( self ):
		return hash( self.m )
	
def translate( x, y ):
	return Transform( 1, 0, x, 0, 1, y )
