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
import os
import languageSupport

TOOLTIPDIRECTORY = os.path.join(WORKDIRECTORY, "toolTips")
# @TODO: move to own file, add text and gif connectiondict
class toolTipMovie(QWidget):
    def __init__(self, rect, parent=None):
        super(toolTipMovie, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(rect)
        
        self.inText = ""
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(3,3,3,3)
        self.setLayout(self.layout)

    def toolTipExists(self, imageName):
    	files = os.listdir(TOOLTIPDIRECTORY)
    	if "%s.gif"%imageName in files:
    		return True
    	return False
    
    def setLanguage(self, inLanguage, inText):
    	try:
    		self.inText = languageSupport.languageDict[inLanguage][inText]
    	except:
    		pass
    		
    def setGifImage(self, gifName):
    	gifImage = os.path.join(TOOLTIPDIRECTORY, "%s.gif"%gifName )
    	self.movie = QMovie( gifImage )
        size = self.geometry().height()
        self.movie.setScaledSize(QSize(size, size))
        self.movie.setCacheMode( QMovie.CacheAll )
        self.textLabel = QTextEdit(self.inText)
        self.textLabel.setMinimumWidth(size)
        self.textLabel.setMaximumWidth(size)
        self.textLabel.setEnabled(False)
        self.gifLabel = QLabel()
        self.gifLabel.setMovie( self.movie )
        self.movie.start()

        self.layout.addWidget(self.gifLabel)
        self.layout.addWidget(self.textLabel)

