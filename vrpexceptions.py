#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
# Last modified: July 29th 2011 by Fabien Tricoire
#
class MissingAttributeException(Exception):
    def __init__(self, attributeType, attributeName):
        self.attributeType = attributeType
        self.attributeName = attributeName

    def __str__(self):
        return 'missing ' + self.attributeType + ': ' + self.attributeName

class VrpInputFileFormatException(Exception):
    def __init__(self, fileFormat, fileName):
        self.fileFormat = fileFormat
        self.fileName = fileName

    def __str__(self):
        return 'File ' + self.fileName + \
            ' is not in the correct format for a ' + \
            self.fileFormat + ' instance'

class SolutionFileFormatException(VrpInputFileFormatException):
    def __str__(self):
        return 'File ' + self.fileName + \
            ' is not in the correct format for a ' + \
            self.fileFormat + ' solution'

class NotImplementedError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return message
