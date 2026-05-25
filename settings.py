# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name:           settings.py
Purpose:    Configuración inicial del pluggin jccm_bar3 y del QGIS3

        --------------------------------------------------------------------
        begin                : 2019-06-05
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
# VERSION QGIS3

from PyQt5.QtCore import QSettings
from qgis.utils import iface
from qgis.core import QgsProject, QgsExpressionContextUtils, QgsApplication, QgsCoordinateReferenceSystem

import os
import sqlite3

from .config import configuration        # CLASE DE CONFIGURACIÓN DE VARIABLES DEL PROGRAMA
from .functions3 import Functions        # CLASE DE CONFIGURACIÓN DE FUNCIONES GENERALES

conf = configuration()

# VARIABLES
srcVal = conf.general["EPSG"]

class Settings:

    def initVAR(self):
        self.qs = QSettings()
        self.fun = Functions()
        self.conf = configuration()


        #       --  Detectamos la UNIDAD del Proyecto
        dirOS = os.getcwd()
        Proj = QgsProject.instance().fileName()
        uniProj = Proj[:2]
        
        #       --  Variables Generales DE USUARIO --
        self.qs.setValue('Qgis/enableMacros',3)                      # Activar Macros - Siempre
        self.qs.setValue('Qgis/warnOldProjectVersion', False)        # Avisar de Proyecto guardado con version ant. - false
        self.qs.setValue('Qgis/checkVersion', False)                 # Chequear Version QGIS al empezar
        self.qs.setValue('Qgis/askToSaveProjectChanges', False)      # Quita el aviso inicial de guardar

        #       --  Proyección a emplear --
        # EPSG = '25830'
        EPSG = str(srcVal)
        ################################################################################
        ####            CONTROL SE DEBE AVISAR SI NO COINCIDE EL SRC                ####
        ################################################################################
        self.qs.setValue('Projections/defaultBehavior', 'useProject')            # Projections/defaultBehaviour - useProject
        self.qs.setValue('Projections/layerDefaultCrs', 'EPSG:'+EPSG)            # Projections/layerDefaultCrs - EPSG:25830
        self.qs.setValue('Projections/projectDefaultCrs', 'EPSG:'+EPSG)          # Projections/projectDefaultCrs - EPSG:25830
        self.qs.setValue('Projections/otfTransformAutoEnable', True)             # Projections/otfTransformAutoEnable - true
        self.qs.setValue('Projections/otfTransformEnabled', False)               # Projections/otfTransformEnabled - false
        self.qs.setValue('Projections/showDatumTransformDialog', False)          # Projections/showDatumTransformDialog - false
        dirTemplates = uniProj+u'\cartografia\datos_Q\QSIG\PLANTILLAS'      
        self.qs.setValue('Composer/searchPathsForTemplates',[dirTemplates])      # Composer/searchPathsForTemplates
        # qs.setValue('Composer/searchPathsForTemplates',[u'Z:\cartografia\datos_Q\QSIG\PLANTILLAS'])
        # qs.setValue('Composer/searchPathsForTemplates',[u'U:\cartografia\datos_Q\QSIG\PLANTILLAS'])



        #  -- Variables del PROYECTO --  
        # Directorios de trabajo 
        DIRCATlocal = u'z:/Cartografia_COTYV/03_CARTOGRAFIA_ORIGINAL_OFICIAL/DG_CATASTRO/'
        DIRCATservtol = u'w:/03_CARTOGRAFIA_ORIGINAL_OFICIAL/DG_CATASTRO/'

        # QgsExpressionContextUtils.setProjectVariable('DIRCATlocal',DIRCATlocal)
        QgsExpressionContextUtils.setProjectVariable(QgsProject.instance(),'DIRCATlocal',DIRCATlocal)
        # QgsExpressionContextUtils.setProjectVariable('DIRCATservtol',DIRCATservtol)
        QgsExpressionContextUtils.setProjectVariable(QgsProject.instance(),'DIRCATservtol',DIRCATservtol)
        
        global gml_salida_file
        
        # print (u'Configuradas las Variables')
        return uniProj
        
    def entrarUser(self):
        # Control de accesos a la aplicacion por medio de USER
        #  --------------------------------------------------------------------
        #                     USUARIOS EDITORES Y ADMINISTRADORES
        #  --------------------------------------------------------------------
        qs = QSettings()

        userEdit =  ['aass04', 'ffas09', 'agusa']
        # userEdit =  ['aass04', 'ffas09']
        userAdmin = ['aass04', 'agusa']
        # userAdmin = ['aass04']
        #  --------------------------------------------------------------------
        
        tittle = u'SIG REGIONAL DE CARRETERAS'
        # msg = QMessageBox()
        
        userSIG = os.environ.get('USERNAME')
        userSIGequipo = os.environ.get('LOGONSERVER')
        if userSIG in userEdit:
            tipoUser = 'EDITOR'
            # QgsExpressionContextUtils.setProjectVariable(QgsProject.instance(),'ACCESOEDITOR','True')
            qs.setValue('JCCM_carreteras/ACCESOEDITOR', True)

            if userSIG in userAdmin:
                tipoUser = 'ADMINISTRADOR'
        else:
            tipoUser = 'BASICO QGIS'
            # QgsExpressionContextUtils.setProjectVariable(QgsProject.instance(),'ACCESOEDITOR','False')
            qs.setValue('JCCM_carreteras/ACCESOEDITOR', False)

        return (userSIG, tipoUser)
        
        
    def setVarUser(self):
        self.qs = QSettings()
        self.conf = configuration()

        # qs.setValue('JCCM_carreteras/00firstUse', False)            # Variable firstUse
        # qs.setValue('JCCM_carreteras/02tipoUser', 'Usuario')        # Variable tipoUser
        
        '''-------------------------------------'''
        '''              GENERAL                '''
        '''-------------------------------------'''
        ''' general (environment / otros / capas) '''
        EPSG = self.qs.value("JCCM_carreteras/GENERAL/EPSG")
        if EPSG is None:
            EPSG = self.conf.general['EPSG']
            self.qs.setValue("JCCM_carreteras/GENERAL/EPSG", EPSG)
        
        Ambito = self.qs.value("JCCM_carreteras/GENERAL/01Ambito")
        if Ambito is None:
            Ambito = self.conf.general["01Ambito"]
            self.qs.setValue("JCCM_carreteras/GENERAL/01Ambito", Ambito)

        wfs_carreteras = self.qs.value("JCCM_carreteras/GENERAL/wfs_carreteras")
        if wfs_carreteras is None:
            wfs_carreteras = self.conf.general['wfs_carreteras']
            self.qs.setValue("JCCM_carreteras/GENERAL/wfs_carreteras", wfs_carreteras)

        wfs_carreteras_layer = self.qs.value("JCCM_carreteras/GENERAL/wfs_carreteras_layer")
        if wfs_carreteras_layer is None:
            wfs_carreteras_layer = self.conf.general['wfs_carreteras_layer']
            self.qs.setValue("JCCM_carreteras/GENERAL/wfs_carreteras_layer", wfs_carreteras_layer)

        rest_carreteras = self.qs.value("JCCM_carreteras/GENERAL/rest_carreteras")
        if rest_carreteras is None:
            rest_carreteras = self.conf.general['rest_carreteras']
            self.qs.setValue("JCCM_carreteras/GENERAL/rest_carreteras", rest_carreteras)

        rest_Pks = self.qs.value("JCCM_carreteras/GENERAL/rest_Pks")
        if rest_Pks is None:
            rest_Pks = self.conf.general['rest_Pks']
            self.qs.setValue("JCCM_carreteras/GENERAL/rest_Pks", rest_Pks)

        rest_poblaciones = self.qs.value("JCCM_carreteras/GENERAL/rest_poblaciones")
        if rest_poblaciones is None:
            rest_poblaciones = self.conf.general['rest_poblaciones']
            self.qs.setValue("JCCM_carreteras/GENERAL/rest_poblaciones", rest_poblaciones)

        campo_poblacion = self.qs.value("JCCM_carreteras/GENERAL/campo_poblacion")
        if campo_poblacion is None:
            campo_poblacion = self.conf.general['campo_poblacion']
            self.qs.setValue("JCCM_carreteras/GENERAL/campo_poblacion", campo_poblacion)
        
        rest_municipios = self.qs.value("JCCM_carreteras/GENERAL/rest_municipios")
        if rest_municipios is None:
            rest_municipios = self.conf.general['rest_municipios']
            self.qs.setValue("JCCM_carreteras/GENERAL/rest_municipios", rest_municipios)

        carpeta_estilos = self.qs.value("JCCM_carreteras/GENERAL/carpeta_estilos")
        if carpeta_estilos is None:
            carpeta_estilos = self.conf.general['carpeta_estilos']
            self.qs.setValue("JCCM_carreteras/GENERAL/carpeta_estilos", carpeta_estilos)
        
        JCCM_fich_config = self.qs.value("JCCM_carreteras/GENERAL/JCCM_fich_config")
        if JCCM_fich_config is None:
            JCCM_fich_config = self.conf.general["fich_config_capas"]
            self.qs.setValue("JCCM_carreteras/GENERAL/fich_config_capas", JCCM_fich_config)
        
        '''-------------------------------------'''
        '''                 LRS                 '''
        '''-------------------------------------'''
        id_ctra_carreteras = self.qs.value("JCCM_carreteras/LRS/id_ctra_carreteras")
        if id_ctra_carreteras is None:
            id_ctra_carreteras = self.conf.lrs["identificador_carretera_carreteras"]
            self.qs.setValue("JCCM_carreteras/LRS/id_ctra_carreteras", id_ctra_carreteras)
        
        carpeta_log = self.qs.value("JCCM_carreteras/LRS/carpeta_log")
        if carpeta_log is None:
            carpeta_log = self.conf.lrs["default_log_folder"]
            self.qs.setValue("JCCM_carreteras/LRS/carpeta_log", carpeta_log)
        
        bal_dest_path = self.qs.value("JCCM_carreteras/LRS/bal_dest_path")
        if bal_dest_path is None:
            bal_dest_path = self.conf.lrs["bal_dest_path"]
            self.qs.setValue("JCCM_carreteras/LRS/bal_dest_path", bal_dest_path)

        bal_nom_layer = self.qs.value("JCCM_carreteras/LRS/bal_nom_layer")
        if bal_nom_layer is None:
            bal_nom_layer = self.conf.lrs["bal_nom_layer"]
            self.qs.setValue("JCCM_carreteras/LRS/bal_nom_layer", bal_nom_layer)

        bal_estiloCAPA = self.qs.value("JCCM_carreteras/LRS/bal_estiloCAPA")
        if bal_estiloCAPA is None:
            bal_estiloCAPA = self.conf.lrs["bal_estiloCAPA"]
            self.qs.setValue("JCCM_carreteras/LRS/bal_estiloCAPA", bal_estiloCAPA)
            
        '''-------------------------------------'''
        '''             CATASTRO_TOOL           '''
        '''-------------------------------------'''
        url_catastro_distancia = self.qs.value("JCCM_carreteras/CATASTRO/url_catastro_distancia")
        if url_catastro_distancia is None:
            url_catastro_distancia = self.conf.catastro_tool["url_catastro_distancia"]
            self.qs.setValue("JCCM_carreteras/CATASTRO/url_catastro_distancia", url_catastro_distancia)
        
        url_catastro_rc = self.qs.value("JCCM_carreteras/CATASTRO/url_catastro_rc")
        if url_catastro_rc is None:
            url_catastro_rc = self.conf.catastro_tool["url_catastro_rc"]
            self.qs.setValue("JCCM_carreteras/CATASTRO/url_catastro_rc", url_catastro_rc)
        
        url_catastro_Provincia = self.qs.value("JCCM_carreteras/CATASTRO/url_catastro_Provincia")
        if url_catastro_Provincia is None:
            url_catastro_Provincia = self.conf.catastro_tool["url_catastro_Provincia"]
            self.qs.setValue("JCCM_carreteras/CATASTRO/url_catastro_Provincia", url_catastro_Provincia)
        
        url_catastro_municipio = self.qs.value("JCCM_carreteras/CATASTRO/url_catastro_municipio")
        if url_catastro_municipio is None:
            url_catastro_municipio = self.conf.catastro_tool["url_catastro_municipio"]
            self.qs.setValue("JCCM_carreteras/CATASTRO/url_catastro_municipio", url_catastro_municipio)

        url_catastro_RCCOOR = self.qs.value("JCCM_carreteras/CATASTRO/url_catastro_RCCOOR")
        if url_catastro_RCCOOR is None:
            url_catastro_RCCOOR = self.conf.catastro_tool["url_catastro_RCCOOR"]
            self.qs.setValue("JCCM_carreteras/CATASTRO/url_catastro_RCCOOR", url_catastro_RCCOOR)

        url_catastro_DNPRC = self.qs.value("JCCM_carreteras/CATASTRO/url_catastro_DNPRC")
        if url_catastro_DNPRC is None:
            url_catastro_DNPRC = self.conf.catastro_tool["url_catastro_DNPRC"]
            self.qs.setValue("JCCM_carreteras/CATASTRO/url_catastro_DNPRC", url_catastro_DNPRC)

        url_catastro_DNPPP = self.qs.value("JCCM_carreteras/CATASTRO/url_catastro_DNPPP")
        if url_catastro_DNPPP is None:
            url_catastro_DNPPP = self.conf.catastro_tool["url_catastro_DNPPP"]
            self.qs.setValue("JCCM_carreteras/CATASTRO/url_catastro_DNPPP", url_catastro_DNPPP)

        url_catastro_DescGML = self.qs.value("JCCM_carreteras/CATASTRO/url_catastro_DescGML")
        if url_catastro_DescGML is None:
            url_catastro_DescGML = self.conf.catastro_tool["url_catastro_DescGML"]
            self.qs.setValue("JCCM_carreteras/CATASTRO/url_catastro_DescGML", url_catastro_DescGML)

        cat_dir_shps = self.qs.value("JCCM_carreteras/CATASTRO/cat_dir_shps")
        if cat_dir_shps is None:
            cat_dir_shps = self.conf.catastro_tool["cat_dir_shps"]
            self.qs.setValue("JCCM_carreteras/CATASTRO/cat_dir_shps", cat_dir_shps)

        cat_year = self.qs.value("JCCM_carreteras/CATASTRO/cat_year")
        if cat_year is None:
            cat_year = self.conf.catastro_tool["cat_year"]
            self.qs.setValue("JCCM_carreteras/CATASTRO/cat_year", cat_year)

        dir_estilos_catastro = self.qs.value("JCCM_carreteras/CATASTRO/dir_estilos_catastro")
        if dir_estilos_catastro is None:
            dir_estilos_catastro = self.conf.catastro_tool["dir_estilos_catastro"]
            self.qs.setValue("JCCM_carreteras/CATASTRO/dir_estilos_catastro", dir_estilos_catastro)

        cat_pos_toc = self.qs.value("JCCM_carreteras/CATASTRO/cat_pos_toc")
        if cat_pos_toc is None:
            cat_pos_toc = self.conf.catastro_tool["cat_pos_toc"]
            self.qs.setValue("JCCM_carreteras/CATASTRO/cat_pos_toc", cat_pos_toc)
            
        ''' DATA_INTERNOS '''
        ###     UNIDADES    ###
        UD_SIGFOMSC = self.qs.value("JCCM_carreteras/DATOS_INT/UD_SIGFOMSC")
        if UD_SIGFOMSC is None:
            UD_SIGFOMSC = self.conf.data_internos["UD_SIGFOMSC"]
            self.qs.setValue("JCCM_carreteras/DATOS_INT/UD_SIGFOMSC", UD_SIGFOMSC)
        
        DIR_SIGFOMSC = self.qs.value("JCCM_carreteras/DATOS_INT/DIR_SIGFOMSC")
        if DIR_SIGFOMSC is None:
            DIR_SIGFOMSC = self.conf.data_internos["DIR_SIGFOMSC"]
            self.qs.setValue("JCCM_carreteras/DATOS_INT/DIR_SIGFOMSC", DIR_SIGFOMSC)

        UD_SIGFOMLO = self.qs.value("JCCM_carreteras/DATOS_INT/UD_SIGFOMLO")
        if UD_SIGFOMLO is None:
            UD_SIGFOMLO = self.conf.data_internos["UD_SIGFOMLO"]
            self.qs.setValue("JCCM_carreteras/DATOS_INT/UD_SIGFOMLO", UD_SIGFOMLO)

        DIR_SIGFOMLO = self.qs.value("JCCM_carreteras/DATOS_INT/DIR_SIGFOMLO")
        if DIR_SIGFOMLO is None:
            DIR_SIGFOMLO = self.conf.data_internos["DIR_SIGFOMLO"]
            self.qs.setValue("JCCM_carreteras/DATOS_INT/DIR_SIGFOMLO", DIR_SIGFOMLO)

        UD_SIGCTRLO = self.qs.value("JCCM_carreteras/DATOS_INT/UD_SIGCTRLO")
        if UD_SIGCTRLO is None:
            UD_SIGCTRLO = self.conf.data_internos["UD_SIGCTRLO"]
            self.qs.setValue("JCCM_carreteras/DATOS_INT/UD_SIGCTRLO", UD_SIGCTRLO)

        DIR_SIGCTRLO = self.qs.value("JCCM_carreteras/DATOS_INT/DIR_SIGCTRLO")
        if DIR_SIGCTRLO is None:
            DIR_SIGCTRLO = self.conf.data_internos["DIR_SIGCTRLO"]
            self.qs.setValue("JCCM_carreteras/DATOS_INT/DIR_SIGCTRLO", DIR_SIGCTRLO)

        UD_CARTOGSC = self.qs.value("JCCM_carreteras/DATOS_INT/UD_CARTOGSC")
        if UD_CARTOGSC is None:
            UD_CARTOGSC = self.conf.data_internos["UD_CARTOGSC"]
            self.qs.setValue("JCCM_carreteras/DATOS_INT/UD_CARTOGSC", UD_CARTOGSC)

        DIR_CARTOGSC = self.qs.value("JCCM_carreteras/DATOS_INT/DIR_CARTOGSC")
        if DIR_CARTOGSC is None:
            DIR_CARTOGSC = self.conf.data_internos["DIR_CARTOGSC"]
            self.qs.setValue("JCCM_carreteras/DATOS_INT/DIR_CARTOGSC", DIR_CARTOGSC)

        GDB_Geometrias = self.qs.value("JCCM_carreteras/DATOS_INT/GDB_Geometrias")
        if GDB_Geometrias is None:
            GDB_Geometrias = self.conf.data_internos["GDB_Geometrias"]
            self.qs.setValue("JCCM_carreteras/DATOS_INT/GDB_Geometrias", GDB_Geometrias)

        GDB_Aforos = self.qs.value("JCCM_carreteras/DATOS_INT/GDB_Aforos")
        if GDB_Aforos is None:
            GDB_Aforos = self.conf.data_internos["GDB_Aforos"]
            self.qs.setValue("JCCM_carreteras/DATOS_INT/GDB_Aforos", GDB_Aforos)

            
