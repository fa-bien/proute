#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: October 4th 2011 by Fabien Tricoire
#
import os
import sys

import wx

import stylesheet
from . import events

from . import guiconfig

class GridManager(wx.Frame):
    def __init__(self, parent, styleSheet, solutionData):
        wx.Frame.__init__(self, parent, wx.ID_ANY,
                          title='Grid management')
        # style sheet for this window
        self.styleSheet = styleSheet
        # layout for this dialog
        mainSizer = wx.FlexGridSizer(7, 2, 10, 10)
        #
        attributeValues = set([ route[self.styleSheet.gridRouteAttribute]
                                for route in solutionData.routes ])
        gridSize = len(attributeValues)
        # first line: is the grid activated?
        label = wx.StaticText(self, -1, 'Activate grid')
        self.activatedCheckBox = wx.CheckBox(self, -1)
        self.activatedCheckBox.SetValue(self.styleSheet.grid)
        mainSizer.Add(label, 0,
                      wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        mainSizer.Add(self.activatedCheckBox, 0,
                      wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.Bind(wx.EVT_CHECKBOX,
                  self.activationHandler, self.activatedCheckBox)
        # second line: parameter on which the grid is constructed
        label = wx.StaticText(self, -1, 'Parameter')
        # only use parameters with hashable values
        choices = [ x for x in solutionData.routeAttributes
                    if solutionData.routes[0][x].__hash__ ]
        self.parameterChoice = wx.Choice(self, -1,
                                         choices=choices)
        if self.styleSheet.gridRouteAttribute:
            self.parameterChoice.SetSelection(\
                solutionData.routeAttributes.index(\
                    self.styleSheet.gridRouteAttribute))
        mainSizer.Add(label, 0,
                      wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        mainSizer.Add(self.parameterChoice, 0,
                      wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.Bind(wx.EVT_CHOICE, self.parameterHandler, self.parameterChoice)
        # third line: also filter nodes?
        label = wx.StaticText(self, -1, 'Filter nodes too')
        self.filterNodesBox = wx.CheckBox(self, -1)
        self.filterNodesBox.SetValue(self.styleSheet.filterNodesInGrid)
        mainSizer.Add(label, 0,
                      wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        mainSizer.Add(self.filterNodesBox, 0,
                      wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.Bind(wx.EVT_CHECKBOX,
                  self.filterNodesTooHandler, self.filterNodesBox)
        # fourth line: grid geometry
        label = wx.StaticText(self, -1, 'Number of columns')
        self.nColumnsControl = wx.SpinCtrl(self, -1)
        self.nColumnsControl.SetRange(1, gridSize)
        self.nColumnsControl.SetValue(self.styleSheet.nColumnsInGrid
                                      if self.styleSheet.nColumnsInGrid
                                      else 1)
        mainSizer.Add(label, 0,
                      wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        mainSizer.Add(self.nColumnsControl, 0,
                      wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.Bind(wx.EVT_SPINCTRL, self.geometryHandler, self.nColumnsControl)
        # fifth line: display grid lines?
        label = wx.StaticText(self, -1, 'Draw grid lines')
        self.drawGridLinesBox = wx.CheckBox(self, -1)
        self.drawGridLinesBox.SetValue(self.styleSheet.drawGridLines)
        mainSizer.Add(label, 0,
                      wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        mainSizer.Add(self.drawGridLinesBox, 0,
                      wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.Bind(wx.EVT_CHECKBOX,
                  self.decorationHandler, self.drawGridLinesBox)
        # sixth line: display cell title?
        label = wx.StaticText(self, -1, 'Title for each cell')
        self.cellTitleBox = wx.CheckBox(self, -1)
        self.cellTitleBox.SetValue(self.styleSheet.displayCellTitle)
        mainSizer.Add(label, 0,
                      wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        mainSizer.Add(self.cellTitleBox, 0,
                      wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.Bind(wx.EVT_CHECKBOX,
                  self.cellTitleActivationHandler, self.cellTitleBox)
        # seventh line: cell title format
        label = wx.StaticText(self, -1, 'Cell title format')
        self.cellTitleFormat = wx.TextCtrl(self, size=(150,-1))
        self.cellTitleFormat.SetValue(self.styleSheet.cellTitleFormat)
        mainSizer.Add(label, 0,
                      wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        mainSizer.Add(self.cellTitleFormat, 0,
                      wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.Bind(wx.EVT_TEXT,
                  self.cellTitleFormatHandler, self.cellTitleFormat)
        #
        self.SetSizer(mainSizer)
#         self.SetSize((400,500))
        mainSizer.Fit(self)
        self.Show()

    def activationHandler(self, event):
        # activate the grid if required
        self.styleSheet.grid = self.activatedCheckBox.GetValue()
        # repaint using the new parameters
        events.postStyleSheetUpdateEvent(self)
        # update number of columns
        self.nColumnsControl.SetValue(self.styleSheet.nColumnsInGrid)

    def parameterHandler(self, event):
        # set the right parameter to build the grid
        self.styleSheet.gridRouteAttribute = \
            self.parameterChoice.GetStringSelection()
        # also reset number of columns because grid size changes
        self.styleSheet.nColumnsInGrid = None
        # repaint using the new parameters
        events.postStyleSheetUpdateEvent(self)
        # update number of columns
        self.nColumnsControl.SetValue(self.styleSheet.nColumnsInGrid)

    def geometryHandler(self, event):
        # adjust number of columns
        self.styleSheet.nColumnsInGrid = self.nColumnsControl.GetValue()
        self.styleSheet.nRowsInGrid = None
        # repaint using the new parameters
        events.postStyleSheetUpdateEvent(self)

    def decorationHandler(self, event):
        # update displaying of grid
        self.styleSheet.drawGridLines = self.drawGridLinesBox.GetValue()
        # repaint using the new parameters
        events.postStyleSheetUpdateEvent(self)

    def cellTitleActivationHandler(self, event):
        # update displaying of cell title
        self.styleSheet.displayCellTitle = self.cellTitleBox.GetValue()
        # repaint using the new parameters
        events.postStyleSheetUpdateEvent(self)
        
    def cellTitleFormatHandler(self, event):
        # update displaying of cell title
        self.styleSheet.cellTitleFormat = self.cellTitleFormat.GetValue()
        # repaint using the new parameters
        events.postStyleSheetUpdateEvent(self)

    def filterNodesTooHandler(self, event):
        # tell the stylesheet to filter nodes too
        self.styleSheet.filterNodesInGrid = self.filterNodesBox.GetValue()
        # repaint using the new parameters
        events.postStyleSheetUpdateEvent(self)        
