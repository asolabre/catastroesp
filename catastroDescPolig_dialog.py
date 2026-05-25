# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name:           catastroDescPolig_dialog.py

                                 A QGIS plugin
                                 
Plugin:     catastroesp - Catastro de España
Purpose:    Descarga parcelas catastrales por coincidencia con un Polígono
        --------------------------------------------------------------------
        begin                : 2021-12-31
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
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import (Qt, pyqtSignal)
from PyQt5.QtWidgets import QDialog
from PyQt5 import uic

import os

from .config import configuration        # CLASE DE CONFIGURACIÓN DE VARIABLES DEL PROGRAMA

QT_VERSION=5
os.environ['QT_API'] = 'pyqt5'

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), './menus/catastroDescargas.ui'))


class catastroDescPolig_dialog(QDialog, FORM_CLASS):
    Signal_OneParameter = pyqtSignal(str)

    def __init__(self, iface, datosMuni, listDescargas, parent=None):
        super(catastroDescPolig_dialog, self).__init__(parent)
        self.setupUi(self)
        
        self.iface = iface
        self.conf = configuration()
        
        self.nombre_plugin = os.path.basename(os.path.dirname(__file__))

        nombre_muni = datosMuni[0]
        codigo = datosMuni[1]
        textMuni = u"Se van a cargar desde la Sede Electrónica de Catastro \n las capas del catastro actual \n del T. M.  {} - ({})\n\n -- LA OPERACIÓN TARDARÁ UNOS MINUTOS --".format(nombre_muni, codigo)
        self.lblAvisoCarga.setText(textMuni)

        self.setWindowIcon(QIcon(f':/plugins/{self.nombre_plugin}/iconos/logo_general.jpg'))
        
        self.resultDialog = []

        self.btnACEPTAR.clicked.connect(lambda: self.emit_signal('ACEPTAR'))
        self.btnCANCELAR.clicked.connect(lambda: self.emit_signal('CANCELAR'))


    def botonACEPTAR(self):
        pass

            
    def cancel(self):
        dialog=catastroDescPolig_dialog(parent)
        result=dialog.exec_()
        listaRes=['CANCEL']
        self.close()

        return (listaRes,result==QDialog.Cancelled)


    def emit_signal(self, btn):
        if btn == 'ACEPTAR':
            if self.ckb_CargaParc.isChecked():
                self.resultDialog.append('CP')
            if self.ckb_CargaEdif.isChecked():
                self.resultDialog.append('BU')
            if self.ckb_CargaDirec.isChecked():
                self.resultDialog.append('AD')

        elif btn == 'CANCELAR':
            self.resultDialog = ['CANCELAR']
        self.close()
