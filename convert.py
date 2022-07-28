#!/usr/bin/env python
#
# File created 18th Feb 2016 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
#
# this script loads a vrp instance and saves it as a pif file

import sys
import string
import math
import types

import config
import vrpdata
import loaddata
import util

USAGE = 'type[:subtype] instance_file [output_file.pif]'

outputFileName = 'routes.pdf'

# main program: load an instance, a solution, and paint it in a PDF file
if __name__ == '__main__':
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print('USAGE:', sys.argv[0], USAGE)
        sys.exit(0)
    else:
        config.initializeConfig()
        # type of input data we're working on
        toks = sys.argv[1].split(':')
        baseType = toks[0]
        subType = toks[1] if len(toks) > 1 else 'default'
        # input file
        inputFileName = sys.argv[2]
        # in case an output file name is provided
        if len(sys.argv) == 4:
            outputFileName = sys.argv[3]
        else:
            outputFileName = inputFileName[:inputFileName.rfind('.')] + '.pif'
        # loader object to load all of this
        loader = loaddata.DataLoader()
        # here we load the data
        try:
            myVrp = loader.loadInstance(inputFileName, baseType, subType)
        except Exception as e:
            print('Exception while trying to load the instance:', e)
            sys.exit(0)
        #
        myVrp.storeAsPIF(outputFileName, sep=';')
