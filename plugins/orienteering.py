#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: August 1st 2011 by Fabien Tricoire
#
import string
import sys

import vrpdata
import stylesheet
import basestyles

class TOPInputData(vrpdata.VrpInputData):
    problemType = 'TOP'
    # load a team orienteering problem instance
    def loadData(self, fName):
        # a TOP has a  profit for each node
        self.nodeAttributes += [ 'profit' ]
        # max duration for a tour
        self.globalAttributes += [ '# vehicles', 'Tmax', '# nodes' ]
        self.nodes = []
        self.attributes = {}
        for line in open(fName).readlines():
            tokens = line.split()
            if len(tokens) == 2:
                if tokens[0] == 'n':
                    self.attributes['# nodes'] = string.atoi(tokens[1])
                elif tokens[0] == 'm':
                    self.attributes['# vehicles'] = string.atoi(tokens[1])
                elif tokens[0] == 'tmax':
                    self.attributes['Tmax'] = string.atof(tokens[1])
                else:
                    print('Incorrect file format for', fName)
                    sys.exit(0)
            elif len(tokens) == 3:
                thisNode = {'index': len(self.nodes)}
                thisNode['x'] = string.atof(tokens[0])
                thisNode['y'] = string.atof(tokens[1])
                thisNode['profit'] = string.atof(tokens[2])
                thisNode['label'] = str(len(self.nodes))
                thisNode['is depot'] = len(self.nodes) == 0 or \
                    len(self.nodes) == self.attributes['# nodes'] - 1
                self.nodes.append(thisNode)
            else:
                print('Incorrect file format for', fName)
                sys.exit(0)
                
class TOPSolutionData(vrpdata.VrpSolutionData):
    problemType = 'TOP'
    solutionType = 'tricoire'
    # load a TOP solution by Tricoire et al.
    def loadData(self, fName, vrpData):
        # add vehicle load information
        self.routeAttributes += [ 'node sequence' ]
        # all routes in the solution (lists of indices)
        self.routes = []
        for line in open(fName).readlines():
            tokens = line.split()
            if tokens[0] == 'Actual' and tokens[1] == 'tours':
                self.routes = []
            elif tokens[0] == 'Expected' and tokens[1] == 'profit':
                self.attributes['profit'] = string.atof(tokens[3])
            elif tokens[0] == 'Total' and tokens[1] == 'time' \
                    and tokens[2] == '=':
                self.attributes['duration'] = string.atof(tokens[3])
            elif tokens[0] == 'Tour:':
                nodes = eval('[' + tokens[1] + ']')
                thisRoute = {'index': len(self.routes),
                             'node sequence': nodes}
                self.routes.append(thisRoute)

class TOPStudentSolutionData(vrpdata.VrpSolutionData):
    problemType = 'TOP'
    solutionType = 'students'
    # load a TOP solution in the format used by students
    def loadData(self, fName, vrpData):
        # add vehicle load information
        self.routeAttributes += [ 'node sequence' ]
        # all routes in the solution (lists of indices)
        self.routes = []
        for line in open(fName).readlines():
            tokens = line.split()
            if tokens[0] == 'route' and tokens[1][-1] == ':':
                nodes = eval('[' + tokens[2] + ']')
                print(nodes)
                thisRoute = {'index': string.atoi(tokens[1][:-1]),
                             'node sequence': nodes}
                self.routes.append(thisRoute)
                
# style for displaying TOP
class TOPStyleSheet(stylesheet.StyleSheet):
    defaultFor = [ 'TOP' ]
    # default stylesheet: display nodes and arcs in a simple way
    def loadDefault(self, keepAspectRatio=True):
        import flexiblestyles
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
        self.styles.append(basestyles.NodeDisplayer({'node size': 2,
                                                     'hide unused nodes':
                                                         False}))
        # display profit for each node
        self.styles.append(\
            flexiblestyles.NodeAttributeAsRectangleDisplayer({\
                    'attribute': 'profit'}))
