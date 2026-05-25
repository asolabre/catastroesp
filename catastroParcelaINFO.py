# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name:            catastroParcelaINFO.py

                                 A QGIS plugin
Plugin:     catastroesp - Catastro de España
Purpose:    Carga el menú de información de parcela
        --------------------------------------------------------------------
        begin                : 2016-06-06
        git sha              : $Format:%H$
        Codigo Corregido     : Agustín Solabre
        email                : agusass@hotmail.com
 ***************************************************************************/ ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt5.QtWidgets import QApplication, QDialog

from PyQt5 import QtGui, QtCore, uic

import os


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), './menus/catastroParcelaINFO.ui'))


class catastroParcelaINFODialog(QDialog, FORM_CLASS):
    def __init__(self, iface,parent=None):
        """Constructor."""
        super(catastroParcelaINFODialog, self).__init__(parent)
        self.setupUi(self)
        
        self.iface = iface;
        

    def encode(self,text):
        """
        For printing unicode characters to the console.
        """
        return text.encode('utf-8')