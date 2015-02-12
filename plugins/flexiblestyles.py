#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: February 10th 2013 by Fabien Tricoire
#
import sys
import math

from style import *

import colours
import shapes
from colourmapping import *

# This module contains flexible, general-purpose styles: they can be reused for
# different purposes and are not restrictive when it comes to required
# attributes.

# Display an interval within a bigger interval. The bigger interval is set by
# taking extreme values over the whole instance for both attributes setting the
# bounds of the subinterval to display.
# The default values for these two attributes allow to use this style directly
# for time window representation.
class FlexibleSubInterval(Style):
    description = 'interval as a rectangle'
    # used multiple times
    colourInfo = ColourParameterInfo()
    parameterInfo = {
        'x offset': IntParameterInfo(-40, 20),
        'y offset': IntParameterInfo(-20, 40),
        'thickness': IntParameterInfo(0, 20),
        'width': IntParameterInfo(6, 200),
        'height': IntParameterInfo(3, 60),
        'contour colour': colourInfo,
        'background colour': colourInfo,
        'time window colour': colourInfo,
        }
    defaultValue = {
        'x offset': 4,
        'y offset': 4,
        'thickness': 1,
        'width': 20,
        'height': 7,
        'contour colour': colours.black,
        'background colour': colours.white,
        'time window colour': colours.dimcyan,
        'left bound attribute': 'release time',
        'right bound attribute': 'due date',
        }
    def initialise(self):
        # parameter info for these needs to be computed later when the data
        # format is known
        self.timeToX = None

    def setParameter(self, parameterName, parameterValue):
        Style.setParameter(self, parameterName, parameterValue)
        if parameterName == 'width':
            self.timeToX = util.intervalMapping(self.earliest,
                                                self.latest,
                                                0.0,
                                                self.parameterValue['width'])
        
    #
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        # first-time-only block
        if not 'left bound attribute' in self.parameterInfo:
            def acceptable(x):
                return (isinstance(x, int) or isinstance(x, float)) and \
                    not isinstance(x, bool)
            self.parameterInfo['right bound attribute'] = \
                NodeInputAttributeParameterInfo(inputData, acceptable)
            self.parameterInfo['left bound attribute'] = \
                NodeInputAttributeParameterInfo(inputData, acceptable)
        # only perform painting if the selected attributes are available
        if not (self.parameterValue['right bound attribute'] in \
                    inputData.nodeAttributes and \
                    self.parameterValue['left bound attribute'] in \
                    inputData.nodeAttributes):
            return
        if self.timeToX is None:
            self.earliest = \
                min( [ x[self.parameterValue['left bound attribute']]
                       for x in inputData.nodes ], 0 )
            self.latest = max( [ x[self.parameterValue['right bound attribute']]
                                 for x in inputData.nodes ] )
            self.timeToX = util.intervalMapping(self.earliest, self.latest,
                                                0.0,
                                                self.parameterValue['width'])
        # now we can display everything we want
        # for each node display its background
        allX, allY, allW, allH = [], [], [], []
        style = DrawingStyle(self.parameterValue['background colour'],
                             self.parameterValue['background colour'],
                             lineThickness=self.parameterValue['thickness'])
        for node in inputData.nodes:
            if not ('x' in node and 'y' in node):
                continue
            allX.append(convertX(node['x']) + self.parameterValue['x offset'])
            allY.append(convertY(node['y']) + self.parameterValue['y offset'])
            allW.append(self.parameterValue['width'])
            allH.append(self.parameterValue['height'])
        canvas.drawRectangles(allX, allY, allW, allH, style,
                              referencePoint='southwest')
        # then display the TWs
        rtParam = self.parameterValue['left bound attribute']
        ddParam = self.parameterValue['right bound attribute']
        allX, allY, allW, allH = [], [], [], []
        style = DrawingStyle(self.parameterValue['time window colour'],
                             self.parameterValue['time window colour'])
        for node in inputData.nodes:
            if not ('x' in node and 'y' in node):
                continue
            allX.append(convertX(node['x']) + self.parameterValue['x offset'] +
                        self.timeToX(node[rtParam]))
            allY.append(convertY(node['y']) + self.parameterValue['y offset'])
            
            allW.append(max(1,
                            self.timeToX(node[ddParam]) -
                            self.timeToX(node[rtParam])))
            allH.append(self.parameterValue['height'])
        canvas.drawRectangles(allX, allY, allW, allH, style,
                              referencePoint='southwest')
        # then the border around
        allX, allY, allW, allH = [], [], [], []
        style = DrawingStyle(self.parameterValue['contour colour'],
                             lineThickness=self.parameterValue['thickness'])
        for node in inputData.nodes:
            if not ('x' in node and 'y' in node):
                continue
            allX.append(convertX(node['x']) + self.parameterValue['x offset'])
            allY.append(convertY(node['y']) + self.parameterValue['y offset'])
            allW.append(self.parameterValue['width'])
            allH.append(self.parameterValue['height'])
        canvas.drawRectangles(allX, allY, allW, allH, style,
                              referencePoint='southwest')

# Display a rectangle proportional to the demand for each node
class NodeAttributeAsRectangleDisplayer( Style ):
    description = 'small bar for attribute'
    # used multiple times
    offsetInfo = IntParameterInfo(-20, 20)
    parameterInfo = {
        'x offset': offsetInfo,
        'y offset': offsetInfo,
        'width': IntParameterInfo(2, 20),
        'max. height': IntParameterInfo(5, 200),
        'colour': ColourParameterInfo(),
        }
    defaultValue = {
        'x offset': -5,
        'y offset': 4,
        'width': 4,
        'min. height': 1,
        'max. height': 20,
        'colour': colours.darkorange,
        'attribute': 'demand',
        }
    def initialise(self):
        self.minValue = None
    #
    def setParameter(self, parameterName, parameterValue):
        Style.setParameter(self, parameterName, parameterValue)
        if parameterName == 'max. height' or parameterName == 'attribute':
            self.minValue = None
    #
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        # first-time-only execution
        if not 'attribute' in self.parameterInfo:
            def acceptable(x):
                return (isinstance(x, int) or isinstance(x, float)) and \
                    not isinstance(x, bool)
            self.parameterInfo['attribute'] = \
                NodeGlobalAttributeParameterInfo(inputData,
                                                 solutionData,
                                                 acceptable)
#         # only perform painting if the selected attributes are available
#         if not self.parameterValue['attribute'] in inputData.nodeAttributes:
#             return
        # first compute min and max demand if it's the first time we're here
        if self.minValue is None:
            self.values = globalNodeAttributeValues(\
                self.parameterValue['attribute'],
                inputData,
                solutionData)
            self.minValue, self.maxValue = min(self.values), max(self.values)
            self.computeHeight =\
                util.intervalMapping(self.minValue, self.maxValue,
                                     self.parameterValue['min. height'],
                                     self.parameterValue['max. height'])
        # second only continue if an attribute is specified
        allX, allY, allW, allH = [], [], [], []
        for node, value in zip(inputData.nodes, self.values):
            if (nodePredicate and not nodePredicate(node)) or node['is depot']:
                continue
            else:
                allX.append(convertX(node['x']) +
                            self.parameterValue['x offset'])
                allY.append(convertY(node['y']) +
                            self.parameterValue['y offset'])
                allW.append(self.parameterValue['width'])
                allH.append(self.computeHeight(value))
        style = DrawingStyle(self.parameterValue['colour'],
                             self.parameterValue['colour'])
        canvas.drawRectangles(allX, allY, allW, allH, style,
                              referencePoint='southeast')

# Display a list of rectangles proportional to cell value of given list
# attribute for each node
class NodeListAttributeAsRectanglesDisplayer(NodeAttributeAsRectangleDisplayer):
    description = 'small bars for list attribute'
    # used multiple times
    offsetInfo = IntParameterInfo(-20, 20)
    parameterInfo = {
        'x offset': offsetInfo,
        'y offset': offsetInfo,
        'padding': IntParameterInfo(0, 60),
        'width': IntParameterInfo(2, 20),
        'max. height': IntParameterInfo(5, 200),
        'colours': ColourMapParameterInfo(),
        }
    defaultValue = {
        'x offset': -5,
        'y offset': 5,
        'padding': 2,
        'width': 4,
        'min. height': 1,
        'max. height': 20,
        'colours': generateRandomColours(100),
        'attribute': '',
        }
    #
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        # first-time-only execution
        if not 'attribute' in self.parameterInfo:
            def acceptable(x):
                return isinstance(x, list) and \
                    (isinstance(x[0], int) or isinstance(x[0], float))
            self.parameterInfo['attribute'] = \
                NodeInputAttributeParameterInfo(inputData, acceptable)
        # only perform painting if the selected attributes are available
        if not self.parameterValue['attribute'] in inputData.nodeAttributes:
            return
        # first compute min and max demand if it's the first time we're here
        if not self.minValue:
            values = [ max(node[self.parameterValue['attribute']])
                       for node in inputData.nodes ]
            self.minValue, self.maxValue = min(values), max(values)
            self.computeHeight =\
                util.intervalMapping(self.minValue, self.maxValue,
                                     self.parameterValue['min. height'],
                                     self.parameterValue['max. height'])
        # second only continue if an attribute is specified
        # we use a different colour (hence style) for each item
        nElements = len(inputData.nodes[0][self.parameterValue['attribute']])
        for i in range(nElements):
            allX, allY, allW, allH = [], [], [], []
            for node in inputData.nodes:
                if (nodePredicate and not nodePredicate(node)) or \
                        node['is depot']:
                    continue
                else:
                    allX.append(convertX(node['x']) +
                                self.parameterValue['x offset'] +
                                i * (self.parameterValue['width'] +
                                     self.parameterValue['padding']))
                    allY.append(convertY(node['y']) +
                                self.parameterValue['y offset'])
                    allW.append(self.parameterValue['width'])
                    allH.append(self.computeHeight(\
                            node[self.parameterValue['attribute']][i]))
            style = DrawingStyle(self.parameterValue['colours'][i],
                                 self.parameterValue['colours'][i])
            canvas.drawRectangles(allX, allY, allW, allH, style,
                                  referencePoint='southeast')

# Display a node with flexible appearance
class FlexibleNodeDisplayer( Style ):
    description = 'customizable nodes'
    # used multiple times
    offsetInfo = IntParameterInfo(-20, 20)
    parameterInfo = {
        'x offset': offsetInfo,
        'y offset': offsetInfo,
        'min. radius': IntParameterInfo(1, 200),
        'max. radius': IntParameterInfo(1, 200),
        'node colouring': EnumerationParameterInfo([ 'constant',
                                                     'palette',
                                                     'gradient' ]),
        'fill colour': ColourMapParameterInfo(),
        'contour colour': ColourMapParameterInfo(),
        'contour thickness': IntParameterInfo(-1, 20),
        'shape type': EnumerationParameterInfo( [ 'circle',
                                                  'polygon',
                                                  'regular star',
                                                  'sharp star',
                                                  'fat star',
                                                  'very fat star',
                                                  ] ),
        'number of edges': IntParameterInfo(3, 100),
        'angle': FloatParameterInfo(-180.0, 180.0),
        'radius by attribute': BoolParameterInfo(),
        'filter active': BoolParameterInfo(),
        }
    defaultValue = {
        'x offset': 0,
        'y offset': 0,
        'min. radius': 3,
        'max. radius': 10,
        'fill colour': ColourMap([colours.funkygreen]),
        'contour colour': ColourMap([colours.black]),
        'shape type': 'polygon',
        'number of edges': 3,
        'angle': 0,
        'radius by attribute': False,
        'radius attribute': 'index',
        'colour attribute': 'index',
        'filter active': False,
        'filter attribute': 'is depot',
        'filter value': 'True',
        'node colouring': 'constant',
        'contour thickness': 1,
        }
    def initialise(self):
        # for radius by attribute
        self.computeRadius = None
        # for node colouring
        self.fillMapping = None
        self.contourMapping = None
        # filter value should be a string
        if 'filter value' in self.parameterValue and \
                not isinstance(self.parameterValue['filter value'], str):
            self.parameterValue['filter value'] = \
                str(self.parameterValue['filter value'])
    #
    def setParameter(self, parameterName, parameterValue):
        Style.setParameter(self, parameterName, parameterValue)
        if parameterName == 'max. radius' and \
                parameterValue < self.parameterValue['min. radius']:
            Style.setParameter(self, 'min. radius', parameterValue)
        if parameterName == 'min. radius' and \
                parameterValue > self.parameterValue['max. radius']:
            Style.setParameter(self, 'max. radius', parameterValue)
        if parameterName == 'radius attribute' \
                or parameterName == 'min. radius' \
                or parameterName == 'max. radius':
            self.computeRadius = None
        # in case we change the way nodes are coloured: update colour mapping
        if parameterName == 'node colouring' \
                or parameterName == 'colour attribute' \
                or parameterName == 'fill colour' \
                or parameterName == 'contour colour':
            self.fillMapping = None
            self.contourMapping = None
        # in case we change the attribute on which the filter is based,
        # we must compute the list of possible values for this attribute
        if parameterName == 'filter attribute':
            del self.parameterInfo['filter value']
            del self.parameterValue['filter value']
    #
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        # first-time-only execution
        if not 'radius attribute' in self.parameterInfo:
            def acceptable(x):
                return (isinstance(x, int) or isinstance(x, float)) and \
                    not isinstance(x, bool)
            self.parameterInfo['radius attribute'] = \
                NodeGlobalAttributeParameterInfo(inputData,
                                                 solutionData,
                                                 acceptable)
#         # only perform painting if the selected attributes are available
#         if not self.parameterValue['attribute'] in inputData.nodeAttributes:
#             return
        if not 'filter attribute' in self.parameterInfo:
            acceptable = \
                lambda x: True #isinstance(x, int) or \
                #isinstance(x, str) or isinstance(x, float)
            self.parameterInfo['filter attribute'] = \
                NodeGlobalAttributeParameterInfo(inputData,
                                                 solutionData,
                                                 acceptable)
        if not 'filter value' in self.parameterInfo:
            values = globalNodeAttributeValues(\
                self.parameterValue['filter attribute'],
                inputData,
                solutionData)
            self.fValues = [ x if isinstance(x, str) else str(x)
                             for x in values ]
            uniqueValues = [ x for x in set ( self.fValues ) ]
            uniqueValues.sort()
            self.parameterInfo['filter value'] = \
                EnumerationParameterInfo(uniqueValues)
            # case where it hasn't been set yet
            if not 'filter value' in self.parameterValue or \
                    not self.parameterValue['filter value'] in uniqueValues:
                self.parameterValue['filter value'] = uniqueValues[0]
        if not 'colour attribute' in self.parameterInfo:
            self.parameterInfo['colour attribute'] = \
                NodeGlobalAttributeParameterInfo(inputData,
                                                 solutionData,
                                                 lambda x: True)
        # compute min and max demand if required
        if self.computeRadius is None:
            self.rValues = globalNodeAttributeValues(\
                self.parameterValue['radius attribute'],
                inputData,
                solutionData)
            self.computeRadius =\
                util.intervalMapping(min(self.rValues), max(self.rValues),
                                     self.parameterValue['min. radius'],
                                     self.parameterValue['max. radius'])
        # enumerate values for colouring the nodes
        if self.fillMapping is None or self.contourMapping is None:
            colourValues = globalNodeAttributeValues(\
                self.parameterValue['colour attribute'],
                inputData,
                solutionData)
            if self.parameterValue['node colouring'] == 'palette':
                self.fillMapping = Palette( self.parameterValue['fill colour'],
                                            colourValues )
                self.contourMapping = \
                    Palette( self.parameterValue['contour colour'],
                             colourValues )
            elif self.parameterValue['node colouring'] == 'gradient':
                self.fillMapping = Gradient( self.parameterValue['fill colour'],
                                             colourValues )
                self.contourMapping = \
                    Gradient( self.parameterValue['contour colour'],
                              colourValues )
        # radius for each node
        allX, allY, allR = [], [], []
        # case where each node has the same colour
        if self.parameterValue['node colouring'] == 'constant':
            style = DrawingStyle( \
                self.parameterValue['contour colour'][0],
                self.parameterValue['fill colour'][0],
                lineThickness=self.parameterValue['contour thickness'])
        # otherwise we must use a different style for each node
        else:
            style = []
        for node, filterValue, rValue in zip(inputData.nodes,
                                             self.fValues,
                                             self.rValues):
            if nodePredicate and not nodePredicate(node):
                continue
            # only display nodes matching the filter
            elif self.parameterValue['filter active'] and \
                    'filter value' in self.parameterValue and \
                    filterValue != self.parameterValue['filter value']:
                continue
            else:
                allX.append(convertX(node['x']) +
                            self.parameterValue['x offset'])
                allY.append(convertY(node['y']) +
                            self.parameterValue['y offset'])
                allR.append(self.computeRadius(rValue) \
                                if self.parameterValue['radius by attribute'] \
                                else self.parameterValue['max. radius'])
                if self.parameterValue['node colouring'] != 'constant':
                    value = globalNodeAttributeValue(self.parameterValue\
                                                         ['colour attribute'],
                                                     node,
                                                     solutionData)
                    style.append(DrawingStyle(\
                            self.contourMapping[value],
                            self.fillMapping[value],
                            lineThickness = \
                                self.parameterValue['contour thickness']))
        # determine shape to use
        if self.parameterValue['shape type'] == 'circle':
            shape = shapes.Circle()
        elif self.parameterValue['shape type'] == 'polygon':
            shape = shapes.makeRegularPolygon(\
                self.parameterValue['number of edges'] )
        elif self.parameterValue['shape type'] == 'regular star':
            shape = shapes.makeStar(\
                self.parameterValue['number of edges'] )
        elif self.parameterValue['shape type'] == 'sharp star':
            shape = shapes.makeStar(\
                self.parameterValue['number of edges'], 3 )
        elif self.parameterValue['shape type'] == 'fat star':
            shape = shapes.makeStar(\
                self.parameterValue['number of edges'], 2 )
        elif self.parameterValue['shape type'] == 'very fat star':
            shape = shapes.makeStar(\
                self.parameterValue['number of edges'], 1.5 )
        else:
            return
        # Now we can draw the shapes
        # In case they all have the same radius and the same style,
        # we can use the faster method
        # otherwise we have to display each polygon separately
        if self.parameterValue['radius by attribute'] or \
                self.parameterValue['node colouring'] != 'constant':
            for i, (x, y, r) in enumerate(zip(allX, allY, allR)):
                canvas.drawShape(shape, x, y, r,
                                 style[i] \
                                     if isinstance(style, list) \
                                     else style,
                                 self.parameterValue['angle'])
        else:
            canvas.drawShapes(shape, allX, allY,
                              self.parameterValue['max. radius'],
                              style,
                              self.parameterValue['angle'])

# Display an arc with variable style
class FlexibleArcDisplayer( Style ):
    description = 'customizable arcs'
    parameterInfo = {
        'show direction': BoolParameterInfo(),
        'arrow length': FloatParameterInfo(0, 100),
        'arrow angle': IntParameterInfo(0, 180),
        'min. thickness': IntParameterInfo(1, 200),
        'max. thickness': IntParameterInfo(1, 200),
        'colouring': EnumerationParameterInfo([ 'constant',
                                                'palette',
                                                'gradient' ]),
        'arc colour': ColourMapParameterInfo(),
        'thickness by attribute': BoolParameterInfo(),
        'draw depot arcs': BoolParameterInfo(),
        'filter active': BoolParameterInfo(),
        'gradient min. value': FloatParameterInfo(-sys.maxint, sys.maxint),
        'gradient max. value': FloatParameterInfo(-sys.maxint, sys.maxint),
        }
    defaultValue = {
        'show direction': False,
        'arrow length': 20,
        'arrow angle': 30,
        'min. thickness': 1,
        'max. thickness': 3,
        'colouring': 'constant',
        'arc colour': ColourMap([colours.black]),
        'thickness by attribute': False,
        'draw depot arcs': True,
        'filter active': False,
        'filter attribute': 'from',
        'filter value': '0',
        # 'gradient min. value': 0,
        # 'gradient max. value': 1,
        }
    def initialise(self):
        # for thickness by attribute
        self.computeThickness = None
        # for arc colouring
        self.colourMapping = None
    #
    def setParameter(self, parameterName, parameterValue):
        Style.setParameter(self, parameterName, parameterValue)
        if parameterName == 'max. thickness' and \
                parameterValue < self.parameterValue['min. thickness']:
            Style.setParameter(self, 'min. thickness', parameterValue)
        if parameterName == 'min. thickness' and \
                parameterValue > self.parameterValue['max. thickness']:
            Style.setParameter(self, 'max. thickness', parameterValue)
        if parameterName == 'thickness attribute' \
                or parameterName == 'min. thickness' \
                or parameterName == 'max. thickness':
            self.computeThickness = None
        # in case we change the way arcs are coloured: update colour mapping
        if parameterName == 'colouring' \
                or parameterName == 'colour attribute' \
                or parameterName == 'arc colour':
            self.colourMapping = None
        # in case we change the attribute on which the filter is based,
        # we must compute the list of possible values for this attribute
        if parameterName == 'filter attribute':
            del self.parameterInfo['filter value']
            del self.parameterValue['filter value']
        # if we change the attribute for colouring the arcs, we should
        # recompute min/max values
        if parameterName == 'colour attribute':
            del self.parameterValue['gradient min. value']
            del self.parameterValue['gradient max. value']
        # if we change the bounds for the colour, we must recompute the
        # colour mapping
        if parameterName == 'gradient min. value' or \
                parameterName == 'gradient max. value':
            self.colourMapping = None
        # consistency
        if parameterName == 'gradient min. value' and \
                'gradient max. value' in self.parameterValue and \
                parameterValue > self.parameterValue['gradient max. value']:
            Style.setParameter(self, 'gradient max. value', parameterValue)
        if parameterName == 'gradient max. value' and \
                'gradient min. value' in self.parameterValue and \
                parameterValue < self.parameterValue['gradient min. value']:
            Style.setParameter(self, 'gradient min. value', parameterValue)
    #
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        # first-time-only execution
        if not 'thickness attribute' in self.parameterInfo:
            def acceptable(x):
                return (isinstance(x, int) or isinstance(x, float)) and \
                    not isinstance(x, bool)
            self.parameterInfo['thickness attribute'] = \
                ArcAttributeParameterInfo(solutionData,
                                          acceptable)
        if not 'thickness attribute' in self.parameterValue:
            if len(self.parameterInfo['thickness attribute'].possibleValues) >0:
                self.parameterValue['thickness attribute'] = \
                    self.parameterInfo['thickness attribute'].possibleValues[0]
        if not 'colour attribute' in self.parameterInfo:
            self.parameterInfo['colour attribute'] = \
                ArcAttributeParameterInfo(solutionData,
                                          lambda x: True)
        if not 'colour attribute' in self.parameterValue:
            self.parameterValue['colour attribute'] = \
                self.parameterInfo['colour attribute'].possibleValues[0]
        if not 'filter attribute' in self.parameterInfo:
            acceptable = \
                lambda x: True #isinstance(x, int) or \
                #isinstance(x, str) or isinstance(x, float)
            self.parameterInfo['filter attribute'] = \
                ArcAttributeParameterInfo(solutionData,
                                          acceptable)
        if not 'filter value' in self.parameterInfo:
            values = [ [ arc[self.parameterValue['filter attribute']]
                         for arc in route['arcs'] ]
                       for route in solutionData.routes ]
            values = reduce(lambda x, y: x+y, values)
            self.fValues = [ x if isinstance(x, str) else str(x)
                             for x in values ]
            uniqueValues = [ x for x in set ( self.fValues ) ]
            uniqueValues.sort()
            self.parameterInfo['filter value'] = \
                EnumerationParameterInfo(uniqueValues)
            # case where it hasn't been set yet
            if not 'filter value' in self.parameterValue or \
                    not self.parameterValue['filter value'] in uniqueValues:
                self.parameterValue['filter value'] = uniqueValues[0]
        if not 'gradient min. value' in self.parameterValue:
            values = reduce(lambda x, y: x + y,
                            [ [ arc[self.parameterValue['colour attribute']]
                                for arc in route['arcs'] ]
                              for route in solutionData.routes ])
            self.setParameter('gradient min. value', min(values))
            self.setParameter('gradient max. value', max(values))
        # build the list of all arcs to display
        arcsToDisplay = []
        allArcs = []
        angleInRadians = math.pi * self.parameterValue['arrow angle'] / 180
        myCos = math.cos(angleInRadians)
        mySin = math.sin(angleInRadians)
        for route in solutionData.routes:
            if routePredicate is None or routePredicate(route):
                for arc in route['arcs']:
                    if arcPredicate is None or arcPredicate(arc):
                        value = arc[self.parameterValue['filter attribute']]
                        if not isinstance(value, str):
                            value = str(value)
                        if not self.parameterValue['filter active'] or \
                                value == self.parameterValue['filter value']:
                            arcsToDisplay.append(arc)
                        # keep track of filtered arcs too
                        allArcs.append(arc)
        # compute min and max demand if required
        if self.computeThickness is None:
            self.tValues = [ arc[self.parameterValue['thickness attribute']]
                             for arc in allArcs ]
            self.computeThickness =\
                util.intervalMapping(min(self.tValues), max(self.tValues),
                                     self.parameterValue['min. thickness'],
                                     self.parameterValue['max. thickness'])
        # enumerate values for colouring the arcs
        if self.colourMapping is None:
            colourValues = [ arc[self.parameterValue['colour attribute']]
                             for arc in allArcs ]
            if self.parameterValue['colouring'] == 'palette':
                self.colourMapping = Palette(self.parameterValue['arc colour'],
                                             colourValues )
            elif self.parameterValue['colouring'] == 'gradient':
                colourValues +=  [ self.parameterValue['gradient min. value'],
                                   self.parameterValue['gradient max. value'] ]
                self.colourMapping = Gradient(self.parameterValue['arc colour'],
                                              colourValues )
        # special case where each arc has the same style: use faster method
        if self.parameterValue['colouring'] == 'constant' and \
                not self.parameterValue['thickness by attribute']:
            style = DrawingStyle( \
                self.parameterValue['arc colour'][0],
                self.parameterValue['arc colour'][0],
                lineThickness=self.parameterValue['min. thickness'])
            x1s, y1s, x2s, y2s = [], [], [], []
            for arc in arcsToDisplay:
                node1 = inputData.nodes[arc['from']]
                node2 = inputData.nodes[arc['to']]
                # add arcs that should be displayed only
                if self.parameterValue['draw depot arcs'] or\
                        ( not node1['is depot'] and not node2['is depot'] ):
                    x1s.append(convertX(node1['x']))
                    y1s.append(convertY(node1['y']))
                    x2s.append(convertX(node2['x']))
                    y2s.append(convertY(node2['y']))
                    # draw an arrow for direction
                    if self.parameterValue['show direction']:
                        x1, y1, x2, y2 = x1s[-1], y1s[-1], x2s[-1], y2s[-1]
                        u, v = x1 - x2, y1 - y2
                        d = math.hypot(u, v)
                        ratio = self.parameterValue['arrow length'] / d
                        x1a = x2 + (myCos * u - mySin * v) * ratio
                        y1a = y2 + (mySin * u + myCos * v) * ratio
                        x2a = x2 + (myCos * u + mySin * v) * ratio
                        y2a = y2 + ( - mySin * u + myCos * v) * ratio
                        # first line of the arrow
                        x1s.append(x2)
                        y1s.append(y2)
                        x2s.append(x1a)
                        y2s.append(y1a)
                        # second line of the arrow
                        x1s.append(x2)
                        y1s.append(y2)
                        x2s.append(x2a)
                        y2s.append(y2a)
            # now draw all arcs at once
            canvas.drawLines(x1s, y1s, x2s, y2s, style)
        # otherwise we must use a different style for each node
        else:
            # for convenience
            cAttr = self.parameterValue['colour attribute']
            tAttr = self.parameterValue['thickness attribute']
            # we compute the style for each arc
            styles = []
            for arc in arcsToDisplay:
                thickness = self.computeThickness(arc[tAttr]) \
                    if self.parameterValue['thickness by attribute'] \
                    else self.parameterValue['min. thickness']
                colour = self.colourMapping[arc[cAttr]] \
                    if self.parameterValue['colouring'] != 'constant'\
                    else self.parameterValue['arc colour'][0]
                styles.append( DrawingStyle( colour, colour, thickness ) )
            # now we can display each arc separately
            for arc, style in zip(arcsToDisplay, styles):
                node1 = inputData.nodes[arc['from']]
                node2 = inputData.nodes[arc['to']]
                if self.parameterValue['draw depot arcs'] or\
                        ( not node1['is depot'] and not node2['is depot'] ):
                    x1, y1 = convertX(node1['x']), convertY(node1['y'])
                    x2, y2 = convertX(node2['x']), convertY(node2['y'])
                    canvas.drawLine(x1, y1, x2, y2, style)
                    # draw an arrow for direction
                    if self.parameterValue['show direction']:
                        if x1 == x2 and y1 == y2:
                            pass
                        else:
                            u, v = x1 - x2, y1 - y2
                            d = math.hypot(u, v)
                            ratio = self.parameterValue['arrow length'] / d
                            x1a = x2 + (myCos * u - mySin * v) * ratio
                            y1a = y2 + (mySin * u + myCos * v) * ratio
                            x2a = x2 + (myCos * u + mySin * v) * ratio
                            y2a = y2 + ( - mySin * u + myCos * v) * ratio
                            # first line of the arrow
                            canvas.drawLine(x2, y2, x1a, y1a, style)
                            # second line of the arrow
                            canvas.drawLine(x2, y2, x2a, y2a, style)
