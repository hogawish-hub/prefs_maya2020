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
from maya import cmds

from ..qtUtil import *
            
from skinningTool.skinningTools     import SkinningTools
'''
When using cmds.skinPercent we can set only 1 row at a time
but it is a lot faster than setting all skin data with cmds.SkinWeights
if we only need a couple hundred rows. When setting more than this amount of
vertices we just apply all weights because SkinWeights is faster at that point.

Value must be tweaked.
'''
SKINPERCENT_BOUNDARY = 1000

class SkinWeightsModel(QObject):
	changed = pyqtSignal()

	def __init__(self, geometry):
		super(SkinWeightsModel, self).__init__()
		self.setGeometry(geometry)
		self.allVertices = []

	def __refresh(self):
		if self.__geometry is None:
			self.__skinCluster = None
			self.__influences = []
			self.__data = []
			self.__zeroColumns = []
			self.__lockedColumns = []
			return

		self.__skinCluster = SkinningTools.skinCluster(self.__geometry)# util.skinClusterFor(self.__geometry)
		self.__influences = cmds.skinCluster(self.__skinCluster, q=True, inf=True)
		self.__data = cmds.SkinWeights(self.__geometry, self.__skinCluster, q=True)
		self.__zeroColumns = [None] * len(self.__influences)
		self.__lockedColumns = [False] * len(self.__influences)

	def __normalizeRow(self, row, setcols, visibleColumns=None):
		cc = self.columnCount()
		values = self.__data[row * cc:(row + 1) * cc]
		setsum = 0.0
		remaindersum = 0.0
		remainderIds = []
		one = 1.0
		for i in range(len(values)):
			if visibleColumns is not None and i not in visibleColumns:
				continue
			if i in setcols:
				setsum += values[i]
			elif self.__lockedColumns[i]:
				one -= values[i] # subtract locked values from our movement space
			else:
				remainderIds.append(i)
				remaindersum += values[i]
		if one <= 0.0:
			# zero out everything if the locked data is already at maximum
			for i in range(len(values)):
				if visibleColumns is not None and i not in visibleColumns:
					continue
				if not self.__lockedColumns[i]:
					values[i] = 0.0
		elif setsum >= one:
			# set remainders to 0 and normalize setsum
			for index in remainderIds:
				values[index] = 0.0
			scale = one / setsum
			for index in setcols:
				values[index] *= scale
		elif remaindersum == 0.0:
			# if remainders are 0 and can't be stretched to fill up the remaining space, simply set them to the
			# average required

			if len(remainderIds) == 0:
				# if we just set all columns to 0 treat setcols as remainder
				remainderIds = setcols

			value = (one - setsum) / len(remainderIds)
			for index in remainderIds:
				values[index] = value
		else:
			# scale remainders to fill remaining space after setting
			scale = (one - setsum) / remaindersum
			for index in remainderIds:
				values[index] *= scale

		self.__data[row * cc:(row + 1) * cc] = values

	def __normalizeRows(self, rows, setcols, visibleColumns=None):
		for row in rows:
			self.__normalizeRow(row, setcols, visibleColumns)

	def __index(self, col, row):
		return row * self.columnCount() + col

	def setVertList(self, input):
		self.allVertices = input

	def getVertList(self, input):
		return self.allVertices

	def setGeometry(self, geometry):
		self.__geometry = geometry
		self.__refresh()

	def geometry(self):
		return self.__geometry

	def influenceName(self, index):
		return self.__influences[index]

	def isLockedColumn(self, col):
		return self.__lockedColumns[col]

	def setLockedColumn(self, col, state):
		self.__lockedColumns[col] = state

	def unlockAllColumns(self):
		for i in range(len(self.__influences)):
			self.__lockedColumns[i] = False

	def isZeroColumn(self, col):
		if self.__zeroColumns[col] is None:
			c = len(self.__influences)
			v = 0
			rc = self.rowCount()
			for i in xrange(rc):
				v += self.__data[i * c + col]
			self.__zeroColumns[col] = (v == 0)
		return self.__zeroColumns[col]

	def rowCount(self):
		if not self.__data: return 0
		return len(self.__data) / len(self.__influences)

	def columnCount(self):
		return len(self.__influences)

	def rows(self):
		for i in xrange(self.rowCount()):
			yield i

	def value(self, col, row):
		return self.__data[self.__index(col, row)]

	def setValue(self, col, row, value, visibleColumns=None):
		if self.__lockedColumns[col]:
			return
		self.__data[self.__index(col, row)] = value
		self.__normalizeRow(row, (col,), visibleColumns)
		cmds.SkinWeights(self.__geometry, self.__skinCluster, weights=self.__data)
		self.changed.emit()

	def setValues(self, cols, rows, values, visibleColumns=None):
		dirty = False
		i = 0
		for y in rows:
			d = False
			setcols = []
			for x in cols:
				if self.__lockedColumns[x]:
					i += 1
					continue
				setcols.append(x)
				self.__data[self.__index(x, y)] = values[i]
				i += 1
				d = True
			if d:
				self.__normalizeRow(y, setcols, visibleColumns)
				dirty = True
		if dirty:
			if len(rows) > SKINPERCENT_BOUNDARY:
				cmds.SkinWeights(self.__geometry, self.__skinCluster, nwt=self.__data)
			else:
				for row in rows:
					geo = self.allVertices[row]
					c = self.columnCount()
					s = row * c
					cmds.skinPercent(self.__skinCluster, geo, tv=zip(self.__influences, self.__data[s:s+c]))
			self.changed.emit()


class SkinWeightsProxyModel(object):
	def __init__(self, model):
		self.__model = model
		self.__hideZeroColumns = False

		# expose the source model's changed signal
		self.changed = model.changed

		self.__refresh()

	def __refresh(self):
		self.__zeroColumns = [None] * self.__model.columnCount()
		self.__rowMap = None
		self.__refreshColumnMap()

	def __refreshColumnMap(self):
		self.__columnMap = []
		self.__zeroColumns = [None] * self.__model.columnCount()
		c = self.__model.columnCount()
		for i in xrange(c):
			if self.__hideZeroColumns and self.__isZeroColumn(i):
				continue
			self.__columnMap.append(i)

	def setVertList(self, input):
		self.__model.setVertList(input)

	def getVertList(self, input):
		return self.__model.getVertList()

	# source model methods
	def setGeometry(self, geometry):
		self.__model.setGeometry(geometry)
		self.__refresh()

	def geometry(self):
		return self.__model.geometry()

	def influenceName(self, index):
		return self.__model.influenceName(self.__columnMap[index])

	def isLockedColumn(self, proxyColumn):
		col = self.__columnMap[proxyColumn]
		return self.__model.isLockedColumn(col)

	def setLockedColumn(self, proxyColumn, state):
		col = self.__columnMap[proxyColumn]
		self.__model.setLockedColumn(col, state)

	def unlockAllColumns(self):
		self.__model.unlockAllColumns()	 

	def __isZeroColumn(self, col):
		if self.__rowMap is None:
			return self.__model.isZeroColumn(col)
		if self.__zeroColumns[col] is None:
			v = 0.0
			for row in self.__rowMap:
				v += self.__model.value(col, row)
			self.__zeroColumns[col] = v == 0.0
		return self.__zeroColumns[col]

	def columnCount(self):
		return len(self.__columnMap)

	def rowCount(self):
		if self.__rowMap is None:
			return self.__model.rowCount()
		return len(self.__rowMap)

	def rows(self):
		for i in xrange(self.rowCount()):
			yield i

	def rowLabel(self, index):
		if self.__rowMap is not None:
			return str(self.__rowMap[index])
		return str(index)

	def value(self, proxyColumn, proxyRow):
		if self.__rowMap is None:
			return self.__model.value(self.__columnMap[proxyColumn], proxyRow)
		return self.__model.value(self.__columnMap[proxyColumn], self.__rowMap[proxyRow])

	def setValue(self, col, row, value):
		if self.__rowMap is not None:
			row = self.__rowMap[row]
		self.__model.setValue(self.__columnMap[col], row, value)

	def setValues(self, cols, rows, values):
		for i in xrange(len(cols)):
			cols[i] = self.__columnMap[cols[i]]
		if self.__rowMap is not None:
			for i in xrange(len(rows)):
				rows[i] = self.__rowMap[rows[i]]
		self.__model.setValues(cols, rows, values, self.__columnMap)

	# additional methods
	def setHideZeroColumns(self, state):
		self.__hideZeroColumns = state
		self.__refreshColumnMap()

	def setVisibleRows(self, indices=None):
		self.__zeroColumns = [None] * self.__model.columnCount()
		self.__rowMap = None if indices is None else indices[::]