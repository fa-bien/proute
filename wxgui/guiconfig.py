#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: September 25th 2011 by Fabien Tricoire
#
# this module stores and extracts information regarding the gui (e.g. position
# and layout)

import os

import wx

import config

guiConfigDir = os.path.join(config.userConfigDir, 'wxgui')
favouriteLayoutFileName = os.path.join(guiConfigDir, 'favourite.layout')
lastSessionFileName = os.path.join(guiConfigDir, 'last.session')
preferencesFile = os.path.join(guiConfigDir, 'preferences')

# This is where we store user preferences
preferences = {}

# initialize config dir if not existing
def initializeConfig():
    # this should not happen...
    if os.path.exists(guiConfigDir) and not os.path.isdir(guiConfigDir):
        print(guiConfigDir, 'exists but is not a directory,', end=' ')
        print('WxGUI config won\'t be saved')
    # create the guiconfig directory if it doesn't exist
    else:
        if not os.path.isdir(guiConfigDir):
            print('Creating user config directory', guiConfigDir)
            os.mkdir(guiConfigDir)
    # if there is a preferences file, load it
    if os.path.exists(preferencesFile) and not os.path.isdir(preferencesFile):
        global preferences
        preferences = eval(open(preferencesFile).read())
    # we can have an erroneous preferences file, or we can have no prefs file
    # in both cases we reset
    if not isinstance(preferences, dict) or len(preferences) == 0:
        setFactoryPreferences()

def setFactoryPreferences():
    preferences['save layout'] = True
    preferences['save session'] = True

def savePreferences():
    try:
        f = open(preferencesFile, 'w')
        f.write(str(preferences) + '\n')
        f.close()
    except Exception as e:
        print('Cannot save preferences:', e)
    
def loadLayout(fName):
    try:
        layout = eval(open(fName).read())
        return layout
    except Exception as e:
        print('Cannot load layout:', e)
        return None

def loadFavouriteLayout():
    if os.path.exists(favouriteLayoutFileName) and \
            not os.path.isdir(favouriteLayoutFileName):
        return loadLayout(favouriteLayoutFileName)
    else:
        return None
    
def saveLayout(layout, fName):
    if fName[-7:] != '.layout':
        fName += '.layout'
    try:
        f = open(fName, 'w')
        f.write(str(layout) + '\n')
        f.close()
    except Exception as e:
        print('Cannot save layout:', e)

def saveAsFavouriteLayout(layout):
    saveLayout(layout, favouriteLayoutFileName)
    
# wxproute program version
def version():
    return '0.1a'
