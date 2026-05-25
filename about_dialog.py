# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name:           about_dialog.py

                                 A QGIS plugin
                                 
Plugin:     catastroesp - Catastro de España
Purpose:    Herramienta de información sobre el plugin
        --------------------------------------------------------------------
        begin                : 2014-11-21
        git sha              : $Format:%H$
        Codigo Corregido     : Agustín Solabre
        email                : agusass@hotmail.es
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
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from PyQt5.QtCore import Qt, QUrl, QFileInfo
from PyQt5 import uic

from qgis.core import *
from qgis.gui import *

import configparser
import os
from time import gmtime, localtime, strftime


CURR_PATH = os.path.dirname(__file__)
FORM_CLASS, _ = uic.loadUiType(os.path.join(CURR_PATH, './menus/about_dialog_base.ui'))

# Comprobamos si existen los ficheros de ayuda
Proj = QgsProject.instance().fileName()
unidadSIG = Proj[:2]
unidadSIG1= u'U:'
unidadSIG2= u'Z:'

if not os.path.exists(unidadSIG+'/cartografia/datos_Q/AYUDA/'):
    print ('No existe unidad - '+ 'file:///'+ unidadSIG+'/cartografia/datos_Q/AYUDA/')
    unidadSIG = unidadSIG1
    if not os.path.exists(unidadSIG+'/cartografia/datos_Q/AYUDA/'):
        print ('No existe unidad - '+ 'file:///'+ unidadSIG+'/cartografia/datos_Q/AYUDA/')
        unidadSIG = unidadSIG2

# VARIABLES DEL FICHERO DE METADATOS
cfg = configparser.ConfigParser()

versionQGS = Qgis.QGIS_VERSION
fileMetadata = os.path.join(os.path.dirname(__file__), 'metadata.txt')
cfg.read(fileMetadata)
fecha = strftime("%d %b %Y %H:%M ", localtime(os.path.getmtime(fileMetadata)))
version = cfg.get('general', 'version')
author= cfg.get('general', 'author')
email= cfg.get('general', 'email')
telefono= cfg.get('general', 'telephone')
organizacion= cfg.get('general', 'organizacion')
about=  cfg.get('general', 'about')
changelog =  cfg.get('general', 'changelog')

# VARIABLES DE FICHEROS DE AYUDA
ayudaCOMPLE='---PENDIENTE---'
ayudaSIG='file:///'+unidadSIG+'/cartografia/datos_Q/AYUDA/SIG%20REG%20CTRAS%20AYUDA.pdf'
ayudaINST='file:///'+unidadSIG+'/cartografia/datos_Q/INSTALACION%20SIG_CLM_QGIS/INSTALACION_SIG_CLM_QGIS%20V105.doc'
ayudaASISTW7='file:///'+unidadSIG+'/cartografia/datos_Q/AYUDA/Asistencia%20remota%20solicitada%20por%20usuario%20final%20en%20Windows%207.pdf'
ayudaASISTWXP='file:///'+unidadSIG+'/cartografia/datos_Q/AYUDA/Asistencia%20remota%20solicitada%20por%20usuario%20final%20en%20Windows%20XP.pdf'
dirREPO='---PENDIENTE---'

ficheroAyuda = 'index.html'

# print 'ayudaCOMPLE --- ', ayudaCOMPLE
# print 'ayudaSIG ------ ', ayudaSIG
# print 'ayudaINST ----- ', ayudaINST
# print 'ayudaASISTW7 -- ', ayudaASISTW7
# print 'ayudaASISTWXP - ', ayudaASISTWXP
# print 'dirREPO ------- ', dirREPO

class AboutDialog(QDialog, FORM_CLASS):
    def __init__(self, iface,parent=None):
        """Constructor."""
        super(AboutDialog, self).__init__(parent)
        self.setupUi(self)

        self.nombre_plugin = os.path.basename(os.path.dirname(__file__))
        
        self.iconoMENU='iconos/catastroesp.jpg'
        self.setWindowIcon(QIcon(f':/plugins/{self.nombre_plugin}/catastroesp.jpg'))
        self.lblLogo.setPixmap(QPixmap(os.path.join(CURR_PATH, self.iconoMENU)))
        self.lblLogo.setFixedSize(60, 60) 
        
        self.pluginDir = os.path.dirname(__file__)

        self.tabWidget.setCurrentIndex(9) ### esto va al tab INFO
        self.btnHelp = self.buttonBox.button(QDialogButtonBox.Help)

        txtVersion  = u'QGIS '+versionQGS + '\n'
        txtVersion += self.tr('Version Plugin: %s Fecha: %s') % (version, fecha)
        
        self.lblVersion.setText(txtVersion)

        self.qtbInfo.setHtml(self.get_about_text())
        self.qtbAyuda.setOpenExternalLinks(True)
        self.qtbAyuda.setSource(QUrl(self.getHelpUrl()))
        self.tbhistorial.setPlainText(changelog)

    def getHelpUrl(self):
        helpFile = u'file:///{}/help/{}'.format(
            self.pluginDir, ficheroAyuda)
        return helpFile

    def get_about_text(self):
        return self.tr(
            '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;"><br /></p>'
            '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt; font-weight:600;">Autor: </span><span style=" font-size:8pt;"> '+author+'</span></p>'
            '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;"><br /></p>'
            '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt; font-weight:600;">CONTACTO:  email: </span><span style=" font-size:8pt;"> </span><a href="mailto:'+email+'"><span style=" font-size:8pt; text-decoration: underline; color:#0000ff;">'+email+'</span></a><span style=" font-size:8pt; font-weight:600;">         Telefono:</span><span style=" font-size:8pt;">  '+telefono+'</span></p>'
            '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;"><br /></p>'
			'<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;"><br /></p>'
            '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt; font-weight:600;">Dir plugin: </span><span style=" font-size:8pt;"> '+self.pluginDir+'</span></p>'
            )

    def get_ayuda_text(self):
        text =self.tr(
            '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><a href="'+ayudaCOMPLE+'"><span style=" font-size:10pt; text-decoration: underline; color:#0000ff;">AYUDA</span></a><span style=" font-size:10pt;"> sobre las FUNCIONALIDADES DE CARRETERAS</span></p>'
            '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><a href="'+ayudaSIG+'"><span style=" font-size:10pt; text-decoration: underline; color:#0000ff;">AYUDA</span></a><span style=" font-size:10pt;"> sobre el SIG DE CARRETERAS</span></p>'
            '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><a href="'+ayudaINST+'"><span style=" font-size:10pt; text-decoration: underline; color:#0000ff;">AYUDA</span></a><span style=" font-size:10pt;"> instalacion SIG DE CARRETERAS</span></p>'
            '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:10pt;"><br /></p>'
            '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><a href="'+ayudaASISTW7+'"><span style=" font-size:10pt; text-decoration: underline; color:#0000ff;">Solicitud</span></a><span style=" font-size:10pt;"> Asistencia Remota Windows 7</span></p>'
            '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><a href="'+ayudaASISTWXP+'"><span style=" font-size:10pt; text-decoration: underline; color:#0000ff;">Solicitud</span></a><span style=" font-size:10pt;"> Asistencia Remota Windows XP</span></p>'
            '<p><strong>Acceso al repositorio:</strong> <a href="'+dirREPO+'">REPOSITORIO</a></p>'
            )
        return text

    def get_historial(self):
        with open(os.path.join(CURR_PATH, 'historial.txt')) as f:
            return f.read()