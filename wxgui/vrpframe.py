#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: August 3rd 2011 by Fabien Tricoire
#
import os
import sys

import wx
from wx.lib.wordwrap import wordwrap

# for version numbers for the 'about' dialog
try:
    import Image
except Exception as e:
    try:
        # is pillow installed?
        from PIL import Image
    except Exception as ee:
        pass
    
try:
    import reportlab
except Exception as e:
    pass

import stylesheet
import events
from vrpexceptions import MissingAttributeException
import vrpdata
import util

import vrpgui
from sscontrols import StyleSheetControls, ssControlWidth, ssControlHeight
from solutionbrowser import SolutionBrowser, nodeInfoWidth
import guiconfig

class VrpFrame(wx.Frame):
    def __init__(self, parent, vrpData, solutions, styleSheet, layout=None,
                 selectedSolution=None):
        wx.Frame.__init__(self, parent, wx.ID_ANY,
                          title='VRP Visualization tool')
        # style sheet for this window
        self.styleSheet = styleSheet
        # input data information for this frame
        self.vrpData = vrpData
        self.solutions = solutions if solutions \
            else [ vrpdata.VrpEmptySolution('', vrpData) ]
        # split the main window: left is for stylesheet control,
        # right is for displaying the VRP data
        self.mainSplitter= wx.SplitterWindow(self,
                                             -1,
                                             style=wx.SP_LIVE_UPDATE | wx.SP_3D)
        # left panel: style sheet control
        self.styleSheetPanel = StyleSheetControls(self.mainSplitter,
                                                  self.styleSheet)
        # sub-section for the right part
        # solution browser panel
        self.browserPanel = SolutionBrowser(self.mainSplitter,
                                            vrpData,
                                            self.solutions,
                                            self.styleSheet)
        if selectedSolution:
            self.browserPanel.solutionBook.SetSelection(selectedSolution)
        # main splitter initialization
        self.mainSplitter.SetMinimumPaneSize(50)
        self.mainSplitter.SplitVertically(self.styleSheetPanel,
                                          self.browserPanel)
        # in case the stylesheet is modified: live update
        self.styleSheetPanel.Bind(wx.EVT_CHECKBOX, self.styleSheetUpdate)
        self.styleSheetPanel.Bind(wx.EVT_CHECKLISTBOX, self.styleSheetUpdate)
        self.styleSheetPanel.Bind(wx.EVT_BUTTON, self.styleSheetUpdate)
        # in case the stylesheet has been updated: repaint
        self.Bind(events.EVT_STYLESHEET_UPDATE, self.styleSheetUpdate)
        # in case the window is maximized
        self.Bind(wx.EVT_SIZE, self.sizeHandler)
        # when the user wants to delete a solution
        self.Bind(events.EVT_DELETE_SOLUTION, self.onDelete)
        # initialize frame starting layout and size
        if layout is None:
            self.useFactoryLayout(vrpData)
        else:
            self.setLayout(layout)
        # set the frame title
        self.SetTitle('Instance: ' + vrpData.name)
        # we also want menus
        self.populateMenuBar()
        # show the frame!
        self.Show()
        # register it to the app
        events.postRegisterFrameEvent(self)

    def sizeHandler(self, event):
        # if the window is not maximized, save its size
        if not self.IsMaximized():
            self.unMaximisedSize = self.GetSize()
            self.unMaximisedPosition = self.GetPosition()
        event.Skip()
        
    # set the starting layout based on existing configuration
    def setLayout(self, layout):
        try:
            self.SetSize(layout['gui dimensions'])
            self.SetPosition(layout['gui position'])
            self.mainSplitter.SetSashPosition(layout['style control width'])
            self.browserPanel.splitter.SetSashPosition(\
                layout['node info width'])
            self.browserPanel.splitter.SetSashGravity(1)
            for i, w in enumerate(layout['node info columns']):
                self.browserPanel.nodeInfoList.SetColumnWidth(i, w)
            self.unMaximisedSize = layout['unmaximised size']
            self.unMaximisedPosition = layout['unmaximised position']
            # if the window appears maximised, tell the OS its normal size
            if self.IsMaximized():
                self.SetPosition(layout['unmaximised position'])
                self.SetSize(layout['unmaximised size'])
                self.Maximize()
        except Exception as e:
            print e

    # populate menu bar
    def populateMenuBar(self):
        # Menu bar
        menuBar = wx.MenuBar()
        # file menu
        fileMenu = wx.Menu()
        # about dialog
        fileMenu.Append(101, 'About wxproute...')
        self.Bind(wx.EVT_MENU, lambda e: self.aboutDialog(), id=101)
        # edit user preferences
        shortcut = 'Ctrl+,' if sys.platform == 'darwin' else 'Ctrl+P'
        fileMenu.Append(105, 'Preferences\t'+shortcut)
        self.Bind(wx.EVT_MENU,
                  lambda e: events.postPreferencesEvent(self), id=105)
        fileMenu.AppendSeparator()
        # open new data in new window
        fileMenu.Append(102, 'Open new data\tCtrl+O')
        self.Bind(wx.EVT_MENU, self.loadData, id=102)
        # re-open same data in new window
        fileMenu.Append(103, 'Re-open same data\tAlt+Ctrl+O')
        self.Bind(wx.EVT_MENU, self.loadData, id=103)
        # open more data in this window
        fileMenu.Append(104,
                        'Add data to this window\tShift+Ctrl+O')
        self.Bind(wx.EVT_MENU, self.addData, id=104)
        fileMenu.AppendSeparator()
        # save as pdf...
        fileMenu.Append(110, 'Export solution to PDF\tCtrl+E')
        self.Bind(wx.EVT_MENU, self.exportToPDF, id=110)
        fileMenu.Append(111, 'Export all solutions to PDF\tShift+Ctrl+E')
        self.Bind(wx.EVT_MENU, self.exportToPDF, id=111)
        fileMenu.AppendSeparator()
        # close this frame
        fileMenu.Append(106, 'Close\tCtrl+W')
        self.Bind(wx.EVT_MENU, self.closingHandler, id=106)
        self.Bind(wx.EVT_CLOSE, lambda e: self.closeFrame())
        # in case the user quits: propagate it to the App instance
        fileMenu.Append(107, 'Quit\tCtrl+Q')
        self.Bind(wx.EVT_MENU, lambda e: events.postQuitEvent(self), id=107)
        # File menu
        menuBar.Append(fileMenu, 'File')
        # stylesheet menu
        styleSheetMenu = wx.Menu()
        styleSheetMenu.Append(201, 'Save\tCtrl+S')
        self.Bind(wx.EVT_MENU, self.saveStyleSheet, id=201)
        styleSheetMenu.Append(202, 'Load\tCtrl+L')
        self.Bind(wx.EVT_MENU, self.loadStyleSheet, id=202)
        styleSheetMenu.Append(203, 'Grid controls\tCtrl+G')
        self.Bind(wx.EVT_MENU, self.popGridControls, id=203)
        menuBar.Append(styleSheetMenu, 'Stylesheet')
        # layout menu
        layoutMenu = wx.Menu()
        layoutMenu.Append(301, 'Save\tShift+Ctrl+S')
        self.Bind(wx.EVT_MENU, self.saveLayout, id=301)
        layoutMenu.Append(302, 'Save as favourite\tAlt+Shift+Ctrl+S')
        self.Bind(wx.EVT_MENU, self.saveLayout, id=302)
        layoutMenu.Append(303, 'Load\tShift+Ctrl+L')
        self.Bind(wx.EVT_MENU, self.loadLayout, id=303)
        layoutMenu.Append(304, 'Restore favourite\tAlt+Shift+Ctrl+L')
        self.Bind(wx.EVT_MENU, self.loadLayout, id=304)
        menuBar.Append(layoutMenu, 'Layout')
        # session menu
        sessionMenu = wx.Menu()
        sessionMenu.Append(401, 'Save\tAlt+Ctrl+S')
        self.Bind(wx.EVT_MENU,
                  lambda e: events.postSaveSessionEvent(self),
                  id=401)
        sessionMenu.Append(402, 'Load\tAlt+Ctrl+L')
        self.Bind(wx.EVT_MENU,
                  lambda e: events.postLoadSessionEvent(self),
                  id=402)
        menuBar.Append(sessionMenu, 'Session')
        # set the menu bar!@#
        self.SetMenuBar(menuBar)
        
        
    # get the current layout
    def getLayout(self):
        return {
            'gui dimensions': self.GetSize(),
            'gui position': self.GetPosition(),
            'style control width': self.mainSplitter.GetSashPosition(),
            'node info width': self.browserPanel.splitter.GetSashPosition(),
            'node info columns': \
                [ self.browserPanel.nodeInfoList.GetColumnWidth(i)
                  for i in \
                      range(self.browserPanel.nodeInfoList.GetColumnCount())
                  ],
            'unmaximised size': self.unMaximisedSize,
            'unmaximised position': self.unMaximisedPosition,
            }
    
    # set a good starting size for the frame
    def useFactoryLayout(self, myVrp):
        self.SetSize(wx.DisplaySize())
        self.SendSizeEvent()
        self.Refresh()
        self.mainSplitter.SetSashPosition(ssControlWidth+10)
        self.browserPanel.splitter.SetSashPosition(-nodeInfoWidth)
        self.browserPanel.splitter.SetSashGravity(1)
        wp, hp = \
            self.browserPanel.solutionBook.GetCurrentPage().GetClientSize()
        wf, hf = self.GetSize()
        newDimensions = (wf - wp + myVrp.width + 2*stylesheet.padding,
                         hf - hp + myVrp.height * (1.0/myVrp.heightOverWidth) +
                         2*stylesheet.padding)
        self.SetSize(newDimensions)
        self.CentreOnScreen()

    # called when the style sheet is modified
    def styleSheetUpdate(self, event):
        if event.__class__.__name__ == 'StyleSheetUpdateEvent':
            self.browserPanel.solutionBook.GetCurrentPage().rePaint()

    # save a styleSheet
    def saveStyleSheet(self, event):
        import stylesheetIO
        dialog = stylesheetIO.SaveStyleSheetDialog(self)
        returnValue = dialog.ShowModal()
        # in case 'Ok' was clicked, we load the selected stylesheet
        if returnValue == wx.ID_OK:
            name = str(dialog.sheetName.GetValue())
            defaultFor = [ str(x)
                           for x in dialog.problemList.GetCheckedStrings() ]
            self.browserPanel.solutionBook.GetCurrentPage().styleSheet.export(\
                name, defaultFor)
            for instanceType in defaultFor:
                # store as default sheet for this type for this session
                pass
                
    # load a stylesheet
    def loadStyleSheet(self, event):
        import stylesheetIO
        chooser = stylesheetIO.LoadStyleSheetDialog(self)
        returnValue = chooser.ShowModal()
        # in case 'Ok' was clicked, we load the selected stylesheet
        if returnValue == wx.ID_OK:
            item = chooser.tree.GetSelection()
            newSheetName = chooser.tree.GetItemText(item)
            parent = chooser.tree.GetItemParent(item)
            moduleName = chooser.tree.GetItemText(parent)
            mod = __import__(moduleName)
            newSheet = mod.__getattribute__(newSheetName)()
            # first we test if the styles in this stylesheet can be applied
            # (irrelevant syles are filtered out)
            newStyles = []
            instance = self.browserPanel.solutionBook.GetCurrentPage().inputData
            solution = self.browserPanel.\
                solutionBook.GetCurrentPage().solutionData
            for style in newSheet.styles:
                try:
                    style.preProcessAttributes(instance, solution)
                    newStyles.append(style)
                except MissingAttributeException as e:
                    dialog = wx.MessageDialog(self,
                                              str(e),
                                              'Can\'t use style: ' +\
                                                  style.description,
                                              wx.OK | wx.ICON_ERROR)
                    dialog.ShowModal()
                    # and we can get rid of the dialog
                    dialog.Destroy()
            # now we replace the list of styles by the filtered version
            newSheet.styles = newStyles
            # replace it in the sscontrols
            self.styleSheetPanel.newStyleSheet(newSheet)
            # replace it in the solution browser too
            self.browserPanel.solutionBook.loadStyleSheet(newSheet)
            # update style sheet
            self.browserPanel.solutionBook.GetCurrentPage().rePaint()
            # the buttons should also be updated
#             self.updateButtons()
        # in any case, empty the selection in the tree
        chooser.Destroy()

    def saveLayout(self, event):
        if event.GetId() == 301:
            wildcard='Layout files (*.layout)|*.layout'
            fileSelector = wx.FileDialog(self,
                                         message="Save layout",
                                         defaultDir=guiconfig.guiConfigDir,
                                         style=wx.FD_SAVE,
                                         wildcard=wildcard)
            if fileSelector.ShowModal() == wx.ID_OK:
                files = fileSelector.GetPaths()
                fName = str(files[0])
                guiconfig.saveLayout(self.getLayout(), fName)
            fileSelector.Destroy()
        elif event.GetId() == 302:
            guiconfig.saveAsFavouriteLayout(self.getLayout())
        
    def loadLayout(self, event):
        if event.GetId() == 303:
            wildcard='Layout files (*.layout)|*.layout'
            fileSelector = wx.FileDialog(self,
                                         message="Save layout",
                                         defaultDir=guiconfig.guiConfigDir,
                                         style=wx.FD_OPEN,
                                         wildcard=wildcard)
            if fileSelector.ShowModal() == wx.ID_OK:
                files = fileSelector.GetPaths()
                fName = str(files[0])
                self.setLayout(guiconfig.loadLayout(fName))
            fileSelector.Destroy()
        elif event.GetId() == 304:
            self.setLayout(guiconfig.loadFavouriteLayout())

    # load vrp and solutions data
    def loadData(self, event):
        # new data in new window
        if event.GetId() == 102:
            myVrp, mySolutions, myStyleSheet = (None, None, None)
        # same data in new window
        elif event.GetId() == 103:
            mySolutions = self.solutions
            myVrp = self.vrpData
            import copy
            myStyleSheet = copy.deepcopy(self.styleSheet)
        # tell the VrpApp to open the data
        events.postLoadDataEvent(self, myVrp, mySolutions, myStyleSheet,
                                 self.GetPosition())

    # add more solutions in this window
    def addData(self, event):
        solutionType = self.solutions[0].solutionType \
            if len(self.solutions) > 0 else None
        vrpData, solutionData, styleSheet = \
            vrpgui.loadDataInteractively(problemType=self.vrpData.problemType,
                                         instanceType=self.vrpData.instanceType,
                                         instanceFileName=self.vrpData.fName,
                                         solutionType=solutionType)
        if vrpData and solutionData:
            self.browserPanel.addSolutions(vrpData, solutionData)
            self.solutions += solutionData

    # delete the currently selected solution
    def onDelete(self, event):
        index = self.browserPanel.solutionBook.GetSelection()
        del self.solutions[index]
        self.browserPanel.solutionBook.removeSolution()
        if len(self.solutions) > 0:
            self.browserPanel.solutionBook.GetCurrentPage().SetFocus()
            
    # pop grid controls frame
    def popGridControls(self, event):
        try:
            self.gridManager.Destroy()
        except AttributeError:
            import gridmanagement
            self.gridManager = \
                gridmanagement.GridManager(self, self.styleSheet,
                                           self.browserPanel.solutionBook.\
                                               GetCurrentPage().solutionData)

    # called when keyboard shortcut or menu is used to close the window
    def closingHandler(self, event):
        if self.IsActive():
            self.closeFrame()
            
    # close this frame
    def closeFrame(self):
        events.postUnregisterFrameEvent(self)
        self.Destroy()

    # about dialog
    def aboutDialog(self):
        about = wx.AboutDialogInfo()
        about.Name = 'wxproute'
        about.Version = guiconfig.version()
        about.Copyright = '(C) Fabien Tricoire 2010-2011'
        description = '\nproute engine version ' + util.version()
        description += '\n\nwxPython version ' + wx.version()
        try:
            description += '\n\nReportLab version ' + reportlab.Version
        except Exception as e:
            description += '\n\nReportLab not installed'
        try:
            description += '\n\nPython Imaging Library (PIL) version ' + \
                Image.VERSION
        except Exception as e:
            description += '\n\nPython Imaging Library (PIL) not installed'
        about.Description = wordwrap(description, 500, wx.ClientDC(self))
        about.WebSite = ('http://proute.berlios.de/', 'proute home page')
        about.Developers = [ 'Fabien Tricoire' ]
        licenseText = ''
        about.License = wordwrap(licenseText, 500, wx.ClientDC(self))
        #
        wx.AboutBox(about)

    # export solution to pdf
    def exportToPDF(self, event):
        # save only active solution
        if event.GetId() == 110:
            # select a pdf file to save...
            wildcard='PDF files (*.pdf)|*.PDF'
            fileSelector = wx.FileDialog(self,
                                         message="Export to PDF",
                                         style=wx.FD_SAVE,
                                         wildcard=wildcard)
            if fileSelector.ShowModal() == wx.ID_OK:
                files = fileSelector.GetPaths()
                fName = str(files[0])
                baseName, extension = os.path.splitext(fName)
                if extension.lower() != 'pdf':
                    fName += '.pdf'
                self.browserPanel.solutionBook.GetCurrentPage().\
                    exportToPDF(fName)
            fileSelector.Destroy()
        else: # save each solution
            # select a directory
            dirSelector = wx.DirDialog(self,
                                       message="Export to directory",
                                       style=wx.DD_DEFAULT_STYLE)
            if dirSelector.ShowModal() == wx.ID_OK:
                dir = dirSelector.GetPath()
                for i in range(self.browserPanel.solutionBook.GetPageCount()):
                    self.browserPanel.solutionBook.GetPage(i).exportToPDF(\
                        dirName=dir)
            dirSelector.Destroy()
