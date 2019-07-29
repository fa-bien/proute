#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: August 8th 2011 by Fabien Tricoire
#
from style import *
import util
import colours

class TimeDataDisplayer(Style):
    description = 'time windows, waiting and service'
    # used multiple times
    colourInfo = ColourParameterInfo()
    parameterInfo = {
        'contour colour': colourInfo,
        'height': IntParameterInfo(3, 60),
        'background colour': colourInfo,
        'width': IntParameterInfo(6, 200),
        'time window colour': colourInfo,
        'waiting time colour': colourInfo,
        'service time colour': colourInfo,
        'y offset': IntParameterInfo(-20, 40),
        'thickness': IntParameterInfo(0, 20),
        'x offset': IntParameterInfo(-40, 20),
        'show waiting time': BoolParameterInfo(),
        'show service time': BoolParameterInfo(),
        }
    defaultValue = {
        'x offset': 4,
        'y offset': 4,
        'thickness': 1,
        'width': 20,
        'height': 7,
        'time window colour': colours.dimcyan,
        'waiting time colour': colours.darkorange,
        'service time colour': colours.red,
        'background colour': colours.white,
        'contour colour': colours.black,
        'show waiting time': True,
        'show service time': True,
        }
    def initialise(self):
        self.requiredNodeAttributes += [ 'release time', 'due date' ]
        # this can only be computed once data is known
        self.timeToX = None

    def setParameter(self, parameterName, parameterValue):
        Style.setParameter(self, parameterName, parameterValue)
        if parameterName == 'width':
            self.timeToX = util.intervalMapping(self.earliest,
                                                self.latest,
                                                0.0,
                                                self.parameterValue['width'])

    #
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        # first-time-only block
        if self.timeToX is None:
            self.earliest = \
                min( 0, min([ x['release time'] for x in inputData.nodes ]) )
            self.latest = max( [ x['due date'] for x in inputData.nodes ] )
            self.timeToX = util.intervalMapping(self.earliest, self.latest,
                                                0.0,
                                                self.parameterValue['width'])
        noDepotPred = lambda node: not node['is depot']
        if nodePredicate:
            newPredicate = \
                lambda node: nodePredicate(node) and noDepotPred(node)
        else:
            newPredicate = noDepotPred
        # now we can display everything we want
        # for each node display its background
        allX, allY, allW, allH = [], [], [], []
        style = DrawingStyle(self.parameterValue['background colour'],
                             self.parameterValue['background colour'],
                             lineThickness=self.parameterValue['thickness'])
        for node in inputData.nodes:
            if not newPredicate(node):
                continue
            allX.append(convertX(node['x']) + self.parameterValue['x offset'])
            allY.append(convertY(node['y']) + self.parameterValue['y offset'])
            allW.append(self.parameterValue['width'])
            allH.append(self.parameterValue['height'])
        canvas.drawRectangles(allX, allY, allW, allH, style,
                              referencePoint='southwest')
        # then display the TWs
        allX, allY, allW, allH = self.computeRectangles(inputData,
                                                        solutionData,
                                                        convertX,
                                                        convertY,
                                                        'release time',
                                                        'due date',
                                                        newPredicate)
        style = DrawingStyle(self.parameterValue['time window colour'],
                             self.parameterValue['time window colour'])
        canvas.drawRectangles(allX, allY, allW, allH, style,
                              referencePoint='southwest')
        # show waiting time if required
        visited = set([ x['index'] for x in solutionData.nodes if x['used'] ])
        if self.parameterValue['show waiting time']:
            allX, allY, allW, allH = self.computeRectangles(inputData,
                                                            solutionData,
                                                            convertX,
                                                            convertY,
                                                            '+arrival time',
                                                            '+start of service',
                                                            newPredicate,
                                                            .6)
            style = DrawingStyle(self.parameterValue['waiting time colour'],
                                 self.parameterValue['waiting time colour'])
            canvas.drawRectangles(allX, allY, allW, allH, style,
                                  referencePoint='southwest')
        # show service time if required
        if self.parameterValue['show service time']:
            allX, allY, allW, allH = self.computeRectangles(inputData,
                                                            solutionData,
                                                            convertX,
                                                            convertY,
                                                            '+start of service',
                                                            '+end of service',
                                                            newPredicate,
                                                            .6,
                                                            1)
            style = DrawingStyle(self.parameterValue['service time colour'],
                                 self.parameterValue['service time colour'])
            canvas.drawRectangles(allX, allY, allW, allH, style,
                                  referencePoint='southwest')
            
        # then the border around
        allX, allY, allW, allH = [], [], [], []
        style = DrawingStyle(self.parameterValue['contour colour'],
                             lineThickness=self.parameterValue['thickness'])
        for node in inputData.nodes:
            if not newPredicate(node):
                continue
            allX.append(convertX(node['x']) + self.parameterValue['x offset'])
            allY.append(convertY(node['y']) + self.parameterValue['y offset'])
            allW.append(self.parameterValue['width'])
            allH.append(self.parameterValue['height'])
        canvas.drawRectangles(allX, allY, allW, allH, style,
                              referencePoint='southwest')

    def computeRectangles(self,
                          inputData,
                          solutionData,
                          convertX,
                          convertY,
                          xMinParam,
                          xMaxParam,
                          nodePredicate,
                          heightRatio=1.0,
                          minWidth=0
                          ):
        allX, allY, allW, allH = [], [], [], []
        leftValues = \
            globalNodeAttributeValues(xMinParam, inputData, solutionData)
        rightValues = \
            globalNodeAttributeValues(xMaxParam, inputData, solutionData)
        for node, left, right in zip(inputData.nodes, leftValues, rightValues):
            if not nodePredicate is None and not nodePredicate(node):
                continue
            allX.append(convertX(node['x']) + \
                            self.parameterValue['x offset'] +
                        self.timeToX(left))
            allY.append(convertY(node['y']) + \
                            self.parameterValue['y offset'] + \
                            (1.0 - heightRatio)/2.0 * \
                            self.parameterValue['height'])
            thisW = self.timeToX(right) - self.timeToX(left)
            if right != left:
                thisW = max(minWidth, thisW)
            allW.append(thisW)
            allH.append(self.parameterValue['height'] * heightRatio)
        return allX, allY, allW, allH
