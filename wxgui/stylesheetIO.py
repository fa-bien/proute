#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
#
import types

import wx

import util
import stylesheet
import loaddata

# this class pops a dialog in order to load a stylesheet
class LoadStyleSheetDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1,
                           title='Available stylesheets')

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        treeSizer = wx.BoxSizer(wx.VERTICAL)
        # panel for the tree!
        treePanel = wx.Panel(self, -1, style=wx.SUNKEN_BORDER)
        self.tree = wx.TreeCtrl(treePanel, -1,
                           wx.DefaultPosition,
                           (-1,-1),
                           wx.TR_HIDE_ROOT |
                           wx.TR_HAS_BUTTONS )
        root = self.tree.AddRoot('Plugins')
        # for each module, add stylesheets found into it to the tree
        for moduleName in util.getPluginNames():
            module = __import__(moduleName)
            subItems = []
            for item in dir(module):
                thisOne = module.__getattribute__(item)
                if type(thisOne) is type and \
                        issubclass(thisOne, stylesheet.StyleSheet) and \
                        not issubclass(stylesheet.StyleSheet, thisOne):
                    name = thisOne.__name__
                    subItems.append(name)
            if len(subItems) > 0:
                thisNode = self.tree.AppendItem(root, module.__name__)
                for item in subItems:
                    self.tree.AppendItem(thisNode, item) 
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onSelection)
        # now add the tree to the sizer in the panel...
        treeSizer.Add(self.tree, 1, wx.EXPAND)
        treePanel.SetSizer(treeSizer)

        # expand the tree by default
        self.tree.ExpandAll()
        
        mainSizer.Add(treePanel, 1, wx.EXPAND)
        mainSizer.Add((0,10), 0)

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        # add standard buttons
        okButton = wx.Button(self, wx.ID_OK)
        cancelButton = wx.Button(self, wx.ID_CANCEL)
        buttonSizer.Add(okButton, 0)
        buttonSizer.Add((20,0), 1)
        buttonSizer.Add(cancelButton, 0)
        mainSizer.Add(buttonSizer, 0, wx.ALIGN_CENTER)
        mainSizer.Add((0,10), 0)
        # now we're ready
        self.SetSizer(mainSizer)
        self.SetSize((400,500))
#         mainSizer.Fit(self)
        self.CenterOnScreen()

    # deactivate nodes, only leaves can be selected
    def onSelection(self, event):
        for item in self.tree.GetSelections():
            # we skip selected items which are not styles
            if self.tree.ItemHasChildren(item):
                self.tree.UnselectItem(item)
                
# this class pops a dialog in order to save the current stylesheet
class SaveStyleSheetDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1,
                           title='Save stylesheet')
        # layout for this dialog
        mainSizer = wx.FlexGridSizer(3, 2, 10, 10)
        # first line: sheet name
        label = wx.StaticText(self, -1, 'Stylesheet name:')
        self.sheetName = wx.TextCtrl(self,
                                     size=(self.GetSize()[0]/2, 22))
        self.sheetName.SetValue(parent.styleSheet.__module__)
        self.sheetName.Bind(wx.EVT_TEXT, self.onTextEntry)
        #
        mainSizer.Add(label, 0, wx.ALIGN_RIGHT|wx.ALL, 5)
        mainSizer.Add(self.sheetName, 0, wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, 5)
        # second line: problems for which this sheet should be the default sheet
        label = wx.StaticText(self, -1, 'Used as default sheet for:')
        # we need this object to find out what we can load
        loader = loaddata.DataLoader()
        availableTypes = loader.getAvailableTypes()
        self.problemList = wx.CheckListBox(self,
                                           choices=availableTypes)
        self.problemList.SetCheckedItems(
            [ i for i, t in enumerate(availableTypes)
              if t in parent.styleSheet.defaultFor ] )
        mainSizer.Add(label, 0, wx.ALIGN_RIGHT|wx.ALL, 5)
        mainSizer.Add(self.problemList, 0, wx.EXPAND, 5)
        # add standard dialog buttons
        self.okButton = wx.Button(self, wx.ID_OK)
        if self.sheetName.GetValue() == '':
            self.okButton.Disable()
        cancelButton = wx.Button(self, wx.ID_CANCEL)
        mainSizer.Add(self.okButton, 0, wx.ALIGN_RIGHT|wx.ALL, 5)
#         mainSizer.Add((20,0), 1)
        mainSizer.Add(cancelButton, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        # now we're ready
        self.SetSizer(mainSizer)
        mainSizer.Fit(self)
        self.CenterOnScreen()

    # update ok button when text is entered
    def onTextEntry(self, event):
        if not self.okButton.IsEnabled() and self.sheetName.GetValue() != '':
            self.okButton.Enable()
            self.okButton.SetDefault()
        elif self.okButton.IsEnabled() and self.sheetName.GetValue() == '':
            self.okButton.Disable()
