# -*- coding: utf-8 -*-
#
# File created August 2nd 2011 by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: August 18th 2011 by Fabien Tricoire
#
import string
import sys

import vrpdata
import vrpexceptions
import stylesheet
import util
import colours
from style import *

# display separate pictures for pickup and delivery nodes
# Basic style for an input data: draw depot and nodes
class PDPNodeDisplayer( Style ):
    description = 'pickup and delivery nodes'
    # used multiple times
    colourInfo = ColourParameterInfo()
    parameterInfo = {
        'delivery colour': colourInfo,
        'delivery contour thickness': IntParameterInfo(0, 20),
        'delivery contour': colourInfo,
        'pickup size': IntParameterInfo(0, 20),
        'delivery size': IntParameterInfo(0, 50),
        'pickup contour': colourInfo,
        'pickup colour': colourInfo,
        'pickup contour thickness': IntParameterInfo(0, 20),
        }
    defaultValue = {
        'pickup colour': Colour(0, 128, 0, 255),
        'pickup contour': Colour(0, 0, 0, 255),
        'delivery size': 8,
        'pickup size': 2,
        'delivery contour': Colour(0, 0, 0, 255),
        'delivery contour thickness': 1,
        'delivery colour': Colour(255, 0, 0, 255),
        'pickup contour thickness': 1
        }
    #
    def initialise(self):
        self.requiredNodeAttributes += [ 'type' ]
    #
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        # display pickup and delivery nodes
        pickupX = []
        pickupY = []
        pickupR = []
        deliveryX = []
        deliveryY = []
        deliveryW = []
        for node in inputData.nodes:
            if nodePredicate and not nodePredicate(node):
                continue
            else:
                if node['type'] == 'pickup':
                    pickupX.append(convertX(node['x']))
                    pickupY.append(convertY(node['y']))
                    pickupR.append(self.parameterValue['pickup size'])
                elif node['type'] == 'delivery':
                    deliveryX.append(convertX(node['x']))
                    deliveryY.append(convertY(node['y']))
                    deliveryW.append(self.parameterValue['delivery size'])
        # paint pickup nodes
        style = \
            DrawingStyle(self.parameterValue['pickup contour'],
                         self.parameterValue['pickup colour'],
                         lineThickness = \
                             self.parameterValue['pickup contour thickness'])
        canvas.drawCircles(pickupX, pickupY, pickupR, style)
        # display delivery nodes
        style = \
            DrawingStyle(self.parameterValue['delivery contour'],
                         self.parameterValue['delivery colour'],
                         lineThickness = \
                             self.parameterValue['delivery contour thickness'])
        canvas.drawRectangles(deliveryX, deliveryY, deliveryW, deliveryW, style)

# display separate pictures for pickup and delivery nodes
# Basic style for an input data: draw depot and nodes
class PickupToDelivery( Style ):
    description = 'pickup and delivery precedence constraints'
    # used multiple times
    colourInfo = ColourParameterInfo()
    parameterInfo = {
        'line colour': colourInfo,
        'line thickness': IntParameterInfo(0, 20),
        }
    defaultValue = {
        'line colour': colours.pastelgold,
        'line thickness': 2,
        }
    #
    def initialise(self):
        self.requiredNodeAttributes += [ 'type' ]
    #
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        style = DrawingStyle(self.parameterValue['line colour'],
                             lineThickness = \
                                 self.parameterValue['line thickness'])
        # display for each pickup node a line to the delivery
        for node in inputData.nodes:
            if nodePredicate and not nodePredicate(node):
                continue
            elif node['type'] == 'pickup':
                canvas.drawLine(convertX(node['x']), convertY(node['y']),
                                convertX(inputData.nodes[node['destination']] \
                                             ['x']),
                                convertY(inputData.nodes[node['destination']] \
                                             ['y']),
                                style)
                
