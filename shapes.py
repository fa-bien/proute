#
# File created August 7th 2011 by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: September 20th 2011 by Fabien Tricoire
#
from math import *

class Circle:
    pass

class CentredPolygon:
    '''
    This class represents a polygon, centred on the point at coordinates
    (0, 0). Centred means that rotation or scaling will be performed with
    (0, 0) as reference point.
    The point in the polygon which is the farthest away from the centre is
    exactly at distance 1 from this centre.
    If the points provided in the constructor do not verify this, the whole
    polygon is scaled to enforce the rule.
    '''
    # points is a list of 2-tuples
    def __init__(self, points):
        self.points = points
        # compute the squared distance from the centre for each point
        maxSD = 0.0
        for x, y in points:
            squareDistance = x * x + y * y
            if squareDistance > maxSD:
                maxSD = squareDistance
        # now we can compute the distance from the farthest point
        dist = sqrt(maxSD)
        factor = 1.0 / dist if dist > 0 else 1.0
        if factor != 1:
            self.points = [ (x * factor, y * factor)
                            for x, y in points ]

    def __repr__(self):
        return 'CentredPolygon(' + str(self.points) + ')'
        
    # provide a list of points corresponding to this polygon transformed using
    # given angle and radius
    def getTransformedPoints(self, radius, angle=0):
        # needed for rotating
        co = cos ( angle * pi / 180.0 )
        si = sin ( angle * pi / 180.0 )
        # now we can generate our points
        xs = []
        ys = []
        points = [ ( (x * co - y * si) * radius, (x * si + y * co) * radius )
                   for x, y in self.points ]
        return points
        
# generate a regular polygon
def makeRegularPolygon(nEdges):
    # convention: starting point is at (0, 1)
    points = [ ( - sin( angle * pi / 180.0), cos ( angle * pi / 180.0 ) )
               for angle in
               [ i * 360.0 / nEdges for i in range(nEdges) ] ]
    return CentredPolygon(points)

# generate a star!
def makeStar(nEdges, factor=2.5):
    # for the inner points we take a regular polygon starting with a
    # horizontal edge
    startingAngle = 180.0 / nEdges
    innerPoints = [ ( - sin( (startingAngle + angle) * pi / 180.0),
                        cos( (startingAngle + angle) * pi / 180.0 ) )
                    for angle in
                    [ i * (360.0 / nEdges) for i in range(nEdges) ] ]
    # for the outer points: regular polygon but larger
    outerPoints = [ ( -factor * sin( angle * pi / 180.0),
                       factor * cos ( angle * pi / 180.0 ) )
                    for angle in
                    [ i * (360.0 / nEdges) for i in range(nEdges) ] ]
    points = []
    for i, o in zip(innerPoints, outerPoints):
        points.append(o)
        points.append(i)
    return CentredPolygon(points)

# more intuitive this way
square = CentredPolygon( [ (1, 1), (1, -1), (-1, -1), (-1, 1) ] )
# standard polygons...
triangle = isoTriangle = makeRegularPolygon(3)
diamond = makeRegularPolygon(4)
pentagon = makeRegularPolygon(5)
hexagon = makeRegularPolygon(6)
heptagon = makeRegularPolygon(7)
octagon = makeRegularPolygon(8)
enneagon = nonagon = makeRegularPolygon(9)
decagon = makeRegularPolygon(10)
hendecagon = makeRegularPolygon(11)
dodecagon = makeRegularPolygon(12)
tridecagon = makeRegularPolygon(13)
tetradecagon = makeRegularPolygon(14)
pentadecagon = makeRegularPolygon(15)
icosagon = makeRegularPolygon(20)

# OMG Satan!!1
pentagram = CentredPolygon( [ pentagon.points[0],
                              pentagon.points[2],
                              pentagon.points[4],
                              pentagon.points[1],
                              pentagon.points[3] ] )
