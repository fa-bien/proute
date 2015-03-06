#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: March 6th 2015 by Fabien Tricoire
#
import os

import wx

import util
import style
import loaddata

# this class pops a window in order to choose one or several styles
class LoadDataDialog(wx.Dialog):
    def __init__(self, parent,
                 problemType=None,
                 instanceType=None,
                 instanceFileName=None,
                 solutionType=None,
                 solutionFileNames=None):
        wx.Dialog.__init__(self, parent, -1,
                           title='Choose an instance and solutions!')
        # we need this object to find out what we can load
        self.loader = loaddata.DataLoader()
        availableTypes = self.loader.getAvailableTypes()
        # layout for this dialog
        mainSizer = wx.GridSizer(0, 2, 10, 10)
        # first line: problem type
        label = wx.StaticText(self, -1, 'Problem type:')
        self.typeChoice = wx.Choice(self, -1,
                                    choices=availableTypes,
#                                     size=(150, 25)
                                    )
        mainSizer.Add(label, 0,
                      wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        mainSizer.Add(self.typeChoice, 0,
                      wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        # second line: instance type
        label = wx.StaticText(self, -1, 'Instance type:')
        self.instanceTypeChoice = wx.Choice(self, -1)#, size=(150, 25))
        mainSizer.Add(label, 0,
                      wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        mainSizer.Add(self.instanceTypeChoice, 0,
                      wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        # third line: load an instance
        self.instanceFileButton = wx.Button(self, -1, 'Select instance')
        mainSizer.Add(self.instanceFileButton, 0,
                      wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.onInstanceButton, self.instanceFileButton)
        self.instanceNameField = wx.TextCtrl(self, size=(200,-1))
        mainSizer.Add(self.instanceNameField, 0,
                      wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        # fourth line: solution subtype
        label = wx.StaticText(self, -1, 'Solution type:')
        self.solutionTypeChoice = wx.Choice(self, -1) #, size=(150, 25))
        mainSizer.Add(label, 0,
                      wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        mainSizer.Add(self.solutionTypeChoice, 0,
                      wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        # fifth line: load a solution
        solutionFilesButton = wx.Button(self, -1, 'Select solutions')
        mainSizer.Add(solutionFilesButton, 0,
                      wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.onSolutionButton, solutionFilesButton)
        self.solutionsNameField = wx.TextCtrl(self, size=(200,-1))
        mainSizer.Add(self.solutionsNameField, 0,
                      wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        # set default problem type if specified
        if problemType:
            self.typeChoice.SetSelection(availableTypes.index(problemType))
            self.typeChoice.Disable()
        # update choice lists
        self.updateChoice()
        # files we want to load
        self.instanceFile = None
        self.solutionFiles = []
        # set default selections if specified
        if problemType and instanceType:
            availableInstanceTypes = \
                self.loader.getAvailableInstanceTypes(problemType)
            self.instanceTypeChoice.SetSelection( \
                availableInstanceTypes.index(instanceType))
            self.instanceTypeChoice.Disable()
        if instanceFileName:
            self.instanceNameField.SetValue(instanceFileName)
            self.instanceNameField.Disable()
            self.instanceFileButton.Disable()
        if problemType and solutionType:
            availableSolutionTypes = \
                self.loader.getAvailableSolutionTypes(problemType)
            self.solutionTypeChoice.SetSelection( \
                availableSolutionTypes.index(solutionType))
        if solutionFileNames:
            self.solutionsNameField.SetValue(solutionFileNames)
        
        # add standard dialog buttons
        self.okButton = wx.Button(self, wx.ID_OK)
        self.okButton.Disable()
        cancelButton = wx.Button(self, wx.ID_CANCEL)
        mainSizer.Add(self.okButton, 0, wx.ALIGN_RIGHT|wx.ALL, 5)
#         mainSizer.Add((20,0), 1)
        mainSizer.Add(cancelButton, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        # now we're ready
        self.SetSizer(mainSizer)
#         self.SetSize((400,500))
        mainSizer.Fit(self)
        self.CenterOnScreen()

        # update instance and solution type choice when appropriate
        self.Bind(wx.EVT_CHOICE , self.onTypeChoice, self.typeChoice)
        
    def onTypeChoice(self, event):
        self.updateChoice()

    def updateChoice(self):
#         loader = loaddata.DataLoader()
        type = self.typeChoice.GetStringSelection()
        availableInstanceTypes = self.loader.getAvailableInstanceTypes(type)
        self.instanceTypeChoice.SetItems(availableInstanceTypes)
        self.instanceTypeChoice.SetSelection(0)
        availableSolutionTypes = self.loader.getAvailableSolutionTypes(type)
        self.solutionTypeChoice.SetItems(availableSolutionTypes)
        self.solutionTypeChoice.SetSelection(0)

    def onInstanceButton(self, event):
        fileSelector = wx.FileDialog(self,
                                     message="Choose an instance file",
#                                      defaultDir=os.getcwd(),
                                     style=wx.OPEN | wx.CHANGE_DIR )
        if fileSelector.ShowModal() == wx.ID_OK:
            files = fileSelector.GetPaths()
            self.instanceNameField.SetValue(str(files[0]))
        fileSelector.Destroy()
        self.okButton.Enable()

    def onSolutionButton(self, event):
        fileSelector = wx.FileDialog(self,
                                     message="Choose solution files",
#                                      defaultDir=os.getcwd(),
                                     style=wx.OPEN | wx.CHANGE_DIR |wx.MULTIPLE)
        if fileSelector.ShowModal() == wx.ID_OK:
            files = fileSelector.GetPaths()
            self.solutionsNameField.SetValue(str([ str(x) for x in files ]))
        fileSelector.Destroy()
        if self.instanceNameField.GetValue():
            self.okButton.Enable()
