#
#    ngSkinTools
#    Copyright (c) 2009-2017 Viktoras Makauskas.
#    All rights reserved.
#    
#    Get more information at 
#        http://www.ngskintools.com
#    
#    --------------------------------------------------------------------------
#
#    The coded instructions, statements, computer programs, and/or related
#    material (collectively the "Data") in these files are subject to the terms 
#    and conditions defined by EULA.
#         
#    A copy of EULA can be found in file 'LICENSE.txt', which is part 
#    of this source code package.
#    

from maya import cmds
from ngSkinTools.log import getLogger


log = getLogger("events")

class Signal:
    '''
    Signal class collects observers, interested in some particular event,and handles
    signaling them all when some event occurs. Both handling and signaling happens outside
    of signal's own code
    '''

    all = []

    def __init__(self,name):
        if name is None:
            raise Exception("need name for debug purposes later")
        self.name = name
        self.reset()
        Signal.all.append(self)
        
    def reset(self):
        self.handlers = []
        self.executing = False
        
    
    def emitDeferred(self,*args):
        import maya.utils as mu
        mu.executeDeferred(self.emit,*args)
        
        
    def emit(self,*args):
        if self.executing:
            raise Exception,'Nested emit on %s detected' % self.name
        
        log.info("Emit %s (%d handlers)",self.name,len(self.handlers) )
        self.executing = True
        try:
            for i in self.handlers[:]:
                try:
                    #log.info('running handler `{0}` for signal {1}'.format(repr(i),self.name))
                    i(*args)
                except Exception,err:
                    import ngSkinTools
                    if ngSkinTools.DEBUG_MODE:
                        import sys
                        import traceback;traceback.print_exc(file=sys.__stderr__)
        finally:
            #log.info("Emit finished in %s (%d handlers)", self.name, len(self.handlers))
            self.executing = False
            

    class UiBoundHandler:
        '''
        Proxy wrapper for event handlers that has a method to deactivate 
        itself after when associated UI is deleted
        '''
        def __init__(self,handler,ownerUI,deactivateHandler):
            scriptJobs.scriptJob(uiDeleted=[ownerUI,self.deactivate])
            self.handler=handler
            self.deactivateHandler=deactivateHandler
        
        def deactivate(self):
            self.deactivateHandler(self)

        def __repr__(self):
            return "UI Handler for "+repr(self.handler)
            
            
        def __call__(self):
            self.handler()
            
            
    def addHandler(self,handler,ownerUI=None):
        if (ownerUI!=None):
            handler=self.UiBoundHandler(handler,ownerUI,self.removeHandler)
            
        self.handlers.append(handler)

    def removeHandler(self,handler):
        # if handler was wrapped, try finding the wrapper first
        for i in self.handlers:
            if isinstance(i, self.UiBoundHandler) and i.handler==handler:
                handler = i
                
        try:
            self.handlers.remove(handler)
        except ValueError:
            # not found in list? no biggie.
            pass
        



class LayerEventsHost:
    """
    layer system related events
    """
    
    def __init__(self):
        self.nameChanged = Signal('layerNameChanged')
        self.layerListModified = Signal('layerDataModified')
        self.currentLayerChanged = Signal('currentLayerChanged')
        self.currentInfluenceChanged = Signal('currentInfluenceChanged')
        self.layerSelectionChanged = Signal('layerSelectionChanged')
        self.layerListUIUpdated = Signal('layerListUIUpdated')
        self.layerAvailabilityChanged = Signal('layerAvailabilityChanged')
        self.influenceListChanged = Signal('influenceListChanged')

        self.mirrorConfigurationChanged= Signal('mirrorConfigurationChanged')
        
class MayaEventsHost:
    '''
    global maya-specific events
    '''
    def __init__(self):
        self.nodeSelectionChanged = Signal('nodeSelectionChanged')
        self.undoRedoExecuted = Signal('undoRedoExecuted')
        self.toolChanged = Signal('toolChanged')
        self.quitApplication = Signal('quitApplication')
        
    def registerScriptJob(self,jobName,handler):
        scriptJobs.scriptJob(e=[jobName,handler])
        

            
    def registerScriptJobs(self):
        self.registerScriptJob('SelectionChanged',self.nodeSelectionChanged.emit)
        self.registerScriptJob('Undo',self.undoRedoExecuted.emit)
        self.registerScriptJob('Redo',self.undoRedoExecuted.emit)
        self.registerScriptJob('ToolChanged',self.toolChanged.emit)        
        self.registerScriptJob('quitApplication',self.quitApplication.emit)    
        
    
    


def restartEvents():
    '''
    removes all handlers from all events (usually just testing/reset purposes)
    '''

    for s in Signal.all:
        s.reset()


class ScriptJobHost:
    def __init__(self):
        self.scriptJobs = []
        
    def scriptJob(self,*args,**kwargs):
        '''
        a proxy on top of cmds.scriptJob for scriptJob creation;
        will register a script job in a global created script jobs list
        '''
        job = cmds.scriptJob(*args,**kwargs)
        self.scriptJobs.append(job)
    
    def deregisterScriptJobs(self):
        for i in self.scriptJobs:
            try:
                cmds.scriptJob(kill=i)
            except:
                # should be no issue if we cannot kill the job anymore (e.g., killing from the
                # import traceback; traceback.print_exc()
                pass
        self.scriptJobs = []
        
scriptJobs = ScriptJobHost()

MayaEvents = MayaEventsHost()
LayerEvents = LayerEventsHost() 
