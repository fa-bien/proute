#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: October 11th 2011 by Fabien Tricoire
#
import util
import shapes

class Canvas:
    """
    Abstract class: should be derived by backend classes.
    Most methods here should be overloaded by the backend version.
    High-level methods such as drawCentredPolygon shouldn't though.
    Rule of thumb: if the method just prints an error message, it should be
    overloaded.

    """
    def __init__(self, width, height):
        self.width = width
        self.height = height

    # return the width and height of this canvas
    def getSize(self):
        return self.width, self.height

    # clear the canvas and set a white background
    def blank(self):
        print 'Error: method clear not implemented in backend'

    # draw a simple border...
    def drawBorder(self):
        print 'Error: method drawBorder not implemented in backend'
        
    # draw a rectangle centered at coordinates x, y
    # if a reference point is specified, it is used, otherwise the coordinates
    # are assumed to be those of the center of the rectangle
    # possible values for the reference point are 'center', 'northwest',
    # 'northeast', 'southeast', 'southwest'
    def drawRectangle(self, x, y, w, h, style, referencePoint='center'):
        print 'Error: method drawRectangle not implemented in backend'

    # draw a list of rectangles with the same style
    # if a reference point is specified, it is used, otherwise the coordinates
    # are assumed to be those of the center of the rectangles
    # possible values for the reference point are 'center', 'northwest',
    # 'northeast', 'southeast', 'southwest'
    # xs, ys, ws, hs are lists
    def drawRectangles(self, xs, ys, ws, hs, style, referencePoint='center'):
        print 'Error: method drawRectangles not implemented in backend'

    # draw a circle centered at coordinates x, y
    def drawCircle(self, x, y, r, style):
        print 'Error: method drawCircle not implemented in backend'

    # draw a list of circles with the same colour style
    # parameters xs, ys, rs should be lists
    def drawCircles(self, xs, ys, rs, style):
        print 'Error: method drawCircles not implemented in backend'

    # draw a line
    def drawLine(self, x1, y1, x2, y2, style):
        print 'Error: method drawLine not implemented in backend'

    # draw a line
    def drawLines(self, x1s, y1s, x2s, y2s, style):
        print 'Error: method drawLines not implemented in backend'

    # draw a polyline
    # x and y are lists
    def drawPolyline(self, x, y, style):
        print 'Error: method drawPolyline not implemented in backend'

    # draw a spline; each element in points is a 2-uple with x,y coordinates
    def drawSpline(self, points, style):
        print 'Error: method drawSpline not implemented in backend'
        
    # draw a polygon
    # xs and ys are lists of point coordinates
    def drawPolygon(self, xs, ys, style):
        print 'Error: method drawPolygon not implemented in backend'

    # draw several times a polygon with the same style
    # xss and yss are lists of lists of point coordinates
    def drawPolygons(self, xss, yss, style):
        print 'Error: method drawPolygons not implemented in backend'

    # draw a shape
    # current version is ugly, should be improved one day to something better
    # with a generic shape/path format etc
    def drawShape(self, shape, x, y, radius, style, angle=0):
        if isinstance(shape, shapes.Circle):
            self.drawCircle(x, y, radius, style)
        elif isinstance(shape, shapes.CentredPolygon):
            self.drawCentredPolygon(shape, x, y, radius, style, angle)
        else:
            print 'Error: unknown type of shape:', shape
    # same with multiple instances
    def drawShapes(self, shape, xs, ys, radius, style, angle=0):
        if isinstance(shape, shapes.Circle):
            self.drawCircles(xs, ys, [ radius for i in xs ], style)
        elif isinstance(shape, shapes.CentredPolygon):
            self.drawCentredPolygons(shape, xs, ys, radius, style, angle)
        else:
            print 'Error: unknown type of shape:', shape
        
    # draw a centred polygon
    # x and y are center coordinates
    def drawCentredPolygon(self, polygon, x, y, radius, style, angle=0):
        points = polygon.getTransformedPoints(radius, angle)
        xs = []
        ys = []
        for a, b in points:
            xs.append(a + x)
            ys.append(b + y)
        self.drawPolygon(xs, ys, style)

    # draw several times a centred polygon with the same style
    def drawCentredPolygons(self, polygon, xs, ys, radius, style, angle=0):
        points = polygon.getTransformedPoints(radius, angle)
        xss = []
        yss = []
        for x, y in zip(xs, ys):
            xs = []
            ys = []
            for a, b in points:
                xs.append(a + x)
                ys.append(b + y)
            xss.append(xs)
            yss.append(ys)
        self.drawPolygons(xss, yss, style)

    # draw a text label with top left corner at x, y
    def drawText(self, label, x, y,
                 font, foregroundColour, backgroundColour):
        print 'Error: method drawText not implemented in backend'
    
    # draw several text labels with top left corners given in x, y
    def drawTexts(self, labels, xs, ys,
                 font, foregroundColour, backgroundColour):
        print 'Error: method drawText not implemented in backend'
    
    # draw a text label at x, y
    # this version allows to specify the coordinates reference point,
    # as well as a rotation
    def drawFancyText(self, label, x, y,
                      font, foregroundColour, backgroundColour,
                      angle=None,
                      referencePoint='northwest'):
        print 'Error: method drawFancyText not implemented in backend'
    
    # draw a bitmap, using the given point as NW corner
    def drawBitmap(self, bitmap, NWcorner):
        print 'Error: method drawBitmap not implemented in backend'
