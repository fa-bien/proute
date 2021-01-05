#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
#
# this file contains styles used to display input and solution data for routing
# problems
# Each class is a style
# Each input data style should implement a
#    paint(inputData, canvas, convertX, convertY) method
# Each solution data style should implement a
#    paint(inputData, solutionData, canvas, convertX, convertY) method
# additionally, predicates may be passed as parameters to perform partial
# painting, e.g. only paint a subset of the nodes
# additionally, a bounding box may be passed as parameter boundingBox as a
# 4-uple (xmin, ymin, xmax, ymax) of the coordinates of the box to paint

import random
import math
import os

import util

from vrpexceptions import MissingAttributeException, NotImplementedError

# generic colour encapsulation class
# arbitrary decision = components take integer values between 0 and 255
class Colour():
    def __init__(self, red, green, blue, alpha=255):
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha

    def getRGBA(self):
        return self.red, self.green, self.blue, self.alpha

    # allows to recreate the object
    def __repr__(self):
        return self.__module__ + '.Colour(' + str(self.red) + ',' + \
            str(self.green) + ',' + str(self.blue) + ',' + str(self.alpha) + ')'

# create a RGB colour from HSV values
# H in [0, 1), S in [0, 1], V in [0, 1]
class HSVColour(Colour):
    def __init__(self, H, S, V):
        C = V * S
        Hprime = H * 6
        X = C * (1 - math.fabs(Hprime % 2 - 1))
        if Hprime < 1:
            R, G, B = C, X, 0
        elif Hprime < 2:
            R, G, B = X, C, 0
        elif Hprime < 3:
            R, G, B = 0, C, X
        elif Hprime < 4:
            R, G, B = 0, X, C
        elif Hprime < 5:
            R, G, B = X, 0, C
        elif Hprime < 6:
            R, G, B = C, 0, X
        else:
            print('incorrect H, S, V values:', H, S, V)
        m = V - C
        self.red = int (255 * (R + m))
        self.green = int (255 * (G + m))
        self.blue = int (255 * (B + m))
        self.alpha = 255
    
# this class encapsulates a list of colours
class ColourMap():
    def __init__(self, colours=[]):
        self.colours = [ c for c in colours ]

    def __repr__(self):
        return self.__module__ + '.ColourMap(' + str(self.colours) + ')'

    def __getitem__(self, n):
        return self.colours[n % len(self.colours) ] if len(self.colours) > 0 \
            else Colour(0,0,0)

    def __len__(self):
        return len(self.colours)
    
# generate k spread colours
def generateSpreadColours(k):
    result = []
    import colourmapping
    import colours
    g = colourmapping.Gradient(ColourMap([colours.red,
                                          colours.yellow,
                                          colours.green,
                                          colours.cyan,
                                          colours.blue,
                                          colours.magenta,
                                          ]),
                               [0, 1],
                               )
    step = 1.0 / max(1, k-1)
    for i in range(k):
        result.append(g[i*step])
    return ColourMap(result)
# # generate k spread colours
# def generateSpreadColours(k):
#     result = []
#     nValues = k ** (1.0/3)
#     values = []
#     v = 255
#     while len(values) < nValues:
#         values.append(v)
#         v = v - 255/nValues
# #         v = (1+v) / 2
# #     values = [ 255 - x for x in values ]
#     for red in values:
#         for green in values:
#             for blue in values:
#                 result.append(Colour(red, green, blue))
#     return ColourMap(result[:k])
# # generate k spread colours
# def generateSpreadColours(k):
#     result = []
#     redMask = 2 ** 8 - 1
#     greenMask = redMask << 8
#     blueMask = greenMask << 8
#     step = (2 ** 24 ) / k
#     rawColours = [ step * i for i in range(1, k+1) ]
#     for c in rawColours:
#         red = c & redMask
#         green = (c & greenMask) >> 8
#         blue = (c & blueMask) >> 16
#         result.append(Colour(red, green, blue, 255))
#     return ColourMap(result)

# generate k colours spread using H,S,V space and golden ratio
def generateCleverSpreadColours(k):
    # our first colour: a bright red
    H, S, V = 0, 1.0, 1.0
    # our first colour: a bright blue
    H, S, V = .6, .99, .99
    # pastel red
    H, S, V = .005555555, .5, .95
    silverRatio = 2.0 / (1 + math.sqrt(5))
    return ColourMap( [ HSVColour((H + silverRatio * x) % 1, S, V)
                        for x in range(k) ] )

# generate k random colours
def generateRandomColours(k):
    return ColourMap([ randomColour() for i in range(k) ])

# standard easy-to-differentiate colours
#standardColours = wx.lib.colourdb.getColourList()

def randomColour():
    red = random.randint(0,255)
    green = random.randint(0,255)
    blue = random.randint(0,255)
    return Colour(red, green, blue, 255)

# generic font encapsulation class
class Font:
    def __init__(self, size, family=None, style='normal'):
        self.size = size
        self.family = family
        self.style = style
    
# generic drawing style encapsulation class: specifies line colour, thickness,
# filling colour etc
class DrawingStyle:
    def __init__(self,
                 lineColour=None,
                 fillColour=None,
                 lineThickness=1,
                 lineStyle='solid'):
        self._lineColour = lineColour
        self.lineThickness = lineThickness
        self.fillColour = fillColour
        self.lineStyle=lineStyle
        
    # property that returns the right line colour depending on thickness

    @property
    def lineColour(self):
        if self.lineThickness <= 0:
            return Colour(0, 0, 0, 255)
        else:
            return self._lineColour
        
    
# abstract style class
class Style( object ):
    """This is the abstract class for all styles used in stylesheets;
    the only mandatory methods are
    paint(self, inputData, solutionData,
          canvas, convertX, convertY,
          nodePredicate, routePredicate, arcPredicate,
          boundingBox)
    and
    setParameter(self, parameterName, parameterValue).

    Additionally, all parameters from a style should have a value in
    self.parameterValue and a ParameterInfo object in self.parameterInfo, both
    of which are dictionaries. For instance, in order to represent a diameter
    parameter, which can take values between 0 and 5, with value 3.5, this would
    hold:
    self.parameterValue['diameter'] == 3.5
    additionally, this would have to hold:
    self.parameterInfo['diameter'].acceptableValue(3.5) == True,
    which would probably mean that self.info['diameter'] has been initialized as
    FloatParameterInfo(0, 5);
    If self.parameterInfo has no entry for a given parameter, then this
    parameter is not supposed to be modified.
    
    """
    description = 'no description'
    def __init__(self, parameters={}, description=None):
        self.parameterValue = {}
        self.parameterInfo = {}
        # does this style have to be drawn only once if in a grid?
        self.oncePerGrid = False
        if description is None:
            self.description = self.__class__.description
        else:
            self.description = description
        # required attributes for this style
        self.requiredGlobalAttributes = [ ]
        self.requiredNodeAttributes = [ 'index', 'x', 'y' ]
        self.requiredRouteAttributes = [ ]#'index', 'arcs', 'node information' ]
        self.requiredArcAttributes = [ ]#'from', 'to' ]
        self.requiredSolutionNodeAttributes = [ ]#'index' ]
        # copy class parameter info to this instance
        for key in self.__class__.parameterInfo:
            self.parameterInfo[key] = self.__class__.parameterInfo[key]
        # do the same with parameter default values
        for key in self.__class__.defaultValue:
            self.parameterValue[key] = self.__class__.defaultValue[key]
        # now we can use the specified values
        for key in parameters:
            self.parameterValue[key] = parameters[key]
        # finally, load any additional information defined by the style
        self.initialise()

    # should be overloaded
    def initialise(self):
        pass

    def __repr__(self):
        return self.__module__ + '.' + self.__class__.__name__ + '(' + \
            'parameters=' + str(self.parameterValue) + ', ' + \
            'description=\'' + self.description +  '\', ' + \
            ')'

    # can be overloaded
    def setParameter(self, parameterName, parameterValue):
        self.parameterValue[parameterName] = parameterValue

    # this is the wrapper method called by the stylesheet class
    def paintData(self, inputData, solutionData,
                  canvas, convertX, convertY,
                  nodePredicate, routePredicate, arcPredicate,
                  boundingBox):
        try:
            self.preProcessAttributes(inputData, solutionData)
            self.paint(inputData, solutionData,
                       canvas, convertX, convertY,
                       nodePredicate, routePredicate, arcPredicate,
                       boundingBox)
        except Exception as e:
            print('Cannot paint using style ' + self.__class__.__name__ + \
                ': ' + str(e))
            
    def preProcessAttributes(self, vrpData, solutionData):
        for attr in self.requiredGlobalAttributes:
            if not attr in vrpData.globalAttributes:
                raise MissingAttributeException('instance attribute',
                                                attr)
        for attr in self.requiredNodeAttributes:
            if not attr in vrpData.nodeAttributes:
                raise MissingAttributeException('instance node attribute',
                                                attr)
        for attr in self.requiredRouteAttributes:
            if not attr in solutionData.routeAttributes:
                raise MissingAttributeException('route attribute',
                                                attr)
        for attr in self.requiredArcAttributes:
            if not attr in solutionData.routeArcAttributes:
                raise MissingAttributeException('route arc attribute',
                                                attr)
        for attr in self.requiredSolutionNodeAttributes:
            if not attr in solutionData.nodeAttributes:
                raise MissingAttributeException('solution node attribute',
                                                attr)
            
    def canBePainted(self):
        for param, value in list(self.parameterValue.items()):
            if not param in self.parameterInfo:
                return False
            if not self.parameterInfo[param].acceptableValue(value):
                print(self, param, value)
                return False
        return True
        
    def paint( self, inputData, solutionData,
               canvas, convertX, convertY,
               nodePredicate, routePredicate, arcPredicate,
               boundingBox):
        raise NotImplementedError( "Method paint() not implemented in style" )
        

# encapsulates style parameter information: type, possible values, etc
class ParameterInfo:
    """This is the abstract class for all ParameterInfo other classes, each of
    which should allow to encapsulate information for a given type of parameter,
    e.g. integer number with lower and upper bounds."""
    def __init__(self):
        pass
    def getType(self):
        return 'abstract parameter'
    def acceptableValue(self, value):
        return False

# boolean parameter information
class BoolParameterInfo(ParameterInfo):
    def getType(self):
        return 'boolean'
    def acceptableValue(self, value):
        return isinstance(value, bool)
    
# integer number parameter information
class IntParameterInfo(ParameterInfo):
    def __init__(self, LB, UB):
        self.LB = LB
        self.UB = UB
    def getType(self):
        return 'int'
    def acceptableValue(self, value):
        return isinstance(value, int) and self.LB <= value <= self.UB
        
# floating point number parameter information
class FloatParameterInfo(IntParameterInfo):
    def getType(self):
        return 'float'
    def acceptableValue(self, value):
        return isinstance(value, float) and self.LB <= value <= self.UB

# colour parameter information
class ColourParameterInfo(ParameterInfo):
    def getType(self):
        return 'colour'
    def acceptableValue(self, value):
        return isinstance(value, Colour)

# colour map parameter information
class ColourMapParameterInfo(ParameterInfo):
    def getType(self):
        return 'colour map'
    def acceptableValue(self, value):
        return isinstance(value, ColourMap)

# class for enumeration type based parameters
class EnumerationParameterInfo(ParameterInfo):
    def __init__(self, possibleValues):
        self.possibleValues = possibleValues
    def getType(self):
        return 'enumeration parameter'
    def acceptableValue(self, value):
        return value in self.possibleValues
    
# node attribute parameter information
# this version only considers the attributes in the input data
class NodeInputAttributeParameterInfo(EnumerationParameterInfo):
    def __init__(self, vrpData, acceptable=lambda x: True):
        if vrpData.nodes:
            candidates = [ x for x in vrpData.nodeAttributes ]
            for node in vrpData.nodes:
                candidates = [ x for x in candidates if acceptable(node[x]) ]
            self.possibleValues = [ x for x in candidates ]
        else:
            self.possibleValues = []
    def getType(self):
        return 'node attribute'
    
# node attribute parameter information
# this version considers both input and solution data attributes
class NodeGlobalAttributeParameterInfo(EnumerationParameterInfo):
    def __init__(self, vrpData, solutionData, acceptable=lambda x: True):
        if vrpData.nodes:
            node = vrpData.nodes[0]
            possibleInputValues = [ x for x in vrpData.nodeAttributes
                                    if x in node and acceptable(node[x]) ]
        else:
            possibleInputValues = []
        if solutionData.nodes:
            node = solutionData.nodes[0]
            possibleSolutionValues = \
                [ '+' + x for x in solutionData.nodeAttributes
                  if x in node and acceptable(node[x]) ]
        else:
            possibleSolutionValues = []
        self.possibleValues = possibleInputValues + possibleSolutionValues
    def getType(self):
        return 'node attribute'

# utility function to retrieve attribute values:
# if there is a heading '+' remove it and look up the attribute in solutionData,
# else look up the attribute in inputData
def globalNodeAttributeValues(attribute, inputData, solutionData,
                              acceptable=lambda x: True):
    if attribute[0] == '+':
        return [ node[attribute[1:]] for node in solutionData.nodes
                 if acceptable(node) ]
    else:
        return [ node[attribute] for node in inputData.nodes
                 if acceptable(node) ]

# utility function to retrieve attribute value:
# same as above but for just one node
def globalNodeAttributeValue(attribute, node, solutionData):
    if attribute[0] == '+':
        return solutionData.nodes[node['index']][attribute[1:]]
    else:
        return node[attribute]


    
# route attribute parameter information
class RouteAttributeParameterInfo(EnumerationParameterInfo):
    def __init__(self, solutionData, acceptable=lambda x: True):
        if solutionData.routes:
            route = solutionData.routes[0]
            self.possibleValues = [ x for x in solutionData.routeAttributes
                                    if x in route and acceptable(route[x]) ]
        else:
            self.possibleValues = []
    def getType(self):
        return 'route attribute'

# arc attribute parameter information
class ArcAttributeParameterInfo(EnumerationParameterInfo):
    def __init__(self, solutionData, acceptable=lambda x: True):
        if solutionData.routes:
            arc = solutionData.routes[0]['arcs'][0]
            self.possibleValues = [ x for x in solutionData.routeArcAttributes
                                    if x in arc and acceptable(arc[x]) ]
        else:
            self.possibleValues = []
    def getType(self):
        return 'arc attribute'

# # map parameter information: keys and values must match given ParameterInfos
# class MapParameterInfo(ParameterInfo):
#     def __init__(self, keyParameterInfo, valueParameterInfo):
#         self.keyParameterInfo = keyParameterInfo
#         self.valueParameterInfo = valueParameterInfo
#     def getType(self):
#         return 'map'
#     def acceptableValue(self, map):
#         if not isinstance(map, dict): return False
#         for key, value in map:
#             if not (keyParameterInfo.acceptableValue(key) and
#                     valueParameterInfo.acceptableValue(value)):
#                 return False
#         return True

# map parameter information: keys and values must match given ParameterInfos
class FileNameParameterInfo(ParameterInfo):
    def getType(self):
        return 'file name'
    def acceptableValue(self, fName):
        return os.path.exists(fName)
