# -*- coding: utf-8 -*-
# SkinWeights command and component editor
# Copyright (C) 2018 Trevor van Hoof
# Website: http://www.trevorius.com
#
# pyqt attribute sliders
# Copyright (C) 2018 Daniele Niero
# Website: http://danieleniero.com/
#
# neighbour finding algorythm
# Copyright (C) 2018 Jan Pijpers
# Website: http://www.janpijpers.com/
#
# skinningTools and UI
# Copyright (C) 2018 Perry Leijten
# Website: http://www.perryleijten.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# See http://www.gnu.org/licenses/gpl.html for a copy of the GNU General
# Public License.
#--------------------------------------------------------------------------------------

__VERSION__ = "20200528.4.0.10"
AUTHOR = "Perry Leijten"

import os, re, functools, webbrowser, cPickle, logging, cStringIO, platform, zipfile, sys, types, shutil
from maya  import cmds, mel, OpenMayaUI, OpenMaya
import xml.etree.ElementTree as xml 

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin, MayaQDockWidget

from qtUtil import *
sys.path.append(os.path.dirname(WORKDIRECTORY))

from skinningTools                         import SkinningTools
from SmoothBrush.globalskinsmooth          import GlobalSkinSmoothBrush
from ControlSlider.skinningtoolssliderlist import SkinningToolsSliderList
from ControlSlider.vertexinfluenceeditor   import VertexInfluenceEditor
from vertexWeightMatcher                   import SkinWeightsWidget, VertexSelectionWidget
from WeightsManagerUI                      import WeightsManager
from SkinWeightsEditor                     import main
from skinBinder                            import SkinBinder
from colorButton                           import QColorButton
from remapper                              import JointRemapper, MeshRemapper
from toolTip                               import toolTipMovie
import createProxyMesh, holdFetch, weightPaintUtils, skeletonGeo
import languageSupport, polySelectionUtils, fallofCurveUI

# load plugin dynammically so users don't have to place everything in seperate folders
pluginSuffix = ".bundle"
if platform.system() == "Windows":
    pluginSuffix = ".mll"

mayaVersion = str(cmds.about(apiVersion=True))[:-2]
if "maya" in sys.executable and platform.system() == "Windows":
    mayaVersion = sys.executable.split("Maya")[-1].split(os.sep)[0]
elif platform.system() != "Windows":
    mayaVersion = cmds.about(version=1)

pluginPath = os.path.normpath("%s/plugin/x64/%sx64/SkinCommands%s"%(os.path.dirname( __file__ ), mayaVersion, pluginSuffix ))
try:
    cmds.loadPlugin( pluginPath, qt=True )
except:
    raise Exception, "Can't find the plugin, make sure it's installed! or that you have a plugin for your version of Maya!: "+mayaVersion + " Plugin path: "+ pluginPath

def softSelection():
    '''function using the api to gather information from the soft selection tool'''
    # https://groups.google.com/forum/?fromgroups=#!topic/python_inside_maya/q1JlddKybyM
    selection     = OpenMaya.MSelectionList()
    softSelection = OpenMaya.MRichSelection()
    OpenMaya.MGlobal.getRichSelection(softSelection)
    softSelection.getSelection(selection)
    
    dagPath = OpenMaya.MDagPath()
    component = OpenMaya.MObject()
    
    iter = OpenMaya.MItSelectionList( selection,OpenMaya.MFn.kMeshVertComponent )
    elements, weights = [], []
    while not iter.isDone(): 
        iter.getDagPath( dagPath, component )
        dagPath.pop() #Grab the parent of the shape node
        node = dagPath.fullPathName()
        fnComp = OpenMaya.MFnSingleIndexedComponent( component )   
        getWeight = lambda i: fnComp.weight( i ).influence() if fnComp.hasWeights() else 1.0
        
        for i in range( fnComp.elementCount() ):
            elements.append( '%s.vtx[%i]' % ( node, fnComp.element( i ) ) )
            weights.append( getWeight( i ) ) 
        iter.next()
        
    return elements, weights


weightdirectory = os.path.join(WORKDIRECTORY, "weights")
Ui_MainWindow, Ui_BaseClass = loadUiType( '%s/SkinningToolsUI.ui'%WORKDIRECTORY )
class SkinningToolsUI(MayaQWidgetDockableMixin, Ui_MainWindow, Ui_BaseClass):
    skinPercentValue = 0.5
    
    def __init__(self, parent=None):
        self.__selecttionPref = cmds.selectPref(q=1, tso=True)
        cmds.selectPref(tso=True)
        super(SkinningToolsUI, self).__init__(parent)
        self.setupUi(self)
        
        cmds.undoInfo( state = True )

        with open( QT_STYLESHEET, "r" ) as fh:
            self.setStyleSheet( fh.read() )

        self._timer = QTimer()
        self._timer.timeout.connect(self.displayToolTip)
        self.curentWidgetAtMouse = None
        self.toolTipWindow = None

        self.__liveJob      = ''
        self.__liveCompJob  = ''
        self.__lineEditList = []
        self.__sliderList   = SkinningToolsSliderList()
        self.skinTool       = SkinningTools()
        self.weightManager  = WeightsManager()
        self.skinBinder     = SkinBinder()
        self.jntRemap       = JointRemapper()
        self.meshRemap      = MeshRemapper()
        self.fcUI           = fallofCurveUI.BezierGraph()
        self.visualiserNode = None
        self.borderIter     = 0
        self.ToolisBusy     = False
        self.origVerts      = None
        self.settings       = QSettings("uiSave","Skintool")
        self.getBoneUnderMouse     = False
        self.borderSelectionBase   = None
        self.storedSkinInformation = None

        self.fcUI.setBaseSize(230, 270)
        self.fcUI.setMinimumWidth(230)
        self.fcUI.setMaximumWidth(230)
        self.fcUI.setMinimumHeight(270)
                
        # ui-building
        self.copyReset()
        self.__addMayaToolsToWindow()
        self.__iconManagement()
        self.skintabWidget.currentChanged.connect(self.tabchanged)
        self.skintabWidget.setCurrentIndex(0)
        self.LiveButton.setCheckable(True)

        self._addContextMenus()
        self._buttonManagement() 
        self.addEXtraMenuOptions()

        # add component editor to ui
        self.componentEdit = main.SkinWeightsEditor()
        self.componentLayout.addWidget(self.componentEdit)
        
        # weightsManager 
        self.ExportWeights_Button.clicked.connect(self.writeSkinBinaryFile)
        self.ImportWeights_Button.clicked.connect(self.readBinaryFile)
        self.WorldPos_radioButton.toggled.connect(self.weightManagerToggleSwitch)
        self.UvPos_radioButton.toggled.connect(self.weightManagerToggleSwitch)
        self.DeleteWeights_Button.clicked.connect(self.__deleteXmlFile)
        self.__readOutFiles()

        # vertex match attachment
        self.vertMWid = VertexSelectionWidget()
        self.sublayoutVT1.addWidget(self.vertMWid)
        self.sublayoutVT2.setSpacing(0)
        self.sublayoutVT2.setContentsMargins(0,0,0,0)
        self.skinweightWidget = SkinWeightsWidget()
        self.skinweightWidget.addLoadingBar( self.tool_progressBar )
        self.sublayoutVT2.addWidget( self.skinweightWidget )

        # event filter attachment
        mainWin, qt_active_view = self.cleanEventFilter()
        mainWin.installEventFilter( self )
        qt_active_view.installEventFilter( self )

        # utilitys
        self.createDockWidgets()
        self.attachCollorButtons()
        # self.connectQt2Node()
        self.colorAttachLayout.addStretch(1)
        
        # tab functions
        self.skintabWidget.setCurrentIndex( 0 )
        self.skintabWidget.setTabEnabled (4, False)
        self.skintabWidget.tabBar().setTabTextColor(4, QColor("red"))
        
        # extra connections beta Tab
        self.addColorButton.clicked.connect( functools.partial(self.skinBinder.addColorControls, self.colorAttachLayout) ) 
        self.analyseSelectionButton.clicked.connect( self.AnalyseMeshColors ) 
        self.hardSkinButton.clicked.connect( self.applyHardSurfaceSkin ) 
        self.softSkinButton.clicked.connect( self.applySoftSurfaceSkin ) 
        self.cleanSkbSceneBtn.clicked.connect(self.cleanSkbScene)

        # preferences
        getState = self.settings.value("windowState")
        if getState != None:        
            if QT_VERSION != "pyqt4":
                self.baseDockWidget.restoreState(getState)
                self.baseDockWidget.restoreGeometry(self.settings.value("geometry"))
            else:        
                self.baseDockWidget.restoreState(getState.toByteArray())
                self.baseDockWidget.restoreGeometry(self.settings.value("geometry").toByteArray())
        
        if QT_VERSION == "pyqt4":
            getLan = self.settings.value("uiLanguage").toString()
        else:
            getLan = str(self.settings.value("uiLanguage"))
        
        if getLan == None or str(getLan) == '':        
            languageSupport.changeLanguage(self, "english")
        else:
            header = languageSupport.changeLanguage(self, str(getLan))
            self.changeLN.setText(header)

        self.recursive_setMouseTracking(self, True)

        # remove beta tab as maya 2020 does not support the rendering:
        self.skintabWidget.removeTab(4)


    def updateItems(self):
        self.fcUI.updateView()

    def changeUILanguage(self):
        if self.sender().text() == "[EN]":
            header = languageSupport.changeLanguage(self, "japanese")
            self.sender().setText(header)
            self.settings.setValue("uiLanguage", "japanese")
        elif self.sender().text() == "[JPN]":
            header = languageSupport.changeLanguage(self, "english")
            self.sender().setText(header)
            self.settings.setValue("uiLanguage", "english")

    def on_context_menu(self, buttonObj, popMenu, point, *args):
        popMenu.exec_(buttonObj.mapToGlobal(point))      

    def add_contextToMenu( self, actionNames,checked, *args ):
        popMenu = QMenu(self)
        allFunctions = []
        for actionName in actionNames:
            check = QAction(actionName, self)
            check.setCheckable(True)
            check.setChecked(checked)
            popMenu.addAction(check)
            allFunctions.append(check)
        
        return allFunctions, popMenu   
    
    def widgets_at(self, pos):
        widgets = []
        widget_at = qApp.widgetAt(pos)
        return widget_at

    def recursive_setMouseTracking(self, parent, flag):
        if hasattr(parent, "mouseMoveEvent"):        
            parent.setMouseTracking(flag)
            parent.__mouseMoveEvent = parent.mouseMoveEvent
            parent.mouseMoveEvent = functools.partial(self.childMouseMoveEvent, parent)

        for child in parent.children():
            self.recursive_setMouseTracking(child, flag)

    def _mouseTracking(self, event):
        if QT_VERSION == "pyside2":
            point = QPoint(event.screenPos().x(), event.screenPos().y())
        else:
            point = QPoint(event.globalPos().x(), event.globalPos().y())
        curWidget = self.widgets_at(point)
        
        if curWidget == None and self.toolTipWindow != None:
            self.toolTipWindow.deleteLater()
            self.toolTipWindow = None
            self._timer.stop()

        if self.curentWidgetAtMouse != curWidget:
            if self.toolTipWindow != None:
                self.toolTipWindow.deleteLater()
                self.toolTipWindow = None
                self._timer.stop()

            if not isinstance(curWidget, QPushButton):
                if self.toolTipWindow != None:
                    self.toolTipWindow.deleteLater()
                self.curentWidgetAtMouse = None
                self._timer.stop()
                return

            self.curentWidgetAtMouse = curWidget
            self._timer.start(700)

    def displayToolTip(self):
        self._timer.stop()
        if self.curentWidgetAtMouse == None or self.tooltipAction.isChecked()== False:
            return
        tip =  self.curentWidgetAtMouse.whatsThis()

        size = 250
        if QDesktopWidget().screenGeometry().height() > 1080:
            size *=1.5
        rct = QRect(QCursor.pos().x()+20, QCursor.pos().y()-(40+size), size, size)
        if (self.window().pos().y() + (self.height()/2)) > QCursor.pos().y():
            rct = QRect(QCursor.pos().x()+20, QCursor.pos().y()+20, size, size)

        self.toolTipWindow = toolTipMovie(rct)
        if not self.toolTipWindow.toolTipExists(tip):
            return 
        self.toolTipWindow.setLanguage(str(self.settings.value("uiLanguage")), tip)
        self.toolTipWindow.setGifImage(tip)
        self.toolTipWindow.show()

    def childMouseMoveEvent(self, child, event):
        self._mouseTracking(event)
        return child.__mouseMoveEvent(event)
        
    def mouseMoveEvent(self, event):
        self._mouseTracking(event)
        super( SkinningToolsUI, self ).mouseMoveEvent( event )

    def __iconManagement(self):
        ''' attach correct items to buttons, QT designer has problems doing this dynamically '''
        def applyPNGIcon(qtObject, qtConnection, iconName, ToolTip = ''):
            qtObject.clicked.connect(qtConnection)
            buttonIcon = QIcon("%s/Icon/%s.png"%(os.path.dirname(__file__), iconName))
            qtObject.setIcon(buttonIcon)
            qtObject.setWhatsThis(ToolTip)

        def applyMayaIcon(qtObject, qtConnection, iconName, ToolTip = ''):
            qtObject.clicked.connect(qtConnection)
            buttonIcon = QIcon(":/%s"%(iconName))
            qtObject.setIcon(buttonIcon)
            qtObject.setWhatsThis(ToolTip)
        
        applyPNGIcon( self.AvarageWeightButton,      self.avarageVertex,           "AvarageVerts",    "average" )
        applyPNGIcon( self.Cop2MultVert,             self.copy2MultVertex,         "copy2Mult",       "copy" )
        applyPNGIcon( self.Bone2BoneSwitchButton,    self.bone2BoneSwitch,         "Bone2Boneswitch", "boneSwitch" )
        applyPNGIcon( self.Copy2BoneButton,          self.copy2Bone,               "Bone2Bone",       "boneMove" )
        applyPNGIcon( self.ShowInfluencedButton,     self.showInfluencedVerts,     "bone2verts",      "vertSelect" )
        applyPNGIcon( self.switchVertexWeightButton, self.switchVertexWeight,      "vert2vert",       "switch" )
        applyPNGIcon( self.jointLabelButton,         self.autoLabelJoints,         "jointLabel",      "label" )
        applyPNGIcon( self.deleteBoneButton,         self.deleteBoneInfluence,     "BoneDelete",      "delBone" )
        applyPNGIcon( self.selectInflJoints,         self.selectInfluencingJoints, "selectinfl",      "selInf" )
        applyPNGIcon( self.unifyJointsButton,        self.unifyjoints,             "unify",           "unify" )
        applyPNGIcon( self.SmoothButton,             self.neighbourAverage,        "smooth" ,         "smooth")
        applyPNGIcon( self.transfermayaskinbutton,   self.transferMayaskin,        "skinToSkin",      "copySkin")
        applyPNGIcon( self.TransferPoseButton,       self.transferMayapose,        "skinToPose",      "copyPose")
        applyPNGIcon( self.addinflbutton,            self.addinfluences,           "add",             "add" )
        applyMayaIcon( self.brushButton,             self.brushOptions,            "brush.svg",       "smoothBrush")

    def _buttonManagement(self):
        ''' attach processes to buttons''' 
        def connectClicked(button, attachment, ToolTip = ''):
            button.clicked.connect(attachment)
            button.setWhatsThis(ToolTip)

        connectClicked( self.ReloadButton,             self.addVertexSliders )
        connectClicked( self.LiveButton,               self.vertexSlidersAutoUpdate )
        connectClicked( self.resetButton,              self.copyReset )
        connectClicked( self.targetButton,             self.target )
        connectClicked( self.sourceButton,             self.source )
        connectClicked( self.copyButton,               self.execCopySourceTarget )
        connectClicked( self.maxInfluencesButton,      self.setMaxJointInfluences, "maxInf" )
        connectClicked( self.showInflButton,           self.getVertOverMaxInfluence , "showMaxInf")
        connectClicked( self.transferSkinButton,       self.transferSkin )
        connectClicked( self.resetJoints,              self.resetJointsinCluster, "resetPose" )
        connectClicked( self.outButton,                self.smoothOutsideSelection, "neighbors")
        connectClicked( self.inAndOutButton,           self.smoothInOutsideSelection, "neighborsPlus")
        connectClicked( self.storeInnerSelectionButton,self.storeInnerSelection)
        connectClicked( self.GrowBorderButton,         self.growBorderSelection)
        connectClicked( self.ShrinkBorderButton,       self.shrinkBorderSelection)
        connectClicked( self.SeperateSkin,             self.seperateSkinnedObjectByShell , "seperate")
        connectClicked( self.keepSelectedInf,          self.keepOnlySelectedInf , "onlySel")
        connectClicked( self.convertToJointButton,     self.convertSelectionToJoint, "convertToJoint")
        # connectClicked( self.skVisualiserButton,       self.AttachVisualiser )
        connectClicked( self.skBindSkinButton,         self.VisualToSkin )
        connectClicked( self.freezeJointButton,        self.freezeSkinnedJoints, "freezeJoint" )
        connectClicked( self.unifyByShellButton,       self.unifybyShells, "shellUnify" )
        connectClicked( self.saveSkinclusterButton,    self.storeSkinCluster )
        connectClicked( self.loadSkinclusterButton,    self.loadSkincluster )
        connectClicked( self.copyVertexWeightButton,   self.copyVertexSkin )
        connectClicked( self.pasteVertexWeightButton,  self.pasteVertexSkin )
        connectClicked( self.getinfluencedMeshes,      self.getmeshesInfluenced, "infMesh" )

    def addEXtraMenuOptions(self):
        # extra options
        self.extraMenu   = QMenu('Extra', self)
        self.holdAction  = QAction("hold Model", self)
        self.holdAction.triggered.connect(self._holdModel)
        self.fetchAction = QAction("fetch Model", self)
        self.fetchAction.triggered.connect(self._fetchModel)
        self.objSkeletonAction = QAction("skeleton -> obj", self)
        self.objSkeletonAction.triggered.connect(self._convertSkel)
        # self.betaAction  = QAction("unlock beta Tab", self)
        # self.betaAction.triggered.connect(self._unlockBetaAcces)
        # self.betaAction.setCheckable(True)
        undockAction = QAction("make tools floatable", self)
        undockAction.setCheckable(True)
        undockAction.triggered.connect(self.dockFloatable)

        self.extraMenu.addAction(self.holdAction)
        self.extraMenu.addAction(self.fetchAction)
        self.extraMenu.addSeparator()
        self.extraMenu.addAction(undockAction)
        self.extraMenu.addSeparator()
        self.extraMenu.addAction(self.objSkeletonAction)
        # self.extraMenu.addSeparator()
        # self.extraMenu.addAction(self.betaAction)

        # help options (helpname adressed because of osx, osx doesnt like to deal with qmenubars and icons)
        helpName = "help"
        if platform.system() == "Windows":
            helpName = ''

        helpAction = QMenu(helpName, self)
        buttonIcon = QIcon("%s/Icon/%s.png"%(os.path.dirname(__file__), "help"))
        helpAction.setIcon(buttonIcon)
        helpAction.setStatusTip('help Functions')

        docAction = QAction("Docs", self)
        helpAction.addAction(docAction)
        docAction.triggered.connect(self.__openHelp)
        self.tooltipAction = QAction("Enhanced ToolTip", self)
        self.tooltipAction.setCheckable(True)
        helpAction.addAction(self.tooltipAction)

        self.menubar.addMenu( helpAction )
        self.menubar.addMenu(self.extraMenu)

        self.changeLN = QAction("[EN]", self)
        self.changeLN.triggered.connect(self.changeUILanguage)
        self.menubar.addAction( self.changeLN )

    def dockFloatable(self):
        isChecked = self.sender().isChecked()
        dockList = [self.dock, self.dock1, self.dock2, self.dock3, self.dock4]
        if isChecked:
            for dock in dockList:
                dock.setFeatures(QDockWidget.AllDockWidgetFeatures)
        else:
            for dock in dockList:
                dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable )

    def cleanEventFilter(self):
        # joint MarkingMenu filter
        mainWin         = wrapinstance(long( OpenMayaUI.MQtUtil.mainWindow() ),QMainWindow)
        active_view     = OpenMayaUI.M3dView.active3dView()
        active_view_ptr = active_view.widget()
        qt_active_view  = wrapinstance(long( active_view_ptr ),QObject)
        
        try:
            mainWin.removeEventFilter(self)
            qt_active_view.removeEventFilter(self)
        except:
            pass
        return mainWin, qt_active_view

    def _addContextMenus(self):
        ''' add extra options to some of the commands '''
        self.AvarageWeightButton.setContextMenuPolicy(Qt.CustomContextMenu)
        self.onDistanceAverageCheck, self.popMenu1 = self.add_contextToMenu(["on distance"], True)
        self.AvarageWeightButton.customContextMenuRequested.connect(functools.partial( self.on_context_menu, self.AvarageWeightButton, self.popMenu1))

        self.Cop2MultVert.setContextMenuPolicy(Qt.CustomContextMenu)
        self.onCop2MultVertCheck, self.popMenu5 = self.add_contextToMenu(["2nd selection"], False)
        self.Cop2MultVert.customContextMenuRequested.connect(functools.partial( self.on_context_menu, self.Cop2MultVert, self.popMenu5))

        self.transfermayaskinbutton.setContextMenuPolicy(Qt.CustomContextMenu)
        self.TransferPoseButton.setContextMenuPolicy(Qt.CustomContextMenu)
        self.smoothTransferCheck, self.popMenu2 = self.add_contextToMenu(["one to one", "UV"], False)
        self.transfermayaskinbutton.customContextMenuRequested.connect(functools.partial( self.on_context_menu, self.transfermayaskinbutton,  self.popMenu2))
        self.TransferPoseButton.customContextMenuRequested.connect(functools.partial( self.on_context_menu, self.TransferPoseButton,  self.popMenu2))

        self.inAndOutButton.setContextMenuPolicy(Qt.CustomContextMenu)
        self.growingCheck, self.popMenu3 = self.add_contextToMenu(["Growing Selection"], False)
        self.inAndOutButton.customContextMenuRequested.connect(functools.partial( self.on_context_menu, self.inAndOutButton, self.popMenu3))

        self.deleteBoneButton.setContextMenuPolicy(Qt.CustomContextMenu)
        self.deleteBonesCheck, self.popMenu4 = self.add_contextToMenu(["fast Conversion"], True)
        self.deleteBoneButton.customContextMenuRequested.connect(functools.partial( self.on_context_menu, self.deleteBoneButton, self.popMenu4))

        self.freezeJointButton.setContextMenuPolicy(Qt.CustomContextMenu)
        self.freezeJointCheck, self.popMenu7 = self.add_contextToMenu(["freeze Hierarchy"], True)
        self.freezeJointButton.customContextMenuRequested.connect(functools.partial( self.on_context_menu, self.freezeJointButton, self.popMenu7))

    def createDockWidgets(self):
        '''some functionality to make sure that panels within the widget are re-arrangable'''
        self.baseDockWidget = QMainWindow(self)
        self.baseDockWidget.setDockOptions(QMainWindow.AnimatedDocks | QMainWindow.AllowNestedDocks)
        self.verticalLayout_FrameDockLayout.addWidget(self.baseDockWidget)

        self.dock4 = QDockWidget("Smoothing Graph", self.baseDockWidget)
        self.dock4.setObjectName('docking_05')
        self.dock4.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable )
        self.dock4.setWidget(self.fcUI)
        self.baseDockWidget.addDockWidget(Qt.RightDockWidgetArea, self.dock4)
        
        self.dock = QDockWidget("Maya Tools", self.baseDockWidget)
        self.dock.setObjectName('docking_01')
        # self.dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable )
        self.dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable )
        self.dock.setWidget(self.mayaToolsGB)
        self.baseDockWidget.addDockWidget(Qt.RightDockWidgetArea, self.dock)

        self.dock1 = QDockWidget("Vertex and Bone Functions", self.baseDockWidget)
        self.dock1.setObjectName('docking_02')
        # self.dock1.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)
        self.dock1.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable )
        self.dock1.setWidget(self.vertexBoneFuncGB)
        self.baseDockWidget.addDockWidget(Qt.LeftDockWidgetArea, self.dock1)

        self.dock2 = QDockWidget("copy/Transfer by Range", self.baseDockWidget)
        self.dock2.setObjectName('docking_03')
        # self.dock2.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)
        self.dock2.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable )
        self.dock2.setWidget(self.copyTransRangeGB)
        self.baseDockWidget.addDockWidget(Qt.RightDockWidgetArea, self.dock2)

        self.dock3 = QDockWidget("Match Vertex Weights", self.baseDockWidget)
        self.dock3.setObjectName('docking_04')
        # self.dock3.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)
        self.dock3.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable )
        self.dock3.setWidget(self.vertexMatchGB)
        self.baseDockWidget.addDockWidget(Qt.BottomDockWidgetArea, self.dock3)


    def changeCompEdCells(self):
        '''give user the ability to swap component editor cell types, current available: spinbox, slider'''
        self.__componentEditorController.setCellType( self.cellTypeBox.currentText() )
        self.__componentEditorController.update()

    def _holdModel(self):
        ''' store a clean version of selected objects '''
        holdFetch.hold(True)

    def _fetchModel(self):
        ''' grabe stored obects and load them in the scene ''' 
        holdFetch.fetch()

    def _convertSkel(self):
        skeletonGeo.showUI()

    # def _unlockBetaAcces(self):
        #@TODO: leave option untill fully integrated
        #@TODO: look at plugin -> fix for maya 2015 or remove functionality entirely for 2015 and older
        # if self.sender().isChecked():
            
        #     result = cmds.confirmDialog( 
        #             title='trying to open Beta Tab', 
        #             message='the beta tab is not propperly tested and contains functions that might break rigs/scenes\nif you would like to check it out be carefull!\nif you might have ideas on how to expand the features found here please email me: perryleijten@gmail.com\n\nDo you want to continue?',
        #             button=['Yes','No'], defaultButton='Yes', 
        #             cancelButton='No', dismissString='No' )

        #     if result == 'Yes':
        #         self.skintabWidget.setTabEnabled (4, True)
        #         self.skintabWidget.tabBar().setTabTextColor(4, QColor("green"))
        #     else:
        #         self.sender().setChecked(False)
        #         self.skintabWidget.tabBar().setTabTextColor(4, QColor("red"))
        # else:
        #     self.skintabWidget.setTabEnabled (4, False)
        #     self.skintabWidget.tabBar().setTabTextColor(4, QColor("red"))

    def __lineEdit_FalseFolderCharacters(self, inLineEdit):
        ''' ckeck if string works for windows files/folders'''
        return re.search(r'[\\/:<>"]', inLineEdit) or re.search(r'[*?|]', inLineEdit) or re.match(r'[0-9]', inLineEdit)

    def __readOutFiles(self,*args):
        self.listWidget.clear()
        if os.path.exists(weightdirectory):
            listing = os.listdir(weightdirectory)
            self.listWidget.addItems(listing)

    def __deleteXmlFile(self, *args):    
        selectedItem = self.listWidget.selectedItems()
        if selectedItem != None and selectedItem != []:
            os.remove(r"%s/%s"%(weightdirectory, str(selectedItem[0].text()) ) )
        self.__readOutFiles()

    def _exportWeightsOptions(self, fileName, default = True ):
        selection = cmds.ls(sl=True, type="transform")
        if len(selection) == 0:
            polygons = cmds.ls(type = "mesh", l=True)
            for i in polygons:
                mesh = cmds.listRelatives(i, parent=True)
                if mesh in selection:
                    continue
                selection.extend(mesh)
        
        if default:
            if not os.path.exists(weightdirectory):
                os.makedirs(weightdirectory)
            return list(set(selection)), os.path.join(weightdirectory, fileName)
        else: 
            getFILEPATH = cmds.fileDialog2(fileFilter="*.zip", fm=0, dir = os.path.dirname(cmds.file(q=True, sn=True)))
            return list(set(selection)), getFILEPATH[0]

    def writeSkinBinaryFile(self):
        ''' read out all information from selected objectsand store as a dictionary '''
        if not os.path.exists(weightdirectory):
            os.makedirs(weightdirectory)
        
        Controller_name_text = self.SkinFilename_LineEdit.displayText()
        if self.__lineEdit_FalseFolderCharacters(Controller_name_text) != None or Controller_name_text == '':
            fileName = ''
        else:
            fileName = "%s.zip"%Controller_name_text

        default = True
        if fileName=='':
            default = False

        selected, zipFileDir = self._exportWeightsOptions(fileName, default=default)
        
        zf = zipfile.ZipFile(zipFileDir, 'w', zipfile.ZIP_DEFLATED)
        try:
            for object in selected:
                xml = self.weightManager.writeSkinBinary(object, weightdirectory, self.tool_progressBar)
                if xml == None:
                    continue   
                zf.write(xml, os.path.basename(xml))
                os.remove(xml)
        finally:
            zf.close()
        
        self.__readOutFiles()
    
    def weightManagerToggleSwitch(self, *args):
        if self.sender() == self.WorldPos_radioButton:
            self.UvPos_radioButton.setChecked(False)
        else:
            self.WorldPos_radioButton.setChecked(False)

    def applySkinWeightsManagerWeights(self, inObjects, xmlStringFile, amount = None, useUv = None, progressBar = None):
        ''' use xml file to determine weight info on current objects'''
        def CalcPosition(vec1, vec2):
            return (OpenMaya.MVector(vec1[0], vec1[1], vec1[2]) - OpenMaya.MVector(vec1[0], vec1[1], vec1[2])).length()

        if progressBar == None:
            progressBar = self.tool_progressBar
        
        progressBar.setValue(0)
        qApp.processEvents()

        vertexNumber = self.weightManager._getVertexInfoFromXML(xmlStringFile)
        vertPos = self.weightManager._getVertexPosInfoFromXML(xmlStringFile)

        remapWeights = True              
        if cmds.polyEvaluate(inObjects[0], v=1) == vertexNumber:
            self.weightManager.setWeightsByVertexId(inObjects, xmlStringFile, progressBar)
            remapWeights = False
                
        if remapWeights:                
            if useUv == True and cmds.polyEvaluate(inObjects[0], uv=1) > 0 :
                self.weightManager.setWeigthsByUv(inObjects, xmlStringFile, amount, progressBar)
            else:
                self.weightManager.setWeightsByPosition(inObjects, xmlStringFile, amount, progressBar)
        
        os.remove(xmlStringFile)

    def readBinaryFile(self, *args):
        ''' parse selected zip file '''
        amount = self.amountSpinBox.value()
        useUv = self.UvPos_radioButton.isChecked()
        
        hasSelection = False
        shapeSelection = []
        selection = cmds.ls(sl=1)
        if selection != None and len(selection) > 0:
            hasSelection = True
            for selected in selection:
                shapes = cmds.listRelatives(selected, s=1)
                if shapes != None and len(shapes) > 0:
                    shapeSelection.append(str(shapes[0]))
        else:
            shapeSelection = cmds.ls(type="mesh", ni=1)            

        allShapes = cmds.ls(type="mesh", ni=1)
        selectedItem = self.listWidget.selectedItems()
        if selectedItem == None or selectedItem == []:
            currentZipFile = cmds.fileDialog2(fileFilter="*.zip", fm=1, dir = os.path.dirname(cmds.file(q=True, sn=True)))
            if currentZipFile == None:
                cmds.error("no file selected!")
                return
            elif type(currentZipFile) == types.ListType or type(currentZipFile) == types.TupleType:    
                currentZipFile = currentZipFile[0]
        else:    
            currentZipFile = os.path.join(weightdirectory , str(selectedItem[0].text()))
        
        zf = zipfile.ZipFile( currentZipFile, mode='r' )
        toRemap = []
        for file in zf.namelist():

            zipDirectory = os.path.join(WORKDIRECTORY, "weight", file)
            if not os.path.exists( zipDirectory ):
                os.makedirs( zipDirectory )
            xmlStringFile = zf.extract( file, zipDirectory )

            shapeName = self.weightManager._getShapeInfoFromXML(xmlStringFile)
            if hasSelection == True and not shapeName in shapeSelection:
                toRemap.append([shapeName, xmlStringFile])
                self.weightManager.clearXmlData()
                continue
            
            if not cmds.objExists(shapeName):
                toRemap.append([shapeName, xmlStringFile])
                self.weightManager.clearXmlData()
                continue
            
            parent = cmds.listRelatives(shapeName, p=1)[0]
            self.applySkinWeightsManagerWeights([parent], xmlStringFile, amount, useUv)
            self.weightManager.clearXmlData()
            if hasSelection == True:
                shapeSelection.remove(shapeName)
            allShapes.remove(shapeName)

            # if os.path.isfile( zipDirectory ):
            #     os.unlink( zipDirectory )
            #     os.remove( zipDirectory )
        zf.close()
        shutil.rmtree(os.path.join(WORKDIRECTORY, "weight"))
        if len(allShapes) == 0:
            return

        if len(shapeSelection) == 0:
            return

        toConnect = allShapes
        if hasSelection == True:
            toConnect = shapeSelection
        
        rShapes = []
        xmlDict = {}
        for remap in toRemap:
            rShapes.append(remap[0])
            bbinfo = self.weightManager._getBBInfoFromXML(remap[1])
            xmlDict[remap[0]] = remap[1]
            self.weightManager.clearXmlData()

        self.meshRemap.setData(xmlDict, amount, useUv, self.tool_progressBar)
        self.meshRemap.relinkMeshdata(rShapes, toConnect, self.applySkinWeightsManagerWeights)
                
    def __openHelp(self):
        '''pdf help document that can will be openend in default program otherwise with webbrowser, assuming webbrowser has pdf plugin'''
        
        ln = "EN"
        if QT_VERSION == "pyqt4" and (self.settings.value("uiLanguage").toString() == "japanese"):
            ln = "JPN"
        elif str(self.settings.value("uiLanguage")) == "japanese":
            ln = "JPN"

        fileToOpen = os.path.join(os.path.dirname(__file__), "Help/SkinningTools_%s.pdf"%ln)
        try:
            os.startfile( r'file:%s'%fileToOpen )  
        except:
            try:
                cmds.warning("could not open Pdf file, trying through webrowser!")
                webbrowser.open_new( r'file:%s'%fileToOpen )  
            except Exception, e:
                cmds.warning(e)

    def boneUnderMouse(self):
        def selectFromScreenApi(x, y, x_rect=None, y_rect=None):
            # find object under mouse, (silently select the object using api and clear selection)
            sel = OpenMaya.MSelectionList()
            OpenMaya.MGlobal.getActiveSelectionList(sel)
            
            args = [x, y]
            if x_rect!=None and y_rect!=None:
                OpenMaya.MGlobal.selectFromScreen(x, y, x_rect, y_rect, OpenMaya.MGlobal.kReplaceList)
            else:
                OpenMaya.MGlobal.selectFromScreen(x, y, OpenMaya.MGlobal.kReplaceList)
            objects = OpenMaya.MSelectionList()
            OpenMaya.MGlobal.getActiveSelectionList(objects)
            
            OpenMaya.MGlobal.setActiveSelectionList(sel, OpenMaya.MGlobal.kReplaceList)
            
            fromScreen = []
            objects.getSelectionStrings(fromScreen)
            return fromScreen

        def getSelectionModeIcons():
            # fix if anything other then object selection is used
            if cmds.selectMode(q=1, object=1):
                selectmode = "object"
            elif cmds.selectMode(q=1, component=1):
                selectmode = "component"
            elif cmds.selectMode(q=1, hierarchical=1):
                selectmode = "hierarchical"
            return selectmode
        
        active_view = OpenMayaUI.M3dView.active3dView()
        pos = QCursor.pos()
        widget = qApp.widgetAt(pos)
        
        try:
            relpos = widget.mapFromGlobal(pos)
        except:
            return False

        margin = 4
        maskOn = cmds.selectType( q=True, joint=True )
        sm = getSelectionModeIcons()    
        mel.eval("changeSelectMode -object;")
        cmds.selectType( joint=True )
        foundObjects = selectFromScreenApi( relpos.x()-margin, 
                                            active_view.portHeight() - relpos.y()-margin, 
                                            relpos.x()+margin, 
                                            active_view.portHeight() - relpos.y()+margin )
        cmds.selectType( joint=maskOn )
        mel.eval("changeSelectMode -%s;"%sm)

        foundBone = False
        boneName = ''
        for fobj in foundObjects:
            if cmds.objectType(fobj) == "joint":
                foundBone = True
                boneName = fobj
                break
        return foundBone, boneName

    def eventFilter(self, obj, event):
        '''middle mouse event to apply skin weight values through a custom marking menu'''
        def cleanupContext():
            if cmds.popupMenu("ContextModModule", exists=True):
                cmds.deleteUI("ContextModModule")

        if event.type() == QEvent.KeyPress:
            keyType = event.key()
            if keyType == Qt.Key_Up:
                pickwalk = weightPaintUtils.pickWalkSkinClusterInfluenceList("up")
                if pickwalk == True:
                    return True

            elif keyType == Qt.Key_Down:
                pickwalk = weightPaintUtils.pickWalkSkinClusterInfluenceList("down")
                if pickwalk == True:
                    return True

        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.AltModifier:
            self.getBoneUnderMouse = False
            return False

        if self.getBoneUnderMouse == False:
            cleanupContext()

        if event.type() == QEvent.MouseButtonPress and event.button() == 4:
            selectionForMM = cmds.ls(sl=True,fl=True)
            if len(selectionForMM) == 0:
                return False
            inObject = selectionForMM[0]

            self.getBoneUnderMouse, boneName  =  self.boneUnderMouse()
            if self.getBoneUnderMouse == False:
                return False

            SkinningTools.doCorrectSelectionVisualization(inObject) 
            
            if len(selectionForMM) == 0:
                return False 
            
            if "." in inObject:
                inObject = selectionForMM[0].split('.')[0]
            else:
                return False 
            
            if SkinningTools.skinCluster(inObject, True) == None:
                return False 

            cmds.popupMenu("ContextModModule", alt=False, ctl=False, button=2,mm=True,p="viewPanes", pmc=functools.partial( self.getItem, boneName ))
            
        if event.type() == QEvent.MouseButtonRelease and event.button() == 4: 
            self.getBoneUnderMouse = False
            
        return False
        
    def valueMenu(self, inputVal = None, *args):
        ''' seperate def for the ability to change the value increment of the marking menu'''
        SkinningToolsUI.skinPercentValue = inputVal

    def valueAddition(self, inputVal = None, *args):
        SkinningToolsUI.skinPercentValue += inputVal    
            
    def getItem(self, jntName, *args):
        ''' find the bone wo work with if all conditions are met and create the marking menu'''

        hitFound      = cmds.dagObjectHit(mn= "ContextModModule")
        popUpChildren = cmds.popupMenu("ContextModModule", q=True, itemArray=True)
        if popUpChildren != None and len(popUpChildren) > 0:
            cmds.popupMenu("ContextModModule",e =True, deleteAllItems=True)
            self.__skinMarkingMenu( jntName, inItems = popUpChildren )
            return

    def __skinMarkingMenu(self, inObject, inItems=None, *args):
        ''' marking menu functionality '''
        selectedObjects = cmds.ls(sl=True,fl=True)
        if not selectedObjects:
            return
        mesh        = selectedObjects[0].split('.')[0]
        skincluster = SkinningTools.skinCluster(mesh, True)
        
        try:
            cmds.deleteUI(inItems)
        except:
            pass
        cmds.menuItem( l = inObject, p = "ContextModModule",  rp = "N", en = False )
        cmds.menuItem( l="set weight: 0",  p = "ContextModModule", rp="W",   c = functools.partial( self.applySkinValues, 0.0, selectedObjects, skincluster, inObject, 4 , mesh ) )
        cmds.menuItem( l="set weight: 1",  p = "ContextModModule", rp="E",   c = functools.partial( self.applySkinValues, 1.0, selectedObjects, skincluster, inObject, 0 , mesh ) )
        cmds.menuItem( l="set weight: %s"%SkinningToolsUI.skinPercentValue,  p = "ContextModModule", rp="SE", c = functools.partial( self.applySkinValues, SkinningToolsUI.skinPercentValue, selectedObjects, skincluster, inObject, 1 , mesh ) )
        cmds.menuItem( l="Add Value %s"%SkinningToolsUI.skinPercentValue,    p = "ContextModModule", rp="NE", c = functools.partial( self.applySkinValues, SkinningToolsUI.skinPercentValue, selectedObjects, skincluster, inObject, 2 , mesh ) )
        cmds.menuItem( l="Remove Value %s"%SkinningToolsUI.skinPercentValue, p = "ContextModModule", rp="NW", c = functools.partial( self.applySkinValues, -(SkinningToolsUI.skinPercentValue), selectedObjects, skincluster, inObject, 3 , mesh ) )
        if cmds.softSelect( q=True, softSelectEnabled=True) == 1:
            softSelectionMode = cmds.softSelect(q=True, softSelectFalloff= True)
            checkboxValue = 0
            if softSelectionMode == 1:
                checkboxValue = 1
            cmds.menuItem( l="surface Aware", p = "ContextModModule", rp="SW", cb=checkboxValue, c= self.setContentAware )
        incrementMenu = cmds.menuItem( l= "increment Value Menu", sm=True,   p = "ContextModModule", rp="S" )
        for i in range(1, 10, 1):
            value = i / 10.0
            cmds.menuItem( label='%s'%value, p = incrementMenu, c = functools.partial( self.valueMenu, value ) )
        
        subMenuEMenu = cmds.menuItem( l= "add 2f values", sm=True, p = incrementMenu, rp="NE" )
        for i in range(-5, 5, 1):
            value = i / 100.0
            cmds.menuItem( label='%s'%value, p = subMenuEMenu, c = functools.partial( self.valueAddition, value ) )
        
        subMenuWMenu = cmds.menuItem( l= "add 3f values", sm=True, p = incrementMenu, rp="NW" )
        for i in range(-5, 5, 1):
            value = i / 1000.0
            cmds.menuItem( label='%s'%value, p = subMenuWMenu, c = functools.partial( self.valueAddition, value ) )

        SkinningTools.doCorrectSelectionVisualization(mesh)
        return

    def setContentAware( self, *args ):
        ''' extra functionality that works with the smooth selection modifier in maya'''
        softSelectionMode = cmds.softSelect(q=True, softSelectFalloff= True)
        if softSelectionMode > 0:
            cmds.softSelect(e=True, softSelectFalloff= 0)
        else:
            cmds.softSelect(e=True, softSelectFalloff= 1)

    def applySkinValues( self,skinValue, expandedVertices, skinCluster, inObject, operation, mesh,*args ):
        '''skin weight functions used in marking menu, currently using skinPercent (slow maya command) '''
        from skinningTool import SkinningToolsUI
        oldSelection = expandedVertices
        cmds.ConvertSelectionToVertices()
        allBones = cmds.skinCluster( mesh, q=True, influence=True )
        
        if not inObject in allBones:
            cmds.skinCluster( skinCluster, e=True, lw=False, wt = 0.0, ai= inObject )

        expandedVertices1 = self.skinTool.convertToVertexList(expandedVertices)
        # option for non soft selected which speeds it up big time
        cmds.select(expandedVertices1)
        if operation == 1:
            cmds.skinPercent( skinCluster, tv =[ inObject, skinValue ], normalize=True)
        elif operation == 4:
            cmds.skinPercent( skinCluster, tv =[ inObject, 0.0 ], normalize=True)
        elif operation == 3:
            # for loop assigning verts: little bit more costly operation but safe for removal of weight information
            for index, obj in enumerate( expandedVertices ):
                val = cmds.skinPercent( skinCluster, obj, transform = inObject, q=True, value=True )
                newVal = val +  skinValue 
                if newVal < 0.0:
                    newVal = 0.0
                cmds.skinPercent( skinCluster, obj, tv =[ inObject, newVal ], normalize=True)
        else:
            cmds.skinPercent( skinCluster, relative=True, tv =[ inObject, skinValue ], normalize=True)
                
        if cmds.softSelect( q=True, softSelectEnabled=True) == 1:
            # costly but only necessary when sof selection is used
            progressDialogue = QProgressDialog()
            # progressDialogue.setWindowModality(1)
            progressDialogue.show()
            progressDialogue.setValue(0)
            
            expandedVertices, weights = SkinningToolsUI.softSelection()
            percentage = 99.0/ len(expandedVertices)
            for index, obj in enumerate( expandedVertices ):
                if weights[index] == 1.0:
                    continue
                val = cmds.skinPercent( skinCluster, obj, transform = inObject, q=True, value=True )
                if operation == 0:
                    newVal = weights[ index ]
                elif operation == 1:
                    newVal = ( skinValue * weights[ index ] )
                elif operation == 2:
                    newVal = val + ( skinValue * weights[ index ] )
                    if newVal > 1.0:
                        newVal = 1.0
                elif operation == 3:
                    newVal = val + ( skinValue * weights[ index ] )
                    if newVal < 0.0:
                        newVal = 0.0
                else:
                    newVal = 0.0
                cmds.skinPercent( skinCluster, obj, tv =[ inObject, newVal ])
                progressDialogue.setValue(percentage * index )
                QApplication.processEvents()
            progressDialogue.setValue(100)
            progressDialogue.close()

        if ".f[" in oldSelection[0]:
            mask = "facet"
        elif ".e[" in oldSelection[0]:
            mask = "edge"
        elif ".cv[" in oldSelection[0]:
            mask = "controlVertex"
        elif ".pt[" in oldSelection[0]:
            mask = "latticePoint"
        else:
            mask = "vertex"

        mel.eval('if( !`exists doMenuComponentSelection` ) eval( "source dagMenuProc" );')
        mel.eval('doMenuComponentSelection("%s", "%s");'%(mesh, mask))

        cmds.select( oldSelection )

        #cleanup marking menu as button is pressed
        self.getBoneUnderMouse = False
        if cmds.popupMenu("ContextModModule", exists=True):
            cmds.deleteUI("ContextModModule")

    def convertVerticesToJoint(self, sel):
        expanded = self.skinTool.convertToVertexList(sel)
        cluster = cmds.cluster()[1]
        cmds.select(cl=1)
        jnt = cmds.joint(n="placeJointVID%s"%expanded[0].split("[")[-1].split("]")[0])
        pc = cmds.pointConstraint(cluster, jnt, mo=0)
        cmds.delete(pc, cluster)
        meshName = expanded[0].split(".")[0]
        skinClusterName = SkinningTools.skinCluster(meshName, True)
        self.applySkinValues(1.0, expanded, skinClusterName, jnt, 0, meshName)
        return jnt

    def convertClusterToJoint(self, sel):
        self.ToolisBusy = True
        self.tool_progressBar.setValue(0)
        QApplication.processEvents()
        shape = cmds.listRelatives(sel[0], s=1, type = "clusterHandle") or None
        
        if shape == None:
            return
        clusterDeformer =  cmds.listConnections(shape,s=1, type = "cluster")[0]
        clusterSet = cmds.listConnections( clusterDeformer, type="objectSet" )
        allConnected = self.skinTool.convertToVertexList(cmds.sets(clusterSet, q=1))
        
        cmds.select(cl=1)
        jnt = cmds.joint(n="placeJointVID%s"%allConnected[0].split("[")[-1].split("]")[0])
        pc = cmds.pointConstraint(sel[0], jnt, mo=0)
        cmds.delete(pc)

        meshes = []
        for connected in allConnected:
            name = connected.split(".")[0]
            if name in meshes:
                continue
            meshes.append(name)

        amountMeshes = len(meshes)
        for iter, mesh in enumerate(meshes):
            
            skinClusterName = SkinningTools.skinCluster(mesh, True)
            allBones = cmds.skinCluster( mesh, q=True, influence=True )
    
            if not jnt in allBones:
                cmds.skinCluster( skinClusterName, e=True, lw=False, wt = 0.0, ai= jnt )
            
            expandedVertices = self.skinTool.convertToVertexList(mesh)
            availableVertices = allConnected
            values = cmds.percent( clusterDeformer , mesh, q=1, v=1)
            
            vertPercentage = 99.0/len(expandedVertices)
            for index, vertex in enumerate(expandedVertices):
                if not vertex in availableVertices:
                    continue
                cmds.skinPercent( skinClusterName, vertex, tv =[ jnt, values[index] ])

                self.tool_progressBar.setValue(((index * vertPercentage) /amountMeshes)*(iter+1))
                QApplication.processEvents()
            cmds.delete(sel[0])  
            self.tool_progressBar.setValue(100.0)
            QApplication.processEvents()  
            self.ToolisBusy = False   

    def convertSelectionToJoint(self):
        ''' use selected components or clusters as a base to generate a joint with a skincluster '''
        sel = cmds.ls(sl=1)
        
        if self.ToolisBusy:
            cmds.warning("please wait with selection untill previous command is done!")
            return
        cmds.undoInfo(ock=1)
        try:
            objType = cmds.objectType(sel[0])
            if objType == "transform":
                self.convertClusterToJoint(sel)
            else:
                cmds.select(self.convertVerticesToJoint(sel), r=1)
        except Exception, e:
            cmds.warning(e)
        finally:
            cmds.undoInfo(cck=1)
            self.ToolisBusy = False

    def copyReset(self, *args):
        '''color managment UI'''
        self.targetLineEdit.setText("")
        self.targetLineEdit.setStyleSheet('background-color: #C23A3A;')
        self.sourceLineEdit.setText("" )
        self.sourceLineEdit.setStyleSheet('background-color: #C23A3A;')
    
    def storeVerts(self, inputVerts):
        '''data management for source and target selections'''
        Mesh        = inputVerts[0].split('.')[0]
        SkinCluster = SkinningTools.skinCluster(Mesh)

        Selection     = []
        for i in inputVerts:
            expandedVertices = self.skinTool.convertToVertexList(i)
            for vert in expandedVertices:
                if vert in Selection:
                    continue
                Selection.append(vert)
        return  Mesh, Selection, SkinCluster

    def storeSkinCluster(self, *args):
        '''Quick store skincluster information'''
        sel = cmds.ls(sl=True)
        stored = self.jntRemap.storeSkinCluster(sel)
        self.origVerts = []
        for vert in self.skinTool.convertToVertexList(sel[0]):
            self.origVerts.append(cmds.xform(vert, q=1, ws=1, t=1))

        if stored:
            self.savedSkinLineEdit.setText(sel[0])

    def loadSkincluster(self, *args):
        sel = cmds.ls(sl=True)
        loaded = self.jntRemap.loadSkincluster(sel, self.origVerts, self.tool_progressBar, 1)
        if loaded:
            self.savedSkinLineEdit.setText("")
        
    def copyVertexSkin(self, *args):
        cmds.undoInfo(ock=True)
        try:        
            sel = cmds.ls(sl=True, fl=True)
            vertAmount = len(sel)
            if vertAmount == 0:
                cmds.error("nothing selected")
            vertexes = self.skinTool.convertToVertexList(sel)
            skinClusterName = self.skinTool.skinCluster(vertexes[0].split(".")[0])
            vtxNumber = vertexes[0].split('.vtx[')[-1].split(']')[0]
            self.vertexCopied.setText(vtxNumber)
    
            self.SkinWeightCopyInfluences = cmds.skinCluster( skinClusterName, q=1 ,influence=1)
            averageList = []
            for vertex in sel:
                cmds.select( vertex, r=1 )
                averageList.append( cmds.skinPercent ( skinClusterName, q=1 ,v =1 ) )

            self.SkinWeightCopyWeights = [sum(x)/vertAmount for x in zip(*averageList)]
        except Exception, e:
            cmds.warning(e)
        finally:
            cmds.undoInfo(cck=True)

    def pasteVertexSkin(self, *args):
        cmds.undoInfo(ock=True)
        try:
            sel = cmds.ls(sl=True, fl=True)
            if len(sel) == 0:
                cmds.error("nothing selected")
            vertexes = self.skinTool.convertToVertexList(sel)
    
            skinClusterName = self.skinTool.skinCluster(vertexes[0].split(".")[0])
    
            cmds.select( vertexes, r=1 )
    
            command = cStringIO.StringIO()
            command.write('cmds.skinPercent("%s", transformValue=['%(skinClusterName))
    
            for count, skinJoint in enumerate( self.SkinWeightCopyInfluences ):
                command.write('("%s", %s)'%(skinJoint, self.SkinWeightCopyWeights[count]))
                if not count == len(self.SkinWeightCopyInfluences)-1:
                     command.write(', ')
            command.write('], normalize=False, zeroRemainingInfluences=True)')
    
            eval(command.getvalue())
        except Exception, e:
            cmds.warning(e)
        finally:
            self.vertexCopied.setText("")
            cmds.undoInfo(cck=True)
    
    def target (self,*arg):
        ''' target selection information '''
        targetVerts = self.skinTool.convertToVertexList(cmds.ls(sl=True,fl=True))
        
        targetMesh, self.TargetSelection, self.TargetSkinCluster = self.storeVerts(targetVerts)
        self.targetLineEdit.setText(targetMesh )
        self.targetLineEdit.setStyleSheet('background-color: #17D206;')
        
        cmds.select(self.TargetSelection)
    
    def source (self,*arg):
        ''' source selection information '''
        sourceVerts = self.skinTool.convertToVertexList(cmds.ls(sl=True,fl=True))
        
        sourceMesh, self.SourceSelection, self.SourceSkinCluster = self.storeVerts(sourceVerts)
        self.sourceLineEdit.setText(sourceMesh )
        self.sourceLineEdit.setStyleSheet('background-color: #17D206;')
        
        cmds.select(self.SourceSelection)     
    
    def execCopySourceTarget(self,*args):
        if self.sourceLineEdit.text == "" or self.targetLineEdit.text =="":
            cmds.warning('source or target selection is not defined!')
            return

        self.skinTool.execCopySourceTarget(
            TargetSkinCluster = self.TargetSkinCluster, 
            SourceSkinCluster = self.SourceSkinCluster, 
            TargetSelection = self.TargetSelection, 
            SourceSelection = self.SourceSelection, 
            smoothValue = self.closestspinBox.value(),
            progressBar = self.tool_progressBar)
        self.copyReset()

    def getVertOverMaxInfluence(self, *args):
        selection = cmds.ls(sl=True)[0]
        vertOver  = self.skinTool.getVertOverMaxInfluence(
            singleObject = selection,
            MaxInfluenceValue = self.maxInfluencesTextEdit.value(), 
            notSelect = False, 
            progressBar = self.tool_progressBar)
        SkinningTools.doCorrectSelectionVisualization(selection)
        cmds.select(vertOver)

    def setMaxJointInfluences(self, *args):
        selection = cmds.ls(sl=True)
        self.skinTool.setMaxJointInfluences(
            objects = selection,
            MaxInfluenceValue = self.maxInfluencesTextEdit.value(), 
            progressBar = self.tool_progressBar)        

    def autoLabelJoints(self):
        MayaWindowPtr = wrapinstance( long( OpenMayaUI.MQtUtil.mainWindow() ) )
        
        inputDialog = DetailsDialog("lableSearch", MayaWindowPtr)
        inputDialog.exec_()
        self.skinTool.autoLabelJoints( inputDialog.l_lineEdit.text(), inputDialog.r_lineEdit.text(), progressBar = self.tool_progressBar )

    def avarageVertex(self):
        selected = cmds.ls(os=True, fl=True)
        useDistance = self.onDistanceAverageCheck[0].isChecked()
        self.skinTool.AvarageVertex(selected, useDistance, self.fcUI, self.tool_progressBar)
        cmds.repeatLast(ac='python("from maya import cmds;from skinningTool.skinningTools import SkinningTools;SkinningTools().AvarageVertex(cmds.ls(os=True, fl=True), %s, %s)")'%(useDistance, self.fcUI.curveAsPoints()))
    
    def copy2MultVertex(self):
        selection     = cmds.ls(os=True,fl=True)
        useSecondSelection = self.onCop2MultVertCheck[0].isChecked()
        self.skinTool.Copy2MultVertex(selection, useSecondSelection)
        cmds.repeatLast(ac='python("from maya import cmds;from skinningTool.skinningTools import SkinningTools;SkinningTools().Copy2MultVertex(cmds.ls(os=True,fl=True), %s)")'%useSecondSelection )
    
    def neighbourAverage(self):
        selected = cmds.ls(sl=True, fl=True)
        self.skinTool.neighbourAverage(selected)
        cmds.repeatLast( ac = 'python("from maya import cmds;from skinningTool.skinningTools import SkinningTools;selected = cmds.ls(sl=True, fl=True);SkinningTools().neighbourAverage(selected)")' )
    
    def brushOptions(self):
        stackTrace = mel.eval("stackTrace -q -state;")
        if stackTrace == 1:
            mel.eval("stackTrace -state 0")
        brush = GlobalSkinSmoothBrush()
        if stackTrace == 1:
            mel.eval("stackTrace -state 1")
        cmds.repeatLast( ac = 'python("from maya import cmds;from skinningTool.SmoothBrush import globalskinsmooth;brush = globalskinsmooth.GlobalSkinSmoothBrush()")' )
            
    def bone2BoneSwitch(self):
        selection = cmds.ls(sl=True)
        if not len(selection) == 3 :
            cmds.warning('not enough or to much Objects selected!')
            return

        bone1 = selection[ 0 ]
        bone2 = selection[ 1 ]
        skin  = selection[ 2 ]
        self.skinTool.BoneSwitch(bone1, bone2, skin)
        cmds.repeatLast( ac = 'python("from maya import cmds;from skinningTool.skinningTools import SkinningTools;selected = cmds.ls(sl=True);SkinningTools().BoneSwitch(selected[0], selected[1], selected[2])")' )
    
    def copy2Bone(self):
        selection = cmds.ls(sl=True)
        if not len(selection) == 3 :
            cmds.warning('not enough or to much Objects selected!')
            return

        bone1 = selection[ 0 ]
        bone2 = selection[ 1 ]
        skin  = selection[ 2 ]
        self.skinTool.BoneMove(bone1, bone2, skin)
        cmds.repeatLast( ac = 'python("from maya import cmds;from skinningTool.skinningTools import SkinningTools;selected = cmds.ls(sl=True);SkinningTools().BoneMove(selected[0], selected[1], selected[2])")' )
    
    def showInfluencedVerts(self):
        selectionMesh = cmds.ls( sl = True, type = "transform" )
        selectionJoint = cmds.ls( sl = True, type = "joint" )
        skinMesh = [ x for x in selectionMesh if x not in selectionJoint ];
        
        influencingVerts = self.skinTool.ShowInfluencedVerts( skinMesh[ 0 ], selectionJoint, self.tool_progressBar)
        cmds.select(influencingVerts, r=1)

        cmds.repeatLast( ac = '''python("from maya import cmds;from skinningTool.skinningTools import SkinningTools;meshes = cmds.ls(sl=True, type='transform');joints = cmds.ls(sl=True, type='joint'); skinMesh = [x for x in meshes if x not in joints]; cmds.select(SkinningTools().ShowInfluencedVerts(skinMesh[0], joints), r=1);")''' )
        
    def switchVertexWeight(self):
        selection     = cmds.ls( sl = True, flatten = True )
        sizeSelection = len( selection )
        if not sizeSelection == 2:
            cmds.warning( 'amount of selected vertices must be 2' )
            return

        vertex1 = selection[ 0 ]
        vertex2 = selection[ 1 ]
        self.skinTool.switchVertexWeight( vertex1, vertex2 )
        cmds.repeatLast( ac = 'python("from maya import cmds;from skinningTool.skinningTools import SkinningTools;verts = cmds.ls(sl=True, fl=1);SkinningTools().switchVertexWeight(verts[0],verts[1])")' )

    def deleteBindPoses(self):
        self.skinTool.removeBindPoses()

    def unifyjoints(self):
        selection = cmds.ls(sl=True)
        self.skinTool.comparejointInfluences(selection)  
        cmds.repeatLast( ac = 'python("from maya import cmds;from skinningTool.skinningTools import SkinningTools;SkinningTools().comparejointInfluences(cmds.ls(sl=True))")' )
    
    def unifybyShells(self, *args):
        selection = cmds.ls(sl=1 )
        cmds.select(self.skinTool.hardSkinSelectionShells(selection, self.tool_progressBar), r=1)

    def labelCheck(self):
        from random import randint
        jnts = cmds.ls(type = "joint")
        jntAmount = len( jnts )
        if cmds.getAttr( jnts[ randint( 0, jntAmount -1) ] + '.type' ) == 0: 
            result = cmds.confirmDialog( 
                title='no labels found', 
                message='would you like to add joint lables?\nthis will give better results!',
                button=['Yes','No'], defaultButton='Yes', 
                cancelButton='No', dismissString='No' )

            if result == 'Yes':
                self.autoLabelJoints()

    def transferMayaskin(self):
        selection = cmds.ls( sl = True, type = "transform" )
        base  = selection[0]
        other = selection[1:]

        self.labelCheck()
    
        nonSmooth =  self.smoothTransferCheck[0].isChecked()
        uvSpace = self.smoothTransferCheck[1].isChecked()
        
        self.skinTool.transferSkinning( base, other, inPlace=False, sAs = nonSmooth, uvSpace = uvSpace )  

        cmds.repeatLast( ac = 'python("from maya import cmds;from skinningTool.skinningTools import SkinningTools;SkinningTools().transferSkinning(cmds.ls(sl=True)[0], cmds.ls(sl=True)[1:], False, %s, %s) ")'%(nonSmooth, uvSpace ))

    def transferMayapose(self):
        selection = cmds.ls( sl = True, type = "transform" )
        base  = selection[ 0 ]
        other = selection[ 1: ]

        self.labelCheck()

        nonSmooth =  self.smoothTransferCheck[0].isChecked()
        uvSpace = self.smoothTransferCheck[1].isChecked()
        
        self.skinTool.transferSkinning(base, other, inPlace=True, sAs = nonSmooth, uvSpace = uvSpace)  
        cmds.repeatLast(ac='python("from maya import cmds;from skinningTool.skinningTools import SkinningTools;SkinningTools().transferSkinning(cmds.ls(sl=True)[0], cmds.ls(sl=True)[1:], True, %s, %s) ")'%(nonSmooth, uvSpace) )

    def seperateSkinnedObjectByShell(self):
        selection = cmds.ls( sl = True, type = "transform" )
        
        self.labelCheck()

        result = cmds.confirmDialog( 
                title='opration not undo-able', 
                message='would you like to continue?',
                button=['Yes','No'], defaultButton='Yes', 
                cancelButton='No', dismissString='No' )

        if result == 'Yes':
            self.skinTool.seperateSkinnedObject( selection, self.tool_progressBar) 

    def extractskinnedFaces(self):
        self.labelCheck()
        selection = cmds.ls( sl = True, fl=True )
        cmds.select(self.skinTool.extractSkinnedShells(selection) , r=1)

    def transferSkin(self):
        selection = cmds.ls(sl=True)
        self.skinTool.transferClosestSkinning( selection, self.closestspinBox.value(), self.tool_progressBar )        
    
    def selectInfluencingJoints(self):
        cmds.select(self.skinTool.getInfluencingjoints(cmds.ls(sl=True, type = "transform")[0]), r=1)
        cmds.repeatLast(ac='python("from maya import cmds;from skinningTool.skinningTools import SkinningTools;cmds.select(SkinningTools().getInfluencingjoints(cmds.ls(sl=True, type = "transform")[0]), r=1)")')

    def addinfluences(self):
        skins = cmds.ls(sl =True, type = "transform")
        joints = cmds.ls(sl =True, type = "joint")

        for skin in skins:
            if cmds.objectType(skin) == "joint":
                continue
            self.skinTool.addUnlockedZeroInfl(joints, skin)
        cmds.repeatLast(ac='''python("from maya import cmds;from skinningTool.skinningTools import SkinningTools;meshes = cmds.ls(sl=True, type='transform');joints = cmds.ls(sl=True, type='joint'); skinMesh = [x for x in meshes if x not in joints]; SkinningTools().addUnlockedZeroInfl(joints, skinMesh[0]);")''')

    def resetJointsinCluster(self):
        if self.selectalljointsCheck.isChecked():
            self.skinTool.resetSkinnedJoints( cmds.ls( type="joint" ) )
        else:
            self.skinTool.resetSkinnedJoints( cmds.ls( sl=True, type="joint" ) )

    def deleteBoneInfluence(self):
        meshes = cmds.ls( sl = True )
        joints = cmds.ls( sl = True, type = "joint" )

        transforms = []
        for mesh in meshes:
            if mesh in joints:
                continue
            transforms.append( mesh )
        if transforms == []:
            meshes = cmds.ls(type = "mesh")
            meshes.extend(cmds.ls(type = "nurbsSurface"))
            meshes.extend(cmds.ls(type = "nurbsCurve"))
            meshes.extend(cmds.ls(type = "lattice"))
            for mesh in meshes:
                transforms.append(cmds.listRelatives(mesh, parent=1)[0])

        self.skinTool.removeJoints(
            skinObjects = transforms, 
            jointsToRemove= joints, 
            useParent = False, 
            fast = self.deleteBonesCheck[0].isChecked(),
            progressBar = self.tool_progressBar)
    
    def getmeshesInfluenced(self, *args):
        currentJoints = cmds.ls(sl=1, type = "joint")
        cmds.select(self.skinTool.getMeshesInfluencedByJoint(currentJoints), r=1)

    def tabchanged(self, *args):
        ''' scriptjob management of tabs '''
        currentIndex = self.skintabWidget.currentIndex()
        
        def killJobs(button, job):
            if job:
                cmds.scriptJob(kill=job, force=True)
                button.setStyleSheet('')
                button.setChecked(False)

        if currentIndex == 1:
            self.addVertexSliders()
            killJobs(self.componentEdit.liveBtn, self.componentEdit.getScriptJob())
        else:
            killJobs(self.LiveButton, self.__liveJob)

        if currentIndex == 2:
            self.componentEdit._refresh()
        
        # if currentIndex == 4:
        #     self.connectQt2Node()

    def addVertexSliders(self, *args):
        self.scrollAreaWidgetContents.setWidget(self.__sliderList)
        self.__sliderList.update()
        self.scrollAreaWidgetContents.setWidgetResizable(True)
        self.scrollAreaWidgetContents.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def vertexSlidersAutoUpdate(self, *args):
        state = self.LiveButton.isChecked()
        if state:
            self.__liveJob = cmds.scriptJob(e=('SelectionChanged', self.__sliderList.update), protected=True)
            self.LiveButton.setStyleSheet('background-color: rgb(255, 0, 0);')
        else:
            cmds.scriptJob(kill=self.__liveJob, force=True)
            self.LiveButton.setStyleSheet('')
            self.__liveJob = None

    def __hammerOperation(self, *args):
        ''' add hammer skin weights to repeat last used action '''
        cmds.undoInfo(ock=True)
        try:
            self.skinTool.hammerVerts(cmds.ls(sl=True), needsReturn = False)
            cmds.repeatLast(ac='python("from maya import cmds;from skinningTool.skinningTools import SkinningTools;SkinningTools().hammerVerts(cmds.ls(sl=True), needsReturn = False)");')
        except Exception, e:
            cmds.warning(e)
        finally:
            cmds.undoInfo(cck=True)
    
    def smoothOutsideSelection(self, *args):
        selection = cmds.ls(sl=True)
        self.skinTool.smoothAndSmoothNeighbours(selection)
        cmds.select(selection, r=1)
        cmds.repeatLast(ac='python("from maya import cmds;from skinningTool.skinningTools import SkinningTools;selection = cmds.ls(sl=True);SkinningTools().smoothAndSmoothNeighbours(selection);cmds.select(selection, r=1)")')

    def smoothInOutsideSelection(self, *args):
        selection = cmds.ls(sl=True)
        selection1 = self.skinTool.smoothAndSmoothNeighbours(selection, True, self.growingCheck[0].isChecked())
        cmds.select(selection1, r=1)
        cmds.repeatLast(ac='python("from maya import cmds;from skinningTool.skinningTools import SkinningTools;selection = cmds.ls(sl=True);selection1 = SkinningTools().smoothAndSmoothNeighbours(selection, True, %s);cmds.select(selection1,r=1)")'%self.growingCheck[0].isChecked())

    def keepOnlySelectedInf(self, *args):
        meshSelection = cmds.ls(sl=True, fl=True)
        jointSelection = cmds.ls(sl=True, type = "joint")

        self.skinTool.keepOnlySelectedInfluences(meshSelection, jointSelection)
        cmds.repeatLast(ac='python("from maya import cmds;from skinningTool.skinningTools import SkinningTools;meshSelection = cmds.ls(sl=True, fl=True);jointSelection = cmds.ls(sl=True, type = "joint");SkinningTools().keepOnlySelectedInfluences(meshSelection, jointSelection);")')
        
    def storeInnerSelection(self, *args):
        selection = cmds.ls(sl=True)
        self.borderSelectionBase = self.skinTool.convertToVertexList(selection)
        self.borderSelection = None
        self.borderIter = 0
        self.ShrinkBorderButton.setEnabled(False)
        self.GrowBorderButton.setEnabled(True)

    def growBorderSelection(self, *args):
        self.borderIter += 1
        self.ShrinkBorderButton.setEnabled(True)
        self.borderSelectionCommand()

    def shrinkBorderSelection(self, *args):
        self.borderIter -= 1
        if self.borderIter == 0:
            self.ShrinkBorderButton.setEnabled(False)
        self.borderSelectionCommand()
            
    def borderSelectionCommand(self, *args):
        for i in range(self.borderIter):
            if i == 0:
                toConvert = self.borderSelectionBase
            else:
                toConvert = self.borderSelection
            
            #grow selection removing stored components (polygon and nurbsSurface only)
            objType = cmds.objectType(toConvert[0])
            if objType == 'mesh': 
                convertedFaces = cmds.polyListComponentConversion(toConvert, tf=True)
                self.borderSelection  = self.skinTool.convertToVertexList(convertedFaces)
            elif objType == "nurbsSurface":
                cmds.select(cl=1)
                cmds.nurbsSelect(toConvert,  gs=1 )
                self.borderSelection = cmds.ls(sl=1, fl=1)
            elif objType == "lattice":
                self.borderSelection = polySelectionUtils.growLatticePoints(toConvert)
            else:
                cmds.error( "current type --%s-- not valid for this commmand, only surface or polygon can be used!"%objType )
        borderSelect = list(set(self.borderSelection) ^ set(self.borderSelectionBase))
        cmds.select(borderSelect, r=1)

    def removeInfl(self, *args):
        ''' fast way to remove unused influences from a skincluater '''
        selection = cmds.ls(sl=True)
        self.skinTool.removeUnusedInfluences(selection, self.tool_progressBar)

    def transferUV(self, *args):
        self.labelCheck()
        selected_objects = cmds.ls(selection=True, l=True)
        cmds.select(self.skinTool.transferUvToSkinnedObject(selected_objects[0], selected_objects[1]), r=1)

    def cleanSkinMesh(self, *args):
        self.labelCheck()
        selected_objects = cmds.ls(selection=True, l=True, type = "transform")
        cmds.select(self.skinTool.freezeSkinnedMesh(selected_objects, self.tool_progressBar), r=1)

    def combineSkinnedMesh(self, *args):
        selection = cmds.ls(sl=True)
        if (int(mayaVersion) >= 2015):
            cmds.polyUniteSkinned( selection, ch= 0, mergeUVSets =1)
        else:
            cmds.select(self.skinTool.combineSkinnedMeshes(selection), r=1)

    def keepOnlySelectedInf(self, *args):
        meshSelection = cmds.ls(sl=True, fl=True)
        jointSelection = cmds.ls(sl=True, type = "joint")

        self.skinTool.keepOnlySelectedInfluences(meshSelection, jointSelection)
        cmds.repeatLast(ac='python("from maya import cmds;from skinningTool.skinningTools import SkinningTools;meshSelection = cmds.ls(sl=True, fl=True);jointSelection = cmds.ls(sl=True, type = "joint");SkinningTools().keepOnlySelectedInfluences(meshSelection, jointSelection);")')
        
    def gotopreBindPose(self, *args):
        cmds.undoInfo(ock=True)
        result = cmds.confirmDialog( 
            title='go to bindpose', 
            message='Are you sure you want to go back to bindpose?', 
            button=['Yes','No'], 
            defaultButton='Yes', cancelButton='No', 
            dismissString='No' )

        if result != 'Yes':
            cmds.undoInfo(cck=True)
            return
        try:
            meshes = cmds.ls(sl=True, type="transform")
            if len(meshes) == 0:
                meshes = []
                mesh = cmds.ls(type="mesh")
                for i in mesh:
                    mesh.append(cmds.listRelatives(i, parent =True)[0])
                
            for mesh in meshes:
                if cmds.objectType(mesh) == "joint":
                    continue
                shape = cmds.listRelatives(mesh, s=True)
                if cmds.objectType(shape[0]) != "mesh":
                    continue
                self.skinTool.resetToBindPose(mesh)
        except Exception, e:
            cmds.warning(e)
        finally:
            cmds.undoInfo(cck=True)

    def __buttonsToAttach(self, name, command,*args):
        button = QPushButton()
        
        button.setText (name)
        button.setObjectName (name)
        
        button.clicked.connect(command)
        button.setMinimumHeight(23)
        self.VerticalMayaSkinToolsLayout.addWidget(button)
        return button

    def __proxybuttonsToAttach(self, name, command,*args):
        layout = QHBoxLayout()
        
        button = QPushButton()
        button.setText (name)
        button.setObjectName (name)
        self.check1 = QCheckBox("internal")
        self.check2 = QCheckBox("fast")
        self.check2.setChecked(True)
        button.clicked.connect(command)

        layout.addWidget(button)
        layout.addWidget(self.check1)
        layout.addWidget(self.check2)
        self.VerticalMayaSkinToolsLayout.addLayout(layout)
        return button

    def __createProxy(self):
        # add window inbetween to prevent mishaps
        sel = cmds.ls(sl=1, type="transform")
        result = cmds.confirmDialog( 
            title='create procy mesh from skinned objects!', 
            message='Creating a proxy mesh can take a while,\ndo you want to continue?', 
            button=['Yes','No'], 
            defaultButton='Yes', cancelButton='No', 
            dismissString='No' )

        if result == 'Yes':
            createProxyMesh.cutCharacterFromSkin(sel, self.check1.isChecked(), self.check2.isChecked(),progressBar = self.tool_progressBar)

    def __mirrorSkinOptions(self,*args):
        self.labelCheck()
        cmds.optionVar( stringValue=( "mirrorSkinAxis", "YZ"))
        cmds.optionVar( intValue= ("mirrorSkinWeightsSurfaceAssociationOption", 3))
        cmds.optionVar( intValue= ("mirrorSkinWeightsInfluenceAssociationOption1", 3))
        cmds.optionVar( intValue= ("mirrorSkinWeightsInfluenceAssociationOption2", 2))
        cmds.optionVar( intValue= ("mirrorSkinWeightsInfluenceAssociationOption3", 1))
        cmds.optionVar( intValue= ("mirrorSkinNormalize", 1))   
        cmds.MirrorSkinWeightsOptions()

    def __copySkinWeightsOptions( self, *args):
        self.labelCheck()
        cmds.optionVar( intValue= ("copySkinWeightsSurfaceAssociationOption", 3))
        cmds.optionVar( intValue= ("copySkinWeightsInfluenceAssociationOption1", 4))
        cmds.optionVar( intValue= ("copySkinWeightsInfluenceAssociationOption2", 4))
        cmds.optionVar( intValue= ("copySkinWeightsInfluenceAssociationOption3", 6))
        cmds.optionVar( intValue= ("copySkinWeightsNormalize", 1))  
        cmds.CopySkinWeightsOptions()

    def __addMayaToolsToWindow(self, *args):
        self.mb01 = self.__buttonsToAttach('Smooth Bind', cmds.SmoothBindSkinOptions)
        self.mb02 = self.__buttonsToAttach('Rigid Bind', cmds.RigidBindSkinOptions)

        self.mb03 = QPushButton()
        self.mb03.setText ('Detach Skin')
        self.mb03.setObjectName ('Detach Skin')
        
        self.mb03.clicked.connect(cmds.DetachSkin)
        self.mb03.setMinimumHeight(25)
        
        detachSkinOptions = QPushButton()
        detachSkinOptions.setObjectName ('[  ]')
        buttonIcon = QIcon("%s/Icon/%s.png"%(os.path.dirname(__file__), "option_gear"))
        detachSkinOptions.setIcon(buttonIcon)
        
        detachSkinOptions.setMaximumWidth(20)
        detachSkinOptions.setMinimumHeight(23)
        detachSkinOptions.clicked.connect(cmds.DetachSkinOptions)
        
        horizontal_layout = QHBoxLayout()
        horizontal_layout.setContentsMargins(0,0,0,0)
        horizontal_layout.setObjectName('Layout__DetachSkin')
        horizontal_layout.addWidget(self.mb03)
        horizontal_layout.addWidget(detachSkinOptions)
        self.VerticalMayaSkinToolsLayout.addLayout(horizontal_layout)

        self.mb04 = self.__buttonsToAttach('Paint Skin Weights',    cmds.ArtPaintSkinWeightsToolOptions) 
        self.mb05 = self.__buttonsToAttach('Mirror Skin Weights',   self.__mirrorSkinOptions)
        self.mb06 = self.__buttonsToAttach('Copy Skin Weights',     self.__copySkinWeightsOptions)
        self.mb07 = self.__buttonsToAttach('Prune Weights',         cmds.PruneSmallWeightsOptions)
        self.mb08 = self.__buttonsToAttach( 'transfer skinned UV ', self.transferUV )
        self.mb09 = self.__buttonsToAttach( 'Clean skinned mesh',   self.cleanSkinMesh )
        self.mb10 = self.__buttonsToAttach( 'Combine skinned mesh', self.combineSkinnedMesh )
        self.mb11 = self.__buttonsToAttach( 'Extract skinned faces',self.extractskinnedFaces )
        self.mb12 = self.__buttonsToAttach('Remove unused Infl',    self.removeInfl)
        self.mb13 = self.__buttonsToAttach('goto Bindpose',         self.gotopreBindPose)
        self.mb14 = self.__buttonsToAttach('delete Bindposes',      self.deleteBindPoses)
        self.mb15 = self.__buttonsToAttach('Weight Hammer',         self.__hammerOperation)
        self.mb16 = self.__proxybuttonsToAttach('create proxy',     self.__createProxy)
    
    def getVisualiser(self, *args):
        getNode = cmds.ls(type="SkinningVisualizer") or None
        if getNode == None:
            return None
        self.visualiserNode = getNode[0]
        PositionalLocators = cmds.listConnections('%s.jointPairs'%self.visualiserNode, s=1)
        return self.visualiserNode

        previousParent = ''
        self.singleLocs = []
        self.doubleLocs = []
        for index, locator in enumerate(PositionalLocators):
            jointParent = cmds.getAttr("%s.parentObj"%locator)
            locParentList.append(jointParent)
            if previousParent != jointParent:
                doubleLocs.append([singleLocs[-1], locator])
                singleLocs.pop(-1)
                previousParent = ''
            else:
                singleLocs.append(locator)
                previousParent = jointParent
        return self.visualiserNode

    def setQtAttr(self, attr):
        cmds.setAttr( '%s.%s'%(self.visualiserNode, attr), self.sender().value() )
    def setQtCheck(self, attr):
        cmds.setAttr('%s.%s'%(self.visualiserNode, attr), self.sender().isChecked())
    def setQtColor(self, attr):
        colorList =  QColor(self.sender().color()).getRgb()
        cmds.setAttr("%s.%s"%(self.visualiserNode, attr), (colorList[0]/255.0), (colorList[1]/255.0), (colorList[2]/255.0), type="double3" )
    
    def fixSelectionMask(self, *args):
        if self.sender().isChecked():
            mel.eval('setObjectPickMask "Surface" false;')
            mel.eval('setObjectPickMask "Joint" false;')
            mel.eval('setObjectPickMask "Marker" false;')
            mel.eval('setObjectPickMask "Curve" false;')
        else:
            mel.eval('setObjectPickMask "Surface" true;')
            mel.eval('setObjectPickMask "Joint" true;')
            mel.eval('setObjectPickMask "Marker" true;')
            mel.eval('setObjectPickMask "Curve" true;')
            
    def attachCollorButtons(self, *args):
        self.qColor1Object = QColorButton()
        self.colorLayoutvis_1.addWidget(self.qColor1Object)
        self.qColor2Object = QColorButton()
        self.colorLayoutvis_2.addWidget(self.qColor2Object)
        self.qColor3Object = QColorButton()
        self.colorLayoutvis_3.addWidget(self.qColor3Object)
       
    def connectQt2Node(self, *args):
        #@TODO: maybe add functionality to move symmetry??
        nodes = [self.transSpinBox, self.radiusSpinBox, self.segmentsSlider, self.segmentsSpinBox, 
                 self.amoundConnSpinBox, self.cullingcheckBox, self.autoScaleCheckBox, self.skBindSkinButton,
                 self.colorFrame1, self.colorFrame2, self.selMaskcheckBox]

        if self.visualiserNode == None:
            obj = self.getVisualiser()
            if obj == None:
                for node  in nodes:
                    node.setEnabled(False)
                return

        for node  in nodes:
            node.setEnabled(True)

        self.segmentsSlider.valueChanged.connect(  self.segmentsSpinBox.setValue )
        self.segmentsSpinBox.valueChanged.connect( self.segmentsSlider.setValue )

        self.transSpinBox.setValue(cmds.getAttr(self.visualiserNode +'.transparency'))
        self.radiusSpinBox.setValue(cmds.getAttr(self.visualiserNode +'.radius'))
        self.segmentsSpinBox.setValue(cmds.getAttr(self.visualiserNode +'.segments'))
        self.amoundConnSpinBox.setValue(cmds.getAttr(self.visualiserNode +'.amountConnected'))
        self.cullingcheckBox.setChecked(cmds.getAttr(self.visualiserNode +'.cullSpaceDiscs'))
        self.autoScaleCheckBox.setChecked(cmds.getAttr(self.visualiserNode +'.screenSpaceDiscs'))
        self.drawInFrontCheck.setChecked(cmds.getAttr(self.visualiserNode +'.drawInFront'))
        color1 = cmds.getAttr(self.visualiserNode +'.controlColor')[0]
        color2 = cmds.getAttr(self.visualiserNode +'.clickedColor')[0]
        color3 = cmds.getAttr(self.visualiserNode +'.discColor')[0]
        
        self.qColor1Object.setColor(QColor(color1[0]*255, color1[1]*255,color1[2]*255, 255).name())
        self.qColor2Object.setColor(QColor(color2[0]*255, color2[1]*255,color2[2]*255, 255).name())
        self.qColor3Object.setColor(QColor(color3[0]*255, color3[1]*255,color3[2]*255, 255).name())

        self.transSpinBox.valueChanged.connect(      functools.partial( self.setQtAttr,  "transparency") )
        self.radiusSpinBox.valueChanged.connect(     functools.partial( self.setQtAttr,  "radius") )
        self.segmentsSpinBox.valueChanged.connect(   functools.partial( self.setQtAttr,  "segments") )
        self.amoundConnSpinBox.valueChanged.connect( functools.partial( self.setQtAttr,  "amountConnected") )
        self.cullingcheckBox.stateChanged.connect(   functools.partial( self.setQtCheck, "cullSpaceDiscs") )
        self.autoScaleCheckBox.stateChanged.connect( functools.partial( self.setQtCheck, "screenSpaceDiscs") )
        self.qColor1Object.colorChanged.connect(     functools.partial( self.setQtColor, "controlColor"))
        self.qColor2Object.colorChanged.connect(     functools.partial( self.setQtColor, "clickedColor"))
        self.qColor3Object.colorChanged.connect(     functools.partial( self.setQtColor, "discColor"))
        self.drawInFrontCheck.stateChanged.connect(  functools.partial( self.setQtCheck, "drawInFront") )
        self.selMaskcheckBox.stateChanged.connect(   self.fixSelectionMask )
        
    def AttachVisualiser(self, *args):
        positionMargin = 1.0 - self.coverageSPBX.value()
        primaryAxis = self.primaryCB.currentText()
        
        self.singleLocs, self.doubleLocs, self.visualiserNode = self.skinBinder.createSkinBindVisualiser(errorMargin = 0.01, positionMargin = positionMargin, primaryAxis = str(primaryAxis), jnts = cmds.ls( type = "joint"))
        self.connectQt2Node()

    def VisualToSkin(self, *args):
        parentLoc = cmds.listRelatives( self.visualiserNode, p=1 )[0]
        cmds.delete( parentLoc )
        divisions = self.divSP.value()
        smoothValue = self.smoothSP.value()
        self.skinBinder.convertVisualToSkin(self.singleLocs, self.doubleLocs, cmds.ls(sl=True), divisions, smoothValue, self.tool_progressBar)

    def AnalyseMeshColors(self, *args):
        selection = cmds.ls(sl=1)
        self.skinBinder.analyseSelection( selection , self.colorAttachLayout )

    def applyHardSurfaceSkin(self, *args):
        sel = cmds.ls(sl=True, fl=1)
        if sel == None or len(sel) == 0:
            cmds.error("select components to use this function")
        mesh = sel[0].split(".")[0]
        vtxList = set( [int(x.split(".vtx[")[-1][:-1]) for x in set(cmds.ls(sl=True, o=False, fl = True)) - set(cmds.ls(sl=True, o=True))])
        self.skinBinder.setHardSurfaceSkin( vtxList , mesh,  self.selectionProgressBar )

    def applySoftSurfaceSkin(self, *args):
        sel = cmds.ls(sl=True, fl=1)
        if sel == None or len(sel) == 0:
            cmds.error("select components to use this function")
        mesh = sel[0].split(".")[0]
        vtxList = set( [int(x.split(".vtx[")[-1][:-1]) for x in set(cmds.ls(sl=True, o=False, fl = True)) - set(cmds.ls(sl=True, o=True))])
        self.skinBinder.setSoftSurfaceSkin( vtxList , mesh, self.selectionProgressBar ) 

    def cleanSkbScene(self, *args):
        self.skinBineder.clearScene()

    def freezeSkinnedJoints(self, *args):
        selection = cmds.ls(sl=1, type="joint")
        allJoints = cmds.listRelatives(selection, ad=1, type = "joint")
        s = set()
        duplicates = set(x for x in allJoints if x in s or s.add(x))
        if duplicates:
            base = selection[:]
            if self.freezeJointCheck[0]:
                for select in selection:
                    jnts = cmds.listRelatives(select, ad=1, type="joint")
                    if jnts == None:
                        continue
                    base.extend(jnts)
            cleanlist = list(set(base))
            cmds.warning( "cannot freeze scale because there are nodes with non unique names: %s\nwill only freeze rotations!"%str(list(duplicates)))
            joints = self.skinTool.freezeSkinnedJoints( cleanlist )
        else:
            joints = self.skinTool.freezeSkinnedJointsFull( allJoints )
        cmds.select(joints, r=1)

    def closeEvent(self, *args):
        cmds.selectPref(tso=self.__selecttionPref)
        self.settings.setValue("windowState", self.baseDockWidget.saveState())
        self.settings.setValue("geometry", self.baseDockWidget.saveGeometry())
        
        ''' Clean up the live state when hiding '''
        if self.__liveJob:
            cmds.scriptJob(kill=self.__liveJob, force=True)
            self.LiveButton.setStyleSheet('')
            self.LiveButton.setChecked(False)
        if self.componentEdit.getScriptJob():
            cmds.scriptJob(kill=self.componentEdit.getScriptJob(), force=True)

        
        self.cleanEventFilter()

class DetailsDialog(QDialog):
    def __init__(self, title, parent = None):
        super(DetailsDialog, self).__init__(parent)

        nameLabel = QLabel("Specify label sides (wildCards '*' can be used!):", self)
        l_lineEditLabel = QLabel("LeftSide", self)
        self.l_lineEdit = QLineEdit("L_*", self)
        r_lineEditLabel = QLabel("RightSide", self)
        self.r_lineEdit = QLineEdit("R_*", self)
        
        leftLayout = QHBoxLayout()
        leftLayout.addWidget(l_lineEditLabel)
        leftLayout.addWidget(self.l_lineEdit)
        rightLayout = QHBoxLayout()
        rightLayout.addWidget(r_lineEditLabel)
        rightLayout.addWidget(self.r_lineEdit)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
  
        buttonBox.accepted.connect(self.verify)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(nameLabel)
        mainLayout.addLayout(leftLayout)
        mainLayout.addLayout(rightLayout)
        mainLayout.addWidget(buttonBox)

        self.setLayout(mainLayout)
        self.setWindowTitle(title)

    def verify(self):
        if self.l_lineEdit.text() != "" and self.r_lineEdit.text() != "" and self.l_lineEdit.text() != self.r_lineEdit.text():
            self.accept()
            return
  
        answer = QMessageBox.warning(self, "Incomplete Form",
                "The form does not contain all the necessary information.\n"
                "Continue with default settings?",
                QMessageBox.Yes, QMessageBox.No)
  
        if answer == QMessageBox.Yes:
            self.reject()

class SkinningToolsDock(MayaQWidgetDockableMixin, QDialog):
    toolName = 'Skinngin_Tools_Dock'

    def __init__(self, inWidget, parent = None):
        self.deleteInstances()
        super(self.__class__, self).__init__(parent = parent)
        self.setObjectName(self.__class__.toolName) 
        
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle('Skinning Tools:%s'%__VERSION__)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(inWidget)
        self.inWidget = inWidget
        self.setLayout(self.mainLayout)

    def dockCloseEventTriggered(self):
        self.inWidget.close()
        self.deleteInstances()

    def deleteInstances(self):
        if (cmds.window("%sWorkspaceControl"%self.__class__.toolName, exists=True)):
            cmds.deleteUI("%sWorkspaceControl"%self.__class__.toolName)
    
    def run(self):
        self.show(dockable = True)

def startUI():
    selection = cmds.ls(sl=True)
    cmds.select(cl=True)
    '''starts UI and makes it dockable within Maya'''
    MayaWindowPtr = wrapinstance( long( OpenMayaUI.MQtUtil.mainWindow() ) )
  
    window_name         = 'Skinning_Tools:%s'%__VERSION__
    dock_control        = 'Skinning_Tools_Dock:%s'%__VERSION__
    
    window = SkinningToolsUI( MayaWindowPtr )
    window.setObjectName( window_name )

    if (cmds.window("%sWorkspaceControl"%dock_control, exists=True)):
        cmds.deleteUI("%sWorkspaceControl"%dock_control)
        
    main = SkinningToolsDock( window, MayaWindowPtr )
    main.resize( 500, 700 )
    main.setMinimumSize( 270, 270 )
    main.run()
    window.updateItems()

    if len(selection) > 0:
        cmds.select( selection )