#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: July 29th 2011 by Fabien Tricoire
#
# -*- coding: utf-8 -*-

import string

import vrpdata
import stylesheet

import cvrp
import ovrptw

class OVRPInputData(cvrp.CVRPInputData):    
    problemType = 'OVRP'

class OVRPSolutionData(ovrptw.OVRPTWKritzingerSolutionData):
    problemType = 'OVRP'
    solutionType = 'kritzinger'

# style for displaying CVRP
class OVRPStyleSheet(stylesheet.StyleSheet):
    defaultFor = [ 'OVRP' ]
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
