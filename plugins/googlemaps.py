#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
#
from collections import defaultdict
import string
import sys
import os
import urllib.request, urllib.parse, urllib.error
import io
import json
from math import *

try:
    import Image
    # print('Loaded PIL')
except Exception as e:
    # print('PIL not installed, looking for Pillow')
    try:
        # is pillow installed?
        from PIL import Image
        # print('Loaded Pillow')
    except Exception as ee:
        print('Cannot find PIL or Pillow! Exiting...')
        sys.exit(65)

import vrpdata
import stylesheet
from style import *
import colours
import basestyles
import config

# Needed for Google Maps static API
API_KEY=''
apiFileName = os.path.join(config.userConfigDir, 'google_maps_api_key.txt')
try:
    with open(apiFileName) as f:
        API_KEY = f.read().replace('\n', '')
except Exception as e:
    print("""
    Cannot find Google Maps static API key, which is necessary for the
    Google Maps plugin. Download an API key for free at
    https://cloud.google.com/maps-platform/#get-started
    Then save it to""", apiFileName, '\n\n')

# use a cache to minimize redundant requests to google
cacheFileName = os.path.join(config.userConfigDir, 'googlemaps.cache')
googleMapsPrefix = 'https://maps.googleapis.com/maps/api/'

cache = util.PersistentWebCache(cacheFileName, googleMapsPrefix)

#print('Using cache:', cacheFileName)

# size of the google maps we download
googleMapSize = 512
# extra border we want to download in some cases to hide the logo in the middle
# logo will still be displayed in corners
googleExtraMapSize = 640 - 512
# Display a map...
class GoogleMapDisplayer( Style ):
    description = 'google map'
    parameterInfo = {}
    defaultValue = {}
    scalingMethod = Image.BICUBIC
    # xNW and yNW are the coordinates of the north-west corner point of the map
    # xSE and ySE are the coordinates of the south-east corner point of the map
    def initialise(self):
        # initialize the bitmap to a nil value to retrieve it the first time
        # we need it
        self.bitmap = None
    #
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        # if the map hasn't been loaded yet, load it
        if self.bitmap is None:
            self.getGoogleMap(inputData, convertX, convertY)
#             return
        # now we can resize the image to the portion we want to display
        # first we extract the useful portion of the map
        w, h = self.bitmap.size
        tmpConvertX = util.intervalMapping(self.xNW, self.xSE , 0, w)
        tmpConvertY = util.intervalMapping(self.yNW, self.ySE , 0, h)
        # the two corner points of the useful part of the bitmap
        topLeft = ( int(tmpConvertX(boundingBox[0])),
                    int(tmpConvertY(boundingBox[3])) )
        bottomRight = ( int(tmpConvertX(boundingBox[2])),
                        int(tmpConvertY(boundingBox[1])) )
        # dimensions of the new bitmap to generate
        newWidth = convertX(boundingBox[2]) - convertX(boundingBox[0])
        newHeight = convertY(boundingBox[3]) - convertY(boundingBox[1])
        if newHeight > 0 and newWidth > 0:
            newBitmap = self.bitmap.crop(topLeft + bottomRight).\
                                         resize( (int(newWidth),
                                                  int(newHeight)),
                                            self.scalingMethod )
            # finally we can paint the bitmap!
            canvas.drawBitmap(newBitmap, (convertX(boundingBox[0]),
                                          convertY(boundingBox[3])))

    # download the map and store it
    def getGoogleMap(self, inputData, convertX, convertY):
        # bound the map we want to get: take a wide interval around the
        # input data coordinate bounds
        self.centerX = (inputData.xmax + inputData.xmin) / 2.0
        self.centerY = (inputData.ymax + inputData.ymin) / 2.0
        # correction of the Mercator projection system
        self.projectionFactor = util.degreeSecant(self.centerY)
        # size of the bitmap we want: iteratively zoom until we should not
        # zoom any more
        # for a size of 256x256, the whole Earth is covered at zoom level 0
        zoomLevel = 0
        mapWidth = 360.0
        mapHeight = 360.0 / self.projectionFactor
        width = inputData.xmax - inputData.xmin
        height = inputData.ymax - inputData.ymin
        while mapWidth / 2 >= width and mapHeight / 2 >= height:
            zoomLevel += 1
            mapWidth /= 2
            mapHeight /= 2
        # finally we add 1 zoom level since we will take a 512x512 picture i.e.
        # four google maps tiles instead of 1
        zoomLevel += 1
        # print(mapWidth, mapHeight)
        # now that we have the optimal zoom level we can compute the coordinates
        # of the top left corner
        self.xNW = self.centerX - mapWidth / 2.0
        self.yNW = self.centerY + mapHeight / 2.0
        # bottom right corner
        self.xSE = self.centerX + mapWidth / 2.0
        self.ySE = self.centerY - mapHeight / 2.0
        # step 2: construct the URL
        prefix = 'staticmap?key=' + str(API_KEY)
        url = prefix + '&center=' + str(self.centerY) + ',' + \
            str(self.centerX) + '&zoom=' + str(zoomLevel) + \
            '&size=' + str(googleMapSize) + 'x' + str(googleMapSize) + \
            '&sensor=false&format=png'
#         print 'built url: ', url
        data = cache.get(url)
        self.bitmap = Image.open(data)
        print(self.xNW, self.xSE, self.ySE, self.yNW)
        print(inputData.xmin, inputData.xmax, inputData.ymin, inputData.ymax)
#         self.bitmap.show()

# This version takes a higher quality map
class GoogleBetterMapDisplayer(GoogleMapDisplayer):
    scalingMethod = Image.LINEAR
    description = 'Google map, improved quality'
    def getGoogleMap(self, inputData, convertX, convertY):
        # bound the map we want to get: take a wide interval around the
        # input data coordinate bounds
        self.centerX =   (inputData.xmax + inputData.xmin) / 2.0
        self.centerY =   (inputData.ymax + inputData.ymin) / 2.0
        # correction of the Mercator projection system
        self.projectionFactor = util.degreeSecant(self.centerY)
        # size of the bitmap we want: iteratively zoom until we should not
        # zoom any more
        # for a size of 256x256, the whole Earth is covered at zoom level 0
        zoomLevel = 0
        mapWidth = 360.0
        mapHeight = 360.0 / self.projectionFactor
        width = inputData.xmax - inputData.xmin
        height = inputData.ymax - inputData.ymin
        while mapWidth / 2 >= width and mapHeight / 2 >= height:
#         while mapWidth / 2 >= width and mapHeight / 2 >= height:
            zoomLevel += 1
            mapWidth /= 2
            mapHeight /= 2
        # finally we add 1 zoom level since we will take a 512x512 picture i.e.
        # four google maps tiles instead of 1
        zoomLevel += 1
        # now that we have the optimal zoom level we can compute the coordinates
        # of the top left corner
        self.xNW = self.centerX - mapWidth / 2.0
        self.yNW = self.centerY + mapHeight / 2.0
        # bottom right corner
        self.xSE = self.centerX + mapWidth / 2.0
        self.ySE = self.centerY - mapHeight / 2.0
        # step 2: construct the URL
        # in this version we divide the map into four parts,
        # and glue them together
        centerYN = (self.centerY + self.yNW) / 2
        centerYS = (self.centerY + self.ySE) / 2
        centerXW = (self.centerX + self.xNW) / 2
        centerXE = (self.centerX + self.xSE) / 2
        prefix = 'staticmap?key=' + str(API_KEY)
        urlNW = prefix + '&center=' + str(centerYN) + ',' + \
            str(centerXW) + '&zoom=' + str(zoomLevel + 1) + \
            '&size=' + str(googleMapSize) + 'x' + str(googleMapSize) + \
            '&sensor=false&format=png'
        urlNE = prefix + '&center=' + str(centerYN) + ',' + \
            str(centerXE) + '&zoom=' + str(zoomLevel + 1) + \
            '&size=' + str(googleMapSize) + 'x' + str(googleMapSize) + \
            '&sensor=false&format=png'
        urlSW = prefix + '&center=' + str(centerYS) + ',' + \
            str(centerXW) + '&zoom=' + str(zoomLevel + 1) + \
            '&size=' + str(googleMapSize) + 'x' + str(googleMapSize) + \
            '&sensor=false&format=png'
        urlSE = prefix + '&center=' + str(centerYS) + ',' + \
            str(centerXE) + '&zoom=' + str(zoomLevel + 1) + \
            '&size=' + str(googleMapSize) + 'x' + str(googleMapSize) + \
            '&sensor=false&format=png'
#         print 'built url: ', url
        dataNW = cache.get(urlNW)
        dataNE = cache.get(urlNE)
        dataSW = cache.get(urlSW)
        dataSE = cache.get(urlSE)
        bitmapNW = Image.open(dataNW)
        bitmapNE = Image.open(dataNE)
        bitmapSW = Image.open(dataSW)
        bitmapSE = Image.open(dataSE)
        bitmap = Image.new('RGBA', (googleMapSize*2, googleMapSize*2))
        bitmap.paste( bitmapNW, (0, 0) )
        bitmap.paste( bitmapNE, (googleMapSize, 0) )
        bitmap.paste( bitmapSW, (0, googleMapSize) )
        bitmap.paste( bitmapSE, (googleMapSize, googleMapSize) )
        self.bitmap = bitmap
#         self.bitmap.show()

# Display routes
class GoogleMapsRoutes( basestyles.RouteColourDisplayer ):
    description = 'google map routes'
    parameterInfo = {
        'draw depot arcs': BoolParameterInfo(),
        'thickness': IntParameterInfo(0, 20),
        'route offset correction': BoolParameterInfo(),
        'colours': ColourMapParameterInfo()
        }
    defaultValue = {
        'attribute': 'index',
        'draw depot arcs': True,
        'thickness': 5,
        'route offset correction': True,
        'colours': generateRandomColours(100),
        }
    def setParameter(self, parameterName, parameterValue):
        self.parameterValue[parameterName] = parameterValue
        # in case we (de)activate path correction, paths must be reloaded
        if parameterName == 'route offset correction':
            newPaths = [ [ None for j in i ]
                           for i in self.paths]
            self.paths = newPaths
    def initialise(self):
#         colours = [ Colour(95, 225, 249), Colour(176, 14, 104) ]
        basestyles.RouteColourDisplayer.initialise(self)
        # here we store paths in order to avoid retrieving them several times
        # two-dimensional array in which self.paths[i][j] is a list of 2-tuples,
        # each of which represents a point in the path between i and j
        self.paths = None
    #
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        # this block is only executed the first time the style is used
        if self.values is None:
            # we construct a unique value-colour mapping
            # we only want to accept attributes that return hashable values
            acceptable = lambda x: \
                not (isinstance(x, dict) or isinstance(x, list))
            self.parameterInfo['attribute'] = \
                RouteAttributeParameterInfo(solutionData, acceptable)
            self.mapping = defaultdict(lambda: len(self.mapping))
            self.values = set([ route[self.parameterValue['attribute']]
                                for route in solutionData.routes ])
            for v in self.values:
                self.mapping[v] = len(self.mapping)
        # also only the first time: allocate arc matrix
        if self.paths is None:
            self.paths = [ [ None for i in inputData.nodes ]
                           for j in inputData.nodes ]
        # now the main loop: for each route, paint it
        attribute = self.parameterValue['attribute']
        for route in solutionData.routes:
            if routePredicate and not routePredicate(route): continue
            # set the appropriate colour for this route
            thisColour = self.parameterValue['colours']\
                [self.mapping[route[attribute]]]
            style = DrawingStyle(thisColour,
                                 lineThickness=self.parameterValue['thickness'])
            # now we can draw the route
            for arc in route['arcs']:
                if arcPredicate and not arcPredicate(arc): continue
                i, j = arc['from'], arc['to']
                node1 = inputData.nodes[i]
                node2 = inputData.nodes[j]
                if self.parameterValue['draw depot arcs'] or\
                        ( not node1['is depot'] and not node2['is depot'] ):
                    # case where the arc has not been retrieved yet
                    if self.paths[i][j] is None:
                        self.paths[i][j] = self.retrievePath(inputData,
                                                             node1,
                                                             node2)
                    elif self.paths[i][j] == []:
                        self.paths[i][j] = self.retrievePath(inputData,
                                                             node1,
                                                             node2,
                                                             reload=True)
                    # now we can paint the path between node1 and node2
                    x, y = [convertX(node1['x'])], [convertY(node1['y'])]
                    for point in self.paths[i][j]:
                        x.append(convertX(point[0]))
                        y.append(convertY(point[1]))
                    # only paint if the polyline has already been retrieved
                    # (in some cases the query fails and should be performed
                    # again later)
                    x.append(convertX(node2['x']))
                    y.append(convertY(node2['y']))
                    if len(x) > 1:
                        canvas.drawPolyline(x, y, style)
                    
    # retrieve all nodes between node1 and node2
    # a list of 2-uple is returned, each of which represents a point on the path
    def retrievePath(self, inputData, node1, node2, reload=False):
        points = []
        prefix = 'directions/json?key=' + str(API_KEY)
        url = prefix + '&directions/json?sensor=false&origin=' + \
            str(node1['y']) + ',' + str(node1['x']) + '&destination=' + \
            str(node2['y']) + ',' + str(node2['x'])
#         print url
        data = json.load(cache.get(url, reload))
        for route in data['routes']:
            polyline = route['overview_polyline']['points']
            # polyline contains lat,long i.e. y,x
            polypoints = decodeGooglePolyline(polyline)
            for point in polypoints:
                points.append( (point[1], point[0]) )
        # post-processing: sometimes google's data is translated for some reason
        # here we try to detect and correct this
        if self.parameterValue['route offset correction'] and len(points) > 0:
            xOffsetStart = points[0][0] - node1['x']
            yOffsetStart = points[0][1] - node1['y']
            xOffsetFinish = points[-1][0] - node2['x']
            yOffsetFinish = points[-1][1] - node2['y']
            epsilon = 0.01
            # case where there is a stable non-negligible offset
            if (xOffsetFinish != 0 and abs(1 - xOffsetStart/xOffsetFinish)
                < epsilon):
                points = [ (e[0]-xOffsetStart, e[1])
                           for e in points ]
            if (yOffsetFinish != 0 and abs(1 - yOffsetStart/yOffsetFinish)
                < epsilon):
                points = [ (e[0], e[1]-yOffsetStart)
                           for e in points ]
#             epsilon = 0.001
#             if (xOffsetStart > epsilon and abs(xOffsetStart-xOffsetFinish)
#                 < epsilon) or \
#                 (yOffsetStart > epsilon and abs(yOffsetStart-yOffsetFinish)
#                  < epsilon):
#                 points = [ (e[0]-xOffsetStart, e[1]-yOffsetStart)
#                            for e in points ]
        return points

# decodes a google polyline
# see
#http://code.google.com/apis/maps/documentation/utilities/polylinealgorithm.html
# for details on the algorithm
def decodeGooglePolyline(polyline):
    values = []
    # position in the string
    index = 0
    while index < len(polyline):
        value = 0x20
        thisNumber = 0
        readBits = 0
        while value >= 0x20:
            # steps 11 and 10 and 9
            value = ord(polyline[index]) - 63
            # step 8
            modifiedValue = value - 0x20 if value > 0x20 else value
            # steps 7 and 6
            thisNumber |= modifiedValue << readBits
            readBits += 5
            index += 1
        # steps 5 and 4
        thisNumber = ~(thisNumber >> 1) if thisNumber & 1 else thisNumber >> 1
        # steps 3, 2, 1
        thisNumber /= 10.0 ** 5
        values.append(thisNumber)
    # now at the end we can reconstruct a list of points
    currentPoint = (values[0], values[1])
    points = [ currentPoint ]
    for i in range(2, len(values), 2):
        currentPoint = (currentPoint[0] + values[i],
                        currentPoint[1] + values[i+1])
        points.append(currentPoint)
    return points
