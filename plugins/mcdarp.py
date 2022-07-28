# -*- coding: utf-8 -*-
#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: August 2nd 2011 by Fabien Tricoire
#
import string
import sys

import vrpdata
import vrpexceptions
import stylesheet
import util
import colours
from style import *

class MCDARPInputData(vrpdata.VrpInputData):
    problemType = 'MCDARP'
    # load a MCDARP instance
    def loadData(self, fName):
        # a MCDARP has a demand for each node
        self.nodeAttributes += [ 'type', 'destination', 'demand',
                                 'release time', 'due date', 'service time',
                                 'max ride time']
        self.globalAttributes += [ 'time matrix' ]
        self.nodes = []
        self.attributes = {}
        # load a MCDARP instance
        for line in open(fName).readlines():
            # skip comments
            if line[0] == '#':
                continue
            line = line.split()
            if len(line) == 4:
                nVehicles, nDepots, nRequests, nNodes = \
                    [ int(x) for x in line ]
                self.attributes['directed'] = True
                self.attributes['time matrix'] = [ [ 0 for i in range(nNodes)]
                                                   for j in range(nNodes) ]
                readLinesInMatrix = 0
            # case where we read vehicle information: we skip it
            elif len(line) == 5 and nVehicles > 0:
                nVehicles -= 1
            # case where we read a request
            elif len(line) == 9 and len(self.nodes) != nNodes:
                thisNode = {}
                thisNode['index'] = int(line[0])
                thisNode['label'] = line[0]
                thisNode['y'], thisNode['x'],\
                    thisNode['demand'], thisNode['service time'] = \
                    [ float(x) for x in line[1:5] ]
                thisNode['destination'] = int(line[5])
                thisNode['release time'] = float(line[6])
                thisNode['due date'] = float(line[7])
                thisNode['max ride time'] = float(line[8])
                thisNode['is depot'] = False
                thisNode['type'] = 'pickup'
                self.nodes.append(thisNode)
            # case of a delivery node
            elif len(line) == 6 and len(self.nodes) >= nRequests:
                thisNode = {}
                thisNode['index'] = int(line[0])
                thisNode['destination'] = int(line[0])
                thisNode['label'] = line[0]
                thisNode['x'] = float(line[2])
                thisNode['y'] = float(line[1])
                thisNode['service time'] = float(line[3])
                thisNode['release time'] = float(line[4])
                thisNode['due date'] = float(line[5])
                thisNode['is depot'] = False
                thisNode['type'] = 'delivery'
                thisNode['demand'] = 0
                self.nodes.append(thisNode)
            # case of a depot node
            elif len(line) == 5 and len(self.nodes) >= nNodes - nDepots:
                thisNode = {}
                thisNode['index'] = int(line[0])
                thisNode['label'] = line[0]
#                 thisNode['x'] = float(line[1])
#                 thisNode['y'] = float(line[2])
                thisNode['release time'] = float(line[3])
                thisNode['due date'] = float(line[4])
                thisNode['is depot'] = True
                thisNode['service time'] = 0
                thisNode['type'] = 'depot'
#                 self.nodes.append(thisNode)
            # line in the distance matrix
            elif len(line) == nNodes:
                self.attributes['time matrix'][readLinesInMatrix] = \
                    [ float(x) for x in line ]
                readLinesInMatrix += 1
            # this clause should never be reached
            else:
#                 print 'Corrupt line in MCDARP instance:', line
#                 print len(line), 'but there are', nNodes, 'node information'
                raise vrpexceptions.VrpInputFileFormatExcepton('MCDARP', fName)
        # standard attribute for time matrix
        self.travelTime = self.attributes['time matrix']
        # post-processing: refine time windows using max ride times
        for r in self.nodes:
            if r['type'] == 'pickup':
#                 print r
                delivery = r['destination']
                latestRT = self.nodes[delivery]['release time'] - \
                    r['max ride time'] - r['service time']
                earliestDD = self.nodes[delivery]['due date'] - \
                    self.attributes['time matrix'][r['index']][delivery] - \
                    r['service time']
                r['release time'] = max(r['release time'], latestRT)
                r['due date'] = min(r['due date'], earliestDD)
#         # test
#         self.nodes.insert(0, self.nodes[0])
                
    # update bounding box with all node coordinates
    # this version changes the aspect ratio in order to take into account the
    # Mercator projection
    def updateBoundingBox(self):
        for node in self.nodes:
            x, y = node['x'], node['y']
            if x > self.xmax:
                self.xmax = x
            if x < self.xmin:
                self.xmin = x
            if y > self.ymax:
                self.ymax = y
            if y < self.ymin:
                self.ymin = y
        # correction of the Mercator projection system
        yCenter = (self.ymax + self.ymin) / 2.0
        projectionFactor = util.degreeSecant(yCenter)
        # compute width/height ratio
        self.width = 600 # len(self.nodes) * widthNodeFactor
        self.heightOverWidth = projectionFactor * \
            float(self.ymax - self.ymin) / (self.xmax - self.xmin)
        self.height = int(self.width * self.heightOverWidth)
        self.heightOverWidth = float(self.height)/self.width
        if self.height > 600:
            self.height = 600.0
            self.width = self.height / self.heightOverWidth

class MCDARPSolutionData(vrpdata.VrpSolutionData):
    problemType = 'MCDARP'
    # load a MCDARP solution by Lehuédé, Parragh, Péton and Tricoire
    def loadData(self, fName, vrpData):
        self.routeAttributes += [ 'node sequence' ]
        # add vehicle load information
        self.routeArcAttributes += [ 'passengers', 'waiting time' ]
        self.nodeAttributes += [ 'beginning of service', 'ride time',
                                 'waiting time' ]
        # subroutine for MCDARP solution loading
        def makeMCDARPRoute(nodes, startTime):
            resultNodes = [ {'index': nodes[0], 'waiting time': 0} ]
            arcs = []
            passengers = [ nodes[0] ]
            for index, node in enumerate(nodes[:-1]):
                successor = nodes[index+1]
                # first we update waiting time
                if vrpData.nodes[successor]['type'] == 'pickup':
                    travelTime = \
                        vrpData.attributes['time matrix'][node][successor]
                    WT = startTime[index+1] - \
                        (startTime[index] +
                         vrpData.nodes[node]['service time'] +
                         travelTime)
                elif vrpData.nodes[successor]['type'] == 'delivery':
                    WT = vrpData.nodes[successor]['due date'] - \
                        startTime[index+1]
                else: # case of a depot
                    WT = 0
                resultNodes.append( {'index': successor,
                                     'waiting time': WT} )
                arcs.append( {'from': node,
                              'to': successor,
                              'waiting time': WT,
                              'passengers': [ x for x in passengers ]} )
                # now we can update passengers
                if vrpData.nodes[successor]['type'] == 'pickup':
                    passengers.append(successor)
                elif vrpData.nodes[successor]['type'] == 'delivery':
                    newPassengers = []
                    for passenger in passengers:
                        if vrpData.nodes[passenger]['destination'] != successor:
                            newPassengers.append(passenger)
                    passengers = newPassengers
                else: # case of a depot
                    pass
            return { 'node information': resultNodes,
                     'arcs': arcs,
                     'node sequence': nodes }
        # all routes in the solution (lists of indices)
        self.routes = []
        # open the file...
        fin = open(fName, 'r')
        # process the header line
        line = fin.readline()
        # now process routes
        while line[0] != '#':
            # read one route
            line = fin.readline()
            if line == 'Route:\n':
                line = fin.readline()
                tmpNodes = []
                tmpStartTime = []
                tmpRideTime = []
                while len(line) > 1 and line[1] == '(':
                    tokens = line.split()
                    tmpNodes.append(int(tokens[1]))
                    tmpStartTime.append(float(tokens[5]))
                    pwet = tokens[0].split('=')
                    if len(pwet) == 2:
                        tmpRideTime.append(float(pwet[1][:-1]))
                    else:
                        tmpRideTime.append(0)
                    line = fin.readline()
                # now we can build the route we read
                thisRoute = makeMCDARPRoute(tmpNodes[1:-1], tmpStartTime[1:-1])
                thisRoute['index'] = len(self.routes)
                self.routes.append(thisRoute)
                # update solution node attributes
                for node in thisRoute['node information']:
                    self.nodes[node['index']]['waiting time'] = \
                        node['waiting time']
                for index, ST, RT in zip(tmpNodes[1:-1],
                                         tmpStartTime[1:-1],
                                         tmpRideTime[1:-1]):
                    self.nodes[index]['beginning of service'] = ST
                    self.nodes[index]['ride time'] = RT
                for i in range(8):
                    line = fin.readline()
            elif line[:21] == '# Unplanned requests:':
                return
            else:
                print(line[:21])
                print('incorrect file format')
                print(line)
                sys.exit(0)

# style for displaying MCDARP
class MCDARPStyleSheet(stylesheet.StyleSheet):
    defaultFor = [ 'MCDARP' ]
    # default stylesheet: display nodes and arcs in a simple way
    def loadDefault(self, keepAspectRatio=True):
        import basestyles, timestyles, googlemaps, pdp
        # True if aspect ratio should be kept, False otherwise
        self.keepAspectRatio = keepAspectRatio
        # initialize styles
        self.styles = []
        # google map
        self.styles.append(googlemaps.GoogleBetterMapDisplayer())
        # precedence constraints
        self.styles.append(pdp.PickupToDelivery())
        # google routes
        self.styles.append(googlemaps.GoogleMapsRoutes())
#         # display each route
#         self.styles.append(basestyles.RouteColourDisplayer(drawDepotArcs=True,
#                                                            attribute='index',
#                                                            thickness=1) )
        # self.styles.append(\
        #     basestyles.RouteDisplayer(drawDepotArcs=True, thickness=1))
        # basic style: display nodes
        self.styles.append(pdp.PDPNodeDisplayer())
#         self.styles.append(basestyles.NodeDisplayer(nodeSize=3))
#         # display a label for each node
#         self.styles.append(basestyles.NodeLabelDisplayer())
        self.styles.append(timestyles.TimeDataDisplayer())
