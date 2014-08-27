#
# File created around August 2nd 2011 by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: September 27th 2011 by Fabien Tricoire
#
# -*- coding: utf-8 -*-

import string

import vrpdata
import stylesheet
import vrpexceptions

# useful when reading a line of data...
def fillDict(keys, values):
    thisDict = {}
    for key, value in zip(keys, values):
        # try to eval, if it doesn't work then it's a string...
        try:
            thisDict[key] = eval(value)
        except Exception as e:
            thisDict[key] = value
    return thisDict

class PIFInputData(vrpdata.VrpInputData):    
    problemType = 'Generic'
    instanceType = 'PIF'
    # load an instance
    def loadData(self, fName):
        stage = 'header'
        self.nodes = []
        self.attributes = {}
        for line in file.readlines(file(fName)):
            line = line.rstrip()
            # ignore comments and empty lines
            if line[0] == '#' or len(line) == 0:
                pass
            # first header line
            elif stage is 'header':
                if line[:19] != 'proute input file v':
                    raise vrpexceptions.VrpInputFileFormatException('PIF',
                                                                    fName)
                else:
                    version = line[19:-1]
                    separator = line[-1]
                    stage = 'format'
            # all lines that are not header / comment / empty
            else:
                # case of an instance attribute
                if line[0] == separator:
                    key, value = line[1:].split(separator)
                    self.globalAttributes.append(key)
                    # try to eval, if it doesn't work then it's a string...
                    try:
                        self.attributes[key] = eval(value)
                    except Exception as e:
                        self.attributes[key] = value
                # line specifying node format
                elif stage == 'format':
                    fields = line.split(separator)
                    already = set(self.nodeAttributes)
                    for f in fields:
                        if not f in already:
                            self.nodeAttributes.append(f)
                    stage = 'content'
                # information for one node
                elif stage == 'content':
                    tokens = line.split(separator)
                    if len(tokens) != len(fields):
                        raise vrpexceptions.VrpInputFileFormatException('PIF',
                                                                       fName)
                    thisNode = fillDict(fields, tokens)
                    thisNode['index'] = len(self.nodes)
                    self.nodes.append(thisNode)

class PSFSolutionData(vrpdata.VrpSolutionData):
    problemType = 'Generic'
    solutionType = 'PSF'
    # load a CVRP solution by Tricoire to a CMT instance
    def loadData(self, fName, vrpData):
        # all routes in the solution (lists of indices)
        self.routes = []
        # extra solution data for all nodes
        self.nodes = [ { 'index': x['index'] } for x in vrpData.nodes ]
        stage = 'header'
        # process each line...
        for line in file.readlines(file(fName)):
            line = line.rstrip()
            # ignore comments and empty lines
            if line[0] == '#' or len(line) == 0:
                pass
            # first header line
            if stage is 'header':
                if line[:22] != 'proute solution file v':
                    raise vrpexceptions.VrpInputFileFormatException('PSF',
                                                                    fName)
                else:
                    version = line[22:-1]
                    separator = line[-1]
                    stage = 'format'
            # all lines that are not header / comment / empty
            else:
                # case of a global solution attribute
                if line[0] == separator:
                    key, value = line[1:].split(separator)
                     # try to eval, if it doesn't work then it's a string...
                    try:
                        self.attributes[key] = eval(value)
                    except Exception as e:
                        self.attributes[key] = value
                # line specifying format
                elif stage == 'format':
                    fields = line.split(separator)
                    # route information format
                    if fields[0] == 'route':
                        routeFields = fields[1:]
                        self.routeAttributes += routeFields
                        self.routeAttributes = \
                            [ x for x in set(self.routeAttributes) ]
                    # arc information format
                    elif fields[0] == 'arc':
                        arcFields = fields[1:]
                        self.routeArcAttributes += arcFields
                        self.routeArcAttributes = \
                            [ x for x in set(self.routeArcAttributes) ]
                    # route-node information format
                    elif fields[0] == 'routenode':
                        routeNodeFields = fields[1:]
                        self.routeNodeAttributes += routeNodeFields
                        self.routeNodeAttributes = \
                            [ x for x in set(self.routeNodeAttributes) ]
                        # logically after this line we switch to content
                        thisRoute = {}
                    # node information format
                    elif fields[0] == 'node':
                        nodeFields = fields[1:]
                        self.nodeAttributes += nodeFields
                        self.nodeAttributes = \
                            [ x for x in set(self.nodeAttributes) ]
                        # logically after this line we switch to content
                        thisRoute = {}
                        stage = 'content'
                # content information
                elif stage == 'content':
                    tokens = line.split(separator)
                    if tokens[0] == 'route':
                        # first we must add the previously read route to the
                        # list of routes
                        if thisRoute != {}:
                            self.routes.append(thisRoute)
                            thisRoute = {}
                        # consistency check
                        if len(tokens[1:]) != len(routeFields):
                            raise vrpexceptions.VrpInputFileFormatException(\
                                'PSF', fName)
                        thisRoute = fillDict(routeFields, tokens[1:])
                        thisRoute['index'] = len(self.routes)
                    elif tokens[0] == 'arc':
                        # consistency check
                        if len(tokens[1:]) != len(arcFields):
                            raise vrpexceptions.VrpInputFileFormatException(\
                                'PSF', fName)
                        thisArc = fillDict(arcFields, tokens[1:])
                        # finally we add the arc to the route
                        if not 'arcs' in thisRoute:
                            thisRoute['arcs'] = []
                        thisRoute['arcs'].append(thisArc)
                    elif tokens[0] == 'routenode':
                        # consistency check
                        if len(tokens[1:]) != len(routeNodeFields):
                            raise vrpexceptions.VrpInputFileFormatException(\
                                'PSF', fName)
                        thisNode = fillDict(routeNodeFields, tokens[1:])
                        # finally we add the node information to the route
                        if not 'nodes' in thisRoute:
                            thisRoute['nodes'] = []
                        thisRoute['nodes'].append(thisNode)
                    elif tokens[0] == 'node':
                        # consistency check
                        if len(tokens[1:]) != len(nodeFields):
                            raise vrpexceptions.VrpInputFileFormatException(\
                                'PSF', fName)
                        thisNode = fillDict(nodeFields, tokens[1:])
                        # finally we add the node information
                        self.nodes[thisNode['index']] = thisNode
        # let's not forget the last route
        self.routes.append(thisRoute)
