# -*- coding: utf-8 -*-
####################################################################################
# geomGetlista.py
#
# Obtenemos la Geometría del elemento pinchado de una capa de polígono
#
####################################################################################

from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QApplication, QMessageBox, QDialogButtonBox, QLabel, QTableWidget, QTextEdit, QTableWidgetItem

from qgis.gui import QgsDialog, QgsMapTool
from qgis.core import (QgsProject, QgsWkbTypes, QgsGeometry, QgsPoint, QgsPointXY, QgsLineString,
                        QgsGeometry, QgsWkbTypes)

# from osgeo import gdal, osr, ogr
from osgeo import ogr
import urllib
import json
import os

from math import fabs

from .config import configuration        # CLASE DE CONFIGURACIÓN DE VARIABLES DEL PROGRAMA
from .functions3 import Functions        # CLASE DE CONFIGURACIÓN DE FUNCIONES GENERALES
current_configuration = configuration()

precision= 3 # Precisión de coordenadas y superficies

class geomGetlista(QgsMapTool):

    def __init__(self, canvas, iface, action):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.fun = Functions()
        self.iface = iface
        
        self.nombre_plugin = os.path.basename(os.path.dirname(__file__))

        cursor = QCursor()
        cursor.setShape(Qt.CrossCursor)
        iface.mapCanvas().setCursor(cursor)
        self.setAction(action)
        self.action = action

    def canvasPressEvent(self, event):
        pass

    def canvasMoveEvent(self, event):
        pass


    def canvasReleaseEvent(self, event):
        #Get the click
        x = event.pos().x()
        y = event.pos().y()

        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)

        coordMouse = "{:.{}f}, {:.{}f}".format(point.x(), precision, point.y(), precision)

        layer = self.iface.activeLayer()
        text2=''
        tittle="ERROR"
        if layer is None:
            text = u'Seleccione una capa de Polígonos'
            self.fun.showMessageERR( text,text2,tittle)
            return
        if layer.type() != 0:
            text = u"La capa '"+ layer.name()  + u"' es de tipo "+str(layer.type())+'. NO VECTORIAL\n\n'
            text += u"SELECCIONE UNA CAPA DE POLÍGONOS"
            self.fun.showMessageERR( text,text2,tittle)
            return
        # geomTypeString = QgsWkbTypes.displayString(int(layer.wkbType()))
        geomTypeString = QgsWkbTypes.displayString(layer.wkbType()) # Corregido para v 3.34

        tipos = ['POLYGON','MULTIPOLYGON','POLYGONZ','MULTIPOLYGONZ','POLYGONM','MULTIPOLYGONM','POLYGONZM','MULTIPOLYGONZM','POLYGON25D','MULTIPOLYGON25D']

        if geomTypeString.upper() not in tipos:
            text = u"La capa '"+ layer.name()  + u"' es de tipo " + geomTypeString+u'\n\n'
            text += u"SELECCIONE UNA CAPA DE POLÍGONOS"
            self.fun.showMessageERR( text,text2,tittle)
            return

        fields = layer.fields()
        field_names = [field.name() for field in fields]
        capa = layer.name() + ' -  TIPO: '+ geomTypeString

        feats = [ feat for feat in layer.getFeatures() ]
        geo_pt = QgsGeometry.fromPointXY(QgsPointXY(point.x(), point.y()))
        id = -1

        camposATTRS = []
        listaGeometria =  'SISTEMA DE COORDENADAS: '+self.iface.mapCanvas().mapSettings().destinationCrs().authid() + u'\n'
        QApplication.setOverrideCursor(Qt.WaitCursor)
        for feat in feats:
            if geo_pt.within(feat.geometry()):

                geom = feat.geometry()
                ctra, pkini, pkfin, distEJE, pointMin, pointMax = self.fun.poligToPKINIPKFIN(geom, self.iface,'NO')
                # print ( 'result : ',ctra, pkini, pkfin)

                id = feat.id()

                try:
                    elemId = str(id)+' - '+ field_names[0]+' - '+ str(feat.attribute(field_names[0]))
                except:
                    elemId = str(id)+' - '+ field_names[0]+' - '+ (feat.attribute(field_names[0])).decode('utf-8')

                for campo in field_names:
                    try:
                        valor = str(feat.attribute(campo))
                    except:
                        valor = '--- UNICODE ---'
                    elem  = campo + ':' +valor

                    camposATTRS.append(elem)

                cadena = self.geomGetLista(geom)

                listaGeometria +=  u'Área = {:04.2f} m2'.format(geom.area()) + u'\n'
                # listaGeometria +=  u'Área = {:04.2f} m2'.format(areaTotal) + u'\n'
                listaGeometria +=  u'Perímetro = {:04.2f} m'.format(geom.length()) + u'\n'
                listaGeometria += cadena

                break

        if id == -1:
            QApplication.restoreOverrideCursor()
            text = u"No hay geometría en la posición del cursor"
            self.fun.showMessageERR( text,text2, tittle)
            return

        text=u"DATOS DE POLÍGONO"
        self.showDialog(text,listaGeometria,camposATTRS, coordMouse, capa, elemId, ctra, pkini, pkfin, self.nombre_plugin)


    def showDialog(self, text,listaGeometria,listaDatos, coordMouse, capa, elemId, ctra, pkini, pkfin, tittle="GEOMETRÍA"):
        main_window = self.iface.mainWindow()
        dialog = QgsDialog(main_window,
                           fl=Qt.WindowFlags(),
                           buttons=QDialogButtonBox.NoButton,
                           orientation=Qt.Vertical)
        dialog.setWindowTitle("LISTADO DE COORDENADAS DE POLÍGONO")
        dialog.setWindowIcon(QIcon(f":/plugins/{self.nombre_plugin}/iconos/cat_listPoligon.jpg"))
        dialog.resize(530, 420)

        # Etiquetas
        labelCoordPinch = QLabel(dialog)
        labelCoordPinch.setGeometry(QRect(5, 5, 510, 20))
        labelCoordPinch.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        labelCoordPinch.setText("COORDENADAS CURSOR: " + coordMouse)
        labelCoordPinch.setTextInteractionFlags(Qt.TextSelectableByMouse)
        labelCapa = QLabel(dialog)
        labelCapa.setGeometry(QRect(5, 25, 510, 20))
        labelCapa.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        labelCapa.setText("CAPA: " + capa)
        labelCapa.setTextInteractionFlags(Qt.TextSelectableByMouse)
        labelElemento = QLabel(dialog)
        labelElemento.setGeometry(QRect(5, 45, 510, 20))
        labelElemento.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        labelElemento.setText("ELEMENTO: " + elemId)
        labelElemento.setTextInteractionFlags(Qt.TextSelectableByMouse)
        labelCtraPks = QLabel(dialog)
        labelCtraPks.setGeometry(QRect(230, 45, 510, 20))
        labelCtraPks.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        labelCtraPks.setTextInteractionFlags(Qt.TextSelectableByMouse)
        if ctra == None:
            labelCtraPks.setText(' --- ')
        else:
            if pkini == 'Ctra sin PK' or  pkfin == 'Ctra sin PK':
                labelCtraPks.setText('Ctra: {}  PKINI: {}  PKFIN: {}'.format(ctra, 'Ctra sin PK', 'Ctra sin PK'))
            else:
                labelCtraPks.setText('Ctra: {}  PKINI: {:.3f}  PKFIN: {:.3f}'.format(ctra, pkini, pkfin))


        # Tabla de atributos
        tableWidget = QTableWidget(dialog)
        tableWidget.setGeometry(QRect(5, 65, 270, 340))
        tableWidget.setObjectName("tableWidget")
        tableWidget.setColumnCount(2)
        tableWidget.setRowCount(len(listaDatos))
        tableWidget.setColumnWidth( 0, 100)
        tableWidget.setColumnWidth( 1, 300)
        tableWidget.setHorizontalHeaderLabels (['CAMPO      ', 'VALOR ATRIBUTO    '])
        j=0
        for data in listaDatos:
            dataDescomp = data.split(':')
            tableWidget.setItem(j, 0,  QTableWidgetItem(dataDescomp[0]))
            tableWidget.setItem(j, 1, QTableWidgetItem(dataDescomp[1]))
            j+=1

        # Listado de Coordenadas
        textEdit = QTextEdit(dialog)
        textEdit.setGeometry(QRect(280, 65, 245, 340))
        textEdit.setObjectName("textEdit")
        textEdit.setText(listaGeometria)

        QApplication.restoreOverrideCursor()
        dialog.show()


    def geomGetLista(self, geometry):
        cadena =''
        # areaTotal = 0

        # Verificar si la geometría es un polígono o multipolígono y obtener todas las partes de la geometría (puede incluir anillos)
        if geometry.wkbType() in [QgsWkbTypes.Polygon, QgsWkbTypes.MultiPolygon]:
            partes = []
            if geometry.wkbType() == QgsWkbTypes.Polygon:
                tipo = "Polígono"
                # Obtener todas las partes de la geometría (puede incluir anillos)
                partes.append(geometry.asPolygon())
            else:
                tipo = "Multipolígono"
                partes.extend(geometry.asMultiPolygon())
            cadena +=f"Tipo de geometría: {tipo} ({len(partes)})"

            # Iterar sobre cada parte de la geometría
            for idx, parte in enumerate(partes):
                area = QgsGeometry.fromPolygonXY(parte).area()
                cadena += "\n\n  Área de la parte {}: {:.{}f} m2".format(idx + 1, area, precision)
                # areaTotal += area

                # Imprimir los puntos de cada parte exterior
                for i, punto in enumerate(parte[0]):
                    cadena += "\n   {}: {:.{}f} - {:.{}f}".format(i+1, punto.x(), precision, punto.y(), precision)

                # Verificar si hay anillos interiores (agujeros)
                if len(parte) > 1:
                    anillos_interiores = parte[1:]  # Excluir la parte exterior
                    for idx_interno, anillo in enumerate(anillos_interiores):
                        area_anillo = QgsGeometry.fromPolygonXY([anillo]).area()
                        cadena += "\n    Área del anillo {}/{}: {:.{}f} m2".format(idx + 1, idx_interno + 1, area_anillo, precision)
                        # areaTotal -= area_anillo

                        # Imprimir los puntos del anillo
                        for i, punto in enumerate(anillo):
                            cadena += "\n     {}: {:.{}f} - {:.{}f}".format(i+1, punto.x(), precision, punto.y(), precision)

        else:
            cadena += "La geometría no es un polígono ni un multipolígono"

        return cadena

    '''
    def geomGetLista0(self, geomWKT, single):
        # CALCULO DE AREAS Y GEOMETRÍA PERO DEVUELVE EL AREA DEL CONJUNTO DE POLÍGONOS
        print (geomWKT , type(geomWKT))
        cadena =''
        for parte in geomWKT:
            cadena += u'Polígono '+str(geomWKT.index(parte)+1)+'\n'
            i=1
            if single:
                for pto in parte:
                    cadena += " ".join([str(i),' - ',"{:.{}f}".format(pto[0], precision),' - ',"{:.{}f}".format(pto[1], precision),'\n'])
                    i += 1
            else:
                for pto in parte[0]:
                    cadena += " ".join([str(i),' - ',"{:.{}f}".format(pto[0], precision),' - ',"{:.{}f}".format(pto[1], precision),'\n'])
                    i += 1
        return cadena


    def geomGetLista1(self, geomWKT, geom, single):
        # CALCULO DE AREAS Y GEOMETRÍA PERO DEVUELVE EL AREA DEL CONJUNTO DE POLÍGONOS
        print ('geomWKT - ', geomWKT, type(geomWKT))
        print ('geom - ', geom, type(geom))
        cadena =''
        for parte in geomWKT:
            cadena += u'Polígono '+str(geomWKT.index(parte)+1)+'\n'
            i=1
            if single:
                for pto in parte:
                    cadena += " ".join([str(i),' - ',"{:.{}f}".format(pto[0], precision),' - ',"{:.{}f}".format(pto[1], precision),'\n'])
                    i += 1
            else:
                for pto in parte[0]:
                    cadena += " ".join([str(i),' - ',"{:.{}f}".format(pto[0], precision),' - ',"{:.{}f}".format(pto[1], precision),'\n'])
                    i += 1
        return cadena


    def geomGetLista2(self, geom):
        cadena =''

        # Verificar si la geometría es un polígono o multipolígono
        print ('TIPO DE GEOM:  ', geom.type())
        # if geom.type() in [QgsWkbTypes.Polygon, QgsWkbTypes.MultiPolygon]:
        if geom.type() == 2:

            # Imprimir el tipo de geometría
            tipo = "Multipolígono" if geom.isMultipart() else "Polígono"
            print(f"Tipo de geometría: {tipo}")
            cadena += f"Tipo de geometría: {tipo}"

            # Obtener el área del polígono o multipolígono
            areas = []
            if tipo == "Polígono":
                areas.append(geom.area())
            else:
                for poligono in geom.asMultiPolygon():
                    areas.append(QgsGeometry.fromPolygonXY(poligono).area())

            # Imprimir las áreas de cada parte
            print("Áreas de cada parte:")
            for idx, area in enumerate(areas):
                print(f"POLIGONO {idx + 1}: {area}")
                cadena += f"POLIGONO {idx + 1}: {area}"

            # Obtener todos los puntos que conforman el polígono o multipolígono
            puntos_poligono = []
            if tipo == "Polígono":
                try:
                    puntos_poligono = [p for p in geom.asPolygon()]
                except:
                    puntos_poligono = [p for p in geom.asMultiPolygon()]

            else:
                for poligono in geom.asMultiPolygon():
                    puntos_poligono.extend([p for p in poligono])

            # Imprimir los puntos del polígono o multipolígono
            print("Puntos del polígono/multipolígono:")
            i = 1
            for punto in puntos_poligono:
                print('Punto - ', i, punto)
                # cadena += " ".join([str(i),' - ',"{:.{}f}".format(punto[0], precision),' - ',"{:.{}f}".format(punto[1], precision),'\n'])
                # cadena += " ".join([str(i),' - ',"{:.{}f}".format(punto[0], precision),' - ',"{:.{}f}".format(punto[1], precision),'\n'])
                cadena += " {} - {:.{}f} - {:.{}f}".format(i, punto[0], punto[1])
                i += 1

        else:
            print("La geometría no es un polígono ni un multipolígono")
            cadena += "\n\nLa geometría no es un polígono ni un multipolígono"

        return cadena


    def geomGetLista(self, geometry):
        cadena =''

        # Verificar si la geometría es un polígono o multipolígono
        if geometry.wkbType() in [QgsWkbTypes.Polygon, QgsWkbTypes.MultiPolygon]:
            partes = []
            if geometry.wkbType() == QgsWkbTypes.Polygon:
                tipo = "Polígono"
                # Obtener todas las partes de la geometría (puede incluir anillos)
                partes.append(geometry.asPolygon())
            else:
                tipo = "Multipolígono"
                partes.extend(geometry.asMultiPolygon())
            # print(f"Tipo de geometría: {tipo}")
            cadena +=f"Tipo de geometría: {tipo} ({len(partes)})"

            # Iterar sobre cada parte de la geometría
            for idx, parte in enumerate(partes):
                area = QgsGeometry.fromPolygonXY(parte).area()
                # print(f"Área de la parte {idx + 1}: {area}")
                cadena += "\n\n  Área de la parte {} - {:.{}f} m2".format(idx + 1, area, precision)
                # print ("Parte - ",idx, parte)

                # Imprimir los puntos de cada parte exterior
                print(f"\nPuntos de la parte {idx + 1}:")
                for i, punto in enumerate(parte[0]):
                    # print(punto)
                    cadena += "\n   {} - {:.{}f} - {:.{}f}".format(i+1, punto.x(), precision, punto.y(), precision)


                # Verificar si hay anillos interiores (agujeros)
                if len(parte) > 1:
                    anillos_interiores = parte[1:]  # Excluir la parte exterior
                    for idx_interno, anillo in enumerate(anillos_interiores):
                        area_anillo = QgsGeometry.fromPolygonXY([anillo]).area()
                        # print("\n\n    Área del anillo {} - {:.{}f} m2".format(idx_interno + 1, area_anillo, precision))
                        cadena += "\n    Área del anillo {}/{} - {:.{}f} m2".format(idx + 1, idx_interno + 1, area_anillo, precision)

                        # Imprimir los puntos del anillo
                        for i, punto in enumerate(anillo):
                            # print(punto)
                            cadena += "\n     {} - {:.{}f} - {:.{}f}".format(i+1, punto.x(), precision, punto.y(), precision)

        else:
            # print("La geometría no es un polígono ni un multipolígono")
            cadena += "La geometría no es un polígono ni un multipolígono"

        return cadena
    '''

    # TROZOS ANTERIORES A BORRAR
    '''
    def geomGetLista01(self, geomWKT, single):
        # CALCULO DE AREAS Y GEOMETRÍA, DEVUELVE EL AREA DE CADA PARTE DEL POLÍGONOS
        print (geomWKT , type(geomWKT))
        cadena =''
        if single:
            for parte in geomWKT:
                for pto in parte:
                    cadena += " ".join([str(i),' - ',"{:.{}f}".format(pto[0], precision),' - ',"{:.{}f}".format(pto[1], precision),'\n'])
                    i += 1
        else:
            # geometria = QgsGeometry.fromWkt(geomWKT)
            partes = geomWKT.asMultiPolygon()
            for idx, parteWkt in enumerate(psrtes):
                area = QgsGeometry.fromPolygonXY(parteWkt).area()
                cadena += u' - AREA '+str(area)+'\n'
                for anillo in parteWkt:
                    i = 0
                    for pto in anillo:
                        cadena += " ".join([str(i),' - ',"{:.{}f}".format(pto[0], precision),' - ',"{:.{}f}".format(pto[1], precision),'\n'])
                        i += 1

        return cadena



    def geomGetLista1(self, geomWKT, single):
        cadena = ''
        geometria = QgsGeometry.fromWkt(geomWKT)
        if single:
            for pto in geomWKT:
                cadena += " ".join([str(i),' - ',"{:.{}f}".format(pto[0], precision),' - ',"{:.{}f}".format(pto[1], precision),'\n'])
                i += 1
        else:
            for idx, parteWkt in enumerate(partes):

            partes = geometria.asMultiPolygon()

        return cadena


        for idx, parteWkt in enumerate(psrtes):
            #geometria = QgsGeometry.fromWkt(parteWkt)

            cadena += u'Polígono '+str(idx+1)+'\n'
            cadena += u' - AREA '+str(geometria.area())+'\n'
            i=1
            if single:
                for pto in parteWkt:
                    cadena += " ".join([str(i),' - ',"{:.{}f}".format(pto[0], precision),' - ',"{:.{}f}".format(pto[1], precision),'\n'])
                    i += 1
            else:
                for pto in parteWkt[0]:
                    cadena += " ".join([str(i),' - ',"{:.{}f}".format(pto[0], precision),' - ',"{:.{}f}".format(pto[1], precision),'\n'])
                    i += 1
        return cadena
        '''
