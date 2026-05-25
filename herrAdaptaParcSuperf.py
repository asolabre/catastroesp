'''
/***************************************************************************
Name:            herrAdaptaParcSuperf.py
Purpose:        Herramienta para adaptar parcelas a una superficie

        --------------------------------------------------------------------
        begin                : 2025-10-31
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

 Características principales:
Interfaz dockwidget con:
- Selector de capa envolvente
- Selector de campo de superficie
- Controles para tolerancias de superficie y lado

Validaciones:
- Verifica que la capa activa sea de polígono
- Comprueba existencia del campo de superficie
- Valida que la superficie deseada sea mayor que la actual

Algoritmo de modificación:
- Identifica lados que coinciden con el perímetro de la capa envolvente
- Expande solo por lados coincidentes (nunca con lados colindantes con otras parcelas)
- Desplazamiento paralelo solo por los lados coincidentes, para lograr la superficie deseada
- Respeta las tolerancias configuradas

Gestión de resultados:
- Crea capa temporal para resultados
- Mantiene todos los atributos originales
- Aplica estilo diferenciado
 ***************************************************************************/
'''

from qgis.PyQt.QtCore import QVariant, QSettings
from qgis.PyQt.QtWidgets import QDockWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QWidget, QCheckBox
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsGeometry, QgsPointXY, QgsField, QgsFeature,
    QgsWkbTypes, QgsDistanceArea, QgsSpatialIndex, QgsRectangle, QgsFeatureRequest,
    QgsPalLayerSettings, QgsTextFormat, QgsTextBufferSettings, QgsVectorLayerSimpleLabeling
)
from qgis.gui import QgsMapToolEmitPoint, QgsMapCanvas
from qgis.PyQt.QtGui import QColor
import os
import math

class herrAdaptaParcSuperf:
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.dock_widget = None
        self.map_tool = None
        self.parcelas_layer = None
        self.envolvente_layer = None
        self.campo_superficie = "SUP_ACTAS"
        self.tolerancia_superficie = 2.0
        self.tolerancia_lado = 0.2
        self.output_layer = None
        self.capa_parcelas_original = None
        self.nombre_plugin = os.path.basename(os.path.dirname(__file__))
        self.qs = QSettings()
        self.debug_layer = None
        self.perimetro_envolvente = None
        self.parcelas_independientes = False
        self.envolvente_feature = None
        self.ultimo_mensaje = None

    def initGui(self):
        """Inicializa la interfaz gráfica"""
        self.create_dock_widget()
        self.iface.addDockWidget(2, self.dock_widget)

    def unload(self):
        """Limpia los recursos al desactivar el plugin"""
        if self.dock_widget:
            self.iface.removeDockWidget(self.dock_widget)
            self.dock_widget.deleteLater()
        if self.map_tool:
            self.canvas.unsetMapTool(self.map_tool)
        self.limpiar_debug()

    def mostrar_mensaje(self, mensaje, tipo='Info', duracion=5):
        """Muestra un mensaje en la barra de mensajes, limpiando los anteriores"""
        self.iface.messageBar().clearWidgets()
        
        if tipo == 'Warning':
            self.ultimo_mensaje = self.iface.messageBar().pushWarning("Advertencia", mensaje)
        elif tipo == 'Error':
            self.ultimo_mensaje = self.iface.messageBar().pushCritical("Error", mensaje)
        else:
            self.ultimo_mensaje = self.iface.messageBar().pushInfo("Info", mensaje)

    def create_dock_widget(self):
        """Crea el widget dockable"""
        self.dock_widget = QDockWidget("Adaptar Parcelas a Superficie")
        widget = QWidget()
        layout = QVBoxLayout()

        # Selector de capa a modificar (A)
        layout.addWidget(QLabel("Capa a Modificar:"))
        self.combo_parcelas = QComboBox()
        self.cargar_capas_poligono_parcelas()
        layout.addWidget(self.combo_parcelas)

        # Selector de capa de referencia (B)
        layout.addWidget(QLabel("Capa de Referencia:"))
        self.combo_envolvente = QComboBox()
        self.cargar_capas_poligono_envolvente()
        layout.addWidget(self.combo_envolvente)

        # Checkbox para modo parcelas independientes
        self.check_parcelas_independientes = QCheckBox("Capa de Parcelas Independiente")
        self.check_parcelas_independientes.setChecked(False)
        layout.addWidget(self.check_parcelas_independientes)

        # Selector de campo de superficie
        layout.addWidget(QLabel("Campo de superficie:"))
        self.combo_campo = QComboBox()
        layout.addWidget(self.combo_campo)

        # Tolerancia superficie
        layout.addWidget(QLabel("Tolerancia superficie (m²):"))
        self.edit_tol_sup = QLineEdit("2.0")
        layout.addWidget(self.edit_tol_sup)

        # Tolerancia lado
        layout.addWidget(QLabel("Tolerancia lado (m):"))
        self.edit_tol_lado = QLineEdit("0.2")
        layout.addWidget(self.edit_tol_lado)

        # Botón para activar herramienta
        self.btn_activar = QPushButton("Activar Herramienta")
        self.btn_activar.clicked.connect(self.activar_herramienta)
        layout.addWidget(self.btn_activar)

        # Botón para crear capa de salida
        self.btn_crear_capa = QPushButton("Crear Capa Resultado")
        self.btn_crear_capa.clicked.connect(self.crear_capa_salida)
        layout.addWidget(self.btn_crear_capa)

        widget.setLayout(layout)
        self.dock_widget.setWidget(widget)

        # Conectar señales
        self.combo_parcelas.currentTextChanged.connect(self.actualizar_campos_desde_capa_parcelas)
        self.canvas.currentLayerChanged.connect(self.actualizar_combo_parcelas_desde_capa_activa)
        QgsProject.instance().layersAdded.connect(self.actualizar_todo)
        QgsProject.instance().layersRemoved.connect(self.actualizar_todo)

        # Cargar configuraciones guardadas
        self.cargar_configuracion()

        # Actualizar campos inicialmente
        self.actualizar_campos_desde_capa_parcelas()

    def cargar_configuracion(self):
        """Carga la configuración guardada"""
        last_parcelas = self.qs.value(f"{self.nombre_plugin}/last/capaParcelas", "")
        if last_parcelas and self.combo_parcelas.findText(last_parcelas) >= 0:
            self.combo_parcelas.setCurrentText(last_parcelas)

        last_envolvente = self.qs.value(f"{self.nombre_plugin}/last/capaEnvolventeParcelas", "")
        if last_envolvente and self.combo_envolvente.findText(last_envolvente) >= 0:
            self.combo_envolvente.setCurrentText(last_envolvente)

        last_campo = self.qs.value(f"{self.nombre_plugin}/last/campoSuperficiesObjeto", "")
        if last_campo and self.combo_campo.findText(last_campo) >= 0:
            self.combo_campo.setCurrentText(last_campo)

        self.edit_tol_sup.setText(self.qs.value(f"{self.nombre_plugin}/last/toleranciaSuperficie", "2.0"))
        self.edit_tol_lado.setText(self.qs.value(f"{self.nombre_plugin}/last/toleranciaLado", "0.2"))

        try:
            self.check_parcelas_independientes.setChecked(
                self.qs.value(f"{self.nombre_plugin}/last/parcelasIndependientes", False)
            )
        except:
            self.check_parcelas_independientes.setChecked(True)

    def guardar_configuracion(self):
        """Guarda la configuración actual"""
        self.qs.setValue(f"{self.nombre_plugin}/last/capaParcelas", self.combo_parcelas.currentText())
        self.qs.setValue(f"{self.nombre_plugin}/last/capaEnvolventeParcelas", self.combo_envolvente.currentText())
        self.qs.setValue(f"{self.nombre_plugin}/last/campoSuperficiesObjeto", self.combo_campo.currentText())
        self.qs.setValue(f"{self.nombre_plugin}/last/toleranciaSuperficie", self.edit_tol_sup.text())
        self.qs.setValue(f"{self.nombre_plugin}/last/toleranciaLado", self.edit_tol_lado.text())
        self.qs.setValue(f"{self.nombre_plugin}/last/parcelasIndependientes", 
                        self.check_parcelas_independientes.isChecked())

    def actualizar_todo(self):
        """Actualiza tanto las capas como los campos"""
        self.cargar_capas_poligono_parcelas()
        self.cargar_capas_poligono_envolvente()
        self.actualizar_campos_desde_capa_parcelas()

    def cargar_capas_poligono_parcelas(self):
        """Carga las capas de polígono en el combo de parcelas"""
        seleccion_actual = self.combo_parcelas.currentText()
        
        self.combo_parcelas.clear()
        capas_poligono = []

        for layer in QgsProject.instance().mapLayers().values():
            if isinstance(layer, QgsVectorLayer) and layer.geometryType() == QgsWkbTypes.PolygonGeometry:
                capas_poligono.append(layer.name())

        self.combo_parcelas.addItems(capas_poligono)

        if not seleccion_actual and self.canvas.currentLayer():
            nombre_capa_activa = self.canvas.currentLayer().name()
            if nombre_capa_activa in capas_poligono:
                self.combo_parcelas.setCurrentText(nombre_capa_activa)
        elif seleccion_actual in capas_poligono:
            self.combo_parcelas.setCurrentText(seleccion_actual)

    def cargar_capas_poligono_envolvente(self):
        """Carga las capas de polígono en el combo de envolvente"""
        seleccion_actual = self.combo_envolvente.currentText()
        
        self.combo_envolvente.clear()
        capas_poligono = []

        capa_parcelas_nombre = self.combo_parcelas.currentText()

        for layer in QgsProject.instance().mapLayers().values():
            if (isinstance(layer, QgsVectorLayer) and 
                layer.geometryType() == QgsWkbTypes.PolygonGeometry and
                layer.name() != capa_parcelas_nombre):
                capas_poligono.append(layer.name())

        self.combo_envolvente.addItems(capas_poligono)

        if seleccion_actual in capas_poligono:
            self.combo_envolvente.setCurrentText(seleccion_actual)

    def actualizar_combo_parcelas_desde_capa_activa(self):
        """Actualiza el combo de parcelas cuando cambia la capa activa"""
        capa_activa = self.canvas.currentLayer()
        if capa_activa and isinstance(capa_activa, QgsVectorLayer) and capa_activa.geometryType() == QgsWkbTypes.PolygonGeometry:
            nombre_capa_activa = capa_activa.name()
            if self.combo_parcelas.findText(nombre_capa_activa) >= 0:
                self.combo_parcelas.setCurrentText(nombre_capa_activa)

    def actualizar_campos_desde_capa_parcelas(self):
        """Actualiza los campos cuando cambia la capa de parcelas"""
        nombre_capa = self.combo_parcelas.currentText()
        if nombre_capa:
            layer = self.obtener_capa_por_nombre(nombre_capa)
            if layer:
                self.actualizar_combo_campos(layer)

    def actualizar_combo_campos(self, layer):
        """Actualiza el combo de campos con los campos de la capa"""
        self.combo_campo.clear()
        if layer:
            campos_numericos = []
            campos_texto = []

            for field in layer.fields():
                if field.type() in [QVariant.Double, QVariant.Int, QVariant.LongLong]:
                    campos_numericos.append(field.name())
                elif field.type() == QVariant.String:
                    campos_texto.append(field.name())

            if campos_numericos:
                self.combo_campo.addItems(campos_numericos)

            if campos_texto:
                self.combo_campo.addItems(campos_texto)

            index_sup_actas = self.combo_campo.findText("SUP_ACTAS")
            if index_sup_actas >= 0:
                self.combo_campo.setCurrentIndex(index_sup_actas)
                self.campo_superficie = "SUP_ACTAS"
            elif self.combo_campo.count() > 0:
                self.campo_superficie = self.combo_campo.currentText()

    def obtener_capa_por_nombre(self, nombre):
        """Obtiene una capa por su nombre"""
        for layer in QgsProject.instance().mapLayers().values():
            if layer.name() == nombre:
                return layer
        return None

    def obtener_capa_salida_existente(self):
        """Busca si ya existe una capa de resultados"""
        for layer in QgsProject.instance().mapLayers().values():
            if (isinstance(layer, QgsVectorLayer) and 
                layer.name() == "Parcelas_Adaptadas" and
                layer.geometryType() == QgsWkbTypes.PolygonGeometry):
                return layer
        return None

    def obtener_envolvente_cercana(self, parcela_geometry):
        """Encuentra la feature de la envolvente que contiene la parcela"""
        if not self.envolvente_layer:
            return None, None

        try:
            envolvente_cercana = None
            mejor_solapamiento = 0

            for feature in self.envolvente_layer.getFeatures():
                envolvente_geom = feature.geometry()
                if not envolvente_geom.isNull() and envolvente_geom.contains(parcela_geometry):
                    envolvente_cercana = feature
                    break
                elif not envolvente_geom.isNull():
                    interseccion = parcela_geometry.intersection(envolvente_geom)
                    if not interseccion.isNull():
                        area_interseccion = interseccion.area()
                        if area_interseccion > mejor_solapamiento:
                            mejor_solapamiento = area_interseccion
                            envolvente_cercana = feature

            if envolvente_cercana:
                envolvente_geom = envolvente_cercana.geometry()
                perimetro = envolvente_geom.convertToType(QgsWkbTypes.LineGeometry, False)
                return perimetro, envolvente_cercana
            else:
                return None, None

        except Exception as e:
            self.mostrar_mensaje(f"Error al obtener envolvente cercana: {str(e)}", 'Error')
            return None, None

    def crear_capa_salida(self):
        """Crea o reutiliza una capa temporal para los resultados"""
        nombre_capa_parcelas = self.combo_parcelas.currentText()
        if not nombre_capa_parcelas:
            self.mostrar_mensaje("Seleccione una capa a modificar", 'Warning')
            return

        capa_parcelas = self.obtener_capa_por_nombre(nombre_capa_parcelas)
        if not capa_parcelas:
            self.mostrar_mensaje("No se encontró la capa a modificar", 'Error')
            return

        # Guardar capa activa actual para restaurarla después
        capa_activa_original = self.canvas.currentLayer()

        # Verificar si ya existe una capa de resultados
        self.output_layer = self.obtener_capa_salida_existente()
        
        if self.output_layer:
            # Verificar si los campos coinciden
            campos_original = [field.name() for field in capa_parcelas.fields()]
            campos_output = [field.name() for field in self.output_layer.fields()]
            
            if campos_original == campos_output:
                self.mostrar_mensaje("Usando capa de resultados existente", 'Info')
            else:
                # Si los campos no coinciden, crear nueva capa
                QgsProject.instance().removeMapLayer(self.output_layer)
                self.output_layer = None

        if not self.output_layer:
            # Crear nueva capa en memoria
            self.output_layer = QgsVectorLayer("Polygon?crs=" + capa_parcelas.crs().authid(), "Parcelas_Adaptadas", "memory")
            
            # Copiar estructura de campos
            provider = self.output_layer.dataProvider()
            provider.addAttributes(capa_parcelas.fields())
            self.output_layer.updateFields()

            # Estilo visual - relleno
            renderer = self.output_layer.renderer()
            symbol = renderer.symbol()
            symbol.setColor(QColor(0, 255, 0, 100))  # Verde semitransparente

            # Configurar etiquetado automático del área
            self.configurar_etiquetado_area()

            QgsProject.instance().addMapLayer(self.output_layer)
            self.mostrar_mensaje("Capa de resultados creada", 'Info')

        # Hacerla visible
        layer_node = QgsProject.instance().layerTreeRoot().findLayer(self.output_layer.id())
        if layer_node:
            layer_node.setItemVisibilityChecked(True)

        # Restaurar capa activa original
        if capa_activa_original:
            self.canvas.setCurrentLayer(capa_activa_original)

        self.capa_parcelas_original = capa_parcelas

    def configurar_etiquetado_area(self):
        """Configura el etiquetado automático para mostrar el área de las parcelas"""
        if not self.output_layer:
            return
        
        # Crear expresión para calcular el área en metros cuadrados sin decimales
        expresion_area = "round($area, 0) || ' m²'"
        
        # Configurar las etiquetas
        settings = QgsPalLayerSettings()
        settings.fieldName = expresion_area
        settings.isExpression = True
        
        # Configurar formato del texto
        text_format = QgsTextFormat()
        text_format.setColor(QColor(0, 100, 0))  # Verde oscuro
        text_format.setSize(8)
        
        # Configurar buffer
        buffer_settings = QgsTextBufferSettings()
        buffer_settings.setEnabled(True)
        buffer_settings.setSize(1)  # 1 mm
        buffer_settings.setColor(QColor(255, 255, 255))  # Blanco
        text_format.setBuffer(buffer_settings)
        
        settings.setFormat(text_format)
        
        # Configurar ubicación de las etiquetas - CORREGIDO
        # Usar AroundPoint en lugar de OverPoint
        settings.placement = QgsPalLayerSettings.AroundPoint
        
        # Aplicar la configuración de etiquetas
        labels = QgsVectorLayerSimpleLabeling(settings)
        self.output_layer.setLabeling(labels)
        self.output_layer.setLabelsEnabled(True)
        
        # Forzar actualización del renderizado
        self.output_layer.triggerRepaint()



    # def crear_capa_salida(self):
        # """Crea o reutiliza una capa temporal para los resultados"""
        # nombre_capa_parcelas = self.combo_parcelas.currentText()
        # if not nombre_capa_parcelas:
            # self.mostrar_mensaje("Seleccione una capa a modificar", 'Warning')
            # return

        # capa_parcelas = self.obtener_capa_por_nombre(nombre_capa_parcelas)
        # if not capa_parcelas:
            # self.mostrar_mensaje("No se encontró la capa a modificar", 'Error')
            # return

        # # Guardar capa activa actual para restaurarla después
        # capa_activa_original = self.canvas.currentLayer()

        # # Verificar si ya existe una capa de resultados
        # self.output_layer = self.obtener_capa_salida_existente()
        
        # if self.output_layer:
            # # Verificar si los campos coinciden
            # campos_original = [field.name() for field in capa_parcelas.fields()]
            # campos_output = [field.name() for field in self.output_layer.fields()]
            
            # if campos_original == campos_output:
                # self.mostrar_mensaje("Usando capa de resultados existente", 'Info')
            # else:
                # # Si los campos no coinciden, crear nueva capa
                # QgsProject.instance().removeMapLayer(self.output_layer)
                # self.output_layer = None

        # if not self.output_layer:
            # # Crear nueva capa en memoria
            # self.output_layer = QgsVectorLayer("Polygon?crs=" + capa_parcelas.crs().authid(), "Parcelas_Adaptadas", "memory")
            
            # # Copiar estructura de campos
            # provider = self.output_layer.dataProvider()
            # provider.addAttributes(capa_parcelas.fields())
            # self.output_layer.updateFields()

            # # Estilo visual
            # renderer = self.output_layer.renderer()
            # symbol = renderer.symbol()
            # symbol.setColor(QColor(0, 255, 0, 100))

            # QgsProject.instance().addMapLayer(self.output_layer)
            # self.mostrar_mensaje("Capa de resultados creada", 'Info')

        # # Hacerla visible
        # layer_node = QgsProject.instance().layerTreeRoot().findLayer(self.output_layer.id())
        # if layer_node:
            # layer_node.setItemVisibilityChecked(True)

        # # Restaurar capa activa original
        # if capa_activa_original:
            # self.canvas.setCurrentLayer(capa_activa_original)

        # self.capa_parcelas_original = capa_parcelas

    def activar_herramienta(self):
        """Activa la herramienta de selección en el mapa"""
        nombre_parcelas = self.combo_parcelas.currentText()
        if not nombre_parcelas:
            self.mostrar_mensaje("Seleccione una capa a modificar", 'Warning')
            return

        self.parcelas_layer = self.obtener_capa_por_nombre(nombre_parcelas)
        if not self.parcelas_layer:
            self.mostrar_mensaje("No se encontró la capa a modificar", 'Error')
            return

        if self.parcelas_layer.geometryType() != QgsWkbTypes.PolygonGeometry:
            self.mostrar_mensaje("La capa a modificar no es de polígono", 'Error')
            return

        nombre_envolvente = self.combo_envolvente.currentText()
        if not nombre_envolvente:
            self.mostrar_mensaje("Seleccione una capa de referencia", 'Warning')
            return

        self.envolvente_layer = self.obtener_capa_por_nombre(nombre_envolvente)
        if not self.envolvente_layer:
            self.mostrar_mensaje("No se encontró la capa de referencia", 'Error')
            return

        try:
            self.tolerancia_superficie = float(self.edit_tol_sup.text())
            self.tolerancia_lado = float(self.edit_tol_lado.text())
            self.campo_superficie = self.combo_campo.currentText()
        except ValueError:
            self.mostrar_mensaje("Valores de tolerancia inválidos", 'Error')
            return

        if self.campo_superficie not in self.parcelas_layer.fields().names():
            self.mostrar_mensaje(f"Campo {self.campo_superficie} no existe en la capa a modificar", 'Error')
            return

        self.guardar_configuracion()
        self.parcelas_independientes = self.check_parcelas_independientes.isChecked()

        self.map_tool = QgsMapToolEmitPoint(self.canvas)
        self.map_tool.canvasClicked.connect(self.procesar_clic)
        self.canvas.setMapTool(self.map_tool)

        modo_texto = "Parcelas Independientes" if self.parcelas_independientes else "Parcelas Envolventes"
        self.mostrar_mensaje(f"Haga clic en una parcela para adaptarla - Modo: {modo_texto}")

    def procesar_clic(self, point, button):
        """Procesa el clic en el mapa"""
        if not self.parcelas_layer or not self.envolvente_layer:
            return

        self.limpiar_debug()

        parcela_feature = self.buscar_parcela_cercana(point)
        if not parcela_feature:
            self.mostrar_mensaje("No se encontró parcela en la posición seleccionada", 'Warning')
            return

        if self.campo_superficie not in parcela_feature.fields().names():
            self.mostrar_mensaje(f"Campo {self.campo_superficie} no encontrado", 'Error')
            return

        parcela_geometry = parcela_feature.geometry()
        self.perimetro_envolvente, self.envolvente_feature = self.obtener_envolvente_cercana(parcela_geometry)

        if not self.perimetro_envolvente or not self.envolvente_feature:
            self.mostrar_mensaje("No se encontró una envolvente que contenga la parcela seleccionada", 'Error')
            return

        superficie_deseada = parcela_feature[self.campo_superficie]
        superficie_actual = parcela_geometry.area()

        if isinstance(superficie_deseada, str):
            try:
                superficie_deseada = float(superficie_deseada.replace(',', '.'))
            except ValueError:
                self.mostrar_mensaje(f"Valor de superficie no válido: {superficie_deseada}", 'Error')
                return

        if superficie_deseada <= superficie_actual:
            self.mostrar_mensaje(
                f"Superficie deseada ({superficie_deseada:.2f}) debe ser mayor que la actual ({superficie_actual:.2f})", 
                'Warning'
            )
            return

        tramos_candidatos = self.encontrar_tramos_expansion(parcela_geometry)
        if not tramos_candidatos:
            self.mostrar_mensaje("No se encontraron tramos válidos para expansión", 'Warning')
            return

        tramo_seleccionado = max(tramos_candidatos, key=lambda x: x['longitud'])

        nueva_geometria = self.desplazar_tramo_completo(parcela_geometry, tramo_seleccionado,
                                                        superficie_actual, superficie_deseada)

        if nueva_geometria:
            nueva_superficie = nueva_geometria.area()
            diferencia = nueva_superficie - superficie_deseada

            if abs(diferencia) <= self.tolerancia_superficie:
                self.guardar_resultado(parcela_feature, nueva_geometria)
                modo_texto = "independiente" if self.parcelas_independientes else "envolvente"
                mensaje = f"Parcela adaptada ({modo_texto}): {superficie_actual:.2f} → {nueva_superficie:.2f} m² (objetivo: {superficie_deseada:.2f})"
                self.mostrar_mensaje(mensaje)
            else:
                self.mostrar_mensaje(
                    f"No se pudo alcanzar la superficie objetivo. Obtenido: {nueva_superficie:.2f} m² vs Objetivo: {superficie_deseada:.2f} m²", 
                    'Warning'
                )
        else:
            self.mostrar_mensaje("No se pudo adaptar la parcela", 'Error')

    def buscar_parcela_cercana(self, point):
        """Busca la parcela más cercana al punto de clic"""
        try:
            search_point = QgsPointXY(point.x(), point.y())
            point_geom = QgsGeometry.fromPointXY(search_point)
            tolerance_map_units = 10.0

            search_rect = QgsRectangle(
                search_point.x() - tolerance_map_units,
                search_point.y() - tolerance_map_units,
                search_point.x() + tolerance_map_units,
                search_point.y() + tolerance_map_units
            )

            request = QgsFeatureRequest().setFilterRect(search_rect)
            features = self.parcelas_layer.getFeatures(request)

            parcela_cercana = None
            distancia_minima = float('inf')

            for feature in features:
                geometry = feature.geometry()
                if geometry.contains(point_geom):
                    return feature

                distancia = geometry.distance(point_geom)
                if distancia < distancia_minima:
                    distancia_minima = distancia
                    parcela_cercana = feature

            if parcela_cercana and distancia_minima <= tolerance_map_units:
                return parcela_cercana
            else:
                return None

        except Exception as e:
            self.mostrar_mensaje(f"Error al buscar parcela: {str(e)}", 'Error')
            return None

    def encontrar_tramos_expansion(self, geometry):
        """Encuentra TRAMOS CONTINUOS de lados según el modo seleccionado"""
        if geometry.isMultipart():
            multi_poligono = geometry.asMultiPolygon()
            if not multi_poligono:
                return []
            poligono_original = multi_poligono[0][0]
        else:
            poligono_original = geometry.asPolygon()[0]

        if not self.perimetro_envolvente:
            return []

        if self.parcelas_independientes:
            lados_candidatos = set()
            
            for i in range(len(poligono_original) - 1):
                punto1 = poligono_original[i]
                punto2 = poligono_original[i + 1]

                punto_medio = QgsPointXY((punto1.x() + punto2.x()) / 2, (punto1.y() + punto2.y()) / 2)
                punto_medio_geom = QgsGeometry.fromPointXY(punto_medio)
                
                distancia = punto_medio_geom.distance(self.perimetro_envolvente)

                if distancia > self.tolerancia_lado:
                    lados_candidatos.add(i)

        else:
            lados_candidatos = set()
            for i in range(len(poligono_original) - 1):
                punto1 = poligono_original[i]
                punto2 = poligono_original[i + 1]

                segmento = QgsGeometry.fromPolylineXY([punto1, punto2])
                distancia = segmento.distance(self.perimetro_envolvente)

                if distancia <= self.tolerancia_lado:
                    lados_candidatos.add(i)

        if not lados_candidatos:
            return []

        tramos = []
        tramo_actual = []
        lados_ordenados = sorted(lados_candidatos)

        for i, lado_idx in enumerate(lados_ordenados):
            if not tramo_actual:
                tramo_actual.append(lado_idx)
            else:
                if lado_idx == tramo_actual[-1] + 1:
                    tramo_actual.append(lado_idx)
                else:
                    if len(tramo_actual) >= 1:
                        tramos.append(tramo_actual)
                    tramo_actual = [lado_idx]

        if tramo_actual:
            tramos.append(tramo_actual)

        if self.parcelas_independientes and tramos:
            tramos_expandidos = []
            for tramo in tramos:
                tramo_expandido = self.expandir_tramo_independiente(tramo, poligono_original)
                tramos_expandidos.append(tramo_expandido)
            tramos = tramos_expandidos

        tramos_info = []
        for tramo in tramos:
            if not tramo:
                continue
                
            longitud_total = 0
            segmentos = []
            puntos_tramo = []

            for lado_idx in tramo:
                punto1 = poligono_original[lado_idx]
                punto2 = poligono_original[lado_idx + 1]
                segmento = QgsGeometry.fromPolylineXY([punto1, punto2])
                longitud_total += segmento.length()
                segmentos.append((lado_idx, segmento))

                if not puntos_tramo:
                    puntos_tramo.append(punto1)
                puntos_tramo.append(punto2)

            if puntos_tramo:
                polilinea_tramo = QgsGeometry.fromPolylineXY(puntos_tramo)

                tramo_info = {
                    'indices': tramo,
                    'segmentos': segmentos,
                    'longitud': longitud_total,
                    'punto_inicio': poligono_original[tramo[0]],
                    'punto_fin': poligono_original[tramo[-1] + 1],
                    'polilinea': polilinea_tramo,
                    'puntos': puntos_tramo,
                    'tipo': 'independiente' if self.parcelas_independientes else 'envolvente'
                }
                tramos_info.append(tramo_info)

        return tramos_info

    def expandir_tramo_independiente(self, tramo_original, poligono_original):
        """Expande el tramo para incluir vértices de transición en modo independiente"""
        if not tramo_original:
            return tramo_original

        primer_lado = tramo_original[0]
        ultimo_lado = tramo_original[-1]
        
        nuevo_inicio = primer_lado
        for i in range(1, 5):
            lado_anterior = (primer_lado - i) % (len(poligono_original) - 1)
            if lado_anterior < 0:
                lado_anterior += (len(poligono_original) - 1)
            
            punto1 = poligono_original[lado_anterior]
            punto2 = poligono_original[lado_anterior + 1]
            punto_medio = QgsPointXY((punto1.x() + punto2.x()) / 2, (punto1.y() + punto2.y()) / 2)
            distancia = QgsGeometry.fromPointXY(punto_medio).distance(self.perimetro_envolvente)
            
            if distancia <= self.tolerancia_lado:
                nuevo_inicio = lado_anterior
                break

        nuevo_fin = ultimo_lado
        for i in range(1, 5):
            lado_siguiente = (ultimo_lado + i) % (len(poligono_original) - 1)
            
            punto1 = poligono_original[lado_siguiente]
            punto2 = poligono_original[lado_siguiente + 1]
            punto_medio = QgsPointXY((punto1.x() + punto2.x()) / 2, (punto1.y() + punto2.y()) / 2)
            distancia = QgsGeometry.fromPointXY(punto_medio).distance(self.perimetro_envolvente)
            
            if distancia <= self.tolerancia_lado:
                nuevo_fin = lado_siguiente
                break

        if nuevo_inicio <= nuevo_fin:
            tramo_expandido = list(range(nuevo_inicio, nuevo_fin + 1))
        else:
            tramo_expandido = list(range(nuevo_inicio, len(poligono_original) - 1)) + \
                             list(range(0, nuevo_fin + 1))

        return tramo_expandido

    def limpiar_debug(self):
        """Limpia la capa de debug"""
        if self.debug_layer:
            QgsProject.instance().removeMapLayer(self.debug_layer.id())
            self.debug_layer = None

    def calcular_vector_normal(self, punto1, punto2, invertir=False):
        """Calcula el vector normal unitario a un segmento"""
        dx = punto2.x() - punto1.x()
        dy = punto2.y() - punto1.y()

        normal_x = -dy
        normal_y = dx

        if invertir:
            normal_x = -normal_x
            normal_y = -normal_y

        longitud = math.sqrt(normal_x**2 + normal_y**2)
        if longitud > 0:
            normal_x /= longitud
            normal_y /= longitud

        return normal_x, normal_y

    def simplificar_geometria(self, geometry, tolerancia_simplificacion=0.1):
        """Simplifica una geometría eliminando vértices redundantes"""
        try:
            geometria_simplificada = geometry.simplify(tolerancia_simplificacion)
            
            if geometria_simplificada and not geometria_simplificada.isEmpty():
                return geometria_simplificada
            else:
                return geometry
        except Exception as e:
            return geometry

    def filtrar_vertices_redundantes(self, puntos, tolerancia=0.2):
        """Filtra vértices redundantes en una lista de puntos"""
        if len(puntos) < 3:
            return puntos
        
        puntos_filtrados = [puntos[0]]
        
        for i in range(1, len(puntos) - 1):
            punto_actual = puntos[i]
            punto_anterior = puntos_filtrados[-1]
            
            distancia = math.sqrt(
                (punto_actual.x() - punto_anterior.x())**2 + 
                (punto_actual.y() - punto_anterior.y())**2
            )
            
            if distancia > tolerancia:
                puntos_filtrados.append(punto_actual)
        
        if puntos[-1] not in puntos_filtrados:
            puntos_filtrados.append(puntos[-1])
        
        return puntos_filtrados

    def desplazar_tramo_completo(self, geometry, tramo, superficie_actual, superficie_deseada):
        """Desplaza todo el tramo como una polilínea continua"""
        try:
            geometry_simplificada = self.simplificar_geometria(geometry, 0.1)
            
            area_necesaria = superficie_deseada - superficie_actual
            desplazamiento = area_necesaria / tramo['longitud']

            if self.parcelas_independientes:
                desplazamiento = -desplazamiento

            if geometry_simplificada.isMultipart():
                multi_poligono = geometry_simplificada.asMultiPolygon()
                poligono_completo = [[list(anillo) for anillo in multi] for multi in multi_poligono]
                es_multipoligono = True
            else:
                poligono_completo = [[list(anillo) for anillo in geometry_simplificada.asPolygon()]]
                es_multipoligono = False

            anillo_exterior = poligono_completo[0][0]
            
            anillo_filtrado = self.filtrar_vertices_redundantes(anillo_exterior, 0.2)
            poligono_completo[0][0] = anillo_filtrado
            anillo_exterior = anillo_filtrado
            
            puntos_tramo_filtrados = []
            for punto_original in tramo['puntos']:
                punto_encontrado = None
                for punto_filtrado in anillo_exterior:
                    if (abs(punto_filtrado.x() - punto_original.x()) < 0.01 and
                        abs(punto_filtrado.y() - punto_original.y()) < 0.01):
                        punto_encontrado = punto_filtrado
                        break
                
                if punto_encontrado and punto_encontrado not in puntos_tramo_filtrados:
                    puntos_tramo_filtrados.append(punto_encontrado)
            
            if not puntos_tramo_filtrados:
                puntos_tramo_filtrados = tramo['puntos']
            
            nuevo_anillo = anillo_exterior.copy()

            for i, punto_original in enumerate(puntos_tramo_filtrados):
                vertice_idx = None
                for j, punto_anillo in enumerate(anillo_exterior):
                    if (abs(punto_anillo.x() - punto_original.x()) < 0.001 and
                        abs(punto_anillo.y() - punto_original.y()) < 0.001):
                        vertice_idx = j
                        break

                if vertice_idx is None:
                    continue

                normales = []

                if i > 0:
                    punto_anterior = puntos_tramo_filtrados[i-1]
                    normal_anterior = self.calcular_vector_normal(punto_anterior, punto_original, self.parcelas_independientes)
                    normales.append(normal_anterior)

                if i < len(puntos_tramo_filtrados) - 1:
                    punto_siguiente = puntos_tramo_filtrados[i+1]
                    normal_siguiente = self.calcular_vector_normal(punto_original, punto_siguiente, self.parcelas_independientes)
                    normales.append(normal_siguiente)

                if normales:
                    normal_x = sum(n[0] for n in normales) / len(normales)
                    normal_y = sum(n[1] for n in normales) / len(normales)

                    longitud = math.sqrt(normal_x**2 + normal_y**2)
                    if longitud > 0:
                        normal_x /= longitud
                        normal_y /= longitud

                    nuevo_punto = QgsPointXY(
                        punto_original.x() + normal_x * desplazamiento,
                        punto_original.y() + normal_y * desplazamiento
                    )
                    
                    if self.envolvente_feature and self.parcelas_independientes:
                        envolvente_geom = self.envolvente_feature.geometry()
                        punto_geom = QgsGeometry.fromPointXY(nuevo_punto)
                        if not envolvente_geom.contains(punto_geom):
                            punto_proyectado = envolvente_geom.nearestPoint(punto_geom)
                            nuevo_punto = punto_proyectado.asPoint()
                    
                    nuevo_anillo[vertice_idx] = nuevo_punto

            poligono_completo[0][0] = nuevo_anillo

            if es_multipoligono:
                nueva_geometria = QgsGeometry.fromMultiPolygonXY(poligono_completo)
            else:
                nueva_geometria = QgsGeometry.fromPolygonXY(poligono_completo[0])

            nueva_geometria_simplificada = self.simplificar_geometria(nueva_geometria, 0.1)
            
            return nueva_geometria_simplificada

        except Exception as e:
            self.mostrar_mensaje(f"Error en desplazamiento: {str(e)}", 'Error')
            return None

    def guardar_resultado(self, original_feature, nueva_geometria):
        """Guarda el resultado en la capa de salida"""
        if not self.output_layer:
            self.crear_capa_salida()
            if not self.output_layer:
                return

        # Guardar capa activa actual
        capa_activa_original = self.canvas.currentLayer()

        nueva_feature = QgsFeature(original_feature.fields())
        nueva_feature.setAttributes(original_feature.attributes())
        nueva_feature.setGeometry(nueva_geometria)

        provider = self.output_layer.dataProvider()
        provider.addFeatures([nueva_feature])
        self.output_layer.triggerRepaint()
        
        layer_node = QgsProject.instance().layerTreeRoot().findLayer(self.output_layer.id())
        if layer_node:
            layer_node.setItemVisibilityChecked(True)

        # Restaurar capa activa original
        if capa_activa_original:
            self.canvas.setCurrentLayer(capa_activa_original)

        self.canvas.refresh()

# Función para inicializar el plugin
def classFactory(iface):
    return herrAdaptaParcSuperf(iface)