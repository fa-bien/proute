#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: August 2nd 2011 by Fabien Tricoire
#
import string

import vrpdata
import stylesheet

class VRPTWInputData(vrpdata.VrpInputData):    
    problemType = 'VRPTW'
    instanceType = 'Solomon'
    # load a VRPTW instance
    def loadData(self, fName):
        # a VRPTW has a demand for each node, a service time and a TW
        self.nodeAttributes += [ 'demand', 'service time',
                                 'release time', 'due date' ]
        self.globalAttributes += [ 'capacity' ]
        self.nodes = []
        self.attributes = {}
        # load a Solomon instance
        cpt = 0
        for line in open(fName).readlines():
            tokens = line.split()
            if len(tokens) == 2 and tokens[0] != 'NUMBER':
                self.attributes['capacity'] = string.atoi(tokens[1])
            elif len(tokens) == 7:
                thisNode = {}
                thisNode['index'] = cpt
                thisNode['label'] = tokens[0]
                thisNode['is depot'] = True if cpt == 0 else False
                thisNode['demand'] = string.atof(tokens[3])
                thisNode['x'] = string.atof(tokens[1])
                thisNode['y'] = string.atof(tokens[2])
                thisNode['release time'] = string.atof(tokens[4])
                thisNode['due date'] = string.atof(tokens[5])
                thisNode['service time'] = string.atof(tokens[6])
                self.nodes.append(thisNode)
                cpt += 1
            else:
                continue

class VRPTWKritzingerSolutionData(vrpdata.VrpSolutionData):
    problemType = 'VRPTW'
    solutionType = 'Kritzinger'
    # load a VRPTW solution by Kritzinger to a VRPTW instance
    def loadData(self, fName, vrpData):
        # add vehicle load information
        self.routeAttributes += [ 'node sequence' ]
        # all routes in the solution (lists of indices)
        self.routes = []
        # process each line
        cpt = 0
        for line in open(fName).readlines():
            tokens = line.split()
            if len(tokens) == 0 or tokens[0] != 'route':
                continue
            else:
                thisRoute = {}
                thisRoute['index'] = string.atoi(tokens[1][:-1])
                thisRoute['node sequence'] = eval('[' + tokens[2] + ']')
                self.routes.append(thisRoute)
                cpt += 1

# style for displaying VRPTW
class VRPTWStyleSheet(stylesheet.StyleSheet):
    defaultFor = [ 'VRPTW' ]
    # default stylesheet: display nodes and arcs in a simple way
    def loadDefault(self, keepAspectRatio=True):
        import basestyles, timestyles
        # True if aspect ratio should be kept, False otherwise
        self.keepAspectRatio = keepAspectRatio
        # initialize styles
        self.styles = []
        # display each route
        self.styles.append(\
            basestyles.RouteDisplayer({'draw depot arcs': True}))
        # basic style: display nodes
        self.styles.append(basestyles.NodeDisplayer({'node size': 3}))
        # display a label for each node
        self.styles.append(basestyles.NodeLabelDisplayer())
#         # display each node's demand
#         self.styles.append(basestyles.NodeDemandDisplayer())
        # display time windows
        self.styles.append(timestyles.TimeDataDisplayer())
        
