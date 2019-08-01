#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: October 11th 2011 by Fabien Tricoire
#
import sys
from math import *

import wx
import wx.lib
import wx.lib.colourdb

import canvas
import style
import colours

# convert a Colour to a wx.Colour
def convertColour(abstractColour):
    return wx.Colour(abstractColour.red,
                     abstractColour.green,
                     abstractColour.blue,
                     abstractColour.alpha)

# convert a Font to a wx.Font
def convertFont(abstractFont):
    # at the moment font family is simply ignored...
    family = wx.FONTFAMILY_DEFAULT
    # font weight
    if abstractFont.style == 'bold':
        weight = wx.FONTWEIGHT_BOLD
    elif abstractFont.style == 'light':
        weight = wx.FONTWEIGHT_LIGHT
    # default style: normal
    else:
        weight = wx.FONTWEIGHT_NORMAL
    # wx font style (necessary for wx)
    style = wx.FONTSTYLE_NORMAL
    return wx.Font(abstractFont.size,
                   family,
                   style,
                   weight)
    
class WxCanvas(canvas.Canvas):
    def __init__(self, dc, width, height):
        self.dc = dc
        self.width = width
        self.height = height
        self.defaultLineThickness = 1

    # clear and set a white background
    def blank(self):
        self.dc.SetBackground(wx.Brush('white'))
        self.dc.Clear()

    def restrictDrawing(self, xmin, ymin, xmax, ymax):
        self.dc.SetClippingRegion(xmin, self.height-ymax, xmax-xmin, ymax-ymin)

    def unrestrictDrawing(self):
        self.dc.DestroyClippingRegion()
        
    # draw a simple border...
    def drawBorder(self):
        tmpStyle = style.DrawingStyle(lineColour=style.Colour(150, 150, 150),
                                      fillColour=None,
                                      lineThickness=2,
                                      lineStyle='solid')
        self.setDrawingStyle(tmpStyle)
        self.dc.DrawRectangle(0, 0, self.width, self.height)
        
        
    # set a drawing style
    # for internal use only
    def setDrawingStyle(self, style):
        pen = self.dc.GetPen()
        if style.lineStyle is None or style.lineStyle == 'solid':
            pen.SetStyle(wx.SOLID)
        elif style.lineStyle == 'dashed' and sys.platform != 'linux2':
            pen.SetStyle(wx.SHORT_DASH)
        if not style.lineColour is None:
            pen.SetColour(convertColour(style.lineColour))
        if not style.fillColour is None:
            self.dc.SetBrush(wx.Brush(convertColour(style.fillColour)))
        else:
            self.dc.SetBrush(wx.Brush(convertColour(colours.white),
                                      style=wx.TRANSPARENT))
        if not style.lineThickness is None:
            pen.SetWidth(style.lineThickness)
        else:
            pen.SetWidth(self.defaultLineThickness)
        self.dc.SetPen(pen)
        
    # set a writing style
    # also for internal use only
    def setWritingStyle(self, font, foregroundColour, backgroundColour):
        self.dc.SetTextForeground(convertColour(foregroundColour))
        self.dc.SetTextBackground(convertColour(backgroundColour))
        self.dc.SetFont(convertFont(font))
           
    # draw a rectangle centered at coordinates x, y
    # if a reference point is specified, it is used, otherwise the coordinates
    # are assumed to be those of the center of the rectangle
    # possible values for the reference point are 'center', 'northwest',
    # 'northeast', 'southeast', 'southwest'
    def drawRectangle(self, x, y, w, h, style, referencePoint='centre'):
        self.setDrawingStyle(style)
        # wxWidgets work with pixels, not points, so we must count the line and
        # the column where the rectangle is centered, hence the w-1 and h-1 in
        # some case
        if referencePoint == 'center' or referencePoint == 'centre':
            x, y = x - (w-1)/2.0, self.height-y-(h-1)/2.0
        elif referencePoint == 'northwest':
            x, y, w, h = x, self.height-y, w, h
        elif referencePoint == 'northeast':
            x, y, w, h = x, self.height-y, -w, h
        elif referencePoint == 'southeast':
            x, y, w, h = x, self.height-y, -w, -h
        elif referencePoint == 'southwest':
            x, y, w, h = x, self.height-y, w, -h
        self.dc.DrawRectangle(x, y, w, h)

    # draw a list of rectangles with the same style
    # if a reference point is specified, it is used, otherwise the coordinates
    # are assumed to be those of the center of the rectangle
    # possible values for the reference point are 'center', 'northwest',
    # 'northeast', 'southeast', 'southwest'
    # xs, ys, ws, hs are lists
    def drawRectangles(self, xs, ys, ws, hs, style, referencePoint='center'):
        self.setDrawingStyle(style)
        # wxWidgets work with pixels, not points, so we must count the line and
        # the column where the rectangle is centered, hence the w-1 and h-1
        for x, y, w, h in zip(xs, ys, ws, hs):
            if referencePoint == 'center':
                x, y = x - (w-1)/2.0, self.height-y-(h-1)/2.0
            elif referencePoint == 'northwest':
                x, y, w, h = x, self.height-y, w, h
            elif referencePoint == 'northeast':
                x, y, w, h = x-w+1, self.height-y, w, h
            elif referencePoint == 'southeast':
                x, y, w, h = x-w+1, self.height-y-h+1, w, h
            elif referencePoint == 'southwest':
                x, y, w, h = x, self.height-y-h+1, w, h
            self.dc.DrawRectangle(x, y, w, h)

    # draw a circle centered at coordinates x, y
    def drawCircle(self, x, y, r, style):
        self.setDrawingStyle(style)
        self.dc.DrawCircle(x, self.height-y, r)

    # draw a list of circles with the same colour style
    # parameters xs, ys, rs should be lists
    def drawCircles(self, xs, ys, rs, style):
        self.setDrawingStyle(style)
        for x, y, r in zip(xs, ys, rs):
            self.dc.DrawCircle(x, self.height-y, r)

    # draw a line
    def drawLine(self, x1, y1, x2, y2, style):
        self.setDrawingStyle(style)
        self.dc.DrawLine(x1, self.height-y1, x2, self.height-y2)

    # draw a line
    def drawLines(self, x1s, y1s, x2s, y2s, style):
        self.setDrawingStyle(style)
        for x1, y1, x2, y2 in zip(x1s, y1s, x2s, y2s):
            self.dc.DrawLine(x1, self.height-y1, x2, self.height-y2)

    # draw a polyline
    # x and y are lists
    def drawPolyline(self, x, y, style):
        self.setDrawingStyle(style)
        points = [ (i, self.height-j) for i, j in zip(x, y) ]
        self.dc.DrawLines(points)
        
    # draw a spline; each element in points is a 2-uple with x,y coordinates
    def drawSpline(self, points, style):
        self.setDrawingStyle(style)
        self.dc.DrawSpline( [ (x, self.height-y) for x,y in points ])        
    
    # draw a text label with top left corner at x, y
    def drawText(self, label, x, y,
                 font, foregroundColour, backgroundColour):
        self.setWritingStyle(font, foregroundColour, backgroundColour)
        self.dc.DrawText(label, x, self.height-y)
    
    # draw several text labels with top left corners given in xs, ys
    def drawTexts(self, labels, xs, ys,
                  font, foregroundColour, backgroundColour):
        self.setWritingStyle(font, foregroundColour, backgroundColour)
        for label, x, y in zip(labels, xs, ys):
            self.dc.DrawText(label, x, self.height-y)
    
    # draw a text label at x, y
    # this version allows to specify an angle and a reference point
    def drawFancyText(self, label, x, y,
                      font, foregroundColour, backgroundColour,
                      angle=None,
                      referencePoint='northwest'):
#         styl = style.DrawingStyle(colours.funkypink,
#                                    colours.funkypink)
#         self.drawCircle(x, y, 3, styl)
        if angle is None:
            angle = 0
        width, height = self.dc.GetTextExtent(label)
        # useful for rotating the text
        co = cos ( angle * pi / 180.0 )
        si = sin ( angle * pi / 180.0 )
        # set starting coordinates depending on text size
        if referencePoint == 'northwest':
            xoffset = 0
            yoffset = 0
        elif referencePoint == 'southwest':
            xoffset = -si * height
            yoffset = co * height
        elif referencePoint == 'northeast':
            xoffset = -co * width
            yoffset = -si * width
        elif referencePoint == 'southeast':
            xoffset = -co * width - si * height
            yoffset = -si * width + co * height
        elif referencePoint == 'centre' or referencePoint == 'center':
            xoffset =  (-co * width - si * height) / 2.0
            yoffset =  (-si * width + co * height) / 2.0
        x += xoffset
        y += yoffset
        self.setWritingStyle(font, foregroundColour, backgroundColour)
#         if angle is None:
#             self.dc.DrawText(label, x, self.height-y)
#         else:
        self.dc.DrawRotatedText(label, x, self.height-y, angle)
        
    # draw a polygon
    # x and y are lists of point coordinates
    def drawPolygon(self, xs, ys, style):
        self.setDrawingStyle(style)
        points = [ (x, self.height-y) for x, y in zip(xs, ys) ]
        self.dc.DrawPolygon(points)

    # draw several polygons with the same style
    # x and y are lists of lists of point coordinates
    # style is either unique or a list of styles to use
    def drawPolygons(self, xss, yss, style):
        self.setDrawingStyle(style)
        for i, (xs, ys) in enumerate(zip(xss, yss)):
            points = [ (x, self.height-y) for x, y in zip(xs, ys) ]
            self.dc.DrawPolygon(points)

    # draw a bitmap using the given north-west corner
    def drawBitmap(self, bitmap, NWcorner):
        image = wx.Image( *bitmap.size )
        image.SetData( bitmap.convert("RGB").tobytes() )
        x, y = NWcorner
        self.dc.DrawBitmap(image.ConvertToBitmap(), x, self.height-y)
        
# class used to paint on a wx thumbnail
class WxThumbnailCanvas(WxCanvas):
    # set a drawing style
    # for internal use only
    def setDrawingStyle(self, thisStyle):
        pen = self.dc.GetPen()
        if thisStyle.lineStyle is None or thisStyle.lineStyle == 'solid':
            pen.SetStyle(wx.SOLID)
        # elif thisStyle.lineStyle == 'dashed':
        #     pen.SetStyle(wx.SHORT_DASH)
        if not thisStyle.lineColour is None:
            # make the line look thinner for the thumbnail, by adding some alpha
            # component
            r,g,b,a = thisStyle.lineColour.getRGBA()
            thumbnailLineColour = style.Colour(r, g, b, max(0,a-100))
            pen.SetColour(convertColour(thumbnailLineColour))
        if not thisStyle.fillColour is None:
            self.dc.SetBrush(wx.Brush(convertColour(thisStyle.fillColour)))
        # we paint on a thumbnail so we use a thin line
        pen.SetWidth(1)
        self.dc.SetPen(pen)
        
    # we don't draw many shapes because they wouldn't be distinguishable anyway
    def drawRectangle(self, x, y, w, h, style, referencePoint='center'):
        pass
    def drawRectangles(self, xs, ys, ws, hs, style, referencePoint='center'):
        pass
    
    # draw a circle centered at coordinates x, y
    def drawCircle(self, x, y, r, style):
        pass
#         self.setDrawingStyle(style)
#         self.dc.DrawCircle(x, self.height-y, .5)
    # draw a list of circles with the same colour style
    # parameters xs, ys, rs should be lists
    def drawCircles(self, xs, ys, rs, style):
        pass
#         self.setDrawingStyle(style)
#         for x, y, r in zip(xs, ys, rs):
#             self.dc.DrawCircle(x, self.height-y, .5)

    # draw a line
    def drawLine(self, x1, y1, x2, y2, style):
        self.setDrawingStyle(style)
        self.dc.DrawLine(x1, self.height-y1, x2, self.height-y2)

    # draw a spline; each element in points is a 2-uple with x,y coordinates
    def drawSpline(self, points, style):
        self.setDrawingStyle(style)
        self.dc.DrawSpline( [ (x, self.height-y) for x,y in points ])
        
    # draw a text label with top left corner at x, y
    def drawText(self, label, x, y,
                 font, foregroundColour, backgroundColour):
        pass
    
    # draw text labels with top left corner at xs, ys
    def drawTexts(self, labels, xs, ys,
                 font, foregroundColour, backgroundColour):
        pass
    
    def drawFancyText(self, label, x, y,
                      font, foregroundColour, backgroundColour,
                      angle=None,
                      referencePoint='centre'):
        pass
    
    def drawPolygon(self, x, y, style):
        pass
    def drawPolygons(self, x, y, style):
        pass
    def drawBitmap(self, bitmap, NWcorner):
        pass
