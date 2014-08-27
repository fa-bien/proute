#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: August 2nd 2011 by Fabien Tricoire
#
# -*- coding: utf-8 -*-

import string

import vrpdata
import stylesheet

class CVRPInputData(vrpdata.VrpInputData):    
    problemType = 'CVRP'
    instanceType = 'CMT'
    # load a CVRP instance
    def loadData(self, fName):
        # a CVRP has a demand for each node
        self.nodeAttributes += [ 'demand' ]
        self.globalAttributes += [ 'capacity', 'maximum duration' ]
        self.nodes = []
        self.attributes = {}
        # load a Christofides, Mingozzi and Toth instance
        cpt = 0
        for line in file.readlines(file(fName)):
            line = line.split()
            if len(line) > 3:
                self.attributes['directed'] = False
                self.attributes['capacity'] = string.atoi(line[1])
                self.attributes['maximum duration'] = string.atoi(line[2])
            elif len(line) >= 2:
                thisNode = {}
                thisNode['index'] = cpt
                thisNode['label'] = str(cpt)
                thisNode['is depot'] = True if cpt == 0 else False
                thisNode['demand'] = string.atoi(line[2])\
                    if len(line) > 2 else 0
                thisNode['x'] = string.atof(line[0])
                thisNode['y'] = string.atof(line[1])
                self.nodes.append(thisNode)
                cpt += 1
            else:
                continue

class VRPLIBInputData(vrpdata.VrpInputData):    
    problemType = 'CVRP'
    instanceType = 'vrplib'
    # load a CVRP instance
    def loadData(self, fName):
        # a CVRP has a demand for each node
        self.nodeAttributes += [ 'demand' ]
        self.globalAttributes += [ 'capacity', 'maximum duration' ]
        self.nodes = []
        self.attributes = {}
        self.attributes['directed'] = False
        # load a VRPLIB instance
        section = 'header'
        for line in file.readlines(file(fName)):
            tokens = line.split()
            if section == 'header':
                if tokens[0] == 'NAME':
                    self.name = tokens[2]
                elif tokens[0] == 'DIMENSION':
                    nNodes = string.atoi(tokens[2])
                elif tokens[0] == 'CAPACITY':
                    self.attributes['capacity'] = string.atoi(tokens[2])
                elif tokens[0] == 'NODE_COORD_SECTION':
                    section = 'coords'
                    self.nodes = [ {} for x in range(nNodes) ]
                elif len(tokens) < 3:
                    raise vrpexceptions.VrpInputFileFormatException('vrplib',
                                                                    fName)
            elif section == 'coords':
                if tokens[0] == 'DEMAND_SECTION':
                    section = 'demand'
                elif len(tokens) == 3:
                    index = string.atoi(tokens[0])
                    x, y = [ string.atof(n) for n in tokens[1:] ]
                    index -= 1
                    label = tokens[0]
                    self.nodes[index]['index'] = index
                    self.nodes[index]['label'] = label
                    self.nodes[index]['x'] = x
                    self.nodes[index]['y'] = y
                    self.nodes[index]['is depot'] = False
                else:
                    raise vrpexceptions.VrpInputFileFormatException('vrplib',
                                                                    fName)
            elif section == 'demand':
                if tokens[0] == 'DEPOT_SECTION':
                    section = 'depot'
                elif len(tokens) == 2:
                    self.nodes[string.atoi(tokens[0])-1]['demand'] = \
                        string.atoi(tokens[1])
                else:
                    raise vrpexceptions.VrpInputFileFormatException('vrplib',
                                                                    fName)
            elif section == 'depot':
                if tokens[0] == 'EOF':
                    section = 'over'
                elif len(tokens) == 1:
                    self.nodes[string.atoi(tokens[0])-1]['is depot'] = True
                else:
                    raise vrpexceptions.VrpInputFileFormatException('vrplib',
                                                                    fName)
                    
class CVRPSolutionData(vrpdata.VrpSolutionData):
    problemType = 'CVRP'
    solutionType = 'tricoire'
    # load a CVRP solution by Tricoire to a CMT instance
    def loadData(self, fName, vrpData):
        # add vehicle load information
        self.routeAttributes += [ 'node sequence' ]
        # all routes in the solution (lists of indices)
        self.routes = []
        # process each line
        for line in file.readlines(file(fName)):
            line = line.split()
            if line[0] != 'route:':
                continue
            else:
                thisRoute = {}
                thisRoute['index'] = len(self.routes)
                thisRoute['node sequence'] = eval('[' + line[1] + ']')
                self.routes.append(thisRoute)

class VRPLIBSolutionData(vrpdata.VrpSolutionData):
    problemType = 'CVRP'
    solutionType = 'vrplib'
    # load a CVRP solution from the VRPLIB
    def loadData(self, fName, vrpData):
        # add vehicle load information
        self.routeAttributes += [ 'node sequence' ]
        # all routes in the solution (lists of indices)
        self.routes = []
        # process each line
        section = 'header'
        for line in file.readlines(file(fName)):
            tokens = line.split()
            if section == 'header':
                if tokens[0] == 'NAME':
                    self.name = tokens[2]
                elif tokens[0] == 'ROUTES':
                    nRoutes = string.atoi(tokens[2])
                elif tokens[0] == 'COST':
                    self.attributes['cost'] = string.atof(tokens[2])
                elif tokens[0] == '#R' or tokens[0] == 'SOLUTION_SECTION':
                    section = 'routes'
                    self.routes = [ {} for x in range(nRoutes) ]
                elif len(tokens) < 3:
                    raise vrpexceptions.SolutionFileFormatException('vrplib',
                                                                    fName)
            elif section == 'routes':
                if tokens[0] == 'DEPOT_SECTION':
                    section = 'depot'
                elif tokens[0][0] == '#':
                    pass
                elif len(tokens) >= 6:
                    nodes = [ string.atoi(n) for n in tokens[5:] ]
                    index = string.atoi(tokens[0]) - 1
                    self.routes[index]['node sequence'] = nodes
                    self.routes[index]['load'] = string.atoi(tokens[1])
                    self.routes[index]['cost'] = string.atof(tokens[2])
                    self.routes[index]['length'] = string.atof(tokens[3])
                    self.routes[index]['index'] = index
                else:
                    raise vrpexceptions.SolutionFileFormatException('vrplib',
                                                                    fName)
            elif section == 'depot':
                if tokens[0] == 'END':
                    section = 'over'
                elif len(tokens) == 1:
                    depot = string.atoi(tokens[0])-1
                    for r in self.routes:
                        r['node sequence'] = \
                            [depot] + r['node sequence'] + [depot]
                else:
                    raise vrpexceptions.SolutionFileFormatException('vrplib',
                                                                    fName)

# style for displaying CVRP
class CVRPStyleSheet(stylesheet.StyleSheet):
    defaultFor = [ 'CVRP' ]
    # default stylesheet: display nodes and arcs in a simple way
    def loadDefault(self, keepAspectRatio=True):
        import basestyles
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
        # display each node's demand
        self.styles.append(basestyles.NodeDemandDisplayer())
