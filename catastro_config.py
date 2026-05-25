# -*- coding: utf-8 -*-
'''
/***************************************************************************
Name:           catastro_config.py

                                 A QGIS plugin
Plugin:     catastroesp - Catastro de España
Purpose:    Nuevo gestor de configuración con variables de usuario
            El configurador es idénico al original de jccm_bar3
        --------------------------------------------------------------------
        begin                : 2020-02-14
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

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QLineEdit, QFileDialog, QWidget,  QMessageBox, QVBoxLayout, QLabel
from PyQt5.QtCore import QSettings, Qt

from PyQt5 import uic
from qgis.core import Qgis, QgsProject

import os
import configparser
import codecs
import ast
import inspect
from time import gmtime, localtime, strftime

from .settings import Settings           # CLASE DE CONFIGURACIÓN DE VARIABLES GLOBALES
from .config import configuration        # CLASE DE CONFIGURACIÓN DE VARIABLES DEL PROGRAMA
from .functions3 import Functions        # CLASE DE CONFIGURACIÓN DE FUNCIONES GENERALES
# from .jccm_bar_config_newCapa_dialog import Form_newCApa

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), './menus/catastro_configurador.ui'))

# FORM_CLASS1, _ = uic.loadUiType(os.path.join(
    # os.path.dirname(__file__), './menus/selectGPKG.ui'))


class catastro_config(QDialog, FORM_CLASS):
    
    def __init__(self, iface, tabConfig, parent=None):
        '''Constructor.'''
        super(catastro_config, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface;
        self.fun = Functions()
        
        self.nombre_plugin = os.path.basename(os.path.dirname(__file__))

        # Inicializa variables globales
        self.Sett = Settings()
        self.qs = QSettings()
        self.conf = configuration()

        self.setWindowIcon(QIcon(f':/plugins/{self.nombre_plugin}/iconos/{self.nombre_plugin}.jpg'))
        self.logo.setPixmap(QPixmap(f':/plugins/{self.nombre_plugin}/iconos/{self.nombre_plugin}.jpg'))

        if self.qs.value(f'{self.nombre_plugin}/ACCESOEDITOR'):
            self.acceso = self.qs.value(f'{self.nombre_plugin}/ACCESOEDITOR')
        else:
            self.qs.setValue(f'{self.nombre_plugin}/ACCESOEDITOR', False)
            self.acceso = False
            text = u' ¡¡¡ PELIGRO !!!\nCAMBIAR LA CONFIGURACIÓN DE USUARIO ESTÁ RESERVADO A USUARIOS AVANZADOS\n\nTENDRÉ CUIDADO, LO PROMETO'
            self.fun.showMessageERR(text,text2='',tittle='JCCM',)

        self.readCustomConfiguration()                          # Lee los datos de configuración en memoria de usuario

        self.tab_configuracion.setCurrentIndex(1)
        
        # Se ocultan determinados TABs para el plugin 'catastroesp'
        if self.nombre_plugin == 'catastroesp':
            # Oculta las pestañas específicas
            self.tab_configuracion.setTabVisible(1, False)  # Oculta la pestaña 'LRS'
            self.tab_configuracion.setTabVisible(4, False)  # Oculta la pestaña 'INVENTARIO'
            self.tab_configuracion.setTabVisible(5, False)  # Oculta la pestaña 'DATOS INTERNOS'
            self.tab_configuracion.setTabVisible(6, False)  # Oculta la pestaña 'DOM.PUBLICO'
                        
            # Verifica si el QGridLayout existe
            if hasattr(self, 'gridLytGENERAL_LRS'):
                # Recorre todos los widgets dentro del QGridLayout
                for i in range(self.gridLytGENERAL_LRS.count()):
                    widget = self.gridLytGENERAL_LRS.itemAt(i).widget()
                    if widget:
                        widget.setVisible(False)  # Oculta cada widget
                        
        ## CONTROL DE TAB ACTIVO
        self.tab_configuracion.setCurrentIndex(tabConfig)       ### esto va al tab SELECCIONADO EN LA LLAMADA


        ######################################################
        #########           CONTROLES GENERALES      #########
        ######################################################

        self.ok_button.clicked.connect(self.ok_pressed)

        self.guardar_conf_button.hide()
        self.cargar_conf_button.hide()

        self.guardar_conf_button.clicked.connect(self.guardar_config)
        self.cargar_conf_button.clicked.connect(self.cargar_conf)
        self.resetDefault.clicked.connect(self.resetDefaultConfig)

        # Detección de cambios en el menú configuración
        self.flagCambio = 0

        lineEdits = self.findChildren(QLineEdit)
        for dato in lineEdits:
            dato.textChanged.connect(self.cambioConfig)


        ######################################################
        #########           TAB   LRS                #########
        ######################################################

        self.btnSelectFichGpkg.clicked.connect(self.btnSelectFichGpkg_clicked)
        self.cbxTipo_consultaCAPA.currentIndexChanged.connect(self.cbxTipo_consultaCAPA_changed)

        self.btnOriFichGpkgCTRAS.clicked.connect(self.btnOriFichGpkgCTRAS_clicked)
        self.btnDestFichGpkgCTRAS.clicked.connect(self.btnDestFichGpkgCTRAS_clicked)

        self.btnCopiar_GDB_CTRAS.clicked.connect(self.btnCopiar_GDB_CTRAS_clicked)

        #--------------------------------------------------------
        #--------------           TODO             --------------
        # self.tbtAnadirFichGpkgCTRAS.clicked.connect(self.TODO)
        # self.tbtQuitaFichGpkgCTRAS.clicked.connect(self.TODO)
        # REVISAR ANCHOS Y RELLENAR DE DATOS DE FUENTES
        self.tablaFichGpkgCTRAS.setColumnWidth(0, 450)   # data['FICHERO GPKG']      ANCHO 650
        self.tablaFichGpkgCTRAS.setColumnWidth(1, 100)   # data['Tabla Carreteras']
        self.tablaFichGpkgCTRAS.setColumnWidth(2, 150)   # data['Tabla Municipios']
        #--------------           TODO             --------------
        #--------------------------------------------------------

        ######################################################
        #########           TAB   CAPAS              #########
        ######################################################

        self.quitarCapaButton.clicked.connect(self.quitarCapa)
        self.addCapaButton.clicked.connect(self.addCapaTable)
        self.editarCapaButton.clicked.connect(self.editarCapaTable)
        self.tbtSelectFichConfigCapas.clicked.connect(self.tbtSelectFichConfigCapas_clicked)


        ######################################################
        #########    CONTROLES TAB EXPROPIACIONES    #########
        ######################################################

        ## CONTROLES CAPA EXPROPIACIONES
        self.cbxTIPOcapaEXPROPIACIONES.currentIndexChanged.connect(self.TIPOcapaEXPROPIACIONES_updated)
        self.tbtSelectLimExpro.clicked.connect(self.tbtSelectLimExpro_clicked)
        self.tbtSelectLimExproDir.clicked.connect(self.tbtSelectLimExproDir_clicked)

        ## CONTROLES CAPA Informes EXPROPIACIONES
        self.cbxTIPOcapaInfEXPROPIACIONES.currentIndexChanged.connect(self.TIPOcapaInfEXPROPIACIONES_updated)
        self.tbtSelectInfoExpro.clicked.connect(self.tbtSelectInfoExpro_clicked)
        self.tbtSelectInfoExprDir.clicked.connect(self.tbtSelectInfoExprDir_clicked)

        ## CONTROLES CAPA PATRIMONIO
        self.cbxTIPOcapaParcPATRI.currentIndexChanged.connect(self.TIPOcapaParcPATRI_updated)
        self.tbtSelectParcPATRI.clicked.connect(self.tbtSelectParcPATRI_clicked)
        self.tbtSelectParcPATRIDir.clicked.connect(self.tbtSelectParcPATRIDir_clicked)

        ## CONTROLES GRUPO EXPROPIACIONES
        self.tbtSelectGRUPOEXPRO.clicked.connect(self.tbtSelectGRUPOEXPRO_clicked)


        ######################################################
        #########   CONTROLES TAB INVENTARIO         #########
        ######################################################

        self.cbxInventarioPROVINCIA.currentIndexChanged.connect(self.cbx_provINVENTARIO_updated)
        self.cbx_provINVENTARIO_updated()

        self.tbtSelectFileOBFA.clicked.connect(self.tbtSelectFileOBFA_clicked)
        self.tbtSelectEstiloOBFA.clicked.connect(self.tbtSelectEstiloOBFA_clicked)

        self.tbtSelectFileSEVE.clicked.connect(self.tbtSelectFileSEVE_clicked)
        self.tbtSelectEstiloSEVE.clicked.connect(self.tbtSelectEstiloSEVE_clicked)

        #--------------------------------------------------------
        #--------------           TODO             --------------
        ## CONTROLES CAPA OBRAS FÁBRICA
        # self.cbxTIPOcapaOBFA.currentIndexChanged.connect(self.TIPOcapaOBFA_updated)
        # self.tbtSelectOBFA.clicked.connect(self.tbtSelectOBFA_clicked)
        #--------------           TODO             --------------
        #--------------------------------------------------------



    def ok_pressed(self):
        if self.flagCambio == 1:
            msg = u'Se han realizado cambios de configuración no guardados \n\n ¿GUARDAR CAMBIOS?'
            result = self.fun.showMessageYESNO(msg,text2='',tittle='JCCM. Cambios sin guardar')
            if result == 1024:
                # self.guardar_config()
                self.guardar_VARconfig()
                self.flagCambio = 0
                self.close()
            return
        else:
            self.close()


    def cambioConfig(self):
        self.flagCambio = 1
        pass

    # def cambioConfig(self, dato): # Cambio de color de fondo
        # self.flagCambio = 1
        # # rosa = '#ffbebe'
        # colorRosa = QtGui.QColor(255, 204, 204) # Light red
        # # blanco = '#ffffff'
        # self.setAutoFillBackground(True)
        # p = dato.palette()
        # p.setColor(dato.backgroundRole(), colorRosa)
        # dato.setPalette(p)
        # pass

    def readCustomConfiguration(self):
        #######################################################################################################
        #    Se lee la configuración de las VARIABLES de usuario o del fichero de configuración si existe
        #       Se colocan los datos en el menu configuración
        #######################################################################################################

        ''' DATOS DE LA APLICACION Y DEL COMPLEMENTO '''
        fileMetadata = os.path.join(os.path.dirname(__file__), 'metadata.txt')
        cfg = configparser.ConfigParser()
        cfg.read(fileMetadata)
        fecha = strftime('%d %b %Y %H:%M ', localtime(os.path.getmtime(fileMetadata)))

        version = cfg.get('general', 'version')
        versionQGS = Qgis.QGIS_VERSION
        userSIG, tipoUser = self.Sett.entrarUser()
        
        txtVersion  = u'QGIS '+versionQGS + '\n'
        txtVersion += self.tr('Version Plugin: %s Fecha: %s') % (version, fecha)
        
        self.lblQGSVersion.setText(txtVersion)
        
        self.lblUSUARIO.setText(u'Usuario: '+userSIG)
        self.lblTIPOUSUARIO.setText(u'Tipo: '+tipoUser)
        # self.lblVersion.setText(u'')
        # self.lblQGSVersion.setText(u'QGIS '+versionQGS)
        self.lbldirPYTJCCM.setText(os.path.dirname(__file__))

        '''     GENERAL          '''
        ''' general (environment / otros) '''
        EPSG = self.qs.value(f'{self.nombre_plugin}/GENERAL/EPSG')
        if EPSG is None:
            EPSG = self.conf.general['EPSG']
            self.qs.setValue(f'{self.nombre_plugin}/GENERAL/EPSG', EPSG)
        self.lneEPSG.setText(str(EPSG))

        Ambito = self.qs.value(f'{self.nombre_plugin}/GENERAL/01Ambito')
        if Ambito is None:
            Ambito = self.conf.general['01Ambito']
            self.qs.setValue(f'{self.nombre_plugin}/GENERAL/01Ambito', Ambito)
        listProv = [self.cbxPROVINCIA.itemText(i) for i in range(self.cbxPROVINCIA.count())]
        if Ambito in listProv:
            self.cbxPROVINCIA.setCurrentIndex(listProv.index(Ambito))

        wfs_carreteras = self.qs.value(f'{self.nombre_plugin}/GENERAL/wfs_carreteras')
        if wfs_carreteras is None:
            wfs_carreteras = self.conf.general['wfs_carreteras']
            self.qs.setValue(f'{self.nombre_plugin}/GENERAL/wfs_carreteras', wfs_carreteras)
        self.wfs_carreteras.setText(wfs_carreteras)

        wfs_carreteras_layer = self.qs.value(f'{self.nombre_plugin}/GENERAL/wfs_carreteras_layer')
        if wfs_carreteras_layer is None:
            wfs_carreteras_layer = self.conf.general['wfs_carreteras_layer']
            self.qs.setValue(f'{self.nombre_plugin}/GENERAL/wfs_carreteras_layer', wfs_carreteras_layer)
        self.wfs_carreteras_layer.setText(wfs_carreteras_layer)

        rest_carreteras = self.qs.value(f'{self.nombre_plugin}/GENERAL/rest_carreteras')
        if rest_carreteras is None:
            rest_carreteras = self.conf.general['rest_carreteras']
            self.qs.setValue(f'{self.nombre_plugin}/GENERAL/rest_carreteras', rest_carreteras)
        self.rest_carreteras.setText(rest_carreteras)

        rest_Pks = self.qs.value(f'{self.nombre_plugin}/GENERAL/rest_Pks')
        if rest_Pks is None:
            rest_Pks = self.conf.general['rest_Pks']
            self.qs.setValue(f'{self.nombre_plugin}/GENERAL/rest_Pks', rest_Pks)
        self.rest_Pks.setText(rest_Pks)

        rest_poblaciones = self.qs.value(f'{self.nombre_plugin}/GENERAL/rest_poblaciones')
        if rest_poblaciones is None:
            rest_poblaciones = self.conf.general['rest_poblaciones']
            self.qs.setValue(f'{self.nombre_plugin}/GENERAL/rest_poblaciones', rest_poblaciones)
        self.rest_poblaciones.setText(rest_poblaciones)

        campo_poblacion = self.qs.value(f'{self.nombre_plugin}/GENERAL/campo_poblacion')
        if campo_poblacion is None:
            campo_poblacion = self.conf.general['campo_poblacion']
            self.qs.setValue(f'{self.nombre_plugin}/GENERAL/campo_poblacion', campo_poblacion)
        self.campo_poblacion.setText(campo_poblacion)

        rest_municipios = self.qs.value(f'{self.nombre_plugin}/GENERAL/rest_municipios')
        if rest_municipios is None:
            rest_municipios = self.conf.general['rest_municipios']
            self.qs.setValue(f'{self.nombre_plugin}/GENERAL/rest_municipios', rest_municipios)
        self.rest_municipios.setText(rest_municipios)

        #--------------------------------------------------------
        #--------------           TODO             --------------
        # municipio_text_field = self.qs.value(f'{self.nombre_plugin}/GENERAL/municipio_text_field')
        # if municipio_text_field is None:
            # municipio_text_field = self.conf.general['municipio_text_field']
            # self.qs.setValue(f'{self.nombre_plugin}/GENERAL/municipio_text_field', municipio_text_field)
        # self.campo_poblacion.setText(municipio_text_field)
        #--------------           TODO             --------------
        #--------------------------------------------------------

        carpeta_estilos = self.qs.value(f'{self.nombre_plugin}/GENERAL/carpeta_estilos')
        if carpeta_estilos is None:
            carpeta_estilos = self.conf.general['carpeta_estilos']
            self.qs.setValue(f'{self.nombre_plugin}/GENERAL/carpeta_estilos', carpeta_estilos)
        self.carpeta_estilos.setText(carpeta_estilos)

        fich_config_capas = self.qs.value(f'{self.nombre_plugin}/GENERAL/fich_config_capas')
        if fich_config_capas is None:
            fich_config_capas = self.conf.general['fich_config_capas']
            self.qs.setValue(f'{self.nombre_plugin}/GENERAL/fich_config_capas', fich_config_capas)
        self.lneFichConfigCapas.setText(fich_config_capas)

        urlWMSmdt = self.qs.value(f'{self.nombre_plugin}/GENERAL/urlWMSmdt')
        if urlWMSmdt is None:
            urlWMSmdt = self.conf.general['urlWMSmdt']
            self.qs.setValue(f'{self.nombre_plugin}/GENERAL/urlWMSmdt', urlWMSmdt)
        self.urlWMSmdt.setText(urlWMSmdt)

        urlWMSmdtLayer = self.qs.value(f'{self.nombre_plugin}/GENERAL/urlWMSmdtLayer')
        if urlWMSmdtLayer is None:
            urlWMSmdtLayer = self.conf.general['urlWMSmdtLayer']
            self.qs.setValue(f'{self.nombre_plugin}/GENERAL/urlWMSmdtLayer', urlWMSmdtLayer)
        self.urlWMSmdtLayer.setText(urlWMSmdtLayer)

        urlWMSmdtValor = self.qs.value(f'{self.nombre_plugin}/GENERAL/urlWMSmdtValor')
        if urlWMSmdtValor is None:
            urlWMSmdtValor = self.conf.general['urlWMSmdtValor']
            self.qs.setValue(f'{self.nombre_plugin}/GENERAL/urlWMSmdtValor', urlWMSmdtValor)
        self.urlWMSmdtValor.setText(urlWMSmdtValor)


        '''     LRS      '''
        tipo_consultaCAPA = self.qs.value(f'{self.nombre_plugin}/LRS/tipo_consultaCAPA')
        if tipo_consultaCAPA is None:
            tipo_consultaCAPA = self.conf.lrs['tipo_consultaCAPA']
            self.qs.setValue(f'{self.nombre_plugin}/LRS/tipo_consultaCAPA', tipo_consultaCAPA)
        listTipo_consultaCAPA = [self.cbxTipo_consultaCAPA.itemText(i) for i in range(self.cbxTipo_consultaCAPA.count())]
        if tipo_consultaCAPA in listTipo_consultaCAPA:
            self.cbxTipo_consultaCAPA.setCurrentIndex(listTipo_consultaCAPA.index(tipo_consultaCAPA))

        ruta_geopackage = self.qs.value(f'{self.nombre_plugin}/LRS/ruta_geopackage')
        if ruta_geopackage is None:
            ruta_geopackage = self.conf.lrs['ruta_geopackage']
            self.qs.setValue(f'{self.nombre_plugin}/LRS/ruta_geopackage', ruta_geopackage)
        self.lneFichGpkgCTRAS.setText(ruta_geopackage)

        nombre_capa_ctras = self.qs.value(f'{self.nombre_plugin}/LRS/nombre_capa_ctras')
        if nombre_capa_ctras is None:
            nombre_capa_ctras = self.conf.lrs['nombre_capa_ctras']
            self.qs.setValue(f'{self.nombre_plugin}/LRS/nombre_capa_ctras', nombre_capa_ctras)
        listnombre_capa_ctras = [self.cbxnombre_capa_ctras.itemText(i) for i in range(self.cbxnombre_capa_ctras.count())]
        if nombre_capa_ctras in listnombre_capa_ctras:
            self.cbxnombre_capa_ctras.setCurrentIndex(listnombre_capa_ctras.index(nombre_capa_ctras))
        else:
            self.cbxnombre_capa_ctras.addItem(nombre_capa_ctras, 0)  # Agrega el elemento en la posición 0
            self.cbxnombre_capa_ctras.setCurrentIndex(0)  # Establece el índice actual en el nuevo elemento

        nombre_capa_munis = self.qs.value(f'{self.nombre_plugin}/LRS/nombre_capa_munis')
        if nombre_capa_munis is None:
            nombre_capa_munis = self.conf.lrs['nombre_capa_munis']
            self.qs.setValue(f'{self.nombre_plugin}/LRS/nombre_capa_munis', nombre_capa_munis)
        listnombre_capa_munis = [self.cbxnombre_capa_munis.itemText(i) for i in range(self.cbxnombre_capa_munis.count())]
        if nombre_capa_munis in listnombre_capa_munis:
            self.cbxnombre_capa_munis.setCurrentIndex(listnombre_capa_munis.index(nombre_capa_munis))
        else:
            self.cbxnombre_capa_munis.addItem(nombre_capa_munis, 0)  # Agrega el elemento en la posición 0
            self.cbxnombre_capa_munis.setCurrentIndex(0)  # Establece el índice actual en el nuevo elemento

        nombre_capa_pobla = self.qs.value(f'{self.nombre_plugin}/LRS/nombre_capa_pobla')
        if nombre_capa_pobla is None:
            nombre_capa_pobla = self.conf.lrs['nombre_capa_pobla']
            self.qs.setValue(f'{self.nombre_plugin}/LRS/nombre_capa_pobla', nombre_capa_pobla)
        listnombre_capa_pobla = [self.cbxnombre_capa_pobla.itemText(i) for i in range(self.cbxnombre_capa_pobla.count())]
        if nombre_capa_pobla in listnombre_capa_pobla:
            self.cbxnombre_capa_pobla.setCurrentIndex(listnombre_capa_pobla.index(nombre_capa_pobla))
        else:
            self.cbxnombre_capa_pobla.addItem(nombre_capa_pobla, 0)  # Agrega el elemento en la posición 0
            self.cbxnombre_capa_pobla.setCurrentIndex(0)  # Establece el índice actual en el nuevo elemento

        OriFichGpkgCTRAS = self.qs.value(f'{self.nombre_plugin}/LRS/OriFichGpkgCTRAS')
        if OriFichGpkgCTRAS is None:
            OriFichGpkgCTRAS = self.conf.lrs['OriFichGpkgCTRAS']
            self.qs.setValue(f'{self.nombre_plugin}/LRS/OriFichGpkgCTRAS', OriFichGpkgCTRAS)
        self.lneOriFichGpkgCTRAS.setText(OriFichGpkgCTRAS)

        DestFichGpkgCTRAS = self.qs.value(f'{self.nombre_plugin}/LRS/DestFichGpkgCTRAS')
        if DestFichGpkgCTRAS is None:
            DestFichGpkgCTRAS = self.conf.lrs['DestFichGpkgCTRAS']
            self.qs.setValue(f'{self.nombre_plugin}/LRS/DestFichGpkgCTRAS', DestFichGpkgCTRAS)
        self.lneDestFichGpkgCTRAS.setText(DestFichGpkgCTRAS)

        #--------------------------------------------------------
        #--------------           TODO             --------------
        #     DESACTIVAMOS CONTROLES QUE NO FUNCIONAN
        #   Deberán permitir añadir servicios de ficheros GPKG donde buscar los datos
        self.lblFichGPKG.setEnabled(False)
        self.tablaFichGpkgCTRAS.setEnabled(False)
        self.tbtAnadirFichGpkgCTRAS.setEnabled(False)
        self.tbtQuitaFichGpkgCTRAS.setEnabled(False)

        #--------------           TODO             --------------
        #--------------------------------------------------------

        id_ctra_carreteras = self.qs.value(f'{self.nombre_plugin}/LRS/id_ctra_carreteras')
        if id_ctra_carreteras is None:
            id_ctra_carreteras = self.conf.lrs['identificador_carretera_carreteras']
            self.qs.setValue(f'{self.nombre_plugin}/LRS/id_ctra_carreteras', id_ctra_carreteras)
        self.identificador_carretera_carreteras.setText(id_ctra_carreteras)

        carpeta_log = self.qs.value(f'{self.nombre_plugin}/LRS/carpeta_log')
        if carpeta_log is None:
            carpeta_log = self.conf.lrs['default_log_folder']
            self.qs.setValue(f'{self.nombre_plugin}/LRS/carpeta_log', carpeta_log)
        self.carpeta_log.setText(carpeta_log)

        bal_dest_path = self.qs.value(f'{self.nombre_plugin}/LRS/bal_dest_path')
        if bal_dest_path is None:
            bal_dest_path = self.conf.lrs['bal_dest_path']
            self.qs.setValue(f'{self.nombre_plugin}/LRS/bal_dest_path', bal_dest_path)
        self.bal_dest_path.setText(bal_dest_path)

        bal_nom_layer = self.qs.value(f'{self.nombre_plugin}/LRS/bal_nom_layer')
        if bal_nom_layer is None:
            bal_nom_layer = self.conf.lrs['bal_nom_layer']
            self.qs.setValue(f'{self.nombre_plugin}/LRS/bal_nom_layer', bal_nom_layer)
        self.bal_nom_layer.setText(bal_nom_layer)

        bal_estiloCAPA = self.qs.value(f'{self.nombre_plugin}/LRS/bal_estiloCAPA')
        if bal_estiloCAPA is None:
            bal_estiloCAPA = self.conf.lrs['bal_estiloCAPA']
            self.qs.setValue(f'{self.nombre_plugin}/LRS/bal_estiloCAPA', bal_estiloCAPA)
        self.bal_estiloCAPA.setText(bal_estiloCAPA)




        '''             CATASTRO_TOOL           '''
        url_catastro_distancia = self.qs.value(f'{self.nombre_plugin}/CATASTRO/url_catastro_distancia')
        if url_catastro_distancia is None:
            url_catastro_distancia = self.conf.catastro_tool['url_catastro_distancia']
            self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/url_catastro_distancia', url_catastro_distancia)
        self.url_catastro_distancia.setText(url_catastro_distancia)

        url_catastro_rc = self.qs.value(f'{self.nombre_plugin}/CATASTRO/url_catastro_rc')
        if url_catastro_rc is None:
            url_catastro_rc = self.conf.catastro_tool['url_catastro_rc']
            self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/url_catastro_rc', url_catastro_rc)
        self.url_catastro_rc.setText(url_catastro_rc)

        url_catastro_Provincia = self.qs.value(f'{self.nombre_plugin}/CATASTRO/url_catastro_Provincia')
        if url_catastro_Provincia is None:
            url_catastro_Provincia = self.conf.catastro_tool['url_catastro_Provincia']
            self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/url_catastro_Provincia', url_catastro_Provincia)
        self.url_catastro_Provincia.setText(url_catastro_Provincia)

        url_catastro_municipio = self.qs.value(f'{self.nombre_plugin}/CATASTRO/url_catastro_municipio')
        if url_catastro_municipio is None:
            url_catastro_municipio = self.conf.catastro_tool['url_catastro_municipio']
            self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/url_catastro_municipio', url_catastro_municipio)
        self.url_catastro_municipio.setText(url_catastro_municipio)

        url_catastro_RCCOOR = self.qs.value(f'{self.nombre_plugin}/CATASTRO/url_catastro_RCCOOR')
        if url_catastro_RCCOOR is None:
            url_catastro_RCCOOR = self.conf.catastro_tool['url_catastro_RCCOOR']
            self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/url_catastro_RCCOOR', url_catastro_RCCOOR)
        self.url_catastro_RCCOOR.setText(url_catastro_RCCOOR)

        url_catastro_DNPRC = self.qs.value(f'{self.nombre_plugin}/CATASTRO/url_catastro_DNPRC')
        if url_catastro_DNPRC is None:
            url_catastro_DNPRC = self.conf.catastro_tool['url_catastro_DNPRC']
            self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/url_catastro_DNPRC', url_catastro_DNPRC)
        self.url_catastro_DNPRC.setText(url_catastro_DNPRC)

        url_catastro_DNPPP = self.qs.value(f'{self.nombre_plugin}/CATASTRO/url_catastro_DNPPP')
        if url_catastro_DNPPP is None:
            url_catastro_DNPPP = self.conf.catastro_tool['url_catastro_DNPPP']
            self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/url_catastro_DNPPP', url_catastro_DNPPP)
        self.url_catastro_DNPPP.setText(url_catastro_DNPPP)

        url_catastro_DescGML = self.qs.value(f'{self.nombre_plugin}/CATASTRO/url_catastro_DescGML')
        if url_catastro_DescGML is None:
            url_catastro_DescGML = self.conf.catastro_tool['url_catastro_DescGML']
            self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/url_catastro_DescGML', url_catastro_DescGML)
        self.url_catastro_DescGML.setText(url_catastro_DescGML)

        cat_dir_shps = self.qs.value(f'{self.nombre_plugin}/CATASTRO/cat_dir_shps')
        if cat_dir_shps is None:
            cat_dir_shps = self.conf.catastro_tool['cat_dir_shps']
            self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/cat_dir_shps', cat_dir_shps)
        self.cat_dir_shps.setText(cat_dir_shps)

        cat_year = self.qs.value(f'{self.nombre_plugin}/CATASTRO/cat_year')
        if cat_year is None:
            cat_year = self.conf.catastro_tool['cat_year']
            self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/cat_year', cat_year)
        self.cat_year.setText(str(cat_year))

        dir_estilos_catastro = self.qs.value(f'{self.nombre_plugin}/CATASTRO/dir_estilos_catastro')
        if dir_estilos_catastro is None:
            dir_estilos_catastro = self.conf.catastro_tool['dir_estilos_catastro']
            self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/dir_estilos_catastro', dir_estilos_catastro)
        self.dir_estilos_catastro.setText(dir_estilos_catastro)

        cat_pos_toc = self.qs.value(f'{self.nombre_plugin}/CATASTRO/cat_pos_toc')
        if cat_pos_toc is None:
            cat_pos_toc = self.conf.catastro_tool['cat_pos_toc']
            self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/cat_pos_toc', cat_pos_toc)
        self.cat_pos_toc.setText(str(cat_pos_toc))

        for data in self.conf.catastro_tool['capas_urbanas']:
            rowPosition = self.tablaCapasUrbanas.rowCount()
            self.tablaCapasUrbanas.insertRow(rowPosition)
            self.tablaCapasUrbanas.setItem(rowPosition , 0, QTableWidgetItem(data['capa']))
            self.tablaCapasUrbanas.setItem(rowPosition , 1, QTableWidgetItem(data['nombre']))
            self.tablaCapasUrbanas.setItem(rowPosition , 2, QTableWidgetItem(data['estilo']))
        for data in self.conf.catastro_tool['capas_rusticas']:
            rowPosition = self.tablaCapasRusticas.rowCount()
            self.tablaCapasRusticas.insertRow(rowPosition)
            self.tablaCapasRusticas.setItem(rowPosition , 0, QTableWidgetItem(data['capa']))
            self.tablaCapasRusticas.setItem(rowPosition , 1, QTableWidgetItem(data['nombre']))
            self.tablaCapasRusticas.setItem(rowPosition , 2, QTableWidgetItem(data['estilo']))


        ''' DATA_INVENTARIO '''
        self.proviINVENTARIO = self.qs.value(f'{self.nombre_plugin}/INVENTARIO/INV_PROVINCIA')
        if self.proviINVENTARIO is None:
            if self.acceso == False:
                self.proviINVENTARIO = 'CM'
            else:
                self.proviINVENTARIO = 'CM'
        lista_provincias = [self.cbxInventarioPROVINCIA.itemText(i) for i in range(self.cbxInventarioPROVINCIA.count())]
        if self.proviINVENTARIO in lista_provincias:
            self.cbxInventarioPROVINCIA.setCurrentIndex(lista_provincias.index(self.proviINVENTARIO))

        # self.cbxPROVINCIA_updated



        # dato = self.qs.value(f'{self.nombre_plugin}/EXPROPIACION/EXPlayerLIMEXPRO')
        # if dato is None:
            # if self.acceso == False:
                # self.lneLayerEXPROPIACIONES.setText(self.conf.expropiacionB['EXPlayerLIMEXPRO'])
            # else:
                # self.lneLayerEXPROPIACIONES.setText(self.conf.expropiacion['EXPlayerLIMEXPRO'])
        # else:
            # self.lneLayerEXPROPIACIONES.setText(dato)





        ''' DATA_INTERNOS '''
        ###     UNIDADES    ###
        UD_SIGFOMSC = self.qs.value(f'{self.nombre_plugin}/DATOS_INT/UD_SIGFOMSC')
        if UD_SIGFOMSC is None:
            UD_SIGFOMSC = self.conf.data_internos['UD_SIGFOMSC']
            self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/UD_SIGFOMSC', UD_SIGFOMSC)
        self.lneUD_SIGFOMSC.setText(UD_SIGFOMSC)

        DIR_SIGFOMSC = self.qs.value(f'{self.nombre_plugin}/DATOS_INT/DIR_SIGFOMSC')
        if DIR_SIGFOMSC is None:
            DIR_SIGFOMSC = self.conf.data_internos['DIR_SIGFOMSC']
            self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/DIR_SIGFOMSC', DIR_SIGFOMSC)
        self.lneDIR_SIGFOMSC.setText(DIR_SIGFOMSC)

        UD_SIGFOMLO = self.qs.value(f'{self.nombre_plugin}/DATOS_INT/UD_SIGFOMLO')
        if UD_SIGFOMLO is None:
            UD_SIGFOMLO = self.conf.data_internos['UD_SIGFOMLO']
            self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/UD_SIGFOMLO', UD_SIGFOMLO)
        self.lneUD_SIGFOMLO.setText(UD_SIGFOMLO)

        DIR_SIGFOMLO = self.qs.value(f'{self.nombre_plugin}/DATOS_INT/DIR_SIGFOMLO')
        if DIR_SIGFOMLO is None:
            DIR_SIGFOMLO = self.conf.data_internos['DIR_SIGFOMLO']
            self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/DIR_SIGFOMLO', DIR_SIGFOMLO)
        self.lneDIR_SIGFOMLO.setText(DIR_SIGFOMLO)

        UD_SIGCTRLO = self.qs.value(f'{self.nombre_plugin}/DATOS_INT/UD_SIGCTRLO')
        if UD_SIGCTRLO is None:
            UD_SIGCTRLO = self.conf.data_internos['UD_SIGCTRLO']
            self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/UD_SIGCTRLO', UD_SIGCTRLO)
        self.lneUD_SIGCTRLO.setText(UD_SIGCTRLO)

        DIR_SIGCTRLO = self.qs.value(f'{self.nombre_plugin}/DATOS_INT/DIR_SIGCTRLO')
        if DIR_SIGCTRLO is None:
            DIR_SIGCTRLO = self.conf.data_internos['DIR_SIGCTRLO']
            self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/DIR_SIGCTRLO', DIR_SIGCTRLO)
        self.lneDIR_SIGCTRLO.setText(DIR_SIGCTRLO)

        UD_CARTOGSC = self.qs.value(f'{self.nombre_plugin}/DATOS_INT/UD_CARTOGSC')
        if UD_CARTOGSC is None:
            UD_CARTOGSC = self.conf.data_internos['UD_CARTOGSC']
            self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/UD_CARTOGSC', UD_CARTOGSC)
        self.lneUD_CARTOGSC.setText(UD_CARTOGSC)

        DIR_CARTOGSC = self.qs.value(f'{self.nombre_plugin}/DATOS_INT/DIR_CARTOGSC')
        if DIR_CARTOGSC is None:
            DIR_CARTOGSC = self.conf.data_internos['DIR_CARTOGSC']
            self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/DIR_CARTOGSC', DIR_CARTOGSC)
        self.lneDIR_CARTOGSC.setText(DIR_CARTOGSC)

        GDB_Geometrias = self.qs.value(f'{self.nombre_plugin}/DATOS_INT/GDB_Geometrias')
        if GDB_Geometrias is None:
            GDB_Geometrias = self.conf.data_internos['GDB_Geometrias']
            self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/GDB_Geometrias', GDB_Geometrias)
        self.GDB_Geometrias.setText(GDB_Geometrias)

        GDB_Aforos = self.qs.value(f'{self.nombre_plugin}/DATOS_INT/GDB_Aforos')
        if GDB_Aforos is None:
            GDB_Aforos = self.conf.data_internos['GDB_Aforos']
            self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/GDB_Aforos', GDB_Aforos)
        self.GDB_Aforos.setText(GDB_Aforos)

        # self.lneUD_SIGFOMSC.setText(self.conf.data_internos['UD_SIGFOMSC'])
        # self.lneDIR_SIGFOMSC.setText(self.conf.data_internos['DIR_SIGFOMSC'])
        # self.lneUD_SIGFOMLO.setText(self.conf.data_internos['UD_SIGFOMLO'])
        # self.lneDIR_SIGFOMLO.setText(self.conf.data_internos['DIR_SIGFOMLO'])
        # self.lneUD_SIGCTRLO.setText(self.conf.data_internos['UD_SIGCTRLO'])
        # self.lneDIR_SIGCTRLO.setText(self.conf.data_internos['DIR_SIGCTRLO'])
        # self.lneUD_CARTOGSC.setText(self.conf.data_internos['UD_CARTOGSC'])
        # self.lneDIR_CARTOGSC.setText(self.conf.data_internos['DIR_CARTOGSC'])

        ###     GEODATABASES    ###
        # self.gdbGEOMETRIA.setText(self.conf.data_internos['GDB_Geometrias'])
        # self.gdbAFOROS.setText(self.conf.data_internos['GDB_Aforos'])


        '''     EXPROPIACION     '''
        proviEXPRO = self.qs.value(f'{self.nombre_plugin}/EXPROPIACION/EXPprovincia')
        if proviEXPRO is None:
            if self.acceso == False:
                proviEXPRO = self.conf.expropiacionB['EXPprovincia']
            else:
                proviEXPRO = self.conf.expropiacion['EXPprovincia']
        lista_provincias = [self.cbxHerrExproPROVINCIA.itemText(i) for i in range(self.cbxHerrExproPROVINCIA.count())]
        if proviEXPRO in lista_provincias:
            self.cbxHerrExproPROVINCIA.setCurrentIndex(lista_provincias.index(proviEXPRO))

        dato = self.qs.value(f'{self.nombre_plugin}/EXPROPIACION/EXPlayerLIMEXPRO')
        if dato is None:
            if self.acceso == False:
                self.lneLayerEXPROPIACIONES.setText(self.conf.expropiacionB['EXPlayerLIMEXPRO'])
            else:
                self.lneLayerEXPROPIACIONES.setText(self.conf.expropiacion['EXPlayerLIMEXPRO'])
        else:
            self.lneLayerEXPROPIACIONES.setText(dato)

        dato = self.qs.value(f'{self.nombre_plugin}/EXPROPIACION/EXPlayerLIMEXPROFich')
        if dato is None:
            if self.acceso == False:
                self.lneFichEXPROPIACIONES.setText(self.conf.expropiacionB['EXPlayerLIMEXPROFich'])
            else:
                self.lneFichEXPROPIACIONES.setText(self.conf.expropiacion['EXPlayerLIMEXPROFich'])
        else:
            # self.lneFichEXPROPIACIONES.setText(dato)
            if dato.find('#') != -1:
                fichName, layerName = dato.split('#')
                # print (fichName, layerName)
                ext = os.path.splitext(fichName)[1]
                self.lneFichEXPROPIACIONES.setText(fichName)
                if ext == '.gpkg':
                    tipos = ['POLYGON','MULTIPOLYGON','POLYGONZ','MULTIPOLYGONZ','POLYGONM','MULTIPOLYGONM','POLYGONZM','MULTIPOLYGONZM','POLYGON25D','MULTIPOLYGON25D']
                    listLayers = self.fun.getListLayerGPKG(fichName, tipos)
                    self.cbxGDBcapaEXPROPIACIONES.clear()
                    self.cbxGDBcapaEXPROPIACIONES.addItems(listLayers)
                    self.cbxGDBcapaEXPROPIACIONES.setEnabled(True)
                    self.cbxGDBcapaEXPROPIACIONES.show()
                    if layerName in listLayers:
                        self.cbxGDBcapaEXPROPIACIONES.setCurrentIndex(listLayers.index(layerName))
                    listEXT = [self.cbxTIPOcapaEXPROPIACIONES.itemText(i) for i in range(self.cbxTIPOcapaEXPROPIACIONES.count())]
                    if ext in listEXT:
                        self.cbxTIPOcapaEXPROPIACIONES.setCurrentIndex(listEXT.index(ext))
                else:
                    self.cbxGDBcapaEXPROPIACIONES.hide()
            else:
                self.lneFichEXPROPIACIONES.setText(dato)
                self.cbxGDBcapaEXPROPIACIONES.hide()

        dato = self.qs.value(f'{self.nombre_plugin}/EXPROPIACION/EXPlayerLIMEXPROexptes')
        if dato is None:
            if self.acceso == False:
                self.lneDirEXPROPIACIONESexptes.setText(self.conf.expropiacionB['EXPlayerLIMEXPROexptes'])
            else:
                self.lneDirEXPROPIACIONESexptes.setText(self.conf.expropiacion['EXPlayerLIMEXPROexptes'])
        else:
            self.lneDirEXPROPIACIONESexptes.setText(dato)

        dato = self.qs.value(f'{self.nombre_plugin}/EXPROPIACION/EXPlayerINFOEXPRO')
        if dato is None:
            if self.acceso == False:
                self.lneLayerInfEXPROPIACIONES.setText(self.conf.expropiacionB['EXPlayerINFOEXPRO'])
            else:
                self.lneLayerInfEXPROPIACIONES.setText(self.conf.expropiacion['EXPlayerINFOEXPRO'])
        else:
            self.lneLayerInfEXPROPIACIONES.setText(dato)

        dato = self.qs.value(f'{self.nombre_plugin}/EXPROPIACION/EXPlayerINFOEXPROFich')
        if dato is None:
            if self.acceso == False:
                self.lneFichInfEXPROPIACIONES.setText(self.conf.expropiacionB['EXPlayerINFOEXPROFich'])
            else:
                self.lneFichInfEXPROPIACIONES.setText(self.conf.expropiacion['EXPlayerINFOEXPROFich'])
        else:
            # self.lneFichInfEXPROPIACIONES.setText(dato)
            if dato.find('#') != -1:
                fichName, layerName = dato.split('#')
                # print (fichName, layerName)
                ext = os.path.splitext(fichName)[1]
                self.lneFichInfEXPROPIACIONES.setText(fichName)
                if ext == '.gpkg':
                    tipos = ['POLYGON','MULTIPOLYGON','POLYGONZ','MULTIPOLYGONZ','POLYGONM','MULTIPOLYGONM','POLYGONZM','MULTIPOLYGONZM','POLYGON25D','MULTIPOLYGON25D']
                    listLayers = self.fun.getListLayerGPKG(fichName, tipos)
                    self.cbxGDBcapaInfEXPROPIACIONES.clear()
                    self.cbxGDBcapaInfEXPROPIACIONES.addItems(listLayers)
                    self.cbxGDBcapaInfEXPROPIACIONES.setEnabled(True)
                    self.cbxGDBcapaInfEXPROPIACIONES.show()
                    if layerName in listLayers:
                        self.cbxGDBcapaInfEXPROPIACIONES.setCurrentIndex(listLayers.index(layerName))
                    listEXT = [self.cbxTIPOcapaInfEXPROPIACIONES.itemText(i) for i in range(self.cbxTIPOcapaInfEXPROPIACIONES.count())]
                    if ext in listEXT:
                        self.cbxTIPOcapaInfEXPROPIACIONES.setCurrentIndex(listEXT.index(ext))
                else:
                    self.cbxGDBcapaInfEXPROPIACIONES.hide()
            else:
                self.lneFichInfEXPROPIACIONES.setText(dato)
                self.cbxGDBcapaInfEXPROPIACIONES.hide()

        dato = self.qs.value(f'{self.nombre_plugin}/EXPROPIACION/EXPlayerINFOEXPROexptes')
        if dato is None:
            if self.acceso == False:
                self.lneFichInfEXPROPIACIONESexptes.setText(self.conf.expropiacionB['EXPlayerINFOEXPROexptes'])
            else:
                self.lneFichInfEXPROPIACIONESexptes.setText(self.conf.expropiacion['EXPlayerINFOEXPROexptes'])
        else:
            self.lneFichInfEXPROPIACIONESexptes.setText(dato)

        dato = self.qs.value(f'{self.nombre_plugin}/EXPROPIACION/EXPlayerParcPATRI')
        if dato is None:
            if self.acceso == False:
                self.lneLayerParcPATRI.setText(self.conf.expropiacionB['EXPlayerParcPATRI'])
            else:
                self.lneLayerParcPATRI.setText(self.conf.expropiacion['EXPlayerParcPATRI'])
        else:
            self.lneLayerParcPATRI.setText(dato)

        dato = self.qs.value(f'{self.nombre_plugin}/EXPROPIACION/EXPlayerParcPATRIFich')
        if dato is None:
            if self.acceso == False:
                self.lneFichParcPATRI.setText(self.conf.expropiacionB['EXPlayerParcPATRIFich'])
            else:
                self.lneFichParcPATRI.setText(self.conf.expropiacion['EXPlayerParcPATRIFich'])
        else:
            # self.lneFichParcPATRI.setText(dato)
            if dato.find('#') != -1:
                fichName, layerName = dato.split('#')
                # print (fichName, layerName)
                ext = os.path.splitext(fichName)[1]
                self.lneFichParcPATRI.setText(fichName)
                if ext == '.gpkg':
                    tipos = ['POLYGON','MULTIPOLYGON','POLYGONZ','MULTIPOLYGONZ','POLYGONM','MULTIPOLYGONM','POLYGONZM','MULTIPOLYGONZM','POLYGON25D','MULTIPOLYGON25D']
                    listLayers = self.fun.getListLayerGPKG(fichName, tipos)
                    self.cbxGDBcapaParcPATRI.clear()
                    self.cbxGDBcapaParcPATRI.addItems(listLayers)
                    self.cbxGDBcapaParcPATRI.setEnabled(True)
                    self.cbxGDBcapaParcPATRI.show()
                    if layerName in listLayers:
                        self.cbxGDBcapaParcPATRI.setCurrentIndex(listLayers.index(layerName))
                    listEXT = [self.cbxTIPOcapaParcPATRI.itemText(i) for i in range(self.cbxTIPOcapaParcPATRI.count())]
                    if ext in listEXT:
                        self.cbxTIPOcapaParcPATRI.setCurrentIndex(listEXT.index(ext))
                else:
                    self.cbxGDBcapaParcPATRI.hide()
            else:
                self.lneFichParcPATRI.setText(dato)
                self.cbxGDBcapaParcPATRI.hide()

        dato = self.qs.value(f'{self.nombre_plugin}/EXPROPIACION/EXPlayerParcPATRIexptes')
        if dato is None:
            if self.acceso == False:
                self.lneFichParcPATRIexptes.setText(self.conf.expropiacionB['EXPlayerParcPATRIexptes'])
            else:
                self.lneFichParcPATRIexptes.setText(self.conf.expropiacion['EXPlayerParcPATRIexptes'])
        else:
            self.lneFichParcPATRIexptes.setText(dato)

        dato = self.qs.value(f'{self.nombre_plugin}/EXPROPIACION/EXP_GRUPEXPROfich')
        if dato is None:
            if self.acceso == False:
                self.lneEXPfich_GRUPEXPRO.setText(self.conf.expropiacionB['EXP_GRUPEXPROfich'])
            else:
                self.lneEXPfich_GRUPEXPRO.setText(self.conf.expropiacion['EXP_GRUPEXPROfich'])
        else:
            self.lneEXPfich_GRUPEXPRO.setText(dato)

        dato = self.qs.value(f'{self.nombre_plugin}/EXPROPIACION/EXP_GRUPEXPROnom')
        if dato is None:
            if self.acceso == False:
                self.lneNOM_GRUPEXPRO.setText(self.conf.expropiacionB['EXP_GRUPEXPROnom'])
            else:
                self.lneNOM_GRUPEXPRO.setText(self.conf.expropiacion['EXP_GRUPEXPROnom'])
        else:
            self.lneNOM_GRUPEXPRO.setText(dato)

        '''     EXPROPIACION (COPIA DE SEGURIDAD)    '''
        # Se comprueba si existe configuración usuario de ficheros de copia seguridad
        grupoCopyExpro = f'{self.nombre_plugin}/EXPROPIACION/EXP_COPYSEG'
        self.qs.beginGroup(grupoCopyExpro)
        listGrupoCopyExpro = self.qs.childKeys()
        self.qs.endGroup()
        # print ('listGrupoCopyExpro tiene '+str(len(listGrupoCopyExpro))+' entradas')

        for var in listGrupoCopyExpro:
            varChild = grupoCopyExpro+'/'+var
            valVar = self.qs.value(varChild)
            # print (var,' - ', valVar )

        if len(listGrupoCopyExpro) == 0:
            for data in self.conf.ficherosCopySeg:
                self.qlwFicherosCopySeg.addItem(data)
            for data in self.conf.extListCopySeg:
                self.qlwExtListCopySeg.addItem(data)
            self.lnedstDIR.setText(self.conf.dstDirCopySeg)

        else:
            # Se cargan las variables al menú desde configuración usuario
            for dato in listGrupoCopyExpro:
                if dato[0:15] == 'EXP_COPYSEGfile':
                    varChild = grupoCopyExpro+'/'+dato
                    valVar = self.qs.value(varChild)
                    self.qlwFicherosCopySeg.addItem(valVar)
                elif dato == 'EXP_COPYSEGext':
                    valVar = self.qs.value(grupoCopyExpro+'/'+dato)
                    for ext in valVar:
                        self.qlwExtListCopySeg.addItem(ext)
                elif dato == 'EXP_COPYSEGdirdst':
                    self.lnedstDIR.setText(self.qs.value(grupoCopyExpro+'/'+dato))

        ###  SE HACEN EDITABLES LAS LISTAS  qlwFicherosCopySeg / qlwExtListCopySeg ######
        ListCopySeg = self.qlwFicherosCopySeg
        ExtListCopySeg = self.qlwExtListCopySeg
        for index in range(ListCopySeg.count()):
            item = ListCopySeg.item(index)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
        for index in range(ExtListCopySeg.count()):
            item = ExtListCopySeg.item(index)
            item.setFlags(item.flags() | Qt.ItemIsEditable)


        '''             CAPAS_INICIO            '''
        self.tablaCapas.setColumnWidth(0, 40)   # data['type']      ANCHO 700
        self.tablaCapas.setColumnWidth(1, 200)  # data['nombre']
        self.tablaCapas.setColumnWidth(2, 250)  # data['source']
        self.tablaCapas.setColumnWidth(3, 150)  # data['estilo']
        self.tablaCapas.setColumnWidth(4, 60)   # data['grupo']
        self.tablaCapas.setColumnWidth(5, 120)  # data['agrupado']

        # FICHERO DE DATOS DE CAPAS
        fich_config = self.qs.value(f'{self.nombre_plugin}/GENERAL/fich_config_capas')
        if fich_config is None:
            fich_config = ''

        # Buscamos el fich_config en unidadpropia, Z: U:
        if not os.path.exists(fich_config) or fich_config == os.path.join(os.path.dirname(__file__), '.capasQSIG.txt'):
            uniProj = QgsProject.instance().fileName()[:2]
            listUnd = [uniProj, 'z:', 'u:']
            fich_config = u'z:/cartografia/datos_Q/QSIG/config/capasQSIG.txt'
            if self.fun.buscaFichUnd(listUnd, fich_config) is not None:
                fich_config = self.fun.buscaFichUnd(listUnd, fich_config)[0]
                self.qs.setValue(f'{self.nombre_plugin}/GENERAL/fich_config_capas', fich_config)

        # Buscamos el fich_config en la instalación del plugin
        if not os.path.exists(fich_config):
            fich_config = os.path.join(os.path.dirname(__file__), './capasQSIG.txt')

        # print ('fich_config: ', fich_config)

        linesFich = []
        with open(fich_config) as file:
            for line in file:
                line = line.strip()
                try:
                    res = ast.literal_eval(line)  # Metodo convert a dict ast
                    listKeys =  ['type','source','nombre','estilo','grupo','agrupado']
                    flag = 1
                    for key in listKeys:
                        if key not in res:
                            flag = 0
                    if flag == 1:
                        linesFich.append(res)
                        # else: print ('LINEA NULA: '+line)
                except:
                    # print ('LINEA NULA: '+line)
                    pass

        if len(linesFich) == 0:
            text = 'No hay capas correctas en el fichero de configuración\n\n'
            text += fich_config
            # print (text)

        for data in linesFich:
            rowPosition = self.tablaCapas.rowCount()
            self.tablaCapas.insertRow(rowPosition)
            # print data['type'],data['nombre'],data['source'],data['estilo'],data['grupo'],data['agrupado']
            if 'type' in data:
                self.tablaCapas.setItem(rowPosition , 0, QTableWidgetItem(data['type']))
            # if data.has_key('nombre'):
            if 'nombre' in data:
                self.tablaCapas.setItem(rowPosition , 1, QTableWidgetItem(data['nombre']))
            # if data.has_key('source'):
            if 'source' in data:
                self.tablaCapas.setItem(rowPosition , 2, QTableWidgetItem(data['source']))
            # if data.has_key('estilo'):
            if 'estilo' in data:
                self.tablaCapas.setItem(rowPosition , 3, QTableWidgetItem(data['estilo']))
            # if data.has_key('grupo'):
            if 'grupo' in data:
                self.tablaCapas.setItem(rowPosition , 4, QTableWidgetItem(data['grupo']))
            # if data.has_key('agrupado'):
            if 'agrupado' in data:
                self.tablaCapas.setItem(rowPosition , 5, QTableWidgetItem(data['agrupado']))

        ''' VARIABLES '''
        self.tablaListVar.setColumnWidth(0, 230)   # Nombre Variable      ANCHO 700
        self.tablaListVar.setColumnWidth(1, 40)    # Tipo variable
        self.tablaListVar.setColumnWidth(2, 550)   # Valor
        # self.tablaListVar.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )

        grupoPLUGIN = self.nombre_plugin
        
        self.lblLISTAVARIABLES.setText(f'LISTADO DE VARIABLES GRUPO: {self.nombre_plugin.upper()}')
        for var in self.qs.allKeys():
            if var.startswith( grupoPLUGIN ):
                valVar = self.qs.value(var)
                tipoVar = valVar.__class__.__name__
                if type(valVar) is list:
                    valVarlista = '['
                    for valor in valVar:
                        valVarlista += valor + ','
                    valVar = valVarlista[0:(len(valVarlista)-1)]
                    valVar += ']'
                # print (var,' - ', valVar )
                rowPosition = self.tablaListVar.rowCount()
                self.tablaListVar.insertRow(rowPosition)
                self.tablaListVar.setRowHeight(rowPosition, 15)
                # self.tablaListVar.setItem(rowPosition , 0, QTableWidgetItem(var[16:]))
                self.tablaListVar.setItem(rowPosition , 0, QTableWidgetItem(var.replace(grupoPLUGIN, '')))
                self.tablaListVar.setItem(rowPosition , 1, QTableWidgetItem(str(tipoVar)))
                if str(tipoVar) == 'str' or str(tipoVar) == 'list':
                    self.tablaListVar.setItem(rowPosition , 2, QTableWidgetItem(valVar))
                elif str(tipoVar) == 'int' or  str(tipoVar) == 'bool':
                    self.tablaListVar.setItem(rowPosition , 2, QTableWidgetItem(str(valVar)))



    '''
    ######################################################
    #########  FUNCIONES TAB LRS                 #########
    ######################################################
    '''

    def cbxTipo_consultaCAPA_changed(self):
        global tipo_consultaCAPA
        tipo_consultaCAPA = self.cbxTipo_consultaCAPA.currentText()
        self.qs.setValue(f'{self.nombre_plugin}/LRS/tipo_consultaCAPA', tipo_consultaCAPA)
        # print ('tipo_consultaCAPA: ', tipo_consultaCAPA, ' - tipo_consultaCAPA (QS): ', self.qs.value(f'{self.nombre_plugin}/LRS/tipo_consultaCAPA'))


    def btnSelectFichGpkg_clicked(self):
        sourceFile = self.lneFichGpkgCTRAS.text()
        extFile = u'*.gpkg'
        filename, tipoFile = QFileDialog.getOpenFileName(self, u'Selecciona fichero GPKG con SERVICIOS DE DATOS', sourceFile, extFile)
        if filename != None and filename != '':
            self.lneFichGpkgCTRAS.setText(filename)
            ext = os.path.splitext(filename)[1]

            tipos_lineas = ['LINESTRING', 'MULTILINESTRING', 'LINESTRINGZ', 'MULTILINESTRINGZ', 'LINESTRINGM', 'MULTILINESTRINGM', 'LINESTRINGZM', 'MULTILINESTRINGZM', 'LINESTRING25D', 'MULTILINESTRING25D']
            listLayers = self.fun.getListLayerGPKG(filename, tipos_lineas)
            nombre_capa_ctras = self.qs.value(f'{self.nombre_plugin}/LRS/nombre_capa_ctras')
            if nombre_capa_ctras in listLayers:
                self.cbxnombre_capa_ctras.clear()
                self.cbxnombre_capa_ctras.addItems(listLayers)
                self.cbxnombre_capa_ctras.setEnabled(True)
                self.cbxnombre_capa_ctras.setCurrentIndex(listLayers.index(nombre_capa_ctras))
            else:
                txt = u'El fichero GPKG'
                txt += '\n'+sourceFile
                txt += u'\n\nNO CONTIENE UNA CAPA CORRECTA DE CARRETERAS Y NO ES VÁLIDO'
                self.fun.showMessageERR(txt)
                self.lneFichGpkgCTRAS.setText(sourceFile)
                return

            tipos_poligonos = ['POLYGON','MULTIPOLYGON','POLYGONZ','MULTIPOLYGONZ','POLYGONM','MULTIPOLYGONM','POLYGONZM','MULTIPOLYGONZM','POLYGON25D','MULTIPOLYGON25D']
            listLayers = self.fun.getListLayerGPKG(filename, tipos_poligonos)
            nombre_capa_munis = self.qs.value(f'{self.nombre_plugin}/LRS/nombre_capa_munis')
            if nombre_capa_munis in listLayers:
                self.cbxnombre_capa_munis.clear()
                self.cbxnombre_capa_munis.addItems(listLayers)
                self.cbxnombre_capa_munis.setEnabled(True)
                self.cbxnombre_capa_munis.setCurrentIndex(listLayers.index(nombre_capa_munis))
            else:
                txt =  u'El fichero GPKG'
                txt += '\n'+sourceFile
                txt += u'\n\nNO CONTIENE UNAS CAPAS CORRECTAS Y NO ES VÁLIDO'
                self.fun.showMessageERR(txt)
                self.lneFichGpkgCTRAS.setText(sourceFile)
                return

            nombre_capa_pobla = self.qs.value(f'{self.nombre_plugin}/LRS/nombre_capa_pobla')
            if nombre_capa_pobla in listLayers:
                self.cbxnombre_capa_pobla.clear()
                self.cbxnombre_capa_pobla.addItems(listLayers)
                self.cbxnombre_capa_pobla.setEnabled(True)
                self.cbxnombre_capa_pobla.setCurrentIndex(listLayers.index(nombre_capa_pobla))
            else:
                txt =  u'El fichero GPKG'
                txt += '\n'+sourceFile
                txt += u'\n\nNO CONTIENE UNAS CAPAS CORRECTAS Y NO ES VÁLIDO'
                self.fun.showMessageERR(txt)
                self.lneFichGpkgCTRAS.setText(sourceFile)
                return


            # -------------------------------------------------------------
            # TODO PENDIENTE COMPROBAR SI LAS CAPAS SON DEL TIPO CORRECTAS
            #   PRIMERO MIRAR SI EL FICHERO CONTIENE ESAS CAPAS
            # -------------------------------------------------------------

        else:
            self.lneFichGpkgCTRAS.setText(sourceFile)


    def btnOriFichGpkgCTRAS_clicked(self):
        xteCtras = False
        xteMunis = False
        xtePobla = False
        nombre_capa_ctras = 'GEO_BTAcalibrada'
        nombre_capa_munis = 'GEO_Municipios_Zona'
        nombre_capa_pobla = 'GEO_NucleosPoblacion'

        sourceFile = self.btnOriFichGpkgCTRAS.text()
        if not os.path.isfile(sourceFile):
            sourceFile = self.lneFichGpkgCTRAS.text()

        extFile = u'*.gpkg'
        filename, tipoFile = QFileDialog.getOpenFileName(self, u'Selecciona fichero GPKG con SERVICIOS DE DATOS', sourceFile, extFile)
        # print ('filename: ', filename, 'tipoFile: ', tipoFile)
        if filename != None and filename != '':

            #Comprobamos si está la capa de ejes 'GEO_BTAcalibrada'
            tipos_lineas = ['LINESTRING', 'MULTILINESTRING', 'LINESTRINGZ', 'MULTILINESTRINGZ', 'LINESTRINGM', 'MULTILINESTRINGM', 'LINESTRINGZM', 'MULTILINESTRINGZM', 'LINESTRING25D', 'MULTILINESTRING25D']
            listLayersLin = self.fun.getListLayerGPKG(filename, tipos_lineas)
            if len(listLayersLin) != 0:
                if nombre_capa_ctras in listLayersLin: xteCtras = True

            tipos_poligonos = ['POLYGON','MULTIPOLYGON','POLYGONZ','MULTIPOLYGONZ','POLYGONM','MULTIPOLYGONM','POLYGONZM','MULTIPOLYGONZM','POLYGON25D','MULTIPOLYGON25D']
            listLayersPol = self.fun.getListLayerGPKG(filename, tipos_poligonos)
            if len(listLayersPol) != 0:
                #Comprobamos si está la capa de municipios 'GEO_Municipios_Zona'
                if nombre_capa_munis in listLayersPol: xteMunis = True

                #Comprobamos si está la capa de municipios 'GEO_NucleosPoblacion'
                if nombre_capa_pobla in listLayersPol: xtePobla = True

            if xteCtras == True and xteMunis == True and xteMunis == True:
                self.lneOriFichGpkgCTRAS.setText(filename)
            else:
                txt = u'El fichero GPKG'
                txt += '\n'+sourceFile
                txt += u'\n\nNO CONTIENE UNAS CAPAS CORRECTAS DE CARRETERAS Y NO ES VÁLIDO'
                txt += u'\n\n      -CAPAS-'
                for layer in listLayersLin: txt += '               '+layer
                for layer in listLayersPol: txt += '               '+layer
                self.fun.showMessageERR(txt)
                return

    def btnDestFichGpkgCTRAS_clicked(self):
        destDir = self.lneDestFichGpkgCTRAS.text()

        # Verificar si el directorio existe
        if not os.path.isdir(destDir):
            destDir = u'C:/cartografia/datos_Q/'

            # Abrir un cuadro de diálogo para seleccionar un directorio
            directorio = QFileDialog.getExistingDirectory(self, 'Seleccionar directorio Destino', destDir)

            # Verificar si se seleccionó un directorio
            if directorio:
                # Mostrar el resultado en el widget de línea
                self.lneDestFichGpkgCTRAS.setText(directorio)

    # def btnCopiar_GDB_CTRAS_clicked(self):
        # # Debe copiar el valor de sourceFile en destDir, advirtiendo si el fichero existe, además situará el valor
        # #       destDir + file (de sourdefile) en el widget linea self.lneFichGpkgCTRAS
        # sourceFile = self.btnOriFichGpkgCTRAS.text()
        # destDir = self.lneDestFichGpkgCTRAS.text()


    def btnCopiar_GDB_CTRAS_clicked(self):
        # Obtener la ruta del archivo de origen y el directorio de destino
        sourceFile = self.lneOriFichGpkgCTRAS.text()
        destDir = self.lneDestFichGpkgCTRAS.text()
        
        # Se comprueba si existe el fichero origen
        if not os.path.isfile(sourceFile):
            txt = u'El archivo\n   {} \n\nNO existe'.format(sourceFile)
            result = self.fun.showMessageERR(txt,'','EL FICHERO ORIGEN NO EXISTE')
            return

        # Obtener el nombre del archivo a partir de la ruta de origen
        fileName = os.path.basename(sourceFile)

        # Construir la ruta completa del archivo en el destino
        destFile = os.path.join(destDir, fileName)
        # Reemplazar las barras invertidas por barras inclinadas
        destFile = destFile.replace('\\', '/')

        # Verificar si el archivo de destino ya existe
        if os.path.exists(destFile):
            # Normalizar la ruta para asegurar que se muestra correctamente
            destFile = os.path.normpath(destFile)

            # Mostrar un cuadro de diálogo con la opción de sobrescribir o no
            txt = u'El archivo\n   {} \nya existe en el directorio de destino.'.format(destFile)
            result = self.fun.showMessageYESNO(txt,'','EL FICHERO YA EXISTE')
            if result != 1024: # No se ha pulsado ACEPTAR
                return

        try:
            # Copiar el archivo desde el origen al destino
            with open(sourceFile, 'rb') as src, open(destFile, 'wb') as dest:
                dest.write(src.read())

            # Actualizar el widget de línea con la ruta completa del archivo copiado
            self.lneFichGpkgCTRAS.setText(destFile)
            QMessageBox.information(self, 'Éxito', f'El archivo {fileName} se ha copiado exitosamente.')
        except Exception as e:
            # Manejar cualquier excepción que pueda ocurrir durante la copia
            QMessageBox.critical(self, 'Error', f'Error al copiar el archivo:\n{str(e)}')


    '''
    ######################################################
    #########  FUNCIONES TAB EXPROPIACIONES      #########
    ######################################################
    '''

    def TIPOcapaEXPROPIACIONES_updated(self):
        if self.cbxTIPOcapaEXPROPIACIONES.currentText() == '.shp':
            self.cbxGDBcapaEXPROPIACIONES.hide()
        else:
            self.cbxGDBcapaEXPROPIACIONES.show()
            if self.cbxGDBcapaEXPROPIACIONES.currentText()[:4] == '(Sel':
                self.cbxGDBcapaEXPROPIACIONES.setEnabled(False)
        pass

    def TIPOcapaInfEXPROPIACIONES_updated(self):
        if self.cbxTIPOcapaInfEXPROPIACIONES.currentText() == '.shp':
            self.cbxGDBcapaInfEXPROPIACIONES.hide()
        else:
            self.cbxGDBcapaInfEXPROPIACIONES.show()
            if self.cbxGDBcapaInfEXPROPIACIONES.currentText()[:4] == '(Sel':
                self.cbxGDBcapaInfEXPROPIACIONES.setEnabled(False)
        pass

    def TIPOcapaParcPATRI_updated(self):
        if self.cbxTIPOcapaParcPATRI.currentText() == '.shp':
            self.cbxGDBcapaParcPATRI.hide()
        else:
            self.cbxGDBcapaParcPATRI.show()
            if self.cbxGDBcapaParcPATRI.currentText()[:4] == '(Sel':
                self.cbxGDBcapaParcPATRI.setEnabled(False)
        pass

    def TIPOcapaOBFA_updated(self):
        if self.cbxTIPOcapaOBFA.currentText() == '.shp':
            self.cbxGDBcapaOBFA.hide()
        else:
            self.cbxGDBcapaOBFA.show()
            if self.cbxGDBcapaOBFA.currentText()[:4] == '(Sel':
                self.cbxGDBcapaOBFA.setEnabled(False)


    def tbtSelectFichConfigCapas_clicked(self):
        sourceFile = self.lneFichConfigCapas.text()
        extFile = u'Fich TXT (*.txt)'
        filename = QFileDialog.getOpenFileName(self, u'Selecciona fichero TXT de CONFIGURACIÓN DE CAPAS', sourceFile, extFile)
        if filename[0] != None and filename[0] != '':
            self.lneFichConfigCapas.setText(filename[0])
            ext = os.path.splitext(filename[0])[1]
        else:
            self.lneFichConfigCapas.setText(sourceFile)


    def tbtSelectLimExpro_clicked(self):
        sourceFile = self.lneFichEXPROPIACIONES.text()
        extFile = u'*'+self.cbxTIPOcapaEXPROPIACIONES.currentText()
        filename = QFileDialog.getOpenFileName(self, u'Selecciona fichero SHP de LÍMITES DE EXPROPIACIÓN', sourceFile, extFile)
        if filename[0] != None and filename[0] != '':
            self.lneFichEXPROPIACIONES.setText(filename[0])
            ext = os.path.splitext(filename[0])[1]
            if ext == '.gpkg':
                tipos = ['POLYGON','MULTIPOLYGON','POLYGONZ','MULTIPOLYGONZ','POLYGONM','MULTIPOLYGONM','POLYGONZM','MULTIPOLYGONZM','POLYGON25D','MULTIPOLYGON25D']
                listLayers = self.fun.getListLayerGPKG(filename[0], tipos)
                self.cbxGDBcapaEXPROPIACIONES.clear()
                self.cbxGDBcapaEXPROPIACIONES.addItems(listLayers)
                self.cbxGDBcapaEXPROPIACIONES.setEnabled(True)
        else:
            self.lneFichEXPROPIACIONES.setText(sourceFile)

    def tbtSelectInfoExpro_clicked(self):
        sourceFile = self.lneFichInfEXPROPIACIONES.text()
        extFile = u'*'+self.cbxTIPOcapaInfEXPROPIACIONES.currentText()
        filename = QFileDialog.getOpenFileName(self, u'Selecciona fichero SHP de Informes de Expropiaciones', sourceFile, extFile)
        if filename[0] != None and filename[0] != '':
            self.lneFichInfEXPROPIACIONES.setText(filename[0])
            ext = os.path.splitext(filename[0])[1]
            if ext == '.gpkg':
                tipos = ['POLYGON','MULTIPOLYGON','POLYGONZ','MULTIPOLYGONZ','POLYGONM','MULTIPOLYGONM','POLYGONZM','MULTIPOLYGONZM','POLYGON25D','MULTIPOLYGON25D']
                listLayers = self.fun.getListLayerGPKG(filename[0], tipos)
                self.cbxGDBcapaInfEXPROPIACIONES.clear()
                self.cbxGDBcapaInfEXPROPIACIONES.addItems(listLayers)
                self.cbxGDBcapaInfEXPROPIACIONES.setEnabled(True)
        else:
            self.lneFichInfEXPROPIACIONES.setText(sourceFile)

    def tbtSelectParcPATRI_clicked(self):
        sourceFile = self.lneFichParcPATRI.text()
        extFile = u'*'+self.cbxTIPOcapaParcPATRI.currentText()
        filename = QFileDialog.getOpenFileName(self, u'Selecciona fichero SHP de PARCELAS PATRIMONIALES', sourceFile, extFile)
        if filename[0] != None and filename[0] != '':
            self.lneFichParcPATRI.setText(filename[0])
            ext = os.path.splitext(filename[0])[1]
            if ext == '.gpkg':
                tipos = ['POLYGON','MULTIPOLYGON','POLYGONZ','MULTIPOLYGONZ','POLYGONM','MULTIPOLYGONM','POLYGONZM','MULTIPOLYGONZM','POLYGON25D','MULTIPOLYGON25D']
                listLayers = self.fun.getListLayerGPKG(filename[0], tipos)
                self.cbxGDBcapaParcPATRI.clear()
                self.cbxGDBcapaParcPATRI.addItems(listLayers)
                self.cbxGDBcapaParcPATRI.setEnabled(True)
        else:
            self.lneFichParcPATRI.setText(sourceFile)

    def tbtSelectGRUPOEXPRO_clicked(self):
        sourceFile = self.lneEXPfich_GRUPEXPRO.text()
        filename = QFileDialog.getOpenFileName(self, u'Selecciona fichero Grupo Expropiaciones', sourceFile, '*.qlr')
        if filename[0] != None and filename[0] != '':
            self.lneEXPfich_GRUPEXPRO.setText(filename[0])
        else:
            self.lneEXPfich_GRUPEXPRO.setText(sourceFile)

    def tbtSelectLimExproDir_clicked(self):
        sourceFile = self.lneDirEXPROPIACIONESexptes.text()
        dirpath = str(QFileDialog.getExistingDirectory(self, u'Selecciona DIRECTORIO DE EXPEDIENTES DE EXPROPIACIÓN', sourceFile, QFileDialog.ShowDirsOnly))
        if dirpath != None and dirpath != '':
            self.lneDirEXPROPIACIONESexptes.setText(dirpath)
        else:
            self.lneDirEXPROPIACIONESexptes.setText(sourceFile)

    def tbtSelectInfoExprDir_clicked(self):
        sourceFile = self.lneFichInfEXPROPIACIONESexptes.text()
        dirpath = str(QFileDialog.getExistingDirectory(self, u'Selecciona DIRECTORIO DE INFORMES DE EXPROPIACIONES', sourceFile, QFileDialog.ShowDirsOnly))
        if dirpath != None and dirpath != '':
            self.lneFichInfEXPROPIACIONESexptes.setText(dirpath)
        else:
            self.lneFichInfEXPROPIACIONESexptes.setText(sourceFile)

    def tbtSelectParcPATRIDir_clicked(self):
        sourceFile = self.lneFichParcPATRIexptes.text()
        dirpath = str(QFileDialog.getExistingDirectory(self, u'Selecciona DIRECTORIO DE BIENES PATRIMONIALES', sourceFile, QFileDialog.ShowDirsOnly))
        if dirpath != None and dirpath != '':
            self.lneFichParcPATRIexptes.setText(dirpath)
        else:
            self.lneFichParcPATRIexptes.setText(sourceFile)

    '''
    ######################################################
    #########         TAB INVENTARIO             #########
    ######################################################
    '''

    def cbx_provINVENTARIO_updated(self):
        self.proviINVENTARIO = self.cbxInventarioPROVINCIA.currentText()     # Provincia seleccionada para inventario
        # print (self.proviINVENTARIO)
        # PROVkey = 'Data_'+self.proviINVENTARIO[-2:]                          # Data_AB , key en el config
        if self.proviINVENTARIO:
            PROVkey = self.proviINVENTARIO[-2:]                                  # AB
        else:
            PROVkey = 'CM'
        # print ('PROVkey- ', PROVkey)

        if ('Data_'+PROVkey) in self.conf.INVENTARIO.keys():            # Data_AB , key en el config
            datosPROVI = self.conf.INVENTARIO['Data_'+PROVkey]                  # Bloque de datos de INVENTARIO
            listINVEN = ['OBFA', 'SEVE']
            listDATA  = ['source', 'estilo', 'nombre', 'tipo']
            txtERRORES = ''
            for tipoINVEN in listINVEN:
                for data in listDATA:
                    try:
                        dataKey = datosPROVI['INV_%s%s_%s'%(tipoINVEN, data, PROVkey)]
                        # print ('TODO VA BIEN CON key: INV_%s%s_%s'%(tipoINVEN, data, PROVkey))
                    except Exception as ex:
                        txtERRORES += 'Error en key: '+str(ex)+ '\n'
                        pass

            if txtERRORES != '':
                msg = u'ERRORES EN EL CONFIG.PY PARA LOS DATOS DE INVENTARIO DE '+self.proviINVENTARIO
                self.fun.errorManaging(txtERRORES, msg, True)
                self.lneFichOBFA.setText('')
                self.lneLayerOBFA.setText('')
                self.lneEstiloOBFA.setText('')
                self.lneFichSEVE.setText('')
                self.lneLayerSEVE.setText('')
                self.lneEstiloSEVE.setText('')
                return

            ##################################################################
            ######          DATOS GENERALES INVENTARIO               #########
            ##################################################################
            #  CM, AB, CR, CU, GU, TO
            self.proviINVENTARIO = self.qs.value(f'{self.nombre_plugin}/INVENTARIO/INV_PROVINCIA')
            try:
                PROVkey = self.proviINVENTARIO[-2:]                  # Data_AB , key en el config
            except:
                PROVkey = 'CM'                                       # Data_CM , key en el config
            # print ('PROVkey- ', PROVkey)

            if ('Data_'+PROVkey) in self.conf.INVENTARIO.keys():
                datosPROVI = self.conf.INVENTARIO['Data_'+PROVkey]   # Bloque de datos de INVENTARIO

            ########################################################### #######
            ######          DATOS OBFA                               #########
            ##################################################################
            dato = self.qs.value(f'{self.nombre_plugin}/INVENTARIO/INV_OBFAsource')
            if dato is None:
                dato=datosPROVI['INV_OBFAsource_'+PROVkey]

            posLYRNM=dato.lower().find('|layername=')
            self.lneLayerOBFA.setText(dato[(posLYRNM)+11:len(dato)])
            self.lneFichOBFA.setText(dato)

            tipoLYR=datosPROVI['INV_OBFAtipo_'+PROVkey][0]
            listatipoLYR = [self.cbxTIPOcapaOBFA.itemText(i) for i in range(self.cbxTIPOcapaOBFA.count())]
            if tipoLYR in listatipoLYR:
                self.cbxTIPOcapaOBFA.setCurrentIndex(listatipoLYR.index(tipoLYR))

            tipoCARGA=datosPROVI['INV_OBFAtipo_'+PROVkey][1]
            listatipoCARGA = [self.cbxTIPOcargaOBFA.itemText(i) for i in range(self.cbxTIPOcargaOBFA.count())]
            if tipoCARGA in listatipoCARGA:
                self.cbxTIPOcargaOBFA.setCurrentIndex(listatipoCARGA.index(tipoCARGA))

            dato = self.qs.value(f'{self.nombre_plugin}/IVENTARIO/INV_OBFAestilo')
            if dato is None:
                self.lneEstiloOBFA.setText(datosPROVI['INV_OBFAestilo_'+PROVkey])
            else:
                self.lneEstiloOBFA.setText(dato)

            ##################################################################
            ######          DATOS SEVE                               #########
            ##################################################################
            dato = self.qs.value(f'{self.nombre_plugin}/INVENTARIO/INV_SEVEsource')
            if dato is None:
                dato=datosPROVI['INV_SEVEsource_'+PROVkey]

            posLYRNM=dato.lower().find('|layername=')
            self.lneLayerSEVE.setText(dato[(posLYRNM)+11:len(dato)])
            self.lneFichSEVE.setText(dato)

            tipoLYR=datosPROVI['INV_SEVEtipo_'+PROVkey][0]
            listatipoLYR = [self.cbxTIPOcapaSEVE.itemText(i) for i in range(self.cbxTIPOcapaSEVE.count())]
            if tipoLYR in listatipoLYR:
                self.cbxTIPOcapaSEVE.setCurrentIndex(listatipoLYR.index(tipoLYR))

            tipoCARGA=datosPROVI['INV_SEVEtipo_'+PROVkey][1]
            listatipoCARGA = [self.cbxTIPOcargaSEVE.itemText(i) for i in range(self.cbxTIPOcargaSEVE.count())]
            if tipoCARGA in listatipoCARGA:
                self.cbxTIPOcargaSEVE.setCurrentIndex(listatipoCARGA.index(tipoCARGA))

            dato = self.qs.value(f'{self.nombre_plugin}/IVENTARIO/INV_SEVEestilo')
            if dato is None:
                self.lneEstiloSEVE.setText(datosPROVI['INV_SEVEestilo_'+PROVkey])
            else:
                self.lneEstiloSEVE.setText(dato)

        else:
            self.lneLayerOBFA.setText('')
            self.lneFichOBFA.setText('')
            self.lneEstiloOBFA.setText('')
            self.lneLayerSEVE.setText('')
            self.lneFichSEVE.setText('')
            self.lneEstiloSEVE.setText('')
            # print(u'NO HAY DATOS PARA EL INVENTARIO DE LA PROVINCIA %s'%(self.proviINVENTARIO))
            msg = u'NO HAY DATOS PARA EL INVENTARIO DE LA PROVINCIA %s'%(self.proviINVENTARIO)
            result = self.fun.showMessage(msg,text2='',tittle='JCCM. Error de CONFIG')


        pass


    def tbtSelectFileOBFA_clicked(self):
        sourceFileWDG = self.lneFichOBFA
        extFile       = u'*'+self.cbxTIPOcapaOBFA.currentText()
        filenameTEXTO = u'OBRAS DE FÁBRICA'
        result = self.tbtSelectFileBoton(sourceFileWDG, extFile, filenameTEXTO)

    def tbtSelectEstiloOBFA_clicked(self):
        sourceFileWDG = self.lneEstiloOBFA
        extFile       = '*.qml'
        filenameTEXTO = u'ESTILO FICHERO OBRAS DE FÁBRICA'
        result = self.tbtSelectFileBoton(sourceFileWDG, extFile, filenameTEXTO)

    def tbtSelectFileSEVE_clicked(self):
        sourceFileWDG = self.lneFichSEVE
        extFile       = u'*'+self.cbxTIPOcapaSEVE.currentText()
        filenameTEXTO = u'OBRAS DE FÁBRICA'
        result = self.tbtSelectFileBoton(sourceFileWDG, extFile, filenameTEXTO)

    def tbtSelectEstiloSEVE_clicked(self):
        sourceFileWDG = self.lneEstiloSEVE
        extFile       = '*.qml'
        filenameTEXTO = u'ESTILO FICHERO OBRAS DE FÁBRICA'
        result = self.tbtSelectFileBoton(sourceFileWDG, extFile, filenameTEXTO)


    def tbtSelectFileBoton(self, sourceFileWDG, extFile, filenameTEXTO):
        sourceFile = sourceFileWDG.text()
        # v:\INVENTARIO\OBRAS_FABRICA\AB\OF_Albacete.gpkg|layername=OF_Albacete
        # print ('sourceFile ANTES- ', sourceFile)
        if '.gpkg|' in sourceFile:
            pos = sourceFile.find('|')
            sourceFile = sourceFile[0:pos]
            # print ('sourceFile DESPU- ', sourceFile)

        # extFile = u'*'+extFileWDG.currentText()
        filename = QFileDialog.getOpenFileName(self, u'Selecciona fichero %s de %s'%(extFile,filenameTEXTO), sourceFile, extFile)
        if filename[0] != None and filename[0] != '':
            ext = os.path.splitext(filename[0])[1]
            if ext == '.gpkg':
                # tipos = ['POLYGON','MULTIPOLYGON','POLYGONZ','MULTIPOLYGONZ','POLYGONM','MULTIPOLYGONM','POLYGONZM','MULTIPOLYGONZM','POLYGON25D','MULTIPOLYGON25D']
                tipos = ['all']
                listLayers = self.fun.getListLayerGPKG01(filename[0], tipos)

                dialog = selectGPKG_dialog(self.iface, sourceFile,listLayers) # Llamamos al cuadro de dialogo tabla GPKG
                dialog.exec_()
                resultCAPA = dialog.resultDialog     # Lista de capas seleccionadas (SOLO DEBE SER UNA)
                if 'CANCELAR' in resultCAPA:         # Se ha pulsado CANCELAR
                    msg = u'SE DEBE SELECCIONAR ALGUNA CAPA'
                    sourceFileWDG.setText(filename[0])
                else:                                # Se ha pulsado ACEPTAR
                    # v:\INVENTARIO\OBRAS_FABRICA\AB\OF_Albacete.gpkg|layername=OF_Albacete
                    fileTable = u'%s|layername=%s'%(filename[0],resultCAPA[0])
                    sourceFileWDG.setText(fileTable)
                    # msg = fileTable

            else:
                sourceFileWDG.setText(filename[0])
        else:
            sourceFileWDG.setText(sourceFile)

        # self.fun.showMessage(msg,text2='',tittle='JCCM. Capa SELECCIONADA en GKPG')

    '''
    ######################################################
    ##                                                  ##
    #########          GUARDA CONFIG             #########
    ##                                                  ##
    ######################################################
    '''

    def guardar_VARconfig(self):
        ''' TAB GENERAL '''
        self.qs.setValue(f'{self.nombre_plugin}/GENERAL/EPSG',                self.lneEPSG.text())
        self.qs.setValue(f'{self.nombre_plugin}/GENERAL/01Ambito',            self.cbxPROVINCIA.currentText())
        self.qs.setValue(f'{self.nombre_plugin}/GENERAL/wfs_carreteras',      self.wfs_carreteras.text())
        self.qs.setValue(f'{self.nombre_plugin}/GENERAL/wfs_carreteras_layer',self.wfs_carreteras_layer.text())
        self.qs.setValue(f'{self.nombre_plugin}/GENERAL/rest_carreteras',     self.rest_carreteras.text())
        self.qs.setValue(f'{self.nombre_plugin}/GENERAL/rest_Pks',            self.rest_Pks.text())
        self.qs.setValue(f'{self.nombre_plugin}/GENERAL/rest_poblaciones',    self.rest_poblaciones.text())
        self.qs.setValue(f'{self.nombre_plugin}/GENERAL/campo_poblacion',     self.campo_poblacion.text())
        self.qs.setValue(f'{self.nombre_plugin}/GENERAL/rest_municipios',     self.rest_municipios.text())
        # self.qs.setValue(f'{self.nombre_plugin}/GENERAL/municipio_text_field',self.campo_muni.text())
        self.qs.setValue(f'{self.nombre_plugin}/GENERAL/carpeta_estilos',     self.carpeta_estilos.text())
        self.qs.setValue(f'{self.nombre_plugin}/GENERAL/urlWMSmdt',           self.urlWMSmdt.text())
        self.qs.setValue(f'{self.nombre_plugin}/GENERAL/urlWMSmdtLayer',      self.urlWMSmdtLayer.text())
        self.qs.setValue(f'{self.nombre_plugin}/GENERAL/urlWMSmdtValor',      self.urlWMSmdtValor.text())

        ''' TAB CAPAS '''
        self.qs.setValue(f'{self.nombre_plugin}/GENERAL/fich_config_capas',   self.lneFichConfigCapas.text())

        ''' TAB LRS '''
        self.qs.setValue(f'{self.nombre_plugin}/LRS/tipo_consultaCAPA',       self.cbxTipo_consultaCAPA.currentText())
        self.qs.setValue(f'{self.nombre_plugin}/LRS/ruta_geopackage',         self.lneFichGpkgCTRAS.text())
        self.qs.setValue(f'{self.nombre_plugin}/LRS/nombre_capa_ctras',       self.cbxnombre_capa_ctras.currentText())
        self.qs.setValue(f'{self.nombre_plugin}/LRS/nombre_capa_munis',       self.cbxnombre_capa_munis.currentText())
        self.qs.setValue(f'{self.nombre_plugin}/LRS/nombre_capa_pobla',       self.cbxnombre_capa_pobla.currentText())

        self.qs.setValue(f'{self.nombre_plugin}/LRS/OriFichGpkgCTRAS',         self.lneOriFichGpkgCTRAS.text())
        self.qs.setValue(f'{self.nombre_plugin}/LRS/DestFichGpkgCTRAS',         self.lneDestFichGpkgCTRAS.text())

        # ---------------------------------------------------------------------
        #     TODO FALTA INCORPORAR LOS DATOS DE TABLA  tablaFichGpkgCTRAS
        # ---------------------------------------------------------------------
        self.qs.setValue(f'{self.nombre_plugin}/LRS/id_ctra_carreteras',      self.identificador_carretera_carreteras.text())
        self.qs.setValue(f'{self.nombre_plugin}/LRS/carpeta_log',             self.carpeta_log.text())
        self.qs.setValue(f'{self.nombre_plugin}/LRS/bal_dest_path',           self.bal_dest_path.text())
        self.qs.setValue(f'{self.nombre_plugin}/LRS/bal_nom_layer',           self.bal_nom_layer.text())
        self.qs.setValue(f'{self.nombre_plugin}/LRS/bal_estiloCAPA',          self.bal_estiloCAPA.text())


        ''' TAB CATASTRO '''
        self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/url_catastro_distancia', self.url_catastro_distancia.text())
        self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/url_catastro_rc',        self.url_catastro_rc.text())
        self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/url_catastro_RCCOOR',    self.url_catastro_RCCOOR.text())
        self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/url_catastro_Provincia', self.url_catastro_Provincia.text())
        self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/url_catastro_municipio', self.url_catastro_municipio.text())
        self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/url_catastro_DNPRC',     self.url_catastro_DNPRC.text())
        self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/url_catastro_DNPPP',     self.url_catastro_DNPPP.text())
        self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/url_catastro_DescGML',   self.url_catastro_DescGML.text())

        self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/dir_shps',                 self.cat_dir_shps.text())
        self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/year',                     self.cat_year.text())
        self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/dir_estilos_catastro',     self.dir_estilos_catastro.text())
        self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/cat_pos_toc',              self.cat_pos_toc.text())

        ''' TAB INVENTARIO '''

        PROVkey = self.cbxInventarioPROVINCIA.currentText()[-2:]
        self.qs.setValue(f'{self.nombre_plugin}/INVENTARIO/INV_PROVINCIA',        PROVkey)
        '''  DATOS OBFA    '''
        self.qs.setValue(f'{self.nombre_plugin}/INVENTARIO/INV_OBFAsource_'+PROVkey,     self.lneFichOBFA.text())
        self.qs.setValue(f'{self.nombre_plugin}/INVENTARIO/INV_OBFAestilo_'+PROVkey,     self.lneEstiloOBFA.text())
        self.qs.setValue(f'{self.nombre_plugin}/INVENTARIO/INV_OBFAnombre_'+PROVkey,     self.lneLayerOBFA.text())
        self.qs.setValue(f'{self.nombre_plugin}/INVENTARIO/INV_OBFAtipo_'+PROVkey,       [self.cbxTIPOcapaOBFA.currentText(),self.cbxTIPOcargaOBFA.currentText()])
        '''  DATOS SEVE    '''
        self.qs.setValue(f'{self.nombre_plugin}/INVENTARIO/INV_SEVEsource_'+PROVkey,     self.lneFichSEVE.text())
        self.qs.setValue(f'{self.nombre_plugin}/INVENTARIO/INV_SEVEestilo_'+PROVkey,     self.lneEstiloSEVE.text())
        self.qs.setValue(f'{self.nombre_plugin}/INVENTARIO/INV_SEVEnombre_'+PROVkey,     self.lneLayerSEVE.text())
        self.qs.setValue(f'{self.nombre_plugin}/INVENTARIO/INV_SEVEtipo_'+PROVkey,       [self.cbxTIPOcapaSEVE.currentText(),self.cbxTIPOcargaSEVE.currentText()])



        ''' TAB DATOS_INT '''
        self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/UD_SIGFOMSC',       self.lneUD_SIGFOMSC.text())
        self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/UD_SIGFOMLO',       self.lneUD_SIGFOMLO.text())
        self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/UD_SIGCTRLO',       self.lneUD_SIGCTRLO.text())
        self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/UD_CARTOGSC',       self.lneUD_CARTOGSC.text())
        self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/DIR_SIGFOMSC',      self.lneDIR_SIGFOMSC.text())
        self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/DIR_SIGFOMLO',      self.lneDIR_SIGFOMLO.text())
        self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/DIR_SIGCTRLO',      self.lneDIR_SIGCTRLO.text())
        self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/DIR_CARTOGSC',      self.lneDIR_CARTOGSC.text())

        # self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/gdbGEOMETRIA',      self.GDB_Geometrias.text())
        self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/GDB_Geometrias',    self.GDB_Geometrias.text())
        # self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/gdbAFOROS',         self.GDB_Aforos.text())
        self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/GDB_Aforos',        self.GDB_Aforos.text())

        ''' TAB EXPROPIACIONES '''
        self.qs.setValue(f'{self.nombre_plugin}/EXPROPIACION/EXPprovincia',           self.cbxHerrExproPROVINCIA.currentText())
        self.qs.setValue(f'{self.nombre_plugin}/EXPROPIACION/EXPlayerLIMEXPRO',       self.lneLayerEXPROPIACIONES.text())
        self.qs.setValue(f'{self.nombre_plugin}/EXPROPIACION/EXPlayerLIMEXPROexptes', self.lneDirEXPROPIACIONESexptes.text())
        if os.path.splitext(self.lneFichEXPROPIACIONES.text())[1].lower() == '.shp':
            self.qs.setValue(f'{self.nombre_plugin}/EXPROPIACION/EXPlayerLIMEXPROFich',   self.lneFichEXPROPIACIONES.text())
        else:
            # Ponemos en LA VARIABLE correspondiente nomficheroGPKG#nomtabla
            var = self.lneFichEXPROPIACIONES.text() + '#'+ self.cbxGDBcapaEXPROPIACIONES.currentText()
            self.qs.setValue(f'{self.nombre_plugin}/EXPROPIACION/EXPlayerLIMEXPROFich',   var)

        self.qs.setValue(f'{self.nombre_plugin}/EXPROPIACION/EXPlayerINFOEXPRO',      self.lneLayerInfEXPROPIACIONES.text())
        self.qs.setValue(f'{self.nombre_plugin}/EXPROPIACION/EXPlayerINFOEXPROexptes',self.lneFichInfEXPROPIACIONESexptes.text())
        if os.path.splitext(self.lneFichInfEXPROPIACIONES.text())[1].lower() == '.shp':
            self.qs.setValue(f'{self.nombre_plugin}/EXPROPIACION/EXPlayerINFOEXPROFich',  self.lneFichInfEXPROPIACIONES.text())
        else:
            # Ponemos en LA VARIABLE correspondiente nomficheroGPKG#nomtabla
            var = self.lneFichInfEXPROPIACIONES.text() + '#'+ self.cbxGDBcapaInfEXPROPIACIONES.currentText()
            self.qs.setValue(f'{self.nombre_plugin}/EXPROPIACION/EXPlayerINFOEXPROFich',   var)

        self.qs.setValue(f'{self.nombre_plugin}/EXPROPIACION/EXPlayerParcPATRI',      self.lneLayerParcPATRI.text())
        self.qs.setValue(f'{self.nombre_plugin}/EXPROPIACION/EXPlayerParcPATRIexptes',self.lneFichParcPATRIexptes.text())
        # self.qs.setValue(f'{self.nombre_plugin}/EXPROPIACION/EXPlayerParcPATRIFich',  self.lneFichParcPATRI.text())
        # print (self.lneFichEXPROPIACIONES.text())
        # print (os.path.splitext(self.lneFichEXPROPIACIONES.text())[1])
        # print (os.path.splitext(self.lneFichEXPROPIACIONES.text())[1].lower() )
        if os.path.splitext(self.lneFichParcPATRI.text())[1].lower() == '.shp':
            self.qs.setValue(f'{self.nombre_plugin}/EXPROPIACION/EXPlayerParcPATRIFich',  self.lneFichParcPATRI.text())
        else:
            # Ponemos en LA VARIABLE correspondiente nomficheroGPKG#nomtabla
            var = self.lneFichParcPATRI.text() + '#'+ self.cbxGDBcapaParcPATRI.currentText()
            self.qs.setValue(f'{self.nombre_plugin}/EXPROPIACION/EXPlayerParcPATRIFich',   var)

        self.qs.setValue(f'{self.nombre_plugin}/EXPROPIACION/EXP_GRUPEXPROfich',      self.lneEXPfich_GRUPEXPRO.text())
        self.qs.setValue(f'{self.nombre_plugin}/EXPROPIACION/EXP_GRUPEXPROnom',       self.lneNOM_GRUPEXPRO.text())

        grupoCopyExpro =     f'{self.nombre_plugin}/EXPROPIACION/EXP_COPYSEG'
        for index in range(self.qlwFicherosCopySeg.count()):   # FICHEROS DE COPIA DE SEGURIDAD
            childValue = f'{self.nombre_plugin}/EXPROPIACION/EXP_COPYSEG/EXP_COPYSEGfile'+'{:0>2}'.format(index+1)
            # print (childValue, self.qlwFicherosCopySeg.item(index).text())
            self.qs.setValue(childValue, self.qlwFicherosCopySeg.item(index).text())
        listExt = []
        for index in range(self.qlwExtListCopySeg.count()):    # EXTENSIONES DE COPIA DE SEGURIDAD
            listExt.append(self.qlwExtListCopySeg.item(index).text())
        self.qs.setValue(grupoCopyExpro+'/'+'EXP_COPYSEGext', listExt)
        # print (listExt)
        self.qs.setValue(grupoCopyExpro+'/'+'EXP_COPYSEGdirdst', self.lnedstDIR.text()) # DIRECTORIO DE DESTINO DE COPIA DE SEGURIDAD


    def quitarCapa(self):
        # print 'Quitando capas'
        rows = self.tablaCapas.selectedItems()
        lineas = []
        for row in rows:
            if row.row() not in lineas:
                lineas.append(row.row())
        for l in lineas:
            self.tablaCapas.removeRow(l)
            self.flagCambio = 1


    def addCapaTable(self):
        self.newCapaDialog = Form_newCApa(self)
        #self.newCapaDialog.open()
        result = self.newCapaDialog.exec_()
        ## See if OK was pressed

        if result:
            capa = self.newCapaDialog.getValues()
            self.addCapaToTable(capa)
            self.flagCambio = 1


    def editarCapaTable(self):
        '''
        ESTO ESTÁ PENDIENTE
        Edición de capas de datos
        '''
        self.flagCambio = 1
        self.newCapaDialog = Form_newCApa(self)
        #self.newCapaDialog.open()
        result = self.newCapaDialog.exec_()
        ## See if OK was pressed

        if result:
            capa = self.newCapaDialog.getValues()
            self.addCapaToTable(capa)

        pass

    def addCapaToTable(self,capa):
        rowPosition = self.tablaCapas.rowCount()
        self.tablaCapas.insertRow(rowPosition)
        self.tablaCapas.setItem(rowPosition , 0, QTableWidgetItem(capa['type']))
        self.tablaCapas.setItem(rowPosition , 1, QTableWidgetItem(capa['nombre']))
        self.tablaCapas.setItem(rowPosition , 2, QTableWidgetItem(capa['source']))
        self.tablaCapas.setItem(rowPosition , 3, QTableWidgetItem(capa['estilo']))
        self.tablaCapas.setItem(rowPosition , 4, QTableWidgetItem(capa['grupo']))
        self.tablaCapas.setItem(rowPosition , 5, QTableWidgetItem(capa['agrupado']))
        pass

    def guardar_config(self):
        # print u'Guardando configuracion personalizada'
        filename = QFileDialog.getSaveFileName(self, 'Guardar configuracion', '', '*.py')
        if filename != None and filename != '':

            target  = codecs.open(filename, 'w+',encoding='utf8')
            target.write('#!/usr/bin/python')
            target.write('\n')
            target.write('# -*- coding: utf-8 -*-')
            target.write('\n')
            target.write('class custom_config:')
            # target.write('class configuration:')
            target.write('\n')

            ''' general(environment) '''
            target.write('  general = {')
            target.write('\n')
            target.write( "    'EPSG': " + self.lneEPSG.text() + ',')
            target.write('\n')
            target.write( "    'wfs_carreteras': u'" + self.wfs_carreteras.text() + "',")
            target.write('\n')
            target.write( "    'wfs_carreteras_layer': u'" + self.wfs_carreteras_layer.text() + "',")
            target.write('\n')
            target.write( "    'rest_carreteras': u'" + self.rest_carreteras.text() + "',")
            target.write('\n')
            target.write( "    'rest_Pks': u'" + self.rest_Pks.text() + "',")
            target.write("\n")
            target.write( "    'rest_poblaciones': u'" + self.rest_poblaciones.text() + "',")
            target.write("\n")
            target.write( "    'campo_poblacion': u'" + self.campo_poblacion.text() + "',")
            target.write("\n")
            target.write( "    'rest_municipios': u'" + self.rest_municipios.text() + "',")
            target.write("\n")
            # target.write( "    'municipio_text_field': u'" + self.campo_muni.text() + "',")
            # target.write("\n")
            target.write( "    'url_catastro_rc': u'" + self.url_catastro_rc.text() + "',")
            target.write("\n")
            target.write( "    'url_catastro_municipio': u'" + self.url_catastro_municipio.text() + "'")
            target.write("\n")
            target.write("    }")
            target.write("\n")

            """ catastro_tool """
            target.write("  catastro_tool ={")
            target.write("\n")
            target.write( "    'url_catastro_distancia': u'" + self.url_catastro_distancia.text() + "',")
            target.write("\n")
            target.write( "    'year': " + self.year.text() + ",")
            target.write("\n")
            target.write( "    'dir_shps': u'" + self.dir_shps.text() + "',")
            target.write("\n")
            target.write( "    'dir_estilos_catastro': u'" + self.dir_estilos_catastro.text() + "',")
            target.write("\n")
            target.write( "    'cat_pos_toc': " + self.cat_pos_toc.text() + ",")
            target.write("\n")
            target.write("    'capas_urbanas' : [")
            target.write("\n")
            rowcount = self.tablaCapasUrbanas.rowCount()
            for row in range(0,rowcount):
                capa = self.tablaCapasUrbanas.item(row,0).text()
                nombre = self.tablaCapasUrbanas.item(row,1).text()
                estilo = self.tablaCapasUrbanas.item(row,2).text()
                target.write("    { 'capa' : u'"+ capa  +"' , 'nombre' : u'"+ nombre  +"' , 'estilo' : u'"+ estilo  +"' }")
                if row != rowcount -1:
                    target.write(",")
                target.write("\n")
            target.write("   ],")
            target.write("\n")
            target.write("    'capas_rusticas' : [")
            target.write("\n")

            rowcount = self.tablaCapasRusticas.rowCount()
            for row in range(0,rowcount):
                capa = self.tablaCapasRusticas.item(row,0).text()
                nombre = self.tablaCapasRusticas.item(row,1).text()
                estilo = self.tablaCapasRusticas.item(row,2).text()
                target.write("    { 'capa' : u'"+ capa  +"' , 'nombre' : u'"+ nombre  +"' , 'estilo' : u'"+ estilo  +"' }")
                if row != rowcount -1:
                    target.write(",")
                target.write("\n")
            target.write("   ]")
            target.write("\n")
            target.write("    }")
            target.write("\n")

            """ lrs """
            target.write("  lrs = {")
            target.write("\n")
            target.write( "    'identificador_carretera_carreteras': u'" + self.identificador_carretera_carreteras.text() + "',")
            target.write("\n")
            target.write( "    'default_log_folder': u'" + self.carpeta_log.text() + "',")
            target.write("\n")
            target.write( "    'bal_dest_path': u'" + self.bal_dest_path.text() + "',")
            target.write("\n")
            target.write( "    'bal_nom_layer': u'" + self.bal_nom_layer.text() + "',")
            target.write("\n")
            target.write( "    'bal_estiloCAPA': u'" + self.bal_estiloCAPA.text() + "'")
            target.write("\n")
            target.write("    }")
            target.write("\n")

            target.write("  otros = {")
            target.write("\n")
            target.write( "    'carpeta_estilos': u'" + self.carpeta_estilos.text() + "'")
            target.write("\n")
            target.write("    }")
            target.write("\n")


            target.write("  capas_inicio = [")
            target.write("\n")
            rowcount = self.tablaCapas.rowCount()
            for row in range(0,rowcount):
                tipo = self.tablaCapas.item(row,0).text()
                nombre = self.tablaCapas.item(row,1).text()
                source = self.tablaCapas.item(row,2).text()
                estilo = self.tablaCapas.item(row,3).text()
                grupo = self.tablaCapas.item(row,4).text()
                if self.tablaCapas.item(row,5) is not None:
                    agrupado = self.tablaCapas.item(row,5).text()
                else:
                    agrupado = ''

                target.write("    { 'type' : u'"+ tipo  +"' , 'source' : u'"+ source +"' , 'nombre' : u'"+ nombre  +"' , 'estilo' : u'"+ estilo  +"' , 'grupo': u'" +  grupo + "' , 'agrupado': u'" +  agrupado + "' }")
                if row != rowcount -1:
                    target.write(",")
                target.write("\n")
            target.write("   ]")
            target.write("\n")

            """ data_internos """
            target.write("  data_internos = {")

            target.write("\n")
            target.write( "    'UD_SIGFOMSC': u'" + self.lneUD_SIGFOMSC.text() + "',")
            target.write("\n")
            target.write( "    'DIR_SIGFOMSC': u'" + self.lneDIR_SIGFOMSC.text() + "',")
            target.write("\n")
            target.write( "    'UD_SIGFOMLO': u'" + self.lneUD_SIGFOMLO.text() + "',")
            target.write("\n")
            target.write( "    'DIR_SIGFOMLO': u'" + self.lneDIR_SIGFOMLO.text() + "',")
            target.write("\n")
            target.write( "    'UD_SIGCTRLO': u'" + self.lneUD_SIGCTRLO.text() + "',")
            target.write("\n")
            target.write( "    'DIR_SIGCTRLO': u'" + self.lneDIR_SIGCTRLO.text() + "',")
            target.write("\n")
            target.write( "    'UD_CARTOGSC': u'" + self.lneUD_CARTOGSC.text() + "',")
            target.write("\n")
            target.write( "    'DIR_CARTOGSC': u'" + self.lneDIR_CARTOGSC.text() + "',")

            target.write("\n")
            target.write( "    'DIR_GRUPEXPRO': u'" + self.lneDIR_GRUPEXPRO.text() + "',")
            target.write("\n")
            target.write( "    'FICH_GRUPEXPRO': u'" + self.lneFICH_GRUPEXPRO.text() + "',")
            target.write("\n")
            target.write( "    'NOM_GRUPEXPRO': u'" + self.lneNOM_GRUPEXPRO.text() + "'")
            target.write("\n")
            target.write("    }")
            target.write("\n")
            target.write("\n")

            """ GENERALIDADES DEL FICHERO """
            # target.write("  max_features = "+ self.num_features.text())
            # target.write("\n")
            # target.write("  custom_configuration = u'" + self.custom_conf_value.text() + "'")
            # target.write("  custom_configuration = u'" + filename + "'")


            target.close()

            self.updateDefaultConfigCustom(filename)
            # self.custom_conf_value.setText(filename)

        pass



    def resetDefaultConfig(self):
        # TOMAMOS LA CONFIGURACIÓN DESDE self.conf.general

        '''
        # Se obtienen todos los datos del fichero config
        attrs = self.conf
        for bloque in inspect.getmembers(attrs):
            # Se eliminan funciones privadas y protegidas
            if not bloque[0].startswith('_'):
                # Se eliminan otros métodos que no empiezan por '_'
                if not inspect.ismethod(bloque[1]):
                    if type(bloque[1]) == list:
                        print ('Bloque ', bloque[0], ' es list')
                        print (bloque[1])
                    elif type(bloque[1]) == tuple:
                        print ('Bloque ', bloque[0], ' es tuple')
                        print (bloque[1])
                    else:
                        print ('Bloque ', bloque[0], ' es ', type(bloque[1]))
                        print (bloque[1])
        '''

        '''     GENERAL          '''
        ''' general (environment / otros) '''
        EPSG = self.conf.general['EPSG']
        self.qs.setValue(f'{self.nombre_plugin}/GENERAL/EPSG', EPSG)
        self.lneEPSG.setText(str(EPSG))

        # SALTAMOS EL DATO -AMBITO-

        wfs_carreteras = self.conf.general['wfs_carreteras']
        self.qs.setValue(f'{self.nombre_plugin}/GENERAL/wfs_carreteras', wfs_carreteras)
        self.wfs_carreteras.setText(wfs_carreteras)

        wfs_carreteras_layer = self.conf.general['wfs_carreteras_layer']
        self.qs.setValue(f'{self.nombre_plugin}/GENERAL/wfs_carreteras_layer', wfs_carreteras_layer)
        self.wfs_carreteras_layer.setText(wfs_carreteras_layer)

        rest_carreteras = self.conf.general['rest_carreteras']
        self.qs.setValue(f'{self.nombre_plugin}/GENERAL/rest_carreteras', rest_carreteras)
        self.rest_carreteras.setText(rest_carreteras)

        rest_Pks = self.conf.general['rest_Pks']
        self.qs.setValue(f'{self.nombre_plugin}/GENERAL/rest_Pks', rest_Pks)
        self.rest_Pks.setText(rest_Pks)

        rest_poblaciones = self.conf.general['rest_poblaciones']
        self.qs.setValue(f'{self.nombre_plugin}/GENERAL/rest_poblaciones', rest_poblaciones)
        self.rest_poblaciones.setText(rest_poblaciones)

        campo_poblacion = self.conf.general['campo_poblacion']
        self.qs.setValue(f'{self.nombre_plugin}/GENERAL/campo_poblacion', campo_poblacion)
        self.campo_poblacion.setText(campo_poblacion)

        rest_municipios = self.conf.general['rest_municipios']
        self.qs.setValue(f'{self.nombre_plugin}/GENERAL/rest_municipios', rest_municipios)
        self.rest_municipios.setText(rest_municipios)

        carpeta_estilos = self.conf.general['carpeta_estilos']
        self.qs.setValue(f'{self.nombre_plugin}/GENERAL/carpeta_estilos', carpeta_estilos)
        self.carpeta_estilos.setText(carpeta_estilos)

        fich_config_capas = self.conf.general['fich_config_capas']
        self.qs.setValue(f'{self.nombre_plugin}/GENERAL/fich_config_capas', fich_config_capas)
        self.lneFichConfigCapas.setText(fich_config_capas)

        urlWMSmdt = self.conf.general['urlWMSmdt']
        self.qs.setValue(f'{self.nombre_plugin}/GENERAL/urlWMSmdt', urlWMSmdt)
        self.urlWMSmdt.setText(urlWMSmdt)

        urlWMSmdtLayer = self.conf.general['urlWMSmdtLayer']
        self.qs.setValue(f'{self.nombre_plugin}/GENERAL/urlWMSmdtLayer', urlWMSmdtLayer)
        self.urlWMSmdtLayer.setText(urlWMSmdtLayer)

        urlWMSmdtValor = self.conf.general['urlWMSmdtValor']
        self.qs.setValue(f'{self.nombre_plugin}/GENERAL/urlWMSmdtValor', urlWMSmdtValor)
        self.urlWMSmdtValor.setText(urlWMSmdtValor)

        '''     LRS      '''
        id_ctra_carreteras = self.conf.lrs['identificador_carretera_carreteras']
        self.qs.setValue(f'{self.nombre_plugin}/LRS/id_ctra_carreteras', id_ctra_carreteras)
        self.identificador_carretera_carreteras.setText(id_ctra_carreteras)

        carpeta_log = self.conf.lrs['default_log_folder']
        self.qs.setValue(f'{self.nombre_plugin}/LRS/carpeta_log', carpeta_log)
        self.carpeta_log.setText(carpeta_log)

        bal_dest_path = self.conf.lrs['bal_dest_path']
        self.qs.setValue(f'{self.nombre_plugin}/LRS/bal_dest_path', bal_dest_path)
        self.bal_dest_path.setText(bal_dest_path)

        bal_nom_layer = self.conf.lrs['bal_nom_layer']
        self.qs.setValue(f'{self.nombre_plugin}/LRS/bal_nom_layer', bal_nom_layer)
        self.bal_nom_layer.setText(bal_nom_layer)

        bal_estiloCAPA = self.conf.lrs['bal_estiloCAPA']
        self.qs.setValue(f'{self.nombre_plugin}/LRS/bal_estiloCAPA', bal_estiloCAPA)
        self.bal_estiloCAPA.setText(bal_estiloCAPA)

        '''             CATASTRO_TOOL           '''
        url_catastro_distancia = self.conf.catastro_tool['url_catastro_distancia']
        self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/url_catastro_distancia', url_catastro_distancia)
        self.url_catastro_distancia.setText(url_catastro_distancia)

        url_catastro_rc = self.conf.catastro_tool['url_catastro_rc']
        self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/url_catastro_rc', url_catastro_rc)
        self.url_catastro_rc.setText(url_catastro_rc)

        url_catastro_Provincia = self.conf.catastro_tool['url_catastro_Provincia']
        self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/url_catastro_Provincia', url_catastro_Provincia)
        self.url_catastro_Provincia.setText(url_catastro_Provincia)

        url_catastro_municipio = self.conf.catastro_tool['url_catastro_municipio']
        self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/url_catastro_municipio', url_catastro_municipio)
        self.url_catastro_municipio.setText(url_catastro_municipio)

        url_catastro_RCCOOR = self.conf.catastro_tool['url_catastro_RCCOOR']
        self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/url_catastro_RCCOOR', url_catastro_RCCOOR)
        self.url_catastro_RCCOOR.setText(url_catastro_RCCOOR)

        url_catastro_DNPRC = self.conf.catastro_tool['url_catastro_DNPRC']
        self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/url_catastro_DNPRC', url_catastro_DNPRC)
        self.url_catastro_DNPRC.setText(url_catastro_DNPRC)

        url_catastro_DNPPP = self.conf.catastro_tool['url_catastro_DNPPP']
        self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/url_catastro_DNPPP', url_catastro_DNPPP)
        self.url_catastro_DNPPP.setText(url_catastro_DNPPP)

        url_catastro_DescGML = self.conf.catastro_tool['url_catastro_DescGML']
        self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/url_catastro_DescGML', url_catastro_DescGML)
        self.url_catastro_DescGML.setText(url_catastro_DescGML)

        cat_dir_shps = self.conf.catastro_tool['cat_dir_shps']
        self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/cat_dir_shps', cat_dir_shps)
        self.cat_dir_shps.setText(cat_dir_shps)

        cat_year = self.conf.catastro_tool['cat_year']
        self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/cat_year', cat_year)
        self.cat_year.setText(str(cat_year))

        dir_estilos_catastro = self.conf.catastro_tool['dir_estilos_catastro']
        self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/dir_estilos_catastro', dir_estilos_catastro)
        self.dir_estilos_catastro.setText(dir_estilos_catastro)

        cat_pos_toc = self.conf.catastro_tool['cat_pos_toc']
        self.qs.setValue(f'{self.nombre_plugin}/CATASTRO/cat_pos_toc', cat_pos_toc)
        self.cat_pos_toc.setText(str(cat_pos_toc))

        ''' DATA_INVENTARIO '''
        ## PENDIENTE DE CREACIÓN

        ''' DATA_INTERNOS '''
        ###     UNIDADES    ###
        UD_SIGFOMSC = self.conf.data_internos['UD_SIGFOMSC']
        self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/UD_SIGFOMSC', UD_SIGFOMSC)
        self.lneUD_SIGFOMSC.setText(UD_SIGFOMSC)

        DIR_SIGFOMSC = self.conf.data_internos['DIR_SIGFOMSC']
        self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/DIR_SIGFOMSC', DIR_SIGFOMSC)
        self.lneDIR_SIGFOMSC.setText(DIR_SIGFOMSC)

        UD_SIGFOMLO = self.conf.data_internos['UD_SIGFOMLO']
        self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/UD_SIGFOMLO', UD_SIGFOMLO)
        self.lneUD_SIGFOMLO.setText(UD_SIGFOMLO)

        DIR_SIGFOMLO = self.conf.data_internos['DIR_SIGFOMLO']
        self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/DIR_SIGFOMLO', DIR_SIGFOMLO)
        self.lneDIR_SIGFOMLO.setText(DIR_SIGFOMLO)

        UD_SIGCTRLO = self.conf.data_internos['UD_SIGCTRLO']
        self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/UD_SIGCTRLO', UD_SIGCTRLO)
        self.lneUD_SIGCTRLO.setText(UD_SIGCTRLO)

        DIR_SIGCTRLO = self.conf.data_internos['DIR_SIGCTRLO']
        self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/DIR_SIGCTRLO', DIR_SIGCTRLO)
        self.lneDIR_SIGCTRLO.setText(DIR_SIGCTRLO)

        UD_CARTOGSC = self.conf.data_internos['UD_CARTOGSC']
        self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/UD_CARTOGSC', UD_CARTOGSC)
        self.lneUD_CARTOGSC.setText(UD_CARTOGSC)

        DIR_CARTOGSC = self.conf.data_internos['DIR_CARTOGSC']
        self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/DIR_CARTOGSC', DIR_CARTOGSC)
        self.lneDIR_CARTOGSC.setText(DIR_CARTOGSC)

        GDB_Geometrias = self.conf.data_internos['GDB_Geometrias']
        self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/GDB_Geometrias', GDB_Geometrias)
        self.GDB_Geometrias.setText(GDB_Geometrias)

        GDB_Aforos = self.conf.data_internos['GDB_Aforos']
        self.qs.setValue(f'{self.nombre_plugin}/DATOS_INT/GDB_Aforos', GDB_Aforos)
        self.GDB_Aforos.setText(GDB_Aforos)

        # VARIABLES DEL FICHERO DE METADATOS
        mtdt = configparser.ConfigParser()

        fileMetadata = os.path.join(os.path.dirname(__file__), 'metadata.txt')
        mtdt.read(fileMetadata)
        email= mtdt.get('general', 'email')
        telefono= mtdt.get('general', 'telephone')

        msg = u'NO SE HA CAMBIADO LA CONFIGURACIÓN DE LOS SIGUIENTES DATOS:\n'
        msg +='   - AMBITO TRABAJO  - Provincia o zona de trabajo\n'
        msg +='   - CAPAS           - Por defecto se leen del directorio de trabajo\n'
        msg +='   - INVENTARIO      - Todo este módulo está en desarrollo (29/9/22)\n'
        msg +='   - DOMINIO PÚBLICO - Ficheros y directorios de trabajo enDP\n'
        msg +='\n\n'
        msg +='      ESTOS DATOS SE DEBEN INTRODUCIR MANUALMENTE\n'
        msg +='      O CONSULTAR CON DESARROLLO'
        msg +='\n\n'
        msg +='      CONTACTO:\n'
        msg +='           Correo electrónico: %s Tfno: %s'%(email, telefono)

        self.fun.showMessage(msg)



    def updateDefaultConfigCustom(self, new_config):
        #Create temp file

        file_path =  os.path.dirname(__file__) + '\config.py'

        fh, abs_path = mkstemp()
        with open(abs_path,'w') as new_file:
            with open(file_path) as old_file:
                for line in old_file:
                    if 'custom_configuration' in line:
                        new_file.write("  custom_configuration= u'" + new_config + "'")
                    else:
                        new_file.write(line)
        close(fh)
        #Remove original file
        remove(file_path)
        #Move new file
        move(abs_path, file_path)
        reloadPlugin('jccm_bar3')
        self.close()

    def cargar_conf(self):
        filename = QFileDialog.getOpenFileName(self, 'Cargar archivo de configuracion','', '*.py')
        if filename != None and filename != '':
            self.updateDefaultConfigCustom(filename)
            #plugins_list = sorted(plugins.keys())
            #reloadPlugin('jccm_bar')
            self.close()

        pass

    def change_text(self,text, encoding):
        return text.encode(encoding,'ignore')



class reordenaVariables:
    def reordenaVariables():
        qs = QSettings()

        nombre_plugin = os.path.basename(os.path.dirname(__file__))

        dato = qs.value(f'{nombre_plugin}/EXPprovincia')
        if dato is not None:
            qs.setValue(f'{nombre_plugin}/EXPROPIACION/EXPprovincia', dato)
            qs.remove(f'{nombre_plugin}/EXPprovincia')

        dato = qs.value(f'{nombre_plugin}/EXPlayerLIMEXPRO')
        if dato is not None:
            qs.setValue(f'{nombre_plugin}/EXPROPIACION/EXPlayerLIMEXPRO', dato)
            qs.remove(f'{nombre_plugin}/EXPlayerLIMEXPRO')

        dato = qs.value(f'{nombre_plugin}/EXPlayerLIMEXPROFich')
        if dato is not None:
            qs.setValue(f'{nombre_plugin}/EXPROPIACION/EXPlayerLIMEXPROFich', dato)
            qs.remove(f'{nombre_plugin}/EXPlayerLIMEXPROFich')

        dato = qs.value(f'{nombre_plugin}/EXPlayerINFOEXPRO')
        if dato is not None:
            qs.setValue(f'{nombre_plugin}/JCCM_EXPRO/EXPlayerINFOEXPRO', dato)
            qs.remove(f'{nombre_plugin}/EXPlayerINFOEXPRO')

        dato = qs.value(f'{nombre_plugin}/EXPlayerINFOEXPROFich')
        if dato is not None:
            qs.setValue(f'{nombre_plugin}/JCCM_EXPRO/EXPlayerINFOEXPROFich', dato)
            qs.remove(f'{nombre_plugin}/EXPlayerINFOEXPROFich')
