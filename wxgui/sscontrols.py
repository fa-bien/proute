#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: March 6th 2015 by Fabien Tricoire
#
import wx

from wx.lib.scrolledpanel import ScrolledPanel

import style
import events
from stylecontrols import StyleEditor
from addstyle import AddStyleDialog
from vrpexceptions import MissingAttributeException

ssControlWidth = 240
ssControlHeight = 200

class StyleSheetControls(ScrolledPanel):
    def __init__(self, parent, styleSheet):
        ScrolledPanel.__init__(self, parent, -1)#, style=wx.BORDER_SUNKEN)
#         self.styleSheet = styleSheet
        sizer = wx.BoxSizer(wx.VERTICAL)
        # add a text label
        sizer.Add(wx.StaticText(self, label='Style sheet control'),
                  proportion=0,
                  flag=wx.ALIGN_CENTER,
                  border=3)
        # padding
        sizer.Add((10,10))
        # style editor
        styleEditor = StyleEditor(self)
        # style sheet editor: it needs the style editor
        self.styleSheetEditor = StyleSheetEditor(self, styleSheet, styleEditor)
        # now we can add them in the correct order
        sizer.Add(self.styleSheetEditor, 0, wx.ALIGN_CENTER | wx.EXPAND)
        # padding
#         sizer.Add((0,5))
        sizer.Add(styleEditor, 1, wx.ALIGN_CENTER | wx.EXPAND )
        # finally let's not forget to assign the sizer
        self.SetSizer(sizer)
        self.SetupScrolling()

    def newStyleSheet(self, newSheet):
        self.styleSheetEditor.newSheet(newSheet)
        
class StyleSheetEditor(wx.Panel):
    def __init__(self, parent, styleSheet, styleControl):
        wx.Panel.__init__(self, parent, -1, style=wx.SUNKEN_BORDER)
        self.styleSheet = styleSheet
        self.styleControl = styleControl
        sizer = wx.BoxSizer(wx.VERTICAL)
        # add a text label
        sizer.Add(wx.StaticText(self, label='Sheet management'),
                  proportion=0,
                  flag=wx.ALIGN_CENTER | wx.ALL,
                  border=3)
        # padding
        sizer.Add((10,10))
        # first style sheet control: aspect ratio checkbox
        self.ratioCheckBox = wx.CheckBox( self,
                                          -1,
                                          'Preserve original aspect ratio' )
        self.ratioCheckBox.SetValue(self.styleSheet.keepAspectRatio)
        sizer.Add(self.ratioCheckBox)
        self.ratioCheckBox.Bind(wx.EVT_CHECKBOX,
                                self.aspectRatioCheckboxHandler)
        # generic style sheet control check list box
        self.styles = [ x for x in self.styleSheet.styles ]
        self.styles.reverse()
        # initial state: all styles in sheet are active
        checked = [ i for i in range(len(self.styles)) ]
        listLabels = [ x.description for x in self.styles ]
        self.styleCheckList = wx.CheckListBox(self,
                                              size=(ssControlWidth,
                                                    ssControlHeight),
                                              choices=listLabels)
        self.styleCheckList.SetChecked(checked)
        sizer.Add(self.styleCheckList, 0, wx.EXPAND)
        # we also add four buttons for manipulating styles
        # for that we use a grid
        grid = wx.GridSizer(0, 2, 10, 10)
        self.addButton = wx.Button(self, wx.ID_ADD)
        self.removeButton = wx.Button(self, wx.ID_REMOVE)
        self.removeButton.Disable()
        self.moveUpButton = wx.Button(self, wx.ID_UP)
        self.moveUpButton.Disable()
        self.moveDownButton = wx.Button(self, wx.ID_DOWN)
        self.moveDownButton.Disable()
        self.renameField = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.renameField.Disable()
        self.renameButton = wx.Button(self, -1, 'Rename style')
        self.renameButton.Disable()
        grid.Add(self.moveUpButton)
        grid.Add(self.addButton)
        grid.Add(self.moveDownButton)
        grid.Add(self.removeButton)
        grid.Add(self.renameField)
        grid.Add(self.renameButton)
        sizer.Add(grid, 0, wx.ALIGN_CENTER)
        sizer.Add((5, 5))
        # finally let's not forget to assign the sizer
        self.SetSizer(sizer)
        # update the stylesheet in case of (un)check event
        self.styleCheckList.Bind(wx.EVT_CHECKLISTBOX, self.updateStyleSheet)
        # update the style edition tool if needed
        self.styleControl.Bind(events.EVT_STYLE_UPDATE, self.onStyleUpdate)
        # update the buttons in case an element is selected in the list
        self.styleCheckList.Bind(wx.EVT_LISTBOX, self.onCheckListSelection)
        # remove the selected element when the "remove" button is clicked
        self.removeButton.Bind(wx.EVT_BUTTON, self.removeStyle)
        # move the selected element up when the "move up" button is clicked
        self.moveUpButton.Bind(wx.EVT_BUTTON, self.moveStyleUp)
        # move the selected element down when the "move down" button is clicked
        self.moveDownButton.Bind(wx.EVT_BUTTON, self.moveStyleDown)
        # rename the current style when needed
        self.renameButton.Bind(wx.EVT_BUTTON, self.renameStyle)
        self.renameField.Bind(wx.EVT_TEXT_ENTER, self.renameStyle)
        # pop a dialog to add a style
        self.addButton.Bind(wx.EVT_BUTTON, self.addStyleInteractively)

    def newSheet(self, newSheet):
        self.styleSheet = newSheet
        self.ratioCheckBox.SetValue(self.styleSheet.keepAspectRatio)
        # generic style sheet control check list box
        self.styles = [ x for x in self.styleSheet.styles ]
        self.styles.reverse()
        # re-initialize state: all styles in sheet are active
        checked = [ i for i in range(len(self.styles)) ]
        listLabels = [ x.description for x in self.styles ]
        self.styleCheckList.Clear()
        self.styleCheckList.AppendItems(listLabels)
        self.styleCheckList.SetChecked(checked)

    # update the keepAspectRatio value if the box is (un)checked
    def aspectRatioCheckboxHandler(self, event):
        self.styleSheet.keepAspectRatio = event.IsChecked()
        # propagate the event to inform the gui that redrawing is in order
        events.postStyleSheetUpdateEvent(self)
#         event.SetEventObject(self)
#         event.Skip()

    # update the style sheet according to the check list box
    def updateStyleSheet(self, event):
        self.styleSheet.styles = [ style
                                   for i, style in enumerate(self.styles)
                                   if self.styleCheckList.IsChecked(i) ]
        self.styleSheet.styles.reverse()
        # propagate the event to inform the gui that redrawing is in order
        events.postStyleSheetUpdateEvent(self)
#         event.SetEventObject(self)
#         event.Skip()

    def onStyleUpdate(self, event):
        index = self.styleCheckList.GetSelection()
        self.styleControl.update()
#         self.GetParent().SetupScrolling()
        

    def onCheckListSelection(self, event):
        index = event.GetSelection()
        # ugly but necessary: under linux when the program exits an event is
        # sent with index = -1
        if index >= 0:
            self.updateButtons()
            self.styleControl.setEditable(self.styles[index])
            self.renameField.SetValue(self.styleCheckList.GetString(index))
            # update the scrolled panel sizer...
            self.GetParent().SetupScrolling()

    def renameStyle(self, event):
        index = self.styleCheckList.GetSelection()
        self.styles[index].description = self.renameField.GetValue()
        self.styleCheckList.SetString(index, self.renameField.GetValue())
        
    # update the style sheet control buttons in case selection changed in the
    # list
    def updateButtons(self):
        index = self.styleCheckList.GetSelection()
        # case where no item is selected
        if index == wx.NOT_FOUND:
            self.removeButton.Disable()
            self.moveUpButton.Disable()
            self.moveDownButton.Disable()
            self.renameField.Disable()
            self.renameField.SetValue('')
            self.renameButton.Disable()
        else:
            # if an item is selected, it can be removed
            self.removeButton.Enable()
            # it can also be renamed
            self.renameButton.Enable()
            self.renameField.SetValue(self.styleCheckList.GetString(index))
            self.renameField.Enable()
            # should we enable "move up"?
            if index > 0:
                self.moveUpButton.Enable()
            else:
                self.moveUpButton.Disable()
            # same thing for the "move down" button
            if index == len(self.styles)-1:
                self.moveDownButton.Disable()
            else:
                self.moveDownButton.Enable()
        # additionally, update scrolling etc
        self.GetParent().SetupScrolling()

    # remove the selected element when the "remove" button is clicked
    def removeStyle(self, event):
        index = self.styleCheckList.GetSelection()
        self.styles = [ style
                        for i, style in enumerate(self.styles)
                        if i != index ]
        self.styleCheckList.Delete(index)
        # We select automatically the style that now has the position of the
        # one we just removed
        newIndex = index if index < len(self.styles) else index - 1
        if newIndex >= 0:
            self.styleCheckList.SetSelection(newIndex)
            self.styleControl.setEditable(self.styles[newIndex])
        else: # disable style editor
            self.styleControl.setEditable(None)
        # we should update the buttons
        self.updateButtons()
        # now we update the style sheet
        self.updateStyleSheet(event)
        
    # move the selected element up when the "move up" button is clicked
    def moveStyleUp(self, event):
        # first we update the listbox...
        index = self.styleCheckList.GetSelection()
        checked = self.styleCheckList.GetCheckedStrings()
        value = self.styleCheckList.GetString(index)
        self.styleCheckList.Delete(index)
        self.styleCheckList.Insert(value, index-1)
        self.styleCheckList.Select(index-1)
        self.styleCheckList.SetCheckedStrings(checked)
        # now we update the style sheet
        self.styles[index-1], self.styles[index] =\
            self.styles[index], self.styles[index-1]
        self.updateStyleSheet(event)
        # the buttons should also be updated
        self.updateButtons()
        
    # move the selected element down when the "move down" button is clicked
    def moveStyleDown(self, event):
        # first we update the listbox...
        index = self.styleCheckList.GetSelection()
        checked = self.styleCheckList.GetCheckedStrings()
        value = self.styleCheckList.GetString(index)
        self.styleCheckList.Delete(index)
        self.styleCheckList.Insert(value, index+1)
        self.styleCheckList.Select(index+1)
        self.styleCheckList.SetCheckedStrings(checked)
        # now we update the style sheet
        self.styles[index+1], self.styles[index] =\
            self.styles[index], self.styles[index+1]
        self.updateStyleSheet(event)
        # the buttons should also be updated
        self.updateButtons()

    # add a style interactively: let the user choose which style to add
    def addStyleInteractively(self, event):
        # create the styleChooser attribute if it doesn't exist, otherwise use
        # the existing one
        try:
            self.styleChooser
        except AttributeError:
            self.styleChooser = AddStyleDialog(self)
        returnValue = self.styleChooser.ShowModal()
        # in case 'Ok' was clicked, we add the selected styles from the tree
        if returnValue == wx.ID_OK:
            # save the current status of checkboxlist
            currentlyActive = list(self.styleCheckList.GetCheckedStrings())
            for item in self.styleChooser.tree.GetSelections():
                # we skip selected items which are not styles
                if self.styleChooser.tree.ItemHasChildren(item): continue
                className = self.styleChooser.tree.GetItemText(item)
                className = className[:className.find(':')]
                parent = self.styleChooser.tree.GetItemParent(item)
                moduleName = self.styleChooser.tree.GetItemText(parent)
                
#                 exec 'import ' + moduleName
#                 thisStyle = eval(moduleName + '.' + className + '()')
                mod = __import__(moduleName)
                thisStyle = mod.__getattribute__(className)()
                
                # only insert the style if it's valid for this problem/solution
                try:
                    # first we test if this style can be applied (if not then an
                    # exception is raised)
                    instance = self.GrandParent.Parent.browserPanel.\
                        solutionBook.GetCurrentPage().inputData
                    solution = self.GrandParent.Parent.browserPanel.\
                        solutionBook.GetCurrentPage().solutionData
                    thisStyle.preProcessAttributes(instance, solution)
                    # arbitrary behaviour: insert on top of the style sheet
                    self.styles.insert(0, thisStyle)
                    currentlyActive.append(thisStyle.description)
                    # we add in the checkbox list the newly added style
                    self.styleCheckList.Insert(thisStyle.description, 0)
                except MissingAttributeException as e:
                    dialog = wx.MessageDialog(self,
                                              str(e),
                                              'Can\'t add style: ' +\
                                                  thisStyle.description,
                                              wx.OK | wx.ICON_ERROR)
                    dialog.ShowModal()
                    dialog.Destroy()
            # we also restore the selection in the list + new styles
            self.styleCheckList.SetCheckedStrings(currentlyActive)
            # finally, we must update our stylesheet
            self.updateStyleSheet(event)
            # and we select automatically the newer style
            self.styleCheckList.Select(0)
            self.styleControl.setEditable(self.styles[0])
            # the buttons should also be updated
            self.updateButtons()
        # in any case, empty the selection in the tree
        self.styleChooser.tree.UnselectAll()
