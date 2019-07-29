#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: August 7th 2011 by Fabien Tricoire
#
import sys

import wx

from . import setool
from . import events

# this widget allows to edit styles
# the object to edit must be set using the method setEditable(style)
# the object to edit should be a style
class StyleEditor(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style=wx.SUNKEN_BORDER)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(wx.StaticText(self, label='Style editor'),
                           0,
                           flag=wx.ALIGN_CENTER | wx.ALL,
                           border=3)
        self.mainSizer.Add((10, 10))
        # place parameters in a grid, itself in a scrolled window
        self.sw = wx.Panel(self, -1)
        # first column = parameter name, second column = editable value
        self.gridSizer = wx.FlexGridSizer(20, 2, 5, 5)
        self.gridSizer.AddGrowableCol(0, 1)
        self.sw.SetSizer(self.gridSizer)
        
        self.mainSizer.Add(self.sw, 0, wx.EXPAND)
        self.SetSizer(self.mainSizer)
#         self.Bind(events.EVT_STYLESHEET_UPDATE, self.prout)

#     def prout(self, event):
#         print 'prout'
#         event.Skip()
        
    def setEditable(self, styleToEdit):
        # delete the last edited style if there is one
        self.gridSizer.Clear(True)
        self.activeTools = []
        if styleToEdit is None:
            return
        # loop over customizable parameters, i.e. those with an entry in
        # style.parameterInfo
        for parameter in sorted(styleToEdit.parameterInfo.keys()):
            # add the name of the parameter
            self.gridSizer.Add(wx.StaticText(self.sw, label=parameter))
            # now add its editable value
            editTool = self.getStyleEditTool(styleToEdit, parameter)
            self.gridSizer.Add(editTool)
            self.activeTools.append(editTool)
        #
        self.sw.Fit()
#         self.gridSizer.FitInside(self.sw)
        self.SendSizeEvent()
#         self.Parent.SendSizeEvent()

    def update(self):
        for t in self.activeTools:
            t.update()
        
        
    def getStyleEditTool(self, styleToEdit, parameterName):
        classFromString = {
            'boolean': setool.BoolStyleEditTool,
            'int': setool.IntStyleEditTool,
            'float': setool.FloatStyleEditTool,
            'colour': setool.ColourStyleEditTool,
            'colour map': setool.ColourMapStyleEditTool,
            'enumeration parameter': setool.ChoiceListStyleEditTool,
            'arc attribute': setool.ChoiceListStyleEditTool,
            'route attribute': setool.ChoiceListStyleEditTool,
            'node attribute': setool.ChoiceListStyleEditTool,
            'file name': setool.FileNameStyleEditTool,
            }
        # the type of the parameter we want to edit
        paramType = styleToEdit.parameterInfo[parameterName].getType()
        if paramType in classFromString:
            thisClass = classFromString[paramType]
            return thisClass(self.sw, styleToEdit, parameterName)
        else:
            paramName = styleToEdit.parameterValue[parameterName]
            return wx.StaticText(self.sw,
                                 label=str(paramName))
