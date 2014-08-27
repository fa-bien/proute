#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: July 29th 2011 by Fabien Tricoire
#
from style import *

import basestyles
import colours
import stylesheet

# Basic style for an input data: draw depot and nodes
class NodeLSDDisplayer( Style ):
    description = 'LSD nodes'
    parameterInfo = {
        'min node size': IntParameterInfo(0, 100),
        'max node size': IntParameterInfo(1, 100),
        }
    defaultValue = {
        'max node size': 5,
        'min node size': 1,
        }
    #
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        # display depots
        for node in inputData.nodes:
            if nodePredicate and not nodePredicate(node):
                continue
            else:
                c = randomColour()
                style = DrawingStyle(c, c)
                if node['is depot']:
                    canvas.drawRectangle(convertX(node['x']),
                                         convertY(node['y']),
                                         7, 7,
                                         style)
                else:
                    canvas.drawCircle(convertX(node['x']),
                                      convertY(node['y']),
                                      random.randint(self.parameterValue\
                                                         ['min node size'],
                                                     self.parameterValue\
                                                         ['max node size']),
                                      style)
        
# Style for a solution data: draw arcs with splines
class RouteSplineDisplayer(basestyles.RouteDisplayer):
    description = 'routes as splines'
    def initialise(self):
        self.requiredRouteAttributes += [ 'node sequence' ]
    # display each route
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        # display each route
        for route in solutionData.routes:
            if routePredicate and not routePredicate(route): continue
            points = []
            for node in route['node sequence']:
                if self.parameterValue['draw depot arcs'] or\
                        not inputData.nodes[node]['is depot']:
                    points.append( ( convertX(inputData.nodes[node]['x']),
                                     convertY(inputData.nodes[node]['y']) ) )
            style = DrawingStyle(self.parameterValue['arc colour'],
                                 lineThickness=self.parameterValue['thickness'])
            canvas.drawSpline(points, style)

# 
class RouteLSDDisplayer(basestyles.RouteDisplayer):
    description = 'LSD routes'
    #
    def initialise(self):
        basestyles.RouteDisplayer.initialise(self)
        del self.parameterInfo['arc colour']
        self.requiredRouteAttributes += [ 'node sequence' ]
                 
    # display each route
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        # display each route
        for route in solutionData.routes:
            if routePredicate and not routePredicate(route): continue
            points = []
            for node in route['node sequence']:
                if self.parameterValue['draw depot arcs'] or\
                        not inputData.nodes[node]['is depot']:
                    points.append( (convertX(inputData.nodes[node]['x']),
                                    convertY(inputData.nodes[node]['y']) ) )
            style = DrawingStyle(randomColour(),
                                 lineThickness=self.parameterValue['thickness'])
            canvas.drawSpline(points, style)
        
# different style for displaying CVRP
class FunkyStyleSheet(stylesheet.StyleSheet):
    # default stylesheet: display nodes and arcs in a simple way
    def loadDefault(self, keepAspectRatio=False):
        import basestyles, extrastyles
        # True if aspect ratio should be kept, False otherwise
        self.keepAspectRatio = keepAspectRatio
        # initialize styles
        self.styles = []
        # display routes as splines
        self.styles.append(extrastyles.RouteSplineDisplayer(
                {'arc colour': colours.funkybrown}))
        # basic style: display nodes
        self.styles.append(basestyles.NodeDisplayer({\
                        'depot colour': colours.funkypink,
                        'depot contour': colours.funkypink,
                        'node colour': colours.funkygreen,
                        'node contour': colours.funkygreen}))

# LSD style for displaying CVRP
class LSDStyleSheet(stylesheet.StyleSheet):
    def loadDefault(self, keepAspectRatio=False):
        import basestyles, extrastyles
        # True if aspect ratio should be kept, False otherwise
        self.keepAspectRatio = keepAspectRatio
        # initialize styles
        self.styles = []
        # display routes as splines
        self.styles.append(extrastyles.RouteLSDDisplayer())
        # display nodes
        self.styles.append(extrastyles.NodeLSDDisplayer())
