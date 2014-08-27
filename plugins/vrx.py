#
# File created July 30th 2011 by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: August 21st 2011 by Fabien Tricoire
#
# -*- coding: utf-8 -*-

import string

import vrpdata
import stylesheet

class VRXInputData(vrpdata.VrpInputData):    
    problemType = 'VRX'
    
    # add dummy request for a depot at specified location, if it isn't there yet
    def addDepot(self, locationID):
        key = 'depot ' + locationID
        if not key in self.requestIDToIndex:
            location = self.locations[self.locationIDToIndex[locationID]]
            thisRequest = { 'label': key,
                            'index': len(self.requests),
                            'location': locationID,
                            'value': 0,
                            'demands': \
                                [ 0.0 for c in \
                                      self.attributes['commodities'] ],
                            'is depot': True,
                            'x': location['x'],
                            'y': location['y'],
                            'release time': 0,
                            'due date': 0,
                            }
            self.requestIDToIndex[key] = len(self.requests)
            self.requests.append(thisRequest)

    # load a VRX instance
    def loadData(self, fName):
        self.nodeAttributes += [ 'demands', 'release time', 'due date',
                                 'service time' ]
        self.globalAttributes += [ 'commodities',
                                   'capacity',
                                   'maximum duration' ]
        self.attributes = {}
        section = None
        self.locations = []
        self.locationIDToIndex = {}
        self.requests = []
        self.requestIDToIndex = {}
        self.depotsForRoute = {}
        # read a section at a time
        for rawLine in file(fName):
            # remove the comments
            line = rawLine[:rawLine.find('#')].rstrip()
            # empty lines
            if len(line) == 0: continue
            # end of a section
            elif line == '*END*':
                section = None
            # beginning of a section
            elif section is None:
                keyword = line.split()[0]
                if keyword == 'VRX':
                    section = 'header'
                # one-line header-type information
                elif keyword[4:] == '_METRIC':
                    pass
                # location section
                elif keyword == 'LOCATIONS':
                    section = 'locations'
                elif keyword == 'VEHICLES':
                    section = 'vehicles'
                elif keyword == 'VEHICLE_COST':
                    section = 'ignored'
                elif keyword == 'ROUTES':
                    section = 'vehicle availabilities'
                elif keyword == 'REQUESTS':
                    section = 'requests'
                elif keyword == 'REQUEST_TIMES':
                    section = 'request times'
            # case where we read a normal line in the file
            elif section != 'ignored':
                tokens = line.split()
                # section-dependent actions
                if section == 'header':
                    if tokens[0] == 'NAME':
                        self.name = tokens[1]
                    elif tokens[0] == 'COMMODITIES':
                        self.attributes['commodities'] = tokens[1:]
                elif section == 'locations':
                    if tokens[0] != 'ANYWHERE':
                        x, y = string.atof(tokens[1]), string.atof(tokens[2])
                    else:
                        x = min( [ a['x'] for a in self.locations] )
                        y = min( [ a['y'] for a in self.locations] )
                    thisLocation = { 'label': tokens[0],
                                     'index': len(self.locations),
                                     'x': x,
                                     'y': y,
                                     'is depot': True }
                    self.locationIDToIndex[tokens[0]] = len(self.locations)
                    self.locations.append(thisLocation)
                elif section == 'vehicles':
                    pass
                elif section == 'vehicle availabilities':
                    self.addDepot(tokens[2])
                    self.addDepot(tokens[3])
                    self.depotsForRoute[tokens[0]] = ('depot ' + tokens[2],
                                                      'depot ' + tokens[3])
                elif section == 'requests':
                    location = \
                        self.locations[self.locationIDToIndex[tokens[1]]]
                    thisRequest = { 'label': tokens[0],
                                    'index': len(self.requests),
                                    'x': location['x'],
                                    'y': location['y'],
                                    'location': tokens[1],
                                    'value': string.atof(tokens[2]),
                                    'demands': [ string.atof(x)
                                                 for x in tokens[3:] ],
                                    'is depot': False,
                                    }
                    self.requestIDToIndex[tokens[0]] = len(self.requests)
                    self.requests.append(thisRequest)
                elif section == 'request times':
                    index = self.requestIDToIndex[tokens[0]]
                    self.requests[index]['release time'] = \
                        string.atoi(tokens[1])
                    self.requests[index]['due date'] = string.atoi(tokens[2])
                    self.requests[index]['service time'] = \
                        string.atoi(tokens[3])
        # design choice: one node per request
        self.nodes = self.requests

# load a solution file produced by indigo
class VRXSolutionData(vrpdata.VrpSolutionData):
    problemType = 'VRX'
    solutionType = 'indigo'
    # load a VRX solution
    def loadData(self, fName, vrpData):
        # route attributes in a solution file produced by indigo
        self.routeAttributes += [ 'vehicle', 'vehicle type', 'ID' ]
        # it is possible to visit several times the same node for different
        # requests
        self.routeNodeAttributes += [ 'request' ]
        # all routes in the solution (lists of indices)
        self.routes = []
        thisRoute = None
        stage = None
        # process each line
        for rawLine in file(fName):
            # remove the comments
            line = rawLine[:rawLine.find('#')].rstrip()
            tokens = line.split()
            if len(tokens) < 2:
                continue
#             print tokens
            # case of a new vehicle
            if tokens[0] == 'Vehicle':
                currentVehicle = tokens[1]
                stage = None
                currentDuration = -1
            # case of a new route for this vehicle
            elif tokens[0] == 'Route':
                currentRoute = tokens[1]
            elif tokens[0] == 'Cost':
                currentCost = string.atoi(tokens[1])
            elif tokens[0] == 'Start:':
                currentStartTime = tokens[1]
            elif tokens[0] == 'Finish:':
                currentFinishTime = tokens[1]
            elif tokens[0] == 'Duration:':
                currentDuration = tokens[1]
            elif tokens[0] == 'Capacity:':
                currentCapacity = string.atoi(tokens[1])
            elif tokens[0] == 'Max' and tokens[1] == 'Load:':
                currentMaxLoad = string.atoi(tokens[2])
            # we already read the last route -> add it and exit
            elif tokens[0] == 'Unassigned' and tokens[1] != 'cost':
                self.routes.append(thisRoute)
                return
            # case of a new route
            elif tokens[0] == 'Count':
                stage = 'route'
                # append previous route if any
                if not thisRoute is None:
                    self.routes.append(thisRoute)
                # create new route
                thisRoute = { 'index': len(self.routes),
                              'ID': currentRoute,
                              'vehicle': currentVehicle,
                              'vehicle type': currentVehicle,
#                               'cost': currentCost,
                              'starting time': currentStartTime,
                              'finishing time': currentFinishTime,
                              'duration': currentDuration,
                              'capacity': currentCapacity,
                              'max. load': currentMaxLoad,
                              'node information': [],
                              }
#                 # add fields to route node attributes if they're not there yet
#                 for field in tokens[3:]:
#                     if not field in self.routeNodeAttributes:
#                         self.routeNodeAttributes.append(field)
                # use these fields for reading the route
                currentFields = tokens
            # case where we read information for one node
            elif stage == 'route':
                # special case: multi-day virtual visit
                if tokens[1][:5] == 'Reuse':
                    continue
                # special case: end of the route
                if tokens[0] == '(End)':
                    tokens = [ None ]  + tokens
                # special case: it's a depot
                if tokens[1] == '(Start)' or tokens[1] == '(End)':
                    requestID = 'depot ' + tokens[2]
                else:
                    requestID = tokens[1]
                thisNode = { 'index': vrpData.requestIDToIndex[requestID] }
                if tokens[1] != '(Start)':
                    for field, value in zip (currentFields[3:], tokens[3:]):
                        prevField = field
                        if field == 'Arrive':
                            thisNode['arrival time'] = value
                        elif field == 'LateArr':
                            thisNode['latest arrival time'] = value
                        elif field == 'Wait':
                            thisNode['waiting time'] = value
                        elif field == 'Start':
                            thisNode['service start'] = value
                        elif field == 'Depart':
                            thisNode['departure time'] = value
                        elif field == 'Cumm' and prevField == 'load':
                            thisNode['load'] = string.atoi(value)
                # finally add the node to current route
                thisRoute['node information'].append(thisNode)

# load a solution file produced by indigo
class VRX_CSVSolutionData(vrpdata.VrpSolutionData):
    problemType = 'VRX'
    solutionType = 'csv'
    # load a VRX solution
    def loadData(self, fName, vrpData):
        # route attributes in a solution file produced by indigo
        self.routeAttributes += [ 'vehicle', 'ID' ]
        # it is possible to visit several times the same node for different
        # requests
        self.routeNodeAttributes += [ 'request' ]
        # all routes in the solution (lists of indices)
        self.routes = []
        thisRoute = None
        stage = None
        # process each line
        for rawLine in file(fName):
            tokens = rawLine.split(',')
            if len(tokens) < 2:
                continue
#             print tokens
            # case of a new route
            if tokens[0] == 'Route':
                thisRoute = { 'index': len(self.routes),
                              'ID': tokens[1],
                              'node information': [],
                              }
            # vehicle for this route
            elif tokens[0] == 'Vehicle':
                thisRoute['vehicle'] = tokens[1]
            elif tokens[0] == 'Total' and tokens[1] == 'cost':
                thisRoute['cost'] = string.atoi(tokens[2])
            # case of a new route
            elif len(tokens) > 2 and tokens[2] == 'Customer':
                stage = 'route'
                # use these fields for reading the route
                currentFields = tokens
            # case where we read information for one node
            elif stage == 'route':
                if tokens[2] == '':
                    continue
                # special case: multi-day virtual visit
                if tokens[2][:5] == 'Reuse':
                    continue
                # special case: it's a depot
                if tokens[2] == '(Start)' or tokens[2] == '(End)':
                    requestID = 'depot ' + tokens[3]
                else:
                    requestID = tokens[2]
                thisNode = { 'index': vrpData.requestIDToIndex[requestID] }
                for field, value in zip (currentFields[4:], tokens[4:]):
                    if tokens[2] != '(Start)' and tokens[2] != '(End)':
                        if field == 'Arrive':
                            thisNode['arrival time'] = value
                        elif field == 'Wait':
                            thisNode['waiting time'] = value
                        elif field == 'Start':
                            thisNode['service start'] = value
                        elif field == 'Leave':
                            thisNode['departure time'] = value
                        elif field == 'Late-Start':
                            thisNode['latest arrival time'] = value
                # finally add the node to current route
                thisRoute['node information'].append(thisNode)
                # special case: end of the route
                if tokens[2] == '(End)':
                    self.routes.append(thisRoute)
                    stage = None

# load a .rt file
class VRXRouteSolutionData(vrpdata.VrpSolutionData):
    problemType = 'VRX'
    solutionType = '.rt'
    # load a VRX solution
    def loadData(self, fName, vrpData):
        # route attributes for a .rt file
        self.routeAttributes += [ 'node sequence',
                                  'vehicle', 'vehicle type', 'ID' ]
        # all routes in the solution (lists of indices)
        self.routes = []
        # process each line
        for rawLine in file(fName):
            # remove the comments
            line = rawLine[:rawLine.find('#')].rstrip()
            if line[:9] == 'Route-Veh':
                tokens = line.split()
                thisRoute = { 'index': len(self.routes),
                              'ID': tokens[1],
                              'vehicle': tokens[2],
                              'vehicle type': tokens[2][tokens[2].find('-'):],
                              }
                sequence = tokens[3:]
                start, finish = vrpData.depotsForRoute[tokens[1]]
                thisRoute['node sequence'] = \
                    [ vrpData.requestIDToIndex[i]
                      for i in [start] + sequence + [finish] ]
                self.routes.append(thisRoute)
            
# style for displaying VRX data
class VRXStyleSheet(stylesheet.StyleSheet):
    defaultFor = [ 'VRX' ]
    # default stylesheet: display nodes and arcs in a simple way
    def loadDefault(self, keepAspectRatio=True):
        import basestyles
        # True if aspect ratio should be kept, False otherwise
        self.keepAspectRatio = keepAspectRatio
        # initialize styles
        self.styles = []
        # display each route
        self.styles.append(\
            basestyles.RouteColourDisplayer({'draw depot arcs': True}))
        # basic style: display nodes
        self.styles.append(basestyles.NodeDisplayer(\
                parameters={ 'node size': 3,
                             'hide unused nodes': True,
                             }))
#         # display a label for each node
#         self.styles.append(basestyles.NodeLabelDisplayer(\
#                 parameters={ 'hide unused nodes':
#                                  True,
#                              }))
#         # display each node's demand
#         self.styles.append(basestyles.NodeDemandDisplayer(\
#                 parameters={ 'hide unused nodes':
#                                  True,
#                              }))
