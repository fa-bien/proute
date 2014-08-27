#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: July 29th 2011 by Fabien Tricoire
#
# -*- coding: utf-8 -*-
# this class uses unicode by default, i.e. every identifier string that can be
# used as a key in a dict will be coverted to unicode
import os
import string
import types

import vrpdata
import stylesheet
import util

# load available plugins
pluginNames = util.getPluginNames()
for name in pluginNames:
    exec 'import ' + name
    
# an instance of data loader handles various procedures
class DataLoader:
    def __init__(self):
        # local storage for what can load what
        # key = problem type, value = class
        # problem type should be in fact a tuple (type, subtype)
        self.vrpInputClasses = {}
        self.vrpSolutionClasses = {}
        self.styleSheetClasses = {}
        # get available plugins
        pluginNames = util.getPluginNames()
        # for each of these we can store what they allow to load
        for name in pluginNames:
            module = __import__(name)
            for item in dir(module):
                if item[:1] == '_': continue
                thisOne = module.__getattribute__(item)
                # interesting case: classes
                if type(thisOne) is types.TypeType:
                    # case 1: input data class
                    if issubclass(thisOne, vrpdata.VrpInputData):
                        key = (unicode(thisOne.problemType),
                               unicode(thisOne.instanceType))
                        self.vrpInputClasses[key] = thisOne
                        if not (key[0], u'default') in self.vrpInputClasses:
                            # add this class as default in case there isn't one
                            self.vrpInputClasses[(key[0], u'default')] = thisOne
                    # case 2: solution data class
                    elif issubclass(thisOne, vrpdata.VrpSolutionData):
                        key = (unicode(thisOne.problemType),
                               unicode(thisOne.solutionType))
                        self.vrpSolutionClasses[key] = thisOne
                        if not (key[0], u'default') in self.vrpSolutionClasses:
                            # add this class as default in case there isn't one
                            self.vrpSolutionClasses[(key[0], u'default')] = \
                                thisOne
                    # case 3: style sheet
                    elif issubclass(thisOne, stylesheet.StyleSheet):
                        for key in thisOne.defaultFor:
                            self.styleSheetClasses[unicode(key)] = thisOne
                    else:
                        # non-appropriate class for this context (e.g. Style)
                        pass

    def getInputClassFromType(self, type, subType):
        return self.vrpInputClasses[(type, subType)]
    
    def getSolutionClassFromType(self, type, subType):
        return self.vrpSolutionClasses[(type, subType)]

    # load the instance in file fName with specified type and subtype
    def loadInstance(self, fName, type, subtype):
        vrp = self.vrpInputClasses[(unicode(type), unicode(subtype))](fName)
        # finally we can return our freshly loaded instance
        return vrp
        
    # load the solutions in file fName to instance (input data) vrp with
    # specified type and subtype
    # if only a solution is returned then it is encapsulated in a list
    def loadSolution(self, fName, vrp, type, solutionSubtype):
        solution = \
            self.vrpSolutionClasses[(unicode(type),
                                     unicode(solutionSubtype))](fName, vrp)
        return solution
#         return solutions if solutions.__class__ == list else [ solutions ]

    # load the default style sheet for the given problem type
    def loadStyleSheet(self, type):
        return self.styleSheetClasses[unicode(type)]() \
            if unicode(type) in self.styleSheetClasses \
            else stylesheet.StyleSheet()

    # return available VRP types
    def getAvailableTypes(self):
        return list(set([ x[0] for x in self.vrpInputClasses ]))
        
    # return available instance subtypes for this type
    def getAvailableInstanceTypes(self, type):
        return list(set([ x[1]
                          for x in self.vrpInputClasses
                          if x[0] == type]))

    # return available solution subtypes for this type
    def getAvailableSolutionTypes(self, type):
        items = list(set([ x[1]
                           for x in self.vrpSolutionClasses
                           if x[0] == type and x[1] != u'default' ]))
        return [u'default'] + items
