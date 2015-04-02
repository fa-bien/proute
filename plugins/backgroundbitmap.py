#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: July 29th 2011 by Fabien Tricoire
#
import string
import sys

try:
    import Image
except Exception as e:
    try:
        # is pillow installed?
        from PIL import Image
    except Exception as ee:
        pass
    
import vrpdata
import stylesheet
from style import *
import colours

# Display a background bitmap
class BackgroundBitmapDisplayer( Style ):
    description = 'background bitmap'
    # xNW and yNW are the coordinates of the north-west corner point of the map
    # xSE and ySE are the coordinates of the south-east corner point of the map
    # acceptable values for corner point parameters
    intInfo = IntParameterInfo(-sys.maxint, sys.maxint)
    parameterInfo = {
        'xNW': intInfo,
        'yNW': intInfo,
        'xSE': intInfo,
        'ySE': intInfo,
        'file name': FileNameParameterInfo(),
        }
    defaultValue = {
        'xNW': None,
        'yNW': None,
        'xSE': None,
        'ySE': None,
        'file name': None,
        'coord style': 'bitmapSize',
        }
    def initialise(self):
        # set the file name if given
        if not self.parameterValue['file name'] is None:
            self.bitmap = Image.open(self.parameterValue['file name'])
        # otherwise, delay the loading until we know the file name
        else:
            self.bitmap = None
    #
    def paint(self, inputData, solutionData,
              canvas, convertX, convertY,
              nodePredicate, routePredicate, arcPredicate,
              boundingBox):
        # if the file name is not specified, do nothing
        if not 'file name' in self.parameterValue:
            return
        # if the map hasn't been loaded yet, load it
        if self.bitmap is None and not self.parameterValue['file name'] is None:
            self.bitmap = Image.open(self.parameterValue['file name'])
        # prevent from continuing if the file hasn't been selected yet
        if self.bitmap is None:
            return
        # if the bounds haven't been set, set default values
        if self.parameterValue['xNW'] is None:
            if self.parameterValue['coord style'] == 'bitmapSize':
                self.parameterValue['xNW'] = 0
                self.parameterValue['yNW'] = self.bitmap.size[1]
                self.parameterValue['xSE'] = self.bitmap.size[0]
                self.parameterValue['ySE'] = 0
            elif self.parameterValue['coord style'] == 'nodeCoords':
                self.parameterValue['xNW'] = inputData.xmin
                self.parameterValue['yNW'] = inputData.ymax
                self.parameterValue['xSE'] = inputData.xmax
                self.parameterValue['ySE'] = inputData.ymin
            else:
                return
        # now we can resize the image to the portion we want to really display
        newWidth = convertX(self.parameterValue['xSE']) - \
            convertX(self.parameterValue['xNW'])
        newHeight = convertY(self.parameterValue['yNW']) - \
            convertY(self.parameterValue['ySE'])
        newBitmap = self.bitmap.resize( (int(newWidth), int(newHeight)) )
        # finally we can paint the bitmap!
        canvas.drawBitmap(newBitmap, (convertX(self.parameterValue['xNW']),
                                      convertY(self.parameterValue['yNW'])))
