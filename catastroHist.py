# -*- coding: utf-8 -*-
'''
/***************************************************************************
Name:           catastroHist.py

                                 A QGIS plugin
                                 
Plugin:     catastroesp - Catastro de España
Purpose:    Permite cargar mediante WMS el catastro histórico
        --------------------------------------------------------------------
        begin                : 2016-06-06
        git sha              : $Format:%H$
        Codigo Corregido     : Agustín Solabre
        email                : agusass@hotmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
'''

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from PyQt5 import uic

import os
from osgeo import ogr, osr
from qgis.core import *
from time import sleep

import urllib
import json

from .config import configuration        # CLASE DE CONFIGURACIÓN DE VARIABLES DEL PROGRAMA
from .functions3 import Functions        # CLASE DE CONFIGURACIÓN DE FUNCIONES GENERALES

current_configuration = configuration()

# VARIABLES
srcVal = current_configuration.general["EPSG"]

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), './menus/catastroHist.ui'))


class catastroHist(QDialog, FORM_CLASS):
    def __init__(self, iface,parent=None):
        """Constructor."""
        super(catastroHist, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface;
        self.fun = Functions()

        self.nombre_plugin = os.path.basename(os.path.dirname(__file__))

        self.setWindowIcon(QIcon(f':/plugins/{self.nombre_plugin}/iconos/cat_historico.jpg'))
        self.buttonBoxOK.clicked.connect(self.cargacatastroHist)


    def encode(self,text):
        """
        For printing unicode characters to the console.
        """
        return text.encode('utf-8')
        
    def cargacatastroHist(self):
        # Funcion creada por ASS
        # PERMITE CARGAR EL CATASTRO DE UNA DETERMINADA FECHA

        #Parámetro TIME
        # Este WMS incorpora un parámetro propio TIME para poder dar un servicio histórico de la cartografía catastral el formato de este parámetro es:
        # TIME = YYYY-MM-DD (siendo: YYYY el año, MM el mes y DD el día)
        #   Ejemplo de petición del servicio WMS con cartografía a la fecha del 23 de octubre de 2003
        #   http://ovc.catastro.meh.es/Cartografia/WMS/ServidorWMS.aspx?TIME=2003-10-23& . 
        #   Solo está disponible la cartografía histórica desde que se tiene cartografía en formato digital (no anterior al año 2002).
        #
        #   url = u'http://ovc.catastro.meh.es/Cartografia/WMS/ServidorWMS.aspx?TIME='
        #   http://ovc.catastro.meh.es/Cartografia/WMS/ServidorWMS.aspx?contextualWMSLegend=0&crs=EPSG:25830&dpiMode=7&featureCount=10&format=image/png&layers=PARCELA&styles=&TIME%3D2003-10-23%26
        #   contextualWMSLegend=0&crs=EPSG:25830&dpiMode=7&featureCount=10&format=image/png&layers=PARCELA&styles=&url=http://ovc.catastro.meh.es/Cartografia/WMS/ServidorWMS.aspx?TIME%3D2003-10-23%26

        # url = u'contextualWMSLegend=0&crs=EPSG:25830&dpiMode=7&featureCount=10&format=image/png&layers=PARCELA&styles=&url=http://ovc.catastro.meh.es/Cartografia/WMS/ServidorWMS.aspx?TIME='
        # layers=PARCELA&layers=TXTPARCELA
        url = u'contextualWMSLegend=0&crs=EPSG:'+str(srcVal)+'&dpiMode=7&featureCount=10&format=image/png&layers=PARCELA&layers=TXTPARCELA&styles=&styles=&url=http://ovc.catastro.meh.es/Cartografia/WMS/ServidorWMS.aspx?TIME='
        dTime = self.dteTIME.dateTime()
        Time = dTime.toString ('yyyy-MM-dd')
        estilo = "Default"
        
        layer = self.iface.addRasterLayer(url+Time, u'Catastro '+Time, 'wms')
        if layer == None:
            QgsMessageLog.logMessage( "Capa no encontrada: " + u'Catastro '+Time,(self.nombre_plugin).upper())
        elif not layer.isValid():
            QgsProject.instance().removeMapLayer(layer.id())
            self.close()
            text = "Fallo al cargar la capa: " + u'Catastro '+Time
            self.fun.showMessageERR(text)
            return
            # QgsMessageLog.logMessage(text ,(self.nombre_plugin).upper())
        else:
            if estilo != "Default":
                layer.loadNamedStyle(self.current_configuration.general["carpeta_estilos"] + u'/' +  estilo)

        pass
        