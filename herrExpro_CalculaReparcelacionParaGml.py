"""
/***************************************************************************
herrExpro_CalculaReparcelacionParaGml.py

Parte de un modelo de QGIS
...\datos_Q\MODEL_BUILDER\HERREXPRO_CALCULA_REPARCELACION_PARA_GML.model3
    - HERREXPRO CALCULA REPARCELACION  PARA GML
    - CARGADO COMO MODELO EN GRUPO 'POLIGONOS'


El modelo hace una intersección entre un conjunto de PARCELAS CATASTRALES y una delimitación de un perimetro, uniendo las parcelas intersecadas
con el criterio de no alterar los POLÍGONOS CATASTRALES y manteniendo el resto de las parcelas matrices con su REFERENCIA CATASTRAL.

                                 A QGIS plugin
 catastro
                             -------------------
        begin                : 2024-10-15
        git sha              : $Format:%H$
        copyright            : (C) A.Solabre 2024
        email                : asolabre@jccm.es
 ***************************************************************************/
Model exported as python.
Name : HERREXPRO CALCULA REPARCELACION  PARA GML
Group : POLIGONOS
With QGIS : 33410
"""

from qgis.core import (QgsProcessing, QgsProcessingAlgorithm, QgsProcessingMultiStepFeedback, QgsProcessingParameterNumber,
                        QgsProcessingParameterVectorLayer, QgsProcessingParameterFile, QgsProcessingParameterString,
                        QgsGeometry, QgsFeature, QgsVectorLayer, QgsPoint, QgsPointXY)

import math
import processing

import os
from .config import configuration        # CLASE DE CONFIGURACIÓN DE VARIABLES DEL PROGRAMA
from .functions3 import Functions        # CLASE DE CONFIGURACIÓN DE FUNCIONES GENERALES



class herrExpro_CalculaReparcelacionParaGml(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):

        self.fun = Functions()

        self.nombre_plugin = os.path.basename(os.path.dirname(__file__))

        # Estudiamos la existencia de diferentes direcciones de ficheros de estilos de expropiaciones
        dirPlugin = os.path.dirname(os.path.abspath(__file__))
        defaultValueSTYLE = self.fun.buscaFichDirs([
                                    'C:\\cartografia\\datos_Q\\QSIG\\ESTILOS CAPAS\\',
                                    'Z:\\cartografia\\datos_Q\\QSIG\\ESTILOS CAPAS\\',
                                    'V:\\cartografia\\datos_Q\\QSIG\\ESTILOS CAPAS\\',
                                    dirPlugin+'\\ESTILOS CAPAS\\'],
                                    'EXPRO_REPARCELACION_REMISION.qml')[0]
                                    # 'EXPRO_REPARCELACION.qml')[0]

        # Capa de Parcelas catastrales. Tipo POLIGONO.
        # Contiene todas las parcelas del ámbito que va a intersectar con la capa de Delimitación de las Expropiaciones, descargadas una por una desde el complemento JCCM Carreteras.
        self.addParameter(QgsProcessingParameterVectorLayer('capadeparcelascatastrales', 'CAPA DE PARCELAS CATASTRALES', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        # Capa de DELIMITACION EXPROPIACIONES Tipo POLIGONO.
        # Contiene todos los parímetros del ámbito que va a intersectar con la capa de Parcelas.
        self.addParameter(QgsProcessingParameterVectorLayer('capa_de_delimitacion_expropiaciones', 'CAPA DE DELIMITACION EXPROPIACIONES', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFile('archivo_de_estilo', 'ARCHIVO DE ESTILO',
            behavior=QgsProcessingParameterFile.File,
            fileFilter='QGIS style (*.qml)', defaultValue=defaultValueSTYLE))
        self.addParameter(QgsProcessingParameterFile('archivo_de_destino', 'FICHERO GPKG DE DESTINO',
            behavior=QgsProcessingParameterFile.File,
            fileFilter='Geopackage (*.gpkg)', defaultValue='c:\\temp\\PARC_RESULTANTES.gpkg'))
        self.addParameter(QgsProcessingParameterString( 'capa_destino', 'NOMBRE DE CAPA EN GPKG',
            defaultValue='PARCELAS_RESULTANTES'))
        self.addParameter(QgsProcessingParameterNumber('valor_minimo_islas_borradas_m2', 'VALOR MINIMO ISLAS BORRADAS (m2)', type=QgsProcessingParameterNumber.Double, defaultValue=0.01))


    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(15, model_feedback)
        results = {}
        outputs = {}

        # Comprobar si existe el directorio destino y si no, se crea
        self.fun.comprobarDirectorio(os.path.dirname(parameters['archivo_de_destino'])+'\\')

        # 1. INT
        alg_params = {
            'INPUT': parameters['capadeparcelascatastrales'],
            'INPUT_FIELDS': [''],
            'OVERLAY': parameters['capa_de_delimitacion_expropiaciones'],
            'OVERLAY_FIELDS': [''],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Int'] = processing.run('native:intersection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # 2. Eliminar geometrías nulas INT
        alg_params = {
            # 'INPUT': outputs['MultiparteAMonoparteInt']['OUTPUT'],
            'INPUT': outputs['Int']['OUTPUT'],
            'REMOVE_EMPTY': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['EliminarGeometrasNulasInt'] = processing.run('native:removenullgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # 3. Disolver INT
        alg_params = {
            'FIELD': ['MASA'],
            'INPUT': outputs['EliminarGeometrasNulasInt']['OUTPUT'],
            'SEPARATE_DISJOINT': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DisolverInt'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # 4. Multiparte a monoparte INT
        alg_params = {
            'INPUT': outputs['DisolverInt']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MultiparteAMonoparteInt'] = processing.run('native:multiparttosingleparts', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # 5. Borrar agujeros INT
        alg_params = {
            'INPUT': outputs['MultiparteAMonoparteInt']['OUTPUT'],
            'MIN_AREA': parameters['valor_minimo_islas_borradas_m2'],
            # 'MIN_AREA': 0.01,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['BorrarAgujerosINT'] = processing.run('native:deleteholes', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # 6. NUEVO_CAMPO_EXPRO
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'TIPORES',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Texto (cadena)
            'FORMULA': "value = 'EXPRO'",
            'GLOBAL': '',
            # 'INPUT': outputs['DisolverInt']['OUTPUT'],
            # 'INPUT': outputs['MultiparteAMonoparteInt']['OUTPUT'],
            'INPUT': outputs['BorrarAgujerosINT']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Nuevo_campo_expro'] = processing.run('qgis:advancedpythonfieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # 7. NUEVO CAMPO AREA EXPRO
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'AREA_PARTE',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Decimal (doble)
            'FORMULA': ' format_number(  $area ,3)',
            'INPUT': outputs['Nuevo_campo_expro']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['NuevoCampoAreaExpro'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # 8. DIF_SIM
        alg_params = {
            'INPUT': parameters['capadeparcelascatastrales'],
            'OVERLAY': parameters['capa_de_delimitacion_expropiaciones'],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Dif_sim'] = processing.run('native:symmetricaldifference', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # 9. Multiparte a monoparte DIF_SIM
        alg_params = {
            'INPUT': outputs['Dif_sim']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MultiparteAMonoparteDif_sim'] = processing.run('native:multiparttosingleparts', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # 10. Eliminar geometrías nulas DIF_SIM
        alg_params = {
            'INPUT': outputs['MultiparteAMonoparteDif_sim']['OUTPUT'],
            'REMOVE_EMPTY': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['EliminarGeometrasNulasDif_sim'] = processing.run('native:removenullgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # 11. Borrar agujeros DIF_SIM
        alg_params = {
            'INPUT': outputs['EliminarGeometrasNulasDif_sim']['OUTPUT'],
            'MIN_AREA': parameters['valor_minimo_islas_borradas_m2'],
            # 'MIN_AREA': 0.01,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['BorrarAgujerosDIF_SIM'] = processing.run('native:deleteholes', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # 12. NUEVO_CAMPO_RESTO DIF_SIM
        alg_params = {
            'FIELD_LENGTH': 48,
            'FIELD_NAME': 'TIPORES',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Texto (cadena)
            'FORMULA': "value = 'RESTO'",
            'GLOBAL': '',
            'INPUT': outputs['BorrarAgujerosDIF_SIM']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Nuevo_campo_resto'] = processing.run('qgis:advancedpythonfieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # 13. NUEVO CAMPO AREA RESTO DIF_SIM
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'AREA_PARTE',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Decimal (doble)
            'FORMULA': ' format_number(  $area ,3)',
            'INPUT': outputs['Nuevo_campo_resto']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['NuevoCampoAreaResto'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}


        # 14. Combinar capas vectoriales y crear geopackage

        alg_params = {
            'CRS': 'ProjectCrs',
            'LAYERS': [outputs['NuevoCampoAreaResto']['OUTPUT'],outputs['NuevoCampoAreaExpro']['OUTPUT']],
            'OUTPUT': 'ogr:dbname='+ parameters['archivo_de_destino']  +' table='+ parameters['capa_destino']  +' (geom)'
            # 'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CombinarCapasVectoriales'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # 15. Cargar capa en el proyecto
        alg_params = {
            'INPUT': outputs['CombinarCapasVectoriales']['OUTPUT'],
            'NAME': 'PARCELAS RESULTANTES'
        }
        outputs['CargarCapaEnElProyecto'] = processing.run('native:loadlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # 16. Establecer el estilo de capa
        alg_params = {
            'INPUT': outputs['CargarCapaEnElProyecto']['OUTPUT'],
            'STYLE': parameters['archivo_de_estilo']
        }
        outputs['EstablecerElEstiloDeCapa'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results







        '''
        ######################################################################################################
        ##########    TODO. NO SE CONSIGUE PASAR LA CAPA A LA HERRAMIENTA DE LIMPIEZA DE  CUÑAS   ############
         ##########                                                                                ############
        # Se depuran las cuñas de las dos capas
        print ('NuevoCampoAreaResto: ', outputs['NuevoCampoAreaResto']['OUTPUT'])
        print ('NuevoCampoAreaExpro: ', outputs['NuevoCampoAreaExpro']['OUTPUT'])
        # capaRESTOdepurada = self.depuraCuniasPoligonos(outputs['NuevoCampoAreaResto']['OUTPUT'], precision=0.01)
        # capaEXPROdepurada = self.depuraCuniasPoligonos(outputs['NuevoCampoAreaExpro']['OUTPUT'], precision=0.01)
        capaResto = QgsVectorLayer(outputs['NuevoCampoAreaResto']['OUTPUT'], "capaRESTO", "ogr")
        capaExpro = QgsVectorLayer(outputs['NuevoCampoAreaExpro']['OUTPUT'], "capaEXPRO", "ogr")
        capaRESTOdepurada = self.depuraCuniasPoligonos(capaResto, precision=0.01)
        capaEXPROdepurada = self.depuraCuniasPoligonos(capaExpro, precision=0.01)

        # # Verificar que las capas se cargaron correctamente
        # if not capaResto.isValid() or not capaExpro.isValid():
            # raise ValueError("Error al cargar las capas desde los resultados del algoritmo.")

        # 14. Combinar capas vectoriales y crear geopackage
        # Comprobar si existe el directorio destino y si no, se crea
        self.fun.comprobarDirectorio(os.path.dirname(parameters['archivo_de_destino'])+'\\')

        alg_params = {
            'CRS': 'ProjectCrs',
            'LAYERS': [capaRESTOdepurada,capaEXPROdepurada],
            'OUTPUT': 'ogr:dbname='+ parameters['archivo_de_destino']  +' table='+ parameters['capa_destino']  +' (geom)'
        }
        outputs['CombinarCapasVectoriales'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}


        # 15. Cargar capa en el proyecto
        alg_params = {
            'INPUT': outputs['CombinarCapasVectoriales']['OUTPUT'],
            'NAME': 'PARCELAS RESULTANTES'
        }
        outputs['CargarCapaEnElProyecto'] = processing.run('native:loadlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # 16. Establecer el estilo de capa
        alg_params = {
            'INPUT': outputs['CargarCapaEnElProyecto']['OUTPUT'],
            'STYLE': parameters['archivo_de_estilo']
        }
        outputs['EstablecerElEstiloDeCapa'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results
        ######################################################################################################
        '''


    def depuraCuniasPoligonos(self, capaPoligonos, precision=0.001):
        # Crear una capa de salida en memoria con los mismos campos que la capa original
        capaDepurada = QgsVectorLayer("Polygon?crs=" + capaPoligonos.crs().authid(), "Polígonos depurados", "memory")
        capaDepuradaData = capaDepurada.dataProvider()

        # Copiar los campos de la capa original a la capa de salida
        capaDepuradaData.addAttributes(capaPoligonos.fields())
        capaDepurada.updateFields()

        # Iterar sobre cada polígono de la capa
        for feature in capaPoligonos.getFeatures():
            geom = feature.geometry()

            # Revisar si es multipolígono o polígono
            if geom.isMultipart():
                geometries = geom.asMultiPolygon()
            else:
                geometries = [geom.asPolygon()]

            # Procesar cada anillo del polígono
            new_polygons = []
            for polygon in geometries:
                new_polygon = []
                for ring in polygon:

                    # Comprobamos el sentido del poligono
                    if self.es_dextrogiro(ring):
                        print("El anillo va en sentido dextrogiro (horario).")
                    else:
                        print("El anillo va en sentido levógiro (antihorario).")
                        ring.reverse()

                    #### Depurar cuñas en el anillo actual ####
                    # Iniciamos o iteramos la depuración si se ha borrado algún p2
                    flagBorrado = False
                    iterator = 0
                    while flagBorrado == False and iterator < 20:
                        iterator += 1
                        depurado_ring = []
                        num_points = len(ring)
                        # Añadir el primer punto
                        depurado_ring.append(QgsPointXY(ring[0]))

                        for i in range(1, num_points - 1):
                            # Puntos de la secuencia
                            p1 = QgsPointXY(ring[i - 1])
                            p2 = QgsPointXY(ring[i])
                            p3 = QgsPointXY(ring[i + 1])

                            # Calcular la distancia perpendicular de p2 al segmento p1-p3
                            # dist_perpendicular = distancia_perpendicular(p1, p3, p2)
                            dist_perpendicular, angulo = self.distancia_perpendicular(p1, p3, p2)
                            # print ('dist_perpendicular: ', dist_perpendicular, '  angulo: ', angulo)

                            # Si la distancia es mayor que el umbral, mantener el punto p2
                            if dist_perpendicular > precision:
                                depurado_ring.append(p2)
                            ############################################################################
                            ##########         TODO. REVISAR EL TEMA DE LOS ÁNGULOS            #########
                            ############################################################################
                            # elif angulo >= 90:
                                # depurado_ring.append(p2)
                            # else:
                                # print ('Borrado')
                            ############################################################################

                        # Añadir el último punto para cerrar el anillo
                        depurado_ring.append(QgsPointXY(ring[-1]))
                        if len(depurado_ring) == len(ring): # Comprobar si se ha borrado algún punto
                            flagBorrado = True
                        if flagBorrado == False:
                            ring = depurado_ring
                            iterator = 0

                    # Añadir solo si tiene más de dos puntos y área mayor a 0
                    area = QgsGeometry.fromPolygonXY([depurado_ring]).area()
                    if len(depurado_ring) > 2 and area > 0:
                        new_polygon.append(depurado_ring)

                # Añadir `new_polygon` solo si tiene anillos válidos
                if len(new_polygon) > 0:
                    new_polygons.append(new_polygon)

            # Crear nueva geometría del polígono depurado
            if len(new_polygons) > 0:  # Asegurarse de que haya polígonos válidos
                if geom.isMultipart():
                    new_geom = QgsGeometry.fromMultiPolygonXY(new_polygons)  # Multipolígono
                else:
                    new_geom = QgsGeometry.fromPolygonXY(new_polygons[0])      # Polígono simple

                # Crear una nueva entidad para el polígono depurado y establecer geometría y atributos
                new_feature = QgsFeature(capaDepurada.fields())
                new_feature.setGeometry(new_geom)
                new_feature.setAttributes(feature.attributes())

                # Añadir el polígono depurado a la nueva capa
                capaDepuradaData.addFeature(new_feature)

        capaDepurada.updateExtents()
        return capaDepurada

    def distancia_perpendicular(self, p1, p3, p):
        """Calcula la distancia perpendicular del punto p al segmento p1-p3"""
        # Convertir los puntos a coordenadas
        x1, y1 = p1.x(), p1.y()
        x2, y2 = p3.x(), p3.y()
        x, y = p.x(), p.y()

        # Calcular el numerador y el denominador para la fórmula de la distancia
        numerador = abs((y2 - y1) * x - (x2 - x1) * y + x2 * y1 - y2 * x1)
        denominador = math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)

        # Evitar división por cero
        distancia_perpendicular = numerador / denominador if denominador != 0 else 0

        d1, az1 = self.fun.calcACIMUT(p, p1)
        d2, az2 = self.fun.calcACIMUT(p, p3)
        angulo = az2 - az1

        if angulo < 0:
            angulo = 360 + angulo

        # Distancia perpendicular
        return (0, angulo) if denominador == 0 else (numerador/denominador, angulo)

    def es_dextrogiro(self, ring):
        """Determina si un anillo (lista de puntos) va en sentido dextrogiro (horario)."""
        area_firmada = 0.0
        num_puntos = len(ring)

        for i in range(num_puntos):
            p1 = ring[i]
            p2 = ring[(i + 1) % num_puntos]
            area_firmada += (p2.x() - p1.x()) * (p2.y() + p1.y())

        # Si el área es negativa, el sentido es dextrogiro
        return area_firmada < 0



    def name(self):
        return 'HERREXPRO CALCULA REPARCELACION  PARA GML'

    def displayName(self):
        return 'HERREXPRO CALCULA REPARCELACION  PARA GML'

    def group(self):
        return 'POLIGONOS'

    def groupId(self):
        return 'POLIGONOS'

    def createInstance(self):
        return herrExpro_CalculaReparcelacionParaGml()

    def shortHelpString(self):
        return 
        """
<html>
<body><p><!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.3pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">El modelo hace una intersección entre un conjunto de PARCELAS CATASTRALES y una delimitación de un perimetro, uniendo las parcelas intersecadas con el criterio de no alterar los POLÍGONOS CATASTRALES y manteniendo el resto de las parcelas matrices con su REFERENCIA CATASTRAL.</p></body></html></p>

<h2>Parámetros de entrada</h2>
<h3>CAPA DE PARCELAS CATASTRALES</h3>
<p>Capa de Parcelas catastrales.
Tipo POLIGONO.

Contiene todas las parcelas del ámbito que va a intersectar con la capa de Delimitación de las Expropiaciones, descargadas de forma masiva a partir de un listado, o una por una, desde el complemento JCCM Carreteras. El formato de descarga debe ser l propio del plugin de carreteras.</p>
<h3>CAPA DE DELIMITACION EXPROPIACIONES</h3>
<p>Capa de Delimitación de EPROPIACIONES
Tipo POLIGONO.

Contiene el/los peíimetro(s) de la zona expropiada, que generará el corte conla capa de parcelas.
Todas las zonas de las parcelas inteiores a la zona expropiada, tendrán como valor del campo TIPO_RES='EXPRO'.

Las partes exteriores de cada parcela catastral, tendrán como valor del campo TIPO_RES='RESTO'.</p>
<h3>ARCHIVO DE ESTILO</h3>
<p>Fichero tipo .qml que asigna el estilo a la capa final de 'PARCELAS RESULTANTES'</p>

<h3>FICHERO GPKG DE DESTINO</h3>
<p>Fichero tipo .gpkg en el que se genera la capa final de 'PARCELAS RESULTANTES'</p>

<h3>NOMBRE DE CAPA EN .GPKG</h3>
<p>Nombre de la capa final, por defecto es 'PARCELAS RESULTANTES'</p>

<br><p align="right">Autor del algoritmo: Agustín Solabre Suarez</p>
<p align="right">Servicio Provincial de Carreteras. Albacete</p>
<p align="right">Versión del algoritmo: 1.10 2/11/24</p>
</body></html>
        """
