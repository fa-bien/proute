#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: August 8th 2011 by Fabien Tricoire
#
import string

import vrpdata
import stylesheet
from functools import reduce

# additional padding for the map: forces a map wider than required to place
# just all nodes
mapPadding=.07

class CTPInputData(vrpdata.VrpInputData):
    problemType = 'CTP'
    # load a covering tour problem instance
    def loadData(self, fName):
        # a CTP has a baseline demand for each node, then an average demand
        # over all stochastic samples, as well as a capacity
        self.nodeAttributes += [ 'baseline demand', 'average demand',
                                 'capacity', 'opening cost' ]
        # trucks also have a capacity
        # dmax1 and dmax2 are used to determine whether nodes are covered
        # completely or partially
        self.globalAttributes += [ 'capacity',
                                   'number of vehicles',
                                   'number of nodes',
                                   'dmax1', 'dmax2',
                                   'distance matrix']
        self.nodes = []
        self.attributes = {}
        # section 1: header
        f = open(fName, 'r')
        line = f.readline()
        while line[0] == '#': line = f.readline()
        value = [ string.atoi(x) for x in line.split() ]
        self.attributes['number of nodes'] = value[0]
        self.attributes['number of vehicles'] = value[1]
        self.attributes['capacity'] = value[2]
        self.attributes['dmax1'] = value[4]
        self.attributes['dmax2'] = value[5]
        self.attributes['distance matrix'] = []
        nSamples = value[3]
        zeta = float(value[6])
        # section 2: node coordinates
        while len(self.nodes) < self.attributes['number of nodes']:
            line = f.readline()
            while line[0] == '#': line = f.readline()
            tokens = line.split()
            thisNode = {}
            thisNode['index'] = string.atoi(tokens[0])
            if len(tokens) > 3:
                thisNode['label'] = reduce(lambda x,y: x + ' ' + y, tokens[3:])
            else:
                thisNode['label'] = tokens[0]
            thisNode['is depot'] = True if thisNode['index'] == 0 else False
            thisNode['x'] = string.atof(tokens[1])
            thisNode['y'] =  string.atof(tokens[2])
            # we can finally add this node
            self.nodes.append(thisNode)
        # section 3: distance matrix
        while len(self.attributes['distance matrix']) < len(self.nodes):
            line = f.readline()
            while line[0] == '#': line = f.readline()
            value = [ string.atoi(x) for x in line.split() ]
            self.attributes['distance matrix'].append(value)
        # section 4: opening costs
        for n in range(len(self.nodes)-1):
            line = f.readline()
            while line[0] == '#': line = f.readline()
            value = [ string.atoi(x) for x in line.split() ]
            self.nodes[value[0]]['opening cost'] = value[1]
        # section 5: population sizes (aka demand)
        self.nodes[0]['demand'] = 0
        for n in range(len(self.nodes)-1):
            line = f.readline()
            while line[0] == '#': line = f.readline()
            value = [ string.atoi(x) for x in line.split() ]
            self.nodes[value[0]]['baseline demand'] = value[1]
        # section 6: capacity
        self.nodes[0]['capacity'] = 0
        for n in range(len(self.nodes)-1):
            line = f.readline()
            while line[0] == '#': line = f.readline()
            value = [ string.atoi(x) for x in line.split() ]
            self.nodes[value[0]]['capacity'] = value[1]
        # section 7: stochastic samples
        sampleFactors = [ [] for node in self.nodes ]
        for n in range(nSamples):
            line = f.readline()
            while line[0] == '#': line = f.readline()
            samples = [ string.atof(x) / zeta for x in line.split() ]
            # read sample values for 1 sample
            for index, sample in enumerate(samples):
                sampleFactors[index+1].append(sample)
        # now that all samples are read, we can compute the average demand
        # over all samples
        for node, samples in zip(self.nodes[1:], sampleFactors[1:]):
            node['average demand'] = node['baseline demand'] * \
                reduce(lambda x,y: x+y, samples) / nSamples
        # that's it for useful data
        f.close()
        # pre-compute a generous bounding box to allow for routes using road
        # network and going out of the minimal box
        xmin = min( [ node['x'] for node in self.nodes ] )
        ymin = min( [ node['y'] for node in self.nodes ] )
        xmax = max( [ node['x'] for node in self.nodes ] )
        ymax = max( [ node['y'] for node in self.nodes ] )
        offsetX = (xmax-xmin) * (mapPadding / 2.0)
        offsetY = (ymax-ymin) * (mapPadding / 2.0)
        self.xmin = xmin - offsetX
        self.ymin = ymin - offsetY
        self.xmax = xmax + offsetX
        self.ymax = ymax + offsetY
        # print 'done padding!', self.xmin, self.xmax, self.ymin, self.ymax
        
class CTPSolutionData(vrpdata.VrpSolutionData):
    problemType = 'CTP'
    # load a CTP solution by Gutjahr & Tricoire
    def loadData(self, fName, vrpData):
        # add vehicle load information
        self.routeArcAttributes += [ 'flow' ]
        self.routeNodeAttributes += [ 'quantity delivered' ]
        self.nodeAttributes += [ 'index', 'covered by', 'open delivery center' ]
        # all routes in the solution (lists of indices)
        self.routes = [ {'index':r, 'arcs':[], 'node information':[]}
                        for r in \
                            range(vrpData.attributes['number of vehicles']) ]
        # all nodes in the solution
        self.nodes = [ {'index':i, 'open delivery center':False}
                       for i in range(vrpData.attributes['number of nodes']) ]
        # temporary variables
        # process each line
        for line in open(fName).readlines():
            line = line.split()
            toks = string.replace(string.replace(line[0], ']', ' '),
                                  '[', ' ').split()
            if line[0][0] == 'x':
                route = string.atoi(toks[3])
                fromNode = string.atoi(toks[1])
                toNode = string.atoi(toks[2])
                flow = string.atoi(line[2])
                # now we can add this new arc to the proper route
                arc = {}
                arc['from'], arc['to'], arc['flow'] = fromNode, toNode, flow
                self.routes[route]['arcs'].append(arc)
            elif line[0][0] == 'z':
                route = string.atoi(toks[2])
                node = string.atoi(toks[1])
                self.routes[route]['node information'].append( {'index': node} )
                self.nodes[node]['open delivery center'] = True
            elif line[0][0] == 'y':
                i = string.atoi(toks[1])
                j = string.atoi(toks[2])
                self.nodes[i]['covered by'] = j

# style section
import sys

from style import *
import colours
# Display a rectangle proportional to the demand for each node, plus a second
# rectangle proportional to the capacity
class NodeDemandAndCapacityDisplayer( Style ):
    description = 'capacity and average demand'
    # both are used multiple times
    offsetInfo = IntParameterInfo(-20, 20)
    colourInfo = ColourParameterInfo()
    parameterInfo = {
        'x offset': offsetInfo,
        'capacity colour': colourInfo,
        'y offset': offsetInfo,
        'demand colour': colourInfo,
        'width': IntParameterInfo(1, 20),
        'max. height': IntParameterInfo(1, 100),
        #         'capacity contour':colourInfo,
        }
    defaultValue = {
        'min. height': 1,
        'max. height': 40,
        'width': 4,
        'demand colour': Colour(250, 2, 2, 255),
        'y offset': 4,
        'capacity colour': Colour(255, 185, 0, 255),
        'capacity contour': Colour(0, 0, 0, 255),
        'x offset': -5,
        }
    def initialise(self):
        self.requiredNodeAttributes += [ 'average demand', 'capacity' ]
        self.minCapacity = False
        self.maxCapacity = False
    #
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        # first compute min and max demand if it's the first time we're here
        if not self.minCapacity:
            capacities = [ node['capacity'] for node in inputData.nodes ]
            self.minCapacity, self.maxCapacity = \
                min(capacities), max(capacities)
            self.computeHeight =\
                util.intervalMapping(self.minCapacity, self.maxCapacity,
                                     self.parameterValue['min. height'],
                                     self.parameterValue['max. height'])
        allX, allY, allW, allHcap, allHdem = [], [], [], [], []
        for node in inputData.nodes:
            if (nodePredicate and not nodePredicate(node)) or node['is depot']:
                continue
            else:
                allX.append(convertX(node['x']) +
                            self.parameterValue['x offset'])
                allY.append(convertY(node['y']) +
                            self.parameterValue['y offset'])
                allW.append(self.parameterValue['width'])
                allHcap.append(self.computeHeight(node['capacity']))
                allHdem.append(self.computeHeight(node['average demand']))
        style = DrawingStyle(self.parameterValue['capacity colour'],
                      self.parameterValue['capacity colour'])
        canvas.drawRectangles(allX, allY, allW, allHcap, style,
                              referencePoint='southwest')
        style = DrawingStyle(self.parameterValue['demand colour'],
                      self.parameterValue['demand colour'])
        canvas.drawRectangles(allX, allY, allW, allHdem, style,
                              referencePoint='southeast')
                                 
# display coverage information for a covering tour problem solution
class CTPCoverageDisplayer( Style ):
    description = 'coverage from delivery centre'
    colourInfo = ColourParameterInfo()
    parameterInfo = {
        'full coverage arc colour': colourInfo,
        'thickness': IntParameterInfo(0, 20),
        'partial coverage arc colour': colourInfo,
        }
    defaultValue = {
        'partial coverage arc colour': colours.cornflowerblue,
        'thickness': 2,
        'full coverage arc colour': colours.applegreen,
        }
    def initialise(self):
        self.requiredSolutionNodeAttributes += ['covered by']
        self.requiredGlobalAttributes += ['dmax1', 'dmax2', 'distance matrix']
    #
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        # display coverage for each node if relevant
        style = DrawingStyle(lineThickness=self.parameterValue['thickness'])
        for node in solutionData.nodes:
            indexFrom = node['index']
            if 'covered by' in node:
                indexTo = node['covered by']
                # case where the node is 100% covered
                if inputData.attributes['distance matrix'][indexFrom][indexTo] \
                        <= inputData.attributes['dmax1']:
                    style.lineColour =\
                        self.parameterValue['full coverage arc colour']
                    style.lineStyle = 'solid'
                # case where the node is partially covered
                elif inputData.attributes['distance matrix']\
                        [indexFrom][indexTo] <= inputData.attributes['dmax2']:
                    style.lineColour =\
                        self.parameterValue['partial coverage arc colour']
                    style.lineStyle = 'dashed'
                # case where the node is too far to be even partially covered
                else:
                    continue
                # now we can draw this line
                canvas.drawLine(convertX(inputData.nodes[indexFrom]['x']),
                                convertY(inputData.nodes[indexFrom]['y']),
                                convertX(inputData.nodes[indexTo]['x']),
                                convertY(inputData.nodes[indexTo]['y']),
                                style)

# style for displaying CTP
class CTPStyleSheet(stylesheet.StyleSheet):
    defaultFor = [ 'CTP' ]
    # default stylesheet: display nodes and arcs in a simple way
    def loadDefault(self, keepAspectRatio=True):
        import basestyles, ctp, backgroundbitmap
        # True if aspect ratio should be kept, False otherwise
        self.keepAspectRatio = keepAspectRatio
        # initialize styles
        self.styles = []
#         # test: background picture
#         self.styles.append(backgroundbitmap.BackgroundBitmapDisplayer(\
#                 fName='data/ctp/map.png'))
        
        # display each route
        self.styles.append(\
            basestyles.RouteDisplayer({'draw depot arcs': True,
                                       'thickness': 2,
                                       'arc colour': colours.funkybrown}))
        
#         import googlemaps
#         # google map
#         self.styles.append(googlemaps.GoogleBetterMapDisplayer())
#         # google routes
#         self.styles.append(googlemaps.GoogleMapsRoutes())

        # display coverage information
        self.styles.append(\
            ctp.CTPCoverageDisplayer({'thickness': 2}))
        # basic style: display nodes
        self.styles.append(basestyles.NodeDisplayer({'node size': 3,
                                                     'hide unused nodes':
                                                         False}))
        # display a label for each node
        self.styles.append(basestyles.NodeLabelDisplayer({'hide unused nodes':
                                                              False}))
        # display each node's demand and capacity
        self.styles.append(ctp.NodeDemandAndCapacityDisplayer())
#         # display arc flows
#         self.styles.append(basestyles.ArcAttributeDisplayer(attribute='flow'))
