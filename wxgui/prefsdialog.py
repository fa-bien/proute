#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: July 29th 2011 by Fabien Tricoire
#
import sys

import wx

from . import guiconfig

class PreferencesDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1,
                           title='User preferences')
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        # do we want to save the toplevel frame layout as default layout
        # when exiting?
        mainSizer.Add((0, 10), 0)
        self.layoutCheckBox = \
            wx.CheckBox( self,
                         -1,
                         'Save current layout as default when exiting program' )
        self.layoutCheckBox.SetValue(guiconfig.preferences['save layout'])
        mainSizer.Add(self.layoutCheckBox)
        # same with curent session
        mainSizer.Add((0, 10), 0)
        self.sessionCheckBox = \
            wx.CheckBox( self,
                         -1,
                         'Save current session when exiting program')
        self.sessionCheckBox.SetValue(guiconfig.preferences['save session'])
        mainSizer.Add(self.sessionCheckBox)
        # add standard buttons
        mainSizer.Add((0, 20), 1)
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, wx.ID_OK)
        cancelButton = wx.Button(self, wx.ID_CANCEL)
        buttonSizer.Add(okButton, 0)
        buttonSizer.Add((20, 0), 1)
        buttonSizer.Add(cancelButton, 0)
        mainSizer.Add(buttonSizer, 0, wx.ALIGN_CENTER)
        mainSizer.Add((0, 10), 0)
        # now we're ready
        paddingSizer = wx.BoxSizer(wx.HORIZONTAL)
        paddingSizer.Add((10,0), 0)
        paddingSizer.Add(mainSizer, 0)
        paddingSizer.Add((10,0), 0)
        self.SetSizer(paddingSizer)
        paddingSizer.Fit(self)
#         self.SetSize((300,300))
        self.CenterOnScreen()
    
