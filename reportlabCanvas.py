#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: October 11th 2011 by Fabien Tricoire
#
import random
from math import *

from reportlab.lib import colors
from reportlab.graphics.shapes import *
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas as rlcanvas

from canvas import *
import colours
import style

# convert an AbstractColour to a reportlab Color
def convertColour(abstractColour):
    if abstractColour is None:
        abstractColour = colours.transparent
    return colors.Color(abstractColour.red / 255.0,
                        abstractColour.green / 255.0,
                        abstractColour.blue / 255.0,
                        alpha = abstractColour.alpha / 255.0)

# adapt the abstract style thickness to reportlab
def getThickness(style):
    if style.lineThickness is None:
        return 1
    else:
        return style.lineThickness

# compute the line going through point x1, y1 that is parallel to the line
# going through points x2,y2 and x3,y3
def parallelThroughPoint(x1, y1, x2, y2, x3, y3):
    a = (y2-y3) / ( x2-x3 if x2 != x3 else .00001)
    b = y1 - (a * x1)
#     print 'line going through', ((x1,y1)), 'parallel to', ((x2,y2)), '--', ((x3,y3)), ': y =', a, '* x +', b
    return lambda(x): a * x + b
    
# reportlab canvas!
class ReportlabCanvas(Canvas):
    def __init__(self, width, height, fName='default.pdf'):
        self.width = width
        self.height = height
        # derive dash array from stoke style
        self.lineStyleArray = { 'solid':[self.width,0], 'dashed':[7,10] }
        self.fName = fName
    
    # return the width and height of this canvas
    def getSize(self):
        return self.width, self.height

    # clear the canvas and set a white background
    def blank(self):
        self.canvas = rlcanvas.Canvas(self.fName)
        self.canvas.setPageSize((self.width, self.height))
        creatorString = 'proute - http://proute.berlios.de'
        self.canvas.setCreator(creatorString)

    def restrictDrawing(self, xmin, ymin, xmax, ymax):
        self.canvas.saveState()
        sub = self.canvas.beginPath()
        sub.rect(xmin, ymin, xmax-xmin, ymax-ymin)
        self.canvas.clipPath(sub, stroke=0)

    def unrestrictDrawing(self):
        self.canvas.restoreState()
        
    # set a drawing style
    # for internal use only
    def setDrawingStyle(self, style):
        if style.lineStyle is None or style.lineStyle == 'solid':
            self.canvas.setDash(self.lineStyleArray['solid'])
        elif style.lineStyle == 'dashed':
            self.canvas.setDash(self.lineStyleArray['dashed'])
        if not style.lineColour is None:
            self.canvas.setStrokeColor(convertColour(style.lineColour))
        if not style.fillColour is None:
            self.canvas.setFillColor(convertColour(style.fillColour))
        else:
            self.canvas.setFillColor(convertColour(colours.transparent))
        self.canvas.setLineWidth(getThickness(style))
           
    # set a writing style
    # also for internal use only
    def setWritingStyle(self, font, foregroundColour, backgroundColour):
        self.canvas.setFontSize(font.size)
        self.canvas.setStrokeColor(convertColour(foregroundColour))
        self.canvas.setFillColor(convertColour(foregroundColour))
           
    # draw a rectangle centred at coordinates x, y
    def drawRectangle(self, x, y, w, h, style, referencePoint='centre'):
        if referencePoint == 'centre' or referencePoint == 'center':
            x, y = x - w/2.0, y - h/2.0
        elif referencePoint == 'northwest':
            x, y = x, y-h
        elif referencePoint == 'northeast':
            x, y = x-w, y-h
        elif referencePoint == 'southeast':
            x, y = x-w, y
        elif referencePoint == 'southwest':
            x, y = x, y
        self.setDrawingStyle(style)
        fill = not style.fillColour is None
        self.canvas.rect(x, y, w, h, fill=fill,
#                          strokeDashArray=[0,100] if thickness <= 0 else [],
                         )

    # draw a list of rectangles with the same style
    # xs, ys, ws, hs are lists
    def drawRectangles(self, xs, ys, ws, hs, style, referencePoint='centre'):
        for x, y, w, h in zip(xs, ys, ws, hs):
            self.drawRectangle(x, y, w, h, style, referencePoint)
                
    # draw a circle centreed at coordinates x, y
    def drawCircle(self, x, y, r, style):
        self.setDrawingStyle(style)
        fill = not style.fillColour is None
        self.canvas.circle(x, y, r, fill=fill,
#                            strokeDashArray=[0,100] if thickness <= 0 else [],
                           )

    # draw a list of circles with the same colour style
    # parameters xs, ys, rs should be lists
    def drawCircles(self, xs, ys, rs, style):
        for x, y, r in zip(xs, ys, rs):
            self.drawCircle(x, y, r, style)

    # draw a line
    def drawLine(self, x1, y1, x2, y2, style):
        self.setDrawingStyle(style)
        self.canvas.line(x1, y1, x2, y2)
        # smooth line joints
        thickness = getThickness(style)
        style.lineThickness = 0.0
        oldFillcolour = style.fillColour
        style.fillColour = style.lineColour
        self.drawCircle(x1, y1, (thickness) /2.0, style)
        self.drawCircle(x2, y2, (thickness) /2.0, style)
        style.lineThickness = thickness
        style.fillColour = oldFillcolour

    # draw lines with the same style
    def drawLines(self, x1s, y1s, x2s, y2s, style):
        self.setDrawingStyle(style)
        for x1, y1, x2, y2 in zip(x1s, y1s, x2s, y2s):
            self.canvas.line(x1, y1, x2, y2)
            # smooth line joints
            thickness = getThickness(style)
            style.lineThickness = 0.0
            oldFillcolour = style.fillColour
            style.fillColour = style.lineColour
            self.drawCircle(x1, y1, (thickness) /2.0, style)
            self.drawCircle(x2, y2, (thickness) /2.0, style)
            style.lineThickness = thickness
            style.fillColour = oldFillcolour

    # draw a polyline
    # x and y are lists
    def drawPolyline(self, x, y, style):
        self.setDrawingStyle(style)
        list = reduce(lambda x,y: x+y, [ [x[i], y[i]] for i in range(len(x)) ] )
        fillCol = convertColour(style.fillColour)
        strokeCol = convertColour(style.lineColour)
        thickness = getThickness(style)
        p = PolyLine(list,
                     strokeColor=strokeCol,
                     fillColor=fillCol,
                     strokeWidth=thickness,
                     strokeLineJoin=1)
        d = Drawing(self.width, self.height)
        d.add(p)
        renderPDF.draw(d, self.canvas, 0, 0)
        
    # draw a spline; each element in points is a 2-uple with x,y coordinates
    def drawSpline(self, points, style):
        # required to close the path on each side
        points = [ points[0] ] + points + [ points[-1] ]
        self.setDrawingStyle(style)
        for i in range(1, len(points)-1):
            self.canvas.bezier((points[i][0] + points[i-1][0]) / 2.0,
                               (points[i][1] + points[i-1][1]) / 2.0,
                               points[i][0],
                               points[i][1],
                               (points[i][0] + points[i+1][0]) / 2.0,
                               (points[i][1] + points[i+1][1]) / 2.0,
                               (points[i][0] + points[i+1][0]) / 2.0,
                               (points[i][1] + points[i+1][1]) / 2.0)
            
    # draw a polygon
    # x and y are lists of point coordinates
    def drawPolygon(self, x, y, style):
        self.setDrawingStyle(style)
        list = reduce(lambda x,y: x+y, [ [x[i], y[i]] for i in range(len(x)) ] )
        fillCol = convertColour(style.fillColour)
        thickness = getThickness(style)
        strokeCol = convertColour(style.lineColour) \
            #if thickness > 0 else fillCol
        p = Polygon(list,
                    strokeColor=strokeCol,
                    fillColor=fillCol,
                    strokeWidth=thickness,
                    strokeLineJoin=1,
#                     strokeDashArray=[0,100] if thickness <= 0 else [],
                    )
        d = Drawing(self.width, self.height)
        d.add(p)
        renderPDF.draw(d, self.canvas, 0, 0)

    # draw several polygons with the same style
    # xs and ys are lists of lists of point coordinates
    def drawPolygons(self, xs, ys, style):
        self.setDrawingStyle(style)
        d = Drawing(self.width, self.height)
        for x, y in zip(xs, ys):
            list = reduce(lambda x,y: x+y,
                          [ [x[i], y[i]] for i in range(len(x)) ] )
            fillCol = convertColour(style.fillColour)
            thickness = getThickness(style)
            strokeCol = convertColour(style.lineColour) \
                #if thickness > 0 else fillCol
            p = Polygon(list,
                        strokeColor=strokeCol,
                        fillColor=fillCol,
                        strokeWidth=thickness,
                        strokeLineJoin=1,
#                         strokeDashArray=[0,100] if thickness <= 0 else [],
                        )
            d.add(p)
            renderPDF.draw(d, self.canvas, 0, 0)

    # draw a text label with top left corner at x, y
    def drawText(self, label, x, y,
                 font, foregroundColour, backgroundColour):
        self.setWritingStyle(font, foregroundColour, backgroundColour)
        finalText = self.canvas.beginText()
        finalText.setStrokeColor = convertColour(foregroundColour)
        finalText.setTextOrigin(x, y - font.size)
        finalText.textOut(label)
        self.canvas.drawText(finalText)

    # draw several text labels with top left corners given in xs, ys
    def drawTexts(self, labels, xs, ys,
                 font, foregroundColour, backgroundColour):
        self.setWritingStyle(font, foregroundColour, backgroundColour)
        for label, x, y in zip(labels, xs, ys):
            finalText = self.canvas.beginText()
            finalText.setStrokeColor = convertColour(foregroundColour)
            finalText.setTextOrigin(x, y - font.size)
            finalText.textOut(label)
            self.canvas.drawText(finalText)

    # draw a text label at x, y
    # this version allows to specify a reference point and an angle
    def drawFancyText(self, label, x, y,
                      font, foregroundColour, backgroundColour,
                      angle=0,
                      referencePoint='northwest'):
#         styl = style.DrawingStyle(colours.funkypink,
#                                   colours.funkypink)
#         self.drawCircle(x, y, 3, styl)
        self.setWritingStyle(font, foregroundColour, backgroundColour)
        # first we write the text without printing it so that we can measure it
        previewText = self.canvas.beginText()
        previewText.setTextOrigin(x, y)
        previewText.textOut(label)
        width = previewText.getX() - x
        height = font.size
        # useful for rotating the text
        co = cos ( angle * pi / 180.0 )
        si = sin ( angle * pi / 180.0 )
#         print angle, angle * pi / 180.0, co, si
        # set starting coordinates depending on text size
        if referencePoint == 'southwest':
            xoffset = 0
            yoffset = 0
        elif referencePoint == 'northwest':
            xoffset = si * height
            yoffset = -co * height
        elif referencePoint == 'southeast':
            xoffset = -co * width
            yoffset = -si * width
        elif referencePoint == 'northeast':
            xoffset = -co * width + si * height
            yoffset = -si * width - co * height
        elif referencePoint == 'centre' or referencePoint == 'center':
            xoffset = (-co * width + si * height) / 2.0
            yoffset = (-si * width - co * height) / 2.0
        # finally we can write and print our transformed text
        finalText = self.canvas.beginText()
        finalText.setStrokeColor = convertColour(foregroundColour)
        finalText.setTextOrigin(x, y)
        finalText.setTextTransform(co, si, -si, co, x+xoffset, y+yoffset)
        finalText.textOut(label)
        self.canvas.drawText(finalText)

#     # draw a text label with top left corner at x, y
#     def drawText(self, label, x, y,
#                  font, foregroundColour, backgroundColour,
#                  angle=None):
#         if angle is None:
#             angle = 0
#         l = self.canvas.beginText()
#         self.setWritingStyle(font, foregroundColour, backgroundColour)
#         l.setStrokeColor = convertColour(foregroundColour)
#         l.setTextOrigin(x, y)
# #         l.boxAnchor = 'nw'
#         if not angle is None:
#             co = cos ( -angle * pi / 180.0 )
#             si = sin ( -angle * pi / 180.0 )
#             s = self.canvas._fontsize
#             xoffset = -si * s
#             yoffset = -co * s
#             l.setTextTransform(co, -si, si, co, x+xoffset, y+yoffset)
#         l.textOut(label)
#         self.canvas.drawText(l)
#         print dir(self.canvas)

    # draw a bitmap using the given north-west corner
    def drawBitmap(self, bitmap, NWcorner):
        x, y = NWcorner
        w, h = bitmap.size
        # import reportlab
        # img = reportlab.pdfgen.canvas.ImageReader(bitmap)
        # ugly workaround since the previous commented method doesn't work with
        # all versions of reportlab
        import StringIO
        dummy = StringIO.StringIO()
        bitmap.save(dummy, format='png')
        dummy.seek(0)
        import reportlab
        img = reportlab.pdfgen.canvas.ImageReader(dummy)
        self.canvas.drawImage(img, x, y-h, w, h)
        
