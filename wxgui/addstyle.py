#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: July 29th 2011 by Fabien Tricoire
#
import types

import wx

import util
import style

# this class pops a window in order to choose one or several styles
class AddStyleDialog(wx.Dialog):
    def __init__(self, parent):
#         import config
        wx.Dialog.__init__(self, parent, -1,
                           title='Available styles')

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        treeSizer = wx.BoxSizer(wx.VERTICAL)
        # panel for the tree!
        treePanel = wx.Panel(self, -1, style=wx.SUNKEN_BORDER)
        self.tree = wx.TreeCtrl(treePanel, -1,
                           wx.DefaultPosition,
                           (-1,-1),
                           wx.TR_HIDE_ROOT |
                           wx.TR_HAS_BUTTONS |
                           wx.TR_MULTIPLE)
        root = self.tree.AddRoot('Style modules')
        # for each module, add styles found into it to the tree
        for moduleName in util.getPluginNames():
            module = __import__(moduleName)
            subItems = []
            for item in dir(module):
                thisOne = module.__getattribute__(item)
                if type(thisOne) is types.TypeType and \
                        issubclass(thisOne, style.Style) and \
                        not issubclass(style.Style, thisOne):
                    subItems.append(thisOne.__name__ +': '+ thisOne.description)
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
        self.SetSize((500,500))
        
        self.CenterOnScreen()

    # deactivate nodes, only leaves can be selected
    def onSelection(self, event):
        for item in self.tree.GetSelections():
            # we skip selected items which are not styles
            if self.tree.ItemHasChildren(item):
                self.tree.UnselectItem(item)
        
