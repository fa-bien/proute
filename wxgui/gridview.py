#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: July 29th 2011 by Fabien Tricoire
#
import sys
import math

import wx

from vrppanel import VrpPanel
import util

# present routes in a grid, with each cell displaying a different part of the
# solution
class GridViewer(wx.Frame):
    def __init__(self, inputData, solutionData, routeAttribute,
                 attributeName=None,
                 styleSheet=None):
        wx.Frame.__init__(self, None, wx.ID_ANY, title='Grid view')

        if attributeName is None:
            attributeName = routeAttribute
        gridStyle = stylesheet.StyleSheet() if styleSheet is None\
            else styleSheet
        # step 1: count and sort the occurrences of the grid attribute
        attributeValues = set([ route[routeAttribute]
                                for route in solutionData.routes ])
        gridSize = len(attributeValues)
        # old version
        gridWidth = int(math.ceil(math.sqrt(gridSize)))
        # new version
        colsPerRow = 4.0/3.0 * inputData.heightOverWidth
        gridWidth = int(colsPerRow * gridWidth)
        #
        gridHeight = 1 + gridSize / gridWidth
        gridSizer = wx.GridSizer(gridHeight, gridWidth,
                                 vgap = 5, hgap = 5)
        #
        # step 2: fill the grid ffs!
        vSizers = [ wx.BoxSizer(wx.VERTICAL) for i in range(gridSize) ]
        labels = [ attributeName + ' ' + str(value)
                   for value in attributeValues ]

        predicates = [ util.makeRoutePredicate(routeAttribute, value)
                       for value in attributeValues ]

        self.panels = [ VrpPanel(self,
                                 inputData = inputData,
                                 solutionData = solutionData,
                                 routePredicate = pred,
                                 styleSheet = gridStyle )
                        for pred in predicates ]
        # add all our panels to our grid
        for vSizer, label, panel, count in zip(vSizers,
                                               labels,
                                               self.panels,
                                               range(len(attributeValues))):
            vSizer.Add(wx.StaticText(self, label=label),
                       proportion=0,
                       flag=wx.ALIGN_CENTER | wx.ALL,
                       border=3)
            vSizer.Add(panel, 1, wx.EXPAND)
            # add the whole box in our grid
            gridSizer.Add(vSizer, 1, wx.EXPAND)
            w = inputData.width / gridWidth
            h = w * inputData.heightOverWidth
            panel.SetSize((w, h))
        
        # display the grid!
        self.SetSizerAndFit(gridSizer)
        self.Show()

