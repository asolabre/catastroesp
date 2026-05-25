# -*- coding: utf-8 -*-
"""
/***************************************************************************
 gestorCapas_ini
                                 A QGIS plugin
 jcml_bar
                             -------------------
        copyright            : (C) 2017 A. Solabre 
        email                : gis.carreteras@jccm.es
        
 ***************************************************************************/


"""
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSettings, Qt, QFileInfo
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QApplication, QListWidgetItem
from PyQt5 import uic

from qgis.core import QgsProject, QgsLayerDefinition, QgsRectangle, QgsMessageLog, QgsCoordinateReferenceSystem,QgsApplication

import os
from osgeo import ogr, osr
import urllib
import json
import ast 

from time import sleep

from .settings import Settings           # CLASE DE CONFIGURACIÓN DE VARIABLES GLOBALES
from .config import configuration        # CLASE DE CONFIGURACIÓN DE VARIABLES DEL PROGRAMA
from .functions3 import Functions        # CLASE DE CONFIGURACIÓN DE FUNCIONES GENERALES

# Definicion de los marcadores regional y provinciales
listMarc = {
        'CASTILLA LA MANCHA - CLM': [25830, 192000, 4209000, 784500, 4576000],
        'ALBACETE - AB':            [25830, 505872, 4202584, 685531, 4370727],
        'CIUDAD REAL - CR':         [25830, 311168, 4241505, 542660, 4385049],
        'CUENCA - CU':              [25830, 436896, 4337604, 707436, 4505361],
        'GUADALAJARA - GU':         [25830, 428872, 4441654, 649725, 4578601],
        'TOLEDO - TO':              [25830, 289007, 4335563, 513324, 4474658]
        }
        

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), './menus/gestorCapas_ini.ui'))


class gestorCapas_ini(QDialog, FORM_CLASS):
    def __init__(self, iface,parent=None):
        """Constructor."""
        super(gestorCapas_ini, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface;

        self.nombre_plugin = os.path.basename(os.path.dirname(__file__))
        
        self.setWindowIcon(QIcon(f":/plugins/{self.nombre_plugin}/iconos/logo_general.jpg"))
        self.logo.setPixmap(QPixmap(f":/plugins/{self.nombre_plugin}/iconos/logo_general.jpg"))

        ##### Forzamos el SRC al de CLM #####
        QgsProject.instance().setCrs(QgsCoordinateReferenceSystem(25830))

        self.fun = Functions()
        self.qs = QSettings()

        self.current_configuration = configuration()

        if configuration.custom_configuration != "":
            #QgsMessageLog.logMessage( "Cargando configuracion personalizada",self.nombre_plugin)
            import imp
            try:

                custom_file = configuration.custom_configuration
                foo = imp.load_source('custom_config', custom_file)
                custom_config =  foo.custom_config()
                self.current_configuration = custom_config
            except:
                #QgsMessageLog.logMessage( "Archivo no encontrado, se carga configuracion por defecto..",self.nombre_plugin)
                pass

        # Se coloca la provincia por defecto
        provSelect = self.qs.value(f"{self.nombre_plugin}/GENERAL/01Ambito")
        if provSelect is None:
            provSelect = self.current_configuration.general["01Ambito"]
        listProv = [self.cbxPROVINCIA.itemText(i) for i in range(self.cbxPROVINCIA.count())]
        if provSelect in listProv:
            self.cbxPROVINCIA.setCurrentIndex(listProv.index(provSelect))

        ##########################################################################
        ###
        # FICHERO DE DATOS DE CAPAS
        fich_config = self.qs.value(f"{self.nombre_plugin}/GENERAL/JCCM_fich_config")
        if fich_config is None:
            fich_config = ''

        # Buscamos el fich_config en unidadpropia, Z: U:
        if not os.path.exists(fich_config) or fich_config == os.path.join(os.path.dirname(__file__), './capasQSIG.txt'):
            uniProj = QgsProject.instance().fileName()[:2]
            listUnd = [uniProj, 'z:', 'u:']
            fich_config = u'z:/cartografia/datos_Q/QSIG/config/capasQSIG.txt'
            if self.fun.buscaFichUnd(listUnd, fich_config) is not None:
                fich_config = self.fun.buscaFichUnd(listUnd, fich_config)[0]
                self.qs.setValue(f"{self.nombre_plugin}/GENERAL/JCCM_fich_config", fich_config)
        
        # Buscamos el fich_config en la instalación del plugin
        if not os.path.exists(fich_config): 
            fich_config = os.path.join(os.path.dirname(__file__), './capasQSIG.txt')

        print ('fich_config: ', fich_config)

        linesFich = []
        with open(fich_config) as file:
            for line in file: 
                line = line.strip()
                try:
                    res = ast.literal_eval(line)  # Metodo convert a dict ast
                    # if 'nombre' in res:
                    listKeys =  ['type','source','nombre','estilo','grupo','agrupado']
                    flag = 1
                    for key in listKeys:
                        if key not in res:
                            flag = 0
                    if flag == 1: linesFich.append(res)
                    else: print ('LINEA NULA: '+line)
                except:
                    print ('LINEA NULA: '+line)

        ###
        ##########################################################################



        capas_inicio = self.getNombresPosiblesGrupo("Inicio", linesFich)
        
        self.createListCheckbox(capas_inicio, self.lwiCheckBoxes)
        
        # self.cargarSelectedButton.clicked.connect(self.cargarSelected)
        self.cargarSelectedButton.clicked.connect(lambda: self.cargarSelected(linesFich))

        self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.cancel)

        
    def createListCheckbox(self, capas_inicio, listChk):
        for nombreCapa in capas_inicio:

            item = QListWidgetItem(nombreCapa)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            listChk.addItem(item)
            
    ''' 
    def getNombresPosiblesGrupo(self,grupo):
        capas = []
        for capa in self.current_configuration.capas_inicio:
            if capa["grupo"] == grupo:
                capas.append(capa["nombre"])
        return capas
    '''
    def getNombresPosiblesGrupo(self, grupo, linesFich):
        capas = []
        for capa in linesFich:
            if capa["grupo"] == grupo:
                capas.append(capa["nombre"])
        return capas


    def getCapaByNombre(self,nombre, linesFich):
        for capa in linesFich:
            if capa["nombre"] == nombre:
                return capa
        return None


    def cargarSelected(self, linesFich):
        self.close()

        # Borrado de TODAS LAS CAPAS y GRUPOS de la TOC
        if self.ckB_EliminarTodo.isChecked():
            message = u'Se van a borrar todas las capas de la Tabla de Contenido'
            resp = self.fun.showMessageYESNO( message,'','BORRADO DE CAPAS' )
            if resp == 4194304: # Se ha pulsado cancelar
                QApplication.restoreOverrideCursor()
                return
                pass

            # ICONO DE ESPERA
            QApplication.setOverrideCursor(Qt.WaitCursor)
                
            # Borrado de TODAS LAS CAPAS
            QgsProject.instance().removeAllMapLayers()
           
            # Borrado de TODOS LOS GRUPOS
            root = QgsProject.instance().layerTreeRoot()
            for node in root.children():
                # print "- "+node.name() +" ("+str(type(node))+")"
                root.removeChildNode (node)

     
        # CARGA DE LAS CAPAS
        for index in range(0,self.lwiCheckBoxes.count()):
            item = self.lwiCheckBoxes.item(index)
            if item.checkState() == Qt.Checked:
                nomCAPA = item
            else:
                continue
            nomCAPA =self.getCapaByNombre(item.text(), linesFich)

            if (nomCAPA["type"] == "Grupo"):
                # layerEXIST = QgsProject.instance().mapLayersByName(item.text())
                # if not layerEXIST:
                    # capa = self.getCapaByNombre(item.text(), linesFich)
                    # self.cargarCapa(capa)
                    
                # Comprobamos si los grupos de capas ya existen
                root = QgsProject.instance().layerTreeRoot()            
                grupoEXIST = root.findGroup(item.text())

                # print ('GRUPO - ',nomCAPA["nombre"],nomCAPA)
                if grupoEXIST is None:
                    root = QgsProject.instance().layerTreeRoot()
                    result=QgsLayerDefinition().loadLayerDefinition(nomCAPA["source"], QgsProject.instance(), root)
                    if result[0]==False:
                        QgsMessageLog.logMessage( "Fallo al cargar la capa: " + nomCAPA["nombre"],self.nombre_plugin)
                        
                        # Buscamos el fichero dentro de la carpeta del pluggin
                        fileGrupo = f"python/plugins/{self.nombre_plugin}/GRUPOS_CAPAS/"+QFileInfo(nomCAPA["source"]).fileName()
                        dirPYTJCCM = QgsApplication.qgisSettingsDirPath()
                        fichPYTGrupo = os.path.normpath(os.path.join(os.path.dirname(dirPYTJCCM), fileGrupo))
                        result1=QgsLayerDefinition().loadLayerDefinition(fichPYTGrupo, QgsProject.instance(), root)
                                 
        QApplication.restoreOverrideCursor()

        # ZOOM A CASTILLA - LA MANCHA O PROV SELECCIONADA
        if self.ckB_zoomClm.isChecked:
            provSelect = self.qs.value(f"{self.nombre_plugin}/GENERAL/01Ambito")
            if provSelect is None:
                provSelect = self.current_configuration.general["01Ambito"]
                
            provSelect = self.cbxPROVINCIA.currentText()
            self.qs.setValue(f"{self.nombre_plugin}/GENERAL/01Ambito", provSelect)
            
            if provSelect in listMarc:
                marc = listMarc[provSelect]
            else:
                marc = [25830, 192000, 4209000, 784500, 4576000]
            
            rectangle = QgsRectangle(marc[1],marc[2],marc[3],marc[4])
            self.iface.mapCanvas().zoomToFeatureExtent(rectangle)    
            self.iface.mapCanvas().refresh()

        else:
            print (u'SI NO QUIERES HACER ZOOM NO HAY ZOOM')
            pass
        pass
                
                
    def crearGruposcapas(self, data):
    # Crear Grupos y subgrupos de capas
    # https://gis.stackexchange.com/questions/108316/how-to-move-a-layer-in-qgis-toc-above-an-existing-group
        s=data["agrupado"]
        listGrupos = s.split("/")
        
        root = QgsProject.instance().layerTreeRoot()
        grupoPadre = root
        nivgrupo = 0
        for grupoCapas in listGrupos:
            encuentraGroup = root.findGroup(grupoCapas)
            if not encuentraGroup:
                grupoPadre = grupoPadre.insertGroup(0, grupoCapas)
            else:
                grupoPadre = encuentraGroup
            nivgrupo += 1               
            
        # print 'Capa:',data["nombre"], listGrupos
        # print  grupoCapas
        return grupoCapas
        
    
    def cancel(self):
        # capas_inicio = self.getNombresPosiblesGrupo("Inicio")
        # self.list_inicio.clear()
        # for capa_inicio in capas_inicio:
            # self.list_inicio.addItem(capa_inicio)
            
        self.reject()