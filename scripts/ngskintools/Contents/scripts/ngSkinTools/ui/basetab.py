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

import maya.cmds as cmds
from ngSkinTools.ui.options import Options
from ngSkinTools.ui.constants import Constants
from ngSkinTools.ui.uiWrappers import FormLayout
from ngSkinTools.log import getLogger
from ngSkinTools.ui import uiWrappers
from ngSkinTools.ui.components import titledRow


class Controls:
    pass


class ActionCommandWrapper:
    def __init__(self,action):
        self.action=action
    def __call__(self,*args):
        self.action.execute()
        
class CommandLayout:
    def __init__(self,helpLink,commandIterator):
        from ngSkinTools.ui.actions import BaseAction
        
        self.buttons = []
        self.outerLayout = FormLayout()
        self.helpButton = BaseTab.createHelpButton(helpLink)
        scrollLayout = BaseTab.createScrollLayout(self.outerLayout)
        self.innerLayout = cmds.columnLayout(adjustableColumn=1)        
        
        self.buttonForm = FormLayout(parent=self.outerLayout,numberOfDivisions=100,height=Constants.BUTTON_HEIGHT)
        for name,command,annotation in commandIterator:
            button = cmds.button(label=name,height=Constants.BUTTON_HEIGHT)
            if isinstance(command, BaseAction):
                cmds.button(button,e=True,command=ActionCommandWrapper(command))
                command.addUpdateControl(button)
            else:
                def anyArgs(command):
                    return lambda *args: command()
                cmds.button(button,e=True,command=anyArgs(command))
                
            if annotation is not None:
                cmds.button(button,e=True,annotation=annotation)
            self.buttons.append(button)
            
        BaseTab.layoutButtonForm(self.buttonForm, self.buttons)
        
        self.outerLayout.attachForm(scrollLayout, 0, 0, None, 0)
        self.outerLayout.attachForm(self.buttonForm,None,Constants.MARGIN_SPACING_HORIZONTAL,Constants.MARGIN_SPACING_VERTICAL,None)
        self.outerLayout.attachControl(scrollLayout, self.buttonForm, None, None, 5, None)
        self.outerLayout.attachControl(self.buttonForm, self.helpButton, None, None, None, Constants.MARGIN_SPACING_HORIZONTAL)
        self.outerLayout.attachForm(self.helpButton,None,None,Constants.MARGIN_SPACING_VERTICAL,Constants.MARGIN_SPACING_HORIZONTAL)



class BaseTab(object):
    '''
    base class for ui group (tab) classes
    '''
    
    
    
    VAR_GROUP_COLLAPSE = 'ngSkinTools_group%s_collapse'
    
    log = getLogger("BaseToolWindow")
    


    def __init__(self):
        # create container for all controls.
        # using fake class instead of dictionary to simplify usage code
        self.controls = Controls()
        self.controls.groups = []
        self.parentWindow = None
        
        self.title = 'Untitled'
        
    def getTitle(self):
        '''
            return title of this gui set. 
            override for functionality
        '''
        return self.title
    
    def setTitle(self,title):
        self.title = title


    def getGroupVariable(self,group):
        title= cmds.frameLayout(group,q=True,label=True)
        title = title.replace(" ", "")
        return self.VAR_GROUP_COLLAPSE % title

    @staticmethod
    def createScrollLayout(parent):
        return  cmds.scrollLayout(parent=parent,childResizable=True)
    
 
    def createUIGroup(self,layout,title,defaultCollapsed=False):
        '''
        creates collapsable UI group
        '''
        cmds.setParent(layout)
        
        group = uiWrappers.frameLayout(label=title, marginWidth=Constants.MARGIN_SPACING_HORIZONTAL,marginHeight=Constants.MARGIN_SPACING_VERTICAL, collapsable=True,
                                 expandCommand=self.saveOptions,collapseCommand=self.saveOptions)
        self.lastCreatedGroup = group
        
        self.controls.groups.append(group)
        cmds.frameLayout(group,e=True,collapse = Options.loadOption(self.getGroupVariable(group), 1 if defaultCollapsed else 0))
        return cmds.columnLayout(adjustableColumn=1,rowSpacing=Constants.MARGIN_SPACING_VERTICAL)

    def createUI(self,parent):
        '''
        override this method to implement gui creation
        '''
        cmds.setParent(parent);
        self.baseLayout = cmds.columnLayout(rowSpacing=Constants.MARGIN_SPACING_VERTICAL,adjustableColumn=1)
        
    def saveOptions(self,*args):
        '''
        save gui options for this tab. this can be directly supplied as a handler to control's "change value" events
        '''
        for group in self.controls.groups:
            Options.saveOption(self.getGroupVariable(group), cmds.frameLayout(group,q=True,collapse = True))
        
    @staticmethod
    def createHelpButton(helpLink):
        import os.path as path
        
        imageName = path.join(path.dirname(__file__),'images','help.png')
        
        return cmds.symbolButton('?',image=imageName,height=Constants.BUTTON_HEIGHT,width=Constants.BUTTON_WIDTH_SMALL,
                                          annotation='Open manual at: '+helpLink.title,
                                          command=lambda *args:helpLink.open())        
    

    @staticmethod
    def createTitledRow(parent,title,innerContentConstructor=None,adjustable=True):
        return titledRow.create(parent, title,innerContentConstructor=innerContentConstructor,adjustable=adjustable)

    @staticmethod    
    def createFixedTitledRow(parent,title):
        return titledRow.createFixed(parent, title)
        
    @staticmethod
    def layoutButtonForm(buttonForm,buttons):
        '''
        horizontally spaces buttons in a form with a grid size of 100
        '''
        for index,button in enumerate(buttons):
            spaceWidth = 100/len(buttons)
            cmds.formLayout(buttonForm,e=True,
                            attachForm=[(button,'top',0),(button,'bottom',0)],
                            attachPosition=[(button,'right',Constants.MARGIN_SPACING_HORIZONTAL/2,spaceWidth*(index+1)),
                                            (button,'left',Constants.MARGIN_SPACING_HORIZONTAL/2,spaceWidth*index)]
                            )
            
        
    def createCommandLayout(self,commandIterator,helpLink):
        '''
        creates a layout that has a help button and command buttons at the bottom of the page, with a scroll layout created for the rest of the page;
        inside scroll layout, column layout is created for adding rows of interface
        
        
        commandIterator should be an iterator or a list of tuples with:
            * button label
            * button handler - either BaseAction action, or an executable object
        '''
        
        return CommandLayout(helpLink, commandIterator)
        

        

