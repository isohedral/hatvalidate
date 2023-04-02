import sys
import math

from geom import Point, Transform
from surround import getLegalNeighbours
from hat import hat_outline

sc = 10
v1 = (sc,0)
v2 = (0.5*sc,0.5*sc*math.sqrt(3))

def getHatOutline( T ):
	ret = []
	for p in hat_outline:
		tp = T * p
		x = tp.x*v1[0] + tp.y*v2[0]
		y = tp.x*v1[1] + tp.y*v2[1]
		ret.append( (x, y) )
	return ret

def drawPolygon( fout, pgon, tx, ty, r, g, b ):
	cmd = 'moveto'
	for p in pgon:
		x = tx + p[0]
		y = ty + p[1]
		fout.write( '{0} {1} {2}\n'.format( x, y, cmd ) )
		cmd = 'lineto'

	fout.write( 'closepath gsave {0} {1} {2} setrgbcolor fill grestore stroke newpath\n'.format( r, g, b ) )

def samplePage( x, y ):
	return (72 + x*(6.5*72/3.0), 10*72 - y*(9*72/4.0))

if __name__ == '__main__':
	ts = getLegalNeighbours( True )

	fout = sys.stdout

	fout.write( '''%!PS-Adobe-3.0

1 setlinewidth 0 setgray
/Helvetica findfont
12 scalefont
setfont
/cshow { dup stringwidth pop -0.5 mul 0 rmoveto show } def
''' )

	id_hat = getHatOutline( Transform() )
	
	x = 0
	y = 0

	for T in ts:
		t_hat = getHatOutline( T )
		xmin = min( p[0] for p in id_hat + t_hat )
		xmax = max( p[0] for p in id_hat + t_hat )
		ymin = min( p[1] for p in id_hat + t_hat )
		ymax = max( p[1] for p in id_hat + t_hat )

		tx, ty = samplePage( x+0.5, y+0.5 )
		tx = tx - 0.5*(xmin+xmax)
		ty = ty - 0.5*(ymin+ymax)

		drawPolygon( fout, id_hat, tx, ty, 0.5, 0.8, 0.5 )
		drawPolygon( fout, t_hat, tx, ty, 0.75, 0.75, 0.75 )

		tx, ty = samplePage( x+0.5, y+0.3 )
		fout.write( '{0} {1} moveto ({2}) cshow\n'.format(
			tx, ty - 100, T ) )

		x = x + 1
		if x == 3:
			x = 0
			y = y + 1
			if y == 4:
				y = 0
				fout.write( 'showpage\n' )

	fout.write( 'showpage\n%%EOF\n' )
