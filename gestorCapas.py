# -*- coding: utf-8 -*-
"""
/***************************************************************************
 jcml_barDialog
                                 A QGIS plugin
 jcml_bar
                             -------------------
        begin                : 2016-06-06
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Agustín Solabre Suárez/DIRECCIÓN GENERAL DE CARRETERAS
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

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSettings, Qt, QFileInfo
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QApplication, QListWidgetItem
from PyQt5 import uic

from qgis.core import (QgsProject, QgsLayerDefinition, QgsRectangle, QgsMessageLog, QgsCoordinateReferenceSystem,
                        QgsApplication, QgsLayerTreeGroup)
import os
from osgeo import ogr, osr
import urllib
import json
import ast

from time import sleep

from .settings import Settings           # CLASE DE CONFIGURACIÓN DE VARIABLES GLOBALES
from .config import configuration        # CLASE DE CONFIGURACIÓN DE VARIABLES DEL PROGRAMA
from .functions3 import Functions        # CLASE DE CONFIGURACIÓN DE FUNCIONES GENERALES

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), './menus/gestorCapas_base.ui'))

uniProj = QgsProject.instance().fileName()[:2]
class gestorCapas(QDialog, FORM_CLASS):
    """
       INICIO RUTINAS
    """
    def __init__(self, iface,parent=None):
        """Constructor."""
        super(gestorCapas, self).__init__(parent)
        self.setupUi(self)
        self.fun = Functions()
        self.qs = QSettings()
        self.iface = iface;
        self.conf = configuration()
        
        self.nombre_plugin = os.path.basename(os.path.dirname(__file__))

        self.setWindowIcon(QIcon(f':/plugins/{self.nombre_plugin}/iconos/cat_capas_gis.jpg'))
        self.logo.setPixmap(QPixmap(f":/plugins/{self.nombre_plugin}/iconos/logo_general.jpg"))


        # FICHERO DE DATOS DE CAPAS
        # fich_config_capas = u'z:/cartografia/datos_Q/QSIG/config/capasQSIG.txt'

        fich_config_capas = self.qs.value(f"{self.nombre_plugin}/GENERAL/fich_config_capas")
        if fich_config_capas is None:
            fich_config_capas = self.conf.general["fich_config_capas"]

        # Buscamos el fich_config_capas en unidadpropia, Z: U:
        if not os.path.exists(fich_config_capas) or fich_config_capas == os.path.join(os.path.dirname(__file__), './capasQSIG.txt'):
            # uniProj = QgsProject.instance().fileName()[:2]
            listUnd = [uniProj, 'u:', 'z:', 'v:']
            fich_config_capas = u'z:/cartografia/datos_Q/QSIG/config/capasQSIG.txt'
            if self.fun.buscaFichUnd(listUnd, fich_config_capas) is not None:
                fich_config_capas = self.fun.buscaFichUnd(listUnd, fich_config_capas)[0]
                self.qs.setValue(f"{self.nombre_plugin}/GENERAL/fich_config_capas", fich_config_capas)

        # Buscamos el fich_config en la instalación del plugin
        if not os.path.exists(fich_config_capas):
            fich_config_capas = os.path.join(os.path.dirname(__file__), './capasQSIG.txt')


        linesFich = []
        with open(fich_config_capas) as file:
            numlin = 0
            for line in file:
                numlin +=1
                line = line.strip()
                try:
                    res = ast.literal_eval(line)  # Metodo convert a dict ast
                    # if 'nombre' in res:
                    listKeys =  ['type','source','nombre','estilo','grupo','agrupado']
                    flag = 1
                    for key in listKeys:
                        if key not in res:
                            flag = 0
                    if flag == 1: linesFich.append(res)
                    else: print ('LINEA NULA: '+ str(numlin)+line)
                except:
                    print ('LINEA NULA: '+ str(numlin)+line)

        if len(linesFich) == 0:
            text = 'No hay capas correctas en el fichero de configuración\n\n'
            text += fich_config_capas
            self.fun.showMessageERR(text,'',"Error de fichero de CONFIGURACIÓN DE CAPAS")

            ##########################################################################
            ###
            ###   TODO REVISAR ESTO PUES NO FUNCIONA
            ##########################################################################
            self.cancel()

        capas_internas = self.getNombresPosiblesGrupo("Internas", linesFich)

        capas_externas = self.getNombresPosiblesGrupo("Externas", linesFich)

        self.createListCheckbox(capas_internas, self.lwiCheckBoxesINT)
        self.createListCheckbox(capas_externas, self.lwiCheckBoxesEXT)

        self.cargarSelectedButton.clicked.connect(lambda: self.cargarSelected(linesFich))

        self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.cancel)


    def createListCheckbox(self, capas_inicio, listChk):
        for nombreCapa in capas_inicio:
            item = QListWidgetItem(nombreCapa)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            listChk.addItem(item)


    def getNombresPosiblesGrupo(self, grupo, linesFich):
        capas = []
        for capa in linesFich:
            if capa["grupo"] == grupo:
                capas.append(capa["nombre"])
        return capas


    def getCapaByNombre(self, nombre, linesFich):
        for capa in linesFich:
            if capa["nombre"] == nombre:
                return capa
        return None


    def cargarSelected(self, linesFich):
        QApplication.setOverrideCursor(Qt.WaitCursor)

        self.close()
      
        for index in range(0,self.lwiCheckBoxesINT.count()):
            item = self.lwiCheckBoxesINT.item(index)
            if item.checkState() == Qt.Checked:
                nomCAPA = item
            else:
                continue
            nomCAPA =self.getCapaByNombre(item.text(), linesFich)

            if (nomCAPA["type"] != "Grupo"):
                layerEXIST = QgsProject.instance().mapLayersByName(item.text())
                if not layerEXIST:
                    capa = self.getCapaByNombre(item.text(), linesFich)
                    print ('capa: ', capa)
                    self.cargarCapa(capa)

            if (nomCAPA["type"] == "Grupo"):
                root = QgsProject.instance().layerTreeRoot()
                grupoEXIST = root.findGroup(item.text())
                # print ('GRUPO - ',nomCAPA["nombre"],nomCAPA)
                if grupoEXIST is None:
                    self.cargarCapa(nomCAPA)

        for index in range(0,self.lwiCheckBoxesEXT.count()):
            item = self.lwiCheckBoxesEXT.item(index)
            if item.checkState() == Qt.Checked:
                nomCAPA = item
            else:
                continue
            nomCAPA =self.getCapaByNombre(item.text(), linesFich)

            if (nomCAPA["type"] != "Grupo"):
                layerEXIST = QgsProject.instance().mapLayersByName(item.text())
                if not layerEXIST:
                    capa = self.getCapaByNombre(item.text(), linesFich)
                    print ('capa: ', capa)
                    self.cargarCapa(capa)

            if (nomCAPA["type"] == "Grupo"):
                root = QgsProject.instance().layerTreeRoot()
                grupoEXIST = root.findGroup(item.text())
                # print ('GRUPO - ',nomCAPA["nombre"],nomCAPA)
                if grupoEXIST is None:
                    self.cargarCapa(nomCAPA)
                    
        QApplication.restoreOverrideCursor()   


    def cargarCapa(self,data):
        # print (data["type"], data["source"], data["nombre"], data["estilo"], data["grupo"],  data["agrupado"])

        if(data["type"] == "WFS"):
            layer = self.iface.addVectorLayer(data["source"], data["nombre"], data["type"])
            if layer == None:
                QgsMessageLog.logMessage( "Capa no encontrada: " + data["nombre"],self.nombre_plugin)
                return
            elif not layer.isValid():
                QgsMessageLog.logMessage( "Fallo al cargar la capa: " + data["nombre"],self.nombre_plugin)
                return
            else:
                if data["estilo"] != "Default":
                    QgsMessageLog.logMessage( "Cargando capa con estilo no default",self.nombre_plugin)
                    QgsMessageLog.logMessage( os.path.join(os.path.dirname(__file__), self.conf.general["carpeta_estilos"] + u'/' +  data["estilo"]),self.nombre_plugin)
                    layer.loadNamedStyle(os.path.join(os.path.dirname(__file__), self.conf.general["carpeta_estilos"] + u'/' +  data["estilo"]))
            # Ponemos la capa arriba
            root = QgsProject.instance().layerTreeRoot()
            myvl = root.findLayer(layer.id())
            myvlclone = myvl.clone()
            parent = myvl.parent()
            root.insertChildNode(0, myvlclone)
            parent.removeChildNode(myvl)

        elif (data["type"] == "WMS"):
            layer = self.iface.addRasterLayer(data["source"], data["nombre"], 'wms')
            if layer == None:
                QgsMessageLog.logMessage( "Capa no encontrada: " + data["nombre"],self.nombre_plugin)
                return
            elif not layer.isValid():
                QgsMessageLog.logMessage( "Fallo al cargar la capa: " + data["nombre"],self.nombre_plugin)
                return
            else:
                if data["estilo"] != "Default":
                    layer.loadNamedStyle(os.path.join(os.path.dirname(__file__), self.conf.general["carpeta_estilos"] + u'/' +  data["estilo"]))
            # Ponemos la capa arriba
            root = QgsProject.instance().layerTreeRoot()
            myvl = root.findLayer(layer.id())
            myvlclone = myvl.clone()
            parent = myvl.parent()
            root.insertChildNode(0, myvlclone)
            parent.removeChildNode(myvl)

        elif(data["type"] == "JSON"):
            layer = self.iface.addVectorLayer(data["source"], data["nombre"], "ogr")
            if layer == None:
                QgsMessageLog.logMessage( "Capa no encontrada: " + data["nombre"],self.nombre_plugin)
                return
            elif not layer.isValid():
                QgsMessageLog.logMessage( "Fallo al cargar la capa: " + data["nombre"],self.nombre_plugin)
                return
            else:
                if data["estilo"] != "Default":
                    QgsMessageLog.logMessage( "Cargando capa con estilo no default",self.nombre_plugin)
                    QgsMessageLog.logMessage( os.path.join(os.path.dirname(__file__), self.conf.general["carpeta_estilos"] + u'/' +  data["estilo"]),self.nombre_plugin)
                    layer.loadNamedStyle(os.path.join(os.path.dirname(__file__), self.conf.general["carpeta_estilos"] + u'/' +  data["estilo"]))
            # Ponemos la capa arriba
            root = QgsProject.instance().layerTreeRoot()
            myvl = root.findLayer(layer.id())
            myvlclone = myvl.clone()
            parent = myvl.parent()
            root.insertChildNode(0, myvlclone)
            parent.removeChildNode(myvl)

        elif (data["type"] == "SHP"):
            # listUnd = ['v:', 'u:', 'z:','w:']
            listUnd = [uniProj,  'v:', 'u:', 'z:', 'w:']
            fichResul = self.fun.buscaFichUnd(listUnd, data["source"])
            # layer = self.iface.addVectorLayer(data["source"], data["nombre"], "ogr")
            if fichResul is not None:
                layer = self.iface.addVectorLayer(fichResul[0], data["nombre"], "ogr")
            else:
                layer == None
            if layer == None:
                QgsMessageLog.logMessage( "Capa no encontrada: " + data["nombre"],self.nombre_plugin)
                return
            elif not layer.isValid():
                QgsMessageLog.logMessage( "Fallo al cargar la capa: " + data["nombre"],self.nombre_plugin)
                return
            else:
                if data["estilo"] != "Default":
                    layer.loadNamedStyle(os.path.join(os.path.dirname(__file__), self.conf.general["carpeta_estilos"] + u'/' +  data["estilo"]))
            # Ponemos la capa arriba
            root = QgsProject.instance().layerTreeRoot()
            myvl = root.findLayer(layer.id())
            myvlclone = myvl.clone()
            parent = myvl.parent()
            root.insertChildNode(0, myvlclone)
            parent.removeChildNode(myvl)

        elif (data["type"] == "Raster"):
            # listUnd = ['v:', 'u:', 'z:']
            listUnd = [uniProj,  'v:', 'u:', 'z:', 'w:']
            fichResul = self.fun.buscaFichUnd(listUnd, data["source"])
            #layer = self.iface.addRasterLayer(data["source"], data["nombre"])
            layer = self.iface.addRasterLayer(fichResul[0], data["nombre"])
            if layer == None:
                QgsMessageLog.logMessage( "Capa no encontrada: " + data["nombre"],self.nombre_plugin)
                return
            elif not layer.isValid():
                QgsMessageLog.logMessage( "Fallo al cargar la capa: " + data["nombre"],self.nombre_plugin)
                return
            else:
                if data["estilo"] != "Default":
                    layer.loadNamedStyle(os.path.join(os.path.dirname(__file__), self.conf.general["carpeta_estilos"] + u'/' +  data["estilo"]))
            # Ponemos la capa arriba
            root = QgsProject.instance().layerTreeRoot()
            myvl = root.findLayer(layer.id())
            myvlclone = myvl.clone()
            parent = myvl.parent()
            root.insertChildNode(0, myvlclone)
            parent.removeChildNode(myvl)

        elif (data["type"] == "Grupo"):

            listUnd = [uniProj, 'v:', 'u:', 'z:', 'w:']
            fichResul = self.fun.buscaFichUnd(listUnd, data["source"])

            ruta_qlr = None

            # 1️⃣ Si se encuentra por buscaFichUnd
            if fichResul is not None and len(fichResul) > 0 and os.path.isfile(fichResul[0]):
                ruta_qlr = fichResul[0]

            else:
                # 2️⃣ Buscar en el directorio del plugin GRUPOS_CAPAS
                nombre_fichero = os.path.basename(data["source"])
                
                fileGrupo = f"python/plugins/{self.nombre_plugin}/GRUPOS_CAPAS/"+nombre_fichero
                dirPYTJCCM = QgsApplication.qgisSettingsDirPath()
                fichPYTGrupo = os.path.normpath(os.path.join(os.path.dirname(dirPYTJCCM), fileGrupo))
                
                # ruta_plugin = f'./plugins/{self.nombre_plugin}/GRUPOS_CAPAS/{nombre_fichero}'

                if os.path.isfile(fichPYTGrupo):
                    ruta_qlr = fichPYTGrupo

            # 3️⃣ Si no se ha encontrado en ningún sitio
            if not ruta_qlr:
                text = (
                    "Fichero de GRUPO no encontrado:\n"
                    f"{data['nombre']}\n\n"
                    f"{data['source']}"
                )
                self.fun.showMessageERR(text, '', "Error de fichero de GRUPO")
                return

            # 4️⃣ Cargar el grupo
            root = QgsProject.instance().layerTreeRoot()
            result = QgsLayerDefinition().loadLayerDefinition(
                ruta_qlr,
                QgsProject.instance(),
                root
            )

            if not result or result[0] is False:
                QgsMessageLog.logMessage(
                    "Fallo al cargar el GRUPO: " + data["nombre"],
                    self.nombre_plugin
                )
                return

            QgsMessageLog.logMessage(
                "Grupo cargado: " + ruta_qlr,
                self.nombre_plugin
            )

            # 5️⃣ Mover el grupo al inicio de la TOC
            ultimo_grupo = root.children()[-1]

            if isinstance(ultimo_grupo, QgsLayerTreeGroup):
                root.insertChildNode(0, ultimo_grupo.clone())
                root.removeChildNode(ultimo_grupo)


    def cancel(self):
        self.reject()