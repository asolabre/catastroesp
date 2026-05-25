#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
/***************************************************************************
Name:           config.py

                                 A QGIS plugin
Plugin:     catastroesp.py
Purpose:    Tools for plugin catastroesp. Configuration file
        --------------------------------------------------------------------
        begin                : 2016-06-07
        git sha              : $Format:%H$
        Codigo Corregido     : Agustín Solabre
        email                : agusass@hotmail.com
 ***************************************************************************/
'''

class configuration:
  general = {
    'EPSG': 25830,
    '01Ambito':         u'ESPAÑA PENINSULAR',
    'wfs_carreteras':   u'https://geoservicios.castillalamancha.es/arcgis/services/WFS/Plan_Carreteras_BTA_WFS/MapServer/WFSServer?',
    'wfs_carreteras_layer': u'GEO_BTAcalibrada',
    'rest_carreteras':  u'https://geoservicios.castillalamancha.es/arcgis/rest/services/WFS/Plan_Carreteras_BTA_WFS/MapServer/0/query?',
    'rest_Pks':         u'https://geoservicios.castillalamancha.es/arcgis/rest/services/WFS/Plan_Carreteras_PKS_WFS/MapServer/0/query?',
    'rest_poblaciones': u'https://geoservicios.castillalamancha.es/arcgis/rest/services/WFS/Plan_Carreteras_Poblaciones_Municipios_WFS/MapServer/0/query?',
    'campo_poblacion': u'Nucleo',
    'rest_municipios':  u'https://geoservicios.castillalamancha.es/arcgis/rest/services/WFS/Plan_Carreteras_Poblaciones_Municipios_WFS/MapServer/1/query?',
    # 'municipio_text_field': u'Nucleo',
    'carpeta_estilos':  u'./ESTILOS CAPAS',
    'fich_config_capas':u'u:/cartografia/datos_Q/QSIG/config/capasQSIG.txt',
    'urlWMSmdt':        u'https://servicios.idee.es/wms-inspire/mdt?',
    # 'urlWMSmdt':        u'https://servicios.idee.es/wmts/mdt?',
    'urlWMSmdtLayer':   u'EL.ElevationGridCoverage',
    # 'urlWMSmdtLayer':   u'EL.GridCoverage',
    'urlWMSmdtValor':   u'mdt:GRAY_INDEX'

    }

  lrs = {
    'tipo_consultaCAPA' : 'url',
    'ruta_geopackage'   : u'\\\\JCLM.ES\APLI\\CARRETERAS_SIG\\cartografia\\datos_Q\\SIG_REGIONAL_CARRETERAS.gpkg',
    'nombre_capa_ctras' : u'GEO_BTAcalibrada',
    'nombre_capa_munis' : u'GEO_Municipios_Zona',
    'nombre_capa_pobla' : u'GEO_NucleosPoblacion',

    'OriFichGpkgCTRAS'  : u'\\\\JCLM.ES\APLI\\CARRETERAS_SIG\\cartografia\\datos_Q\\SIG_REGIONAL_CARRETERAS.gpkg',
    'DestFichGpkgCTRAS' : u'c:\\cartografia\\datos_Q',

    'identificador_carretera_carreteras': u'Matricula',
    'default_log_folder': u'C:/TEMP/',
    'bal_dest_path': u'C:/TEMP/',
    'bal_nom_layer': u'BALIZAS DE CARRETERA',
    'bal_estiloCAPA': u'./ESTILOS CAPAS/BALIZAS DE CARRETERA.qml'
    }

  catastro_tool ={
    'url_catastro_distancia': u'http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCoordenadas.asmx/Consulta_RCCOOR_Distancia?',
    'url_catastro_rc':        u'http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCoordenadas.asmx/Consulta_CPMRC?',
    'url_catastro_RCCOOR':    u'http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCoordenadas.asmx/Consulta_RCCOOR?',
    'url_catastro_Provincia': u'http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/ConsultaProvincia?',
    'url_catastro_municipio': u'http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/ConsultaMunicipio?',
    'url_catastro_DNPRC':     u'http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/Consulta_DNPRC?',
    'url_catastro_DNPPP':     u'http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/Consulta_DNPPP?',
    'url_catastro_DescGML':   u'http://ovc.catastro.meh.es/INSPIRE/wfsCP.aspx?',

    'cat_dir_shps': u'//jclm.es/otvu/sc/DAT_CARTOGRAFIA/03_CARTOGRAFIA_ORIGINAL_OFICIAL/DG_CATASTRO/CATASTRO_',
    'cat_year': 2016,
    'dir_estilos_catastro': u'./ESTILOS CAPAS/',
    'cat_pos_toc': 0,

    'capas_urbanas' : [
        { 'capa' : u'CONSTRU.shp' , 'nombre' : u'U-Cons-' , 'estilo' : u'CAT_U_CONSTRU.qml' },
        { 'capa' : u'PARCELA.shp' , 'nombre' : u'U-Par-' , 'estilo' : u'CAT_U_PARCELA.qml' },
        { 'capa' : u'MASA.shp' , 'nombre' : u'U-Pol-' , 'estilo' : u'CAT_U_POLIGONO.qml' }
        ],
        'capas_rusticas' : [
        { 'capa' : u'SUBPARCE.shp' , 'nombre' : u'R-Sub-' , 'estilo' : u'CAT_R_SUBPARCE.qml' },
        { 'capa' : u'MASA.shp' , 'nombre' : u'R-Pol-' , 'estilo' : u'CAT_R_POLIGONO.qml' },
        { 'capa' : u'PARCELA.shp' , 'nombre' : u'R-Par-' , 'estilo' : u'CAT_R_PARCELA.qml' }
        ]
    }


  INVENTARIO = {
    'Data_CM':  # Datos CASTILLA LA MANCHA
        {'INV_OBFAtipo_CM'   : ['Grupo', 'TODAS'],
         'INV_OBFAsource_CM' : u'U:/INVENTARIO/OBRAS_FABRICA/CM/OF_CM.qlr',
         'INV_OBFAestilo_CM' : u'defecto',
         'INV_OBFAnombre_CM' : u'defecto',
         'INV_SEVEtipo_CM'   : ['GPKG', 'CTRAS'],
         'INV_SEVEsource_CM' : u'U:/INVENTARIO/SENALIZACION_VERT/CM/SV_CM.gpkg|layername=SV_CM',
         'INV_SEVEestilo_CM' : u'U:/INVENTARIO/OBRAS_FABRICA/CM/SV_CM.qml',
         'INV_SEVEnombre_CM' : u'SV_CM',
         },
    'Data_AB':  # Datos ALBACETE
        {'INV_OBFAtipo_AB'  : ['GPKG', 'TODAS'],
         'INV_OBFAsource_AB': u'U:\INVENTARIO\OBRAS_FABRICA\AB\OF_Albacete.gpkg|layername=OF_Albacete',
         'INV_OBFAestilo_AB' : u'defecto',
         'INV_OBFAnombre_AB' : u'OF_Albacete',
         'INV_SEVEtipo_AB'  : ['GPKG', 'CTRAS'],
         'INV_SEVEsource_AB': u'U:/INVENTARIO/SENALIZACION_VERT/AB/SV_Albacete.gpkg|layername=SV_Albacete',
         'INV_SEVEestilo_AB' : u'U:/INVENTARIO/OBRAS_FABRICA/AB/SV_Albacete.qml',
         'INV_SEVEnombre_AB' : u'SV_Albacete',
         }

    }


  data_internos = {
    'UD_SIGFOMSC': u'U:',
    'DIR_SIGFOMSC': u'//JCLM.ES/INFR/CARRETERAS_SIG',
    'UD_SIGFOMLO': u'Z:',
    'DIR_SIGFOMLO': u'//jclm.es/INFR/AB/SIG_FOMENTO_AB',
    'UD_SIGCTRLO': u'V:',
    'DIR_SIGCTRLO': u'//JCLM.ES/INFR/AB/SIG_CTRAS_AB',
    'UD_CARTOGSC': u'W:',
    'DIR_CARTOGSC': u'//jclm.es/otvu/sc/DAT_CARTOGRAFIA',
    'DIR_GRUPEXPRO': u'u:/cartografia/datos_Q/Qsig/GRUPOS_CAPAS/',
    'FICH_GRUPEXPRO': u'012 EXPRO PATRIMONIO - CASILLAS_EDIT.qlr',
    'NOM_GRUPEXPRO': u'EXPROPIACIONES B.INMU EDIT',
    'GDB_Geometrias': u'u:/SIGCLM/APPJCCM/Datos/sig_reg_ctras.gdb',
    'GDB_Aforos': u'u:/SIGCLM/APPJCCM/Datos/sig_reg_ctras.gdb'
    }

  ####################################
  ### ESTO LO DEBEMOS QUITAR
  ####################################
  ficherosCopySeg = {
    u'v:/cartografia/datos/EXPROPIACIONES/02_ALBACETE/00_EXPROPIACIONES COMPLETAS/EXPROPIACIONES_COMPLETAS_AB.gpkg',
    # u'x:/cartografia/datos/EXPROPIACIONES/02_ALBACETE/00_EXPROPIACIONES COMPLETAS/EXPROPIACIONES_COMPLETAS_ALBACETE.shp',
    # u'z:/cartografia/datos/EXPROPIACIONES/02_ALBACETE/00_EXPROPIACIONES COMPLETAS/INFORMES EXPROPIACIONES.shp',
    # u'z:/cartografia/datos/EXPROPIACIONES/02_ALBACETE/00_EXPROPIACIONES COMPLETAS/EXPROPIACIONES_PARCELAS_ALBACETE.shp'
    }
  dstDirCopySeg = u'v:/cartografia/datos/EXPROPIACIONES/02_ALBACETE/00_EXPROPIACIONES COMPLETAS/COPIA_SEGURIDAD/'
  extListCopySeg = {'.gpkg', '.shp', '.shx', '.dbf'}


  ficherosCopyLocal = [
    {'origen': u'c:/cartografia/datos/EXPROPIACIONES/02_ALBACETE/00_EXPROPIACIONES COMPLETAS/EXPROPIACIONES_COMPLETAS_AB.gpkg',
    'destino': u'd:/Users/agusa/OneDrive - JCCM/cartografia/datos/EXPROPIACIONES/02_ALBACETE/00_EXPROPIACIONES COMPLETAS/EXPROPIACIONES_COMPLETAS_AB.gpkg'}
    ]



  ####################################
  ### ESTO LO DEBEMOS QUITAR
  ####################################

  expropiacion = {
    'EXPprovincia'              : 'ALBACETE - AB',
    'EXPlayerLIMEXPRO'          : 'LIMITES DE EXPROPIACION AB',
    'EXPlayerLIMEXPROFich'      : 'v:/cartografia/datos/EXPROPIACIONES/02_ALBACETE/00_EXPROPIACIONES COMPLETAS/EXPROPIACIONES_COMPLETAS_ALBACETE.shp',
    'EXPlayerLIMEXPROexptes'    : 'v:/cartografia/datos/EXPROPIACIONES/02_ALBACETE/',
    'EXPlayerINFOEXPRO'         : 'Informes de Expropiaciones',
    'EXPlayerINFOEXPROFich'     : 'v:/cartografia/datos/EXPROPIACIONES/02_ALBACETE/00_EXPROPIACIONES COMPLETAS/INFORMES EXPROPIACIONES.shp',
    'EXPlayerINFOEXPROexptes'   : 'P:/Documentacion/Expropiaciones/',
    'EXPlayerParcPATRI'         : 'CASILLAS P.C. ETRS89',
    'EXPlayerParcPATRIFich'     : 'v:/cartografia/datos/Casillas_PC_OFICINAS_DESTACAMENTOS_ALMACENES/casillas_pc_area_ETRS89.shp',
    'EXPlayerParcPATRIexptes'   : 'v:/cartografia/datos/Casillas_PC_OFICINAS_DESTACAMENTOS_ALMACENES/',
    'EXP_GRUPEXPROfich'         : u'v:/cartografia/datos_Q/Qsig/GRUPOS_CAPAS/012 EXPRO PATRIMONIO - CASILLAS_EDIT.qlr',
    'EXP_GRUPEXPROnom'          : u'EXPROPIACIONES B.INMU EDIT',
    'dstDirCopySeg'             : u'v:/cartografia/datos/EXPROPIACIONES/02_ALBACETE/00_EXPROPIACIONES COMPLETAS/COPIA_SEGURIDAD/',
    'extListCopySeg'            : {'.gpkg', '.shp', '.shx', '.dbf'},

    'ficherosCopySeg'           : {
        u'v:/cartografia/datos/EXPROPIACIONES/02_ALBACETE/00_EXPROPIACIONES COMPLETAS/EXPROPIACIONES_COMPLETAS_AB.gpkg'
        # u'v:/cartografia/datos/EXPROPIACIONES/02_ALBACETE/00_EXPROPIACIONES COMPLETAS/EXPROPIACIONES_COMPLETAS_ALBACETE.shp',
        # u'v:/cartografia/datos/EXPROPIACIONES/02_ALBACETE/00_EXPROPIACIONES COMPLETAS/INFORMES EXPROPIACIONES.shp',
        # u'v:/cartografia/datos/EXPROPIACIONES/02_ALBACETE/00_EXPROPIACIONES COMPLETAS/EXPROPIACIONES_PARCELAS_ALBACETE.shp'
        }
    }

  expropiacionB = {
    'EXPprovincia'              : 'ALBACETE - AB',
    'EXPlayerLIMEXPRO'          : u'LIMITES DE EXPROPIACION AB',
    'EXPlayerLIMEXPROFich'      : u'v:/cartografia/datos/EXPROPIACIONES/00_EXPROPIACIONES COMPLETAS/EXPROPIACIONES_COMPLETAS_AB.gpkg',
    'EXPlayerLIMEXPROexptes'    : u'v:/cartografia/datos/EXPROPIACIONES/02_ALBACETE/',
    'EXPlayerINFOEXPRO'         : u'Informes de Expropiaciones',
    'EXPlayerINFOEXPROFich'     : u'v:/cartografia/datos/EXPROPIACIONES/00_EXPROPIACIONES COMPLETAS/EXPROPIACIONES_COMPLETAS_AB.gpkg',
    'EXPlayerINFOEXPROexptes'   : u'P:/Documentacion/Expropiaciones/',
    'EXPlayerParcPATRI'         : u'CASILLAS P.C. ETRS89',
    'EXPlayerParcPATRIFich'     : u'v:/cartografia/datos/Casillas_PC_OFICINAS_DESTACAMENTOS_ALMACENES/casillas_pc_area_ETRS89.shp',
    'EXPlayerParcPATRIexptes'   : u'v:/cartografia/datos/Casillas_PC_OFICINAS_DESTACAMENTOS_ALMACENES/',
    'EXP_GRUPEXPROfich'         : u'v:/cartografia/datos_Q/Qsig/GRUPOS_CAPAS/012 EXPRO PATRIMONIO - CASILLAS.qlr',
    'EXP_GRUPEXPROnom'          : u'EXPROPIACIONES B.INMU',
    'dstDirCopySeg'             : u'v:/cartografia/datos/EXPROPIACIONES/02_ALBACETE/00_EXPROPIACIONES COMPLETAS/COPIA_SEGURIDAD/',
    'extListCopySeg'            : {'.gpkg', '.shp', '.shx', '.dbf'},

    'ficherosCopySeg'           : {
        u'v:/cartografia/datos/EXPROPIACIONES/02_ALBACETE/00_EXPROPIACIONES COMPLETAS/EXPROPIACIONES_COMPLETAS_AB.gpkg'
        # u'v:/cartografia/datos/EXPROPIACIONES/02_ALBACETE/00_EXPROPIACIONES COMPLETAS/EXPROPIACIONES_COMPLETAS_ALBACETE.shp',
        # u'v:/cartografia/datos/EXPROPIACIONES/02_ALBACETE/00_EXPROPIACIONES COMPLETAS/INFORMES EXPROPIACIONES.shp',
        # u'v:/cartografia/datos/EXPROPIACIONES/02_ALBACETE/00_EXPROPIACIONES COMPLETAS/EXPROPIACIONES_PARCELAS_ALBACETE.shp'
        }
    }

  listTIPOEXPTE = [
        'INVASION',
        'INVASION AEE',
        'BIENES PATRIMONIALES',
        'NO INVASION',
        'NO INVASION, URBANO',
        'NO COLIND CTRA JCCM',
        'REMISION CATASTRAL',
        'ACLAR RECT.CATASTRAL',
        'PERMUTA',
        'REVERSION',
        'SIN CLASIFICAR'
        ]

  listMARGEN = [
        'Ambas',
        'Izquierda',
        'Derecha'
        ]
        
  listCORREOELEC = [
        ]


  listINTERESADO  = [
        'REGISTRO DE LA PROPIEDAD DE ALBACETE 1',
        'REGISTRO DE LA PROPIEDAD DE ALBACETE 2',
        'REGISTRO DE LA PROPIEDAD DE ALBACETE 3',
        'REGISTRO DE LA PROPIEDAD DE ALBACETE 4',
        'REGISTRO DE LA PROPIEDAD DE ALMANSA',
        'REGISTRO DE LA PROPIEDAD DE ALCARAZ',
        'REGISTRO DE LA PROPIEDAD DE LA RODA',
        'REGISTRO DE LA PROPIEDAD DE CHINCHILLA DE MONTE-ARAGÓN',
        'REGISTRO DE LA PROPIEDAD DE VILLARROBLEDO',
        'REGISTRO DE LA PROPIEDAD DE CASAS-IBÁÑEZ',
        'REGISTRO DE LA PROPIEDAD DE HELLÍN',
        'REGISTRO DE LA PROPIEDAD DE YESTE',
        'GERENCIA PROVINCIAL DE CATASTRO',
        'SECCIÓN DE CONTRATACIÓN EXPROPIACIÓN Y ASUNTOS JURÍDICOS'
        ]

  custom_configuration = ""

  # DEFINICIÓN DE CAMPOS DE CAPAS DE CATASTRO CARGADAS
  defCamposCatastro = [
      {'name': "RC14",      'type': 'String', 'len': 20,  'prec': 0, 'comment': 'RC14.- Referencia Catastral 14 digitos'},
      {'name': "NOM_MUNI",  'type': 'String', 'len': 255, 'prec': 0, 'comment': 'NOM_MUNI.- Nombre literal del Municipio'},
      {'name': "DELEGACIO", 'type': 'Int',    'len': 0,   'prec': 0, 'comment': 'DELEGACIO.- Cod. Catastral Provincia'},
      {'name': "MUNICIPIO", 'type': 'Int',    'len': 0,   'prec': 0, 'comment': 'MUNICIPIO.- Cod. Catastral Municipio'},
      {'name': "MASA",      'type': 'String', 'len': 10,  'prec': 0, 'comment': 'MASA.- Número poligono'},
      {'name': "PARCELA",   'type': 'String', 'len': 10,  'prec': 0, 'comment': 'PARCELA.- Número parcela'},
      {'name': "TIPO",      'type': 'String', 'len': 10,  'prec': 0, 'comment': 'TIPO.- urbano (UR) o rústico (RU)'},
      {'name': "AREA",      'type': 'Double', 'len': 10,  'prec': 2, 'comment': 'AREA.- Superficie de la parcela'},
      {'name': "CAT_NMSPC", 'type': 'String', 'len': 50,  'prec': 0, 'comment': 'CAT_NMSPC.- (ES.SDGC.CP) o (ES.LOCAL.CP)'},
      {'name': "PCAT1",     'type': 'String', 'len': 7,   'prec': 0, 'comment': 'PCAT1.- 7 Dígitos iniciales de la RC14'},
      {'name': "PCAT2",     'type': 'String', 'len': 7,   'prec': 0, 'comment': 'PCAT2.- 7 Dígitos finales de la RC14'},
      {'name': "PARAJE",    'type': 'String', 'len': 255, 'prec': 0, 'comment': 'PARAJE.- Texto del Paraje'},
      {'name': "EJERCICIO", 'type': 'Int',    'len': 0,   'prec': 0, 'comment': 'EJERCICIO.- '},
      {'name': "NUM_EXP",   'type': 'Int',    'len': 0,   'prec': 0, 'comment': 'NUM_EXP.- '},
      {'name': "CONTROL",   'type': 'Int',    'len': 0,   'prec': 0, 'comment': 'CONTROL.- '},
      {'name': "VIA",       'type': 'String', 'len': 255, 'prec': 0, 'comment': 'VIA.- Código de vial'},
      {'name': "NUMERO",    'type': 'Int',    'len': 0,   'prec': 0, 'comment': 'NUMERO.- Número de policía'},
      {'name': "NUMERODUP", 'type': 'String', 'len': 50,  'prec': 0, 'comment': 'NUMERODUP.- '},
      {'name': "NUMSYMBOL", 'type': 'Int',    'len': 0,   'prec': 0, 'comment': 'NUMSYMBOL.- '},
      {'name': "FECHAALTA", 'type': 'String', 'len': 25,  'prec': 0, 'comment': 'FECHAALTA.- '},
      {'name': "FECHABAJA", 'type': 'String', 'len': 25,  'prec': 0, 'comment': 'FECHABAJA.- '},
      {'name': "MAPA",      'type': 'String', 'len': 25,  'prec': 0, 'comment': 'MAPA.- '},
      {'name': "HOJA",      'type': 'String', 'len': 25,  'prec': 0, 'comment': 'HOJA.- '},
      {'name': "COORX",     'type': 'Double', 'len': 10,  'prec': 2, 'comment': 'COORX.- X centroide parcela'},
      {'name': "COORY",     'type': 'Double', 'len': 10,  'prec': 2, 'comment': 'COORY.- Y centroide parcela'},
      {'name': "DIRECCION", 'type': 'String', 'len': 255, 'prec': 0, 'comment': 'DIRECCION.- Dirección de la Parcela'},
      {'name': "PROVINCIA", 'type': 'String', 'len': 50,  'prec': 0, 'comment': 'PROVINCIA.- Provincia'},
      {'name': "REF_CAT",   'type': 'String', 'len': 25,  'prec': 0, 'comment': 'REF_CAT.- Referencia Catastral 20 dig.'},
      {'name': "COD_INE",   'type': 'String', 'len': 10,  'prec': 0, 'comment': 'COD_INE.- Código INI Municipio.'}
      ]


  # DEFINICIÓN DE CAMPOS DE CAPAS DE CATASTRO DE CONSULTA MASIVA

  defCamposCatastroMasivas = [
        # Campo calculado
        { 'name': "RC14",  'type': 'String', 'len': 255, 'prec': 0, 'comment': "Referencia Catastral de 14 dígitos (primeros 14 caracteres de PCA)"},
        { 'name': "CAT_NMSPC",'type':'String','len': 50, 'prec': 0, 'comment': 'CAT_NMSPC.- (ES.SDGC.CP) o (ES.LOCAL.CP)'},

        # Raíz y metadatos de salida
        { 'name': "DS",    'type': 'String', 'len': 255, 'prec': 0, 'comment': "Documento de salida de la consulta masiva"},
        { 'name': "LAT",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Lista de ámbitos territoriales"},
        { 'name': "ATE",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Ámbito territorial según privilegios del usuario"},
        { 'name': "LDS",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Lista de datos de salida"},
        { 'name': "DSA",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Datos de salida (bloque por dato de entrada)"},
        { 'name': "ERR",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Bloque de error en los datos de entrada"},
        { 'name': "COD",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Código del error (dato de entrada)"},
        { 'name': "DES",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Descripción del error (dato de entrada)"},

        # Datos de entrada reflejados en la salida
        { 'name': "NIF",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Dato de entrada: NIF/CIF (también se usa dentro de titulares)"},
        { 'name': "APE",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Dato de entrada: Apellidos y Nombre"},
        { 'name': "RC",    'type': 'String', 'len': 255, 'prec': 0, 'comment': "Dato de entrada: Referencia Catastral"},
        { 'name': "PROV",  'type': 'String', 'len': 255, 'prec': 0, 'comment': "Dato de entrada: provincia"},
        { 'name': "MUN",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Dato de entrada: municipio / (en IBI) Código de municipio según MEH"},
        { 'name': "POL",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Dato de entrada: polígono"},
        { 'name': "PAR",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Dato de entrada: parcela"},

        # Lista de bienes
        { 'name': "LBI",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Lista de Bienes"},
        { 'name': "BIE",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Bien inmueble (registro individual)"},

        # Identificación del bien (IBI)
        { 'name': "IBI",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Identificación del Bien Inmueble"},
        { 'name': "DEL",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Código de Delegación del MEH (Hacienda)"},
        { 'name': "TIP",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Naturaleza del bien (UR urbano, RU rústico, ES especiales). En ES incluye tipo"},
        { 'name': "RCA",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Referencia Catastral (bloque)"},
        { 'name': "PCA",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Parcela catastral (14 caracteres alfanuméricos)"},
        { 'name': "CAR",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Número secuencial del bien fiscal (Número de cargo) dentro de la parcela"},
        { 'name': "CDC1",  'type': 'String', 'len': 255, 'prec': 0, 'comment': "Primer carácter de control de la referencia"},
        { 'name': "CDC2",  'type': 'String', 'len': 255, 'prec': 0, 'comment': "Segundo carácter de control de la referencia"},
        { 'name': "USO",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Uso del inmueble (solo para inmuebles urbanos)"},
        { 'name': "SUP_construida", 'type': 'String', 'len': 255, 'prec': 0, 'comment': "Superficie construida (m²). Nota: también existe SUP en subparcelas (ha)"},
        { 'name': "ACO",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Año de construcción del bien"},
        { 'name': "FAL",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Fecha de alta"},

        # Domicilio tributario
        { 'name': "DTR",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Domicilio Tributario (texto general)"},

        # Domicilio estructurado (DT)
        { 'name': "DT",    'type': 'String', 'len': 255, 'prec': 0, 'comment': "Domicilio estructurado (bloque completo)"},
        { 'name': "LOINE", 'type': 'String', 'len': 255, 'prec': 0, 'comment': "Localización del INE (bloque)"},
        { 'name': "CP",    'type': 'String', 'len': 255, 'prec': 0, 'comment': "Código INE de la provincia"},
        { 'name': "CM",    'type': 'String', 'len': 255, 'prec': 0, 'comment': "Código INE del municipio"},
        { 'name': "CMC",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Código de municipio DGC (Catastro)"},
        { 'name': "NP",    'type': 'String', 'len': 255, 'prec': 0, 'comment': "Nombre de la provincia"},
        { 'name': "NM",    'type': 'String', 'len': 255, 'prec': 0, 'comment': "Nombre del municipio"},
        { 'name': "NEM",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Nombre de la entidad menor"},
        { 'name': "LOCS",  'type': 'String', 'len': 255, 'prec': 0, 'comment': "Localización municipal (bloque)"},
        { 'name': "LOUS",  'type': 'String', 'len': 255, 'prec': 0, 'comment': "Localización municipal del bien urbano (bloque)"},

        # Localización urbana (LOURB)
        { 'name': "LOURB", 'type': 'String', 'len': 255, 'prec': 0, 'comment': "Localización urbana (bloque)"},
        { 'name': "DIR",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Dirección (bloque)"},
        { 'name': "CV",    'type': 'String', 'len': 255, 'prec': 0, 'comment': "Código de vía"},
        { 'name': "TV",    'type': 'String', 'len': 255, 'prec': 0, 'comment': "Tipo de vía"},
        { 'name': "NV",    'type': 'String', 'len': 255, 'prec': 0, 'comment': "Nombre de vía"},
        { 'name': "PNP",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Primer número de policía"},
        { 'name': "PLP",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Primera letra asociada al número de policía"},
        { 'name': "SNP",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Segundo número de policía"},
        { 'name': "SLP",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Segunda letra asociada al número de policía"},
        { 'name': "KM",    'type': 'String', 'len': 255, 'prec': 0, 'comment': "Kilómetro"},
        { 'name': "TD",    'type': 'String', 'len': 255, 'prec': 0, 'comment': "Dirección no estructurada"},
        { 'name': "LOINT", 'type': 'String', 'len': 255, 'prec': 0, 'comment': "Localización interna (bloque)"},
        { 'name': "BQ",    'type': 'String', 'len': 255, 'prec': 0, 'comment': "Bloque"},
        { 'name': "ES",    'type': 'String', 'len': 255, 'prec': 0, 'comment': "Escalera"},
        { 'name': "PT",    'type': 'String', 'len': 255, 'prec': 0, 'comment': "Planta"},
        { 'name': "PU",    'type': 'String', 'len': 255, 'prec': 0, 'comment': "Puerta"},
        { 'name': "DP",    'type': 'String', 'len': 255, 'prec': 0, 'comment': "Código postal"},
        { 'name': "DM",    'type': 'String', 'len': 255, 'prec': 0, 'comment': "Distrito municipal"},

        # Localización rústica (LORS / LORUS) y adicionales
        { 'name': "LORS",  'type': 'String', 'len': 255, 'prec': 0, 'comment': "Localización rústica (bloque)"},
        { 'name': "LORUS", 'type': 'String', 'len': 255, 'prec': 0, 'comment': "Localización rústica adicional (bloque)"},
        { 'name': "CMA",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Código de municipio agregado"},
        { 'name': "CZC",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Código de zona de concentración"},
        { 'name': "CPP",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Identificador polígono-parcela (bloque)"},
        { 'name': "CPO",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Código de polígono"},
        { 'name': "CPA",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Código de parcela (en localización rústica)"},
        { 'name': "NPA",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Nombre de paraje"},
        { 'name': "CPAJ",  'type': 'String', 'len': 255, 'prec': 0, 'comment': "Código de paraje"},

        # Localización urbana adicional
        { 'name': "LOURS", 'type': 'String', 'len': 255, 'prec': 0, 'comment': "Localización urbana adicional (bloque)"},

        # Finca (FIN)
        { 'name': "FIN",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Finca (bloque)"},
        { 'name': "LFL",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Localización de la finca"},
        { 'name': "SUCF",  'type': 'String', 'len': 255, 'prec': 0, 'comment': "Superficie construida (finca/solar)"},
        { 'name': "SUPF",  'type': 'String', 'len': 255, 'prec': 0, 'comment': "Superficie del suelo (finca/solar)"},
        { 'name': "TIF",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Tipo de finca"},

        # Subparcelas (LSU / SPA)
        { 'name': "LSU",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Lista de subparcelas"},
        { 'name': "SPA",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Subparcela (registro)"},
        { 'name': "SUB",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Identificación de la subparcela"},
        { 'name': "CUL",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Cultivo"},
        { 'name': "INT",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Intensidad"},
        { 'name': "VCS",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Valor catastral de la subparcela"},
        { 'name': "SUP",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Superficie de la subparcela (hectáreas)"},

        # Elementos constructivos (LEC / ELC)
        { 'name': "LEC",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Lista de elementos constructivos"},
        { 'name': "ELC",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Elemento constructivo"},
        { 'name': "UEC",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Uso del elemento constructivo"},
        { 'name': "ESC",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Escalera del elemento constructivo"},
        { 'name': "PLA",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Planta del elemento constructivo"},
        { 'name': "PUE",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Puerta del elemento constructivo"},
        { 'name': "SEC",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Superficie catastral del elemento constructivo"},

        # Lista de titulares (LIT / TIT)
        { 'name': "LIT",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Lista de titulares"},
        { 'name': "TIT",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Titular (registro)"},
        { 'name': "APN",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Primer apellido, segundo apellido y nombre; o razón social"},
        { 'name': "DER",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Derecho (CA: nuda propiedad, DS: dominio, US: usufructo, PR: propietario, DF: usufructo vitalicio)"},
        { 'name': "PDE",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Porcentaje del derecho (dos decimales)"},
        { 'name': "SUF",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Sufijo de titularidad"},
        { 'name': "DFT1",  'type': 'String', 'len': 255, 'prec': 0, 'comment': "Domicilio fiscal del titular: calle, número, escalera, planta, puerta"},
        { 'name': "DFT2",  'type': 'String', 'len': 255, 'prec': 0, 'comment': "Domicilio fiscal del titular: CP, municipio, provincia"},
        { 'name': "CBI",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Comunidad de bienes formal a la que pertenece el titular (NIF/Razón social)"},

        # Datos económicos (DEB)
        { 'name': "DEB",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Datos económicos del bien inmueble (bloque)"},
        { 'name': "AAC",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Año del Valor Catastral y Base Liquidable"},
        { 'name': "VCA",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Valor catastral (euros)"},
        { 'name': "VSU",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Valor catastral del suelo (euros)"},
        { 'name': "VCO",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Valor catastral de la construcción (euros)"},

        # Finca registral (FR)
        { 'name': "FR",    'type': 'String', 'len': 255, 'prec': 0, 'comment': "Finca registral (bloque)"},
        { 'name': "PROVFR",'type': 'String', 'len': 255, 'prec': 0, 'comment': "Provincia de la finca registral"},
        { 'name': "REGFR", 'type': 'String', 'len': 255, 'prec': 0, 'comment': "Código del registro de la finca registral"},
        { 'name': "FINFR", 'type': 'String', 'len': 255, 'prec': 0, 'comment': "Número de la finca registral"},

        # Coeficiente de participación (fuera del bloque rústico)
        { 'name': "CPA_coef", 'type': 'String', 'len': 255, 'prec': 0, 'comment': "Coeficiente de participación del inmueble en la finca (porcentaje)"},

        # Errores de datos (LER2)
        { 'name': "LER2",  'type': 'String', 'len': 255, 'prec': 0, 'comment': "Lista de errores de datos (bloque)"}, { 'name': "ER2",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Error de datos (registro)"},
        { 'name': "CO2",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Código del error de datos"},
        { 'name': "DE2",   'type': 'String', 'len': 255, 'prec': 0, 'comment': "Descripción del error de datos"},
        ]

        
  # Comentarios de campos (XSD + Anejo 2 del PDF de Catastro)
  dictCatastroFields = {
        # Campo calculado por tu script
        "RC14": "Referencia Catastral de 14 dígitos (primeros 14 caracteres de PCA)",

        # Raíz y metadatos de salida
        "DS": "Documento de salida de la consulta masiva",
        "LAT": "Lista de ámbitos territoriales",
        "ATE": "Ámbito territorial según privilegios del usuario",
        "LDS": "Lista de datos de salida",
        "DSA": "Datos de salida (bloque por dato de entrada)",
        "ERR": "Bloque de error en los datos de entrada",
        "COD": "Código del error (dato de entrada)",
        "DES": "Descripción del error (dato de entrada)",

        # Datos de entrada reflejados en la salida
        "NIF": "Dato de entrada: NIF/CIF (también se usa dentro de titulares)",
        "APE": "Dato de entrada: Apellidos y Nombre",
        "RC": "Dato de entrada: Referencia Catastral",
        "PROV": "Dato de entrada: provincia",
        "MUN": "Dato de entrada: municipio / (en IBI) Código de municipio según MEH",
        "POL": "Dato de entrada: polígono",
        "PAR": "Dato de entrada: parcela",

        # Lista de bienes
        "LBI": "Lista de Bienes",
        "BIE": "Bien inmueble (registro individual)",

        # Identificación del bien (IBI)
        "IBI": "Identificación del Bien Inmueble",
        "DEL": "Código de Delegación del MEH (Hacienda)",
        "TIP": "Naturaleza del bien (UR urbano, RU rústico, ES especiales). En ES incluye tipo",
        "RCA": "Referencia Catastral (bloque)",
        "PCA": "Parcela catastral (14 caracteres alfanuméricos)",
        "CAR": "Número secuencial del bien fiscal (Número de cargo) dentro de la parcela",
        "CDC1": "Primer carácter de control de la referencia",
        "CDC2": "Segundo carácter de control de la referencia",
        "USO": "Uso del inmueble (solo para inmuebles urbanos)",
        "SUP": "Superficie construida (m²). Nota: también existe SUP en subparcelas (ha)",
        "ACO": "Año de construcción del bien",

        # Domicilio tributario (etiqueta de nivel IBI sin detalle estructurado)
        "DTR": "Domicilio Tributario (texto general)",

        # Domicilio estructurado (DT)
        "DT": "Domicilio estructurado (bloque completo)",
        "LOINE": "Localización del INE (bloque)",
        "CP": "Código INE de la provincia",
        "CM": "Código INE del municipio",
        "CMC": "Código de municipio DGC (Catastro)",
        "NP": "Nombre de la provincia",
        "NM": "Nombre del municipio",
        "NEM": "Nombre de la entidad menor",
        "LOCS": "Localización municipal (bloque)",
        "LOUS": "Localización municipal del bien urbano (bloque)",

        # Localización urbana (LOURB)
        "LOURB": "Localización urbana (bloque)",
        "DIR": "Dirección (bloque)",
        "CV": "Código de vía",
        "TV": "Tipo de vía",
        "NV": "Nombre de vía",
        "PNP": "Primer número de policía",
        "PLP": "Primera letra asociada al número de policía",
        "SNP": "Segundo número de policía",
        "SLP": "Segunda letra asociada al número de policía",
        "KM": "Kilómetro",
        "TD": "Dirección no estructurada",
        "LOINT": "Localización interna (bloque)",
        "BQ": "Bloque",
        "ES": "Escalera",
        "PT": "Planta",
        "PU": "Puerta",
        "DP": "Código postal",
        "DM": "Distrito municipal",

        # Localización rústica (LORS / LORUS) y adicionales
        "LORS": "Localización rústica (bloque)",
        "LORUS": "Localización rústica adicional (bloque)",
        "CMA": "Código de municipio agregado",
        "CZC": "Código de zona de concentración",
        "CPP": "Identificador polígono-parcela (bloque)",
        "CPO": "Código de polígono",
        "CPA": "Código de parcela (en localización rústica) / Coeficiente de participación del inmueble en la finca (%)",
        "NPA": "Nombre de paraje",
        "CPAJ": "Código de paraje",

        # Localización urbana adicional
        "LOURS": "Localización urbana adicional (bloque)",  # algunas versiones lo muestran como 'LOURB' adicional
        # (repite DIR, LOIN T, etc., con el mismo significado)

        # Finca (FIN)
        "FIN": "Finca (bloque)",
        "LFL": "Localización de la finca",
        "SUCF": "Superficie construida (finca/solar)",
        "SUPF": "Superficie del suelo (finca/solar)",
        "TIF": "Tipo de finca",

        # Subparcelas (LSU / SPA)
        "LSU": "Lista de subparcelas",
        "SPA": "Subparcela (registro)",
        "SUB": "Identificación de la subparcela",
        "CUL": "Cultivo",
        "INT": "Intensidad",
        "VCS": "Valor catastral de la subparcela",
        # Ojo: aquí aparece también SUP pero con significado distinto:
        "SUP_subparcela": "Superficie de la subparcela (hectáreas) — si renombrado por desambiguación",

        # Elementos constructivos (LEC / ELC)
        "LEC": "Lista de elementos constructivos",
        "ELC": "Elemento constructivo",
        "UEC": "Uso del elemento constructivo",
        "ESC": "Escalera del elemento constructivo",
        "PLA": "Planta del elemento constructivo",
        "PUE": "Puerta del elemento constructivo",
        "SEC": "Superficie catastral del elemento constructivo",

        # Lista de titulares (LIT / TIT)
        "LIT": "Lista de titulares",
        "TIT": "Titular (registro)",
        # (Dentro de TIT vuelven a aparecer etiquetas ya conocidas)
        "APN": "Primer apellido, segundo apellido y nombre; o razón social",
        "DER": "Derecho (CA: nuda propiedad, DS: dominio, US: usufructo, PR: propietario, DF: usufructo vitalicio)",
        "PDE": "Porcentaje del derecho (dos decimales)",
        "SUF": "Sufijo de titularidad",
        "DFT1": "Domicilio fiscal del titular: calle, número, escalera, planta, puerta",
        "DFT2": "Domicilio fiscal del titular: CP, municipio, provincia",
        "CBI": "Comunidad de bienes formal a la que pertenece el titular (NIF/Razón social)",

        # Datos económicos (DEB)
        "DEB": "Datos económicos del bien inmueble (bloque)",
        "AAC": "Año del Valor Catastral y Base Liquidable",
        "VCA": "Valor catastral (euros)",
        "VSU": "Valor catastral del suelo (euros)",
        "VCO": "Valor catastral de la construcción (euros)",

        # Finca registral (FR)
        "FR": "Finca registral (bloque)",
        "PROVFR": "Provincia de la finca registral",
        "REGFR": "Código de la finca registral",
        "FINFR": "Número de la finca registral",

        # Coeficiente de participación (aparece como CPA fuera del bloque rústico)
        "CPA_coef": "Coeficiente de participación del inmueble en la finca (porcentaje)",

        # Errores de datos (LER2)
        "LER2": "Lista de errores de datos (bloque)",
        "ER2": "Error de datos (registro)",
        "CO2": "Código del error de datos",
        "DE2": "Descripción del error de datos",
        }

