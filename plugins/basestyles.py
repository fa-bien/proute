#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: September 27th 2011 by Fabien Tricoire
#
from style import *

import colours

# Basic style for an input data: draw depot and nodes
class NodeDisplayer( Style ):
    description = 'nodes'
    # used multiple times
    colourInfo = ColourParameterInfo()
    parameterInfo = { 'depot colour': colourInfo,
                      'depot contour': colourInfo,
                      'depot size': IntParameterInfo(0, 50),
                      'node colour': colourInfo,
                      'node contour': colourInfo,
                      'node size': IntParameterInfo(0, 20),
                      'depot contour thickness': IntParameterInfo(0, 20),
                      'node contour thickness': IntParameterInfo(0, 20),
                      'hide unused nodes': BoolParameterInfo(),
                      }
    defaultValue = { 'depot colour': Colour(255, 0, 0, 255),
                     'depot contour': Colour(0, 0, 0, 255),
                     'depot size': 7,
                     'node colour': Colour(0, 128, 0, 255),
                     'node contour': Colour(0, 0, 0, 255),
                     'node size': 3,
                     'depot contour thickness': 1,
                     'node contour thickness': 1,
                     'hide unused nodes': False,
                      }

    #
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        # display depots
        depotX = []
        depotY = []
        depotW = []
        nodeX = []
        nodeY = []
        nodeR = []
        for node in inputData.nodes:
            if (nodePredicate and not nodePredicate(node)) or \
                    self.parameterValue['hide unused nodes'] and \
                    not solutionData.nodes[node['index']]['used']:
                continue
            # case of a depot
            if node['is depot']:
                depotX.append(convertX(node['x']))
                depotY.append(convertY(node['y']))
                depotW.append(self.parameterValue['depot size'])
            else:
                nodeX.append(convertX(node['x']))
                nodeY.append(convertY(node['y']))
                nodeR.append(self.parameterValue['node size'])
        # draw all non-depots
        style = DrawingStyle(self.parameterValue['node contour'],
                             self.parameterValue['node colour'],
                             lineThickness = \
                                 self.parameterValue['node contour thickness'])
        canvas.drawCircles(nodeX, nodeY, nodeR, style)
        # draw all depots
        style = DrawingStyle(self.parameterValue['depot contour'],
                             self.parameterValue['depot colour'],
                             lineThickness = \
                                 self.parameterValue['depot contour thickness'])
        canvas.drawRectangles(depotX, depotY, depotW, depotW, style)
        
# Display a label for each node
class NodeLabelDisplayer( Style ):
    description = 'node label'
    # used multiple times
    colourInfo = ColourParameterInfo()
    parameterInfo = { 
        'foreground colour': colourInfo,
        'y offset': IntParameterInfo(-20, 40),
        'x offset': IntParameterInfo(-40, 20),
        'font size': IntParameterInfo(6, 40),
        'hide unused nodes': BoolParameterInfo(),
        }
    defaultValue = {
        'attribute': 'label',
        'x offset': 3,
        'y offset': 0,
        'foreground colour': Colour(0, 0, 0, 255),
        'background colour': Colour(0, 0, 0, 255),
        'font size': 9,
        'font family': 'Verdana',
        'font style': 'normal',
        'hide unused nodes': False,
        }
    #
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        # one-time-only block
        if not 'attribute' in self.parameterInfo:
            self.parameterInfo['attribute'] = \
                NodeGlobalAttributeParameterInfo(inputData, solutionData)
        font = Font(self.parameterValue['font size'],
                    self.parameterValue['font family'],
                    self.parameterValue['font style'])
        foreground = self.parameterValue['foreground colour']
        background = self.parameterValue['background colour']
        labels, xs, ys = [], [], []
        for node in inputData.nodes:
            if (nodePredicate and not nodePredicate(node)) or \
                    self.parameterValue['hide unused nodes'] and \
                    not solutionData.nodes[node['index']]['used']:
                continue
            labels.append(str(globalNodeAttributeValue(self.parameterValue\
                                                           ['attribute'],
                                                       node,
                                                       solutionData)))
            xs.append(convertX(node['x']) + self.parameterValue['x offset'])
            ys.append(convertY(node['y']) + self.parameterValue['y offset'])
        canvas.drawTexts(labels, xs, ys, font, foreground, background)

# Display a rectangle proportional to the demand for each node
class NodeDemandDisplayer( Style ):
    description = 'small bar for demand'
    # used multiple times
    offsetInfo = IntParameterInfo(-20, 20)
    parameterInfo = { 
        'x offset': offsetInfo,
        'y offset': offsetInfo,
        'width': IntParameterInfo(2, 20),
        'max. height': IntParameterInfo(5, 200),
        'colour': ColourParameterInfo(),
        'hide unused nodes': BoolParameterInfo(),
        }
    defaultValue = {
        'x offset': -5,
        'y offset': 4,
        'width': 4,
        'min. height': 1,
        'max. height': 20,
        'colour': Colour(100, 100, 250, 255),
        'hide unused nodes': False,
        }
    #
    def initialise(self):
        self.requiredNodeAttributes += [ 'demand' ]
        self.minDemand = False
        self.maxDemand = False
    #
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        # first compute min and max demand if it's the first time we're here
        if not self.minDemand:
            demands = [ node['demand'] for node in inputData.nodes ]
            self.minDemand, self.maxDemand = min(demands), max(demands)
            self.computeHeight =\
                util.intervalMapping(self.minDemand, self.maxDemand,
                                     self.parameterValue['min. height'],
                                     self.parameterValue['max. height'])
        allX, allY, allW, allH = [], [], [], []
        for node in inputData.nodes:
            if (nodePredicate and not nodePredicate(node)) or \
                    self.parameterValue['hide unused nodes'] and \
                    not solutionData.nodes[node['index']]['used']:
                continue
            allX.append(convertX(node['x']) +
                        self.parameterValue['x offset'])
            allY.append(convertY(node['y']) +
                        self.parameterValue['y offset'])
            allW.append(self.parameterValue['width'])
            allH.append(self.computeHeight(node['demand']))
        style = DrawingStyle(self.parameterValue['colour'],
                             self.parameterValue['colour'])
        canvas.drawRectangles(allX, allY, allW, allH, style,
                              referencePoint='southeast')

# Basic style for a solution data: draw arcs
class RouteDisplayer( Style ):
    description = 'route arcs'
    parameterInfo = { 
        'arc colour': ColourParameterInfo(),
        'thickness': IntParameterInfo(0, 20),
        'draw depot arcs': BoolParameterInfo(),
        }
    defaultValue = {
        'draw depot arcs': True,
        'thickness': 1,
        'arc colour': colours.black,
        }
    #
    def initialise(self):
        self.requiredArcAttributes += [ 'from', 'to' ]
    #
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        # display each route
        for route in solutionData.routes:
            if routePredicate and not routePredicate(route): continue
            for arc in route['arcs']:
                if arcPredicate and not arcPredicate(arc): continue
                node1 = inputData.nodes[arc['from']]
                node2 = inputData.nodes[arc['to']]
                style=DrawingStyle(lineColour=self.parameterValue['arc colour'],
                              lineThickness=self.parameterValue['thickness'])
                if self.parameterValue['draw depot arcs'] or\
                        ( not node1['is depot'] and not node2['is depot'] ):
                    canvas.drawLine(convertX(node1['x']),
                                    convertY(node1['y']),
                                    convertX(node2['x']),
                                    convertY(node2['y']),
                                    style)

# Basic style for a solution data: draw arcs
class RoutePolylineDisplayer( Style ):
    description = 'routes using polylines'
    parameterInfo = { 
        'arc colour': ColourParameterInfo(),
        'thickness': IntParameterInfo(0, 20),
        'draw depot arcs': BoolParameterInfo(),
        }
    defaultValue = {
        'draw depot arcs': True,
        'thickness': 1,
        'arc colour': colours.black,
        }
    #
    def initialise(self):
        self.requiredRouteAttributes += [ 'node sequence' ]
    #
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        style=DrawingStyle(lineColour=self.parameterValue['arc colour'],
                           lineThickness=self.parameterValue['thickness'])
        # display each route
        for route in solutionData.routes:
            if routePredicate and not routePredicate(route): continue
            x, y = [], []
            for node in route['node sequence']:
                x.append(convertX(inputData.nodes[node]['x']))
                y.append(convertY(inputData.nodes[node]['y']))
            if len(x) > 1:
                canvas.drawPolyline(x, y, style)

# Draw routes with different colours depending on attributes
class RouteColourDisplayer( Style ):
    description = 'coloured routes'
    # parameters for this style
    # paraminfo['attribute'] is delayed until we know on which problem and
    # solution types we are working
    parameterInfo = { 'draw depot arcs': BoolParameterInfo(),
                      'thickness': IntParameterInfo(0, 20),
                      'colours': ColourMapParameterInfo(),
                      }
    defaultValue = {
        'attribute': 'index',
        'draw depot arcs': True,
#         'colours': generateSpreadColours(100),
        'colours': generateRandomColours(100),
        'thickness': 1,
        }
                      
    # overload setParameter to reset colour map when the attribute parameter
    # is changed
    def setParameter(self, parameterName, parameterValue):
        self.parameterValue[parameterName] = parameterValue
        if parameterName == 'attribute':
            self.values = None
            
    def initialise(self):
        # lets paint() know that colours have yet to be allocated
        self.requiredRouteAttributes += [ 'node sequence' ]
        self.values = None
    #
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        # this block is only executed the first time the style is used
        if self.values is None:
            # we construct a unique value-colour mapping
            # we only want to accept attributes that return hashable values
            acceptable = lambda x: \
                not (isinstance(x, dict) or isinstance(x, list))
            self.parameterInfo['attribute'] = \
                RouteAttributeParameterInfo(solutionData, acceptable)
            self.mapping = {}
        # make sure that each route is present in the mapping
        self.values = set([ route[self.parameterValue['attribute']]
                            for route in solutionData.routes ])
        for v in self.values:
            if not v in self.mapping:
                self.mapping[v] = len(self.mapping)
        # end of first-time-only block
        # display each route
        attribute = self.parameterValue['attribute']
        for route in solutionData.routes:
            if routePredicate and not routePredicate(route): continue
            # set the appropriate colour for this route
            thisColour = self.parameterValue['colours']\
                [self.mapping[route[attribute]]]
            style = DrawingStyle(thisColour,
                                 lineThickness=self.parameterValue['thickness'])
            x, y = [], []
            for node in route['node sequence']:
                if self.parameterValue['draw depot arcs'] or\
                        not inputData.nodes[node]['is depot']:
                    x.append(convertX(inputData.nodes[node]['x']))
                    y.append(convertY(inputData.nodes[node]['y']))
            if len(x) > 1:
                canvas.drawPolyline(x, y, style)
#             # now we can draw the route
#             for arc in route['arcs']:
#                 if arcPredicate and not arcPredicate(arc): continue
#                 node1 = inputData.nodes[arc['from']]
#                 node2 = inputData.nodes[arc['to']]
#                 if self.parameterValue['draw depot arcs'] or\
#                         ( not node1['is depot'] and not node2['is depot'] ):
#                     canvas.drawLine(convertX(node1['x']),
#                                     convertY(node1['y']),
#                                     convertX(node2['x']),
#                                     convertY(node2['y']),
#                                     style)

# display the value of an arc attribute on a parallel line to the arc
class ArcAttributeDisplayer( Style ):
    description = 'arc attribute'
    # used multiple times
    colourInfo = ColourParameterInfo()
    parameterInfo = {
        'foreground colour': colourInfo,
        'background colour': colourInfo,
        'padding': IntParameterInfo(0, 100),
        'font size': IntParameterInfo(6, 40),
        'position on arc': FloatParameterInfo(0.0, 1.0),
        }
    # (arc attribute parameter info is delayed until we know the solution)
    defaultValue = {
        'font family': 'Verdana',
        'font style': 'normal',
        'position on arc': .4,
        'font size': 16,
        'attribute': 'to',
        'padding': 5,
        'foreground colour': colours.rosybrown,
        'background colour': colours.black,
        }
    #
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        # first-time-only execution
        if 'attribute' not in self.parameterInfo:
            self.parameterInfo['attribute'] = \
                ArcAttributeParameterInfo(solutionData)
        # display coverage for each node if relevant
        font = Font(self.parameterValue['font size'],
                    self.parameterValue['font family'],
                    self.parameterValue['font style'])
        foreground = self.parameterValue['foreground colour']
        background = self.parameterValue['background colour']
        # display each route
        for route in solutionData.routes:
            if routePredicate and not routePredicate(route): continue
            for arc in route['arcs']:
                if arcPredicate and not arcPredicate(arc): continue
                if not self.parameterValue['attribute'] in arc: continue
                node1 = inputData.nodes[arc['from']]
                node2 = inputData.nodes[arc['to']]
                # here we calculate the position and angle of our label
                x1, y1 = convertX(node1['x']), convertY(node1['y'])
                x2, y2 = convertX(node2['x']), convertY(node2['y'])
                # test
                if x1 < x2:
                    x1, y1, x2, y2 = x2, y2, x1, y1
                # first the angle...
                u, v = x2 - x1, y2 - y1
                # we want an angle in degrees..
                angle = math.asin(v / max(.0001, math.hypot(u, v)) )
                angle = math.degrees(angle)
                if u < 0:
                    angle *= -1
                # then the coordinates
                x, y = x1 + u * self.parameterValue['position on arc'], \
                    y1 + v * self.parameterValue['position on arc']
                # normal vector for appropriate padding
                nfactor = max(.00001, math.hypot(u,v))
                na = self.parameterValue['padding'] * -v / nfactor
                nb = self.parameterValue['padding'] * u / nfactor
                x += na
                y += nb
                # finally we can write the text!
                canvas.drawFancyText(str(arc[self.parameterValue['attribute']]),
                                     x, y,
                                     font, foreground, background,
                                     angle=angle)

# display solution attributes
# Basic style for an input data: draw depot and nodes
class SolutionAttributesDisplayer( Style ):
    description = 'solution attributes in a corner'
    parameterInfo = { 'font size': IntParameterInfo(4, 40),
                      'foreground colour': ColourParameterInfo(),
                      'background colour': ColourParameterInfo(),
                      'corner': EnumerationParameterInfo( [ 'top left',
                                                            'top right',
                                                            'bottom left',
                                                            'bottom right' ] ),
                      'x offset': IntParameterInfo(-200, 200),
                      'y offset': IntParameterInfo(-200, 200),
                      'vertical padding': IntParameterInfo(0, 50),
                      'horizontal padding': IntParameterInfo(-50, 50),
                      }
    defaultValue = { 'font size': 12,
                     'foreground colour': colours.darkpurple,
                     'background colour': colours.white,
                     'corner': 'top left',
                     'x offset': 0,
                     'y offset': 0,
                     'vertical padding': 6,
                     'horizontal padding': 0,
                     'font family': 'Verdana',
                     'font style': 'normal',
                     }
    #
    def initialise(self):
        self.oncePerGrid = True
    #
    def processAttributes(self, solutionData):
        for attribute in solutionData.attributes:
            if not 'display ' + attribute in self.parameterInfo:
                self.parameterInfo['display ' + attribute] = BoolParameterInfo()
            if not 'display ' + attribute in self.parameterValue:
                self.parameterValue['display ' + attribute] = True
    #
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        self.processAttributes(solutionData)
        # two columns: attribute and value
        # for each column we want to compute the width,
        # i.e. the max width of an element
        widthLeft = max( [ len(str(x)) for x in solutionData.attributes ] )
        widthRight = max( [ len(str(solutionData.attributes[x]))
                            for x in solutionData.attributes ] )
        # now we compute the length in points.
        # we don't really have a way to do this so we take a heuristic
        # upper bound
        wLPoints = widthLeft * self.parameterValue['font size'] / 1.7
        wRPoints = widthRight * self.parameterValue['font size'] / 1.7
        # dimensions of the rectangle hull around the text we want to display
        width = wLPoints + wRPoints
        height = \
            ( self.parameterValue['font size'] + \
                  self.parameterValue['vertical padding'] ) *\
                  (len(solutionData.attributes) - 1)
#         for a in solutionData.attributes:
#             print a, solutionData.attributes[a]
        # starting coordinates
        if self.parameterValue['corner'] == 'top left' or \
                self.parameterValue['corner'] == 'bottom left':
            x = convertX(inputData.xmin)
        else:
            x = convertX(inputData.xmax) - width
        if self.parameterValue['corner'] == 'top left' or \
                self.parameterValue['corner'] == 'top right':
            y = convertY(inputData.ymax)
        else:
            y = convertY(inputData.ymin) + height
        # write something about every attribute
        font = Font(self.parameterValue['font size'],
                    self.parameterValue['font family'],
                    self.parameterValue['font style'])
        foreground = self.parameterValue['foreground colour']
        background = self.parameterValue['background colour']
        for attribute in solutionData.attributes:
            # only display attribute if it is selected
            if not self.parameterValue['display ' + attribute]:
                continue
            canvas.drawFancyText(attribute,
                                 x + self.parameterValue['x offset'],
                                 y + self.parameterValue['y offset'],
                                 font, foreground, background)
            canvas.drawFancyText(str(solutionData.attributes[attribute]),
                                 x + wLPoints + \
                                     self.parameterValue['horizontal padding']\
                                     + self.parameterValue['x offset'],
                                 y + self.parameterValue['y offset'],
                                 font, foreground, background)
            y -= self.parameterValue['font size'] + \
                self.parameterValue['vertical padding']
