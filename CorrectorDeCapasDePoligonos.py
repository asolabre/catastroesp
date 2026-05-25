"""
/***************************************************************************
CorrectorDeCapasDePoligonos.py
                                 A QGIS plugin
 catastro
                             -------------------
        begin                : 2024-10-13
        git sha              : $Format:%H$
        copyright            : (C) A.Solabre 2024
        email                : asolabre@jccm.es
 ***************************************************************************/
Model exported as python.
Name : CORRECTOR_DE_CAPAS_DE_POLIGONOS
Group : POLIGONOS
With QGIS : 33410
"""

from qgis.core import (QgsProcessing, QgsProcessingAlgorithm, QgsProcessingMultiStepFeedback,
                        QgsProcessingParameterMapLayer, QgsProcessingParameterNumber, QgsProcessingParameterFeatureSink)
import processing

class CorrectorDeCapasDePoligonos(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterMapLayer('capa_de_poligonos_de_entrada', 'CAPA DE POLIGONOS DE ENTRADA', defaultValue=None, types=[QgsProcessing.TypeVectorPolygon]))
        # Valor mínimo en m2 para borrar islas
        self.addParameter(QgsProcessingParameterNumber('valor_minimo_islas_borradas_m2', 'VALOR MINIMO ISLAS BORRADAS (m2)', type=QgsProcessingParameterNumber.Double, defaultValue=0.005))
        self.addParameter(QgsProcessingParameterFeatureSink('CapaDepurada', 'CAPA DEPURADA', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(10, model_feedback)
        results = {}
        outputs = {}

        # Corregir geometrías
        alg_params = {
            'INPUT': parameters['capa_de_poligonos_de_entrada'],
            'METHOD': 1,  # Estructura
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CorregirGeometrias'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Multiparte a monoparte
        alg_params = {
            'INPUT': outputs['CorregirGeometrias']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MultiparteAMonoparte'] = processing.run('native:multiparttosingleparts', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Borrar geometrías duplicadas
        alg_params = {
            'INPUT': outputs['MultiparteAMonoparte']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['BorrarGeometriasDuplicadas'] = processing.run('native:deleteduplicategeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Extraer por expresión area > 0
        alg_params = {
            'EXPRESSION': ' $area > 0.001',
            'INPUT': outputs['BorrarGeometriasDuplicadas']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtraerPorExpresinArea0'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Eliminar geometrías nulas
        alg_params = {
            'INPUT': outputs['ExtraerPorExpresinArea0']['OUTPUT'],
            'REMOVE_EMPTY': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['EliminarGeometriasNulas'] = processing.run('native:removenullgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Eliminar vértices duplicados
        alg_params = {
            'INPUT': outputs['EliminarGeometriasNulas']['OUTPUT'],
            'TOLERANCE': 0.001,
            'USE_Z_VALUE': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['EliminarVerticesDuplicados'] = processing.run('native:removeduplicatevertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Borrar agujeros
        alg_params = {
            'INPUT': outputs['EliminarVerticesDuplicados']['OUTPUT'],
            'MIN_AREA': parameters['valor_minimo_islas_borradas_m2'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['BorrarAgujeros'] = processing.run('native:deleteholes', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Fuerza la regla de la mano derecha
        alg_params = {
            'INPUT': outputs['BorrarAgujeros']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FuerzaLaReglaDeLaManoDerecha'] = processing.run('native:forcerhr', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Calculadora de campos AREA_CALC
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'AREA_CALC',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (doble)
            'FORMULA': ' format_number(  $area ,2)',
            'INPUT': outputs['FuerzaLaReglaDeLaManoDerecha']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalculadoraDeCamposArea_calc'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Calculadora de campos NUM_VERT
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'NUM_VERT',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Entero (32 bit)
            'FORMULA': ' format_number(  num_points(  $geometry ) ,0) ',
            'INPUT': outputs['CalculadoraDeCamposArea_calc']['OUTPUT'],
            'OUTPUT': parameters['CapaDepurada']
        }
        outputs['CalculadoraDeCamposNum_vert'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['CapaDepurada'] = outputs['CalculadoraDeCamposNum_vert']['OUTPUT']
        return results

    def name(self):
        return 'CORRECTOR_DE_CAPAS_DE_POLIGONOS'

    def displayName(self):
        return 'CORRECTOR_DE_CAPAS_DE_POLIGONOS'

    def group(self):
        return 'POLIGONOS'

    def groupId(self):
        return 'POLIGONOS'

    def shortHelpString(self):
        return """<html><body><p><!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head>CORRECTOR DE CAPAS DE POLIGONOS<style type="text/css">
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8.25pt;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:10pt; text-decoration: underline;">Permite corregir diferentes errores de los polígonos:</span></p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:9pt;"><br /></p>
<ul style="margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;"><li style=" font-size:8.25pt;" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Elimina geometrías incorrectas</li>
<ul style="margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;"><li style=" font-size:8.25pt;" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Convierte geometrías multiparte en monoparte</li>
<ul style="margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;"><li style=" font-size:8.25pt;" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Borra geometrías duplicadas</li>
<ul style="margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;"><li style=" font-size:8.25pt;" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Elimina geometrías de superficie 0</li>
<ul style="margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;"><li style=" font-size:8.25pt;" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Elimina geometrías nulas</li>
<ul style="margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;"><li style=" font-size:8.25pt;" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Elimina vértices duplicados</li>
<ul style="margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;"><li style=" font-size:8.25pt;" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Borra agujeros de superficie menor de una tolerancia dada</li>
<ul style="margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;"><li style=" font-size:8.25pt;" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Fuerza a generar polígonos en sentido dextrógiro<</li></ul></body></html></p>
<p><!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p></body></html></p><br><p align="left">Autor del algoritmo: (C) Agustín Solabre 
asolabre@jccm.es</p><p align="left">Versión del algoritmo: v. 1.00</p></body></html>
"""

    def createInstance(self):
        return CorrectorDeCapasDePoligonos()
