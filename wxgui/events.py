#
# File created during the fall of 2010 (northern hemisphere) by Fabien Tricoire
# fabien.tricoire@univie.ac.at
#
import wx.lib.newevent

# stylesheet update: whenever a repaint is needed due to stylesheet modification
styleSheetUpdateEventType = wx.NewEventType()
EVT_STYLESHEET_UPDATE = wx.PyEventBinder(styleSheetUpdateEventType, 1)
class StyleSheetUpdateEvent(wx.PyCommandEvent):
    def __init__(self, eventType, id):
        wx.PyCommandEvent.__init__(self, eventType, id)
# post an event to signal an update of the style sheet
# this should be called from outside e.g. events.postStyleSheetUpdateEvent(self)
def postStyleSheetUpdateEvent(object):
    event = StyleSheetUpdateEvent(styleSheetUpdateEventType, object.GetId())
    object.GetEventHandler().ProcessEvent(event)

# style update: whenever a refresh of the style edit tools is required
styleUpdateEventType = wx.NewEventType()
EVT_STYLE_UPDATE = wx.PyEventBinder(styleUpdateEventType, 1)
class StyleUpdateEvent(wx.PyCommandEvent):
    def __init__(self, eventType, id):
        wx.PyCommandEvent.__init__(self, eventType, id)
# post an event to signal an update of the style
def postStyleUpdateEvent(object):
    event = StyleUpdateEvent(styleUpdateEventType, object.GetId())
    object.GetEventHandler().ProcessEvent(event)

# quit event: when the user wants to quit
quitEventType = wx.NewEventType()
EVT_QUIT = wx.PyEventBinder(quitEventType, 1)
class QuitEvent(wx.PyCommandEvent):
    def __init__(self, eventType, id):
        wx.PyCommandEvent.__init__(self, eventType, id)
def postQuitEvent(object):
    event = QuitEvent(quitEventType, object.GetId())
    object.GetEventHandler().ProcessEvent(event)

# load data event: when the user wants to load data in a new frame
# position is the position of the VrpFrame initiating data loading
# this is useful since we want to avoid completely hiding this previous VrpFrame
loadDataEventType = wx.NewEventType()
EVT_LOAD_DATA = wx.PyEventBinder(loadDataEventType, 1)
class LoadDataEvent(wx.PyCommandEvent):
    def __init__(self, object, eventType,
                 vrpData, solutionData, styleSheet, position):
        wx.PyCommandEvent.__init__(self, eventType, object.GetId())
        self.vrpData = vrpData
        self.solutionData = solutionData
        self.styleSheet = styleSheet
        self.position = position
def postLoadDataEvent(object, vrpData, solutionData, styleSheet, position):
    event = LoadDataEvent(object, loadDataEventType,
                          vrpData, solutionData, styleSheet, position)
    object.GetEventHandler().ProcessEvent(event)
    
# frame registration event: VrpFrame objects send that so that they are
# registered in the WxApp object
registerFrameEventType = wx.NewEventType()
EVT_REGISTER_FRAME = wx.PyEventBinder(registerFrameEventType, 1)
class RegisterFrameEvent(wx.PyCommandEvent):
    def __init__(self, eventType, object):
        wx.PyCommandEvent.__init__(self, eventType, object.GetId())
        self.EventObject = object
def postRegisterFrameEvent(object):
    event = RegisterFrameEvent(registerFrameEventType, object)
    object.GetEventHandler().ProcessEvent(event)
# frame unregistration event: VrpFrame objects send that so that they are
# unregistered from the WxApp object (when they are closed)
unregisterFrameEventType = wx.NewEventType()
EVT_UNREGISTER_FRAME = wx.PyEventBinder(unregisterFrameEventType, 1)
class UnregisterFrameEvent(wx.PyCommandEvent):
    def __init__(self, eventType, object):
        wx.PyCommandEvent.__init__(self, eventType, object.GetId())
        self.EventObject = object
def postUnregisterFrameEvent(object):
    event = UnregisterFrameEvent(unregisterFrameEventType, object)
    object.GetEventHandler().ProcessEvent(event)
    
# session load/save events: when the user wants to load or save the session
saveSessionEventType = wx.NewEventType()
loadSessionEventType = wx.NewEventType()
EVT_SAVE_SESSION = wx.PyEventBinder(saveSessionEventType, 1)
EVT_LOAD_SESSION = wx.PyEventBinder(loadSessionEventType, 1)
class saveSessionEvent(wx.PyCommandEvent):
    def __init__(self, eventType, id):
        wx.PyCommandEvent.__init__(self, eventType, id)
class loadSessionEvent(wx.PyCommandEvent):
    def __init__(self, eventType, id):
        wx.PyCommandEvent.__init__(self, eventType, id)
def postSaveSessionEvent(object):
    event = saveSessionEvent(saveSessionEventType, object.GetId())
    object.GetEventHandler().ProcessEvent(event)
def postLoadSessionEvent(object):
    event = loadSessionEvent(loadSessionEventType, object.GetId())
    object.GetEventHandler().ProcessEvent(event)

# preferences event: signal that the user wants to modify preferences
preferencesEventType = wx.NewEventType()
EVT_PREFERENCES = wx.PyEventBinder(preferencesEventType, 1)
class PreferencesEvent(wx.PyCommandEvent):
    def __init__(self, eventType, object):
        wx.PyCommandEvent.__init__(self, eventType, object.GetId())
        self.EventObject = object
def postPreferencesEvent(object):
    event = PreferencesEvent(preferencesEventType, object)
    object.GetEventHandler().ProcessEvent(event)

# solution delete event: signal that the user wants to remove a solution
deleteSolutionEventType = wx.NewEventType()
EVT_DELETE_SOLUTION = wx.PyEventBinder(deleteSolutionEventType, 1)
class DeleteSolutionEvent(wx.PyCommandEvent):
    def __init__(self, eventType, object):
        wx.PyCommandEvent.__init__(self, eventType, object.GetId())
        self.EventObject = object
def postDeleteSolutionEvent(object):
    event = DeleteSolutionEvent(deleteSolutionEventType, object)
    object.GetEventHandler().ProcessEvent(event)
