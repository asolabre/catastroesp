# -*- coding: utf-8 -*-
'''
/***************************************************************************
Name:           catastro_generaGMLconst.py

                                 A QGIS plugin
Plugin:     catastroesp - Catastro de España
Purpose:        RUTINA catastro_generaGMLconst.PY IMPORTADA DESDE catastroPlantillaGMLconst.py
        --------------------------------------------------------------------
        begin                : 2017-01-25
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

RUTINA crea_gml IMPORTADA DESDE catastroPlantillaGML.py
---------------------------------------------------------------------------
Autor:    A.Solabre
Fuentes:
    - Marcos Manuel Ortega :: Indavelopers :: DXFPARCELA2GMLCATASTRO (plugin)
    - Andrés V. O. :: SEC4QGIS (plugin)
Descripción:
El script genera el correspondiente fichero GML de construcciones catastrales según las
    especificaciones de Castastro, para la generación del ICUC
Especificaciones:
    https://www.catastro.hacienda.gob.es/ayuda/vga/ayuda_ICUC.htm
Requisistos:
    - Es necesario tener instalado Python y el módulo GDAL
Ejemplos:
    - .\TEMPLATES\EJEMPLO CONSTRUCCIONES CON ANILLO OTRASCONST.gml
'''

from PyQt5.QtWidgets import QDialog, QFileDialog, QDialogButtonBox, QTableWidget, QLabel, QTableWidgetItem, QApplication

from PyQt5.QtGui import QIcon

from PyQt5 import uic
from PyQt5.QtCore import QSettings, Qt, QRect, QUrl
from qgis.core import (Qgis, QgsMessageLog, QgsVectorLayer, QgsMapLayer, QgsApplication, QgsGeometry, QgsFeature,
                QgsCoordinateReferenceSystem, QgsProject, QgsLayerTreeLayer, QgsWkbTypes, QgsExpression, QgsFeatureRequest)
from qgis.gui import QgsDialog, QgsMapTool
import qgis.utils

import sys
import os, codecs
import re


import configparser
import urllib
import requests
from requests.exceptions import Timeout, ConnectionError, RequestException

import json
from time import sleep, gmtime, localtime, strftime, time
from datetime import datetime

## Se intentan cargar las librerías GDAL
try:
    from osgeo import ogr, osr, gdal
except ImportError:
    sys.exit('ERROR: Paquetes GDAL/OGR no encontrados. Compruebe que están instalados correctamente')


from .config import configuration        # CLASE DE CONFIGURACIÓN DE VARIABLES DEL PROGRAMA
from .functions3 import Functions        # CLASE DE CONFIGURACIÓN DE FUNCIONES GENERALES
from .settings import Settings           # CLASE DE CONFIGURACIÓN DE VARIABLES GLOBALES


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), './menus/catastro_generaGMLconst.ui'))

# Constante para el timeout de las peticiones HTTP (segundos)
TIMEOUT_SEGUNDOS = 5

class catastro_generaGMLconst(QDialog, FORM_CLASS):
    
    def __init__(self, iface, parent=None):
        """Constructor de la clase catastro_generaGMLconst"""
        # Clase para el submenu catastro_generaGMLconst.ui

        # Cambiar a cursor de espera al inicio de la inicialización
        QApplication.setOverrideCursor(Qt.WaitCursor)
        
        try:
            super(catastro_generaGMLconst, self).__init__(parent)
            # Se establece el menu de usuario desde el diseñador
            self.setupUi(self)

            self.iface = iface
            self.fun = Functions()
            self.qs = QSettings()
            self.conf = configuration()

            # Obtenemos SRC de la vista del proyecto
            srs = self.iface.mapCanvas().mapSettings().destinationCrs().authid()
            self.srcVal = srs.lower().replace('epsg:','')

            self.nombre_plugin = os.path.basename(os.path.dirname(__file__))
            self.version_plugin = self.get_plugin_version()

            self.setWindowIcon(QIcon(f':/plugins/{self.nombre_plugin}/iconos/cat_gmlConst.jpg'))

            # Cargar ayuda desde archivo HTML externo
            plugin_dir = os.path.dirname(os.path.abspath(__file__))
            help_file = os.path.join(plugin_dir, "help", "catastro_generaGMLconst_help.html")

            if os.path.exists(help_file):
                self.txbAyuda.setSource(QUrl.fromLocalFile(help_file))
            else:
                self.txbAyuda.setHtml(f"<p style='color:red'>Ayuda no disponible: {help_file}</p>")

            # Obtener las capas de la TOC (operación que puede ser lenta)
            lista_CAPAS = self.getCAPAS()
            
            # ACTUALIZA CAMPOS SI CAMBIAS LA TABLA SELECCIONADA
            self.cbxCapaentrada.currentIndexChanged.connect(self.actualizarCampos)

            # Comprueba si hay elementos seleccionados
            self.cbxCapaentrada.currentIndexChanged.connect(self.actualizarEstadoCargaGML)

            self.cbxCapaentrada.clear()
            self.cbxCapaentrada.addItems(lista_CAPAS)

            # Comprobamos si la última capa está en lista_CAPAS y se pone como current en el combo
            lastCapaParaGMLconst = self.qs.value(f"{self.nombre_plugin}/last/lastCapaParaGMLconst")
            if lastCapaParaGMLconst in lista_CAPAS:
                self.cbxCapaentrada.setCurrentIndex(lista_CAPAS.index(lastCapaParaGMLconst))

            # Comprobamos si la capa activa está en lista_CAPAS y se pone como current en el combo
            self.cbxCapaentrada.setCurrentIndex(1)
            if iface.activeLayer():
                if iface.activeLayer().name() in lista_CAPAS:
                    self.cbxCapaentrada.setCurrentText(iface.activeLayer().name())
            self.cbxCapaentrada.setEditable(True)

            self.actualizarEstadoCargaGML()

            self.lastDirGMLconst = self.qs.value(f"{self.nombre_plugin}/last/lastDirGMLconst")
            if self.lastDirGMLconst is None:
                self.lastDirGMLconst = 'C:/temp/fichero.gml'
            self.srcExtORI = '.gml'
            self.lneGMLsalida.setText(self.lastDirGMLconst)

            self.btnGENERAGML.clicked.connect(self.generaGML)
            self.btnCANCELA.clicked.connect(self.cancela)
            self.progressBar.setMinimum(0)
            self.progressBar.setMaximum(100)
            self.btnSeleccionfich.clicked.connect(self.gml_salida_file_click)
            self.btnAsignNomCapa.setEnabled(True)
            self.btnAsignNomCapa.clicked.connect(self.AsignNomCapa)

            #   TABLA DE DATOS DE CONSTRUCCIONES
            self.cbxCTRL_localid_rep.setChecked(False)
            self.tbw_CONSTRUCCIONES.setColumnWidth(0, 50)    # 0 'ID'
            self.tbw_CONSTRUCCIONES.setColumnWidth(1, 100)   # 1 'LOCALID'
            self.tbw_CONSTRUCCIONES.setColumnWidth(2, 100)   # 2 'NAMESPACE'
            self.tbw_CONSTRUCCIONES.setColumnWidth(3, 180)   # 3 'NOM_CONST'
            self.tbw_CONSTRUCCIONES.setColumnWidth(4, 140)   # 4 'USO_CONST'
            self.tbw_CONSTRUCCIONES.setColumnWidth(5, 70)    # 5 'NUMPLANTAS'
            self.tbw_CONSTRUCCIONES.setColumnWidth(6, 140)   # 6 'TIPOCONST'

            # Conectar eventos para actualizar la tabla
            self.cbx_campoLOCALID.currentIndexChanged.connect(self.cargarDatosEnTabla)
            self.cbx_campoNMSPC.currentIndexChanged.connect(self.cargarDatosEnTabla)
            self.cbx_campoNomConst.currentIndexChanged.connect(self.cargarDatosEnTabla)
            self.cbx_campoUso.currentIndexChanged.connect(self.cargarDatosEnTabla)
            self.cbx_campoNumPlantas.currentIndexChanged.connect(self.cargarDatosEnTabla)
            self.cbx_campoTipo.currentIndexChanged.connect(self.cargarDatosEnTabla)
            self.chbELEMSELEC.stateChanged.connect(self.cargarDatosEnTabla)
            
            # Cargar datos iniciales en la tabla
            self.cargarDatosEnTabla()
            
        finally:
            # Restaurar cursor normal cuando termine la inicialización
            QApplication.restoreOverrideCursor()
    
    
    def getCAPAS(self):
        """Obtiene las capas de la vista"""
        capas = []
        for layer in QgsProject.instance().mapLayers().values():
            if layer.type() == QgsMapLayer.VectorLayer:
                if layer.wkbType() == QgsWkbTypes.Polygon:
                    feat=layer.featureCount()
                    featsel=layer.selectedFeatureCount()
                    capas.append(layer.name())
                if layer.wkbType() == QgsWkbTypes.MultiPolygon:
                    feat=layer.featureCount()
                    featsel=layer.selectedFeatureCount()
                    capas.append(layer.name())

        return capas

    def actualizarCampos(self):
        """Actualiza los valores de todos los campos"""
        layername = self.cbxCapaentrada.currentText()
        if layername == "":
            self.fun.showMessage("Debes cargar una capa SHP de POLÍGONOS en la tabla de contenidos")
            return None

        selected_table = self.fun.getLayerByName(layername)
        fields = selected_table.fields()
        text_fields = []
        numeric_fields = []  # Inicializar como lista vacía

        for field in fields:
            if field.typeName().lower() in ["string", "text", "esrifieldtypestring"]:
                text_fields.append(field.name())
            # También añadir campos numéricos para plantas (pueden ser enteros)
            if field.typeName().lower() in ["integer", "integer64", "int", "long", "longlong", "double", "real"]:
                numeric_fields.append(field.name())

        # Colocamos los nombres de campos en los combos
        self.cbx_campoLOCALID.clear()
        self.cbx_campoLOCALID.addItems(text_fields)

        self.cbx_campoNMSPC.clear()
        self.cbx_campoNMSPC.addItems(text_fields)

        self.cbx_campoNomConst.clear()
        self.cbx_campoNomConst.addItems(text_fields)

        self.cbx_campoUso.clear()
        self.cbx_campoUso.addItems(text_fields)

        # Para PLANTAS: combinar text_fields + numeric_fields
        self.cbx_campoNumPlantas.clear()
        all_plantas_fields = text_fields + numeric_fields
        self.cbx_campoNumPlantas.addItems(all_plantas_fields)

        self.cbx_campoTipo.clear()
        self.cbx_campoTipo.addItems(text_fields)

        # Buscamos si existen los campos tipo en la capa (NOMBRES RECOMENDADOS)
        campoLOCALIDtipo = 'LOCALID'
        campoNMSPCtipo   = 'NAMESPACE'
        campoNomConst    = 'NOM_CONST'
        campoUso         = 'USO_CONST'
        campoNumPlantas  = 'NUMPLANTAS'
        campoTipo        = 'TIPOCONST'

        # LOCALID
        if campoLOCALIDtipo in text_fields or campoLOCALIDtipo.lower() in text_fields:
            try:
                self.cbx_campoLOCALID.setCurrentIndex(text_fields.index(campoLOCALIDtipo))
            except:
                self.cbx_campoLOCALID.setCurrentIndex(text_fields.index(campoLOCALIDtipo.lower()))

        # NAMESPACE
        if campoNMSPCtipo in text_fields or campoNMSPCtipo.lower() in text_fields:
            try:
                self.cbx_campoNMSPC.setCurrentIndex(text_fields.index(campoNMSPCtipo))
            except:
                self.cbx_campoNMSPC.setCurrentIndex(text_fields.index(campoNMSPCtipo.lower()))

        # NOMBRE CONSTRUCCIÓN
        if campoNomConst in text_fields or campoNomConst.lower() in text_fields:
            try:
                self.cbx_campoNomConst.setCurrentIndex(text_fields.index(campoNomConst))
            except:
                self.cbx_campoNomConst.setCurrentIndex(text_fields.index(campoNomConst.lower()))

        # USO
        if campoUso in text_fields or campoUso.lower() in text_fields:
            try:
                self.cbx_campoUso.setCurrentIndex(text_fields.index(campoUso))
            except:
                self.cbx_campoUso.setCurrentIndex(text_fields.index(campoUso.lower()))

        # NÚMERO PLANTAS (buscar en la lista combinada)
        if campoNumPlantas in all_plantas_fields or campoNumPlantas.lower() in all_plantas_fields:
            try:
                self.cbx_campoNumPlantas.setCurrentIndex(all_plantas_fields.index(campoNumPlantas))
            except:
                self.cbx_campoNumPlantas.setCurrentIndex(all_plantas_fields.index(campoNumPlantas.lower()))

        # TIPO (para OtherConstruction)
        if campoTipo in text_fields or campoTipo.lower() in text_fields:
            try:
                self.cbx_campoTipo.setCurrentIndex(text_fields.index(campoTipo))
            except:
                self.cbx_campoTipo.setCurrentIndex(text_fields.index(campoTipo.lower()))

        # MODIFICAR NOMBRE DE FICHERO con el nombre de la capa
        srcDir, srcFilExtName = os.path.split(self.lneGMLsalida.text())
        srcFilName, srcExt = os.path.splitext(srcFilExtName)
        if srcFilName.lower() == "prueba" or srcFilName == "":
            resultFiledir = os.path.join(srcDir, layername + srcExt)
            self.lneGMLsalida.setText(resultFiledir)

        # CARGAR DATOS EN LA TABLA después de actualizar campos
        self.cargarDatosEnTabla()

    def actualizarEstadoCargaGML(self):
        """Actualiza el estado de la carga del GML"""
        layer_name = self.cbxCapaentrada.currentText()
        layer = self.fun.getLayerByName(layer_name)

        if not layer or layer.selectedFeatureCount() == 0:
            try:
                self.lblElemSelec.setText(f'0/{layer.featureCount()} Elementos seleccionados ')
            except:
                self.lblElemSelec.setText('0 Elementos seleccionados ')
            self.chbELEMSELEC.setChecked(False)
            self.chbELEMSELEC.setEnabled(False)
        else:
            self.lblElemSelec.setText(f'{layer.selectedFeatureCount()}/{layer.featureCount()} Elementos seleccionados ')
            self.chbELEMSELEC.setChecked(True)
            self.chbELEMSELEC.setEnabled(True)

    def AsignNomCapa(self):
        """Asigna el nombre de la capa"""
        layer_name = self.cbxCapaentrada.currentText().strip()

        # Limpiamos el nombre de caracteres extraños (acentos, barras, etc.)
        layer_name = re.sub(r'[\\/:*?"<>|]', '_', layer_name)

        if not layer_name:
            self.fun.showMessage("No hay ninguna capa seleccionada")
            return

        ruta_actual = self.lneGMLsalida.text().strip()
        if not ruta_actual:
            self.fun.showMessage("No hay una ruta de salida definida")
            return

        # Separar directorio y extensión
        directorio, fichero = os.path.split(ruta_actual)
        _, extension = os.path.splitext(fichero)

        if not extension:
            extension = '.gml'

        # Construir nueva ruta
        nueva_ruta = os.path.join(directorio, f"{layer_name}{extension}")

        self.lneGMLsalida.setText(nueva_ruta)

    def generaGML(self):
        """Metodo principal para generar el archivo GML de construcciones."""
        # Iniciar temporizador
        tiempo_inicio = time()

        gml_salida_file = self.lneGMLsalida.text()
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Comprobamos si el fichero existe
        result = os.path.exists(gml_salida_file)
        if result == True:
            QApplication.restoreOverrideCursor()
            text = u'El fichero %s ya EXISTE - \n\n     ¿QUIERE SOBREESCRIBIRLO?' % (gml_salida_file)
            result = self.fun.showMessWarnYESNO(text, '', 'Catastro Genera GML')

            if result != 1024:  # Se ha pulsado CANCELAR
                QApplication.restoreOverrideCursor()
                return ('ERROR')
            else:
                QApplication.setOverrideCursor(Qt.WaitCursor)

        # Verificar repeticiones si el control está activado
        if self.cbxCTRL_localid_rep.isChecked():
            QApplication.setOverrideCursor(Qt.WaitCursor)
            self.lblINFO.setText("Comprobando repeticiones de LocalID...")
            self.lblINFO.repaint()

            hay_repetidos = self.compruebaIdlocalRepet()

            QApplication.restoreOverrideCursor()

            if hay_repetidos:
                return 'ERROR'

            QApplication.setOverrideCursor(Qt.WaitCursor)
            self.lblINFO.setText("")

        # Creación Fichero y Capa de log
        QgsMessageLog.logMessage("Creando archivo de log GML", "Catastro")
        log_csv = self.conf.lrs["default_log_folder"] + "Log_gml.csv"

        target = codecs.open(log_csv, 'w+', encoding='utf-8')

        encabezado = u'"RC_PARCELA"; "NAMESPACE"; "ERROR_DETECTADO"'
        target.write(encabezado)
        target.write("\n")
        target.close()

        self.qs.setValue(f"{self.nombre_plugin}/last/lastCapaParaGMLconst", self.cbxCapaentrada.currentText())
        self.qs.setValue(f"{self.nombre_plugin}/last/lastDirGMLconst", self.lneGMLsalida.text())

        gmlDir, gmlFilExtName = os.path.split(gml_salida_file)
        gmlFilName, gmlExt = os.path.splitext(gmlFilExtName)
        nomCAPA = str(gmlFilName)

        layer_origen = QgsProject.instance().mapLayersByName(self.cbxCapaentrada.currentText())

        # Pasamos datos a la creación del GML
        self.crea_gml_construcciones(layer_origen, nomCAPA, gml_salida_file, str(self.srcVal), log_csv)

        # Calcular tiempo transcurrido
        tiempo_fin = time()
        tiempo_transcurrido = tiempo_fin - tiempo_inicio

        # Mostrar mensaje en lblINFO
        self.lblINFO.setText(f'INFO: -- TERMINADO -- en {tiempo_transcurrido:.1f} seg.')
        self.lblINFO.repaint()  # Forzar actualización visual

        QApplication.restoreOverrideCursor()

    def crea_gml_construcciones(self, layer_origen, nomCAPA, gml_salida_file, src, log_csv):
        """Genera GML de construcciones a partir de una capa de poligonos"""

        # Importar la plantilla de construcciones
        from .catastroPlantillaGMLconst import catGMLconstv4 as catGML
        self.catGML = catGML

        layer = layer_origen[0]

        # Obtener campos seleccionados en la UI
        campo_localid = self.cbx_campoLOCALID.currentText()
        campo_namespace = self.cbx_campoNMSPC.currentText()
        campo_nombre_const = self.cbx_campoNomConst.currentText()
        campo_uso = self.cbx_campoUso.currentText()
        campo_plantas = self.cbx_campoNumPlantas.currentText()

        # Campo opcional para indicar si es OtherConstruction (piscina, etc.)
        campo_tipo = getattr(self, 'cbx_campoTipo', None)
        if campo_tipo:
            campo_tipo = campo_tipo.currentText()

        DecCoord = self.spbDecCoord.value()
        precision = self.lne_Precision.text()
        fecha = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        # Obtener features a procesar
        if self.chbELEMSELEC.isChecked() and layer.selectedFeatureCount() > 0:
            features = layer.selectedFeatures()
        else:
            features = layer.getFeatures()

        with open(gml_salida_file, 'w', encoding='ISO-8859-1') as filegml:
            # Escribir cabecera
            filegml.write(self.catGML.PLANTILLA_1.format(
                plugin=self.nombre_plugin,
                version=self.version_plugin,
                fecha=fecha
            ))

            nfeat = 0
            total = layer.selectedFeatureCount() if self.chbELEMSELEC.isChecked() else layer.featureCount()

            for feature in features:
                # Obtener valores de atributos
                localid = str(feature[campo_localid]) if feature[campo_localid] else "SIN_ID"
                namespace = str(feature[campo_namespace]) if feature[campo_namespace] else "ES.LOCAL.BU"
                nombre_const = str(feature[campo_nombre_const]) if feature[campo_nombre_const] else "CONSTRUCCION"
                uso_raw = str(feature[campo_uso]) if campo_uso and feature[campo_uso] else "residential"
                plantas = str(feature[campo_plantas]) if campo_plantas and feature[campo_plantas] else "1"

                # Limpiar nombre (eliminar caracteres extraños)
                nombre_const = re.sub(r'[^\w\-_]', '_', nombre_const)

                # Mapear uso al estándar INSPIRE
                uso = self.catGML.USO_MAPPING.get(uso_raw, "residential")

                geom = feature.geometry()
                if not geom or geom.isEmpty():
                    continue

                # Determinar si es Building u OtherConstruction
                es_other = False
                naturaleza = ""
                if campo_tipo and feature[campo_tipo]:
                    tipo_val = str(feature[campo_tipo]).lower()
                    es_other = tipo_val in ["piscina", "deposito", "tendedero", "pista", "OtherConstruction", "otherconstruction"]
                    naturaleza = self.catGML.CONSTRUCTION_NATURE.get(
                        tipo_val.capitalize(), "openAirPool"
                    )

                if es_other:
                    # Generar OtherConstruction (geometría más simple)
                    coords_str = self.geom_to_poslist(geom, DecCoord)
                    filegml.write(self.catGML.PLANTILLA_OTHERCONSTRUCTION.format(
                        namespace=namespace,
                        localid=localid,
                        nombreConst=nombre_const,
                        fecha=fecha,
                        naturaleza=naturaleza,
                        src=src,
                        coordenadas=coords_str
                    ))
                else:
                    # Generar Building (con soporte para huecos/interiores)
                    filegml.write(self.catGML.PLANTILLA_BUILDING_INICIO.format(
                        namespace=namespace,
                        localid=localid,
                        nombreConst=nombre_const,
                        fecha=fecha,
                        uso=uso,
                        src=src
                    ))

                    # Escribir geometría (maneja multipolígono y anillos interiores)
                    self.escribir_geometria_construccion(feature, namespace, localid, nombre_const, src, DecCoord, filegml)

                    filegml.write(self.catGML.PLANTILLA_BUILDING_FIN.format(
                        precision=precision,
                        plantas=plantas
                    ))

                nfeat += 1
                self.progressBar.setValue(int(100 * nfeat / total))

            # Cierre del GML
            filegml.write(self.catGML.PLANTILLA_FIN)

        # Cargar GML en QGIS si está marcado
        if self.chbCARGAGML.isChecked() and nfeat > 0:
            crs = QgsCoordinateReferenceSystem(int(src), QgsCoordinateReferenceSystem.EpsgCrsId)
            layer_gml = QgsVectorLayer(gml_salida_file, f"{nomCAPA}_CONST_GML", 'ogr')
            if layer_gml.isValid():
                layer_gml.setCrs(crs)
                QgsProject.instance().addMapLayer(layer_gml)

    def escribir_geometria_construccion(self, feature, namespace, localid, nombre_const, src, DecCoord, filegml):
        """Escribe la geometria de una construccion soportando MULTIPOLYGON y anillos interiores"""

        geom = feature.geometry()
        wkb_type = geom.wkbType()

        # Convertir a multipolígono si es necesario
        if wkb_type in [QgsWkbTypes.Polygon, QgsWkbTypes.CurvePolygon]:
            geom = QgsGeometry.fromMultiPolygonXY([geom.asPolygon()])

        multipolygon = geom.asMultiPolygon()

        for polygon_idx, polygon in enumerate(multipolygon):
            # Para cada polígono (exterior + interiores)
            for ring_idx, ring in enumerate(polygon):
                # Filtrar nodos duplicados consecutivos (manteniendo cierre)
                puntos_filtrados = self.filtrar_nodos_duplicados(ring, DecCoord)

                # Generar posList
                poslist_str = ""
                for point in puntos_filtrados:
                    poslist_str += f"{point.x():.{DecCoord}f} {point.y():.{DecCoord}f}\n"

                if ring_idx == 0:
                    # Anillo exterior
                    filegml.write(self.catGML.PLANTILLA_GEOMETRY_INICIO.format(
                        namespace=namespace,
                        localid=localid,
                        nombreConst=nombre_const,
                        src=src
                    ))
                    filegml.write(poslist_str)
                    filegml.write(self.catGML.PLANTILLA_GEOMETRY_EXTERIOR_FIN)
                else:
                    # Anillo interior (hueco)
                    filegml.write(self.catGML.PLANTILLA_GEOMETRY_INTERIOR_INICIO)
                    filegml.write(poslist_str)
                    filegml.write(self.catGML.PLANTILLA_GEOMETRY_INTERIOR_FIN)

            filegml.write(self.catGML.PLANTILLA_GEOMETRY_FIN)

    def filtrar_nodos_duplicados(self, ring, DecCoord):
        """Filtra nodos duplicados consecutivos en un anillo, pero mantiene el cierre del poligono"""
        puntos_filtrados = []
        tolerancia = 10 ** (-DecCoord - 1)

        for i, punto in enumerate(ring):
            if i == 0:
                puntos_filtrados.append(punto)
            else:
                punto_anterior = puntos_filtrados[-1]
                if (abs(punto.x() - punto_anterior.x()) > tolerancia or
                    abs(punto.y() - punto_anterior.y()) > tolerancia):
                    puntos_filtrados.append(punto)

        # Verificar cierre del polígono
        # El último punto DEBE ser igual al primero (polígono cerrado)
        if len(puntos_filtrados) > 1:
            primero = puntos_filtrados[0]
            ultimo = puntos_filtrados[-1]
            if (abs(primero.x() - ultimo.x()) <= tolerancia and
                abs(primero.y() - ultimo.y()) <= tolerancia):
                # Ya está cerrado, no hacer nada
                pass
            else:
                # No está cerrado, añadir el primer punto al final
                puntos_filtrados.append(primero)

        return puntos_filtrados

    def geom_to_poslist(self, geom, DecCoord):
        """Convierte una geometria a string posList (para OtherConstruction)"""
        if geom.isMultipart():
            polygon = geom.asMultiPolygon()[0][0]  # Primer anillo del primer polígono
        else:
            polygon = geom.asPolygon()[0]

        puntos_filtrados = self.filtrar_nodos_duplicados(polygon, DecCoord)

        poslist = ""
        for point in puntos_filtrados:
            poslist += f"{point.x():.{DecCoord}f} {point.y():.{DecCoord}f}\n"

        # NOTA: filtrar_nodos_duplicados ya garantiza que el polígono está cerrado
        # No necesitamos añadir el primer punto manualmente

        return poslist.strip()

    def descargaGmlParcCat(self, url, rc, crs):
        """Descarga el GML de una parcela catastral y extrae area y geometria"""
        # Args:
            # url: URL base del servicio WFS
            # rc: Referencia catastral (14 dígitos)
            # crs: Sistema de referencia (ej: 'EPSG:25830')

        # Returns:
            # tuple: (response, areaParcela, geomParcela) o (False, None, None) en caso de error

        srsname = crs.replace( 'EPSG:', 'EPSG::')
        # print ('crs.lower(): ', crs.lower())
        crs= 'crs='+ crs.lower()
        # print ('crs= ', crs)
        epsg = int(crs.replace('crs=epsg:', ''))

        # Construir la URL de consulta
        params = {
            'service': 'wfs',
            'version': '2.0.0',
            'request': 'getfeature',
            'STOREDQUERIE_ID': 'GetParcel',
            'refcat': rc,
            'srsname': srsname
        }

        # Codificar parámetros
        str_values = {}
        for k, v in params.items():
            # str_values[k] = unicode(v).encode('utf-8')
            str_values[k] = str(v).encode('utf-8')
        data = urllib.parse.urlencode(str_values)
        sourceCAPA = url + data

        # Realizar la petición HTTP con timeout
        try:
            response = requests.get(sourceCAPA, timeout=TIMEOUT_SEGUNDOS)
        except Timeout:
            QApplication.restoreOverrideCursor()
            QgsMessageLog.logMessage(f"Timeout al descargar GML para RC: {rc}", "Catastro")
            return 'ERROR', 'ERROR', 'ERROR'
        except ConnectionError:
            QApplication.restoreOverrideCursor()
            QgsMessageLog.logMessage(f"Error de conexión al descargar GML para RC: {rc}", "Catastro")
            return 'ERROR', 'ERROR', 'ERROR'
        except RequestException as e:
            QApplication.restoreOverrideCursor()
            QgsMessageLog.logMessage(f"Error en petición para RC {rc}: {str(e)}", "Catastro")
            return 'ERROR', 'ERROR', 'ERROR'

        destDir = r"c:/Temp/"
        nombreGML = destDir + 'GMLprov.gml'
        with open(nombreGML, 'wb') as file:
            file.write(response.content)
        layer = QgsVectorLayer(nombreGML, rc, 'ogr')
        layer.setCrs(QgsCoordinateReferenceSystem(epsg, QgsCoordinateReferenceSystem.EpsgCrsId))

        # Obtención de valores del GML, area, geometría, centroide
        feats = layer.getFeatures()

        # Contar el número de características manualmente
        feature_count = sum(1 for _ in feats)
        # print ('NUM_FEATURES=',feature_count)

        # Verificar si el número de características es 0
        if feature_count == 0:
            QApplication.restoreOverrideCursor()
            # print ('Error de selección de parcelas')
            # return (u'ERROR ')
            return 'ERROR', 'ERROR', 'ERROR'

        # Se vuelve a generar feats con valores del GML, area, geometría, centroide
        feats = layer.getFeatures()
        areagml = 0
        for feat in feats:
            geomParcela = feat.geometry()
            # print (parcGML.type())
            areagml += geomParcela.area()

        return response, areagml, geomParcela

    def cancela(self):
        """Cancelar"""
        self.close()
        pass

    def get_plugin_version(self):
        """Obtiene la version del plugin desde metadata.txt"""
        fileMetadata = os.path.join(os.path.dirname(__file__), 'metadata.txt')
        if os.path.exists(fileMetadata):
            cfg = configparser.ConfigParser()
            cfg.read(fileMetadata)
            try:
                return cfg.get('general', 'version')
            except:
                return "1.0"
        return "1.0"

    def gml_salida_file_click(self):
        """Cuadro de dialogo de selector de fichero"""
        gml_salida_file= self.lneGMLsalida.text()
        ext = "*.gml"
        filename, tipofile = QFileDialog.getSaveFileName(self, "Fichero GML de salida", gml_salida_file, ext)
        if filename != None and filename != "":
            self.lneGMLsalida.setText(filename)
        else:
            filename = gml_salida_file

        # Comprobamos que existe el directorio y si no, se crea
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

    def compruebaRCorigen(self, rc, featGeom, precis=1):
        """Comprueba si la geometria de featGeom es identica a la descargada de Catastro para una RC dada"""
            # - rc, REF. CATASTRAL a descargar y comparar
            # - featGeom, geometría a incluír en el GML con dicha RC y namespace = 'ES.SDGC.CP'
            # - precis. precisión decimal de compraración, por defecto  1 deciaml
        crs = 'EPSG:25830'
        url = self.conf.catastro_tool["url_catastro_DescGML"]

        # Área de la geometría origen
        areaGML = featGeom.area()

        response, areaParcela, geomParcela = self.descargaGmlParcCat(url, rc, crs)
        
        # Verificar si hubo error en la descarga
        if response == 'ERROR' or areaParcela == 'ERROR' or geomParcela == 'ERROR':
            print(f'Error al descargar la parcela {rc}')
            return 'DISTINTA'

        # Filtro rápido por superficie
        print ('rc:', rc, 'areaGML: ', areaGML, 'areaParcela: ', areaParcela)
        areaGML = float(areaGML)
        precis = int(precis)
        if areaParcela in (None, '', 'ERROR'):
            areaParcela = 0
        else:
            areaParcela = float(areaParcela)

        if round(areaGML, precis) != round(areaParcela, precis):
            return 'DISTINTA'

        # Comprobaciones de seguridad
        if not featGeom or not geomParcela:
            return 'DISTINTA'

        if not featGeom.isGeosValid():
            featGeom = featGeom.makeValid()

        if not geomParcela.isGeosValid():
            geomParcela = geomParcela.makeValid()

        # Intersección geométrica
        inters = featGeom.intersection(geomParcela)

        if inters.isEmpty():
            return 'DISTINTA'

        area_inters = inters.area()

        # Comparación de áreas (primer decimal)
        if (
            round(area_inters, 1) != round(areaGML, precis) or
            round(area_inters, 1) != round(areaParcela, precis)
        ):
            return 'DISTINTA'

        print(f'La parcela {rc} es idéntica a la original de catastro')
        return 'IGUAL'


    def showDialog(self, listaerrorGML, layer, nomCAPA, gml_salida_file, textINFO, tittle="GML CATASTRO"):
        """Se crea un cuadro de dialogo con una serie de rotulos y una tablewidget de tres columnas y N líneas"""
        main_window = self.iface.mainWindow()
        dialog = QgsDialog(main_window,
                           fl=Qt.WindowFlags(),
                           buttons=QDialogButtonBox.NoButton,
                           orientation=Qt.Vertical)
        # dialog.setWindowTitle("LISTADO DE ERRORES EN EL GML - EL FICHERO NO SERÁ VÁLIDO PARA CATASTRO")
        dialog.setWindowTitle("LISTADO DE ERRORES EN EL GML")
        dialog.setWindowIcon(QIcon(f':/plugins/{self.nombre_plugin}/iconos/cat_gmlConst.jpg'))
        dialog.resize(530, 420)

        # Etiquetas
        labeNOMCAPA = QLabel(dialog)
        labeNOMCAPA.setGeometry(QRect(5, 5, 510, 20))
        labeNOMCAPA.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        labeNOMCAPA.setText("CAPA: " + layer.name())
        labeNOMCAPA.setTextInteractionFlags(Qt.TextSelectableByMouse)
        labelLAYER = QLabel(dialog)
        labelLAYER.setGeometry(QRect(15, 25, 500, 30))
        labelLAYER.setWordWrap(True)
        labelLAYER.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        labelLAYER.setText(layer.source())
        labelLAYER.setTextInteractionFlags(Qt.TextSelectableByMouse)
        labelGMLSALIDAFILE = QLabel(dialog)
        labelGMLSALIDAFILE.setGeometry(QRect(5, 45, 510, 20))
        labelGMLSALIDAFILE.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        labelGMLSALIDAFILE.setText("FICHERO SALIDA: " + gml_salida_file)
        labelGMLSALIDAFILE.setTextInteractionFlags(Qt.TextSelectableByMouse)

        labelINFO = QLabel(dialog)
        # Fuente del mensaje de INFO
        font = labelINFO.font()
        font.setBold(True)
        font.setPointSize(int(font.pointSize() * 1.5))
        labelINFO.setFont(font)
        labelINFO.setStyleSheet("color: red;")

        labelINFO.setGeometry(QRect(5, 70, 510, 20))
        labelINFO.setAlignment(Qt.AlignBottom | Qt.AlignCenter)
        labelINFO.setText(textINFO)
        labelINFO.setTextInteractionFlags(Qt.TextSelectableByMouse)


        # Tabla de ERRORES
        tableWidget = QTableWidget(dialog)
        tableWidget.setGeometry(QRect(5, 95, 500, 330))
        tableWidget.setObjectName("tableWidget")
        tableWidget.setColumnCount(3)
        tableWidget.setRowCount(len(listaerrorGML))
        tableWidget.setColumnWidth(0, 140)
        tableWidget.setColumnWidth(1, 100)
        tableWidget.setColumnWidth(2, 240)
        tableWidget.setHorizontalHeaderLabels(['RC PARCELA      ', 'NAMESPACE    ', 'ERROR DETECTADO    '])
        j=0
        for data in listaerrorGML:
            # dataDescomp = data.split(',')
            tableWidget.setItem(j, 0, QTableWidgetItem(data[0]))
            tableWidget.setItem(j, 1, QTableWidgetItem(data[1]))
            tableWidget.setItem(j, 2, QTableWidgetItem(data[2]))
            j+=1

        QApplication.restoreOverrideCursor()
        dialog.show()


    def compruebaIdlocalRepet(self):
        """Comprueba si hay valores repetidos en el campo seleccionado como localid."""
        # Retorna:
            # - False: No hay valores repetidos
            # - True: Hay valores repetidos, y se muestra diálogo con los errores
        
        # Obtener la capa seleccionada
        layer_name = self.cbxCapaentrada.currentText()
        if not layer_name:
            self.fun.showMessage("Debes seleccionar una capa primero")
            return False

        layer = self.fun.getLayerByName(layer_name)
        if not layer:
            self.fun.showMessage("No se pudo cargar la capa seleccionada")
            return False

        # Obtener el campo seleccionado para localid
        campo_localid = self.cbx_campoLOCALID.currentText()
        if not campo_localid:
            self.fun.showMessage("Debes seleccionar un campo para LOCALID")
            return False

        # Obtener namespace si está disponible
        campo_namespace = self.cbx_campoNMSPC.currentText() if self.cbx_campoNMSPC.currentText() else ""

        # Crear diccionario para contar ocurrencias
        conteo_valores = {}

        # Verificar si usar solo elementos seleccionados
        if self.chbELEMSELEC.isChecked() and layer.selectedFeatureCount() > 0:
            features = layer.selectedFeatures()
        else:
            features = layer.getFeatures()

        # Contar ocurrencias de cada valor
        for feature in features:
            valor = feature[campo_localid]
            if valor is None:
                valor = ""  # Tratar valores nulos como string vacío

            valor_str = str(valor)

            if valor_str in conteo_valores:
                conteo_valores[valor_str]["count"] += 1
                conteo_valores[valor_str]["features"].append(feature.id())
            else:
                # Obtener namespace si existe
                namespace_val = ""
                if campo_namespace and campo_namespace in feature.fields().names():
                    namespace_val = feature[campo_namespace] or ""

                conteo_valores[valor_str] = {
                    "count": 1,
                    "features": [feature.id()],
                    "namespace": str(namespace_val) if namespace_val else ""
                }

        # Filtrar solo los valores repetidos
        valores_repetidos = []
        for valor, info in conteo_valores.items():
            if info["count"] > 1:
                # Obtener el namespace (tomar el primero si hay varios)
                namespace_mostrar = info["namespace"] if info["namespace"] else "No definido"

                valores_repetidos.append({
                    "localid": valor,
                    "namespace": namespace_mostrar,
                    "repeticiones": info["count"],
                    "ids_features": info["features"],
                    "mensaje_error": f"Repetido {info['count']} veces"
                })

        # Si hay valores repetidos, mostrar diálogo y retornar True
        if valores_repetidos:
            # Preparar lista para showDialog (formato esperado: (localid, namespace, mensaje_error))
            lista_errores = []
            for error in valores_repetidos:
                lista_errores.append((
                    error["localid"],
                    error["namespace"],
                    error["mensaje_error"]
                ))

            # Mostrar diálogo con errores
            self.close()
            self.showDialog(
                lista_errores,
                layer,
                f"LocalID Repetidos - {layer_name}",
                self.lneGMLsalida.text(),
                "ERROR: Valores de LocalID Repetidos"
            )

            # También escribir en log si es necesario
            log_csv = self.conf.lrs["default_log_folder"] + "Log_repetidos.csv"
            if os.path.exists(os.path.dirname(log_csv)):
                with codecs.open(log_csv, 'w', encoding='utf-8') as target:
                    target.write('"RC_PARCELA"; "NAMESPACE"; "ERROR_DETECTADO"\n')
                    for error in valores_repetidos:
                        linea = f'{error["localid"]};{error["namespace"]};{error["mensaje_error"]}'
                        target.write(linea + "\n")

            return True

        # Si no hay repetidos, retornar False
        return False


    def compruebaRC_gml(self, layer, campoLocalid, valCampoLocalid, valCampoNamespace):
        """Comprobar localid repetidos"""
        # Comprobar si namespace = ES.SDGC.CP  que localid es RC válida
        # Comprobar si namespace = ES.LOCAL.CP que localid no es RC válida

        result = 'OK'

        # Comprobar localid repetidos
        # Si el valor del campo localid es NULL se pone '01'
        if not valCampoLocalid:
            valCampoLocalid = '01'
        consulta = campoLocalid+u' = \''+valCampoLocalid+'\''
        expr = QgsExpression( consulta )
        it = layer.getFeatures( QgsFeatureRequest( expr ) )
        ids = [j.id() for j in it]
        if len(ids) == 1:
            pass
        else:
            result = 'Rep.%s veces'%(str(len(ids)))

        if valCampoNamespace == 'ES.SDGC.CP' or valCampoNamespace == 'ES.SDGC.BU':
            # Comprobar localid namespace = ES.SDGC.CP o  ES.SDGC.BU y 14/20 caracteres
            lenLOCALID = len(valCampoLocalid)
            if lenLOCALID != 14 and lenLOCALID != 20:
                if result == 'OK':
                    result = u'RCmal %s car.'%(str(lenLOCALID))
                else:
                    result += u' / RCmal %s car.'%(str(lenLOCALID))

            # Comprobar localid namespace = ES.SDGC.CP y RC existe
            point_response = self.fun.getPointFromRC(self.iface,valCampoLocalid)

            point = None
            if point_response is not None and point_response[0] == "Error":
                respRC = 'RC no resp'
            elif point_response is not None:
                point = point_response[1]
                ldt =  point_response[2]
            if point is not None:
                respRC = 'OK'
            if respRC != 'OK':
                if result == 'OK':
                    result = respRC
                else:
                    result += u' / '+respRC
        elif valCampoNamespace != 'ES.LOCAL.CP':
            # Caso de NAMESPACE distinto de 'ES.SDGC.CP' o 'ES.LOCAL.CP'
            result = u'NAMESPACE INCORRECTO'

        if not valCampoNamespace:
            valCampoNamespace = 'ES.LOCAL.CP'
            result = u'NAMESPACE NULO'

        return (valCampoLocalid, valCampoNamespace, result)


    def describe_polygon(self, feature_polygon, localidf, nmspclocalid, src, filegml):
        """Descriptor del poligono"""
        geometry_multipolygon = QgsGeometry.fromMultiPolygonXY([feature_polygon.geometry().asPolygon()])
        feature_multipolygon = QgsFeature()
        feature_multipolygon.setGeometry(geometry_multipolygon)
        n, nElim = self.describe_multipolygon(feature_multipolygon, localidf, nmspclocalid, src, filegml)
        return n, nElim


    def describe_multipolygon(self, feature_multipolygon, localidf, nmspclocalid, src, filegml):
        """Descriptor del multipoligono"""
        # PERMITE ELIMINACIÓN DE NODOS REPETIDOS
        perimetro = feature_multipolygon.geometry()
        # Obtener el número de decimales deseado
        DecCoord = self.spbDecCoord.value()
        nElim = 0 # Número nodos repetido eliminados

        n = 0
        poligon = 0
        for polygon_1 in range(len(perimetro.asMultiPolygon())):
            poligon += 1
            filegml.writelines('''                    <gml:surfaceMember>
                            <gml:Surface gml:id="Surface_'''+nmspclocalid+'.'+localidf+'" srsName="urn:ogc:def:crs:EPSG:'+src+'''">
                                <gml:patches>
                                    <gml:PolygonPatch>''')
            filegml.writelines('\n')
            ring = 0
            for ring_1 in range(len(perimetro.asMultiPolygon()[polygon_1])):
                ring += 1
                if ring_1 == 0:
                    filegml.writelines('''                                    <gml:exterior>''')
                    filegml.writelines('\n')
                else:
                    filegml.writelines('''                                    <gml:interior>''')
                    filegml.writelines('\n')

                # Obtener los puntos originales del ring
                puntos_originales = perimetro.asMultiPolygon()[polygon_1][ring_1]

                # FILTRAR NODOS DUPLICADOS CONSECUTIVOS (algoritmo simplificado)
                puntos_filtrados = []

                for i, punto_actual in enumerate(puntos_originales):
                    if i == 0:
                        # Siempre añadir el primer punto
                        puntos_filtrados.append(punto_actual)
                    else:
                        # Comparar con el punto anterior
                        punto_anterior = puntos_filtrados[-1]  # Último punto añadido

                        # Verificar si son diferentes
                        if (abs(punto_actual.x() - punto_anterior.x()) > 10**(-DecCoord-1) or
                            abs(punto_actual.y() - punto_anterior.y()) > 10**(-DecCoord-1)):
                            puntos_filtrados.append(punto_actual)
                        else:
                            # Punto duplicado consecutivo - omitir
                            print(f"Eliminado nodo duplicado: ({punto_actual.x():.{DecCoord}f}, {punto_actual.y():.{DecCoord}f})")
                            nElim += 1

                # VERIFICAR CIERRE DEL POLÍGONO
                # Si el último punto no es igual al primero, añadir el primero al final
                if (len(puntos_filtrados) > 1 and
                    (abs(puntos_filtrados[0].x() - puntos_filtrados[-1].x()) > 10**(-DecCoord-1) or
                     abs(puntos_filtrados[0].y() - puntos_filtrados[-1].y()) > 10**(-DecCoord-1))):
                    puntos_filtrados.append(puntos_filtrados[0])
                    # print(f"Polígono cerrado añadiendo punto inicial")

                points_number = len(puntos_filtrados)

                filegml.writelines('''                                        <gml:LinearRing>
                                                <gml:posList srsDimension="2" count="'''+str(points_number)+'''">'''+'\n')

                # ESCRIBIR PUNTOS FILTRADOS
                for point_1 in range(points_number):
                    n += 1
                    filegml.writelines("{:.{prec}f} {:.{prec}f}".format(
                        puntos_filtrados[point_1].x(),
                        puntos_filtrados[point_1].y(),
                        prec=DecCoord
                    ))

                    if point_1 != points_number - 1:
                        filegml.writelines(("   ") + '\n')

                filegml.writelines('''
                                                </gml:posList>
                                            </gml:LinearRing>''')
                filegml.writelines('\n')
                if ring_1 == 0:
                    filegml.writelines('''                                    </gml:exterior>''')
                    filegml.writelines('\n')
                else:
                    filegml.writelines('''                                    </gml:interior>''')
                    filegml.writelines('\n')
            filegml.writelines('''                                </gml:PolygonPatch>
                                </gml:patches>
                            </gml:Surface>
                        </gml:surfaceMember>''')
            filegml.writelines('\n')
        return n, nElim

    def cargarDatosEnTabla(self):
        """Carga los datos de las construcciones en la tabla tbw_CONSTRUCCIONES"""

        layername = self.cbxCapaentrada.currentText()
        if layername == "":
            self.tbw_CONSTRUCCIONES.setRowCount(0)
            return

        layer = self.fun.getLayerByName(layername)
        if not layer:
            self.tbw_CONSTRUCCIONES.setRowCount(0)
            return

        # Obtener los campos seleccionados
        campo_localid = self.cbx_campoLOCALID.currentText()
        campo_namespace = self.cbx_campoNMSPC.currentText()
        campo_nom_const = self.cbx_campoNomConst.currentText()
        campo_uso = self.cbx_campoUso.currentText()
        campo_plantas = self.cbx_campoNumPlantas.currentText()
        campo_tipo = self.cbx_campoTipo.currentText()

        # Verificar si debemos usar solo elementos seleccionados
        if self.chbELEMSELEC.isChecked() and layer.selectedFeatureCount() > 0:
            features = layer.selectedFeatures()
        else:
            features = layer.getFeatures()

        # Configurar la tabla
        self.tbw_CONSTRUCCIONES.setRowCount(0)
        self.tbw_CONSTRUCCIONES.setColumnCount(7)
        self.tbw_CONSTRUCCIONES.setHorizontalHeaderLabels([
            'Nº', 'LOCALID', 'NAMESPACE', 'NOM_CONST', 'USO_CONST', 'NUMPLANTAS', 'TIPOCONST'
        ])

        # Ajustar anchos de columna
        self.tbw_CONSTRUCCIONES.setColumnWidth(0, 40)   # Nº
        self.tbw_CONSTRUCCIONES.setColumnWidth(1, 140)  # LOCALID
        self.tbw_CONSTRUCCIONES.setColumnWidth(2, 120)  # NAMESPACE
        self.tbw_CONSTRUCCIONES.setColumnWidth(3, 140)  # NOM_CONST
        self.tbw_CONSTRUCCIONES.setColumnWidth(4, 140)  # USO_CONST
        self.tbw_CONSTRUCCIONES.setColumnWidth(5, 80)   # NUMPLANTAS
        self.tbw_CONSTRUCCIONES.setColumnWidth(6, 120)  # TIPOCONST

        row = 0
        for feature in features:
            # Obtener valores
            localid = str(feature[campo_localid]) if campo_localid and feature[campo_localid] else ""
            namespace = str(feature[campo_namespace]) if campo_namespace and feature[campo_namespace] else "ES.LOCAL.BU"
            nom_const = str(feature[campo_nom_const]) if campo_nom_const and feature[campo_nom_const] else ""
            uso = str(feature[campo_uso]) if campo_uso and feature[campo_uso] else ""
            plantas = str(feature[campo_plantas]) if campo_plantas and feature[campo_plantas] is not None else ""
            tipo = str(feature[campo_tipo]) if campo_tipo and feature[campo_tipo] else ""

            # Añadir fila
            self.tbw_CONSTRUCCIONES.insertRow(row)

            self.tbw_CONSTRUCCIONES.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.tbw_CONSTRUCCIONES.setItem(row, 1, QTableWidgetItem(localid))
            self.tbw_CONSTRUCCIONES.setItem(row, 2, QTableWidgetItem(namespace))
            self.tbw_CONSTRUCCIONES.setItem(row, 3, QTableWidgetItem(nom_const))
            self.tbw_CONSTRUCCIONES.setItem(row, 4, QTableWidgetItem(uso))
            self.tbw_CONSTRUCCIONES.setItem(row, 5, QTableWidgetItem(plantas))
            self.tbw_CONSTRUCCIONES.setItem(row, 6, QTableWidgetItem(tipo))

            row += 1

        # Ajustar número total de elementos seleccionados
        self.lblElemSelec.setText(f'{layer.selectedFeatureCount()}/{layer.featureCount()} Elementos seleccionados ')