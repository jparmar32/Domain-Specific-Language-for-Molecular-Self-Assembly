
from __future__ import print_function, division

import copy,collections
from _collections import deque
from types import NoneType
from test.pickletester import initarg
from test.test_new import NewTest

VERBOSE_SIGNALS = True

"""Contains classes and functions for creating and
manipulating 2D tiles and tile assembly systems in the Tile 
Assembly Model. The fundamental classes are
- Multisignal: a mapping type, mapping signal names to values
- MultisignalType: a mapping type, mapping signal names to lists of valid 
                   values
        
- Tile: a type of tile, composed of one glue on each of the four sides, as well
        as a name, label, and possible other properties such as tilecolor, 
        textcolor, concentration, etc.
            
- TileSystem: a list of unique tiles together with a seed assembly, which is
              a dict mapping 2D coordinates ((int,int) pairs) to Tiles
              
- TileTemplate: a class for specifying a family of Tiles that share a common 
                set of input sides, each with the same GlueTemplate, and a 
                common set of output sides, each with the same GlueTemplate.
                
- TileSetTemplate: a group of TileTemplates and Tiles. This object is
                   responsible for managing the input-output relationships 
                   between the TileTemplates, and can be used to generate a
                   list of all the tiles that are represented by all the
                   TileTemplates (and Tiles) it contains.
"""


##############################################################################
## Exceptions
##############################################################################

class TAMError(Exception):
    """Base class for exceptions produced by the TAM library."""
    pass
    
class TAMImmediateError(TAMError):
    '''Immediate errors are those that ought to result in an excepton immediately
    being raised, since there is no valid reason to want the error to persist
    even temporarily.'''
    pass
    
class TAMLazyError(TAMError):
    '''Lazy errors are those that we allow the user to make temporarily, which will
    prevent the tiles from being generated if TileSetTemplate.createTiles is
    called, but which otherwise will be allowed to persist as they construct the
    TileSetTemplate (for instance, in a GUI), so that the errors may be visually
    reported to the user without stopping them from continuing to work.'''
    pass

class ErrorListError(TAMError):
    """Raised to indicate that one or more errors occurred when executing
    TileSetTemplate.createTiles. It can be queried to retrieve that list."""
    def __init__(self, errorList):
        self.errorList = errorList
        
    def errors(self):
        return self.errorList
        

class DuplicateSignalNameConflictingValuesError(TAMError):
    '''JP - Raised to indicated that two different multisignals that wish to be combined must have signals with the same value to be joined'''

    def __init__(self, signal_name, multisignal1, multisignal1value, multisignal2, multisignal2value):
        self.signal_name = signal_name
        self.multisignal1 = multisignal1
        self.multisignal1value = multisignal1value
        self.multisignal2 = multisignal2
        self.multisignal2value = multisignal2value
    
        
    def __str__(self):
        return 'signal {} contained in multisignal {} with value {} and multisignal {} with value {}; must be exactly equal to {} to combine these Multisignals'.format(self.signal_name,
        self.multisignal1,
        self.multisignal1value,
        self.multisignal2,
        self.multisignal2value)

# Immediate errors are those that ought to result in an excepton immediately
# being raised, since there is no valid reason to want the error to persist
# even temporarily.

# Lazy errors are those that we allow the user to make temporarily, which will
# prevent the tiles from being generated if TileSetTemplate.createTiles is
# called, but which otherwise will be allowed to persist as they construct the
# TileSetTemplate (for instance, in a GUI), so that the errors may be visually
# reported to the user without stopping them from continuing to work.

# immediate
class NonexistentTransitionError(TAMError):
    """Raised to indicate that a transition attempted to be removed does not exist."""
    """JP- TODO: add the Tile Template to which the user is trying to remove the transition for?"""
    def __init__(self, outputNamesGiven, transitions):
        self.outputNamesGiven = outputNamesGiven
        self.transitions = transitions
        
    def __str__(self):
        return '{0} is not a set of outputs defining any transition in the list {1}'.format(self.outputNamesGiven, self.transitions)

# immediate when calling create or restrict on a MultisignalType
# lazy when input signal names or output signal names given with transition are invalid
class ExisitngParrentError(TAMError):
    def __init__(self,child,type,name,parent):
        self.child = child
        self.parent = parent
    def __str__(self):
        return "the child: {}, which is of type: {}, has sough to be added to: {} already has the parent: {}".format(self.child, self.type,self.name, self.parent)
class SignalInvalidNameError(TAMError):
    """Raised to indicate an invalid signal name."""
    def __init__(self, invalidName, validNames):
        self.invalidName = invalidName
        self.validNames = validNames
        
    def __str__(self):
        return '"{0}" is an invalid signal name; valid signal names are {1}'.format(
               self.invalidName, self.validNames)
        
class tooManyInitatiorPortsError(TAMError):
    ''' raised when there are the strength of initiator ports attached to a module is greater than 2 '''
    def __init__(self, moduleName):
        self.moduleName = moduleName
    def __str__(self):
        return "the strength of initiator ports in the module {} exceeds 2".format(self.moduleName)
class portParentConfigurationNotMet(TAMError):
    def __init__(self,tileTemplate):
        self.tileTemplate = tileTemplate
        
    def __str__(self):
        return "The list of ports contained in the portNeihborhod of the tileTemplate: {} do not meet the required parent configuration".format(self.tileTemplate)
# immediate when joining or rejoining and MultisignalType objects with overlapping signal names are used
class SignalDuplicateNameError(TAMError):
    """Raised to indicate a duplicate signal name."""
   
    def __init__(self, name):
        self.name = name
        
    def __str__(self):
        return '"{0}" appears more than once as a signal name'.format(self.name)
# lazy when transition applied for specific TileTemplate
class DuplicateOutputSignalValues(TAMError):
    def __init__(self, signal_name, olddirection, newdirection,tileTemplate):
        self.signal_name = signal_name
        self.olddirection = olddirection
        self.newdirection = newdirection
        self.tileTemplate = tileTemplate
    def __str__(self):
        return "same output multisignal {} for tile template: {} is used in two different directions: {} and {}".format(self.signal_name,self.tileTemplate, self.olddirection, self.newdirection)
        
    

# immediate when restricting multisignaltype; 
# lazy when transition outputs invalid value
class SignalInvalidValueError(TAMError):
    """Raised to indicate an invalid signal value."""
    def __init__(self, signalName, invalidVal, validVals):
        self.signalName = signalName
        self.invalidVal = invalidVal
        self.validVals = validVals
    '''JP - added __str__ function as it was not listed before'''
    def __str__(self):
        return 'The signal: {0} contains the invalid value: {1}. Valid values are {2}'.format(self.signalname,self.invalidVal,self.validVals)
       
# immediate when creating or restricting multisignal type
class SignalDuplicateValueError(TAMError):
    """Raised to indicate a duplicate signal name."""
    '''JP - TODO: List which duplicate signal valid values are contained?'''
    def __init__(self, vals):
        self.vals = vals
        
    def __str__(self):
        return '"{0}" contains duplicate signal valid values'.format(self.vals)

# immediate; should result in prompting to see if user wants to update other joins
class SignalMissingNameError(TAMError):
    """Raised to indicate a join is missing a signal name for its neighborhood."""
    
    def __init__(self, neighborhood, join, signalType):
        self.signalType = signalType
        self.neighborhood = neighborhood
        self.join = join
        
    def __str__(self):
        return 'join {0} is missing signal type {1} required for neighborhood {2}'.format(self.join, self.signalType, self.join)

# immediate
class InputOutputSideConflictError(TAMError):
    """Raised to indicate that a single tile template side has been specified as both an input and an output."""
    '''JP - TODO: add the join which is acting as an input and the join acting as the output to make debugging easier'''
    def __init__(self, tileTemplate, direction):
        self.tileTemplate = tileTemplate
        self.direction = direction
        
    def __str__(self):
        return 'tile template {0} cannot have side {1} as both an input and output'.format(self.tileTemplate, self.direction)

# lazy
class StrengthError(TAMError):
    """Raised to indicate that a join has the incorrect strength, as calculated by the number of input sides on the 
    TileTemplate on the output direction of the join."""
    def __init__(self, tileTemplate, join):
        self.tileTemplate = tileTemplate
        self.join = join
        
    def __str__(self):
        properStrength = 1 if self.tileTemplate.numInputSides() == 2 else 2
        return 'tile template {0} has {1} input sides and must therefore have strength {2} on join {3}'.format(self.tileTemplate, self.tileTemplate.numInputSides(), properStrength, self.join)

# lazy
class TooManyInputSidesError(TAMError):
    """Raised to indicate that a tile template has too many input sides."""
    '''JP - TODO: add which sides act as input sides '''
    def __init__(self, tileTemplate):
        self.tileTemplate = tileTemplate
        
    def __str__(self):
        return 'tile template {0} has {1} input sides but must have at most 2'.format(self.tileTemplate, self.tileTemplate.numInputSides())

# lazy
class OutputNotComputedError(TAMError):
    """Raised to indicate that one of the output signals of a TileTemplate was not computed by any transition."""

    def __init__(self, tileTemplate,outputSignal):
        self.tileTemplate = tileTemplate
        self.outputSignal = outputSignal
   
    def __str__(self):
        return 'the output signal {0} for the tile template: {1} was not computed by any transition'.format(self.outputSignal,self.tileTemplate)

# lazy 
class OutputMultiplyComputedError(TAMError):
    """Raised to indicate that one of the output signals of a TileTemplate has more than one transition computing it."""

    def __init__(self,outputSignal,tileTemplate,transitions):
        self.outputSignal = outputSignal
        self.tileTemplate = tileTemplate
        self.transitions = transitions

    def __str__(self):
        return 'the output signal: {0} for the tile template {1} has the following transition computing it {2}, must only be computed by one'.format(self.outputSignal,self.tileTemplate,self.transitions)

    
# lazy because it is only dynamically detectable by calling function with all possible inputs (not all of
# which may have been specified yet if there are remaining TileTemplates left to wire as inputs to this one)
class OutputArityError(TAMError):
    """Raised to indicate that an output tuple from a transition does not have the same length as the list
    of output signal names."""
    def __init__(self,outputTuple,transition,TileTemplate,outputSigNames):
        self.outputTuple = outputTuple
        self.transition = transition
        self.TileTemplate = TileTemplate
        self.outputSigNames = outputSigNames
    def __str__(self):
        return 'the output tuple: {0} computed by the transition {1} for the tile template {2} must have the same length as the list of output signal names: {3}'.format(self.outputTuple,self.transition,self.TileTemplate,self.outputSigNames)
class TileTemplateFromObjNotConfomingtoModuleConfigurationError(TAMError):
    def __init__(self,fromObj,toObj):
        self.fromObj = fromObj.parent
        self.toObj = toObj.parent
    def __str__(self):
        return 'the parents of the fromObj,tileTemplate:{0} and the toObj,{1} do not fit an allowed configuration for modules'.format(self.fromObj,self.toObj)
class PortFromObjNotConformingtoModuleConfigurationError():
    def __init__(self,fromObj,toObj):
        self.fromObj = fromObj.parent
        self.toObj = toObj.parent
    def __str__(self):
        return 'the parents of the fromObj,port:{0} and the toObj,{1} do not fit an allowed configuration for modules'.format(self.fromObj,self.toObj)

# immediate because immediately detectable from signature of function
class InputArityError(TAMError):
    """Raised to indicate that the arity of a transition does not have the same length as the list
    of input signal names. If the function takes varargs, then it ensures that the number of input signal
    names specified is at least the number of non-varargs given."""
    def __init__(self,transition,tileTemplate,inputSignalNames):
        self.transition = transition
        self.tileTemplate = tileTemplate
        self.inputSignalNames = inputSignalNames
    def __str__(self):
        return 'The arity of the transition: {0} for tile template {1} must have the same length as the input signal names: {2}'.format(self.transition,self.tileTemplate,self.inputSignalNames)


# lazy
class InvalidChooserTileTemplateError(TAMError):
    """Raised to indicate that a tile template or list of tile templates is not an element/subset of the TileTemplates
    that could actually be the output."""
    def __init__(self,tileTemplates,outputTileTemplates,chooserFunction):
        self.tileTemplates = tileTemplates
        self.outputTileTemplates = outputTileTemplates
        self.chooserFunction = chooserFunction
    def __str__(self):
        return 'The tile template(s): {0} are not an element of the tile templates {1} that can be used as an output for the chooser function {2}'.format(self.tileTemplates,self.outputTileTemplates,self.chooserFunction)

    
# lazy
class MissingChooserError(TAMError):
    """Raised to indicate that the user needs to specify which of multiple TileTemplates to choose for a
    given input multisignal, when more than one could be the output as computed by the library."""
    def __init__(self,tileTemplates,multisignal):
        self.tileTemplates = tileTemplates
        self.multisignal = multisignal
    def __str__(self):
        return 'The tile templates: {0} need a choser function for the input multisignal {1}'.format(self.tileTemplates,self.multisignal)


# lazy
class ConflictingChooserError(TAMError):
    """Raised to indicate that there are multiple chooser functions defined for a chooser set on
    a given input multisignal."""
    def __init__(self,tileTemplates,chooserFunctions,inputMultisignal):
        self.tileTemplates = tileTemplates
        self.chooserFunction = chooserFunctions
        self.inputMultisignal = inputMultisignal
    def __str__(self):
        return 'There a multiple conflicting chooser functions: {0} for the input multisignal: {1} contained within the tile templates {2}'.format(self.chooserFunction,self.inputMultisignal,self.tileTemplates)

class portsNotConnectedtoTileTemplatesOutput(TAMError):
    def __init__(self, unvistedPortsList):
        self.unvisistedPortsList = unvistedPortsList
    def __str__(self):
        return "The ports within the following list: {0} are not connected to a tile templates output side".format(self.unvisistedPortsList)
        
class portsNotConnectedToTileTemplatesInput(TAMError):
    def __init__(self, unvistedPortsList):
        self.unvisistedPortsList = unvistedPortsList
    def __str__(self):
        return "The ports within the following list: {0} are not connected to a tile templates input side".format(self.unvisistedPortsList)
#when there are multiple from objects in a neighborhood and a port is contained in this list 
class fromObjectsPortError(TAMError):
    def __init__(self, neighborhood):
        self.neighborhood = neighborhood
    def __str__(self):
        return "The from objects contained within the joins in the neighborhood: {0} have a port when their are multiple objects".format(self.neighborhood)
#when there are multiple to objects in a neighborhood and a port is contained in this list 
class toObjectsPortError(TAMError):
    def __init__(self, neighborhood):
        self.neighborhood = neighborhood
    def __str__(self):
        return "The to objects contained within the joins in the neighborhood: {0} have a port when their are multiple objects".format(self.neighborhood)
# immediate
class NameDifferenceError(TAMError):
    """Raised to indicate that two multisignals cannot be valueUnion'ed because their signal names are not identical."""
    '''JP - TODO: List for which multisingals these signal names belong to'''
    def __init__(self, names1, names2):
        self.names1 = names1
        self.names2 = names2
        
    def __str__(self):
        return 'list of names {0} must be identical to {1}'.format(self.names1, self.names2)
        
# immediate
class NameOverlapError(TAMError):
    """Raised to indicate that two multisignals cannot be nameUnion'ed because their signal names are not disjoint."""
    '''JP - TODO: List for which multisingals these signal names belong to'''
    def __init__(self, names1, names2):
        self.names1 = names1
        self.names2 = names2
        
    def __str__(self):
        return 'list of names {0} must be disjoint from to {1}'.format(self.names1, self.names2)

class NonexistentChooserSetError(TAMError):
    """Raised to indicate that a chooserSet consisting of the set of tiles does not exist."""
    def __init__(self, tileSet):
        self.tileSet = tileSet
        
    def __str__(self):
        nameList = list([tile.name for tile in self.tileSet])
        return 'There is no chooser set consisting of this list of tile templates: {0}'.format(nameList)

class InputSideMismatchError(TAMError):
    """Raised to indicate that a tileTemplate does not have input sides matching the chooserSet it's being added to"""
    def __init__(self, tileTemplate, tileTemplateInDirs, chooserSetInDirs):
        self.tileTemplate = tileTemplate
        self.tileTemplateInDirs = tileTemplateInDirs
        self.chooserSetInDirs = chooserSetInDirs
        
    def __str__(self):
        return 'TileTemplate {0} has input side list {1} which does not match the list for the chooserSet {2}'.format(self.tileTemplate.name, self.tileTemplateInDirs, self.chooserSetInDirs)

##############################################################################
## These aren't really tile related, but they are useful.
##############################################################################

# allow multi-arity identity; e.g. identity(3,4,5) = (3,4,5)
def identity(*x):
    """Return x, returning a tuple for 0-arity or multi-arity calls.
    
    e.g. identity(3,'a',5) = (3, 'a', 5)"""
    if len(x) == 1:
        return x[0]
    else:
        return x

def reprByProps(obj):
    """Create a string representing obj using the properties. 
    
    Assumes each property can be specified in the constructor.
    
    For instance, an object of type moduleName.A with properties self.a = 123 
    and self.b = 'abc' would have the string 
    "moduleName.A(a=123,b='abc')" returned.
    
    Except for the top-level call, which always performs this pairing, it uses
    the condition of whether obj defines __repr__ to decide whether to use
    repr(val) to represent an attribute value, or to recurse into the property
    and use reprByProps to represent that value also. The idea is that we
    want to use the object's way of representing itself literally if it has
    defined one, but since we use this function to make defining __repr__ 
    easier (and not to replace it), we don't want to perform this check on obj
    itself, which will have __repr__ defined but will rely on reprByProps
    to define it.
    
    WARNING: this should only be used to help define __repr__ in the following
    way:
    
    def __repr__(self):
        return tam.reprByProps(self)
        
    Other than that one use case, it should not be called or used directly.
    
    This is not a serialization mechanism; it will not handle loops in the 
    object graph. It is just a way to make creating "standard" __repr__ 
    methods easier.
    """
    className = obj.__class__.__name__
    nameValList = ', '.join(
        "{0}={1}".format(name, repr(val) if hasattr(val, '__repr__') else reprByProps(val))
        for name, val in sorted(obj.__dict__.items())
    )
#    this code was an attempt to use only those properties that the constructor
#      specifies through arguments, but it has some issues that I forget
#    nameValList = ', '.join(
#        "{0}={1}".format(name, repr(obj.__dict__[name]) if hasattr(obj.__dict__[name],'__repr__') else reprByProps(obj.__dict__[name]))
#        for name in sorted(inspect.getargspec(obj.__init__).args)
#        if name != 'self'
#    )
    moduleName = obj.__class__.__module__
    return '{moduleName}.{className}({nameValList})'.format(
        moduleName=moduleName, className=className, nameValList=nameValList)


# taken from http://code.activestate.com/recipes/413486/
def Enum(*names):
    assert names, "Empty enums are not supported" # <- Don't like empty enums? Uncomment!

    class EnumClass(object):
        __slots__ = tuple(names) + ('__dict__',)
        def __iter__(self):        return iter(constants)
        def __len__(self):         return len(constants)
        def __getitem__(self, i):  return constants[i]
        def __repr__(self):        return 'Enum' + str(names)
        def __str__(self):         return 'enum ' + str(constants)

    class EnumValue(object):
        __slots__ = ('__value')
        def __init__(self, value): self.__value = value
        Value = property(lambda self: self.__value)
        EnumType = property(lambda self: EnumType)
        def __hash__(self):        return hash(self.__value)
        def __cmp__(self, other):
            # C fans might want to remove the following assertion
            # to make all enums comparable by ordinal value {;))
            assert self.EnumType is other.EnumType, "Only values from the same enum are comparable"
            return cmp(self.__value, other.__value)
        def __invert__(self):      return constants[maximum - self.__value]
        def __nonzero__(self):     return bool(self.__value)
        def __repr__(self):        return str(names[self.__value])

    maximum = len(names) - 1
    constants = [None] * len(names)
    for i, each in enumerate(names):
        val = EnumValue(i)
        setattr(EnumClass, each, val)
        constants[i] = val
    constants = tuple(constants)
    EnumType = EnumClass()
    return EnumType

Direction = Enum('East', 'North', 'South', 'West', 'Nondet')
def oppositeDirection(self):
    """Gets opposite direction of self; raises ValueError if self is Nondet."""
    if self == Direction.East: return Direction.West
    if self == Direction.West: return Direction.East
    if self == Direction.North: return Direction.South
    if self == Direction.South: return Direction.North
    if self == Direction.Nondet: raise ValueError('there is no opposite of Direction.Nondet')

def directionShortName(self):
    if self == Direction.East: return 'E'
    if self == Direction.West: return 'W'
    if self == Direction.North: return 'N'
    if self == Direction.South: return 'S'
    if self == Direction.Nondet: return 'Nondet'
def rotateDirectionClockwise90(self):
    if self == Direction.East: return Direction.South
    if self == Direction.West: return Direction.North
    if self == Direction.North: return Direction.East
    if self == Direction.South: return Direction.West
    if self == Direction.Nondet: raise ValueError('there is no opposite of Direction.Nondet')
def rotateDirectionCounterclockwise90(self):
    if self == Direction.East: return Direction.North
    if self == Direction.West: return Direction.South
    if self == Direction.North: return Direction.West
    if self == Direction.South: return Direction.East
    if self == Direction.Nondet: raise ValueError('there is no opposite of Direction.Nondet')

N = Direction.North
S = Direction.South
E = Direction.East
W = Direction.West
NONDET = Direction.Nondet

# Usage of Enum:
#
#if __name__ == '__main__':
#    print('\n*** Enum Demo ***')
#    print('--- Days of week ---')
#    Days = Enum('Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su')
#    print(Days)
#    print(Days.Mo)
#    print(Days.Fr)
#    print(Days.Mo < Days.Fr)
#    print(list(Days))
#    for each in Days:
#        print('Day:', each)
#    print('--- Yes/No ---')
#    Confirmation = Enum('No', 'Yes')
#    answer = Confirmation.No
#    print('Your answer is not {0}'.format(not answer))


##############################################################################
## Tile stuff below here.
##############################################################################

class Tile(object):
    """
    Represents a tile type, with the properties that are recognized by
    Matt Patitz's TAS application.
    """
    def __init__(self, name, label='',
                 tilecolor='white', textcolor='black', concentration=1,
                 northglue=('', 0), southglue=('', 0),
                 westglue=('', 0), eastglue=('', 0)):
        """
        Each glue is a tuple (label, strength).
        """
        self.name = name
        self.label = label
        self.tilecolor = tilecolor
        self.textcolor = textcolor
        self.concentration = concentration
        self.northglue = northglue
        self.southglue = southglue
        self.westglue = westglue
        self.eastglue = eastglue
        self.parent = None
    
    def clone(self):
        newName = self.name 
        newLabel = self.label
        newTileColor = self.tilecolor
        newTextColor = self.textcolor
        newConcentration = self.concentration
        newNorthGlue = self.northglue
        newSouthGlue = self.southglue
        newWestGlue = self.westglue
        newEastGlue = self.eastglue
        newTile = Tile(newName, newLabel, newTextColor, newTileColor, newConcentration, newNorthGlue, newSouthGlue, newWestGlue, newEastGlue)
        return newTile
        
        
    
    def __eq__(self, other):
        return all(self.__dict__[propname] == other.__dict__[propname] 
                   for propname in self.__dict__.keys())
    
    def __ne__(self, other):
        return not (self == other)

    def tdsFormat(self):
        """
        Returns a string in the format recognized by the TAS application,
        suitable for writing to a .TDS file.
        """
        return """TILENAME %s
LABEL %s
TILECOLOR %s
TEXTCOLOR %s
CONCENTRATION %s
NORTHBIND %s
SOUTHBIND %s
WESTBIND %s
EASTBIND %s
NORTHLABEL %s
SOUTHLABEL %s
WESTLABEL %s
EASTLABEL %s
CREATE""" % (self.name, self.label, self.tilecolor, self.textcolor,
             self.concentration,
             self.northglue[1], self.southglue[1],
             self.westglue[1], self.eastglue[1],
             self.northglue[0], self.southglue[0],
             self.westglue[0], self.eastglue[0])

    def __str__(self):
        return self.tdsFormat()
    
    def __repr__(self):
        return reprByProps(self)
    
    def reflectNS(self):
        """Reflect tile north/south."""
        return Tile(
            name=self.name,
            label=self.label,
            tilecolor=self.tilecolor,
            textcolor=self.textcolor,
            concentration=self.concentration,
            northglue=self.southglue,
            southglue=self.northglue,
            westglue=self.westglue,
            eastglue=self.eastglue
        )
        
    def reflectEW(self):
        """Reflect tile east/west."""
        return Tile(
            name=self.name,
            label=self.label,
            tilecolor=self.tilecolor,
            textcolor=self.textcolor,
            concentration=self.concentration,
            northglue=self.northglue,
            southglue=self.southglue,
            westglue=self.eastglue,
            eastglue=self.westglue
        )
    
    def rotateLeft(self):
        """Rotate tile left."""
        return Tile(
            name=self.name,
            label=self.label,
            tilecolor=self.tilecolor,
            textcolor=self.textcolor,
            concentration=self.concentration,
            northglue=self.eastglue,
            southglue=self.westglue,
            westglue=self.northglue,
            eastglue=self.southglue
        )
        
    def rotateRight(self):
        """Rotate tile left."""
        return Tile(
            name=self.name,
            label=self.label,
            tilecolor=self.tilecolor,
            textcolor=self.textcolor,
            concentration=self.concentration,
            northglue=self.westglue,
            southglue=self.eastglue,
            westglue=self.southglue,
            eastglue=self.northglue
        )
    
    def rotate180(self):
        """Rotate tile 180 degrees.
        
        Note that this is different from reflecting since sides along both axes
        are swapped."""
        return Tile(
            name=self.name,
            label=self.label,
            tilecolor=self.tilecolor,
            textcolor=self.textcolor,
            concentration=self.concentration,
            northglue=self.southglue,
            southglue=self.northglue,
            westglue=self.eastglue,
            eastglue=self.westglue
        )
    
    
class TileSystem:
    """
    Represents a tile assembly system. This is a set of tile types, together with
    all other contextual information (such as the seed assembly and temperature)
    needed to simulate the self assembly of the tiles.
    """
    def __init__(self, name, tileTypes=[], seedAssembly={}):
        """Create a tile assembly system with the given name, no tile types,
        and an empty seed assembly."""
        self.name = name        # name of the tile assembly system
        self.tileTypes = tileTypes    # set of tile types
        self.seedAssembly = seedAssembly  # maps position in Z^3 to tile type
    
    def tdpFormat(self):
        """TDP format of this tile assembly system.
        
        Return a string representing the tile assembly system's .TDP file, suitable
        for creating a file that can be read by the TAS application.
        """
        seedTileNamesAndPositions = (
            "{0} {1}".format(self.seedAssembly[pos].name, ' '.join(map(str, pos)))
            for pos in self.seedAssembly.keys())
        return self.name + ".tds\n" + '\n'.join(seedTileNamesAndPositions)

    def tdsFormat(self):
        """TDS format of tile set of this tile assembly system.
        
        Return a string representing all the tiles in the format recognized 
        by the TAS application, suitable for writing to a .TDS file.
        """
        return '\n\n'.join(map(Tile.tdsFormat, self.tileTypes))

    def __str__(self):
        return self.tdpFormat()

    def __repr__(self):
        return reprByProps(self)

    def addTileType(self, tile):
        """Add tile to this tile assembly system's set of tiles."""
        #self.tileTypes.add(tile)
        #self.tileTypes.append(tile)
        self.addTileTypes([tile])

    def addTileTypes(self, tiles):
        """Add tiles to this tile assembly system's set of tiles."""
        #self.tileTypes |= set(tiles)
        #existingNames = {tile.name for tile in self.tileTypes} #PYTHON3
        existingNames = set([tile.name for tile in self.tileTypes])
        for name in (tile.name for tile in tiles):
            if name in existingNames:
                raise ValueError('tile with name {0} already exists'.format(name))
            existingNames.add(name)
        self.tileTypes += tiles
        
    def addToSeedAssembly(self, pos, tile):
        """Add tile to 3D position represented by pos."""
        self.seedAssembly[pos] = tile
    
    def writeToFiles(self, outFilename):
        """Write out tile assembly system to files for use by TAS program.
        
        Write the given tileSystem to the files named <outFilename>.tdp
        (for tile system) and <outFilename>.tds (for tile set), in the format
        recognized by the TAS application.
        """
        tds = open(outFilename + '.tds', 'w')
        tds.write(self.tdsFormat())
        tds.close()
        tdp = open(outFilename + '.tdp', 'w')
        tdp.write(self.tdpFormat())
        tdp.close()

def isSequence(seq):
#    return type(seq) in (tuple, list)
    return isinstance(seq, tuple) or isinstance(seq, list)

class MultisignalType(object):
    """Tuple of signal types.
    
    Each signal type is a pair (name, validValues), where name is a string 
    representing the name of the signal and valid values is a list of strings
    representing the values the signal can take."""
    def __init__(self, verbose=VERBOSE_SIGNALS, **signalTypeDict):
        self.signalTypeDict = dict(signalTypeDict)
        for name, values in self.signalTypeDict.items():
            if not isSequence(values):
                self.signalTypeDict[name] = (values,)
            else:
                self.signalTypeDict[name] = tuple(values)
        self.updateSignalTypeList()
        self.verbose = verbose
        for validVals in self.signalTypeDict.values():
            if len(set(validVals)) != len(validVals):
                raise SignalDuplicateValueError(validVals)
        
       
    def noChoiceMultisignal(self):
        """Returns the multisignal consisting of those signals which have only one valid value"""

        ret = Multisignal([(signalName, signalValues[0]) for (signalName,signalValues) in self.signalTypeDict.items() 
                               if len(signalValues) == 1])
        return ret
       
    def __len__(self):
        return len(self.signalTypeDict)

    def names(self):
        """Return list of signal names."""
        return [name for (name, values) in self.signalTypeList]
    
    @classmethod
    def empty(verbose=VERBOSE_SIGNALS):
        return MultisignalType(**dict())
            
    def clone(self):
        newDict = dict(self.signalTypeDict)
        newMultisignalType = MultisignalType(self.verbose, **newDict)
        return newMultisignalType
#         return MultisignalType(self.verbose, **dict(self.signalTypeDict))
        
    def updateSignalTypeList(self):
        self.signalTypeList = list(self.signalTypeDict.items())
        self.signalTypeList.sort(key=lambda (name, vals): name)
        
    def addSignalTypes(self, **newSignalTypeDict):
        """Add new signal types."""
        for validVals in newSignalTypeDict.values():
            if len(set(validVals)) != len(validVals):
                raise SignalDuplicateValueError(validVals)
        for name, validVals in newSignalTypeDict.items():
            if name in self.signalTypeDict:
                raise SignalDuplicateNameError(name)
            self.signalTypeDict[name] = tuple(validVals)
            self.signalTypeList.append((name, validVals))
        self.signalTypeList.sort(key=lambda (name, vals): name)
        
    def removeSignalTypes(self, *names):
        """Remove signal types with the given names."""
        for name in names:
            if name not in self.signalTypeDict:
                raise SignalInvalidNameError(name, self.signalTypeDict.keys())
            del self.signalTypeDict[name]
        self.signalTypeList = list(self.signalTypeDict.items())
        self.signalTypeList.sort(key=lambda (name, vals): name)
        
    def create(self, **nameValDict):
        """Create a multisignal with the specified mapping of names to values."""
        for name, val in nameValDict.items():
            if name not in self.signalTypeDict:
                raise SignalInvalidNameError(name, self.signalTypeDict.keys())
            validVals = self.signalTypeDict[name]
            if val not in validVals:
                raise SignalInvalidValueError(name, val, validVals)
        nameValList = [(name, nameValDict[name]) for (name, validVals) in self.signalTypeList]
        return Multisignal(nameValList, self.verbose)

    def createNoNameCheck(self, **nameValDict):
        """Create a multisignal with the specified mapping of names to values.
        
        The names are not checked, so the given nameValDict could contain
        more or fewer signal names than this MultisignalType represents."""
        for name, val in nameValDict.items():
            if name in self.signalTypeDict:
                validVals = self.signalTypeDict[name]
                if val not in validVals:
                    raise SignalInvalidValueError(name, val, validVals)
        nameValList = [(name, nameValDict[name]) for (name, validVals) in self.signalTypeList
                       if name in nameValDict]
        return Multisignal(nameValList, self.verbose)

    def restrict(self, **nameValuesDict):
        """Create a MultisignalType with the given restrictions of values.
        
        Assume for any unspecified signal name that all original values are kept."""
        for name, values in nameValuesDict.items():
            if not isSequence(values): 
                nameValuesDict[name] = values = (values,)
            if name not in self.signalTypeDict:
                raise SignalInvalidNameError(name, self.signalTypeDict.keys())
            validVals = self.signalTypeDict[name]
            for value in values:
                if value not in validVals:
                    raise SignalInvalidValueError(name, value, validVals)
        for name, values in self.signalTypeDict.items():
            if name not in nameValuesDict:
                nameValuesDict[name] = values
        return MultisignalType(verbose=self.verbose, **nameValuesDict)
        
    def __getitem__(self, name):
        """Allows multisignals to index values by name; i.e. ms['bit'] == ['0','1']"""
        return self.signalTypeDict[name]

    def __setitem__(self, name, validVals):
        """Allows multisignals to alter valid values by name; i.e. ms['bit'] = ['0','1']"""
        self.signalTypeDict[name] = tuple(validVals)
        self.updateSignalTypeList()

    def __delitem__(self, name):
        """Allows multisignals to delete values by name; i.e. del(ms['bit'])"""
        del(self.signalTypeDict[name])
        self.signalTypeList = [(sigName, validVals) 
                               for (sigName, validVals) in self.signalTypeList 
                               if name != sigName]

    def __str__(self):
        return ';'.join('{0}:{1}'.format(name, validVals) for name, validVals in self.signalTypeList)
    
    def __repr__(self):
        return (("tam.MultisignalType(verbose={v}, "
             + "**{signalTypeDict})").format(
               signalTypeDict=self.signalTypeDict, v=self.verbose))

    def __iter__(self):
        return self.multisignals()
    
    def multisignals(self):
        """Enumerate all possible multisignals represented by this type."""
        lengths = [len(values) for name, values in self.signalTypeList]
        curSignalIndices = [0] * len(self.signalTypeList)
        numGlues = 1
        for length in lengths:
            numGlues *= length
        for glueIdx in range(numGlues):
            multisignalDict = dict((signalName, signalsList[i]) for i, (signalName, signalsList)
                    in zip(curSignalIndices, self.signalTypeList))
            yield self.create(**multisignalDict)
            # increment to next glue using carry addition
            for i in range(len(self.signalTypeList)):
                curSignalIndices[i] += 1
                # update next index if necessary, otherwise leave rest alone
                if curSignalIndices[i] == lengths[i]:
                    curSignalIndices[i] = 0
                else:
                    break
                
    def __eq__(self, other):
        if set(self.signalTypeDict.keys()) != set(other.signalTypeDict.keys()):
            return False
        for ((name, values), (otherName, otherValues)) in zip(self.signalTypeList, other.signalTypeList):
            if values != otherValues:
                return False
        return True


    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(tuple(self.signalTypeList))
    
    def nameUnion(self, other):
        """Combine signal types with disjoint names to be the union of the signal types.
        
        For instance,
        
            carryMst = tam.MultisignalType(carry=['n','c'])
            borrowMst = tam.MultisignalType(borrow=['nb','b'])
            carryBorrowMst = carryMst.nameUnion(borrowMst)
        
        creates a MultisignalType that can represent a carry and a borrow
        simultaneously. They must also have disjoint signal names.
        """
        for name, validVals in self.signalTypeDict.items():
            if name in other.signalTypeDict:
                raise NameOverlapError(list(self.signalTypeDict.keys()), list(other.signalTypeDict.keys()))
        signalTypeDict = dict(self.signalTypeDict)
        signalTypeDict.update(other.signalTypeDict)
        newMst = MultisignalType(verbose=self.verbose, **signalTypeDict)
        return newMst
    
    def valueUnion(self, other):
        """Combine signal types with the same names by taking the union of their
        values for each shared name.
        
        For instance,
        
            carryMst = tam.MultisignalType(carry=['n','c'])
            borrowMst = tam.MultisignalType(carry=['n','b'])
            carryBorrowMst = carryMst.valueUnion(borrowMst)
        
        creates a MultisignalType that can represent a carry with values
        ['n','b','c']. They must also have exactly the same signal names.
        """
        if set(self.signalTypeDict.keys()) != set(other.signalTypeDict.keys()):
            raise NameDifferenceError(list(self.signalTypeDict.keys()), list(other.signalTypeDict.keys()))
        signalTypeDict = dict(self.signalTypeDict)
        for name in signalTypeDict:
            signalTypeDict[name] = list(set(signalTypeDict[name] + other.signalTypeDict[name]))
        newMst = MultisignalType(verbose=self.verbose, **signalTypeDict)
        return newMst
    
    def isValidMultisignal(self, ms):
        """Indicates whether ms is a Multisignal that this MultisignalType produces."""
        if set(ms.nameValDict.keys()) != set(self.signalTypeDict.keys()):
            return False
        for name, value in ms.nameValDict.items():
            if value not in self.signalTypeDict[name]:
                return False
        return True
    


class Multisignal:
    """Tuple of signals.
    
    Do not use the constructor; use MultisignalType.createMultisignal
    
    If you must use this constructor, pass it a list of (key,value) pairs."""
    def __init__(self, nameValList, verbose=VERBOSE_SIGNALS):
        self.nameValDict = dict(nameValList)
        self.nameValList = sorted(nameValList)
        self.verbose = verbose
        
    def __str__(self):
        """Return string in a format suitable for using as a glue label."""
        if self.verbose:
            return ','.join('{0}={1}'.format(name, val) for name, val in self.nameValList)
        else:
            return ','.join('{0}'.format(val) for name, val in self.nameValList)
    
    def __len__(self):
        return len(self.nameValDict)

    def __repr__(self):
        return (("tam.Multisignal(nameValList={nameValList}, "
             + "verbose={verbose})").format(nameValList=self.nameValList,
                                           verbose=self.verbose))
    
    def __getitem__(self, name):
        """Allows multisignals to index values by name; i.e. ms['bit'] == '1'"""
        try:
            self.nameValDict[name]
        except KeyError:
            pass
        return self.nameValDict[name]

    def __setitem__(self, name, val):
        """Allows multisignals to alter values by name; i.e. ms['bit'] = '0'"""
        oldval = self.nameValDict[name]
        self.nameValDict[name] = val
        self.nameValList[self.nameValList.index((name, oldval))] = val

    def __delitem__(self, name):
        """Allows multisignals to delete values by name; i.e. del(ms['bit'])"""
        del(self.nameValDict[name])
        self.nameValList = [(sigName, val) 
                            for (sigName, val) in self.nameValList 
                            if name != sigName]

    def __eq__(self, other):
        """Indicate if these represent the same name/value pairs; ignores verbosity."""
        return self.nameValList == other.nameValList
        
    def __ne__(self, other):
        return not (self == other)
    
    def __hash__(self):
        return hash(tuple(self.nameValList))
    
    def __add__(self, other):
        selfNameSet = set(name for (name,value) in self.nameValList)
        otherNameSet = set(name for (name,value) in other.nameValList)
        if not selfNameSet.isdisjoint(otherNameSet):
            raise SignalDuplicateNameError(selfNameSet & otherNameSet)
        nameValList = self.nameValList + other.nameValList
        nameValList.sort(key=lambda (name, value): name)
        return Multisignal(nameValList, verbose=self.verbose)
    
    def nameUnionDuplicateSignalAllowed(self, other):
        '''JP - Indicates that two different multisignals have a common signal between them'''
        selfNameSet = set(name for (name,value) in self.nameValList)
        otherNameSet = set(name for (name,value) in other.nameValList)
        if not selfNameSet.isdisjoint(otherNameSet):
            for name in (selfNameSet & otherNameSet):
                if self.nameValDict[name] != other.nameValDict[name]:
                    raise DuplicateSignalNameConflictingValuesError(name, str(self), self.nameValDict[name], str(other), other.nameValDict[name])
            nameValDict = dict(self.nameValDict)
            nameValDict.update(other.nameValDict)
            nameValList = list(nameValDict.items())
        else:
            nameValList = self.nameValList + other.nameValList
        nameValList.sort(key=lambda (name, value): name)
        return Multisignal(nameValList, verbose=self.verbose)
    
    def __iter__(self):
        """Iterate over (name,value) pairs of this multisignal."""
        return iter(self.nameValList)
    






class GlueTemplate:
    """A GlueTemplate represents a "type of glue".
    
    A GlueTemplate specifies a binding strength and a MultisignalType.
    
    It is for binding tiles in specific positions in an assembly, and 
    encompasses a collection of related glues.
    It is not intended for direct use by client code, but is used to configure
    signal passing between TileTemplates by the tam library.
    
    A GlueTemplate is added as either an input side or an output side to a
    TileTemplate; while nothing prevents doing otherwise, it only makes sense
    to add a GlueTemplate as an input side to at least one TileTemplate and as
    an output side to at least one TileTemplate (not necessarily a different
    TileTemplate).
    """
    def __init__(self, strength=1, multisignalType=MultisignalType(verbose=False)):
        self.strength = strength
        self.multisignalType = multisignalType
    
    def create(self, **nameValDict):
        """Converts a name/value dict to a glue, a pair (label,strength).
        The multisignal is presented as a keyword argument list.
        The form is 'name1=value1,name2=value2,...' if property names are
        enabled for this TileTemplate; otherwise the format is
        value1,value2,..."""
        return (str(self.multisignalType.create(**nameValDict)), self.strength)
    
    def createLabel(self, **nameValDict):
        """Converts a dict of name:value pairs to a string representing the 
        glue label.
        The form is 'name1=value1,name2=value2,...' if property names are
        enabled for this TileTemplate; otherwise the format is
        value1_value2..."""
        return (self.create(**nameValDict))[0]
    
    def __str__(self):
        return '[strength={0}, multisignalType={1}]'.format(
            self.strength, self.multisignalType)

    def __repr__(self):
        return reprByProps(self)

    def __iter__(self):
        """Enumerate all possible glues, represented as (string,int) pairs,
        for this template. In the __add__ example above,
            for glue in embedCarryAndBorrowGlue:
                print(glue)
        prints the four glues
            (n_nb,1)
            (n_b,1)
            (c_nb,1)
            (c_b,1)
        """
        return self.glues()

    def glues(self):
        """
        Used by __iter__ to create the generator for enumerating all possible
        glue labels (as a string), given the list of lists of signals.
        """
        for multisignal in self.multisignalType:
            yield (str(multisignal), self.strength)

class Transition:
    """Represents a signal transition for computing output signals
    of a tile from input signals."""
    def __init__(self, inputs=(), outputs=(), function=None, expression=None, table=None):
        """Add a transition computing output signal(s) to this TileTemplate.
        
        inputs and outputs are lists of strings specifying the names of the input
        and output signal names, in the order in which the function transition 
        receives them as arguments or returns them in a tuple."""
        self.function = ensureIsFunction(inputs, function, expression, table)
        self.inputNames = tuple(inputs)
        self.outputNames = tuple(outputs)
    
#     def clone(self):
#         return Transition(self.inputs, self.outputs, self.function)
    
    def __call__(self, *args):
        """Call this transition's function."""
        return self.function(*args)
    
    def apply(self, inputMultisignal):
        """Call this transition's function with the given input multisignal
        and return an output multisignal.
        
        The difference between this and __call__ is the preservation of input
        and output names instead of positional parameters for input and 
        output tuples for output."""
        inputValues = [inputMultisignal[inputName] for inputName in self.inputNames]
        # compute output from input
        outputValues = self.function(*inputValues)
        # if outputs is None, propagate that
        if outputValues is None:
            return None
        # place output in a tuple if it is not a sequence already
        if not isSequence(outputValues):
            outputValues = (outputValues,)
        outputNameValueList = [(self.outputNames[pos], outputValue) 
                               for (pos,outputValue) in enumerate(outputValues)]
        outputMultisignal = Multisignal(outputNameValueList, verbose=inputMultisignal.verbose)
        return outputMultisignal


class PropertyFunction:
    """Represents a function for computing non-glue properties of a tile from
    either output and/or input signals."""
    def __init__(self, inputs=(), outputs=(), function=None, expression=None):
        """Add a transition computing output signal(s) to this TileTemplate.
        
        inputs and outputs are lists of strings specifying the names of the input
        and output signal names, in the order in which the function transition 
        receives them as arguments or returns them in a tuple.
        
        Note that names in expression can refer only to signal names that are
        contained in exactly one of inputNames or outputNames. Otherwise, the
        positional ordering of inputs to function must be used, in which
        function will be called with the values associated with inputNames
        given first, followed by those in outputNames."""
        if not isSequence(inputs):
            inputs = (inputs,)
        if not isSequence(outputs):
            outputs = (outputs,)
        inputNamesSet = set(inputs)
        outputNamesSet = set(outputs)
        if not (inputNamesSet.isdisjoint(outputNamesSet)):
            raise SignalDuplicateNameError(inputNamesSet & outputNamesSet)
        
        self.function = ensureIsFunction(inputs + outputs, function, expression, None)        
        self.inputNames = inputs
        self.outputNames = outputs
    
    def apply(self, inputMultisignal, outputMultisignal):
        """Call this transition's function with the given input and output
        multisignals and return the value of the property."""
        inputValues = [inputMultisignal[inputName] for inputName in self.inputNames]
        outputValues = [outputMultisignal[outputName] for outputName in self.outputNames]
        # compute output from input
        propertyValue = self.function(*(inputValues + outputValues))
        return propertyValue

class ChooserFunction:
    """Represents a function for computing which tileset should be generated from
    within a chooserSet for a given input multisignal."""
    def __init__(self, inputNames=(), function=None, expression=None, table=None):
        """Add a function for selecting the appropriate tileTemplate from a chooserSet.
        
        inputs and outputs are lists of strings specifying the names of the input
        and output signal names, in the order in which the function transition 
        receives them as arguments or returns them in a tuple.
        
        Note that names in expression can refer only to signal names that are
        contained in exactly one of inputNames or outputNames. Otherwise, the
        positional ordering of inputs to function must be used, in which
        function will be called with the values associated with inputNames
        given first, followed by those in outputNames."""
        if not isSequence(inputNames):
            inputNames = (inputNames,)

        self.function = ensureIsFunction(inputNames, function, expression, table)        
        self.inputNames = inputNames
    
    def apply(self, inputMultisignal):
        """Call this transition's function with the given input and output
        multisignals and return the value of the property."""
        inputValues = [inputMultisignal[inputName] for inputName in self.inputNames]
        # compute output from input
        tileNames = ensureIsSequence(self.function(*(inputValues)))
        return tileNames
    

def expressionToFunction(expression, inputNames):
    """Turns an expression as a string, with a list of input names, into a 
    function taking parameters with those names as inputs, which returns the
    value of the expression."""
    def function(*vargs):
        z = zip(inputNames, vargs)
        d = dict(z)
        return eval(expression, {}, dict(zip(inputNames, vargs)))
    return function


def tableToFunction(table):
    """Turns a table of input/output pairs of tuples (implemented either as a 
    list of pairs of input/output tuples, or a dict mapping input tuples to 
    output tuples) into a function taking parameters, which returns the
    value of the output tuple, or raises a ValueError if the input tuple is not
    in the table."""
    if isinstance(table, list):
        table = dict(table)
    def function(*vargs):
        return table[tuple(vargs)]
    return function

def ensureIsFunction(inputNames, function, expression, table):
    numNotNone = 0
    if expression is not None:
        retFunction = expressionToFunction(expression, inputNames)
        numNotNone += 1
    if table is not None:
        retFunction = tableToFunction(table)
        numNotNone += 1
    if function is not None:
        retFunction = function
        numNotNone += 1
    if numNotNone != 1:
        raise ValueError('exactly one of function, expression, or table must be specified')
    return retFunction

class TileTemplate(object):
    """Represents a "kind of tile type", a family of related tile types.
    It can only be used for specifying a collection of related tiles
    that all share the same input/output/terminal side designations.
    
    A TileTemplate consists of 1-4 (GlueTemplates, direction) pairs, one for
    each of the north, south, east, and west sides of the tile type,
    specifying the type of glue that goes on that side and whether it is an
    input or output side (sides without glue are terminal). GlueTemplates are
    not intended to be controlled by the client, but by a TileSetTemplate
    object, which handles the input/output relationships between TileTemplate
    objects. A TileTemplate also requires
    functions specifying how signals from the input sides create signals on
    the output sides. Any direction not added as an input side or output side
    is implicitly a terminal side, and will result in strength 0 glues being
    produced on that side. Each tile type produced by this template will be
    given a unique name and label based on the input side glues.
    """
    
    def __init__(self, name, **tileTypeArgs):
        """Create a TileTemplate with all terminal sides.
        tileTypeArgs is a dict specifying extra keyword arguments to be passed
        to the TileType constructor when creating tile types; for instance,
        tilecolor or textcolor. It should not contain any of the glues or 
        label or name, as these are computed from the input signals. This means
        that TileTemplates can be fed these arguments, e.g.:
          tileTemplate = TileTemplate(name='start',tilecolor='green',textcolor='orange')
        """
        self.name = name # a special prefix to attach to all tile type names
        self.inputJoins = []  # list of Joins
        self.outputJoins = [] # list of Joins
        self.transitions = [] # list of triples (func, inputs, outputs)
        self.propertyFunctions = {} # dict mapping property name to triple (func, inputs, outputs)
        self.tileTypeArgs = tileTypeArgs # dict giving tile type properties to hardcode, e.g.  {'label': 0}
        self.auxiliaryInputMultisignalType = MultisignalType.empty()
        self.parent = ""
        #TODO: compute next two on the fly from joins as they are needed
        self.outputObjectDict = {}
        self.inputObjectDict = {}
        
    def clone(self):
        new_name = self.name 
        newTileTypeArgs = dict(self.tileTypeArgs)
        newAuxInputMultisignalType = self.auxiliaryInputMultisignalType.clone()
        #TODO: change if deep copy is needed
        newPropertyFunctions = dict(self.propertyFunctions)
        newTransitions = list(self.transitions)
        newOutputObjectDict = dict(self.outputObjectDict)
        newInputObjectDict = dict(self.inputObjectDict)
        #XXX: module is responsible for copying inputJoins, outputJoins, parent
        newTT = TileTemplate(new_name, **newTileTypeArgs)
        newTT.outputObjectDict = newOutputObjectDict
        newTT.inputObjectDict = newInputObjectDict
        newTT.auxiliaryInputMultisignalType = newAuxInputMultisignalType
        newTT.propertyFunctions = newPropertyFunctions
        newTT.transitions = newTransitions
        return newTT
    
        
        
    def __repr__(self):
        return self.name
        
    def addAuxiliaryInput(self, multisignalType):
        """Used to allow two or more tile types with the same input signal values to nondeterministically compete to bind.
        
        The auxiliary input multisignal type is used to create different tile types with the same input multisignal
        but different output multisignals. An auxiliary input multisignal is given to the transitions, along with
        the input multisignals that are actually coming from input directions, and all of these together are
        used by the transitions to determine output signal values.
        
        There are other ways to add nondeterminism (e.g., chooser functions to choose among different tile templates)
        but this is used to have nondeterminism within a single TileTemplate."""
        self.auxiliaryInputMultisignalType = self.auxiliaryInputMultisignalType.nameUnion(multisignalType)

    def inputDirMultisignalTypeDict(self):
        """Return dict mapping direction (including Nondet) to input MultisignalType."""
        ret = collections.defaultdict(MultisignalType)
        for join in self.inputJoins:
            direction = oppositeDirection(join.neighborhood.direction)
            if direction in ret:
                ret[direction] = ret[direction].valueUnion(join.multisignalType)
            else:
                ret[direction] = join.multisignalType
        if self.auxiliaryInputMultisignalType:
            ret[Direction.Nondet] = self.auxiliaryInputMultisignalType
        return ret
    
    def outputDirMultisignalTypeDict(self):
        """Return dict mapping (direction, MultisignalType), 
        of output multisignal types."""
        ret = collections.defaultdict(MultisignalType)
        for join in self.outputJoins:
            direction = join.neighborhood.direction
            if direction in ret:
                ret[direction] = ret[direction].valueUnion(join.multisignalType)
            else:
                ret[direction] = join.multisignalType

        return ret
    
    def inputDirMultisignalTypeList(self):
        """Return list of pairs (direction, MultisignalType), in alphabetical
        order of direction, including Nondet, of input multisignal types."""
        ret = self.inputDirMultisignalTypeDict()
        ret = list(ret.items())
        ret.sort()
        return ret
    
    def outputDirMultisignalTypeList(self):
        """Return list of pairs (direction, MultisignalType), in alphabetical
        order of direction, of output multisignal types."""
        ret = self.outputDirMultisignalTypeDict()
        ret = list(ret.items())
        ret.sort()
        return ret

    def isInputSide(self, direction):
        ''' JP - ensures that the specified direction is an input side'''
        for join in self.inputJoins:
            if join.neighborhood.direction == oppositeDirection(direction):
                return True
        return False

    def inputNeighborhood(self, direction):
        ''' JP - Returns the neighborhood given on the input side '''
        for join in self.inputJoins:
            if join.neighborhood.direction == oppositeDirection(direction):
                return join.neighborhood
        raise ValueError('no input neighborhood in direction {0}'.format(direction))

    def inputNeighborhoods(self):
        retDict = {}
        for direction in (N,S,W,E):
            for join in self.inputJoins:
                if join.neighborhood.direction == oppositeDirection(direction):
                    retDict[direction] = join.neighborhood
        return retDict

    def isOutputSide(self, direction):
        ''' JP - ensures that the specified direction is an output side'''
        for join in self.outputJoins:
            if join.neighborhood.direction == direction:
                return True
        return False

    def outputNeighborhood(self, direction):
        ''' JP - Returns the neighborhood given on the output side '''
        for join in self.outputJoins:
            if join.neighborhood.direction == direction:
                return join.neighborhood
        raise ValueError('no output neighborhood in direction {0}'.format(direction))

    def createTilesFromInputMultisignal(self, inputMultisignal):
        ''' JP - creates tiles from the inputMultisingal provided.'''
        if self.auxiliaryInputMultisignalType:
            return [self.createTileFromFullInputMultisignal(inputMultisignal + auxiliaryInputMultisignal) for auxiliaryInputMultisignal in self.auxiliaryInputMultisignalType]
        else:
            return [self.createTileFromFullInputMultisignal(inputMultisignal)]
    
    def createTileFromFullInputMultisignal(self, inputMultisignal):
        """Create a tile from the input multisignal provided."""
        inputDirMultisignalTypeList = self.inputDirMultisignalTypeList()   

        separator = '_' if len(inputMultisignal.nameValDict) > 0 else ''
        tilename = self.name + separator + '_'.join('{0}:{1}'.format(
            direction, multisignalType.createNoNameCheck(**inputMultisignal.nameValDict))
            for (direction, multisignalType) in inputDirMultisignalTypeList
        )
        northglue,southglue,eastglue,westglue = [None]*4
        
        # set input glues
        for direction,multisignalType in inputDirMultisignalTypeList:
            # TODO: figure out why a new Multisignal is created from inputMultisignal, when it already is a Multisignal
            glueLabel = str(multisignalType.createNoNameCheck(**inputMultisignal.nameValDict))
            inputNeighborhood = self.inputNeighborhood(direction)
            glueAnnotation = inputNeighborhood.glueAnnotation
            glue = (glueLabel + glueAnnotation, inputNeighborhood.strength)
            if   direction == N: northglue = glue
            elif direction == S: southglue = glue
            elif direction == W: westglue = glue
            elif direction == E: eastglue = glue
            elif direction == NONDET: pass
            else: raise ValueError('{0} is not a valid direction'.format(direction))

        outputMultisignal = Multisignal({})
         
        # populate outputMultisignal
        for transition in self.transitions:
            outputMultisignal += transition.apply(inputMultisignal)
        
        # set output glues
        completeOutputMultisignal = Multisignal({})
        outputDirMultisignalTypeList = self.outputDirMultisignalTypeList()
        for direction,multisignalType in outputDirMultisignalTypeList:
            outputDirMultisignal = multisignalType.createNoNameCheck(**outputMultisignal.nameValDict)
            # ensure that if there is only one output value, a transition isn't necessary
            noChoiceMs = multisignalType.noChoiceMultisignal()
            outputDirMultisignal = outputDirMultisignal.nameUnionDuplicateSignalAllowed(noChoiceMs)
            try:
                completeOutputMultisignal = completeOutputMultisignal.nameUnionDuplicateSignalAllowed(outputDirMultisignal)
            except DuplicateSignalNameConflictingValuesError as error:
                 raise error
                
            glueLabel = str(outputDirMultisignal)
            outputNeighborhood = self.outputNeighborhood(direction)
            glueAnnotation = outputNeighborhood.glueAnnotation
            
            glue = (glueLabel + glueAnnotation, outputNeighborhood.strength)
            if   direction == N: northglue = glue
            elif direction == S: southglue = glue
            elif direction == W: westglue = glue
            elif direction == E: eastglue = glue
            else: raise ValueError('{0} is not a valid direction'.format(direction))
        
        # set property values
        tilePropertiesToSet = {}
        for propertyName,propertyFunction in self.propertyFunctions.items():
            propertyValue = propertyFunction.apply(inputMultisignal, completeOutputMultisignal)
            tilePropertiesToSet[propertyName] = propertyValue
        
        # place calculated glues in tileProperties to set along with other properties

        gluePropertiesToSet = {}
        for glue,gluename in zip((northglue,southglue,eastglue,westglue), 
                                 ('northglue','southglue','eastglue','westglue')):
            
            if glue:
#                if gluename in self.tileTypeArgs:
#                    raise ValueError('glue {0} is already hardcoded into {1} and cannot be calculated'.format(gluename, self)) 
                gluePropertiesToSet[gluename] = glue
                
        
        tilePropertiesToSet.update(self.tileTypeArgs)
        tilePropertiesToSet.update(gluePropertiesToSet)
      
        tile = Tile(name = tilename, **(tilePropertiesToSet)
        )
        \
        return tile
    
    def getStrengthErrors(self):
        """Return list of errors associated with strength mismatches.
        
        If the number of input sides is 1, the strength must be 2.
        If the number of input sides is 2, the strength of each must be 1.
        If the number of input sides is > 2, this alone constitutes an error. """
        errors = []
        if self.numInputSides() == 1:
            joins = self.inputSides()[0]
            for join in joins:
                if join.strength != 2:
                    errors.append(StrengthError(self, join))
        if self.numInputSides() == 2:
            for joins in self.inputSides.values():
                for join in joins:
                    if join.strength != 1:
                        errors.append(StrengthError(self, join))
        if self.numInputSides() > 2:
            errors.append(TooManyInputSidesError(self))
        return errors
    
    def isValidInputMultisignal(self, ms):
        """Indicates whether ms is a valid multisignal for this TileTemplate's total input multisignal type."""
        inputMultisignalType = self.inputMultisignalType()
        return inputMultisignalType.isValidMultisignal(ms)
    
    def inputMultisignalType(self, direction=None):
        """If direction is None or unspecified, returns multisignal type of all inputs.
        if direction is one of Direction enum values, then returns the MultisignalType
        of just that direction (including nondeterministic inputs)"""
        mst = MultisignalType(VERBOSE_SIGNALS)
        mstDict = self.inputDirMultisignalTypeDict()
        if direction is None:
            for d in mstDict.keys():
                mst = mst.nameUnion(mstDict[d])
        else:
            mst = mstDict[direction]
        return mst
        
    def addTransition(self, inputs=(), outputs=(), function=None, 
                      expression=None, table=None):
        """Add a transition computing output signal(s) to this TileTemplate.
        
        inputs and outputs are lists of strings specifying the names of the input
        and output signal names, in the order in which the function transition 
        receives them as arguments or returns them in a tuple."""
        inputs = ensureIsSequence(inputs)
        outputs = ensureIsSequence(outputs)
        self.transitions.append(Transition(inputs=inputs, outputs=outputs, 
                    function=function, expression=expression, table=table))
        
    def removeTransition(self, outputs):
        """Removes the transition with the given list of output signal names.
        
        If no such tuple of output signal names exists, raises a TODO"""
        if not isSequence(outputs):
            outputs = (outputs,)
        else:
            outputs = tuple(outputs)
        newTransitions = filter(lambda t: t.outputNames != outputs, self.transitions)
        if len(newTransitions) != len(self.transitions) - 1:
            raise NonexistentTransitionError(outputs, self.transitions)
        else:
            self.transitions = newTransitions
    
    def setPropertyFunction(self, name, inputs=[], outputs=[], function=None, expression=None):
        self.propertyFunctions[name] = PropertyFunction(inputs=inputs, 
            outputs=outputs, function=function, expression=expression)
        
    def setLabelFunction(self, inputs=[], outputs=[], function=None, expression=None):
        self.setPropertyFunction('label', inputs, outputs, function, expression)
        
    def setConcentrationFunction(self, inputs=[], outputs=[], function=None, expression=None):
        self.setPropertyFunction('concentration', inputs, outputs, function, expression)
        
    def setTilecolorFunction(self, inputs=[], outputs=[], function=None, expression=None):
        self.setPropertyFunction('tilecolor', inputs, outputs, function, expression)
        
    def setTextcolorFunction(self, inputs=[], outputs=[], function=None, expression=None):
        self.setPropertyFunction('textcolor', inputs, outputs, function, expression)
        
    def removePropertyFunction(self, name):
        del self.propertyFunctions[name]
    
    def numInputSides(self):
        if not self.inputJoins:
            return 0
        sides = set(join.neighborhood.direction for join in self.inputJoins)
        return len(sides)
    
    def numOutputSides(self):
        if not self.outputJoins:
            return 0
        sides = set(join.neighborhood.direction for join in self.outputJoins)
        return len(sides)
    

def ensureIsSequence(obj):
    """If"""
    if isSequence(obj):
        return tuple(obj)
    else:
        return (obj,)

class Neighborhood:
    
    """They must all share the same MultisignalType.
        
    JP - Also Includes all TileTemplates which share this multisignal type"""
    def __init__(self, strength, direction):
        self.strength = strength
        self.direction = direction
        self.glueAnnotation = None
        self.multisignalType = None
        self.joins = []
        
    def clone(self):
        #do joins here?
        '''joinTemp = list(self.joins)
        newJoins = []
        for join in joinTemp:
            newJ = join.clone()
            newJoins.append(newJ)'''
        newStrength = self.strength
        newDirection = self.direction
        newGlueAnnotation = self.glueAnnotation
        newMultisignalType = self.multisignalType.clone()
        newNeighborhood = Neighborhood(newStrength,newDirection)
        newNeighborhood.glueAnnotation = newGlueAnnotation
        newNeighborhood.multisignalType = newMultisignalType
        ##newNeighborhood.joins = newJoins
        return newNeighborhood
        
        
        
    def addJoin(self, join):
        self.joins.append(join)
        self._update()
    
    def addJoins(self, joins):
        self.joins.extend(joins)
        self._update()

    def _update(self):
        """Updates glueAnnotation and multisignalType to reflect all joins."""
        self.multisignalType = None
        input_names = set()
        output_names = set()
        for join in self.joins:
            input_names.add(join.fromObj.name)
            output_names.add(join.toObj.name)
            if self.multisignalType is None:
                self.multisignalType = join.multisignalType
            else:
                self.multisignalType.valueUnion(join.multisignalType)
        input_names = sorted(input_names)
        output_names = sorted(output_names)
        self.glueAnnotation = ';{0}-{1}>{2}'.format(','.join(input_names),
                                                    directionShortName(self.direction),
                                                    ','.join(output_names))

    def combine(self, other):
        assert self.direction == other.direction and self.strength == other.strength
        ret = Neighborhood(self.strength, self.direction)
        ret.addJoins(self.joins)
        ret.addJoins(other.joins)
        for join in ret.joins:
            join.neighborhood = ret
        return ret
        


class ChooserSet:
    # A ChooserSet contains exactly the set of TileTemplates which are in the same
    # neighborhoods for all input sides
    # set of tile templates; disjoint union of all chooser sets should be set of all tile templates in tile set template
    # needs chooser function in addition to tile templates if there are more than 1
    # chooser only needs to work for overlapping input signal values; library should make correct choice otherwise
    
    # inputMultisignalType() (nameUnion over input sides of the valueUnion over tile templates)
    
    def __init__(self, tileSetTemplate, tileTemplate):
        self.tileSetTemplate = tileSetTemplate
        self.tileTemplate = tileTemplate # XXX: we conjecture this not needed, but maybe it is
        self.inputMst = tileTemplate.inputMultisignalType()
        self.tileSet = [tileTemplate] #XXX: rename this
        self.neighborhoods = tileTemplate.inputNeighborhoods()
        self.inputs = None
        self.function = None
    
    def clone(self, tile_templates):
        nameTTDict = {}
        for tile in tile_templates:
            nameTTDict[tile.name] = tile
            
        newTileSetTemplate = self.tileSetTemplate
        newTileTemplate = nameTTDict.get(self.tileTemplate.name)
        newInputMst = self.inputMst.clone()
        newTileSet = []
        for tile in self.tileSet:
            newTile = nameTTDict.get(tile.name)
            newTileSet.append(newTile)
        
        newNeighborhoods = {}
        #for value in newNeighborhoods.values():
            #value.clone()
        for direction in (N,S,W,E):
            if self.neighborhoods.get(direction) is not None:
                newNbrhdVal = self.neighborhoods.get(direction)
                newNbrhdValCopy = newNbrhdVal.clone()
                newNeighborhoods[direction] = newNbrhdValCopy
        cpChooserSet = ChooserSet(newTileSetTemplate, newTileTemplate)
        cpChooserSet.inputMst = newInputMst
        cpChooserSet.tileSet = newTileSet
        cpChooserSet.neighborhoods = newNeighborhoods
        return cpChooserSet
        
        
   
        
        
        

    def inputMultisignalType(self):
        return self.inputMst
    

    def chooseTileTemplates(self, inputMultisignal):
        matchSet = set()
        for tt in self.tileSet:
            if tt.isValidInputMultisignal(inputMultisignal):
                matchSet.add(tt)
        if len(matchSet) == 1:
            return list(matchSet)
        elif len(matchSet) == 0:
            return []
        else:
            tileTemplatesNamesWithChoosers = set(tileTemplate.name for tileTemplate in matchSet) & set(self.tileSetTemplate.chooserFunctionDict.keys())
            if len(tileTemplatesNamesWithChoosers) == 0:
                raise(MissingChooserError(matchSet))
            elif len(tileTemplatesNamesWithChoosers) > 1:
                raise(ConflictingChooserError(matchSet))

            chooserFunction = self.tileSetTemplate.chooserFunctionDict[tileTemplatesNamesWithChoosers.pop()]
            retList = chooserFunction.apply(inputMultisignal)

            #TODO: move this outside of the chooseTileTemplate method to be its own method in ChooserSet
            #  Make sure we're returning tileTemplate objects instead of strings
            def ensureNameIsTileTemplate(tt):
                if isinstance(tt, str):
                    return self.findTileTemplateByName(tt)
                elif tt not in matchSet:
                    raise InvalidChooserTileTemplateError(matchSet, tileTemplate=tt)
                else:
                    return tt

            retList = (ensureNameIsTileTemplate(tt) for tt in retList) #XXX: test changing this to list; i.e., replace parens with brackets

            return retList

    def findTileTemplateByName(self, name):
        for tt in self.tileSet:
            if name == tt.name:
                return tt
        raise InvalidChooserTileTemplateError(self.tileSet, name=name)

    def belongsInSet(self, tileTemplate):
        return self.neighborhoods == tileTemplate.inputNeighborhoods()
    
    def isInSet(self, tileTemplate):
        return (tileTemplate in self.tileSet)

    def addTileTemplate(self, tileTemplate):
        if not self.belongsInSet(tileTemplate):
            raise ValueError('{0} tile template does not belong in chooser set {1}'.format(tileTemplate, self))
        # This will throw an exception if the signal names are not identical
#TODO - make sure not to include auxiliary inputs
        self.addMultisignalValues(tileTemplate)
        self.tileSet.append(tileTemplate)
    
    def addMultisignalValues(self, tileTemplate):
        self.inputMst = self.inputMst.valueUnion(tileTemplate.inputMultisignalType())

    def removeTileTemplate(self, tileTemplate):      
        self.inputMst = None
        self.tileSet.remove(tileTemplate)

        for tt in self.tileSet:
            if self.inputMst is None:
                self.inputMst = tt.inputMultisignalType()
            else:
                self.inputMst.valueUnion(tt.inputMultisignalType())
     
               


class Join:
    # needs direction, in and out tiles/tile templates, multisignal type, neighborhood, strength

#DSD: no strength or direction here anymore because all joins in a neighborhood
# share that, so the neighborhood has that info
#Obj - Tile Template or Port
    def __init__(self, fromObj, toObj, neighborhood, multisignalType):
        self.fromObj = fromObj
        self.toObj = toObj
        self.neighborhood = neighborhood
        self.multisignalType = multisignalType
#MJP: TODO - should this throw an exception if the join is already in these lists?  probably.
        if self not in toObj.inputJoins:
            toObj.inputJoins.append(self)
        if self not in fromObj.outputJoins:
            fromObj.outputJoins.append(self)
            
    def clone(self, tile_templates):
        nameToTT = {}
        for tile in tile_templates:
            nameToTT[tile.name] = tile
            
        newFromObj = nameToTT.get(self.fromObj.name)
        newToObj = nameToTT.get(self.toObj.name)
        newNeighborhood = self.neighborhood.clone()
        newMultisignalType = self.multisignalType.clone()
        newJoin = Join(newFromObj, newToObj, newNeighborhood, newMultisignalType)
        
        return newJoin

class TileSetTemplate(object):
    # needs list of chooser sets, list of joins, and list of neighborhoods, and list of hard-coded tiles
    
    # join, unjoin, rejoin, add/remove chooser, add/remove tile template/tile, createTiles
    
    def __init__(self):
        self.hardcodedTiles = []
        self.neighborhood_list = []
        self.chooserSets = []
#         self.tilesWithoutInputs = []
        self.chooserFunctionDict = {}
        ##onlt tiles and ports and tiletemplates
        self.moduleTiles = []
        self.outputObjectsDict = {}
        self.inputObjectsDict = {}
        self.modulePorts = []
        self.frDict = {}
        self.frLst = []
        self.tileTempToPortDict = {}
        self.tileTempToPortDictReverse = {}
        self.toDict = {}
        
        
    
    def errors(self):
        errors = []
        
#        for tt in self.tileSetTemplates():
#            errors += tt.getStrengthErrors()
#        
#        try:
#            self.createTilesAndBuildErrors()
#        except ErrorListError as errorListError:
#            errors += errorList.errors()
            
        return errors
    
#    def createTilesAndBuildErrors(self):
#        errors = self.errors()
#        if len(errors) > 0:
#            raise errors[0]
#        
#        for chooserSet in self.chooserSets:
#            errors += chooserSet.getMissingChooserErrors()
#            for inputMultisignal in chooserSet.inputMultisignalType():
#                pass
#        # for each chooser set cs
#        #   for each input multisignal ims shared by all tile templates in cs
#        #     call chooser for cs to find list [tt1,tt2,...,ttK] of tile templates to generate a tile from
#        #     for each tile template tt in [tt1,tt2,...,ttK]
#        #       generate tile from tt on input ims
    
    def addTile(self, tile):
        """Add tile to this TileSetTemplate so it will be enumerated with the
        generated tiles and the tiles that were joined to a TileTemplate.
        
        This only needs to be called if the tile is never joined to a 
        TileTemplate, simply as a way to alert the TileSetTemplate of its
        existence."""
        self.hardcodedTiles.append(tile)
    
    def ensureIsTemplate(self, tile):
        """Wrap tile in a TileTemplate if tile is not a TileTemplate already.
        
        This TileTemplate has no transitions or property functions, so it will do
        nothing interesting when TileTemplate.createTilesFromInputMultisignal is
        called, but will create a tile with the same properties as this one."""
        if isinstance(tile, TileTemplate):
            return tile
        else:
            props = dict(tile.__dict__)
            name = props['name']
            del props['name']
            tt = TileTemplate(name, **props)
#TODO - give this a single signal            tt.addAuxiliaryInput()
            return tt

    def setChooser(self, tileTemplate, inputs=(), function=None, expression=None, table=None):
        self.chooserFunctionDict[tileTemplate.name] = ChooserFunction(inputs, function, expression, table)

    def removeChooser(self, tileTemplate):
        if tileTemplate.name in self.chooserFunctionDict:
            del self.chooserFunctionDict[tileTemplate.name]
        else:
            raise NonexistentChooserSetError(tileTemplate)

    def createTiles(self):
        """Return list of all tiles this TileSetTemplate generates.
        
        If unresolved errors exist, the first such error encountered is raised."""
        errors = self.errors()
        if errors:
            raise errors[0]
        tiles = list(self.hardcodedTiles)
        tileTemplatesWithoutInputs = set()
        for chooserSet in self.chooserSets:
            for inputMultisignal in chooserSet.inputMultisignalType():
                tileTemplates = chooserSet.chooseTileTemplates(inputMultisignal)
                for tileTemplate in tileTemplates:
                    tilesFromTileTemplate = tileTemplate.createTilesFromInputMultisignal(inputMultisignal)
                    tiles.extend(tilesFromTileTemplate)
                    if tileTemplate.numInputSides() == 0:
                        tileTemplatesWithoutInputs.add(tileTemplate)
        
        # Handle tiles with no inputs, which are typically Tiles wrapped in TileTemplates        
        emptyMs = Multisignal(())
        
#         for tileTemplateWithoutInput in self.tilesWithoutInputs:
        for tileTemplateWithoutInput in tileTemplatesWithoutInputs:
            tilesFromTileTemplate = tileTemplateWithoutInput.createTilesFromInputMultisignal(emptyMs)
            tiles.extend(tilesFromTileTemplate)

        return [tile for tile in tiles if tile is not None]
    

    def removeJoin(self, strength, direction, fromTileTemplate, toTileTemplate):
        #  Find the join which is to be removed
        joinToRemove = None
        for neighborhood in self.neighborhood_list:
            if neighborhood.strength == strength and neighborhood.direction == direction:
                for j in neighborhood.joins:
                    if j.from_port == fromTileTemplate and j.to_port == toTileTemplate:
                        joinToRemove = j
                        break
            if joinToRemove is not None:
                break
        
        if joinToRemove is not None:
            #  Remove the join from the list of joins associated with the to and from tile templates
            if joinToRemove in joinToRemove.to_port.inputJoins:
                joinToRemove.to_port.inputJoins.remove(joinToRemove)
            if joinToRemove in joinToRemove.from_port.outputJoins:
                joinToRemove.from_port.outputJoins.remove(joinToRemove)
            
            #  Get rid of the neighborhood that this join was in and build a new one(s)
            nbrhdToRemove = joinToRemove.neighborhood
            if nbrhdToRemove in self.neighborhood_list:
                self.neighborhood_list.remove(nbrhdToRemove)

            #  Remove join from the join list, then find new neighborhoods for the other joins
            nbrhdToRemove.joins.remove(joinToRemove)
            for j in nbrhdToRemove.joins:
                newNbrhd = self._getNeighborhoodForJoin(j.neighborhood.strength, j.neighborhood.direction, j.from_port, j.to_port)
                newNbrhd.addJoin(j)

            #  Remove the 'to_port' from its chooser set and then find/create the one it should be in
            for chooserSet in self.chooserSets:
                if chooserSet.isInSet(joinToRemove.to_port):
                    chooserSet.removeTileTemplate(joinToRemove.to_port)
                    if len(chooserSet.tileSet) == 0:
                        self.chooserSets.remove(chooserSet)
                    break

            bInSet = False
            for chooserSet in self.chooserSets:
                if chooserSet.belongsInSet(joinToRemove.to_port):
                    chooserSet.addTileTemplate(joinToRemove.to_port)
                    bInSet = True
                    break
            if not bInSet:
                cs = ChooserSet(self, joinToRemove.to_port)
                self.chooserSets.append(cs)
                
            # In case the tile which was receiving the join no longer has an input, make sure it isn't lost
#             if joinToRemove.to_port.numInputSides() == 0:
#                 self.tilesWithoutInputs.append(joinToRemove.to_port)


    def _getNeighborhoodForJoin(self, strength, direction, fromTileTemplate, toTileTemplate):
        """Find/create neigbhorhood
           Because we could be joining Tiles or TileTemplates, 
             loop over all neighborhoods to look for a fit"""
        inNbrhd = None
        outNbrhd = None
        for nbrhd in self.neighborhood_list:
            if nbrhd.direction == direction:
                for join in nbrhd.joins:
                    if fromTileTemplate == join.fromObj:
                        inNbrhd = nbrhd
                        if strength != nbrhd.strength:
                            raise StrengthError('strengths {0} and {1} do not match'.format(
                                                strength,nbrhd.strength))
                    if toTileTemplate == join.toObj:
                        outNbrhd = nbrhd
                        if strength != nbrhd.strength:
                            raise StrengthError('strengths {0} and {1} do not match'.format(
                                                strength,nbrhd.strength))

        myNbrhd = None
        if (inNbrhd is not None) and (outNbrhd is not None) and (inNbrhd is not outNbrhd):
            # There are two disjoint neighborhoods which need to be combined to
            # form a single neighborhood as long as the multiSignalType names match
            myNbrhd = inNbrhd.combine(outNbrhd)
            self.neighborhood_list.remove(inNbrhd)
            self.neighborhood_list.remove(outNbrhd)
        elif inNbrhd is not None:
            # Either there is only an inNbrhd to join to, or inNbrhd and outNbrhd
            # are the same.  Either way, enter inNbrhd as long as the multiSignalType names match            
            myNbrhd = inNbrhd
        elif outNbrhd is not None:
            # There is only an outNbrhd, so enter it as long as the multiSignalType names match
            myNbrhd = outNbrhd
        else:
            # There is no applicable, existing neighborhood, so create a new one
            myNbrhd = Neighborhood(strength, direction)
            self.neighborhood_list.append(myNbrhd)

        return myNbrhd
        
    #TODO: make a better error to show that an object has not been added to a module
    def join(self, strength, direction, fromTileTemplate, toTileTemplate, 
             multisignalType=None, **kwargs):
        # combine multisignalType with signals specified in kwargs
        if multisignalType is None:
            multisignalType = MultisignalType(**kwargs)
        else:
            multisignalType = copy.copy(multisignalType)
            multisignalType.addSignalTypes(**kwargs)
            
        from_is_port = fromTileTemplate is Port
        to_is_port = toTileTemplate is Port
            
        #TODO: check to ensure signal names in multisignalType do not occur in 
        # from_port or to_port already in a different direction
        fromTileTemplateName = fromTileTemplate.name
       
            
        # wrap Tile in TileTemplate if necessary
        if not from_is_port:
            fromTileTemplate = self.ensureIsTemplate(fromTileTemplate)
        if not to_is_port:
            toTileTemplate = self.ensureIsTemplate(toTileTemplate)
        
        #check to ensure signal names in multisignalType do not occur in 
        # from_port or to_port already in a different direction
        if fromTileTemplateName not in self.frLst:
            self.frLst.append(fromTileTemplateName)
            msDict = {multisignalType : direction}
            self.frDict[fromTileTemplateName] = msDict
        else:
            multiSigDict = self.frDict.get(fromTileTemplateName)
            
            if multisignalType in multiSigDict:
                oldDirec = multiSigDict.get(multisignalType)
                if(oldDirec != direction):
                    raise DuplicateOutputSignalValues(multisignalType, oldDirec, direction,fromTileTemplateName)
                    
            else:
                multiSigDict[multisignalType] = direction
        
       
    
        
        
        #TODO: check if either TileTemplate is new; if so, ensure name not already in use
        
        # Make sure there isn't already a join in this direction between these two tiles
        for neighborhood in self.neighborhood_list:
            for join in neighborhood.joins:
                if (join.neighborhood.direction == direction and 
                    join.fromObj == fromTileTemplate and 
                    join.toObj == toTileTemplate):
                    raise ValueError('{0} and {1} are already joined in direction {2}'.format(
                        fromTileTemplate.name,toTileTemplate.name,direction))

        # Ensure direction of join doesn't conflict with fromTileType's current status as input of output
        if direction in fromTileTemplate.inputDirMultisignalTypeDict().keys():
            raise InputOutputSideConflictError(fromTileTemplate, direction)
        # Ensure direction of join doesn't conflict with toTileType's current status as input or output
        if oppositeDirection(direction) in toTileTemplate.outputDirMultisignalTypeDict().keys():
            raise InputOutputSideConflictError(toTileTemplate, direction)

        #  Find/create the neighborhood for this join
        myNbrhd = self._getNeighborhoodForJoin(strength, direction, fromTileTemplate, toTileTemplate)

        newJoin = Join(fromTileTemplate, toTileTemplate, myNbrhd, multisignalType)
        myNbrhd.addJoin(newJoin)

        toTileTemplates = set([join.toObj for join in myNbrhd.joins])
        for toTileTemplate in toTileTemplates:
            bInSet = False
            for chooserSet in self.chooserSets:
                if chooserSet.belongsInSet(toTileTemplate):
                    if not chooserSet.isInSet(toTileTemplate):
                        chooserSet.addTileTemplate(toTileTemplate)
                    else:
                        chooserSet.addMultisignalValues(toTileTemplate)
                    bInSet = True
                    break
            if not bInSet:
                cs = ChooserSet(self, toTileTemplate)
                self.chooserSets.append(cs)

            for chooserSet in self.chooserSets[:]:
                if chooserSet.isInSet(toTileTemplate):
                    if not chooserSet.belongsInSet(toTileTemplate):
                        chooserSet.removeTileTemplate(toTileTemplate)
                        if len(chooserSet.tileSet) == 0:
                            self.chooserSets.remove(chooserSet)

#         # In case the tile which is outputting to the join doesn't have an input, make sure it isn't lost
#         if from_port.numInputSides() == 0:
#             if from_port not in self.tilesWithoutInputs:
#                 self.tilesWithoutInputs.append(from_port)
#         
#         # If to_port was in the list of tile templates without inputs, remove it
#         if to_port in self.tilesWithoutInputs:
#             self.tilesWithoutInputs.remove(to_port)
        
        return newJoin
    #eventually this function should be integrated within another function, but for the time being simply focusin on functionality
    ##Do with input as well if this is correct
    ##implement it into join
    def ensurePortToTileOutputSide(self):
        graph = self.outputObjectsDict
        tile_template_unvisited_set = set(self.moduleTiles)
        for tile in tile_template_unvisited_set:
            if tile not in graph:
                graph[tile] = []
        port_unvisited_set = set(self.modulePorts)
        for port in port_unvisited_set:
            if port not in graph:
                graph[port] = []
        ##add check to ensure that tile temp univsited isnt size zero as well as unit test for this func 
        root = next(iter(tile_template_unvisited_set))
        visitedSet = set()
        
        while root:
            #portsSet = set()
            queue = collections.deque([root])
            while queue:
                objt = queue.popleft()
                if objt not in visitedSet:
                    visitedSet.add(objt)
                    if type(objt) is TileTemplate:
                        tile_template_unvisited_set.remove(objt)
                    else:
                        port_unvisited_set.remove(objt)
                    for neighbor in graph[objt]: 
                        if neighbor not in visitedSet: 
                            queue.append(neighbor)
            if tile_template_unvisited_set:
                root = next(iter(tile_template_unvisited_set))
            else:
                root = None
#             for obj in visitedSet:
#                 if type(obj) is Port:
#                     portsSet.add(obj)
        if port_unvisited_set:
            raise portsNotConnectedtoTileTemplatesOutput(list(port_unvisited_set))
        
        '''portsList = list(portsSet)
        if portsList == self.modulePorts:
            pass
        else:
            #make an error class for this
            raise ValueError'''
    def ensurePortToTileInputSide(self):
        graph = self.inputObjectsDict
        tile_template_unvisited_set = set(self.moduleTiles)
        for tile in tile_template_unvisited_set:
            if tile not in graph:
                graph[tile] = []
        port_unvisited_set = set(self.modulePorts)
        for port in port_unvisited_set:
            if port not in graph:
                graph[port] = []
        ##add check to ensure that tile temp univsited isnt size zero as well as unit test for this func 
        root = next(iter(tile_template_unvisited_set))
        visitedSet = set()
        
        while root:
            #portsSet = set()
            queue = collections.deque([root])
            while queue:
                objt = queue.popleft()
                if objt not in visitedSet:
                    visitedSet.add(objt)
                    if type(objt) is TileTemplate:
                        tile_template_unvisited_set.remove(objt)
                    else:
                        port_unvisited_set.remove(objt)
                    for neighbor in graph[objt]: 
                        if neighbor not in visitedSet: 
                            queue.append(neighbor)
            if tile_template_unvisited_set:
                root = next(iter(tile_template_unvisited_set))
            else:
                root = None
#             for obj in visitedSet:
#                 if type(obj) is Port:
#                     portsSet.add(obj)
        if port_unvisited_set:
            raise portsNotConnectedToTileTemplatesInput(list(port_unvisited_set))
        '''portsList = list(portsSet)
        if portsList == self.modulePorts:
            pass
        else:
            #make an error class for this
            raise ValueError'''
#there must always be a root module created whose name is root module  
#try to implement tiles within Modules at one point in time?    
#feature to implement: create function that copies module into a new one and can rotate it, one that can flip it, and one that can copy it 
class Module(object):
    def __init__(self, name):
        self.tile_templates = []
        self.submodules = []
        self.parent = None
        self.ports = []
        self.name = name
        self.hardcodedTiles = []
        self.neighborhood_list = []
        self.chooserSets = []
        self.chooserFunctionDict = {}
        self.frDict = {}
        self.frLst = []
        self.total_strength_initiator_ports = 0
        self.tiles = []
        self.joins = []
        self.tileTempDictForCopy = {}
        self.tileTempDictReverseForCopy = {}

    def add(self, child):
        if type(child) not in [TileTemplate, Module, Tile]:
            raise ValueError("child must be TileTemplate or Module but is {}".format(type(child)))
        if child.parent:
            raise ExisitngParrentError(self,child,type(child),self.name, child.parent)
        if type(child) == TileTemplate:
            self.tile_templates.append(child)
        elif type(child) == Module:
            self.submodules.append(child)
        elif type(child) == Tile:
            self.tiles.append(child)
        else:
            assert False
        child.parent = self
        
    def errors(self):
        errors = []
            
        return errors
        
    def remove(self,child):
        if child not in self.tile_templates or self.submodules:
            raise ValueError("child: {} must have been added to the module in order to be removed  ".format(self.child))
        if child in self.tile_templates:
            self.tile_templates.remove(child)
        elif child in self.submodules:
            self.submodules.remove(child)
    def add_port(self, port, direction):
        if type(port) not in [Port, initiatorPort]:
            raise ValueError("added object must be a port but is {}".format(type(port)))
        self.ports.append(port)
        port.outputDirection = direction
        
        if type(port) is initiatorPort:
            if port.toModule == True:
                    
                self.total_strength_initiator_ports = self.total_strength_initiator_ports + port.strength
                if self.total_strength_initiator_ports > 2:
                    raise tooManyInitatiorPortsError(self.name)
        
        port.inputDirection = oppositeDirection(direction)
        port.parent = self

    def remove_port(self,port):
        if port not in self.ports:
            raise ValueError("port: {} must have been added to the module in order to be removed".format(self.port))
        self.ports.remove(port)
    def addTile(self,tile):
        self.hardcodedTiles.append(tile)
    def ensureIsTemplate(self, tile):
        """Wrap tile in a TileTemplate if tile is not a TileTemplate already.
        
        This TileTemplate has no transitions or property functions, so it will do
        nothing interesting when TileTemplate.createTilesFromInputMultisignal is
        called, but will create a tile with the same properties as this one."""
        if isinstance(tile, TileTemplate):
            return tile
        else:
            props = dict(tile.__dict__)
            name = props['name']
            del props['name']
            tt = TileTemplate(name, **props)
            return tt

    def removeJoin(self, strength, direction, fromTileTemplate, toTileTemplate):
        #  Find the join which is to be removed
        joinToRemove = None
        for neighborhood in self.neighborhood_list:
            if neighborhood.strength == strength and neighborhood.direction == direction:
                for j in neighborhood.joins:
                    if j.fromObj == fromTileTemplate and j.toObj == toTileTemplate:
                        joinToRemove = j
                        break
            if joinToRemove is not None:
                break
        
        if joinToRemove is not None:
            #  Remove the join from the list of joins associated with the to and from tile templates
            if joinToRemove in joinToRemove.toObj.inputJoins:
                joinToRemove.toObj.inputJoins.remove(joinToRemove)
            if joinToRemove in joinToRemove.fromObj.outputJoins:
                joinToRemove.fromObj.outputJoins.remove(joinToRemove)
            
            #  Get rid of the neighborhood that this join was in and build a new one(s)
            nbrhdToRemove = joinToRemove.neighborhood
            if nbrhdToRemove in self.neighborhood_list:
                self.neighborhood_list.remove(nbrhdToRemove)

            #  Remove join from the join list, then find new neighborhoods for the other joins
            nbrhdToRemove.joins.remove(joinToRemove)
            for j in nbrhdToRemove.joins:
                newNbrhd = self._getNeighborhoodForJoin(j.neighborhood.strength, j.neighborhood.direction, j.fromObj, j.toObj)
                newNbrhd.addJoin(j)

            '''#  Remove the 'to_port' from its chooser set and then find/create the one it should be in
            for chooserSet in self.chooserSets:
                if chooserSet.isInSet(joinToRemove.to_port):
                    chooserSet.removeTileTemplate(joinToRemove.to_port)
                    if len(chooserSet.tileSet) == 0:
                        self.chooserSets.remove(chooserSet)
                    break
            bInSet = False
            for chooserSet in self.chooserSets:
                if chooserSet.belongsInSet(joinToRemove.to_port):
                    chooserSet.addTileTemplate(joinToRemove.to_port)
                    bInSet = True
                    break
            if not bInSet:
                cs = ChooserSet(self, joinToRemove.to_port)
                self.chooserSets.append(cs)
                '''
            # In case the tile which was receiving the join no longer has an input, make sure it isn't lost
#             if joinToRemove.to_port.numInputSides() == 0:
#                 self.tilesWithoutInputs.append(joinToRemove.to_port)

    #fix for both ports and joins
    def _getNeighborhoodForJoin(self, strength, direction, fromObj, toObj):
        """Find/create neigbhorhood
           Because we could be joining Tiles or TileTemplates, 
             loop over all neighborhoods to look for a fit"""
        inNbrhd = None
        outNbrhd = None
        for nbrhd in self.neighborhood_list:
            if nbrhd.direction == direction:
                for join in nbrhd.joins:
                    if fromObj == join.fromObj:
                        inNbrhd = nbrhd
                        if strength != nbrhd.strength:
                            raise StrengthError('strengths {0} and {1} do not match'.format(
                                                strength,nbrhd.strength))
                    if toObj == join.toObj:
                        outNbrhd = nbrhd
                        if strength != nbrhd.strength:
                            raise StrengthError('strengths {0} and {1} do not match'.format(
                                                strength,nbrhd.strength))

        myNbrhd = None
        if (inNbrhd is not None) and (outNbrhd is not None) and (inNbrhd is not outNbrhd):
            # There are two disjoint neighborhoods which need to be combined to
            # form a single neighborhood as long as the multiSignalType names match
            myNbrhd = inNbrhd.combine(outNbrhd)
            self.neighborhood_list.remove(inNbrhd)
            self.neighborhood_list.remove(outNbrhd)
        elif inNbrhd is not None:
            # Either there is only an inNbrhd to join to, or inNbrhd and outNbrhd
            # are the same.  Either way, enter inNbrhd as long as the multiSignalType names match            
            myNbrhd = inNbrhd
        elif outNbrhd is not None:
            # There is only an outNbrhd, so enter it as long as the multiSignalType names match
            myNbrhd = outNbrhd
        else:
            # There is no applicable, existing neighborhood, so create a new one
            myNbrhd = Neighborhood(strength, direction)
            self.neighborhood_list.append(myNbrhd)

        return myNbrhd
   

    # generate neighborhod then go through the joins of that neighborhodd and create an input object to output object set then see for any set that has size greater than one that it does not contain ports
    def join(self, strength, direction, fromObj, toObj, tileSetTemplate,
             multisignalType=None, **kwargs):
        if not type(fromObj) in [ initiatorPort, Port,Tile,TileTemplate]:
            raise ValueError("fromObj must either be a Tile, Port, or TileTemplate but is {}".format(type(fromObj)))
        if not type(toObj) in [ initiatorPort, Port, Tile,TileTemplate]:
            raise ValueError("toObj must either be a Tile, Port, or TileTemplate but is {}".format(type(toObj)))
        if type(fromObj) is TileTemplate:
            if fromObj.parent.name == toObj.parent.name or fromObj.parent.name == (toObj.parent).parent.name:
                pass
            else:
                raise TileTemplateFromObjNotConfomingtoModuleConfigurationError(fromObj,toObj)
        if type(fromObj) is Port and type(toObj) is TileTemplate:
            if fromObj.parent.name == toObj.parent.name or fromObj.parent.name == (toObj.parent).parent.name:
                pass
            else:
                raise PortFromObjNotConformingtoModuleConfigurationError(fromObj,toObj)
        if type(fromObj) is Port and type(toObj) is Port:
            
            if (fromObj.parent).parent.name == (toObj.parent).parent.name or fromObj.parent.name == (toObj.parent).parent.name or (fromObj.parent).parent.name == toObj.parent.name:
                pass
            else:
                raise PortFromObjNotConformingtoModuleConfigurationError(fromObj,toObj)
        
        if direction in fromObj.outputObjectDict:
             fromObj.outputObjectDict[direction].append(toObj)
        else:
             fromObj.outputObjectDict[direction] = [toObj]
        if oppositeDirection(direction) in toObj.inputObjectDict:
             toObj.inputObjectDict[oppositeDirection(direction)].append(fromObj)
        else:
             toObj.inputObjectDict[oppositeDirection(direction)] = [fromObj]
        if type(tileSetTemplate) not in [TileSetTemplate]:
            raise ValueError("tileSetTemplate must be a TileSetTemplate but is {}".format(type(tileSetTemplate)))
        
        if type(fromObj) in [TileTemplate,Tile]:
            if fromObj not in tileSetTemplate.moduleTiles:
                (tileSetTemplate.moduleTiles).append(fromObj)
        if type(toObj) in [TileTemplate,Tile]:
            if toObj not in tileSetTemplate.moduleTiles:
                (tileSetTemplate.moduleTiles).append(toObj)
        if type(fromObj) in [Port, initiatorPort]:
            if fromObj not in tileSetTemplate.modulePorts:
                (tileSetTemplate.modulePorts).append(fromObj)
        if type(toObj) in [Port, initiatorPort]:
            if toObj not in tileSetTemplate.modulePorts:
                (tileSetTemplate.modulePorts).append(toObj)
        if tileSetTemplate.outputObjectsDict.get(fromObj) == None:
            tileSetTemplate.outputObjectsDict[fromObj] = [toObj]
        else:
            tileSetTemplate.outputObjectsDict[fromObj].append(toObj)
        if tileSetTemplate.inputObjectsDict.get(toObj) == None:
            tileSetTemplate.inputObjectsDict[toObj] = [fromObj]
        else:
            tileSetTemplate.inputObjectsDict[toObj].append(fromObj)
        
        '''if fromObj not in tileSetTemplate.hardcodedTiles:
            tileSetTemplate.hardcodedTiles.append(fromObj)
        if toObj not in tileSetTemplate.hardcodedTiles:
            tileSetTemplate.hardcodedTiles.append(toObj)'''
            
        ##populate a dict to see how from objects go to toObjects
        
        fromObjTup = (fromObj, direction, strength)
        toObjTup = (toObj, direction, strength)

        if tileSetTemplate.tileTempToPortDict.get(fromObjTup) == None:
            tileSetTemplate.tileTempToPortDict[fromObjTup] = [toObjTup]
        else:
            tileSetTemplate.tileTempToPortDict[fromObjTup].append(toObjTup)
        
        #initializing variables needed to transfer data in this dict to the copy module    
        fromObjNameForCopyDict = fromObj.name
        objDictForCopy = {}
        fromTupForCopy = (direction, strength)
        toTupForCopy = (toObj.name, direction, strength)
        objDictForCopy[fromTupForCopy] = toTupForCopy
        
        
        if self.tileTempDictForCopy.get(fromObjNameForCopyDict) == None:
            self.tileTempDictForCopy[fromObjNameForCopyDict] = [objDictForCopy]
        else:
            self.tileTempDictForCopy[fromObjNameForCopyDict].append(objDictForCopy)
             
             
        #fromObjTupRev = (fromObj, oppositeDirection(direction), strength)
        #toObjTupRev = (toObj, oppositeDirection(direction), strength) should work with regular direction if it doesnt use this
        fromObjTupRev = (fromObj, direction, strength)
        toObjTupRev = (toObj, direction, strength)
         
        
        if tileSetTemplate.tileTempToPortDictReverse.get(toObjTupRev) == None:
            tileSetTemplate.tileTempToPortDictReverse[toObjTupRev] = [fromObjTupRev]
        else:
            tileSetTemplate.tileTempToPortDictReverse[toObjTupRev].append(fromObjTupRev)
            #or (tileSetTemplate.tileTempToPortDictReverse.get(toObjTupRev)).append(fromObjTupRev)
        
        toObjNameForCopyRevDict = toObj.name
        objDictRevForCopy = {}
        toTupRevForCopy = (direction, strength)
        fromTupRevForCopy = (fromObj.name, direction, strength)
        objDictRevForCopy[toTupRevForCopy] = fromTupRevForCopy
        
        
        if self.tileTempDictReverseForCopy.get(toObjNameForCopyRevDict) == None:
            self.tileTempDictReverseForCopy[toObjNameForCopyRevDict] = [objDictRevForCopy]
        else:
            self.tileTempDictReverseForCopy[toObjNameForCopyRevDict].append(objDictRevForCopy)
                
                
            
        # combine multisignalType with signals specified in kwargs
        if multisignalType is None:
            multisignalType = MultisignalType(**kwargs)
        else:
            multisignalType = copy.copy(multisignalType)
            multisignalType.addSignalTypes(**kwargs)
            
        from_is_port = fromObj in [Port,initiatorPort]
        to_is_port = toObj in [Port,initiatorPort]
            
        #TODO: check to ensure signal names in multisignalType do not occur in 
        # from_port or to_port already in a different direction
        fromObjName = fromObj.name
       
            
        # wrap Tile in TileTemplate if necessary
        if not from_is_port:
            fromTileTemplate = self.ensureIsTemplate(fromObj)
        if not to_is_port:
            toTileTemplate = self.ensureIsTemplate(toObj)
        
        #check to ensure signal names in multisignalType do not occur in 
        # from_port or to_port already in a different direction
        if fromObjName not in self.frLst:
            self.frLst.append(fromObjName)
            msDict = {multisignalType : direction}
            self.frDict[fromObjName] = msDict
        else:
            multiSigDict = self.frDict.get(fromObjName)
            
            if multisignalType in multiSigDict:
                oldDirec = multiSigDict.get(multisignalType)
                if(oldDirec != direction):
                    raise DuplicateOutputSignalValues(multisignalType, oldDirec, direction,fromObjName)
                    
            else:
                multiSigDict[multisignalType] = direction
                
        
        if tileSetTemplate.toDict.get(fromObj) == None:
            tileSetTemplate.toDict[fromObj] = [toObj]
        else:
            tileSetTemplate.toDict[fromObj].append(toObj)
       
    
        
        
        #TODO: check if either TileTemplate is new; if so, ensure name not already in use
        
        # Make sure there isn't already a join in this direction between these two tiles
        for neighborhood in self.neighborhood_list:
            for join in neighborhood.joins:
                if (join.neighborhood.direction == direction and 
                    join.fromObj == fromObj and 
                    join.toObj == toObj):
                    raise ValueError('{0} and {1} are already joined in direction {2}'.format(
                        fromTileTemplate.name,toTileTemplate.name,direction))

        # Ensure direction of join doesn't conflict with fromTileType's current status as input of output
        if fromObj in [Port,initiatorPort]:
            if direction in fromObj.inputDirMultisignalTypeDict().keys():
                raise InputOutputSideConflictError(fromObj, direction)
        # Ensure direction of join doesn't conflict with toTileType's current status as input or output
        if toObj in [Port, initiatorPort]:
            if oppositeDirection(direction) in toObj.outputDirMultisignalTypeDict().keys():
                raise InputOutputSideConflictError(toObj, direction)

        #  Find/create the neighborhood for this join
        myNbrhd = self._getNeighborhoodForJoin(strength, direction, fromObj, toObj)

        newJoin = Join(fromObj, toObj, myNbrhd, multisignalType)
        myNbrhd.addJoin(newJoin)
        
        #ensures ports follow many to single rule

        
        fromObjJoinSet = { join.fromObj for join in myNbrhd.joins }
        toObjJoinSet = { join.toObj for join in myNbrhd.joins }
        
        if len(fromObjJoinSet) > 1:
            if any(type(obj) == Port for obj in fromObjJoinSet):
                raise fromObjectsPortError(myNbrhd)
        
        if len(toObjJoinSet) > 1:
            if any(type(obj) == Port for obj in toObjJoinSet):
                raise toObjectsPortError(myNbrhd)
        
         
         
        #creates a chooser set
        '''if type(toObj) in [initiatorPort, Port]:
            if type(fromObj) is TileTemplate:
                cs = ChooserSet(self, fromObj)
                self.chooserSets.append(cs)'''
                      
        toTileTemplates = {join.toObj for join in myNbrhd.joins if type(join.toObj) is TileTemplate}
        for toTileTemplate in toTileTemplates:
            bInSet = False
            for chooserSet in self.chooserSets:
                if chooserSet.belongsInSet(toTileTemplate):
                    if not chooserSet.isInSet(toTileTemplate):
                        chooserSet.addTileTemplate(toTileTemplate)
                    else:
                        chooserSet.addMultisignalValues(toTileTemplate)
                    bInSet = True
                            
                    break
            if not bInSet:
                cs = ChooserSet(self, toTileTemplate)
                self.chooserSets.append(cs)

            for chooserSet in self.chooserSets[:]:
                if chooserSet.isInSet(toTileTemplate):
                    if not chooserSet.belongsInSet(toTileTemplate):
                        chooserSet.removeTileTemplate(toTileTemplate)
                        if len(chooserSet.tileSet) == 0:
                            self.chooserSets.remove(chooserSet)
            
            
        

        self.joins.append(newJoin)
      
     
        return newJoin
         
    def copyModule(self,tileSetTemplate):
        
        #cloning tile templates 
        newTTList = list(self.tile_templates)
        newTileTemplates = []
        for tile in newTTList:
            newTile = tile.clone()
            newTileTemplates.append(newTile)
    
            
        #recursively copy modules contained wihtin 
        newSubMods = list(self.submodules)
        newSubmodules = []
        for module in newSubMods:
            newModules = module.copyModule(tileSetTemplate)
            newSubmodules.append(newModules)
        
        #set parent to none, decided at user descrision
        newParent = None #can be added to any module and that module will become its parent
        
        #cloning ports
        newPortList = list(self.ports)
        newPorts = []
        for port in newPortList:
            newPort = port.clone()
            newPorts.append(newPort)
            
        #name blank, can be renamed afterwards    
        newName = None #option to rename 
        
        
        #tiles cloned
        newHardcodedTiles = []
        for tile in self.hardcodedTiles:
            newTile = tile.clone()
            newHardcodedTiles.append(newTile)
            
        #clone chooser sets 
        newChooserSets = []
        for chooserSet in self.chooserSets:
            newChooserSetCp = chooserSet.clone(newTileTemplates)
            newChooserSets.append(newChooserSetCp)
        
        
        newTileTempDictForCopy = dict(self.tileTempDictForCopy)
        newTileTempDictReverseForCopy = dict(self.tileTempDictReverseForCopy)

        newNeighborhoods = list(self.neighborhood_list)
        newNeighborhoodList = []
        for neighborhood in newNeighborhoods:
            newNbrhd = neighborhood.clone()
            newNeighborhoodList.append(newNbrhd)
        newTList = list(self.tiles)
        newTiles = []
        for tile in newTList:
            newTile = tile.clone()
            newTiles.append(newTile)
        newChooserFunctionDict = dict(self.chooserFunctionDict)
        newTotalStrengthInitiatorPorts = self.total_strength_initiator_ports
        newFrLst = list(self.frLst)
        newFrDict = dict(self.frDict)
        newJoins = []
        for join in self.joins:  
            newJoin = join.clone(newTileTemplates)
            newJoins.append(newJoin)
        #cant do it explicitly with the objects bc obj are diff since one contains joins one doesnst, first put names of the tile templates and ports into a list
        tileTempNames = []
        tileTempNameDict = {}
        for tile in newTileTemplates:
            name = tile.name
            tileTempNames.append(name)
            tileTempNameDict[name] = tile
        portNames = []
        portNameDict = {}
        for port in newPorts:
            name = port.name
            portNames.append(name)
            portNameDict[name] = port
        nbrhdGlueAnnotations = []
        glueAnnotationToNbrhdDict = {}
        for nbrhd in newNeighborhoodList:
            glueAnot = nbrhd.glueAnnotation
            nbrhdGlueAnnotations.append(glueAnot)
            glueAnnotationToNbrhdDict[glueAnot] = nbrhd
        for join in newJoins:
            if join.fromObj.name in tileTempNames:
                tile = tileTempNameDict.get(join.fromObj.name)
                tile.outputJoins.append(join)
                #tile.parent = self
            if join.toObj.name in tileTempNames:
                tile = tileTempNameDict.get(join.toObj.name)
                tile.inputJoins.append(join)
                #tile.parent = self
            if join.fromObj.name in portNames:
                port = portNameDict.get(join.fromObj.name)
                port.outputJoins.append(join)
                #port.parent = self
            if join.toObj.name in portNames:
                port = portNameDict.get(join.toObj.name)
                port.inputJoins.append(join)
                #port.parent = self
            if join.neighborhood.glueAnnotation in nbrhdGlueAnnotations:
                nbrhd = glueAnnotationToNbrhdDict.get(join.neighborhood.glueAnnotation)
                nbrhd.joins.append(join)
            
        newModule = Module(newName)
        newModule.tile_templates = newTileTemplates
        newModule.submodules = newSubmodules
        newModule.parent = None
        newModule.ports = newPorts
        newModule.hardcodedTiles = newHardcodedTiles
        newModule.neighborhood_list = newNeighborhoodList
        newModule.chooserSets = newChooserSets
        newModule.chooserFunctionDict = newChooserFunctionDict
        newModule.frDict = newFrDict
        newModule.frLst = newFrLst
        newModule.total_strength_initiator_ports = newTotalStrengthInitiatorPorts
        newModule.tiles = newTiles
        newModule.joins = newJoins
        newModule.tileTempDictForCopy = newTileTempDictForCopy
        newModule.tileTempDictReverseForCopy = newTileTempDictReverseForCopy
        #for chooserSet in newModule.chooserSets:
            #for tile in chooserSet.tileSet:
                #tile.parent = newModule
                
        nameToTTDict = {}
        for tileTemp in newModule.tile_templates:
            nameToTTDict[tileTemp.name] = tileTemp
            
        for tileTemp in newModule.tile_templates:
            tileTemp.parent = newModule
        for port in newModule.ports:
            port.parent = newModule
        for join in newModule.joins:
            join.fromObj.parent = newModule
            join.toObj.parent = newModule
        
      
        #populate joins list in neighborhood - may have already done it, check
        #for chooserSet in newModule.chooserSets:
            #chooserSet.tileTemplate.parent = newModule
            #for tile in chooserSet.tileSet: 
                #tile.parent = newModule
            #if chooserSet.tileTemplate.name in nameToTTDict.keys():
                #chooserSet.tileTemplate = nameToTTDict.get(chooserSet.tileTemplate.name)
            #fix this to recognize these tiles as same in tile_templates, once done everyhting should be good to go
            #for tile in chooserSet.tileSet: 
                #if tile.name in nameToTTDict.keys():
                    #tile = nameToTTDict.get(tile.name)
                    
        
        #add all tile template to the tiletemptoportdict and tiletemptoportdictreverse dictionaries
       
            
       
        for tileTemp in newModule.tile_templates:
            ttName = tileTemp.name
            if ttName in newModule.tileTempDictForCopy.keys():
                tileTempDictList = newModule.tileTempDictForCopy.get(ttName)
                for ttDict in tileTempDictList:
                    for key in ttDict.keys():
                        newFromTupDirection = key[0]
                        newFromTupStrength = key[1]
                        ttFromTup = tileTemp
                        toTup = ttDict.get(key)
                        toTTName = toTup[0]
                        if toTTName in nameToTTDict: 
                            toTT = nameToTTDict.get(toTTName)
                            toTTDirection = toTup[1]
                            toTTStrength = toTup[2]
                            fromObjTup = (ttFromTup, newFromTupDirection, newFromTupStrength)
                            toObjTup = (toTT,toTTDirection,toTTStrength)
                        
                            if tileSetTemplate.tileTempToPortDict.get(fromObjTup) == None:
                                tileSetTemplate.tileTempToPortDict[fromObjTup] = [toObjTup]
                                
                            else:
                                tileSetTemplate.tileTempToPortDict[fromObjTup].append(toObjTup)
                            
        
        for tileTemp in newModule.tile_templates:
            ttName = tileTemp.name
            if ttName in newModule.tileTempDictReverseForCopy.keys():
                tileTempDictList = newModule.tileTempDictReverseForCopy.get(ttName)
                
                for ttDict in tileTempDictList:
                    for key in ttDict.keys():
                        newToTupDirection = key[0]
                        newToTupStrength = key[1]
                        ttToTup = tileTemp
                        fromTup = ttDict.get(key)
                        
                        fromTTName = fromTup[0]
                       
                        if fromTTName in nameToTTDict: 
                            fromTT = nameToTTDict.get(fromTTName)
                            
                            fromTTDirection = fromTup[1]
                            fromTTStrength = fromTup[2]
                            toObjTupRev = (ttToTup, newToTupDirection, newToTupStrength)
                            fromObjTupRev = (fromTT,fromTTDirection,fromTTStrength)
                        
                            if tileSetTemplate.tileTempToPortDictReverse.get(toObjTupRev) == None:
                                tileSetTemplate.tileTempToPortDictReverse[toObjTupRev] = [fromObjTupRev]
                                
                            else:
                                tileSetTemplate.tileTempToPortDictReverse[toObjTupRev].append(fromObjTupRev)
                        
                
            
            
            
        #do the same for ports eventually 
        return newModule 
       
    def renameModule(self, newName):
        self.name = newName
            
    #takes an existing module and rotates it, so must copy first then rotate
    #should just rotate the join's direction to the right
    #make a rotate direction function so no manual chekcs
    #roatedirectionclockwise90
    def rotateClockwise90(self, tileSetTemplate):
        for nbrhd in self.neighborhood_list:
            newDirection = rotateDirectionClockwise90(nbrhd.direction)
            nbrhd.direction = newDirection
            
        
        for join in self.joins:
            newDirection = rotateDirectionClockwise90(join.neighborhood.direction)
            join.neighborhood.direction = newDirection
        
        
            
        nameToTTDict = {}
        for tileTemp in self.tile_templates:
            nameToTTDict[tileTemp.name] = tileTemp
            
        for tileTemp in self.tile_templates:
            ttName = tileTemp.name
            if ttName in self.tileTempDictForCopy.keys():
                tileTempDictList = self.tileTempDictForCopy.get(ttName)
                for ttDict in tileTempDictList:
                    for key in ttDict.keys():
                        newFromTupDirection = key[0]
                        newFromTupStrength = key[1]
                        ttFromTup = tileTemp
                        fromObjTup = (ttFromTup, newFromTupDirection, newFromTupStrength) 
                        tileSetTemplate.tileTempToPortDict.pop(fromObjTup, None)
                       
        
        for tileTemp in self.tile_templates:
            ttName = tileTemp.name
            if ttName in self.tileTempDictForCopy.keys():
                tileTempDictList = self.tileTempDictForCopy.get(ttName)
                for ttDict in tileTempDictList:
                    for key in ttDict.keys():
                        newFromTupDirection = key[0]
                        newFromTupStrength = key[1]
                        ttFromTup = tileTemp
                        toTup = ttDict.get(key)
                        toTTName = toTup[0]
                        if toTTName in nameToTTDict: 
                            toTT = nameToTTDict.get(toTTName)
                            toTTDirection = toTup[1]
                            toTTStrength = toTup[2]
                            rotatedFromDirection = rotateDirectionClockwise90(newFromTupDirection)
                            rotatedToDirection = rotateDirectionClockwise90(toTTDirection)
                            fromObjTup = (ttFromTup, rotatedFromDirection, newFromTupStrength)
                            toObjTup = (toTT,rotatedToDirection,toTTStrength)
                        
                            if tileSetTemplate.tileTempToPortDict.get(fromObjTup) == None:
                                tileSetTemplate.tileTempToPortDict[fromObjTup] = [toObjTup]
                                
                            else:
                                tileSetTemplate.tileTempToPortDict[fromObjTup].append(toObjTup)
        
        for tileTemp in self.tile_templates:
            ttName = tileTemp.name
            if ttName in self.tileTempDictReverseForCopy.keys():
                tileTempDictList = self.tileTempDictReverseForCopy.get(ttName)
                
                for ttDict in tileTempDictList:
                    for key in ttDict.keys():
                        newToTupDirection = key[0]
                        newToTupStrength = key[1]
                        ttToTup = tileTemp
                        toObjTupRev = (ttToTup, newToTupDirection, newToTupStrength)
                        tileSetTemplate.tileTempToPortDictReverse.pop(toObjTupRev, None)
        
        for tileTemp in self.tile_templates:
            ttName = tileTemp.name
            if ttName in self.tileTempDictReverseForCopy.keys():
                tileTempDictList = self.tileTempDictReverseForCopy.get(ttName)
                
                for ttDict in tileTempDictList:
                    for key in ttDict.keys():
                        newToTupDirection = key[0]
                        newToTupStrength = key[1]
                        ttToTup = tileTemp
                        fromTup = ttDict.get(key)
                        
                        fromTTName = fromTup[0]
                       
                        if fromTTName in nameToTTDict: 
                            fromTT = nameToTTDict.get(fromTTName)
                            
                            fromTTDirection = fromTup[1]
                            fromTTStrength = fromTup[2]
                            newToTupDirectionRotated = rotateDirectionClockwise90(newToTupDirection)
                            fromTTDirectionRotated = rotateDirectionClockwise90(fromTTDirection)
                            toObjTupRev = (ttToTup, newToTupDirectionRotated, newToTupStrength)
                            fromObjTupRev = (fromTT,fromTTDirectionRotated,fromTTStrength)
                        
                            if tileSetTemplate.tileTempToPortDictReverse.get(toObjTupRev) == None:
                                tileSetTemplate.tileTempToPortDictReverse[toObjTupRev] = [fromObjTupRev]
                                
                            else:
                                tileSetTemplate.tileTempToPortDictReverse[toObjTupRev].append(fromObjTupRev)
                        
             
        #neighborhood list and joins and tile template joins
    #should just rotate the join's direction to the left
    def rotateCounterclockwise90(self):
        pass
    
    #horizontal and vertical functions
    #how would this occur in reference to joins - i.e : W -> E basically?
    #use oppositedirectionfunctions so switch W,E
    def reflectModuleHorizontal(self):
        pass
    #use oppositedirectionfunctions so switch W,E
    def reflectModuleVertical(self):
        pass
    
    
    
    def mirrorCopy(self):
        pass
    


    #ask about how this works/ adapt modules to be similar to tst
    #way to do this without using chooser sets? could we use something else in the join instead - just create a dictionary in the join function that stores all of this information?
    def createTiles(self, tileSetTemplate):
        
        
        errors = self.errors()
        if errors:
            raise errors[0]
        tiles = list(self.hardcodedTiles)
        tileTemplatesWithoutInputs = set()
        for chooserSet in self.chooserSets:
         
            
            chooserSetNbhds = chooserSet.neighborhoods
            
            wNbhd = chooserSetNbhds.get(E)
            if wNbhd is not None:
                wNbhdStrength = wNbhd.strength
            else:
                wNbhdStrength = None
            eNbhd = chooserSetNbhds.get(W)
            if eNbhd is not None:
                eNbhdStrength = eNbhd.strength
            else:
                eNbhdStrength = None
            nNbhd = chooserSetNbhds.get(S)
            if nNbhd is not None:
                nNbhdStrength = nNbhd.strength
            else:
                nNbhdStrength = None
            sNbhd = chooserSetNbhds.get(N)
            if sNbhd is not None:
                sNbhdStrength = sNbhd.strength
            else:
                sNbhdStrength = None
                
            
            for tileTemplate in chooserSet.tileSet:
                
                toTileTemplateCs = tileTemplate
                tupW = (toTileTemplateCs, Direction.West, wNbhdStrength)
                tupE = (toTileTemplateCs, Direction.East, eNbhdStrength)
                tupN = (toTileTemplateCs, Direction.North, nNbhdStrength)
                tupS = (toTileTemplateCs, Direction.South, sNbhdStrength)
            
                tupWOtherDirectionOne = (toTileTemplateCs, Direction.West, 1)
                tupEOtherDirectionOne = (toTileTemplateCs, Direction.East, 1)
                tupNOtherDirectionOne = (toTileTemplateCs, Direction.North, 1)
                tupSOtherDirectionOne = (toTileTemplateCs, Direction.South, 1)
            
                tupWOtherDirectionTwo = (toTileTemplateCs, Direction.West, 2)
                tupEOtherDirectionTwo = (toTileTemplateCs, Direction.East, 2)
                tupNOtherDirectionTwo = (toTileTemplateCs, Direction.North, 2)
                tupSOtherDirectionTwo = (toTileTemplateCs, Direction.South, 2)
            
            
            
                ##alters the glueAnnotation for ports on the "West" Side of the toTileTemplateCs
            
                retWList = tileSetTemplate.tileTempToPortDictReverse.get(tupW)
            
                if retWList is not None:
                
                    if len(retWList) <= 1: #if there is more than one tuple in the list cant be a port since port only comes alone in a neighborhood
                    
                        retW = retWList[0]
                    
                        if type(retW[0]) in [Port,initiatorPort]:
                            inputnames = set()
                            inputnames.add(retW[0].name)
                        
                        
                            portParentConfigurationMet = False #
                            portSharedParent = None #
                        
                       
                        
                            previousPort = retW[0] #
                        
                            newVal = tileSetTemplate.tileTempToPortDictReverse.get(retW)
                            newValTup = newVal[0] 
                            currentPort = newValTup[0] #
                        
                        
                            while type(newValTup[0]) not in [TileTemplate,Tile]:
                            
                                if (previousPort.parent).parent == (currentPort.parent).parent: #
                                    portParentConfigurationMet = True #
                                    portSharedParent = (previousPort.parent).parent #
                              
                                previousPort = currentPort #
                                inputnames.add((newValTup)[0].name)
                                newValTup = tileSetTemplate.tileTempToPortDictReverse.get(newValTup)[0]
                                currentPort = newValTup[0] #
                       
                        
                        
                            if portParentConfigurationMet == False:  #
                                raise portParentConfigurationNotMet(toTileTemplateCs) #
                            ancestorSet = set() #
                            if portSharedParent.name is not "rootMod": #
                                traceToRoot = portSharedParent #
                                while traceToRoot.name is not "rootMod": #
                                    ancestorSet.add(traceToRoot.name) #
                                    traceToRoot = traceToRoot.parent #
                                ancestorSet.add("rootMod") #
                            else: #
                                ancestorSet.add(portSharedParent.name) #
                            
                        
                            
                            inputNbrhd = (toTileTemplateCs.parent)._getNeighborhoodForJoin(wNbhdStrength, Direction.West, retW[0], toTileTemplateCs)
                            toTileTempFromNewVal = tileSetTemplate.tileTempToPortDict.get(newValTup)[0]
                            
                            outputNbrhd = (newValTup[0].parent)._getNeighborhoodForJoin(newValTup[2], Direction.West, newValTup[0],toTileTempFromNewVal[0] )
                            
                            for join in outputNbrhd.joins:
                                inputnames.add(join.fromObj.name)
            
                            outputnames = set()
                            for join in inputNbrhd.joins:
                                outputnames.add(join.toObj.name)
            
                            newGlueAnnotation = ';{0}-{1}>{2}-{3}'.format(','.join(inputnames),directionShortName(Direction.West),','.join(outputnames),",".join(ancestorSet)) #
                          
                            inputNbrhd.glueAnnotation = newGlueAnnotation
                            outputNbrhd.glueAnnotation = newGlueAnnotation
                        
            
                retWListOtherDirectionOne = tileSetTemplate.tileTempToPortDict.get(tupWOtherDirectionOne)
            
           
                if retWListOtherDirectionOne is not None:
                
                    if len(retWListOtherDirectionOne) <= 1: #if there is more than one tuple in the list cant be a port since port only comes alone in a neighborhood
                    
                        retWOtherDirection = retWListOtherDirectionOne[0]
                    
                        if type(retWOtherDirection[0]) in [Port,initiatorPort]:
                            inputnames = set()
                            inputnames.add(retWOtherDirection[0].name)
                        
                            portParentConfigurationMet = False #
                            portSharedParent = None #
                        
                        
                            previousPort = retWOtherDirection[0] #
                        
    
            
                            newVal = tileSetTemplate.tileTempToPortDict.get(retWOtherDirection)
                            newValTup = newVal[0]
                            currentPort = newValTup[0] #
                        
                            while type(newValTup[0]) not in [TileTemplate,Tile]:
                            
                                if (previousPort.parent).parent == (currentPort.parent).parent: #
                                    portParentConfigurationMet = True #
                                    portSharedParent = (previousPort.parent).parent #
                            
                                previousPort = currentPort #    
                                inputnames.add((newValTup)[0].name)
                                newValTup = tileSetTemplate.tileTempToPortDict.get(newValTup)[0]
                                currentPort = newValTup[0] #
                            
                            if portParentConfigurationMet == False:  #
                                raise portParentConfigurationNotMet(toTileTemplateCs) #
                            ancestorSet = set() #
                            if portSharedParent.name is not "rootMod": #
                                traceToRoot = portSharedParent #
                                while traceToRoot.name is not "rootMod": #
                                    ancestorSet.add(traceToRoot.name) #
                                    traceToRoot = traceToRoot.parent #
                                ancestorSet.add("rootMod") #
                            else: #
                                ancestorSet.add(portSharedParent.name) #
                            
                            
                            outputNbrhd = (toTileTemplateCs.parent)._getNeighborhoodForJoin(1, Direction.West, toTileTemplateCs, retWOtherDirection[0])
                            toTileTempFromNewValOtherDirection = tileSetTemplate.tileTempToPortDictReverse.get(newValTup)[0]
            
                            inputNbrhd = (toTileTempFromNewValOtherDirection[0].parent)._getNeighborhoodForJoin(newValTup[2], Direction.West, toTileTempFromNewValOtherDirection[0],newValTup[0] )
            
                            outputnames = set()
            
                            for join in inputNbrhd.joins:
                                outputnames.add(join.toObj.name)
            
                        
                            for join in outputNbrhd.joins:
                                inputnames.add(join.fromObj.name)
            
                            newGlueAnnotation = ';{0}-{1}>{2}-{3}'.format(','.join(inputnames),directionShortName(Direction.West),','.join(outputnames),",".join(ancestorSet))
            
                            inputNbrhd.glueAnnotation = newGlueAnnotation
                            outputNbrhd.glueAnnotation = newGlueAnnotation
            
           
                retWListOtherDirectionTwo = tileSetTemplate.tileTempToPortDict.get(tupWOtherDirectionTwo)
                if retWListOtherDirectionTwo is not None:
                
                    if len(retWListOtherDirectionTwo) <= 1: #if there is more than one tuple in the list cant be a port since port only comes alone in a neighborhood
                    
                        retWOtherDirection = retWListOtherDirectionTwo[0]
                    
                        if type(retWOtherDirection[0]) in [Port,initiatorPort]:
                        
                            inputnames = set()
                            inputnames.add(retWOtherDirection[0].name)
                        
                            portParentConfigurationMet = False #
                            portSharedParent = None #
                        
                            previousPort = retWOtherDirection[0] #
                        
    
            
                            newVal = tileSetTemplate.tileTempToPortDict.get(retWOtherDirection)
                            newValTup = newVal[0]
                            currentPort = newValTup[0] #
                            while type(newValTup[0]) not in [TileTemplate,Tile]:
                            
                                if (previousPort.parent).parent == (currentPort.parent).parent: #
                                    portParentConfigurationMet = True #
                                    portSharedParent = (previousPort.parent).parent #
                                
                                previousPort = currentPort #  
                                inputnames.add((newValTup)[0].name)
                                newValTup = tileSetTemplate.tileTempToPortDict.get(newValTup)[0]
                                currentPort = newValTup[0] #
                            
                            if portParentConfigurationMet == False:  #
                                raise portParentConfigurationNotMet(toTileTemplateCs) #
                            ancestorSet = set() #
                            if portSharedParent.name is not "rootMod": #
                                traceToRoot = portSharedParent #
                                while traceToRoot.name is not "rootMod": #
                                    ancestorSet.add(traceToRoot.name) #
                                    traceToRoot = traceToRoot.parent #
                                ancestorSet.add("rootMod") #
                            else: #
                                ancestorSet.add(portSharedParent.name) #
                            
                            outputNbrhd = (toTileTemplateCs.parent)._getNeighborhoodForJoin(2, Direction.West, toTileTemplateCs, retWOtherDirection[0])
                            toTileTempFromNewValOtherDirection = tileSetTemplate.tileTempToPortDictReverse.get(newValTup)[0]
            
                            inputNbrhd = (toTileTempFromNewValOtherDirection[0].parent)._getNeighborhoodForJoin(newValTup[2], Direction.West, toTileTempFromNewValOtherDirection[0],newValTup[0] )
                            outputnames = set()
            
                            for join in inputNbrhd.joins:
                                outputnames.add(join.toObj.name)
            
                        
                            for join in outputNbrhd.joins:
                                inputnames.add(join.fromObj.name)
            
                            newGlueAnnotation = ';{0}-{1}>{2}-{3}'.format(','.join(inputnames),directionShortName(Direction.West),','.join(outputnames),",".join(ancestorSet))
            
                            inputNbrhd.glueAnnotation = newGlueAnnotation
                            outputNbrhd.glueAnnotation = newGlueAnnotation
            
            
                #Alters the Glue Annotation for the "East" Side
            
                retEList = tileSetTemplate.tileTempToPortDictReverse.get(tupE)
            
                if retEList is not None:
                
                    if len(retEList) <= 1: #if there is more than one tuple in the list cant be a port since port only comes alone in a neighborhood
                    
                        retE = retEList[0]
                    
                        if type(retE[0]) in [Port,initiatorPort]:
                            inputnames = set()
                            inputnames.add(retE[0].name)
                        
                            portParentConfigurationMet = False #
                            portSharedParent = None #
                        
                       
                        
                            previousPort = retE[0] #
                        
    
            
                            newVal = tileSetTemplate.tileTempToPortDictReverse.get(retE)
                            newValTup = newVal[0]
                            currentPort = newValTup[0] #
                            while type(newValTup[0]) not in [TileTemplate,Tile]:
                            
                                if (previousPort.parent).parent == (currentPort.parent).parent: #
                                    portParentConfigurationMet = True #
                                    portSharedParent = (previousPort.parent).parent #
                                
                                previousPort = currentPort #  
                                inputnames.add((newValTup)[0].name)
                                newValTup = tileSetTemplate.tileTempToPortDictReverse.get(newValTup)[0]
                                currentPort = newValTup[0] #
                            
                            if portParentConfigurationMet == False:  #
                                raise portParentConfigurationNotMet(toTileTemplateCs) #
                            ancestorSet = set() #
                            if portSharedParent.name is not "rootMod": #
                                traceToRoot = portSharedParent #
                                while traceToRoot.name is not "rootMod": #
                                    ancestorSet.add(traceToRoot.name) #
                                    traceToRoot = traceToRoot.parent #
                                ancestorSet.add("rootMod") #
                            else: #
                                ancestorSet.add(portSharedParent.name) #
                            
                        
                            
                            inputNbrhd = (toTileTemplateCs.parent)._getNeighborhoodForJoin(eNbhdStrength, Direction.East, retE[0], toTileTemplateCs)
                            toTileTempFromNewVal = tileSetTemplate.tileTempToPortDict.get(newValTup)[0]
            
                            outputNbrhd = (newValTup[0].parent)._getNeighborhoodForJoin(newValTup[2], Direction.East, newValTup[0],toTileTempFromNewVal[0] )
            
                            for join in outputNbrhd.joins:
                                inputnames.add(join.fromObj.name)
            
                            outputnames = set()
                            for join in inputNbrhd.joins:
                                outputnames.add(join.toObj.name)
            
                            newGlueAnnotation = ';{0}-{1}>{2}-{3}'.format(','.join(inputnames),directionShortName(Direction.East),','.join(outputnames),",".join(ancestorSet))
            
                            inputNbrhd.glueAnnotation = newGlueAnnotation
                            outputNbrhd.glueAnnotation = newGlueAnnotation
                        
            
                #for other direction strength one
                retEListOtherDirectionOne = tileSetTemplate.tileTempToPortDict.get(tupEOtherDirectionOne)
            
           
                if retEListOtherDirectionOne is not None:
                
                    if len(retEListOtherDirectionOne) <= 1: #if there is more than one tuple in the list cant be a port since port only comes alone in a neighborhood
                    
                        retEOtherDirection = retEListOtherDirectionOne[0]
                    
                        if type(retEOtherDirection[0]) in [Port,initiatorPort]:
                            inputnames = set()
                            inputnames.add(retEOtherDirection[0].name)
                        
                            portParentConfigurationMet = False #
                            portSharedParent = None #
                        
                            previousPort = retEOtherDirection[0] #
                        
    
            
                            newVal = tileSetTemplate.tileTempToPortDict.get(retEOtherDirection)
                            newValTup = newVal[0]
                            currentPort = newValTup[0] #
                            while type(newValTup[0]) not in [TileTemplate,Tile]:
                                if (previousPort.parent).parent == (currentPort.parent).parent: #
                                    portParentConfigurationMet = True #
                                    portSharedParent = (previousPort.parent).parent #
                                
                                previousPort = currentPort # 
                                inputnames.add((newValTup)[0].name)
                                newValTup = tileSetTemplate.tileTempToPortDict.get(newValTup)[0]
                                currentPort = newValTup[0] #
                            
                            if portParentConfigurationMet == False:  #
                                raise portParentConfigurationNotMet(toTileTemplateCs) #
                            ancestorSet = set() #
                            if portSharedParent.name is not "rootMod": #
                                traceToRoot = portSharedParent #
                                while traceToRoot.name is not "rootMod": #
                                    ancestorSet.add(traceToRoot.name) #
                                    traceToRoot = traceToRoot.parent #
                                ancestorSet.add("rootMod") #
                            else: #
                                ancestorSet.add(portSharedParent.name) #
                            
                            outputNbrhd = (toTileTemplateCs.parent)._getNeighborhoodForJoin(1, Direction.East, toTileTemplateCs, retEOtherDirection[0])
                            toTileTempFromNewValOtherDirection = tileSetTemplate.tileTempToPortDictReverse.get(newValTup)[0]
            
                            inputNbrhd = (toTileTempFromNewValOtherDirection[0].parent)._getNeighborhoodForJoin(newValTup[2], Direction.East, toTileTempFromNewValOtherDirection[0],newValTup[0] )
            
                            outputnames = set()
            
                            for join in inputNbrhd.joins:
                                outputnames.add(join.toObj.name)
            
                        
                            for join in outputNbrhd.joins:
                                inputnames.add(join.fromObj.name)
            
                            newGlueAnnotation = ';{0}-{1}>{2}-{3}'.format(','.join(inputnames),directionShortName(Direction.East),','.join(outputnames),",".join(ancestorSet))
            
                            inputNbrhd.glueAnnotation = newGlueAnnotation
                            outputNbrhd.glueAnnotation = newGlueAnnotation
            
                #for other direction strength 2
           
                retEListOtherDirectionTwo = tileSetTemplate.tileTempToPortDict.get(tupEOtherDirectionTwo)
                if retEListOtherDirectionTwo is not None:
                
                    if len(retEListOtherDirectionTwo) <= 1: #if there is more than one tuple in the list cant be a port since port only comes alone in a neighborhood
                    
                        retEOtherDirection = retEListOtherDirectionTwo[0]
                    
                        if type(retEOtherDirection[0]) in [Port,initiatorPort]:
                        
                            inputnames = set()
                            inputnames.add(retEOtherDirection[0].name)
                        
                            portParentConfigurationMet = False #
                            portSharedParent = None #
                        
                            previousPort = retEOtherDirection[0] #
                        
    
            
                            newVal = tileSetTemplate.tileTempToPortDict.get(retEOtherDirection)
                            newValTup = newVal[0]
                            currentPort = newValTup[0] #
                            while type(newValTup[0]) not in [TileTemplate,Tile]:
                                if (previousPort.parent).parent == (currentPort.parent).parent: #
                                    portParentConfigurationMet = True #
                                    portSharedParent = (previousPort.parent).parent #
                                
                                previousPort = currentPort # 
                                inputnames.add((newValTup)[0].name)
                                newValTup = tileSetTemplate.tileTempToPortDict.get(newValTup)[0]
                                currentPort = newValTup[0] #
                        
                            if portParentConfigurationMet == False:  #
                                raise portParentConfigurationNotMet(toTileTemplateCs) #
                            ancestorSet = set() #
                            if portSharedParent.name is not "rootMod": #
                                traceToRoot = portSharedParent #
                                while traceToRoot.name is not "rootMod": #
                                    ancestorSet.add(traceToRoot.name) #
                                    traceToRoot = traceToRoot.parent #
                                ancestorSet.add("rootMod") #
                            else: #
                                ancestorSet.add(portSharedParent.name) #
                            
                            
                            outputNbrhd = (toTileTemplateCs.parent)._getNeighborhoodForJoin(2, Direction.East, toTileTemplateCs, retEOtherDirection[0])
                            toTileTempFromNewValOtherDirection = tileSetTemplate.tileTempToPortDictReverse.get(newValTup)[0]
            
                            inputNbrhd = (toTileTempFromNewValOtherDirection[0].parent)._getNeighborhoodForJoin(newValTup[2], Direction.East, toTileTempFromNewValOtherDirection[0],newValTup[0] )
                            outputnames = set()
            
                            for join in inputNbrhd.joins:
                                outputnames.add(join.toObj.name)
            
                        
                            for join in outputNbrhd.joins:
                                inputnames.add(join.fromObj.name)
            
                            newGlueAnnotation = ';{0}-{1}>{2}-{3}'.format(','.join(inputnames),directionShortName(Direction.East),','.join(outputnames),",".join(ancestorSet))
            
                            inputNbrhd.glueAnnotation = newGlueAnnotation
                            outputNbrhd.glueAnnotation = newGlueAnnotation
            
                #Alters the Glue annotation for the "North" side
            
                retNList = tileSetTemplate.tileTempToPortDictReverse.get(tupN)
            
                if retNList is not None:
                
                    if len(retNList) <= 1: #if there is more than one tuple in the list cant be a port since port only comes alone in a neighborhood
                    
                        retN = retNList[0]
                    
                        if type(retN[0]) in [Port,initiatorPort]:
                            inputnames = set()
                            inputnames.add(retN[0].name)
                        
                            portParentConfigurationMet = False #
                            portSharedParent = None #
                        
                       
                        
                            previousPort = retN[0] #
                        
    
            
                            newVal = tileSetTemplate.tileTempToPortDictReverse.get(retN)
                            newValTup = newVal[0]
                            currentPort = newValTup[0] #
                            while type(newValTup[0]) not in [TileTemplate,Tile]:
                                if (previousPort.parent).parent == (currentPort.parent).parent: #
                                    portParentConfigurationMet = True #
                                    portSharedParent = (previousPort.parent).parent #
                                
                                previousPort = currentPort # 
                                inputnames.add((newValTup)[0].name)
                                newValTup = tileSetTemplate.tileTempToPortDictReverse.get(newValTup)[0]
                                currentPort = newValTup[0] #
                            
                            if portParentConfigurationMet == False:  #
                                raise portParentConfigurationNotMet(toTileTemplateCs) #
                            ancestorSet = set() #
                            if portSharedParent.name is not "rootMod": #
                                traceToRoot = portSharedParent #
                                while traceToRoot.name is not "rootMod": #
                                    ancestorSet.add(traceToRoot.name) #
                                    traceToRoot = traceToRoot.parent #
                                ancestorSet.add("rootMod") #
                            else: #
                                ancestorSet.add(portSharedParent.name) #
                        
                            
                            inputNbrhd = (toTileTemplateCs.parent)._getNeighborhoodForJoin(nNbhdStrength, Direction.North, retN[0], toTileTemplateCs)
                            toTileTempFromNewVal = tileSetTemplate.tileTempToPortDict.get(newValTup)[0]
            
                            outputNbrhd = (newValTup[0].parent)._getNeighborhoodForJoin(newValTup[2], Direction.North, newValTup[0],toTileTempFromNewVal[0] )
            
                            for join in outputNbrhd.joins:
                                inputnames.add(join.fromObj.name)
            
                            outputnames = set()
                            for join in inputNbrhd.joins:
                                outputnames.add(join.toObj.name)
            
                            newGlueAnnotation = ';{0}-{1}>{2}-{3}'.format(','.join(inputnames),directionShortName(Direction.North),','.join(outputnames),",".join(ancestorSet))
            
                            inputNbrhd.glueAnnotation = newGlueAnnotation
                            outputNbrhd.glueAnnotation = newGlueAnnotation
                        
            
                #for other direction strength one
                retNListOtherDirectionOne = tileSetTemplate.tileTempToPortDict.get(tupNOtherDirectionOne)
        
           
                if retNListOtherDirectionOne is not None:
                
                    if len(retNListOtherDirectionOne) <= 1: #if there is more than one tuple in the list cant be a port since port only comes alone in a neighborhood
                    
                        retNOtherDirection = retNListOtherDirectionOne[0]
                    
                        if type(retNOtherDirection[0]) in [Port,initiatorPort]:
                            inputnames = set()
                            inputnames.add(retNOtherDirection[0].name)
                        
                            portParentConfigurationMet = False #
                            portSharedParent = None #
                        
                       
                        
                            previousPort = retNOtherDirection[0] #
                        
    
            
                            newVal = tileSetTemplate.tileTempToPortDict.get(retNOtherDirection)
                            newValTup = newVal[0]
                            currentPort = newValTup[0] #
                            while type(newValTup[0]) not in [TileTemplate,Tile]:
                                if (previousPort.parent).parent == (currentPort.parent).parent: #
                                    portParentConfigurationMet = True #
                                    portSharedParent = (previousPort.parent).parent #
                                
                                previousPort = currentPort # 
                                inputnames.add((newValTup)[0].name)
                                newValTup = tileSetTemplate.tileTempToPortDict.get(newValTup)[0]
                                currentPort = newValTup[0] #
                            
                            if portParentConfigurationMet == False:  #
                                raise portParentConfigurationNotMet(toTileTemplateCs) #
                            ancestorSet = set() #
                            if portSharedParent.name is not "rootMod": #
                                traceToRoot = portSharedParent #
                                while traceToRoot.name is not "rootMod": #
                                    ancestorSet.add(traceToRoot.name) #
                                    traceToRoot = traceToRoot.parent #
                                ancestorSet.add("rootMod") #
                            else: #
                                ancestorSet.add(portSharedParent.name) #
                            
                            outputNbrhd = (toTileTemplateCs.parent)._getNeighborhoodForJoin(1, Direction.North, toTileTemplateCs, retNOtherDirection[0])
                            toTileTempFromNewValOtherDirection = tileSetTemplate.tileTempToPortDictReverse.get(newValTup)[0]
            
                            inputNbrhd = (toTileTempFromNewValOtherDirection[0].parent)._getNeighborhoodForJoin(newValTup[2], Direction.North, toTileTempFromNewValOtherDirection[0],newValTup[0] )
            
                            outputnames = set()
            
                            for join in inputNbrhd.joins:
                                outputnames.add(join.toObj.name)
            
                        
                            for join in outputNbrhd.joins:
                                inputnames.add(join.fromObj.name)
            
                            newGlueAnnotation = ';{0}-{1}>{2}-{3}'.format(','.join(inputnames),directionShortName(Direction.North),','.join(outputnames),",".join(ancestorSet))
            
                            inputNbrhd.glueAnnotation = newGlueAnnotation
                            outputNbrhd.glueAnnotation = newGlueAnnotation
            
                #for other direction strength 2
           
                retNListOtherDirectionTwo = tileSetTemplate.tileTempToPortDict.get(tupNOtherDirectionTwo)
         
                if retNListOtherDirectionTwo is not None:
                
                    if len(retNListOtherDirectionTwo) <= 1: #if there is more than one tuple in the list cant be a port since port only comes alone in a neighborhood
                    
                        retNOtherDirection = retNListOtherDirectionTwo[0]
                    
                        if type(retNOtherDirection[0]) in [Port,initiatorPort]:
                        
                            inputnames = set()
                            inputnames.add(retNOtherDirection[0].name)
                        
                            portParentConfigurationMet = False #
                            portSharedParent = None #
                        
                       
                        
                            previousPort = retNOtherDirection[0] #
                        
    
            
                            newVal = tileSetTemplate.tileTempToPortDict.get(retNOtherDirection)
                            newValTup = newVal[0]
                            currentPort = newValTup[0] #
                            while type(newValTup[0]) not in [TileTemplate,Tile]:
                                if (previousPort.parent).parent == (currentPort.parent).parent: #
                                    portParentConfigurationMet = True #
                                    portSharedParent = (previousPort.parent).parent #
                                
                                previousPort = currentPort # 
                                inputnames.add((newValTup)[0].name)
                                newValTup = tileSetTemplate.tileTempToPortDict.get(newValTup)[0]
                                currentPort = newValTup[0] #
                            
                            if portParentConfigurationMet == False:  #
                                raise portParentConfigurationNotMet(toTileTemplateCs) #
                            ancestorSet = set() #
                            if portSharedParent.name is not "rootMod": #
                                traceToRoot = portSharedParent #
                                while traceToRoot.name is not "rootMod": #
                                    ancestorSet.add(traceToRoot.name) #
                                    traceToRoot = traceToRoot.parent #
                                ancestorSet.add("rootMod") #
                            else: #
                                ancestorSet.add(portSharedParent.name) #
                            
                            
                            outputNbrhd = (toTileTemplateCs.parent)._getNeighborhoodForJoin(2, Direction.North, toTileTemplateCs, retNOtherDirection[0])
                            toTileTempFromNewValOtherDirection = tileSetTemplate.tileTempToPortDictReverse.get(newValTup)[0]
            
                            inputNbrhd = (toTileTempFromNewValOtherDirection[0].parent)._getNeighborhoodForJoin(newValTup[2], Direction.North, toTileTempFromNewValOtherDirection[0],newValTup[0] )
                            outputnames = set()
            
                            for join in inputNbrhd.joins:
                                outputnames.add(join.toObj.name)
            
                        
                            for join in outputNbrhd.joins:
                                inputnames.add(join.fromObj.name)
            
                            newGlueAnnotation = ';{0}-{1}>{2}-{3}'.format(','.join(inputnames),directionShortName(Direction.North),','.join(outputnames),",".join(ancestorSet))
            
                            inputNbrhd.glueAnnotation = newGlueAnnotation
                            outputNbrhd.glueAnnotation = newGlueAnnotation
            
                #Alters the Glue Annotation for the "South" Side
                retSList = tileSetTemplate.tileTempToPortDictReverse.get(tupS)
            
                if retSList is not None:
                
                    if len(retSList) <= 1: #if there is more than one tuple in the list cant be a port since port only comes alone in a neighborhood
                    
                        retS = retSList[0]
                    
                        if type(retS[0]) in [Port,initiatorPort]:
                            inputnames = set()
                            inputnames.add(retS[0].name)
                        
                            portParentConfigurationMet = False #
                            portSharedParent = None #
                        
                       
                        
                            previousPort = retS[0] #
                        
                        
    
            
                            newVal = tileSetTemplate.tileTempToPortDictReverse.get(retS)
                            newValTup = newVal[0]
                            currentPort = newValTup[0] #
                            while type(newValTup[0]) not in [TileTemplate,Tile]:
                                if (previousPort.parent).parent == (currentPort.parent).parent: #
                                    portParentConfigurationMet = True #
                                    portSharedParent = (previousPort.parent).parent #
                                
                                previousPort = currentPort # 
                                inputnames.add((newValTup)[0].name)
                                newValTup = tileSetTemplate.tileTempToPortDictReverse.get(newValTup)[0]
                                currentPort = newValTup[0] #
                            
                            if portParentConfigurationMet == False:  #
                                raise portParentConfigurationNotMet(toTileTemplateCs) #
                            ancestorSet = set() #
                            if portSharedParent.name is not "rootMod": #
                                traceToRoot = portSharedParent #
                                while traceToRoot.name is not "rootMod": #
                                    ancestorSet.add(traceToRoot.name) #
                                    traceToRoot = traceToRoot.parent #
                                ancestorSet.add("rootMod") #
                            else: #
                                ancestorSet.add(portSharedParent.name) #
                        
                            
                        
                            
                            inputNbrhd = (toTileTemplateCs.parent)._getNeighborhoodForJoin(sNbhdStrength, Direction.South, retS[0], toTileTemplateCs)
                            toTileTempFromNewVal = tileSetTemplate.tileTempToPortDict.get(newValTup)[0]
            
                            outputNbrhd = (newValTup[0].parent)._getNeighborhoodForJoin(newValTup[2], Direction.South, newValTup[0],toTileTempFromNewVal[0] )
            
                            for join in outputNbrhd.joins:
                                inputnames.add(join.fromObj.name)
            
                            outputnames = set()
                            for join in inputNbrhd.joins:
                                outputnames.add(join.toObj.name)
            
                            newGlueAnnotation = ';{0}-{1}>{2}-{3}'.format(','.join(inputnames),directionShortName(Direction.South),','.join(outputnames),",".join(ancestorSet))
            
                            inputNbrhd.glueAnnotation = newGlueAnnotation
                            outputNbrhd.glueAnnotation = newGlueAnnotation
                        
            
                #for other direction strength one
                retSListOtherDirectionOne = tileSetTemplate.tileTempToPortDict.get(tupSOtherDirectionOne)
            
           
                if retSListOtherDirectionOne is not None:
                
                    if len(retSListOtherDirectionOne) <= 1: #if there is more than one tuple in the list cant be a port since port only comes alone in a neighborhood
                    
                        retSOtherDirection = retSListOtherDirectionOne[0]
                    
                        if type(retSOtherDirection[0]) in [Port,initiatorPort]:
                            inputnames = set()
                            inputnames.add(retSOtherDirection[0].name)
                        
                            portParentConfigurationMet = False #
                            portSharedParent = None #
                        
                       
                        
                            previousPort = retSOtherDirection[0] #
                        
                        
    
            
                            newVal = tileSetTemplate.tileTempToPortDict.get(retSOtherDirection)
                            newValTup = newVal[0]
                            currentPort = newValTup[0] #
                            while type(newValTup[0]) not in [TileTemplate,Tile]:
                                if (previousPort.parent).parent == (currentPort.parent).parent: #
                                    portParentConfigurationMet = True #
                                    portSharedParent = (previousPort.parent).parent #
                                
                                previousPort = currentPort # 
                                inputnames.add((newValTup)[0].name)
                                newValTup = tileSetTemplate.tileTempToPortDict.get(newValTup)[0]
                                currentPort = newValTup[0] #
                            
                            if portParentConfigurationMet == False:  #
                                raise portParentConfigurationNotMet(toTileTemplateCs) #
                            ancestorSet = set() #
                            if portSharedParent.name is not "rootMod": #
                                traceToRoot = portSharedParent #
                                while traceToRoot.name is not "rootMod": #
                                    ancestorSet.add(traceToRoot.name) #
                                    traceToRoot = traceToRoot.parent #
                                ancestorSet.add("rootMod") #
                            else: #
                                ancestorSet.add(portSharedParent.name) #
                            
                            outputNbrhd = (toTileTemplateCs.parent)._getNeighborhoodForJoin(1, Direction.South, toTileTemplateCs, retSOtherDirection[0])
                            toTileTempFromNewValOtherDirection = tileSetTemplate.tileTempToPortDictReverse.get(newValTup)[0]
            
                            inputNbrhd = (toTileTempFromNewValOtherDirection[0].parent)._getNeighborhoodForJoin(newValTup[2], Direction.South, toTileTempFromNewValOtherDirection[0],newValTup[0] )
                        
                            outputnames = set()
            
                            for join in inputNbrhd.joins:
                                outputnames.add(join.toObj.name)
            
                        
                            for join in outputNbrhd.joins:
                                inputnames.add(join.fromObj.name)
            
                            newGlueAnnotation = ';{0}-{1}>{2}-{3}'.format(','.join(inputnames),directionShortName(Direction.South),','.join(outputnames),",".join(ancestorSet))
            
                            inputNbrhd.glueAnnotation = newGlueAnnotation
                            outputNbrhd.glueAnnotation = newGlueAnnotation
            
                #for other direction strength 2
           
                retSListOtherDirectionTwo = tileSetTemplate.tileTempToPortDict.get(tupSOtherDirectionTwo)
                if retSListOtherDirectionTwo is not None:
                
                    if len(retSListOtherDirectionTwo) <= 1: #if there is more than one tuple in the list cant be a port since port only comes alone in a neighborhood
                    
                        retSOtherDirection = retSListOtherDirectionTwo[0]
                    
                        if type(retSOtherDirection[0]) in [Port,initiatorPort]:
                        
                            inputnames = set()
                            inputnames.add(retSOtherDirection[0].name)
                        
                            portParentConfigurationMet = False #
                            portSharedParent = None #
                        
                       
                        
                            previousPort = retSOtherDirection[0] #
                        
    
            
                            newVal = tileSetTemplate.tileTempToPortDict.get(retSOtherDirection)
                            newValTup = newVal[0]
                            currentPort = newValTup[0] #
                            while type(newValTup[0]) not in [TileTemplate,Tile]:
                                if (previousPort.parent).parent == (currentPort.parent).parent: #
                                    portParentConfigurationMet = True #
                                    portSharedParent = (previousPort.parent).parent #
                                
                                previousPort = currentPort # 
                                inputnames.add((newValTup)[0].name)
                                newValTup = tileSetTemplate.tileTempToPortDict.get(newValTup)[0]
                                currentPort = newValTup[0] #
                            
                            if portParentConfigurationMet == False:  #
                                raise portParentConfigurationNotMet(toTileTemplateCs) #
                            ancestorSet = set() #
                            if portSharedParent.name is not "rootMod": #
                                traceToRoot = portSharedParent #
                                while traceToRoot.name is not "rootMod": #
                                    ancestorSet.add(traceToRoot.name) #
                                    traceToRoot = traceToRoot.parent #
                                ancestorSet.add("rootMod") #
                            else: #
                                ancestorSet.add(portSharedParent.name) #
                            
                            
                            outputNbrhd = (toTileTemplateCs.parent)._getNeighborhoodForJoin(2, Direction.South, toTileTemplateCs, retSOtherDirection[0])
                            toTileTempFromNewValOtherDirection = tileSetTemplate.tileTempToPortDictReverse.get(newValTup)[0]
            
                            inputNbrhd = (toTileTempFromNewValOtherDirection[0].parent)._getNeighborhoodForJoin(newValTup[2], Direction.South, toTileTempFromNewValOtherDirection[0],newValTup[0] )
                            outputnames = set()
            
                            for join in inputNbrhd.joins:
                                outputnames.add(join.toObj.name)
            
                        
                            for join in outputNbrhd.joins:
                                inputnames.add(join.fromObj.name)
            
                            newGlueAnnotation = ';{0}-{1}>{2}-{3}'.format(','.join(inputnames),directionShortName(Direction.South),','.join(outputnames),",".join(ancestorSet))
            
                            inputNbrhd.glueAnnotation = newGlueAnnotation
                            outputNbrhd.glueAnnotation = newGlueAnnotation
                
                #add module to tile template glue
                #west        
                retWTileTempList = tileSetTemplate.tileTempToPortDictReverse.get(tupW)
                if retWTileTempList is not None:
                    retWTileTemp = retWTileTempList[0]
                    if type(retWTileTemp[0]) in [TileTemplate,Tile]:
                        #add output neighborhood
                        inputNbrhd = (toTileTemplateCs.parent)._getNeighborhoodForJoin(wNbhdStrength, Direction.West, retWTileTemp[0], toTileTemplateCs)
                        if inputNbrhd.glueAnnotation is not None:
                            if toTileTemplateCs.parent.name in inputNbrhd.glueAnnotation:
                                pass
                            else:
                                inputNbrhd.glueAnnotation += "-" + toTileTemplateCs.parent.name
                                
                            if inputNbrhd != toTileTemplateCs.inputNeighborhood(Direction.East):
                                if toTileTemplateCs.parent.name in toTileTemplateCs.inputNeighborhood(Direction.East).glueAnnotation:
                                    pass
                                else:
                                    toTileTemplateCs.inputNeighborhood(Direction.East).glueAnnotation += "-" + toTileTemplateCs.parent.name
                                
                        
                if tupW in tileSetTemplate.tileTempToPortDict.keys():
                    newValTupTileTemp = tileSetTemplate.tileTempToPortDict.get(tupW)[0]
                    if type(newValTupTileTemp[0]) in [TileTemplate,Tile]:
                        outputNbrhd = (newValTupTileTemp[0].parent)._getNeighborhoodForJoin(newValTupTileTemp[2], Direction.West, toTileTemplateCs,newValTupTileTemp[0])
                        if outputNbrhd.glueAnnotation is not None:
                            if toTileTemplateCs.parent.name in outputNbrhd.glueAnnotation:
                                pass
                            else:
                                outputNbrhd.glueAnnotation += "-" + toTileTemplateCs.parent.name
                                
                            if outputNbrhd != toTileTemplateCs.outputNeighborhood(Direction.West):
                                if toTileTemplateCs.parent.name in toTileTemplateCs.outputNeighborhood(Direction.West).glueAnnotation:
                                    pass
                                else:
                                    toTileTemplateCs.outputNeighborhood(Direction.West).glueAnnotation += "-" + toTileTemplateCs.parent.name
                                
                if tupWOtherDirectionOne in tileSetTemplate.tileTempToPortDict.keys():
                    newValTupTileTemp = tileSetTemplate.tileTempToPortDict.get(tupWOtherDirectionOne)[0]
                    if type(newValTupTileTemp[0]) in [TileTemplate,Tile]:
                        outputNbrhd = (newValTupTileTemp[0].parent)._getNeighborhoodForJoin(1, Direction.West, toTileTemplateCs,newValTupTileTemp[0])
                        if outputNbrhd.glueAnnotation is not None:
                            if toTileTemplateCs.parent.name in outputNbrhd.glueAnnotation:
                                pass
                            else:
                                outputNbrhd.glueAnnotation += "-" + toTileTemplateCs.parent.name
                                
                            if outputNbrhd != toTileTemplateCs.outputNeighborhood(Direction.West):
                                if toTileTemplateCs.parent.name in toTileTemplateCs.outputNeighborhood(Direction.West).glueAnnotation:
                                    pass
                                else:
                                    toTileTemplateCs.outputNeighborhood(Direction.West).glueAnnotation += "-" + toTileTemplateCs.parent.name
                                
                if tupWOtherDirectionTwo in tileSetTemplate.tileTempToPortDict.keys():
                    newValTupTileTemp = tileSetTemplate.tileTempToPortDict.get(tupWOtherDirectionTwo)[0]
                    if type(newValTupTileTemp[0]) in [TileTemplate,Tile]:
                        outputNbrhd = (newValTupTileTemp[0].parent)._getNeighborhoodForJoin(2, Direction.West, toTileTemplateCs,newValTupTileTemp[0])
                        if outputNbrhd.glueAnnotation is not None:
                            if toTileTemplateCs.parent.name in outputNbrhd.glueAnnotation:
                                pass
                            else:
                                outputNbrhd.glueAnnotation += "-" + toTileTemplateCs.parent.name 
                            
                            if outputNbrhd != toTileTemplateCs.outputNeighborhood(Direction.West):
                                if toTileTemplateCs.parent.name in toTileTemplateCs.outputNeighborhood(Direction.West).glueAnnotation:
                                    pass
                                else:
                                    toTileTemplateCs.outputNeighborhood(Direction.West).glueAnnotation += "-" + toTileTemplateCs.parent.name
                                   
                #east
                retETileTempList = tileSetTemplate.tileTempToPortDictReverse.get(tupE)
                if retETileTempList is not None:
                    
                    retETileTemp = retETileTempList[0]
                    if type(retETileTemp[0]) in [TileTemplate,Tile]:
                        #add output neighborhood
                        inputNbrhd = (toTileTemplateCs.parent)._getNeighborhoodForJoin(eNbhdStrength, Direction.East, retETileTemp[0], toTileTemplateCs)
                        if inputNbrhd.glueAnnotation is not None:
                            if toTileTemplateCs.parent.name in inputNbrhd.glueAnnotation:
                                pass
                            else:
                                inputNbrhd.glueAnnotation += "-" + toTileTemplateCs.parent.name
                                
                            if inputNbrhd != toTileTemplateCs.inputNeighborhood(Direction.West):
                                if toTileTemplateCs.parent.name in toTileTemplateCs.inputNeighborhood(Direction.West).glueAnnotation:
                                    pass
                                else:
                                    toTileTemplateCs.inputNeighborhood(Direction.West).glueAnnotation += "-" + toTileTemplateCs.parent.name
                        
                        
                if tupE in tileSetTemplate.tileTempToPortDict.keys():
                    newValTupTileTemp = tileSetTemplate.tileTempToPortDict.get(tupE)[0]
                    if type(newValTupTileTemp[0]) in [TileTemplate,Tile]:
                        outputNbrhd = (newValTupTileTemp[0].parent)._getNeighborhoodForJoin(newValTupTileTemp[2], Direction.East, toTileTemplateCs,newValTupTileTemp[0] )
                        if outputNbrhd.glueAnnotation is not None:
                            if toTileTemplateCs.parent.name in outputNbrhd.glueAnnotation:
                                pass
                            else:
                                outputNbrhd.glueAnnotation += "-" + toTileTemplateCs.parent.name
                            
                            if outputNbrhd != toTileTemplateCs.outputNeighborhood(Direction.East):
                                if toTileTemplateCs.parent.name in toTileTemplateCs.outputNeighborhood(Direction.East).glueAnnotation:
                                    pass
                                else:
                                    toTileTemplateCs.outputNeighborhood(Direction.East).glueAnnotation += "-" + toTileTemplateCs.parent.name
                            
                if tupEOtherDirectionOne in tileSetTemplate.tileTempToPortDict.keys():
                    newValTupTileTemp = tileSetTemplate.tileTempToPortDict.get(tupEOtherDirectionOne)[0]
                    if type(newValTupTileTemp[0]) in [TileTemplate,Tile]:
                        outputNbrhd = (newValTupTileTemp[0].parent)._getNeighborhoodForJoin(1, Direction.East, toTileTemplateCs,newValTupTileTemp[0])
                        if outputNbrhd.glueAnnotation is not None:
                            if toTileTemplateCs.parent.name in outputNbrhd.glueAnnotation:
                                pass
                            else:
                                outputNbrhd.glueAnnotation += "-" + toTileTemplateCs.parent.name
                                
                            if outputNbrhd != toTileTemplateCs.outputNeighborhood(Direction.East):
                                if toTileTemplateCs.parent.name in toTileTemplateCs.outputNeighborhood(Direction.East).glueAnnotation:
                                    pass
                                else:
                                    toTileTemplateCs.outputNeighborhood(Direction.East).glueAnnotation += "-" + toTileTemplateCs.parent.name
                            
                if tupEOtherDirectionTwo in tileSetTemplate.tileTempToPortDict.keys():
                    newValTupTileTemp = tileSetTemplate.tileTempToPortDict.get(tupEOtherDirectionTwo)[0]
                    if type(newValTupTileTemp[0]) in [TileTemplate,Tile]:
                        outputNbrhd = (newValTupTileTemp[0].parent)._getNeighborhoodForJoin(2, Direction.East, toTileTemplateCs,newValTupTileTemp[0])
                        if outputNbrhd.glueAnnotation is not None:
                            if toTileTemplateCs.parent.name in outputNbrhd.glueAnnotation:
                                pass
                            else:
                                outputNbrhd.glueAnnotation += "-" + toTileTemplateCs.parent.name  
                                
                            if outputNbrhd != toTileTemplateCs.outputNeighborhood(Direction.East):
                                if toTileTemplateCs.parent.name in toTileTemplateCs.outputNeighborhood(Direction.East).glueAnnotation:
                                    pass
                                else:
                                    toTileTemplateCs.outputNeighborhood(Direction.East).glueAnnotation += "-" + toTileTemplateCs.parent.name
                             
                
                #north
                retNTileTempList = tileSetTemplate.tileTempToPortDictReverse.get(tupN)
                if retNTileTempList is not None:
                    retNTileTemp = retNTileTempList[0]
                    if type(retNTileTemp[0]) in [TileTemplate,Tile]:
                        #add output neighborhood
                        
                        inputNbrhd = (toTileTemplateCs.parent)._getNeighborhoodForJoin(nNbhdStrength, Direction.North, retNTileTemp[0], toTileTemplateCs)
                        if inputNbrhd.glueAnnotation is not None:
                            if toTileTemplateCs.parent.name in inputNbrhd.glueAnnotation:
                                pass
                            else:
                                inputNbrhd.glueAnnotation += "-" + toTileTemplateCs.parent.name
                                
                            if inputNbrhd != toTileTemplateCs.inputNeighborhood(Direction.South):
                                
                                if toTileTemplateCs.parent.name in toTileTemplateCs.inputNeighborhood(Direction.South).glueAnnotation:
                                    pass
                                else:
                                    toTileTemplateCs.inputNeighborhood(Direction.South).glueAnnotation += "-" + toTileTemplateCs.parent.name
                  
                                
                        
                if tupN in tileSetTemplate.tileTempToPortDict.keys():
                    newValTupTileTemp = tileSetTemplate.tileTempToPortDict.get(tupN)[0]
                    if type(newValTupTileTemp[0]) in [TileTemplate,Tile]:
                        outputNbrhd = (newValTupTileTemp[0].parent)._getNeighborhoodForJoin(newValTupTileTemp[2], Direction.North, toTileTemplateCs,newValTupTileTemp[0] )
                        if outputNbrhd.glueAnnotation is not None:
                            if toTileTemplateCs.parent.name in outputNbrhd.glueAnnotation:
                                pass
                            else:
                                outputNbrhd.glueAnnotation += "-" + toTileTemplateCs.parent.name
                           
                            if outputNbrhd != toTileTemplateCs.outputNeighborhood(Direction.North):
                                if toTileTemplateCs.parent.name in toTileTemplateCs.outputNeighborhood(Direction.North).glueAnnotation:
                                    pass
                                else:
                                    toTileTemplateCs.outputNeighborhood(Direction.North).glueAnnotation += "-" + toTileTemplateCs.parent.name
                            
                if tupNOtherDirectionOne in tileSetTemplate.tileTempToPortDict.keys():
                    newValTupTileTemp = tileSetTemplate.tileTempToPortDict.get(tupNOtherDirectionOne)[0]
                    if type(newValTupTileTemp[0]) in [TileTemplate,Tile]:
                        outputNbrhd = (newValTupTileTemp[0].parent)._getNeighborhoodForJoin(1, Direction.North, toTileTemplateCs,newValTupTileTemp[0])
                        if outputNbrhd.glueAnnotation is not None:
                            if toTileTemplateCs.parent.name in outputNbrhd.glueAnnotation:
                                pass
                            else:
                                outputNbrhd.glueAnnotation += "-" + toTileTemplateCs.parent.name
                            
                            if outputNbrhd != toTileTemplateCs.outputNeighborhood(Direction.North):
                                if toTileTemplateCs.parent.name in toTileTemplateCs.outputNeighborhood(Direction.North).glueAnnotation:
                                    pass
                                else:
                                    toTileTemplateCs.outputNeighborhood(Direction.North).glueAnnotation += "-" + toTileTemplateCs.parent.name
                               
                if tupNOtherDirectionTwo in tileSetTemplate.tileTempToPortDict.keys():
                    newValTupTileTemp = tileSetTemplate.tileTempToPortDict.get(tupNOtherDirectionTwo)[0]
                    if type(newValTupTileTemp[0]) in [TileTemplate,Tile]:
                        outputNbrhd = (newValTupTileTemp[0].parent)._getNeighborhoodForJoin(2, Direction.North, toTileTemplateCs,newValTupTileTemp[0])
                        if outputNbrhd.glueAnnotation is not None:
                            if toTileTemplateCs.parent.name in outputNbrhd.glueAnnotation:
                                pass
                            else:
                                outputNbrhd.glueAnnotation += "-" + toTileTemplateCs.parent.name
                            
                            if outputNbrhd != toTileTemplateCs.outputNeighborhood(Direction.North):
                                if toTileTemplateCs.parent.name in toTileTemplateCs.outputNeighborhood(Direction.North).glueAnnotation:
                                    pass
                                else:
                                    toTileTemplateCs.outputNeighborhood(Direction.North).glueAnnotation += "-" + toTileTemplateCs.parent.name
                                
                                
                            
                #south
                retSTileTempList = tileSetTemplate.tileTempToPortDictReverse.get(tupS)
                if retSTileTempList is not None:
                    retSTileTemp = retSTileTempList[0]
                    if type(retSTileTemp[0]) in [TileTemplate,Tile]:
                        #add output neighborhood
                        inputNbrhd = (toTileTemplateCs.parent)._getNeighborhoodForJoin(sNbhdStrength, Direction.South, retSTileTemp[0], toTileTemplateCs)
                        if inputNbrhd.glueAnnotation is not None:
                            if toTileTemplateCs.parent.name in inputNbrhd.glueAnnotation:
                                pass
                            else:
                                inputNbrhd.glueAnnotation += "-" + toTileTemplateCs.parent.name
                            
                            if inputNbrhd != toTileTemplateCs.inputNeighborhood(Direction.North):
                                
                                if toTileTemplateCs.parent.name in toTileTemplateCs.inputNeighborhood(Direction.North).glueAnnotation:
                                    pass
                                else:
                                    toTileTemplateCs.inputNeighborhood(Direction.North).glueAnnotation += "-" + toTileTemplateCs.parent.name
                        
                        
                if tupS in tileSetTemplate.tileTempToPortDict.keys():
                    newValTupTileTemp = tileSetTemplate.tileTempToPortDict.get(tupS)[0]
                    if type(newValTupTileTemp[0]) in [TileTemplate,Tile]:
                        outputNbrhd = (newValTupTileTemp[0].parent)._getNeighborhoodForJoin(newValTupTileTemp[2], Direction.South, toTileTemplateCs,newValTupTileTemp[0] )
                        if outputNbrhd.glueAnnotation is not None:
                            if toTileTemplateCs.parent.name in outputNbrhd.glueAnnotation:
                                pass
                            else:
                                outputNbrhd.glueAnnotation += "-" + toTileTemplateCs.parent.name
                                
                            if outputNbrhd != toTileTemplateCs.outputNeighborhood(Direction.South):
                                if toTileTemplateCs.parent.name in toTileTemplateCs.outputNeighborhood(Direction.South).glueAnnotation:
                                    pass
                                else:
                                    toTileTemplateCs.outputNeighborhood(Direction.South).glueAnnotation += "-" + toTileTemplateCs.parent.name
                                
                if tupSOtherDirectionOne in tileSetTemplate.tileTempToPortDict.keys():
                    newValTupTileTemp = tileSetTemplate.tileTempToPortDict.get(tupSOtherDirectionOne)[0]
                    if type(newValTupTileTemp[0]) in [TileTemplate,Tile]:
                        outputNbrhd = (newValTupTileTemp[0].parent)._getNeighborhoodForJoin(1, Direction.South, toTileTemplateCs,newValTupTileTemp[0])
                        if outputNbrhd.glueAnnotation is not None:
                            if toTileTemplateCs.parent.name in outputNbrhd.glueAnnotation:
                                pass
                            else:
                                outputNbrhd.glueAnnotation += "-" + toTileTemplateCs.parent.name
                                
                            if outputNbrhd != toTileTemplateCs.outputNeighborhood(Direction.South):
                                if toTileTemplateCs.parent.name in toTileTemplateCs.outputNeighborhood(Direction.South).glueAnnotation:
                                    pass
                                else:
                                    toTileTemplateCs.outputNeighborhood(Direction.South).glueAnnotation += "-" + toTileTemplateCs.parent.name
                                
                if tupSOtherDirectionTwo in tileSetTemplate.tileTempToPortDict.keys():
                    newValTupTileTemp = tileSetTemplate.tileTempToPortDict.get(tupSOtherDirectionTwo)[0]
                    if type(newValTupTileTemp[0]) in [TileTemplate,Tile]:
                        outputNbrhd = (newValTupTileTemp[0].parent)._getNeighborhoodForJoin(2, Direction.South, toTileTemplateCs,newValTupTileTemp[0])
                        if outputNbrhd.glueAnnotation is not None:
                            if toTileTemplateCs.parent.name in outputNbrhd.glueAnnotation:
                                pass
                            else:
                                outputNbrhd.glueAnnotation += "-" + toTileTemplateCs.parent.name   
                        
                        if outputNbrhd != toTileTemplateCs.outputNeighborhood(Direction.South):
                                if toTileTemplateCs.parent.name in toTileTemplateCs.outputNeighborhood(Direction.South).glueAnnotation:
                                    pass
                                else:
                                    toTileTemplateCs.outputNeighborhood(Direction.South).glueAnnotation += "-" + toTileTemplateCs.parent.name
                                 
                
                
                
                
                
            
            for inputMultisignal in chooserSet.inputMultisignalType():
                tileTemplates = chooserSet.chooseTileTemplates(inputMultisignal)
                for tileTemplate in tileTemplates:
                    tilesFromTileTemplate = tileTemplate.createTilesFromInputMultisignal(inputMultisignal)
                    tiles.extend(tilesFromTileTemplate)
                    if tileTemplate.numInputSides() == 0:
                        tileTemplatesWithoutInputs.add(tileTemplate)
        
        # Handle tiles with no inputs, which are typically Tiles wrapped in TileTemplates        
        emptyMs = Multisignal(())
        
#         for tileTemplateWithoutInput in self.tilesWithoutInputs:
        for tileTemplateWithoutInput in tileTemplatesWithoutInputs:
            tilesFromTileTemplate = tileTemplateWithoutInput.createTilesFromInputMultisignal(emptyMs)
            tiles.extend(tilesFromTileTemplate)

        return [tile for tile in tiles if tile is not None]
    

        
        
        
        
        
        
        
       

#The Multisignal passed within a Port must be singular and have only one value
class Port(object):
    def __init__(self, name):
        self.name = name
        self.outputDirection = None
        self.inputDirection = None
        self.parent = None
        self.outputJoins = []
        self.inputJoins = []
        self.inputObjectDict = {}
        self.outputObjectDict = {}
        
    def __repr__(self):
        return self.name 
    
    def clone(self):
        newName = self.name 
        newOutputDirection = self.outputDirection
        newInputDirection = self.inputDirection
        newInputObjectDict = dict(self.inputObjectDict)
        newOutputObjectDict = dict(self.outputObjectDict)
        
        newPort = Port(newName)
        newPort.outputDirection = newOutputDirection
        newPort.inputDirection = newInputDirection
        newPort.inputObjectDict = newInputObjectDict
        newPort.outputObjectDict = newOutputObjectDict
        
        return newPort
        
        
        
    def outputDirMultisignalTypeDict(self):
        """Return dict mapping (direction, MultisignalType), 
        of output multisignal types."""
        ret = collections.defaultdict(MultisignalType)
        for join in self.outputJoins:
            direction = join.neighborhood.direction
            if direction in ret:
                ret[direction] = ret[direction].valueUnion(join.multisignalType)
            else:
                ret[direction] = join.multisignalType

        return ret
    def inputDirMultisignalTypeDict(self):
        """Return dict mapping (direction, MultisignalType), including Nondet, 
        of input multisignal types."""
        ret = collections.defaultdict(MultisignalType)
        for join in self.inputJoins:
            direction = oppositeDirection(join.neighborhood.direction)
            if direction in ret:
                ret[direction] = ret[direction].valueUnion(join.multisignalType)
            else:
                ret[direction] = join.multisignalType
        
        return ret
    def inputNeighborhoods(self):
        retDict = {}
        for direction in (N,S,W,E):
            for join in self.inputJoins:
                if join.neighborhood.direction == oppositeDirection(direction):
                    retDict[direction] = join.neighborhood
        return retDict
    def outputNeighborhood(self, direction):
        ''' JP - Returns the neighborhood given on the output side '''
        for join in self.outputJoins:
            if join.neighborhood.direction == direction:
                return join.neighborhood
        raise ValueError('no output neighborhood in direction {0}'.format(direction))
    def inputMultisignalType(self, direction=None):
        """If direction is None or unspecified, returns multisignal type of all inputs.
        if direction is one of Direction enum values, then returns the MultisignalType
        of just that direction (including nondeterministic inputs)"""
        mst = MultisignalType(VERBOSE_SIGNALS)
        mstDict = self.inputDirMultisignalTypeDict()
        if direction is None:
            for d in mstDict.keys():
                mst = mst.nameUnion(mstDict[d])
        else:
            mst = mstDict[direction]
        return mst
    
    def isValidInputMultisignal(self, ms):
        """Indicates whether ms is a valid multisignal for this TileTemplate's total input multisignal type."""
        inputMultisignalType = self.inputMultisignalType()
        return inputMultisignalType.isValidMultisignal(ms)



#how to implement it, like distinguish it from the filler Port in the Join - just have it in the add portion of the module and set a condition for the strength?
class initiatorPort(object):
    def __init__(self, name, strength, toModule ):
        self.name = name
        self.outputDirection = None
        self.inputDirection = None
        self.parent = None
        self.outputJoins = []
        self.inputJoins = []
        self.inputObjectDict = {}
        self.outputObjectDict = {}
        self.strength = strength
        self.toModule = toModule #is this to the Module it is added to or from it
    def __repr__(self):
        return self.name 
    
    def clone(self):
        newName = self.name 
        newOutputDirection = self.outputDirection
        newInputDirection = self.inputDirection
        newInputObjectDict = dict(self.inputObjectDict)
        newOutputObjectDict = dict(self.outputObjectDict)
        newStrength = self.strength
        newToModule = self.toModule
        
        newPort = initiatorPort(newName, newStrength, newToModule)
        newPort.outputDirection = newOutputDirection
        newPort.inputDirection = newInputDirection
        newPort.inputObjectDict = newInputObjectDict
        newPort.outputObjectDict = newOutputObjectDict
  
        
        return newPort
        
    def outputDirMultisignalTypeDict(self):
        """Return dict mapping (direction, MultisignalType), 
        of output multisignal types."""
        ret = collections.defaultdict(MultisignalType)
        for join in self.outputJoins:
            direction = join.neighborhood.direction
            if direction in ret:
                ret[direction] = ret[direction].valueUnion(join.multisignalType)
            else:
                ret[direction] = join.multisignalType

        return ret
    def inputDirMultisignalTypeDict(self):
        """Return dict mapping (direction, MultisignalType), including Nondet, 
        of input multisignal types."""
        ret = collections.defaultdict(MultisignalType)
        for join in self.inputJoins:
            direction = oppositeDirection(join.neighborhood.direction)
            if direction in ret:
                ret[direction] = ret[direction].valueUnion(join.multisignalType)
            else:
                ret[direction] = join.multisignalType
        
        return ret
    def inputNeighborhoods(self):
        retDict = {}
        for direction in (N,S,W,E):
            for join in self.inputJoins:
                if join.neighborhood.direction == oppositeDirection(direction):
                    retDict[direction] = join.neighborhood
        return retDict
    
    def outputNeighborhood(self, direction):
        ''' JP - Returns the neighborhood given on the output side '''
        for join in self.outputJoins:
            if join.neighborhood.direction == direction:
                return join.neighborhood
        raise ValueError('no output neighborhood in direction {0}'.format(direction))
    def inputMultisignalType(self, direction=None):
        """If direction is None or unspecified, returns multisignal type of all inputs.
        if direction is one of Direction enum values, then returns the MultisignalType
        of just that direction (including nondeterministic inputs)"""
        mst = MultisignalType(VERBOSE_SIGNALS)
        mstDict = self.inputDirMultisignalTypeDict()
        if direction is None:
            for d in mstDict.keys():
                mst = mst.nameUnion(mstDict[d])
        else:
            mst = mstDict[direction]
        return mst
    
    def isValidInputMultisignal(self, ms):
        """Indicates whether ms is a valid multisignal for this TileTemplate's total input multisignal type."""
        inputMultisignalType = self.inputMultisignalType()
        return inputMultisignalType.isValidMultisignal(ms)
    


