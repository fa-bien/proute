#!/bin/sh
DIR='wxproute_for_linux'
# create a directory where we put everything
mkdir $DIR
# generate the .app
echo " * Generating binary with pyinstaller"
/usr/bin/env python Build.py -y wxproute/wxproute.spec
# # change the icon
# echo " * Changing icon"
# cp ./icons/proute.icns dist/wxproute.app/Contents/App.icns
# add the .app to the bundle
mv ./wxproute/dist/wxproute $DIR
# add the licences to the bundle
echo " * Copying licences and FAQ"
cp -R ../local/licences $DIR
cp trunk/FAQ.txt $DIR
# # add sample data files
# echo " * Adding sample data"
# cp -R ../local/sample\ data $DIR
# generate archive
echo " * Generating archive"
tar czf $DIR.tar.gz $DIR
# delete temporary directory
rm -rf $DIR