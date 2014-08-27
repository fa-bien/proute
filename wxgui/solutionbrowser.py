#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: September 27th 2011 by Fabien Tricoire
#
import sys

import wx
import wx.grid

import vrpdata
import wxcanvas
from vrppanel import VrpPanel
import style
import events

nodeAttributeColWidth = 120
nodeValueColWidth = 90
nodeInfoWidth = nodeAttributeColWidth + nodeValueColWidth + 3

# This class allows to browse solutions. Solutions are displayed in a listbook
# (one page contains one solution), and a NodeInputInformationList displays
# on-the-fly information on nodes where the mouse hovers
class SolutionBrowser(wx.Panel):
    def __init__(self, parent, vrpData, solutions, styleSheet):
        wx.Panel.__init__(self, parent, -1, style=wx.BORDER_SUNKEN)
        self.styleSheet = styleSheet
        # main sizer
        browserSizer = wx.BoxSizer(wx.VERTICAL)
        # text label for the solution browser panel
        browserSizer.Add(wx.StaticText(self, label='Solution browser'),
                         proportion=0,
                         flag=wx.ALIGN_CENTER | wx.ALL,
                         border=3)

        # splitter for the solution book on the left side and the node
        # information on the right side
        # split the main window: left is for stylesheet control,
        # right is for displaying the VRP data
        self.splitter = wx.SplitterWindow(self,
                                          -1,
                                          style=wx.SP_LIVE_UPDATE|wx.SP_3DSASH)

        # left: solution book
        self.solutionBook = SolutionListBook(self.splitter, -1)
#         # right: node information
        self.nodeInfoList = NodeInputInformationList(self.splitter,
                                                     -1,
                                                     vrpData,
                                                     solutions[0])
        # add solutions...
        self.solutionBook.addSolutions(vrpData, solutions,
                                       self.styleSheet, self.nodeInfoList)
        # main splitter initialization
        self.splitter.SplitVertically(self.solutionBook,
                                      self.nodeInfoList,
                                      -nodeInfoWidth)
        self.splitter.SetMinimumPaneSize(100)
        # add visualization/selection
        browserSizer.Add(self.splitter, 1, wx.EXPAND)
        # assign the correct sizer
        self.SetSizer(browserSizer)
        self.splitter.SetSashGravity(1)

    # add more solutions to this browser
    def addSolutions(self, vrp, solutions):
        self.solutionBook.addSolutions(vrp, solutions,
                                       self.styleSheet, self.nodeInfoList)
        
class SolutionListBook(wx.Listbook):
    def __init__(self, parent, id ):
        wx.Listbook.__init__(self, parent, id,
                             style=wx.BK_RIGHT|wx.BORDER_SUNKEN)
        self.thumbnailWidth, self.thumbnailHeight = 64, 48
        self.AssignImageList(wx.ImageList(self.thumbnailWidth,
                                          self.thumbnailHeight))

    # add a solution to this browser
    # nodeInfoList is the NodeInputInformationList where to display node
    # information when the mouse hovers over nodes
    def addSolution(self, vrp, solution, sheet, nodeInfoList):
        # thumbnail creation
        memdc = wx.MemoryDC()
        bitmap = wx.EmptyBitmap(self.thumbnailWidth, self.thumbnailHeight)
        memdc.SelectObject(bitmap)
        dc = wx.GCDC(memdc)
        canvas = wxcanvas.WxThumbnailCanvas(dc,
                                            self.thumbnailWidth,
                                            self.thumbnailHeight)
        sheet.paint(vrp, solution, canvas, thumbnail=True)
        memdc.Destroy()
        self.GetImageList().Add(bitmap)
        # panel creation
        panel = VrpPanel(self,
                         inputData=vrp,
                         solutionData=solution,
                         styleSheet=sheet,
                         nodeInfoList=nodeInfoList)
#         newName = reduce(lambda x, y: x+ y,
#                          [ x if i % 10 != 9 else x + '\n'
#                            for i, x in enumerate(solution.name) ] )
#         print newName
        newName = solution.name if len(solution.name) < 15 \
            else solution.name[:12] + '...' + solution.name[-3:]
        self.AddPage(panel,
                     newName,
                     imageId=self.GetPageCount())

    # add several solutions at once
    def addSolutions(self, vrp, solutions, sheet, nodeInfoList):
        for s in solutions:
            self.addSolution(vrp, s, sheet, nodeInfoList)

    # load a new stylesheet
    def loadStyleSheet(self, newSheet):
        for i in range(self.GetPageCount()):
            # update the sheet for this panel
            self.GetPage(i).styleSheet = newSheet
            # update the thumbnail
            memdc = wx.MemoryDC()
            bitmap = wx.EmptyBitmap(self.thumbnailWidth, self.thumbnailHeight)
            memdc.SelectObject(bitmap)
            dc = wx.GCDC(memdc)
            canvas = wxcanvas.WxThumbnailCanvas(dc,
                                                self.thumbnailWidth,
                                                self.thumbnailHeight)
            newSheet.paint(self.GetPage(i).inputData,
                           self.GetPage(i).solutionData,
                           canvas, thumbnail=True)
            memdc.Destroy()
            self.GetImageList().Replace(i, bitmap)
            # required to refresh thumbnails
            self.Refresh()

    # remove the currently selected solution
    def removeSolution(self):
        self.DeletePage(self.GetSelection())
        
class NodeInputInformationList(wx.ListCtrl):
    def __init__(self, parent, ID,
                 vrpData, solutionData):
        wx.ListCtrl.__init__(self, parent, ID, style=wx.LC_REPORT)
        # store the list of attributes for this type of VRP, starting
        # with the most common attributes
        attributes = vrpData.nodeAttributes + \
            [ '+' + x
              for x in solutionData.nodeAttributes
              if x != 'index' ]
        self.sortedAttributes = attributes
#         self.sortedAttributes = vrp.VrpInputData().nodeAttributes + \
#             vrp.VrpSolutionData().nodeAttributes
        alreadyAdded = set(self.sortedAttributes)
#         for a in attributes:
#             if not a in alreadyAdded:
#                 self.sortedAttributes.append(a)
        # set column names
        self.InsertColumn(0, 'Node attribute', width=nodeAttributeColWidth)
        self.InsertColumn(1, 'Value', width=nodeValueColWidth)
        # fill attribute names already
        for a in self.sortedAttributes:
            index = self.InsertStringItem(sys.maxint, a)
            self.SetItemBackgroundColour(index, 'white' if index % 2 == 0 else \
                                             wx.Colour(245,245,245))
        # internal data storage (wx.ListCtrl does not provide it, wtf)
        self.values = dict([ [a,''] for a in self.sortedAttributes ])
        
    def updateNodeInfo(self, node, solutionData):
        if node is None:
            # only set to no node if there is still the information of a node
            # displayed in the cells
            if self.values[self.sortedAttributes[0]] != '':
                for index in range(self.GetItemCount()):
                    self.values[self.GetItemText(index)] = ''
                    self.SetStringItem(index, 1, '')
        # case where we just hovered over a node
        else:
            nodeSol = solutionData.nodes[node['index']]
            for index in range(self.GetItemCount()):
                try:
                    self.values[self.GetItemText(index)] = \
                        style.globalNodeAttributeValue(self.GetItemText(index),
                                                       node,
                                                       solutionData)
                except Exception as e:
                    self.values[self.GetItemText(index)] = ''
                self.SetStringItem(index, 1,
                                   str(self.values[self.GetItemText(index)]))

# obsolete class?
class NodeInputInformationGrid(wx.grid.Grid):
    def __init__(self, parent, ID,
                 vrpData,
                 nRows = 50):
        # number of rows
        self.nRows = nRows
        wx.grid.Grid.__init__(self, parent, ID)
        # store the list of attributes for this type of VRP, starting
        # with the most common attributes
        attributes = set(vrpData.nodeAttributes)
        self.sortedAttributes = vrp.VrpInputData().nodeAttributes
        alreadyAdded = set(self.sortedAttributes)
        for a in attributes:
            if not a in alreadyAdded:
                self.sortedAttributes.append(a)

        # count the number of columns we need for displaying attributes,
        # knowing that we use nRows rows or less
        self.nColumns = 1 + (len(self.sortedAttributes)-1) / self.nRows
        # create each necessary column (and its "value" counterpart)
        self.CreateGrid(self.nRows, self.nColumns * 2)
        # set column names
        for i in range(self.nColumns):
            self.SetColLabelValue(2 * i, 'Attribute')
            self.SetColLabelValue(2 * i + 1, 'Value')
        # colour rows for easier reading
        for i in range(self.nRows):
            attr = wx.grid.GridCellAttr()
            attr.SetBackgroundColour('white' if i % 2 == 1 else
                                     wx.Colour(255, 228, 196))
            self.SetRowAttr(i, attr)
        # additional cosmetic settings
        self.EnableGridLines(False)
 	self.EnableDragColSize(True)
        self.DisableCellEditControl()
 	self.DisableDragCell()
 	self.DisableDragColMove()
 	self.DisableDragGridSize()
 	self.DisableDragRowSize()
 	self.EnableEditing(False)
        self.SetColLabelSize(0)
        self.SetRowLabelSize(0)
        # fill attribute names already
        maxWidth = 0
#         for i in range(0, self.nColumns*2):
#             self.SetColSize(i, self.GetColSize(i) * 1.3)
        for index, a in enumerate(self.sortedAttributes):
            self.SetCellValue(index % self.nRows,
                              2 * (index / self.nRows),
                              a)

    def updateNodeInfo(self, node):
        if node is None:
            # only set to no node if there is still the information of a node
            # displayed in the cells
            if self.GetCellValue(1, 1) != '':
                for index, a in enumerate(self.sortedAttributes):
                    self.SetCellValue(index % self.nRows,
                                      2 * (index / self.nRows) + 1,
                                      '')
        # case where we just hovered over a node
        else:
            for index, a in enumerate(self.sortedAttributes):
                self.SetCellValue(index % self.nRows,
                                  2 * (index / self.nRows) + 1,
                                  str(node[a]) if a in node else '')
