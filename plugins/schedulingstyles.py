#
# File created October 3rd 2011 by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: October 4th 2011 by Fabien Tricoire
#
from style import *

import colours

dateInputAttributes = [ 'release time', 'due date' ]
dateSolutionAttributes = [ 'start of service' ]

def computeNodeIndices(inputData,
                       solutionData,
                       nodePredicate,
                       routePredicate):
    nodeIndices = []
    indicesAsSet = set()
    for route in solutionData.routes:
        # add nodes from routes that are to be displayed
        if routePredicate is None or routePredicate(route):
            for nodeIndex in route['node sequence']:
                if nodePredicate is None or \
                        nodePredicate(inputData.nodes[nodeIndex]):
                    if not nodeIndex in indicesAsSet:
                        nodeIndices.append(nodeIndex)
                        indicesAsSet.add(nodeIndex)
    return nodeIndices

def computeHorizon(inputData,
                   solutionData):
    dates = []
    indices = list(range(len(inputData.nodes)))
    for index in indices:
        for attr in dateInputAttributes:
            if attr in inputData.nodes[index]:
                dates.append(inputData.nodes[index][attr])
        for attr in dateSolutionAttributes:
            if attr in solutionData.nodes[index]:
                dates.append(solutionData.nodes[index][attr])
    dMin, dMax = min(dates), max(dates)
    return dMin, dMax
    
class SchedulingNodes( Style ):
    description = 'scheduling'
    # used multiple times
    colourInfo = ColourParameterInfo()
    parameterInfo = {
        'alpha blending': IntParameterInfo(0, 255),
        'node guide': BoolParameterInfo(),
        'font colour': colourInfo,
        'font size': IntParameterInfo(6, 40),
        'time window': BoolParameterInfo(),
        'time window colour': colourInfo,
        'rect. height (input)': IntParameterInfo(6, 40),
        'waiting time': BoolParameterInfo(),
        'waiting time colour': colourInfo,
        'service time': BoolParameterInfo(),
        'service time colour': colourInfo,
        'rect. height (solution)': IntParameterInfo(6, 40),
        'lunch break': BoolParameterInfo(),
        'lunch break colour': colourInfo,
        'vehicle line': BoolParameterInfo(),
        'vehicle line colour': colourInfo,
        'vehicle line thickness': IntParameterInfo(0, 10),
        'time scale': BoolParameterInfo(),
        'time scale precision': IntParameterInfo(2, 20),
        'row height is fixed': BoolParameterInfo(),
        'row height': IntParameterInfo(5, 50),
        }
    defaultValue = {
        'alpha blending': 170,
        'node guide': True,
        'font colour': colours.black,
        'font size': 9,
        'rect. height (input)': 10,
        'time window': True,
        'time window colour': colours.dimcyan,
        'waiting time': True,
        'waiting time colour': colours.darkorange,
        'service time': True,
        'service time colour': colours.red,
        'rect. height (solution)': 6,
        'lunch break': False,
        'lunch break colour': colours.transparent,
        'vehicle line': True,
        'vehicle line colour': colours.black,
        'vehicle line thickness': 1,
        'time scale': True,
        'time scale precision': 5,
        'font family': 'Verdana',
        'font style': 'normal',
        'row height is fixed': False,
        'row height': 16,
        }

    #
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        # box where we'll draw
        xmin, ymin, xmax, ymax = boundingBox
        x0, y0, x1, y1 = \
            convertX(xmin), convertY(ymin), convertX(xmax), convertY(ymax)
        y0 += 2 * self.parameterValue['font size']
        x0 += 2 * self.parameterValue['font size']
#         # useless border
#         style = DrawingStyle(colours.red,
#                              None,
#                              1)
#         canvas.drawRectangle(x0, y0, x1 - x0, y1 - y0,
#                              style,
#                              referencePoint='southwest'
#                              )
        # compute useful nodes in the correct order
        nodeIndices = computeNodeIndices(inputData,
                                         solutionData,
                                         nodePredicate,
                                         routePredicate)
        if self.parameterValue['row height is fixed']:
            rowHeight = self.parameterValue['row height']
        else:
            rowHeight = (y1 - y0) / len(nodeIndices)
        halfRowHeight = rowHeight / 2.0
        inputHalfRectHeight = self.parameterValue['rect. height (input)'] / 2.0
        solutionHalfRectHeight = \
            self.parameterValue['rect. height (solution)'] / 2.0
        halfRectHeight = max (inputHalfRectHeight, solutionHalfRectHeight)
        indexToRow = {}
        for index in nodeIndices:
            indexToRow[index] = len(indexToRow)
        # time horizon
        dMin, dMax = computeHorizon(inputData,
                                    solutionData)
        # convert time to x coordinate
        timeToX = util.intervalMapping(dMin, dMax, x0, x1)
        # global font for this style
        font = Font(self.parameterValue['font size'],
                    self.parameterValue['font family'],
                    self.parameterValue['font style'])
        fontColour = self.parameterValue['font colour']
        # display time scale if needed
        if self.parameterValue['time scale']:
            style=DrawingStyle(lineColour=colours.black,
                               lineThickness=1)
            canvas.drawLine(x0, y0, x1, y0, style)
            for i in range(self.parameterValue['time scale precision']):
                value = i * (dMax - dMin) \
                    / self.parameterValue['time scale precision']
                canvas.drawLine( timeToX(value),
                                 y0,
                                 timeToX(value),
                                 y0 - self.parameterValue['font size'] / 3.0,
                                 style)
                canvas.drawFancyText(str(value),
                                     timeToX(value),
                                     y0 - self.parameterValue['font size'],
                                     font, fontColour, fontColour,
                                     referencePoint='centre')
        # list of things to display (input and solution)
        inputRectangleInfo, solutionRectangleInfo = \
            self.initialiseRectangles()
        # now fill this with data
        # First, input data
        for rect in inputRectangleInfo:
            for nodeIndex in indexToRow:
                row = indexToRow[nodeIndex]
                begin = timeToX(inputData.nodes[nodeIndex][rect['begin']])
                end = timeToX(inputData.nodes[nodeIndex][rect['end']])
                rect['xs'].append(begin)
                rect['ys'].append(y0 + row * rowHeight + \
                                      halfRowHeight + inputHalfRectHeight)
                rect['ws'].append(end - begin)
                rect['hs'].append(self.parameterValue['rect. height (input)'])
        # Next, solution data
        for rect in solutionRectangleInfo:
            for route in solutionData.routes:
                if routePredicate and not routePredicate(route):
                    continue
                for node in route['node information']:
                    nodeIndex = node['index']
                    if not nodeIndex in indexToRow:
                        continue
                    row = indexToRow[nodeIndex]
                    begin = timeToX(node[rect['begin']])
                    end = timeToX(node[rect['end']])
                    # even tiny intervals should be displayed
                    if node[rect['begin']] != node[rect['end']]:
                        end = max(end, begin + 1)
                    rect['xs'].append(begin)
                    rect['ys'].append(y0 + row * rowHeight + halfRowHeight + \
                                          solutionHalfRectHeight)
                    rect['ws'].append(end - begin)
                    rect['hs'].append(\
                        self.parameterValue['rect. height (solution)'])
        # for each node, display various stuff
        for nodeIndex in indexToRow:
            index = nodeIndex
            row = indexToRow[index]
            yBase = y0 + row * rowHeight + halfRowHeight
            # node guide
            if self.parameterValue['node guide']:
                y = yBase + self.parameterValue['font size'] / 2.0
                canvas.drawText(str(index),
                                x0 - 2 * self.parameterValue['font size'], y,
                                font, fontColour, fontColour)
                # line for each node
                canvas.drawLine(x0, yBase, x1, yBase,
                                DrawingStyle(colours.funkygreen,
                                             colours.funkygreen,
                                             .1))
        # now we can display all the rectangle
        for rect in inputRectangleInfo + solutionRectangleInfo:
            colour = rect['colour']
            colour.alpha = self.parameterValue['alpha blending']
            canvas.drawRectangles(rect['xs'], rect['ys'],
                                  rect['ws'], rect['hs'],
                                  DrawingStyle(colour, colour, 0),
                                  'northwest')
        # display routes
        if self.parameterValue['vehicle line']:
            colour = self.parameterValue['vehicle line colour']
            colour.alpha = self.parameterValue['alpha blending']
            style = DrawingStyle(colour, colour,
                                 self.parameterValue['vehicle line thickness'])
            for route in solutionData.routes:
                if routePredicate and not routePredicate(route):
                    continue
                for i, node in enumerate(route['node information'][:-1]):
                    nextNode = route['node information'][i+1]
                    row1 = indexToRow[node['index']]
                    row2 = indexToRow[nextNode['index']]
                    y1 = y0 + row1 * rowHeight + halfRowHeight
                    y2 = y0 + row2 * rowHeight + halfRowHeight
                    xArrival = timeToX(node['arrival time'])
                    xDeparture = timeToX(node['end of service'])
                    xNextArrival = timeToX(nextNode['arrival time'])
                    # horizontal line from arrival at this node
                    # until departure
                    canvas.drawLine(xArrival, y1, xDeparture, y1, style)
                    # travel line to the next node
                    canvas.drawLine(xDeparture, y1, xNextArrival, y2, style)
                # service at the last node
                lastNode = route['node information'][-1]
                row = indexToRow[lastNode['index']]
                y = y0 + row * rowHeight + halfRowHeight
                xArrival = timeToX(lastNode['arrival time'])
                xDeparture = timeToX(lastNode['end of service'])
                canvas.drawLine(xArrival, y, xDeparture, y, style)

    # initialise the rectangles we want to display
    def initialiseRectangles(self):
        # input data
        inputRectangleInfo = []
        if self.parameterValue['time window']:
            inputRectangleInfo.append( { 'begin': 'release time',
                                         'end': 'due date',
                                         'colour': \
                                             self.parameterValue\
                                             ['time window colour'],
                                         'xs': [],
                                         'ys': [],
                                         'ws': [],
                                         'hs': [],
                                         } )
        # solution data
        solutionRectangleInfo = []
        if self.parameterValue['waiting time']:
            solutionRectangleInfo.append( { 'begin': 'arrival time',
                                            'end': 'start of service',
                                            'colour': \
                                                self.parameterValue\
                                                ['waiting time colour'],
                                            'xs': [],
                                            'ys': [],
                                            'ws': [],
                                            'hs': [],
                                            } )
        if self.parameterValue['service time']:
            solutionRectangleInfo.append( { 'begin': 'start of service',
                                            'end': 'end of service',
                                            'colour': \
                                                self.parameterValue\
                                                ['service time colour'],
                                            'xs': [],
                                            'ys': [],
                                            'ws': [],
                                            'hs': [],
                                            } )
        return inputRectangleInfo, solutionRectangleInfo
