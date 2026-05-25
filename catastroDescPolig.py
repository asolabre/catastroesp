 # -*- coding: utf-8 -*-
"""
/***************************************************************************
Name:           catastroDescPolig.py
Purpose:        Descarga de parcelas de un polígono previamente cargado en una capa

        --------------------------------------------------------------------
        begin                : 2021-11-09
        git sha              : $Format:%H$
        Codigo Corregido     : Agustín Solabre
        email                : agusass@hotmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License",         or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt5.QtWidgets import QDialog, QFileDialog, QListWidgetItem, QInputDialog, QLineEdit
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtCore import QSettings, Qt, QVariant
from PyQt5 import uic
from qgis.core import Qgis, QgsProcessingFeatureSourceDefinition, QgsVectorLayer, QgsField, QgsProject, \
                    QgsFeature, QgsLayerTreeLayer, QgsMapLayer, QgsWkbTypes, QgsFeatureRequest, QgsExpression, \
                    QgsGeometry, QgsVectorFileWriter, QgsProcessing, QgsProcessingMultiStepFeedback

from qgis import processing

from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QApplication

import sys
import os
import timeit
import datetime

from .config import configuration        # CLASE DE CONFIGURACIÓN DE VARIABLES DEL PROGRAMA
from .functions3 import Functions        # CLASE DE CONFIGURACIÓN DE FUNCIONES GENERALES
from .settings import Settings           # CLASE DE CONFIGURACIÓN DE VARIABLES GLOBALES
current_configuration = configuration()

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), './menus/catastroDescPolig.ui'))

# VARIABLES
srcVal = current_configuration.general["EPSG"]

# CLASES PROGRAMADAS
class catastro_DescargaPOL(QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        """Constructor."""
        super(catastro_DescargaPOL, self).__init__(parent)

        self.setupUi(self)
        self.iface = iface;
        self.fun = Functions()

        self.nombre_plugin = os.path.basename(os.path.dirname(__file__))

        self.setVar = QSettings()
        self.conf = configuration()

        try:
            lista_CAPAS = self.getCAPAS()
            capasPol = self.compruebaSELECT
            print (capasPol)
            if capasPol == ['ERROR']:
                self.close()
                return
            self.cbxCapaentrada.currentIndexChanged.connect(self.compruebaSELECT) # Comprueba si hay elementos seleccionados
            self.cbxCapaentrada.clear()
            self.cbxCapaentrada.addItems(lista_CAPAS)
            lastCapaentradaExpro = self.setVar.value(f"{self.nombre_plugin}/last/lastCapaentradaExpro")

            # Comprobamos si la capa activa está en lista_CAPAS y se pone como current en el combo
            self.cbxCapaentrada.setCurrentIndex(1)
            if iface.activeLayer():
                if iface.activeLayer().name() in lista_CAPAS:
                    self.cbxCapaentrada.setCurrentText(iface.activeLayer().name())
            self.cbxCapaentrada.setEditable(True)
                
            self.lastDirGPKG = self.setVar.value(f"{self.nombre_plugin}/last/lastDirGPKG")
            if self.lastDirGPKG is None:
                self.lastDirGPKG = 'C:/temp/catastroDescPol.gpkg'
            self.srcExtORI = '.gpkg'
            self.lneGPKGsalida.setText(self.lastDirGPKG)
            
            self.rbtCargadosTTMM.toggled.connect(self.cambiaWidgetsTTMM)

            self.setWindowIcon(QIcon(f':/plugins/{self.nombre_plugin}/iconos/cat_poligon.jpg'))
            # self.chbELEMSELEC.setEnabled(True)
            self.chbCARGAGPKG.setEnabled(True)

            self.chbCargaTTMM.setEnabled(True)
            self.chbCargaTTMM.setChecked(False)
            
            nomCapaParcelas = 'PARCELAS CATASTRALES'
            self.lneGPKGtable.setText(nomCapaParcelas)

            self.btnSeleccionfich.setEnabled(False) # Desactivados hasta nueva orden
            self.lneGPKGsalida.setEnabled(False)
            self.lblGPKGsalida.setEnabled(False)

            self.chbCALCInt.hide()              # Desactivados hasta nueva orden
            self.chbCALCInt.setEnabled(True)
            self.chbCALCInt.setChecked(False)
            
            self.chbDESCUENTOS.hide()           # Desactivados hasta nueva orden
            self.chbDESCUENTOS.setEnabled(False)
            self.chbDESCUENTOS.setChecked(False)
            
            self.btnGENERA.clicked.connect(self.generaCapaParcelas)
            self.btnCANCELA.clicked.connect(self.cancela)
            self.progressBar.setMinimum(0)
            self.progressBar.setMaximum(100)
            self.btnSeleccionfich.clicked.connect(self.gpkg_salida_file_click)
            self.lblINFO.show() == True
        except Exception as e:
            print(f"Error: {e}")
            self.close()  # Cierra la ventana si ocurre cualquier otro error
            return  # Sale del método __init__ para evitar que el formulario se abra

    def getCAPAS(self):
        capas = []
        for layer in QgsProject.instance().mapLayers().values():
            if layer.type() == QgsMapLayer.VectorLayer:
                if layer.wkbType() == QgsWkbTypes.Polygon:
                    feat=layer.featureCount()
                    featsel=layer.selectedFeatureCount()
                    capas.append(layer.name())
                if layer.wkbType() == QgsWkbTypes.MultiPolygon:
                    feat=layer.featureCount()
                    featsel=layer.selectedFeatureCount()
                    capas.append(layer.name())
        return capas


    def compruebaSELECT(self):
        self.chbELEMSELEC.setEnabled(False)
        self.chbELEMSELEC.setChecked(False)
        capaPolig = self.cbxCapaentrada.currentText()
        layersExpro = QgsProject.instance().mapLayersByName(capaPolig)
        try:
            sf = layersExpro[0].selectedFeatures() #returns QgsFeature object
            if len(sf) == 0:
                self.chbELEMSELEC.setEnabled(False)
                self.chbELEMSELEC.setChecked(False)
            else:
                self.chbELEMSELEC.setEnabled(True)
                self.chbELEMSELEC.setChecked(True)
        except:
            text = 'PARECE QUE NO HAY CAPAS DE POLÍGONO VÁLIDAS'
            self.fun.showMessageERR(text)
            return ['ERROR']
                
        

    def cambiaWidgetsTTMM(self):
        if self.rbtCargadosTTMM.isChecked():
            # DETECTAMOS LOS TTMM CARGADOS
            capasCat = []
            for layer in QgsProject.instance().mapLayers().values():
                if layer.type() == QgsMapLayer.VectorLayer:
                    if layer.name()[:8] == 'CAT- PAR':
                        capasCat.append(layer.name())
                        self.lwgLISTA_TM.addItem(layer.name())
            if len(capasCat) == 0:
                message = u'NO EXISTEN CAPAS DE PARCELAS CATASTRALES\n\n  - SE DEBEN CARGAR - '
                self.fun.showMessage( message,'','FALTA CATASTRO' )
                self.btnGENERA.setEnabled(False)
            return
        else:
            self.btnGENERA.setEnabled(True)
            return
        return


    def cancela(self):
        self.close()
        pass


    def gpkg_salida_file_click(self):
        gpkg_salida_file= self.lneGPKGsalida.text()
        ext = "*.gpkg"
        filename, tipofile = QFileDialog.getSaveFileName(self, "Fichero GPKG de salida", gpkg_salida_file, ext)
        print (filename, tipofile)
        if filename != None and filename != "":
            self.lneGPKGsalida.setText(filename)
        else:
            filename = gpkg_salida_file
        # Comprobamos que existe el directorio y si no, se crea
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))


    def generaCapaParcelas(self):
        start = timeit.default_timer()
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # VARIABLES
        srs =  self.iface.mapCanvas().mapSettings().destinationCrs().authid()
        capaPolig = self.cbxCapaentrada.currentText()

        layerResultFile= self.lneGPKGsalida.text().replace(" ", "_")
        layerResultName = self.lneGPKGtable.text()

        # Controlamos si la capa de entrada existe
        layerEXIST = QgsProject.instance().mapLayersByName(capaPolig)
        if not layerEXIST:
            message = u"PARECE QUE NO EXISTE LA CAPA\n"+capaPolig
            self.fun.showMessage( message,'','Error de capa' )
            QApplication.restoreOverrideCursor()
            return
            
        # Comprobamos si existe la capa de parcelas
        layerEXIST = QgsProject.instance().mapLayersByName(self.lneGPKGtable.text())
        if not layerEXIST or layerEXIST[0].featureCount() == 0:
            # CREACIÓN DE LA CAPA
            destLYR = self.creaFichRESUL("Polygon?crs=epsg:"+str(srcVal), self.lneGPKGtable.text())
            estiloCAPA = os.path.join(os.path.dirname(__file__), u"./ESTILOS CAPAS/PARCELAS_SELECCION.qml")
            destLYR.loadNamedStyle(estiloCAPA)              # Establecemos el estilo de la capa
        else:
            destLYR = layerEXIST[0]

        if self.rbtCargadosTTMM.isChecked():
            listcapaCatastro=[]
            listcapaCatastro =  [str(self.lwgLISTA_TM.item(i).text()) for i in range(self.lwgLISTA_TM.count())]
        
        else:
            # Detectar los TM del servicio de MUNIPIOS y PROVINCIAS
            text1 = u'PASO 1. DETECTANDO TTMM'
            paso = 1
            self.iface.mainWindow().statusBar().showMessage(text1)
            self.lblINFO.setText(text1)
            self.progressBar.setValue(5)
            self.fun.wait(0.5)

            listPolig = []
            layersExpro = QgsProject.instance().mapLayersByName(capaPolig)
            sf = layersExpro[0].selectedFeatures() #returns QgsFeature object
            if len(sf) == 0:
                sf = layersExpro[0].getFeatures() #returns QgsFeature object
            
            for feat in sf:
                listPolig.append(feat.geometry())
            listaProv, listaMuni = self.fun.buscaTTMMpoligono(listPolig)
            
            if listaProv == "error":
                text = 'ERROR: error de solicitud - ' + listaMuni
                self.lblINFO.setText(self.lblINFO.text()+' - '+text)
                self.progressBar.setValue(100)
                self.fun.showMessage(text1 + '\n' + text)
                QApplication.restoreOverrideCursor()
                return

            root = QgsProject.instance().layerTreeRoot()
            listcapaCatastroFich=[]
            numpasos = 1+len(listaMuni)*3
            numTermMuni = 0
            totalTermMuni = len(listaMuni)
            
            for Muni in listaMuni:
                # print ('Muni - ',Muni[0],Muni[1],Muni[2])
                self.lwgLISTA_TM.addItem(u'%s %s %s'%(Muni[2][0:2],Muni[2][2:5], Muni[1].upper()))

                paso += 1
                text1 = u'PASO %s. OBTENIENDO DATOS CATASTRALES DE TTMM'%(str(paso))
                self.iface.mainWindow().statusBar().showMessage(text1)
                self.lblINFO.setText(text1)
                self.progressBar.setValue(int(100 * paso/numpasos))
                self.fun.wait(0.5)

                codigo_provincia = Muni[2][0:2]
                nombre_prov = self.fun.consultaCatastroCodProvtoProvincia(codigo_provincia)
                codineMuni = Muni[2]
                nombre_muni = Muni[1].upper()
                nombre_prov = self.fun.consultaCatastroCodProvtoProvincia(codigo_provincia)
                nombre_muni1, cmc = self.fun.consultaCatastroCodMunitoMunicipio(nombre_prov, codineMuni[2:5])
                codigo_muni_final = self.fun.completarCeros(cmc,3)
            
                codigo = self.fun.completarCeros(codigo_provincia,2) + codigo_muni_final
                nombregrupo = "CAT - " + nombre_muni + " - " + codigo + " - (WEB)"

                paso += 1
                text1 = u'PASO %s. CARGANDO %s %s'%(str(paso),codigo, nombre_muni)
                self.iface.mainWindow().statusBar().showMessage(text1)
                self.lblINFO.setText(text1)
                self.progressBar.setValue(int(100 * paso/numpasos))
                self.fun.wait(0.5)

                # COMPROBAMOS SI EXISTE CARGADO EL GRUPO DE PARCELAS CATASTRALES
                nombregrupo = "CAT - " + nombre_muni + " - " + codigo + " - (WEB)"
                grupoBUSCAT = QgsProject.instance().layerTreeRoot().findGroup(nombregrupo)

                mess = False
                cargaIface = False
                if self.chbCargaTTMM.isChecked():
                    cargaIface = True
                
                if grupoBUSCAT is None:
                    capaCatPol, capaCatPar, capaCatPolFich, capaCatParFich  = self.fun.cargaCatastroMuni(codigo_provincia, codigo_muni_final, nombre_muni, 'web', 'WEB', self.iface, mess, cargaIface)
                    listcapaCatastroFich.append([capaCatParFich, capaCatPar])
                    capaCatastroFich = capaCatParFich
                    capaCatastro = capaCatPar
                else:
                    listcapaCatastroFich.append("CAT- PAR- " + nombre_muni + " - " + codigo)
                    capaCatastro = "CAT- PAR- " + nombre_muni + " - " + codigo
            
            numTermMuni +=1


        numTermMuni = 0
        totalTermMuni = len(listcapaCatastroFich)
        no_orden = 1
        for muni in listcapaCatastroFich:
            capaCatastroFich = muni[0]
            capaCatastro = muni[1]
            print (capaCatastroFich)
            print (capaCatastro)
            print (capaPolig)
            nombre_muni = capaCatastro[10:(len(capaCatastro)-8)]
            codigo = capaCatastro[-5:]
            cp = int(codigo[:2])
            cm = int(codigo[2:5])


            ############################################################
            #####       SELECCIÓN DE ELEMENTOS EN CAPACATASTRO     #####
            ############################################################
            paso += 1 
            text1 = u'PASO %s. %s %s - SELECCIONANDO ELEMENTOS'%(str(paso), codigo, nombre_muni)
            self.iface.mainWindow().statusBar().showMessage(text1)
            self.lblINFO.setText(text1)
            self.progressBar.setValue(int(100 * paso/numpasos))
            self.fun.wait(0.5)
            
            print ('Número de feats select en capaPolig - ',  layersExpro[0].selectedFeatureCount())
            
            if layersExpro[0].selectedFeatureCount() > 0:
                paramINTERSECT = QgsProcessingFeatureSourceDefinition(capaPolig, True)
            else:
                paramINTERSECT = QgsProcessingFeatureSourceDefinition(capaPolig, False)
            
            algresult = processing.run("native:extractbylocation", {
                            'INPUT' : capaCatastroFich,
                            'PREDICATE': [0],  # intersecan
                            'INTERSECT' : paramINTERSECT, 
                            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
                            })

            print ('algresult - ', algresult)
            estiloCAPA = os.path.join(os.path.dirname(__file__), self.conf.catastro_tool["dir_estilos_catastro"] + 'PARCELAS_SELECCION.qml')
            try:
                vlayer0 = algresult['OUTPUT']
                vlayer0.loadNamedStyle(estiloCAPA)
            except:
                text = u"FALLÓ LA CARGA DE LA CAPA DE SELECCIÓN"
                self.lblINFO.setText(self.lblINFO.text()+' - '+text)
                self.progressBar.setValue(100)
                self.fun.showMessage(text1 + '\n' + text)
                QApplication.restoreOverrideCursor()
                return
                
            # estiloCAPA = os.path.join(os.path.dirname(__file__), self.conf.catastro_tool["dir_estilos_catastro"] + 'PARCELAS_SELECCION.qml')
            
            vlayer0.setName(layerResultName+'pre')
            print ('Número de feats en vlayer0 - ',  vlayer0.featureCount())

            alias = {'RC14':'localId','supcat':'areaValue','AREA':'areaValue'}
            self.copiaFeatToLayer(self.iface, codigo, nombre_muni, destLYR, vlayer0, alias)

        # Añadimos la capa a la vista
        destLYR.setName(layerResultName+'_pro')
        QgsProject.instance().addMapLayer(destLYR)
           
        # Ponemos la capa arriba (1)
        root = QgsProject.instance().layerTreeRoot()
        myvl = root.findLayer(destLYR.id())
        myvlclone = myvl.clone()
        parent = myvl.parent()
        root.insertChildNode(0, myvlclone)
        myvlclone.setName(layerResultName)
        try:
            parent.removeChildNode(myvl)
        except:
            # root.removeChildNode(myvl)    # QgsLayerTreeNode
            print ('parent - ', parent.name(), type(parent), '   IMPOSIBLE BORRAR')
            # QgsProject.instance().removeMapLayers([destLYR.id()])
        

        ## Metemos todo en la capa GPKG final
        # # # options = QgsVectorFileWriter.SaveVectorOptions()
        # # # options.layerName = layerResultTable          # Nombre de la capa
        # # # options.fileEncoding = "UTF-8"                # Encoding
        # # # options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer 
        # # # options.EditionCapability = QgsVectorFileWriter.CanAddNewLayer
        
        # # # _writer = QgsVectorFileWriter.writeAsVectorFormat(destLYR, layerResultFile, options)
        # # # if _writer:
            # # # print(destLYR.name(), _writer, 'line 390')

        # # # self.layerResultFIN=QgsVectorLayer(layerResultFile,layerResultTable,"ogr")
        # # # self.layerResultFIN.loadNamedStyle(estiloCAPA)
        # # # QgsProject.instance().addMapLayer(self.layerResultFIN)
        
        QApplication.restoreOverrideCursor()
        
        stop = timeit.default_timer()
        text = '  --- TERMINADO ---'
        tiempo = 'Tiempo: '+"%0.2f"%(stop - start)+' seg.'
        self.lblINFO.setText(text+tiempo)
        self.fun.showMessage(text+'\n\n'+tiempo)
        self.close()
        return


    def creaFichRESUL(self,uri,name,dest='memory'):
        # createVectorLayer(self,uri,name,dest='memory')
        #   Crea una capa vectorial memoria añadiendoles campos
        #           LISTA CAMPOS
        #   Devuelve la capa vectorial
        #   return vl

        vl = QgsVectorLayer(uri, name, dest)

        pr = vl.dataProvider()

        # Enter editing mode
        vl.startEditing()

        # add fields
        pr.addAttributes([
            # DATOS PARA CAPA 'PARCELAS CATASTRALES'
            QgsField('RC14',        QVariant.String,'',250,0, u"Ref. Catrastal.- Referencia catastral."),
            QgsField('CAT_NMSPC',   QVariant.String,'',250,0,''),
            QgsField('NOM_MUNI',    QVariant.String,'',250,0,''),
            QgsField('PCAT1',       QVariant.String,'',250,0,''),
            QgsField('PCAT2',       QVariant.String,'',250,0,''),
            QgsField('AREA',        QVariant.Double,'',0,0),
            QgsField('MASA',        QVariant.String,'',250,0,''),
            QgsField('PARCELA',     QVariant.String,'',250,0,''),
            QgsField('DELEGACIO',   QVariant.Int,''),
            QgsField('MUNICIPIO',   QVariant.Int,''),
            QgsField('TIPO',        QVariant.String,'',250,0,''),
            QgsField('EJERCICIO',   QVariant.Int,''),
            QgsField('NUM_EXP',     QVariant.Int,''),
            QgsField('CONTROL',     QVariant.Int,''),
            QgsField('VIA',         QVariant.String,'',250,0,''),
            QgsField('NUMERO',      QVariant.Int,''),
            QgsField('NUMERODUP',   QVariant.String,'',250,0,''),
            QgsField('NUMSYMBOL',   QVariant.Int,''),
            QgsField('FECHAALTA',   QVariant.String,'',250,0,''),
            QgsField('FECHABAJA',   QVariant.String,'',250,0,''),
            QgsField('MAPA',        QVariant.String,'',250,0,''),
            QgsField('HOJA',        QVariant.String,'',250,0,''),
            QgsField('COORX',       QVariant.Double,'',0,0),
            QgsField('COORY',       QVariant.Double,'',0,0)
            ] )

        '''
        pr.addAttributes([
            # DATOS PARCELA CATASTRAL EXPROPIADA
            QgsField('no_orden'     ,QVariant.String,'', 50,0,u"Nº Orden.- Número de orden de la finca relativo al proyecto; único para cada finca dentro del expediente. Texto: 1, 2,3…"),
            QgsField('EXPEDIENTE'   ,QVariant.String,'', 50,0,u"EXPEDIENTE.- Clave del expediente de Expropiaciones. Texto: 50"),
            QgsField('term_munic'   ,QVariant.String,'',150,0,u"term_munic.- Nombre término municipal donde radica la finca. Texto: 150"),
            QgsField('cod_term_m'   ,QVariant.String,'',  5,0,u"Cod. Term. Municipal.- Código del término municipal donde radica la finca,"),
            QgsField('pedanía'      ,QVariant.String,'',150,0,u"Pedanía.- En caso de que el término municipal esté dividido en pedanías, nombre de la pedanía donde se ubica la finca."),
            QgsField('pol'          ,QVariant.String,'',  5,0,u"Poligono.- Polígono catastral donde se ubica la finca."),
            QgsField('par'          ,QVariant.String,'',  5,0,u"Parcela.- Parcela catastral donde se ubica la finca."),
            QgsField('subpar'       ,QVariant.String,'',  3,0,u"SubParcela.- Subparcela catastral donde ubica la finca (en caso de existir)."),
            # QgsField('RC14'         ,QVariant.String,'', 20,0,u"Ref. Catrastal.- Referencia catastral."),
            QgsField('dirfinca'     ,QVariant.String,'',255,0,u"Dirección.- Para aquellas fincas de las que se disponga de este dato."),
            QgsField('paraje'       ,QVariant.String,'',255,0,u"Paraje.- Donde se encuentra la finca."),
            QgsField('uso'          ,QVariant.String,'',150,0,u"Uso.- Uso del terreno de la finca."),
            QgsField('concepto'     ,QVariant.String,'', 50,0,u"Concepto.- Dentro del proyecto a realizar, uso que se le dará al terreno; usado sobre todo por IACLM; ejemplo EDAR, línea eléctrica, tubería…"),
            QgsField('tipopropi'    ,QVariant.String,'',  1,0,u"Propiedad Pública.- 0 en caso de propiedad privada, 1 en caso de propiedad a nombre de la JCCM y 2 en caso de propiedad pública no JCCM."),
            QgsField('supcat'       ,QVariant.Double,'', 10,2,u"Superf. Catastral Comp.- Superficie completa de la finca según el catastro en metros cuadrados."),
            QgsField('calificacion' ,QVariant.String,'',  5,0,u"Calificación.- Urbana (U), o Rústica (R). Toda la columna de contener o R o U. Si es Domini Público poner R.")
            ] )

        pr.addAttributes([
            # DATOS SUPERFICIES EXPROPIACIÓN
            QgsField('superfpd'     ,QVariant.Double,'', 10,2,u"Superf. P.D.- Superficie en metros cuadrados a ser expropiada en pleno dominio."),
            QgsField('valorunitpd'  ,QVariant.Double,'', 10,2,u"Valor Unit. P.D.- Valor unitario por metro cuadrado que supone la expropiación en pleno dominio de esta finca."),
            QgsField('importepd'    ,QVariant.Double,'', 10,2,u"Importe P.D.- Importe total a abonar por la parte expropiada en pleno dominio."),
            QgsField('superfot'     ,QVariant.Double,'', 10,2,u"Superf. O.T.- Superficie en metros cuadrados a ser expropiada en ocupación temporal."),
            QgsField('valorunitot'  ,QVariant.Double,'', 10,2,u"Valor Unit. O.T.- Valor unitario por metro cuadrado que supone la expropiación en ocupación temporal de esta finca."),
            QgsField('importeot'    ,QVariant.Double,'', 10,2,u"Importe O.T.- Importe total a abonar por la parte expropiada en ocupación temporal."),
            QgsField('superfsp'     ,QVariant.Double,'', 10,2,u"Superf. S.P.- Superficie en metros cuadrados a ser expropiada en servidumbre de paso."),
            QgsField('valorunitsp'  ,QVariant.Double,'', 10,2,u"Valor Unit. S.P.- Valor unitario por metro cuadrado que supone la expropiación en servidumbre de paso de esta finca."),
            QgsField('importesp'    ,QVariant.Double,'', 10,2,u"Importe S.P.- Importe total a abonar por la parte expropiada en servidumbre de paso."),
            QgsField('superfsv'     ,QVariant.Double,'', 10,2,u"Superf. S.V.- Superficie en metros cuadrados a ser expropiada en servidumbre de vuelo."),
            QgsField('valorunitsv'  ,QVariant.Double,'', 10,2,u"Valor Unit. S.V.- Valor unitario por metro cuadrado que supone la expropiación en servidumbre de vuelo de esta finca."),
            QgsField('importesv'    ,QVariant.Double,'', 10,2,u"Importe S.V.- Importe total a abonar por la parte expropiada en servidumbre de vuelo."),
            # DATOS CAPA
            QgsField('TIPORES'      ,QVariant.String,'', 25,0,u"TIPO PARCELA.- 'EXPRO', 'RESTO', 'DESCUENTO'"),
            QgsField('X_LABEL'      ,QVariant.Double,'', 10,2,u"X_LABEL. - X para etiquetado"),
            QgsField('Y_LABEL'      ,QVariant.Double,'', 10,2,u"X_LABEL. - Y para etiquetado")
            ] )
        '''
        
        # Commit changes
        vl.commitChanges()
        return vl


    def copiaFeatToLayer(self, iface, codigo, nombre_muni, destLYR, vlayer, alias):
        # Se copian los elementos de layerResultName0 a layerResultName
        pr = destLYR.dataProvider()
        destfield_names = [field.name() for field in destLYR.fields()]
        srcfield_names = [field.name() for field in vlayer.fields()]

        destLYR.startEditing()
        sourceLYR = vlayer

        values = [1]
        newIndex = 1
        for feat in destLYR.getFeatures():
            attrs = feat.attributes()
            if isinstance(attrs[0], int) == True:
                values.append(attrs[0])

        if len(values) != 0:
            newIndex = max(values) + 1
        else:
            newIndex = 1

        for feature in sourceLYR.getFeatures():
            fet = QgsFeature(destLYR.fields())
            fet.setGeometry(feature.geometry())
            concepto = 'DP CARRETERA'
            pol = 's/d'
            par = 's/d'
            calificacion = 's/d'
            tipopropi = '0'
            for field in destLYR.fields():
                if field.name() == 'fid':
                    fet.setAttribute('fid', newIndex)
                    newIndex += 1
                    continue
                if sourceLYR.fields().indexFromName(field.name()) != -1:
                    fet.setAttribute(field.name(), feature[field.name()])

                # Cálculo de campos
                concepto = 'DP CARRETERA'
                pol = 's/d'
                par = 's/d'
                calificacion = 's/d'
                califURBRUS = 'X'
                tipopropi = '0'
                for aliascampo in alias:
                    if aliascampo in destfield_names and alias[aliascampo] in srcfield_names:
                        fet.setAttribute(aliascampo, feature[alias[aliascampo]])

                    # if aliascampo == 'RC14' and feature['TIPORES'] != 'DESCUENTO':
                    if aliascampo == 'RC14':
                        RC14 = feature[alias['RC14']]
                        if RC14[5].isalpha():   # Parcela Rústica
                            pol = RC14[6:9]
                            par = RC14[9:14]
                            if RC14[10] == '9':
                                tipopropi = '2' # Parcela Rústica DP
                                calificacion = 'X'
                                califURBRUS = 'X'
                            else:               # Parcela Rústica Privada
                                tipopropi = '0'
                                calificacion = 'R'
                                califURBRUS = 'RU'
                        else:                   # Parcela Urbana
                            pol = RC14[:5]
                            par = RC14[5:7]
                            calificacion = 'U'
                            califURBRUS = 'UR'
                            tipopropi = '0'

            fet.setAttribute('CAT_NMSPC',   'ES.SDGC.CP') # QVariant.String,'',250,0,''),
            fet.setAttribute('NOM_MUNI',    nombre_muni) # QVariant.String,'',250,0,''),
            fet.setAttribute('PCAT1',       RC14[:7]) # QVariant.String,'',250,0,''),
            fet.setAttribute('PCAT2',       RC14[7:14]) # QVariant.String,'',250,0,''),
            fet.setAttribute('MASA',        pol) # QVariant.String,'',250,0,''),
            fet.setAttribute('PARCELA',     par) # QVariant.String,'',250,0,''),
            fet.setAttribute('EJERCICIO',   0) # QVariant.Int,''),
            fet.setAttribute('NUM_EXP',     0) # QVariant.Int,''),
            fet.setAttribute('CONTROL',     0) # QVariant.Int,''),
            fet.setAttribute('VIA',         's/d') # QVariant.String,'',250,0,''),
            fet.setAttribute('NUMERO',      0) # QVariant.Int,''),
            fet.setAttribute('NUMERODUP',   's/d') # QVariant.String,'',250,0,''),
            fet.setAttribute('NUMSYMBOL',   0) # QVariant.Int,''),
            fet.setAttribute('FECHAALTA',   's/d') # QVariant.String,'',250,0,''),
            fet.setAttribute('FECHABAJA',   's/d') # QVariant.String,'',250,0,''),
            fet.setAttribute('MAPA',        's/d') # QVariant.String,'',250,0,''),
            # cp = int(codigo[:2])
            # cm = int(codigo[2:5])
            fet.setAttribute('DELEGACIO',   int(codigo[:2])) # QVariant.Int,''),
            fet.setAttribute('MUNICIPIO',   int(codigo[2:5])) # QVariant.Int,''),
            fet.setAttribute('HOJA',        's/d') # QVariant.String,'',250,0,''),
            fet.setAttribute('TIPO',        califURBRUS) # QVariant.String,'',250,0,''),
            fet.setAttribute('COORX',       feature.geometry().centroid().asPoint()[0]) # QVariant.Double,'',0,0),
            fet.setAttribute('COORY',       feature.geometry().centroid().asPoint()[1]) # QVariant.Double,'',0,0)

            '''
            # DATOS PARCELA CATASTRAL EXPROPIADA
            fet.setAttribute('EXPEDIENTE'   , 'EXP_EXPRO')
            fet.setAttribute('pedanía'      , 's/d')       #"Pedanía.- En caso de que el término municipal esté dividido en pedanías, nombre de la pedanía donde se ubica la finca."
            fet.setAttribute('pol'          , pol)         #"Poligono.- Polígono catastral donde se ubica la finca."
            fet.setAttribute('par'          , par)         #"Parcela.- Parcela catastral donde se ubica la finca."
            fet.setAttribute('subpar'       , 's/d')       #"SubParcela.- Subparcela catastral donde ubica la finca (en caso de existir)."
            fet.setAttribute('dirfinca'     , 's/d')       #"Dirección.- Para aquellas fincas de las que se disponga de este dato."
            fet.setAttribute('paraje'       , 's/d')       #"Paraje.- Donde se encuentra la finca."
            fet.setAttribute('uso'          , 's/d')       #"Uso.- Uso del terreno de la finca."
            fet.setAttribute('concepto'     , concepto)    #"Concepto.- Dentro del proyecto a realizar, uso que se le dará al terreno; usado sobre todo por IACLM; ejemplo EDAR, línea eléctrica, tubería…"
            fet.setAttribute('tipopropi'    , tipopropi)   #"Propiedad Pública.- 0 en caso de propiedad privada, 1 en caso de propiedad a nombre de la JCCM y 2 en caso de propiedad pública no JCCM."
            fet.setAttribute('calificacion' , calificacion)#"Calificación.- Urbana (U) o Rústica (R). Toda la columna de contener o R o U. Si es Domini Público poner R."
            # fet.setAttribute('superfpd'     , feature.geometry().area())
            fet.setAttribute('X_LABEL'      , feature.geometry().centroid().asPoint()[0])
            fet.setAttribute('Y_LABEL'      , feature.geometry().centroid().asPoint()[1])
            '''
            
            pr.addFeatures( [ fet ] )

        destLYR.updateExtents()
        destLYR.commitChanges()

        QgsProject.instance().removeMapLayer(vlayer)
