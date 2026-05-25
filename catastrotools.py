'''
/***************************************************************************
Name:            catastrotools.py
Purpose:        Tools for plugin catastroesp

        --------------------------------------------------------------------
        begin                : 2016-06-07
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

from PyQt5.QtGui import QCursor, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSettings, QVariant
from PyQt5.QtWidgets import QApplication, QDialog

from qgis.gui import QgsMapTool
from qgis.core import (QgsFeature, QgsProject, QgsVectorLayer, QgsLayerTreeLayer, QgsGeometry,
                        QgsPointXY, QgsVectorDataProvider, QgsField, QgsWkbTypes)

from qgis.PyQt.QtCore import QVariant

import urllib

from xml.etree import cElementTree as ElementTree
from xml.dom import minidom
from xml.dom.minidom import parseString

from osgeo import ogr, osr

import os
import json
import locale
from time import sleep

from .config import configuration        # CLASE DE CONFIGURACIÓN DE VARIABLES DEL PROGRAMA
from .functions3 import Functions        # CLASE DE CONFIGURACIÓN DE FUNCIONES GENERALES


# Cargamos la clase del menú dialogo de Parcela catastral
from .catastroParcelaINFO import catastroParcelaINFODialog

locale.setlocale(locale.LC_ALL, 'ESP')

class catastroCargaMuni(QgsMapTool):
    # Carga del catastro de todo un municipio pinchado
    # ------------------------------------------------
    # Cambiamos los parametros que mandan el codigo ine para obtener el catastral
    # Se manda un mesnsaje que diga que se va a abrir la capa
    #       falta un aviso si no existe la capa o no hay acceso al repositorio, pero todo se andará
    def __init__(self,canvas,iface,action):

        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.fun = Functions()
        self.qs = QSettings()

        self.nombre_plugin = os.path.basename(os.path.dirname(__file__))

        cursor = QCursor()
        cursor.setShape(Qt.CrossCursor)
        iface.mapCanvas().setCursor(cursor)
        self.iface = iface
        self.setAction(action)
        self.action = action
        self.url_catastro_municipios = self.qs.value(f'{self.nombre_plugin}/CATASTRO/url_catastro_municipio')
        QApplication.restoreOverrideCursor()

    def canvasPressEvent(self, event):
        pass

    def canvasMoveEvent(self, event):
        pass

    def canvasReleaseEvent(self, event):
        # ICONO DE ESPERA
        QApplication.setOverrideCursor(Qt.WaitCursor)
        progress = 'Cargando datos desde CATASTRO {txt}...'.format(txt='')
        self.iface.mainWindow().statusBar().showMessage(progress)

        # year = str(self.conf_catastro_tool['year'])
        year = str(self.qs.value(f'{self.nombre_plugin}/CATASTRO/cat_year'))
        cat_dir_shps = self.qs.value(f'{self.nombre_plugin}/CATASTRO/cat_dir_shps')

        origenData = 'Dir'

        # --------------- QUITAR ESTO ---------------
        # # if not os.path.exists(self.conf_catastro_tool['dir_shps'] +   year + u'/'):
        # if not os.path.exists(cat_dir_shps + year + u'/'):
            # origenData = 'web'

        # FORZAMOS ORIGENDATA a hacerlo desde web
        # origenData = 'dir'
        origenData = 'web'
        # --------------- QUITAR ESTO ---------------

        #Get the click
        x = event.pos().x()
        y = event.pos().y()

        # Obtener el Sistema de Referencia de Coordenadas (SRS) actual del proyecto
        #   y obtener el identificador de autoridad (authid) del SRS actual
        # srs = QgsProject.instance().crs().authid()
        
        srs =  self.iface.mapCanvas().mapSettings().destinationCrs().authid()
        print('srs= ', srs)  # Imprimir el identificador de autoridad (authid) del SRS actual
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        print ('Punto pinchado: ', point )


        # CONSULTA DE RC POR COORDENADAS DIST - Se mete en functions.py
        try:
            result = self.fun.consultaCatastroXYDISTtoRC(point[0], point[1] ,srs)
        except:
            QApplication.restoreOverrideCursor()
            resp = self.fun.showMessageYESNO( '- NO HAY RESPUESTA DE CATASTRO -\n'+'(catastrotools-114- self.fun.consultaCatastroXYDISTtoRC)','','Capas de Catastro' )
            self.iface.mainWindow().statusBar().clearMessage()
            return
        if result[0] == u'ERROR':
            return
        codigo_provincia = result[5]
        codigo_muni_ine = result[6]
        print ('codigo_provincia:',codigo_provincia,' codigo_muni_ine:', codigo_muni_ine)
        # CONSULTA DE NOMBRE PROVINCIA DESDE COD_PROV - Se mete en functions.py
        try:
            nombre_prov = self.fun.consultaCatastroCodProvtoProvincia(codigo_provincia)
        except:
            QApplication.restoreOverrideCursor()
            resp = self.fun.showMessageYESNO( '- NO HAY RESPUESTA DE CATASTRO -\n'+'(catastrotools-133- self.fun.consultaCatastroCodProvtoProvincia)','','Capas de Catastro' )
            self.iface.mainWindow().statusBar().clearMessage()
            return

        # CONSULTA DE LOS MUNICIPIOS DE LA PROVINCIA
        try:
            print ('self.fun.consultaCatastroCodMunitoMunicipio')
            print (nombre_prov, codigo_muni_ine)
            result = self.fun.consultaCatastroCodMunitoMunicipio(nombre_prov, codigo_muni_ine)
        except:
            QApplication.restoreOverrideCursor()
            resp = self.fun.showMessageYESNO( '- NO HAY RESPUESTA DE CATASTRO -\n'+'(catastrotools-158 except1- self.fun.consultaCatastroCodMunitoMunicipio lin:159)','','Capas de Catastro' )
            self.iface.mainWindow().statusBar().clearMessage()
            return

        if result[0] == 'ERROR':
            QApplication.restoreOverrideCursor()
            resp = self.fun.showMessageYESNO( '- NO HAY RESPUESTA DE CATASTRO -\n'+'(catastrotools-164 except2- self.fun.consultaCatastroCodMunitoMunicipio)','','Capas de Catastro' )
            self.iface.mainWindow().statusBar().clearMessage()
            return

        nombre_muni = result[0]
        codigo_muni = result[1]
        nombre_muni = str(nombre_muni)

        # self.fun.cargaCatastroMuni(codigo_provincia, codigo_muni, nombre_muni, origenData, year, self.iface, mess = True)
        mess = True
        cargaIface = True
        print ('self.fun.cargaCatastroMuni')
        print (codigo_provincia, codigo_muni, nombre_muni, origenData, year, self.iface, mess , cargaIface )
        self.fun.cargaCatastroMuni(codigo_provincia, codigo_muni, nombre_muni, origenData, year, self.iface, mess , cargaIface )

        QApplication.restoreOverrideCursor()
        self.iface.mainWindow().statusBar().clearMessage()


    def activate(self):
        pass

    def deactivate(self):
        pass

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return False

    def getProvinciaText(self,cp):
        #print cp
        if cp == '02':
            return 'ALBACETE'
        elif cp == '13':
            return 'CIUDAD_REAL'
        elif cp == '16':
            return 'CUENCA'
        elif cp == '45':
            return 'TOLEDO'
        elif cp == '19':
            return 'GUADALAJARA'
        else:
            return 'OTRA'


class catastroToolINF(QgsMapTool):
    # Funcion creada por ASS
    # -----------  PERMITE IDENTIFICAR UNA PARCELA CATASTRAL AL PINCHARLA  -----------

    def __init__(self,canvas,iface,action):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        # self.conf_catastro_tool = conf_catastro_tool
        self.fun = Functions()
        self.qs = QSettings()
        
        self.nombre_plugin = os.path.basename(os.path.dirname(__file__))

        cursor = QCursor()
        cursor.setShape(Qt.CrossCursor)
        iface.mapCanvas().setCursor(cursor)
        self.iface = iface
        self.setAction(action)
        self.action = action
        self.url_catastro_municipios = self.qs.value(f'{self.nombre_plugin}/CATASTRO/url_catastro_municipio')
        self.dlg = catastroParcelaINFODialog(iface)

        QApplication.restoreOverrideCursor()
        self.dlg.setFixedSize(550, 500)
        self.dlg.btnIMGcatastro.setEnabled(False)
        # http://ovc.catastro.meh.es/OVCServWeb/OVCWcfLibres/OVCFotoFachada.svc/RecuperarFotoFachadaGet?ReferenciaCatastral=02055A02100200.jpeg
        self.dlg.btnIMGcatastro.clicked.connect(lambda: self.setIMGcatastro())

        self.dlg.btnREGPROP.setEnabled(True)
        self.dlg.btnREGPROP.clicked.connect(lambda: self.fun.BUSCRegistroCOMP( 'rfc', self.dlg.valREFCAT.toPlainText()))
        # Hace zoom a la parcela REGISTRAL en la web https://geoportal.registradores.org
        # https://geoportal.registradores.org/idtramite/ID02005200002291
        # https://geoportal.registradores.org/idufir/02005000756030
        # https://geoportal.registradores.org/rfc/7269302WH8876N

    def canvasPressEvent(self, event):
        pass

    def canvasMoveEvent(self, event):
        pass

    def canvasReleaseEvent(self, event):
        # ICONO DE ESPERA
        QApplication.setOverrideCursor(Qt.WaitCursor)
        progress = 'Cargando parcela catastral {txt}...'.format(txt='')
        self.iface.mainWindow().statusBar().showMessage(progress)

        #Get the click
        x = event.pos().x()
        y = event.pos().y()
        srs =  self.iface.mapCanvas().mapSettings().destinationCrs().authid()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        print ('Punto pinchado CAT: ', point )
        print ('srs = ', srs )


        # CONSULTA DE RC POR COORDENADAS - Se mete en functions.py
        try:
            result = self.fun.consultaCatastroXYtoRC(point[0], point[1] ,srs)
        except:
            QApplication.restoreOverrideCursor()
            resp = self.fun.showMessageYESNO( '- NO HAY RESPUESTA DE CATASTRO -','','Capas de Catastro' )
            self.iface.mainWindow().statusBar().clearMessage()
            return

        # print result[0]
        if result[0] == u'ERROR' or result[0] == 'E' or result[0] is None:
            QApplication.restoreOverrideCursor()
            # resp = self.fun.showMessageYESNO( '- NO HAY RESPUESTA DE CATASTRO -','','Capas de Catastro' )
            self.iface.mainWindow().statusBar().clearMessage()
            return

        RC14 = result[0]
        xml_txt = result [1]
        pc1 = result [2]
        pc2 = result [3]
        ldt = result [4]
        cp = ''
        cm = ''

        # print (pc1,pc2,' ',pc1[5],' ',pc2[3])
        if pc1[5] =='A' or  pc1[5] =='B':
            # Obtencion de tipoPAR en caso de parcelas de RC rústica
            if pc2[3] =='9':
                tipoPAR =  u'X-Descuento'
            else:
                tipoPAR =  u'RU-Rústica'
            cpo = pc1[6]+pc2[0:2]
            cpa = pc2[2:7]
            HOJA= pc1[0:6]
        else:
            # Obtencion de tipoPAR en caso de parcelas de RC urbana y diseminados
            if ldt[0:14] == 'TN DISEMINADOS':
                tipoPAR =  u'DI- Diseminado'
            else:
                tipoPAR = u'UR-Urbana'
            cpo = pc1[0:5]
            cpa = pc1[5:7]
            HOJA = pc2

        # print tipoPAR
        # print result[0]
        # print pc1+pc2 +' '+ ldt

        # tipoPAR = 'N'         #0 - TIPO DE PARCELA (Urbana, Rústica)
        codnomPRO = ''          #1 - Código y nombre de provincia
        codnomMUN = ''          #2 - Código y nombre de municipio
        message = ''            #3 - Contador de BI, CONS y SUBP
        listaSUBP = ''          #4 - Listado del contenido de los datos de supparcelas
        listaCONSTRU = ''       #5 - Listado del contenido de los datos de construcciones
        supTOTAL = 0            #6 - Superficie de la parcela
        supCONSTR = 0           #7 - Superficie construida
        DATOSURBA = ''          #8- Datos generales parcela urbana
        cp = 0                  #9- Código de la provincia
        cm = ''                 #10- Código del Municipio
        cmc = 0                 #11- Código del Municipio
        REFCAT = RC14       #12- REFCAT completa (20 dígitos)
        cn = 'N'                #13- Tipo parcela R, U, D, X
        cv =  ''                #16- Codigo de la via
        pnp = 0                 #17- Numero de la via
        np = ''                 #18- Nombre de Provincia
        nm = ''                 #19- Nombre de Municipio
        CAT_NMSPC = 'ES.SDGC.CP'#20- nmspc del GML ES.SDGC.CP,  ES.LOCAL.CP
        PARAJE = 's/d'          #21- NOMBRE PARAJE
        direccion = ldt         #21- Dato Dirección en catastro
        codine = str(cp)+str(cm)

        # Se ejecuta la consulta a catastro datos dado un RC
        # result = self.fun.consultaCatastroDATPARCELA(RC14)
        result = self.fun.consultaCatastroDATPARCELA(RC14, 'SI')
        # print (result)

        if result[:5] == 'ERROR':
            # Recibe error porque no hay Respuesta de catastro -Consulta_DNPRC-
            message = result
            listaSUBP = result
            listaCONSTRU = result

            QApplication.restoreOverrideCursor()
            self.iface.mainWindow().statusBar().clearMessage()

        else:
            codnomPRO = result[1]      #1 - Código y nombre de provincia
            codnomMUN = result[2]      #2 - Código y nombre de municipio
            message = result[3]        #3 - Contador de BI, CONS y SUBP
            listaSUBP = result[4]      #4 - Listado del contenido de los datos de supparcelas
            listaCONSTRU = result[5]   #5 - Listado del contenido de los datos de construcciones
            supTOTAL = result[6]       #6 - Superficie de la parcela
            supCONSTR = result[7]      #7 - Superficie construida
            DATOSURBA = result[8]      #8- Datos generales parcela urbana
            cp = result[9]             #9- Código de la provincia
            cm = result[10]            #10- Código del Municipio
            cmc = result[11]           #11- Código del Municipio
            REFCAT = result[12]        #12- REFCAT completa (20 dígitos)
            cn = result[13]            #13- Tipo parcela R, U, D, X
            cpo = result[14]           #14- Poligono
            cpa = result[15]           #15- Parcela
            cv =  result[16]           #16- Codigo de la via
            pnp = result[17]           #17- Numero de la via
            np = result[18]            #18- Nombre de Provincia
            nm = result[19]            #19- Nombre de Municipio
            CAT_NMSPC =   'ES.SDGC.CP' #20- nmspc del GML ES.SDGC.CP,  ES.LOCAL.CP
            PARAJE = result[21]        #21- NOMBRE PARAJE
            direccion = ldt            #22- Dato Dirección en catastro
            codine = str(cp)+str(cm)

        # Confeccionamos la URL de info catastral en SEC
        # url ANTIGUA
        # https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?
            # del=2&mun=81&RefC=02081A141090010000IY
        # url ACTUAL (ene/2019)
        # https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?
            # UrbRus=R&RefC=02075B012106870000RW&esBice=&RCBice1=&RCBice2=&DenoBice=&from=OVCBusqueda&pest=rc&RCCompleta=02075B01210687&final=&del=2&mun=75
        url = u'https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?'
        params = {
            'del': cp,
            'mun': cmc,
            'RefC': REFCAT}
        str_values = {}
        for k, v in params.items():
            str_values[k] = unicode(v).encode('utf-8')
        data = urllib.parse.urlencode(str_values)

        # data = urllib.urlencode(params)
        urlSEC= url+data
        print (urlSEC)

        # AÑADIR LA CAPA INDIVIDUAL DE LA PARCELA
        nombregrupo = 'PARCELAS CATASTRALES'            #Esto solo es interesante para la carga en grupo
        nombrecapa = 'PARCELAS CATASTRALES'
        tipolayer = 'shp'
        MAPA=0
        HOJA='XXXXXX'

        #                RC14,            PCAT1,       PCAT2,       EJERCICIO,     NUM_EXP,     CONTROL,     COORY,     VIA,
        #            NUMERO,       NUMERODUP,     NUMSYMBOL,     AREA,    FECHAALTA,     FECHABAJA,     MAPA,     DELEGACIO,
        #            MUNICIPIO,      MASA,        HOJA,      TIPO,      PARCELA,       COORX,     NOM_MUNI,     CAT_NMSPC
        #            DIRECCION       PROVINCIA        REF_CAT            COD_INE,        PARAJE

        atributosDICT={ 'RC14':RC14, 'PCAT1':pc1, 'PCAT2':pc2, 'EJERCICIO':0, 'NUM_EXP':0, 'CONTROL':0, 'COORY':0, 'VIA':cv,
                    'NUMERO':pnp, 'NUMERODUP':0, 'NUMSYMBOL':0, 'AREA':0 ,'FECHAALTA':0,'FECHABAJA':0, 'MAPA':0, 'DELEGACIO':cp,
                    'MUNICIPIO':cmc,'MASA':cpo , 'HOJA':pc2,'TIPO':cn, 'PARCELA':cpa, 'COORX':0, 'NOM_MUNI':nm,'CAT_NMSPC':CAT_NMSPC,
                    'DIRECCION':ldt, 'PROVINCIA':np, 'REF_CAT':REFCAT,  'COD_INE':codine, 'PARAJE':PARAJE
                    }
        result = self.fun.cargarCapaParcelaCatastral(RC14,nombrecapa, atributosDICT, 'shp', srs)

        if result[0] =='ERROR':
            QApplication.restoreOverrideCursor()
            return
        layer = result[0]
        supTOTAL = result[1]
        # print 'supTOTAL= ', supTOTAL

        #Creación de la lista de valores a enviar al menú dialogo Parcela Catastral
        listaVALORES = [RC14,       #0 - REFCAT de 14 posiciones
                        tipoPAR,        #1 - TIPO DE PARCELA (Urbana, Rústica)
                        codnomPRO,      #2 - Código y nombre de provincia
                        codnomMUN,      #3 - Código y nombre de municipio
                        ldt,            #4 - Situación de la Parcela
                        message,        #5 - Contador de BI, CONS y SUBP
                        listaSUBP,      #6 - Listado del contenido de los datos de supparcelas
                        listaCONSTRU,   #7 - Listado del contenido de los datos de construcciones
                        supTOTAL,       #8 - Superficie de la parcela
                        supCONSTR,      #9 - Superficie construida
                        DATOSURBA,      #10- Datos generales parcela urbana
                        urlSEC,         #11- URL de Enlace a la SEC de la parcela
                        REFCAT          #12- REFCAT de 20 posiciones
                        ]
                        # tenemos que seguir metiendo datos

        # Se lanza el cuadro de diálogo de parcela
        result = self.rundialogparcela(listaVALORES)
        QApplication.restoreOverrideCursor()
        self.iface.mainWindow().statusBar().clearMessage()
        pass

    def activate(self):
        pass

    def deactivate(self):
        # self.action.setChecked(False)
        pass

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return False

    def getProvinciaText(self,cp):
        #print cp
        if cp == '02':
            return 'ALBACETE'
        elif cp == '13':
            return 'CIUDAD_REAL'
        elif cp == '16':
            return 'CUENCA'
        elif cp == '45':
            return 'TOLEDO'
        elif cp == '19':
            return 'GUADALAJARA'
        else:
            return 'OTRA'

    def rundialogparcela(self,listaVALORES):
        #Rutina de introducción de datos en el menú Parcela Catastral y apertura del menú

        self.dlg.logo.setPixmap(QPixmap(f':/plugins/{self.nombre_plugin}/iconos/catastroesp.jpg'))
        self.dlg.setWindowIcon(QIcon(f':/plugins/{self.nombre_plugin}/iconos/cat_identificador.jpg'))

        self.dlg.valREFCAT.setText(listaVALORES[0])
        self.dlg.valTIPO.setText(listaVALORES[1])
        self.dlg.valPROVINCIA.setText(listaVALORES[2])
        self.dlg.valMUNICIPIO.setText(listaVALORES[3])
        self.dlg.valSITUACION.setText(listaVALORES[4])
        self.dlg.valCUENTAS.setText(listaVALORES[5])
        self.dlg.valSUBPARC.setText(''.join(listaVALORES[6]))
        self.dlg.valCONSTRU.setText(''.join(listaVALORES[7]))

        self.dlg.valSUPTOTAL.setText(u'SUP: %s m2'%str(listaVALORES[8]))

        self.dlg.valSUPCONS.setText(u'SUP.Const: %s m2'%str(listaVALORES[9]))
        self.dlg.lblDATOSURBA.setText(listaVALORES[10])
        self.dlg.enlaceWEB.setText(u'<html><head/><body><p><a href="'+listaVALORES[11]+
            u'"><span style=" text-decoration: underline; color:#0000ff;">'+listaVALORES[12]+
            u'</span></a></p></body></html>')
        # https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?UrbRus=R&RefC=02075B012106870000RW&esBice=&RCBice1=&RCBice2=&DenoBice=&from=OVCBusqueda&pest=rc&RCCompleta=02075B01210687&final=&del=2&mun=75
        QApplication.restoreOverrideCursor()
        result = self.dlg.exec_()


        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def setIMGcatastro(self):
        self.dlg.setFixedSize(900, 500)

        pass


class catastroToolINF01(QgsMapTool):    ### TODO  ### REVISANDO NUEVO SISTEMA DE DATOS DE CAPA
    # Funcion creada por ASS
    # -----------  PERMITE IDENTIFICAR UNA PARCELA CATASTRAL AL PINCHARLA  -----------

    def __init__(self,canvas,iface,action):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        # self.conf_catastro_tool = conf_catastro_tool
        self.fun = Functions()
        self.qs = QSettings()
        
        self.nombre_plugin = os.path.basename(os.path.dirname(__file__))

        cursor = QCursor()
        cursor.setShape(Qt.CrossCursor)
        iface.mapCanvas().setCursor(cursor)
        self.iface = iface
        self.setAction(action)
        self.action = action
        self.url_catastro_municipios = self.qs.value(f'{self.nombre_plugin}/CATASTRO/url_catastro_municipio')
        self.dlg = catastroParcelaINFODialog(iface)

        QApplication.restoreOverrideCursor()
        self.dlg.setFixedSize(550, 500)
        self.dlg.btnIMGcatastro.setEnabled(False)
        # http://ovc.catastro.meh.es/OVCServWeb/OVCWcfLibres/OVCFotoFachada.svc/RecuperarFotoFachadaGet?ReferenciaCatastral=02055A02100200.jpeg
        self.dlg.btnIMGcatastro.clicked.connect(lambda: self.setIMGcatastro())

        self.dlg.btnREGPROP.setEnabled(True)
        self.dlg.btnREGPROP.clicked.connect(lambda: self.fun.BUSCRegistroCOMP( 'rfc', self.dlg.valREFCAT.toPlainText()))
        # Hace zoom a la parcela REGISTRAL en la web https://geoportal.registradores.org
        # https://geoportal.registradores.org/idtramite/ID02005200002291
        # https://geoportal.registradores.org/idufir/02005000756030
        # https://geoportal.registradores.org/rfc/7269302WH8876N

    def canvasPressEvent(self, event):
        pass

    def canvasMoveEvent(self, event):
        pass

    def canvasReleaseEvent(self, event):
        # ICONO DE ESPERA
        QApplication.setOverrideCursor(Qt.WaitCursor)
        progress = 'Cargando parcela catastral {txt}...'.format(txt='')
        self.iface.mainWindow().statusBar().showMessage(progress)

        #Get the click
        x = event.pos().x()
        y = event.pos().y()
        srs =  self.iface.mapCanvas().mapSettings().destinationCrs().authid()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        print ('Punto pinchado CAT: ', point )
        print ('srs = ', srs )


        # CONSULTA DE RC POR COORDENADAS - Se mete en functions.py
        try:
            result = self.fun.consultaCatastroXYtoRC(point[0], point[1] ,srs)
        except:
            QApplication.restoreOverrideCursor()
            resp = self.fun.showMessageYESNO( '- NO HAY RESPUESTA DE CATASTRO -','','Capas de Catastro' )
            self.iface.mainWindow().statusBar().clearMessage()
            return

        # print result[0]
        if result[0] == u'ERROR' or result[0] == 'E' or result[0] is None:
            QApplication.restoreOverrideCursor()
            # resp = self.fun.showMessageYESNO( '- NO HAY RESPUESTA DE CATASTRO -','','Capas de Catastro' )
            self.iface.mainWindow().statusBar().clearMessage()
            return

        RC14 = result[0]
        xml_txt = result [1]
        pc1 = result [2]
        pc2 = result [3]
        ldt = result [4]
        cp = ''
        cm = ''

        # print (pc1,pc2,' ',pc1[5],' ',pc2[3])
        if pc1[5] =='A' or  pc1[5] =='B':
            # Obtencion de tipoPAR en caso de parcelas de RC rústica
            if pc2[3] =='9':
                tipoPAR =  u'X-Descuento'
            else:
                tipoPAR =  u'RU-Rústica'
            cpo = pc1[6]+pc2[0:2]
            cpa = pc2[2:7]
            HOJA= pc1[0:6]
        else:
            # Obtencion de tipoPAR en caso de parcelas de RC urbana y diseminados
            if ldt[0:14] == 'TN DISEMINADOS':
                tipoPAR =  u'DI- Diseminado'
            else:
                tipoPAR = u'UR-Urbana'
            cpo = pc1[0:5]
            cpa = pc1[5:7]
            HOJA = pc2

        # print tipoPAR
        # print result[0]
        # print pc1+pc2 +' '+ ldt

        # DATOS PARCELA CON VARIABLES ESTANDARD
        datosParcela = {
            'RC14': RC14,       #12- REFCAT completa (20 dígitos)
            'CP':'',            #9- Código de la provincia
            'NP':'',            #18- Nombre de Provincia
            'CMC':'',           #11- Código del Municipio Catastro
            'NM':'',            #19- Nombre de Municipio
            'CM':'',            #10- Código del Municipio INE
            'DTR':'',
            'NEM':'',
            'NPA':'',           #21- NOMBRE PARAJE
            'CPO':'',           # Código de polígono
            'CPA':'',           # Código de parcela
            'TIP':'',           # Naturaleza del bien (UR urbano, RU rústico, ES especiales). En ES incluye tipo
            'LSU':'',           #4 - Listado del contenido de los datos de supparcelas
            'LEC':'',           #5 - Listado del contenido de los datos de construcciones
            'UEC':'', 
            'USO':'',
                                #6 - Superficie de la parcela
                                #7 - Superficie construida
            'CAT_NMSPC': 'ES.SDGC.CP',#20- nmspc del GML ES.SDGC.CP,  ES.LOCAL.CP
            'codnomPRO': '',          #1 - Código y nombre de provincia
            'codnomMUN': '',          #2 - Código y nombre de municipio
            'codine': str(cp)+str(cm),
            'message': '',            #3 - Contador de BI, CONS y SUBP
            }

        # tipoPAR = 'N'      #0 - TIPO DE PARCELA (Urbana, Rústica)
        # codnomPRO = ''          #1 - Código y nombre de provincia
        # codnomMUN = ''          #2 - Código y nombre de municipio
        # message = ''            #3 - Contador de BI, CONS y SUBP
        # listaSUBP = ''          #4 - Listado del contenido de los datos de supparcelas
        # listaCONSTRU = ''       #5 - Listado del contenido de los datos de construcciones
        # supTOTAL = 0            #6 - Superficie de la parcela
        # supCONSTR = 0           #7 - Superficie construida
        DATOSURBA = ''          #8- Datos generales parcela urbana
        # cp = 0                  #9- Código de la provincia
        # cm = ''                 #10- Código del Municipio
        # cmc = 0                 #11- Código del Municipio
        # REFCAT = RC14       #12- REFCAT completa (20 dígitos)
        cn = 'N'                #13- Tipo parcela R, U, D, X
        cv =  ''                #16- Codigo de la via
        pnp = 0                 #17- Numero de la via
        # np = ''                 #18- Nombre de Provincia
        # nm = ''                 #19- Nombre de Municipio
        # PARAJE = 's/d'          #21- NOMBRE PARAJE
        direccion = ldt         #21- Dato Dirección en catastro
        # codine = str(cp)+str(cm)

        # # tipoPAR = 'N'         #0 - TIPO DE PARCELA (Urbana, Rústica)
        # codnomPRO = ''          #1 - Código y nombre de provincia
        # codnomMUN = ''          #2 - Código y nombre de municipio
        # message = ''            #3 - Contador de BI, CONS y SUBP
        # listaSUBP = ''          #4 - Listado del contenido de los datos de supparcelas
        # listaCONSTRU = ''       #5 - Listado del contenido de los datos de construcciones
        # supTOTAL = 0            #6 - Superficie de la parcela
        # supCONSTR = 0           #7 - Superficie construida
        # DATOSURBA = ''          #8- Datos generales parcela urbana
        # cp = 0                  #9- Código de la provincia
        # cm = ''                 #10- Código del Municipio
        # cmc = 0                 #11- Código del Municipio
        # REFCAT = RC14       #12- REFCAT completa (20 dígitos)
        # cn = 'N'                #13- Tipo parcela R, U, D, X
        # cv =  ''                #16- Codigo de la via
        # pnp = 0                 #17- Numero de la via
        # np = ''                 #18- Nombre de Provincia
        # nm = ''                 #19- Nombre de Municipio
        # CAT_NMSPC = 'ES.SDGC.CP'#20- nmspc del GML ES.SDGC.CP,  ES.LOCAL.CP
        # PARAJE = 's/d'          #21- NOMBRE PARAJE
        # direccion = ldt         #21- Dato Dirección en catastro
        # codine = str(cp)+str(cm)

        # Se ejecuta la consulta a catastro datos dada una RC14
        result = self.fun.consultaCatastroDATPARCELA01(RC14, 'SI') ### TODO REVISAR
        print (result)

        if result[:5] == 'ERROR':
            # Recibe error porque no hay Respuesta de catastro -Consulta_DNPRC-
            message = result
            listaSUBP = result
            listaCONSTRU = result

            QApplication.restoreOverrideCursor()
            self.iface.mainWindow().statusBar().clearMessage()

        else:
            codnomPRO = result[1]      #1 - Código y nombre de provincia
            codnomMUN = result[2]      #2 - Código y nombre de municipio
            message = result[3]        #3 - Contador de BI, CONS y SUBP
            listaSUBP = result[4]      #4 - Listado del contenido de los datos de supparcelas
            listaCONSTRU = result[5]   #5 - Listado del contenido de los datos de construcciones
            supTOTAL = result[6]       #6 - Superficie de la parcela
            supCONSTR = result[7]      #7 - Superficie construida
            DATOSURBA = result[8]      #8- Datos generales parcela urbana
            cp = result[9]             #9- Código de la provincia
            cm = result[10]            #10- Código del Municipio
            cmc = result[11]           #11- Código del Municipio
            REFCAT = result[12]        #12- REFCAT completa (20 dígitos)
            cn = result[13]            #13- Tipo parcela R, U, D, X
            cpo = result[14]           #14- Poligono
            cpa = result[15]           #15- Parcela
            cv =  result[16]           #16- Codigo de la via
            pnp = result[17]           #17- Numero de la via
            np = result[18]            #18- Nombre de Provincia
            nm = result[19]            #19- Nombre de Municipio
            CAT_NMSPC =   'ES.SDGC.CP' #20- nmspc del GML ES.SDGC.CP,  ES.LOCAL.CP
            PARAJE = result[21]        #21- NOMBRE PARAJE
            direccion = ldt            #22- Dato Dirección en catastro
            codine = str(cp)+str(cm)

        # Confeccionamos la URL de info catastral en SEC
        # url ANTIGUA
        # https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?
            # del=2&mun=81&RefC=02081A141090010000IY
        # url ACTUAL (ene/2019)
        # https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?
            # UrbRus=R&RefC=02075B012106870000RW&esBice=&RCBice1=&RCBice2=&DenoBice=&from=OVCBusqueda&pest=rc&RCCompleta=02075B01210687&final=&del=2&mun=75
        url = u'https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?'
        params = {
            'del': cp,
            'mun': cmc,
            'RefC': REFCAT}
        str_values = {}
        for k, v in params.items():
            str_values[k] = unicode(v).encode('utf-8')
        data = urllib.parse.urlencode(str_values)

        # data = urllib.urlencode(params)
        urlSEC= url+data
        print (urlSEC)

        # AÑADIR LA CAPA INDIVIDUAL DE LA PARCELA
        nombregrupo = 'PARCELAS CATASTRALES'            #Esto solo es interesante para la carga en grupo
        nombrecapa = 'PARCELAS CATASTRALES'
        tipolayer = 'shp'
        MAPA=0
        HOJA='XXXXXX'

        #                RC14,            PCAT1,       PCAT2,       EJERCICIO,     NUM_EXP,     CONTROL,     COORY,     VIA,
        #            NUMERO,       NUMERODUP,     NUMSYMBOL,     AREA,    FECHAALTA,     FECHABAJA,     MAPA,     DELEGACIO,
        #            MUNICIPIO,      MASA,        HOJA,      TIPO,      PARCELA,       COORX,     NOM_MUNI,     CAT_NMSPC
        #            DIRECCION       PROVINCIA        REF_CAT            COD_INE,        PARAJE

        atributosDICT={ 'RC14':RC14, 'PCAT1':pc1, 'PCAT2':pc2, 'EJERCICIO':0, 'NUM_EXP':0, 'CONTROL':0, 'COORY':0, 'VIA':cv,
                    'NUMERO':pnp, 'NUMERODUP':0, 'NUMSYMBOL':0, 'AREA':0 ,'FECHAALTA':0,'FECHABAJA':0, 'MAPA':0, 'DELEGACIO':cp,
                    'MUNICIPIO':cmc,'MASA':cpo , 'HOJA':pc2,'TIPO':cn, 'PARCELA':cpa, 'COORX':0, 'NOM_MUNI':nm,'CAT_NMSPC':CAT_NMSPC,
                    'DIRECCION':ldt, 'PROVINCIA':np, 'REF_CAT':REFCAT,  'COD_INE':codine, 'PARAJE':PARAJE
                    }
        result = self.fun.cargarCapaParcelaCatastral(RC14,nombrecapa, atributosDICT, 'shp', srs)

        if result[0] =='ERROR':
            QApplication.restoreOverrideCursor()
            return
        layer = result[0]
        supTOTAL = result[1]
        # print 'supTOTAL= ', supTOTAL

        #Creación de la lista de valores a enviar al menú dialogo Parcela Catastral
        listaVALORES = [RC14,       #0 - REFCAT de 14 posiciones
                        tipoPAR,        #1 - TIPO DE PARCELA (Urbana, Rústica)
                        codnomPRO,      #2 - Código y nombre de provincia
                        codnomMUN,      #3 - Código y nombre de municipio
                        ldt,            #4 - Situación de la Parcela
                        message,        #5 - Contador de BI, CONS y SUBP
                        listaSUBP,      #6 - Listado del contenido de los datos de supparcelas
                        listaCONSTRU,   #7 - Listado del contenido de los datos de construcciones
                        supTOTAL,       #8 - Superficie de la parcela
                        supCONSTR,      #9 - Superficie construida
                        DATOSURBA,      #10- Datos generales parcela urbana
                        urlSEC,         #11- URL de Enlace a la SEC de la parcela
                        REFCAT          #12- REFCAT de 20 posiciones
                        ]
                        # tenemos que seguir metiendo datos

        # Se lanza el cuadro de diálogo de parcela
        result = self.rundialogparcela(listaVALORES)
        QApplication.restoreOverrideCursor()
        self.iface.mainWindow().statusBar().clearMessage()
        pass

    def activate(self):
        pass

    def deactivate(self):
        # self.action.setChecked(False)
        pass

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return False

    def getProvinciaText(self,cp):
        #print cp
        if cp == '02':
            return 'ALBACETE'
        elif cp == '13':
            return 'CIUDAD_REAL'
        elif cp == '16':
            return 'CUENCA'
        elif cp == '45':
            return 'TOLEDO'
        elif cp == '19':
            return 'GUADALAJARA'
        else:
            return 'OTRA'

    def rundialogparcela(self,listaVALORES):
        #Rutina de introducción de datos en el menú Parcela Catastral y apertura del menú

        self.dlg.logo.setPixmap(QPixmap(f':/plugins/{self.nombre_plugin}/iconos/catastroesp.jpg'))
        self.dlg.setWindowIcon(QIcon(f':/plugins/{self.nombre_plugin}/iconos/cat_identificador.jpg'))

        self.dlg.valREFCAT.setText(listaVALORES[0])
        self.dlg.valTIPO.setText(listaVALORES[1])
        self.dlg.valPROVINCIA.setText(listaVALORES[2])
        self.dlg.valMUNICIPIO.setText(listaVALORES[3])
        self.dlg.valSITUACION.setText(listaVALORES[4])
        self.dlg.valCUENTAS.setText(listaVALORES[5])
        self.dlg.valSUBPARC.setText(''.join(listaVALORES[6]))
        self.dlg.valCONSTRU.setText(''.join(listaVALORES[7]))

        self.dlg.valSUPTOTAL.setText(u'SUP: %s m2'%str(listaVALORES[8]))

        self.dlg.valSUPCONS.setText(u'SUP.Const: %s m2'%str(listaVALORES[9]))
        self.dlg.lblDATOSURBA.setText(listaVALORES[10])
        self.dlg.enlaceWEB.setText(u'<html><head/><body><p><a href="'+listaVALORES[11]+
            u'"><span style=" text-decoration: underline; color:#0000ff;">'+listaVALORES[12]+
            u'</span></a></p></body></html>')
        # https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?UrbRus=R&RefC=02075B012106870000RW&esBice=&RCBice1=&RCBice2=&DenoBice=&from=OVCBusqueda&pest=rc&RCCompleta=02075B01210687&final=&del=2&mun=75
        QApplication.restoreOverrideCursor()
        result = self.dlg.exec_()


        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def setIMGcatastro(self):
        self.dlg.setFixedSize(900, 500)

        pass


class catastroCargaPARC(QgsMapTool):
    # Funcion creada por ASS
    # -----------  PERMITE IDENTIFICAR UNA PARCELA CATASTRAL AL PINCHARLA  -----------

    def __init__(self,canvas,iface,action):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        # self.conf_catastro_tool = conf_catastro_tool
        self.fun = Functions()
        self.qs = QSettings()
        
        self.nombre_plugin = os.path.basename(os.path.dirname(__file__))

        cursor = QCursor()
        cursor.setShape(Qt.CrossCursor)
        iface.mapCanvas().setCursor(cursor)
        self.iface = iface
        self.setAction(action)
        self.action = action
        self.url_catastro_municipios = self.qs.value(f'{self.nombre_plugin}/CATASTRO/url_catastro_municipio')
        self.dlg = catastroParcelaINFODialog(iface)
        QApplication.restoreOverrideCursor()
        self.dlg.setFixedSize(550, 500)
        self.dlg.btnIMGcatastro.setEnabled(False)
        # http://ovc.catastro.meh.es/OVCServWeb/OVCWcfLibres/OVCFotoFachada.svc/RecuperarFotoFachadaGet?ReferenciaCatastral=02055A02100200.jpeg
        self.dlg.btnIMGcatastro.clicked.connect(lambda: self.setIMGcatastro())

        self.dlg.btnREGPROP.setEnabled(True)
        self.dlg.btnREGPROP.clicked.connect(lambda: self.fun.BUSCRegistroCOMP( 'rfc', self.dlg.valREFCAT.toPlainText()))
        # Hace zoom a la parcela REGISTRAL en la web https://geoportal.registradores.org
        # https://geoportal.registradores.org/idtramite/ID02005200002291
        # https://geoportal.registradores.org/idufir/02005000756030
        # https://geoportal.registradores.org/rfc/7269302WH8876N

    def canvasPressEvent(self, event):
        pass

    def canvasMoveEvent(self, event):
        pass

    def canvasReleaseEvent(self, event):
        # ICONO DE ESPERA
        QApplication.setOverrideCursor(Qt.WaitCursor)
        progress = 'Cargando parcela catastral {txt}...'.format(txt='')
        self.iface.mainWindow().statusBar().showMessage(progress)

        #Get the click
        x = event.pos().x()
        y = event.pos().y()
        srs =  self.iface.mapCanvas().mapSettings().destinationCrs().authid()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)

        # CONSULTA DE RC POR COORDENADAS - Se mete en functions.py
        result = self.fun.consultaCatastroXYDISTtoRC(point[0], point[1] ,srs)

        # print (result)
        if result[0] == u'ERROR' or result[0] == 'E' or result[0] is None:
            QApplication.restoreOverrideCursor()
            # resp = self.fun.showMessageYESNO( '- NO HAY RESPUESTA DE CATASTRO -','','Capas de Catastro' )
            self.iface.mainWindow().statusBar().clearMessage()
            return

        RC14 = result[0]
        xml_txt = result [1]
        pc1 = result [2]
        pc2 = result [3]
        ldt = result [4]
        cp = result [5]
        cm = result [6]
        tipoPAR = result [7]
        listRC = result [8]

        # print (pc1,pc2,' ',pc1[5],' ',pc2[3])
        if pc1[5] =='A' or  pc1[5] =='B':
            # Obtencion de tipoPAR en caso de parcelas de RC rústica
            if pc2[3] =='9':
                tipoPAR =  u'X-Descuento'
            else:
                tipoPAR =  u'RU-Rústica'
            cpo = pc1[6]+pc2[0:2]
            cpa = pc2[2:7]
            HOJA= pc1[0:6]
        else:
            # Obtencion de tipoPAR en caso de parcelas de RC urbana y diseminados
            if ldt[0:14] == 'TN DISEMINADOS':
                tipoPAR =  u'DI- Diseminado'
            else:
                tipoPAR = u'UR-Urbana'
            cpo = pc1[0:5]
            cpa = pc1[5:7]
            HOJA = pc2

        # tipoPAR = 'N'        #0 - TIPO DE PARCELA (Urbana, Rústica)
        codnomPRO = ''       #1 - Código y nombre de provincia
        codnomMUN = ''       #2 - Código y nombre de municipio
        message = ''         #3 - Contador de BI, CONS y SUBP
        listaSUBP = ''       #4 - Listado del contenido de los datos de supparcelas
        listaCONSTRU = ''    #5 - Listado del contenido de los datos de construcciones
        supTOTAL = 0         #6 - Superficie de la parcela
        supCONSTR = 0        #7 - Superficie construida
        DATOSURBA = ''       #8- Datos generales parcela urbana
        cp = ''              #9- Código de la provincia
        cm = ''              #10- Código del Municipio
        cmc = ''             #11- Código del Municipio
        REFCAT = RC14    #12- REFCAT completa (20 dígitos)
        cn = 'N'             #13- Tipo parcela R, U, D, X
        cv =  ''             #16- Codigo de la via
        pnp = ''             #17- Numero de la via


        # Se ejecuta la consulta a catastro datos dado un RC
        result = self.fun.consultaCatastroDATPARCELA(RC14, 'SI')
        # print (result)

        if result[:5] == 'ERROR':
            # Recibe error porque no hay Respuesta de catastro -Consulta_DNPRC-
            message = result
            listaSUBP = result
            listaCONSTRU = result

            QApplication.restoreOverrideCursor()
            self.iface.mainWindow().statusBar().clearMessage()

        else:
            codnomPRO = result[1]      #1 - Código y nombre de provincia
            codnomMUN = result[2]      #2 - Código y nombre de municipio
            message = result[3]        #3 - Contador de BI, CONS y SUBP
            listaSUBP = result[4]      #4 - Listado del contenido de los datos de supparcelas
            listaCONSTRU = result[5]   #5 - Listado del contenido de los datos de construcciones
            supTOTAL = result[6]       #6 - Superficie de la parcela
            supCONSTR = result[7]      #7 - Superficie construida
            DATOSURBA = result[8]      #8- Datos generales parcela urbana
            cp = result[9]             #9- Código de la provincia
            cm = result[10]            #10- Código del Municipio
            cmc = result[11]           #11- Código del Municipio
            REFCAT = result[12]        #12- REFCAT completa (20 dígitos)
            cn = result[13]            #13- Tipo parcela R, U, D, X
            cpo = result[14]           #14- Poligono
            cpa = result[15]           #15- Parcela
            cv =  result[16]           #16- Codigo de la via
            pnp = result[17]           #17- Numero de la via
            np = result[18]            #18- Nombre de Provincia
            nm = result[19]            #19- Nombre de Municipio
            CAT_NMSPC =   'ES.SDGC.CP' #20- nmspc del GML ES.SDGC.CP,  ES.LOCAL.CP
            PARAJE = result[19]        #21- Paraje

        # Confeccionamos la URL de info catastral en SEC
        # url ANTIGUA
        # https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?
            # del=2&mun=81&RefC=02081A141090010000IY
        # url ACTUAL (ene/2019)
        # https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?
            # UrbRus=R&RefC=02075B012106870000RW&esBice=&RCBice1=&RCBice2=&DenoBice=&from=OVCBusqueda&pest=rc&RCCompleta=02075B01210687&final=&del=2&mun=75
        url = u'https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?'
        params = {
            'del': cp,
            'mun': cmc,
            'RefC': REFCAT}
        str_values = {}
        for k, v in params.items():
            str_values[k] = unicode(v).encode('utf-8')
        data = urllib.parse.urlencode(str_values)

        # data = urllib.urlencode(params)
        urlSEC= url+data
        print (urlSEC)

        # AÑADIR LA CAPA INDIVIDUAL DE LA PARCELA
        nombregrupo = 'PARCELAS CATASTRALES'            #Esto solo es interesante para la carga en grupo
        nombrecapa = 'PARCELAS CATASTRALES'
        tipolayer = 'shp'
        MAPA=0
        HOJA='XXXXXX'

        #           RC14    ,PCAT1 ,PCAT2,EJERCICIO,NUM_EXP,CONTROL,COORY,VIA,NUMERO,NUMERODUP,NUMSYMBOL,AREA    ,FECHAALTA,FECHABAJA,MAPA ,DELEGACIO,MUNICIPIO,MASA,HOJA    ,TIPO   ,PARCELA,COORX,NOM_MUNI
        #atributos=[RC14, pc1  ,pc2  ,0        ,0      ,0      ,0    ,cv ,pnp   ,0        ,0        ,0       ,0        ,0        ,0    ,cp       ,cmc      ,cpo ,pc2     ,cn     ,cpa    ,0    ,nm      ,CAT_NMSPC ]
        #result = self.fun.cargarCapaParcelaCatastroSHP(RC14,nombrecapa, atributos, 'shp', srs)

        #                RC14,            PCAT1,       PCAT2,       EJERCICIO,     NUM_EXP,     CONTROL,     COORY,     VIA,
        #            NUMERO,       NUMERODUP,     NUMSYMBOL,     AREA,    FECHAALTA,     FECHABAJA,     MAPA,     DELEGACIO,
        #            MUNICIPIO,      MASA,        HOJA,      TIPO,      PARCELA,       COORX,     NOM_MUNI,     CAT_NMSPC
        atributosDICT={ 'RC14':RC14, 'PCAT1':pc1, 'PCAT2':pc2, 'EJERCICIO':0, 'NUM_EXP':0, 'CONTROL':0, 'COORY':0, 'VIA':cv,
                    'NUMERO':pnp, 'NUMERODUP':0, 'NUMSYMBOL':0, 'AREA':0 ,'FECHAALTA':0,'FECHABAJA':0, 'MAPA':0, 'DELEGACIO':cp,
                    'MUNICIPIO':cmc,'MASA':cpo , 'HOJA':pc2,'TIPO':cn, 'PARCELA':cpa, 'COORX':0, 'NOM_MUNI':nm,'CAT_NMSPC':CAT_NMSPC,
                    'PARAJE':PARAJE
                    }
        result = self.fun.cargarCapaParcelaCatastral(RC14,nombrecapa, atributosDICT, 'shp', srs)

        if result[0] =='ERROR':
            QApplication.restoreOverrideCursor()
            return
        layer = result[0]
        supTOTAL = result[1]
        # print 'supTOTAL= ', supTOTAL

        #Creación de la lista de valores a enviar al menú dialogo Parcela Catastral
        listaVALORES = [RC14,       #0 - REFCAT de 14 posiciones
                        tipoPAR,        #1 - TIPO DE PARCELA (Urbana, Rústica)
                        codnomPRO,      #2 - Código y nombre de provincia
                        codnomMUN,      #3 - Código y nombre de municipio
                        ldt,            #4 - Situación de la Parcela
                        message,        #5 - Contador de BI, CONS y SUBP
                        listaSUBP,      #6 - Listado del contenido de los datos de supparcelas
                        listaCONSTRU,   #7 - Listado del contenido de los datos de construcciones
                        supTOTAL,       #8 - Superficie de la parcela
                        supCONSTR,      #9 - Superficie construida
                        DATOSURBA,      #10- Datos generales parcela urbana
                        urlSEC,         #11- URL de Enlace a la SEC de la parcela
                        REFCAT          #12- REFCAT de 20 posiciones
                        ]
                        # tenemos que seguir metiendo datos

        # Se lanza el cuadro de diálogo de parcela
        result = self.rundialogparcela(listaVALORES, listRC)
        QApplication.restoreOverrideCursor()
        self.iface.mainWindow().statusBar().clearMessage()
        pass

    def activate(self):
        pass

    def deactivate(self):
        # self.action.setChecked(False)
        pass

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return False

    def getProvinciaText(self,cp):
        #print cp
        if cp == '02':
            return 'ALBACETE'
        elif cp == '13':
            return 'CIUDAD_REAL'
        elif cp == '16':
            return 'CUENCA'
        elif cp == '45':
            return 'TOLEDO'
        elif cp == '19':
            return 'GUADALAJARA'
        else:
            return 'OTRA'

    def rundialogparcela(self,listaVALORES,listRC):
        #Rutina de introducción de datos en el menú Parcela Catastral y apertura del menú

        self.dlg.logo.setPixmap(QPixmap(f':/plugins/{self.nombre_plugin}/iconos/catastroesp.jpg'))
        self.dlg.setWindowIcon(QIcon(f':/plugins/{self.nombre_plugin}/iconos/cat_identificador.jpg'))

        self.dlg.valREFCAT.setText(listaVALORES[0])
        self.dlg.valTIPO.setText(listaVALORES[1])
        self.dlg.valPROVINCIA.setText(listaVALORES[2])
        self.dlg.valMUNICIPIO.setText(listaVALORES[3])
        self.dlg.valSITUACION.setText(listaVALORES[4])
        self.dlg.valCUENTAS.setText(listaVALORES[5])
        self.dlg.valSUBPARC.setText(''.join(listaVALORES[6]))
        self.dlg.valCONSTRU.setText(''.join(listaVALORES[7]))

        self.dlg.valSUPTOTAL.setText(u'SUP: %s m2'%str(listaVALORES[8]))

        self.dlg.valSUPCONS.setText(u'SUP.Const: %s m2'%str(listaVALORES[9]))
        self.dlg.lblDATOSURBA.setText(listaVALORES[10])
        self.dlg.enlaceWEB.setText(u'<html><head/><body><p><a href="'+listaVALORES[11]+
            u'"><span style=" text-decoration: underline; color:#0000ff;">'+listaVALORES[12]+
            u'</span></a></p></body></html>')
        # https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?UrbRus=R&RefC=02075B012106870000RW&esBice=&RCBice1=&RCBice2=&DenoBice=&from=OVCBusqueda&pest=rc&RCCompleta=02075B01210687&final=&del=2&mun=75

        # Colocamos la lista de RCS
        valoresRCs = ''
        for RC in listRC:
            if RC['RC14'] != listaVALORES[0]:
                valoresRCs += u'%s %s (%s m.)\n'%(RC['RC14'], RC['tipoPar'], RC['dis'])
        self.dlg.listaRCcolind.setText(valoresRCs)


        QApplication.restoreOverrideCursor()
        result = self.dlg.exec_()


        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def setIMGcatastro(self):
        self.dlg.setFixedSize(900, 500)

        pass



class catastroBorraParc(QgsMapTool):
    # Funcion creada por ASS
    # -----------  PERMITE BORRAR UNA PARCELA CATASTRAL AL PINCHARLA  -----------

    def __init__(self,canvas,iface,action):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.fun = Functions()
        self.qs = QSettings()
        
        self.nombre_plugin = os.path.basename(os.path.dirname(__file__))

        cursor = QCursor()
        cursor.setShape(Qt.CrossCursor)
        iface.mapCanvas().setCursor(cursor)
        self.iface = iface
        self.setAction(action)
        self.action = action
        self.url_catastro_municipios = self.qs.value(f'{self.nombre_plugin}/CATASTRO/url_catastro_municipio')
        QApplication.restoreOverrideCursor()

    def canvasReleaseEvent(self, event):
        # ICONO DE ESPERA
        QApplication.setOverrideCursor(Qt.WaitCursor)
        progress = 'Borrado de parcela catastral'.format(txt='')
        self.iface.mainWindow().statusBar().showMessage(progress)

        # Obtener las coordenadas del clik y transformarlas al SRS
        x = event.pos().x()
        y = event.pos().y()
        srs =  self.iface.mapCanvas().mapSettings().destinationCrs().authid()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)

        try:
            layerPARC = QgsProject.instance().mapLayersByName('PARCELAS CATASTRALES')[0]
        except:
            QApplication.restoreOverrideCursor()
            text = u'NO HAY PARCELA CARGADA EN ESTA POSICIÓN'
            resp = self.fun.showMessage( text )
            return

        MyPnt = QgsGeometry.fromPointXY(QgsPointXY(point[0],point[1]))
        feats = layerPARC.getFeatures()
        for feat in feats:
         if MyPnt.intersects(feat.geometry()):
             # featureID = feat.id()
             feature = feat
        try:
            print(feature['RC14'])
        except:
            QApplication.restoreOverrideCursor()
            text = u'NO HAY PARCELA CARGADA EN ESTA POSICIÓN'
            resp = self.fun.showMessage( text )
            return

        RC14sel = feature['RC14']

        # Obtener una lista de los features de la capa, y se crea una lista vacía
        caps = layerPARC.dataProvider().capabilities()
        if caps & QgsVectorDataProvider.DeleteFeatures:
            dfeats = []
            featureslayerPARC = layerPARC.getFeatures()

            for featLayerPARC in featureslayerPARC:      #Cada elemento de la capa PARCELAS. Se llamará featLayerPARC
                RC14 = featLayerPARC['RC14']
                if RC14 == RC14sel:
                    dfeats.append(featLayerPARC.id())

            res = layerPARC.dataProvider().deleteFeatures(dfeats)
            progress = 'Borrado de parcela catastral %s'%(RC14)
            self.iface.mainWindow().statusBar().showMessage(progress)

            layerPARC.triggerRepaint()
            layerPARC.updateExtents()

        QApplication.restoreOverrideCursor()


class catastroASIGNA_RC(QgsMapTool):
    # Funcion creada por ASS
    #   INICIADA 20/3/25
    # -----------  PERMITE ASIGNAR AL ELEMENTO DE LA CAPA ACTIVA, VALORES DE LA PARCELA CATASTRAL DEL PUNTO PINCHADO  -----------

    def __init__(self,canvas,iface,action):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.fun = Functions()
        self.qs = QSettings()
        
        self.nombre_plugin = os.path.basename(os.path.dirname(__file__))

        cursor = QCursor()
        cursor.setShape(Qt.CrossCursor)
        iface.mapCanvas().setCursor(cursor)
        self.iface = iface
        self.setAction(action)
        self.action = action
        self.url_catastro_municipios = self.qs.value(f'{self.nombre_plugin}/CATASTRO/url_catastro_municipio')
        QApplication.restoreOverrideCursor()

    def canvasReleaseEvent(self, event):
        # ICONO DE ESPERA
        QApplication.setOverrideCursor(Qt.WaitCursor)
        progress = 'Borrado de parcela catastral'.format(txt='')
        self.iface.mainWindow().statusBar().showMessage(progress)

        # Obtener las coordenadas del clik y transformarlas al SRS
        x = event.pos().x()
        y = event.pos().y()
        srs =  self.iface.mapCanvas().mapSettings().destinationCrs().authid()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)

        # CONSULTA DE RC POR COORDENADAS - Se mete en functions.py
        try:
            result = self.fun.consultaCatastroXYtoRC(point[0], point[1] ,srs)
        except:
            QApplication.restoreOverrideCursor()
            resp = self.fun.showMessageYESNO( '- NO HAY RESPUESTA DE CATASTRO -','','Capas de Catastro' )
            self.iface.mainWindow().statusBar().clearMessage()
            return
            
        # print (result)
        if result[0] == u'ERROR' or result[0] == 'E' or result[0] is None:
            QApplication.restoreOverrideCursor()
            # resp = self.fun.showMessageYESNO( '- NO HAY RESPUESTA DE CATASTRO -','','Capas de Catastro' )
            self.iface.mainWindow().statusBar().clearMessage()
            return

        RC14 = result[0]
        xml_txt = result [1]
        pc1 = result [2]
        pc2 = result [3]
        ldt = result [4]
        cp = ''
        cm = ''

        print (RC14, pc1,pc2,' ',pc1[5],' ',pc2[3])
        
        if pc1[5] =='A' or  pc1[5] =='B':
            # Obtencion de tipoPAR en caso de parcelas de RC rústica
            if pc2[3] =='9':
                tipoPAR =  u'X-Descuento'
            else:
                tipoPAR =  u'RU-Rústica'
            cpo = pc1[6]+pc2[0:2]
            cpa = pc2[2:7]
            HOJA= pc1[0:6]
        else:
            # Obtencion de tipoPAR en caso de parcelas de RC urbana y diseminados
            if ldt[0:14] == 'TN DISEMINADOS':
                tipoPAR =  u'DI- Diseminado'
            else:
                tipoPAR = u'UR-Urbana'
            cpo = pc1[0:5]
            cpa = pc1[5:7]
            HOJA = pc2

        # tipoPAR = 'N'         #0 - TIPO DE PARCELA (Urbana, Rústica)
        codnomPRO = ''          #1 - Código y nombre de provincia
        codnomMUN = ''          #2 - Código y nombre de municipio
        message = ''            #3 - Contador de BI, CONS y SUBP
        listaSUBP = ''          #4 - Listado del contenido de los datos de supparcelas
        listaCONSTRU = ''       #5 - Listado del contenido de los datos de construcciones
        supTOTAL = 0            #6 - Superficie de la parcela
        supCONSTR = 0           #7 - Superficie construida
        DATOSURBA = ''          #8- Datos generales parcela urbana
        cp = 0                  #9- Código de la provincia
        cm = ''                 #10- Código del Municipio
        cmc = 0                 #11- Código del Municipio
        REFCAT = RC14       #12- REFCAT completa (20 dígitos)
        cn = 'N'                #13- Tipo parcela R, U, D, X
        cv =  ''                #16- Codigo de la via
        pnp = 0                 #17- Numero de la via
        np = ''                 #18- Nombre de Provincia
        nm = ''                 #19- Nombre de Municipio
        CAT_NMSPC = 'ES.SDGC.CP'#20- nmspc del GML ES.SDGC.CP,  ES.LOCAL.CP
        direccion = ldt         #21- Dato Dirección en catastro
        codine = str(cp)+str(cm)
        
        # Se ejecuta la consulta a catastro datos dado un RC
        result = self.fun.consultaCatastroDATPARCELA(RC14, 'SI')

        if result[:5] == 'ERROR':
            # Recibe error porque no hay Respuesta de catastro -Consulta_DNPRC-
            message = result
            listaSUBP = result
            listaCONSTRU = result

            QApplication.restoreOverrideCursor()
            self.iface.mainWindow().statusBar().clearMessage()

        else:   
            codnomPRO = result[1]      #1 - Código y nombre de provincia
            codnomMUN = result[2]      #2 - Código y nombre de municipio
            message = result[3]        #3 - Contador de BI, CONS y SUBP
            listaSUBP = result[4]      #4 - Listado del contenido de los datos de supparcelas
            listaCONSTRU = result[5]   #5 - Listado del contenido de los datos de construcciones
            supTOTAL = result[6]       #6 - Superficie de la parcela
            supCONSTR = result[7]      #7 - Superficie construida
            DATOSURBA = result[8]      #8- Datos generales parcela urbana
            cp = result[9]             #9- Código de la provincia
            cm = result[10]            #10- Código del Municipio
            cmc = result[11]           #11- Código del Municipio
            REFCAT = result[12]        #12- REFCAT completa (20 dígitos)
            cn = result[13]            #13- Tipo parcela R, U, D, X
            cpo = result[14]           #14- Poligono
            cpa = result[15]           #15- Parcela
            cv =  result[16]           #16- Codigo de la via
            pnp = result[17]           #17- Numero de la via
            np = result[18]            #18- Nombre de Provincia
            nm = result[19]            #19- Nombre de Municipio
            CAT_NMSPC =   'ES.SDGC.CP' #20- nmspc del GML ES.SDGC.CP,  ES.LOCAL.CP
            direccion = ldt            #21- Dato Dirección en catastro
            codine = str(cp)+str(cm)

        # atributosDICT={ 'RC14':RC14, 'PCAT1':pc1, 'PCAT2':pc2, 'EJERCICIO':0, 'NUM_EXP':0, 'CONTROL':0, 'COORY':0, 'VIA':cv,
                    # 'NUMERO':pnp, 'NUMERODUP':0, 'NUMSYMBOL':0, 'AREA':0 ,'FECHAALTA':0,'FECHABAJA':0, 'MAPA':0, 'DELEGACIO':cp,
                    # 'MUNICIPIO':cmc,'MASA':cpo , 'HOJA':pc2,'TIPO':cn, 'PARCELA':cpa, 'COORX':0, 'NOM_MUNI':nm,'CAT_NMSPC':CAT_NMSPC
                    # }
        atributosDICT={ 'RC14':RC14, 
                        'PCAT1':pc1, 
                        'PCAT2':pc2, 
                        'EJERCICIO':0, 
                        'NUM_EXP':0, 
                        'CONTROL':0, 
                        'COORY':0, 
                        'VIA':cv,
                        'NUMERO':pnp, 
                        'NUMERODUP':0, 
                        'NUMSYMBOL':0, 
                        'AREA':supTOTAL ,
                        'FECHAALTA':0,
                        'FECHABAJA':0, 
                        'MAPA':0, 
                        'DELEGACIO':cp,
                        'MUNICIPIO':cmc,
                        'MASA':cpo , 
                        'HOJA':pc2,
                        'TIPO':cn, 
                        'PARCELA':cpa, 
                        'COORX':0, 
                        'NOM_MUNI':nm,
                        'CAT_NMSPC':CAT_NMSPC,
                        'DIRECCION':ldt, 
                        'PROVINCIA':np, 
                        'REF_CAT':REFCAT,  
                        'COD_INE':codine
                    }
        self.asignaAtribCatastro(point, atributosDICT)

        QApplication.restoreOverrideCursor()

        
    def asignaAtribCatastro(self, point, atributosDICT):
        # # Se asignan los atributos al polígono de la capa activa en el punto pinchado
        # #   point = punto pinchado
        # #   atributosDICT, dictionary donde buscar los campos en la capa activa.
        # #       Solo son obligatorios, y se crearán si no existen los campos:
        # #           'RC14', tipo CHARACTER
        # #           'CAT_NMSPC', tipo CHARACTER
        
        # from qgis.core import QgsWkbTypes, QgsGeometry, QgsPointXY, QgsField
        # from PyQt5.QtCore import QVariant
        # from PyQt5.QtWidgets import QApplication

        layer = self.iface.activeLayer()

        if not layer:
            self.fun.showMessageERR("No hay ninguna capa activa.")
            QApplication.restoreOverrideCursor()
            return

        if layer.geometryType() != QgsWkbTypes.PolygonGeometry:
            self.fun.showMessageERR(f"La capa activa {layer.name()} no es de tipo polígono.")
            QApplication.restoreOverrideCursor()
            return

        # Convertir todos los nombres de atributos a mayúsculas
        atributosDICT = {k.upper(): v for k, v in atributosDICT.items()}

        # Obtener los campos de la capa en un diccionario {NOMBRE_MAYUS: QgsField}
        fields = layer.fields()
        fields_dict = {field.name().upper(): field for field in fields}

        # Campos obligatorios y sus tipos
        campos_obligatorios = {'RC14': QVariant.String, 'CAT_NMSPC': QVariant.String}

        nuevos_campos = []
        for campo, tipo in campos_obligatorios.items():
            if campo not in fields_dict:
                nuevos_campos.append(QgsField(campo, tipo))  

        if nuevos_campos:
            layer.startEditing()
            layer.dataProvider().addAttributes(nuevos_campos)
            layer.updateFields()
            layer.commitChanges()

            fields = layer.fields()
            fields_dict = {field.name().upper(): field for field in fields}

        # Buscar el polígono en el punto pinchado
        point_geometry = QgsGeometry.fromPointXY(QgsPointXY(point))
        
        layer.startEditing()

        try:
            for feature in layer.getFeatures():
                if feature.geometry().contains(point_geometry):
                    for field_name, value in atributosDICT.items():
                        field_name_upper = field_name.upper()
                        if field_name_upper in fields_dict:
                            field = fields_dict[field_name_upper]
                            field_type = field.type()

                            # Convertir valor al tipo correcto
                            try:
                                if field_type == QVariant.Int:
                                    value = int(value)
                                elif field_type == QVariant.Double:
                                    value = float(value)
                                elif field_type == QVariant.String:
                                    value = str(value)
                                elif field_type == QVariant.Bool:
                                    value = bool(value)

                                feature.setAttribute(field.name(), value)
                                print(f'Asignado {value} ({type(value).__name__}) a {field.name()}')
                            except (ValueError, TypeError):
                                print(f'No se pudo convertir {value} a {field.name()} ({field.typeName()})')

                    layer.updateFeature(feature)
                    layer.commitChanges()
                    self.fun.showMessage(f"Atributos asignados correctamente\n\nRC {feature[fields_dict['RC14'].name()]}")
                    return

            layer.rollBack()
            self.fun.showMessageERR("No se encontró ningún polígono en el punto pinchado.")

        except Exception as e:
            layer.rollBack()
            self.fun.showMessageERR(f"Error al modificar la capa: {str(e)}")
        
        QApplication.restoreOverrideCursor()

        
        
        
        
        
        # layer = self.iface.activeLayer()

        # if not layer:
            # txt = "No hay ninguna capa activa."
            # QApplication.restoreOverrideCursor()
            # self.fun.showMessageERR(txt)
            # return

        # if layer.geometryType() != QgsWkbTypes.PolygonGeometry:
            # txt = f"La capa activa\n\n{layer.name()}  - ({QgsWkbTypes.geometryDisplayString(layer.geometryType())})\n\nNo es de tipo polígono."
            # QApplication.restoreOverrideCursor()
            # self.fun.showMessageERR(txt)
            # return

        # # Obtener los campos de la capa en un diccionario {nombre_lower: QgsField}
        # fields = layer.fields()
        # fields_dict = {field.name().lower(): field for field in fields}

        # # Campos obligatorios y sus tipos
        # campos_obligatorios = {'rc14': QVariant.String, 'cat_nmspc': QVariant.String}

        # nuevos_campos = []
        # for campo, tipo in campos_obligatorios.items():
            # if campo not in fields_dict:
                # nuevos_campos.append(QgsField(campo.upper(), tipo))  # Añadirlo en mayúsculas

        # if nuevos_campos:
            # layer.dataProvider().addAttributes(nuevos_campos)
            # layer.updateFields()
            # fields = layer.fields()  # Refrescar los campos después de añadirlos
            # fields_dict = {field.name().lower(): field for field in fields}  # Volver a crear el diccionario

        # # Buscar el polígono en el punto pinchado
        # point_geometry = QgsGeometry.fromPointXY(QgsPointXY(point))

        # # Iniciar edición si no está en modo edición
        # if not layer.isEditable():
            # layer.startEditing()

        # for feature in layer.getFeatures():
            # if feature.geometry().contains(point_geometry):
                # for field_name, value in atributosDICT.items():
                    # field_name_lower = field_name.lower()
                    # if field_name_lower in fields_dict:
                        # field = fields_dict[field_name_lower]
                        # field_type = field.type()

                        # # Convertir valor al tipo del campo
                        # try:
                            # if field_type == QVariant.Int:
                                # value = int(value)
                            # elif field_type == QVariant.Double:
                                # value = float(value)
                            # elif field_type == QVariant.String:
                                # value = str(value)
                            # elif field_type == QVariant.Bool:
                                # value = bool(value)
                            
                            # # Asignar el valor convertido
                            # feature.setAttribute(field.name(), value)
                            # print(f'Asignado {value} ({type(value).__name__}) a {field.name()}')
                        # except (ValueError, TypeError):
                            # print(f'No se pudo convertir {value} a {field.name()} ({field.typeName()})')

                # layer.updateFeature(feature)
                
                # # Confirmar edición
                # if layer.commitChanges():
                    # txt = f"Atributos asignados correctamente\n\nRC {feature[fields_dict['rc14'].name()]}"
                    # QApplication.restoreOverrideCursor()
                    # self.fun.showMessage(txt)
                # else:
                    # error_msg = layer.lastError()
                    # print(f"Error al guardar los cambios: {error_msg}")
                    # layer.rollBack()
                    # txt = f"Error al guardar los cambios en la capa:\n{error_msg}"
                    # QApplication.restoreOverrideCursor()
                    # self.fun.showMessageERR(txt)
                
                # return

        # layer.rollBack()  # Si no se encuentra ninguna feature en el punto, cancelar edición
        # txt = "No se encontró ningún polígono en el punto pinchado."
        # QApplication.restoreOverrideCursor()
        # self.fun.showMessageERR(txt)

        
        
        
    # def asignaAtribCatastro(self, point, atributosDICT):
        # # # Se asignan los atributos al polígono de la capa activa en el punto pinchado
        # # #   point = punto pinchado
        # # #   atributosDICT, dictionary donde buscar los campos en la capa activa.
        # # #       Solo son obligatorios, y se crearán si no existen los campos:
        # # #           'RC14', tipo CHARACTER
        # # #           'CAT_NMSPC', tipo CHARACTER
        
        # layer = self.iface.activeLayer()

        # if not layer:
            # txt = "No hay ninguna capa activa."
            # QApplication.restoreOverrideCursor()
            # self.fun.showMessageERR(txt)
            # return

        # if layer.geometryType() != QgsWkbTypes.PolygonGeometry:
            # txt = f"La capa activa\n\n{layer.name()}  - ({QgsWkbTypes.geometryDisplayString(layer.geometryType())})\n\nNo es de tipo polígono."
            # QApplication.restoreOverrideCursor()
            # self.fun.showMessageERR(txt)
            # return

        # # # Verificar si los campos obligatorios existen y crearlos si es necesario
        # # fields = layer.fields()
        # # campo_obligatorios = {'RC14': QVariant.String, 'CAT_NMSPC': QVariant.String}

        # # nuevos_campos = []
        # # for campo, tipo in campo_obligatorios.items():
            # # if campo not in fields.names():
                # # nuevos_campos.append(QgsField(campo, tipo))

        # # if nuevos_campos:
            # # layer.dataProvider().addAttributes(nuevos_campos)
            # # layer.updateFields()
            # # fields = layer.fields()  # Refrescar los campos después de añadirlos
        
        # # Verificar si los campos obligatorios existen, si no, crearlos
        # fields = layer.fields()
        # if 'RC14' not in fields.names() and 'rc14' not in fields.names():        # 'RC14' Campo de referencia catastral 'localid'
            # layer.dataProvider().addAttributes([QgsField('RC14', QVariant.String)])
            # layer.updateFields()
        # if 'CAT_NMSPC' not in fields.names() and 'cat_nmspc' not in fields.names():   # 'CAT_NMSPC' Campo de 'namespace'
            # layer.dataProvider().addAttributes([QgsField('CAT_NMSPC', QVariant.String)])
            # layer.updateFields()
        
        # # Actualizar la lista de campos después de posibles cambios
        # fields = layer.fields()

        # # Buscar el polígono en el punto pinchado
        # point_geometry = QgsGeometry.fromPointXY(QgsPointXY(point))

        # # Iniciar edición
        # if not layer.isEditable():
            # layer.startEditing()

        # for feature in layer.getFeatures():
            # if feature.geometry().contains(point_geometry):
                # for field_name, value in atributosDICT.items():
                    # if field_name in fields.names():
                        # # Obtener tipo del campo en la capa
                        # field_type = fields.field(field_name).type()

                        # # Convertir valor al tipo correcto
                        # try:
                            # if field_type == QVariant.Int:
                                # value = int(value)
                            # elif field_type == QVariant.Double:
                                # value = float(value)
                            # elif field_type == QVariant.String:
                                # value = str(value)
                            # elif field_type == QVariant.Bool:
                                # value = bool(value)
                            # # Asignar el valor convertido
                            # feature.setAttribute(field_name, value)
                            # print(f'Asignado {value} ({type(value).__name__}) a {field_name}')
                        # except (ValueError, TypeError):
                            # print(f'No se pudo convertir {value} a {field_name} ({fields.field(field_name).typeName()})')

                # layer.updateFeature(feature)
                
                # # Confirmar edición
                # if layer.commitChanges():
                    # txt = f"Atributos asignados correctamente\n\nRC {feature['RC14']}"
                    # QApplication.restoreOverrideCursor()
                    # self.fun.showMessage(txt)
                # else:
                    # error_msg = layer.lastError()
                    # print(f"Error al guardar los cambios: {error_msg}")
                    # layer.rollBack()
                    # txt = f"Error al guardar los cambios en la capa:\n{error_msg}"
                    # QApplication.restoreOverrideCursor()
                    # self.fun.showMessageERR(txt)
                
                # return

        # layer.rollBack()  # Si no se encuentra ninguna feature en el punto, cancelar edición
        # txt = "No se encontró ningún polígono en el punto pinchado."
        # QApplication.restoreOverrideCursor()
        # self.fun.showMessageERR(txt)
            
            
            
        
        

    # def asignaAtribCatastro(self, point, atributosDICT):
        # # Se asignan los atributos al polígono de la capa activa en el punto pinchado
        # #   point = punto pinchado
        # #   atributosDICT, dictionary donde buscar los campos en la capa activa.
        # #       Solo son obligatorios, y se crearán si no existen los campos:
        # #           'RC14', tipo CHARACTER
        # #           'CAT_NMSPC', tipo CHARACTER

        # # Obtener la capa activa
        # layer = self.iface.activeLayer()
        
        # # Verificar si la capa es de tipo polígono
        # if not layer:
            # txt= f"No hay ninguna capa activa."
            # QApplication.restoreOverrideCursor()
            # self.fun.showMessageERR(txt)
            # return

        # if layer.geometryType() != QgsWkbTypes.PolygonGeometry:
            # txt= f"La capa activa\n\n{layer.name()}  - ({QgsWkbTypes.geometryDisplayString(layer.geometryType())})\n\nNo es de tipo polígono."
            # QApplication.restoreOverrideCursor()
            # self.fun.showMessageERR(txt)
            # return
                    
        # # Iniciar edición de la capa
        # layer.commitChanges()
        # layer.startEditing()
        
        # # Verificar si los campos obligatorios existen, si no, crearlos
        # fields = layer.fields()
        # if 'RC14' not in fields.names() and 'rc14' not in fields.names():        # 'RC14' Campo de referencia catastral 'localid'
            # layer.dataProvider().addAttributes([QgsField('RC14', QVariant.String)])
            # layer.updateFields()
        # if 'CAT_NMSPC' not in fields.names() and 'cat_nmspc' not in fields.names():   # 'CAT_NMSPC' Campo de 'namespace'
            # layer.dataProvider().addAttributes([QgsField('CAT_NMSPC', QVariant.String)])
            # layer.updateFields()
        
        # # Actualizar la lista de campos después de posibles cambios
        # fields = layer.fields()
        
        # # Buscar el polígono en el punto pinchado
        # point_geometry = QgsGeometry.fromPointXY(QgsPointXY(point))
        # for feature in layer.getFeatures():
            # if feature.geometry().contains(point_geometry):
                # # Asignar los valores de los campos si existen en la capa
                # for field_name, value in atributosDICT.items():
                    # try:
                        # if field_name in fields.names():
                            # feature[field_name] = value
                        # print (f'Asignamos valor {feature[field_name]} a feature[{field_name}] ')
                    # except:
                        # print (f'No se puede asignar valor {value} a campo: {field_name} ')
                        # pass
                
                # # Actualizar la feature en la capa
                # layer.commitChanges()
                # layer.updateExtents()
                # layer.updateFeature(feature)
                # txt= f"Atributos asignados correctamente\n\nRC {feature['RC14']}"
                # QApplication.restoreOverrideCursor()
                # self.fun.showMessage(txt)
                # return
        
        # # Si no se encontró ningún polígono, cancelar la edición
        # layer.rollBack()
        # txt= "No se encontró ningún polígono en el punto pinchado."
        # QApplication.restoreOverrideCursor()
        # self.fun.showMessageERR(txt)


