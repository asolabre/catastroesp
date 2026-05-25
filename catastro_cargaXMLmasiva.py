# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name:           catastro_cargaXMLmasiva.py
Purpose: Permite la carga de un fichero XML de consulta masiva al catastro en forma de tabla de datos en QGIS

        --------------------------------------------------------------------
        begin                : 2024-08-20
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Agustín Solabre (JCCM)
        Codigo               : ASS
        email                : gis.carreteras@jccm.es
 ***************************************************************************/

Adaptado para:
- Recorre cada <DSA>.
- Dentro busca <LBI> y sus <BIE>.
- Cada <BIE> = feature base.
- Si hay repetidos (<SPA>, <ELC>, <TIT>…), genera features adicionales.
 ***************************************************************************/
"""

import os
from qgis.PyQt.QtXml import QDomDocument
from qgis.PyQt.QtWidgets import QFileDialog
from qgis.core import QgsVectorLayer, QgsField, QgsFeature, QgsProject
from qgis.PyQt.QtCore import QVariant

from PyQt5.QtWidgets import (QApplication)
from PyQt5.QtCore import    (Qt)

from .config import configuration        # CLASE DE CONFIGURACIÓN DE VARIABLES DEL PROGRAMA
from .functions3 import Functions        # CLASE DE CONFIGURACIÓN DE FUNCIONES GENERALES


class catastro_cargaXMLmasiva:

    def __init__(self, iface):
        """Constructor."""
        self.fun = Functions()
        self.conf = configuration()

        self.nombre_plugin = os.path.basename(os.path.dirname(__file__))
        
        self.campos = set()
        self.creaDictCatastro()

        self.cargar_tabla_desde_xml_dinamico()
        
        
    def creaDictCatastro(self):
    
        # Comentarios de campos 
        # XSD + Anejo 2 del PDF de Catastro 
        #   https://www.catastro.hacienda.gob.es/ayuda/masiva/Descripcion_consulta_masiva_datos_Catastrales.pdf
        #   AMBIGÜEDADES
        #       CPA: en localización rústica es código de parcela; en economía/registro aparece como coeficiente de participación.
        #       SUP: aparece tanto en IBI (m²) como en SPA (ha)
        
        # Datos de todos los campos de catastro de CONSULTA MASIVA leídos desde CONGIG.PY
        self.defCamposCatastroMasivas = self.conf.defCamposCatastroMasivas
        
        # Orden para colocar los campos
        self.listCamposINI =['RC14', 'CP', 'NP', 'CMC', 'NM', 'CM', 'DTR', 'NEM', 'NPA', 'CPO', 'CPA' ,'TIP',  # Localización general y tipo
                        'LSU', 'LEC', 'UEC', 'USO',  # Usos
                        'SUCF', 'SUPF',              # Superficies
                        'LBI','BIE',                                      # Lista de bienes
                            # Identificación del bien (IBI)
                        'IBI','DEL','RCA','PCA','CAR','CDC1','CDC2','SUP_construida','ACO','FAL',
                            # Domicilio estructurado (DT)
                        'DT','LOINE','LOCS','LOUS',                        
                            # Localización urbana (LOURB)
                        'LOURB','DIR','CV','TV','NV','PNP','PLP','SNP','SLP','KM','TD','LOINT','BQ','ES','PT','PU','DP','DM','LOURS',
                            # Localización rústica (LORS / LORUS) y adicionales
                        'LORS','LORUS','CMA','CZC','CPP','CPAJ',
                            # Finca (FIN)
                        'FIN','LFI','SUCF','SUPF','TIF',
                            # Subparcelas (LSU / SPA)
                        'SPA','SUB','CUL','INT','VCS','SUP',
                            # Elementos constructivos (LEC / ELC)
                        'ELC','ESC','PLA','PUE','SEC',
                            # Lista de titulares (LIT / TIT)
                        'LIT','TIT','APN','DER','PDE','SUF','DFT1','DFT2','CBI',
                            # Datos económicos (DEB)
                        'DEB','AAC','VCA','VSU','VCO',
                            # Finca registral (FR)
                        'FR','PROVFR','REGFR','FINFR',
                            # Coeficiente de participación (aparece como CPA fuera del bloque rústico)
                        'CPA_coef',
                        'NIF', 'APE','RC','PROV','MUN','POL','PAR',             # Datos de entrada reflejados en la salida
                        'DS', 'LAT', 'ATE', 'LDS', 'DSA', 'ERR', 'COD', 'DES']  # Raíz y metadatos de salida
                

    def cargar_tabla_desde_xml_dinamico(self):
        xml_path, _ = QFileDialog.getOpenFileName(None, "Seleccionar archivo XML", "", "Archivos XML (*.xml)")
        if not xml_path:
            print("No se seleccionó ningún archivo.")
            text = u'No se seleccionó ningún archivo'
            self.fun.showMessageERR(text,"",tittle=self.nombre_plugin,)
            return

        QApplication.setOverrideCursor(Qt.WaitCursor)   # Cursor TRABAJANDO

        xml_Dir, xml_FilExtName = os.path.split(xml_path)
        xml_file, xml_Ext = os.path.splitext(xml_FilExtName)
        XML_tabla_name = xml_file + '_XML'
        print("Nombre del fichero:", xml_file)

        doc = QDomDocument()
        with open(xml_path, 'r', encoding='utf-8') as f:
            if not doc.setContent(f.read()):
                QApplication.restoreOverrideCursor() # Se restituye cursor
                print("Error al cargar el archivo XML")
                text = u'Error al cargar el archivo XML\n\n'+xml_file
                self.fun.showMessageERR(text,"",tittle=self.nombre_plugin,)
                return

        raiz = doc.documentElement()

        # ====== DETECCIÓN DE CAMPOS ======
        nodo_dsa = raiz.firstChildElement("LDS").firstChildElement("DSA")
        while not nodo_dsa.isNull():
            nodo_bie = nodo_dsa.firstChildElement("LBI").firstChildElement("BIE")
            while not nodo_bie.isNull():
                self.obtener_campos(nodo_bie)
                nodo_bie = nodo_bie.nextSiblingElement("BIE")
            nodo_dsa = nodo_dsa.nextSiblingElement("DSA")

        print(f"Campos detectados: {len(self.campos)} -> {self.campos}")


        # ====== CREACIÓN DE LA TABLA EN MEMORIA ======
        layer = QgsVectorLayer("None", XML_tabla_name, "memory")
        provider = layer.dataProvider()

        # Mapeo de tipos
        mapTipos = {
            'String': QVariant.String,
            'Int': QVariant.Int,
            'Double': QVariant.Double
        }

        # Creamos un diccionario para localizar rápido la definición de cada campo
        dictCamposCatastro = {c['name']: c for c in self.defCamposCatastroMasivas}

        fields = []

        for campoINI in self.listCamposINI:
            if campoINI in dictCamposCatastro:
                # Crear campo según definición en defCamposCatastroMasivas
                campo = dictCamposCatastro[campoINI]
                qtype = mapTipos[campo['type']]
                length = campo['len'] if campo['len'] else 0
                prec   = campo['prec'] if campo['prec'] else 0
                # comentario = campo.get('comment', "")
                comentario = campo['comment'] if campo['comment'] else ''
                f = QgsField(
                    name    = campo['name'],
                    type    = qtype,
                    len     = length,
                    prec    = prec,
                    comment = comentario
                )
                fields.append(f)
            else:
                # Si no está definido en defCamposCatastroMasivas → añadir como String genérico
                f = QgsField(
                    name    = campoINI,
                    type    = QVariant.String,
                    len     = 255,
                    prec    = 0,
                    comment = ""  # o podrías usar self.dictCatastroFields.get(campoINI, "")
                )
                fields.append(f)

        provider.addAttributes(fields)
        layer.updateFields()


        # ====== PROCESAR REGISTROS ======
        nodo_dsa = raiz.firstChildElement("LDS").firstChildElement("DSA")
        while not nodo_dsa.isNull():
            nodo_bie = nodo_dsa.firstChildElement("LBI").firstChildElement("BIE")
            while not nodo_bie.isNull():
                self.procesar_nodo_bie(nodo_bie, layer, provider)
                nodo_bie = nodo_bie.nextSiblingElement("BIE")
            nodo_dsa = nodo_dsa.nextSiblingElement("DSA")

        QgsProject.instance().addMapLayer(layer)
        QApplication.restoreOverrideCursor() # Se restituye cursor
        
        # Mensaje de EXITO
        print("Tabla del XML cargada con éxito.")
        text = u'Tabla del XML cargada con éxito\n\nFichero:  '+xml_file
        self.fun.showMessage(text,"",tittle=self.nombre_plugin,)


    def obtener_campos(self, nodo):
        """recorre recursivamente y guarda todos los nombres de campos posibles"""
        if not nodo.isNull():
            child = nodo.firstChild()
            while not child.isNull():
                elemento = child.toElement()
                if not elemento.isNull():
                    campo_nombre = elemento.tagName()
                    self.campos.add(campo_nombre)
                    self.obtener_campos(elemento)
                child = child.nextSibling()


    def procesar_nodo_bie(self, nodo_bie, layer, provider):
        """procesa un <BIE>, genera features base y duplicadas si hay repetidos"""
        feature_base = QgsFeature()
        feature_base.setFields(layer.fields())

        # rellenar atributos comunes del BIE
        self.rellenar_atributos(nodo_bie, feature_base, layer)

        # nodos que pueden repetirse
        repetibles = ["SPA", "ELC", "TIT"]
        any_repeats = False

        for rep_tag in repetibles:
            rep_node = nodo_bie.firstChildElement(rep_tag)
            while not rep_node.isNull():
                # clonar la base
                feat = QgsFeature(feature_base)
                feat.setFields(layer.fields())
                feat.setAttributes(feature_base.attributes())

                # sobreescribir con valores específicos de este nodo repetido
                self.rellenar_atributos(rep_node, feat, layer)

                provider.addFeatures([feat])
                any_repeats = True
                rep_node = rep_node.nextSiblingElement(rep_tag)

        # si no había repetidos, añadir la base
        if not any_repeats:
            provider.addFeatures([feature_base])


    def rellenar_atributos(self, nodo, feature, layer):
        """recorre recursivamente un nodo y asigna valores a un feature"""
        child = nodo.firstChild()
        while not child.isNull():
            elemento = child.toElement()
            if not elemento.isNull():
                campo_nombre = elemento.tagName()
                valor = elemento.text().strip() if elemento.text() else ""

                # === DESAMBIGUACIÓN DE CAMPOS ===
                padre = nodo.tagName()

                if campo_nombre == "CPA":
                    if padre == "CPP":   # Bloque de localización rústica
                        campo_nombre = "CPA"
                    else:                # En DEB/FR u otros
                        campo_nombre = "CPA_coef"

                if campo_nombre == "SUP":
                    if padre == "IBI":
                        campo_nombre = "SUP_construida"
                    elif padre == "SPA":
                        campo_nombre = "SUP"

                # Caso especial: RCA -> PCA -> RC14
                if campo_nombre == "PCA" and valor:
                    rc14 = valor[:14]   # solo los 14 primeros
                    if layer.fields().indexOf("RC14") != -1:
                        feature.setAttribute("RC14", rc14)

                        
                # Guardar atributo en el feature si el campo existe
                if layer.fields().indexOf(campo_nombre) != -1 and valor:
                    feature.setAttribute(campo_nombre, valor)

                # continuar recursivamente
                self.rellenar_atributos(elemento, feature, layer)
            child = child.nextSibling()
            

