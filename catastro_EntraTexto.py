# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name:            catastro_EntraTexto.

                                 A QGIS plugin
Plugin:     catastroesp - Catastro de España
Purpose:    Carga de texto para interpretar Referencias catastrales
        --------------------------------------------------------------------
        begin                : 2023-12-04
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
"""

from PyQt5.QtWidgets import QDialog, QPushButton, QDialogButtonBox, QFileDialog, QApplication
from PyQt5.QtCore import QSettings, Qt
from PyQt5 import uic

import os
import glob
import re


from .config import configuration        # CLASE DE CONFIGURACIÓN DE VARIABLES DEL PROGRAMA

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), './menus/catastro_EntradaTXT.ui'))

class catastro_EntraTexto(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(catastro_EntraTexto, self).__init__(parent)
        self.setupUi(self)
        
        self.current_configuration = configuration()

        self.btnCONVERTIR.clicked.connect(self.btnCONVERTIRclick)
        self.btnCARGAR.clicked.connect(self.btnCARGARclick)
        self.listRRCC = []

        self.cambiaWIDGETSfmto()
        self.rbtNOTIFICATAS.toggled.connect(self.cambiaWIDGETSfmto)
        self.rbtSEPARADORES.toggled.connect(self.cambiaWIDGETSfmto)


    def cambiaWIDGETSfmto(self):
        if self.rbtNOTIFICATAS.isChecked():
            self.gbxSEPARADORES.setEnabled(False)
        else:
            self.gbxSEPARADORES.setEnabled(True)
            
        return    


    def getInputs(self):
        return (self.listRRCC)


    def btnCONVERTIRclick(self):
        text = self.txeREFSCATASTRAL.toPlainText()
        NoParc = 0

        # Limpiamos la lista de self.listaRCs
        self.listaRCs.clear()
            
        if self.rbtSEPARADORES.isChecked():
            # FORMATO LINEA DE TEXTO CON SEPARADORES
           
            # Analizamos cuales son los separadores a usar
            separCHAR= '['
            if self.chbSepCOMA.isChecked():
                separCHAR += ','
            if self.chbSepPUNTOCOMA.isChecked():
                separCHAR += ';'
            if self.chbSepDOSPUNTOS.isChecked():
                separCHAR += ':'
            if self.chbSepSEPARADOR.isChecked():
                separCHAR += '/'
            # if self.chbSepSEPARADORTRAS.isChecked():
                # separCHAR += '\\'
            if self.chbSepSEPARADOR.isChecked():
                separCHAR += 'y'
            separCHAR += ']'
            
            # Se divide la lista con los separadores
            # listRRCC = text.split(",")
            # listRRCC = re.split("[;,:/\]", text)
            if separCHAR != '[]':
                listRRCC = re.split(separCHAR, text)
                for RC in listRRCC:
                    val = RC.strip()
                    val = val.replace(" ","")
                    val = val[0:14]
                    if len(val)<14:
                        val = val +' RC NO VÁLIDA'
                    else:
                        NoParc += 1
                    self.listaRCs.addItem(val)
            else:
                return
        else:
            # FORMATO TIPO NOTIFICACIÓN CATASTRAL
            listRRCCbruta = text.splitlines()
            listRRCC = []
            for RC in listRRCCbruta:
                val = RC[0:23]
                val = val.replace(" ","")
                val = val[0:14]
                if len(val)<14:
                    val = val +' RC NO VÁLIDA'
                else:
                    NoParc += 1
                self.listaRCs.addItem(val)
                pass

        self.lbNoPARCELAS.setText(str(NoParc) + " Parcelas Convertidas")
                

    def btnCARGARclick(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        for x in range(self.listaRCs.count()):
            RC = str(self.listaRCs.item(x).text())
            if not ' NO ' in RC:
                self.listRRCC.append(RC)

        self.accept()

        
    def cancel(self):
        self.reject()
        
'''
FORMATO TIPO NOTIFICACIÓN CATASTRAL

02055A0 1700038 0000 MA Polígono 017 Parcela 00038 Paraje MAJADA DE LAS VACAS - NERPIO ( ALBACETE )
02055A0 1700043 0000 MY Polígono 017 Parcela 00043 Paraje SALTADOR - NERPIO ( ALBACETE )
02055A0 1700065 0000 MS Polígono 017 Parcela 00065 Paraje CAÑADA DE BOGARRA - NERPIO ( ALBACETE )
02055A0 1800002 0000 MD Polígono 018 Parcela 00002 Paraje UMBRIA ARROYO BLANCO - NERPIO ( ALBACETE )
02055A0 1800265 0000 MS Polígono 018 Parcela 00265 Paraje MOLATA DE LA CASILLA - NERPIO ( ALBACETE )
02055A0 1800345 0000 MT Polígono 018 Parcela 00345 Paraje SOLANA DEL MACALON - NERPIO ( ALBACETE )
02055A0 1800469 0000 MP Polígono 018 Parcela 00469 Paraje UMBRIA ARROYO BLANCO - NERPIO ( ALBACETE )
02055A0 1809007 0000 MA Polígono 018 Parcela 09007 Paraje CTRA DE BOJADILLAS - NERPIO ( ALBACETE )
02055A0 1809015 0000 MP Polígono 018 Parcela 09015 Paraje CARRETERA CM-3229 - NERPIO ( ALBACETE )
02055A0 1909004 0000 MX Polígono 019 Parcela 09004 Paraje CTRA DE BOJADILLAS - NERPIO ( ALBACETE )



FORMATO LINEA DE TEXTO CON SEPARADORES

02056A0  0900526xxxx, 02056A00900 604aaaa, 020 56A00900267, 02056A009002 69, 02056A009006 25, 02056A00 90026, 02056A00909002, 02056A00909031

02056A0  0900526xxxx, 02056A00900 604aaaa, 020 56A00900267; 02056A009002 69: 02056A009006 25, 02056A00 90026, 02056A00909002, 02056A00909031

'''


