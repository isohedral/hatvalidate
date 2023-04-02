import sys

from geom import Point, Transform

def readPatches( fin ):
	'''Read an input file and extract all the patches.  Return a list of
	dictionaries, where each dictionary maps transforms in the patch to
	level (0 = kernel, 1 = first corona, 2 = second corona, etc.)'''

	ret = []
	while True:
		l = fin.readline()
		if len(l) == 0:
			return ret
		n = int( l )
		patch = {}

		for i in range( n ):
			l = fin.readline()
			k = int(l[0])
			xs = (int(x) for x in l[5:-2].split(','))
			patch[ Transform( *xs ) ] = k
		
		ret.append( patch )

def getLabel( T, patch ):
	'''Get the label for the tile at transform T in the given patch.'''

	if T * Transform(1,1,2,0,-1,2) in patch:
		return 'H1'

	if ((T * Transform(0,-1,4,-1,0,-2) in patch) and
		(T * Transform(0,-1,8,1,1,-4) in patch)):
		return 'H2'

	if T * Transform(0,-1,-2,-1,0,4) in patch:
		return 'H3'

	if T * Transform(1,1,-4,0,-1,2) in patch:
		return 'H4'

	if ((T * Transform(0,-1,2,1,1,2) in patch) and
		(T * Transform(1,1,6,-1,0,0) in patch)):
		return 'T1'

	if ((T * Transform(-1,0,2,0,-1,-4) in patch) and
		(T * Transform(1,1,4,-1,0,-2) in patch)):
		return 'P2'

	if ((T * Transform(-1,-1,8,1,0,-4) in patch) and
		(T * Transform(0,1,4,-1,-1,4) in patch)):
		return 'F2'

	return 'FP1'

def getPatchLabels( patch ):
	'''Using the classification rules in Section 4 of the paper, build
	a dictionary giving labels to all the transformation matrices in the
	0- and 1-coronas of a 2-patch'''

	ret = {}
	for T in patch.keys():
		if patch[T] < 2:
			ret[T] = getLabel( T, patch )

	return ret

def withinClusterChecks( patch, labels ):
	'''Apply the within-cluster matching checks in Section 4.2 of the
	paper.'''

	## Get the label for the central tile in the patch
	cen = labels[Transform()]

	if cen == 'H1':
		## Central tile is H1; need to check that neighbours H2, H3, and H4
		## are there.
		if labels[ Transform(0,-1,-2,-1,0,4) ] != 'H2':
			print( 'H1 without an adjacent H2!' )
			return False
		if labels[ Transform(0,-1,4,-1,0,-2) ] != 'H3':
			print( 'H1 without an adjacent H3!' )
			return False
		if labels[ Transform(1,1,2,0,-1,2) ] != 'H4':
			print( 'H1 without an adjacent H4!' )
			return False
	elif cen == 'H2':
		if labels[ Transform(0,-1,4,-1,0,-2) ] != 'H1':
			print( 'H3 without an adjacent H1!' )
			return False
	elif cen == 'H3':
		if labels[ Transform(0,-1,-2,-1,0,4) ] != 'H1':
			print( 'H3 without an adjacent H1!' )
			return False
	elif cen == 'H4':
		if labels[ Transform(1,1,-4,0,-1,2) ] != 'H1':
			print( 'H4 without an adjacent H1!' )
			return False
	elif cen == 'FP1':
		if labels[ Transform(0,-1,2,1,1,2) ] not in ('P2', 'F2'):
			print( 'FP1 without an adjacent P2 or F2!' )
			return False
	elif cen in ('P2', 'F2'):
		if labels[ Transform(1,1,-4,-1,0,2) ] != 'FP1':
			print( 'P2 or F2 without an adjacent FP1!' )
			return False

	return True

def betweenClusterChecks( patch, labels ):
	'''Apply the between-cluster matching checks in Section 4.3 of
	the paper.'''

	## Get the label for the central tile in the patch
	cen = labels[Transform()]

	## H edge A+
	if cen == 'H2':
		if Transform(0,-1,-2,1,1,-2) in patch:
			if labels[Transform(0,-1,-2,1,1,-2)] not in ('T1', 'P2'):
				print( 'H2 A+ neighbour (alt. 1) without valid label!' )
				return False
		elif Transform(1,1,-4,-1,0,2) in patch:
			if labels[Transform(1,1,-4,-1,0,2)] != 'T1':
				print( 'H2 A+ neighbour (alt. 2) without valid label!' )
				return False
		else:
			print( 'H2 didn\'t have a valid A+ neighbour!' )
			return False

	## H upper edge B-
	if cen == 'H1':
		if labels[Transform(-1,-1,2,0,1,-4)] not in ('T1', 'FP1'):
			print( 'H1 didn\'t have valid upper edge B- neighbour!' )
			return False

	## H lower edge B-
	if cen == 'H3':
		if labels[Transform(1,1,-2,-1,0,-2)] not in ('T1', 'FP1'):
			print( 'H3 didn\'t have valid lower edge B- neighbour!' )
			return False
		
	## T upper edge A-
	if cen == 'T1':
		if labels[Transform(0,-1,2,1,1,2)] != 'H2':
			print( 'T1 didn\'t have valid upper edge A- neighbour!' )
			return False

	## T or P lower edge A- 
	if cen in ('T1', 'P2'):
		if labels[Transform(1,1,4,-1,0,-2)] != 'H2':
			print( 'T or P didn\'t have valid lower edge A- neighbour!' )
			return False

	## T, P or F edge B+
	if cen in ('T1', 'FP1'):
		if labels[Transform(1,1,-4,-1,0,2)] not in ('H3', 'H4'):
			print( 'T, P or F didn\'t have valid edge B+ neighbour!' )
			return False

	## F edge F+
	if cen == 'F2':
		if labels[Transform(-1,-1,8,1,0,-4)] != 'F2':
			print( 'F didn\'t have valid edge F+ neighbour!' )
			return False
			
	## F edge F-
	if cen == 'F2':
		if labels[Transform(0,1,4,-1,-1,4)] != 'F2':
			print( 'F didn\'t have valid edge F- neighbour!' )
			return False

	## X+ edge at top of polykite
	if cen in ('H2', 'P2', 'F2'):
		if Transform(0,1,0,-1,-1,6) in patch:
			if labels[Transform(0,1,0,-1,-1,6)] not in ('H2', 'P2'):
				print( 'X+ top edge (alt. 1) didn\'t have valid neighbour!' )
				return False
		elif Transform(1,0,-2,0,1,4) in patch:
			if labels[Transform(1,0,-2,0,1,4)] not in ('H3', 'H4', 'FP1', 'F2'):
				print( 'X+ top edge (alt. 2) didn\'t have valid neighbour!' )
				return False
		else:
			print( 'X+ top edge didn\'t have valid neighbour!' )
			return False

	## X+ edge at right of polykite
	if cen in ('H3', 'H4', 'FP1'):
		if Transform(-1,-1,8,1,0,-4) in patch:
			if labels[Transform(-1,-1,8,1,0,-4)] not in ('H2', 'P2'):
				print( 'X+ right edge (alt. 1) didn\'t have valid neighbour!' )
				return False
		elif Transform(0,1,6,-1,-1,0) in patch:
			if labels[Transform(0,1,6,-1,-1,0)] not in ('H3', 'H4', 'FP1', 'F2'):
				print( 'X+ right edge (alt. 2) didn\'t have valid neighbour!' )
				return False
		else:
			print( 'X+ right edge didn\'t have valid neighbour!' )
			return False

	## X- edge at right of polykite
	if cen in ('H2', 'P2'):
		if Transform(-1,-1,6,1,0,0) in patch:
			if labels[Transform(-1,-1,6,1,0,0)] not in ('H2', 'F2', 'P2'):
				print( 'X- right edge (alt. 1) didn\'t have valid neighbour!' )
				return False
		elif Transform(0,1,4,-1,-1,4) in patch:
			if labels[Transform(0,1,4,-1,-1,4)] not in ('H3', 'H4', 'FP1'):
				print( 'X- right edge (alt. 2) didn\'t have valid neighbour!' )
				return False
		else:
			print( 'X- right edge didn\'t have valid neighbour!' )
			return False

	## X- edge at bottom of polykite
	if cen in ('H3', 'H4', 'FP1', 'F2'):
		if Transform(1,0,2,0,1,-4) in patch:
			if labels[Transform(1,0,2,0,1,-4)] not in ('H2', 'F2', 'P2'):
				print( 'X- bottom edge (alt. 1) didn\'t have valid neighbour!' )
				return False
		elif Transform(-1,-1,6,1,0,-6) in patch:
			if labels[Transform(-1,-1,6,1,0,-6)] not in ('H3', 'H4', 'FP1'):
				print( 'X- bottom edge (alt. 2) didn\'t have valid neighbour!' )
				return False
		else:
			print( 'X- bottom edge didn\'t have valid neighbour!' )
			return False
				
	## L edge at right of polykite
	if cen == 'P2':
		if Transform(-1,0,10,0,-1,-2) in patch:
			if labels[Transform(-1,0,10,0,-1,-2)] != 'P2':
				print( 'L edge at right (alt. 1) didn\'t have valid neighbour!' )
				return False
		elif Transform(1,1,6,-1,0,0) in patch:
			if labels[Transform(1,1,6,-1,0,0)] not in ('FP1', 'F2'):
				print( 'L edge at right (alt. 2) didn\'t have valid neighbour!' )
				return False
		else:
			print( 'L edge at right didn\'t have valid neighbour!' )
			return False

	## L edge at bottom of polykite
	if cen in ('FP1', 'F2'):
		if Transform(0,-1,0,1,1,-6) in patch:
			if labels[Transform(0,-1,0,1,1,-6)] not in ('P2'):
				print( 'L edge at bottom (alt. 1) didn\'t have valid neighbour!' )
				return False
		elif Transform(-1,0,2,0,-1,-4) in patch:
			if labels[Transform(-1,0,2,0,-1,-4)] not in ('FP1', 'F2'):
				print( 'L edge at bottom (alt. 2) didn\'t have valid neighbour!' )
				return False
		else:
			print( 'L edge at bottom didn\'t have valid neighbour!' )
			return False

	return True

def processPatch( patch ):
	labs = getPatchLabels( patch )
	if not withinClusterChecks( patch, labs ):
		return False
	if not betweenClusterChecks( patch, labs ):
		return False
	return True

if __name__ == '__main__':
	passed = 0

	patches = readPatches( sys.stdin )
	for patch in patches:
		if processPatch( patch ):
			passed = passed + 1

	print( '{0}/{1} patches passed checks'.format( passed, len(patches) ) )
