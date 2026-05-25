"""
***************************************************************************
herr_CorrCapasPoligonos.py
                                 A QGIS plugin
                             -------------------
        begin                : 2025-03-14
        git sha              : $Format:%H$
 ***************************************************************************/
"""

from PyQt5.QtGui import QIcon, QPixmap
from qgis.core import (QgsProject, QgsProcessing, QgsProcessingAlgorithm, QgsProcessingMultiStepFeedback, QgsMapLayer, QgsWkbTypes,
                      QgsProcessingFeedback, QgsVectorLayer)
from qgis.PyQt.QtWidgets import QDialog, QFileDialog, QApplication
from PyQt5.QtCore import QSettings, Qt

from qgis.PyQt import uic
from qgis import processing

import os

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), './menus/herr_CorrCapasPoligonos.ui'))

class herr_CorrCapasPoligonos(QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        """Constructor."""
        super(herr_CorrCapasPoligonos, self).__init__(parent)
        self.iface = iface
        self.setupUi(self)

        self.nombre_plugin = os.path.basename(os.path.dirname(__file__))

        self.setWindowIcon(QIcon(f":/plugins/{self.nombre_plugin}/iconos/cat_poligon.jpg"))

        # Conectar el botón de selección de archivo
        self.btnSeleccionfich.clicked.connect(self.seleccionar_archivo_salida)

        # Conectar el botón de corrección
        self.btnCorregirCAPA.clicked.connect(self.corregir_capa)

        # Se rrelena el combo cbxCapaentrada
        lista_CAPAS = self.getCAPAS()
        self.cbxCapaentrada.clear()
        self.cbxCapaentrada.addItems(lista_CAPAS)

        # Comprobamos si la capa activa está en lista_CAPAS y se pone como current en el combo
        self.cbxCapaentrada.setCurrentIndex(1)
        if iface.activeLayer():
            if iface.activeLayer().name() in lista_CAPAS:
                self.cbxCapaentrada.setCurrentText(iface.activeLayer().name())
        self.cbxCapaentrada.setEditable(True)

        self.btnCANCELA.clicked.connect(self.cancela)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)


    def seleccionar_archivo_salida(self):
        """Abre un diálogo para seleccionar el archivo de salida."""
        archivo_salida, _ = QFileDialog.getSaveFileName(
            self, "Seleccionar archivo de salida", "", "GeoPackage (*.gpkg)")
        if archivo_salida:
            self.lneGPKGsalida.setText(archivo_salida)

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

    def cancela(self):
        self.close()
        pass

    def corregir_capa(self):
        """Ejecuta las correcciones en la capa de entrada según las opciones seleccionadas."""
        QApplication.setOverrideCursor(Qt.WaitCursor)   # ICONO DE ESPERA

        try:
            # Obtener la capa de entrada
            nombre_capa = self.cbxCapaentrada.currentText()
            capa_entrada = QgsProject.instance().mapLayersByName(nombre_capa)[0]

            if not capa_entrada or not capa_entrada.isValid():
                self.iface.messageBar().pushCritical("Error", "La capa de entrada no es válida.")
                QApplication.restoreOverrideCursor()
                return

            # Obtener el archivo de salida
            archivo_salida = self.lneGPKGsalida.text()

            # Crear un feedback para el procesamiento
            feedback = QgsProcessingFeedback()

            # Iniciar el procesamiento
            resultados = {}
            salida_temporal = None

            # 1. Corregir geometrías
            if self.chbCorregirGeom.isChecked():
                salida_temporal = self.ejecutar_algoritmo(
                    'native:fixgeometries', {
                        'INPUT': capa_entrada,
                        'METHOD': 1,  # Estructura
                        'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
                    }, feedback, salida_temporal)

            # 2. Convertir multiparte a monoparte
            if self.chbConvMultiMono.isChecked():
                salida_temporal = self.ejecutar_algoritmo(
                    'native:multiparttosingleparts', {
                        'INPUT': salida_temporal if salida_temporal else capa_entrada,
                        'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
                    }, feedback, salida_temporal)

            # 3. Eliminar geometrías duplicadas
            if self.chbElimGeomRep.isChecked():
                salida_temporal = self.ejecutar_algoritmo(
                    'native:deleteduplicategeometries', {
                        'INPUT': salida_temporal if salida_temporal else capa_entrada,
                        'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
                    }, feedback, salida_temporal)

            # 4. Eliminar partes con superficie 0
            if self.chbElimSup0.isChecked():
                salida_temporal = self.ejecutar_algoritmo(
                    'native:extractbyexpression', {
                        'EXPRESSION': '$area > 0.001',
                        'INPUT': salida_temporal if salida_temporal else capa_entrada,
                        'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
                    }, feedback, salida_temporal)

            # 5. Eliminar mini islas
            if self.chbElimMiniIslas.isChecked():
                salida_temporal = self.ejecutar_algoritmo(
                    'native:deleteholes', {
                        'INPUT': salida_temporal if salida_temporal else capa_entrada,
                        'MIN_AREA': 0.001,  # Tolerancia para eliminar mini islas
                        'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
                    }, feedback, salida_temporal)

            # 6. Eliminar vértices repetidos
            if self.chbElimVertRepet.isChecked():
                salida_temporal = self.ejecutar_algoritmo(
                    'native:removeduplicatevertices', {
                        'INPUT': salida_temporal if salida_temporal else capa_entrada,
                        'TOLERANCE': 0.001,  # Tolerancia para eliminar vértices repetidos
                        'USE_Z_VALUE': False,
                        'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
                    }, feedback, salida_temporal)

            # 8. Eliminar Segmentos Comunes
            if self.chbElimSegmComun.isChecked():
                salida_temporal = self.ejecutar_algoritmo(
                    'native:difference', {
                        'INPUT': salida_temporal if salida_temporal else capa_entrada,
                        'OVERLAY': salida_temporal if salida_temporal else capa_entrada,
                        'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
                    }, feedback, salida_temporal)

            # 9. Depurar Autointersección
            if self.chbDepurarAutoint.isChecked():
                salida_temporal = self.ejecutar_algoritmo(
                    'native:fixgeometries', {
                        'INPUT': salida_temporal if salida_temporal else capa_entrada,
                        'METHOD': 1,  # Estructura
                        'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
                    }, feedback, salida_temporal)
        
            # 10. Ordenar Dextrógiro
            if self.chbOrdenarDextro.isChecked():
                salida_temporal = self.ejecutar_algoritmo(
                    'native:forcerhr', {
                        'INPUT': salida_temporal if salida_temporal else capa_entrada,
                        'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
                    }, feedback, salida_temporal)
                    
            # 11. Crear campos AREA_CALC y NUM_VERT
            # if self.chbCreaCAMPOS.isChecked():
            salida_temporal = self.ejecutar_algoritmo(
                'native:fieldcalculator', {
                    'FIELD_LENGTH': 10,
                    'FIELD_NAME': 'AREA_CALC',
                    'FIELD_PRECISION': 2,
                    'FIELD_TYPE': 0,  # Decimal (doble)
                    'FORMULA': 'format_number($area, 2)',
                    'INPUT': salida_temporal if salida_temporal else capa_entrada,
                    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
                }, feedback, salida_temporal)

            salida_temporal = self.ejecutar_algoritmo(
                'native:fieldcalculator', {
                    'FIELD_LENGTH': 0,
                    'FIELD_NAME': 'NUM_VERT',
                    'FIELD_PRECISION': 0,
                    'FIELD_TYPE': 1,  # Entero (32 bit)
                    'FORMULA': 'num_points($geometry)',
                    'INPUT': salida_temporal if salida_temporal else capa_entrada,
                    'OUTPUT': archivo_salida
                }, feedback, salida_temporal)

            # Guardar la capa corregida en el archivo de salida
            if not archivo_salida or not archivo_salida.endswith('.gpkg'):
                self.iface.messageBar().pushCritical("Error", "El archivo de salida no es válido.")
                return
            
            if salida_temporal:
                resultados['CapaDepurada'] = salida_temporal
                self.iface.messageBar().pushInfo("Proceso completado", f"Capa guardada en {archivo_salida}")
            
                # Cargar la capa desde el archivo de salida
                capa_depurada = QgsVectorLayer(archivo_salida, "Polígonos Depurados", "ogr")
                
                # Verificar si la capa se cargó correctamente
                if capa_depurada.isValid():
                    QgsProject.instance().addMapLayer(capa_depurada)
                    self.iface.messageBar().pushInfo("Proceso completado", f"Capa 'Polígonos Depurados' cargada correctamente.")
                else:
                    self.iface.messageBar().pushCritical("Error", "No se pudo cargar la capa depurada.")
            
            QApplication.restoreOverrideCursor()  # ICONO NORMAL
        
        except Exception as e:
            self.iface.messageBar().pushCritical("Error", f"Se produjo un error: {str(e)}")
        finally:
            QApplication.restoreOverrideCursor()  # ICONO NORMAL

    def ejecutar_algoritmo(self, algoritmo, parametros, feedback, entrada_anterior=None):
        """Ejecuta un algoritmo de procesamiento y devuelve la salida."""
        if entrada_anterior:
            parametros['INPUT'] = entrada_anterior
        resultado = processing.run(algoritmo, parametros, feedback=feedback)
        return resultado['OUTPUT']