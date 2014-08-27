#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: July 30th 2011 by Fabien Tricoire
#
import os
import sys

import wx

import vrpframe
import gridview
import stylesheet
import events
import prefsdialog
# from vrpexceptions import MissingAttributeException

# from sscontrols import StyleSheetControls, ssControlWidth, ssControlHeight
# from solutionbrowser import SolutionBrowser, nodeInfoWidth
# from gridview import GridViewer
import guiconfig

class VrpGui(wx.App):
    def __init__(self, myVrp, mySolutions, myStyleSheet,
                 redirect=False, filename=None):
        wx.App.__init__(self, redirect, filename)
        # initialize gui config
        guiconfig.initializeConfig()
        # load the favourite layout if there exists one
        layout = guiconfig.loadFavouriteLayout()
        # list of all open frames (useful for saving layout)
        self.openFrames = []
        # all events that can reach this object
        self.Bind(events.EVT_QUIT, lambda(e): self.quitApp())
        self.Bind(events.EVT_SAVE_SESSION, lambda e: self.saveSession())
        self.Bind(events.EVT_LOAD_SESSION, lambda e: self.loadSession())
        self.Bind(events.EVT_LOAD_DATA, self.loadDataEventHandler)
        self.Bind(events.EVT_REGISTER_FRAME, self.registerFrame)
        self.Bind(events.EVT_UNREGISTER_FRAME, self.unregisterFrame)
        self.Bind(events.EVT_PREFERENCES, setPreferences)
        # if a previous session must be restored, restore it
        if myVrp is None and os.path.exists(guiconfig.lastSessionFileName):
            try:
                self.loadSession(guiconfig.lastSessionFileName)
                # if for some reason (e.g. tampered or incorrect session file)
                # loading the session did not lead to opening windows, consider
                # it a failure
                if len(self.openFrames) > 0:
                    return
            except Exception as e:
                print 'Unable to load session:', \
                    guiconfig.lastSessionFileName
                print e #, dir(e)
        self.loadData(myVrp, mySolutions, myStyleSheet)
        
        
#         self.gridView = gridview.GridViewer(myVrp, mySolutions[0],
#                                             'index', 'Route # ',
# #                                    'vehicle', 'Routes of vehicle',
# #                                    'day', 'Routes on day',
#                                             styleSheet = myStyleSheet)       

    # load data event handler (event comes form VrpFrame)
    def loadDataEventHandler(self, event):
        myVrp = event.vrpData
        mySolutions = event.solutionData
        myStyleSheet = event.styleSheet
        x, y = event.position
        self.loadData(myVrp, mySolutions, myStyleSheet, (x+50, y+50) )

    # load data in this gui (i.e. a open new frame)
    # position on screen is used if specified
    def loadData(self, myVrp, mySolutions, myStyleSheet, position=None):
        if myVrp is None:
            myVrp, mySolutions, myStyleSheet = loadDataInteractively()
        # TODO: check that modifying the stylesheet won't modify styles on
        # other already open frames
        # HINT: it will, a deep copy must be performed
        # open the data in a new frame
        if not myVrp is None:
            # load the favourite layout if there exists one
            layout = guiconfig.loadFavouriteLayout()
            # open the data in a new window
            frame = vrpframe.VrpFrame(None,
                                      myVrp, mySolutions, myStyleSheet, layout)
            if not position is None:
                frame.SetPosition(position)
        else:
            # case where nothing is opened
            # in case there is no open window: exit appplication
            if self.openFrames == []:
                self.quitApp()

    # quit the app! here's the place to perform various checks and
    # postprocessing e.g. save layout or session
    def quitApp(self):
        # save preferences
        guiconfig.savePreferences()
        # save favourite layout if required
        if guiconfig.preferences['save layout']:
            # find the frame which currently has the focus
            activeFrames = [ x for x in self.openFrames if x.IsActive() ]
            if activeFrames:
                guiconfig.saveAsFavouriteLayout(activeFrames[0].getLayout())
        # save favourite session if required
        if guiconfig.preferences['save session']:
            self.saveSession(guiconfig.lastSessionFileName)
        # /!\ do not save the session if no frame is open
        # this can happen if the user cancels the program from the start
        # saving the session and automatically loading it at program startup
        # would result in the program exiting immediately
        self.Exit()
        sys.exit(0)

    # save the session
    def saveSession(self, fName=None):
        if not self.openFrames: return
        if fName is None:
            wildcard='Session files (*.session)|*.session'
            fileSelector = wx.FileDialog(None,
                                         message="Save session",
                                         defaultDir=guiconfig.guiConfigDir,
                                         style=wx.FD_SAVE,
                                         wildcard=wildcard)
            if fileSelector.ShowModal() == wx.ID_OK:
                files = fileSelector.GetPaths()
                fName = str(files[0])
            fileSelector.Destroy()
        if not fName is None:
            # add a suffix
            if not fName[-8:] == '.session':
                fName += '.session'
            f = open(fName, 'w')
            for frame in self.openFrames:
                # first we build the list of all required modules for this frame
                modules = [ frame.vrpData.__module__,
                            frame.styleSheet.__module__ ]
                for s in frame.solutions:
                    modules.append(s.__module__)
                for s in frame.styleSheet.styles:
                    modules.append(s.__module__)
                modules = set(modules)
                # now we can write the import statement
                f.write('import style, stylesheet, ' + \
                            reduce(lambda x, y: str(x) + ', ' + str(y),
                                   list(modules)) + '\n')
                f.write('myData = ' + str(frame.vrpData) + '\n')
                f.write('mySolutions = ' + str(frame.solutions) + '\n')
                f.write('myStyleSheet = ' + str(frame.styleSheet) + '\n')
                f.write('myLayout = ' + str(frame.getLayout()) + '\n')
                f.write('mySelectedSolution = ' + \
                            str(frame.browserPanel.solutionBook.GetSelection())\
                            + '\n')
                f.write('vrpframe.VrpFrame(None, myData, mySolutions,' + \
                            'myStyleSheet, myLayout,' + \
                            'selectedSolution=mySelectedSolution)' + '\n')

            f.close()
            print 'Stored session to', fName

    # load the session
    def loadSession(self, fileName=None):
        # if no file name is specified, ask the user
        if fileName is None:
            wildcard='Session files (*.session)|*.session'
            fileSelector = wx.FileDialog(None,
                                         message="Load session",
                                         defaultDir=guiconfig.guiConfigDir,
                                         style=wx.FD_OPEN,
                                         wildcard=wildcard)
            if fileSelector.ShowModal() == wx.ID_OK:
                files = fileSelector.GetPaths()
                fileName = str(files[0])
            fileSelector.Destroy()
        if not fileName is None:
            # save the frames previously opened for later deletion
            oldFrames = [ x for x in self.openFrames ]
#         fileName = 'saved.session'
            f = open(fileName, 'r')
            lines = f.readlines()
            for i, line in enumerate(lines):
                try:
                    exec(line)
                except Exception as e:
                    print 'problem while loading session with line', line
                    print e
#                 self.quitApp()
#             # case where we read everything we need for this frame
#                 if line[:18] == 'mySelectedSolution':
# #             if i % 6 == 5:
#                     vrpframe.VrpFrame(None, myData, mySolutions,
#                                       myStyleSheet, myLayout,
#                                       selectedSolution=mySelectedSolution)
#                     myData, mySolutions, myStyleSheet, myLayout = [None] * 4
            f.close()
            # clear already opened frames
            for frame in oldFrames:
                frame.closeFrame()
            print 'Loaded session from', fileName

    # register a new frame
    def registerFrame(self, event):
        self.openFrames.append(event.GetEventObject())
        
    # unregister a frame
    def unregisterFrame(self, event):
        self.openFrames.remove(event.GetEventObject())
        # if this was the last frame, exit application
        if not self.openFrames:
            self.quitApp()
        
# set user preferences
def setPreferences(event):
    dialog = prefsdialog.PreferencesDialog(None)
    returnValue = dialog.ShowModal()
    if returnValue == wx.ID_OK:
        guiconfig.preferences['save layout'] = dialog.layoutCheckBox.GetValue()
        guiconfig.preferences['save session']= dialog.sessionCheckBox.GetValue()
        
# load data interactively
def loadDataInteractively(problemType=None,
                          instanceType=None,
                          instanceFileName=None,
                          solutionType=None,
                          solutionFileNames=None):
    import loadfiles
    import loaddata
    fileLoader = loadfiles.LoadDataDialog(None,
                                          problemType,
                                          instanceType,
                                          instanceFileName,
                                          solutionType,
                                          solutionFileNames)
    while True:
        returnValue = fileLoader.ShowModal()
        if returnValue == wx.ID_OK:
            type = fileLoader.typeChoice.GetStringSelection()
            instanceType = fileLoader.instanceTypeChoice.GetStringSelection()
            solutionType = fileLoader.solutionTypeChoice.GetStringSelection()
            loader = loaddata.DataLoader()
            fName = fileLoader.instanceNameField.GetValue()
            try:
                myVrp = loader.loadInstance(fName,
                                            type,
                                            instanceType)
                solutionFNames = \
                    eval(fileLoader.solutionsNameField.GetValue()) \
                    if fileLoader.solutionsNameField.GetValue() else []
                mySolutions = [ loader.loadSolution(fName,
                                                    myVrp,
                                                    type,
                                                    solutionType)
                                for fName in solutionFNames ]
                myStyleSheet = loader.loadStyleSheet(type)
                fileLoader.Destroy()
                return myVrp, mySolutions, myStyleSheet
            except Exception as ex:
                dialog = wx.MessageDialog(None,
                                          'Error while loading data: ' +str(ex),
                                          'Unable to load data!@#',
                                          wx.OK | wx.ICON_ERROR)
                dialog.ShowModal()
                dialog.Destroy()
        else:
            return None, None, None
