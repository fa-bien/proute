# -*- mode: python -*-
# embed plugins as data files
pluginDir = os.path.join('.', 'trunk', 'plugins')
pluginFiles = [ fName
                for fName in os.listdir(pluginDir)
                if fName[-3:] == '.py' ]
pluginsAsData = \
    [ (os.path.join('plugins', fName), os.path.join(pluginDir, fName), 'DATA')
      for fName in pluginFiles ]
# analyse program entry point
inputFiles = [ os.path.join('.', 'trunk', 'wxproute.py') ]
# plugins too, in order to provide all required packages
inputFiles += [ os.path.join('.', 'trunk', 'plugins', fName)
                for fName in pluginFiles ]
# platform-dependent icon
if sys.platform == 'darwin':
    iconFile = os.path.join('icons', 'proute.icns')
elif sys.platform == 'win32':
    iconFile = os.path.join('icons', 'proute.ico')
else:
    iconFile = None

# non-required binaries that take space
unwantedBinaries = [ ('libwx_macud-2.8.0.dylib', '', ''),
                     ('libncursesw.5.dylib', '', ''),
                     ('libz.1.dylib', '', ''),
                     ('libjpeg.8.dylib', '', ''),
                     ('libfreetype.6.dylib', '', ''),
                     #
                     ('pyexpat', '', ''),
                     ('readline', '', ''),
                     ('bz2', '', ''),
                     ]

# name of the executable
if sys.platform == 'win32':
    name=os.path.join('build','pyi.win32','wxproute','wxproute.exe')
else:
    name=os.path.join('build', 'pyi.' + sys.platform, 'wxproute','wxproute')

# analyse all of this...
a = Analysis([ os.path.join(HOMEPATH,'support','_mountzlib.py'),
               os.path.join(HOMEPATH,'support','useUnicode.py') ]
             + inputFiles
             ,
#              pathex=[ #'./trunk/plugins',
#                       '/Users/fabien/pyinstaller-1.5'],
             )
              
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=name,
          debug=False,
          strip=True,
          upx=True,
          console=False,
          icon=iconFile)

coll = COLLECT( exe,
                a.binaries - unwantedBinaries,
                a.zipfiles,
                a.datas,
                pluginsAsData,
                strip=True,
                upx=True,
                name=os.path.join('dist', 'wxproute'))

if sys.platform == 'darwin':
    app = BUNDLE(coll,
                 name=os.path.join('dist', 'wxproute.app'))
