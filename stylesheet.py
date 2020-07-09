#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
#
import os
import string
import re
from math import *

import config
import style
import util
import colours
from vrpexceptions import *

padding = 200
cellTitleFontSize = 13
gridCellPadding = 3
gridDecorationStyle = style.DrawingStyle(lineColour=colours.lightgray,
                                         fillColour=colours.lightgray,
                                         lineThickness=1,
                                         lineStyle='solid')
gridDecorationFont = style.Font(cellTitleFontSize)

# # load available plugins
# pluginNames = util.getPluginNames()
# for pluginName in pluginNames:
#     exec 'import ' + pluginName

# This class encapsulates all routines to draw a VrpInputData and a
# VrpSolutionData to a VrpPanel using a given style.
class StyleSheet(object):
    """
    A StyleSheet paints input data onto a canvas using the paint() method.
    This class wraps all calls to the individual style paint() methods.
    It also manages grid operations as well as zoom level and aspect ratio.

    """
    # the types of problem this class of stylesheet should be default for
    defaultFor = []
    def __init__(self,
                 keepAspectRatio=True, styles=None, currentBox=None,
                 grid=False, gridRouteAttribute=None, filterNodesInGrid=False,
                 gridLines=True,
                 nColumns=None,
                 cellTitle=True, cellTitleFormat='%a %v'):
        if currentBox:
            self.xmin, self.ymin, self.xmax, self.ymax = currentBox
        else:
            # default: bounds for displayed box are initialized later
            self.xmin = None
        # start grid management code here!
        # attribute on which grid should be built
        self.grid = grid
        self.gridRouteAttribute = gridRouteAttribute
        self.filterNodesInGrid = filterNodesInGrid
        # grid decoration
        self.drawGridLines = gridLines
        # preferred number of columns in the grid or None for default
        self.nColumnsInGrid = nColumns if nColumns else None
        # do we display a title for each cell?
        self.displayCellTitle = cellTitle
        # string format to display as title for each cell
        # %a = attribute, %v = value
        self.cellTitleFormat = cellTitleFormat
#         # are we using a specific projection?
#         self.projection = None
        # load default parameters supplied by the derivated class
        if styles is None:
            self.loadDefault()
        else: # this should never match...
            self.keepAspectRatio = keepAspectRatio
            self.styles = styles

    # default stylesheet: display nodes and arcs in a simple way
    def loadDefault(self, keepAspectRatio=True):
        import basestyles
        # True if aspect ratio should be kept, False otherwise
        self.keepAspectRatio = keepAspectRatio
        # all styles for this stylesheet
        self.styles = [basestyles.NodeDisplayer()]

    # compute bounding box for drawing operations
    # this returns a box that has the appropriate ratio in case aspect ratio
    # should be preserved
    def computeInnerBoundingBox(self,
                                xmin, xmax, ymin, ymax,
                                inputData,
                                padding):
        # first-time only: set starting box to the whole problem
        if self.xmin is None:
            self.xmin, self.ymin, self.xmax, self.ymax = \
                inputData.xmin, inputData.ymin, inputData.xmax, inputData.ymax
        # compute mapping of x,y coordinates to a panel of this size
        width = float(xmax-xmin) - 2 * padding
        height = float(ymax-ymin) - 2 * padding
        # case where aspect ratio should be kept
        if self.keepAspectRatio:
            # case where the panel is too wide
            if float(height) / width < inputData.heightOverWidth:
                myWidth = float(height) / inputData.heightOverWidth
                myHeight = float(height)
            # other case: panel is too high
            else:
                myHeight = float(width) * inputData.heightOverWidth
                myWidth = float(width)
        # case where aspect ratio is not preserved
        else:
            myWidth, myHeight = float(width), float(height)
        # now we can normalize coordinates
        xDiff = (xmax - xmin - myWidth) / 2.0
        yDiff = (ymax - ymin - myHeight) / 2.0
        return xmin+xDiff, xmax-xDiff, ymin+yDiff, ymax-yDiff

    # compute bounding box for drawing operations
    # this version returns the whole available drawing area
    def computeOuterBoundingBox(self,
                                xmin, xmax, ymin, ymax,
                                inputData,
                                padding):
        return xmin + padding, xmax - padding, ymin + padding, ymax - padding

    # compute coordinate transformations
    def getTransformations(self, xmin, xmax, ymin, ymax, inputData, padding):
        xmin, xmax, ymin, ymax = self.computeInnerBoundingBox(xmin, xmax,
                                                              ymin, ymax,
                                                              inputData,
                                                              padding)
        convertX = util.intervalMapping(self.xmin, self.xmax, xmin, xmax)
        convertY = util.intervalMapping(self.ymin, self.ymax, ymin, ymax)
#         # new version: projection is integrated
#         if self.projection is None:
#             convertX = util.intervalMapping(self.xmin, self.xmax, xmin, xmax)
#             convertY = util.intervalMapping(self.ymin, self.ymax, ymin, ymax)
#         else:
#             if projection == 'Mercator':
#                 # Mercator cylindric projection
#                 projX = lambda x: x
#                 projY = lambda y: \
#                     log( (1 + sin(y * pi / 180.0)) / cos(y * pi / 180.0))
#             else:
#                 pass
#             # project first, then convert the projected value
#             tmpX = util.intervalMapping(projX(self.xmin), projX(self.xmax),
#                                         xmin, xmax)
#             tmpY = util.intervalMapping(projY(self.ymin), projY(self.ymax),
#                                         ymin, ymax)
#             convertX = lambda x: tmpX(projX(x))
#             convertY = lambda y: tmpY(projY(y))
        # in any case, return the transformations
        return convertX, convertY

    def getReverseCoordMapping(self, canvas, inputData):
        # compute bounding box for drawing
        width, height = canvas.getSize()
        # compute the size of a cell
        if self.grid:
            nColumns = self.nColumnsInGrid
            nRows = self.nRowsInGrid
        # case where we don't use a grid
        else:
            nColumns = 1
            nRows = 1
        cellWidth = float(width + gridCellPadding) / nColumns
        cellHeight = float(height + gridCellPadding) / nRows
        # corners for the bottom left cell
        cellXmin = 0
        cellXmax = cellXmin + cellWidth - gridCellPadding
        cellYmin = 0
        cellYmax = cellYmin + cellHeight - gridCellPadding
        if self.grid and self.displayCellTitle:
            cellYmax -= cellTitleFontSize
        xmin, xmax, ymin, ymax = \
            self.computeInnerBoundingBox(cellXmin, cellXmax,
                                         cellYmin, cellYmax,
                                         inputData,
                                         padding)
        revX = util.intervalMappingModulo(xmin, xmax,
                                          self.xmin, self.xmax,
                                          cellWidth)
        revY = util.intervalMappingModulo(ymin, ymax,
                                          self.ymin, self.ymax,
                                          cellHeight)
        return revX, revY
            
    # paint using stylesheet
    def paint(self, inputData, solutionData, canvas,
              nodePredicate=None, #lambda(x): True,
              routePredicate=None, #lambda(x): True,
              arcPredicate=None, #lambda(x): True,
              thumbnail=False):
        """
        Paint inputData and solutionData on canvas.
        The predicates are used to filter out some nodes, routes and arcs if
        required. They are passed to each style's individual paint() call.
        The style is supposed to paint only the entities that satisfy the
        predicate.
        
        """
        canvas.blank()
        # case where we want to paint a thumbnail: smaller padding and a border
        if thumbnail:
            margin = 2
            canvas.drawBorder()
        else:
            margin = padding

        # compute bounding box for drawing
        width, height = canvas.getSize()
        
        # start grid code here!
        if not self.gridRouteAttribute and solutionData.routeAttributes:
            self.gridRouteAttribute = 'index'
        # case where a grid is defined but the grid attribute does not exist in
        # the routes
        for route in solutionData.routes:
            if not self.gridRouteAttribute in route:
                self.gridRouteAttribute = 'index'
                break
        # only use a grid if the solution isn't empty
        if self.grid and solutionData.routes:
            # count and sort the occurrences of the grid attribute
            attributeValues = set([ route[self.gridRouteAttribute]
                                    for route in solutionData.routes ])
            gridSize = len(attributeValues)
            # if we must use a grid but haven't specified dimensions for it yet
            if not self.nColumnsInGrid:
                # approximate a square grid
                wPrime = 1.0 / inputData.heightOverWidth
                self.nColumnsInGrid = \
                    int(ceil(sqrt(gridSize * wPrime) / wPrime))
            self.nRowsInGrid = 1 + (gridSize-1) // self.nColumnsInGrid
            # compute number of rows from number of columns
            nColumns = self.nColumnsInGrid
            nRows = self.nRowsInGrid
        # case where we don't use a grid
        else:
            # in case grid is set to True but the solution is empty
            self.grid = False
            nColumns = 1
            nRows = 1
            attributeValues = set([None])
        cellWidth = float(width + gridCellPadding) / nColumns
        cellHeight = float(height + gridCellPadding) / nRows
        # for each cell in the grid, compute its bounding box
        # draw a grid if needed
        # (do it before displaying the cell's title)
        if self.drawGridLines and self.grid:
            self.drawGrid(canvas, nColumns, nRows)
        for i, cell in enumerate(attributeValues):
            # grid coordinates for the cell
            cellX = i % nColumns
            cellY = i // nColumns
            # real coordinates of the cell
            cellXmin = cellX * cellWidth
            cellXmax = cellXmin + cellWidth - gridCellPadding
            cellYmax = height - cellY * cellHeight
            cellYmin = cellYmax - cellHeight + gridCellPadding
            # In case grid decoration is required
            if self.grid and self.displayCellTitle:
                titleText = \
                    self.cellTitleFormat.replace('%a',
                                                 str(self.gridRouteAttribute))\
                                                 .replace('%v', str(cell))
                canvas.drawFancyText(titleText,
                                     cellXmin + (cellXmax - cellXmin) / 2.0,
                                     cellYmax - cellTitleFontSize / 2.0,
                                     gridDecorationFont,
                                     colours.black, colours.white,
                                     referencePoint='centre')
                cellYmax -= cellTitleFontSize
#                 self.drawCellBorder(canvas,
#                                     cellXmin, cellXmax, cellYmin, cellYmax)
            # only draw in this cell
            canvas.restrictDrawing(cellXmin, cellYmin, cellXmax, cellYmax)
            # next steps:
            xmin, xmax, ymin, ymax = \
                self.computeOuterBoundingBox(cellXmin, cellXmax,
                                             cellYmin, cellYmax,
                                             inputData,
                                             margin)
            revX, revY = self.getReverseCoordMapping(canvas, inputData)
            convertX, convertY = self.getTransformations(cellXmin, cellXmax,
                                                         cellYmin, cellYmax,
                                                         inputData,
                                                         margin)
            # predicate if required for grid
            tmpNodePredicate = lambda x: True
            if not self.grid:
                newRoutePredicate = routePredicate
            else:
                tmpPredicate = util.makeRoutePredicate(self.gridRouteAttribute,
                                                       cell)
                newRoutePredicate = \
                    lambda route: tmpPredicate(route) and \
                    (routePredicate is None or routePredicate(route))
                # in case we also need to filter nodes
                if self.filterNodesInGrid:
                    tmpNodePredicate = \
                        util.makeNodeInRoutePredicate(solutionData,
                                                      newRoutePredicate)
            newNodePredicate = lambda node: tmpNodePredicate(node) and\
                (nodePredicate is None or nodePredicate(node))
            # display all styles sequentially
            for style in self.styles:
                if i == 0 or not style.oncePerGrid:
                    style.paintData(inputData, solutionData,
                                    canvas, convertX, convertY,
                                    newNodePredicate,
                                    newRoutePredicate,
                                    arcPredicate,
                                    (revX(xmin-padding+2), revY(ymin-padding+2),
                                     revX(xmax+padding-2), revY(ymax+padding-2))
                                )
            # allow to draw everywhere again
            canvas.unrestrictDrawing()

    # export the stylesheet as a new class
    def export(self, name, defaultFor=[]):
        # keep only alphanumeric characters
        name = re.sub(r'\W+', '', name)
        if name[0].isdigit():
            name = 'a' + name
        print('exporting with name=', name)
        # do not export to a module with the same name as a builtin module
        if os.path.exists(\
            os.path.join(config.builtinPluginDir, name + '.py')) or \
            os.path.exists(\
            os.path.join(config.userPluginDir, name + '.py')):
            outputFileName = os.path.join(config.userSheetDir,
                                          name + '_user.py')
        else:
            outputFileName = os.path.join(config.userSheetDir, name + '.py')
        # (first we check that the directory exists)
        if not os.path.isdir(config.userSheetDir):
            print('Creating user sheets directory', config.userSheetDir)
            os.mkdir(config.userSheetDir)
        f = open(outputFileName, 'w')
        indent1 = '    '
        indent2 = indent1+indent1
        requiredModules = set([x.__module__ for x in self.styles])
        requiredModules.add('style')
        requiredModules.add('stylesheet')
        for m in requiredModules:
            f.write( 'import ' + m + '\n')
        f.write('# user stylesheet' + '\n')
        className = name + 'UserStyleSheet'
        className = className[0].upper() + className[1:]
        f.write('class ' + className + '(stylesheet.StyleSheet):' + '\n')
        f.write(indent1 + 'defaultFor = ' + str(defaultFor) + '\n')
        f.write(indent1 + '# load sheet defaults' + '\n')
        f.write(indent1 + 'def loadDefault(self):' + '\n')
        # special line for aspect ratio
        f.write(indent2 + '# preserve original aspect ratio?' + '\n')
        f.write(indent2 + 'self.keepAspectRatio = ' + \
                         str(self.keepAspectRatio) + '\n')
        # grid information
        f.write(indent2 + '# grid information\n')
        f.write(indent2 + 'self.grid = ' + str(self.grid) + '\n')
        f.write(indent2 + 'self.gridRouteAttribute = \'' + \
                    str(self.gridRouteAttribute) + '\'\n')
        f.write(indent2 + 'self.filterNodesInGrid = ' + \
                    str(self.filterNodesInGrid) + '\n')
        f.write(indent2 + 'self.drawGridLines = ' + \
                    str(self.drawGridLines) + '\n')
#         f.write(indent2 + 'self.nColumnsInGrid = ' + \
#                     str(self.nColumnsInGrid) + '\n')
        f.write(indent2 + 'self.displayCellTitle = ' + \
                    str(self.displayCellTitle) + '\n')
        f.write(indent2 + 'self.cellTitleFormat = \'' + \
                    str(self.cellTitleFormat) + '\'\n')
#         # save current box size
#         f.write(indent2 + \
#                     'self.xmin, self.ymin, self.xmax, self.ymax = ' + \
#                     str((self.xmin, self.ymin, self.xmax, self.ymax)) + \
#                     '\n')
        f.write(indent2 + '# initialize styles' + '\n')
        f.write(indent2 + 'self.styles = []' + '\n')
        for i, s in enumerate(self.styles):
            f.write(indent2 + '# style ' + str(i+1) + ': ' + \
                        s.description + '\n')
            f.write(indent2 + 'self.styles.append(' + str(s) + ')' + '\n')
        # close the file..
        f.close()
        print('Stored stylesheet to ' + outputFileName)

    # print the stylesheet
    def __repr__(self):
        return self.__module__ + '.' + self.__class__.__name__ + \
            '(keepAspectRatio=' + str(self.keepAspectRatio) + \
            ', grid=' + str(self.grid) + \
            ', gridRouteAttribute=\'' + str(self.gridRouteAttribute) + '\'' + \
            ', filterNodesInGrid=' + str(self.filterNodesInGrid) + '' + \
            ', gridLines=' + str(self.drawGridLines) + \
            ', nColumns=' + str(self.nColumnsInGrid) + \
            ', cellTitle=' + str(self.displayCellTitle) + \
            ', cellTitleFormat=\'' + str(self.cellTitleFormat) + '\'' + \
            ', currentBox=' + \
            str((self.xmin, self.ymin, self.xmax, self.ymax)) + \
            ', styles=' + str(self.styles) + ')'

    # used for debug
    def drawCellBorder(self, canvas, cellXmin, cellXmax, cellYmin, cellYmax):
        canvas.drawCircle(cellXmin, cellYmin, 20, gridDecorationStyle)
        canvas.drawRectangle(cellXmin,
                             cellYmin,
                             cellXmax-cellXmin,
                             cellYmax-cellYmin,
                             gridDecorationStyle,
                             referencePoint='southwest')
        canvas.drawLine(cellXmin + (cellXmax-cellXmin) / 2.0,
                        cellYmin + (cellXmax-cellXmin) / 2.0,
                        cellXmax + (cellXmax-cellXmin) / 2.0,
                        cellYmin - (cellYmax-cellYmin) / 2.0,
                        gridDecorationStyle)                        

    # draw the grid borders
    def drawGrid(self, canvas, nColumns, nRows):
        # compute bounding box for drawing
        width, height = canvas.getSize()
        cellWidth = float(width + gridCellPadding) / nColumns
        cellHeight = float(height + gridCellPadding) / nRows
        for col in range(nColumns - 1):
            x = col * cellWidth + cellWidth - gridCellPadding / 2.0
            y = height / 2.0
            canvas.drawRectangle(x, y, gridCellPadding, height,
                                 gridDecorationStyle,
                                 referencePoint='centre')
        for row in range(nRows - 1):
            x = width / 2.0
            y = height - row * cellHeight - cellHeight + gridCellPadding / 2.0
            canvas.drawRectangle(x, y, width, gridCellPadding,
                                 gridDecorationStyle,
                                 referencePoint='centre')
