#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: July 29th 2011 by Fabien Tricoire
#
import string

import vrpdata
import stylesheet

from style import *

class PVRPInputData(vrpdata.VrpInputData):
    problemType = 'PVRP'
    instanceType = 'Cordeau'
    # load a PVRP instance
    def loadData(self, fName):
        # a PVRP has a demand for each node, as well as a frequency,
        # service time and possible combinations
        self.nodeAttributes += [ 'demand', 'service time',
                                 'frequency', 'combinations',
                                 'raw combinations' ]
        self.globalAttributes += [ 'capacity', 'maximum duration',
                                   'number of vehicles', 'number of nodes',
                                   'number of days' ]
        self.nodes = []
        self.attributes = {}
        # load a Cordeau, Gendreau and Laporte instance
        cpt = 0
        for line in open(fName).readlines():
            value = [ string.atof(x) for x in line.split() ]
            if len(value) == 4 and cpt == 0:
                if value[0] != 1:
                    print('Wrong file type for PVRP instance')
                    sys.exit(1)
                else:
                    self.attributes['number of vehicles'] = int(value[1])
                    self.attributes['number of nodes'] = int(value[2])
                    self.attributes['number of days'] = int(value[3])
                    self.attributes['maximum duration'] = []
                    self.attributes['capacity'] = []
            elif len(value) == 2 and cpt == 0:
                self.attributes['maximum duration'].append(int(value[0]))
                self.attributes['capacity'].append(int(value[1]))
                if len(self.attributes['capacity']) >\
                        self.attributes['number of days']:
                    print('Too many day-information lines in PVRP instance')
                    sys.exit(1)
            elif len(value) >= 7:
                thisNode = {}
                thisNode['index'] = cpt
                thisNode['label'] = str(int(value[0]))
                thisNode['is depot'] = True if cpt == 0 else False
                thisNode['x'] = value[1]
                thisNode['y'] = value[2]
                thisNode['service time'] = value[3]
                thisNode['demand'] = value[4]
                thisNode['frequency'] = int(value[5])
                thisNode['raw combinations'] = [ int(x)
                                                 for x in
                                                 value[7:7+int(value[6])] ]
                combinations = [ bin(x)[2:]
                                 for x in thisNode['raw combinations'] ]
                def expand_binary(c):
                    res = ''
                    for i in range(self.attributes['number of days'] - len(c)):
                        res += '0'
                    return res + c
                thisNode['combinations'] = [ expand_binary(x)
                                             for x in combinations]
                # we can finally add this node
                self.nodes.append(thisNode)
                cpt += 1
                
class PVRPSolutionData(vrpdata.VrpSolutionData):
    problemType = 'PVRP'
    # load a PVRP solution by Cacchiani, Hemmelmayr and Tricoire
    def loadData(self, fName, vrpData):
        # add vehicle load information
        self.routeAttributes += [ 'vehicle', 'day', 'cost', 'node sequence' ]
        # all routes in the solution (lists of indices)
        self.routes = []
        self.loadPVRP(fName)
        
    def loadPVRP(self, fName):
        # process each line
        cpt = 0
        for line in open(fName).readlines():
            line = line.split()
            # case where we read a whole log file
            if line[0] == 'Initialized':
                self.loadPVRPFromLog(fName)
                break
            if len(line) < 6:
                continue
            else:
                thisRoute = {}
                thisRoute['index'] = cpt
                thisRoute['day'] = string.atoi(line[0])
                thisRoute['vehicle'] = string.atoi(line[1])
                thisRoute['cost'] = string.atof(line[2])
                thisRoute['node sequence'] = \
                    [ string.atoi(x) for x in line[3:] ]
                self.routes.append(thisRoute)
                cpt += 1

# load a solution from a log file
class PVRPLogSolutionData(PVRPSolutionData):
    problemtype = 'PVRP'
    solutionType = 'log'
    # load a PVRP solution from a log file by Cacchiani, Hemmelmayr and Tricoire
    def loadData(self, fName, vrpData):
        # add vehicle load information
        self.routeAttributes += [ 'vehicle', 'day', 'node sequence' ]
        # all routes in the solution (lists of indices)
        self.routes = []
        self.loadPVRPFromLog(fName)
        
    # load a PVRP solution from a log file by Cacchiani et al.
    def loadPVRPFromLog(self, fName):
        # process each line
        cpt = 0
        for line in open(fName).readlines():
            line = line.split()
            # case where we read a new solution
            if len(line) == 0:
                continue
            elif line[0] == 'Found':
                self.routes = []
                vehicleForDay = {}
                cpt = 0
            elif len(line) >= 10 and line[9] == 'Route':
                thisRoute = {}
                thisRoute['index'] = len(self.routes)
                day = string.atoi(line[12])
                thisRoute['day'] = day
                if day in vehicleForDay:
                    thisRoute['vehicle'] = vehicleForDay[day]
                    vehicleForDay[day] += 1
                else:
                    thisRoute['vehicle'] = 1
                    vehicleForDay[day] = 2
                thisRoute['node sequence'] = \
                    [0] + [ string.atoi(x) for x in line[15:] ] + [0]
                self.routes.append(thisRoute)
                cpt += 1
            else: continue

    
# different style for displaying PVRP
class PVRPStyleSheet(stylesheet.StyleSheet):
    defaultFor = [ 'PVRP' ]
    # default stylesheet: display nodes and arcs in a simple way
    def loadDefault(self, keepAspectRatio=True):
        import basestyles
        # True if aspect ratio should be kept, False otherwise
        self.keepAspectRatio = keepAspectRatio
        # grid with one cell per day
        self.grid = True
        self.gridRouteAttribute = 'day'
        # initialize styles
        self.styles = []
        # display colourful routes
        self.styles.append(\
            basestyles.RouteColourDisplayer({\
                    'draw depot arcs': True,
                    'attribute': 'vehicle',
                    'thickness': 2,
                    'colours': ColourMap([ Colour(255,0,0,255),
                                           Colour(0,255,0,255),
                                           Colour(0,0,255,255),
                                           Colour(0,255,255,255),
                                           Colour(255,0,255,255),
                                           Colour(255,255,0,255),
                                           Colour(0,0,0,255) ])
                    }) )
        # basic style: display nodes
        self.styles.append(basestyles.NodeDisplayer({'node size': 1}))
        # display a label for each node
#         self.inputDataStyles.append(basestyles.NodeLabelDisplayer())
        # display each node's demand
#         self.inputDataStyles.append(basestyles.NodeDemandDisplayer())

