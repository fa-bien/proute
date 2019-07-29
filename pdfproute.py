#!/usr/bin/env python
#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: July 29th 2011 by Fabien Tricoire
#
# this script loads a vrp instance and a solution and paints them to a PDF file

import sys
import string
import math
import types

from reportlab.graphics import renderPDF

import style
import stylesheet
import config
import vrpdata
import loaddata
import util
from reportlabCanvas import ReportlabCanvas

USAGE = 'type[:subtype] instance_file [:solution subtype] solution_file\
 [output_file.pdf]'

outputFileName = 'routes.pdf'

# main program: load an instance, a solution, and paint it in a PDF file
if __name__ == '__main__':
    config.initializeConfig()
    if len(sys.argv) < 4 or len(sys.argv) > 6:
        print('USAGE:', sys.argv[0], USAGE)
        sys.exit(0)
    else:
        # type of input data we're working on
        toks = sys.argv[1].split(':')
        type = toks[0]
        subtype = toks[1] if len(toks) > 1 else 'default'
        # solutions to load and their subtype
        if sys.argv[3][0] == ':':
            solutionSubtype = sys.argv[3][1:]
            solutionFileName = sys.argv[4]
        else:
            solutionSubtype = 'default'
            solutionFileName = sys.argv[3]
        # in case an output file name is provided
        if (sys.argv[3][0] == ':' and len(sys.argv) == 6) or \
           (sys.argv[3][0] != ':' and len(sys.argv) == 5):
            outputFileName = sys.argv[-1]
        # loader object to load all of this
        loader = loaddata.DataLoader()
        # here we load the data
        myVrp = loader.loadInstance(sys.argv[2], type, subtype)
        mySolution = loader.loadSolution(solutionFileName, myVrp,
                                         type, solutionSubtype)
        myStyleSheet = loader.loadStyleSheet(type)
        # now we can paint it to a PDF canvas
        width, height = myVrp.width, myVrp.height
        canvas = ReportlabCanvas(width, height, outputFileName)
        myStyleSheet.paint( myVrp, mySolution, canvas )
        canvas.canvas.showPage()
        canvas.canvas.save()
        print('Saved to', outputFileName)
