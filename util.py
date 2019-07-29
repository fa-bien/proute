#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
#
import os
import pickle
import urllib.request, urllib.error, urllib.parse
import io
from math import *

import config

# useful general-purpose functions

# returns a function mapping input values between inputMin and inputMax to
# output values between outputMin and outputMax
# the mapping is linear
def intervalMapping(inputMin, inputMax, outputMin, outputMax):
    if inputMin == inputMax:
        return lambda x: (outputMax + outputMin) / 2.0
    else:
        return lambda x: outputMin\
            + (x - float(inputMin)) / (inputMax - inputMin)\
            * (outputMax - outputMin)

# same as above but uses a modulo so that the value always matches
def intervalMappingModulo(inputMin, inputMax,
                          outputMin, outputMax,
                          inputModulo):
    return lambda x: outputMin\
        + ( (x % inputModulo) - float(inputMin)) / (inputMax - inputMin)\
        * (outputMax - outputMin) #if x >= inputMin and x <= inputMax else None

# return a predicate returning true if the route has the right value for the
# specified attribute
def makeRoutePredicate(attribute, value):
    return lambda route: route[attribute] == value

# return a predicate returning true if the node is present in a route of
# solutionData satisfying routePredicate
def makeNodeInRoutePredicate(solutionData, routePredicate):
    acceptableIndices = set()
    for route in solutionData.routes:
        if routePredicate(route):
            for i in route['node sequence']:
                acceptableIndices.add(i)
    return lambda node: node['index'] in acceptableIndices

# return the end index of the longest common substring starting at index 0
def longestStartingSubstringIndex(strings):
    l = 0
    while l < len(strings[0]):
        for s in strings[1:]:
            if s[l] != strings[0][l]:
                return l
        l += 1
    # case where all strings start like the first one
    return l

# return the begin index of the longest common substring finishing at the end
# of each of the strings
def longestEndingSubstringIndex(strings):
    l = -1
    while -l < len(strings[0]):
        for s in strings[1:]:
            if s[l] != strings[0][l]:
                return l
        l -= 1
    return l

# reorder the strings given as parameter using the only part they have that is
# different
def reorder(strings):
    a = longestStartingSubstringIndex(strings)
    b = longestEndingSubstringIndex(strings)
    pairs = [ (int(s[a:b+1]) if len(s[a:b+1]) > 0 and s[a:b+1].isdigit() \
                   else 0, s)
              for s in strings ]
    pairs.sort()
    return [ s[1] for s in pairs ]

# return the names of available plugin modules
def getPluginNames():
    names = []
    # for each plugin directory: try to load the plugins in it
    for pluginDir in config.pluginDirectories:
        try:
            newNames = [ fName[:-3]
                         for fName in os.listdir(pluginDir)
                         if fName[-3:] == '.py' ]
            names += newNames
        except OSError as e:
            print('[Warning] unable to load plugins:', e)
    return names

# compute the secant of the given angle (given in degrees)
# This is useful to correct Mercator projections so that they look nice
# This is useful for every instance where node coordinates are provided as
# latitude and longitude
def degreeSecant(x):
    angle = x * pi / 180.0
    secant = 1.0 / cos(angle)
    return secant

# this class implements a simple persistent web cache
# it can retrieve documents with given URLs
# a prefix can be specified in case all URLs start with the same prefix
# For instance 'http://' is a valid prefix for all HTTP URLs
# A file name must also be specified. This file is where the cache reads/stores
# itself: it reads itself in the constructor if the file exists, and it stores
# itself in the destructor
class PersistentWebCache:
    def __init__(self, fileName, prefix=None):
        self.fileName = fileName
        self.prefix = prefix
        self.dict = {}
        self.modified = False
        # if the file already exists, try to load it
        if os.path.exists(self.fileName):
            try:
                f = open(self.fileName, 'r')
                loadedPrefix = pickle.load(f)
                if self.prefix == loadedPrefix:
                    self.dict = pickle.load(f)
                    if isinstance(self.dict, dict):
                        print('Loaded web cache from', self.fileName)
                    else:
                        self.dict = {}
                f.close()
            except Exception as e:
                print(e)
                f.close()
                        
    def get(self, key, reload=False):
        if reload or not key in self.dict:
            print('downloading', key)
            url = self.prefix + key
            data = urllib.request.urlopen(url).read()
            self.dict[key] = data
            self.modified = True
        else:
            data = self.dict[key]
        return io.StringIO(data)

    def __del__(self):
        if self.modified:
            f = open(self.fileName, 'w')
            pickle.dump(self.prefix, f)
            pickle.dump(self.dict, f)
            f.close()
            print('Stored web cache to', self.fileName)

# escape characters that might otherwise be interpreted in an inappropriate way
def escapeFileName(fileName):
    return fileName.replace('\\', '\\\\').replace('\'', '\\\'')

# proute program version
def version():
    return '0.1a'
# proute program copyright
def copyright():
    return '(C) Fabien Tricoire 2010-2011'
# proute program contact information
def contact():
    return 'f_tricoire@yahoo.fr'
