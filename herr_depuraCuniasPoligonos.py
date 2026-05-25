
"""
/***************************************************************************
Name:           Herr_depuraCuniasPoligonos.py

                                 A QGIS plugin
                                 
Plugin:     catastroesp - Catastro de España
Purpose:    Herramienta de depuración de cuñas de polígonos
        --------------------------------------------------------------------
        begin                : 2024-10-13
        git sha              : $Format:%H$
        Codigo Corregido     : Agustín Solabre
        email                : agusass@hotmail.es
 ***************************************************************************/
Descripción:

Permite eliminar 'cuñas' entre los vértices de un polígono. El script elimina vértices analizando ternas P1,P2,P3 
(secuencias de tres vértices consecutivos), identificando cuando la distancia de P2 a la linea P1-P3 es menor de un valor (precisión), 
en P2 además se debe formar un ángulo < 90 para ser eliminado.
Igualmente, elimina polígonos de solo dos vértices.

DATOS DE ENTRADA:
capaPoligonos, Capa cargada en la TOC obligatoriamente de Polígonos
precision=0.01, valor de la precisón, vajo el qu se eliminan vértices

Model exported as python.
Name : Herr_depuraCuniasPoligonos
Group : POLIGONOS
With QGIS : 33410
"""

from qgis.core import (QgsGeometry, QgsFeature, QgsVectorLayer, QgsPoint, QgsPointXY,
                       QgsWkbTypes, QgsProject)
from PyQt5.QtWidgets import (QMessageBox)
import math

from .functions3 import Functions        # CLASE DE CONFIGURACIÓN DE FUNCIONES GENERALES


class herr_depuraCuniasPoligonos():
    def __init__(self, iface, parent=None):

        self.fun = Functions()
        
        capaPoligonos = iface.activeLayer()
        mess = ''
        if capaPoligonos is None:
            mess = 'Error. No se ha elegido una Capa'
        elif capaPoligonos.type() != QgsVectorLayer.VectorLayer:          # Comprobamos si es vectorial
            mess = 'Error. La capa NO es vectorial'
        elif capaPoligonos.geometryType() != QgsWkbTypes.PolygonGeometry: # Comprobamos si es polígono o multipolígono (incluye variantes 2D y 3D)
            mess = 'Error. La capa NO es de polígonos'

        if mess[:5] == 'Error':
            self.fun.showMessageERR(mess,tittle='Error de Capa')
        else:
            capaDepurada = self.depuraCuniasPoligonos(capaPoligonos, precision=0.01)

            # Añadir la capa al proyecto
            QgsProject.instance().addMapLayer(capaDepurada)


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

