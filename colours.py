#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: July 29th 2011 by Fabien Tricoire
#
from style import Colour

transparent = Colour(255, 128, 0, 0)
white = Colour(255, 255, 255)
black = Colour(0, 0, 0)
red = Colour(255, 0, 0)
green = Colour(0, 255, 0)
blue = Colour(0, 0, 255)
magenta = Colour(255, 0, 255)
yellow = Colour(255, 255, 0)
cyan = Colour(0, 255, 255)
dimcyan = Colour(128, 200, 255)
cornflowerblue = Colour(100, 149, 237, 255) # taken from reportlab
applegreen = Colour(124, 252, 0, 255) # lawngreen from reportlab
darkorange = Colour(255, 165, 0)
funkybrown = Colour(100, 10, 25, 255)
funkypink = Colour(255, 0, 100, 255)
funkygreen = Colour(0, 190, 0, 255)
pastelgold = Colour(255, 177, 89)
rosybrown = Colour(188, 143, 143, 255) # taken from reportlab
darkpurple = Colour(126, 0, 152)
lightgray = lightgrey = Colour(200, 200, 200)

# 2 steps otherwise one reference too many appears in dir()
tralala = dir()
colours = [ eval(colour) for colour in tralala
            if isinstance(eval(colour), Colour) ]
