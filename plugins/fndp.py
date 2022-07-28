#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: August 6th 2011 by Fabien Tricoire
#
import string
import sys

import vrpdata
import vrpexceptions
import stylesheet

class FNDPInputData(vrpdata.VrpInputData):
    problemType = 'FNDP'
    # load a free newspaper delivery problem
    def loadData(self, fName):
        self.nodeAttributes += [ 'demand', 'capacity', 'demand per period' ]
        self.nodes = []
        self.attributes = {'# periods': 0}
        # load a MCDARP instance
        for line in open(fName).readlines():
            if line[0] == '#':
                continue
            else:
                tokens = line.split(';')
                if len(tokens) == 7:
                    self.attributes['nNodes'], \
                        self.attributes['# periods'], \
                        nVehicles, \
                        self.attributes['capacity'], \
                        self.attributes['service time'], \
                        self.attributes['depot ID'], \
                        self.attributes['period duration'] = \
                        [ int(x) for x in tokens ]
                elif len(tokens) == self.attributes['# periods'] and \
                        not 'production schedule' in self.attributes:
                    self.attributes['production schedule'] = [ int(x)
                                                               for x in tokens ]
                elif len(tokens) == 5:
                    thisNode = {}
                    thisNode['index'] = int(tokens[0])
                    thisNode['label'] = int(tokens[0])
                    thisNode['demand'], thisNode['x'], thisNode['y'], \
                        thisNode['capacity'] = [ float(x)
                                                 for x in tokens[1:] ]
                    thisNode['is depot'] = \
                        thisNode['index'] == self.attributes['depot ID']
                    thisNode['demand per period'] = \
                        [ x * thisNode['demand'] / 100.0
                          for x in self.attributes['production schedule'] ]
                    self.nodes.append(thisNode)
        
class FNDPSolutionData(vrpdata.VrpSolutionData):
    problemType = 'FNDP'
    # load a free newspaper solution by Archetti et al.
    def loadData(self, fName, vrpData):
        self.routeAttributes += [ 'starting time' ]
        self.routeNodeAttributes += [ 'quantity' ]
        self.nodeAttributes += [ 'first period' ]
        self.routes = []
        for node in self.nodes:
            node['first period'] = sys.maxsize
        for line in open(fName).readlines():
            tokens = line.split()
            if tokens[0] == '***':
                continue
            elif tokens[1] != 'Trip':
#                 print 'incorrect file format'
#                 print line
                raise \
                    vrpexceptions.SolutionFileFormatException(self.problemType,
                                                              fName)
            else:
                nodes = [ int(x.split('(')[0])
                          for x in tokens[6:-3] ]
                rest = [ x.split('(')[1][:-1].split(':') for x in tokens[6:-3] ]
                period = [ int(x[0]) for x in rest ]
                qty = [ int(x[1]) for x in rest ]
                startingTime = int(tokens[5][:-1])
                routeNodes = [ {'index': node, 'quantity': quantity,
                                'period': period}
                               for node, quantity, period in
                               zip(nodes, qty, period) ]
                thisRoute = {'index': len(self.routes),
                             'node sequence': nodes,
                             'node information': routeNodes,
                             'starting time': startingTime }
                # update the period of first delivery for each node
                for node in routeNodes:
                    if self.nodes[node['index']]['first period'] \
                            > node['period']:
                        self.nodes[node['index']]['first period'] = \
                            node['period']
                # let's not forget to add the route...
                self.routes.append(thisRoute)

class FNDPStyleSheet(stylesheet.StyleSheet):
    defaultFor = [ 'FNDP' ]
    # default stylesheet: display nodes and arcs in a simple way
    def loadDefault(self, keepAspectRatio=True):
        import basestyles
        # True if aspect ratio should be kept, False otherwise
        self.keepAspectRatio = keepAspectRatio
        # initialize styles
        self.styles = []
        # display each route
        self.styles.append(basestyles.RouteColourDisplayer(\
                {'draw depot arcs':True,
                 'attribute': 'index',
                 'thickness': 1} ) )
        # basic style: display nodes
        self.styles.append(basestyles.NodeDisplayer({'node size': 2}))
#         # display a label for each node
#         self.styles.append(basestyles.NodeLabelDisplayer())
