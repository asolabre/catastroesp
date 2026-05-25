# HERRCAT_DETECTA_SOLAPES_HUECOS.PY

from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry, QgsWkbTypes, QgsField
from qgis.PyQt.QtCore import QVariant


# Obtener la capa activa
layer = iface.activeLayer()

# Crear una nueva capa de polígonos en memoria para almacenar las zonas solapadas
solapes_layer = QgsVectorLayer("Polygon?crs=" + layer.crs().authid(), "Zonas_solapadas", "memory")
solapes_layer_data = solapes_layer.dataProvider()

# Añadir campos para el área del solape y el valor del círculo máximo inscribible
solapes_layer_data.addAttributes([
    QgsField("area", QVariant.Double),
    QgsField("MAX_CIRCULO", QVariant.Double)
])
solapes_layer.updateFields()

# Recorrer los elementos de la capa original y detectar solapes
features = list(layer.getFeatures())
for i, feat1 in enumerate(features):
    for feat2 in features[i + 1:]:
        geom1 = feat1.geometry()
        geom2 = feat2.geometry()
        if not geom1.isGeosValid():
            geom1 = geom1.makeValid()
        if not geom2.isGeosValid():
            geom2 = geom2.makeValid()
        # Obtener atributos RC14 de ambos features
        RC1 = feat1['RC14']  # Acceso directo al campo
        RC2 = feat2['RC14']
        print (f'RC1={RC1} - RC2={RC2}')
        if geom1.intersects(geom2):
            solape_geom = geom1.intersection(geom2)
            if not solape_geom.isEmpty():
                # Calcular el área del solape
                area_solape = solape_geom.area()
                
                # Calcular el mayor círculo inscribible utilizando poleOfInaccessibility
                pole = solape_geom.poleOfInaccessibility(0.1)  # Precisión a 0.1 para más exactitud
                max_radio = pole[1] if pole else 0  # El tercer valor en pole es el radio
                
                # Crear un nuevo feature para las zonas solapadas
                solape_feat = QgsFeature()
                solape_feat.setGeometry(solape_geom)
                solape_feat.setAttributes([area_solape, max_radio])
                solapes_layer_data.addFeature(solape_feat)

# Añadir la capa al proyecto
QgsProject.instance().addMapLayer(solapes_layer)

'''
# DETECTA SOLAPES
# Obtener la capa activa
layer = iface.activeLayer()

# Crear una nueva capa de polígonos en memoria para almacenar las zonas solapadas
solapes_layer = QgsVectorLayer("Polygon?crs=" + layer.crs().authid(), "Zonas_solapadas", "memory")
solapes_layer_data = solapes_layer.dataProvider()

# Añadir un campo para el área del solape
solapes_layer_data.addAttributes([QgsField("area", QVariant.Double)])
solapes_layer.updateFields()

# Recorrer los elementos de la capa original y detectar solapes
features = list(layer.getFeatures())
for i, feat1 in enumerate(features):
    for feat2 in features[i + 1:]:
        geom1 = feat1.geometry()
        geom2 = feat2.geometry()
        if geom1.intersects(geom2):
            solape_geom = geom1.intersection(geom2)
            if not solape_geom.isEmpty():
                # Crear un nuevo feature para las zonas solapadas
                solape_feat = QgsFeature()
                solape_feat.setGeometry(solape_geom)
                solape_feat.setAttributes([solape_geom.area()])
                solapes_layer_data.addFeature(solape_feat)

# Añadir la capa al proyecto
QgsProject.instance().addMapLayer(solapes_layer)
'''

# DETECTA HUECOS
# Crear una nueva capa de polígonos en memoria para almacenar los huecos
huecos_layer = QgsVectorLayer("Polygon?crs=" + layer.crs().authid(), "Huecos", "memory")
huecos_layer_data = huecos_layer.dataProvider()

# Obtener la geometría total de todos los polígonos
total_geom = None
for feat in layer.getFeatures():
    geom = feat.geometry()
    if total_geom is None:
        total_geom = QgsGeometry(geom)
    else:
        total_geom = total_geom.combine(geom)

# Calcular los huecos restando las geometrías de la capa activa al bounding box de la capa
bounding_box = layer.extent().asWktPolygon()
bounding_geom = QgsGeometry.fromWkt(bounding_box)

huecos_geom = bounding_geom.difference(total_geom)
if not huecos_geom.isEmpty():
    hueco_feat = QgsFeature()
    hueco_feat.setGeometry(huecos_geom)
    huecos_layer_data.addFeature(hueco_feat)

# Añadir la capa al proyecto
QgsProject.instance().addMapLayer(huecos_layer)
