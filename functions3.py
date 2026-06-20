# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name:           functions3.py
                                 A QGIS plugin
Plugin:     jccm_bar3 / catastroesp
Purpose:    Funciones generales
        --------------------------------------------------------------------
        begin                : 2019-09-03
        git sha              : $Format:%H$
        copyright            : (C) 2019 by JCCM. Dirección General de Carreteras
        Codigo               : Agustín Solabre (JCCM)
        email                : gis.carreteras@jccm.es
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.PyQt.QtGui import (QIcon, QColor, QCursor,        # Sustituimos librería PyQt5.QtGui por qgis.PyQt.QtGui
                        QFont, QPainter, QPainterPath, QFontMetrics)

from qgis.PyQt.QtCore import (Qt, QSettings, QTranslator, QCoreApplication,
                        QPoint, QRectF, QUrl, QUrlQuery, QEventLoop, QVariant)

# from qgis.PyQt.QtCore import *

from qgis.PyQt.QtWidgets import (QAction, QApplication, QWidget, QPushButton, QMessageBox, QToolButton,
                        QMenu, QProgressBar, QTextEdit)     # Sustituimos librería PyQt5.QtWidgets por qgis.PyQt.QtWidgets

# https://qgis.org/pyqgis/3.0/gui/index.html
from qgis.gui import QgsVertexMarker, QgsMapCanvasItem, QgsMapToolEmitPoint

# https://qgis.org/pyqgis/3.0/core/index.html
from qgis.core import (Qgis, QgsPointXY, QgsVectorLayer, QgsGeometry, QgsPoint, QgsRectangle,
                        QgsMessageLog, QgsProject, QgsField, QgsCoordinateReferenceSystem,QgsExpression,
                        QgsFeatureRequest,QgsFeature, QgsMapLayer, QgsVectorFileWriter, QgsWkbTypes,
                        QgsSpatialIndex, QgsLayerTreeLayer, QgsVectorDataProvider, QgsGeometryUtils,
                        QgsCoordinateTransformContext, QgsProcessingFeedback, QgsCoordinateTransform,
                        QgsNetworkAccessManager)

from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply

from qgis.utils import iface

from osgeo import ogr, gdal, osr

import os, glob, codecs
import re
from os import fdopen, remove
from os.path import isfile, join

import sys
import zipfile, io
import linecache

import json

# Importaciones de módulos relacionados con URLs
import urllib.parse
import urllib.request
from urllib.error import URLError, HTTPError

# Importaciones de requests
import requests
from requests.exceptions import Timeout, ConnectionError, RequestException

import webbrowser

# Importaciones redundantes de módulos de tiempo
import timeit
import time
from socket import timeout
import datetime

import math

# Importaciones de XML
import xml.etree.ElementTree as ET
from xml.dom import minidom
from xml.dom.minidom import parse, parseString

from tempfile import mkstemp
from shutil import move

import locale

import shapely
from shapely.wkt import loads as wkt_loads
from shapely.geometry import shape

from .catastroDescPolig_dialog import catastroDescPolig_dialog   # Carga de menú de descargas  de Ficheros
from .config import configuration        # CLASE DE CONFIGURACIÓN DE VARIABLES DEL PROGRAMA

current_configuration = configuration()

# VARIABLES
crsVal = current_configuration.general["EPSG"]
TIMEOUT_SEGUNDOS = 5

# CLASES PROGRAMADAS
class Functions:
    def __init__(self):
        self.qs = QSettings()
        self.conf = configuration()

        self.nombre_plugin = os.path.basename(os.path.dirname(__file__))

        # CONFIGURACIÓN DEL SISTEMA
        self.enableUseOfGlobalCrs()

        pass

    """
    ##################################################################################################################
    ##################################################################################################################
    ###################                                                                            ###################
    ###################                    RUTINAS DE CONFIGURACION INICIAL                        ###################
    ###################                                                                            ###################
    ##################################################################################################################
    ##################################################################################################################
    """

    def enableUseOfGlobalCrs(self):
        #   Por medio de esta rutina se configura el sistema para que el CRS de las nuevs capas sea el de proyecto, y no pregunte
        # PyQGIS like a Boss  http://pyqgis.blogspot.com.es/
        # 'set new Layers to use the Project-CRS'

        # MODIFICAR A EPSG ACTIVO

        self.qs = QSettings()
        self.oldValidation = self.qs.value(str("/Projections/defaultBehaviour"))
        self.qs.setValue( "/Projections/defaultBehaviour", "useProject" )    # CRS para nuevas capas, por defecto usa el del proyecto
        self.qs.setValue( "/Projections/layerDefaultCrs", "EPSG:"+str(crsVal) )

    def buscaUnidadesGDB(self, listGDB, GDBCLASS):
    # La rutina permite buscar el fichero de GDB en las diferentes unidades en el orden del fichero CONFIGURACION
    #******************************************************************
    # COMPROBAMOS QUE EXISTE LA GDB/GDBCLASS ENTRE LAS DE LA LISTA
    #******************************************************************
        driver = ogr.GetDriverByName("OpenFileGDB")

        GDB = ''
        for gdbData in listGDB:
            try:
                GDB = gdbData

                data = driver.Open(GDB, 0)
                if data is not None:
                    for i in data:
                        foo = i.GetName()
                        if i.GetName() == GDBCLASS:
                            return GDB
                else:
                    GDB = ''
            except:
                continue
        print ('La GDB es ', GDB)
        return GDB


    """
    ##################################################################################################################
    ##################################################################################################################
    ###################                                                                            ###################
    ###################               RUTINAS DE SALIDAS DE MENSAJES EN PANTALLA                   ###################
    ###################                                                                            ###################
    ##################################################################################################################
    ##################################################################################################################
    """

    def showMessage(self,text,text2="",tittle="",):
        # showMessage(self,text,text2="",tittle,)
        #   Mensaje de INFORMACION
        QApplication.restoreOverrideCursor() # Se restituye cursor
        if tittle!="":
            tittle=(self.nombre_plugin).upper()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(text)
        msg.setWindowIcon(QIcon(f':/plugins/{self.nombre_plugin}/iconos/logo_general.jpg'));
        #   setWindowIcon(QIcon(':/plugins/Spanish_Inspire_Catastral_Downloader/icon.png'));
        msg.setInformativeText(text2)
        msg.setWindowTitle(tittle)
        msg.exec_()

    def showMessageYESNO(self,text,text2="",tittle="",):
        # showMessageYESNO(self,text,text2="",tittle=(self.nombre_plugin).upper(),)
        #       Mensaje YESNO
        # resp == 1024:       # Se ha pulsado ACEPTAR
        # resp == 4194304:    # Se ha pulsado CANCELAR
        QApplication.restoreOverrideCursor() # Se restituye cursor
        if tittle!="":
            tittle=(self.nombre_plugin).upper()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons (QMessageBox.Ok | QMessageBox.Cancel)
        msg.setDefaultButton(QMessageBox.Cancel)
        msg.setText(text)
        msg.setWindowIcon(QIcon(f':/plugins/{self.nombre_plugin}/iconos/logo_general.jpg'))
        #msg.setText(unicode(text).encode('utf-8'))
        msg.setInformativeText(text2)
        msg.setWindowTitle(tittle)
        retval = msg.exec_()
        # print u"Valor del mensage del botón pulsado: ", retval
        return retval

    def showMessWarnYESNO(self,text,text2="",tittle="",):
        # showMessageYESNO(self,text,text2="",tittle=(self.nombre_plugin).upper(),)
        #       Mensaje YESNO
        # resp == 1024:       # Se ha pulsado ACEPTAR
        # resp == 4194304:    # Se ha pulsado CANCELAR
        QApplication.restoreOverrideCursor() # Se restituye cursor
        if tittle!="":
            tittle=(self.nombre_plugin).upper()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons (QMessageBox.Ok | QMessageBox.Cancel)
        msg.setDefaultButton(QMessageBox.Cancel)
        msg.setText(text)
        msg.setWindowIcon(QIcon(f':/plugins/{self.nombre_plugin}/iconos/logo_general.jpg'))
        #msg.setText(unicode(text).encode('utf-8'))
        msg.setInformativeText(text2)
        msg.setWindowTitle(tittle)
        retval = msg.exec_()
        # print u"Valor del mensage del botón pulsado: ", retval
        return retval

    def showMessageERR(self,text,text2="",tittle="",):
        # showMessageERR(text,text2="",tittle=(self.nombre_plugin).upper(),)
        # Mensaje error
        QApplication.restoreOverrideCursor() # Se restituye cursor
        if tittle!="":
            tittle=(self.nombre_plugin).upper()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(text)
        msg.setWindowIcon(QIcon(f':/plugins/{self.nombre_plugin}/iconos/logo_general.jpg'))
        #msg.setText(unicode(text).encode('utf-8'))
        msg.setInformativeText(text2)
        msg.setWindowTitle(tittle)
        msg.exec_()

    def showWorkin(self,text='PACIENCIA',text2="ESTAMOS TODAVÍA TRABAJANDO",tittle="",):
        # showMessage(self,text,text2="",tittle,)
        #   Mensaje de INFORMACION DE WORKIN
        QApplication.restoreOverrideCursor() # Se restituye cursor
        if tittle!="":
            tittle=(self.nombre_plugin).upper()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(text)
        msg.setWindowIcon(QIcon(f':/plugins/{self.nombre_plugin}iconos/logo_general.jpg'));
        msg.setInformativeText(text2)
        msg.setWindowTitle(tittle)
        msg.exec_()


    """
    ##################################################################################################################
    ##################################################################################################################
    ###################                                                                            ###################
    ###################               RUTINAS DE SALIDAS DE MENSAJES EN PANTALLA                   ###################
    ###################                               JCCM                                         ###################
    ##################################################################################################################
    ##################################################################################################################
    """

    def showJCCMessage(self,text,text2="",tittle="JCCM",):
        # showJCCMessage(self,text,text2="",tittle="JCCM",)
        #   Mensaje de INFORMACION
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(text)
        msg.setWindowIcon(QIcon(f':/plugins/{self.nombre_plugin}iconos/logo_general.jpg'));
        #   setWindowIcon(QIcon(':/plugins/Spanish_Inspire_Catastral_Downloader/icon.png'));
        msg.setInformativeText(text2)
        msg.setWindowTitle(tittle)
        msg.exec_()

    def showJCCMessageYESNO(self,text,text2="",tittle="JCCM",):
        # showJCCMessageYESNO(self,text,text2="",tittle="JCCM",)
        #       Mensaje YESNO
        # resp == 1024:       # Se ha pulsado ACEPTAR
        # resp == 4194304:    # Se ha pulsado CANCELAR

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons (QMessageBox.Ok | QMessageBox.Cancel)
        msg.setDefaultButton(QMessageBox.Cancel)
        msg.setText(text)
        msg.setWindowIcon(QIcon(f':/plugins/{self.nombre_plugin}iconos/logo_general.jpg'))
        #msg.setText(unicode(text).encode('utf-8'))
        msg.setInformativeText(text2)
        msg.setWindowTitle(tittle)
        retval = msg.exec_()
        # print u"Valor del mensage del botón pulsado: ", retval
        return retval

    def showJCCMessWarnYESNO(self,text,text2="",tittle="JCCM",):
        # showJCCMessageYESNO(self,text,text2="",tittle="JCCM",)
        #       Mensaje YESNO
        # resp == 1024:       # Se ha pulsado ACEPTAR
        # resp == 4194304:    # Se ha pulsado CANCELAR

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons (QMessageBox.Ok | QMessageBox.Cancel)
        msg.setDefaultButton(QMessageBox.Cancel)
        msg.setText(text)
        msg.setWindowIcon(QIcon(f':/plugins/{self.nombre_plugin}iconos/logo_general.jpg'))
        #msg.setText(unicode(text).encode('utf-8'))
        msg.setInformativeText(text2)
        msg.setWindowTitle(tittle)
        retval = msg.exec_()
        # print u"Valor del mensage del botón pulsado: ", retval
        return retval

    def showJCCMessageERR(self,text,text2="",tittle="JCCM",):
        # showJCCMessageERR(text,text2="",tittle="JCCM",)
        # Mensaje error
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(text)
        msg.setWindowIcon(QIcon(f':/plugins/{self.nombre_plugin}iconos/logo_general.jpg'))
        #msg.setText(unicode(text).encode('utf-8'))
        msg.setInformativeText(text2)
        msg.setWindowTitle(tittle)
        msg.exec_()

    def trabajando(self, text, busyDlg):
        if text != u'--- CERRAR ---':
            main_window = iface.mainWindow()
            busy_indicator_dialog = QgsBusyIndicatorDialog(text, main_window,
                                                           fl=Qt.WindowFlags())
            busy_indicator_dialog.setWindowTitle( self.nombre_plugin )
            busy_indicator_dialog.setMinimumWidth( 250 )

            busy_indicator_dialog.show()
            return busy_indicator_dialog
        else:
            busyDlg.destroy()

    def PrintException(self):
        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        basename = os.path.basename(filename)
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        # result = 'ERROR EN ({}, LINEA {} "{}"): {}'.format(basename, lineno, line.strip(), exc_obj)
        # result = 'ERROR EN ({}, LINEA {}):\n\n {} {}'.format(basename, lineno, line.strip(), exc_obj)
        result = f'ERROR EN ({basename}, LINEA {lineno}):\n\n {line.strip()} {exc_obj}'
        # print (result)
        return result


    """
    ##################################################################################################################
    ##################################################################################################################
    ###################                                                                            ###################
    ###################        RUTINAS DE ANALISIS Y TRANSFORMACION DE VARIABLES Y FICHEROS        ###################
    ###################                                                                            ###################
    ##################################################################################################################
    ##################################################################################################################
    """

    def isFloat(self,number):
        try:
            inNumberfloat = float(number)
            return True
        except ValueError:
            return False

    def completarCeros(self,text,num):
        texto = str(text)
        longitud= len(texto)

        while (longitud < num):
            texto = "0" +texto
            longitud = len(texto)
        return texto

    def cambiaelemlista(self,lista,elem,valor):
        lista[elem]=valor
        return lista

    def Extract_PlainText(self, label):
        Rtf_text = label.text()
        # Temp_Obj = QtGui.QTextEdit()
        Temp_Obj = QTextEdit()
        Temp_Obj.setText(Rtf_text)
        Plain_text = Temp_Obj.toPlainText()
        del Temp_Obj
        return Plain_text

    def replace(self, file_path, pattern, subst):
        # Reemplaza en el fichero 'file_path' la cadena 'pattern' con 'subst'

        #Create temp file
        fh, abs_path = mkstemp()
        with fdopen(fh,'w') as new_file:
            with open(file_path) as old_file:
                for line in old_file:
                    new_file.write(line.replace(pattern, subst))
        #Remove original file
        remove(file_path)
        #Move new file
        move(abs_path, file_path)

    def mostrarPK(self,val,num):
        # mostrarPK(self,val,num)
        #   FUNCIÓN de presentación de un valor kilométrico (numero) KK.MMMmmm en formato (string) KK+MMM.mmm
        #   return texto
        # Creada ASS
        # print val
        if ((val != None) and (str(val) != 'nan')):
            km = int(val)
            m = round((val - km)*1000,num)
            texto = str(km) + "+" + "{:0{}.{}f}".format( m, 4+num, num )
            return texto
        else:
            return 'None'

    def encode(self,text):
        # For printing unicode characters to the console.

        return text.encode('utf-8')

    def timeTOhms(self,time):
        # import datetime
        x=datetime.timedelta(seconds=int(time))
        # time.strftime('%H:%M:%S', time.gmtime(12345))
        return x
        pass

    def pair(self, list):
        '''Iterate over pairs in a list '''
        for i in range(1, len(list)):
            yield list[i-1], list[i]


    """
    ##################################################################################################################
    ##################################################################################################################
    ###################                                                                            ###################
    ###################                      RUTINAS DE FEATURES Y ZOOM                            ###################
    ###################                                                                            ###################
    ##################################################################################################################
    ##################################################################################################################
    """

    def dibujarPunto(self,x,y,iface,r=0,g=255,b=0):
        # dibujarPunto(self,x,y,iface,r=0,g=255,b=0)
        #   Dibuja un punto de un color RGB
        m = QgsVertexMarker(iface.mapCanvas())
        m.setCenter(QgsPointXY(x, y))
        m.setColor(QColor(r, g, b))
        m.setIconSize(5)
        m.setIconType(QgsVertexMarker.ICON_BOX) # or ICON_CROSS, ICON_X
        m.setPenWidth(3)
        return m


    def zoomToOgrGeometriesLin(self, iface, geometries):
        # # zoomToOgrGeometriesLin(self,iface,geometries)
        # #   Hace zoom a un grupo de geometrias

        # ###################################################################################
        # # PROBLEMA DE LAS VERSIONES DE QGIS
        # versionQGS = Qgis.QGIS_VERSION
        # ###################################################################################
        cur_env = None

        for geom in geometries:
            if geom is None or geom.IsEmpty():
                continue

            env = geom.GetEnvelope()
            minx, maxx, miny, maxy = env

            # descartar envelopes degenerados (0,0,0,0 o puntos)
            if minx == maxx and miny == maxy:
                continue

            if cur_env is None:
                cur_env = [minx, maxx, miny, maxy]
            else:
                cur_env[0] = min(cur_env[0], minx)
                cur_env[1] = max(cur_env[1], maxx)
                cur_env[2] = min(cur_env[2], miny)
                cur_env[3] = max(cur_env[3], maxy)

        if cur_env is None:
            # no había geometrías válidas
            return

        rectangle = QgsRectangle(cur_env[0], cur_env[2],
                                 cur_env[1], cur_env[3])

        iface.mapCanvas().zoomToFeatureExtent(rectangle)
        iface.mapCanvas().refresh()


    def zoomToGeometry(self,iface,geometry, Nomark = 'SI'):
        # zoomToGeometry(self,iface,geometry)
        #   Hace zoom a una geometria

        geomtype = geometry.GetGeometryType()
        # print geomtype
        if geomtype == ogr.wkbPoint or geomtype == ogr.wkbPoint25D :

            margin = 250
            rectangle = QgsRectangle(geometry.GetX() -margin ,geometry.GetY() - margin ,geometry.GetX() +margin ,geometry.GetY() + margin)
            # print rectangle
            iface.mapCanvas().setExtent(rectangle)
            iface.mapCanvas().refresh()

            if Nomark == 'SI':
                m = QgsVertexMarker(iface.mapCanvas())
                m.setCenter(QgsPointXY(geometry.GetX() , geometry.GetY() ))
                m.setColor(QColor(0, 255, 0))
                m.setIconSize(5)
                m.setIconType(QgsVertexMarker.ICON_BOX) # or ICON_CROSS, ICON_X
                m.setPenWidth(3)
        else:
            e = geometry.GetEnvelope()
            # print e
            rectangle = QgsRectangle(e[0],e[2],e[1],e[3])

            iface.mapCanvas().zoomToFeatureExtent(rectangle)
            iface.mapCanvas().refresh()

            if Nomark == 'SI':
                m = QgsVertexMarker(iface.mapCanvas())
                m.setCenter(QgsPointXY(geometry.Centroid().GetX(), geometry.Centroid().GetY()))
                m.setColor(QColor(0, 255, 0))
                m.setIconSize(5)
                m.setIconType(QgsVertexMarker.ICON_BOX) # or ICON_CROSS, ICON_X
                m.setPenWidth(3)

    def zoomELEMENTO(self, iface, capaDATOS, datoBUSCADO, ordenDATO, listaCAMPOS, ordenCAMPO, escala ):
        # Rutina que hace zoom a un elemento o elementos seleccionados en el combo (C) ASS
        #   capaDATOS, Nombre de la capa en la que se va a buscar
        #   datoBUSCADO, Puede ser un dato único o con separadores tipo ' | '
        #   ordenDATO, 0 por defecto, caso único; si es un elemento con separadores ' | ' coge el indicado 0,1,2...
        #       ej: CM-332 | EX-2016/007 | Alatoz, 0=CM-332, 1=EX-2016/007, 2=Alatoz
        #   listaCAMPOS, lista completa o parcial de atributos de la capa
        #   ordenCAMPO, posición en listaCAMPOS del campo en que buscar datoBUSCADO
        #   escala, 0 por defecto, escala al BBOX del elemento, si !=0 se hace zoom a esa escala
        canvas = iface.mapCanvas()

        allLayers = canvas.layers()
        n = len(allLayers)
        for i in range(0, n):
            if allLayers[i].name() == capaDATOS:
                break
        layer = allLayers[i]
        iface.setActiveLayer(layer)
        # iface.legendInterface().setLayerVisible(layer, True)
        QgsProject.instance().layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(True)

        # Se obtiene el valor a buscar de la selección del combo
        valorBUSCADO= (datoBUSCADO.split(' | '))[ordenDATO]

        # Se obtiene el campo de la lista de campos
        campo = listaCAMPOS[ordenCAMPO]

        # Obtiene un iterador de elementos desde una expresión
        consulta = u'"'+campo+'" = \''+valorBUSCADO+'\''
        expr = QgsExpression( consulta )
        it = layer.getFeatures( QgsFeatureRequest( expr ) )

        # Se construye una lista de IDs de elementos del resultado obtenido antes
        ids = [j.id() for j in it]

        # Selecciona elementos con los ids obtenidos
        feats=layer.selectByIds( ids )


        # Zoom a los elementos seleccionados
        canvas.zoomToSelected()
        if escala != 0:
            canvas.zoomScale(escala)
            # self.zoomToGeometry(self.iface,point)
            # self.zoomToQgsFeature(self.iface,feats[0])
        pass


    """
    ##################################################################################################################
    ##################################################################################################################
    ###################                                                                            ###################
    ################### RUTINAS DE GESTION DE RUTAS Y DATOS DE GDB (CARRETERA Y PK) Y TOPOGRÁFICOS ###################
    ###################                ( CONTRA APIREST DE GEODATABASE CARRETERAS )                ###################
    ###################                                                                            ###################
    ##################################################################################################################
    ##################################################################################################################
    """

    def getRoadLmits(self,road_name):
        # getRoadLmits(self,road_name)
        #   Rutina de obtención del minimoM y maximoM de una ruta
        #       limits.append([min_m,max_m])
        #   return limits

        url = self.conf.general["rest_carreteras"]
        posSPC = road_name.find(' ')
        r_name = road_name
        if posSPC != -1 :
            r_name = road_name[:posSPC+2]
            whereCONS = self.conf.lrs["identificador_carretera_carreteras"] + " like '" + r_name + u"%' and Matricula <> '9000'"
        else:
            whereCONS = self.conf.lrs["identificador_carretera_carreteras"] + " = '" + r_name + u"' and Matricula <> '9000'"


        values = {'where' : whereCONS,
        # values = {'where' :  self.conf.lrs["identificador_carretera_carreteras"] + " = '" + road_name + u"'",
                  'text': '',
                  'objectIds': '',
                  'geometryType' : 'esriGeometryPolyline',
                  'returnGeometry' : 'true',
                 'returnM': 'true' ,
                 'f': 'json'}

        str_values = {}
        for k, v in values.items():
            str_values[k] = unicode(v).encode('utf-8')
        data = urllib.parse.urlencode(str_values)

        try:
            response = requests.get(url+data, timeout=TIMEOUT_SEGUNDOS)
            response.raise_for_status()  # Lanza excepción si hay error HTTP (4xx, 5xx)
            response = response.json()  # Esto ya es el JSON parseado
        except requests.exceptions.Timeout:
            QApplication.restoreOverrideCursor()
            txt = u"Timeout: El servidor de carreteras no responde\n"
            self.showMessageERR(txt, text2="", tittle=self.nombre_plugin + " - Timeout")
            return
        except requests.exceptions.ConnectionError:
            QApplication.restoreOverrideCursor()
            txt = u"Error de conexión a internet (SERVIDOR CARRETERAS)\n"
            txt += self.PrintException()
            self.showMessageERR(txt, text2="", tittle=self.nombre_plugin + " - Error de conexión")
            return
        except requests.exceptions.RequestException as e:
            QApplication.restoreOverrideCursor()
            txt = u"Error en la petición HTTP: {}\n".format(str(e))
            txt += self.PrintException()
            self.showMessageERR(txt, text2="", tittle=self.nombre_plugin + " - Error HTTP")
            return
        except json.JSONDecodeError as e:
            QApplication.restoreOverrideCursor()
            txt = u"Error al parsear la respuesta JSON: {}\n".format(str(e))
            self.showMessageERR(txt, text2="", tittle=self.nombre_plugin + " - Error JSON")
            return

        # try:
            # response = json.load(urllib.request.urlopen(url+data, timeout=TIMEOUT_SEGUNDOS))
        # except urllib.error.URLError as e:
            # QApplication.restoreOverrideCursor()
            # txt = u"Error de conexión a internet (SERVIDOR CARRETERAS)\n"
            # txt += self.PrintException()
            # self.showMessageERR(txt, text2="", tittle=self.nombre_plugin+" - Error de conexión a internet")
            # return
        # except TimeoutError:
            # QApplication.restoreOverrideCursor()
            # txt = u"Timeout: El servidor de carreteras no responde\n"
            # self.showMessageERR(txt, text2="", tittle=self.nombre_plugin+" - Timeout")
            # return

        # try:
            # response = json.load(urllib.request.urlopen(url+data))
        # except:
            # QApplication.restoreOverrideCursor()
            # txt = u"Error de conexión a internet (SERVIDOR CARRETERAS)\n"
            # txt+= self.PrintException()
            # self.showMessageERR(txt,text2="",tittle=self.nombre_plugin+" - Error de conexión a internet",)
            # return

        features =  response["features"]    # Los distintos features encontrados en la búsqueda


        # print features
        # print ('Encontrados %d elementos'%(len(features)))

        if features == []:
            return "No hay features"
        limits = []

        for feat in features:
            emes = []
            geometry = feat["geometry"]
            paths = geometry["paths"]
            for path in paths:
                for point in path:
                    if(point[2] is not None):
                        # print 'X - Y - M ', point[0], point[1], point[2]
                        emes.append(point[2])
            if(len(emes) > 0):
                # print emes
                min_m = min(emes)
                max_m =  max(emes)
                limits.append([min_m,max_m])
            else:
                # limits.append( [None,None])
                limits.append( [0,0])

        limits.sort(key=lambda x: x[0])
        # limits.sort()

        return limits

    def zoomToPk(self, iface,road_name, pk, pkDistEnt, disteje, tipomed = 'DISTPK', tipo_consultaCAPA = 'url'):
        # zoomToPk(self, iface,road_name, pk)
        #   Rutina de zoom a CARRETERA, PK, disteje
        #   return x,y
        #   return None

        # result = self.CtraPktoCoorsAcim(road_name, pk)
        if tipo_consultaCAPA == 'url':
            result = self.CtraPktoCoorsAcim(road_name, pk, pkDistEnt, tipomed)
        else:
            result = self.CtraPktoCoorsAcim_GPKG(road_name, pk, pkDistEnt, tipomed)

        if not self.isFloat(result[0]):
            return result
        else:
            # print 'Resultado - ', result[0], result[1]
            point = ogr.Geometry(ogr.wkbPoint)
            acim = result[2]
            x = result[0] + disteje * math.cos(acim*math.pi/180)
            y = result[1] - disteje * math.sin(acim*math.pi/180)

            point.AddPoint(x, y)
            self.zoomToGeometry(iface,point)
            return result[0], result[1]

    def CtraPktoCoorsAcim(self, road_name, pk, pkDistEnt = 0, tipomed = 'DISTPK'):
        # PRUEBA DE IDENTIFICACIÓN POR DISTANCIA A PK ANTERIOR
        # CtraPktoCoorsAcim(self, road_name, pk, pkDistEnt = 0, tipomed = 'DISTPK')
        #   road_name - Matrícula de la carretera
        #   pk        - Punto Km, en caso de tipomed = 'DISTPK' puede ser la placa entera solo
        #   pkDistEnt - Distancia a la placa de 'pk'. Si = 0 y tipomed = 'DISTPK', se evalúa la distancia por los decimales de pk
        #   tipomed - Flag de análisis del tipo de PK medido
        #       tipomed = 'DISTPK' - El Pk se ubica por distancia a la placa de PK anterior
        #       tipomed = 'CALIBRADO' - El Pk se ubica por interpolación entre las placas
        #   Rutina de transformación de CARRETERA, PK a X, Y, Acim
        #   return x,y
        #   return None

        url = self.conf.general["rest_carreteras"]

        # Caso de que road_name esté vacío
        if (road_name == ""):
            return 'Error: Carretera sin nombre'
        posSPC = road_name.find(' ')
        r_name = road_name
        if posSPC != -1 :
            r_name = road_name[:posSPC+2]
            whereCONS = self.conf.lrs["identificador_carretera_carreteras"] + " like '" + r_name + u"%' and Matricula <> '9000'"
        else:
            whereCONS = self.conf.lrs["identificador_carretera_carreteras"] + " = '" + r_name + u"' and Matricula <> '9000'"

        values = {'where' : whereCONS,
                  'text': '',
                  'objectIds': '',
                  'geometryType' : 'esriGeometryPolyline',
                  'returnGeometry' : 'true',
                  'returnM': 'true' ,
                  'f': 'json'}


        data = urllib.parse.urlencode(values)

        try:
            response = requests.get(url+data, timeout=TIMEOUT_SEGUNDOS)
            response.raise_for_status()  # Lanza excepción si hay error HTTP (4xx, 5xx)
            response = response.json()  # Esto ya es el JSON parseado
            features =  response["features"]
        except urllib.error.URLError as e:
            QApplication.restoreOverrideCursor()
            txt = u"Error de conexión a internet (SERVIDOR CARRETERAS)\n"
            txt += self.PrintException()
            txt += u"\n\nPROBAMOS A OBTENER DATOS DESDE EL SERVIDOR LOCAL DE SU CONFIGURACIÓN"
            self.showMessageERR(txt)
            return 'Error: No hay elementos'
        except TimeoutError:
            QApplication.restoreOverrideCursor()
            self.showMessageERR(u"Timeout: El servidor de carreteras no responde")
            return 'Error: Timeout'

        # try:
            # response = json.load(urllib.request.urlopen(url+data))
            # features =  response["features"]
        # except:
            # QApplication.restoreOverrideCursor()
            # txt = u"Error de conexión a internet (SERVIDOR CARRETERAS)\n"
            # txt+= self.PrintException()
            # txt+= u"\n\nPROBAMOS A OBTENER DATOS DESDE EL SERVIDOR LOCAL DE SU CONFIGURACIÓN"
            # self.showMessageERR(txt)
            # return 'Error: No hay elementos'

        nfeat = 1
        pkencontrado = 0
        acim = 360
        listLimites= []

        if len(features) == 0:
            return 'Error: Matricula Incorrecta'

        if tipomed == 'DISTPK':
            ###############################################################
            ######                                                   ######
            ######                tipomed = 'DISTPK'                 ######
            ######                                                   ######
            ###############################################################
            if pkDistEnt == 0:
                pkEnt = int(pk)
                pkDistEnt = (pk - pkEnt)*1000
            else:
                pkEnt = int(pk)

            # Busqueda de posición de PK entero
            for feat in features:
                npath = 1
                if pkencontrado == 1:
                    break
                # print nfeat, ' de ',len(features), ' features'
                if feat is not None:
                    geometry = feat["geometry"]
                    paths = geometry["paths"]
                    for path in paths:
                        # print (path)
                        path2D = []
                        for point in path:
                            path2D.append(QgsPoint(point[0],point[1]))
                        geomPath = QgsGeometry.fromPolyline(path2D)

                        posini = 0
                        posfin = len(path)-1
                        while path[posini][2] == None and posini<len(path)-1:    # Buscamos el primer punto del tramo sin valor None
                            # print ('posini ',posini, path[posini][2])
                            posini+=1
                        while path[posfin][2] == None and posfin>0:              # Buscamos el último punto del tramo sin valor None
                            # print ('posfin ',posfin, path[posfin][2])
                            posfin-=1
                        if path[posini][2] == None or path[posfin][2] == None:
                            continue

                        # print ('INI-  ',path[posini][2],'  FIN-  ',path[posfin][2])
                        if path[posini][2]<path[posfin][2]: # Sentido CRECIENTE
                            limites = [path[posini][2],path[posini][0],path[posini][1],path[posfin][2],path[posfin][0],path[posfin][1]]
                            sentido = 'CRECIENTE'
                        else:   # Sentido DECRECIENTE
                            limites = [path[posfin][2],path[posfin][0],path[posfin][1],path[posini][2],path[posini][0],path[posini][1]]
                            sentido = 'DECRECIENTE'
                        listLimites.append(limites)
                        # print '%s de %s paths - %s puntos'%(npath, len(paths), len(path))
                        # print limites
                        npointprev = 0
                        npoint = 1
                        if pkencontrado == 1:
                            break
                        Mprev = None
                        # Mprev = 0.0
                        while (Mprev == None and npointprev<len(path)):
                            Pprev = path[npointprev]
                            Pprev = ogr.Geometry(ogr.wkbPoint)
                            Pprev.AddPoint(path[npointprev][0], path[npointprev][1])
                            Xprev = path[npointprev][0]
                            Yprev = path[npointprev][1]
                            Mprev = path[npointprev][2]
                            sentido = 'CRECIENTE'
                            iniloop = npointprev+1
                            npointprev += 1
                        if npointprev == len(path):
                            break

                        for npoint in range(iniloop,len(path)):
                            point = path[npoint]
                            # print '    PRE {:.0f} {:.2f} {:.2f} {:.7f}'.format(npointprev, Xprev, Yprev, Mprev),
                            # print '    ACT {:.0f} {:.2f} {:.2f} {:.7f}'.format(npoint+1, point[0], point[1], point[2])
                            if(point[2] is not None):
                                if point[2] == pkEnt:   # El pkEnt es el vértice

                                    xPkEnt = point[0]
                                    yPkEnt = point[1]

                                    distOriPK = geomPath.lineLocatePoint(QgsGeometry.fromPointXY(QgsPointXY(xPkEnt,yPkEnt)))
                                    if sentido == 'CRECIENTE':
                                        # distOriPoint = distOriPK + 1000*pkDistEnt
                                        distOriPoint = distOriPK + pkDistEnt
                                    else:
                                        # distOriPoint = distOriPK - 1000*pkDistEnt
                                        distOriPoint = distOriPK - pkDistEnt
                                    # print (distOriPK, distOriPoint)

                                    pointResul = geomPath.interpolate(distOriPoint)
                                    # print (pointResul)
                                    if pointResul.isEmpty():
                                        return u'Error: Imposible cálculo'
                                    else:
                                        x = pointResul.asPoint().x()
                                        y = pointResul.asPoint().y()

                                    acim = 0
                                    # CALCULO DEL ACIMUT
                                    (sqDist, nearestPoint, afterVertex, leftOf) = geomPath.closestSegmentWithContext(QgsPointXY(x,y), 0.01)
                                    # print ('sqDist= ',sqDist, 'nearestPoint= ', nearestPoint, 'afterVertex= ', afterVertex, 'leftOf=', leftOf)
                                    if sentido == 'CRECIENTE':
                                        pointANT = geomPath.vertexAt(afterVertex)
                                        pointPOS = geomPath.vertexAt(afterVertex+1)
                                    else:
                                        pointANT = geomPath.vertexAt(afterVertex+1)
                                        pointPOS = geomPath.vertexAt(afterVertex)
                                    distSegm, acim = self.calcACIMUT(pointANT,pointPOS)
                                    # acim= res1[1]
                                    if acim < 0:
                                        acim += 360
                                    # print ('acim=', acim)

                                    pkencontrado = 1
                                    if point[2]> path[(point in path)+1][2]:
                                        sentido = 'DECRECIENTE'
                                    # print 'COINCIDE CON Punto %s M=%s'%(npoint, point[2])
                                    break

                                else:
                                    # Se debe analizar si el punto es M=Null
                                    if (pkEnt>=Mprev and pkEnt<point[2]) or (pkEnt<=Mprev and pkEnt>point[2]):
                                        # El pkEnt está entre el vértice previo y el siguiente
                                        if pkEnt>=Mprev and pkEnt<point[2]:
                                            sentido = 'CRECIENTE'
                                        else:
                                            sentido = 'DECRECIENTE'
                                        Psig = ogr.Geometry(ogr.wkbPoint)
                                        Psig.AddPoint(point[0], point[1])
                                        # print 'SENTIDO- %s , ENCONTRADO ENTRE Punto %s M=%s %s M=%s'%(sentido, npointprev, Mprev, npoint+1, point[2])
                                        r = (pkEnt - Mprev) / (point[2] - Mprev)
                                        modulo = r * (Pprev.Distance(Psig))

                                        alfa = math.atan2((point[1] - Yprev ) , (point[0]  - Xprev))

                                        xPkEnt = Xprev + modulo * math.cos(alfa)
                                        yPkEnt = Yprev + modulo * math.sin(alfa)

                                        pointQ = QgsGeometry.fromPointXY(QgsPointXY(xPkEnt,yPkEnt))
                                        distOriPK = geomPath.lineLocatePoint(pointQ)
                                        if sentido == 'CRECIENTE':
                                            # distOriPoint = distOriPK + 1000*pkDistEnt
                                            distOriPoint = distOriPK + pkDistEnt
                                        else:
                                            # distOriPoint = distOriPK - 1000*pkDistEnt
                                            distOriPoint = distOriPK - pkDistEnt
                                        # print (distOriPK, distOriPoint)

                                        pointResul = geomPath.interpolate(distOriPoint)
                                        # print (pointResul)
                                        if pointResul.isEmpty():
                                            return u'Error: Imposible cálculo'
                                        else:
                                            x = pointResul.asPoint().x()
                                            y = pointResul.asPoint().y()

                                        # # CALCULO DEL ACIMUT
                                        (sqDist, nearestPoint, afterVertex, leftOf) = geomPath.closestSegmentWithContext(QgsPointXY(x,y), 0.01)
                                        # print ('sqDist= ',sqDist, 'nearestPoint= ', nearestPoint, 'afterVertex= ', afterVertex, 'leftOf=', leftOf)
                                        if sentido == 'CRECIENTE':
                                            pointANT = geomPath.vertexAt(afterVertex)
                                            pointPOS = geomPath.vertexAt(afterVertex+1)
                                        else:
                                            pointANT = geomPath.vertexAt(afterVertex+1)
                                            pointPOS = geomPath.vertexAt(afterVertex)
                                        distSegm, acim = self.calcACIMUT(pointANT,pointPOS)
                                        if acim < 0:
                                            acim += 360
                                        # print ('acim=', acim)

                                        pkencontrado = 1
                                        break
                            else:
                                # M es None
                                pass

                            # El pkEnt no está en este segmento
                            npointprev += 1
                            npoint += 1
                            Pprev = point
                            Pprev = ogr.Geometry(ogr.wkbPoint)
                            Pprev.AddPoint(point[0], point[1])
                            Xprev = point[0]
                            Yprev = point[1]
                            Mprev = point[2]

                        npath += 1

                nfeat += 1

            if pkencontrado == 0 and features !=[] and listLimites != [] :
                # Analizamos los tramos entre paths para localizar el pkEnt en los huecos

                listLimites.sort()
                # for limites in listLimites:
                    # print limites
                Tramo0 = 0
                Mini0 = listLimites[0][0]
                Mfin0 = listLimites[0][3]
                Xfin0 = listLimites[0][4]
                Yfin0 = listLimites[0][5]
                for limites in listLimites[1:]:
                    Mini1 = limites[0]
                    Mfin1 = limites[3]
                    Xini1 = limites[1]
                    Yini1 = limites[2]
                    if (pkEnt>Mfin0 and pkEnt<Mini1):
                        # Encontramos el pkEnt en un hueco
                        # print 'Encontramos el pkEnt en un hueco -', Mfin0, Mini1

                        Pprev = ogr.Geometry(ogr.wkbPoint)
                        Pprev.AddPoint(Xfin0, Yfin0)
                        Psig = ogr.Geometry(ogr.wkbPoint)
                        Psig.AddPoint(Xini1, Yini1)

                        r = (pkEnt - Mfin0) / (Mini1 - Mfin0)
                        modulo = r * (Pprev.Distance(Psig))
                        alfa = math.atan2((Yini1-Yfin0) , (Xini1-Xfin0))
                        x = Xfin0 + modulo * math.cos(alfa)
                        y = Yfin0 + modulo * math.sin(alfa)
                        # print 'r=%s mod=%s alfa=%s '%(r,modulo,alfa)
                        # print 'Xfin0=%s Yfin0=%s Xini1=%s Yini1=%s'%(Xfin0, Yfin0, Xini1, Yini1)
                        res1 = self.calcACIMUT(QgsPointXY(Xfin0, Yfin0),QgsPointXY(Xini1, Yini1))
                        acim= res1[1]
                        # if acim < 0:
                            # acim += 360
                        pkencontrado = 1
                        # print x,y, acim
                        break

                    Tramo0 += 1
                    Mini0 = Mini1
                    Mfin0 = Mfin1
                    Xfin0 = limites[4]
                    Yfin0 = limites[5]
                pass


            if pkencontrado == 1:
                Xmin =  291000
                Ymin = 4205000
                Xmax =  680000
                Ymax = 4576000
                if (x < Xmin or x > Xmax or y < Ymin or y > Ymax):
                    # print 'Las coordenadas no caen en CLM'
                    QApplication.restoreOverrideCursor()
                    return 'Error: Las coordenadas no caen en CLM'
                return x,y,acim
            else:
                # print 'El PK no esta en el tramo'
                QApplication.restoreOverrideCursor()
                return 'Error: El PK no esta en el tramo'
            nfeat += 1

        else:
            ###############################################################
            ######                                                   ######
            ######                tipomed = 'CALIBRADO'              ######
            ######                                                   ######
            ###############################################################

            for feat in features:
                npath = 1
                if pkencontrado == 1:
                    break
                # print nfeat, ' de ',len(features), ' features'
                if feat is not None:
                    geometry = feat["geometry"]
                    paths = geometry["paths"]
                    for path in paths:
                        posini = 0
                        posfin = len(path)-1
                        while path[posini][2] == None and posini<len(path)-1:    # Buscamos el primer punto del tramo sin valor None
                            # print ('posini ',posini, path[posini][2])
                            posini+=1
                        while path[posfin][2] == None and posfin>0:              # Buscamos el último punto del tramo sin valor None
                            # print ('posfin ',posfin, path[posfin][2])
                            posfin-=1
                        if path[posini][2] == None or path[posfin][2] == None:
                            continue

                        # print ('INI-  ',path[posini][2],'  FIN-  ',path[posfin][2])
                        if path[posini][2]<path[posfin][2]: # Sentido CRECIENTE
                            limites = [path[posini][2],path[posini][0],path[posini][1],path[posfin][2],path[posfin][0],path[posfin][1]]
                        else:   # Sentido DECRECIENTE
                            limites = [path[posfin][2],path[posfin][0],path[posfin][1],path[posini][2],path[posini][0],path[posini][1]]
                        listLimites.append(limites)
                        # print '%s de %s paths - %s puntos'%(npath, len(paths), len(path))
                        # print limites
                        npointprev = 0
                        npoint = 1
                        if pkencontrado == 1:
                            break
                        Mprev = None
                        # Mprev = 0.0
                        while (Mprev == None and npointprev<len(path)):
                            Pprev = path[npointprev]
                            Pprev = ogr.Geometry(ogr.wkbPoint)
                            Pprev.AddPoint(path[npointprev][0], path[npointprev][1])
                            Xprev = path[npointprev][0]
                            Yprev = path[npointprev][1]
                            Mprev = path[npointprev][2]
                            sentido = 'CRECIENTE'
                            iniloop = npointprev+1
                            npointprev += 1
                        if npointprev == len(path):
                            break

                        for npoint in range(iniloop,len(path)):
                            point = path[npoint]
                            # print '    PRE {:.0f} {:.2f} {:.2f} {:.7f}'.format(npointprev, Xprev, Yprev, Mprev),
                            # print '    ACT {:.0f} {:.2f} {:.2f} {:.7f}'.format(npoint+1, point[0], point[1], point[2])
                            if(point[2] is not None):
                                if point[2] == pk:    # El PK es el vértice
                                    x = point[0]
                                    y = point[1]

                                    # CALCULO DEL ACIMUT
                                    pointANT = QgsPointXY(Xprev,Yprev)
                                    pointPOS = QgsPointXY(x,y)
                                    res1 = self.calcACIMUT(pointANT,pointPOS)
                                    acim= res1[1]
                                    if acim < 0:
                                        acim += 360

                                    pkencontrado = 1
                                    if point[2]> path[(point in path)+1][2]:
                                        sentido = 'DECRECIENTE'
                                    # print 'COINCIDE CON Punto %s M=%s'%(npoint, point[2])
                                    break

                                else:
                                    # Se debe analizar si el punto es M=Null
                                    if Mprev is None:
                                        ### TODO QUITAR ESTO ###
                                        text = road_name + '/'+str(pk)
                                        text+= u' pk>=Mprev '+str(pk)+'/'+str(Mprev)
                                        text+= u' point[2] '+ str(point[2])
                                        text+= u'\n ERROR EN MEDIDA DE VÉRTICE'
                                        print (text)
                                        # self.showMessageERR(text)
                                        ### TODO QUITAR ESTO ###
                                        break
                                        pass
                                    if (pk>=Mprev and pk<point[2]) or (pk<=Mprev and pk>point[2]):
                                        # El PK está entre el vértice previo y el siguiente
                                        if pk>=Mprev and pk<point[2]:
                                            sentido = 'CRECIENTE'
                                        else:
                                            sentido = 'DECRECIENTE'
                                        Psig = ogr.Geometry(ogr.wkbPoint)
                                        Psig.AddPoint(point[0], point[1])
                                        # print 'SENTIDO- %s , ENCONTRADO ENTRE Punto %s M=%s %s M=%s'%(sentido, npointprev, Mprev, npoint+1, point[2])
                                        r = (pk - Mprev) / (point[2] - Mprev)
                                        modulo = r * (Pprev.Distance(Psig))

                                        alfa = math.atan2((point[1] - Yprev ) , (point[0]  - Xprev))

                                        x = Xprev + modulo * math.cos(alfa)
                                        y = Yprev + modulo * math.sin(alfa)

                                        # CALCULO DEL ACIMUT
                                        pointANT = QgsPointXY(Xprev,Yprev)
                                        pointPOS = QgsPointXY(x,y)
                                        res1 = self.calcACIMUT(pointANT,pointPOS)
                                        acim= res1[1]
                                        # if acim < 0:
                                            # acim += 360

                                        pkencontrado = 1
                                        break
                            else:
                                # M es None
                                pass


                            # El PK no está en este segmento
                            npointprev += 1
                            npoint += 1
                            Pprev = point
                            Pprev = ogr.Geometry(ogr.wkbPoint)
                            Pprev.AddPoint(point[0], point[1])
                            Xprev = point[0]
                            Yprev = point[1]
                            Mprev = point[2]

                        npath += 1

                nfeat += 1

            if pkencontrado == 0 and features!=[]:
                # Analizamos los tramos entre paths para localizar el PK en los huecos

                listLimites.sort()
                # for limites in listLimites:
                    # print limites
                Tramo0 = 0
                Mini0 = listLimites[0][0]
                Mfin0 = listLimites[0][3]
                Xfin0 = listLimites[0][4]
                Yfin0 = listLimites[0][5]
                for limites in listLimites[1:]:
                    Mini1 = limites[0]
                    Mfin1 = limites[3]
                    Xini1 = limites[1]
                    Yini1 = limites[2]
                    if (pk>Mfin0 and pk<Mini1):
                        # Encontramos el PK en un hueco
                        # print 'Encontramos el PK en un hueco -', Mfin0, Mini1

                        Pprev = ogr.Geometry(ogr.wkbPoint)
                        Pprev.AddPoint(Xfin0, Yfin0)
                        Psig = ogr.Geometry(ogr.wkbPoint)
                        Psig.AddPoint(Xini1, Yini1)

                        r = (pk - Mfin0) / (Mini1 - Mfin0)
                        modulo = r * (Pprev.Distance(Psig))
                        alfa = math.atan2((Yini1-Yfin0) , (Xini1-Xfin0))
                        x = Xfin0 + modulo * math.cos(alfa)
                        y = Yfin0 + modulo * math.sin(alfa)
                        # print 'r=%s mod=%s alfa=%s '%(r,modulo,alfa)
                        # print 'Xfin0=%s Yfin0=%s Xini1=%s Yini1=%s'%(Xfin0, Yfin0, Xini1, Yini1)
                        res1 = self.calcACIMUT(QgsPointXY(Xfin0, Yfin0),QgsPointXY(Xini1, Yini1))
                        acim= res1[1]
                        # if acim < 0:
                            # acim += 360
                        pkencontrado = 1
                        # print x,y, acim
                        break

                    Tramo0 += 1
                    Mini0 = Mini1
                    Mfin0 = Mfin1
                    Xfin0 = limites[4]
                    Yfin0 = limites[5]
                pass


            if pkencontrado == 1:
                Xmin =  291000
                Ymin = 4205000
                Xmax =  680000
                Ymax = 4576000
                if (x < Xmin or x > Xmax or y < Ymin or y > Ymax):
                    # print 'Las coordenadas no caen en CLM'
                    QApplication.restoreOverrideCursor()
                    return 'Error: Las coordenadas no caen en CLM'
                return x,y,acim
            else:
                # print 'El PK no esta en el tramo'
                QApplication.restoreOverrideCursor()
                return 'Error: El PK no esta en el tramo'
            nfeat += 1

    def CtraPktoCoorsAcim_GPKG(self, road_name, pk, pkDistEnt, tipomed):
        # PRUEBA DE IDENTIFICACIÓN POR DISTANCIA A PK ANTERIOR
        # CtraPktoCoorsAcim(self, road_name, pk, pkDistEnt = 0, tipomed = 'DISTPK')
        #   road_name - Matrícula de la carretera
        #   pk        - Punto Km, en caso de tipomed = 'DISTPK' puede ser la placa entera solo
        #   pkDistEnt - Distancia a la placa de 'pk'. Si = 0 y tipomed = 'DISTPK', se evalúa la distancia por los decimales de pk
        #   tipomed - Flag de análisis del tipo de PK medido
        #       tipomed = 'DISTPK' - El Pk se ubica por distancia a la placa de PK anterior
        #       tipomed = 'CALIBRADO' - El Pk se ubica por interpolación entre las placas
        #   Rutina de transformación de CARRETERA, PK a X, Y, Acim
        #   return x,y
        #   return None

        ruta_geopackage = self.qs.value(f"{self.nombre_plugin}/LRS/ruta_geopackage")
        nombre_capa_ctras = self.qs.value(f"{self.nombre_plugin}/LRS/nombre_capa_ctras")


        url = self.conf.general["rest_carreteras"]

        # Caso de que road_name esté vacío
        if (road_name == ""):
            return 'Error: Carretera sin nombre'
        posSPC = road_name.find(' ')
        r_name = road_name
        if posSPC != -1 :
            r_name = road_name[:posSPC+2]
            whereCONS = self.conf.lrs["identificador_carretera_carreteras"] + " like '" + r_name + u"%' and Matricula <> '9000'"
        else:
            whereCONS = self.conf.lrs["identificador_carretera_carreteras"] + " = '" + r_name + u"' and Matricula <> '9000'"

        values = {'where' : whereCONS,
                  'text': '',
                  'objectIds': '',
                  'geometryType' : 'esriGeometryPolyline',
                  'returnGeometry' : 'true',
                  'returnM': 'true' ,
                  'f': 'json'}


        data = urllib.parse.urlencode(values)
        try:
            response = requests.get(url+data, timeout=TIMEOUT_SEGUNDOS)
            response.raise_for_status()  # Lanza excepción si hay error HTTP (4xx, 5xx)
            response = response.json()  # Esto ya es el JSON parseado
            features =  response["features"]
        except urllib.error.URLError as e:
            QApplication.restoreOverrideCursor()
            self.showMessage(u"Error de conexión a internet (SERVIDOR CARRETERAS) fun.CtraPktoCoorsAcim LIN:559")
            return 'Error: No hay elementos'
        except TimeoutError:
            QApplication.restoreOverrideCursor()
            self.showMessage(u"Timeout: El servidor de carreteras no responde")
            return 'Error: Timeout'

        # try:
            # response = json.load(urllib.request.urlopen(url+data))
            # features =  response["features"]
        # except:
            # QApplication.restoreOverrideCursor()
            # self.showMessage(u"Error de conexión a internet  (SERVIDOR CARRETERAS) fun.CtraPktoCoorsAcim LIN:559")
            # return 'Error: No hay elementos'
        nfeat = 1
        pkencontrado = 0
        acim = 360
        listLimites= []

        if len(features) == 0:
            return 'Error: Matricula Incorrecta'

        if tipomed == 'DISTPK':
            ###############################################################
            ######                                                   ######
            ######                tipomed = 'DISTPK'                 ######
            ######                                                   ######
            ###############################################################
            if pkDistEnt == 0:
                pkEnt = int(pk)
                pkDistEnt = (pk - pkEnt)*1000
            else:
                pkEnt = int(pk)

            # Busqueda de posición de PK entero
            for feat in features:
                npath = 1
                if pkencontrado == 1:
                    break
                # print nfeat, ' de ',len(features), ' features'
                if feat is not None:
                    geometry = feat["geometry"]
                    paths = geometry["paths"]
                    for path in paths:
                        # print (path)
                        path2D = []
                        for point in path:
                            path2D.append(QgsPoint(point[0],point[1]))
                        geomPath = QgsGeometry.fromPolyline(path2D)

                        posini = 0
                        posfin = len(path)-1
                        while path[posini][2] == None and posini<len(path)-1:    # Buscamos el primer punto del tramo sin valor None
                            # print ('posini ',posini, path[posini][2])
                            posini+=1
                        while path[posfin][2] == None and posfin>0:              # Buscamos el último punto del tramo sin valor None
                            # print ('posfin ',posfin, path[posfin][2])
                            posfin-=1
                        if path[posini][2] == None or path[posfin][2] == None:
                            continue

                        # print ('INI-  ',path[posini][2],'  FIN-  ',path[posfin][2])
                        if path[posini][2]<path[posfin][2]: # Sentido CRECIENTE
                            limites = [path[posini][2],path[posini][0],path[posini][1],path[posfin][2],path[posfin][0],path[posfin][1]]
                            sentido = 'CRECIENTE'
                        else:   # Sentido DECRECIENTE
                            limites = [path[posfin][2],path[posfin][0],path[posfin][1],path[posini][2],path[posini][0],path[posini][1]]
                            sentido = 'DECRECIENTE'
                        listLimites.append(limites)
                        # print '%s de %s paths - %s puntos'%(npath, len(paths), len(path))
                        # print limites
                        npointprev = 0
                        npoint = 1
                        if pkencontrado == 1:
                            break
                        Mprev = None
                        # Mprev = 0.0
                        while (Mprev == None and npointprev<len(path)):
                            Pprev = path[npointprev]
                            Pprev = ogr.Geometry(ogr.wkbPoint)
                            Pprev.AddPoint(path[npointprev][0], path[npointprev][1])
                            Xprev = path[npointprev][0]
                            Yprev = path[npointprev][1]
                            Mprev = path[npointprev][2]
                            sentido = 'CRECIENTE'
                            iniloop = npointprev+1
                            npointprev += 1
                        if npointprev == len(path):
                            break

                        for npoint in range(iniloop,len(path)):
                            point = path[npoint]
                            # print '    PRE {:.0f} {:.2f} {:.2f} {:.7f}'.format(npointprev, Xprev, Yprev, Mprev),
                            # print '    ACT {:.0f} {:.2f} {:.2f} {:.7f}'.format(npoint+1, point[0], point[1], point[2])
                            if(point[2] is not None):
                                if point[2] == pkEnt:   # El pkEnt es el vértice

                                    xPkEnt = point[0]
                                    yPkEnt = point[1]

                                    distOriPK = geomPath.lineLocatePoint(QgsGeometry.fromPointXY(QgsPointXY(xPkEnt,yPkEnt)))
                                    if sentido == 'CRECIENTE':
                                        # distOriPoint = distOriPK + 1000*pkDistEnt
                                        distOriPoint = distOriPK + pkDistEnt
                                    else:
                                        # distOriPoint = distOriPK - 1000*pkDistEnt
                                        distOriPoint = distOriPK - pkDistEnt
                                    # print (distOriPK, distOriPoint)

                                    pointResul = geomPath.interpolate(distOriPoint)
                                    # print (pointResul)
                                    if pointResul.isEmpty():
                                        return u'Error: Imposible cálculo'
                                    else:
                                        x = pointResul.asPoint().x()
                                        y = pointResul.asPoint().y()

                                    acim = 0
                                    # CALCULO DEL ACIMUT
                                    (sqDist, nearestPoint, afterVertex, leftOf) = geomPath.closestSegmentWithContext(QgsPointXY(x,y), 0.01)
                                    # print ('sqDist= ',sqDist, 'nearestPoint= ', nearestPoint, 'afterVertex= ', afterVertex, 'leftOf=', leftOf)
                                    if sentido == 'CRECIENTE':
                                        pointANT = geomPath.vertexAt(afterVertex)
                                        pointPOS = geomPath.vertexAt(afterVertex+1)
                                    else:
                                        pointANT = geomPath.vertexAt(afterVertex+1)
                                        pointPOS = geomPath.vertexAt(afterVertex)
                                    distSegm, acim = self.calcACIMUT(pointANT,pointPOS)
                                    # acim= res1[1]
                                    if acim < 0:
                                        acim += 360
                                    # print ('acim=', acim)

                                    pkencontrado = 1
                                    if point[2]> path[(point in path)+1][2]:
                                        sentido = 'DECRECIENTE'
                                    # print 'COINCIDE CON Punto %s M=%s'%(npoint, point[2])
                                    break

                                else:
                                    # Se debe analizar si el punto es M=Null
                                    if (pkEnt>=Mprev and pkEnt<point[2]) or (pkEnt<=Mprev and pkEnt>point[2]):
                                        # El pkEnt está entre el vértice previo y el siguiente
                                        if pkEnt>=Mprev and pkEnt<point[2]:
                                            sentido = 'CRECIENTE'
                                        else:
                                            sentido = 'DECRECIENTE'
                                        Psig = ogr.Geometry(ogr.wkbPoint)
                                        Psig.AddPoint(point[0], point[1])
                                        # print 'SENTIDO- %s , ENCONTRADO ENTRE Punto %s M=%s %s M=%s'%(sentido, npointprev, Mprev, npoint+1, point[2])
                                        r = (pkEnt - Mprev) / (point[2] - Mprev)
                                        modulo = r * (Pprev.Distance(Psig))

                                        alfa = math.atan2((point[1] - Yprev ) , (point[0]  - Xprev))

                                        xPkEnt = Xprev + modulo * math.cos(alfa)
                                        yPkEnt = Yprev + modulo * math.sin(alfa)

                                        pointQ = QgsGeometry.fromPointXY(QgsPointXY(xPkEnt,yPkEnt))
                                        distOriPK = geomPath.lineLocatePoint(pointQ)
                                        if sentido == 'CRECIENTE':
                                            # distOriPoint = distOriPK + 1000*pkDistEnt
                                            distOriPoint = distOriPK + pkDistEnt
                                        else:
                                            # distOriPoint = distOriPK - 1000*pkDistEnt
                                            distOriPoint = distOriPK - pkDistEnt
                                        # print (distOriPK, distOriPoint)

                                        pointResul = geomPath.interpolate(distOriPoint)
                                        # print (pointResul)
                                        if pointResul.isEmpty():
                                            return u'Error: Imposible cálculo'
                                        else:
                                            x = pointResul.asPoint().x()
                                            y = pointResul.asPoint().y()

                                        # # CALCULO DEL ACIMUT
                                        (sqDist, nearestPoint, afterVertex, leftOf) = geomPath.closestSegmentWithContext(QgsPointXY(x,y), 0.01)
                                        # print ('sqDist= ',sqDist, 'nearestPoint= ', nearestPoint, 'afterVertex= ', afterVertex, 'leftOf=', leftOf)
                                        if sentido == 'CRECIENTE':
                                            pointANT = geomPath.vertexAt(afterVertex)
                                            pointPOS = geomPath.vertexAt(afterVertex+1)
                                        else:
                                            pointANT = geomPath.vertexAt(afterVertex+1)
                                            pointPOS = geomPath.vertexAt(afterVertex)
                                        distSegm, acim = self.calcACIMUT(pointANT,pointPOS)
                                        if acim < 0:
                                            acim += 360
                                        # print ('acim=', acim)

                                        pkencontrado = 1
                                        break
                            else:
                                # M es None
                                pass

                            # El pkEnt no está en este segmento
                            npointprev += 1
                            npoint += 1
                            Pprev = point
                            Pprev = ogr.Geometry(ogr.wkbPoint)
                            Pprev.AddPoint(point[0], point[1])
                            Xprev = point[0]
                            Yprev = point[1]
                            Mprev = point[2]

                        npath += 1

                nfeat += 1

            if pkencontrado == 0 and features !=[] and listLimites != [] :
                # Analizamos los tramos entre paths para localizar el pkEnt en los huecos

                listLimites.sort()
                # for limites in listLimites:
                    # print limites
                Tramo0 = 0
                Mini0 = listLimites[0][0]
                Mfin0 = listLimites[0][3]
                Xfin0 = listLimites[0][4]
                Yfin0 = listLimites[0][5]
                for limites in listLimites[1:]:
                    Mini1 = limites[0]
                    Mfin1 = limites[3]
                    Xini1 = limites[1]
                    Yini1 = limites[2]
                    if (pkEnt>Mfin0 and pkEnt<Mini1):
                        # Encontramos el pkEnt en un hueco
                        # print 'Encontramos el pkEnt en un hueco -', Mfin0, Mini1

                        Pprev = ogr.Geometry(ogr.wkbPoint)
                        Pprev.AddPoint(Xfin0, Yfin0)
                        Psig = ogr.Geometry(ogr.wkbPoint)
                        Psig.AddPoint(Xini1, Yini1)

                        r = (pkEnt - Mfin0) / (Mini1 - Mfin0)
                        modulo = r * (Pprev.Distance(Psig))
                        alfa = math.atan2((Yini1-Yfin0) , (Xini1-Xfin0))
                        x = Xfin0 + modulo * math.cos(alfa)
                        y = Yfin0 + modulo * math.sin(alfa)
                        # print 'r=%s mod=%s alfa=%s '%(r,modulo,alfa)
                        # print 'Xfin0=%s Yfin0=%s Xini1=%s Yini1=%s'%(Xfin0, Yfin0, Xini1, Yini1)
                        res1 = self.calcACIMUT(QgsPointXY(Xfin0, Yfin0),QgsPointXY(Xini1, Yini1))
                        acim= res1[1]
                        # if acim < 0:
                            # acim += 360
                        pkencontrado = 1
                        # print x,y, acim
                        break

                    Tramo0 += 1
                    Mini0 = Mini1
                    Mfin0 = Mfin1
                    Xfin0 = limites[4]
                    Yfin0 = limites[5]
                pass


            if pkencontrado == 1:
                Xmin =  291000
                Ymin = 4205000
                Xmax =  680000
                Ymax = 4576000
                if (x < Xmin or x > Xmax or y < Ymin or y > Ymax):
                    # print 'Las coordenadas no caen en CLM'
                    QApplication.restoreOverrideCursor()
                    return 'Error: Las coordenadas no caen en CLM'
                return x,y,acim
            else:
                # print 'El PK no esta en el tramo'
                QApplication.restoreOverrideCursor()
                return 'Error: El PK no esta en el tramo'
            nfeat += 1

        else:
            ###############################################################
            ######                                                   ######
            ######                tipomed = 'CALIBRADO'              ######
            ######                                                   ######
            ###############################################################

            for feat in features:
                npath = 1
                if pkencontrado == 1:
                    break
                # print nfeat, ' de ',len(features), ' features'
                if feat is not None:
                    geometry = feat["geometry"]
                    paths = geometry["paths"]
                    for path in paths:
                        posini = 0
                        posfin = len(path)-1
                        while path[posini][2] == None and posini<len(path)-1:    # Buscamos el primer punto del tramo sin valor None
                            # print ('posini ',posini, path[posini][2])
                            posini+=1
                        while path[posfin][2] == None and posfin>0:              # Buscamos el último punto del tramo sin valor None
                            # print ('posfin ',posfin, path[posfin][2])
                            posfin-=1
                        if path[posini][2] == None or path[posfin][2] == None:
                            continue

                        # print ('INI-  ',path[posini][2],'  FIN-  ',path[posfin][2])
                        if path[posini][2]<path[posfin][2]: # Sentido CRECIENTE
                            limites = [path[posini][2],path[posini][0],path[posini][1],path[posfin][2],path[posfin][0],path[posfin][1]]
                        else:   # Sentido DECRECIENTE
                            limites = [path[posfin][2],path[posfin][0],path[posfin][1],path[posini][2],path[posini][0],path[posini][1]]
                        listLimites.append(limites)
                        # print '%s de %s paths - %s puntos'%(npath, len(paths), len(path))
                        # print limites
                        npointprev = 0
                        npoint = 1
                        if pkencontrado == 1:
                            break
                        Mprev = None
                        # Mprev = 0.0
                        while (Mprev == None and npointprev<len(path)):
                            Pprev = path[npointprev]
                            Pprev = ogr.Geometry(ogr.wkbPoint)
                            Pprev.AddPoint(path[npointprev][0], path[npointprev][1])
                            Xprev = path[npointprev][0]
                            Yprev = path[npointprev][1]
                            Mprev = path[npointprev][2]
                            sentido = 'CRECIENTE'
                            iniloop = npointprev+1
                            npointprev += 1
                        if npointprev == len(path):
                            break

                        for npoint in range(iniloop,len(path)):
                            point = path[npoint]
                            # print '    PRE {:.0f} {:.2f} {:.2f} {:.7f}'.format(npointprev, Xprev, Yprev, Mprev),
                            # print '    ACT {:.0f} {:.2f} {:.2f} {:.7f}'.format(npoint+1, point[0], point[1], point[2])
                            if(point[2] is not None):
                                if point[2] == pk:    # El PK es el vértice
                                    x = point[0]
                                    y = point[1]

                                    # CALCULO DEL ACIMUT
                                    pointANT = QgsPointXY(Xprev,Yprev)
                                    pointPOS = QgsPointXY(x,y)
                                    res1 = self.calcACIMUT(pointANT,pointPOS)
                                    acim= res1[1]
                                    if acim < 0:
                                        acim += 360

                                    pkencontrado = 1
                                    if point[2]> path[(point in path)+1][2]:
                                        sentido = 'DECRECIENTE'
                                    # print 'COINCIDE CON Punto %s M=%s'%(npoint, point[2])
                                    break

                                else:
                                    # Se debe analizar si el punto es M=Null
                                    if Mprev is None:
                                        ### TODO QUITAR ESTO ###
                                        text = road_name + '/'+str(pk)
                                        text+= u' pk>=Mprev '+str(pk)+'/'+str(Mprev)
                                        text+= u' point[2] '+ str(point[2])
                                        text+= u'\n ERROR EN MEDIDA DE VÉRTICE'
                                        print (text)
                                        # self.showMessageERR(text)
                                        ### TODO QUITAR ESTO ###
                                        break
                                        pass
                                    if (pk>=Mprev and pk<point[2]) or (pk<=Mprev and pk>point[2]):
                                        # El PK está entre el vértice previo y el siguiente
                                        if pk>=Mprev and pk<point[2]:
                                            sentido = 'CRECIENTE'
                                        else:
                                            sentido = 'DECRECIENTE'
                                        Psig = ogr.Geometry(ogr.wkbPoint)
                                        Psig.AddPoint(point[0], point[1])
                                        # print 'SENTIDO- %s , ENCONTRADO ENTRE Punto %s M=%s %s M=%s'%(sentido, npointprev, Mprev, npoint+1, point[2])
                                        r = (pk - Mprev) / (point[2] - Mprev)
                                        modulo = r * (Pprev.Distance(Psig))

                                        alfa = math.atan2((point[1] - Yprev ) , (point[0]  - Xprev))

                                        x = Xprev + modulo * math.cos(alfa)
                                        y = Yprev + modulo * math.sin(alfa)

                                        # CALCULO DEL ACIMUT
                                        pointANT = QgsPointXY(Xprev,Yprev)
                                        pointPOS = QgsPointXY(x,y)
                                        res1 = self.calcACIMUT(pointANT,pointPOS)
                                        acim= res1[1]
                                        # if acim < 0:
                                            # acim += 360

                                        pkencontrado = 1
                                        break
                            else:
                                # M es None
                                pass


                            # El PK no está en este segmento
                            npointprev += 1
                            npoint += 1
                            Pprev = point
                            Pprev = ogr.Geometry(ogr.wkbPoint)
                            Pprev.AddPoint(point[0], point[1])
                            Xprev = point[0]
                            Yprev = point[1]
                            Mprev = point[2]

                        npath += 1

                nfeat += 1

            if pkencontrado == 0 and features!=[]:
                # Analizamos los tramos entre paths para localizar el PK en los huecos

                listLimites.sort()
                # for limites in listLimites:
                    # print limites
                Tramo0 = 0
                Mini0 = listLimites[0][0]
                Mfin0 = listLimites[0][3]
                Xfin0 = listLimites[0][4]
                Yfin0 = listLimites[0][5]
                for limites in listLimites[1:]:
                    Mini1 = limites[0]
                    Mfin1 = limites[3]
                    Xini1 = limites[1]
                    Yini1 = limites[2]
                    if (pk>Mfin0 and pk<Mini1):
                        # Encontramos el PK en un hueco
                        # print 'Encontramos el PK en un hueco -', Mfin0, Mini1

                        Pprev = ogr.Geometry(ogr.wkbPoint)
                        Pprev.AddPoint(Xfin0, Yfin0)
                        Psig = ogr.Geometry(ogr.wkbPoint)
                        Psig.AddPoint(Xini1, Yini1)

                        r = (pk - Mfin0) / (Mini1 - Mfin0)
                        modulo = r * (Pprev.Distance(Psig))
                        alfa = math.atan2((Yini1-Yfin0) , (Xini1-Xfin0))
                        x = Xfin0 + modulo * math.cos(alfa)
                        y = Yfin0 + modulo * math.sin(alfa)
                        # print 'r=%s mod=%s alfa=%s '%(r,modulo,alfa)
                        # print 'Xfin0=%s Yfin0=%s Xini1=%s Yini1=%s'%(Xfin0, Yfin0, Xini1, Yini1)
                        res1 = self.calcACIMUT(QgsPointXY(Xfin0, Yfin0),QgsPointXY(Xini1, Yini1))
                        acim= res1[1]
                        # if acim < 0:
                            # acim += 360
                        pkencontrado = 1
                        # print x,y, acim
                        break

                    Tramo0 += 1
                    Mini0 = Mini1
                    Mfin0 = Mfin1
                    Xfin0 = limites[4]
                    Yfin0 = limites[5]
                pass


            if pkencontrado == 1:
                Xmin =  291000
                Ymin = 4205000
                Xmax =  680000
                Ymax = 4576000
                if (x < Xmin or x > Xmax or y < Ymin or y > Ymax):
                    # print 'Las coordenadas no caen en CLM'
                    QApplication.restoreOverrideCursor()
                    return 'Error: Las coordenadas no caen en CLM'
                return x,y,acim
            else:
                # print 'El PK no esta en el tramo'
                QApplication.restoreOverrideCursor()
                return 'Error: El PK no esta en el tramo'
            nfeat += 1

    def pointToPK(self,point,iface,pintar,no9000):
        # pointToPK(self,point,iface,pintar,no9000)
        #   Devuelve diferentes datos de salida de una carretera a partir de un punto
        #       return [the_road, m_final, the_road, funcion, atributos, distEJE, acimEJE]
        #   ENTRADA:
        #       point- Geometria punto (x,y)
        #       iface- Interface de la vista
        #       pintar- 'SI', 'NO'
        #       no9000= 'SI', 'NO' - SI Busca primero matriculas NO 9000
        #       noJCCM= 'SI', 'NO' - NO Busca primero matriculas Titularidad=JCCM
        #   SALIDA:
        #       0 the_road - Matricula de la carretera
        #       1 m_final - Valor M (PK) de las coordenadas.
        #       2 the_road - Matricula de la carretera ############## ¿repetida? ##############
        #       3 funcion - Funcionalidad de la via
        #       4 atributos - Conjunto compelto de atributos como los devuelve el REST
        #       5 distEJE - Distancia del punto al eje
        #       6 acimEJE - Acimut del punto perpendicular del eje
        #       7 pointEJE- Punto en el eje (coordenas XY)

        # no9000= 'SI'

        clicked_QgsPoint = QgsPointXY(point[0],point[1])
        qgs_point_geometry = QgsGeometry.fromPointXY(clicked_QgsPoint)

        margin = 100        # Margen de búsqueda de viales en la GDB
        geomCons='{"xmin": ' + str(point[0] - margin) + ' , "ymin": ' + str(point[1] - margin) + ' , "xmax": ' + str(point[0] + margin) + ' , "ymax": ' + str(point[1] + margin) + ' , "spatialReference":{crsVal}}'
        print (point)
        print ('geomCons: ',geomCons)
        # print ('{"xmin":' + str(point[0] - margin) + ', "ymin": ' + str(point[1] - margin) + ' , "xmax":' + str(point[0] + margin) + ' , "ymax": ' + str(point[1] + margin) + ' , "spatialReference": {25830}}')
        url = self.conf.general["rest_carreteras"]
        values = {'where' : '',
                  'text': '',
                  'objectIds': '',
                  'outFields': '*',
                  'geometry' : geomCons,
                  # 'geometry':'{"xmin": ' + str(point[0] - margin) + ' , "ymin": ' + str(point[1] - margin) + ' , "xmax": ' + str(point[0] + margin) + ' , "ymax": ' + str(point[1] + margin) + ' , "spatialReference":{crsVal}}',
                  'geometryType' : 'esriGeometryEnvelope',
                  'returnGeometry' : 'true',
                  'spatialRel': 'esriSpatialRelIntersects',
                  'returnM': 'true' ,
                  'f': 'json'}

        str_values = {}
        for k, v in values.items():
            str_values[k] = unicode(v).encode('utf-8')
        data = urllib.parse.urlencode(str_values)
        try:
            response = requests.get(url+data, timeout=TIMEOUT_SEGUNDOS)
            response.raise_for_status()  # Lanza excepción si hay error HTTP (4xx, 5xx)
            response = response.json()  # Esto ya es el JSON parseado
        except urllib.error.URLError as e:
            QApplication.restoreOverrideCursor()
            txt = u"Error de conexión a internet\n"
            txt += self.PrintException()
            txt += u"\n\nPROBAMOS A OBTENER DATOS DESDE EL SERVIDOR LOCAL DE SU CONFIGURACIÓN"
            self.showMessageERR(txt)
            return
        except TimeoutError:
            QApplication.restoreOverrideCursor()
            self.showMessageERR(u"Timeout: El servidor de carreteras no responde")
            return
        # try:
            # response = json.load(urllib.request.urlopen(url+data))
        # except:
            # QApplication.restoreOverrideCursor()
            # txt = u"Error de conexión a internet\n"
            # txt+= self.PrintException()
            # txt += u"\n\nPROBAMOS A OBTENER DATOS DESDE EL SERVIDOR LOCAL DE SU CONFIGURACIÓN"
            # self.showMessageERR(txt)
            # return

        print (url+data)
        # print (response)

        try:
            features =  response["features"]    # Los distintos features encontrados en la búsqueda
        except:
            QApplication.restoreOverrideCursor()
            txt = u"Error de consulta a GEODATABASE\n"
            txt+= self.PrintException()
            txt += u"\n\nPROBAMOS A OBTENER DATOS DESDE EL SERVIDOR LOCAL DE SU CONFIGURACIÓN"
            self.showMessageERR(txt)
            return

        c_distance = 100000     # Distancia límite de cálculo, por debajo no devuelve datos, se reduce con todas las dist calculadas
        the_feature = None
        the_line = None
        the_lineM = None
        the_geometry = None
        the_road = None
        matric = None
        funcion = None
        atributos = None
        numFeat = 1
        for feature in features:
            polyline = []
            polylineM = [] ### Añadida M ###

            geometry = feature["geometry"]
            attr =  feature["attributes"]
            # print (attr)
            # plan = attr['Matricula_Plan'] # Matrícula_plan del elemento
            matric = attr['Matricula']        # Matrícula del elemento
            Titu = attr['Titularidad']      # Titularidad del elemento
            if no9000 == 'SI' and matric == '9000':
                continue
            funcion = attr['Funcionalidad']
            paths = geometry["paths"]
            for path in paths:
                for point in path:
                    polyline.append(QgsPoint(point[0],point[1],point[2]))
                    if(point[2] == None):
                        polylineM.append(QgsPoint(point[0],point[1]))
                    else:
                        polylineM.append(QgsPoint(point[0],point[1],point[2]))

            gLine = QgsGeometry.fromPolyline(polyline)
            gLineM = QgsGeometry.fromPolyline(polylineM)
            distance = gLine.distance(qgs_point_geometry)
            # print (matric, distance, c_distance, Titu, gLine)
            # print (matric, distance, c_distance, Titu)

            if distance <= c_distance:
                c_distance = distance
                the_road = matric
                Titularidad = Titu
                the_line = gLine
                the_lineM = gLineM
                the_feature = feature
                the_geometry = geometry
                atributos = attr
            numFeat += 1

        # print ('')
        # print ('ELEGIDO: ', the_road, c_distance, Titu, )
        # print (the_line)


        if the_line == None:
            return None

        hasM = True
        # SE OBTIENE EL PUNTO MÁS PRÓXIMO AL PINCHADO
        closest_point_geometry = QgsGeometryUtils.closestPoint(the_line.get(), QgsPoint(clicked_QgsPoint))
        closest_x = closest_point_geometry.x()
        closest_y = closest_point_geometry.y()
        closest_M = closest_point_geometry.z()
        if type(closest_M) is type(None) or closest_M != closest_M:
            closest_M = 0
            hasM = False
        pointEJE = QgsPointXY(closest_x,closest_y)

        # DISTANCIA A LO LARGO DE LA POLYLINEA DEL PUNTO DEL EJE
        distINI = self.distancePTLN( the_line, QgsGeometry.fromPointXY(QgsPointXY(closest_x, closest_y)))
        if distINI is None:
            print('the_line.get().length() - distINI ', the_line.get().length(), distINI)
            distINI = 0
        distFIN = the_line.get().length() - distINI
        # print ('Distancia en la Polylinea distINI - ', distINI)

        # cALCULO DEL VÉRTICE MÁS PROXIMO AL PUNTO PINCHADO
        vertex_prox = QgsGeometryUtils.closestVertex(the_line.get(), QgsPoint(clicked_QgsPoint))
        vertex_prox_no = the_line.vertexNrFromVertexId(vertex_prox[1])      # Nº de vértice en la polilinea
        vertex_prox_d = the_line.distanceToVertex(vertex_prox_no)           # Distancia del vértice al origen
        vertex_prox_point = vertex_prox[0]                                  # QGSPOINT del vértice

        # CÁLCULO DE LOS VÉRTICES ANTERIOR Y POSTERIOR
        if vertex_prox_d <= distINI:
            pointANT = vertex_prox_point
            vertex_prox1_no = the_line.vertexNrFromVertexId(vertex_prox[1])+1   # Nº de vértice en la polilinea
            vertex_prox1_d = the_line.distanceToVertex(vertex_prox1_no)         # Distancia del vértice al origen
            pointPOS = the_line.vertexAt(vertex_prox1_no)
            # print ('PointANT = '+ str(vertex_prox_no) +' - '+str(vertex_prox_d) +' - '+ str(pointANT))
            # print ('PointPOS = '+ str(vertex_prox1_no)+' - '+str(vertex_prox1_d)+' - '+ str(pointPOS))
        else:
            pointPOS = vertex_prox_point
            vertex_prox1_no = the_line.vertexNrFromVertexId(vertex_prox[1])-1   # Nº de vértice en la polilinea
            vertex_prox1_d = the_line.distanceToVertex(vertex_prox1_no)         # Distancia del vértice al origen
            pointANT = the_line.vertexAt(vertex_prox1_no)
            # print ('PointANT = '+ str(vertex_prox1_no)+' - '+str(vertex_prox1_d)+' - '+str(vertex_prox_point))
            # print ('PointPOS = '+ str(vertex_prox_no) +' - '+str(vertex_prox_d) +' - '+str(vertex_prox_point))

        # DISTANCIA PERPENDICULAR A LA POLILINEA
        distEJE = c_distance

        # Lado de la polilinea
        ladoEJE = QgsGeometryUtils.leftOfLine(clicked_QgsPoint[0],clicked_QgsPoint[1], pointANT.x(),  pointANT.y(), pointPOS.x(), pointPOS.y()) # int:
        if ladoEJE != 0:
            distEJE = distEJE * ladoEJE


        # CALCULO DEL ACIMUT
        acimEJE= 0
        res = self.calcACIMUT(QgsPoint(pointANT.x(),  pointANT.y()), QgsPoint(pointPOS.x(), pointPOS.y()))
        acimEJE= res[1]
        if acimEJE < 0:
            acimEJE += 360

        # Dibujamos un punto
        if pintar == 'SI':
            m = self.dibujarPunto(pointEJE.x(), pointEJE.y(),iface)

        if hasM == True:
            # Cálculo de la distancia a placa anterior
            PKplca = int( closest_M )
            numVert = 0
            for vert in the_line.vertices():
                vertAnt = vert
                vertA_x = vert.x()
                vertA_y = vert.y()
                vertA_M = vert.z()
                if vert.z() > PKplca:
                    vertSig = vert
                    vertS_x = vert.x()
                    vertS_y = vert.y()
                    vertS_M = vert.z()
                    # print ('vertS:', numVert, vertS_x, vertS_y, vertS_M)
                    break
                numVert = numVert + 1

            try:
                segmento = QgsGeometry.fromPolyline([vertAnt, vertSig])
                lengSegmento = segmento.length()
                if lengSegmento != 0:
                    distanciaPK = (PKplca-vertA_M)/(vertS_M-vertA_M)*lengSegmento
                else:
                    distanciaPK = 0
                pointPK = segmento.interpolate(distanciaPK)
                DistPkPlaca = distINI - self.distancePTLN( the_line, QgsGeometry.fromPointXY(QgsPointXY(pointPK.get().x(), pointPK.get().y())))
            except:
                DistPkPlaca = 0

        else:
            DistPkPlaca = 0

        #print  (the_road, closest_M, the_road, funcion, atributos, distEJE, acimEJE, pointEJE, geometry, distINI, distFIN, DistPkPlaca)
        #return        0          1         2        3          4        5        6         7,         8        9       10           11
        # return [the_road, closest_M, the_road, funcion, atributos, distEJE, acimEJE, pointEJE, the_lineM, distINI, distFIN, DistPkPlaca]
        return [the_road, closest_M, the_road, funcion, atributos, distEJE, acimEJE, pointEJE, the_geometry, distINI, distFIN, DistPkPlaca]

    def pointToPK_GPKG(self,point,iface,pintar,no9000, tipoCapa, ruta_geopackage, nombre_capa):
        # Rutina de calculo alternativo sobre fichero GPKG
        # ------------------------------------------------------------

        # pointToPK_GPKG(self,point,iface,pintar,no9000)
        #   Devuelve diferentes datos de salida de una carretera a partir de un punto
        #       return [the_road, m_final, the_road, funcion, atributos, distEJE, acimEJE]
        #   ENTRADA:
        #       point- Geometria punto (x,y)
        #       iface- Interface de la vista
        #       pintar- 'SI', 'NO'
        #       no9000= 'SI', 'NO' - SI Busca primero matriculas NO 9000
        #       tipoCapa=1 Capa tipo carreteras, tipoCapa=0 Capa de lineas estandard
        #       ruta_geopackage= Dirección del fichero GPKG
        #       nombre_capa= Nombre de la capa de carreteras calibrada en el GPKG
        #   SALIDA:
        #       0  the_road - Matricula de la carretera
        #       1  m_final - Valor M (PK) de las coordenadas.
        #       2  the_road - Matricula de la carretera ############## ¿repetida? ##############
        #       3  funcion - Funcionalidad de la via
        #       4  atributos - Conjunto compelto de atributos como los devuelve el REST
        #       5  distEJE - Distancia del punto al eje
        #       6  acimEJE - Acimut del punto perpendicular del eje
        #       7  pointEJE- Punto en el eje (coordenas XY)
        #       8  geometry- Geometria del elemento
        #       9  distINI - Distancia al inicio del elemento
        #       10 distFIN - Distancia al final del elemento


        # Ruta al archivo GeoPackage y nombre de la capa
        # ------ TODO ------------------------------------------------------
        # RUTA_GEOPACKAGE = 'C:\\USERS\\AGUSA\\ONEDRIVE - JCCM\\CARTOGRAFIA\\SIG_REGIONAL_CARRETERAS.GPKG'
        # NOMBRE_CAPA = 'GEO_BTACALIBRADA'
        # print (point)
        # coordenadas = (603234.579, 4318476.858)  # Coordenadas a buscar
        # ------------------------------------------------------------------

        clicked_QgsPoint = QgsPointXY(point[0],point[1])
        qgs_point_geometry = QgsGeometry.fromPointXY(clicked_QgsPoint)

        margin = 100        # Margen de búsqueda de viales en la GDB

        # Abre el GeoPackage
        geopackage = ogr.Open(ruta_geopackage)

        if geopackage is None:
            print("Error al abrir el GeoPackage")
            return None
        else:
            # Obtén la capa 'GEO_EJES'
            layer = QgsVectorLayer('{}|layername={}'.format(ruta_geopackage, nombre_capa), nombre_capa, 'ogr')

        rectMargin = QgsRectangle(point[0] - margin, point[1] - margin, point[0] + margin, point[1] + margin)

        c_distance = 100000     # Distancia límite de cálculo, por debajo no devuelve datos, se reduce con todas las dist calculadas
        the_feature = None
        qgsLines = []
        the_road = None
        matric = None
        funcion = None
        atributos = None
        the_lineM = None
        featsProx = []
        numFeat = 1

        message = ''

        featuresLine = layer.getFeatures()

        for feature in featuresLine:
            polyline = []
            polylineM = [] ### Añadida M ###

            geom_line = feature.geometry()
            if geom_line.intersects(rectMargin):
                geometry = feature.geometry()
                attr = {}
                for field in layer.fields():
                    attr[field.name()] = feature[field.name()]

                if tipoCapa == 1:
                    matric = feature["Matricula"]        # Matrícula del elemento
                    Titu = feature["Titularidad"]      # Titularidad del elemento
                    funcion = feature["Funcionalidad"]
                else:
                    matric = 's/d'        # Matrícula del elemento
                    Titu = 's/d'      # Titularidad del elemento
                    funcion = 's/d'

                paths = []
                if geometry.isMultipart():
                    for part in geometry.asGeometryCollection():
                        paths.append(part)
                else:
                    paths.append(geometry)

                # Habría que corregir la creación de la polylineM para casos de pths invertidos
                for path in paths:
                    novertices = len(path.asPolyline())
                    for id in range(novertices):
                        pointP = path.vertexAt(id)
                        gPnt = QgsGeometry.fromPointXY(QgsPointXY(pointP.x(),pointP.y()))
                        if(pointP.m() == None):
                            QgsMessageLog.logMessage("Ojo.. valor sin M",self.nombre_plugin)
                            polylineM.append(QgsPoint(pointP.x(),pointP.y()))
                        else:
                            polylineM.append(QgsPoint(pointP.x(),pointP.y(),pointP.m()))

                gLineM = QgsGeometry.fromPolyline(polylineM)
                distance = gLineM.distance(qgs_point_geometry)

                featsProx.append([matric, Titu, distance, feature, attr, gLineM, numFeat])

                if distance <= c_distance:
                    the_road = matric
                    c_distance = distance
                    the_feature = feature
                    atributos = attr
                    the_lineM = gLineM
                numFeat += 1

                if tipoCapa == 1:
                    message += 'MATRIC= %s DIST= %s\n'%(matric, str(round(distance,2)))
                else:
                    message += next(iter(attr))+':'+str(next(iter(attr.values())))+ ' DIST= '+ str(round(distance,2))+ '\n'


        # Analizar si matric = 9000
        if no9000 == 'SI' and the_road == '9000':
            c_distance = 1000000
            for featP in featsProx:
                if featP[0] != '9000':
                    if featP[2] <= c_distance:
                        the_road = featP[0]
                        c_distance = featP[2]
                        the_feature = featP[3]
                        atributos = featP[4]
                        the_lineM = featP[5]
                    pass

        if the_lineM == None:
            return None

        closest_point_geometry, dist, punto_anterior, punto_posterior, m_final, distINI, distFIN = self.calculaMproximo(the_lineM, clicked_QgsPoint)

        pointEJE = QgsPointXY(closest_point_geometry.x(),closest_point_geometry.y())
        pointANT = QgsPointXY(punto_anterior.x(),punto_anterior.y())
        pointPOS = QgsPointXY(punto_posterior.x(),punto_posterior.y())

        if pintar == 'SI':
            m = self.dibujarPunto(closest_point_geometry.x(),closest_point_geometry.y(),iface)

        # CALCULO DEL ACIMUT
        res = self.calcACIMUT(clicked_QgsPoint,pointEJE)
        res1 = self.calcACIMUT(pointANT,pointPOS)

        acimTRANS= res[1]
        acimEJE= res1[1]
        lado = (acimEJE - acimTRANS)
        if math.fabs(lado) > 180:
            if lado > 0:
                lado = -(lado-180)
            else:
                lado = -(lado+180)

        vlado = lado/90
        distEJE= res[0] * vlado
        if acimEJE < 0:
            acimEJE += 360

        # ------ TODO ------------------------------------------------------
        DistPkPlaca = 0
        # ------ TODO ------------------------------------------------------

        #return        0        1         2        3          4        5        6         7,        8        9       10           11
        return [the_road, m_final, the_road, funcion, atributos, distEJE, acimEJE, pointEJE, geometry, distINI, distFIN, DistPkPlaca]

    def distancePTLN(self, line, point):
        ## https://qgis-developer.osgeo.narkive.com/cXKHUfzR/calculate-distance-from-two-points-along-line-in-pyqgis
        sum = 0
        for seg_start, seg_end in self.pair(line.asPolyline()):
            if QgsGeometry.fromPolyline([QgsPoint(seg_start), QgsPoint(seg_end)]).distance(point) > 1e-8 : # correction of the floating point precision errors
                sum = sum + QgsGeometry.fromPolyline([QgsPoint(seg_start),QgsPoint(seg_end)]).length()
            if QgsGeometry.fromPolyline([QgsPoint(seg_start), QgsPoint(seg_end)]).distance(point) < 1e-8 :
                return sum + QgsGeometry.fromPolyline([QgsPoint(seg_start), QgsPoint(point.asPoint())]).length()

    def calcACIMUT(self, point1, point2):
        # calcACIMUT(self, point1, point2)
        #   Calcula el acimut y la distancia entre dos puntos point1, point2

        dist= point1.distance(point2)
        acim = point1.azimuth(point2)
        if acim < 0:
            acim += 360
        return (dist, acim)

    def pointToPKfich(self,point,iface,pintar,no9000, tipoCapa):
        # pointToPK(self,point,iface,pintar,no9000)
        #   Devuelve diferentes datos de salida de una carretera a partir de un punto
        #       return [the_road, m_final, the_road, funcion, atributos, distEJE, acimEJE]
        #   ENTRADA:
        #       point- Geometria punto (x,y)
        #       iface- Interface de la vista
        #       pintar- 'SI', 'NO'
        #       no9000= 'SI', 'NO' - SI Busca primero matriculas NO 9000
        #       tipoCapa=1 Capa tipo carreteras, tipoCapa=0 Capa de lineas estandard
        #   SALIDA:
        #       0  the_road - Matricula de la carretera
        #       1  m_final - Valor M (PK) de las coordenadas.
        #       2  the_road - Matricula de la carretera ############## ¿repetida? ##############
        #       3  funcion - Funcionalidad de la via
        #       4  atributos - Conjunto compelto de atributos como los devuelve el REST
        #       5  distEJE - Distancia del punto al eje
        #       6  acimEJE - Acimut del punto perpendicular del eje
        #       7  pointEJE- Punto en el eje (coordenas XY)
        #       8  geometry- Geometria del elemento
        #       9  distINI - Distancia al inicio del elemento
        #       10 distFIN - Distancia al final del elemento

        clicked_QgsPoint = QgsPointXY(point[0],point[1])
        # qgs_point_geometry = QgsGeometry.fromPointXY(QgsPointXY(point[0],point[1]))
        qgs_point_geometry = QgsGeometry.fromPointXY(clicked_QgsPoint)

        margin = 100        # Margen de búsqueda de viales en la GDB

        layer = iface.activeLayer()
        featuresLine = layer.getFeatures()

        rectMargin = QgsRectangle(point[0] - margin, point[1] - margin, point[0] + margin, point[1] + margin)

        c_distance = 100000     # Distancia límite de cálculo, por debajo no devuelve datos, se reduce con todas las dist calculadas
        the_feature = None
        qgsLines = []
        the_road = None
        matric = None
        funcion = None
        atributos = None
        the_lineM = None
        featsProx = []
        numFeat = 1

        message = ''

        for feature in featuresLine:
            polyline = []
            polylineM = [] ### Añadida M ###

            geom_line = feature.geometry()
            # print ('geom_line')
            # print (geom_line)
            if geom_line.intersects(rectMargin):
                geometry = feature.geometry()
                attr = {}
                for field in layer.fields():
                    attr[field.name()] = feature[field.name()]
                # print (attr)

                if tipoCapa == 1:
                    matric = feature["Matricula"]        # Matrícula del elemento
                    Titu = feature["Titularidad"]      # Titularidad del elemento
                    funcion = feature["Funcionalidad"]
                else:
                    matric = 's/d'        # Matrícula del elemento
                    Titu = 's/d'      # Titularidad del elemento
                    funcion = 's/d'

                paths = []
                if geometry.isMultipart():
                    for part in geometry.asGeometryCollection():
                        paths.append(part)
                else:
                    paths.append(geometry)

                # Habría que corregir la creación de la polylineM para casos de pths invertidos
                for path in paths:
                    novertices = len(path.asPolyline())
                    for id in range(novertices):
                        pointP = path.vertexAt(id)
                        gPnt = QgsGeometry.fromPointXY(QgsPointXY(pointP.x(),pointP.y()))
                        if(pointP.m() == None):
                            QgsMessageLog.logMessage("Ojo.. valor sin M",self.nombre_plugin)
                            polylineM.append(QgsPoint(pointP.x(),pointP.y()))
                        else:
                            polylineM.append(QgsPoint(pointP.x(),pointP.y(),pointP.m()))

                gLineM = QgsGeometry.fromPolyline(polylineM)
                distance = gLineM.distance(qgs_point_geometry)

                featsProx.append([matric, Titu, distance, feature, attr, gLineM, numFeat])

                if distance <= c_distance:
                    the_road = matric
                    c_distance = distance
                    the_feature = feature
                    atributos = attr
                    the_lineM = gLineM
                numFeat += 1

                if tipoCapa == 1:
                    # message += 'MATRIC= '+matric+ ' DIST= '+ str(round(distance,2))+ '\n'
                    message += 'MATRIC= %s DIST= %s\n'%(matric, str(round(distance,2)))
                else:
                    message += next(iter(attr))+':'+str(next(iter(attr.values())))+ ' DIST= '+ str(round(distance,2))+ '\n'

        # Analizar si matric = 9000
        if no9000 == 'SI' and the_road == '9000':
            c_distance = 1000000
            for featP in featsProx:
                if featP[0] != '9000':
                    if featP[2] <= c_distance:
                        the_road = featP[0]
                        c_distance = featP[2]
                        the_feature = featP[3]
                        atributos = featP[4]
                        the_lineM = featP[5]
                    pass

        if the_lineM == None:
            return None

        # self.showMessage( message,'','Identificador de Carreteras' )

        closest_point_geometry, dist, punto_anterior, punto_posterior, m_final, distINI, distFIN = self.calculaMproximo(the_lineM, clicked_QgsPoint)

        pointEJE = QgsPointXY(closest_point_geometry.x(),closest_point_geometry.y())
        pointANT = QgsPointXY(punto_anterior.x(),punto_anterior.y())
        pointPOS = QgsPointXY(punto_posterior.x(),punto_posterior.y())

        if pintar == 'SI':
            m = self.dibujarPunto(closest_point_geometry.x(),closest_point_geometry.y(),iface)

        # CALCULO DEL ACIMUT
        res = self.calcACIMUT(clicked_QgsPoint,pointEJE)
        res1 = self.calcACIMUT(pointANT,pointPOS)

        acimTRANS= res[1]
        acimEJE= res1[1]
        lado = (acimEJE - acimTRANS)
        if math.fabs(lado) > 180:
            if lado > 0:
                lado = -(lado-180)
            else:
                lado = -(lado+180)

        vlado = lado/90
        distEJE= res[0] * vlado
        if acimEJE < 0:
            acimEJE += 360

        #return        0        1         2        3          4        5        6         7,        8        9       10
        return [the_road, m_final, the_road, funcion, atributos, distEJE, acimEJE, pointEJE, geometry, distINI, distFIN]

    def poligToPKINIPKFIN(self, geomPol, iface, no9000):

        # poligToPKINIPKFIN(geomPol, iface, no9000)
        #   Devuelve diferentes datos de salida de una carretera a partir de un punto
        #       return (ctraBusq, mmin, mmax)
        #   ENTRADA:
        #       geomPol- Geometria del polígono
        #       iface- Interface de la vista
        #       noJCCM= 'SI', 'NO' - NO Busca primero matriculas Titularidad=JCCM
        #   SALIDA:
        #       0 ctraBusq - Matricula de la carretera
        #       1 mmin - Valor M (PK) del mínimo PK próximo del polígono
        #       2 mmax - Valor M (PK) del máximo PK próximo del polígono
        precision = 3

        if geomPol.isMultipart():
            polygon = geomPol.asMultiPolygon()
            single = False
        else:
            polygon = geomPol.asPolygon()
            single = True

        ## Obtenemos la geometría de la parcela con un buffer de 'bufDist'
        bufDist = 100
        geomBuffer = geomPol.buffer(bufDist, 1)
        geomArcgisESRI = geomBuffer.asJson().replace('coordinates','rings')
        # print ('GEOMETRIA DE LA PARCELA')
        # print (geomArcgisESRI)

        # geomXY = geomPol.asWkt().replace('MultiPolygon ','')

        resultINT = geomPol.poleOfInaccessibility(precision)    # Obtenemos el poleOfInaccessibility del polígono
        centerPolig = resultINT[0].asPoint()
        qgs_point_geometry = QgsGeometry.fromPointXY(QgsPointXY(centerPolig[0],centerPolig[1]))


        # Hacemos una consulta a la GDB de las vías que cortan un buffer de 'bufDist'
        url = current_configuration.general["rest_carreteras"]

        values = {'where' : '',
                  'text': '',
                  'objectIds': '',
                  'outFields': '*',
                  'geometry': geomArcgisESRI,
                  'geometryType' : 'esriGeometryPolygon',
                  'spatialRel': 'esriSpatialRelIntersects',
                  'spatialReference' : crsVal,
                  'outSR' : crsVal,
                  'geometryPrecision': 3,
                  'returnGeometry' : 'true',
                  'returnM': 'true' ,
                  'f': 'json'}

        str_values = {}
        for k, v in values.items():
            str_values[k] = unicode(v).encode('utf-8')
        data = urllib.parse.urlencode(str_values)
        # print ('fun.poligToPKINIPKFIN: ',url+data)

        try:
            response = requests.get(url+data, timeout=TIMEOUT_SEGUNDOS)
            response.raise_for_status()  # Lanza excepción si hay error HTTP (4xx, 5xx)
            response = response.json()  # Esto ya es el JSON parseado
        except urllib.error.URLError as e:
            QApplication.restoreOverrideCursor()
            txt = u"Error de conexión a internet\n"
            txt += self.PrintException()
            self.showMessageERR(txt)
            return None, None, None, None, None, None
        except TimeoutError:
            QApplication.restoreOverrideCursor()
            self.showMessageERR(u"Timeout: El servidor de carreteras no responde")
            return None, None, None, None, None, None
        # try:
            # response = json.load(urllib.request.urlopen(url+data))
        # except:
            # QApplication.restoreOverrideCursor()
            # # print (url+data)
            # txt = u"Error de conexión a internet\n"
            # txt+= self.PrintException()
            # self.showMessageERR(txt)
            # return None, None, None, None, None, None

        try:
            features =  response["features"]    # Los distintos features encontrados en la búsqueda
        except:
            QApplication.restoreOverrideCursor()
            txt = u"Error de ausencia de elementos en la respuesta\n"
            txt+= self.PrintException()
            self.showMessageERR(txt)
            return None, None, None, None, None, None

        c_distance = 100000     # Distancia límite de cálculo, por debajo no devuelve datos, se reduce con todas las dist calculadas
        the_feature = None
        qgsLines = []
        the_line = None
        ctraBusq = None
        matric = None
        funcion = None
        atributos = None
        featsProx = []
        numFeat = 1

        for feature in features:
            polyline = []
            polylineM = [] ### Añadida M ###

            geometry = feature["geometry"]
            attr =  feature["attributes"]
            matric = attr['Matricula']          # Matrícula del elemento
            Titu = attr['Titularidad']          # Titularidad del elemento

            funcion = attr['Funcionalidad']
            paths = geometry["paths"]
            # points = []
            for path in paths:
                for point in path:
                    polyline.append(QgsPoint(point[0],point[1]))
                    polylineM.append(QgsPoint(point[0],point[1],point[2]))  ### Añadida M ###

            gLine = QgsGeometry.fromPolyline(polyline)
            gLineM = QgsGeometry.fromPolyline(polylineM) ### Añadida M ###
            distance = gLine.distance(qgs_point_geometry) # Se calcula la distancia del centroide al elemento particular
            featsProx.append([matric, Titu, distance, gLine, feature, attr, numFeat, gLineM])

            if distance <= c_distance:
                ctraBusq = matric
                c_distance = distance
                the_line = gLine
                the_feature = feature
                atributos = attr
                the_lineM = gLineM ### Añadida M ###
            numFeat += 1

        num = 0
        for feat in featsProx:
            print ('ELEMENTO', num, feat[0],feat[1], feat[2])
            num += 1
        ###############################################################
        ###### TODO Esto se debe rehacer para dar prioridad a:   ######
        ######  - Elementos tronco sobre elementos 9000          ######
        ######  - Elementos Titularidad=JCCM sobre el resto      ######
        ######      aunque tuvieran mayor distancia              ######
        ###############################################################
        # Analizar si matric = 9000
        if no9000 == 'SI' and ctraBusq == '9000':
            c_distance = 1000000
            for featP in featsProx:             # Se analiza cada una de las feats Próximas
                if featP[0] != '9000':
                    if featP[2] <= c_distance:
                        ctraBusq = featP[0]
                        c_distance = featP[2]
                        the_line = featP[3]
                        the_feature = featP[4]
                        atributos = featP[5]
                        the_lineM = featP[6]    ### Añadida M ###
                    pass

        if the_line == None:
            return None, None, None, None, None, None


        # EMPEZAMOS A HACER LOS CÁLCULOS SOBRE LA LINEA

        cadena =''
        mmin = 1000000
        mmax = 0
        pointMin = 0
        pointMax = 0
        for parte in polygon:
            cadena += 'Poligono '+str(polygon.index(parte)+1)+'\n'
            i=1
            if single:
                for pto in parte:
                    cadena += " ".join([str(i),' - ',"{:.{}f}".format(pto[0], precision),' - ',"{:.{}f}".format(pto[1], precision),'\n'])
                    closest_point_geometry, dist, punto_anterior, punto_posterior, m_final, distINI, distFIN = self.calculaMproximo(the_lineM, pto)
                    # print (closest_point_geometry, dist, punto_anterior, punto_posterior, m_final)
                    if m_final == 'nan':
                        # print ('ctraBusq= ', ctraBusq,'PKINI: ', mmin, 'PKFIN: ', mmax)
                        return ctraBusq, 'Ctra sin PK', 'Ctra sin PK', None, None, None
                    if m_final < mmin:
                        mmin = m_final
                        pointMin = closest_point_geometry
                    if m_final > mmax:
                        mmax = m_final
                        pointMax = closest_point_geometry
                    i += 1
            else:
                for pto in parte[0]:
                    cadena += " ".join([str(i),' - ',"{:.{}f}".format(pto[0], precision),' - ',"{:.{}f}".format(pto[1], precision),'\n'])
                    closest_point_geometry, dist, punto_anterior, punto_posterior, m_final, distINI, distFIN = self.calculaMproximo(the_lineM, pto)
                    # print (closest_point_geometry, dist, punto_anterior, punto_posterior, m_final)
                    if m_final < mmin:
                        mmin = m_final
                        pointMin = closest_point_geometry
                    if m_final > mmax:
                        mmax = m_final
                        pointMax = closest_point_geometry
                    i += 1

        pointCentroid = QgsPointXY(centerPolig[0],centerPolig[1])
        pointEJE = QgsPointXY(closest_point_geometry.x(),closest_point_geometry.y())
        pointANT = QgsPointXY(punto_anterior.x(),punto_anterior.y())
        pointPOS = QgsPointXY(punto_posterior.x(),punto_posterior.y())

        # CALCULO DEL ACIMUT
        res = self.calcACIMUT(pointCentroid,pointEJE)
        res1 = self.calcACIMUT(pointANT,pointPOS)

        acimTRANS= res[1]
        acimEJE= res1[1]
        lado = (acimEJE - acimTRANS)
        if math.fabs(lado) > 180:
            if lado > 0:
                lado = -(lado-180)
            else:
                lado = -(lado+180)

        vlado = lado/90
        distEJE= res[0] * vlado
        if acimEJE < 0:
            acimEJE += 360

        if mmin == 1000000:
            # print ('ctraBusq= ', ctraBusq,'PKINI: ', mmin, 'PKFIN: ', mmax)
            # return ctraBusq, 'Ctra sin PK', 'Ctra sin PK', distEJE, None, None
            return ctraBusq, 'Ctra sin PK', 'Ctra sin PK', distEJE, 0, 0
        # print ('ctraBusq= ', ctraBusq,'PKINI: ', mmin, 'PKFIN: ', mmax, 'distEJE: ', distEJE)
        return ctraBusq, mmin, mmax, distEJE, pointMin, pointMax

    def calculaMproximo(self, the_lineM,  pto):
        # calculaMproximo(the_lineM,  pto)
        #   Devuelve el valor M de una geoemtría y punto
        #       return (target_point, dist, punto_anterior, punto_posterior, m_final, distINI, distFIN)
        #   ENTRADA:
        #       the_lineM - Geometria de la linea con M
        #       pto - geometría del punto
        #   SALIDA:
        #       0 target_point
        #       1 dist
        #       2 punto_anterior
        #       3 punto_posterior
        #       4 m_final
        #       5 distINI
        #       6 distFIN

        res = the_lineM.closestSegmentWithContext(pto)
        target_point =  QgsPoint(res[1][0],res[1][1])   # Punto más próximo en el eje mas próximo
        dist = res[0]                                   # Distancia del punto a la polilinea
        punto_posterior = the_lineM.vertexAt(res[2])    # N0. orden vértice posterior al pto. próximo
        m_posterior =  punto_posterior.z()              # Valor M del vértice posterior al pto. próximo
        # if m_posterior == 'nan':
            # m_final = 'noM'
            # return ('', '', '', '', m_final)
        # print ('m_posterior =', m_posterior)
        if res[2] > 0:
            punto_anterior = the_lineM.vertexAt(res[2]-1)
            m_anterior =  punto_anterior.z()
            # if m_anterior == 'nan':
                # m_final = 'noM'
                # return ('', '', '', '', m_final)
            # print ('m_anterior =', m_anterior)
            if punto_posterior.distance(punto_anterior) != 0:
                m_final = m_posterior - (punto_posterior.distance(target_point) / punto_posterior.distance(punto_anterior)) * (m_posterior - m_anterior)
            else:
                m_final = m_posterior
        else:
            m_final = m_posterior

        # print ('m_anterior:', m_anterior, ' m_posterior:', m_posterior, ' m_final:', m_final)

        distINI = the_lineM.distanceToVertex(res[2]-1)+target_point.distance(punto_anterior)
        distFIN = the_lineM.length()- distINI
        # print (the_lineM.length(), distINI, distFIN)

        return (target_point, dist, punto_anterior, punto_posterior, m_final, distINI, distFIN)

    def getValoresCampo(self, campo, filtro):
        url = self.conf.general["rest_carreteras"]
        params = {'where' : '1=1',
                  'text': '',
                  'objectIds': '',
                  'outFields': campo,
                  'orderByFields': campo,
                  'returnDistinctValues' : 'true',
                  'geometryType' : 'esriGeometryPolyline',
                  'returnGeometry' : 'false',
                 'returnM': 'false' ,
                 'f': 'json'}

        data = urllib.parse.urlencode(params)
        # print (url+data)
        try:
            response = requests.get(url+data, timeout=TIMEOUT_SEGUNDOS)
            response.raise_for_status()  # Lanza excepción si hay error HTTP (4xx, 5xx)
            response = response.json()  # Esto ya es el JSON parseado
            features =  response["features"]
        except:
            QApplication.restoreOverrideCursor()
            txt = u"Error de conexión a internet\n\n"
            txt+= self.PrintException()
            txt+= f'\n\nCargando valores de \'{campo}\''
            self.showMessageERR(txt)
            return

        # features =  response["features"]

        valores = []
        for feat in features:
            valor = feat["attributes"][campo]
            valores.append(valor)

        return valores

    def getFeaturesBTAcalibrada(self,values):

        url = self.conf.general["rest_carreteras"]
        campoBusqueda = self.conf.lrs["identificador_carretera_carreteras"]
        # https://geoservicios.castillalamancha.es/arcgis/rest/services/WFS/Plan_Carreteras_BTA_WFS/MapServer/0/query?
        # values = {'where' : self.conf.lrs["identificador_carretera_carreteras"] + " = '" + road_name + u"'",
        # values = {'where' : 'Matricula' + " = '" + road_name + u"'",
        # values = {'where' : u"'" + campoBusqueda + u"' = '" + road_name + u"'",
        # values = {'where' : 'Matricula_Plan' + " = '" + road_name + u"'",
                  # 'text': '',
                  # 'objectIds': '',
                  # 'geometryType' : 'esriGeometryPolyline',
                  # 'returnGeometry' : 'true',
                  # 'returnM': 'true',
                  # 'geometryPrecision': 3,
                  # 'outFields': '*',
                  # 'f': 'json'}

        str_values = {}
        for k, v in values.items():
            str_values[k] = unicode(v).encode('utf-8')
        data = urllib.parse.urlencode(str_values)
        # print (url+data)
        try:
            response = requests.get(url+data, timeout=TIMEOUT_SEGUNDOS)
            response.raise_for_status()  # Lanza excepción si hay error HTTP (4xx, 5xx)
            response = response.json()  # Esto ya es el JSON parseado
            features = response["features"]
            return features
        except urllib.error.URLError as e:
            QApplication.restoreOverrideCursor()
            result = self.PrintException()
            self.showMessageERR(result, text2="", tittle=self.nombre_plugin+" - Error de código")
            return []
        except TimeoutError:
            QApplication.restoreOverrideCursor()
            self.showMessageERR("Timeout: El servidor de carreteras no responde", tittle=self.nombre_plugin+" - Timeout")
            return []
        # try:
            # response = json.load(urllib.request.urlopen(url+data))
            # # print (response)
            # features =  response["features"]
            # # print (features)
            # return features
        # except:
            # QApplication.restoreOverrideCursor()
            # result = self.PrintException()
            # self.showMessageERR(result,text2="",tittle=self.nombre_plugin+" - Error de código",)
            # return []

    def getFeaturesBTAcalibradaCount(self,values):
        url = self.conf.general["rest_carreteras"]

        str_values = {}
        for k, v in values.items():
            str_values[k] = unicode(v).encode('utf-8')
        data = urllib.parse.urlencode(str_values)
        # req = urllib.request.Request(url, data)

        try:
            response = requests.get(url+data, timeout=TIMEOUT_SEGUNDOS)
            response.raise_for_status()  # Lanza excepción si hay error HTTP (4xx, 5xx)
            response = response.json()  # Esto ya es el JSON parseado
            return response
        except urllib.error.URLError as e:
            QApplication.restoreOverrideCursor()
            result = self.PrintException()
            self.showMessageERR(result, text2="", tittle=self.nombre_plugin+" - Error de código")
            return []
        except TimeoutError:
            QApplication.restoreOverrideCursor()
            self.showMessageERR("Timeout: El servidor de carreteras no responde", tittle=self.nombre_plugin+" - Timeout")
            return []
        # try:
            # response = json.load(urllib.request.urlopen(url+data))
            # return response
        # except:
            # QApplication.restoreOverrideCursor()
            # result = self.PrintException()
            # self.showMessageERR(result,text2="",tittle=self.nombre_plugin+" - Error de código",)
            # return []

    def getFeaturesCarretera(self,road_name):

        # https://geoservicios.castillalamancha.es/arcgis/rest/services/WFS/Plan_Carreteras_BTA_WFS/MapServer/0/query?
        # values = {'where' : self.conf.lrs["identificador_carretera_carreteras"] + " = '" + road_name + u"'",
        # values = {'where' : 'Matricula' + " = '" + road_name + u"'",
        # values = {'where' : u"'" + campoBusqueda + u"' = '" + road_name + u"'",

        url = self.conf.general["rest_carreteras"]
        campoBusqueda = self.conf.lrs["identificador_carretera_carreteras"]
        # whereCONS = self.conf.lrs["identificador_carretera_carreteras"] + " like '" + road_name + u"%' and Matricula <> '9000'"
        # values = {'where' : u"'" + campoBusqueda + "' = '" + road_name + u"'",
        # whereCONS = campoBusqueda + " like '" + road_name + u"%' and Matricula <> '9000'"
        whereCONS = campoBusqueda + " like '" + road_name + u"' and Matricula <> '9000'"
        values = {'where' : whereCONS,
                  'text': '',
                  'objectIds': '',
                  'geometryType' : 'esriGeometryPolyline',
                  'returnGeometry' : 'true',
                  'returnM': 'true',
                  'geometryPrecision': 3,
                  'outFields': '*',
                  'f': 'json'}

        data = urllib.parse.urlencode(values)
        # print ('getFeaturesCarretera = ',data)
        try:
            response = requests.get(url+data, timeout=TIMEOUT_SEGUNDOS)
            response.raise_for_status()  # Lanza excepción si hay error HTTP (4xx, 5xx)
            response = response.json()  # Esto ya es el JSON parseado
            features = response["features"]
            return features
        except urllib.error.URLError as e:
            QApplication.restoreOverrideCursor()
            result = self.PrintException()
            self.showMessageERR(result, text2="", tittle=self.nombre_plugin+" - Error de código")
            return []
        except TimeoutError:
            QApplication.restoreOverrideCursor()
            self.showMessageERR("Timeout: El servidor de carreteras no responde", tittle=self.nombre_plugin+" - Timeout")
            return []
        # try:
            # response = json.load(urllib.request.urlopen(url+data))
            # features =  response["features"]
            # # print (features)
            # return features
        # # except Exception, e:
        # except:
            # QApplication.restoreOverrideCursor()
            # result = self.PrintException()
            # self.showMessageERR(result,text2="",tittle=self.nombre_plugin+" - Error de código",)
            # return []

    def getFeaturesCarretera_GPKG(self, road_name, ruta_geopackage, nombre_capa_ctras):
        ###################################################################################
        # PROBLEMA DE LAS VERSIONES DE QGIS
        versionQGS = Qgis.QGIS_VERSION
        print ('versionQGS= ', versionQGS)
        ###################################################################################

        if versionQGS < '3.29':  # Caso de QGIS v 3.28.xx (con Fiona)
            import fiona
            campoBusqueda = self.conf.lrs["identificador_carretera_carreteras"]
            features = []
            geometrias = []

            try:
                with fiona.open(ruta_geopackage, 'r', layer=nombre_capa_ctras) as src:
                    campo_existente = campoBusqueda.lower() in [campo.lower() for campo in src.schema['properties']]
                    if not campo_existente:
                        print(f"Advertencia: El campo {campoBusqueda} no existe en la capa {nombre_capa_ctras}")
                        return [], []  # Devuelve listas vacías

                    for feature in src:
                        if feature['properties'][campoBusqueda] == road_name:
                            features.append(feature)
                            shapely_geometry = wkt_loads(shape(feature['geometry']).wkt)
                            ogr_geometry = ogr.CreateGeometryFromWkt(shapely_geometry.wkt)
                            geometrias.append(ogr_geometry)

            except Exception as e:
                print(f"Error al procesar el archivo GPKG: {e}")
                return [], []  # Devuelve listas vacías en caso de error

            return features, geometrias  # Devuelve las listas llenas o vacías

        else:  # Caso para QGIS 3.29+ (PyQGIS)
            campoBusqueda = self.conf.lrs["identificador_carretera_carreteras"]
            features = []
            geometrias = []

            try:
                # Cargar la capa vectorial desde el GeoPackage
                layer_path = f"{ruta_geopackage}|layername={nombre_capa_ctras}"
                print(f"Intentando cargar la capa desde: {layer_path}")
                layer = QgsVectorLayer(layer_path, nombre_capa_ctras, "ogr")

                # Verificar si la capa se carga correctamente
                if not layer.isValid():
                    print(f"Advertencia: No se pudo cargar la capa {nombre_capa_ctras} desde {ruta_geopackage}")
                    return [], []  # Devuelve listas vacías en caso de error

                print(f"Capa {nombre_capa_ctras} cargada correctamente.")

                # Verificar si el campo de búsqueda existe en la capa
                campo_existente = campoBusqueda.lower() in [field.name().lower() for field in layer.fields()]
                if not campo_existente:
                    print(f"Advertencia: El campo {campoBusqueda} no existe en la capa {nombre_capa_ctras}")
                    return [], []  # Devuelve listas vacías si el campo no existe

                print(f"Campo {campoBusqueda} encontrado en la capa.")

                # Crear expresión para buscar las features que coincidan con el road_name
                expression = QgsExpression(f'"{campoBusqueda}" = \'{road_name}\'')
                print(f"Expresión de búsqueda: {expression.expression()}")

                if expression.hasParserError():
                    print(f"Error en la expresión: {expression.parserErrorString()}")
                    return [], []  # Retorna listas vacías si hay un error en la expresión

                request = QgsFeatureRequest(expression)

                # Iterar sobre las features que cumplen la condición
                for feature in layer.getFeatures(request):
                    features.append(feature)
                    geometrias.append(feature.geometry())

                print(f"Se encontraron {len(features)} features para la carretera {road_name}.")
                return features, geometrias  # Devuelve las listas llenas o vacías

            except Exception as e:
                print(f"Error al procesar la capa en PyQGIS: {e}")
                return [], []  # Devuelve listas vacías en caso de error

    def restLineFeaturesToOgrFeatures(self,restFeatures):
        features = []
        for feat in restFeatures:
            line = ogr.Geometry(ogr.wkbLineStringM)
            geometry = feat["geometry"]
            paths = geometry["paths"]
            for path in paths:
                for point in path:
                    line.AddPoint(point[0],point[1])
            features.append(line)
        return features

    def mostraEventosFromCSVLayer(self,layer, iface,tipomed,campo_carretera,campo_pkini,campo_pkiniDist,campo_pkfin,campo_pkfinDist,campo_disteje,dest_path,progressBar_dlg,infolbl,dest_name,maxfeat,RECALC,FactPKINI,FactPKFIN, menu):
        # (selected_table,self.iface,tipomed,campo_carretera,campo_pk_ini,campo_pkiniDist,campo_pk_fin,campo_pkfinDist,campo_disteje,dest_path,progressBar_dlg,infolbl,dest_name,maxfeat,self.RECALC,FactPKINI,FactPKFIN,menu)
        # mostraEventosFromCSVLayer(self,layer, iface,campo_carretera,campo_pkini,campo_pkfin,dest_path)
        #   Crea una capa a partir de eventos CTRA, PKINI, PKFIN

        es_puntual = False
        es_disteje = False

        #Borrado del fichero y capa si existen
        layerEXIST = QgsProject.instance().mapLayersByName(dest_name)
        # print (dest_name)
        if layerEXIST:
            for layer1 in layerEXIST:
                QgsProject.instance().removeMapLayer( layer1.id() )
                # print ('borrada - ',dest_name)


        if (campo_pkfin == ""):
            es_puntual = True

        if (campo_disteje != ""):
            es_disteje = True

        es_memoria = False
        if dest_path == "" or dest_path == "en_memoria":
            es_memoria = True
        else:
            self.comprobarDirectorio(dest_path)

        # Se crea la estructura de las capas
        if es_puntual:  # Capa Puntual
            dest_layer = self.createVectorLayer("point?crs=epsg:"+str(crsVal), dest_name)
            if tipomed == 'CALIBRADO':
                estiloCAPA = os.path.join(os.path.dirname(__file__), self.conf.general["carpeta_estilos"] + '/EVENTOS_PUNTUALES.qml')
            else:
                estiloCAPA = os.path.join(os.path.dirname(__file__), self.conf.general["carpeta_estilos"] + '/EVENTOS_PUNTUALES_dist.qml')
        else:           # Capa Lineal
            dest_layer = self.createVectorLayer("linestring?crs=epsg:"+str(crsVal), dest_name)

        # Detección de campos de la capa CSV origen
        fields = layer.fields()

        # Creación Fichero y Capa de log
        QgsMessageLog.logMessage( "Creando archivo de log",self.nombre_plugin)
        log_csv = self.conf.lrs["default_log_folder"] + "Log.csv"
        if(es_memoria == False):
            log_csv =  os.path.splitext(dest_path)[0] +  os.path.splitext(dest_path)[1].split(".")[0] + "_log.csv"

        target  = codecs.open(log_csv, 'w+',encoding='utf-8')
        if tipomed == 'CALIBRADO':
            encabezado = u'"carretera";"pk_ini";"pk_fin";"dist";"result";"observaciones"'
        else:
            encabezado = u'"carretera";"pk_ini";"pk_iniDist";"pk_fin";"pk_finDist";"dist";"result";"observaciones"'
        for field in fields:
            encabezado += u';' + field.name()
        target.write(encabezado)
        target.write("\n")
        target.close()

        log_csv_uri = u"file:///"+ log_csv +"?type=csv&geomType=none&subsetIndex=no&delimiter=%s&watchFile=no" % (";")

        # Creación de la capa de LOG
        log_lyr = QgsVectorLayer(log_csv_uri, 'Log','delimitedtext')
        QgsProject.instance().addMapLayer(log_lyr)

        #Creación de campos de la capa SHAPE
        pr = dest_layer.dataProvider()
        dest_layer.startEditing()
        # fields = layer.fields()
        attributes = []
        for field in fields:
            attributes.append(QgsField(field.name(),field.type()))
        pr.addAttributes(attributes)
        dest_layer.updateFields()
        dest_layer.commitChanges()


        nofeat = 1
        if maxfeat == 0:
            maxfeat = 99999
        features = layer.selectedFeatures()
        numfeat = len(features)

        if numfeat == 0:
            features = layer.getFeatures()
            numfeat = layer.featureCount()

        self.running = True

        if (numfeat > 600 and maxfeat > 600):
            # Debemos poner un aviso de que el cálculo puede no salir bien
            if maxfeat == 99999:
                text = u'La capa de origen tiene '+"%0.0f"%(numfeat)+' elementos.\n'
            else:
                text = u'Se ha limitado el proceso a '+"%0.0f"%(maxfeat)+' elementos de '+"%0.0f"%(numfeat)+' en total.\n'
            text +=u'Realizar este proceso con más de 600 elementos podría generar interrupciones del mismo.\n\n'
            text +=u'Se recomienda dividir el fichero de entrada en otros ficheros con un máximo de 600 elementos.\n\n'
            text +=u'               ¿DESEA CONTINUAR?'
            result = self.showMessageYESNO(text,'','EXCESO DE ELEMENTOS' )
            if result != 1024: # No e ha pulsado ACEPTAR
                return
            pass

        time0 = timeit.default_timer()
        # print ('maxfeat', maxfeat)
        for feature in features:
            if nofeat > maxfeat:
                infolbl.setText('INFO: ('+str(nofeat)+' / '+str(numfeat)+') ALCANZADO MÁXIMO '+ str(maxfeat) )
                break

            target  = codecs.open(log_csv, 'a',encoding='utf-8')

            matricula = feature[campo_carretera]
            if not matricula:
                matricula = 'NO-CARRETERA'

            if (es_puntual):    ####  ES PUNTUAL   ####
                # print 'Evento Puntual: ('+str(nofeat)+' / '+str(numfeat),')',
                # print ' CTRA:',matricula,' PKINI:',feature[campo_pkini]
                if tipomed == 'CALIBRADO':   #### tipomed == 'CALIBRADO'   ####
                    try:
                        pk_ini = float(feature[campo_pkini])/float(FactPKINI)
                        pk_iniDist = 0
                        # pk_ini = Decimal(feature[campo_pkini])/Decimal(FactPKINI)
                    except:
                        pk_ini = None
                        pk_iniDist = None

                    # print ('matricula', matricula, 'feature[campo_pkini]', feature[campo_pkini])
                    # if pk_ini is not NULL or pk_ini == 0.0:
                    if pk_ini not in (None, 0.0):
                        disteje = 0
                        if es_disteje:
                            try:
                                disteje = float(feature[campo_disteje])
                            except:
                                pass
                        result = self.addEventoPuntual(iface,dest_layer,matricula,pk_ini, pk_iniDist,disteje,feature,fields,log_csv,tipomed)
                        # print ('resp', result[0],result[1])
                else:    #### tipomed == 'DIST A PLACA'   ####
                    try:
                        pk_ini = float(feature[campo_pkini])
                        pk_iniDist = float(feature[campo_pkiniDist])

                        # pk_ini = Decimal(feature[campo_pkini])/Decimal(FactPKINI)
                    except:
                        pk_ini = None
                        pk_iniDist = None

                    # if pk_ini is not NULL or pk_ini == 0.0:
                    if pk_ini not in (None, 0.0):
                        disteje = 0
                        if es_disteje:
                            try:
                                disteje = float(feature[campo_disteje])
                            except:
                                pass
                        result = self.addEventoPuntual(iface,dest_layer,matricula,pk_ini, pk_iniDist,disteje,feature,fields,log_csv,tipomed)

                        # (self,layer, iface,tipomed,campo_carretera,campo_pkini,campo_pkiniDist,campo_pkfin,campo_pkfinDist,campo_disteje,dest_path,progressBar_dlg,infolbl,dest_name,maxfeat,RECALC,FactPKINI,FactPKFIN, menu)

                    else:
                        result = ["Error","PK nulo"]

                resp = result[0]
                error= result[1]
                # linea = u'"'+ matricula +'";'+str(pk_ini)+ ';;;'+resp+';'+error+';""'
                linea = u'"'+ matricula +'";'+str(pk_ini)+ ';;;'+resp+';'+error
                for field in fields:
                    linea += u';' + str(feature[field.name()])
                target.write(linea)
                target.write("\n")
                target.close()


            else:   ####  ES LINEAL   ####
                # print 'Evento lineal: ('+str(nofeat)+' / '+str(numfeat),')',
                # print ' CTRA:',matricula,' PKINI:',feature[campo_pkini], ' PKFIN:',feature[campo_pkfin]

                if tipomed == 'CALIBRADO':   #### tipomed == 'CALIBRADO'   ####
                    try:
                        pk_ini = float(feature[campo_pkini])/float(FactPKINI)
                        # pk_ini = Decimal(feature[campo_pkini])/Decimal(FactPKINI)
                    except:
                        pk_ini = None

                    try:
                        pk_fin = float(feature[campo_pkfin])/float(FactPKFIN)
                    except:
                        pk_fin = None

                    disteje = 0
                    if es_disteje:
                        try:
                            disteje = float(feature[campo_disteje])
                        except:
                            pass

                    if pk_ini is not None and pk_fin is not None and  pk_fin > pk_ini:
                        # Se añade evento lineal
                        # result = self.addEventoLineal(iface,dest_layer,matricula,pk_ini,pk_fin,feature,fields,log_csv)
                        result = self.addEventoLineal(iface,dest_layer,matricula,pk_ini,pk_fin,disteje,feature,fields,log_csv)
                    else:
                        if pk_ini is None and pk_fin is None:
                            result = ["Error","PK Ini y Fin nulos"]
                        elif pk_ini is None:
                            result = ["Error","PK Inicial nulo"]
                        elif pk_fin is None:
                            result = ["Error","PK Final nulo"]
                        elif pk_fin <= pk_ini:
                            result = ["Error","PKFin < PKIni"]

                    resp = result[0]
                    error= result[1]
                    # linea = u'"'+ matricula +'";'+str(pk_ini)+ ';'+str(pk_fin)+ ';;'+resp+';'+error+';""'
                    linea = u'"'+ matricula +'";'+str(pk_ini)+ ';'+str(pk_fin)+ ';;'+resp+';'+error
                    for field in fields:
                        linea += u';' + str(feature[field.name()])
                    target.write(linea)
                    target.write("\n")
                    target.close()

                else: #### tipomed == 'DIST A PLACA'   ####
                    mess = u'-- LA APLICACIÓN NO CALCULA AÚN TRAMOS CON LA OPCIÓN -DIST A PLACA --'
                    self.showMessage(mess)


            # print ('resp', resp,result[1]))
            timeACT = timeit.default_timer()
            faltaTime = 0
            if maxfeat != 99999 and maxfeat<numfeat:
                progressBar_dlg.setValue(int(100*nofeat/maxfeat))
                if nofeat > 0:
                    faltaTime = (timeACT - time0)/nofeat*maxfeat-(timeACT - time0)
                infolbl.setText('INFO: ('+str(nofeat)+' / '+str(maxfeat)+') Total: '+str(numfeat)+' elementos' + '    Falta: '+str(self.timeTOhms(faltaTime))+' s.')
            else:
                # progressBar_dlg.setValue(100*nofeat/numfeat)
                progressBar_dlg.setValue(int(100*nofeat/numfeat))
                if nofeat > 0:
                    faltaTime = (timeACT - time0)/nofeat*numfeat-(timeACT - time0)
                infolbl.setText('INFO: ('+str(nofeat)+' / '+str(numfeat)+') '+resp+' - '+error + '    Falta: '+str(self.timeTOhms(faltaTime))+' s.')

            # self.btnCancelar.clicked.connect(self.cancelar_Calculo)
            #self.btnCancelar.clicked.connect(self.running = False)

            #https://gis.stackexchange.com/questions/137537/stopping-pyqgis-script-that-has-infinite-loop-using-keyboard
            # print 'procesando - '+str(nofeat)+'/'+str(numfeat)

            nofeat += 1


        if(es_memoria):
            QgsProject.instance().addMapLayer(dest_layer)
        else:
            pr = dest_layer.dataProvider()
            fields = pr.fields()

            field_names = []
            for field_name in fields:
                field_names.append(field_name.name())
            #print field_names

            ruta, shp_file = os.path.split(dest_path)
            shp_name = shp_file.split(".")[0]

            if os.path.isfile(dest_path):
                 for path in os.listdir(ruta):
                     ruta_tmp, file = os.path.split(path)
                     if(file.split(".")[0]  == shp_name):
                         file_path= ruta + "/" + file
                         os.remove(file_path)


            if es_puntual:
                writer = QgsVectorFileWriter(dest_path, "latin-1", fields, QgsWkbTypes.Point, pr.crs(), "ESRI Shapefile")
            else:
                writer = QgsVectorFileWriter(dest_path, "latin-1", fields, QgsWkbTypes.MultiLineStringZM, pr.crs(), "ESRI Shapefile")
            iter = dest_layer.getFeatures()
            for ft in iter:  # Bucle del conjunto de elementos
                # Se crea un nuevo elemento de cada elemento original
                new_ft = QgsFeature()
                # Asignamos una geometría
                new_ft.setGeometry(ft.geometry())
                attributes = []
                for field in field_names:
                    attributes.append(ft[field])
                #print attributes
                # Only keep the 2 selected fields :
                new_ft.setAttributes(attributes)
                # Add the feature to the writer, ie. your output shapefile :
                #print ft
                writer.addFeature(new_ft)

            del writer # Features are written when the writer is deleted
            new_layer = iface.addVectorLayer(dest_path, dest_name, "ogr")

            if es_puntual:  # Capa Puntual
                new_layer.loadNamedStyle(estiloCAPA)
            QgsProject.instance().addMapLayer(new_layer)

        pass

    def getFeatureForPK(self, features ,pk, tipo):

        pk_feature = None
        #print "Features: " + str(len(features))

        min0 = 100000
        max0 =-100000
        featureMin = None
        featureMax = None
        for feature in features:
            geometry = feature["geometry"]
            paths = geometry["paths"]
            puntos = []
            for path in paths:
                for point in path:
                    puntos.append(point)

            #print "puntos: " + str(len(puntos))

            creciente = True
            min = puntos[0][2]
            max = puntos[0][2]

            for point in puntos:
                if point[2] is not None and point[2] < min:
                    #####################################################
                    # error en elemento en que PKINI es igual a PKFIN
                    #####################################################
                    min = point[2]
                if point[2] is not None and point[2] > max:
                    max = point[2]
            if (min is not None and max is not None):
                if (min <= pk and pk <= max):
                    pk_feature = feature
                    #print "Feature max: " + str(min)
                    #print "Feature min: " + str(max)
                    # print ('min= ', min, '  pk= ', pk , ' max= ', max, 'FEATURE: ', feature.index(features),'/',len(features))
                    print ('min= ', min, '  pk= ', pk , ' max= ', max)
                    return pk_feature, min, max

                if min <= min0:
                    min0 = min
                    featureMin = feature
                if max >= max0:
                    max0=max
                    featureMax = feature

        if tipo == 'min' and min0 is not None:
            print ('min0= ', min0, '  pk= ', pk , ' max= ', max)
            return featureMin, min0, max
        if tipo == 'max' and max0 is not None:
            print ('min= ', min, '  pk= ', pk , ' max0= ', max0)
            return featureMax, min, max0

        print ('pk_feature:', pk_feature,'min= ', min, '  pk= ', pk , ' max= ', max, 'FEATURE: ', pk_feature.index(features),'/',len(features))
        return pk_feature, min, max

    def addEventoPuntual(self,iface,vectorlayer,matricula,pk, pk_iniDist,disteje,feature,fields,log_csv,tipomed):
        # QgsMessageLog.logMessage( "Evento puntual: " + matricula +", " + str( pk), self.nombre_plugin)

        #run registro en el log_csv por punto...
        # ANALIZAR QUÉ PASA CON VIÑEDOS
        #https://geoservicios.castillalamancha.es/arcgis/rest/services/WFS/Plan_Carreteras_BTA_WFS/MapServer/0/query?
        # where=Matricula_plan+%3D+%27CM-42+D+%28Av.de+los+Vi%C3%B1edos%29%27
        # &geometryType=esriGeometryEnvelope
        # &spatialRel=esriSpatialRelIntersects
        # &outFields=*
        # &returnGeometry=false
        # &returnTrueCurves=false
        # &returnIdsOnly=false&returnCountOnly=false
        # &returnZ=false
        # &returnM=false
        # &returnDistinctValues=false
        # &returnExtentsOnly=false
        # &f=html

        if (pk is None or pk == ""):
            #print "Pk nulo o incorrecto"
            resp = "Error"
            error = "Pk nulo o incorrecto"
            linea = u'"'+ matricula +'";'+str(pk)+ ';'';;'+resp+';'+error+';""'
            return resp, error

        elif matricula in (None, ""):
            #print "Evento puntual sin matricula"
            resp = "Error"
            error = "Matricula incorrecta o nula"
            linea = u'"'+ matricula +'";'+str(pk)+ ';'';;'+resp+';'+error+';""'
            return resp, error

        # coords = self.CtraPktoCoorsAcim(matricula, pk)
        coords = self.CtraPktoCoorsAcim(matricula, pk, pk_iniDist, tipomed)

        if not self.isFloat(coords[0]):
            #print "No hay datos M"
            resp = "Error"
            error = coords [7:]
            linea = u'"'+ matricula +'";'+str(pk)+ ';'';;'+resp+';'+error+';""'
            return resp, error

        pr = vectorlayer.dataProvider()
        vectorlayer.startEditing()
        # Añade un elemento
        fet = QgsFeature(vectorlayer.fields())

        fieldnames = []
        for field in fields:
           #print "fieldname = "  + field.name()
           fieldnames.append(field.name())

        # SE CALCULA EL DESPLAZADO CON EL ACIMUT
        acim = coords[2]
        if (disteje != 0 and disteje != None):
            x = coords[0] + disteje * math.cos(acim*math.pi/180)
            y = coords[1] - disteje * math.sin(acim*math.pi/180)
            # print matricula, pk, acim, disteje, disteje * math.cos(acim), disteje * math.sin(acim)
            fet.setGeometry( QgsGeometry.fromPointXY(QgsPointXY(x,y)) )
        else:
            fet.setGeometry( QgsGeometry.fromPointXY(QgsPointXY(coords[0],coords[1])) )
        fet.setAttribute("carretera", matricula)
        fet.setAttribute("pk_ini", pk)
        if tipomed == 'DISTPK':
            fet.setAttribute("pk_iniDist", pk_iniDist)
        fet.setAttribute("acimut", acim)
        fet.setAttribute("distancia", disteje)

        for field_name in fieldnames:
            fet.setAttribute(field_name,feature[field_name])

        pr.addFeatures( [ fet ] )
        vectorlayer.updateExtents()
        vectorlayer.commitChanges()

        resp = "OK"
        error = ""
        linea = u'"'+ matricula +'";'+str(pk)+ ';'';;'+resp+';'+error+';""'
        return resp, error

    def addEventoLineal(self,iface,vectorlayer,matricula,pk_ini,pk_fin,disteje,feature_csv,fields,log_csv):
        # print ("Evento lineal: " + matricula + ", " + str(pk_ini) + ", " + str(pk_fin) +", " + str(disteje) )

        if pk_ini == pk_fin:
            resp = "Error"
            error = "PK inicial igual PK final"
            return resp, error

        features = self.getFeaturesCarretera(matricula)
        line_ogr_error = None
        aviso = ""
        if len(features) == 0:
            resp = "Error"
            error = "Matricula desconocida"
            return resp, error
            # linea = u'"'+ matricula +'";'+str(pk_ini)+ ';'+str(pk_fin) +';;'+resp+';'+error+';""'


        ##############################################################################

        ######      INICIO CAMBIOS

        ##############################################################################
        # Calculamos el tramo de linea correspondiente a la carretera y tramo
        gLine, MminTramo, MmaxTramo, attrFinales, multiline  = self.getTramoCtra(matricula, pk_ini, pk_fin, disteje)

        # AQUÍ HAY QUE CALCULAR EL DESPLAZADO CON EL ACIMUT

        if gLine.isEmpty():
            resp = "Error"
            error = 'EL TRAMO NO EXISTE'
            return resp, error

        pr = vectorlayer.dataProvider()
        vectorlayer.startEditing()
        # Añadimos el feature
        fet = QgsFeature(vectorlayer.fields())

        fet.setGeometry( gLine )
        fet.setAttribute("carretera", matricula)
        fet.setAttribute("pk_ini", MminTramo)
        fet.setAttribute("pk_fin", MmaxTramo)

        ##############################################################################
        ##############################################################################

        ##############################################################################
        ######      FINAL CAMBIOS
        ##############################################################################



        fieldnames = []

        for field in fields:
            fieldnames.append(field.name())

        for field_name in fieldnames:
            fet.setAttribute(field_name,feature_csv[field_name])


        if(line_ogr_error is not None or aviso != ""):
            if line_ogr_error is None:
                line_ogr_error = ""
            resp = "AVISO"
            error = line_ogr_error+ '. ' + aviso
            # linea = u'"'+ matricula +'";'+str(pk_ini)+ ';'+str(pk_fin) +';;'+resp+';'+error+';""'
        else:
            resp = "OK"
            if disteje !=0:
                resp = "OK, Dist"+ str(disteje)+" IGNORADA"
            error = ''
            # linea = u'"'+ matricula +'";'+str(pk_ini)+ ';'+str(pk_fin) +';;'+resp+';'+error+';""'

        pr.addFeatures( [ fet ] )
        vectorlayer.updateExtents()
        vectorlayer.commitChanges()
        return resp, error

    def getTramoCtra(self, road_name, pkini, pkfin, disteje):
        ####################################################################################
        ####################################################################################
        #
        # Devuelve la geometria y atributos de un tramo dado por 'road_name, pkini, pkfin, disteje)'
        #           return (gLine, MminTramo, MmaxTramo, attrFinales)
        # TODO pendiente de hacer algo con DISTEJE en elementos lineales
        ####################################################################################
        ####################################################################################

        features = self.getFeaturesCarretera(road_name)
        line_ogr_error = None
        aviso = ""

        restfeatures = self.getFeaturesCarretera(road_name)

        if len(features) == 0:
            msg = u'TRAMO DE CARRETERA DESONOCIDA\n\n'
            msg += 'CARRETERA: '+ road_name + ' - pkini: ' + str(pkini) + ' - pkfin: ' + str(pkfin)
            # print (msg)
            return None,None,None,None,None

        multiline = ogr.Geometry(ogr.wkbMultiLineString)

        MminTramo = 1000000
        MmaxTramo = 0

        for feat in restfeatures:
            geometry = feat["geometry"]
            paths = geometry["paths"]
            attr =  feat["attributes"]
            if road_name != attr['Matricula']:
                continue
            attrFinales = ''
            if attr['Matricula'] == '9000':
                # print (attr['Matricula'])
                continue
            # print (attr['Matricula'])

            for path in paths:
                line1 = ogr.Geometry(ogr.wkbLineString)
                posinpath = 0
                for point in path:
                    if posinpath < len(path)-1:
                        pointSIG = path[posinpath+1]
                    try:
                        if point[2]:
                            # El punto tiene 'M'
                            if pkini == point[2]:                           # El punto es 'pkini'
                                line1.AddPoint(point[0],point[1],point[2])
                                MminTramo = point[2]

                            if pkfin == point[2]:                           # El punto es 'pkfin'
                                line1.AddPoint(point[0],point[1],point[2])
                                MmaxTramo = point[2]

                            if point[2]<pointSIG[2]:                        # Segmento PK Creciente ++++
                                if (point[2] < pkini and pkini < pointSIG[2]):    # Segmento del PKINI
                                    xINI, yINI, acimINI = self.pointMsegment(pkini, point, pointSIG)
                                    line1.AddPoint(xINI, yINI, pkini)
                                    MminTramo = pkini
                                    attrFinales = attr
                                if (point[2] < pkfin and pkfin < pointSIG[2]):    # Segmento del PKFIN
                                    xFIN, yFIN, acimFIN = self.pointMsegment(pkfin, point, pointSIG)
                                    line1.AddPoint(xFIN, yFIN, pkfin)
                                    MmaxTramo = pkfin
                                    attrFinales = attr
                            if point[2]>pointSIG[2]:                        # Segmento PK Decreciente ----
                                if (point[2] > pkini and pkini > pointSIG[2]):    # Segmento del PKINI
                                    xINI, yINI, acimINI = self.pointMsegment(pkini, point, pointSIG)
                                    line1.AddPoint(xINI, yINI, pkini)
                                    MminTramo = pkini
                                    attrFinales = attr
                                if (point[2] > pkfin and pkfin > pointSIG[2]):    # Segmento del PKFIN
                                    xFIN, yFIN, acimFIN = self.pointMsegment(pkfin, point, pointSIG)
                                    line1.AddPoint(xFIN, yFIN, pkfin)
                                    MmaxTramo = pkfin
                                    attrFinales = attr

                            if pkini < point[2] and point[2] < pkfin:         # El punto está entre 'pkini' y 'pkfin' CON 'M'
                                # El punto está entre 'pkini' y 'pkfin'
                                line1.AddPoint(point[0],point[1],point[2])
                                if point[2] <= MminTramo: MminTramo = point[2]
                                if point[2] >= MmaxTramo: MmaxTramo = point[2]

                    except:
                        pass                                                  # El punto NO tiene 'M'
                    posinpath += 1

                # Se desplaza la linea a la distancia disteje si es distinto de 0
                if disteje != 0:
                    displaced_line = self.desplazaEje(line1, disteje)
                    multiline.AddGeometry(displaced_line)
                else:
                    multiline.AddGeometry(line1)

        gLine = QgsGeometry.fromWkt(multiline.ExportToWkt())

        # print ('road_name, pkini, pkfin ', road_name, pkini, pkfin, 'MminTramo, MmaxTramo ', MminTramo, MmaxTramo)
        return (gLine, MminTramo, MmaxTramo, attrFinales, multiline)

    def desplazaEje(self, line1, disteje):
        # Desplaza una línea paralela a una distancia especificada, preservando los valores M.

        # :param line1: ogr.Geometry (línea original, tipo x,y,M)
        # :param disteje: float (distancia para desplazar la línea)
        # :return: ogr.Geometry (línea desplazada)

        # Crea una nueva línea vacía del mismo tipo que la original
        displaced_line = ogr.Geometry(ogr.wkbLineStringM)

        # Obtener la cantidad de puntos en la línea original
        num_points = line1.GetPointCount()

        # Lista para almacenar los nuevos puntos desplazados
        displaced_points = []

        # Itera sobre los puntos de la línea original
        for i in range(num_points - 1):
            # Punto actual y siguiente
            p1 = line1.GetPoint(i)
            p2 = line1.GetPoint(i + 1)

            # Obtener la medida M si está presente (asumimos que el formato es x, y, z, m)
            m1 = line1.GetM(i)
            m2 = line1.GetM(i + 1)

            # Calcula el ángulo de la línea
            angle = math.atan2(p2[1] - p1[1], p2[0] - p1[0])

            # Calcula el ángulo perpendicular
            perp_angle = angle - math.pi / 2

            # Desplaza los puntos perpendicularmente
            dx = disteje * math.cos(perp_angle)
            dy = disteje * math.sin(perp_angle)

            displaced_p1 = (p1[0] + dx, p1[1] + dy, p1[2], m1)
            displaced_p2 = (p2[0] + dx, p2[1] + dy, p2[2], m2)

            if i == 0:
                displaced_points.append(displaced_p1)
            elif i < (num_points - 2):
                displaced_points.append(displaced_p2)



        # Añade el último punto utilizando el ángulo del último segmento
        # last_p1 = line1.GetPointM(num_points - 2)
        # last_p2 = line1.GetPointM(num_points - 1)
        # last_angle = math.atan2(last_p2[1] - last_p1[1], last_p2[0] - last_p1[0])
        # last_perp_angle = last_angle - math.pi / 2
        # last_dx = disteje * math.cos(last_perp_angle)
        # last_dy = disteje * math.sin(last_perp_angle)
        # displaced_last_p = (last_p2[0] + last_dx, last_p2[1] + last_dy, last_p2[2])
        # displaced_points[-1] = displaced_last_p

        # Crea la nueva geometría de línea con los puntos desplazados
        for point in displaced_points:
            displaced_line.AddPoint(point[0], point[1], point[2])

        return displaced_line

    def pointMsegment(self, pk, point, pointSIG):
        if point[2]<=pointSIG[2]:
            m_anterior = point[2]
            m_siguiente = pointSIG[2]
            punto_anterior = ogr.Geometry(ogr.wkbPoint)
            punto_anterior.AddPoint(point[0], point[1])
            punto_siguiente = ogr.Geometry(ogr.wkbPoint)
            punto_siguiente.AddPoint(pointSIG[0], pointSIG[1])

        else:
            m_anterior = pointSIG[2]
            m_siguiente = point[2]
            punto_anterior = ogr.Geometry(ogr.wkbPoint)
            punto_anterior.AddPoint(pointSIG[0], pointSIG[1])
            punto_siguiente = ogr.Geometry(ogr.wkbPoint)
            punto_siguiente.AddPoint(point[0], point[1])

        r = (pk - m_anterior) / (m_siguiente - m_anterior)
        modulo = r * (punto_siguiente.Distance(punto_anterior))
        alfa = math.atan2((punto_siguiente.GetY() - punto_anterior.GetY() ) , (punto_siguiente.GetX()  - punto_anterior.GetX()))

        diff = pk - m_anterior

        x = punto_anterior.GetX() + modulo * math.cos(alfa)
        y = punto_anterior.GetY() + modulo * math.sin(alfa)

        # CALCULO DEL ACIMUT
        pointANT = QgsPoint(punto_anterior.GetX(),punto_anterior.GetY())
        pointPOS = QgsPoint(punto_siguiente.GetX(),punto_siguiente.GetY())
        res1 = self.calcACIMUT(pointANT,pointPOS)
        acim= res1[1]

        print (' pk, point[2], pointSIG[2]',pk, point[2], pointSIG[2], 'r, modulo', r, modulo )

        return (x,y,acim)

    def createVectorLayer(self,uri,name,dest='memory'):
        # createVectorLayer(self,uri,name,dest='memory')
        #   Crea una capa vectorial de careteras en memoria añadiendoles campos
        #           'carretera', 'pk_ini', 'pk_fin', 'acimut', 'distancia'
        #   Devuelve la capa vectorial
        #   return vl

        vl = QgsVectorLayer(uri, name, dest)
        pr = vl.dataProvider()


        # Enter editing mode
        vl.startEditing()

        # add fields
        pr.addAttributes( [ QgsField("carretera", QVariant.String),
                        QgsField("pk_ini", QVariant.Double),
                        QgsField("pk_iniDist", QVariant.Double),
                        QgsField("pk_fin", QVariant.Double),
                        QgsField("pk_finDist", QVariant.Double),
                        QgsField("acimut", QVariant.Double),
                        QgsField("distancia", QVariant.Double)
                        ] )
        # Commit changes
        vl.commitChanges()
        return vl

    def cargaGPKGjson(self, layerJSON, fichGPKG, capaGPKG, nomCAPA, estiloCAPA, cargaVISTA=True):
        # Convierte una capa GeoJSON en GeoPackage, la carga en QGIS y le aplica un estilo.

        # :param layerJSON: QgsVectorLayer de origen (tipo GeoJSON)
        # :param fichGPKG: Ruta del archivo GeoPackage a generar
        # :param capaGPKG: Nombre de la capa dentro del GeoPackage
        # :param nomCAPA: Nombre de la capa en la vista de QGIS
        # :param estiloCAPA: Ruta al archivo .qml de estilo
        # :param cargaVISTA: Booleano para decidir si se carga en el mapa

        # Verificamos que layerJSON sea una capa válida
        if not layerJSON.isValid():
            print(f"La capa {layerJSON.name()} no es válida")
            return

        # Guardamos la capa GeoJSON como GeoPackage
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "GPKG"
        options.layerName = capaGPKG  # Nombre de la capa dentro del GeoPackage
        error = QgsVectorFileWriter.writeAsVectorFormatV2(
            layerJSON, fichGPKG, QgsCoordinateTransformContext(), options
        )

        if error[0] != QgsVectorFileWriter.NoError:
            print(f"Error al guardar la capa en el GeoPackage: {error[1]}")
            return

        # Cargamos la capa GPKG en QGIS si se indica
        if cargaVISTA:
            uri = f"{fichGPKG}|layername={capaGPKG}"
            new_layer = QgsVectorLayer(uri, nomCAPA, "ogr")
            if not new_layer.isValid():
                print(f"Error al cargar la capa desde el GPKG: {uri}")
                return

            # Aplicar el estilo (si se ha especificado)
            if estiloCAPA:
                new_layer.loadNamedStyle(estiloCAPA)
                new_layer.triggerRepaint()

            # Añadir la capa al proyecto, desactivando su adición automática a la TOC
            QgsProject.instance().addMapLayer(new_layer, False)  # 'False' evita que la capa se añada automáticamente al TOC

            # Obtener la raíz del proyecto
            root = QgsProject.instance().layerTreeRoot()

            # Comprobar si existe el grupo en el que queremos insertar la capa
            group = root.findGroup(capaGPKG)  # Busca el grupo donde quieres insertar la capa

            if group:
                # Si hay un grupo, insertar la capa en la primera posición dentro de ese grupo
                group.insertChildNode(0, QgsLayerTreeLayer(new_layer))
            else:
                # Si no hay grupo, insertar la capa en la primera posición de la raíz
                root.insertChildNode(0, QgsLayerTreeLayer(new_layer))

            # Contraer la leyenda de la capa
            layer_node = root.findLayer(new_layer.id())  # Encuentra el nodo de la capa en el árbol
            if layer_node:
                layer_node.setExpanded(False)  # Contrae la leyenda de la capa

    def createGeometryOGR(self,feature,pk_ini,pk_fin,return_M = "false"):

        #print "Creando geometria desde OGR: " + str(pk_ini) + " hasta: " + str (pk_fin)

        n = 0
        line = ogr.Geometry(ogr.wkbLineStringM)
        geometry = feature["geometry"]
        paths = geometry["paths"]
        points = []
        for path in paths:
            for point in path:
                if(return_M == "true"):
                    if(point[2] == None):
                        #print "Coordenada sin M, la saltamos...la eme"
                        n +=1
                        line.AddPoint(point[0],point[1])
                        continue
                    line.AddPointM(point[0],point[1],point[2])
                else:
                    line.AddPoint(point[0],point[1])
        if n > 0:
            QgsMessageLog.logMessage( "Feature con " + str(n) + " coordenadas sin M",self.nombre_plugin)
            return [line,"Feature con " + str(n) + " coordenadas sin M"]
        return [line,None]

    def createGeometryQGS(self,feature,pk_ini,pk_fin):

        #print "Creando geometria QGS desde : " + str(pk_ini) + " hasta: " + str (pk_fin)

        geometry = feature["geometry"]
        paths = geometry["paths"]
        points = []
        for path in paths:
            for point in path:
                gPnt =QgsPoint(point[0],point[1])
                points.append(gPnt)
        line  = QgsGeometry.fromPolyline(points)

        return line

    def getCoordsFeaturePK(self,feat,pk):
        ################################################
        ######   SEGURO PARA EL CÁLCULO DE PK=0   ######
        ################################################
        # Sumamos 0.01 m en caso de pk = 0
        if pk == 0.0:
            pk = pk+0.00001
        ################################################
        ################################################

        n = 0
        acim = 360
        mensaje_final = ""
        line = ogr.Geometry(ogr.wkbLineStringM)
        #print "feature"
        geometry = feat["geometry"] # La geometría del elemento detectado
        paths = geometry["paths"]   # Las diferentes partes de la geometría del elemento detectado
        attr =  feat["attributes"]  # Los atributos del elemento detectado
        # print attr
        mat_plan = attr['Matricula']
        for path in paths:
            for point in path:
                if(point[2] == None):
                    n += 1
                    continue
                line.AddPointM(point[0],point[1],point[2])
        creciente = True
        if line.GetM(1) < line.GetM(0):
            creciente = False

        m_anterior = 0
        m_siguiente = 0
        if creciente == True:
            # print mat_plan +" - (partes:"+ str(len(paths))+") Creciente"
            for i in range(line.GetPointCount()):
                current_m = line.GetM(i)
                # if (pk == current_m):
                    # target_point_coords = line.GetPoint(i);
                    # point = ogr.Geometry(ogr.wkbPoint)
                    # point.AddPoint(target_point_coords[0], target_point_coords[1])
                    # return [target_point_coords[0], target_point_coords[1]]
                    # #self.zoomToGeometry(iface,point)
                    # return None
                if(current_m >= pk):
                    punto_anterior = ogr.Geometry(ogr.wkbPoint)
                    punto_anterior.AddPoint(line.GetPoint(i-1)[0], line.GetPoint(i-1)[1])

                    punto_siguiente = ogr.Geometry(ogr.wkbPoint)
                    punto_siguiente.AddPoint(line.GetPoint(i)[0], line.GetPoint(i)[1])

                    m_anterior = line.GetM(i-1)
                    m_siguiente = line.GetM(i)

                    break
        else:
            # print mat_plan +" - (partes:"+ str(len(paths))+") Decreciente"
            for i in range(line.GetPointCount()):
                current_m = line.GetM(i)
                # if (pk == current_m):
                    # target_point_coords = line.GetPoint(i);
                    # target_point_coords1 = line.GetPoint(i+1);
                    # point = ogr.Geometry(ogr.wkbPoint)
                    # point.AddPoint(target_point_coords[0], target_point_coords[1])
                    # return [target_point_coords[0], target_point_coords[1]]
                if(current_m <= pk):
                    punto_anterior = ogr.Geometry(ogr.wkbPoint)
                    punto_anterior.AddPoint(line.GetPoint(i)[0], line.GetPoint(i)[1])

                    punto_siguiente = ogr.Geometry(ogr.wkbPoint)
                    punto_siguiente.AddPoint(line.GetPoint(i-1)[0], line.GetPoint(i-1)[1])

                    m_anterior = line.GetM(i)
                    m_siguiente = line.GetM(i-1)
                    break

        if m_siguiente != m_anterior:
            r = (pk - m_anterior) / (m_siguiente - m_anterior)
            modulo = r * (punto_siguiente.Distance(punto_anterior))
            #m = (punto_siguiente[1] - punto_anterior[1]) / (punto_siguiente[0] - punto_anterior [0])
            alfa = math.atan2((punto_siguiente.GetY() - punto_anterior.GetY() ) , (punto_siguiente.GetX()  - punto_anterior.GetX()))

            diff = pk - m_anterior

            x = punto_anterior.GetX() + modulo * math.cos(alfa)
            y = punto_anterior.GetY() + modulo * math.sin(alfa)

            # CALCULO DEL ACIMUT
            pointANT = QgsPoint(punto_anterior.GetX(),punto_anterior.GetY())
            pointPOS = QgsPoint(punto_siguiente.GetX(),punto_siguiente.GetY())
            res1 = self.calcACIMUT(pointANT,pointPOS)
            acim= res1[1]
            # if acim < 0:
                # acim += 360

        else:
            QgsMessageLog.logMessage("Feature con " + str(n) +" Mal calibrada",self.nombre_plugin)
            # print mat_plan +" - (partes:"+ str(len(paths))+") Mal calibrada"
            return None

        if n > 0:
            QgsMessageLog.logMessage(mat_plan + str(len(paths))+"Feature con " + str(n) + " coordenadas sin M",self.nombre_plugin)
            # print mat_plan +" - (partes:"+ str(len(paths))+"Feature con " + str(n) + ") coordenadas sin M"


        # CONTROL DE COORDENADAS EN ZONA CLM
        Xmin =  291000
        Ymin = 4205000
        Xmax =  680000
        Ymax = 4576000
        if (x < Xmin or x > Xmax or y < Ymin or y > Ymax):
            return None

        # print mat_plan, pk, x, y, acim
        return [x,y,acim]


    """
    ##################################################################################################################
    ##################################################################################################################
    ###################                                                                            ###################
    ###################               RUTINAS DE GESTION DE MUNICIPIOS Y POBLACIONES               ###################
    ###################                ( CONTRA APIREST DE GEODATABASE CARRETERAS )                ###################
    ###################                                                                            ###################
    ##################################################################################################################
    ##################################################################################################################
    """

    def buscaTTMMpoligono(self, listPolig):
        # Obtiene datos de los TTMM que intersectan con un polígono.
        # ENTRADA:
        #   - listPolig: lISTA DE GEOMETRÍAS DE TODOS LOS ELEMENTOS A BUSCAR
        # SALIDA:
        #   - listaProv, [Provincia,ProvNombre,Provcodine]
        #       Provincia  = u'%s (%s)'%(Nombre, codine[0:2])
        #       ProvNombre = Nombre
        #       Provcodine = codine
        #   - listaMuni, [Municipio,MuniNombre,Municodine]
        #       Municipio = u'%s (%s)'%(Nombre, codine)
        #       MuniNombre = Nombre
        #       Municodine = codine

        srs = crsVal
        listaProv = []
        listaMuni = []
        error = True
        for polig in listPolig:     # INTENTAMOS DETECTAR LOS DATOS EN https://geoservicios.castillalamancha.es
            perimetroGeom = polig.asJson(3)
            perimetroGeomdecoded = json.loads(perimetroGeom)

            perimetroGeomFin = {}
            for entity in perimetroGeomdecoded["coordinates"]:
                perimetroGeomFin['rings'] = entity
            # print(perimetroGeomFin)

            url = current_configuration.general["rest_municipios"]
            # url = u'https://geoservicios.castillalamancha.es/arcgis/rest/services/WFS/Plan_Carreteras_Poblaciones_Municipios_WFS/MapServer/1/query?'

            params = {
                    'geometry': perimetroGeomFin,
                    'geometryType':'esriGeometryPolygon',
                    'inSR': srs,
                    'spatialRel':'esriSpatialRelIntersects',
                    'outFields':'*',
                    'returnGeometry':'false',
                    'f':'pjson'
                    }

            data = urllib.parse.urlencode(params)
            print (url+data)

            ###  LINEA DE DATOS DE TEST DE ERROR  ###
            # data = 'geometry=kk%7B%27rings%27%3A+%5B%5B%5B624929.74%2C+4341991.661%5D%2C+%5B625269.156%2C+4342027.181%5D%2C+%5B625249.422%2C+4341851.553%5D%2C+%5B625073.794%2C+4341776.566%5D%2C+%5B624911.98%2C+4341845.633%5D%2C+%5B624910.006%2C+4341849.58%5D%2C+%5B624929.74%2C+4341991.661%5D%5D%5D%7D&geometryType=esriGeometryPolygon&inSR=25830&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=false&f=pjson'
            try:
                response = requests.get(url+data, timeout=TIMEOUT_SEGUNDOS)
                response.raise_for_status()  # Lanza excepción si hay error HTTP (4xx, 5xx)
                response = response.json()  # Esto ya es el JSON parseado
            except urllib.error.URLError as e:
                error = True
                textErr = "Problemas de conexión con \n" + url
                result = self.PrintException()
                return "error", textErr
            except TimeoutError:
                error = True
                textErr = "Timeout: El servidor de municipios no responde"
                return "error", textErr
            # try:
                # response = json.load(urllib.request.urlopen(url+data))
                # # print (response)
            # except:
                # error = True
                # textErr = "Problemas de conexión con \n" + url
                # result = self.PrintException()
                # # print (result)
                # return "error", textErr

            # if "error" in response:
            if "error" in response:
                error = True
            else:
                error = False

                features =  response["features"]
                attr = None
                # listAttr = []
                Municipio = 'NADA'
                Provincia = 'NADA'
                MuniNombre ='NADA'
                Municodine ='NADA'
                ProvNombre ='NADA'
                Provcodine ='NADA'
                for feature in features:
                    attr =  feature["attributes"]
                    codine = attr['codine']
                    Nombre = attr['Nombre']
                    if codine[2:5] == '000':
                        Provincia = u'%s (%s)'%(Nombre, codine[0:2])
                        ProvNombre = Nombre
                        Provcodine = codine
                        if [Provincia,ProvNombre,Provcodine] not in listaProv:
                            listaProv.append ([Provincia,ProvNombre,Provcodine])
                    else:
                        Municipio = u'%s (%s)'%(Nombre, codine)
                        MuniNombre = Nombre
                        Municodine = codine
                        if [Municipio,MuniNombre,Municodine] not in listaMuni:
                            listaMuni.append ([Municipio,MuniNombre,Municodine])

        if error == True:
            QApplication.restoreOverrideCursor()
            # result = self.PrintException()
            textErr = json.dumps(response["error"])
            # self.showMessageERR(textErr,text2="",tittle=self.nombre_plugin+" - Error de código",)
            return "error", textErr

        return listaProv, listaMuni

    def getJCCMMuniProv(self, point, iface, pintar):
        # Obtiene la provincioa y Municipio de un punto pinchado a partir del servicio D.G.Carreteras JCCM
        #       url = u'https://geoservicios.castillalamancha.es/arcgis/rest/services/WFS/Plan_Carreteras_Poblaciones_Municipios_WFS/MapServer/1/query?'
        #   https://geoservicios.castillalamancha.es/arcgis/rest/services/WFS/Plan_Carreteras_Poblaciones_Municipios_WFS/MapServer/1/query?
            # where=&
            # text=&
            # objectIds=&
            # time=&
            # geometry=x%3D589804.912%2Cy%3D4293820.724&
            # geometryType=esriGeometryPoint&
            # inSR=&
            # spatialRel=esriSpatialRelWithin&relationParam=&outFields=*&returnGeometry=false&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&returnDistinctValues=false&resultOffset=&resultRecordCount=&queryByDistance=&returnExtentsOnly=false&datumTransformation=&parameterValues=&rangeValues=&f=pjson
            #   where=1%3D1&text=&objectIds=&time=&geometry=x%3D589804.912%2Cy%3D4293820.724&geometryType=esriGeometryPoint&inSR=&spatialRel=esriSpatialRelWithin&relationParam=&outFields=*&returnGeometry=false&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&returnDistinctValues=false&resultOffset=&resultRecordCount=&queryByDistance=&returnExtentsOnly=false&datumTransformation=&parameterValues=&rangeValues=&f=pjson

        FUENTE = f'WMS: geoservicios D.G.Ctras. JCCM'

        Xpoint=point[0]
        Ypoint=point[1]
        srs = crsVal

        url = current_configuration.general["rest_municipios"]
        # url = u'https://geoservicios.castillalamancha.es/arcgis/rest/services/WFS/Plan_Carreteras_Poblaciones_Municipios_WFS/MapServer/1/query?'

        params = {
                'geometry':u'{"x" : %s, "y" : %s}'%("{:.3f}".format(Xpoint),"{:.3f}".format(Ypoint)),
                'geometryType':'esriGeometryPoint',
                'inSR':srs,
                # 'spatialRel':'esriSpatialRelRelation',
                'spatialRel':'esriSpatialRelWithin',
                'outFields':'*',
                'returnGeometry':'false',
                'f':'pjson'
                }

        data = urllib.parse.urlencode(params)
        try:
            response = requests.get(url+data, timeout=TIMEOUT_SEGUNDOS)
            response.raise_for_status()  # Lanza excepción si hay error HTTP (4xx, 5xx)
            response = response.json()  # Esto ya es el JSON parseado
        except urllib.error.URLError as e:
            QApplication.restoreOverrideCursor()
            result = self.PrintException()
            print(result)
            return 's/d', 's/d', 's/d', 's/d', 's/d', 's/d', FUENTE
        except TimeoutError:
            QApplication.restoreOverrideCursor()
            print("Timeout: El servidor de municipios no responde")
            return 's/d', 's/d', 's/d', 's/d', 's/d', 's/d', 'no data', FUENTE

        # try:
            # response = json.load(urllib.request.urlopen(url+data))
            # # print (response)
        # except:
            # QApplication.restoreOverrideCursor()
            # result = self.PrintException()
            # print (result)
            # return 's/d', 's/d', 's/d', 's/d', 's/d', 's/d', FUENTE

        try:
            features =  response["features"]
        except:
            QApplication.restoreOverrideCursor()
            a = response["error"]
            result = self.PrintException()
            print (result)
            return 's/d', 's/d', 's/d', 's/d', 's/d', 's/d', 'no data', FUENTE

        attr = None
        # listAttr = []
        Municipio = 'NADA'
        Provincia = 'NADA'
        MuniNombre ='NADA'
        Municodine ='NADA'
        ProvNombre ='NADA'
        Provcodine ='NADA'
        for feature in features:
            attr =  feature["attributes"]
            codine = attr['codine']
            Nombre = attr['Nombre']
            if codine[2:5] == '000':
                Provincia = u'%s (%s)'%(Nombre, codine[0:2])
                ProvNombre = Nombre
                Provcodine = codine
            else:
                Municipio = u'%s (%s)'%(Nombre, codine)
                MuniNombre = Nombre
                Municodine = codine

        return Municipio, Provincia, MuniNombre, Municodine, ProvNombre, Provcodine, 'no data', FUENTE

    def getJCCMMuniProv_GPKG(self, point, iface, pintar, ruta_geopackage, nombre_capa):
        #  Rutina de calculo alternativo sobre fichero GPKG. Obtiene la provincioa y Municipio de un punto pinchado

        FUENTE = f'GPKG: {ruta_geopackage}'

        clicked_QgsPoint = QgsPointXY(point[0],point[1])
        qgs_point_geometry = QgsGeometry.fromPointXY(clicked_QgsPoint)

        # Abre el GeoPackage
        geopackage = ogr.Open(ruta_geopackage)

        if geopackage is None:
            print("Error al abrir el GeoPackage")
        else:
            # Obtén la capa 'GEO_Municipios_Zona'
            layer = QgsVectorLayer('{}|layername={}'.format(ruta_geopackage, nombre_capa), nombre_capa, 'ogr')

        # Construye una expresión de consulta espacial
        expression = 'intersects($geometry, geomFromWKT(\'POINT({} {})\'))'.format(point[0],point[1])

        # Selecciona las entidades que cumplen con la expresión
        layer.selectByExpression(expression, QgsVectorLayer.SetSelection)

        # Obtén las entidades seleccionadas
        selected_features = [feature for feature in layer.getSelectedFeatures()]

        # Limpia la selección
        layer.removeSelection()


        attr = None
        # listAttr = []
        Municipio  = None
        Provincia  = None
        MuniNombre = None
        Municodine = None
        ProvNombre = None
        Provcodine = None

        for feature in selected_features:

            codine = feature.attribute('codine')
            nombre = feature.attribute('Nombre')

            if codine[2:5] == '000':
                Provincia = u'%s (%s)'%(nombre, codine[0:2])
                ProvNombre = nombre
                Provcodine = codine
            else:
                Municipio = u'%s (%s)'%(nombre, codine)
                MuniNombre = nombre
                Municodine = codine

        return Municipio, Provincia, MuniNombre, Municodine, ProvNombre, Provcodine, 'no data', FUENTE


    """
    ##################################################################################################################
    ##################################################################################################################
    ###################                                                                            ###################
    ###################                 RUTINAS DE BÚSQUEDA EN IGN Y CARTOCIUDAD                   ###################
    ###################                                                                            ###################
    ##################################################################################################################
    ##################################################################################################################
    """

    def getCARTOCMuniProv(self, point, iface, pintar='NO'):
        # Petición GET:
        # http://www.cartociudad.es/geocoder/api/geocoder/reverseGeocode?lon=-0.3719472885131836&lat=39.48668753230887
        # http://www.cartociudad.es/geocoder/api/geocoder/reverseGeocode?lon=-1.5841380614657519&lat=38.79729901329633
        # https://www.cartociudad.es/geocoder/api/geocoder/reverseGeocode?lon=-1.371939&lat=41.487733

        # Respuesta:
        # {"id":"462500009634","province":"Valencia/València","muni":"Valencia","type":"portal","address":"FRAY PEDRO
        # VIVES","postalCode":"46009","poblacion":"Valencia","geom":"POINT (-0.3720243982087104
        # 39.486756297555154)","tip_via":"CALLE","lat":39.486756297555154,"lng":-
        # 0.3720243982087104,"portalNumber":35,"stateMsg":"Resultado exacto de la
        # búsqueda","state":1,"priority":0,"countryCode":"011","refCatastral":null}


        # Obtiene municipio y provincia de un punto usando el servicio CartoCiudad
        # Args:
            # point: Punto en coordenadas (lon, lat) en EPSG:4326
            # iface: Interfaz de QGIS
            # pintar: No utilizado, mantenido por compatibilidad

        # Returns:
            # tuple: (Municipio, Provincia, Nombre_Municipio, Codigo_Municipio, Nombre_Provincia, Codigo_Provincia)

        FUENTE = 'Cartociudad'

        # Obtener el canvas actual
        self.canvas = iface.mapCanvas()

        # Crear y activar la herramienta
        # point_tool = PointTool(canvas)
        # canvas.setMapTool(point_tool)

        # Obtener coordenadas del punto pinchado
        # point = self.toMapCoordinates(event.pos())

        # Transformar coordenadas a EPSG:4326 si es necesario
        canvas_crs = self.canvas.mapSettings().destinationCrs()
        if canvas_crs.authid() != 'EPSG:4326':
            transform = QgsCoordinateTransform(canvas_crs, QgsCoordinateReferenceSystem('EPSG:4326'), QgsProject.instance())
            point = transform.transform(point)

        lon = point.x()
        lat = point.y()

        # Construir URL de la API
        url = f"https://www.cartociudad.es/geocoder/api/geocoder/reverseGeocode?lon={lon}&lat={lat}"

        try:
            # Hacer la petición a la API con requests
            response = requests.get(url, timeout=TIMEOUT_SEGUNDOS)
            response.raise_for_status()  # Lanza excepción para códigos HTTP 4xx/5xx

            # Parsear el JSON
            data = response.json()

            # Extraer los datos que nos interesan
            ProvNombre = data.get('province', 'No encontrado')
            Provcodine = data.get('provinceCode', 'No encontrado')
            MuniNombre = data.get('muni', 'No encontrado')
            Municodine = data.get('muniCode', 'No encontrado')

            Municipio = f'{MuniNombre} ({Municodine})'
            Provincia = f'{ProvNombre} ({Provcodine})'

            # # Mostrar resultados (comentado como en tu código original)
            # result = f"Provincia: {ProvNombre}\nCódigo de provincia: {Provcodine}\nMunicipio: {MuniNombre}\nCódigo de municipio: {Municodine}\nCoordenadas (lon, lat): {lon:.6f}, {lat:.6f}"
            # QMessageBox.information(None, "Resultados", result)
            # print(result)

            return Municipio, Provincia, MuniNombre, Municodine, ProvNombre, Provcodine, data, FUENTE

        except requests.exceptions.Timeout:
            print("Timeout: El servidor de Cartociudad no responde")
            return 's/d', 's/d', 's/d', 's/d', 's/d', 's/d', 'no data', FUENTE

        except requests.exceptions.ConnectionError as e:
            print(f"Error de conexión: No se pudo obtener la información: {str(e)}")
            return 's/d', 's/d', 's/d', 's/d', 's/d', 's/d', 'no data', FUENTE

        except requests.exceptions.HTTPError as e:
            print(f"Error HTTP {response.status_code}: {str(e)}")
            return 's/d', 's/d', 's/d', 's/d', 's/d', 's/d', 'no data', FUENTE

        except requests.exceptions.RequestException as e:
            print(f"No se pudo obtener la información: {str(e)}")
            return 's/d', 's/d', 's/d', 's/d', 's/d', 's/d', 'no data', FUENTE

        except Exception as e:
            # Captura cualquier otro error inesperado
            print(f"No se pudo obtener la información: {str(e)}")
            return 's/d', 's/d', 's/d', 's/d', 's/d', 's/d', 'no data', FUENTE

        # try:
            # with urllib.request.urlopen(url, timeout=TIMEOUT_SEGUNDOS) as response:
                # data = json.loads(response.read().decode())

                # # Extraer los datos que nos interesan
                # ProvNombre = data.get('province', 'No encontrado')
                # Provcodine = data.get('provinceCode', 'No encontrado')
                # MuniNombre = data.get('muni', 'No encontrado')
                # Municodine = data.get('muniCode', 'No encontrado')

                # Municipio = f'{MuniNombre} ({Municodine})'
                # Provincia = f'{ProvNombre} ({Provcodine})'

                # # # Mostrar resultados
                # # result = f"Provincia: {ProvNombre}
                # # Código de provincia: {Provcodine}
                # # Municipio: {MuniNombre}
                # # Código de municipio: {Municodine}
                # # Coordenadas (lon, lat): {lon:.6f}, {lat:.6f}"
                # # result = f"Provincia: {ProvNombre}\nCódigo de provincia: {Provcodine}\nMunicipio: {MuniNombre}\nCódigo de municipio: {Municodine}\nCoordenadas (lon, lat): {lon:.6f}, {lat:.6f}"

                # # QMessageBox.information(None, "Resultados", result)
                # # print (result)

                # return Municipio, Provincia, MuniNombre, Municodine, ProvNombre, Provcodine, data, FUENTE

        # except urllib.error.URLError as e:
            # print(f"No se pudo obtener la información: {str(e)}")
            # return 's/d', 's/d', 's/d', 's/d', 's/d', 's/d', 'no data', FUENTE
        # except TimeoutError:
            # print("Timeout: El servidor de Cartociudad no responde")
            # return 's/d', 's/d', 's/d', 's/d', 's/d', 's/d', 'no data', FUENTE
        # # try:
            # # # Hacer la petición a la API
            # # with urllib.request.urlopen(url) as response:
                # # data = json.loads(response.read().decode())


        # except Exception as e:
            # # QMessageBox.critical(None, "Error", f"No se pudo obtener la información: {str(e)}")
            # print (f"No se pudo obtener la información: {str(e)}")
            # return 's/d', 's/d', 's/d', 's/d', 's/d', 's/d', 'no data', FUENTE

    def getIGNunidAdminMuniProv(self, point, iface, pintar='NO'):
        FUENTE = 'Serv. wms: IGN Unidades administrativas'

        urlWMSIGNpromun =   'https://www.ign.es/wms-inspire/unidades-administrativas?'
        urlWMSIGNmunLyr=    'AU.AdministrativeUnit'
        urlWMSIGNmunValorNom=  '0_1:nameunit'
        urlWMSIGNmunValorCod=  '0_1:nationalcode'
        urlWMSIGNproLyr=    'AU.AdministrativeUnit/0_0'
        urlWMSIGNproValorNom=  '0_0:nameunit'
        urlWMSIGNproValorCod=  '0_0:nationalcode'

        tipo = 'text/xml'

        resultmun=self.WMSgetFeatureInfo(point,iface, pintar,
                urlWMSIGNpromun, tipo, urlWMSIGNmunLyr)
        resultpro=self.WMSgetFeatureInfo(point,iface, pintar,
                urlWMSIGNpromun, tipo, urlWMSIGNproLyr)

        if resultmun[0] == 'Error':
            Municipio, MuniNombre, Municodine =  's/d', 's/d', 's/d'
        else:
            urlRes=resultmun[0]
            print (urlRes)
            xml_txt=resultmun[1]
            print (xml_txt)

            try:
                xml_dom = parseString(xml_txt)
                MuniNombre = xml_dom.getElementsByTagName(urlWMSIGNmunValorNom)[0].toxml()
                Municodine = xml_dom.getElementsByTagName(urlWMSIGNmunValorCod)[0].toxml()
                Municipio = f'{MuniNombre} ({Municodine})'
            except:
                resultmun = self.PrintException()
                print (resultmun)
                Municipio, MuniNombre, Municodine =  's/d', 's/d', 's/d'


        if resultpro[0] == 'Error':
            Provincia, ProvNombre, Provcodine =  's/d', 's/d', 's/d'
        else:
            urlRes=resultpro[0]
            print (urlRes)
            xml_txt=resultpro[1]
            print (xml_txt)

            try:
                xml_dom = parseString(xml_txt)
                ProvNombre = xml_dom.getElementsByTagName(urlWMSIGNproValorNom)[0].toxml()
                Provcodine = xml_dom.getElementsByTagName(urlWMSIGNproValorCod)[0].toxml()
                Provincia = f'{ProvNombre} ({Provcodine})'
            except:
                resultpro = self.PrintException()
                print (resultpro)
                Provincia, ProvNombre, Provcodine =  's/d', 's/d', 's/d'


        return Municipio, Provincia, MuniNombre, Municodine, ProvNombre, Provcodine, 'no data', FUENTE

        pass


    """
    ##################################################################################################################
    ##################################################################################################################
    ###################                                                                            ###################
    ###################                       RUTINAS CALCULOS SOBRE MDT                           ###################
    ###################                                                                            ###################
    ##################################################################################################################
    ##################################################################################################################
    """

    def Zmdt(self, point,iface,pintar):
        # Obtiene la Z del modelo MDT 5m. del IGN, a partir del servicio WMS
        #       url = u'http://www.ign.es/wms-inspire/mdt?'
        # Se obtiene el dato por medio de 'request=GetFeatureInfo'

        # urlWMSmdt     = u'http://www.ign.es/wms-inspire/mdt?'         ### ANTIGUA ###
        # urlWMSmdt     = u'https://servicios.idee.es/wms-inspire/mdt?'
        # urlWMSmdtLayer= 'EL.GridCoverage' - desde 2022 esta no vale
        # urlWMSmdtLayer= 'EL.ElevationGridCoverage'
        # urlWMSmdtValor= 'mdt:GRAY_INDEX'

        urlWMSmdt = self.qs.value(f"{self.nombre_plugin}/GENERAL/urlWMSmdt")
        # print (urlWMSmdt)
        if urlWMSmdt is None:
            urlWMSmdt = self.conf.general["urlWMSmdt"]
            self.qs.setValue(f"{self.nombre_plugin}/GENERAL/urlWMSmdt", urlWMSmdt)

        urlWMSmdtLayer = self.qs.value(f"{self.nombre_plugin}/GENERAL/urlWMSmdtLayer")
        if urlWMSmdtLayer is None:
            urlWMSmdtLayer = self.conf.general["urlWMSmdtLayer"]
            self.qs.setValue(f"{self.nombre_plugin}/GENERAL/urlWMSmdtLayer", urlWMSmdtLayer)

        urlWMSmdtValor = self.qs.value(f"{self.nombre_plugin}/GENERAL/urlWMSmdtValor")
        if urlWMSmdtValor is None:
            urlWMSmdtValor = self.conf.general["urlWMSmdtValor"]
            self.qs.setValue(f"{self.nombre_plugin}/GENERAL/urlWMSmdtValor", urlWMSmdtValor)

        tipo = 'text/xml'
        result=self.WMSgetFeatureInfo(point,iface, pintar, urlWMSmdt, tipo, urlWMSmdtLayer)
        # print (result)
        if result[0] == 'Error':
            return ('Error')
        else:
            urlRes=result[0]
            xml_txt=result[1]

            try:
                xml_dom = parseString(xml_txt)
                Zmdt = xml_dom.getElementsByTagName(urlWMSmdtValor)[0].toxml()
                Zmdt = float(Zmdt.replace('<'+urlWMSmdtValor+'>','').replace('</'+urlWMSmdtValor+'>',''))
            except:
                result = self.PrintException()
                print (result)
                return ('Error')

        return Zmdt

    def WMSgetFeatureInfo(self, point,iface, pintar, url, tipo, layerQueryable):
        # Obtiene un valor en un punto generico contra un getFeatureInfo, a partir del servicio WMS
        # Se obtiene el dato por medio de 'request=GetFeatureInfo'

        Xpoint=point[0]
        Ypoint=point[1]
        srs = crsVal

        params = {
                'service':'wms',
                'version':'1.1.1',
                'request':'GetFeatureInfo',
                'query_layers':layerQueryable,
                'srs':'EPSG:'+ str(srs),
                'format':tipo,
                'layers':layerQueryable,
                'bbox':str(Xpoint)+','+str(Ypoint)+','+str(Xpoint+1)+','+str(Ypoint+1),
                'width':'1',
                'height':'1',
                'info_format':tipo,
                'feature_count':'50',
                'x':'1',
                'y':'1',
                # 'exceptions':'application%2Fvnd.ogc.se_xml'
                }

        data = urllib.parse.urlencode(params)
        # print (url+data)

        try:
            response = requests.get(url+data, timeout=TIMEOUT_SEGUNDOS)
            response.raise_for_status()  # Lanza excepción si hay error HTTP (4xx, 5xx)
            response = response.json()  # Esto ya es el JSON parseado
        except urllib.error.URLError as e:
            QApplication.restoreOverrideCursor()
            result = self.PrintException()
            print(result, self.nombre_plugin+" - Error de consulta web COTA EN IGN")
            return ('Error', 'Error de consulta web COTA EN IGN')
        except TimeoutError:
            QApplication.restoreOverrideCursor()
            print("Timeout: El servidor WMS no responde")
            return ('Error', 'Timeout: El servidor WMS no responde')
        # try:
            # req = urllib.request.urlopen(url+data)
        # except:
            # QApplication.restoreOverrideCursor()
            # result = self.PrintException()
            # print (result, self.nombre_plugin+" - Error de consulta web COTA EN IGN")
            # return ('Error', 'Error de consulta web COTA EN IGN')

        xml_txt =  response.read()
        # xml_txt =  req.read()

        # print (xml_txt)

        return url+data, xml_txt


    """
    ##################################################################################################################
    ##################################################################################################################
    ###################                                                                            ###################
    ###################          RUTINAS DE GESTION DE CAPAS DE LA VISTA Y SALIDAS                 ###################
    ###################                                                                            ###################
    ##################################################################################################################
    ##################################################################################################################
    """

    def makeHtmlListCoord(self, geometry):

        listCoord =''
        pathNum=1
        Mant = None

        listCoordHtml = (
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">'
            '<html><head><meta name="qrichtext" content="1" /><style type="text/css">'
            'p, li { white-space: pre-wrap; }'
            '</style></head><body style=" font-size:8.25pt; font-weight:400; font-style:normal;">'
            )

        try:
            paths = geometry["paths"]
            for path in paths:
                listCoordHtml += '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt; font-weight:600;">'
                listCoordHtml += 'TRAMO %s/%s (%s puntos)\n'%(str(pathNum),len(paths),len(path))
                listCoordHtml += '</span></p>'
                for point in path:
                    if point[2] is not None:
                        if Mant is not None:
                            if point[2]-Mant <0:
                                listCoordHtml += '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">'
                                listCoordHtml += "  %0.2f"%(point[0])+','+"%0.2f"%(point[1])+','+" %0.5f"%(point[2])+',</span><span style=" font-size:8pt; font-weight:600; color:#ff5500;">'+"%0.5f"%(point[2]-Mant)+'</span></p>'
                            else:
                                listCoordHtml += '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">'
                                listCoordHtml += "  %0.2f"%(point[0])+','+"%0.2f"%(point[1])+','+" %0.5f"%(point[2])+','+"%0.5f"%(point[2]-Mant)+'\n'
                                listCoordHtml += '</span></p>'
                        else:
                            listCoordHtml += '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">'
                            listCoordHtml += "  %0.2f"%(point[0])+','+"%0.2f"%(point[1])+','+" %0.5f"%(point[2])+'\n'
                            listCoordHtml += '</span></p>'
                        Mant = point[2]
                    else:
                        # listCoord += ' %s,%s,%s\n'%(str(round(point[0],2)),str(round(point[1],2)),'None')
                        listCoordHtml += '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">'
                        listCoordHtml += "  %0.2f"%(point[0])+','+" %0.2f"%(point[1])+',</span><span style=" font-size:8pt; font-weight:600; color:#ff5500;">'+" None"+'</span></p>'
                pathNum +=1
        except:
            paths = []
            if geometry.isMultipart():
                for part in geometry.asGeometryCollection ():
                    paths.append(part)
            else:
                paths.append(geometry)

            for path in paths:
                novertices = len(path.asPolyline())

                listCoordHtml += '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt; font-weight:600;">'
                listCoordHtml += 'TRAMO %s/%s (%s puntos)\n'%(str(pathNum),len(paths),novertices)
                listCoordHtml += '</span></p>'

                for id in range(novertices):
                    point = path.vertexAt(id)

                    if point.m() is not None:
                        if Mant is not None:
                            if point.m()-Mant <0:
                                listCoordHtml += '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">'
                                listCoordHtml += "  %0.2f"%(point.x())+','+"%0.2f"%(point.y())+','+" %0.5f"%(point.m())+',</span><span style=" font-size:8pt; font-weight:600; color:#ff5500;">'+"%0.5f"%(point.m()-Mant)+'</span></p>'
                            else:
                                listCoordHtml += '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">'
                                listCoordHtml += "  %0.2f"%(point.x())+','+"%0.2f"%(point.y())+','+" %0.5f"%(point.m())+','+"%0.5f"%(point.m()-Mant)+'\n'
                                listCoordHtml += '</span></p>'
                        else:
                            listCoordHtml += '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">'
                            listCoordHtml += "  %0.2f"%(point.x())+','+"%0.2f"%(point.y())+','+" %0.5f"%(point.m())+'\n'
                            listCoordHtml += '</span></p>'
                        Mant = point.m()
                    else:
                        listCoordHtml += '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">'
                        listCoordHtml += "  %0.2f"%(point.x())+','+" %0.2f"%(point.y())+',</span><span style=" font-size:8pt; font-weight:600; color:#ff5500;">'+" None"+'</span></p>'
                pathNum +=1

        return listCoordHtml

    def getLayerByName(self,name):
        layer = None
        for lyr in QgsProject.instance().mapLayers().values():
            if lyr.name() == name:
                layer = lyr
                break
        return layer

    def getCapasCsv(self, iface):
        layers =  QgsProject.instance().mapLayers().values()
        layer_names = []
        for layer in layers:
            source = layer.source()
            if layer.type() == QgsMapLayer.VectorLayer or (source.find('type=csv') > -1):
                if layer.name() != '':
                    layer_names.append(layer.name())
        return layer_names


    """
    ##################################################################################################################
    ##################################################################################################################
    ###################                                                                            ###################
    ###################                 RUTINAS DE GESTION DE DATOS CATASTRALES                    ###################
    ###################                                                                            ###################
    ##################################################################################################################
    ##################################################################################################################
    """

    def getCatastroMuniProv(self, point, iface, pintar):
        # Obtiene la provincia y Municipio de un punto pinchado a partir del servicio de catastro
        FUENTE = f'Servicios JSON Catastro'
        Municipio = 's/d'
        Provincia = 's/d'

        try:
            x, y = point[0], point[1]

            # Construir la URL para la API de Catastro
            url_base = "http://ovc.catastro.meh.es/OVCServWeb/OVCWcfCallejero/COVCCoordenadas.svc/json/Consulta_RCCOOR"
            query = QUrlQuery()
            query.addQueryItem("CoorX", str(int(round(x))))
            query.addQueryItem("CoorY", str(int(round(y))))
            query.addQueryItem("SRS", "EPSG:25830")

            full_url = QUrl(url_base)
            full_url.setQuery(query)
            print("URL de consulta:", full_url.toString())  # Para depuración

            # Configurar y enviar petición HTTP CORRECTAMENTE
            request = QNetworkRequest(full_url)
            request.setRawHeader(b"User-Agent", b"QGIS Plugin")
            network_manager = QgsNetworkAccessManager.instance()
            reply = network_manager.get(request)

            # Esperar a que termine la solicitud
            loop = QEventLoop()
            reply.finished.connect(loop.quit)
            loop.exec_()

            if reply.error() == QNetworkReply.NoError:
                data = reply.readAll().data().decode('utf-8')
                print("Respuesta Catastro:", data)  # Para depuración

                try:
                    json_data = json.loads(data)

                    # Extraer información de la descripción
                    ldt = json_data.get('Consulta_RCCOORResult', {}).get('coordenadas', {}).get('coord', [{}])[0].get('ldt', '')

                    if ldt:
                        # Ejemplo de ldt_text: "Polígono 1 Parcela 5110 CARRASCAL. MOTILLEJA (ALBACETE)"
                        pattern = r".*\.\s*([^\(]+)\s*\(([^\)]+)\)"
                        match = re.search(pattern, ldt)

                        if match:
                            Municipio = match.group(1).strip()
                            Provincia = match.group(2).strip()

                            return Municipio, Provincia, Municipio, 's/d', Provincia, 's/d', 'no data', FUENTE

                except (json.JSONDecodeError, KeyError, IndexError) as e:
                    print(f"Error procesando respuesta: {str(e)}")

            else:
                print(f"Error en la respuesta: {reply.errorString()}")

        except Exception as e:
            print(f"Error en la consulta: {str(e)}")

        # Si llegamos aquí es porque hubo algún error
        return 's/d', 's/d', 's/d', 's/d', 's/d', 's/d', 'no data', FUENTE

    def consultaCatastroXYtoRC(self, x ,y ,srs):
        # consultaCatastroXYtoRC(x,y)
        #   Permite obtener la REFCAT y otros datos de la parcela a partir de las coordenadas pinchada
        #   return (RC14, xml_txt, pc1, pc2, ldt)
        #   ENTRADA:
        #       x - X del punto pinchado
        #       y - Y del punto pinchado
        #       srs - Sistema Referencia de coordenadas (por defecto EPSG:25830 )
        #   SALIDA:
        #       RC14 - Referencia catastral de la parcela 14 dígitos
        #       xml_txt - Contenido completo del XML de respuesta
        #       pc1 - 7 primeros dígitos de la RefCat
        #       pc2 - 7 primeros dígitos de la RefCat
        #       ldt - DIRECCIÓN (CALLE, NÚMERO, MUNICIPIO O POLÍGONO, PARCELA Y MUNICIPIO) DE LA PARCELA
        #CREADA ASS

        # url = u'http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCoordenadas.asmx/Consulta_RCCOOR?'
        url = self.conf.catastro_tool["url_catastro_RCCOOR"]

        params = {
            'SRS':  srs,
            'Coordenada_X':x,
            'Coordenada_Y':y}

        str_values = {}
        for k, v in params.items():
            str_values[k] = unicode(v).encode('utf-8')
        data = urllib.parse.urlencode(str_values)
        print ('consultaCatastroXYtoRC - ', url+data)
        # try:
            # req = urllib.request.urlopen(url+data, timeout=TIMEOUT_SEGUNDOS)
        try:
            response = requests.get(url+data, timeout=TIMEOUT_SEGUNDOS)
            response.raise_for_status()  # Lanza excepción si hay error HTTP (4xx, 5xx)
            response = response.json()  # Esto ya es el JSON parseado
        except urllib.error.URLError as e:
            QApplication.restoreOverrideCursor()
            self.showMessage(u"Error de conexión a internet (fun.consultaCatastroXYtoRC)")
            return ("ERROR")
        except TimeoutError:
            QApplication.restoreOverrideCursor()
            self.showMessage(u"Timeout: El servidor de Catastro no responde")
            return ("ERROR")
        # try:
            # req = urllib.request.urlopen(url+data)
        # except:
            # QApplication.restoreOverrideCursor()
            # self.showMessage(u"Error de conexión a internet (fun.consultaCatastroXYtoRC)")
            # return ("ERROR")

        xml_txt =  response.read()
        xml = ET.fromstring(xml_txt)
        xml_dom = parseString(xml_txt)
        # print xml_txt

        try:
            cuerr = xml_dom.getElementsByTagName('cuerr')[0].toxml()
            cuerr = cuerr.replace('<cuerr>','').replace('</cuerr>','')
        except:
            cuerr = "0"
        # print "cuerr:  " + cuerr
        if (cuerr != "0"):
            cod = xml_dom.getElementsByTagName('cod')[0].toxml()
            cod = cod.replace('<cod>','').replace('</cod>','')
            des = xml_dom.getElementsByTagName('des')[0].toxml()
            des = des.replace('<des>','').replace('</des>','')
            if 'SRS' in des:
                message = f'PARECE QUE NO HAY CONFIGURADO UN SISTEMA DE COORDENADAS\n\nERROR: {str(cod)}  {des}'
            else:
                message = "ERROR: "+ str(cod)+ "\t" + des + u"\n\n -- PROBAR A PINCHAR OTRA POSICIÓN --"
            QApplication.restoreOverrideCursor()
            self.showMessageERR( message,'','Identificador de Catastro' )
            return (u'ERROR',message)


        for loc1 in xml.iter(u"{http://www.catastro.meh.es/}pc"):
            pc1 = loc1.find(u"{http://www.catastro.meh.es/}pc1").text
            pc2 = loc1.find(u"{http://www.catastro.meh.es/}pc2").text
            RC14 = pc1 + pc2

        for loc2 in xml.iter(u"{http://www.catastro.meh.es/}coord"):
            ldt = loc2.find(u"{http://www.catastro.meh.es/}ldt").text

        return (RC14, xml_txt, pc1, pc2, ldt)

    def consultaCatastroXYDISTtoRC(self, x ,y ,srs):
        # --CREADA ASS--
        # consultaCatastroXYDISTtoRC(x,y)
        #   Permite obtener la REFCAT y otros datos de la parcela a partir de las coordenadas pinchada
        #   return (REFCAT14, xml_txt, pc1, pc2, ldt)
        #   ENTRADA:
        #       x - X del punto pinchado
        #       y - Y del punto pinchado
        #       srs - Sistema Referencia de coordenadas (por defecto EPSG:25830 )
        #   SALIDA:
        #       REFCAT14 - Referencia catastral de la parcela 14 dígitos
        #       xml_txt - Contenido completo del XML de respuesta
        #       pc1 - 7 primeros dígitos de la RefCat
        #       pc2 - 7 primeros dígitos de la RefCat
        #       ldt - DIRECCIÓN (CALLE, NÚMERO, MUNICIPIO O POLÍGONO, PARCELA Y MUNICIPIO) DE LA PARCELA

        # url = u'http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCoordenadas.asmx/Consulta_RCCOOR?'
        # url = self.conf.catastro_tool["url_catastro_RCCOOR"]
        url = self.conf.catastro_tool["url_catastro_distancia"]

        params = {
            'SRS':  srs,
            'Coordenada_X':x,
            'Coordenada_Y':y}

        str_values = {}
        for k, v in params.items():
            str_values[k] = unicode(v).encode('utf-8')
        data = urllib.parse.urlencode(str_values)
        print ('consultaCatastroXYtoRC - ', url+data)

        try:
            response = requests.get(url+data, timeout=TIMEOUT_SEGUNDOS)
            response.raise_for_status()  # Lanza excepción si hay error HTTP (4xx, 5xx)
            response = response.json()  # Esto ya es el JSON parseado
        except urllib.error.URLError as e:
            QApplication.restoreOverrideCursor()
            message = u"Error de conexión a internet (fun.consultaCatastroXYtoRC)"
            self.showMessage(message)
            return (u'ERROR', message)
        except TimeoutError:
            QApplication.restoreOverrideCursor()
            message = u"Timeout: El servidor de Catastro no responde"
            self.showMessage(message)
            return (u'ERROR', message)
        # try:
            # req = urllib.request.urlopen(url+data)
        # except:
            # QApplication.restoreOverrideCursor()
            # message = u"Error de conexión a internet (fun.consultaCatastroXYtoRC)"
            # self.showMessage(message)
            # # return ("ERROR")
            # return (u'ERROR',message)

        xml_txt =  response.read()
        xml = ET.fromstring(xml_txt)
        xml_dom = parseString(xml_txt)
        # print (xml_txt)

        try:
            cuerr = xml_dom.getElementsByTagName('cuerr')[0].toxml()
            cuerr = cuerr.replace('<cuerr>','').replace('</cuerr>','')
        except:
            cuerr = "0"
        # print "cuerr:  " + cuerr
        if (cuerr != "0"):
            cod = xml_dom.getElementsByTagName('cod')[0].toxml()
            cod = cod.replace('<cod>','').replace('</cod>','')
            des = xml_dom.getElementsByTagName('des')[0].toxml()
            des = des.replace('<des>','').replace('</des>','')
            if 'SRS' in des:
                message = f'PARECE QUE NO HAY CONFIGURADO UN SISTEMA DE COORDENADAS\n\nERROR: {str(cod)}  {des}'
            else:
                message = "ERROR: "+ str(cod)+ "\t" + des + u"\n\n -- PROBAR A PINCHAR OTRA POSICIÓN --"
            # self.showMessageERR( message,'','Identificador de Catastro' )
            QApplication.restoreOverrideCursor()
            self.showMessageERR( message,'','Identificador de Catastro' )
            return (u'ERROR',message)

        # Detección de todas las RCs pinchada y colindantes
        listRC = []
        countParc = 0
        for pc in xml.iter(u"{http://www.catastro.meh.es/}pc"):
            pc1 = pc.find(u"{http://www.catastro.meh.es/}pc1").text
            pc2 = pc.find(u"{http://www.catastro.meh.es/}pc2").text
            REFCAT14 = pc1 + pc2
            countParc += 1
            listRC.append({'count':countParc, 'REFCAT14':REFCAT14, 'pc1':pc1, 'pc2':pc2})
            # print (countParc, 'REFCAT14:', REFCAT14, 'pc1:', pc1, 'pc2:', 'pc2:', pc2)

        countParc = 0
        for pcd in xml.iter(u"{http://www.catastro.meh.es/}pcd"):
            ldt = pcd.find(u"{http://www.catastro.meh.es/}ldt").text
            dis = pcd.find(u"{http://www.catastro.meh.es/}dis").text
            listRC[countParc]["ldt"] = ldt
            listRC[countParc]["dis"] = dis
            countParc += 1

        countParc = 0
        for loine in xml.iter(u"{http://www.catastro.meh.es/}loine"):
            cp = loine.find(u"{http://www.catastro.meh.es/}cp").text
            cm = loine.find(u"{http://www.catastro.meh.es/}cm").text
            listRC[countParc]["cp"] = cp
            listRC[countParc]["cm"] = cm
            countParc += 1

        countParc = 0
        for dir in xml.iter(u"{http://www.catastro.meh.es/}dir"):
            pnp = ''
            pnpTag = dir.find(u"{http://www.catastro.meh.es/}pnp")
            if pnpTag != None: pnp = pnpTag.text
            cv = ''
            cvTag = dir.find(u"{http://www.catastro.meh.es/}cv")
            if cvTag != None: cv = cvTag.text
            plp = ''
            plpTag = dir.find(u"{http://www.catastro.meh.es/}plp")
            if plpTag != None: cv = plpTag.text

            if pnp != '-1':
                tipoPar ='UR'
            else:
                tipoPar ='RU'
            if listRC[countParc]['pc2'][3] == '9':
                tipoPar ='X'

            listRC[countParc]["cv"] = cv
            listRC[countParc]["pnp"] = pnp
            listRC[countParc]["plp"] = plp
            listRC[countParc]["tipoPar"] = tipoPar
            countParc += 1

        # Detectamos la parcela pinchada
        REFCAT14 = ''
        pc1 = ''
        pc2 = ''
        ldt = ''
        tipoPar = ''
        countParc = 0
        for RC in listRC:
            # print (RC)
            if RC['dis'] == '0':
                REFCAT14 = listRC[countParc]['REFCAT14']
                pc1 = listRC[countParc]['pc1']
                pc2 = listRC[countParc]['pc2']
                ldt = listRC[countParc]['ldt']
                cp = listRC[countParc]['cp']
                cm = listRC[countParc]['cm']
                tipoPar = listRC[countParc]['tipoPar']
            countParc += 1

        # Detectamos si la parcela pinchada es DESCUENTO
        if REFCAT14 == '':
            message = "ERROR:  parcela sin Referencia Catastral\nProbablemente DESCUENTO\n\n -- PROBAR A PINCHAR OTRA POSICIÓN --"
            QApplication.restoreOverrideCursor()
            self.showMessageERR( message,'','Identificador de Catastro' )
            return (u'ERROR',message, listRC)
        cp = self.completarCeros(cp,2)
        cm = self.completarCeros(cm,3)

        #return(0         1        2    3    4    5   6   7        8
        # '''
        # for loc1 in xml.iter(u"{http://www.catastro.meh.es/}pc"):
            # pc1 = loc1.find(u"{http://www.catastro.meh.es/}pc1").text
            # pc2 = loc1.find(u"{http://www.catastro.meh.es/}pc2").text
            # REFCAT14 = pc1 + pc2

        # for loc2 in xml.iter(u"{http://www.catastro.meh.es/}coord"):
            # ldt = loc2.find(u"{http://www.catastro.meh.es/}ldt").text

        # return (REFCAT14, xml_txt, pc1, pc2, ldt)
        # '''
        return (REFCAT14, xml_txt, pc1, pc2, ldt, cp, cm, tipoPar, listRC)



    def consultaCatastroDATPARCELA(self, REFCAT14, mess = 'NO'):
        # CONSULTA DE DATOS DE PARCELA POR RC - Se debe meter en config
        #   Devuelve los datos libres de la parcela catastral
        #    ENTRADA
        #       REFCAT14 - Referencia catastral de la parcela 14 dígitos
        #    SALIDA
        #       tipoPAR,        #0 - TIPO DE PARCELA (Urbana, Rústica, Diseminado, X-Descuento)
        #       codnomPRO,      #1 - Código y nombre de provincia
        #       codnomMUN,      #2 - Código y nombre de municipio
        #       message,        #3 - Contador de BI, CONS y SUBP
        #       listaSUBP,      #4 - Listado del contenido de los datos de supparcelas
        #       listaCONSTRU,   #5 - Listado del contenido de los datos de construcciones
        #       supTOTAL,       #6 - Superficie de la parcela
        #       supCONSTR,      #7 - Superficie construida
        #       DATOSURBA,      #8 - Datos generales parcela urbana
        #       cp,             #9- Código de la provincia
        #       cm,             #10- Código del Municipio
        #       cmc,            #11- Código catastral del Municipio
        #       REFCAT,         #12- REFCAT completa (20 dígitos)
        #       cn,             #13- Tipo parcela RU, UR, DI, X
        #       cpo,            #14- Poligono
        #       cpa,            #15- Parcela
        #       cv,             #16- Codigo de la via
        #       pnp             #17- Numero de la via

        #       cat_nmspc       #20- nmspc del GML ES.SDGC.CP,  ES.LOCAL.CP
        #       PARAJE          #21- Nombre del paraje

        # url = u'http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/Consulta_DNPRC?'
        url = self.conf.catastro_tool["url_catastro_DNPRC"]

        params = {
            'Provincia': '',
            'Municipio': '',
            'RC': REFCAT14}

        str_values = {}
        for k, v in params.items():
            str_values[k] = unicode(v).encode('utf-8')
        data = urllib.parse.urlencode(str_values)
        print ('consultaCatastroDATPARCELA - '+url+data)
        # try:
            # req = urllib.request.urlopen(url+data, timeout=TIMEOUT_SEGUNDOS)
        try:
            response = requests.get(url+data, timeout=TIMEOUT_SEGUNDOS)
            response.raise_for_status()  # Lanza excepción si hay error HTTP (4xx, 5xx)
            response = response.json()  # Esto ya es el JSON parseado
        except urllib.error.URLError as e:
            QApplication.restoreOverrideCursor()
            self.showMessage(u"Error de conexión a internet (fun.consultaCatastroDATPARCELA)")
            return ("ERROR")
        except TimeoutError:
            QApplication.restoreOverrideCursor()
            self.showMessage(u"Timeout: El servidor de Catastro no responde")
            return ("ERROR")
        # try:
            # # response = json.load(urllib.request.urlopen(url+data)
            # # req = json.load(urllib.request.urlopen(url+data))
            # req = urllib.request.urlopen(url+data)
        # except:
            # QApplication.restoreOverrideCursor()
            # self.showMessage(u"Error de conexión a internet (fun.consultaCatastroDATPARCELA)")
            # return ("ERROR")

        if response==None:
            err = u'ERROR de Respuesta de catastro -Consulta_DNPRC-'
            #self.showMessage(err)
            return err

        xml_txt =  response.read()
        xml = ET.fromstring(xml_txt)
        xml_dom = parseString(xml_txt)
        # print (xml_txt)

        # Detectamos si catastro devuelve ERROR
        try:
            cuerr = xml_dom.getElementsByTagName('cuerr')[0].toxml()
            cuerr = cuerr.replace('<cuerr>','').replace('</cuerr>','')
        except:
            cuerr = "0"

        # print ("cuerr:  " + cuerr)
        if (cuerr != "0"):
            cod = xml_dom.getElementsByTagName('cod')[0].toxml()
            cod = cod.replace('<cod>','').replace('</cod>','')
            des = xml_dom.getElementsByTagName('des')[0].toxml()
            des = des.replace('<des>','').replace('</des>','')
            message = "ERROR: "+ str(cod)+ "\t" + des +u"\n      -- DESCUENTOS CATASTRALES --"
            # self.showMessageERR( message,'','Identificador de Catastro' )
            QApplication.restoreOverrideCursor()
            if mess == 'SI':
                self.showMessageERR( message,'','Identificador de Catastro' )
            return (u'ERROR '+message)

        # IDENTIFICAMOS DATOS CATASTRALES
        # print xml_txt
        cn = None
        cudnp = None
        cucons = None
        cucul = None

        message = u''       # Mensaje con el contenido de construcciones y subparcelas
        supTOTAL = 0        # Superficie total de la parcela
        supCONSTR = 0       # Superficie construida
        listaSUBP = ['No hay subparcelas']          # Listado del contenido de los datos de supparcelas
        listaCONSTRU = ['No hay construcciones']    # Listado del contenido de los datos de construcciones
        DATOSURBA = u''             #   Datos generales parcela urbana

        for loc in xml.iter(u"{http://www.catastro.meh.es/}idbi"):
            cn_dat = loc.find(u"{http://www.catastro.meh.es/}cn")
            if cn_dat != None:
                cn = cn_dat.text
                pass

        for loc in xml.iter(u"{http://www.catastro.meh.es/}control"):
            cudnp = loc.find(u"{http://www.catastro.meh.es/}cudnp")
            cucons = loc.find(u"{http://www.catastro.meh.es/}cucons")
            cucul = loc.find(u"{http://www.catastro.meh.es/}cucul")

        for loc in xml.iter(u"{http://www.catastro.meh.es/}rc"):
            pc1 = loc.find(u"{http://www.catastro.meh.es/}pc1").text
            pc2 = loc.find(u"{http://www.catastro.meh.es/}pc2").text
            car = loc.find(u"{http://www.catastro.meh.es/}car").text
            cc1 = loc.find(u"{http://www.catastro.meh.es/}cc1").text
            cc2 = loc.find(u"{http://www.catastro.meh.es/}cc2").text
            REFCAT = pc1 + pc2 + car + cc1 + cc2
        # print REFCAT

        cpo = '000'
        cpa = '00000'
        cv = '000'
        nv = 'XXX'
        pnp = '0000'
        npa = 's/d'
        if cn == 'UR':
            tipoPAR = 'URBANA'          # DATOS CATASTRALES URBANO
            listcv = xml_dom.getElementsByTagName('cv')
            if listcv: cv = listcv[0].toxml()
            cv = cv.replace('<cv>','').replace('</cv>','')
            listnv = xml_dom.getElementsByTagName('nv')
            if listnv: nv = listnv[0].toxml()
            nv = nv.replace('<nv>','').replace('</nv>','')
            listpnp = xml_dom.getElementsByTagName('pnp')
            if listpnp: pnp = listpnp[0].toxml()
            pnp = pnp.replace('<pnp>','').replace('</pnp>','')

            for loc in xml.iter(u"{http://www.catastro.meh.es/}debi"):
                luso = loc.find(u"{http://www.catastro.meh.es/}luso")
                sfc = loc.find(u"{http://www.catastro.meh.es/}sfc")
                cpt = loc.find(u"{http://www.catastro.meh.es/}cpt")
                ant = loc.find(u"{http://www.catastro.meh.es/}ant")
                if luso != None: DATOSURBA += "USO: "+ luso.text + "\n"
                # if cpt != None: DATOSURBA += "Coef.Part: "+ cpt.text + "\n"
                if cpt != None: DATOSURBA += "Coef.Part: "+ cpt.text
                if ant != None: DATOSURBA += "   Antiguedad: "+ ant.text
                # if sfc != None: supTOTAL = float(sfc.text)
                if sfc != None: supTOTAL += float(sfc.text)
                else: sfc = 0
            cpo = pc1[:4]
            cpa = pc1[4:7]


        elif cn == 'RU':
            tipoPAR = 'RUSTICA'         # DATOS CATASTRALES RUSTICA
            cpo = xml_dom.getElementsByTagName('cpo')[0].toxml()
            cpo = cpo.replace('<cpo>','').replace('</cpo>','')
            cpa = xml_dom.getElementsByTagName('cpa')[0].toxml()
            cpa = cpa.replace('<cpa>','').replace('</cpa>','')
            cpo = self.completarCeros(cpo,3)
            cpa = self.completarCeros(cpa,5)
            npa = xml_dom.getElementsByTagName('npa')[0].toxml()
            npa = npa.replace('<npa>','').replace('</npa>','')

        else:
            tipoPAR = 'S/D'             # DATOS CATASTRALES RÚSTICA/URBANA (Diseminados)

        cp = xml_dom.getElementsByTagName('cp')[0].toxml()
        cp = cp.replace('<cp>','').replace('</cp>','')
        cm = xml_dom.getElementsByTagName('cm')[0].toxml()
        cm = cm.replace('<cm>','').replace('</cm>','')
        cp = self.completarCeros(cp,2)
        cm = self.completarCeros(cm,3)

        cmc = xml_dom.getElementsByTagName('cmc')[0].toxml()
        cmc = cmc.replace('<cmc>','').replace('</cmc>','')
        cmc = self.completarCeros(cmc,3)
        np = xml_dom.getElementsByTagName('np')[0].toxml()
        np = np.replace('<np>','').replace('</np>','')
        nm = xml_dom.getElementsByTagName('nm')[0].toxml()
        nm = nm.replace('<nm>','').replace('</nm>','')
        codnomPRO = cp + "-" + np                           #Código y nombre de provincia
        codnomMUN = cm + "-" + nm + " (CODCAT:"+ cmc +")"   #Código y nombre de municipio
        # print codnomPRO
        # print codnomMUN

        if cudnp != None:
            message += u'Num.B.I.: ' + str(cudnp.text) + u'    '
            cudnpVAL = int(cudnp.text)

        if cucons != None:      # COMPROBACIÓN DE NÚMERO DE CONSTRUCCIONES

            listaCONSTRU = []
            message += u'Num.Cons: ' + str(cucons.text) + u'    '
            cuconsVAL = int(cucons.text)
            if (cuconsVAL > 0):
                # Hay varias Construcciones en la misma REFCAT
                count = 0
                # FALLA EN PARCELA 02071A50800010
                lcd=u's/d'
                es=u's/d'
                pt=u's/d'
                pu=u's/d'
                stl=u'0'

                for loc in xml.iter(u"{http://www.catastro.meh.es/}cons"):
                    CONST = u'CONSTRUCCIÓN: '
                    lcdVAL = loc.find(u"{http://www.catastro.meh.es/}lcd")
                    if lcdVAL!= None : lcd= lcdVAL.text
                    for loc1 in loc.iter(u"{http://www.catastro.meh.es/}loint"):
                        esVAL = loc1.find(u"{http://www.catastro.meh.es/}es")
                        if esVAL!= None : es= esVAL.text
                        ptVAL = loc1.find(u"{http://www.catastro.meh.es/}pt")
                        if ptVAL!= None : pt= ptVAL.text
                        puVAL = loc1.find(u"{http://www.catastro.meh.es/}pu")
                        if puVAL!= None : pu= puVAL.text
                    for loc1 in  loc.iter(u"{http://www.catastro.meh.es/}dfcons"):
                        stlVAL = loc1.find(u"{http://www.catastro.meh.es/}stl")
                        if stlVAL!= None : stl= stlVAL.text

                    # CONST += u'' + lcd + '  Esca:' + es + '  Plan:' + pt + '  Puer:' + pu + '  '+ locale.format("%d", float(stl), grouping=True) + u' m2\n'
                    CONST += u'' + lcd + '  Esca:' + es + '  Plan:' + pt + '  Puer:' + pu + '  '+ str(float(stl)) + u' m2\n'
                    listaCONSTRU.append(CONST)
                    count += 1
                    supCONSTR += float(stl)
                    pass

                pass
            else:
                listaCONSTRU = ['No hay construcciones']

        if cucul != None:   # COMPROBACIÓN DE NÚMERO DE SUBPARCELAS
            listaSUBP = []
            message += u'Num.Subp: ' + str(cucul.text) + u'    '
            cuculVAL = int(cucul.text)
            if (cuculVAL > 0):
                # Hay varias Subparcelas en la misma REFCAT
                count = 0
                for loc in xml.iter(u"{http://www.catastro.meh.es/}spr"):
                    SUBP = u'SUBP: '
                    cspr = loc.find(u"{http://www.catastro.meh.es/}cspr").text
                    ccc = xml_dom.getElementsByTagName('ccc')[count].toxml()
                    ccc = ccc.replace('<ccc>','').replace('</ccc>','')
                    dcc = xml_dom.getElementsByTagName('dcc')[count].toxml()
                    dcc = dcc.replace('<dcc>','').replace('</dcc>','')
                    ip = xml_dom.getElementsByTagName('ip')[count].toxml()
                    ip = ip.replace('<ip>','').replace('</ip>','')
                    ssp = xml_dom.getElementsByTagName('ssp')[count].toxml()
                    ssp = ssp.replace('<ssp>','').replace('</ssp>','')
                    # SUBP += u'' + cspr + '  ' + ccc + '  ' + dcc + '   Int.Prod:' + ip + '   Sup: ' + locale.format("%d", float(ssp), grouping=True) + u' m2\n'
                    SUBP += u'' + cspr + '  ' + ccc + '  ' + dcc + '   Int.Prod:' + ip + '   Sup: ' + str(float(ssp)) + u' m2\n'
                    listaSUBP.append(SUBP)
                    count += 1
                    supTOTAL += float(ssp)
                    if ccc =='VT':
                        tipoPAR = 'X-Descuento (D.P.)'
                        cn = 'X'
                    if ccc =='HG':
                        tipoPAR = u'X-Descuento (Hidrografia)'
                        cn = 'X'

                    pass
            else:
                listaSUBP = ['No hay subparcelas']

        if nv[:1] == 'D':
            tipoPAR = nv
            cn = nv[:2]

        if tipoPAR == 'S/D':
            cn = 'X'

        cat_nmspc = 'ES.SDGC.CP'

        # print (REFCAT14, '  ', cn, tipoPAR)
        # print ('REFCAT:%s supTOTAL:%s'%(REFCAT,supTOTAL))

        return (tipoPAR,        #0 - TIPO DE PARCELA (Urbana, Rústica, Diseminado, X-Descuento)
                codnomPRO,      #1 - Código y nombre de provincia
                codnomMUN,      #2 - Código y nombre de municipio
                message,        #3 - Contador de BI, CONS y SUBP
                listaSUBP,      #4 - Listado del contenido de los datos de supparcelas
                listaCONSTRU,   #5 - Listado del contenido de los datos de construcciones
                supTOTAL,       #6 - Superficie de la parcela
                supCONSTR,      #7 - Superficie construida
                DATOSURBA,      #8 - Datos generales parcela urbana
                cp,             #9 - Código de la provincia
                cm,             #10- Código del Municipio
                cmc,            #11- Código catastral del Municipio
                REFCAT,         #12- REFCAT completa (20 dígitos)
                cn,             #13- Tipo parcela RU, UR, DI, X
                cpo,            #14- Poligono
                cpa,            #15- Parcela
                cv,             #16- Codigo de la via
                pnp,            #17- Numero de la via
                np,             #18- Nombre de Provincia
                nm,             #19- Nombre de Municipio
                cat_nmspc,      #20- nmspc del GML ES.SDGC.CP,  ES.LOCAL.CP
                npa             #21- Nombre del paraje (si existe)
                )

    def consultaCatastroDATPARCELA01(self, REFCAT14, mess = 'NO'):
        # CONSULTA DE DATOS DE PARCELA POR RC - Se debe meter en config
        #   Devuelve los datos libres de la parcela catastral
        #    ENTRADA
        #       REFCAT14 - Referencia catastral de la parcela 14 dígitos
        #    SALIDA
        #       tipoPAR,        #0 - TIPO DE PARCELA (Urbana, Rústica, Diseminado, X-Descuento)
        #       codnomPRO,      #1 - Código y nombre de provincia
        #       codnomMUN,      #2 - Código y nombre de municipio
        #       message,        #3 - Contador de BI, CONS y SUBP
        #       listaSUBP,      #4 - Listado del contenido de los datos de supparcelas
        #       listaCONSTRU,   #5 - Listado del contenido de los datos de construcciones
        #       supTOTAL,       #6 - Superficie de la parcela
        #       supCONSTR,      #7 - Superficie construida
        #       DATOSURBA,      #8 - Datos generales parcela urbana
        #       cp,             #9- Código de la provincia
        #       cm,             #10- Código del Municipio
        #       cmc,            #11- Código catastral del Municipio
        #       REFCAT,         #12- REFCAT completa (20 dígitos)
        #       cn,             #13- Tipo parcela RU, UR, DI, X
        #       cpo,            #14- Poligono
        #       cpa,            #15- Parcela
        #       cv,             #16- Codigo de la via
        #       pnp             #17- Numero de la via

        #       cat_nmspc       #20- nmspc del GML ES.SDGC.CP,  ES.LOCAL.CP
        #       PARAJE          #21- Nombre del paraje

        # url = u'http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/Consulta_DNPRC?'
        url = self.conf.catastro_tool["url_catastro_DNPRC"]

        params = {
            'Provincia': '',
            'Municipio': '',
            'RC': REFCAT14}

        str_values = {}
        for k, v in params.items():
            str_values[k] = unicode(v).encode('utf-8')
        data = urllib.parse.urlencode(str_values)
        print ('consultaCatastroDATPARCELA - '+url+data)
        # try:
            # req = urllib.request.urlopen(url+data, timeout=TIMEOUT_SEGUNDOS)
        try:
            response = requests.get(url+data, timeout=TIMEOUT_SEGUNDOS)
            response.raise_for_status()  # Lanza excepción si hay error HTTP (4xx, 5xx)
            response = response.json()  # Esto ya es el JSON parseado
        except urllib.error.URLError as e:
            QApplication.restoreOverrideCursor()
            self.showMessage(u"Error de conexión a internet (fun.consultaCatastroDATPARCELA)")
            return ("ERROR")
        except TimeoutError:
            QApplication.restoreOverrideCursor()
            self.showMessage(u"Timeout: El servidor de Catastro no responde")
            return ("ERROR")
        # try:
            # # response = json.load(urllib.request.urlopen(url+data)
            # # req = json.load(urllib.request.urlopen(url+data))
            # req = urllib.request.urlopen(url+data)
        # except:
            # QApplication.restoreOverrideCursor()
            # self.showMessage(u"Error de conexión a internet (fun.consultaCatastroDATPARCELA)")
            # return ("ERROR")

        if response==None:
            err = u'ERROR de Respuesta de catastro -Consulta_DNPRC-'
            #self.showMessage(err)
            return err

        xml_txt =  response.read()
        xml = ET.fromstring(xml_txt)
        xml_dom = parseString(xml_txt)
        print ('xml_txt:\n', xml_txt)

        # Detectamos si catastro devuelve ERROR
        try:
            cuerr = xml_dom.getElementsByTagName('cuerr')[0].toxml()
            cuerr = cuerr.replace('<cuerr>','').replace('</cuerr>','')
        except:
            cuerr = "0"

        # print ("cuerr:  " + cuerr)
        if (cuerr != "0"):
            cod = xml_dom.getElementsByTagName('cod')[0].toxml()
            cod = cod.replace('<cod>','').replace('</cod>','')
            des = xml_dom.getElementsByTagName('des')[0].toxml()
            des = des.replace('<des>','').replace('</des>','')
            message = "ERROR: "+ str(cod)+ "\t" + des +u"\n      -- DESCUENTOS CATASTRALES --"
            # self.showMessageERR( message,'','Identificador de Catastro' )
            QApplication.restoreOverrideCursor()
            if mess == 'SI':
                self.showMessageERR( message,'','Identificador de Catastro' )
            return (u'ERROR '+message)

        # IDENTIFICAMOS DATOS CATASTRALES
        # print xml_txt
        cn = None
        cudnp = None
        cucons = None
        cucul = None

        message = u''       # Mensaje con el contenido de construcciones y subparcelas
        supTOTAL = 0        # Superficie total de la parcela
        supCONSTR = 0       # Superficie construida
        listaSUBP = ['No hay subparcelas']          # Listado del contenido de los datos de supparcelas
        listaCONSTRU = ['No hay construcciones']    # Listado del contenido de los datos de construcciones
        DATOSURBA = u''             #   Datos generales parcela urbana

        for loc in xml.iter(u"{http://www.catastro.meh.es/}idbi"):
            cn_dat = loc.find(u"{http://www.catastro.meh.es/}cn")
            if cn_dat != None:
                cn = cn_dat.text
                pass

        for loc in xml.iter(u"{http://www.catastro.meh.es/}control"):
            cudnp = loc.find(u"{http://www.catastro.meh.es/}cudnp")
            cucons = loc.find(u"{http://www.catastro.meh.es/}cucons")
            cucul = loc.find(u"{http://www.catastro.meh.es/}cucul")

        for loc in xml.iter(u"{http://www.catastro.meh.es/}rc"):
            pc1 = loc.find(u"{http://www.catastro.meh.es/}pc1").text
            pc2 = loc.find(u"{http://www.catastro.meh.es/}pc2").text
            car = loc.find(u"{http://www.catastro.meh.es/}car").text
            cc1 = loc.find(u"{http://www.catastro.meh.es/}cc1").text
            cc2 = loc.find(u"{http://www.catastro.meh.es/}cc2").text
            REFCAT = pc1 + pc2 + car + cc1 + cc2
        # print REFCAT

        cpo = '000'
        cpa = '00000'
        cv = '000'
        nv = 'XXX'
        pnp = '0000'
        npa = 's/d'
        if cn == 'UR':
            tipoPAR = 'URBANA'          # DATOS CATASTRALES URBANO
            listcv = xml_dom.getElementsByTagName('cv')
            if listcv: cv = listcv[0].toxml()
            cv = cv.replace('<cv>','').replace('</cv>','')
            listnv = xml_dom.getElementsByTagName('nv')
            if listnv: nv = listnv[0].toxml()
            nv = nv.replace('<nv>','').replace('</nv>','')
            listpnp = xml_dom.getElementsByTagName('pnp')
            if listpnp: pnp = listpnp[0].toxml()
            pnp = pnp.replace('<pnp>','').replace('</pnp>','')

            for loc in xml.iter(u"{http://www.catastro.meh.es/}debi"):
                luso = loc.find(u"{http://www.catastro.meh.es/}luso")
                sfc = loc.find(u"{http://www.catastro.meh.es/}sfc")
                cpt = loc.find(u"{http://www.catastro.meh.es/}cpt")
                ant = loc.find(u"{http://www.catastro.meh.es/}ant")
                if luso != None: DATOSURBA += "USO: "+ luso.text + "\n"
                # if cpt != None: DATOSURBA += "Coef.Part: "+ cpt.text + "\n"
                if cpt != None: DATOSURBA += "Coef.Part: "+ cpt.text
                if ant != None: DATOSURBA += "   Antiguedad: "+ ant.text
                # if sfc != None: supTOTAL = float(sfc.text)
                if sfc != None: supTOTAL += float(sfc.text)
                else: sfc = 0
            cpo = pc1[:4]
            cpa = pc1[4:7]


        elif cn == 'RU':
            tipoPAR = 'RUSTICA'         # DATOS CATASTRALES RUSTICA
            cpo = xml_dom.getElementsByTagName('cpo')[0].toxml()
            cpo = cpo.replace('<cpo>','').replace('</cpo>','')
            cpa = xml_dom.getElementsByTagName('cpa')[0].toxml()
            cpa = cpa.replace('<cpa>','').replace('</cpa>','')
            cpo = self.completarCeros(cpo,3)
            cpa = self.completarCeros(cpa,5)
            npa = xml_dom.getElementsByTagName('npa')[0].toxml()
            npa = npa.replace('<npa>','').replace('</npa>','')

        else:
            tipoPAR = 'S/D'             # DATOS CATASTRALES RÚSTICA/URBANA (Diseminados)

        cp = xml_dom.getElementsByTagName('cp')[0].toxml()
        cp = cp.replace('<cp>','').replace('</cp>','')
        cm = xml_dom.getElementsByTagName('cm')[0].toxml()
        cm = cm.replace('<cm>','').replace('</cm>','')
        cp = self.completarCeros(cp,2)
        cm = self.completarCeros(cm,3)

        cmc = xml_dom.getElementsByTagName('cmc')[0].toxml()
        cmc = cmc.replace('<cmc>','').replace('</cmc>','')
        cmc = self.completarCeros(cmc,3)
        np = xml_dom.getElementsByTagName('np')[0].toxml()
        np = np.replace('<np>','').replace('</np>','')
        nm = xml_dom.getElementsByTagName('nm')[0].toxml()
        nm = nm.replace('<nm>','').replace('</nm>','')
        codnomPRO = cp + "-" + np                           #Código y nombre de provincia
        codnomMUN = cm + "-" + nm + " (CODCAT:"+ cmc +")"   #Código y nombre de municipio
        # print codnomPRO
        # print codnomMUN

        if cudnp != None:
            message += u'Num.B.I.: ' + str(cudnp.text) + u'    '
            cudnpVAL = int(cudnp.text)

        if cucons != None:      # COMPROBACIÓN DE NÚMERO DE CONSTRUCCIONES

            listaCONSTRU = []
            message += u'Num.Cons: ' + str(cucons.text) + u'    '
            cuconsVAL = int(cucons.text)
            if (cuconsVAL > 0):
                # Hay varias Construcciones en la misma REFCAT
                count = 0
                # FALLA EN PARCELA 02071A50800010
                lcd=u's/d'
                es=u's/d'
                pt=u's/d'
                pu=u's/d'
                stl=u'0'

                for loc in xml.iter(u"{http://www.catastro.meh.es/}cons"):
                    CONST = u'CONSTRUCCIÓN: '
                    lcdVAL = loc.find(u"{http://www.catastro.meh.es/}lcd")
                    if lcdVAL!= None : lcd= lcdVAL.text
                    for loc1 in loc.iter(u"{http://www.catastro.meh.es/}loint"):
                        esVAL = loc1.find(u"{http://www.catastro.meh.es/}es")
                        if esVAL!= None : es= esVAL.text
                        ptVAL = loc1.find(u"{http://www.catastro.meh.es/}pt")
                        if ptVAL!= None : pt= ptVAL.text
                        puVAL = loc1.find(u"{http://www.catastro.meh.es/}pu")
                        if puVAL!= None : pu= puVAL.text
                    for loc1 in  loc.iter(u"{http://www.catastro.meh.es/}dfcons"):
                        stlVAL = loc1.find(u"{http://www.catastro.meh.es/}stl")
                        if stlVAL!= None : stl= stlVAL.text

                    # CONST += u'' + lcd + '  Esca:' + es + '  Plan:' + pt + '  Puer:' + pu + '  '+ locale.format("%d", float(stl), grouping=True) + u' m2\n'
                    CONST += u'' + lcd + '  Esca:' + es + '  Plan:' + pt + '  Puer:' + pu + '  '+ str(float(stl)) + u' m2\n'
                    listaCONSTRU.append(CONST)
                    count += 1
                    supCONSTR += float(stl)
                    pass

                pass
            else:
                listaCONSTRU = ['No hay construcciones']

        if cucul != None:   # COMPROBACIÓN DE NÚMERO DE SUBPARCELAS
            listaSUBP = []
            message += u'Num.Subp: ' + str(cucul.text) + u'    '
            cuculVAL = int(cucul.text)
            if (cuculVAL > 0):
                # Hay varias Subparcelas en la misma REFCAT
                count = 0
                for loc in xml.iter(u"{http://www.catastro.meh.es/}spr"):
                    SUBP = u'SUBP: '
                    cspr = loc.find(u"{http://www.catastro.meh.es/}cspr").text
                    ccc = xml_dom.getElementsByTagName('ccc')[count].toxml()
                    ccc = ccc.replace('<ccc>','').replace('</ccc>','')
                    dcc = xml_dom.getElementsByTagName('dcc')[count].toxml()
                    dcc = dcc.replace('<dcc>','').replace('</dcc>','')
                    ip = xml_dom.getElementsByTagName('ip')[count].toxml()
                    ip = ip.replace('<ip>','').replace('</ip>','')
                    ssp = xml_dom.getElementsByTagName('ssp')[count].toxml()
                    ssp = ssp.replace('<ssp>','').replace('</ssp>','')
                    # SUBP += u'' + cspr + '  ' + ccc + '  ' + dcc + '   Int.Prod:' + ip + '   Sup: ' + locale.format("%d", float(ssp), grouping=True) + u' m2\n'
                    SUBP += u'' + cspr + '  ' + ccc + '  ' + dcc + '   Int.Prod:' + ip + '   Sup: ' + str(float(ssp)) + u' m2\n'
                    listaSUBP.append(SUBP)
                    count += 1
                    supTOTAL += float(ssp)
                    if ccc =='VT':
                        tipoPAR = 'X-Descuento (D.P.)'
                        cn = 'X'
                    if ccc =='HG':
                        tipoPAR = u'X-Descuento (Hidrografia)'
                        cn = 'X'

                    pass
            else:
                listaSUBP = ['No hay subparcelas']

        if nv[:1] == 'D':
            tipoPAR = nv
            cn = nv[:2]

        if tipoPAR == 'S/D':
            cn = 'X'

        cat_nmspc = 'ES.SDGC.CP'

        # print (REFCAT14, '  ', cn, tipoPAR)
        # print ('REFCAT:%s supTOTAL:%s'%(REFCAT,supTOTAL))

        return (tipoPAR,        #0 - TIPO DE PARCELA (Urbana, Rústica, Diseminado, X-Descuento)
                codnomPRO,      #1 - Código y nombre de provincia
                codnomMUN,      #2 - Código y nombre de municipio
                message,        #3 - Contador de BI, CONS y SUBP
                listaSUBP,      #4 - Listado del contenido de los datos de supparcelas
                listaCONSTRU,   #5 - Listado del contenido de los datos de construcciones
                supTOTAL,       #6 - Superficie de la parcela
                supCONSTR,      #7 - Superficie construida
                DATOSURBA,      #8 - Datos generales parcela urbana
                cp,             #9 - Código de la provincia
                cm,             #10- Código del Municipio
                cmc,            #11- Código catastral del Municipio
                REFCAT,         #12- REFCAT completa (20 dígitos)
                cn,             #13- Tipo parcela RU, UR, DI, X
                cpo,            #14- Poligono
                cpa,            #15- Parcela
                cv,             #16- Codigo de la via
                pnp,            #17- Numero de la via
                np,             #18- Nombre de Provincia
                nm,             #19- Nombre de Municipio
                cat_nmspc,      #20- nmspc del GML ES.SDGC.CP,  ES.LOCAL.CP
                npa             #21- Nombre del paraje (si existe)
                )

    def cargarCapaParcCatBbox(self, nombrecapa, BboxLayer, tipo, crs):
        # cargarCapaParcelaCatastral(self,rc,nombrecapa,atributos, tipo,crs)
        #   Permite cargar desde internet el GMl de una parcela y la mete en un grupo
        #   ENTRADA:
        #       nombrecapa - Nombre de la capa en la que se añadira la parcela
        #       BboxLayer -
        #       tipo='gml', tipo='shp'
        #       crs= EPSG:25830
        #   SALIDA:
        #       layer - layer de la parcela cargada
        #
        #CREADA ASS

        # VARIABLES
        nom_layer = nombrecapa
        estiloCAPA = os.path.join(os.path.dirname(__file__), self.conf.catastro_tool["dir_estilos_catastro"] + u'/PARCELAS_SELECCION.qml')
        srsname = crs.replace( 'EPSG:', 'EPSG::')
        crs= 'crs='+ crs.lower()
        epsg = int(crs.replace('crs=epsg:', ''))
        tipo_layer= 'MultiPolygon'
        dest = 'memory'
        destDir = r"c:/Temp/"
        if not os.path.exists(destDir):
            os.makedirs(destDir)

        X0 = BboxLayer.xMaximum()
        Y0 = BboxLayer.yMaximum()
        X1 = BboxLayer.xMinimum()
        Y1 = BboxLayer.yMinimum()

        BboxTXT = str(int(X0))+','+str(int(Y0))+','+str(int(X1))+','+str(int(Y1))
        print (BboxTXT)

        # Obtención del GML de la parcela por Bbox (EJEMPLO)
        #   http://ovc.catastro.meh.es/INSPIRE/wfsCP.aspx?
        #       service=wfs&
        #       request=getfeature&
        #       Typenames=cp.cadastralparcel&
        #       SRSname=EPSG::25830&
        #       bbox=233673,4015968,233761,4016008

        url = self.conf.catastro_tool["url_catastro_DescGML"]

        params = {
            'service': 'wfs',
            'request': 'getfeature',
            'Typenames' : 'cp.cadastralparcel',
            'SRSname': srsname,
            'bbox' : BboxTXT,
            }
        str_values = {}
        for k, v in params.items():
            str_values[k] = unicode(v).encode('utf-8')
        data = urllib.parse.urlencode(str_values)
        sourceCAPA = url+data
        nombreFichGML = destDir + 'GMLprov.gml'
        print (url+data)

        # try:
            # response = urllib.request.urlopen(url+data, timeout=TIMEOUT_SEGUNDOS)
        try:
            response = requests.get(url+data, timeout=TIMEOUT_SEGUNDOS)
            response.raise_for_status()  # Lanza excepción si hay error HTTP (4xx, 5xx)
            response = response.json()  # Esto ya es el JSON parseado
            # response = urllib.request.urlopen(url+data)
        except:
            message = "ERROR: Problema de conexión"
            QApplication.restoreOverrideCursor()
            self.showMessageERR( message,'','Descarga Catastral' )
            # return (u'ERROR '+message)
            return (u'ERROR', message)

        xml_txt =  response.read()
        xml_dom = parseString(xml_txt)

        # Detectamos si catastro devuelve ERROR
        try:
            cuerr = xml_dom.getElementsByTagName('Exception')[0].toxml()
            cuerr = cuerr.replace('<Exception>','').replace('</Exception>','')
        except:
            cuerr = "0"
        if (cuerr != "0"):
            cod = xml_dom.getElementsByTagName('ExceptionText')[0].toxml()
            cod = cod.replace('<ExceptionText>','').replace('</ExceptionText>','')
            message = "ERROR: "+ str(cod)
            if 'Area of extension out of limits' in str(cod):
                message += u"\n\n -- POLÍGONO DE EXTENSIÓN DEMASIADO GRANDE --"
            QApplication.restoreOverrideCursor()
            self.showMessageERR( message,'','Descarga Catastral' )
            # return (u'ERROR '+message)
            return (u'ERROR', message)


        with open(nombreFichGML, 'wb') as file:
            file.write(xml_txt)
        catGML = QgsVectorLayer(nombreFichGML, 'GMLdesc', 'ogr')
        catGML.setCrs(QgsCoordinateReferenceSystem(epsg, QgsCoordinateReferenceSystem.EpsgCrsId))

        '''
        # Cargar capa catGML y poner arriba en el grupo 'PARCELAS CATASTRALES'
        QgsProject.instance().addMapLayer(catGML, False)          # Añadimos la capa a la TOC
        root = QgsProject.instance().layerTreeRoot()                # Root de la TOC
        nombregrupo="PARCELAS CATASTRALES"                          # Grupo en el que se insertará la nueva capa
        grupoBUSCAT = root.findGroup(nombregrupo)                   # Comprobamos si existe el grupo
        if grupoBUSCAT is None:
            grupoBUSCAT = root.insertGroup(0, nombregrupo)          # Se crea el nuevo grupo arriba
        grupoBUSCAT.insertChildNode(0, QgsLayerTreeLayer(catGML)) # Se coloca la capa en el grupo
        grupoBUSCAT.setExpanded(True)                               # Se expande el grupo (NO FUNCIONA)
        '''

        # CREACIÓN DE CAPA DE PARCELAS
        # Comprobamos si existe la capa de parcelas
        layerEXIST = QgsProject.instance().mapLayersByName(nom_layer)
        if not layerEXIST or layerEXIST[0].featureCount() == 0:
            if layerEXIST and layerEXIST[0].featureCount() == 0:
                vl = layerEXIST[0]
                QgsProject.instance().removeMapLayer( vl.id() )

            # CREACIÓN DE LA CAPA
            if dest == 'memory':
                vl = QgsVectorLayer(tipo_layer+'?'+crs, nom_layer, dest)
            else:
                if not os.path.isfile(dest):
                    print (u'NO EXISTE %s - HAY QUE CREARLO'%(dest))
                    # return
                vl = QgsVectorLayer(dest+'|'+tipo_layer+'?'+crs, nom_layer, "ogr")

                error = QgsVectorFileWriter.writeAsVectorFormat(vl, dest, nom_layer, None, "ESRI Shapefile")
                if error == QgsVectorFileWriter.NoError:
                    print("EXITO!")
                    pass
                vl.setCrs(QgsCoordinateReferenceSystem(epsg, QgsCoordinateReferenceSystem.EpsgCrsId))

            pr = vl.dataProvider()
            vl.startEditing()

            # AÑADIMOS LOS CAMPOS
            camposCatastro = self.defineCamposCatastro()    # Los campos catastrales se añaden de una forma común
            pr.addAttributes(camposCatastro)
            # pr.addAttributes([
                # QgsField("RC14", QVariant.String,       len= 20, comment='RC14.- Referencia Catastral 14 digitos'),
                # QgsField("NOM_MUNI", QVariant.String,   len=255, comment='NOM_MUNI.- Nombre literal del Municipio'),
                # QgsField("DELEGACIO", QVariant.Int,              comment='DELEGACIO.- Cod. Catastral Provincia'),
                # QgsField("MUNICIPIO", QVariant.Int,              comment='MUNICIPIO.- Cod. Catastral Municipio'),
                # QgsField("MASA", QVariant.String,       len= 10, comment='MASA.- Número poligono'),
                # QgsField("PARCELA", QVariant.String,    len= 10, comment='PARCELA.- Número parcela'),
                # QgsField("TIPO", QVariant.String,       len= 10, comment='TIPO.- urbano (UR) o rústico (RU)'),
                # QgsField("AREA", QVariant.Double,       len= 10, prec=2, comment='AREA.- Superficie de la parcela'),
                # QgsField("CAT_NMSPC", QVariant.String,  len= 10, comment='CAT_NMSPC.- (ES.SDGC.CP) o (ES.LOCAL.CP)'),
                # QgsField("PCAT1", QVariant.String,      len=  7, comment='PCAT1.- 7 Dígitos iniciales de la RC14'),
                # QgsField("PCAT2", QVariant.String,      len=  7, comment='PCAT2.- 7 Dígitos finales de la RC14'),
                # QgsField("PARAJE", QVariant.String,     len=255, comment='PARAJE.- Texto del Paraje'),
                # QgsField("EJERCICIO", QVariant.Int,              comment='EJERCICIO.- '),
                # QgsField("NUM_EXP", QVariant.Int,                comment='NUM_EXP.- '),
                # QgsField("CONTROL", QVariant.Int,                comment='CONTROL.- '),
                # QgsField("VIA", QVariant.String,        len=255, comment='VIA.- Código de vial'),
                # QgsField("NUMERO", QVariant.Int,                 comment='NUMERO.- Número de policía'),
                # QgsField("NUMERODUP", QVariant.String,  len= 50, comment='NUMERODUP.- '),
                # QgsField("NUMSYMBOL", QVariant.Int,              comment='NUMSYMBOL.- '),
                # QgsField("FECHAALTA", QVariant.String,  len= 25, comment='FECHAALTA.- '),
                # QgsField("FECHABAJA", QVariant.String,  len= 25, comment='FECHABAJA.- '),
                # QgsField("MAPA", QVariant.String,       len= 25, comment='MAPA.- '),
                # QgsField("HOJA", QVariant.String,       len= 25, comment='HOJA.- '),
                # QgsField("COORX",     QVariant.Double,  len= 10, prec=2, comment='COORX.- X centroide parcela'),
                # QgsField("COORY",     QVariant.Double,  len= 10, prec=2, comment='COORY.- Y centroide parcela'),
                # QgsField("DIRECCION", QVariant.String,  len=255, comment='DIRECCION.- Dirección de la Parcela'),
                # QgsField("PROVINCIA", QVariant.String,  len= 50, comment='PROVINCIA.- Provincia'),
                # QgsField("REF_CAT",   QVariant.String,  len= 25, comment='REF_CAT.- Referencia Catastral 20 dig.'),
                # QgsField("COD_INE",   QVariant.String,  len= 10, comment='COD_INE.- Código INI Municipio.')
                # ])

                    # else:
                        # field = QgsField(
                            # field_def['name'],
                            # field_def['type'],
                            # len=field_def.get('len', 255),
                            # comment=field_def['comment'])

            vl.updateFields()

            # Añade la capa a la TOC
            QgsProject.instance().addMapLayer(vl)

            # Establecemos el estilo de la capa
            vl.loadNamedStyle(estiloCAPA)

            # Commit changes y vuelve a editar
            vl.commitChanges()
        else:
            vl = layerEXIST[0]

        vl.startEditing()

        # Hacemos la capa visible
        QgsProject.instance().layerTreeRoot().findLayer(vl.id()).setItemVisibilityChecked(True)

        # Obtención de valores del GML, area, geometría, centroide
        feats = catGML.getFeatures()
        areagml = 0
        for feat in feats:
            RC14 = feat['localid']
            pc1 = RC14[:7]
            pc2 = RC14[7:14]
            areagml = feat['areaValue']     # AREA SACADA DEL GML
            cpcmc = RC14[:5]
            if pc2.isdigit():
                tipoPar ='RU'
                cp = cpcmc[:2]
                cmc = cpcmc[2:5]
                cpo = self.completarCeros(RC14[6:9],3)
                cpa = self.completarCeros(RC14[9:14],5)
                if RC14[10] == '9':
                    tipoPar ='X'
            else:
                tipoPar ='UR'
                cp = '00'
                cmc = '000'
                cpo = RC14[:4]
                cpa = RC14[4:7]

            beginLifespanVersion = feat['beginLifespanVersion']     # beginLifespanVersion SACADO DEL GML
            # print ('Parcela %s - Area '%rc, areagml )
            parcGML = feat.geometry()
            bbox = feat.geometry().boundingBox()
            centroid = feat.geometry().boundingBox().center()   # El centroide es el del boundingBox
            xgeom = centroid[0]
            ygeom = centroid[1]

            # Comprobamos si la parcela ya existe
            consulta = u'"RC14" = \''+feat['localid']+'\''
            expr = QgsExpression( consulta )
            it = vl.getFeatures( QgsFeatureRequest( expr ) )
            ids = [j.id() for j in it]
            if len(ids) == 0:

                # Añadimos la Geometría y Atributos al ELEMENTO de la capa PARCELAS
                feat1 = QgsFeature(vl.fields())
                feat1.setGeometry(parcGML)
                countAT = 0

                feat1.setAttribute('RC14', RC14)
                feat1.setAttribute('NOM_MUNI', 'nm')     # QVariant.String
                feat1.setAttribute('DELEGACIO', int(cp)) # QVariant.Int
                feat1.setAttribute('MUNICIPIO', int(cmc))# QVariant.Int
                feat1.setAttribute('MASA', cpo)          # QVariant.String
                feat1.setAttribute('PARCELA', cpa)       # QVariant.String
                feat1.setAttribute('TIPO', tipoPar)
                feat1.setAttribute('AREA', areagml)
                feat1.setAttribute('CAT_NMSPC', 'ES.SDGC.CP')
                feat1.setAttribute('PCAT1', pc1)
                feat1.setAttribute('PCAT2', pc2)
                # feat1.setAttribute('PARAJE', PARAJE)
                feat1.setAttribute('EJERCICIO', 0)
                feat1.setAttribute('NUM_EXP', 0)
                feat1.setAttribute('CONTROL', 0)
                feat1.setAttribute('VIA', '000' )
                feat1.setAttribute('NUMERO', 0 )
                feat1.setAttribute('NUMERODUP', '000' )
                feat1.setAttribute('NUMSYMBOL', 0 )
                feat1.setAttribute('FECHAALTA', beginLifespanVersion)
                feat1.setAttribute('FECHABAJA', 0 )
                feat1.setAttribute('MAPA', '000' )
                feat1.setAttribute('HOJA', '000')
                feat1.setAttribute('COORX', xgeom)
                feat1.setAttribute('COORY', ygeom)

                # Se añade el elemento en la capa
                vl.addFeature(feat1)

        vl.commitChanges()
        vl.updateExtents()


        # Ponemos la capa arriba
        root = QgsProject.instance().layerTreeRoot()
        myvl = root.findLayer(vl.id())
        parent = myvl.parent()
        myvlclone = myvl.clone()
        root.insertChildNode(0, myvlclone)
        try:
            parent.removeChildNode(myvl)
        except:
            print ('parent - ', parent.name(), type(parent), '   IMPOSIBLE BORRAR')

        return vl

    def defineCamposCatastro(self):
        # Se leen los tipos de campos desde config.py
        defCamposCatastro = self.conf.defCamposCatastro

        mapTipos = {
            'String': QVariant.String,
            'Int': QVariant.Int,
            'Double': QVariant.Double
        }

        camposCatastro = []
        for campo in defCamposCatastro:
            qtype = mapTipos[campo['type']]
            length = campo['len'] if campo['len'] else 0
            prec   = campo['prec'] if campo['prec'] else 0

            f = QgsField(
                name    = campo['name'],
                type    = qtype,
                len     = length,
                prec    = prec,
                comment = campo['comment']
            )
            camposCatastro.append(f)

        return camposCatastro

    def cargarCapaParcelaCatastral(self,rc,nombrecapa,atributos, tipo,crs):
        # cargarCapaParcelaCatastral(self,rc,nombrecapa,atributos, tipo,crs)
        #   Permite cargar desde internet el GMl de una parcela y la mete en un grupo
        #   ENTRADA:
        #       rc - Referencia catastral de la parcela
        #       nombrecapa - Nombre de la capa en la que se añadira la parcela
        #       atributos =
        #            RC14,PCAT1,PCAT2,EJERCICIO,NUM_EXP,CONTROL,COORY,VIA,
        #            NUMERO,NUMERODUP,NUMSYMBOL,AREA,FECHAALTA,FECHABAJA,MAPA,DELEGACIO,
        #            MUNICIPIO,MASA,HOJA,TIPO,PARCELA,COORX,NOM_MUNI,CAT_NMSPC, PARAJE
        #       tipo='gml', tipo='shp'
        #       crs= EPSG:25830
        #   SALIDA:
        #       layer - layer de la parcela cargada
        #
        #CREADA ASS

        # VARIABLES
        nom_layer = nombrecapa
        estiloCAPA = os.path.join(os.path.dirname(__file__), self.conf.catastro_tool["dir_estilos_catastro"] + u'/PARCELAS_SELECCION.qml')
        srsname = crs.replace( 'EPSG:', 'EPSG::')
        # print ('crs.lower(): ', crs.lower())
        crs= 'crs='+ crs.lower()
        # print ('crs= ', crs)
        epsg = int(crs.replace('crs=epsg:', ''))
        tipo_layer= 'MultiPolygon'
        dest = 'memory'
        destDir = r"c:/Temp/"
        if not os.path.exists(destDir):
            os.makedirs(destDir)

        # CREACIÓN DE CAPA DE PARCELAS
        # Comprobamos si existe la capa de parcelas
        layerEXIST = QgsProject.instance().mapLayersByName(nom_layer)
        if not layerEXIST or layerEXIST[0].featureCount() == 0:
            if layerEXIST and layerEXIST[0].featureCount() == 0:
                vl = layerEXIST[0]
                QgsProject.instance().removeMapLayer( vl.id() )

            # CREACIÓN DE LA CAPA
            if dest == 'memory':
                vl = QgsVectorLayer(tipo_layer+'?'+crs, nom_layer, dest)
            else:
                if not os.path.isfile(dest):
                    print (u'NO EXISTE %s - HAY QUE CREARLO'%(dest))
                    # return
                vl = QgsVectorLayer(dest+'|'+tipo_layer+'?'+crs, nom_layer, "ogr")

                error = QgsVectorFileWriter.writeAsVectorFormat(vl, dest, nom_layer, None, "ESRI Shapefile")
                if error == QgsVectorFileWriter.NoError:
                    print("EXITO!")
                    pass
                vl.setCrs(QgsCoordinateReferenceSystem(epsg, QgsCoordinateReferenceSystem.EpsgCrsId))

            pr = vl.dataProvider()
            vl.startEditing()

            # AÑADIMOS LOS CAMPOS
            camposCatastro = self.defineCamposCatastro()    # Los campos catastrales se añaden de una forma común
            pr.addAttributes(camposCatastro)

            vl.updateFields()

            # Añade la capa a la TOC
            QgsProject.instance().addMapLayer(vl)

            # Establecemos el estilo de la capa
            vl.loadNamedStyle(estiloCAPA)

            # Commit changes y vuelve a editar
            vl.commitChanges()
            vl.startEditing()
        else:
            vl = layerEXIST[0]
            vl.startEditing()

        # Hacemos la capa visible
        QgsProject.instance().layerTreeRoot().findLayer(vl.id()).setItemVisibilityChecked(True)

        url = self.conf.catastro_tool["url_catastro_DescGML"]

        response = self.descargaGmlParcCat(url, rc, srsname)

        nombreGML = destDir + 'GMLprov.gml'
        with open(nombreGML, 'wb') as file:
            file.write(response.content)
        layer = QgsVectorLayer(nombreGML, rc, 'ogr')
        layer.setCrs(QgsCoordinateReferenceSystem(epsg, QgsCoordinateReferenceSystem.EpsgCrsId))

        # Obtención de valores del GML, area, geometría, centroide
        feats = layer.getFeatures()

        # Contar el número de características manualmente
        feature_count = sum(1 for _ in feats)
        print ('NUM_FEATURES=',feature_count)

        # Verificar si el número de características es 0
        if feature_count == 0:
            QApplication.restoreOverrideCursor()
            print ('Error de selección de parcelas')
            # return (u'ERROR ')
            return (u'ERROR')

        # Se vuelve a generar feats con valores del GML, area, geometría, centroide
        feats = layer.getFeatures()
        areagml = 0
        for feat in feats:
            # areagml = feat['areaValue']     # AREA SACADA DEL GML
            # areagml += feat['areaValue']     # AREA SACADA DEL GML
            beginLifespanVersion = feat['beginLifespanVersion']     # beginLifespanVersion SACADO DEL GML
            # print ('Parcela %s - Area '%rc, areagml )
            # print ('areagml= ',areagml)
            parcGML = feat.geometry()
            # print (parcGML.type())
            areagml += parcGML.area()
            bbox = feat.geometry().boundingBox()
            centroid = feat.geometry().boundingBox().center()   # El centroide es el del boundingBox
            xgeom = centroid[0]
            ygeom = centroid[1]
            atributos['AREA'] = areagml
            atributos['FECHAALTA'] = beginLifespanVersion
            atributos['COORX'] = xgeom
            atributos['COORY'] = ygeom

            # Comprobamos si la parcela ya existe
            consulta = u'"RC14" = \''+atributos['RC14']+'\''
            expr = QgsExpression( consulta )
            it = vl.getFeatures( QgsFeatureRequest( expr ) )
            ids = [j.id() for j in it]
            # print consulta
            # print ('ENCONTRADOS '+ str(len(ids))+' CON RC= '+rc)
            if len(ids) == 0:
                # print ('añadimos la parcela '+rc[:14])
                # print 'NO EXISTE LA PARCELA '+rc

                # Añadimos la Geometría y Atributos al ELEMENTO de la capa PARCELAS
                feat1 = QgsFeature()
                feat1.setGeometry(parcGML)
                countAT = 0

                # Se añaden los atributos que al nuevo elemento
                fields = vl.fields()
                feat1.setFields(fields)
                for attr in atributos:
                    field_index = fields.indexFromName(attr)
                    if field_index != -1:
                        # if attr in fields:
                        feat1[attr] = atributos[attr]

                # Se añade el elemento en la capa
                vl.addFeature(feat1)

        # Se actualizan los cambios en la capa
        vl.commitChanges()
        vl.updateExtents()

        # Ponemos la capa arriba (1)
        root = QgsProject.instance().layerTreeRoot()
        myvl = root.findLayer(vl.id())
        parent = myvl.parent()
        myvlclone = myvl.clone()
        root.insertChildNode(0, myvlclone)
        try:
            parent.removeChildNode(myvl)
        except:
            print ('parent - ', parent.name(), type(parent), '   IMPOSIBLE BORRAR')

        # myvl.setName('BORRAR')
        # QgsProject.instance().removeMapLayers([myvl.id()])
        # QgsProject.instance().removeMapLayers([myvl])

        areagml = round(areagml,2)
        return vl, areagml, parcGML, bbox


    def descargaGmlParcCat(self, url, rc, srsname):
        # Obtención del GML de la parcela (EJEMPLO)
        #   http://ovc.catastro.meh.es/INSPIRE/wfsCP.aspx?
        #     service=wfs&
        #     version=2&
        #     request=getfeature&
        #     STOREDQUERIE_ID=GetParcel&
        #     refcat=3662001TF3136S&
        #     srsname=EPSG::25830

        # url = u'http://ovc.catastro.meh.es/INSPIRE/wfsCP.aspx?'
        #####
        #####     http://ovc.catastro.meh.es/INSPIRE/wfsCP.aspx?
        ###         service=wfs&
        ###         version=2&
        ###         request=getfeature&
        ###         typenames=cp:CadastralParcel&
        ###         STOREDQUERIE_ID=GetNeighbourParcel&
        ###         srsname=EPSG:25830&
        ###         REFCAT=02055A01900035
        #####
        params = {
            'service': 'wfs',
            'version': 2,
            'request': 'getfeature',
            'STOREDQUERIE_ID': 'GetParcel',
            'refcat': rc,
            'srsname': srsname
            }
        # print ('rc= ',rc)
        # print ('srsname= ',srsname)
        str_values = {}
        for k, v in params.items():
            str_values[k] = unicode(v).encode('utf-8')
        data = urllib.parse.urlencode(str_values)
        sourceCAPA = url+data
        print (url+data)

        try:
            response = requests.get(sourceCAPA, timeout=TIMEOUT_SEGUNDOS)
            return response
        except requests.exceptions.Timeout:
            message = "ERROR: Timeout - La petición excedió el tiempo de espera"
            QApplication.restoreOverrideCursor()
            self.showMessageERR(message)
            return False
        except requests.exceptions.ConnectionError:
            message = "ERROR: Problema de conexión"
            QApplication.restoreOverrideCursor()
            self.showMessageERR(message)
            return False
        except requests.exceptions.RequestException as e:
            message = f"ERROR: Problema en la petición - {str(e)}"
            QApplication.restoreOverrideCursor()
            self.showMessageERR(message)
            return False
        # try:
            # response = requests.get(sourceCAPA)
            # return response
        # except:
            # message = "ERROR: Problema de conexión"
            # QApplication.restoreOverrideCursor()
            # return False



    def consultaCatastroCodProvtoProvincia(self,codigo_provincia):
        # consultaCatastroCodProvtoProvincia(self,codigo_provincia)
        #   Devuelve el Nombre de la Provincia a partir del codigo
        #   return nombre_prov
        # url = u'http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/ConsultaProvincia?'
        url = self.conf.catastro_tool["url_catastro_Provincia"]

        print ('consultaCatastroCodProvtoProvincia -'+ url)
        # try:
            # req = urllib.request.urlopen(url, timeout=TIMEOUT_SEGUNDOS)
        try:
            response = requests.get(url+data, timeout=TIMEOUT_SEGUNDOS)
            response.raise_for_status()  # Lanza excepción si hay error HTTP (4xx, 5xx)
            response = response.json()  # Esto ya es el JSON parseado
            # req = urllib.request.urlopen(url)
        except:
            QApplication.restoreOverrideCursor()
            self.showMessage(u"Error de conexión a internet (fun.consultaCatastroCodProvtoProvincia lin:1762)")
            return ("ERROR")
        xml_txt =  response.read()
        xml = ET.fromstring(xml_txt)

        nombre_prov = 'NOMBRE_PROV'

        for prov in xml.iter(u"{http://www.catastro.meh.es/}prov"):
            # print prov.find(u"{http://www.catastro.meh.es/}cpine").text , prov.find(u"{http://www.catastro.meh.es/}np").text
            if(prov.find(u"{http://www.catastro.meh.es/}cpine").text == codigo_provincia):
                nombre_prov = prov.find(u"{http://www.catastro.meh.es/}np").text
                break
        # print ('codigo_provincia = ', codigo_provincia, '  nombre_prov = ', nombre_prov, '(fun.consultaCatastroCodProvtoProvincia lin:1774)')
        return nombre_prov


    def consultaCatastroCodMunitoMunicipio(self,nombre_prov, codigo_muni):
        # consultaCatastroCodMunitoMunicipio(self,nombre_prov, codigo_muni)
        #   Devuelve el Nombre del Municipio a partir de la Provincia del codigo_muni
        #   return nombre_muni

        # url = u'http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/ConsultaMunicipio?'
        url = self.conf.catastro_tool["url_catastro_municipio"]

        params = {
            'Provincia' : nombre_prov.encode("utf-8", errors="ignore"),
            'Municipio' : ''
            }
        data = urllib.parse.urlencode(params)
        # print ('consultaCatastroCodMunitoMunicipio -'+ url+data)
        # try:
            # req = urllib.request.urlopen(url+data, timeout=TIMEOUT_SEGUNDOS)
        try:
            response = requests.get(url+data, timeout=TIMEOUT_SEGUNDOS)
            response.raise_for_status()  # Lanza excepción si hay error HTTP (4xx, 5xx)
            response = response.json()  # Esto ya es el JSON parseado
            # req = urllib.request.urlopen(url+data)
        except:
            QApplication.restoreOverrideCursor()
            self.showMessage(u"Error de conexión a internet (fun.consultaCatastroCodMunitoMunicipio lin:1865)")
            return ("ERROR")
        xml_txt =  response.read()
        xml = ET.fromstring(xml_txt)

        # print ('nombre_prov = '+nombre_prov, '  codigo_muni = '+codigo_muni, '(fun.consultaCatastroCodMunitoMunicipio lin:1869)')

        nombre_muni = 'NOMBRE_MUNI'
        cmc = '000'

        for muni in xml.iter(u"{http://www.catastro.meh.es/}muni"):
            loine = muni.find(u"{http://www.catastro.meh.es/}loine")
            nombre_muni = muni.find(u"{http://www.catastro.meh.es/}nm").text
            cm = loine.find(u"{http://www.catastro.meh.es/}cm")
            cm = self.completarCeros(cm.text,3)
            locat = muni.find(u"{http://www.catastro.meh.es/}locat")
            cmc = locat.find(u"{http://www.catastro.meh.es/}cmc")
            cmc = self.completarCeros(cmc.text,3)
            # print (nombre_muni, cm, cmc)
            if(cm == codigo_muni):
                break
        # print ('ENTRADA: ', nombre_prov, codigo_muni)
        # print ('SALIDA: ', nombre_muni, cmc)
        return nombre_muni, cmc

    def cargaCatastroMuni(self, cp, cmc, nombre_muni, origenData, year, iface, mess, cargaIface):
        # Permite descargarse las capas de catastro de Polígonos y Parcelas conforme a Inspire
        # cp = '02' Código de Provincia
        # cmc = '008' Código de Municipio Catastral
        # nombre_muni =
        # origenData = 'web' o 'dir'
        # year = 'WEB', o Año a cargar si es desde diretorio
        # iface = interface
        # mess = True, False - Aparecen o no los mensajes de avisos
        # cargaIface = True, False - Se cargan o no las capas en la vista de mapa

        # URL PARCELAS       'https://www.catastro.hacienda.gob.es/INSPIRE/CadastralParcels/02/02006-ALCADOZO/A.ES.SDGC.CP.02006.zip'
        # URL DIRECCIONES    'https://www.catastro.hacienda.gob.es/INSPIRE/Addresses/02/02005-ALBOREA/A.ES.SDGC.AD.02005.zip'
        # URL CONSTRUCCIONES 'https://www.catastro.hacienda.gob.es/INSPIRE/Buildings/02/02004-ALBATANA/A.ES.SDGC.BU.02004.zip'

        # MODIFICADA url Base Catastro
        #   DONDE DECÍA:    http://www.catastro.minhap.es/INSPIRE
        #   DEBE DECIR:     https://www.catastro.hacienda.gob.es/INSPIRE
        ##-------------------------------------------------------------------------------------------------------------------##
        srs =  iface.mapCanvas().mapSettings().destinationCrs().authid()

        urlBaseCatastro = 'https://www.catastro.hacienda.gob.es'
        # print ('cp, cmc, nombre_muni, origenData, year, iface, mess, cargaIface')
        # print (cp, cmc, nombre_muni, origenData, year, iface, mess, cargaIface)

        if origenData == 'web':
            year = 'WEB'

        if(cmc == None):
            QApplication.restoreOverrideCursor()
            message = u"TÉRMINO MUNICIPAL NO DETECTADO"+ u"\n\n -- PROBAR A PINCHAR OTRA POSICIÓN --"
            self.showMessage( message,'','Capas de Catastro' )
            self.iface.mainWindow().statusBar().clearMessage()
            return 'ERROR', 'ERROR'

        codigo_muni_final = self.completarCeros(cmc,3)
        # cp = self.completarCeros(cp,2)
        # cmc = self.completarCeros(cmc,3)
        codigo = self.completarCeros(cp,2) + codigo_muni_final
        cpcmc= cp+cmc

        root = QgsProject.instance().layerTreeRoot()
        nombregrupo = "CAT - " + nombre_muni + " - " + codigo + " - (" +year + ")"
        grupoBUSCAT = root.findGroup(nombregrupo)
        resultCODTTMM = ['CP']  # Lista de ficheros a descargar definitiva

        if grupoBUSCAT is None: # NO está cargado el grupo de capas de catastro del TTMM
            message = u"Se van a cargar las capas del \n Catastro del año {} de {} - ({})\n\n -- LA OPERACIÓN TARDARÁ UNOS MINUTOS --".format(year,nombre_muni, codigo)
            if mess == True:
                if origenData == 'web':
                    message = u"Se van a cargar desde la Sede Electrónica de Catastro \n las capas del catastro actual \n del T. M.  {} - ({})\n\n -- LA OPERACIÓN TARDARÁ UNOS MINUTOS --".format(nombre_muni, codigo)
                QApplication.restoreOverrideCursor()

                # Abrimos cuadro de diálogo de consulta de carga de capas de TTMM
                listDescargas = ['CP']  # Lista de ficheros a descargar para pasar al menú de consulta
                datosMuni = [nombre_muni, codigo]
                dialog = catastroDescPolig_dialog(iface, datosMuni,listDescargas)
                dialog.exec_()
                resultCODTTMM = dialog.resultDialog # Lista de ficheros a descargar definitiva devuelta por el menú
                # print ('resultCODTTMM - ', resultCODTTMM)

                # if resultCODTTMM[0] == 'CANCELAR': # Se ha pulsado cancelar
                if 'CANCELAR' in resultCODTTMM: # Se ha pulsado cancelar
                    QApplication.restoreOverrideCursor()
                    iface.mainWindow().statusBar().clearMessage()
                    return 'ERROR', 'ERROR'

                ##---------------------------------------------------------------------------------------------------------##
                ##---------------------------------------------------------------------------------------------------------##
                # resp = self.showMessageYESNO( message,'','Capas de Catastro' )
                # if resp == 4194304: # Se ha pulsado cancelar
                    # QApplication.restoreOverrideCursor()
                    # iface.mainWindow().statusBar().clearMessage()
                    # return 'ERROR', 'ERROR'
                ##---------------------------------------------------------------------------------------------------------##
                ##---------------------------------------------------------------------------------------------------------##

                QApplication.setOverrideCursor(Qt.WaitCursor)

        else:
            QApplication.restoreOverrideCursor()
            if mess == True:
                message = u"Ya están cargadas las Capas del Catastro de \n" + nombre_muni + " (" + codigo + ")"
                self.showMessage( message,'','Capas de Catastro' )
                iface.mainWindow().statusBar().clearMessage()
            capaCatPol = "CAT- POL- " + nombre_muni+ " - " + codigo
            capaCatPar = "CAT- PAR- " + nombre_muni+ " - " + codigo
            return capaCatPol, capaCatPar


        # COMIENZA LA CARGA DE CAPAS DE CATASTRO DEL TTMM
        ##------------------------------------------------##
        progress = u'Cargando datos desde CATASTRO {codigo} - {nombre_muni}...'.format(codigo=codigo, nombre_muni=nombre_muni)
        iface.mainWindow().statusBar().showMessage(progress)

        resumen_capas = []
        if (codigo_muni_final != None):

            if origenData == 'web':       # ------- CARGA DE CAPAS DE CATASTRO DESDE SEDE ELECTRÓNICA DE CATASTRO ---------
                # result = self.cargaCatastroMuni(codigo_provincia, codigo_muni_final, nombre_muni)

                # 'https://www.catastro.hacienda.gob.es/INSPIRE/CadastralParcels/02/02006-ALCADOZO/A.ES.SDGC.CP.02006.zip',
                # 'https://www.catastro.hacienda.gob.es/INSPIRE/Addresses       /02/02005-ALBOREA /A.ES.SDGC.AD.02005.zip',
                # 'https://www.catastro.hacienda.gob.es/INSPIRE/Buildings       /02/02004-ALBATANA/A.ES.SDGC.BU.02004.zip'

                listCodFicheros = ['CP','AD','BU']
                messagePRUEBA = u"Se van a cargar las capas del catastro actual \n del T. M. ({}) {}".format(cp,cmc)
                # print (u"Se van a cargar las capas del catastro actual \n del T. M. ({}) {}".format(cp,cmc))

                dest = u'c:/temp/catastro_temp/'
                if not os.path.exists(dest):
                    os.makedirs(dest)

                # for codDESC in listCodFicheros:
                for codDESC in resultCODTTMM:
                    # if codDESC in resultCODTTMM:
                        # cpcmc= cp+cmc

                    if codDESC == 'CP':
                        tipoDESC = 'CadastralParcels'
                        nomFichDesc = 'cadastralparcel'
                        nomFichPar = u'A.ES.SDGC.CP.%s.cadastralparcel.gml'%(cpcmc)
                        nomFichPol = u'A.ES.SDGC.CP.%s.cadastralzoning.gml'%(cpcmc)
                        filelist = [nomFichPar,nomFichPol]
                    elif codDESC == 'BU':
                        tipoDESC = 'Buildings'
                        nomFichDesc = 'building'
                        nomFichBui = u'A.ES.SDGC.BU.%s.building.gml'%(cpcmc)
                        nomFichBup = u'A.ES.SDGC.BU.%s.buildingpart.gml'%(cpcmc)
                        nomFichOth = u'A.ES.SDGC.BU.%s.otherconstruction.gml'%(cpcmc)
                        filelist = [nomFichBui, nomFichBup, nomFichOth]
                    elif codDESC == 'AD':
                        tipoDESC = 'Addresses'
                        nomFichDesc = 'desconocido'
                        filelist = []

                    # Comprobar si existen los ficheros 'gml'
                    nomFichGENERICO = u'A.ES.SDGC.CP.%s.%s.gml'%(cpcmc, nomFichDesc)
                    # nomFichPol = u'A.ES.SDGC.CP.%s.cadastralzoning.gml'%(cpcmc)
                    if os.path.exists(dest + nomFichGENERICO):        # Existen los ficheros de parcela 'gml'
                        # print ('Existen los ficheros - ' + str(filelist))
                        pass
                    else:
                        # No existen los ficheros 'gml'
                        # web xml de datos
                        # https://www.catastro.hacienda.gob.es/INSPIRE/CadastralParcels/02/ES.SDGC.CP.atom_02.xml
                        # url = 'http://www.catastro.minhap.es/INSPIRE/{tipoD}/{prov}/ES.SDGC.{codD}.atom_{prov}.xml'.format(tipoD=tipoDESC, codD=codDESC, prov=cp)
                        # url = 'http://www.catastro.minhap.es/INSPIRE/{tipoD}/{prov}/{cmc}-{nombre_muni}/ES.SDGC.{codD}.atom_{prov}.xml' .format(tipoD=tipoDESC, codD=codDESC, prov=cp, cmc=cmc, nombre_muni=nombre_muni)

                        ## URL CAMBIADA EN 2024/10
                        url = urlBaseCatastro+'/INSPIRE/{tipoD}/{prov}/ES.SDGC.{codD}.atom_{prov}.xml'.format(tipoD=tipoDESC, codD=codDESC, prov=cp)

                        # print ('URL DE LA PROVINCIA A DESCARGAR')
                        # print (url)

                        urlALT = 'https://www.catastro.hacienda.gob.es/INSPIRE/CadastralParcels/ES.SDGC.CP.atom.xml'

                        # try:
                            # response = urllib.request.urlopen(urlALT, timeout=TIMEOUT_SEGUNDOS)
                        try:
                            response = requests.get(urlALT, timeout=TIMEOUT_SEGUNDOS)
                            response.raise_for_status()  # Lanza excepción si hay error HTTP (4xx, 5xx)
                            response = response.json()  # Esto ya es el JSON parseado
                            # response = urllib.request.urlopen(urlALT)
                        except urllib.error.URLError as e:
                            QApplication.restoreOverrideCursor()
                            text = f"Error al conectar con Catastro\n\n{urlALT}"
                            self.showMessage(text, '', 'Consulta a Catastro')
                            return 'ERROR', 'ERROR'
                        except TimeoutError:
                            QApplication.restoreOverrideCursor()
                            self.showMessage("Timeout: El servidor de Catastro no responde", '', 'Consulta a Catastro')
                            return 'ERROR', 'ERROR'
                        # response = urllib.request.urlopen(urlALT, timeout=100)
                        html = response.read()
                        # print (html)

                        try:
                            response = requests.get(url, timeout=TIMEOUT_SEGUNDOS)
                            response.raise_for_status()
                            xmldoc = minidom.parseString(response.text)
                        except requests.exceptions.Timeout:
                            QApplication.restoreOverrideCursor()
                            self.showMessage("Timeout: El servidor de Catastro no responde", '', 'Consulta a Catastro')
                            return 'ERROR', 'ERROR'
                        except requests.exceptions.ConnectionError as e:
                            text = f"Error al conectar con Catastro\n\n{url}\n\n{str(e)}"
                            QApplication.restoreOverrideCursor()
                            self.showMessage(text, '', 'Consulta a Catastro')
                            return 'ERROR', 'ERROR'
                        except requests.exceptions.HTTPError as e:
                            text = f"Error HTTP {e.response.status_code} al conectar con Catastro\n\n{url}"
                            QApplication.restoreOverrideCursor()
                            self.showMessage(text, '', 'Consulta a Catastro')
                            return 'ERROR', 'ERROR'
                        except requests.exceptions.RequestException as e:
                            text = f"Error al conectar con Catastro\n\n{url}\n\n{str(e)}"
                            QApplication.restoreOverrideCursor()
                            self.showMessage(text, '', 'Consulta a Catastro')
                            return 'ERROR', 'ERROR'
                        # try:
                            # xmldoc = minidom.parse(urllib.request.urlopen(url, timeout=TIMEOUT_SEGUNDOS))
                        # except urllib.error.URLError as e:
                            # text = f"Error al analizar el XML mediante la url \n\n{url}"
                            # QApplication.restoreOverrideCursor()
                            # self.showMessage(text, '', 'Consulta a Catastro')
                            # iface.mainWindow().statusBar().clearMessage()
                            # return 'ERROR', 'ERROR'
                        # except TimeoutError:
                            # QApplication.restoreOverrideCursor()
                            # self.showMessage("Timeout: El servidor de Catastro no responde", '', 'Consulta a Catastro')
                            # return 'ERROR', 'ERROR'
                        # try:
                            # xmldoc = minidom.parse(urllib.request.urlopen(url))
                        # except:
                            # # Si hay un error, muestra el mensaje
                            # text = f"Error al analizar el XML mediante la url \n\n{url}"
                            # QApplication.restoreOverrideCursor()
                            # resp = self.showMessage( text,'','Consulta a Catastro' )
                            # iface.mainWindow().statusBar().clearMessage()
                            # return 'ERROR', 'ERROR'

                        itemlist = xmldoc.getElementsByTagName('link')
                        zip_file_url = ''
                        for s in itemlist:
                            zip_file_url_tm = s.attributes['href'].value
                            # if zip_file_url_tm.find(cmc) != -1:
                            if zip_file_url_tm.find(cpcmc) != -1:
                                zip_file_url = zip_file_url_tm
                                break

                        print ('cargaCatastroMuni - '+zip_file_url)
                        try:
                            zip_file_url = self.convertTOurl(zip_file_url)
                        except:
                            QApplication.restoreOverrideCursor()
                            resp = self.showMessageYESNO( '- NO HAY RESPUESTA DE CATASTRO -','','Consulta a Catastro' )
                            iface.mainWindow().statusBar().clearMessage()
                            return 'ERROR', 'ERROR'

                        filelist = []

                        try:
                            # Descargar el archivo ZIP con requests
                            response = requests.get(zip_file_url, timeout=TIMEOUT_SEGUNDOS)
                            response.raise_for_status()  # Lanza excepción para códigos HTTP 4xx/5xx

                            # Procesar el ZIP desde la memoria
                            z = zipfile.ZipFile(io.BytesIO(response.content))
                            z.extractall(dest)

                            for file in z.namelist():
                                filelist.append(file)

                            result = 'OK'

                        except requests.exceptions.Timeout:
                            print(f'Timeout al descargar el fichero de {cpcmc} - {nombre_muni}')
                            QApplication.restoreOverrideCursor()
                            result = 'ERROR'

                        except requests.exceptions.ConnectionError as e:
                            print(f'No se puede descargar el fichero de {cpcmc} - {nombre_muni}\n{str(e)}')
                            QApplication.restoreOverrideCursor()
                            result = 'ERROR'

                        except requests.exceptions.HTTPError as e:
                            print(f'Error HTTP {response.status_code} al descargar el fichero de {cpcmc} - {nombre_muni}\n{str(e)}')
                            QApplication.restoreOverrideCursor()
                            result = 'ERROR'

                        except requests.exceptions.RequestException as e:
                            print(f'No se puede descargar el fichero de {cpcmc} - {nombre_muni}\n{str(e)}')
                            QApplication.restoreOverrideCursor()
                            result = 'ERROR'

                        except Exception as e:
                            print(f'No se puede descargar el fichero de {cpcmc} - {nombre_muni}\n{str(e)}')
                            QApplication.restoreOverrideCursor()
                            result = 'ERROR'

                        # try:
                            # # print ('Descargado el fichero de '+ cpcmc +' - '+ nombre_muni+ '\n')
                            # url = urllib.request.urlopen(zip_file_url, timeout=TIMEOUT_SEGUNDOS) ## VER ESTO
                            # # url = urllib.request.urlopen(zip_file_url)
                            # z = zipfile.ZipFile(io.BytesIO(url.read()))
                            # z.extractall(dest)
                            # for file in z.namelist():
                                # # filelist.append(file[4:])
                                # filelist.append(file)
                                # # print file[4:]
                            # result = 'OK'

                        # except urllib.error.URLError as e:      ## VER ESTO
                            # print(f'No se puede descargar el fichero de {cpcmc} - {nombre_muni}\n{str(e)}')
                            # QApplication.restoreOverrideCursor()
                            # result = 'ERROR'
                        # except TimeoutError:                    ## VER ESTO
                            # print(f'Timeout al descargar el fichero de {cpcmc} - {nombre_muni}')
                            # QApplication.restoreOverrideCursor()
                            # result = 'ERROR'

                        # except Exception as e:
                            # print ('No se puede descargar el fichero de '+ cpcmc +' - '+ nombre_muni+ '\n'+ str(e))
                            # QApplication.restoreOverrideCursor()
                            # result = 'ERROR'

                    # dest = result[1]
                    epsg = int(srs[5:])
                    crs = 'crs='+ srs.lower()
                    tipo_layer= 'Polygon'
                    abs_path = []

                    # Se cargan los ficheros 'GML'
                    capaCatPol = ''
                    capaCatPolFich = ''
                    capaCatPar = ''
                    capaCatParFich = ''
                    for file in filelist:
                        if file.endswith(".gml"):
                            abs_file = dest+file

                            # Establecemos el nombre y estilo de la capa
                            if file.find('cadastralzoning') != -1:      # Capa de Poligonos
                                nombreCAPA = "CAT- POL- " + nombre_muni+ " - " + codigo
                                estiloCAPA = os.path.join(os.path.dirname(__file__), self.conf.catastro_tool["dir_estilos_catastro"] + 'CAT_POLIGONO_WEB.qml')
                                capaCatPol = nombreCAPA
                                capaCatPolFich = abs_file
                            elif file.find('cadastralparcel') != -1:    # Capa de Parcelas
                                nombreCAPA = "CAT- PAR- " + nombre_muni+ " - " + codigo
                                estiloCAPA = os.path.join(os.path.dirname(__file__), self.conf.catastro_tool["dir_estilos_catastro"] + 'CAT_PARCELA_WEB.qml')
                                capaCatPar = nombreCAPA
                                capaCatParFich = abs_file
                            elif file.find('building.') != -1:          # Capa de Edificaciones
                                nombreCAPA = "CAT- EDI- " + nombre_muni+ " - " + codigo
                                estiloCAPA = os.path.join(os.path.dirname(__file__), self.conf.catastro_tool["dir_estilos_catastro"] + 'CAT_EDIFICA_WEB.qml')
                            elif file.find('buildingpart.') != -1:      # Capa de Edificaciones Partes
                                nombreCAPA = "CAT- EDP- " + nombre_muni+ " - " + codigo
                                estiloCAPA = os.path.join(os.path.dirname(__file__), self.conf.catastro_tool["dir_estilos_catastro"] + 'CAT_EDIFICAPARTES_WEB.qml')
                            elif file.find('otherconstruction') != -1:  # Capa de Otras Construcciones
                                nombreCAPA = "CAT- EOT- " + nombre_muni+ " - " + codigo
                                estiloCAPA = os.path.join(os.path.dirname(__file__), self.conf.catastro_tool["dir_estilos_catastro"] + 'CAT_EDIFICAOTRAS_WEB.qml')
                            else:                                       # Capa de Direcciones
                                nombreCAPA = "CAT- DIR- " + nombre_muni+ " - " + codigo
                                estiloCAPA = os.path.join(os.path.dirname(__file__), self.conf.catastro_tool["dir_estilos_catastro"] + 'CAT_DIRECCIONES_WEB.qml')

                            # vl = QgsVectorLayer(abs_file+'|'+tipo_layer+'?'+crs, nombreCAPA, "ogr")
                            if cargaIface: # Se carga la capa en la vista
                                vl = QgsVectorLayer(abs_file, nombreCAPA, "ogr")
                                # print ('SE CARGA - ', nombreCAPA, abs_file)
                                if estiloCAPA != '':
                                    vl.loadNamedStyle(estiloCAPA)
                                QgsProject.instance().addMapLayer(vl, False)
                                resumen_capas.append(vl)

            else:       # ------- CARGA DE CAPAS DE CATASTRO DESDE DIRECTORIO ---------
                ################################################################################################
                ################################################################################################
                #               TODO. REVISAR LA CARGA DESDE DIRECTORIO
                ################################################################################################
                ################################################################################################
                # CAPAS DE CATASTRO DE URBANA
                for capa in self.conf.catastro_tool["capas_urbanas"]:
                    # year = str(self.conf.catastro_tool["year"])
                    provincia_text = self.getProvinciaText(codigo_provincia)
                    if(provincia_text == None):
                        QApplication.restoreOverrideCursor()
                        QgsMessageLog.logMessage( "Provincia no perteneciente a Castilla La Mancha",self.nombre_plugin)
                        iface.mainWindow().statusBar().clearMessage()
                        return
                    source = self.conf.catastro_tool["dir_shps"] + year + u"/" + provincia_text + u"/" + codigo_provincia + codigo_muni_final + u"u/" + capa["capa"]
                    nombre = "CAT-" + capa["nombre"] + nombre_muni + " " + year
                    estilo = os.path.join(os.path.dirname(__file__), self.conf.catastro_tool["dir_estilos_catastro"] + capa["estilo"])
                    capa_cargada = self.getSHP(self.iface, source, nombre, estilo)
                    if(capa_cargada != None):
                        QgsMapLayerRegistry.instance().addMapLayer(capa_cargada, False)
                        resumen_capas.append(capa_cargada)

                    pass

                # CAPAS DE CATASTRO DE RÚSTICA
                for capa in self.conf.catastro_tool["capas_rusticas"]:
                    year = str(self.conf.catastro_tool["year"])
                    provincia_text = self.getProvinciaText(codigo_provincia)
                    if(provincia_text == None):
                        QApplication.restoreOverrideCursor()
                        QgsMessageLog.logMessage( "Provincia no perteneciente a Castilla La Mancha",self.nombre_plugin)
                        iface.mainWindow().statusBar().clearMessage()
                        return
                    source = self.conf.catastro_tool["dir_shps"] + year + u"/" + provincia_text + u"/" + codigo_provincia + codigo_muni_final + u"r/" + capa["capa"]
                    nombre = "CAT-" + capa["nombre"] + nombre_muni + " " + year
                    estilo = os.path.join(os.path.dirname(__file__), self.conf.catastro_tool["dir_estilos_catastro"] + capa["estilo"])
                    capa_cargada = self.getSHP(self.iface, source, nombre, estilo)
                    if(capa_cargada != None):
                        QgsMapLayerRegistry.instance().addMapLayer(capa_cargada, False)
                        resumen_capas.append(capa_cargada)
                ################################################################################################
                ################################################################################################
                pass

            if cargaIface:
                if not resumen_capas:
                    # Se comprueba si la lista de capas de catastro está vacía
                    QApplication.restoreOverrideCursor()
                    message = "No hay capas para cargar del catastro \n" + nombregrupo
                    QApplication.restoreOverrideCursor()
                    self.showMessageERR( message,'','Carga de capas de Catastro' )
                    iface.mainWindow().statusBar().clearMessage()
                    return

                grupoCAT = root.insertGroup(self.conf.catastro_tool["cat_pos_toc"], nombregrupo)

                for capa in resumen_capas:
                    grupoCAT.insertChildNode(0, QgsLayerTreeLayer(capa))

            print ('capaCatPol ',capaCatPol, 'capaCatPar ', capaCatPar, 'capaCatPolFich ', capaCatPolFich, 'capaCatParFich ', capaCatParFich)
            return capaCatPol, capaCatPar, capaCatPolFich, capaCatParFich

    def getProvinciasCatastro(self):
        # url = u'http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/ConsultaProvincia?'
        url = self.conf.catastro_tool['url_catastro_Provincia']
        # time = 60

        print ('getProvinciasCatastro - ', url)
        req = self.uptime_bot(url)

        xml_txt =  req.read()
        try:
            xml = ET.fromstring(xml_txt)
        except:
            msg = '-NO HAY RESPUESTA DE CATASTRO-\n PRUEBE MÁS TARDE'
            self.showMessage(msg)
            return 'nocat','nocat'


        lista_provincias = []
        lista_cpine = []

        for prov in xml.iter(u"{http://www.catastro.meh.es/}prov"):
            np = prov.find(u"{http://www.catastro.meh.es/}np")
            cpine = prov.find(u"{http://www.catastro.meh.es/}cpine")
            lista_provincias.append(np.text)
            lista_cpine.append(cpine.text)
            # print (cpine.text,',', np.text)

        return lista_provincias, lista_cpine

    def getProvinciaCode(self,provincia):
        # getProvinciaCode(self,provincia)
        #   Devuelve el código catastral de Provincia
        #   return codigo_provincia

        # url = u'http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/ConsultaProvincia?'
        url = self.conf.catastro_tool['url_catastro_Provincia']

        print ('getProvinciaCode - ',url)
        req = self.uptime_bot(url)

        try:
            xml_txt =  req.read()
        except:
            QApplication.restoreOverrideCursor()
            self.showMessage(u"Error de conexión a catastro")
            return

        xml = ET.fromstring(xml_txt)

        codigo_provincia = ''

        for prov in xml.iter(u"{http://www.catastro.meh.es/}prov"):
           if(prov.find(u"{http://www.catastro.meh.es/}np").text == provincia):
               codigo_provincia = prov.find(u"{http://www.catastro.meh.es/}cpine").text
        return codigo_provincia

    def getMunicipiosCatastro(self, provincia):
        # url = 'http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/ConsultaMunicipio?'
        url = self.conf.catastro_tool["url_catastro_municipio"]
        # time = 2

        params = {'Provincia' : provincia,
                  'Municipio' : ''
                  }

        data = urllib.parse.urlencode(params)
        print ('getMunicipiosCatastro - ', url+data)

        try:
            req = self.uptime_bot(url+data)         ## VER ESTO
            if req == 'Error de internet' or req == 'Timeout':
                self.showMessage(u"Error de conexión a catastro en LISTA MUNICIPIOS")
                return
        except Exception as e:
            self.showMessage(u"Error de conexión a catastro en LISTA MUNICIPIOS")
            return
        # req = self.uptime_bot(url+data)

        try:
            xml_txt =  req.read()
        except:
            self.showMessage(u"Error de conexión a catastro en LISTA MUNICIPIOS")
            return
        xml = ET.fromstring(xml_txt)
        # print (xml_txt)

        lista_municipios = []

        for muni in xml.iter(u"{http://www.catastro.meh.es/}muni"):
            nm = muni.find(u"{http://www.catastro.meh.es/}nm")
            locat = muni.find(u"{http://www.catastro.meh.es/}locat")
            cd = locat.find(u"{http://www.catastro.meh.es/}cd")
            cmc = locat.find(u"{http://www.catastro.meh.es/}cmc")
            loine = muni.find(u"{http://www.catastro.meh.es/}loine")
            cm = loine.find(u"{http://www.catastro.meh.es/}cm")
            lista_municipios.append(nm.text)
            # print (cmc.text, cm.text, nm.text)
            # print (cd.text,',',cmc.text,',',self.completarCeros(cd.text,2)+self.completarCeros(cmc.text,3),',',cm.text,',',nm.text)

        return lista_municipios

    def getMuniCode(self,nombre_prov, nombre_muni):
        # getMuniCode(self,nombre_prov, nombre_muni)
        #   Devuelve el código catastral del Muhicipio
        #   return codigo_muni

        # url = u'http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/ConsultaMunicipio?'
        url = self.conf.catastro_tool["url_catastro_municipio"]

        params = [
            ('Provincia',nombre_prov.encode("utf-8", errors="ignore")),
            ('Municipio',nombre_muni.encode("utf-8", errors="ignore"))
            ]
        data = urllib.parse.urlencode(params)
        print ('getMuniCode - ', url+data)
        # try:
            # req = urllib.request.urlopen(url+data, timeout=TIMEOUT_SEGUNDOS)
        try:
            response = requests.get(url+data, timeout=TIMEOUT_SEGUNDOS)
            response.raise_for_status()  # Lanza excepción si hay error HTTP (4xx, 5xx)
            response = response.json()  # Esto ya es el JSON parseado
        except urllib.error.URLError as e:
            QApplication.restoreOverrideCursor()
            self.showMessage(u"Error de conexión a internet (fun.getMuniCode)")
            return
        except TimeoutError:
            QApplication.restoreOverrideCursor()
            self.showMessage(u"Timeout: El servidor de Catastro no responde")
            return
        # try:
            # req = urllib.request.urlopen(url+data)
        # except:
            # QApplication.restoreOverrideCursor()
            # self.showMessage(u"Error de conexión a internet (fun.getMuniCode lin:1877)")
            # return

        xml_txt =  response.read()
        xml = ET.fromstring(xml_txt)

        codigo_muni = ''

        #print xml_txt
        for muni in xml.iter(u"{http://www.catastro.meh.es/}muni"):
           if(muni.find(u"{http://www.catastro.meh.es/}nm").text == nombre_muni):
               locat = muni.find(u"{http://www.catastro.meh.es/}locat")
               cmc = locat.find(u"{http://www.catastro.meh.es/}cmc")
               codigo_muni = cmc.text
        return codigo_muni

    def consultaCatastroDATProMunPolPar(self, Provincia, Municipio, Poligono, Parcela):
        #    Obtenemos datos de la parcela con entrada de polígono y parcela
        # http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/Consulta_DNPPP?
        # http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/Consulta_DNPPP?Provincia=CUENCA&Municipio=EL VALLE DE ALTOMIRA&Poligono=27&Parcela=112

        params = [
            ('Provincia', Provincia),
            ('Municipio', Municipio),
            ('Poligono', Poligono),
            ('Parcela', Parcela)
            ]

        url = self.conf.catastro_tool["url_catastro_DNPPP"]
        # url = 'http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/Consulta_DNPPP?'

        data = urllib.parse.urlencode(params)
        print ('consultaCatastroDATPARCELA - ', url+data)
        # try:
            # req = urllib.request.urlopen(url+data, timeout=TIMEOUT_SEGUNDOS)
        try:
            response = requests.get(url+data, timeout=TIMEOUT_SEGUNDOS)
            response.raise_for_status()  # Lanza excepción si hay error HTTP (4xx, 5xx)
            response = response.json()  # Esto ya es el JSON parseado
        except urllib.error.URLError as e:
            QApplication.restoreOverrideCursor()
            self.showMessage(u"Error de conexión a internet (fun.consultaCatastroDATProMunPolPar)")
            return ('ERROR', 'Error de conexión a internet')
        except TimeoutError:
            QApplication.restoreOverrideCursor()
            self.showMessage(u"Timeout: El servidor de Catastro no responde")
            return ('ERROR', 'Timeout: El servidor de Catastro no responde')
        # try:
            # req = urllib.request.urlopen(url+data)
        # except:
            # QApplication.restoreOverrideCursor()
            # self.showMessage(u"Error de conexión a internet (fun.consultaCatastroDATPARCELA lin:3917)")
            # return ('ERROR', 'Error de conexión a internet (fun.consultaCatastroDATPARCELA lin:3917)')

        xml_txt =  response.read()
        xml = ET.fromstring(xml_txt)

        try:
            cuerr = "0"
            for loc in xml.iter(u"{http://www.catastro.meh.es/}control"):
                cuerr = loc.find(u"{http://www.catastro.meh.es/}cuerr").text
        except:
            cuerr = "0"

        print ('cuerr =', cuerr )

        # print ("cuerr:  " + cuerr)
        rclist = []
        if (cuerr != "0"):
            for loc in xml.iter(u"{http://www.catastro.meh.es/}err"):
                cod = loc.find(u"{http://www.catastro.meh.es/}cod").text
                des = loc.find(u"{http://www.catastro.meh.es/}des").text
                message = "ERROR: "+ str(cod)+ "\t" + des
                QApplication.restoreOverrideCursor()
                self.showMessageERR( message,'','Identificador de Catastro' )
            return (u'ERROR' , str(cod)+ "\t" + des)
        else:
            for loc in xml.iter(u"{http://www.catastro.meh.es/}rc"):
                pc1 = loc.find(u"{http://www.catastro.meh.es/}pc1").text
                pc2 = loc.find(u"{http://www.catastro.meh.es/}pc2").text
                car = loc.find(u"{http://www.catastro.meh.es/}car").text
                cc1 = loc.find(u"{http://www.catastro.meh.es/}cc1").text
                cc2 = loc.find(u"{http://www.catastro.meh.es/}cc2").text
                rc = pc1+pc2
                rclist.append(rc)
            return (rclist, 'OK', xml_txt)

    def getPointFromRC(self,iface,rc, mess = 'SI'):
        # Función traida desde jclm_bar_dialog2
        srs =  crsVal
        # print (srs)

        params = [
            ('SRS', 'EPSG:'+ str(srs) ),
            ('RC',rc),
            ('Provincia',''),
            ('Municipio','') ]

        # url = self.conf.general["url_catastro_rc"]
        url = self.conf.catastro_tool["url_catastro_rc"]
        data = urllib.parse.urlencode(params)
        # print ('getPointFromRC - ', url+data)
        # try:
            # req = urllib.request.urlopen(url+data, timeout=TIMEOUT_SEGUNDOS)
        try:
            response = requests.get(url+data, timeout=TIMEOUT_SEGUNDOS)
            response.raise_for_status()  # Lanza excepción si hay error HTTP (4xx, 5xx)
            response = response.json()  # Esto ya es el JSON parseado
        except urllib.error.URLError as e:
            QApplication.restoreOverrideCursor()
            if mess == 'SI':
                self.showMessage(u"Error de conexión a internet (fun.getPointFromRC)")
            return
        except TimeoutError:
            QApplication.restoreOverrideCursor()
            if mess == 'SI':
                self.showMessage(u"Timeout: El servidor de Catastro no responde")
            return
        # try:
            # req = urllib.request.urlopen(url+data, timeout=TIMEOUT_SEGUNDOS)
            # req = urllib.request.urlopen(url+data)
        # except:
            # QApplication.restoreOverrideCursor()
            # if mess == 'SI':
                # self.showMessage(u"Error de conexión a internet (fun.getPointFromRC lin:1931)")
            # return

        xml_txt =  response.read()
        xml = ET.fromstring(xml_txt)

        # print (xml_txt)
        x = None
        y = None
        for elem in xml.iter(u"{http://www.catastro.meh.es/}xcen"):
            x = float(elem.text)
        for elem in xml.iter(u"{http://www.catastro.meh.es/}ycen"):
            y = float(elem.text)
        for elem in xml.iter(u"{http://www.catastro.meh.es/}ldt"):
            ldt = elem.text
        if (x is None or y is None):
            for elem in xml.iter(u"{http://www.catastro.meh.es/}des"):
                error = elem.text
                QApplication.restoreOverrideCursor()
                return ["Error",error]
        else:
            source = osr.SpatialReference()
            source.ImportFromEPSG(srs)
            target_qg = iface.mapCanvas().mapSettings().destinationCrs()
            target_txt = target_qg.authid()
            # print ('target_txt: ', target_txt)
            try:
                target_id = target_txt.split(":")[1]
            except:
                target_id = str(srs)
            # print ('target_id: ', target_id)
            target = osr.SpatialReference()
            target.ImportFromEPSG(int(target_id))

            transform = osr.CoordinateTransformation(source, target)
            point = ogr.Geometry(ogr.wkbPoint)
            point.AddPoint(x,y)
            point.Transform(transform)

            return ["OK",point,ldt]


    """
    ##################################################################################################################
    ###################                 RUTINAS DEL BUSCADOR DE CATASTRO                           ###################
    ##################################################################################################################
    """

    def addRCtoListClicked(self, menu):
        rc = menu.ref_catastral.text().upper()  ## Todo se pone en mayúsculas
        rc = rc.replace(" ", "")                ## Eliminamos espacios
        menu.ref_catastral.setText(rc)

        # Se comprueba si la RC tiene 14 dígitos
        if len(rc)!=14:
            if len(rc)>14:
                rc = rc[:14]
                text = u'LA REFERENCIA CATASTRAL DEBE SER DE 14 POSICIONES\n'
                text+= u' SE TRUNCA A 14 DÍGITOS-  '+rc

        # Se comprueba si la RC existe ya en la lista
        if len(menu.listaRCs.findItems(rc, Qt.MatchExactly)) > 0:
            # print 'Ya existe la RC ', rc
            return

        point = None
        # Esto comprueba la existencia de la referencia catastral
        point_response = self.getPointFromRC(menu.iface,rc)

        if point_response is not None and point_response[0] == "Error":
            self.showMessage(point_response[1])
        elif point_response is not None:
            point = point_response[1]
            ldt =  point_response[2]
        if point is not None:
            puntoData = [point, rc]
            menu.listaRCs.addItem(rc)

            # NUEVO: Actualizar estado de controles
            if hasattr(menu, 'actualizar_estado_controles'):
                menu.actualizar_estado_controles()
        pass

        self.qs.setValue(f"{self.nombre_plugin}/last/lastRC14Select", menu.ref_catastral.text().upper())
        if menu.objectName() == 'herrDP_informes_invasionDPdlg':
            # Se añade numero de parcelas que se van cargando. CASO MENU ANALISIS INVASIÓN
            menu.lblListaREFS.setText(u'Lista de REF CAT (%s)'%(menu.listaRCs.count()))
        else:
            # Se añade numero de parcelas que se van cargando. CASO MENU BUSCADOR CATASTRAL
            menu.lblParCarga.setText(u'(%s)'%(menu.listaRCs.count()))

    def addToListRusticaButtonClicked(self, menu):
        provincia_selected = menu.combo_provincia.currentText()
        # provincia_code = self.getProvinciaCode(provincia_selected)
        municipio_selected = menu.combo_tmuni.currentText()
        # municipio_code = self.getMuniCode(provincia_selected, municipio_selected)
        poligono = menu.poligono.text()
        parcela = menu.parcela.text()

        # Comprobamos si existe la parcela y obtenemos la RC
        result = self.consultaCatastroDATProMunPolPar(provincia_selected, municipio_selected, poligono, parcela)

        if result[0] != 'ERROR':
            rclist = result[0]
        else:
            return

        if len(rclist) > 0:
            listaRefs = ''
            listaRCsPROV = []
            for rc in rclist:
                # Se comprueba si la RC existe ya en la lista
                if len(menu.listaRCs.findItems(rc, Qt.MatchExactly)) > 0:
                    return

                point = None
                point_response = self.getPointFromRC(menu.iface, rc)
                if point_response is not None and point_response[0] == "Error":
                    self.showMessage(point_response[1])
                elif point_response is not None:
                    point = point_response[1]
                    ldt =  point_response[2]
                    listaRefs += rc + ' - ' +ldt + '\n'
                    # print (ldt)
                if point is not None:
                    puntoData = [point, rc]
                    listaRCsPROV.append(rc)

            if len(rclist) > 1:
                ### AQUÍ HABRÍA QUE SELECCIONAR LAS PARCELAS DESEADAS ###
                self.showMessage(listaRefs)

            for rc in listaRCsPROV:
                menu.listaRCs.addItem(rc)

                # NUEVO: Actualizar estado de controles
                if hasattr(menu, 'actualizar_estado_controles'):
                    menu.actualizar_estado_controles()

            self.qs.setValue(f"{self.nombre_plugin}/last/lastProvSelect", menu.combo_provincia.currentText())
            self.qs.setValue(f"{self.nombre_plugin}/last/lastMuniSelect", menu.combo_tmuni.currentText())
            self.qs.setValue(f"{self.nombre_plugin}/last/lastNPOLSelect", menu.poligono.text())
            self.qs.setValue(f"{self.nombre_plugin}/last/lastNPARSelect", menu.parcela.text())

        if menu.objectName() == 'herrDP_informes_invasionDPdlg':
            # Se añade numero de parcelas que se van cargando. CASO MENU ANALISIS INVASIÓN
            menu.lblListaREFS.setText(u'Lista de REF CAT (%s)'%(menu.listaRCs.count()))
        else:
            # Se añade numero de parcelas que se van cargando. CASO MENU BUSCADOR CATASTRAL
            menu.lblParCarga.setText(u'(%s)'%(menu.listaRCs.count()))

    def cargaListRCS(self, iface, nom_layer, srs, lista_rc, mess='SI'):
        # Carga todas las parcelas de la lista de RC y les añade los atributos, hace zoom y cierra el menu
        #   nom_layer - nombre de la capa donde se cargan las parcelas
        #   srs       - Sist. Ref. Coordenadas, Ej:  'EPSG:25830'
        #   lista_rc  - lista de referencias catastrales de 14 digitos

        layerEXIST = QgsProject.instance().mapLayersByName(nom_layer)
        if layerEXIST:
            vl = layerEXIST[0]

        src= 'crs='+ srs.lower()
        bbox = None
        listaParcErr=[]
        textMsgINI = 'CARGANDO PARCELAS CATASTRALES...'+'\n'

        for rc in lista_rc:
            pc1= rc[:7]
            pc2= rc[7:14]
            progress = 'Cargando Parcela %s de %s - %s ...'%(str(lista_rc.index(rc)+1), str(len(lista_rc)), rc)
            iface.mainWindow().statusBar().showMessage(progress)

            # Comprobamos si la parcela ya existe en la capa
            ids = []
            noids = 0
            if layerEXIST:
                # consulta = u'"PCAT1" = \''+pc1+'\' and "PCAT2" = \''+pc2+'\''
                consulta = u'"RC14" = \''+rc+'\''
                expr = QgsExpression( consulta )
                it = vl.getFeatures( QgsFeatureRequest( expr ) )    # Obtiene un iterador de elementos desde una expresión
                for feat in it:
                    noids += 1

            if noids == 0 or not layerEXIST:   ## LA PARCELA NO ESTÁ EN LA LISTA. SE CARGA
                result  = self.getPointFromRC(iface,rc)
                # result1 = self.consultaCatastroDATPARCELA(rc)
                # result1 = self.consultaCatastroDATPARCELA(rc, 'SI')
                result1 = self.consultaCatastroDATPARCELA(rc, mess)

                if result is not None:
                    if result[0] == "Error":
                        continue

                xp = result[0]
                yp = result[1]
                ldt= result[2]

                if result1[:5] == "ERROR":
                    # Recibe error porque no hay Respuesta de catastro -Consulta_DNPRC-
                    message = result1
                    listaSUBP = result1
                    listaCONSTRU = result1
                    QApplication.restoreOverrideCursor()
                    iface.mainWindow().statusBar().clearMessage()

                    supTOTAL =     0            #6 - Superficie de la parcela
                    cp =           ''           #9- Código de la provincia
                    cm =           ''           #10- Código del Municipio
                    cmc =          ''           #11- Código del Municipio
                    tipoPAR =      'X'          #13- Tipo parcela R, U, D, X
                    cpo =          ''           #14- Poligono
                    cpa =          ''           #15- Parcela
                    cv =           ''           #16- Codigo de la via
                    pnp =          ''           #17- Numero de la via
                    np =           ''           #18- Nombre de Provincia
                    nm =           ''           #19- Nombre de Municipio
                    CAT_NMSPC =    'ES.SDGC.CP' #20- nmspc del GML ES.SDGC.CP,  ES.LOCAL.CP
                    # DIRECCION =    ldt          #21- Dato Dirección en catastro
                    PARAJE =       ''           #21- Nombre del Paraje
                    codine = str(cp)+str(cm)

                else:
                    codnomPRO =    result1[1]   #1 - Código y nombre de provincia
                    codnomMUN =    result1[2]   #2 - Código y nombre de municipio
                    message =      result1[3]   #3 - Contador de BI, CONS y SUBP
                    listaSUBP =    result1[4]   #4 - Listado del contenido de los datos de supparcelas
                    listaCONSTRU = result1[5]   #5 - Listado del contenido de los datos de construcciones
                    supTOTAL =     result1[6]   #6 - Superficie de la parcela
                    supCONSTR =    result1[7]   #7 - Superficie construida
                    DATOSURBA =    result1[8]   #8- Datos generales parcela urbana
                    cp =           result1[9]   #9- Código de la provincia
                    cm =           result1[10]  #10- Código del Municipio
                    cmc =          result1[11]  #11- Código del Municipio
                    REFCAT =       result1[12]  #12- REFCAT completa (20 dígitos)
                    tipoPAR =      result1[13]  #13- Tipo parcela R, U, D, X
                    cpo =          result1[14]  #14- Poligono
                    cpa =          result1[15]  #15- Parcela
                    cv =           result1[16]  #16- Codigo de la via
                    pnp =          result1[17]  #17- Numero de la via
                    np =           result1[18]  #18- Nombre de Provincia
                    nm =           result1[19]  #19- Nombre de Municipio
                    CAT_NMSPC =    'ES.SDGC.CP' #20- nmspc del GML ES.SDGC.CP,  ES.LOCAL.CP
                    # DIRECCION =    ldt          #21- Dato Dirección en catastro
                    PARAJE =       result1[21]  #21- Nombre del Paraje
                    codine = str(cp)+str(cm)

                print ('PARAJE:  ',PARAJE)

                #                RC14,            PCAT1,       PCAT2,       EJERCICIO,     NUM_EXP,     CONTROL,     COORY,     VIA,
                #            NUMERO,       NUMERODUP,     NUMSYMBOL,     AREA,    FECHAALTA,     FECHABAJA,     MAPA,     DELEGACIO,
                #            MUNICIPIO,      MASA,        HOJA,      TIPO,      PARCELA,       COORX,     NOM_MUNI,     CAT_NMSPC
                #            DIRECCION       PROVINCIA        REF_CAT            COD_INE

                #                      [rc,        pc1  ,       pc2  ,           0           ,0           ,0         ,yp       ,cv ,
                #                       pnp,             0 ,            0        ,supTOTAL,            0,            0,        0,             cp,
                #                       cmc,       cpo,         pc2,       tipoPAR,           cpa,         xp,            nm,            CAT_NMSPC ]
                atributosDICT={ 'RC14':rc, 'PCAT1':pc1, 'PCAT2':pc2, 'EJERCICIO':0, 'NUM_EXP':0, 'CONTROL':0, 'COORY':yp, 'VIA':cv,
                            'NUMERO':   pnp, 'NUMERODUP':0, 'NUMSYMBOL':0, 'AREA':supTOTAL,'FECHAALTA':0,'FECHABAJA':0, 'MAPA':0, 'DELEGACIO':cp,
                            'MUNICIPIO':cmc,'MASA':cpo , 'HOJA':pc2,'TIPO':tipoPAR, 'PARCELA':cpa, 'COORX':xp, 'NOM_MUNI':nm,'CAT_NMSPC':CAT_NMSPC,
                            'DIRECCION':ldt, 'PROVINCIA':np, 'REF_CAT':REFCAT,  'COD_INE':codine, 'PARAJE':PARAJE
                            }


                # Esta opcion genera o añade las parcelas a una capa unica
                #       llamada 'PARCELAS CATASTRALES'

                # AÑADIR LA PARCELA INDIVIDUAL A LA CAPA
                tipolayer = 'shp'
                MAPA=0
                HOJA='XXXXXX'

                result = self.cargarCapaParcelaCatastral(rc,nom_layer, atributosDICT, 'shp', srs)


                if result == u'ERROR':
                    # La RC no tiene geometría
                    listaParcErr.append(rc)
                    # textMsg = rc.encode("utf-8")+ u' SIN GEOMETRÍA'
                    textMsg = rc.encode("utf-8") + u' SIN GEOMETRÍA'.encode("utf-8")
                    # menu.txeAVISOS.append(textMsg)
                    continue
                newbox = result[3]

                if bbox == None:
                    bbox = newbox
                else:
                    ## DA ERROR LA RC 02074A01909000
                    if(newbox.xMinimum() < bbox.xMinimum()):
                        bbox.setXMinimum(newbox.xMinimum())
                    if(newbox.yMinimum() < bbox.yMinimum()):
                        bbox.setYMinimum(newbox.yMinimum())
                    if(newbox.xMaximum() > bbox.xMaximum()):
                        bbox.setXMaximum(newbox.xMaximum())
                    if(newbox.yMaximum() > bbox.yMaximum()):
                        bbox.setYMaximum(newbox.yMaximum())

            else:
                consulta = u'"RC14" = \''+rc+'\''
                expr = QgsExpression( consulta )
                it = vl.getFeatures( QgsFeatureRequest( expr ) )

                for feat in it:
                    newbox = feat.geometry().boundingBox()
                    if bbox == None:
                        bbox = newbox
                    else:
                        if(newbox.xMinimum() < bbox.xMinimum()):
                            bbox.setXMinimum(newbox.xMinimum())
                        if(newbox.yMinimum() < bbox.yMinimum()):
                            bbox.setYMinimum(newbox.yMinimum())
                        if(newbox.xMaximum() > bbox.xMaximum()):
                            bbox.setXMaximum(newbox.xMaximum())
                        if(newbox.yMaximum() > bbox.yMaximum()):
                            bbox.setYMaximum(newbox.yMaximum())
                    print ('bbox: ', bbox)

        return bbox

    def zoomToCurrentList(self, close, tipoCARGA, menu):
        # Carga todas las parcelas de la lista de RC y les añade los atributos, hace zoom y cierra el menu
            # close - True cierra el 'menu', False no lo cierra
            # tipoCARGA = 'CAPAPAR' # tipoCARGA = 'CAPAPAR' - Carga las parcelas en una capa única
            #             'CAPAIND' # tipoCARGA = 'CAPAIND' - Carga las parcelas en capas individuales
            # menu - el 'menu' de donde viene la funcion

        QApplication.setOverrideCursor(Qt.WaitCursor)

        nom_layer = 'PARCELAS CATASTRALES'

        # Comprobamos si se debe quitar la capa PARCELAS CATASTRALES
        try:
            if menu.chb_EliminarCapa.isChecked():
                print ('BORRANDO CAPA PARCELAS CATASTRALES')
                lyrLIST = QgsProject.instance().mapLayersByName(nom_layer)
                if len(lyrLIST) >0:
                    for lyr in lyrLIST:
                        QgsProject.instance().removeMapLayer(lyr.id())
        except:
            pass

        self.qs.setValue(f"{self.nombre_plugin}/last/lastProvSelect", menu.combo_provincia.currentText())
        self.qs.setValue(f"{self.nombre_plugin}/last/lastMuniSelect", menu.combo_tmuni.currentText())

        current_lista_rc =  [str(menu.listaRCs.item(i).text()) for i in range(menu.listaRCs.count())]
        # print 'current_lista_rc - ', len(current_lista_rc), ' elementos'
        if len(current_lista_rc) < 1:
            QApplication.restoreOverrideCursor()
            self.showMessage("No hay elementos en la lista")
            return

        # Comprobamos si existe la capa
        srs =  menu.iface.mapCanvas().mapSettings().destinationCrs().authid()
        if srs == '' or not srs:
            txt = 'EL PROYECTO NO TIENE NINGUNA PROYECCIÓN\n\nDEBE CONFIGURAR UNA PARA LA CARGA DE PARCELAS'
            QApplication.restoreOverrideCursor()
            self.showMessageERR(txt)
            return

        src= 'crs='+ srs.lower()
        # src= 'crs='+ srs
        # src= 'crs:'+ (srs.lower()).replace(":", "=")
        print ('src lin7252=', src)

        layerEXIST = QgsProject.instance().mapLayersByName(nom_layer)
        if layerEXIST:
            vl = layerEXIST[0]

        layers = []
        geometries = []
        bbox = None

        listaParcErr=[]
        textMsgINI = 'CARGANDO PARCELAS CATASTRALES...'+'\n'

        bbox = self.cargaListRCS(menu.iface ,nom_layer, srs, current_lista_rc)

        if tipoCARGA == 'CAPAIND':
            # Zoom a las capas INDIVIDUALES añadidas
            self.zoomToListLayer(layers,menu.iface)
        else:
            # Zoom a los elementos (parcelas) añadidos
            if bbox is not None:
                ## ERROR CON 02074A01909000
                menu.iface.mapCanvas().zoomToFeatureExtent(bbox)
                menu.iface.mapCanvas().refresh()

            if len(listaParcErr)>0:
                QApplication.restoreOverrideCursor()
                menu.setFixedSize(750, 440)
                menu.btnCargaMasiva.setEnabled(True)
                menu.btnIrCargaMasiva.setEnabled(False)
                menu.combo_tabla.setEnabled(False)
                menu.combo_REFCAT.setEnabled(False)
                text = u'La SEC no devuelve geometría para la(s) parcela(s)\n'
                textMsg = u'%s Parcelas SIN GEOMETRÍA'%str(len(listaParcErr))
                menu.txeAVISOS.append(textMsg)
                for rc in listaParcErr:
                    text += rc +u'\n'
                self.showMessage(text)
                close = False

        if close == True:
            #Cerrar el cuadro de diálogo
            menu.close()

        progress = 'FINALIZADO- %s Parcelas Cargadas'%(str(len(current_lista_rc)))
        menu.iface.mainWindow().statusBar().showMessage(progress)
        QApplication.restoreOverrideCursor()

    def quitarSelectedItemsList(self, menu, tipoMenu):
        # Se borran los elementos seleccionados en la lista de RC
        listItems=menu.listaRCs.selectedItems()
        if not listItems: return

        for item in listItems:
            RC14sel = item.text()
            index = menu.listaRCs.row(item)
            if tipoMenu == 'INF':
                layerPARCnom = 'PARCELAS CATASTRALES'
                if len(QgsProject.instance().mapLayersByName(layerPARCnom))==0:
                    return
                layerPARC = QgsProject.instance().mapLayersByName(layerPARCnom)[0]
                # Se obtiene una lista de los elementos de la capa y crea una capa vacía
                caps = layerPARC.dataProvider().capabilities()
                if caps & QgsVectorDataProvider.DeleteFeatures:
                    dfeats = []
                    featureslayerPARC = layerPARC.getFeatures()

                    for featLayerPARC in featureslayerPARC:      #Cada elemento de la capa PARCELAS. Se llamará featLayerPARC
                        RC14 = featLayerPARC["RC14"]
                        if RC14 == RC14sel:
                            self.showMessage('Borrando RC14')
                            # res = layerPARC.dataProvider().deleteFeatures(featLayerPARC)
                            dfeats.append(featLayerPARC.id())

                    res = layerPARC.dataProvider().deleteFeatures(dfeats)

                    layerPARC.triggerRepaint()
                    layerPARC.updateExtents()

            menu.listaRCs.takeItem(index)

        # NUEVO: Actualizar estado de controles después de quitar
        if hasattr(menu, 'actualizar_estado_controles'):
            menu.actualizar_estado_controles()

        if menu.objectName() == 'herrDP_informes_invasionDPdlg':
            # Se añade numero de parcelas que se van cargando. CASO MENU ANALISIS INVASIÓN
            menu.lblListaREFS.setText(u'Lista de REF CAT (%s)'%(menu.listaRCs.count()))
        else:
            # Se añade numero de parcelas que se van cargando. CASO MENU BUSCADOR CATASTRAL
            menu.lblParCarga.setText(u'(%s)'%(menu.listaRCs.count()))

    def limpiarListaClicked(self, menu):
        # Se borran todos los elementos en la lista de RC
        current_lista_rc =  [str(menu.listaRCs.item(i).text()) for i in range(menu.listaRCs.count())]
        for i in range(len(current_lista_rc)):
            menu.listaRCs.takeItem(0)

        # NUEVO: Actualizar estado de controles después de limpiar
        if hasattr(menu, 'actualizar_estado_controles'):
            menu.actualizar_estado_controles()

        if menu.objectName() == 'herrDP_informes_invasionDPdlg':
            # Se añade numero de parcelas que se van cargando. CASO MENU ANALISIS INVASIÓN
            menu.lblListaREFS.setText(u'Lista de REF CAT (%s)'%(menu.listaRCs.count()))
        else:
            # Se añade numero de parcelas que se van cargando. CASO MENU BUSCADOR CATASTRAL
            menu.lblParCarga.setText(u'(%s)'%(menu.listaRCs.count()))

    def updateCombos(self, menu):
        provincia_selected = menu.combo_provincia.currentText()
        provincia_code = self.getProvinciaCode(provincia_selected)

        provincia_selected = provincia_selected.encode('utf-8', errors='ignore')
        municipios = self.getMunicipiosCatastro(provincia_selected)

        if municipios != 'nocat':
            menu.combo_tmuni.clear()
            menu.combo_tmuni.addItems(municipios)
            lastMuniSelect = self.qs.value(f"{self.nombre_plugin}/last/lastMuniSelect")
            if lastMuniSelect in municipios:
                menu.combo_tmuni.setCurrentIndex(municipios.index(lastMuniSelect))


    """
    ##################################################################################################################
    ##################################################################################################################
    ###################                                                                            ###################
    ###################         RUTINAS DE GESTION DE DATOS EN REGISTRO DE LA PROPIEDAD            ###################
    ###################                                                                            ###################
    ##################################################################################################################
    ##################################################################################################################
    """

    def BUSCRegistro(self, menu):
        # Hace zoom a la parcela REGISTRAL en la web https://geoportal.registradores.org
        ## https://geoportal.registradores.org/idufir/02006000989688

        # 02006000989688

        QApplication.setOverrideCursor(Qt.WaitCursor)

        urlREG = u'https://geoportal.registradores.org/idufir/'

        idufir = menu.idufirREGISTRO.text().replace(" ", "")    ## Eliminamos espacios
        menu.idufirREGISTRO.setText(idufir)
        htmlSalida = urlREG+idufir
        print (htmlSalida)
        webbrowser.open_new(htmlSalida)

        self.qs.setValue(f"{self.nombre_plugin}/last/lastIdufirSelect", idufir)
        # self.qs.setValue(f"{self.nombre_plugin}/last/lastRC14Select", menu.ref_catastral.text().upper())

        QApplication.restoreOverrideCursor()

    def BUSCRegistroCOMP(self, tipoBUSQ, data):
        # Hace zoom a la parcela REGISTRAL en la web https://geoportal.registradores.org
        ## https://geoportal.registradores.org/idufir/02006000989688
        # https://geoportal.registradores.org/idtramite/ID02005200002291
        # https://geoportal.registradores.org/idufir/02005000756030
        # https://geoportal.registradores.org/rfc/7269302WH8876N

        # 02006000989688

        text = u"Si la web 'https://geoportal.registradores.org'\n"
        text+= u"no accede directo a la posición del dato\n\n"
        text+= u"        {} - {}\n\n".format(tipoBUSQ, data)
        text+= u"probablemente no ha sido aun dado de alta\n"
        text+= u"en el geoportal\n\n"
        text+= u"-PRUEBE A USAR SU BUSCADOR-"

        self.showMessage(text)

        QApplication.setOverrideCursor(Qt.WaitCursor)
        urlREG = u'https://geoportal.registradores.org/{}/{}'.format(tipoBUSQ, data)

        htmlSalida = urlREG
        print (htmlSalida)
        webbrowser.open_new(htmlSalida)

        if tipoBUSQ == 'idufir':
            self.qs.setValue(f"{self.nombre_plugin}/last/lastIdufirSelect", idufir)

        QApplication.restoreOverrideCursor()


    """
    ##################################################################################################################
    ##################################################################################################################
    ###################                                                                            ###################
    ###################           RUTINAS DE  EXPTES EXPROPIACIONES Y DOMINO PÚBLICO               ###################
    ###################                                                                            ###################
    ##################################################################################################################
    ##################################################################################################################
    """

    def creaEXPTE(self, menu):
        ## SE CREA EL EXPEDIENTE A PARTIR DE DATOS EXISTENTES EN 'MENU'

        # Directorio de trabajo de Informes de expropiaciones
        dirINFEXPRO = self.qs.value(f"{self.nombre_plugin}/EXPROPIACION/EXPlayerINFOEXPROexptes")
        if dirINFEXPRO is None:
            dirINFEXPRO=configuration().expropiacion["EXPlayerINFOEXPROexptes"]

        #  Datos de expediente y directorios
        Expte = menu.EX_NUMEXPRO.text()
        anoLast = Expte[3:7]
        # print (Expte,anoLast.isnumeric(), Expte[-3:], Expte[-3:].isnumeric(), Expte[:2], len(Expte))
        if not anoLast.isnumeric() or not Expte[-3:].isnumeric() or Expte[:3] != 'EX-' or len(Expte) != 10:
            text = 'El valor de expediente ' + Expte + ' es incorrecto.\n\n'
            text +='Debe ser del tipo EX-AAAAnnn\n'
            text +='    AAAA es el año (p.e. 2020)\n'
            text +='    nnn es el n de expte. (p.e. 023)'
            QApplication.restoreOverrideCursor()
            self.showMessageERR(text,"",tittle=self.nombre_plugin,)
            return ('ERROR')

        dirExpteAno = dirINFEXPRO + u'Año_' + str(anoLast)
        dirExpte = dirExpteAno + u'/' + Expte

        QApplication.restoreOverrideCursor()
        text = u'¿Crear directorio para el expediente - ' + Expte +' ?\n\n'+ dirExpte
        result = self.showMessageYESNO(text, '', self.nombre_plugin)

        if result != 1024:       # Se ha pulsado CANCELAR
            QApplication.restoreOverrideCursor()
            return ('ERROR')
        else:
            QApplication.setOverrideCursor(Qt.WaitCursor)


        # Creación del directorio
        if not os.path.exists(dirExpte) and result == 1024:
            try:
                os.makedirs(dirExpte)
            except:
                QApplication.restoreOverrideCursor()
                text = u'ES IMPOSIBLE CREAR EL DIRECTORIO:\n'+dirExpte
                self.showMessageERR(text,"",tittle=self.nombre_plugin,)
                QApplication.setOverrideCursor(Qt.WaitCursor)
                return ('ERROR')
                pass

        # Creación del fichero de intercambio
        self.creaFICHintercambio(dirExpte, menu)

        return dirExpte

    def creaFICHintercambio(self, dirExpte, menu):
        # Se crea el fichero DE INTERCAMBIO A ACCESS en el directorio del expediente
        listaVAL = []
        listaVAL.append(menu.EX_NUMEXPRO.text()[3:10])                                          # 00 NUMEXPRO;2020033
        # listaVAL.append(self.datoNumVacio(menu.EX_REGISTRO.text()))                             # 01 REGISTRO;79945
        listaVAL.append("'"+self.datoTextVacio(menu.EX_REGISTRO.text())+"'")                    # 01 REGISTRO;79945
        # listaVAL.append("    #"+menu.EX_FECHA.date().toString('dd/MM/yyyy')+"#")                # 02 FECHA; Expte remisión; 01/01/2020
        listaVAL.append("    #"+menu.EX_FECHA.date().toString('MM/dd/yyyy')+"#")                # 02 FECHA; Expte remisión; 01/01/2020
        listaVAL.append("'"+self.datoTextVacio(menu.EX_SOLICITANTE.currentText())+"'")          # 03 SOLICITANTE;FRANCISCO MANGANESO HELIO
        listaVAL.append("'"+self.datoTextVacio(menu.EX_INTERESADO.currentText())+"'")           # 04 INTERESADO;ARTURO SELENIO RUBIDIO
        listaVAL.append("'-'")                                                                  # 05 DNI;123456789
        listaVAL.append("'-'")                                                                  # 06 NOMBRE;HEREDEROS
        listaVAL.append("'-'")                                                                  # 07 DOMICILIO;C/ ELEMENTOS, 27
        listaVAL.append("'-'")                                                                  # 08 CODIGOPOST;02630
        listaVAL.append("'-'")                                                                  # 09 TLFNO;987654321
        listaVAL.append("'-'")                                                                  # 10 POBLACION;BONETE
        listaVAL.append("'"+self.datoTextVacio(menu.EX_CARRETERA.text())+"'")                   # 11 CARRETERA;CM3209
        listaVAL.append(self.datoNumVacio(menu.EX_KILOMETRO.text()))                            # 12 KILOMETRO;0
        listaVAL.append(self.datoNumVacio(menu.EX_KILOMET2.text()))                             # 13 KILOMET2;16124
        listaVAL.append("'"+self.datoTextVacio(menu.EX_MARGEN.currentText())+"'")               # 14 MARGEN;IZQDA
        listaVAL.append("'"+self.datoTextVacio(menu.EX_OBSERVAPK.text())+"'")                   # 15 OBSERVAPK;ESTE ES UN FICHERO DE PRUEBA
        listaVAL.append("'"+self.datoTextVacio(menu.EX_TIPO.toPlainText())+"'")                 # 16 TIPO;Solicitud de comprobación de posible invasión de parcela catastral
        listaVAL.append("'-'")                                                                  # 17 ARCHIVO;PENDIENTE
        listaVAL.append("'"+self.datoTextVacio(self.datoINICIALES(menu.EX_INGENIERO.currentText()))+"'") # 18 IG;ASS
        listaVAL.append("'"+self.datoTextVacio(menu.EX_INGENIERO.currentText())+"'")            # 19 INGENIERO;Agustín Solabre Suarez
        listaVAL.append("'-'")                                                                  # 20 ADMIN;sl
        listaVAL.append("'"+self.datoTextVacio(self.datochbTOSINO(menu.EX_ESTAARCHIVADO))+"'")  # 21 ESTAARCHIVADO;FALSO
        listaVAL.append("'-'")                                                                  # 22 FECHAARCHIVO;02/01/2020
        listaVAL.append("'"+self.datoTextVacio(menu.EX_EXPTE_EXPROPIACION.text())+"'")          # 23 EXPTE_EXPROPIACION;CN-AB-96/115
        listaVAL.append("'"+self.datoTextVacio(menu.EX_EXPTES_RELACIONADOS.text())+"'")         # 24 EXPTES_RELACIONADOS;CN-AB-96/115-M
        listaVAL.append("'"+self.datoTextVacio(menu.EX_NOMBRE_TRAMO.text())+"'")                # 25 NOMBRE_TRAMO;EjeManchuela_Villamalea_A31 (Tramo 2)
        listaVAL.append("'"+self.datoTextVacio(menu.EX_DECR_ACUERDO_RESOLUCION.text())+"'")     # 26 DECR_ACUERDO_RESOLUCION;30-OCTUBRE-06
        listaVAL.append("'"+self.datoTextVacio(menu.EX_ACTAS_PREVIAS.text())+"'")               # 27 ACTAS_PREVIAS;jun-07
        listaVAL.append("'"+self.datoTextVacio(menu.EX_REMISION_CATASTRAL.text())+"'")          # 28 REMISION_CATASTRAL;25/03/2019
        listaVAL.append("'"+self.datoTextVacio(menu.EX_NUMORDEN.text())+"'")                    # 29 NUMORDEN;73-131
        listaVAL.append("'"+self.datoTextVacio(menu.EX_POLIGONO.text())+"'")                    # 30 POLIGONO;4-3
        listaVAL.append("'"+self.datoTextVacio(menu.EX_PARCELAS.text())+"'")                    # 31 PARCELAS;583-376
        listaVAL.append("'"+self.datoTextVacio(menu.EX_TM.text())+"'")                          # 32 TM;BONETE
        listaVAL.append("'"+self.datoTextVacio(menu.EX_TIPO_EXPEDIENTE.currentText())+"'")      # 33 TIPO_EXPEDIENTE;NO INVASION
        listaVAL.append("'-'")                                                                  # 34 FECHAINFORME;02/01/2020
        listaVAL.append("'"+self.datoTextVacio(menu.EX_TITULO_EXPROPIACION.toPlainText())+"'")  # 35 TITULO_EXPROPIACION;ACONDICIONAMIENTO CTRA B-11 (CM-3209), P.K. 0 AL 16,124. MONTEALEGRE-BONETE-ESTACION DE BONETE
        listaVAL.append("'-'")                                                                  # 36 EX_EXPTE_OBRA_RELACIONADO;
        listaVAL.append("'"+self.datoTextVacio(menu.EX_REF_CATASTRAL.text())+"'")               # 37 REF_CATASTRAL;400016BWJ9140S
        # listaVAL.append("    #"+menu.EX_FECHA_ULTIMO_TRAMITE.date().toString('dd/MM/yyyy')+"#") # 38 FECHA_ULTIMO_TRAMITE;04/09/2018
        listaVAL.append("    #"+menu.EX_FECHA_ULTIMO_TRAMITE.date().toString('MM/dd/yyyy')+"#") # 38 FECHA_ULTIMO_TRAMITE;04/09/2018
        listaVAL.append("'"+self.datoTextVacio(menu.EX_TRAMITE_EXPROPIACION.text())+"'")        # 39 TRAMITE_EXPROPIACION;ARCHIVADO
        listaVAL.append("'"+self.datoTextVacio(menu.EX_CORREOELEC.toPlainText())+"'")           # 40 CORREOELEC;COSA@VAINA.ES
        listaVAL.append("'"+self.datoTextVacio(menu.EX_PROTOCOLO_REGISTRO.text())+"'")   # 41 PROTOCOLO;ASUNTO 567

        # Creamos el fichero
        fich_csv = dirExpte + "/" + menu.EX_NUMEXPRO.text() + '.txt'
        target  = codecs.open(fich_csv, 'w+',encoding='mbcs')

        count = 1
        for l in listaVAL:
            if count < len(listaVAL):
                try:
                    target.write(str(l)+',')
                    target.write("\r\n")
                except:
                    target.write(u"'-- DATOS ERRONEOS --',")
                    target.write("\r\n")
            else:
                target.write(str(l))
            count += 1

        target.close()

    # def creaRegInformesExcel(self, archivoXCL, menu):
        # # Comprobamos si existe el excel de destino ## TODO SE QUEDA EN herrDP_informes_invasionDP.py
        # if not os.path.isfile(archivoXCL):
            # print ('NO EXISTE EL FICHERO:\n   '+archivoXCL)

        # else:
            # print ('EXISTE EL FICHERO:\n   '+archivoXCL)

        # ### --------------------------------------------------------------------------------------------------------------------------------------------
        # ### --------------------------------------------------------------------------------------------------------------------------------------------
        # ### --------------------------------------------------------------------------------------------------------------------------------------------
        # ### -------------------------------------   POR AQUÍ    ----------------------------------------------------------------------------------------
        # ### --------------------------------------------------------------------------------------------------------------------------------------------
        # ### --------------------------------------------------------------------------------------------------------------------------------------------
        # pass

    def crea_gmlfile(self, layer_origen, nomCAPA, gml_salida_file, src, menu):
        # Transforma la información de la geometría de una capa al estándar de Catastro en formato GML.
        #   layer_origen:      Capa con la geometría de origen
        #   gml_salida_file:   Dirección del archivo en formato GML a sobreescribir con el resultado
        #   src:               Sistema de Referencia de Coordendas de la capa origen. Según cógigos  EPSG
        #       SRC_DICT=['25828', '25829', '25830', '25831']

        # print ('layer_origen - ', layer_origen)
        # print ('nomCAPA - ', nomCAPA)
        # print ('gml_salida_file - ', gml_salida_file)
        # print ('src - ', src)
        # print ('menu - ', menu)

        # Comprueba que catastroPlantillaGML.py existe en el directorio actual
        try:
            from .catastroPlantillaGML import SRC_DICT, PLANTILLA_1, PLANTILLA_2, PLANTILLA_3, PLANTILLA_4, PLANTILLA_5
        except ImportError:
            sys.exit('ERROR functions3.crea_gmlfile: No se encuentra el script plantilla "catastroPlantillaGML" en el directorio')
            mess= u'ERROR functions3.crea_gmlfile: \nNo se encuentra el script plantilla "catastroPlantillaGML" en el directorio'
            self.showMessageERR( mess)
            return

        if menu != '':
            menu.progressBar.setValue(0)
            menu.lblINFO.show() == True
            menu.lblINFO.setText("")
            localid = menu.lneLOCALID.text()
            ini_localid=int(menu.lneLOCALID_2.text())
        else:
            localid = '[rc14]_{NUM}'
            ini_localid = 1

        layer = layer_origen[0]

        text = (
            # u'<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600; text-decoration: underline;">Generar GML para catastro desde capa de Poligonos</span></p>'+
            # u'<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; text-decoration: underline;"><br /></p>'+
            # u'<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" text-decoration: underline;">DATOS DE ENTRADA:</span></p>'+
            # u'<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600;">CAPA DE ENTRADA:</span></p>'+
            # u'<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">   {}</p>'.format(layer.name())+
            # u'<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:7.8pt; font-weight:600;">SRC:</span><span style=" font-size:7.8pt;"> {}</span></p>'.format(str(src))+
            # u'<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600;">FICHERO GML SALIDA:</span></p>'+
            # u'<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">   {}</p>'.format(gml_salida_file)
            )

        if src not in SRC_DICT:     # Comprueba que el SRC es correcto
            mess= u'ERROR: El código SRC ({}) indicado es incorrecto.'.format(src)
            mess+= u'\n ' + 'Los SRC permitidos son 25828, 25829, 25830 o 25831'
            self.showMessageERR( mess)
            # sys.exit()
            return


        with open(gml_salida_file, 'w') as filegml:
            filegml.writelines(PLANTILLA_1) # Añade el encabezamiento al GML

            nfeat = 0

            if menu != '':
                if menu.chbELEMSELEC.isChecked():
                    feats = layer.selectedFeatures()
                    numfeats = layer.selectedFeatureCount()
                    if numfeats == 0:
                        feats = layer.getFeatures()
                        numfeats = layer.featureCount()
                else:
                    feats = layer.getFeatures()
                    numfeats = layer.featureCount()

                campoNamespace = menu.cbx_campoNMSPC.currentText()
            else:
            ### --------------------------------------------------------------------------------------------------------------------------------------------
            ### --------------------------------------------------------------------------------------------------------------------------------------------
                feats = layer.selectedFeatures()
                numfeats = layer.selectedFeatureCount()
                if numfeats == 0:
                    feats = layer.getFeatures()
                    numfeats = layer.featureCount()

                campoNamespace = 'cat_nmspc'

            ### --------------------------------------------------------------------------------------------------------------------------------------------
            ### --------------------------------------------------------------------------------------------------------------------------------------------
            # print ('localid - ', localid, 'ini_localid - ', ini_localid)
            # text+= u'<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">LOCALID= {} - INI= {}</p>'.format(localid, ini_localid)
            # text+= u'<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">NAMESPACE= {}</p>'.format(campoNamespace)
            # text+= u'<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">TOTAL selec. {} de {} geometría(s).</p>'.format(numfeats, layer.featureCount())
            fracfeats = 0
            if localid.find('[') != -1:
                campoLocalid = localid[localid.find('[')+1:localid.find(']')]

            for feature in feats:
                ### --------------------------------------------------------------------------------------------------------------------------------------------
                # TODO Si renombramos RC n origen, esto no es necesario
                # numidf = self.completarCeros(str(ini_localid),3)
                numidf = self.completarCeros(str(ini_localid),2)
                ### --------------------------------------------------------------------------------------------------------------------------------------------


                attrs = feature.attributes()
                valCampoLocalid = feature[campoLocalid]
                localidf = str(valCampoLocalid)

                valCampoNamespace = feature[campoNamespace]
                nmspcf = str(valCampoNamespace)
                if nmspcf != 'ES.SDGC.CP':
                    nmspcf = 'ES.LOCAL.CP'

                if localid.find('{NUM}')!=-1 and nmspcf == 'ES.LOCAL.CP':   # Solo se numeran las parcelas 'ES.LOCAL.CP'
                    # localidf += '_{NUM}'.format(NUM=numidf)
                    ### --------------------------------------------------------------------------------------------------------------------------------------------
                    # TODO Si renombramos RC n origen, esto no es necesario
                    # localidf = localidf[:14] + '_{NUM}'.format(NUM=numidf)
                    localidf = f'{localidf[:14]}_{numidf}'
                    ### --------------------------------------------------------------------------------------------------------------------------------------------


                if len(localidf) == 14 and nmspcf == 'ES.SDGC.CP':          # Se comprueba si la RC puede ser de 14 caracteres, incluso, si existe
                    pass
                else:                                                       # Si no es RC se asigna   nmspcf = 'ES.LOCAL.CP'
                    nmspcf = 'ES.LOCAL.CP'
                    ini_localid +=1
                # ini_localid +=1

                filegml.writelines(PLANTILLA_2.format(nmspc=nmspcf, localid=localidf)) # Añade el encabezamiento de cada Feature al GML

                geom = feature.geometry()

                if geom is None: continue           # Si es una geometría vacía, se continua

                area = geom.area()
                nfeat += 1
                # text+= u'<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">{} S= {:.4f} m2.</p>'.format(localidf, area)

                filegml.writelines('{:.4f}'.format(area))       # Añade el área al GML
                filegml.writelines(PLANTILLA_3.format(src=src,nmspc=nmspcf,localid=localidf)) # Añade la parte anterior a las coordenadas de cada feature al GML

                if geom.wkbType() == 3:
                    n = self.describe_polygon(feature, localidf, nmspcf, src, filegml)

                elif geom.wkbType() == 6:
                    n = self.describe_multipolygon(feature, localidf, nmspcf, src, filegml)

                if menu != '':
                    prog = 100 * nfeat/numfeats
                    menu.progressBar.setValue(int(prog))

                # text+= u'<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">--Vértices: {}</p>'.format(n)

                filegml.writelines(PLANTILLA_4.format(localidf=localidf,nmspc=nmspcf))     # Añade la parte posterior a las coordenadas de cada feature al GML
                fracfeats += 1/numfeats

            filegml.writelines(PLANTILLA_5)     # Añade el final al GML


        # Carga del GML en la TOC
        if menu != '':
            if menu.chbCARGAGML.isChecked():
                ### --------------------------------------------------------------------------------------------------------------------------------------------
                ### --------------------------------------------------------------------------------------------------------------------------------------------
                ##      REVISAR NOMBRE DE CAPA
                # nomCAPA = localidf = localid.format(NUM='TODAS')
                ### --------------------------------------------------------------------------------------------------------------------------------------------
                ### --------------------------------------------------------------------------------------------------------------------------------------------
                #nomCAPA =  'FICHERO'
                crs = QgsCoordinateReferenceSystem(int(src),QgsCoordinateReferenceSystem.EpsgCrsId)
                layer = QgsVectorLayer(gml_salida_file, nomCAPA+"_GML" , 'ogr')
                layer.setCrs(crs,True)
                QgsProject.instance().addMapLayer(layer, False)
                root = QgsProject.instance().layerTreeRoot()
                nombregrupo="PARCELAS CATASTRALES"
                grupoBUSCAT = root.findGroup(nombregrupo)
                if grupoBUSCAT is None:
                    grupoBUSCAT = root.insertGroup(0, nombregrupo)
                grupoBUSCAT.insertChildNode(0, QgsLayerTreeLayer(layer))
                pass
            menu.close()
        else:
            crs = QgsCoordinateReferenceSystem(int(src),QgsCoordinateReferenceSystem.EpsgCrsId)
            layer = QgsVectorLayer(gml_salida_file, nomCAPA+"_GML" , 'ogr')
            layer.setCrs(crs,True)
            QgsProject.instance().addMapLayer(layer, False)
            root = QgsProject.instance().layerTreeRoot()
            nombregrupo="PARCELAS CATASTRALES"
            grupoBUSCAT = root.findGroup(nombregrupo)
            if grupoBUSCAT is None:
                grupoBUSCAT = root.insertGroup(0, nombregrupo)
            grupoBUSCAT.insertChildNode(0, QgsLayerTreeLayer(layer))

    def describe_polygon(self, feature_polygon, localidf, nmspclocalid, src, filegml):
        geometry_multipolygon = QgsGeometry.fromMultiPolygonXY([feature_polygon.geometry().asPolygon()])
        feature_multipolygon = QgsFeature()
        feature_multipolygon.setGeometry(geometry_multipolygon)
        n = self.describe_multipolygon(feature_multipolygon, localidf, nmspclocalid, src, filegml)
        return n

    def describe_multipolygon(self, feature_multipolygon, localidf, nmspclocalid, src, filegml):
        perimetro = feature_multipolygon.geometry()
        n=0
        poligon =0
        for polygon_1 in range(len(perimetro.asMultiPolygon())):
            poligon +=1
            filegml.writelines('''          <gml:surfaceMember>
            <gml:Surface gml:id="Surface_'''+nmspclocalid+'.'+localidf+'" srsName="urn:ogc:def:crs:EPSG:'+src+'''">
              <gml:patches>
                <gml:PolygonPatch>''')
            # <gml:Surface gml:id="Surface_'''+nmspclocalid+'.'+localidf+'.'+"Polygon_%04d"%(polygon_1+1, )+'" srsName="urn:ogc:def:crs:EPSG'+src+'''">
            filegml.writelines('\n')
            ring=0
            for ring_1 in range(len(perimetro.asMultiPolygon()[polygon_1])):
                ring +=1
                if ring_1==0:
                    filegml.writelines('''                  <gml:exterior>''')
                    filegml.writelines('\n')
                else:
                    filegml.writelines('''                  <gml:interior>''')
                    filegml.writelines('\n')
                points_number = len(perimetro.asMultiPolygon()[polygon_1][ring_1])
                filegml.writelines('''                    <gml:LinearRing>
                      <gml:posList srsDimension="2" count="'''+str(points_number)+'''">'''+'\n')
                for point_1 in range(points_number):
                    n+=1
                    filegml.writelines("{:.2f} {:.2f}".format(perimetro.asMultiPolygon()[polygon_1][ring_1][point_1].x(), perimetro.asMultiPolygon()[polygon_1][ring_1][point_1].y()))
                    if point_1 != points_number-1:
                        filegml.writelines(("   ")+'\n')
                filegml.writelines('''
                      </gml:posList>
                    </gml:LinearRing>
                  ''')
                if ring_1==0:
                    filegml.writelines('''</gml:exterior>''')
                    filegml.writelines('\n')
                else:
                    filegml.writelines('''</gml:interior>''')
                    filegml.writelines('\n')
            filegml.writelines('''                </gml:PolygonPatch>
              </gml:patches>
            </gml:Surface>
          </gml:surfaceMember>''')
            filegml.writelines('\n')
        return n


    """
    ##################################################################################################################
    ##################################################################################################################
    ###################                                                                            ###################
    ###################           RUTINAS            VARIAS                                        ###################
    ###################                                                                            ###################
    ##################################################################################################################
    ##################################################################################################################
    """

    def datoTextVacio(self,dato):
        if dato == '':
            return "-"
        else:
            return dato

    def datoNumVacio(self,dato):
        if dato == '':
            return 0
        else:
            return int(float(dato))

    def datoINICIALES(self, dato):
        if dato != '':
            iniciales = ''
            for word in dato.split():
                iniciales += word[0]
            return iniciales.upper()
        else:
            return '-'

    def datochbTOSINO(self, chb):
        if chb.isChecked():
            return 'SI'
        else:
            return 'NO'

    def wait(self, duration=2.0):
        QApplication.processEvents() # clear current event queue
        time.sleep(duration) # this will block gui updates

    def errorManaging(self, excepcion, msg, mensaje):
        print(excepcion)
        if mensaje == True:
            msg += u'\n\n'+ str(excepcion)
            result = self.showMessage(msg,text2="",tittle=self.nombre_plugin+". Error de CONFIG")

    def uptime_bot(self, url):
        delayer = 60
        counter = 0

        # try:
            # conn = urllib.request.urlopen(url, timeout=TIMEOUT_SEGUNDOS)
        try:
            response = requests.get(url, timeout=TIMEOUT_SEGUNDOS)
            response.raise_for_status()  # Lanza excepción si hay error HTTP (4xx, 5xx)
            response = response.json()  # Esto ya es el JSON parseado
        except urllib.error.HTTPError as e:
            # print(f'HTTPError: {e.code} for {url}')
            return f'HTTPError: {e.code} for {url}'
        except urllib.error.URLError as e:
            # print(f'URLError: {e} for {url}')
            return 'Error de internet'
        except TimeoutError:
            # print(f'Timeout: {url}')
            return 'Timeout'
        else:
            return response
        # try:
            # conn = urllib.request.urlopen(url, timeout=TIMEOUT_SEGUNDOS)
            # # conn = urllib.request.urlopen(url)
        # except urllib.error.HTTPError as e:
            # # Email admin / log
            # print(f'HTTPError: {e.code} for {url}')
            # return f'HTTPError: {e.code} for {url}'
        # except urllib.error.URLError as e:
            # # Email admin / log
            # # print(f'URLError: {e.code} for {url}')
            # return 'Error de internet'
        # else:
            # # Website is up
            # # print(f'{url} is up')
            # return conn

        # # time.sleep(delayer)
        # # counter = counter + 1
        # pass

    def convertTOurl(self, text):
        text = unicode(text.replace(u" ", u"%20" ))
        text = unicode(text.replace(u"(", u"%28" ))
        text = unicode(text.replace(u")", u"%29" ))
        text = unicode(text.replace(u"Ñ", u"%C3%91" ))
        text = unicode(text.replace(u"Á", u"%C3%81" ))
        text = unicode(text.replace(u"É", u"%C3%89" ))
        text = unicode(text.replace(u"Í", u"%C3%8D" ))
        text = unicode(text.replace(u"Ó", u"%C3%93" ))
        text = unicode(text.replace(u"Ú", u"%C3%9A" ))
        text = unicode(text.replace(u"ñ", u"%C3%B1" ))
        text = unicode(text.replace(u"á", u"%C3%A1" ))
        text = unicode(text.replace(u"é", u"%C3%A9" ))
        text = unicode(text.replace(u"í", u"%C3%AD" ))
        text = unicode(text.replace(u"ó", u"%C3%B3" ))
        text = unicode(text.replace(u"ú", u"%C3%BA" ))


        listORIG = ['ñ','Ñ','á','é','í','ó','ú','ü','Ü']
        listDEST = ['%C3%B1','%C3%91','%C3%A1','%C3%A9','%C3%AD','%C3%B3','%C3%BA','%C3%BC','%C3%9C']
        textURL = text
        # print textURL
        return textURL

    def comprobar_directorio_archivo(self, directorio, archivo):
        if self.validar_nombre(directorio) and self.validar_nombre(archivo):
            return True
            print("El nombre del directorio y del archivo son válidos.")
        else:
            text = u"El nombre del directorio y/o del archivo contienen caracteres no permitidos.\n\n"
            text += directorio +'/'+ archivo
            text += u'Solo puede incluir letras, números, guiones bajos, puntos, guiones y espacios'
            print(text)
            self.showMessageERR(text,text2="",tittle=self.nombre_plugin)
            return False

    def comprobarDirectorio(self, filename):
        # Comprobamos que existe el directorio de 'filename' y si no se crea
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

    def validar_nombre(self, nombre):
        # Expresión regular que coincide con caracteres especiales
        patron = re.compile(r'[^\w.-_ ]')  # Excluye letras, números, guiones bajos, puntos, guiones y espacios.
        return not bool(patron.search(nombre))

    def buscaFichUnd(self, listUnd, Fich):
        # La rutina permite buscar el fichero 'Fich' en las diferentes unidades 'listUnd' en el orden de la lista de unidadesº
            # Devueve el path completo con unidad del fichero 'path' y la unidad 'unit'
            # path = buscaFichUnd(['z:', 'u:', 'c:'], '/cartografia/datos_Q/QSIG/GRUPOS_CAPAS/012 EXPRO PATRIMONIO - CASILLAS.qlr')
            # print ('Encontrado en :', path[0])

        # Quitamos a Fich la unidad
        FichCapado = Fich[2:]
        FileNotFind = True
        it =0
        while FileNotFind and it < len(listUnd):
            unit = listUnd[it]
            path = unit + FichCapado
            result = os.path.exists(path)
            if result == True:
                FileNotFind = False
                break
            # print (it, ' No se encuentra :', path)
            it += 1

        if FileNotFind == True:
            return 'Error', 'Error'
        else:
            # print ('Encontrado :', path, unit)
            return path, unit

    def buscaFichDirs(self, listDirs, Fich):
        # La rutina permite buscar el fichero 'Fich' en los diferentes directorios 'listDirs' en el orden de la lista de directoriosº
            # Devueve el path completo con unidad del fichero 'path' y la unidad 'unit'
            # fichEncontrado = buscaFichDirs([
            #                       'z:',
            #                       'u:',
            #                       'c:'],
            #                       '012 EXPRO PATRIMONIO - CASILLAS.qlr')
            # print ('Encontrado en :', path[0])

        # Quitamos a Fich la unidad
        # FichCapado = Fich[2:]
        FileNotFind = True
        it =0
        while FileNotFind and it < len(listDirs):
            dir = listDirs[it]
            path = dir + Fich
            result = os.path.exists(path)
            if result == True:
                FileNotFind = False
                break
            # print (it, ' No se encuentra :', path)
            it += 1

        if FileNotFind == True:
            return 'Error', 'Error'
        else:
            # print ('Encontrado :', path, dir)
            return path, dir


    def getListLayerGPKG(self, file, tipos):
        """
        Rutina que devuelve un listado de las tablas de un GPKG según sus tipos.

        :param file: Ruta al archivo GPKG
        :param tipos: Lista de tipos de geometría a incluir
        :return: Lista de nombres de capas que cumplen el criterio
        """
        listLayers = []
        if not os.path.isfile(file):
            return listLayers

        try:
            from osgeo import ogr
            ds = ogr.Open(file)
            if ds is None:
                return listLayers

            for i in range(ds.GetLayerCount()):
                layer = ds.GetLayerByIndex(i)
                name = layer.GetName()

                # Obtener el primer feature para determinar el tipo
                feature = layer.GetNextFeature()
                layer.ResetReading()

                if feature:
                    geom = feature.GetGeometryRef()
                    if geom:
                        geom_name = geom.GetGeometryName()
                        if geom_name in tipos:
                            listLayers.append(name)
                else:
                    # Capa vacía, intentar obtener tipo de la definición
                    layer_defn = layer.GetLayerDefn()
                    geom_type = layer_defn.GetGeomType()
                    # Mapeo simplificado de tipos OGR a nombres
                    tipo_nombres = {
                        1: 'POINT', 2: 'LINESTRING', 3: 'POLYGON',
                        4: 'MULTIPOINT', 5: 'MULTILINESTRING', 6: 'MULTIPOLYGON'
                    }
                    geom_name = tipo_nombres.get(geom_type, '')
                    if geom_name in tipos:
                        listLayers.append(name)

            ds = None
        except Exception as e:
            print(f"Error al leer GPKG: {e}")

        return listLayers


    # def getListLayerGPKG(self, file, tipos):
        # """
        # Rutina que devuelve un listado de las tablas de un GPKG según sus tipos.
        # """
        # listLayers = []

        # if not os.path.isfile(file):
            # print(f"Archivo no encontrado: {file}")
            # return listLayers

        # try:
            # ds = ogr.Open(file)
            # if ds is None:
                # print(f"No se pudo abrir: {file}")
                # return listLayers

            # for i in range(ds.GetLayerCount()):
                # layer = ds.GetLayerByIndex(i)
                # name = layer.GetName()

                # # Intentar obtener el primer feature para determinar el tipo
                # feature = layer.GetNextFeature()
                # layer.ResetReading()  # Importante: resetear después de GetNextFeature

                # if feature is None:
                    # # Capa vacía - intentar obtener tipo de la definición
                    # geom_type = layer.GetGeomType()
                    # if geom_type != ogr.wkbNone:
                        # # Si es 'all' o el tipo base está en la lista, añadir
                        # if tipos[0] == 'all' or self._tipo_en_lista(geom_type, tipos):
                            # listLayers.append(name)
                # else:
                    # # Capa con features
                    # geom = feature.GetGeometryRef()
                    # if geom is not None:
                        # geom_name = geom.GetGeometryName()
                        # if tipos[0] == 'all' or geom_name in tipos:
                            # listLayers.append(name)

        # except Exception as e:
            # print(f"Error: {e}")

        # return listLayers

    def _tipo_en_lista(self, geom_type, tipos):
        """Helper para verificar tipos OGR."""
        # Mapeo simplificado de tipos OGR a nombres
        tipo_nombres = {
            ogr.wkbPoint: 'POINT',
            ogr.wkbLineString: 'LINESTRING',
            ogr.wkbPolygon: 'POLYGON',
            ogr.wkbMultiPoint: 'MULTIPOINT',
            ogr.wkbMultiLineString: 'MULTILINESTRING',
            ogr.wkbMultiPolygon: 'MULTIPOLYGON',
            ogr.wkbPoint25D: 'POINT25D',
            ogr.wkbLineString25D: 'LINESTRING25D',
            ogr.wkbPolygon25D: 'POLYGON25D',
            ogr.wkbMultiPoint25D: 'MULTIPOINT25D',
            ogr.wkbMultiLineString25D: 'MULTILINESTRING25D',
            ogr.wkbMultiPolygon25D: 'MULTIPOLYGON25D',
        }

        nombre = tipo_nombres.get(geom_type, '')
        return nombre in tipos


    """
    ##################################################################################################################
    ##################################################################################################################
    ######
    ######    RUTINAS DE DATOS DE LAS GEODATABASES
    ######    IDENTIFICACIÓN DE DATOS DE LA GEODATABASE DE CARRETERAS
    ######
    ##################################################################################################################
    ##################################################################################################################
    """

    def getGeomCTRA(self, ctraBUSQ, pk, GDB, GDBCLASS, LAYNOM , LAYTIPE):
        # -----  DATOS DE GEOMETRÍA -----
        # GDB = "U:\SIGCLM\APPJCCM\Datos\sig_reg_ctras_AB.gdb"
        # GDBCLASS = "GEOMETRIA"
        # LAYNOM = "GEOMETRIA"
        # LAYTIPE = "ogr"

        # ctraBUSQ  =  'CM-3203'
        # pk = 17.152        pkBUSQ = str(int(pk))

        pkBUSQ = str(int(pk))
        pkdBUSQ = str(round((pk - int(pk))*100)*10)
        print ('ctraBUSQ=%s pkBUSQ=%s pkdBUSQ=%s pk=%s LAYNOM=%s LAYTIPE=%s'%(ctraBUSQ, pkBUSQ, pkdBUSQ, pk, LAYNOM, LAYTIPE))

        # layerEXIST = QgsMapLayerRegistry.instance().mapLayersByName(LAYNOM)
        layerEXIST = QgsProject.instance().mapLayersByName(LAYNOM)
        if not layerEXIST:
            layer = iface.addVectorLayer(GDB+"|layername="+GDBCLASS, LAYNOM, LAYTIPE)
            estiloCAPA = os.path.join(os.path.dirname(__file__), current_configuration.catastro_tool["dir_estilos_catastro"] + u'/GEOMETRIA_CTRA_TRA.qml')
            layer.loadNamedStyle(estiloCAPA)
            QgsProject.instance().layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(True)

        else:
            # QgsMapLayerRegistry.instance().removeMapLayers(layerEXIST)
            # layer = iface.addVectorLayer(GDB+"|layername="+GDBCLASS, LAYNOM, LAYTIPE)
            layer = layerEXIST[0]
            # iface.legendInterface().setLayerVisible(layer, False)
            QgsProject.instance().layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(True)

        consulta = u'"Carretera" = \''+ctraBUSQ+'\' and "PKHito" = \''+pkBUSQ+'\' and "PKDist" = \''+pkdBUSQ+'\''
        expr = QgsExpression( consulta )
        features = layer.getFeatures( QgsFeatureRequest( expr ) )
        try:
            feat = next(features)
            attrDict = {}
            for field in layer.fields():
                    attrDict[field.name()] = feat[field.name()]
        except:
            attrDict = {}

        return attrDict

    def getGeomCTRA_SHP(self, ctraBUSQ, pk, filSHP, LAYNOM , LAYTIPE):
        pkBUSQ = str(int(pk))
        pkdBUSQ = str(round((pk - int(pk))*100)*10)
        print ('ctraBUSQ=%s pkBUSQ=%s pkdBUSQ=%s pk=%s LAYNOM=%s LAYTIPE=%s'%(ctraBUSQ, pkBUSQ, pkdBUSQ, pk, LAYNOM, LAYTIPE))

        # layerEXIST = QgsMapLayerRegistry.instance().mapLayersByName(LAYNOM)
        layerEXIST = QgsProject.instance().mapLayersByName(LAYNOM)
        if not layerEXIST:
            layer = iface.addVectorLayer( filSHP, LAYNOM, LAYTIPE)
        else:
            # QgsMapLayerRegistry.instance().removeMapLayers(layerEXIST)
            # layer = iface.addVectorLayer( filSHP, LAYNOM, LAYTIPE)
            layer = layerEXIST[0]

        consulta = u'"Carretera" = \''+ctraBUSQ+'\' and "PKHito" = \''+pkBUSQ+'\' and "PKDist" = \''+pkdBUSQ+'\''
        expr = QgsExpression( consulta )
        features = layer.getFeatures( QgsFeatureRequest( expr ) )
        try:
            feat = next(features)
            attrs = feat.attributes()
        except:
            attrs = ['s/d']
        return attrs

    def getAforoCTRA(self, ctraBUSQ, pk, GDB, GDBCLASS, LAYNOM , LAYTIPE):
        # -----  DATOS DE AFOROS -----

        # ctraBUSQ  =  'CM-3203'
        # pk = 17.152        pkBUSQ = str(int(pk))

        pk = str(pk )
        print ('ctraBUSQ=%s pk=%s LAYNOM=%s LAYTIPE=%s'%(ctraBUSQ, pk, LAYNOM, LAYTIPE))

        # layerEXIST = QgsMapLayerRegistry.instance().mapLayersByName(LAYNOM)
        layerEXIST = QgsProject.instance().mapLayersByName(LAYNOM)
        if not layerEXIST:
            layer = iface.addVectorLayer(GDB+"|layername="+GDBCLASS, LAYNOM, LAYTIPE)
            # iface.legendInterface().setLayerVisible(layer, False)
            QgsProject.instance().layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(True)
            estiloCAPA = os.path.join(os.path.dirname(__file__), current_configuration.catastro_tool["dir_estilos_catastro"] + u'/GEOMETRIA_CTRA_TRA.qml')
            # print estiloCAPA
            layer.loadNamedStyle(estiloCAPA)

        else:
            layer = layerEXIST[0]
            # iface.legendInterface().setLayerVisible(layer, False)
            QgsProject.instance().layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(True)
        consulta = u'"Carretera" = \''+ctraBUSQ+'\' and "KMi" <= '+pk+' and "KMf" >= '+pk+''
        expr = QgsExpression( consulta )
        features = layer.getFeatures( QgsFeatureRequest( expr ) )
        try:
            feat = next(features)
            attrs = feat.attributes()
        except:
            attrs = ['s/d']
        return attrs

    def crsString(self, crs):
        crs_string = crs.authid()
        if not crs_string.lower().startswith('epsg'):
            crs_string = 'internal:%s' % crs.srsid()
        return crs_string


    """
    ##################################################################################################################
    ##################################################################################################################
    ###################                                                                            ###################
    ###################               RUTINAS DE DATOS EN -RT- RED DE TRANSPORTES                  ###################
    ###################                                                                            ###################
    ##################################################################################################################
    ##################################################################################################################
    """

    def getPointRT(self, point, iface):
        # Obtener datos del elemento pinchado en la GDB

        pintar='NO'
        urlWMS='https://servicios.idee.es/wms-inspire/transportes?'
        tipo = 'text/xml'
        urlWMSLayer='TN.RoadTransportNetwork.RoadLink'
        result=self.WMSgetFeatureInfo(point, iface, pintar, urlWMS, tipo, urlWMSLayer)

        def parse_xml_to_dict(xml_content):
            # Convierte un XML en un diccionario.
            # :param xml_content: str, contenido XML en formato string.
            # :return: dict, diccionario con los datos del XML.

            tree = ET.ElementTree(ET.fromstring(xml_content))
            root = tree.getroot()

            def element_to_dict(element):
                # Convierte un elemento XML y sus hijos en un diccionario.

                return {
                    child.tag: element_to_dict(child) if list(child) else child.text
                    for child in element
                }

            return element_to_dict(root)

        result_dict = parse_xml_to_dict(result[1])

        xml_data = result[1]

        # Parsear el XML
        tree = ET.fromstring(xml_data)

        # Lista de claves deseadas sin prefijo en dato RT
        desired_keys = [
            'id_unique', 'id_tramo', 'id_vial', 'rotulo', 'tipo_viald', 'clased',
            'ordend', 'titulard', 'tipo_tramod', 'calzadad', 'accesod', 'firmed',
            'ncarrilesd', 'sentidod', 'situaciond', 'estadofisd', 'tipovehicd',
            'geometry',
        ]

        # Lista para almacenar los resultados
        features_list = []

        # Iterar sobre cada featureMember
        for feature_member in tree.findall('.//{*}featureMember'):
            feature_dict = {}
            for key in desired_keys:
                # Buscar las subclaves dentro de featureMember
                element = feature_member.find(f'.//{{*}}{key}')
                if element is not None:
                    feature_dict[key] = element.text
                else:
                    feature_dict[key] = None  # Si no existe, lo dejamos como None

            # Añadir el diccionario del feature a la lista
            features_list.append(feature_dict)

            # Mostrar resultados
            text = 'ELEMENTO SELECCIONADO\n\n'
            for feature in features_list:
                # print("Feature:")
                for key, value in feature.items():  # Usar .items() para iterar sobre clave y valor
                    text += f"  {key}: {value}\n"
                    # print(f"  {key}: {value}")
                # print("-" * 20)  # Separador entre features

            self.showMessage('DATOS RT', text)

        return
        # '''
        # 'id_unique': '20030138479608000000284',
        # 'id_tramo': '20030138479',
        # 'id_vial': '608000000284',
        # 'rotulo': 'CM-3203',
        # 'tipo_viald': 'Carretera',
        # 'clased': 'Carretera convencional',
        # 'ordend': 'Segundo orden',
        # 'titulard': 'Comunidad Autónoma',
        # 'tipo_tramod': 'Troncal',
        # 'calzadad': 'Duplicada o superior',
        # 'accesod': 'Libre',
        # 'firmed': 'Pavimentado',
        # 'ncarrilesd': '2',
        # 'sentidod': 'Único',
        # 'situaciond': 'En superficie',
        # 'estadofisd': 'En servicio',
        # 'tipovehicd': 'Peatón+bici+vehículo',
        # '{http://192.168.192.39:8080/geoserver/geoserver/transportes}
        # geometry': LineString': {'{http://www.opengis.net/gml}
        # coordinates': '597564.85575002,4313908.26880028 597570.95814424,4313990.67427626'}}}
        # '''
