#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
/***************************************************************************
 catastroPlantillaGMLconst.py
                                 A QGIS plugin
Plantillas para GENERACIÓN DE GML DE CONSTRUCCIONES (Building y OtherConstruction)
según esquema INSPIRE de Catastro

                             -------------------
        begin                : 2017-01-25
        git sha              : $Format:%H$
        copyright            : A.Solabre 2017
        email                : asolabre@jccm.es
 ***************************************************************************/
'''

class catGMLconstv4:
    SRC_DICT = ['25828', '25829', '25830', '25831']

    # Tipos de uso permitidos (mapeo desde tus valores)
    USO_MAPPING = {
        "Residencial": "residential",
        "Almacén-Estacionamiento": "storageParking",
        "Comercial": "commercial",
        "Oficinas": "office",
        "Industrial": "industrial",
        "Ocio y Hostelería": "leisureHospitality",
        "Cultural / Deportivo": "culturalSport",
        "Edificios Singulares": "singularBuilding"
    }

    # Tipos de otras construcciones
    CONSTRUCTION_NATURE = {
        "Piscina": "openAirPool",
        "Depósito": "tank",
        "Tendedero": "dryingYard",
        "PistaDeportiva": "sportsField"
    }

    # PLANTILLA PRINCIPAL (FeatureCollection con namespaces correctos)
    PLANTILLA_1 = """<?xml version="1.0" encoding="ISO-8859-1"?>
<!-- Generado con QGIS plugin {plugin}, v{version} -->

<gml:FeatureCollection gml:id="ES.LOCAL.BU"  xmlns:ad="urn:x-inspire:specification:gmlas:Addresses:3.0" xmlns:base="urn:x-inspire:specification:gmlas:BaseTypes:3.2" xmlns:bu-base="http://inspire.jrc.ec.europa.eu/schemas/bu-base/3.0" xmlns:bu-core2d="http://inspire.jrc.ec.europa.eu/schemas/bu-core2d/2.0" xmlns:bu-ext2d="http://inspire.jrc.ec.europa.eu/schemas/bu-ext2d/2.0" xmlns:cp="urn:x-inspire:specification:gmlas:CadastralParcels:3.0" xmlns:el-bas="http://inspire.jrc.ec.europa.eu/schemas/el-bas/2.0" xmlns:el-cov="http://inspire.jrc.ec.europa.eu/schemas/el-cov/2.0" xmlns:el-tin="http://inspire.jrc.ec.europa.eu/schemas/el-tin/2.0" xmlns:el-vec="http://inspire.jrc.ec.europa.eu/schemas/el-vec/2.0" xmlns:gco="http://www.isotc211.org/2005/gco" xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:gmlcov="http://www.opengis.net/gmlcov/1.0" xmlns:gn="urn:x-inspire:specification:gmlas:GeographicalNames:3.0" xmlns:gsr="http://www.isotc211.org/2005/gsr" xmlns:gss="http://www.isotc211.org/2005/gss" xmlns:gts="http://www.isotc211.org/2005/gts" xmlns:swe="http://www.opengis.net/swe/2.0" xmlns:xlink="http://www.w3.org/1999/xlink"  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://inspire.jrc.ec.europa.eu/schemas/bu-ext2d/2.0 http://inspire.ec.europa.eu/draft-schemas/bu-ext2d/2.0/BuildingExtended2D.xsd">
"""

    # PLANTILLA PARA BUILDING (inicio)
    PLANTILLA_BUILDING_INICIO = """
  <!--Building.   {localid} - {nombreConst}-->
  <gml:featureMember>
   <bu-ext2d:Building gml:id="{namespace}.{localid}_{nombreConst}">
    <bu-core2d:beginLifespanVersion>{fecha}</bu-core2d:beginLifespanVersion>
    <bu-core2d:conditionOfConstruction>functional</bu-core2d:conditionOfConstruction>
    <bu-core2d:inspireId>
     <base:Identifier>
      <base:localId>{localid}_{nombreConst}</base:localId>
      <base:namespace>{namespace}</base:namespace>
     </base:Identifier>
    </bu-core2d:inspireId>
    <!--bu-ext2d:currentUse>{uso}</bu-ext2d:currentUse   ESTA LINEA O SU CONTENIDO ES DUDOSA EN ESTE SITIO-->
    <bu-ext2d:geometry>
     <bu-core2d:BuildingGeometry>
      <bu-core2d:geometry>
"""

    # PLANTILLA PARA GEOMETRÍA EXTERIOR (con o sin huecos)
    PLANTILLA_GEOMETRY_INICIO = """       <gml:Surface gml:id="Surface_{namespace}.{localid}_{nombreConst}" srsName="urn:ogc:def:crs:EPSG::{src}">
        <gml:patches>
         <gml:PolygonPatch>
          <gml:exterior>
           <gml:LinearRing>
            <gml:posList>     <!--Geometria EXTERIOR en sentido de las agujas del reloj-->
"""

    PLANTILLA_GEOMETRY_EXTERIOR_FIN = """            </gml:posList>
           </gml:LinearRing>
          </gml:exterior>
"""

    PLANTILLA_GEOMETRY_INTERIOR_INICIO = """          <gml:interior>
           <gml:LinearRing>
            <gml:posList>     <!--Geometria INTERIOR en sentido contrario de las agujas del reloj-->
"""

    PLANTILLA_GEOMETRY_INTERIOR_FIN = """            </gml:posList>
           </gml:LinearRing>
          </gml:interior>
"""

    PLANTILLA_GEOMETRY_FIN = """         </gml:PolygonPatch>
        </gml:patches>
       </gml:Surface>
"""

    # PLANTILLA PARA BUILDING (fin)
    PLANTILLA_BUILDING_FIN = """	  </bu-core2d:geometry>
      <bu-core2d:horizontalGeometryEstimatedAccuracy uom="m">{precision}</bu-core2d:horizontalGeometryEstimatedAccuracy>
      <bu-core2d:horizontalGeometryReference>footPrint</bu-core2d:horizontalGeometryReference>
      <bu-core2d:referenceGeometry>true</bu-core2d:referenceGeometry>
     </bu-core2d:BuildingGeometry>
    </bu-ext2d:geometry>
    <bu-ext2d:numberOfFloorsAboveGround>{plantas}</bu-ext2d:numberOfFloorsAboveGround>
   </bu-ext2d:Building>
  </gml:featureMember>
"""

    # PLANTILLA PARA OTHERCONSTRUCTION
    PLANTILLA_OTHERCONSTRUCTION = """  <gml:featureMember>
   <bu-ext2d:OtherConstruction gml:id="{namespace}.{localid}_{nombreConst}">
    <bu-core2d:beginLifespanVersion>{fecha}</bu-core2d:beginLifespanVersion>
    <bu-core2d:conditionOfConstruction xsi:nil="true" nilReason="other:unpopulated"/>
    <bu-core2d:inspireId>
     <base:Identifier>
      <base:localId>{localid}_{nombreConst}</base:localId>
      <base:namespace>{namespace}</base:namespace>
     </base:Identifier>
    </bu-core2d:inspireId>
    <bu-ext2d:constructionNature>{naturaleza}</bu-ext2d:constructionNature>
    <bu-ext2d:geometry>
     <gml:Polygon gml:id="Polygon_{namespace}.{localid}_{nombreConst}" srsName="urn:ogc:def:crs:EPSG::{src}">
      <gml:exterior>
       <gml:LinearRing>
        <gml:posList>
{coordenadas}
        </gml:posList>
       </gml:LinearRing>
      </gml:exterior>
     </gml:Polygon>
    </bu-ext2d:geometry>
   </bu-ext2d:OtherConstruction>
  </gml:featureMember>"""

    # PLANTILLA CIERRE
    PLANTILLA_FIN = """</gml:FeatureCollection>"""