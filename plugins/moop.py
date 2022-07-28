#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: July 29th 2011 by Fabien Tricoire
#
import string

import vrpdata
import stylesheet

from style import *

class MOOPInputData(vrpdata.VrpInputData):    
    problemType = 'MOOP'
    instanceType = 'Schilde'
    # load a MOOP instance
    def loadData(self, fName):
        # a CVRP has a demand for each node
        self.nodeAttributes += [ 'scores' ]
        self.globalAttributes += [ 'maximum duration', '# objectives',
                                   'starting point', 'ending point' ]
        self.nodes = []
        self.attributes = {}
        self.attributes['directed'] = False
        for line in open(fName).readlines():
            # remove comments
            tokens = line.split('//')[0].split(',')
            # header line
            if len(tokens) == 2:
                if tokens[0] == 'S':
                    self.attributes['# objectives'] = int(tokens[1])
                elif tokens[0] == 'B':
                    self.attributes['starting point'] = int(tokens[1])
                elif tokens[0] == 'E':
                    self.attributes['ending point'] = int(tokens[1])
                else:
                    pass # useless information for displaying
            elif len(tokens) == 3 and tokens[0] == 'U':
                self.attributes['maximum duration'] = int(tokens[2])
            # case where we read a node
            elif len(tokens) == 5:
                thisNode = {'index': len(self.nodes),
                            'label':tokens[0],
                            'x': float(tokens[1]),
                            'y': float(tokens[2]),
                            'scores': [ int(x) for x in tokens[3:] ],
                            'is depot': False}
                self.nodes.append(thisNode)
            else:
                continue
        # set the two depots
        self.nodes[self.attributes['starting point']]['is depot'] = True
        self.nodes[self.attributes['ending point']]['is depot'] = True

class MOOPSolutionData(vrpdata.VrpSolutionData):
    problemType = 'MOOP'
    solutionType = 'tricoire'
    # load a MOOP solution by Tricoire
    # only loads one solution in the file (the first one)
    def loadData(self, fName, vrpData):
        # add vehicle load information
        self.routeAttributes += [ 'node sequence' ]
        # all routes in the solution (lists of indices)
        self.routes = []
        # process each line
        cpt = 0
        for line in open(fName).readlines():
            line = line.split()
            if line[0] != 'Tour:':
                continue
            else:
                thisRoute = {}
                thisRoute['index'] = cpt
                thisRoute['node sequence'] = \
                    [ int(x) for x in line[1:] ]
                self.routes.append(thisRoute)
                return

class MOOPStyleSheet(stylesheet.StyleSheet):
    defaultFor = ['MOOP']
    # default stylesheet: display nodes and arcs in a simple way
    def loadDefault(self, keepAspectRatio=True):
        import basestyles, flexiblestyles, colours
        # True if aspect ratio should be kept, False otherwise
        self.keepAspectRatio = keepAspectRatio
        # initialize styles
        self.styles = []
        # display each route
        self.styles.append(\
            basestyles.RouteDisplayer({\
                    'draw depot arcs': True,
                    'thickness': 1}))
        # basic style: display nodes
        self.styles.append(basestyles.NodeDisplayer())
        # display profit for each node
        self.styles.append(\
            flexiblestyles.NodeListAttributeAsRectanglesDisplayer({\
                    'attribute': 'scores',
                    'colours': ColourMap([ colours.rosybrown,
                                           colours.cornflowerblue ]),
                    }))
