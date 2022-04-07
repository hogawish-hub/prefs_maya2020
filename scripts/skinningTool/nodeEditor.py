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
from qtUtil import *

class NodeScene(QGraphicsScene):
    def __init__(self):
        super(NodeScene, self).__init__()
        hugeSize = 10000
        self.setSceneRect(-hugeSize, -hugeSize, hugeSize * 2, hugeSize * 2)
        self.__undoStack = QUndoStack()

    def undoStack(self):
        return self.__undoStack

class NodeCreateConnectionCommand(QUndoCommand):
    def __init__(self, scene, sourceSocket, targetSocket, description=None, parent=None):
        super(NodeCreateConnectionCommand, self).__init__(description or self.__class__.__name__[4:-7], parent)

        assert isinstance(scene, QGraphicsScene)
        assert isinstance(sourceSocket, NodeSocketOut)
        assert isinstance(targetSocket, NodeSocketIn)

        self.__scene = scene
        self.__connection = NodeConnection(sourceSocket, targetSocket)

    def redo(self):
        super(NodeCreateConnectionCommand, self).redo()
        self.__scene.addItem(self.__connection)
        self.__connection.register()

    def undo(self):
        super(NodeCreateConnectionCommand, self).undo()
        self.__scene.removeItem(self.__connection)
        self.__connection.deregister()


class NodeDeleteConnectionCommand(QUndoCommand):
    def __init__(self, scene, connection, description=None, parent=None):
        super(NodeDeleteConnectionCommand, self).__init__(description or self.__class__.__name__[4:-7], parent)

        assert isinstance(scene, QGraphicsScene)
        assert isinstance(connection, NodeConnection)

        self.__scene = scene
        self.__connection = connection

    def redo(self):
        super(NodeDeleteConnectionCommand, self).redo()
        self.__scene.removeItem(self.__connection)
        self.__connection.deregister()

    def undo(self):
        super(NodeDeleteConnectionCommand, self).undo()
        self.__scene.addItem(self.__connection)
        self.__connection.register()


class NodeDeleteCommand(QUndoCommand):
    def __init__(self, scene, node, description=None, parent=None):
        super(NodeDeleteCommand, self).__init__(description or self.__class__.__name__[4:-7], parent)
        assert isinstance(scene, QGraphicsScene)
        assert isinstance(node, NodeItem)

        self.__scene = scene
        self.__node = node

    def redo(self):
        super(NodeDeleteCommand, self).redo()
        self.__node.breakConnections(self)
        self.__scene.removeItem(self.__node)

    def undo(self):
        super(NodeDeleteCommand, self).undo()
        self.__scene.addItem(self.__node)


class NodeAddCommand(QUndoCommand):
    def __init__(self, scene, node, description=None, parent=None):
        super(NodeAddCommand, self).__init__(description or self.__class__.__name__[4:-7], parent)
        assert isinstance(scene, QGraphicsScene)
        assert isinstance(node, NodeItem)

        self.__scene = scene
        self.__node = node

    def redo(self):
        super(NodeAddCommand, self).redo()
        self.__scene.addItem(self.__node)

    def undo(self):
        super(NodeAddCommand, self).undo()
        self.__scene.removeItem(self.__node)


class NodeMoveCommand(QUndoCommand):
    def __init__(self, nodes, oldPositions, newPositions, description=None, parent=None):
        super(NodeMoveCommand, self).__init__(description or self.__class__.__name__[4:-7], parent)
        assert len(nodes) == len(oldPositions) and len(oldPositions) == len(newPositions)
        self.__nodes = nodes
        self.__oldPositions = oldPositions
        self.__newPositions = newPositions

    def redo(self):
        super(NodeMoveCommand, self).redo()
        for i in xrange(len(self.__nodes)):
            self.__nodes[i].setPos(self.__newPositions[i])

    def undo(self):
        super(NodeMoveCommand, self).undo()
        for i in xrange(len(self.__nodes)):
            self.__nodes[i].setPos(self.__oldPositions[i])


class NodeLineBase(QGraphicsPathItem):
    pen = QPen()
    pen.setStyle(Qt.SolidLine)
    pen.setWidth(2)
    pen.setColor(QColor(80, 229, 80, 255))  # line color

    selPen = QPen()
    selPen.setStyle(Qt.SolidLine)
    selPen.setWidth(3)
    selPen.setColor(QColor(255, 51, 0, 255))

    def __init__(self):
        super(NodeLineBase, self).__init__()
        self.setZValue(-1)

    def _updatePath(self, startPos, endPos):
        path = QPainterPath()
        path.moveTo(startPos)

        d = endPos - startPos
        ctrl1 = QPointF(d.x() * 0.666, d.y() * 0.0)
        ctrl2 = d - ctrl1
        path.cubicTo(startPos + ctrl1, startPos + ctrl2, endPos)

        self.setPath(path)

    def paint(self, painter, option, widget):
        if self.isSelected():
            painter.setPen(self.selPen)
        else:
            painter.setPen(self.pen)
        painter.drawPath(self.path())


class NodeConnection(NodeLineBase):
    def __init__(self, source, target):
        super(NodeConnection, self).__init__()
        self._source = source
        self._target = target
        self.updatePath()

        self.setFlag(QGraphicsItem.ItemIsSelectable)

    def register(self):
        self._source.registerConnection(self)
        self._target.registerConnection(self)

    def deregister(self):
        self._source.deregisterConnection(self)
        self._target.deregisterConnection(self)

    def updatePath(self):
        startPos = self._source.mapToScene(self._source.center())
        endPos = self._target.mapToScene(self._target.center())
        super(NodeConnection, self)._updatePath(startPos, endPos)


class NodeTempLine(NodeLineBase):
    pen = QPen()
    pen.setStyle(Qt.SolidLine)
    pen.setWidth(2)
    pen.setColor(QColor(80, 229, 80, 255))  # line color

    def __init__(self, startPos, endPos):
        super(NodeTempLine, self).__init__()
        self.__startPos = startPos
        self.__endPos = endPos

    def setStartPos(self, startPos):
        self.__startPos = startPos
        self.updatePath()

    def setEndPos(self, endPos):
        self.__endPos = endPos
        self.updatePath()

    def updatePath(self):
        super(NodeTempLine, self)._updatePath(self.__startPos, self.__endPos)

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        painter.drawPath(self.path())


class NodeSocket(QGraphicsItem):
    brush = QBrush()
    brush.setStyle(Qt.SolidPattern)
    brush.setColor(QColor(80, 230, 80, 255))  # attachColor

    pen = QPen()
    pen.setStyle(Qt.SolidLine)
    pen.setWidth(2)
    pen.setColor(QColor(104, 104, 104, 255))  # outlineColor

    def __init__(self, rect, parent):
        super(NodeSocket, self).__init__(parent)
        self.rect = rect
        self.lines = []

    def center(self):
        return self.boundingRect().center()

    def shape(self):
        path = QPainterPath()
        path.addEllipse(self.boundingRect())
        return path

    def boundingRect(self):
        return QRectF(self.rect)

    def paint(self, painter, option, widget):
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        painter.drawEllipse(self.rect)

    def getCenter(self):
        rect = self.boundingRect()
        center = QPointF(rect.x() + rect.width() / 2, rect.y() + rect.height() / 2)
        center = self.mapToScene(center)
        return center

    def mousePressEvent(self, event):
        self._dragging = NodeTempLine(self.mapToScene(event.pos()), self.mapToScene(self.center()))
        self.scene().addItem(self._dragging)

    def mouseMoveEvent(self, event):
        self._dragging.setStartPos(self.mapToScene(event.pos()))

    def _createConnection(self, item):
        raise NotImplementedError()

    def mouseReleaseEvent(self, event):
        self.scene().removeItem(self._dragging)
        item = self.scene().itemAt(event.scenePos().toPoint(), QTransform())
        for connection in self.lines:
            if connection._source == item or connection._target == item:
                return
        self._createConnection(item)

    def registerConnection(self, connection):
        assert isinstance(connection, NodeConnection)
        self.lines.append(connection)

    def deregisterConnection(self, connection):
        self.lines.remove(connection)


class NodeSocketIn(NodeSocket):
    def _createConnection(self, item):
        if not isinstance(item, NodeSocketOut):
            return

        cmd = NodeCreateConnectionCommand(self.scene(), item, self)
        self.scene().undoStack().push(cmd)


class NodeSocketOut(NodeSocket):
    def _createConnection(self, item):
        if not isinstance(item, NodeSocketIn):
            return
        cmd = NodeCreateConnectionCommand(self.scene(), self, item)
        self.scene().undoStack().push(cmd)


class NodeItem(QGraphicsItem):
    brush = QBrush()
    brush.setStyle(Qt.SolidPattern)
    brush.setColor(QColor(42, 42, 42, 255))  # base color

    pen = QPen()
    pen.setStyle(Qt.SolidLine)
    pen.setWidth(2)
    pen.setColor(QColor(104, 104, 104, 255))  # outline not selected

    selPen = QPen()
    selPen.setStyle(Qt.SolidLine)
    selPen.setWidth(2)
    selPen.setColor(QColor(67, 255, 163, 255))  # outline selected

    def __init__(self, numInputs, numOutputs, name=''):
        super(NodeItem, self).__init__()
        self.name = name
        self.__rect = QRectF(0, 0, 200, 40)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

        assert (numInputs == 1) != (numOutputs == 1), 'Must have exactly 1 socket (0 in 1 out) (1 in 0 out). Other configurations are not supported (you gave %s in %s out).' % (numInputs, numOutputs)
        self.__inputs = []
        self.__outputs = []

        rect = self.boundingRect()
        spDim = 20
        for i in xrange(numInputs):
            self.__inputs.append(NodeSocketIn(QRect(-10, (rect.height() / 2) - (spDim / 2), spDim, spDim), self))
        for j in xrange(numOutputs):
            self.__outputs.append(NodeSocketOut(QRect(rect.width() - 10, (rect.height() / 2) - (spDim / 2), spDim, spDim), self))

    def inputs(self):
        return self.__inputs

    def outputs(self):
        return self.__outputs

    def breakConnections(self, undoCommandParent=None):
        for socket in self.__inputs + self.__outputs:
            for line in socket.lines:
                NodeDeleteConnectionCommand(self.scene(), line, parent=undoCommandParent)

    def setPos(self, pos):
        super(NodeItem, self).setPos(pos)
        self._updateLines()

    def shape(self):
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def boundingRect(self):
        return QRectF(self.__rect)

    def paint(self, painter, option, widget):
        rect = self.boundingRect()
        painter.setBrush(self.brush)
        if self.isSelected():
            painter.setPen(self.selPen)
        else:
            painter.setPen(self.pen)
        painter.drawRect(self.__rect)
        painter.drawText(QPointF(30.0, (rect.height() / 2) + 4), self.name)

    def mouseMoveEvent(self, event):
        super(NodeItem, self).mouseMoveEvent(event)
        self._updateLines()

    def _updateLines(self):
        for socket in self.__inputs + self.__outputs:
            for line in socket.lines:
                line.updatePath()


class NodeView(QGraphicsView):
    def __init__(self, parent=None):
        super(NodeView, self).__init__(parent)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Color.
        windowCss = '''background-color: rgb(60,60,60); border: 1px solid rgb(90,70,30);'''
        self.setStyleSheet(windowCss)

        # track whether we are moving the camera
        self.__panning = None

        # track where items were moved from, we can't hook into QGraphicsScene's drag behaviour but we do want undo
        self.__nodeStates = None
    
    def createUndoRedoActions(self):
        undo = self.scene().undoStack().createUndoAction(self)
        redo = self.scene().undoStack().createRedoAction(self)
        undo.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_Z))
        redo.setShortcuts((QKeySequence(Qt.CTRL + Qt.Key_Y),
                           QKeySequence(Qt.SHIFT + Qt.Key_Z),
                           QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_Z)))
        return undo, redo

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            # Delete connections first, so they are properly deregistered
            group = QUndoCommand('Delete')
            self.__deleteConnections(group)
            self.__deleteNodes(group)
            self.scene().undoStack().push(group)
        if event.key() == Qt.Key_F:
            self.focusScene()


    def focusScene(self):
        rect = self.scene().itemsBoundingRect()
        self.fitInView(rect, Qt.KeepAspectRatio)

    def __deleteNodes(self, parent):
        for item in self.scene().selectedItems():
            if not isinstance(item, NodeItem):
                continue
            cmd = NodeDeleteCommand(self.scene(), item, parent=parent)
            if parent is None:
                self.scene().undoStack().push(cmd)

    def __deleteConnections(self, parent):
        for item in self.scene().selectedItems():
            if not isinstance(item, NodeConnection):
                continue
            cmd = NodeDeleteConnectionCommand(self.scene(), item, parent=parent)
            if parent is None:
                self.scene().undoStack().push(cmd)

    def addNode(self, node):
        cmd = NodeAddCommand(self.scene(), node)
        self.scene().undoStack().push(cmd)

    def wheelEvent(self, event):
        inFactor = 1.25
        outFactor = 1 / inFactor
        oldPos = self.mapToScene(event.pos())
        if event.delta() > 0:
            zoomFactor = inFactor
        else:
            zoomFactor = outFactor
        self.scale(zoomFactor, zoomFactor)
        newPos = self.mapToScene(event.pos())
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())

    def __beginDragNodes(self, event):
        if event.button() != Qt.LeftButton:
            return

        self.setDragMode(QGraphicsView.RubberBandDrag)

        self.__nodeStates = {}
        for item in self.scene().items():
            if not isinstance(item, NodeItem):
                continue
            self.__nodeStates[item] = item.pos()  # make a copy

    def __endDragNodes(self):
        if self.__nodeStates is None:
            return

        itemLocationRemap = []
        for item in self.__nodeStates.keys():
            if self.__nodeStates[item] == item.pos():
                del self.__nodeStates[item]
                continue
            itemLocationRemap.append(item.pos())  # make a copy
        if itemLocationRemap:
            self.scene().undoStack().push(NodeMoveCommand(self.__nodeStates.keys(), self.__nodeStates.values(), itemLocationRemap))

        self.__nodeStates = None

    def __beginCameraPan(self, event):
        if event.button() != Qt.MiddleButton or event.modifiers() != Qt.AltModifier:
            return

        self.setDragMode(QGraphicsView.NoDrag)
        self.__panning = event.pos()
        self.setCursor(Qt.SizeAllCursor)

    def mousePressEvent(self, event):
        self.__beginCameraPan(event)
        self.__beginDragNodes(event)
        super(NodeView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super(NodeView, self).mouseMoveEvent(event)
        # pan camera
        if self.__panning is None:
            return

        delta = self.mapToScene(self.__panning) - self.mapToScene(event.pos())
        center = QPoint(self.viewport().width() * 0.5 + delta.x(), self.viewport().height() * 0.5 + delta.y())
        center = self.mapToScene(center)
        self.centerOn(center)
        self.__panning = event.pos()

    def mouseReleaseEvent(self, event):
        if self.__panning:
            self.__panning = None
            self.setCursor(Qt.ArrowCursor)
        self.__endDragNodes()
        super(NodeView, self).mouseReleaseEvent(event)

class JointWindow(QMainWindow):
    def __init__(self, parent=None):
        super(JointWindow, self).__init__(parent)

        self.setWindowTitle('Node Window')
        self.inItems = []
        self.outItems = []
        self.resize(600, 800)
        self.closeCommand = None
        self.__view = NodeView()
        self.__view.setScene(NodeScene())
        self.setCentralWidget(self.__view)

        undo, redo = self.__view.createUndoRedoActions()
        bar = QMenuBar()
        self.setMenuBar(bar)
        edit = bar.addMenu('Edit')
        edit.addAction(undo)
        edit.addAction(redo)

    def scene(self):
        return self.__view.scene()

    def sizeHint(self):
        return QSize(500, 700)

    def focus(self):
        self.__view.focusScene()

    def getInputItems(self):
        return self.inItems

    def setCloseCommand(self, inCommand):
        self.closeCommand = inCommand

    def addJoints(self, originals, new):
        for i in range(len(originals)):
            box = NodeItem(0, 1, originals[i])
            self.inItems.append(box)
            self.__view.addNode(box)
            cmd = NodeMoveCommand([box], [QPoint()], [QPoint(-100, i * 70)])
            self.scene().undoStack().push(cmd)

        for i in range(len(new)):
            box = NodeItem(1, 0, new[i])
            self.outItems.append(box)
            self.__view.addNode(box)
            cmd = NodeMoveCommand([box], [QPoint()], [QPoint(200, i * 70)])
            self.scene().undoStack().push(cmd)

    def addConnection(self, startNodeName, endNodeName):
        box1 = None
        box2 = None
        for item in self.inItems:
            if item.name == startNodeName:
                box1 = item
        for item in self.outItems:
            if item.name == endNodeName:
                box2 = item
        outSocket = box1.outputs()[0]
        inSocket = box2.inputs()[0]

        for connection in outSocket.lines:
            if connection._target == inSocket:
                # already exists
                return

        cmd = NodeCreateConnectionCommand(self.scene(), outSocket, inSocket)
        self.scene().undoStack().push(cmd)

    def closeEvent(self, *args, **kwargs):
        if not self.closeCommand == None:
            mapDict = {}
            for i in self.inItems:
                if len( i.outputs() ) == 0: 
                    continue
                mapDict[i.name] = []
                for line in i.outputs()[0].lines:
                    mapDict[i.name].append(line._target.parentItem().name)
            
            self.closeCommand(mapDict)

