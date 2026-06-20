# -*- coding: utf-8 -*-
'''
/***************************************************************************
Name:           catastroBuscador.py
Purpose:        Tools for plugin catastroesp

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

from PyQt5.QtGui import QIcon, QPixmap, QTextCursor
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtWidgets import QDialog, QApplication, QInputDialog, QLineEdit
from PyQt5 import uic

from qgis.core import QgsProject, QgsVectorLayer, QgsExpression, QgsFeatureRequest
from qgis.gui import QgsDialog

import os
import urllib
from xml.etree import cElementTree as ElementTree
from osgeo import ogr, osr
from osgeo import ogr, osr, gdal
import datetime

from .config import configuration        # CLASE DE CONFIGURACIÓN DE VARIABLES DEL PROGRAMA
from .functions3 import Functions        # CLASE DE CONFIGURACIÓN DE FUNCIONES GENERALES
from .catastro_EntraTexto import catastro_EntraTexto

#----------------------------------------------------------------------
# TODO quitar esto cuando funcione ENTRA TEXTO
from .settings import Settings           # CLASE DE CONFIGURACIÓN DE VARIABLES GLOBALES
#----------------------------------------------------------------------

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), './menus/catastro_buscador.ui'))

tipoCARGA = 'CAPAPAR'
current_configuration = configuration()

# VARIABLES
srcVal = current_configuration.general['EPSG']

class catastroBuscador(QDialog, FORM_CLASS):

    def __init__(self, iface, parent=None):
        '''Constructor.'''
        super(catastroBuscador, self).__init__(parent)
        self.setupUi(self)
        self.current_configuration = configuration()
        self.Sett = Settings()
        self.setVar = QSettings()
        self.fun = Functions()
        self.iface = iface
        menu = self

        # Bandera para controlar errores
        self.error_occurred = False

        self.nombre_plugin = os.path.basename(os.path.dirname(__file__))

        try:
            # Configuración inicial del diálogo
            self.logo_BuscCat.setPixmap(QPixmap(f':/plugins/{self.nombre_plugin}/iconos/catastroesp.jpg'))
            self.setWindowIcon(QIcon(f':/plugins/{self.nombre_plugin}/iconos/cat_buscador.jpg'))
            self.setFixedSize(750, 282)
            self.lblNOCATASTRO.hide()

            # Comprobamos el rol del usuario
            userSIG, tipoUser = self.Sett.entrarUser()

            # Obtener lista de provincias
            lista_provincias, lista_cpine = self.fun.getProvinciasCatastro()
            self.combo_provincia.clear()
            if lista_provincias is not None and lista_provincias != 'nocat':
                self.combo_provincia.addItems(lista_provincias)
                lastProvSelect = self.setVar.value(f'{self.nombre_plugin}/last/lastProvSelect')
                if lastProvSelect in lista_provincias:
                    self.combo_provincia.setCurrentIndex(lista_provincias.index(lastProvSelect))
            else:
                text = 'PARECE QUE HAY PROBLEMAS DE CONEXIÓN'
                self.fun.showMessage(text)
                self.error_occurred = True  # Activar bandera de error
                return  # Salir del constructor

            # Configuración de valores por defecto
            lastRC14Select = self.setVar.value(f'{self.nombre_plugin}/last/lastRC14Select')
            self.ref_catastral.setText(lastRC14Select)
            lastIdufirSelect = self.setVar.value(f'{self.nombre_plugin}/last/lastIdufirSelect')
            self.idufirREGISTRO.setText(lastIdufirSelect)
            lastNPOLSelect = self.setVar.value(f'{self.nombre_plugin}/last/lastNPOLSelect')
            self.poligono.setText(lastNPOLSelect)
            lastNPARSelect = self.setVar.value(f'{self.nombre_plugin}/last/lastNPARSelect')
            self.parcela.setText(lastNPARSelect)

            self.fun.updateCombos(self)  # Actualiza el combo Municipios

            # Conexiones de botones
            self.addToListRCButton.clicked.connect(lambda: self.fun.addRCtoListClicked(self))
            self.addToListRusticaButton.clicked.connect(lambda: self.fun.addToListRusticaButtonClicked(self))
            self.zoomYCerrarButton.clicked.connect(lambda: self.fun.zoomToCurrentList(True, tipoCARGA, self))
            self.quitarItemButton.clicked.connect(lambda: self.fun.quitarSelectedItemsList(self, 'BUSC'))
            self.limpiarListaButton.clicked.connect(lambda: self.fun.limpiarListaClicked(self))
            self.btnBUSCRegistro.clicked.connect(lambda: self.fun.BUSCRegistro(self))
            self.btnEntraTXT.clicked.connect(self.menuEntraTXT)
            self.combo_provincia.currentIndexChanged.connect(lambda: self.fun.updateCombos(self))
            self.btnCargaMasiva.clicked.connect(lambda: self.cargaMasiva(self.iface))
            self.combo_tabla.currentIndexChanged.connect(self.actualizarCampos)
            self.btnIrCargaMasiva.clicked.connect(self.IrCargaMasiva)
            self.btnGeneraConsMasivaCAT.clicked.connect(self.GeneraConsMasivaCAT)
            self.ref_catastral.returnPressed.connect(lambda: self.fun.addRCtoListClicked(self))
            self.parcela.returnPressed.connect(lambda: self.fun.addToListRusticaButtonClicked(self))

            self.lblFichDest.hide()

            # TODO. Se ocultan las referencias al Registro de la propiedad
            self.lblidufirREGISTRO.hide()
            self.idufirREGISTRO.hide()
            self.btnBUSCRegistro.hide()

            QApplication.restoreOverrideCursor()

            # Cargar configuración personalizada si existe
            if configuration.custom_configuration != '':
                import imp
                try:
                    custom_file = configuration.custom_configuration
                    foo = imp.load_source('custom_config', custom_file)
                    custom_config = foo.custom_config()
                    self.current_configuration = custom_config
                except Exception as e:
                    print(f"Error al cargar configuración personalizada: {e}")
                    # QgsMessageLog.logMessage('Archivo no encontrado, se carga configuración por defecto..', 'jccm_bar')

            # Flag para eliminación de CAPA PARCELAS CATASTRALES
            self.chb_EliminarCapa.setChecked(False)
            self.chb_EliminarCapa.clicked.connect(self.flagEliminarCapa)

        except Exception as e:
            # Si ocurre un error, muestra un mensaje y activa la bandera de error
            self.fun.showMessage(f"Error durante la inicialización: {str(e)}")
            self.error_occurred = True  # Activar bandera de error
            return  # Salir del constructor

    def exec_(self):
        '''Sobrescribir el método exec_ para evitar que el diálogo se muestre si hay un error.'''
        if not self.error_occurred:
            return super().exec_()  # Mostrar el diálogo solo si no hay errores
        else:
            return QDialog.Rejected  # Devolver Rejected si hay un error


    '''
    ***************************************************************************/
    ***    FUNCIONES PARA CARGA MASIVA   ***
    ***************************************************************************/
    '''

    def cargaMasiva(self, iface):
        lista_CAPAS = self.fun.getCapasCsv(self.iface)
        if len(lista_CAPAS) == 0:
            self.fun.showMessage('No hay ninguna capa vectorial o tabla con RefCat para cargar')
            return

        self.combo_tabla.clear()
        self.combo_tabla.setEditable(False)
        self.combo_tabla.addItems(lista_CAPAS)

        try:
            if iface.activeLayer().name() in lista_CAPAS:
                self.combo_tabla.setCurrentText(iface.activeLayer().name())
            else:
                self.combo_tabla.setCurrentIndex(0)
        except:
            self.combo_tabla.setCurrentIndex(0)

        self.setFixedSize(750, 440)
        self.btnCargaMasiva.setEnabled(False)
        self.btnIrCargaMasiva.setEnabled(True)
        self.combo_tabla.setEnabled(True)
        self.combo_REFCAT.setEnabled(True)


    def flagEliminarCapa(self):
        if self.chb_EliminarCapa.isChecked():
            # self.lneMaxFeat.setEnabled(True)
            flagEliminarCAPA = True
            pass
        else:
            # self.lneMaxFeat.setEnabled(False)
            flagEliminarCAPA = False
            pass
        pass


    def actualizarCampos(self):
        layername = self.combo_tabla.currentText()
        if layername == '':
            # self.fun.showMessage('Debes cargar una capa csv en la tabla de contenidos')
            return None
        selected_table = self.fun.getLayerByName(layername)
        fields = selected_table.fields()
        list_fields = ['']
        for field in fields:
            # print field.type(), field.name()
            if (field.type() == 10): # Solo campos alfanuméricos
                list_fields.append(field.name())

        self.combo_REFCAT.clear()
        self.combo_REFCAT.addItems(list_fields)
        for field in list_fields:
            if field != '':
                self.combo_REFCAT.setCurrentIndex(list_fields.index(field))
                break


    def IrCargaMasiva(self):
        menu = self
        campo_REFCAT = self.combo_REFCAT.currentText()
        layername = self.combo_tabla.currentText()
        selected_table = self.fun.getLayerByName(layername)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if campo_REFCAT != '' and (selected_table is not None):
            self.obtenerRCFromLayer(selected_table,self.iface,campo_REFCAT,menu)
            QApplication.restoreOverrideCursor()
        else:
            QApplication.restoreOverrideCursor()
            self.fun.showMessage(u'Seleccione una TABLA y un CAMPO')
            return


    def GeneraConsMasivaCAT(self):
        # Analiamos si la lista de REFCAT tiene alguna entrada
        current_lista_rc =  [str(self.listaRCs.item(i).text()) for i in range(self.listaRCs.count())]
        if len(current_lista_rc) < 1:
            self.fun.showMessage('No hay elementos en la lista')
            QApplication.restoreOverrideCursor()
            return

        # Creación de fichero de consulta XML
        ###############################################################
        ###                  CONTROL    qué fichero                 ###
        ###############################################################
        xml_salida_file= 'c:/temp/CATASTRO_ENVIO.XML'

        self.fun.comprobarDirectorio(xml_salida_file)

        now = datetime.datetime.now()
        fecha = now.strftime('%d/%m/%y')

        # Introducir FINALIDAD
        qid = QInputDialog()
        qid.setWindowIcon(QIcon(f':/plugins/{self.nombre_plugin}/iconos/catastroesp.jpg'))

        title = 'CONSULTA MASIVA CATASTRO - FINALIDAD -'
        label = 'FINALIDAD: --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---'
        mode = QLineEdit.Normal
        default = 'CONSULTA COLINDANTES A CARRETERA '
        finalidad, ok = QInputDialog.getText(qid, title, label, mode, default)
        if ok == False:
            QApplication.restoreOverrideCursor()
            return

        QApplication.setOverrideCursor(Qt.WaitCursor)

        filexml = open(xml_salida_file, 'w')
        PLANTILLA_1  = u'<?xml version="1.0" encoding="UTF-8"?>\n'
        PLANTILLA_1 += u'   <LISTADATOS>\n'
        PLANTILLA_1 += u'       <FEC>%s</FEC>\n'%fecha
        PLANTILLA_1 += u'       <FIN>%s</FIN>\n'%finalidad
        filexml.writelines(PLANTILLA_1) # Añade el encabezamiento al GML


        for rc in current_lista_rc:
            linXml = u'       <DAT><RC>%s</RC></DAT>\n'%rc
            filexml.writelines(linXml) # Añade el dato RC al XML

        PLANTILLA_2 = u'   </LISTADATOS>\n'
        filexml.writelines(PLANTILLA_2) # Añade el final al XML
        self.lblFichDest.setText('Fichero destino:   '+xml_salida_file)
        self.lblFichDest.show()

        QApplication.restoreOverrideCursor()


    def obtenerRCFromLayer(self, layer, iface, campo_REFCAT, menu):
        # print 'EMPEZAMOS A CARGAR LAS RC'
        features = layer.getFeatures()
        numfeat = layer.featureCount()
        listaParcelas = []
        cuentaParcelas = 0
        textMsg = ''
        textMsgINI = 'CARGANDO PARCELAS CATASTRALES...'+'\n'
        self.txeAVISOS.setText(textMsgINI)
        for feature in features:
            QApplication.processEvents()
            rc = feature[campo_REFCAT]
            if not rc:
                rc = 'NO-PARCELA'
            else:
                # print ('rc=', rc)
                point = None
                rc = rc[0:14].upper()
                if len(self.listaRCs.findItems(rc, Qt.MatchExactly)) == 0:
                    # Esto comprueba la existencia de la referencia catastral
                    point_response = self.fun.getPointFromRC(self.iface,rc, mess = 'NO')
                    if point_response is not None and point_response[0] == 'Error':
                        textMsg = rc+ ' '+ point_response[1]
                        self.txeAVISOS.append(textMsg)
                    elif point_response is None:
                        textMsg = rc+ ' ERROR DE RESPUESTA'
                        self.txeAVISOS.append(textMsg)
                    elif point_response is not None:
                            textMsg = rc + u' OK'
                            listaParcelas.append(rc)
                            self.listaRCs.addItem(rc)
                            # Se añade numero de parcelas que se van cargando. CASO MENU BUSCADOR CATASTRAL
                            self.lblParCarga.setText(u'(%s)'%(menu.listaRCs.count()))
                            cuentaParcelas += 1
                            textMsg = '%s/%s - '%(str(cuentaParcelas),str(numfeat)) + textMsg
                            self.txeAVISOS.append(textMsg)
                else:
                    textMsg = rc + ' REPETIDA'
                    self.txeAVISOS.append(textMsg)

            # Se coloca el cursos rl final del mensaje
            cursor = self.txeAVISOS.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.txeAVISOS.setTextCursor(cursor)

        textMsg1 = u'   %s de %s RefCat  válidas leídas'%(cuentaParcelas, numfeat)
        self.txeAVISOS.append(textMsg1)


        if cuentaParcelas >0:
            return listaParcelas
        else:
            self.fun.showMessage(u'No se ha añadido ninguna RefCat de un total de %s registros'%(numfeat))
            return


    def menuEntraTXT(self):
        d = catastro_EntraTexto(self)
        d.show()
        if d.exec_():
            result = d.getInputs()

        try:
            listaParcelas = []
            cuentaParcelas = 0

            for rc in result:
                if len(self.listaRCs.findItems(rc, Qt.MatchExactly)) == 0:

                    # Esto comprueba la existencia de la referencia catastral
                    point_response = self.fun.getPointFromRC(self.iface,rc)
                    if point_response is not None and point_response[0] == 'Error':
                        textMsg = rc+ ' '+ point_response[1]
                        # print (textMsg)
                        self.txeAVISOS.append(textMsg)
                    elif point_response is not None:
                        textMsg = rc + u' OK'
                        # print (textMsg)
                        listaParcelas.append(rc)
                        self.listaRCs.addItem(rc)
                        cuentaParcelas += 1
                        self.txeAVISOS.append(textMsg)
                else:
                    textMsg = rc + ' REPETIDA'
                    # print (textMsg)
                    self.txeAVISOS.append(textMsg)

            if cuentaParcelas >0:
                QApplication.restoreOverrideCursor()
                return listaParcelas
            else:
                self.fun.showMessage(u'No se ha añadido ninguna RefCat de un total de %s registros'%(numfeat))
                QApplication.restoreOverrideCursor()
                return

        except:
            QApplication.restoreOverrideCursor()
            return
