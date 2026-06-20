# -*- coding: utf-8 -*-
'''
/***************************************************************************
Name:           catastro_generaGML.py

                                 A QGIS plugin
Plugin:     catastroesp - Catastro de España
Purpose:        RUTINA crea_gml. IMPORTADA DESDE catastroPlantillaGML.py
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
Autor en origen:
Patricio Soriano :: SIGdeletras.com
Adaptada:
    A.Solabre
Fuentes:
    - Marcos Manuel Ortega :: Indavelopers :: DXFPARCELA2GMLCATASTRO (plugin)
    - Andrés V. O. :: SEC4QGIS (plugin)
Descripción:
El script genera el correspondiente fichero GML de las parcelas catastrales según las
    especificaciones de Castastro.
Especificaciones:
    - http://www.catastro.minhap.gob.es/esp/formatos_intercambio.asp
Requisistos:
    - Es necesario tener instalado Python y el módulo GDAL
Ejemplos:
    - python dxfgmlcatastro.py archivocad.dxf gmlsalida.gml 25831
'''

from PyQt5.QtWidgets import QDialog, QFileDialog, QDialogButtonBox, QTableWidget, QLabel, QTableWidgetItem, QApplication

from PyQt5.QtGui import QIcon

from PyQt5 import uic
from PyQt5.QtCore import QSettings, Qt, QRect

from qgis.core import (Qgis, QgsMessageLog, QgsVectorLayer, QgsMapLayer, QgsApplication, QgsGeometry, QgsFeature, QgsCoordinateReferenceSystem, QgsProject,
                QgsLayerTreeLayer, QgsWkbTypes, QgsExpression, QgsFeatureRequest)
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
from time import sleep, gmtime, localtime, strftime
from datetime import datetime

## Se intentan cargar las librerías GDAL
try:
    from osgeo import ogr, osr, gdal
except ImportError:
    sys.exit('ERROR: Paquetes GDAL/OGR no encontrados. Compruebe que están instalados correctamente')


from .config import configuration        # CLASE DE CONFIGURACIÓN DE VARIABLES DEL PROGRAMA
from .functions3 import Functions        # CLASE DE CONFIGURACIÓN DE FUNCIONES GENERALES
from .settings import Settings           # CLASE DE CONFIGURACIÓN DE VARIABLES GLOBALES



### IMPORTADO parcialmente de dxfparcela2gmlcatastro.py ###

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), './menus/catastro_generaGML.ui'))

# Constante para el timeout de las peticiones HTTP (segundos)
TIMEOUT_SEGUNDOS = 5

# class herrExpro_generaGML(QDialog, FORM_CLASS):
class catastro_generaGML(QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
    # Clase para el submenu catastro_generaGML.ui

        """Constructor."""
        # super(herrExpro_generaGML, self).__init__(parent)
        super(catastro_generaGML, self).__init__(parent)
        # Se establece el menu de usuario desde el diseñador
        #   Después de ejecutar 'setupUI', puedes acceder a cualquier objeto del diseño haciendo
        #   self.<objectname>, y puedes usar slots de autoconexión - ver
        #    http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        #    #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.iface = iface
        self.fun = Functions()
        self.qs = QSettings()
        self.conf = configuration()

        self.nombre_plugin = os.path.basename(os.path.dirname(__file__))

        # Obtenemos SRC de la vista del proyecto
        srs =  self.iface.mapCanvas().mapSettings().destinationCrs().authid()
        self.srcVal= srs.lower().replace('epsg:','')

        self.setWindowIcon(QIcon(f':/plugins/{self.nombre_plugin}/iconos/cat_gml.jpg'))

        lista_CAPAS = self.getCAPAS()
        # ACTUALIZA CAMPOS SI CAMBIAS LA TABLA SELECCIONADA
        self.cbxCapaentrada.currentIndexChanged.connect(self.actualizarCampos)

        # Comprueba si hay elementos seleccionados
        self.cbxCapaentrada.currentIndexChanged.connect(self.actualizarEstadoCargaGML)

        self.cbxCapaentrada.clear()
        self.cbxCapaentrada.addItems(lista_CAPAS)

        # Comprobamos si la última capa está en lista_CAPAS y se pone como current en el combo
        lastCapaParaGML = self.qs.value(f"{self.nombre_plugin}/last/lastCapaParaGML")
        if lastCapaParaGML in lista_CAPAS:
            self.cbxCapaentrada.setCurrentIndex(lista_CAPAS.index(lastCapaParaGML))

        # Comprobamos si la capa activa está en lista_CAPAS y se pone como current en el combo
        self.cbxCapaentrada.setCurrentIndex(1)
        if iface.activeLayer():
            if iface.activeLayer().name() in lista_CAPAS:
                self.cbxCapaentrada.setCurrentText(iface.activeLayer().name())
        self.cbxCapaentrada.setEditable(True)

        self.actualizarEstadoCargaGML()

        self.lastDirGML = self.qs.value(f"{self.nombre_plugin}/last/lastDirGML")
        if self.lastDirGML is None:
            self.lastDirGML = 'C:/temp/fichero.gml'
        self.srcExtORI = '.gml'
        self.lneGMLsalida.setText(self.lastDirGML)

        self.btnGENERAGML.clicked.connect(self.generaGML)
        self.btnCANCELA.clicked.connect(self.cancela)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.btnSeleccionfich.clicked.connect(self.gml_salida_file_click)
        self.cbxCTRL_localid_rep.setChecked(True)
        self.cbxCTRL_RRCC_identicas.setChecked(True)
        self.btnAsignNomCapa.setEnabled(True)
        self.btnAsignNomCapa.setGeometry(140, 85, 230, 25)
        self.btnAsignNomCapa.clicked.connect(self.AsignNomCapa)

        self.btnAsignDatExptExpro.hide()
        self.cbxCTRL_3.hide()
        self.cbxCTRL_4.hide()
        self.cbxCTRL_5.hide()


    def getCAPAS(self):
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
        layername = self.cbxCapaentrada.currentText()
        if layername == "":
            self.fun.showMessage("Debes cargar una capa SHP de POLÍGONOS en la tabla de contenidos")
            return None
        selected_table = self.fun.getLayerByName(layername)
        fields = selected_table.fields()
        text_fields = []
        numeric_fields = [""]
        for field in fields:
            if field.typeName().lower() in ["string", "text", "esrifieldtypestring"]:
                text_fields.append(field.name())

        # Colocamos los nombres de campos en los combos
        self.cbx_campoLOCALID.clear()
        self.cbx_campoLOCALID.addItems(text_fields)

        self.cbx_campoNMSPC.clear()
        self.cbx_campoNMSPC.addItems(text_fields)

        # Buscamos si existen los campos tipo en la capa
        campoLOCALIDtipo = 'RC14'
        campoNMSPCtipo   = 'CAT_NMSPC'
        if campoLOCALIDtipo in text_fields or campoLOCALIDtipo.lower() in text_fields:
            try:
                self.cbx_campoLOCALID.setCurrentIndex(text_fields.index(campoLOCALIDtipo))
            except:
                self.cbx_campoLOCALID.setCurrentIndex(text_fields.index(campoLOCALIDtipo.lower()))
        if campoNMSPCtipo in text_fields or campoNMSPCtipo.lower() in text_fields:
            try:
                self.cbx_campoNMSPC.setCurrentIndex(text_fields.index(campoNMSPCtipo))
            except:
                self.cbx_campoNMSPC.setCurrentIndex(text_fields.index(campoNMSPCtipo.lower()))

        # MODIFICAR NOMBRE DE FICHERO
        srcDir, srcFilExtName = os.path.split(self.lneGMLsalida.text())
        srcFilName, srcExt = os.path.splitext(srcFilExtName)
        resultFiledir = srcDir+'/'+layername+srcExt
        self.lneGMLsalida.setText(resultFiledir)

        # MODIFICAR NOMBRE DE FICHERO AL DEL INFORME SELECCIONADO
        self.layerINFEXPnom = self.qs.value(f"{self.nombre_plugin}/EXPROPIACION/EXPlayerINFOEXPRO")
        # print ('layerINFEXPnom=', self.layerINFEXPnom, 'layername=', layername)
        if self.layerINFEXPnom is not None:
            if layername == self.layerINFEXPnom:
                mess= u'Se debe poner el directorio y nombre del GML'
                pass

    def actualizarEstadoCargaGML(self):
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
        gml_salida_file= self.lneGMLsalida.text()
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Comprobamos si el fichero existe
        result = os.path.exists(gml_salida_file)
        if result == True:
            QApplication.restoreOverrideCursor()
            text = u'El fichero %s ya EXISTE - \n\n     ¿QUIERE SOBREESCRIBIRLO?'%(gml_salida_file)
            result = self.fun.showMessWarnYESNO(text, '', 'Catastro Genera GML')

            if result != 1024:       # Se ha pulsado CANCELAR
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
        QgsMessageLog.logMessage( "Creando archivo de log GML","Catastro")
        log_csv = self.conf.lrs["default_log_folder"] + "Log_gml.csv"

        target  = codecs.open(log_csv, 'w+',encoding='utf-8')

        encabezado = u'"RC_PARCELA"; "NAMESPACE"; "ERROR_DETECTADO"'
        target.write(encabezado)
        target.write("\n")
        target.close()

        self.qs.setValue(f"{self.nombre_plugin}/last/lastCapaParaGML", self.cbxCapaentrada.currentText())
        self.qs.setValue(f"{self.nombre_plugin}/last/lastDirGML", self.lneGMLsalida.text())

        gmlDir, gmlFilExtName = os.path.split(gml_salida_file)
        gmlFilName, gmlExt = os.path.splitext(gmlFilExtName)
        nomCAPA = str(gmlFilName)

        layer_origen = QgsProject.instance().mapLayersByName(self.cbxCapaentrada.currentText())
        # src='25830'

        # Pasamos datos a la creación del GML
        self.crea_gml(layer_origen, nomCAPA, gml_salida_file, str(self.srcVal), log_csv)

        QApplication.restoreOverrideCursor()


    def descargaGmlParcCat(self, url, rc, crs):
        """
        Descarga el GML de una parcela catastral y extrae área y geometría

        Args:
            url: URL base del servicio WFS
            rc: Referencia catastral (14 dígitos)
            crs: Sistema de referencia (ej: 'EPSG:25830')

        Returns:
            tuple: (response, areaParcela, geomParcela) o (False, None, None) en caso de error
        """

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
            str_values[k] = unicode(v).encode('utf-8')
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


    def descargaGmlParcCatANT(self, url, rc, srsname):
        """
        Método antiguo de descarga de GML (mantenido por compatibilidad)
        """
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
        sourceCAPA = url + data
        print (url + data)

        try:
            response = requests.get(sourceCAPA, timeout=TIMEOUT_SEGUNDOS)
            return response
        except Timeout:
            message = "ERROR: Timeout - La petición excedió el tiempo de espera"
            QApplication.restoreOverrideCursor()
            QgsMessageLog.logMessage(message, "Catastro")
            return False
        except ConnectionError:
            message = "ERROR: Problema de conexión con el servidor"
            QApplication.restoreOverrideCursor()
            QgsMessageLog.logMessage(message, "Catastro")
            return False
        except RequestException as e:
            message = f"ERROR: Problema en la petición - {str(e)}"
            QApplication.restoreOverrideCursor()
            QgsMessageLog.logMessage(message, "Catastro")
            return False


    def cancela(self):
        self.close()
        pass


    def gml_salida_file_click(self):
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


    def crea_gml(self, layer_origen, nomCAPA, gml_salida_file, src, log_csv):
        # Transforma la información de la geometría de una capa al estándar de Catastro en formato GML.
        #   layer_origen:      Capa con la geometría de origen
        #   gml_salida_file:   Dirección del archivo en formato GML a sobreescribir con el resultado
        #   src:               Sistema de Referencia de Coordendas de la capa origen. Según cógigos  EPSG
        #   log_csv:           Capa de fichero log de resultados

        ## Definiciones principales
        layer = layer_origen[0]
        campoLocalid = self.cbx_campoLOCALID.currentText()  # Detección de campo LOCALID
        campoNamespace = self.cbx_campoNMSPC.currentText()  # Detección de campo NAMESPACE

        DecArea = self.spbDecArea.value()       # Decimales para el valor de area
        DecCoord = self.spbDecCoord.value()     # Decimales para las coordenadas

        # Se identifica si usar plantilla v3 o v4
        if self.rbtGMLV3.isChecked():
            self.versionGML = 'v3'
            from .catastroPlantillaGML import catGMLv3 as catGML
        else:
            self.versionGML = 'v4'
            from .catastroPlantillaGML import catGMLv4 as catGML
        # print ('VersionGML: ',self.versionGML)
        self.catGML=catGML

        ## Inicializando progress y lblINFO
        self.progressBar.setValue(0)
        self.lblINFO.show() == True
        self.lblINFO.setText("")

        ## Se obtiene la versión del plugin y fecha
        fileMetadata = os.path.join(os.path.dirname(__file__), 'metadata.txt')
        cfg = configparser.ConfigParser()
        cfg.read(fileMetadata)
        fecha = datetime.fromtimestamp(os.path.getmtime(fileMetadata)).strftime("%Y-%m-%dT%H:%M:%S")
        version = cfg.get('general', 'version')

        # Comprueba que el SRC es correcto
        if src not in self.catGML.SRC_DICT:
            mess= u'ERROR: El código SRC ({}) indicado es incorrecto.'.format(src)
            mess+= u'\n ' + 'Los SRC permitidos son 25828, 25829, 25830 o 25831'
            self.fun.showMessageERR( mess)
            return

        with open(gml_salida_file, 'w') as filegml:
            ## Obtenemos el número de features a meter en GML
            if self.chbELEMSELEC.isChecked():
                feats = layer.selectedFeatures()
                numfeats = layer.selectedFeatureCount()
                if numfeats == 0:
                    feats = layer.getFeatures()
                    numfeats = layer.featureCount()
            else:
                feats = layer.getFeatures()
                numfeats = layer.featureCount()

            ## Se escribe PLANTILLA_1. Encabezados y versión del plugin
            filegml.writelines(self.catGML.PLANTILLA_1.format(version=version, fecha=fecha, numfeats=numfeats, versGML=self.versionGML))      # Añade el encabezamiento al GML

            nfeat = 0

            fracfeats = 0

            errorGML = False
            listaerrorGML = []
            for feature in feats:

                attrs = feature.attributes()
                valCampoLocalid = feature[campoLocalid]
                if valCampoLocalid:
                    localidf = str(valCampoLocalid)
                else:
                    localidf = '01'

                valCampoNamespace = feature[campoNamespace]
                if not valCampoNamespace:
                    valCampoNamespace = 'ES.LOCAL.CP'


                # Comprobamos si la RC es válida y no repetida
                respRC = self.compruebaRC_gml(layer, campoLocalid, valCampoLocalid, valCampoNamespace)

                respRcOrigen = ''
                # Comprobamos si la parcela es idéntica a la original
                if self.cbxCTRL_RRCC_identicas.isChecked():
                    url = self.conf.catastro_tool["url_catastro_DescGML"]
                    respRcOrigen = self.compruebaRCorigen(localidf, feature.geometry())

                nmspcf = str(valCampoNamespace)
                geom = feature.geometry()

                if respRC[2] != 'OK' or  respRcOrigen == 'IGUAL':
                    # Verificar si respRC[0] ya existe en el primer elemento de alguna lista
                    existe = any(respRC[0] == error[0] for error in listaerrorGML)

                    if not existe:
                        errorGML = True
                        ## escribir linea en log
                        target = codecs.open(log_csv, 'a', encoding='utf-8')
                        # linea = u'' + localidf + ';' + nmspcf + ';' + respRC[2]
                        if respRcOrigen == 'IGUAL':
                            linea = u'' + localidf + ';' + nmspcf + ';Idéntica. No se incluye en GML'
                            listaerrorGML.append([valCampoLocalid,valCampoNamespace,'Idéntica. No se incluye en GML'])
                        else:
                            linea = u'' + localidf + ';' + nmspcf + ';' + respRC[2]
                            listaerrorGML.append(respRC)
                        target.write(linea)
                        target.write("\n")
                        target.close()

                if self.cbxCTRL_RRCC_identicas.isChecked() and respRcOrigen == 'IGUAL':
                    continue

                # Si es un NAMESPACE incorrecto, se continua
                if nmspcf != 'ES.SDGC.CP' and  nmspcf != 'ES.SDGC.BU' and  nmspcf != 'ES.LOCAL.CP': continue

                # Si es una geometría vacía, se continua
                if geom is None: continue

                # Se comprueba si la RC puede ser de 14 caracteres, incluso, si existe
                if len(localidf) == 14 and (nmspcf == 'ES.SDGC.CP' and nmspcf == 'ES.SDGC.BU'):
                    pass
                else:
                    # Si no es RC (nmspcf == 'ES.SDGC.CP' o  'ES.SDGC.BU') se asigna nmspcf = 'ES.LOCAL.CP'
                    nmspcf = 'ES.LOCAL.CP'

                area = round(geom.area(), DecArea)
                nfeat += 1

                # Se escribe PLANTILLA_2. Encabezamiento de cada Feature al GML
                filegml.writelines(self.catGML.PLANTILLA_2.format(area=str(area), nmspc=nmspcf, localid=localidf, src=src))

                if geom.wkbType() == 3:
                    n, nElim = self.describe_polygon(feature, localidf, nmspcf, src, filegml)

                elif geom.wkbType() == 6:
                    n, nElim = self.describe_multipolygon(feature, localidf, nmspcf, src, filegml)

                if nElim != 0:
                    print (localidf +', Eliminados '+ str(nElim) +' nodos')

                prog = 100 * nfeat/numfeats
                self.progressBar.setValue(int(prog))

                # Se escribe PLANTILLA_3. Añade la parte posterior a las coordenadas de cada feature al GML
                filegml.writelines(self.catGML.PLANTILLA_3.format(localidf=localidf,nmspc=nmspcf))
                fracfeats += 1/numfeats

            # Se escribe PLANTILLA_4. Añade el final al GML
            filegml.writelines(self.catGML.PLANTILLA_4)     # Añade el final al GML


        # Carga del GML en la TOC
        if self.chbCARGAGML.isChecked() and nfeat > 0:
            crs = QgsCoordinateReferenceSystem(int(src),QgsCoordinateReferenceSystem.EpsgCrsId)
            layerGML = QgsVectorLayer(gml_salida_file, nomCAPA+"_GML" , 'ogr')

            layerGML.setCrs(crs,False)

            QgsProject.instance().addMapLayer(layerGML)

            root = QgsProject.instance().layerTreeRoot()

            # Ponemos la capa arriba
            myvl = root.findLayer(layerGML.id())
            parent = myvl.parent()
            myvlclone = myvl.clone()
            root.insertChildNode(0, myvlclone)
            try:
                parent.removeChildNode(myvl)
            except:
                print ('parent - ', parent.name(), type(parent), '   IMPOSIBLE BORRAR')

        QApplication.restoreOverrideCursor()

        self.close()

        if errorGML == True:
            if nfeat == 0:
                textINFO = '--- NO SE CARGA GML ---'
            else:
                textINFO = '---EL FICHERO PUEDE NO SER VÁLIDO PARA CATASTRO---'

            self.showDialog(listaerrorGML, layer, nomCAPA, gml_salida_file, textINFO)

            project = QgsProject.instance()
            # Eliminar capas LOG existentes
            for lyr in project.mapLayers().values():
                if lyr.name() == 'Log GML':
                    project.removeMapLayer(lyr.id())

            # Creación de la capa de LOG
            log_csv_uri = u"file:///"+ log_csv +"?type=csv&geomType=none&subsetIndex=no&delimiter=%s&watchFile=no" % (";")
            log_lyr = QgsVectorLayer(log_csv_uri, 'Log GML','delimitedtext')
            project.addMapLayer(log_lyr)


    def compruebaRCorigen(self, rc, featGeom, precis=1):
        """
        Comprueba si la geometría de featGeom es idéntica a la descargada de Catastro
        para una RC dada.
            - rc, REF. CATASTRAL a descargar y comparar
            - featGeom, geometría a incluír en el GML con dicha RC y namespace = 'ES.SDGC.CP'
            - precis. precisión decimal de compraración, por defecto  1 deciaml
        """
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
        
        # if round(areaGML, 1) != round(areaParcela, precis):
            # return 'DISTINTA'

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
        # Se crea un cuadro de diálogo con una serie de rótulos y una tablewidget de tre columnas y N líneas
        main_window = self.iface.mainWindow()
        dialog = QgsDialog(main_window,
                           fl=Qt.WindowFlags(),
                           buttons=QDialogButtonBox.NoButton,
                           orientation=Qt.Vertical)
        # dialog.setWindowTitle("LISTADO DE ERRORES EN EL GML - EL FICHERO NO SERÁ VÁLIDO PARA CATASTRO")
        dialog.setWindowTitle("LISTADO DE ERRORES EN EL GML")
        dialog.setWindowIcon(QIcon(f':/plugins/{self.nombre_plugin}/iconos/cat_gml.jpg'))
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
        tableWidget.setColumnWidth( 0, 140)
        tableWidget.setColumnWidth( 1, 100)
        tableWidget.setColumnWidth( 2, 240)
        tableWidget.setHorizontalHeaderLabels (['RC PARCELA      ', 'NAMESPACE    ', 'ERROR DETECTADO    '])
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
        """
        Comprueba si hay valores repetidos en el campo seleccionado como localid.
        Retorna:
            - False: No hay valores repetidos
            - True: Hay valores repetidos, y se muestra diálogo con los errores
        """
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
        # Comprobar localid repetidos
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
        geometry_multipolygon = QgsGeometry.fromMultiPolygonXY([feature_polygon.geometry().asPolygon()])
        feature_multipolygon = QgsFeature()
        feature_multipolygon.setGeometry(geometry_multipolygon)
        n, nElim = self.describe_multipolygon(feature_multipolygon, localidf, nmspclocalid, src, filegml)
        return n, nElim


    def describe_multipolygon(self, feature_multipolygon, localidf, nmspclocalid, src, filegml):
        ## PERMITE ELIMINACIÓN DE NODOS REPETIDOS
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