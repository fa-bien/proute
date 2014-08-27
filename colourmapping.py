#
# File created September 24th by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: September 28th 2011 by Fabien Tricoire
#
import util
import style
import colours

class ColourMapping:
    def __init__(self,
                 map=style.ColourMap([ colours.green,
                                       colours.yellow,
                                       colours.red ]),
                 values=[0, 1]):
        self.update(map, values)

    def update(self, map, values):
        self.colours = map.colours
        self.values = values
        self.process()
        
    def __getitem__(self, x):
        try:
            return self.getColour(x)
        except Exception as e:
            self.addItem(x)
            return self.getColour(x)

    def addItem(self, item):
        self.values.append(item)
        self.process()

class Palette(ColourMapping):
    def process(self):
        self.map = {}
        values = set(self.values)
        for i, v in enumerate(values):
            self.map[v] = self.colours[i % len(self.colours)]

    def getColour(self, value):
        return self.map[value]
    
class Gradient(ColourMapping):
    def process(self):
        # pre-compute differences between consecutive colours
        self.colourDifference = [ style.Colour(c2.red - c1.red,
                                               c2.green - c1.green,
                                               c2.blue - c1.blue,
                                               c2.alpha - c1.alpha)
                                  for c1, c2 in zip(self.colours[:-1],
                                                    self.colours[1:])
                                  ]
        # map input values to some index in the list of colours
        self.mapping = util.intervalMapping(min(self.values), max(self.values),
                                            0, float(len(self.colours) - 1) )

    def getColour(self, value):
        mappedValue = self.mapping(value)
        index = int(mappedValue)
        # now we have a float value for the index so we must compute the
        # ratio colour between its ceil and floor
        # special case: last colour
        if index == len(self.colours) - 1:
            return self.colours[-1]
        # regular case
        else:
            offset = mappedValue % 1.0
            red = self.colours[index].red + \
                offset * self.colourDifference[index].red
            green = self.colours[index].green + \
                offset * self.colourDifference[index].green
            blue = self.colours[index].blue + \
                offset * self.colourDifference[index].blue
            alpha = self.colours[index].alpha + \
                offset * self.colourDifference[index].alpha
            return style.Colour(red, green, blue, alpha)

# g = Gradient()
# print g[0]
# print g[0.5]
# print g[1]
# p = Palette(values=[1,2,3,4,5,6])
# print p[1]
# print p[2]
# print p[3]
# print p[4]
# print p[5]
