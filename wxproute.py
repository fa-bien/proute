#!/usr/bin/env python
#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: August 2nd 2011 by Fabien Tricoire
#

import sys
import string
import math
import types

import style
import stylesheet
import config
import vrpdata
import loaddata
import util
import wxgui.vrpgui

USAGE = 'type[:subtype] instance_file [:solution subtype] [solution_files]'
    
# main program: load an instance, several solutions, and open a GUI with them
def main():
    config.initializeConfig()
    if len(sys.argv) < 3:
        print('USAGE:', sys.argv[0], USAGE)
        # sys.exit(0)
        myVrp, solutions, myStyleSheet = None, None, None
    else:
        # type of input data we're working on
        toks = sys.argv[1].split(':')
        type = toks[0]
        subtype = toks[1] if len(toks) > 1 else 'default'
        # solutions to load and their subtype
        if len(sys.argv) > 3 and sys.argv[3][0] == ':':
            solutionSubtype = sys.argv[3][1:]
            solutionFileNames = sys.argv[4:]
        elif len(sys.argv) > 2:
            solutionSubtype = 'default'
            solutionFileNames = sys.argv[3:]
        else:
            solutionFileNames = False
        # loader object to load all of this
        loader = loaddata.DataLoader()
        # here we load the data
        myVrp = loader.loadInstance(sys.argv[2], type, subtype)
        # reorder solutions using numbers in file names
        if solutionFileNames:
            solutionFileNames = util.reorder(solutionFileNames)
            solutions = [ loader.loadSolution(fName, myVrp,
                                              type, solutionSubtype)
                          for fName in solutionFileNames ]
        else:
            solutions = None
        myStyleSheet = loader.loadStyleSheet(type)
#         myStyleSheet = loaddata.stylesheetFromType(type)
#     myStyleSheet = stylesheet.FunkyStyleSheet()
    app = wxgui.vrpgui.VrpGui(myVrp, solutions, myStyleSheet)
    app.MainLoop()

if __name__ == '__main__':
    main()
