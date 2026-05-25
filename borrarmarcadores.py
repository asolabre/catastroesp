# -*- coding: utf-8 -*-
"""
/***************************************************************************
 jccm_borrarmarcadores
                                 A QGIS plugin
 Collection of internet map services
                             -------------------
        begin                : 2014-11-21

        git sha              : $Format:%H$
        copyright            : (C) 2017 A.Solabre. JCCM. D.G.Carreteras
        email                : asolabre@jccm.es
 ***************************************************************************/
"""
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
from qgis.core import Qgis, QgsProject, QgsLayerTreeGroup

from qgis.gui import QgsVertexMarker

import os

from .functions3 import Functions        # CLASE DE CONFIGURACIÓN DE FUNCIONES GENERALES

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), './menus/borrarmarcadores.ui'))

class borrarmarcadores(QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        """Constructor."""
        super(borrarmarcadores, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface
        self.fun = Functions()

        self.setWindowIcon(QIcon(':/plugins/catastroesp/cat_borrarcapas.jpg'))

        self.chbBORRAMARCAS.setChecked(True)
        self.chbBORRAPARCAT.setChecked(False)
        self.chbBORRATMCAT.setChecked(False)
        self.chbCAPASCATALOGO.setChecked(False)
        self.btnBORRAR.clicked.connect(self.borrado_click)
        self.btnCANCELA.clicked.connect(self.cancela)

        self.chbCAPASCATALOGO.hide()
        
        self.versionQGS = Qgis.QGIS_VERSION

    def borrado_click(self):
        if self.chbBORRAMARCAS.isChecked():             # Borrado de las marcas de las búsquedas
            nombreCAPA = 'TRAMOS_BUSCADOS'
            # Borrado de las capas de 'TRAMOS_BUSCADOS'
            for layer in QgsProject.instance().mapLayers().values():
                if layer.name() == nombreCAPA:
                    QgsProject.instance().removeMapLayers([layer.id()])

            if float(self.versionQGS[:4]) >= 3.16:
                print (self.versionQGS)

                vertex_items = [ i for i in self.iface.mapCanvas().scene().items() if issubclass(type(i), QgsVertexMarker)]
                for ver in vertex_items:
                    if ver in self.iface.mapCanvas().scene().items():
                        self.iface.mapCanvas().scene().removeItem(ver)
            else:
                text = u'La versión '+self.versionQGS+u' no admite el borrado de puntos\n'
                text+= u'Se puede ya cambiar a QGIS 3.16 o superior'
                self.fun.showMessage(text)
       
        if self.chbBORRAPARCAT.isChecked():             # Borrado de los grupos de PARCELAS CATASTRALES
            nombreCAPA = 'PARCELAS CATASTRALES'

            # Borrado de los grupos de PARCELAS CATASTRALES
            root = QgsProject.instance().layerTreeRoot()
            grupoBUSCAT = root.findGroup(nombreCAPA)
            if not grupoBUSCAT is None:
                root.removeChildNode(grupoBUSCAT)
            
            # Borrado de las capas de PARCELAS CATASTRALES
            for layer in QgsProject.instance().mapLayers().values():
                if layer.name() == nombreCAPA:
                    QgsProject.instance().removeMapLayers([layer.id()])
            

        if self.chbBORRATMCAT.isChecked():              # Borrado de capas de catastro correspondienes a Terminos Municipales
            nomCATtm = 'CAT -'

            # Borrado de los Grupos de TERMINOS CATASTRALES
            root = QgsProject.instance().layerTreeRoot()
            for grupo in root.children():
                if isinstance(grupo, QgsLayerTreeGroup):
                    nom = grupo.name()
                    if nom[:5] == nomCATtm:
                        root.removeChildNode(grupo)

            # Borrado de las capas de TERMINOS CATASTRALES
            root = QgsProject.instance().layerTreeRoot()
            for layer in QgsProject.instance().mapLayers().values():
                if layer.name()[0:4] == nomCATtm:
                    QgsProject.instance().removeMapLayers([layer.id()])

        if self.chbBORRATEMP.isChecked():               # Borrado de capas temporales.
            root = QgsProject.instance().layerTreeRoot()
            for layer in QgsProject.instance().mapLayers().values():
                if layer.dataProvider().name() == 'memory':
                    QgsProject.instance().removeMapLayers([layer.id()])            
            
        
        if self.chbBORRAcartociudad.isChecked():        # Borrado de capas cargadas con Cartociudad.
            prefixCARTOC = 'DIRECCIONES_CARTOCIUDAD'
            root = QgsProject.instance().layerTreeRoot()
            for layer in QgsProject.instance().mapLayers().values():
                if prefixCARTOC in layer.name():  # Verifica si 'prefixCARTOC' está en 'layer.name()'
                    QgsProject.instance().removeMapLayers([layer.id()])            
        
        
        if self.chbCAPASCATALOGO.isChecked():
            bcap = True
        self.close()

        self.iface.mapCanvas().refresh()            


    def cancela(self):
        self.close()
        pass