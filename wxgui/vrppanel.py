#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: August 21st 2011 by Fabien Tricoire
#
import os
import sys
import math

import wx

import config
from . import wxcanvas
from . import events

# zoom operations on the displayed solution
maxZoom=10000
zoomFactor=1.1
zoomKeyStep=0.05

# tolerance factor: how close to a neighbour must the mouse be before we
# consider it's over it?
# 0 means the mouse must be exactly at the coordinates of the node
# 1 means always select the closest node no matter how far it is
maxDistToNeighbourFactor = 0.01

class VrpPanel(wx.Panel):
    def __init__(self, parent, inputData=None, solutionData=None,
                 styleSheet=None,
                 routePredicate=None, #lambda(route): True,
                 nodePredicate=None, #lambda(node): True,
                 nodeInfoList=None):
        wx.Panel.__init__(self, parent, -1)
        self.inputData = inputData
        self.parent = parent
        self.solutionData = solutionData
        self.routePredicate = routePredicate
        self.nodePredicate = nodePredicate
        self.nodeInfoList = nodeInfoList
        if styleSheet is None:
            self.styleSheet = stylesheet.StyleSheet()
        else:
            self.styleSheet = styleSheet
        # default dummy values
        self.revX = lambda x: 0
        self.revY = lambda x: 0
        # event handlers for painting etc
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.Bind(wx.EVT_SIZE, self.onSize)
        # if moving the mouse: display node information or drag the map,
        # depending on whether the left button is pressed or not
        self.Bind(wx.EVT_MOTION, self.onMotion)
        # store mouse position when pressing left mouse button
        # this is useful for dragging the map
        self.dragX, self.dragY = None, None
        self.Bind(wx.EVT_LEFT_DOWN, self.storePosition)
        self.Bind(wx.EVT_LEFT_UP, self.resetPosition)
        # double-click handler
        self.Bind(wx.EVT_LEFT_DCLICK, self.onDoubleClick)
        # debug: display coordinates on right click
        self.Bind(wx.EVT_RIGHT_DOWN, self.onRightClick)
        # zoom using the scroll wheel
        self.Bind(wx.EVT_MOUSEWHEEL, self.onMouseWheel)
        # also navigate the map with the arrow keys
        self.Bind(wx.EVT_KEY_DOWN, self.onChar)
        # useful to build file name for saving a same panel multiple times
        self.nTimesSaved = 0
        
    def onPaint(self, event):
        ww, hh = self.GetClientSize()
        # Declaration of the device context for drawing
        if self.IsDoubleBuffered() and self.CanSetTransparent():
            dc = wx.PaintDC(self)
        else:
            myBuffer = wx.Bitmap(ww, hh)
            dc = wx.GCDC(wx.BufferedPaintDC(self, myBuffer))
        # end of device context declaration
        # Now we need to declare a canvas object...
        canvas = wxcanvas.WxCanvas(dc, ww, hh)
#         import cProfile
#         cProfile.runctx('self.styleSheet.paint(self.inputData, self.solutionData, canvas, routePredicate = self.routePredicate, nodePredicate = self.nodePredicate, )', globals(), locals(), 'profiling-data')
        self.styleSheet.paint(self.inputData, self.solutionData, canvas,
                              routePredicate = self.routePredicate,
                              nodePredicate = self.nodePredicate,
                              )
        self.revX, self.revY = \
            self.styleSheet.getReverseCoordMapping(canvas, self.inputData)
#         allowedNodes = set([ node['index'] for node in self.inputData.nodes
#                              if node['x'] > 35 and node['y'] < 35 ])
#         self.styleSheet.paint(self.inputData, self.solutionData, dc,
#                               arcPredicate = lambda(arc):\
#                                   arc['from'] in allowedNodes and\
#                                   arc['to'] in allowedNodes)

    def rePaint(self):
        ww, hh = self.GetClientSize()
        if self.IsDoubleBuffered() and self.CanSetTransparent():
            dc = wx.ClientDC(self)
        else:
            myBuffer = wx.Bitmap(ww, hh)
            dc = wx.GCDC(wx.BufferedDC(wx.ClientDC(self), myBuffer))
        # end of device context declaration
        # Now we need to declare a canvas object...
        canvas = wxcanvas.WxCanvas(dc, ww, hh)
        self.styleSheet.paint(self.inputData, self.solutionData, canvas,
                              routePredicate = self.routePredicate,
                              nodePredicate = self.nodePredicate,
                              )
        self.revX, self.revY = \
            self.styleSheet.getReverseCoordMapping(canvas, self.inputData)
#         allowedNodes = set([ node['index'] for node in self.inputData.nodes
#                              if node['x'] > 35 and node['y'] < 35 ])
#         self.styleSheet.paint(self.inputData, self.solutionData, dc,
#                               arcPredicate = lambda(arc):\
#                                   arc['from'] in allowedNodes and\
#                                   arc['to'] in allowedNodes)

    def onSize(self, event):
        if self.IsDoubleBuffered():
            self.Refresh()
        else:
            self.rePaint()

    # general handler for mouse motion events; redirects to the appropriate
    # method
    def onMotion(self, event):
        if event.Dragging():
            self.dragMap(event)
        else:
            self.mouseOverMap(event)

    # interpret mouse hovering to display node information
    def mouseOverMap(self, event):
        self.SetFocus()
        x, y = event.GetPosition()
        y = self.GetClientSize()[1] - y
        maxDist = maxDistToNeighbourFactor * \
            math.hypot(self.styleSheet.xmax - self.styleSheet.xmin,
                       self.styleSheet.ymax - self.styleSheet.ymin)
        thisNode = self.inputData.getNodeAtCoords(self.revX(x),
                                                  self.revY(y),
                                                  maxDist)
        if self.nodeInfoList is None:
            if not thisNode is None:
                print(thisNode)
        else:
            self.nodeInfoList.updateNodeInfo(thisNode, self.solutionData)

    # mouse dragging: drag the map if possible
    def dragMap(self, event):
        x, y = event.GetPosition()
        x, y = self.revX(x), self.revY(self.GetClientSize()[1] - y)
        width = self.styleSheet.xmax - self.styleSheet.xmin
        height = self.styleSheet.ymax - self.styleSheet.ymin
        centerX = (self.styleSheet.xmax + self.styleSheet.xmin) / 2.0
        centerY = (self.styleSheet.ymax + self.styleSheet.ymin) / 2.0
        centerX += self.dragX - x
        centerY += self.dragY - y
        self.updateView(centerX, centerY, width, height)
        self.rePaint()
        # update the coordinates _after_ updating the view, in case we
        # requested something out of the map
        x, y = event.GetPosition()
        x, y = self.revX(x), self.revY(self.GetClientSize()[1] - y)
        self.dragX, self.dragY = x, y
            
    # double-click event handler: save the panel to a pdf file
    def onDoubleClick(self, event):
        self.exportToPDF()

    def exportToPDF(self, fName=None, dirName=None):
        self.nTimesSaved += 1
#         ww, hh = (self.inputData.width, self.inputData.height) \
#             if self.styleSheet.keepAspectRatio else self.GetClientSize()
        ww, hh = self.GetClientSize()
        if fName is None:
            fName = self.solutionData.name + '-' + str(self.nTimesSaved) +'.pdf'
        if not dirName is None:
            fName = os.path.join(dirName, fName)
        try:
            import reportlabCanvas
            canvas = reportlabCanvas.ReportlabCanvas(ww, hh, fName)
            self.styleSheet.paint( self.inputData, self.solutionData, canvas,
                                   routePredicate = self.routePredicate,
                                   nodePredicate = self.nodePredicate )
            # store it to a file
            from reportlab.graphics import renderPDF
#             currentDir = os.getcwd()
#             os.chdir(config.startingDir)
#         renderPDF.drawToFile(canvas.drawing, fName)
            canvas.canvas.showPage()
            canvas.canvas.save()
            print('Saved to', fName)
#             os.chdir(currentDir)
        except Exception as e:
            dialog = wx.MessageDialog(self,
                                      str(e) + '\n\nIs ReportLab installed?',
                                      'Can\'t export to PDF',
                                      wx.OK | wx.ICON_ERROR)
            dialog.ShowModal()
            

    # zoom using scroll wheel
    def onMouseWheel(self, event):
        # normalisation of the value: depending on the platform the values can
        # be totally different
        value = 1 if event.GetWheelRotation() > 0 else -1
        x, y = event.GetPosition()
        x, y = self.revX(x), self.revY(self.GetClientSize()[1] - y)
        width = self.styleSheet.xmax - self.styleSheet.xmin
        height = self.styleSheet.ymax - self.styleSheet.ymin
        dx1 = x - (self.styleSheet.xmin + width / 2.0)
        dy1 = y - (self.styleSheet.ymin + height / 2.0)
        # zoom in or out depending on whether we scrolled up or down
        factor = zoomFactor ** value
        # new width and height in inputData coordinates
        newWidth = (self.styleSheet.xmax - self.styleSheet.xmin) / factor
        newHeight = (self.styleSheet.ymax - self.styleSheet.ymin) / factor
        dx2 = dx1 * newWidth / width
        dy2 = dy1 * newHeight / height
        newCentreX = x - dx2
        newCentreY = y - dy2
        # update the view
        self.updateView(newCentreX, newCentreY, newWidth, newHeight)
        self.rePaint()

    # this method updates the view so that it s around coordinates x, y and with
    # given width and height
    # all these parameters are given in the coordinate system of self.inputData
    def updateView(self, x, y, width, height):
        # make sure that we don't zoom out further than scale 1
        width = min(width, self.inputData.xmax - self.inputData.xmin)
        height = min(height, self.inputData.ymax - self.inputData.ymin)
        # also make sure that we don't zoom in too much
        width = max(width,
                    (self.inputData.xmax - self.inputData.xmin) / maxZoom)
        height = max(height,
                     (self.inputData.ymax - self.inputData.ymin) / maxZoom)
#         print (self.inputData.ymax - self.inputData.ymin) / height, \
#             (self.inputData.xmax - self.inputData.xmin) / width
        # now we can compute the new bounding box
        newXmin, newXmax = x - width / 2, x + width / 2
        newYmin, newYmax = y - height / 2, y + height / 2
        # make sure that we don't move out of the map
        if newXmin < self.inputData.xmin:
            newXmax += self.inputData.xmin - newXmin
            newXmin = self.inputData.xmin
        elif newXmax > self.inputData.xmax:
            newXmin -= newXmax - self.inputData.xmax
            newXmax = self.inputData.xmax
        if newYmin < self.inputData.ymin:
            newYmax += self.inputData.ymin - newYmin
            newYmin = self.inputData.ymin
        elif newYmax > self.inputData.ymax:
            newYmin -= newYmax - self.inputData.ymax
            newYmax = self.inputData.ymax
        # now we can update the view
        self.styleSheet.xmin = newXmin
        self.styleSheet.ymin = newYmin
        self.styleSheet.xmax = newXmax
        self.styleSheet.ymax = newYmax

    # for debug purpose only
    def onRightClick(self, event):
        x, y = event.GetPosition()
        x, y = self.revX(x), self.revY(self.GetClientSize()[1] - y)
        print(x, y)

    # store mouse position when pressing mouse button, in order to allow to drag
    # the map
    def storePosition(self, event):
        x, y = event.GetPosition()
        self.dragX, self.dragY = \
            self.revX(x), self.revY(self.GetClientSize()[1] - y)
        
    # store mouse position when pressing mouse button, in order to allow to drag
    # the map
    def resetPosition(self, event):
        self.dragX, self.dragY = None, None

    # move/zoom the map with arrow and +/- keys
    # delete the current solution with del or backspace
    def onChar(self, event):
#         print event.GetKeyCode(), event.GetUnicodeKey(), chr(event.GetKeyCode()), unichr(event.GetUnicodeKey())
        # move the map by 10%
        xoffset = (self.styleSheet.xmax - self.styleSheet.xmin) * zoomKeyStep
        yoffset = (self.styleSheet.ymax - self.styleSheet.ymin) * zoomKeyStep
        centerX = (self.styleSheet.xmax + self.styleSheet.xmin) / 2.0
        centerY = (self.styleSheet.ymax + self.styleSheet.ymin) / 2.0
        width = self.styleSheet.xmax - self.styleSheet.xmin
        height = self.styleSheet.ymax - self.styleSheet.ymin
        # left
        if event.GetKeyCode() == wx.WXK_LEFT:
            centerX -= xoffset 
        # right
        elif event.GetKeyCode() == wx.WXK_RIGHT:
            centerX += xoffset
        # top
        elif event.GetKeyCode() == wx.WXK_UP:
            centerY += yoffset
        # bottom
        elif event.GetKeyCode() == wx.WXK_DOWN:
            centerY -= yoffset
        # +
        elif chr(event.GetUnicodeKey()) == '+':
            width /= zoomFactor
            height /= zoomFactor
        # -
        elif chr(event.GetUnicodeKey()) == '-':
            width *= zoomFactor
            height *= zoomFactor
        elif event.GetUnicodeKey() == wx.WXK_DELETE or \
                event.GetUnicodeKey() == wx.WXK_BACK:
            events.postDeleteSolutionEvent(self)
            return
        else:
            event.Skip()
            return
        self.updateView(centerX, centerY, width, height)
        self.rePaint()
        event.Skip()
