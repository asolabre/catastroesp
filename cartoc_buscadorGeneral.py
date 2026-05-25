# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name:           cartoc_buscadorGeneral.py

                                 A QGIS plugin
                                 
Plugin:         catastroesp - Catastro de España / jccm_bar3
Purpose:        Buscador de fenómenos por medio de las herramientas de CARTOCIUDAD
        --------------------------------------------------------------------
        begin                : 2021-08-04
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

## INFORMACIÓN DE LOS SERVICIOS ##
## https://www.cartociudad.es/recursos/Documentacion_tecnica/CARTOCIUDAD_ServiciosWeb.pdf

## POR LISTA DE CANDIDATOS ##
# url = 'http://www.cartociudad.es/geocoder/api/geocoder/candidatesJsonp?q=a-2%20272&limit=10'


"""

from PyQt5.QtGui import QIcon, QPixmap, QKeySequence
from PyQt5.QtCore import QSettings, Qt, QVariant
from PyQt5.QtWidgets import QDialog, QApplication, QShortcut
from PyQt5 import uic, QtCore, QtGui

from qgis.gui import QgsDialog
from qgis.core import (Qgis, QgsPointXY, QgsVectorLayer, QgsGeometry,QgsFeature, QgsProject, QgsPoint, QgsVectorFileWriter,
                        QgsAbstractGeometry, QgsExpression, QgsFeatureRequest, QgsField, QgsWkbTypes,
                        QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsVectorDataProvider,
                        QgsCoordinateTransformContext)

import os
import json
import urllib.request
import math
# from math import *
from osgeo import ogr, osr

import json
import urllib
import requests

from .settings import Settings           # CLASE DE CONFIGURACIÓN DE VARIABLES GLOBALES
from .functions3 import Functions        # CLASE DE CONFIGURACIÓN DE FUNCIONES GENERALES
from .config import configuration        # CLASE DE CONFIGURACIÓN DE VARIABLES DEL PROGRAMA
conf = configuration()

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), './menus/cartoc_buscadorgral.ui'))

# VARIABLES
# Flag de error a reconocer por todas las rutinas que buscan conexión
errorConexion = False

class cartoc_buscadorGeneral(QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        """Constructor."""
        super(cartoc_buscadorGeneral, self).__init__(parent)

        self.setupUi(self)
        self.conf = configuration()
        self.setVar = QSettings()

        self.nombre_plugin = os.path.basename(os.path.dirname(__file__))

        self.fun = Functions()
        self.iface = iface;
        self.setWindowIcon(QIcon(f':/plugins/{self.nombre_plugin}/logo_general.jpg'))

        self.qs = QSettings()

        EPSG = self.iface.mapCanvas().mapSettings().destinationCrs().authid()
        self.srcVal = EPSG[5:15]
        self.goToPk_button.clicked.connect(self.goToPK_clicked)
        self.buscaDireccion_button.clicked.connect(self.goToDireccion_clicked)
        self.lne_Direccion.returnPressed.connect(self.goToDireccion_clicked)
        self.listDIRECCION = []
        self.goToDireccion_button.clicked.connect(self.IRaDireccionCARTOCIUDAD)

        self.logo.setPixmap(QPixmap(f":/plugins/{self.nombre_plugin}/iconos/cartociudad_IGN.jpg"))

        # Colocamos los últimos valores seleccionados en el cuadro de Diálogo
        lastCartocCtra = self.qs.value(f"{self.nombre_plugin}/last/lastCartocCtra")
        self.lne_carretera.setText(lastCartocCtra)
        lastCartocPk = self.qs.value(f"{self.nombre_plugin}/last/lastCartocPk")
        self.lne_pk.setText(lastCartocPk)
        lastCartocDireccion = self.qs.value(f"{self.nombre_plugin}/last/lastCartocDireccion")
        self.lne_Direccion.setText(lastCartocDireccion)

        # TIPO (CATEGORÍAS DEL CAMPO 'TIPO')
        self.tiposDIR ={
        'callejero'         : 'LINESTRING',# 'para viales urbanos',                              # LINESTRING / POINT
        'portal'            : 'POINT',     # 'portal o punto kilométrico',                       # POINT
        'carretera'         : 'LINESTRING',# 'viales interurbanos',                              # LINESTRING
        'Municipio'         : 'POLYGON',   # 'Municipio',                                        # POLYGON
        'provincia'         : 'POLYGON',   # 'provincia',                                        # POLYGON
        'comunidad autonoma': 'POLYGON',   # 'comunidad autonoma',                               # POLYGON
        'toponimo'          : 'POINT',     # 'toponimo',                                         # POINT
        'poblacion'         : 'POINT',     # 'poblacion',                                        # POINT
        'expendeduría'      : 'POINT',     # 'Expendedurías (procedentes de Comisión de Tabacos),# POINT
        'ngbe'              : 'POINT',     # 'Topónimos Nomenclador Geog.Básico de España',      # POINT
        'refcatastral'      : 'POLYGON'    # 'refcatastral'                                      # POLYGON
        }

        
        # Se definen los campos del futuro GPKG de Cartociudad
        self.defineCamposCARTOC()
        
        # Se definen las URLs de la API de Cartociudad
        self.defineUrlsCARTOC()


    def defineUrlsCARTOC(self):
        # DIRECCIONES API CARTOCIUDAD
        # url = 'http://www.cartociudad.es/geocoder/api/geocoder/findJsonp?type=carretera&tip_via=&id=600000000042&portal=272
        self.urlPORTALPK = 'http://www.cartociudad.es/geocoder/api/geocoder/findJsonp?'
        
        ## ACCESO A CARTOCIUDAD POR DIRECCIÓN EN TEXTO LIBRE --- candidatesJsonp --- ##
        # url = 'http://www.cartociudad.es/geocoder/api/geocoder/candidatesJsonp?q=a-2%20272&limit=10'
        self.urlCANDIDATES = 'http://www.cartociudad.es/geocoder/api/geocoder/candidatesJsonp?'
        
        
    def defineCamposCARTOC(self):
        self.camposCartociudad = [
            {'campo':'id',                    'tipo':'string', 'comment': 'Identificador de la referencia'},
            {'campo':'type',                  'tipo':'string', 'comment': 'Tipo de entidad'},
            {'campo':'address',               'tipo':'string', 'comment': 'Texto completo del nombre de los resultados'},
            {'campo':'tip_via',               'tipo':'string', 'comment': 'Especifica el tipo de vía'},
            {'campo':'portalNumber',          'tipo':'string', 'comment': 'Número de portal o punto kilométrico (si se especifica en la consulta)'},
            {'campo':'noNumber',              'tipo':'string', 'comment': 'Valor “true” portal con número S-N, “false” portal con número distinto S-N'},
            {'campo':'extension',             'tipo':'string', 'comment': 'Extensión del número del portal'},
            {'campo':'muni',                  'tipo':'string', 'comment': 'Municipio al que pertenece (si corresponde al tipo de entidad)'},
            {'campo':'muniCode',              'tipo':'int'   , 'comment': 'Código del municipio'},
            {'campo':'province',              'tipo':'string', 'comment': 'Provincia a la que pertenece (si corresponde)'},
            {'campo':'provinceCode',          'tipo':'int'   , 'comment': 'Código de la provincia a la que pertenece'},
            {'campo':'comunidadAutonoma',     'tipo':'string', 'comment': 'Comunidad Autónoma a la que pertenece (si corresponde)'},
            {'campo':'comunidadAutonomaCode', 'tipo':'int'   , 'comment': 'Código de la Comunidad Autónoma a la que pertenece'},
            {'campo':'poblacion',             'tipo':'string', 'comment': 'Población a la que pertenece (si corresponde)'},
            {'campo':'postalCode',            'tipo':'string', 'comment': 'Código postal (si corresponde)'},
            {'campo':'countryCode',           'tipo':'int'   , 'comment': 'Código del país (por defecto \'011\' para España)'},
            {'campo':'refCatastral',          'tipo':'string', 'comment': 'Referencia catastral (si corresponde)'},
            {'campo':'lat',                   'tipo':'double', 'comment': 'Coordenada que representa la latitud de la entidad de los elementos puntuales'},
            {'campo':'lng',                   'tipo':'double', 'comment': 'Coordenada que representa la longitud de la entidad de los elementos puntuales'},
            {'campo':'stateMsg',              'tipo':'string', 'comment': 'Vacío'},
            {'campo':'state',                 'tipo':'string', 'comment': 'Vacío'},
            {'campo':'geom',                  'tipo':'string', 'comment': 'Geometria'}
            ]

        '''
        # Dominios de Campos de capa CARTOCIUDAD
        # ---------------------------------------
            # id: Identificador de la referencia.
            # type: Tipo de entidad. Los valores pueden ser:
                    # 'callejero' (viales urbanos),
                    # 'portal' (portal o punto kilométrico),
                    # 'carretera' (viales interurbanos),
                    # 'municipio',
                    # 'provincia',
                    # 'comunidad autonoma',
                    # 'toponimo',
                    # 'poblacion',
                    # 'expendeduría',
                    # 'punto_recarga_electrica',
                    # 'ngbe',
                    # 'refcatastral'.
            # address: Texto completo del nombre de los resultados.
            # tip_via: Especifica el tipo de vía
            # portalNumber: Número de portal o punto kilométrico (si se especifica en la consulta).
            # noNumber: su valor puede ser:
                    # “true” cuando el portal encontrado tiene como número S-N,
                    # “false” cuando se esté buscando un número de portal distinto a S-N.
            # extension: Extensión del número del portal
            # muni: Municipio al que pertenece (si corresponde al tipo de entidad).
            # muniCode: Código del municipio.
            # province: Provincia a la que pertenece (si corresponde).
            # provinceCode: Código de la provincia a la que pertenece.
            # comunidadAutonoma: Comunidad Autónoma a la que pertenece (si corresponde)
            # comunidadAutonomaCode: Código de la Comunidad Autónoma a la que pertenece.
            # poblacion: Población a la que pertenece (si corresponde)
            # postalCode: Código postal (si corresponde).
            # countryCode: Código del país (por defecto '011' para España).
            # refCatastral: Referencia catastral (si corresponde).
            # lat: Coordenada que representa la latitud de la entidad de los elementos puntuales(portales,
                    # puntos kilométricos, puntos de interés y topónimos).
            # lng: Coordenada que representa la longitud de la entidad de los elementos puntuales
                    # (portales, puntos kilométricos, puntos de interés y topónimos).
            # geom: no disponible con esta petición.
            # state: 0 (este valor con la versión actual del geocoder, se ha suprimido, ya que se emplea
                    # elasticsearch y no se puede configurar la salida de candidates según grado de coincidencia).
            # stateMsg: Vacío (este valor con la versión actual del geocoder, se ha suprimido, ya que se
                    # emplea elasticsearch y no se puede configurar la salida candidates según grado de
                    # coincidencia)
        '''


    def goToPK_clicked(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Colocamos el valor últimos valores seleccionados en el cuadro de Diálogo
        self.qs.setValue(f"{self.nombre_plugin}/last/lastCartocCtra", self.lne_carretera.text())
        self.qs.setValue(f"{self.nombre_plugin}/last/lastCartocPk", self.lne_pk.text())

        ctra = self.lne_carretera.text()
        pk = self.lne_pk.text()
        if ctra != '' and  pk != '':
            pointRES = self.getRoadPkCARTOCIUDAD(ctra, pk)
        else:
            pointRES = 'Error'

        if pointRES != 'Error':
            pointOGR = ogr.Geometry(ogr.wkbPoint)
            pointOGR.AddPoint(pointRES.x(), pointRES.y())
            self.fun.zoomToGeometry(self.iface,pointOGR, Nomark = 'SI')
        else:
            text =  'CTRA: '+ctra + ' PK: '+ pk +'\n'
            text += 'DATOS ERRONEOS'
            self.fun.showMessageERR(text)

        QApplication.restoreOverrideCursor()


    def goToDireccion_clicked(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Colocamos el valor últimos valores seleccionados en el cuadro de Diálogo
        self.qs.setValue(f"{self.nombre_plugin}/last/lastCartocDireccion", self.lne_Direccion.text())

        direccion = self.lne_Direccion.text()
        if direccion != '':
            listDIRECCION, lstCANDIDATOS_DIRECC = self.getDireccionCARTOCIUDAD(direccion)
            if listDIRECCION != 'error':
                self.listDIRECCION = listDIRECCION
                self.lstCANDIDATOS_DIRECC.clear()
                for candidato in lstCANDIDATOS_DIRECC:
                    self.lstCANDIDATOS_DIRECC.addItem(candidato)
            else:
                self.fun.showMessageERR(lstCANDIDATOS_DIRECC)

            
        QApplication.restoreOverrideCursor()


    def getRoadPkCARTOCIUDAD(self, ctra, pk):
        # getRoadPkCARTOCIUDAD(self,ctra, pk)
        #   Rutina de obtención de las coordenadas de una CTRA - PK en CARTOCIUDAD
        #       ctra = NOMBRE DE LA CARRETERA
        #       pk   = PK DE LA CARRETERA

        if not self.urlPORTALPK:
            self.defineUrlsCARTOC()
            
        url = self.urlPORTALPK
            
        consulta = ctra + " " + pk

        values = {'q' : consulta,
                  'limit': 4}

        str_values = {}
        for k, v in values.items():
            str_values[k] = unicode(v).encode('utf-8')
        data = urllib.parse.urlencode(str_values)
        # print (url+data)
        dataf = requests.get(url+data).text          # Request data from link as 'str'
        # print (dataf)

        # Se extrae del resultado JSONP la parte entre paréntesis
        startidx = dataf.find('(')
        endidx = dataf.rfind(')')
        response = json.loads(dataf[startidx + 1:endidx])
        # print (response)
        if response:
            address = response['address']
            portalNumber = response['portalNumber']
            lat = response['lat']
            lon = response['lng']

            geom = QgsGeometry(QgsPoint(lat,lon))
            sourceCrs = QgsCoordinateReferenceSystem(4258)
            destCrs = QgsCoordinateReferenceSystem(int(self.srcVal))
            transformContext = QgsProject.instance().transformContext()
            xform = QgsCoordinateTransform(sourceCrs, destCrs, transformContext)
            point = xform.transform(QgsPointXY(lon,lat))
            # print('CTRA:{} PK:{}  X:{}, Y:{}'.format(address, portalNumber, point.x(), point.y()))
            return point
        else:
            # print('CTRA:{} PK:{}  -NO RECIBE RESPUESTA-'.format(ctra, pk))
            return 'Error'


    def getDireccionCARTOCIUDAD(self, direccion):
        #   Rutina de obtención de las coordenadas de candidatos de de una Direccion CARTOCIUDAD
        #       direccion = DIRECCIÓN EN TEXTO LIBRE DEL SITIO A ENCONTRAR

        ## ACCESO A CARTOCIUDAD POR DIRECCIÓN EN TEXTO LIBRE --- candidatesJsonp --- ##
        # url = 'http://www.cartociudad.es/geocoder/api/geocoder/candidatesJsonp?q=a-2%20272&limit=10'
        # url = 'http://www.cartociudad.es/geocoder/api/geocoder/candidatesJsonp?'
        
        if not self.urlCANDIDATES:
            self.defineUrlsCARTOC()
        
        url = self.urlCANDIDATES

        if not self.camposCartociudad:
            self.defineCamposCARTOC()
        
        values = {'q' : direccion,
                  'limit': 20}

        str_values = {}
        for k, v in values.items():
            str_values[k] = unicode(v).encode('utf-8')
        data = urllib.parse.urlencode(str_values)
        # print (url+data)
        dataf = requests.get(url+data).text          # Request data from link as 'str'
        # print (dataf)

        # Se extrae del resultado JSONP la parte entre paréntesis
        startidx = dataf.find('(')
        endidx = dataf.rfind(')')
        response = json.loads(dataf[startidx + 1:endidx])

        # Convertir todas las cadenas en 'response' a UTF-8
        # response = self.convert_to_utf8(json.loads(dataf[startidx + 1:endidx]))
        # response = self.convert_to_latin1(json.loads(dataf[startidx + 1:endidx]))

        # print (response)
        listDIRECCION = []
        lstCANDIDATOS_DIRECC = []
        if response:
            # listDIRECCION = []
            for i in response:
                # print (i)
                direccionDICT = {}
                for campo in self.camposCartociudad:
                    try:
                        direccionDICT[campo['campo']] = i[campo['campo']]
                    except:
                        direccionDICT[campo['campo']] = None

                direccTXT = '{}, ({})  TIPO:{}  ID:{}'.format(direccionDICT['address'], direccionDICT['province'], direccionDICT['type'], direccionDICT['id'])
                # print('Direccion: '+direccTXT)
                listDIRECCION.append(direccionDICT)
                lstCANDIDATOS_DIRECC.append(direccTXT)
                
            # print('listDIRECCION: ', listDIRECCION, 'lstCANDIDATOS_DIRECC: ', lstCANDIDATOS_DIRECC)
            return listDIRECCION, lstCANDIDATOS_DIRECC
            
        else:
            text =  'Direccion: {}  -NO SE ENCUENTRA DIRECCION-'.format(direccion)
            return 'error', text


    def IRaDireccionCARTOCIUDAD(self):

        if self.lstCANDIDATOS_DIRECC.count() == 0:
            return

        # Si no se ha seleccionado nada se vuelve
        if len(self.lstCANDIDATOS_DIRECC.selectedItems()) == 0:
            text =  'SE DEBE SELECIONAR ALGUNA DE LAS DIRECCIONES ENCONTRADAS'
            self.fun.showMessageERR(text)
            return

        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Obtener el tipo de geometría
        direccENCONT = self.lstCANDIDATOS_DIRECC.selectedItems()[0].text()
        posDireccENCONT = self.lstCANDIDATOS_DIRECC.row(self.lstCANDIDATOS_DIRECC.selectedItems()[0])
        direccENCONTdata = self.listDIRECCION[posDireccENCONT]

        # address = direccENCONT.split(',')[0]
        address = direccENCONTdata['address'].lstrip()  # 'address' dirección seleccionada
        id = direccENCONTdata['id']                     # 'id' en Cartociudad del elemento seleccionado
        tipo = direccENCONTdata['type']                 # 'tipo' en Cartociudad del elemento seleccionado
        portalNumber = direccENCONTdata['portalNumber']

        # print (self.lstCANDIDATOS_DIRECC.item(posDireccENCONT))
        # print (direccENCONTdata)

        # Definir la ruta del GeoPackage
        gpkg_path = 'c:/temp/cartoGeom.gpkg'

        # Obtener el tipo de geometría
        geom_type = self.tiposDIR[tipo]

        # Determinar el nombre de la capa basado en el tipo de geometría
        if geom_type == 'POINT':
            layer_name = 'DIRECCIONES_CARTOCIUDAD (pto)'
            estiloCAPA = os.path.join(os.path.dirname(__file__), self.conf.general["carpeta_estilos"] + '/cartoc_pto.qml')
            geom_wkb = 'MultiPoint'
        elif geom_type == 'LINESTRING':
            layer_name = 'DIRECCIONES_CARTOCIUDAD (lin)'
            estiloCAPA = os.path.join(os.path.dirname(__file__), self.conf.general["carpeta_estilos"] + '/cartoc_lin.qml')
            geom_wkb = 'MultiLineString'
        elif geom_type == 'POLYGON':
            layer_name = 'DIRECCIONES_CARTOCIUDAD (pol)'
            estiloCAPA = os.path.join(os.path.dirname(__file__), self.conf.general["carpeta_estilos"] + '/cartoc_pol.qml')
            geom_wkb = 'MultiPolygon'
        else:
            raise ValueError("Tipo de geometría no reconocido")

        # Crear la capa si no existe
        # if not os.path.exists(gpkg_path) and not QgsProject.instance().mapLayersByName(layer_name):
        if not os.path.exists(gpkg_path) or not QgsProject.instance().mapLayersByName(layer_name):        
            # Se crea la capa
            vlayer = self.creaCapaCartociudad(self.iface, layer_name, geom_wkb, estiloCAPA, gpkg_path)

        else:
            # Asignar la capa existente
            vlayer = QgsProject.instance().mapLayersByName(layer_name)[0]

        geomDIRECCION, atributosDICT = self.IrURLDireccionCARTOCIUDAD(address, id, tipo, portalNumber)
        self.zoomCreaGeometry(self.iface, address, geomDIRECCION, atributosDICT, vlayer, Nomark='SI', zoomGeom = True, cargaTodo = True)
         
        QApplication.restoreOverrideCursor()

        return

    def IrURLDireccionCARTOCIUDAD(self, address, id, tipo, portalNumber):

        if not self.camposCartociudad:
            self.defineCamposCARTOC()
            
        if not self.urlPORTALPK:
            self.defineUrlsCARTOC()
            
        url = self.urlPORTALPK

        # Comprobamos si existe la capa y el 'id' seleccionado
        ### TODO. ESTO ESTÁ SIN HACER
        existeID = self.compruebaIDexists(id)
        if existeID == 'SI':
            return

        values = {'type' : tipo,
                  'id': id,
                  'portal': portalNumber}

        str_values = {}
        for k, v in values.items():
            str_values[k] = unicode(v).encode('utf-8')
        data = urllib.parse.urlencode(str_values)
        # print (url+data)
        dataf = requests.get(url+data).text          # Request data from link as 'str'
        # print (dataf)

        # Se extrae del resultado JSONP la parte entre paréntesis
        startidx = dataf.find('(')
        endidx = dataf.rfind(')')
        try:
            response = json.loads(dataf[startidx + 1:endidx])
        except:
            QApplication.restoreOverrideCursor()
            self.fun.showMessage(u"Error de respuesta de internet (IRaDireccionCARTOCIUDAD LIN:291)")
            return 'Error: No hay respuesta'

        # Convertir todas las cadenas en 'response' a UTF-8
        # print (response)

        if response:
            atributosDICT = {}
            for campo in self.camposCartociudad:
                # Se asignan todos los keys de response, que existan en camposCartociudad
                if response.get(campo['campo']):
                    atributosDICT[campo['campo']] = response[campo['campo']]
            
        else:
            return

        geomDIRECCION = QgsGeometry.fromWkt(atributosDICT['geom'])
        sourceCrs = QgsCoordinateReferenceSystem(4258)
        destCrs = QgsCoordinateReferenceSystem(int(self.srcVal))
        transformContext = QgsProject.instance().transformContext()
        xform = QgsCoordinateTransform(sourceCrs, destCrs, transformContext)
        geomDIRECCION.transform(QgsCoordinateTransform(sourceCrs, destCrs, transformContext))

        return (geomDIRECCION, atributosDICT)


    def creaCapaCartociudad(self, iface, layer_name, geom_wkb, estiloCAPA, gpkg_path):
        layer_uri = f'{gpkg_path}|layername={layer_name}'
        ### TODO :METER EN GEOPACKAGE
        vlayer = QgsVectorLayer(f'{geom_wkb}?crs=EPSG:{self.srcVal}&encoding=UTF-8', layer_name, 'memory')
        
        if not self.camposCartociudad:
            self.defineCamposCARTOC()

        if estiloCAPA:
            vlayer.loadNamedStyle(estiloCAPA)
            vlayer.triggerRepaint()

        # Añadir campos a lista
        provider = vlayer.dataProvider()        
        dataCamposCARCIU = []
        # Se añaden campos desde la lista camposCartociudad
        for campo in self.camposCartociudad:
            if campo['tipo'] == 'string':
                dataCamposCARCIU.append(QgsField(campo['campo'], QVariant.String,   comment=campo['comment']))
            elif campo['tipo'] == 'int':
                dataCamposCARCIU.append(QgsField(campo['campo'], QVariant.Int,      comment=campo['comment']))
            elif campo['tipo'] == 'double':
                dataCamposCARCIU.append(QgsField(campo['campo'], QVariant.Double,   comment=campo['comment']))
            else:       # Si la sintaxis no es correcta, se pone string
                dataCamposCARCIU.append(QgsField(campo['campo'], QVariant.String,   comment=campo['comment']))

        # Añadir campos a provider
        provider.addAttributes(dataCamposCARCIU)
        
        # Actualizar la capa con los cambios
        vlayer.updateFields()

        return vlayer


    def zoomCreaGeometry(self, iface, address, geomDIRECCION, atributosDICT, vlayer, Nomark='SI', zoomGeom = True, cargaTodo = False):
        # Comprobamos si la DIRECCIÓN existe, mediante el 'id'
        ids = []
        noids = 0
        consulta = u'"id" = \''+atributosDICT['id']+'\''
        expr = QgsExpression( consulta )
        it = vlayer.getFeatures( QgsFeatureRequest( expr ) )    # Obtiene un iterador de elementos desde una expresión
        for feat in it:
            noids += 1

        if noids == 0 or cargaTodo is True:   ## EL 'id' NO ESTÁ EN LA LISTA. SE CARGA
            # Añadir la geometría y los atributos a la capa
            provider = vlayer.dataProvider()
            feat = QgsFeature()
            feat.setGeometry(geomDIRECCION)

            # Añadir los atributos del 'atributosDICT'
            fields = vlayer.fields()
            feat.setFields(fields)
            for attr in atributosDICT:
                field_index = fields.indexFromName(attr)
                if field_index != -1:
                    if atributosDICT[attr]:
                        if isinstance(atributosDICT[attr], str):  # Verifica si es un string
                            # feat[attr] = atributosDICT[attr].encode('utf-8').decode('utf-8')
                            feat[attr] = self.utf8_encode(atributosDICT[attr])
                            # feat[attr] = atributosDICT[attr]
                        else:
                            feat[attr] = atributosDICT[attr]
                            
                            
            provider.addFeature(feat)
            vlayer.updateExtents()

        # Cargar la capa al proyecto si es necesario
        if not QgsProject.instance().mapLayersByName(vlayer.name()) and Nomark != 'NO':
            # Se crea la capa
            # vlayer = self.creaCapaCartociudad(self.iface, layer_name, geom_wkb, estiloCAPA, gpkg_path)
           
            QgsProject.instance().addMapLayer(vlayer)
            
            # Ponemos la capa arriba
            root = QgsProject.instance().layerTreeRoot()
            myvl = root.findLayer(vlayer.id())
            myvlclone = myvl.clone()
            parent = myvl.parent()
            root.insertChildNode(0, myvlclone)
            parent.removeChildNode(myvl)

        # Hacer zoom a la geometría
        if zoomGeom:
            iface.mapCanvas().setExtent(geomDIRECCION.boundingBox())
            iface.mapCanvas().refresh()


    def compruebaIDexists(self, id):
        ### TODO HAY QUE HACER TODO ESTO
        return 'NO'
        pass


    # Asegúrate de que la codificación se maneje adecuadamente
    def utf8_encode(self, value):
        if isinstance(value, str):
            return value.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
        return value


    '''
    ## EJEMPLOS SALIDAS CARTOCIUDAD
    
    ## TIPO POLÍGONO
    response=
    {
    int 'id': '800003390',
    str 'province': 'Albacete',
    int 'provinceCode': '02',
    str 'comunidadAutonoma': 'Castilla-La Mancha',
    int 'comunidadAutonomaCode': '08',
    str 'muni': 'Chinchilla de Monte-Aragón',
    int 'muniCode': '02029',
    str 'type': 'poblacion',
    str 'address': 'Pozo de la Peña',
    int 'postalCode': None,
    str 'poblacion': 'Pozo de la Peña',
    geo 'geom': [la geometria en lat/lon]
    str 'tip_via': None,
    dbl 'lat': 38.90419479018109,
    dbl 'lng': -1.7375099296800953,
    int 'portalNumber': None,
    int 'noNumber': None,
    str 'stateMsg': '',
    str 'extension': None,
    int 'state': 0,
    str 'refCatastral': None,
    int 'countryCode': '011'}

    ## TIPO MULTILINESTRING
    {
    'id': '20290000160',
    'province': 'Albacete',
    'provinceCode': '02',
    'comunidadAutonoma': 'Castilla-La Mancha',
    'comunidadAutonomaCode': '08',
    'muni': 'Chinchilla de Monte-Arag√≥n',
    'muniCode': '02029',
    'type': 'callejero',
    'address': 'CHINCHILLA (LA FELIPA)',
    'postalCode': '02156',
    'poblacion': 'La Felipa',
    'geom': 'MULTILINESTRING((-1.70274105599998 39.035416233,-1.70246419499995 39.034461089),(-1.70313095999995 39.0367354000001,-1.70274105599998 39.035416233),(-1.70342915999993 39.03884198,-1.70348268999993 39.03898882),(-1.70313095999995 39.0367354000001,-1.70325533999994 39.03779597),(-1.70325533999994 39.03779597,-1.70336022999993 39.0385998200001,-1.70342915999993 39.03884198))',
    'tip_via': 'CALLE',
    'lat': 39.03671357724625,
    'lng': -1.7030307514149308,
    'portalNumber': None,
    'noNumber': None,
    'stateMsg': '',
    'extension': None,
    'state': 0,
    'refCatastral': None,
    'countryCode': '011'}
    '''

