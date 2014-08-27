#
# File created August 21st by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: August 21st 2011 by Fabien Tricoire
#
# -*- coding: utf-8 -*-

import util
import math
import sys

mapDimension = 500
cellRangeInMap = 6

# this class allows to find the closest neighbour to a given node
class NeighbourFinder:
    pass
# fast but inaccurate: fixed-size 2D map
class MapNeighbourFinder(NeighbourFinder):
    def __init__(self, vrpData):
    # create a (n, n) matrix used as an approximation map to locate nodes:
    # each cell is either -1 (no node) or the index value of the closest node
    # in this region
        dimension = mapDimension#max(len(self.nodes), 100)
        self.map = [ [ -1 for i in range(dimension) ]
                     for j in range(dimension) ]
        # functions to convert coordinates to cells
        self.xCoordToRow = util.intervalMapping(vrpData.xmin, vrpData.xmax,
                                                0, dimension-1)
        self.yCoordToRow = util.intervalMapping(vrpData.ymin, vrpData.ymax,
                                                0, dimension-1)
        # now we fill it!
        for node in vrpData.nodes:
            i = int(round(self.xCoordToRow(node['x'])))
            j = int(round(self.yCoordToRow(node['y'])))
            for ioffset in range(1 - cellRangeInMap, cellRangeInMap):
                if i + ioffset < 0 or i + ioffset >= dimension:
                    continue
                for joffset in range(1 - cellRangeInMap, cellRangeInMap):
                    if j + joffset < 0 or j + joffset >= dimension:
                        continue
                    self.map[i + ioffset][j + joffset] = node['index']

    # if there is a node nearby the specified coordinates, return it
    # otherwise return None
    def getNodeIndexAtCoords(self, x, y, maxDist=None):
        i = int(round(self.xCoordToRow(x)))
        j = int(round(self.yCoordToRow(y)))
        if i < 0 or i >= len(self.map) or j < 0 or j >= len(self.map)\
                or self.map[i][j] == -1:
            return None
        return self.map[i][j]

# This class encapsulates a 2d-tree
horizontal = 0
vertical = 1
class TwoDTree:
    # create a 2d-tree
    def __init__(self, index, x, y, split=vertical):
        self.index = index
        self.x = x
        self.y = y
        self.split = split
        self.less = None
        self.more = None
    # add a node in a 2d-tree
    def insert(self, index, x, y):
        # fist determine in which subtree we must continue
        if self.split == vertical:
            less = x < self.x
        else:
            less = y < self.y
        if less and self.less is None:
            self.less = TwoDTree(index, x, y, (self.split + 1) % 2)
        elif less:
            self.less.insert(index, x, y)
        elif self.more is None:
            self.more = TwoDTree(index, x, y, (self.split + 1) % 2)
        else:
            self.more.insert(index, x, y)
    # find the closest node in the tree from x, y
    # returns a node index and a float (closest node found and distance to it)
    def findClosest(self, x, y, distUB=sys.maxint):
        # fist determine in which subtree we must continue
        if self.split == vertical:
            less = x < self.x
        else:
            less = y < self.y
        # special case: no successor on the most promising side
        if (less and self.less is None) or (not less and self.more is None):
            dist = sys.maxint
            node = None
        # general case 1
        elif less:
            node, dist = self.less.findClosest(x, y, distUB)
        # general case 2
        else:
            node, dist = self.more.findClosest(x, y, distUB)
        # now let's see if we can finish already
        distUB = min(dist, distUB)
        if self.split == vertical and math.fabs(x - self.x) >= distUB:
            return node, dist
        elif self.split == horizontal and math.fabs(y - self.y) >= distUB:
            return node, dist
        # case where we cannot finish now
        else:
            # first compare to this node
            thisDist = math.hypot(x - self.x, y - self.y)
            if thisDist < distUB:
                dist = distUB = thisDist
                node = self.index
            # next compare to the yet unexplored subtree
            if less and not self.more is None:
                    newNode, newDist = self.more.findClosest(x, y, distUB)
            elif not less and not self.less is None:
                    newNode, newDist = self.less.findClosest(x, y, distUB)
            else:
                newNode, newDist = None, sys.maxint
            if newDist < distUB:
                node, dist = newNode, newDist
            # finally...
            return node, dist
    # compute tree height
    def height(self):
        if self.less is None and self.more is None:
            return 1
        elif self.less is None:
            return 1 + self.more.height()
        elif self.more is None:
            return 1 + self.less.height()
        else:
            return 1 + max(self.less.height(), self.more.height())

# this class balances the 2d-tree at creation
class BalancedTwoDTree:
    # create a 2d-tree
    def __init__(self, nodes, split=vertical):
        self.split = split
        if len(nodes) == 0:
           self.node = None
        else:
            nodes.sort(key=lambda node: node['x' if split == vertical else 'y'])
            median = len(nodes) // 2
            self.node = nodes[median]['index']
            self.x = nodes[median]['x']
            self.y = nodes[median]['y']
            self.less = BalancedTwoDTree(nodes[:median], (self.split + 1) % 2)
            self.more = BalancedTwoDTree(nodes[median+1:], (self.split + 1) % 2)
    # find the closest node in the tree from x, y
    # returns a node and a float (closest node found and distance to it)
    def findClosest(self, x, y, distUB=sys.maxint):
        # termination case
        if self.node is None:
            return None, distUB
        # else, determine in which subtree we must look fist
        elif (self.split == vertical and x < self.x) or \
                (self.split == horizontal and y < self.y):
            firstSubtree, secondSubtree = self.less, self.more
        else:
            firstSubtree, secondSubtree = self.more, self.less
        # general case
        node, dist = firstSubtree.findClosest(x, y, distUB)
        # now let's see if we can finish already
        distUB = min(dist, distUB)
        if (self.split == vertical and math.fabs(x - self.x) >= distUB) or \
                (self.split == horizontal and math.fabs(y - self.y) >= distUB):
            return node, dist
        # case where we cannot finish now
        else:
            # first compare to this node
            thisDist = math.hypot(x - self.x, y - self.y)
            if thisDist < distUB:
                dist = distUB = thisDist
                node = self.node
            # next compare to the yet unexplored subtree
            newNode, newDist = secondSubtree.findClosest(x, y, distUB)
            if newDist < distUB:
                node, dist = newNode, newDist
            # finally...
            return node, dist
    # compute tree height
    def height(self):
        if self.node is None:
            return 0
        else:
            return 1 + max(self.less.height(), self.more.height())
        
# use a 2D-tree to find the nearest neighbour
class TwoDTreeNeighbourFinder(NeighbourFinder):
    def __init__(self, vrpData):
#         print '# elements:', len(vrpData.nodes)
        # construct the 2D-tree
        index, x, y = 0, vrpData.nodes[0]['x'], vrpData.nodes[0]['y']
        tree = TwoDTree(index, x, y)
        for i, node in enumerate(vrpData.nodes[1:]):
            index, x, y = i+1, node['x'], node['y']
            tree.insert(index, x, y)
#         print 'unbalanced tree height:', tree.height()
        # balanced version
        nodes = [ node for node in vrpData.nodes ]
        balanced = BalancedTwoDTree(nodes)
#         print 'balanced tree height:', balanced.height()
        # choose one
        self.tree = balanced
        # arbitrary value
        self.defaultDistUB = 0.01 * math.hypot(vrpData.xmax - vrpData.xmin,
                                               vrpData.ymax - vrpData.ymin)
        
    # if there is a node nearby the specified coordinates, return it
    # otherwise return None
    def getNodeIndexAtCoords(self, x, y, maxDist=None):
        if maxDist is None:
            maxDist = self.defaultDistUB
        index, distance = self.tree.findClosest(x, y, maxDist)
        return index
