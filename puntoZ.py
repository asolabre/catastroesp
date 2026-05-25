# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name:               puntoZ.py
Purpose:            Tools for plugin catastroesp

        --------------------------------------------------------------------
        begin                : 2019-09-11
        git sha              : $Format:%H$
        Codigo Corregido     : Agustín Solabre
        email                : agusass@hotmail.com ***************************************************************************/
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QApplication, QTextEdit

from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtCore import QRect

from qgis.gui import QgsMapTool, QgsDialog

import os

from .config import configuration        # CLASE DE CONFIGURACIÓN DE VARIABLES DEL PROGRAMA
from .functions3 import Functions        # CLASE DE CONFIGURACIÓN DE FUNCIONES GENERALES

current_configuration = configuration()

# VARIABLES
srcVal = current_configuration.general["EPSG"]

class puntoZ(QgsMapTool):

    def __init__(self,canvas, iface, action):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas    
        self.fun = Functions()
        
        self.nombre_plugin = os.path.basename(os.path.dirname(__file__))
        
        cursor = QCursor()
        cursor.setShape(Qt.CrossCursor)
        iface.mapCanvas().setCursor(cursor)
        self.iface = iface
        self.setAction(action)
        self.action = action
    

    def canvasPressEvent(self, event):
        pass

    def canvasMoveEvent(self, event):
        pass

    def canvasReleaseEvent(self, event):
        #Get the click
        x = event.pos().x()
        y = event.pos().y()
        
        QApplication.setOverrideCursor(Qt.WaitCursor)
        layerAct = self.iface.activeLayer()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        Zmdt = self.fun.Zmdt(point, self.iface, pintar='NO')
        Result = self.fun.getJCCMMuniProv(point, self.iface, pintar='NO')

        if Zmdt == 'Error':
            textResult = u'Elevación: %s\n'%("SIN DATOS")
        else:
            textResult = u'Elevación: %s\n'%("{:.3f}".format(Zmdt))
        textResult+= u'  (Modelo Digital del Terreno IGN 5 m.)\n\n'
        textResult+= u'X: %s\n'%("{:.3f}".format(point[0]))
        textResult+= u'Y: %s\n'%("{:.3f}".format(point[1]))
        textResult+= u'  (UTM30-ETRS89)\n\n'
        
        textResult+= u'Provincia: %s\n'%Result[1]
        textResult+= u'Municipio: %s\n'%Result[0]

        # Presentar mensaje en pantalla
        for w in self.iface.mainWindow().findChildren(QgsDialog):
            w.close()
        
        main_window = self.iface.mainWindow()
        dialog = QgsDialog(main_window,
                           fl=Qt.WindowFlags(),
                           orientation=Qt.Horizontal)
        textEdit = QTextEdit(dialog)
        textEdit.setGeometry(QRect(10, 10, 200, 200))
        textEdit.setObjectName("textEdit")
        textEdit.setText(textResult)
        dialog.resize(340, 220)
        dialog.setWindowTitle('DATOS DEL PUNTO')
        dialog.setWindowIcon(QIcon(f':/plugins/{self.nombre_plugin}/iconos/logo_general.jpg'))

        QApplication.restoreOverrideCursor()
        dialog.show()
        pass


