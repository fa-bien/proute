#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: August 3rd 2011 by Fabien Tricoire
#
import sys
import os

# startingDir = os.getcwd()
startingDir = os.path.dirname(sys.argv[0])
if startingDir == '' or startingDir == '.': startingDir = os.getcwd()
startingDir = os.path.abspath(startingDir)
#if startingDir == '': startingDir = '.'
# user config directory
homeDir =  os.getenv('USERPROFILE') or os.getenv('HOME')
userConfigDir = os.path.join(homeDir, '.proute')
# built in plugins
builtinPluginDir = os.path.join(startingDir, 'plugins')
# user plugins
userPluginDir = os.path.join(userConfigDir, 'plugins')
# stylesheets saved by user
userSheetDir = os.path.join(userConfigDir, 'stylesheets')
# all plugins
pluginDirectories = [ builtinPluginDir, userPluginDir, userSheetDir ]

# add all plugin directories to the loading path
sys.path += pluginDirectories

print 'sys.path =', sys.path

# initialize config dir if not existing
def initializeConfig():
    if os.path.exists(userConfigDir) and not os.path.isdir(userConfigDir):
        print userConfigDir, 'exists but is not a directory,',
        print 'user config won\'t be saved'
    else:
        if not os.path.isdir(userConfigDir):
            print 'Creating user config directory', userConfigDir
            os.mkdir(userConfigDir)
        if not os.path.exists(userPluginDir):
            print 'Creating user plugin directory', userPluginDir
            os.mkdir(userPluginDir)
        if not os.path.exists(userSheetDir):
            print 'Creating user plugin directory', userSheetDir
            os.mkdir(userSheetDir)
