#!/bin/sh
DIR=macbuild
# create a directory where we put everything
mkdir $DIR
# generate the .app
echo " * Generating .app with pyinstaller"
/usr/bin/env python Build.py -y wxproute/wxproute.spec
# change the icon
echo " * Changing icon"
cp ./icons/proute.icns dist/wxproute.app/Contents/App.icns
# add the .app to the bundle
mv ./dist/wxproute.app $DIR
# add the licences to the bundle
echo " * Copying licences and FAQ"
cp -R ../local/licences $DIR
cp trunk/FAQ.txt $DIR
# # add sample data files
# echo " * Adding sample data"
# cp -R ../local/sample\ data $DIR
# generate .dmg
echo " * Generating .dmg image"
rm -f proute.dmg
hdiutil create -srcfolder $DIR -volname proute proute.dmg
# delete temporary directory
rm -rf $DIR