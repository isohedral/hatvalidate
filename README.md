### hatvalidate

This repository contains Python code to accompany the article "An aperiodic monotile".  The goal of this code is to validate the case-based computations in Section 4 of the paper, which establish that hat polykites are forced to cluster correctly into the metatiles that are used as one of the proofs of aperiodicity.  Here are some quick instructions.

1. It's helpful to have a chart showing all possible neighbours of a
   central hat, together with the affine transformation matrices
   associated with those neighbours (assuming the central hat uses
   the identity matrix).  The `viz_neighbours` script generates such
   a chart:

    ```
    $ python viz_neighbours.py > neighbours.ps
    $ pstopdf neighbours.ps
    ```
    
   The provided file `neighbours.pdf` is the result of executing the
   commands above.  There are 54 potential neighbours.  Many of these
   cannot actually occur in a tiling by hats (or even in a 1-patch
   around a central hat), but it doesn't hurt to have all of them.
   Appendix B of the paper includes diagrams that show how to eliminate
   many of the 54 potential neighbours.

2. The starting point for the case-based analysis is to generate all
   "surroundable 2-patches".  These are the subset of the 2380 possible
   2-patches that can themslves be surrounded to yield a 3-patch.  There
   are 188 such patches.  They can be generated using the "surround" script:

    ```
    $ python surround.py > 2patches.txt
    ```

   The computation proceeds by brute force, and deliberately avoids
   optimization for the sake of clarity.  It completes in about 32
   minutes on a 2019 laptop (2.4 GHz 8-Core Intel Core i9).  The
   provided file `2patches.txt` is the result of executing the
   command above.  The file is a sequence of 2-patches.  Each one
   first gives the number N of tiles in the patch on its own line,
   then N lines, each containing a corona number and a transformation
   matrix for a tile in the patch (the top two rows of a 2D affine
   transformation; see geom.py for details).

3. The actual case-based analysis is performed by `matching.py`:

    ```
    $ python matching.py < 2patches.txt
    ```

   This script will read in patches, and for each one verify that it
   satisfies all the conditions of Section 4.  It assigns labels to
   all tiles in the 0- and 1-coronas using the rules of Figure 4.2, and
   then verifies the within-cluster (Figure 4.3) and between-cluster
   (Figure 4.4) matching conditions.  If everything checks out (which
   it does!), the result is a bit of an anticlimax: the program will
   simply print "188/188 patches passed checks" and stop.  Of course,
   That's a cause for celebration!



For more information, including a link to the paper, see [my web page](https://cs.uwaterloo.ca/~csk/hat/) about this project.
