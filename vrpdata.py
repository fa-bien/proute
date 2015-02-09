#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: September 28th 2011 by Fabien Tricoire
#
# -*- coding: utf-8 -*-
# This file contains all routines to encapsulate and read all kinds of VRP data,
# be it input or solution data

import os
import sys
import string
import math

import util
import vrpexceptions
import findneighbour

widthNodeFactor = 3

# this class represents input data for any kind of routing problem
class VrpInputData(object):
    """
    This class encapsulates input data for a routing problem. That's mainly
    node information such as index, label, demand and coordinates.
    In order to load a new type of data, the normal procedure is to derive this
    class and define the loadData(fName). The constructor should not be
    overloaded.
    Notable attributes:
    - problemType (class attribute): string description of the problem handled
                                     by this class, e.g. 'CVRP' or 'VRPTW'.
    - instanceType (class attribute): string description of the instance type
                                      handled by this class, e.g. 'vrplib' or
                                      'Solomon'.
    - nodeAttributes: a list of attributes defined for each node for this
                      problem type, e.g. demand.
    - nodes: a list containing the data for each node.
    Node data is stored in dictionaries: for node i, nodes[i] is a dictionary
    containing the attributes and their values, e.g. {'label': 'node 1',
                                                      'demand': 12.
                                                      'x': 3,
                                                      'y': 6}
    
    """
    problemType = 'Change me'
    instanceType = 'default'
    # print the vrpData
    def __repr__(self):
        return self.__module__ + '.' + self.__class__.__name__ + \
            '(\'' + util.escapeFileName(self.fName) + '\')'
#         return self.__module__ + '.' + self.__class__.__name__ + \
#             '(fName=\'' + self.fName + '\')'
    
    def __init__(self, fName):
        """
        Do some preprocessing, load the data from fName and do some
        postprocessing. This method should be called from the outside,
        but it should never be overloaded.
        The loadData(fName) method should be defined instead.
        
        """
        # we store the file name for future reference
        self.fName = os.path.abspath(fName)
        self.name = os.path.basename(fName)
        # all node attributes for this VrpData
        # here we only ad the data present for all kinds of VRP
        self.nodeAttributes = [ 'index', 'label', 'x', 'y', 'is depot' ]
        self.globalAttributes = [ 'directed' ]
        # box bounds for plotting
        self.xmin = sys.maxint
        self.ymin = sys.maxint
        self.xmax = -sys.maxint
        self.ymax = -sys.maxint
        # load from file
        try:
            self.loadData(fName)
        except IOError as e:
            raise e
        except Exception as e:
            print 'Exception while loading a file:', e
            raise vrpexceptions.VrpInputFileFormatException(self.problemType,
                                                            fName)
        # generate missing information
        self.generateMissingData()
        # in case the travel time matrix doesn't exist, make a simple one
        try:
            self.travelTime
        except Exception as e:
            if len(self.nodes) < 500: # arbitrary
                self.computeEuclideanTravelTimes()
        # we must update the bounding box of all nodes we just read
        self.updateBoundingBox()
        # we also create a neighbour finder
#         self.neighbourFinder = findneighbour.MapNeighbourFinder(self)
        self.neighbourFinder = findneighbour.TwoDTreeNeighbourFinder(self)

    # get closest node to given coordinates
    def getNodeAtCoords(self, x, y, maxDist):
        index = self.neighbourFinder.getNodeIndexAtCoords(x, y, maxDist)
        return None if index is None else self.nodes[index]
        
    # complete missing data
    def generateMissingData(self):
        for node in self.nodes:
            if not 'is depot' in node:
                node['is depot'] = False
        # update node attributes with what's been loaded
        nodeAttributes = set()
        for node in self.nodes:
            for attribute in node:
                nodeAttributes.add(attribute)
        for x in nodeAttributes:
            if not x in self.nodeAttributes:
                self.nodeAttributes.append(x)
        
    # update bounding box with all node coordinates
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
        # compute width/height ratio
        self.width = 600 # len(self.nodes) * widthNodeFactor
        self.heightOverWidth =\
            float(self.ymax - self.ymin) / (self.xmax - self.xmin)
        self.height = int(self.width * self.heightOverWidth)
        self.heightOverWidth = float(self.height)/self.width
        if self.height > 600:
            self.height = 600.0
            self.width = self.height / self.heightOverWidth

    # compute travel times using euclidean distance
    def computeEuclideanTravelTimes(self):
        self.travelTime = [ [ round(math.hypot(n1['x'] - n2['x'],
                                               n1['y'] - n2['y'], ),
                                    2)
                              for n1 in self.nodes ]
                            for n2 in self.nodes ]
            
# this class stores solution data for any kind of routing problem
class VrpSolutionData(object):
    """
    This class encapsulates solution data for a routing problem.
    This includes route information (e.g. node sequence in the route) and node
    information (e.g. is a node visited or not).
    In order to load a new type of data, the normal procedure is to derive this
    class and define the loadData(fName). The constructor should not be
    overloaded.
    Most of the data here is stored in the routes attribute, which is a list
    of routes. Each route is a dictionary. Mandatory entries in this dictionary
    are 'index', 'arcs', 'node information'.
    Another common entry is 'node sequence', and new entries can be added by
    deriving this class and writing the loadData(fName) method.
    Notable attributes:
    - problemType (class attribute): string description of the problem handled
                                     by this class, e.g. 'CVRP' or 'VRPTW'.
    - solutionType (class attribute): string description of the solution type
                                      handled by this class, e.g. 'vrplib' or
                                      any other solution file format.
    - nodeAttributes: a list of attributes defined for each node for this
                      solution type, e.g. quantity delivered.
    - routeAttributes: a list of attributes defined for each route, e.g.
                       nodes, arcs or cost.
    - routeNodeAttributes: each route contains a 'node information' entry,
                           which is a list of dictionaries, one per node
                           visited by the route. This list defines which
                           entries such node dictionaries contain.
    - routeArcAttributes: same as above but with arcs. Mandatory entries are
                          'from' and 'to', both taking a node index as value.
                          User-defined values can be added when deriving this
                          class, e.g. 'travel speed' or 'passengers'.
                          
    """
    problemType = 'Change me'
    solutionType = 'default'
    
    # print the solutionData
    def __repr__(self):
        # trick: allows to load a solution with eval() provided there is a
        # vrpData instance loaded and called myData
        return self.__module__ + '.' + self.__class__.__name__ + \
            '(\'' + util.escapeFileName(self.fName) + '\', myData)'
#         return self.__module__ + '.' + self.__class__.__name__ + \
#             '(fName=\'' + self.fName + '\', vrpData=myData)'

    # standard constructor, always called. It does all kinds of necessary
    # initialisations then calls the specialised self.loadData() method
    def __init__(self, fName, vrpData):
        self.fName = os.path.abspath(fName)
        # solution attributes e.g. cost
        self.attributes = {}
        # route attributes (e.g. day, duration, etc)
        self.routeAttributes = [ 'index', 'arcs', 'node information' ]
        # route arc attributes: a route contains, among others, a set of arcs,
        # and to each of these arcs are associated attributes (e.g. departure
        # date, flow value, etc)
        self.routeArcAttributes = [ 'from', 'to' ]
        # route node attributes: information related to a route and a node,
        # e.g. quantity delivered by this route to this node
        self.routeNodeAttributes = [ 'index' ]
        # node information from the solution (e.g. index of node covering this
        # node in a covering tour problem)
        self.nodeAttributes = [ 'index' ]
        # identifier for this solution
        # default name, can be overwritten in subsequent load*() procedures
        # remove the extension by default
        self.name = os.path.basename(fName)
        lastDotIndex = self.name.rfind('.')
        if lastDotIndex > 0:
            self.name = self.name[:lastDotIndex]
        self.nodes = [ { 'index':node['index'] } for node in vrpData.nodes ]
        # load from file
        try:
            self.loadData(fName, vrpData)
        except IOError as e:
            raise e
        except Exception as e:
            print e
            raise vrpexceptions.SolutionFileFormatException(self.problemType,
                                                            fName)
        # in case the route information provided by loadData() is not complete:
        # generate the missing data e.g. generate node sequence from arcs
        self.populateRouteData(vrpData)
        # in case the route information provided by loadData() is inconsistent:
        # remove inconsistencies
        self.filterRouteData()
        # generate solution information on each node
        self.populateNodeData(vrpData)
        # generate scheduling information if needed and possible
        if 'release time' in vrpData.nodeAttributes \
                and 'due date' in vrpData.nodeAttributes \
                and not 'start of service' in self.nodeAttributes:
            self.computeSimpleScheduling(vrpData)
        # enrich solution data
        self.generateMetaData(vrpData)

    # generate information on nodes if it's missing
    def populateNodeData(self, vrpData):
        # case of an empty solution
        if self.routes != []:
            # for each node, store if it is visited or not
            # first we store each node visited
            visitedNodes = set( reduce( lambda x, y: x + y,
                                        [ route['node sequence']
                                          for route in self.routes ] ) )
        else:
            visitedNodes = set()
        # now we can set for each node whether it's visited or not
        # if the information is already stored we do not overwrite it, even if
        # it is inconsistent with visitedNodes: we assume that the previous
        # call to loadData() has the final word on what to store, and that it
        # has problem-specific knowledge that we lack here
        for node in self.nodes:
            if not 'used' in node:
                node['used'] = node['index'] in visitedNodes
        
    # generate missing data from route information
    def populateRouteData(self, vrpData):
        # assumption: all the routes are constructed in the same way
        if self.routes:
            if 'node sequence' in self.routes[0]:
                self.populateRouteDataFromNodeSequence()
            elif 'node information' in self.routes[0]:
                self.populateRouteDataFromNodes()
            elif 'arcs' in self.routes[0]:
                self.populateRouteDataFromArcs(vrpData)
        # enrich arc information
        for i, route in enumerate(self.routes):
            for arc in route['arcs']:
                arc['route'] = i
        self.routeArcAttributes.append('route')

    # generate missing data from route information
    def filterRouteData(self):
        # update node attributes with what's been loaded
        routeAttributes = set()
        for route in self.routes:
            for attribute in route:
                routeAttributes.add(attribute)
        self.routeAttributes = [ x for x in routeAttributes ]

    # generate node information and arc information from node sequence
    def populateRouteDataFromNodeSequence(self):
        for route in self.routes:
            # create node information if non-existing
            if not 'node information' in route:
                route['node information'] = [ {'index': i}
                                              for i in route['node sequence'] ]
            # same with arcs
            if not 'arcs' in route:
                route['arcs'] = []
                for i in range(len(route['node sequence'])-1):
#                     thisArc = {}
#                     a, b = route['node sequence'][i], \
#                         route['node sequence'][i+1]
#                     thisArc['from'], thisArc['to'] = a, b
                    route['arcs'].append( {'from': route['node sequence'][i],
                                           'to': route['node sequence'][i+1] } )
                    
    # generate node sequence information and arc information from nodes
    def populateRouteDataFromNodes(self):
        for route in self.routes:
            # create node information if non-existing
            if not 'node sequence' in route:
                route['node sequence'] = [ x['index']
                                          for x in route['node information'] ]
        # now the previous method can be used for generating arcs
        self.populateRouteDataFromNodeSequence()
                
    # generate node sequence information and node information from arcs
    def populateRouteDataFromArcs(self, vrpData):
        # reconstruct node sequence by filling an array of successors
        def sequenceFromArcs(arcs):
            successor = [ -1 for x in vrpData.nodes ]
            startingPoint = arcs[0]['from']
            for arc in arcs:
                successor[arc['from']] = arc['to']
                if vrpData.nodes[arc['from']]['is depot']:
                    startingPoint = arc['from']
            # now the successors are filled, we just need to follow them
            sequence = [ startingPoint ]
            next = successor[startingPoint]
            while next != -1 and next != startingPoint and not next in sequence:
                sequence.append(next)
                next = successor[next]
            if next == startingPoint:
                sequence.append(next)
            return sequence
        for route in self.routes:
            # create node information if non-existing
            if not 'node sequence' in route:
                route['node sequence'] = sequenceFromArcs(route['arcs'])
        # now the previous method can be used for generating nodes
        self.populateRouteDataFromNodeSequence()

    # generate scheduling information
    # precondition: release time and due date are defined numeric values
    # for each node in the input data
    def computeSimpleScheduling(self, vrpData):
        self.nodeAttributes += [ 'arrival time', 'start of service',
                                 'end of service' ]
        for route in self.routes:
            sequence = route['node sequence'] + [ route['node sequence'][-1] ]
            currentTime = 0
            for i, index in enumerate( sequence[:-1] ):
                if index != route['node information'][i]['index']:
                    print 'Inconsistent node information data in route'
                    return
                self.nodes[index]['arrival time'] = currentTime
                route['node information'][i]['arrival time'] = currentTime
                currentTime = max(vrpData.nodes[index]['release time'],
                                  currentTime)
                self.nodes[index]['start of service'] = currentTime
                route['node information'][i]['start of service'] = currentTime
                # generate missing info on the fly
                if not 'service time' in vrpData.nodes[index]:
                    vrpData.nodes[index]['service time'] = 0
                currentTime += vrpData.nodes[index]['service time']
                self.nodes[index]['end of service'] = currentTime
                route['node information'][i]['end of service'] = currentTime
                currentTime += vrpData.travelTime[index][sequence[i+1]]
        # add dummy data for unvisited nodes
        for node in self.nodes:
            if not node['used']:
                node['arrival time'] = -1
                node['start of service'] = -1
                node['end of service'] = -1

    # enrich solution data
    def generateMetaData(self, vrpData):
        self.attributes['# routes'] = len(self.routes)
        try:
            totalLength = 0
            for route in self.routes:
                for a, b in zip(route['node sequence'][:-1],
                                route['node sequence'][1:]):
                    totalLength += vrpData.travelTime[a][b]
            self.attributes['travel time'] = totalLength
        except Exception as e:
            pass
            
# this class encapsulates an empty solution
# this is useful for cases where we only want to display vrp data
class VrpEmptySolution(VrpSolutionData):
    def loadData(self, fName, vrpData):
        # all routes in the solution (lists of indices)
        self.routes = []
        self.name = vrpData.name
