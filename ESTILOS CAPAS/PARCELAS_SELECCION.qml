<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="AllStyleCategories" minScale="100000" readOnly="0" simplifyDrawingTol="1" version="3.8.2-Zanzibar" hasScaleBasedVisibilityFlag="1" labelsEnabled="1" simplifyLocal="1" maxScale="0" simplifyMaxScale="1" simplifyDrawingHints="1" simplifyAlgorithm="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 enableorderby="0" forceraster="0" type="singleSymbol" symbollevels="0">
    <symbols>
      <symbol force_rhr="0" clip_to_extent="1" name="0" alpha="1" type="fill">
        <layer locked="0" class="SimpleFill" pass="0" enabled="1">
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="224,87,32,0"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="255,0,25,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.8"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <labeling type="simple">
    <settings>
      <text-style textOpacity="1" textColor="227,26,28,255" namedStyle="Normal" fontWordSpacing="0" fontLetterSpacing="0" previewBkgrdColor="#ffffff" fontStrikeout="0" blendMode="0" fieldName="RC14" useSubstitutions="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontItalic="0" fontWeight="50" fontSize="8" isExpression="0" fontUnderline="0" fontSizeUnit="Point" fontCapitals="0" multilineHeight="1" fontFamily="Arial">
        <text-buffer bufferNoFill="0" bufferSize="1" bufferJoinStyle="64" bufferColor="255,255,255,255" bufferBlendMode="0" bufferOpacity="1" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferSizeUnits="MM" bufferDraw="1"/>
        <background shapeType="0" shapeSVGFile="" shapeSizeY="0" shapeSizeX="0" shapeBorderColor="128,128,128,255" shapeFillColor="255,255,255,255" shapeRadiiUnit="MM" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeSizeType="0" shapeBorderWidthUnit="MM" shapeRotation="0" shapeOffsetY="0" shapeRotationType="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeOpacity="1" shapeBorderWidth="0" shapeJoinStyle="64" shapeBlendMode="0" shapeOffsetX="0" shapeDraw="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiY="0" shapeSizeUnit="MM" shapeOffsetUnit="MM" shapeRadiiX="0"/>
        <shadow shadowOpacity="0" shadowScale="100" shadowOffsetAngle="135" shadowRadiusUnit="MM" shadowRadiusAlphaOnly="0" shadowDraw="0" shadowOffsetDist="1" shadowOffsetUnit="MM" shadowUnder="0" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowBlendMode="6" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowColor="0,0,0,255" shadowRadius="0" shadowOffsetGlobal="1"/>
        <substitutions/>
      </text-style>
      <text-format wrapChar="" formatNumbers="0" multilineAlign="0" addDirectionSymbol="0" decimals="3" autoWrapLength="0" leftDirectionSymbol="&lt;" reverseDirectionSymbol="0" placeDirectionSymbol="0" plussign="0" rightDirectionSymbol=">" useMaxLineLengthForAutoWrap="1"/>
      <placement offsetUnits="MapUnit" distMapUnitScale="3x:0,0,0,0,0,0" repeatDistanceUnits="MM" placementFlags="10" yOffset="0" maxCurvedCharAngleIn="20" maxCurvedCharAngleOut="-20" placement="1" xOffset="0" geometryGeneratorType="PointGeometry" preserveRotation="1" quadOffset="4" priority="5" dist="0" offsetType="0" centroidInside="0" repeatDistance="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" geometryGenerator="" distUnits="MM" rotationAngle="0" fitInPolygonOnly="0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" geometryGeneratorEnabled="0" centroidWhole="0"/>
      <rendering scaleMin="1" obstacleType="0" limitNumLabels="0" upsidedownLabels="0" drawLabels="1" mergeLines="0" fontMinPixelSize="3" minFeatureSize="0" zIndex="0" obstacleFactor="1" scaleMax="10000000" labelPerPart="0" obstacle="1" fontMaxPixelSize="10000" fontLimitPixelSize="0" maxNumLabels="2000" scaleVisibility="0" displayAll="0"/>
      <dd_properties>
        <Option type="Map">
          <Option value="" name="name" type="QString"/>
          <Option name="properties"/>
          <Option value="collection" name="type" type="QString"/>
        </Option>
      </dd_properties>
    </settings>
  </labeling>
  <customproperties>
    <property key="dualview/previewExpressions">
      <value>COALESCE(   "RC14" , '&lt;NULL>' ) ||  '\n'  ||  coalesce(   "MUNICIPIO"  , '&lt;NULL>' ) || ' ' ||  coalesce(    "MUNI_nm"   , '&lt;NULL>' )</value>
      <value>COALESCE(   "RC14" , '&lt;NULL>' ) ||  '\n'  ||  coalesce(   "MUNICIPIO"  , '&lt;NULL>' )</value>
      <value>COALESCE(   "RC14" , '&lt;NULL>' ) ||  '\n'  ||  coalesce(   "MUNICIPIO"  , '&lt;NULL>' ) || ' ' ||  coalesce(    "MUNI_nm"   , '&lt;NULL>' )</value>
    </property>
    <property value="0" key="embeddedWidgets/count"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer diagramType="Pie" attributeLegend="1">
    <DiagramCategory lineSizeScale="3x:0,0,0,0,0,0" width="15" sizeScale="3x:0,0,0,0,0,0" penColor="#000000" backgroundColor="#ffffff" maxScaleDenominator="1e+08" minScaleDenominator="0" scaleDependency="Area" diagramOrientation="Up" barWidth="5" rotationOffset="270" sizeType="MM" enabled="0" height="15" minimumSize="0" scaleBasedVisibility="0" penAlpha="255" lineSizeType="MM" backgroundAlpha="255" labelPlacementMethod="XHeight" penWidth="0" opacity="1">
      <fontProperties description="MS Shell Dlg 2,8.25,-1,5,50,0,0,0,0,0" style=""/>
      <attribute label="" color="#000000" field=""/>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings placement="0" zIndex="0" showAll="1" dist="0" obstacle="0" priority="0" linePlacementFlags="2">
    <properties>
      <Option type="Map">
        <Option value="" name="name" type="QString"/>
        <Option name="properties"/>
        <Option value="collection" name="type" type="QString"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <fieldConfiguration>
    <field name="RC14">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="PCAT1">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="PCAT2">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="EJERCICIO">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="NUM_EXP">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="CONTROL">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="COORY">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="VIA">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="NUMERO">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="NUMERODUP">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="NUMSYMBOL">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="AREA">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="FECHAALTA">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="FECHABAJA">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="MAPA">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="DELEGACIO">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="MUNICIPIO">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="MASA">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="HOJA">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="TIPO">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="PARCELA">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="COORX">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias name="" index="0" field="RC14"/>
    <alias name="" index="1" field="PCAT1"/>
    <alias name="" index="2" field="PCAT2"/>
    <alias name="" index="3" field="EJERCICIO"/>
    <alias name="" index="4" field="NUM_EXP"/>
    <alias name="" index="5" field="CONTROL"/>
    <alias name="" index="6" field="COORY"/>
    <alias name="" index="7" field="VIA"/>
    <alias name="" index="8" field="NUMERO"/>
    <alias name="" index="9" field="NUMERODUP"/>
    <alias name="" index="10" field="NUMSYMBOL"/>
    <alias name="" index="11" field="AREA"/>
    <alias name="" index="12" field="FECHAALTA"/>
    <alias name="" index="13" field="FECHABAJA"/>
    <alias name="" index="14" field="MAPA"/>
    <alias name="" index="15" field="DELEGACIO"/>
    <alias name="" index="16" field="MUNICIPIO"/>
    <alias name="" index="17" field="MASA"/>
    <alias name="" index="18" field="HOJA"/>
    <alias name="" index="19" field="TIPO"/>
    <alias name="" index="20" field="PARCELA"/>
    <alias name="" index="21" field="COORX"/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default applyOnUpdate="0" expression="" field="RC14"/>
    <default applyOnUpdate="0" expression="" field="PCAT1"/>
    <default applyOnUpdate="0" expression="" field="PCAT2"/>
    <default applyOnUpdate="0" expression="" field="EJERCICIO"/>
    <default applyOnUpdate="0" expression="" field="NUM_EXP"/>
    <default applyOnUpdate="0" expression="" field="CONTROL"/>
    <default applyOnUpdate="0" expression="" field="COORY"/>
    <default applyOnUpdate="0" expression="" field="VIA"/>
    <default applyOnUpdate="0" expression="" field="NUMERO"/>
    <default applyOnUpdate="0" expression="" field="NUMERODUP"/>
    <default applyOnUpdate="0" expression="" field="NUMSYMBOL"/>
    <default applyOnUpdate="0" expression="" field="AREA"/>
    <default applyOnUpdate="0" expression="" field="FECHAALTA"/>
    <default applyOnUpdate="0" expression="" field="FECHABAJA"/>
    <default applyOnUpdate="0" expression="" field="MAPA"/>
    <default applyOnUpdate="0" expression="" field="DELEGACIO"/>
    <default applyOnUpdate="0" expression="" field="MUNICIPIO"/>
    <default applyOnUpdate="0" expression="" field="MASA"/>
    <default applyOnUpdate="0" expression="" field="HOJA"/>
    <default applyOnUpdate="0" expression="" field="TIPO"/>
    <default applyOnUpdate="0" expression="" field="PARCELA"/>
    <default applyOnUpdate="0" expression="" field="COORX"/>
  </defaults>
  <constraints>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="RC14"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="PCAT1"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="PCAT2"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="EJERCICIO"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="NUM_EXP"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="CONTROL"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="COORY"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="VIA"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="NUMERO"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="NUMERODUP"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="NUMSYMBOL"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="AREA"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="FECHAALTA"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="FECHABAJA"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="MAPA"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="DELEGACIO"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="MUNICIPIO"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="MASA"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="HOJA"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="TIPO"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="PARCELA"/>
    <constraint notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0" field="COORX"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" desc="" field="RC14"/>
    <constraint exp="" desc="" field="PCAT1"/>
    <constraint exp="" desc="" field="PCAT2"/>
    <constraint exp="" desc="" field="EJERCICIO"/>
    <constraint exp="" desc="" field="NUM_EXP"/>
    <constraint exp="" desc="" field="CONTROL"/>
    <constraint exp="" desc="" field="COORY"/>
    <constraint exp="" desc="" field="VIA"/>
    <constraint exp="" desc="" field="NUMERO"/>
    <constraint exp="" desc="" field="NUMERODUP"/>
    <constraint exp="" desc="" field="NUMSYMBOL"/>
    <constraint exp="" desc="" field="AREA"/>
    <constraint exp="" desc="" field="FECHAALTA"/>
    <constraint exp="" desc="" field="FECHABAJA"/>
    <constraint exp="" desc="" field="MAPA"/>
    <constraint exp="" desc="" field="DELEGACIO"/>
    <constraint exp="" desc="" field="MUNICIPIO"/>
    <constraint exp="" desc="" field="MASA"/>
    <constraint exp="" desc="" field="HOJA"/>
    <constraint exp="" desc="" field="TIPO"/>
    <constraint exp="" desc="" field="PARCELA"/>
    <constraint exp="" desc="" field="COORX"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortOrder="0" sortExpression="" actionWidgetStyle="dropDown">
    <columns>
      <column width="-1" hidden="0" name="RC14" type="field"/>
      <column width="-1" hidden="0" name="PCAT1" type="field"/>
      <column width="-1" hidden="0" name="PCAT2" type="field"/>
      <column width="-1" hidden="0" name="EJERCICIO" type="field"/>
      <column width="-1" hidden="0" name="NUM_EXP" type="field"/>
      <column width="-1" hidden="0" name="CONTROL" type="field"/>
      <column width="-1" hidden="0" name="COORY" type="field"/>
      <column width="-1" hidden="0" name="VIA" type="field"/>
      <column width="-1" hidden="0" name="NUMERO" type="field"/>
      <column width="-1" hidden="0" name="NUMERODUP" type="field"/>
      <column width="-1" hidden="0" name="NUMSYMBOL" type="field"/>
      <column width="-1" hidden="0" name="AREA" type="field"/>
      <column width="-1" hidden="0" name="FECHAALTA" type="field"/>
      <column width="-1" hidden="0" name="FECHABAJA" type="field"/>
      <column width="-1" hidden="0" name="MAPA" type="field"/>
      <column width="-1" hidden="0" name="DELEGACIO" type="field"/>
      <column width="-1" hidden="0" name="MUNICIPIO" type="field"/>
      <column width="-1" hidden="0" name="MASA" type="field"/>
      <column width="-1" hidden="0" name="HOJA" type="field"/>
      <column width="-1" hidden="0" name="TIPO" type="field"/>
      <column width="-1" hidden="0" name="PARCELA" type="field"/>
      <column width="-1" hidden="0" name="COORX" type="field"/>
      <column width="-1" hidden="1" type="actions"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <editform tolerant="1"></editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath></editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
QGIS forms can have a Python function that is called when the form is
opened.

Use this function to add extra logic to your forms.

Enter the name of the function in the "Python Init function"
field.
An example follows:
"""
from PyQt4.QtGui import QWidget

def my_form_open(dialog, layer, feature):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>generatedlayout</editorlayout>
  <editable>
    <field name="AREA" editable="1"/>
    <field name="CONTROL" editable="1"/>
    <field name="COORX" editable="1"/>
    <field name="COORY" editable="1"/>
    <field name="DELEGACIO" editable="1"/>
    <field name="EJERCICIO" editable="1"/>
    <field name="FECHAALTA" editable="1"/>
    <field name="FECHABAJA" editable="1"/>
    <field name="HOJA" editable="1"/>
    <field name="MAPA" editable="1"/>
    <field name="MASA" editable="1"/>
    <field name="MUNICIPIO" editable="1"/>
    <field name="MUNI_cd" editable="0"/>
    <field name="MUNI_cdcmc" editable="0"/>
    <field name="MUNI_cmc" editable="0"/>
    <field name="MUNI_codine" editable="0"/>
    <field name="MUNI_nm" editable="0"/>
    <field name="NUMERO" editable="1"/>
    <field name="NUMERODUP" editable="1"/>
    <field name="NUMSYMBOL" editable="1"/>
    <field name="NUM_EXP" editable="1"/>
    <field name="PARCELA" editable="1"/>
    <field name="PCAT1" editable="1"/>
    <field name="PCAT2" editable="1"/>
    <field name="RC14" editable="1"/>
    <field name="TIPO" editable="1"/>
    <field name="VIA" editable="1"/>
  </editable>
  <labelOnTop>
    <field name="AREA" labelOnTop="0"/>
    <field name="CONTROL" labelOnTop="0"/>
    <field name="COORX" labelOnTop="0"/>
    <field name="COORY" labelOnTop="0"/>
    <field name="DELEGACIO" labelOnTop="0"/>
    <field name="EJERCICIO" labelOnTop="0"/>
    <field name="FECHAALTA" labelOnTop="0"/>
    <field name="FECHABAJA" labelOnTop="0"/>
    <field name="HOJA" labelOnTop="0"/>
    <field name="MAPA" labelOnTop="0"/>
    <field name="MASA" labelOnTop="0"/>
    <field name="MUNICIPIO" labelOnTop="0"/>
    <field name="MUNI_cd" labelOnTop="0"/>
    <field name="MUNI_cdcmc" labelOnTop="0"/>
    <field name="MUNI_cmc" labelOnTop="0"/>
    <field name="MUNI_codine" labelOnTop="0"/>
    <field name="MUNI_nm" labelOnTop="0"/>
    <field name="NUMERO" labelOnTop="0"/>
    <field name="NUMERODUP" labelOnTop="0"/>
    <field name="NUMSYMBOL" labelOnTop="0"/>
    <field name="NUM_EXP" labelOnTop="0"/>
    <field name="PARCELA" labelOnTop="0"/>
    <field name="PCAT1" labelOnTop="0"/>
    <field name="PCAT2" labelOnTop="0"/>
    <field name="RC14" labelOnTop="0"/>
    <field name="TIPO" labelOnTop="0"/>
    <field name="VIA" labelOnTop="0"/>
  </labelOnTop>
  <widgets/>
  <previewExpression>COALESCE(   "RC14" , '&lt;NULL>' ) ||  '\n'  ||  coalesce(   "MUNICIPIO"  , '&lt;NULL>' ) || ' ' ||  coalesce(    "MUNI_nm"   , '&lt;NULL>' )</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>2</layerGeometryType>
</qgis>
