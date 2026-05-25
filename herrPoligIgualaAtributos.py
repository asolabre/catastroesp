'''
/***************************************************************************
Name:            herrPoligIgualaAtributos.py
Purpose:        Tools for plugin catastroesp

        --------------------------------------------------------------------
        begin                : 2025-10-26
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
'''

from qgis.PyQt.QtCore import QSettings, Qt, pyqtSignal
from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                                QComboBox, QPushButton, QLabel, 
                                QCheckBox, QMessageBox)
from qgis.PyQt.QtGui import QCursor
from qgis.core import (QgsProject, QgsVectorLayer, QgsFeature, 
                      QgsGeometry, QgsPointXY, QgsWkbTypes, QgsField)
from qgis.gui import QgsMapTool, QgsMapCanvas, QgsMapMouseEvent


class SelectorCapaOrigen(QDialog):
    """Widget dockable para seleccionar la capa origen"""
    
    capa_seleccionada = pyqtSignal(QgsVectorLayer)
    
    def __init__(self, parent=None, capa_ultima=None):
        super().__init__(parent)
        self.capa_ultima = capa_ultima
        self.initUI()
        self.cargar_capas_poligonos()
        
    def initUI(self):
        self.setWindowTitle("Transferir Atributos")
        self.setFixedSize(300, 150)
        
        layout = QVBoxLayout()
        
        # Título
        titulo = QLabel("Seleccionar capa origen:")
        layout.addWidget(titulo)
        
        # Selector de capas
        self.combo_capas = QComboBox()
        self.combo_capas.setMinimumHeight(30)
        layout.addWidget(self.combo_capas)
        
        # Checkbox para mantener activo
        self.chk_mantener = QCheckBox("Mantener activo")
        self.chk_mantener.setChecked(True)  # Por defecto mantener activo
        layout.addWidget(self.chk_mantener)
        
        # Botones
        layout_botones = QHBoxLayout()
        
        self.btn_confirmar = QPushButton("Confirmar")
        self.btn_confirmar.clicked.connect(self.confirmar_seleccion)
        
        self.btn_cancelar = QPushButton("Cerrar")
        self.btn_cancelar.clicked.connect(self.close)
        
        layout_botones.addWidget(self.btn_confirmar)
        layout_botones.addWidget(self.btn_cancelar)
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
        
    def cargar_capas_poligonos(self):
        """Carga todas las capas de polígonos del proyecto"""
        self.combo_capas.clear()
        capas_poligonos = []
        
        for layer in QgsProject.instance().mapLayers().values():
            if (isinstance(layer, QgsVectorLayer) and 
                layer.geometryType() == QgsWkbTypes.PolygonGeometry):
                capas_poligonos.append(layer)
        
        # Ordenar por nombre
        capas_poligonos.sort(key=lambda x: x.name())
        
        for capa in capas_poligonos:
            self.combo_capas.addItem(capa.name(), capa)
            
        # Seleccionar la última capa usada si existe
        if self.capa_ultima and self.capa_ultima in capas_poligonos:
            index = self.combo_capas.findText(self.capa_ultima.name())
            if index >= 0:
                self.combo_capas.setCurrentIndex(index)
    
    def confirmar_seleccion(self):
        """Confirma la selección de la capa origen"""
        capa = self.combo_capas.currentData()
        if capa:
            self.capa_seleccionada.emit(capa)
            # Solo cerrar si el usuario no quiere mantenerlo activo
            if not self.chk_mantener.isChecked():
                self.close()


class MapaToolTransferirAtributos(QgsMapTool):
    """Herramienta de mapa para transferir atributos"""
    
    def __init__(self, canvas, plugin):
        super().__init__(canvas)
        self.canvas = canvas
        self.plugin = plugin
        self.capa_origen = None
        self.capa_destino_actual = None
        self.selector_abierto = False
        self.primer_uso = True
        
    def canvasReleaseEvent(self, event: QgsMapMouseEvent):
        """Manejador del evento de clic en el mapa"""
        if event.button() == Qt.LeftButton:
            self.procesar_clic(event.mapPoint())
    
    def procesar_clic(self, punto: QgsPointXY):
        """Procesa el clic según el estado actual"""
        capa_destino = self.canvas.currentLayer()
        
        # Verificar condiciones para primer uso
        if self.es_primer_uso(capa_destino):
            self.primer_uso = True
            self.mostrar_selector_capa(punto)
        else:
            # Uso normal - transferir directamente
            self.transferir_atributos_directo(punto, capa_destino)
    
    def es_primer_uso(self, capa_destino):
        """Determina si es necesario mostrar el selector (primer uso)"""
        if self.primer_uso:
            return True
        
        # Verificar si la capa destino ha cambiado
        if capa_destino != self.capa_destino_actual:
            return True
        
        # Verificar si la capa origen ya no existe
        if self.capa_origen and self.capa_origen not in QgsProject.instance().mapLayers().values():
            return True
        
        # Verificar si no hay capa origen definida
        if not self.capa_origen:
            return True
            
        return False
    
    def transferir_atributos_directo(self, punto: QgsPointXY, capa_destino=None):
        """Transfiere atributos directamente sin mostrar selector"""
        if not capa_destino:
            capa_destino = self.canvas.currentLayer()
            
        if not capa_destino or not isinstance(capa_destino, QgsVectorLayer):
            QMessageBox.warning(None, "Advertencia", 
                              "No hay una capa vectorial activa seleccionada")
            return False
            
        # Actualizar capa destino actual
        self.capa_destino_actual = capa_destino
        
        # Realizar la transferencia
        return self.ejecutar_transferencia(punto, capa_destino)
    
    def mostrar_selector_capa(self, punto=None):
        """Muestra el selector de capa origen"""
        if not self.selector_abierto:
            self.selector_abierto = True
            self.punto_click = punto  # Guardar el punto para usarlo después
            self.selector = SelectorCapaOrigen(
                parent=self.canvas, 
                capa_ultima=self.capa_origen
            )
            self.selector.capa_seleccionada.connect(self.establecer_capa_origen)
            self.selector.finished.connect(self.cerrar_selector)
            
            # Posicionar en esquina superior derecha
            canvas_geo = self.canvas.geometry()
            selector_geo = self.selector.geometry()
            x = canvas_geo.right() - selector_geo.width() - 10
            y = canvas_geo.top() + 10
            
            self.selector.move(x, y)
            self.selector.show()
    
    def establecer_capa_origen(self, capa):
        """Establece la capa origen seleccionada"""
        self.capa_origen = capa
        self.primer_uso = False
        # Guardar en configuración
        self.plugin.guardar_ultima_capa(capa)
        
        # Actualizar capa destino actual
        self.capa_destino_actual = self.canvas.currentLayer()
        
        # Si tenemos un punto guardado, ejecutar la transferencia
        if hasattr(self, 'punto_click') and self.punto_click:
            self.transferir_atributos_directo(self.punto_click)
    
    def cerrar_selector(self):
        """Maneja el cierre del selector"""
        self.selector_abierto = False
        # Limpiar el punto guardado
        if hasattr(self, 'punto_click'):
            del self.punto_click
    
    def ejecutar_transferencia(self, punto: QgsPointXY, capa_destino: QgsVectorLayer):
        """Ejecuta la transferencia de atributos"""
        try:
            # Buscar feature en capa origen
            feature_origen = self.buscar_feature_en_punto(self.capa_origen, punto)
            if not feature_origen:
                QMessageBox.information(None, "Información", 
                                      "No se encontró ningún polígono en la posición seleccionada (capa origen)")
                return False
            
            # Buscar feature en capa destino
            feature_destino = self.buscar_feature_en_punto(capa_destino, punto)
            if not feature_destino:
                QMessageBox.information(None, "Información", 
                                      "No se encontró ningún polígono en la posición seleccionada (capa destino)")
                return False
            
            # Obtener identificadores para el mensaje
            id_origen = self.obtener_identificador_feature(feature_origen, self.capa_origen)
            id_destino = self.obtener_identificador_feature(feature_destino, capa_destino)
            
            # Clonar campos si es necesario (excluyendo campos índice)
            self.clonar_campos_si_necesario(capa_destino)
            
            # Transferir atributos
            cambios_realizados = self.transferir_atributos_features(feature_origen, feature_destino, capa_destino)
            
            if cambios_realizados:
                mensaje = f"Atributos transferidos correctamente\n\nDesde:\n   Capa: {self.capa_origen.name()}\n   Elemento: {id_origen}\n\nA:\n   Capa: {capa_destino.name()}\n   Elemento: {id_destino}\n\nSe transfirieron {cambios_realizados} atributos"
                QMessageBox.information(None, "Éxito", mensaje)
            else:
                mensaje = f"No se encontraron atributos para transferir\n\nOrigen:\n   Capa: {self.capa_origen.name()}\n   Elemento: {id_origen}\n\nDestino:\n   Capa: {capa_destino.name()}\n   Elemento: {id_destino}"
                QMessageBox.information(None, "Información", mensaje)
            
            return True
            
        except Exception as e:
            QMessageBox.critical(None, "Error", 
                               f"Error al transferir atributos: {str(e)}")
            return False
    
    def obtener_identificador_feature(self, feature: QgsFeature, capa: QgsVectorLayer) -> str:
        """Obtiene un identificador legible para el feature"""
        # Primero intentar con campos comunes de identificación
        campos_id = ['nombre', 'id', 'fid', 'gid', 'codigo', 'referencia']
        
        for campo in campos_id:
            if capa.fields().indexOf(campo) >= 0:
                valor = feature.attribute(campo)
                if valor is not None and str(valor).strip():
                    return f"{campo}: {valor}"
        
        # Si no encuentra campos específicos, usar el ID interno
        return f"ID: {feature.id()}"
    
    def buscar_feature_en_punto(self, capa: QgsVectorLayer, punto: QgsPointXY) -> QgsFeature:
        """Busca un feature en la posición del punto"""
        tolerance = 10 / self.canvas.scale()  # Tolerancia en unidades del mapa
        
        for feature in capa.getFeatures():
            if feature.geometry().contains(punto):
                return feature
            # También verificar con buffer para mayor tolerancia
            buffered_geom = feature.geometry().buffer(tolerance, 5)
            if buffered_geom.contains(punto):
                return feature
                
        return None
    
    def es_campo_indice(self, nombre_campo, capa=None):
        """
        Determina si un campo es un campo índice que no debe modificarse.
        Considera el contexto de infraestructuras donde 'pk' es Punto Kilométrico.
        """
        # Nombres que SIEMPRE son índices (independientemente del contexto)
        nombres_indice_global = ['fid', 'id', 'gid', 'oid', 'feature_id', 'primary_key']
        
        nombre_lower = nombre_campo.lower()
        
        # Si está en la lista global, es índice
        if nombre_lower in nombres_indice_global:
            return True
            
        # Verificar si es llave primaria de la capa
        if capa:
            provider = capa.dataProvider()
            if hasattr(provider, 'pkAttributeIndexes'):
                pk_indexes = provider.pkAttributeIndexes()
                campos = capa.fields()
                for idx in pk_indexes:
                    if idx < campos.count() and campos.field(idx).name().lower() == nombre_lower:
                        return True
        
        return False
    
    def clonar_campos_si_necesario(self, capa_destino: QgsVectorLayer):
        """Clona los campos de la capa origen a la destino si no existen, excluyendo campos índice"""
        campos_origen = [field.name() for field in self.capa_origen.fields()]
        campos_destino = [field.name() for field in capa_destino.fields()]
        
        campos_faltantes = []
        provider = capa_destino.dataProvider()
        
        for campo in self.capa_origen.fields():
            # Excluir campos índice
            if (campo.name() not in campos_destino and 
                not self.es_campo_indice(campo.name(), self.capa_origen)):
                campos_faltantes.append(campo)
        
        if campos_faltantes:
            # Añadir campos faltantes
            if provider.addAttributes(campos_faltantes):
                capa_destino.updateFields()
    
    def transferir_atributos_features(self, feature_origen: QgsFeature, 
                                    feature_destino: QgsFeature, 
                                    capa_destino: QgsVectorLayer) -> int:
        """
        Transfiere los atributos de un feature a otro, excluyendo campos índice.
        Retorna el número de atributos transferidos.
        """
        # Obtener campos destino
        campos_destino = capa_destino.fields()
        
        # Crear diccionario de cambios
        cambios = {}
        campos_transferidos = 0
        
        for idx_destino in range(campos_destino.count()):
            campo_destino = campos_destino.field(idx_destino)
            campo_nombre = campo_destino.name()
            
            # Saltar campos índice
            if self.es_campo_indice(campo_nombre, capa_destino):
                continue
            
            # Buscar campo en origen
            idx_origen = self.capa_origen.fields().lookupField(campo_nombre)
            
            if idx_origen >= 0:
                valor_origen = feature_origen.attribute(idx_origen)
                valor_actual = feature_destino.attribute(idx_destino)
                
                # Solo transferir si el valor es diferente y compatible
                if (valor_origen != valor_actual and 
                    self.son_tipos_compatibles(valor_origen, campo_destino.type())):
                    cambios[idx_destino] = valor_origen
                    campos_transferidos += 1
        
        # Aplicar cambios si hay alguno
        if cambios:
            capa_destino.startEditing()
            if capa_destino.changeAttributeValues(feature_destino.id(), cambios):
                if capa_destino.commitChanges():
                    # Refrescar el canvas para ver los cambios
                    self.canvas.refresh()
                    return campos_transferidos
                else:
                    capa_destino.rollBack()
                    raise Exception("Error al guardar los cambios en la capa destino")
            else:
                capa_destino.rollBack()
                raise Exception("Error al aplicar los cambios en la capa destino")
        
        return 0
    
    def son_tipos_compatibles(self, valor, tipo_destino):
        """Verifica si los tipos de datos son compatibles"""
        if valor is None:
            return True
            
        # Mapeo de tipos QgsField a tipos Python
        tipo_qgs_a_python = {
            # Enteros
            2: [int],  # QVariant.Int
            4: [int],  # QVariant.LongLong
            # Decimales
            6: [int, float],  # QVariant.Double
            # Cadenas
            10: [str, int, float],  # QVariant.String
            # Booleanos
            1: [bool, int],  # QVariant.Bool
            # Fechas
            14: [str],  # QVariant.Date
            15: [str],  # QVariant.Time
            16: [str],  # QVariant.DateTime
        }
        
        tipo_valor = type(valor)
        
        # Verificar compatibilidad
        if tipo_destino in tipo_qgs_a_python:
            tipos_compatibles = tipo_qgs_a_python[tipo_destino]
            for tipo_compatible in tipos_compatibles:
                if isinstance(valor, tipo_compatible):
                    return True
        
        # Para tipos no mapeados, intentar conversión genérica
        try:
            # Intentar una conversión simple
            if tipo_destino in [2, 4] and isinstance(valor, (str, float)):
                int(valor)
                return True
            elif tipo_destino == 6 and isinstance(valor, (str, int)):
                float(valor)
                return True
            elif tipo_destino == 10:
                str(valor)
                return True
        except (ValueError, TypeError):
            return False
            
        return False


class HerrPoligIgualaAtributos:
    """Clase principal para la herramienta de transferencia de atributos"""
    
    def __init__(self, iface, nombre_plugin):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.nombre_plugin = nombre_plugin
        self.qs = QSettings()
        
        self.herramienta = None
        self.herramienta_activa = False
    
    def initGui(self):
        """Inicializa la interfaz gráfica"""
        self.activar_herramienta()
    
    def unload(self):
        """Descarga la herramienta"""
        self.desactivar_herramienta()
    
    def activar_herramienta(self):
        """Activa la herramienta en el canvas"""
        if not self.herramienta:
            self.herramienta = MapaToolTransferirAtributos(self.canvas, self)
        
        self.canvas.setMapTool(self.herramienta)
        self.herramienta_activa = True
        
        # Cargar última capa usada
        ultima_capa = self.cargar_ultima_capa()
        if ultima_capa:
            self.herramienta.capa_origen = ultima_capa
            self.herramienta.primer_uso = False
    
    def desactivar_herramienta(self):
        """Desactiva la herramienta"""
        if self.herramienta and self.herramienta_activa:
            self.canvas.unsetMapTool(self.herramienta)
            self.herramienta_activa = False
    
    def cargar_ultima_capa(self) -> QgsVectorLayer:
        """Carga la última capa usada desde la configuración"""
        capa_nombre = self.qs.value(f"{self.nombre_plugin}/last/capaIgualaAtributos")
        if capa_nombre:
            for layer in QgsProject.instance().mapLayers().values():
                if layer.name() == capa_nombre and isinstance(layer, QgsVectorLayer):
                    return layer
        return None
    
    def guardar_ultima_capa(self, capa: QgsVectorLayer):
        """Guarda la última capa usada en la configuración"""
        if capa:
            self.qs.setValue(f"{self.nombre_plugin}/last/capaIgualaAtributos", capa.name())