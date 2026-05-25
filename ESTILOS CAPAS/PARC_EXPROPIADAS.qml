<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="AllStyleCategories" simplifyDrawingHints="1" maxScale="-4.65661e-10" readOnly="0" hasScaleBasedVisibilityFlag="0" simplifyMaxScale="1" minScale="5000" simplifyLocal="1" simplifyDrawingTol="1" simplifyAlgorithm="0" version="3.10.6-A Coruña" labelsEnabled="1">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 symbollevels="1" attr="TIPORES" type="categorizedSymbol" forceraster="0" enableorderby="0">
    <categories>
      <category value="EXPRO" label="Parte EXPROPIADA" render="true" symbol="0"/>
      <category value="RESTO" label="RESTO PARCELA" render="true" symbol="1"/>
    </categories>
    <symbols>
      <symbol clip_to_extent="1" alpha="1" force_rhr="0" name="0" type="fill">
        <layer enabled="1" locked="0" pass="1" class="SimpleFill">
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="72,255,0,51"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="1,13,255,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.4"/>
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
        <layer enabled="1" locked="0" pass="1" class="GeometryGenerator">
          <prop k="SymbolType" v="Marker"/>
          <prop k="geometryModifier" v=" point_on_surface( $geometry )"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol clip_to_extent="1" alpha="1" force_rhr="0" name="@0@1" type="marker">
            <layer enabled="1" locked="0" pass="0" class="SimpleMarker">
              <prop k="angle" v="0"/>
              <prop k="color" v="1,13,255,255"/>
              <prop k="horizontal_anchor_point" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="name" v="circle"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="0,0,0,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0"/>
              <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="scale_method" v="diameter"/>
              <prop k="size" v="1"/>
              <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="size_unit" v="MM"/>
              <prop k="vertical_anchor_point" v="1"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer enabled="1" locked="0" pass="2" class="GeometryGenerator">
          <prop k="SymbolType" v="Line"/>
          <prop k="geometryModifier" v=" make_line(  make_point(  &quot;X_LABEL&quot; , &quot;Y_LABEL&quot; ),  point_on_surface( $geometry ))"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol clip_to_extent="1" alpha="1" force_rhr="0" name="@0@2" type="line">
            <layer enabled="1" locked="0" pass="0" class="SimpleLine">
              <prop k="capstyle" v="square"/>
              <prop k="customdash" v="5;2"/>
              <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="customdash_unit" v="MM"/>
              <prop k="draw_inside_polygon" v="0"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="line_color" v="1,13,255,255"/>
              <prop k="line_style" v="solid"/>
              <prop k="line_width" v="0.4"/>
              <prop k="line_width_unit" v="MM"/>
              <prop k="offset" v="0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="ring_filter" v="0"/>
              <prop k="use_custom_dash" v="0"/>
              <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol clip_to_extent="1" alpha="1" force_rhr="0" name="1" type="fill">
        <layer enabled="1" locked="0" pass="0" class="SimpleFill">
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="255,249,124,51"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="255,149,1,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.4"/>
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
    <source-symbol>
      <symbol clip_to_extent="1" alpha="1" force_rhr="0" name="0" type="fill">
        <layer enabled="1" locked="0" pass="0" class="SimpleFill">
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="199,221,236,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="1,13,255,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.4"/>
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
        <layer enabled="1" locked="0" pass="0" class="GeometryGenerator">
          <prop k="SymbolType" v="Marker"/>
          <prop k="geometryModifier" v=" point_on_surface( $geometry )"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol clip_to_extent="1" alpha="1" force_rhr="0" name="@0@1" type="marker">
            <layer enabled="1" locked="0" pass="0" class="SimpleMarker">
              <prop k="angle" v="0"/>
              <prop k="color" v="255,0,0,255"/>
              <prop k="horizontal_anchor_point" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="name" v="circle"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="0,0,0,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0"/>
              <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="scale_method" v="diameter"/>
              <prop k="size" v="1"/>
              <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="size_unit" v="MM"/>
              <prop k="vertical_anchor_point" v="1"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer enabled="1" locked="0" pass="0" class="GeometryGenerator">
          <prop k="SymbolType" v="Line"/>
          <prop k="geometryModifier" v=" make_line(  make_point(  &quot;X_LABEL&quot; , &quot;Y_LABEL&quot; ),  point_on_surface( $geometry ))"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol clip_to_extent="1" alpha="1" force_rhr="0" name="@0@2" type="line">
            <layer enabled="1" locked="0" pass="0" class="SimpleLine">
              <prop k="capstyle" v="square"/>
              <prop k="customdash" v="5;2"/>
              <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="customdash_unit" v="MM"/>
              <prop k="draw_inside_polygon" v="0"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="line_color" v="12,40,254,255"/>
              <prop k="line_style" v="solid"/>
              <prop k="line_width" v="0.4"/>
              <prop k="line_width_unit" v="MM"/>
              <prop k="offset" v="0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="ring_filter" v="0"/>
              <prop k="use_custom_dash" v="0"/>
              <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
    </source-symbol>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <labeling type="simple">
    <settings calloutType="simple">
      <text-style fontSize="7" textOrientation="horizontal" fieldName="CASE WHEN  &quot;TIPORES&quot;  =  'RESTO' &#xd;&#xa;THEN &#xd;&#xa;&quot;pol&quot; +'-'+ &quot;par&quot; &#xd;&#xa;ELSE&#xd;&#xa;&#x9;CASE WHEN  &quot;TIPORES&quot;  =   'EXPRO' &#xd;&#xa;&#x9;THEN &#xd;&#xa;&#x9;'Nº '+  &quot;no_orden&quot;  +  '\n'+ &#xd;&#xa;     &quot;pol&quot;  +' / '+  &quot;par&quot;  +' '+   &quot;uso&quot; + '\n'+&#xd;&#xa;    format_number(  &quot;superfpd&quot;  ,1)+ ' m2'&#xd;&#xa;&#x9;END&#xd;&#xa;END&#xd;&#xa;&#xd;&#xa;&#xd;&#xa;" namedStyle="Normal" blendMode="0" multilineHeight="1" fontKerning="1" fontWeight="50" fontItalic="0" textOpacity="1" fontStrikeout="0" fontUnderline="0" fontWordSpacing="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontSizeUnit="Point" isExpression="1" fontFamily="MS Shell Dlg 2" textColor="31,120,180,255" fontCapitals="0" previewBkgrdColor="0,0,0,255" fontLetterSpacing="0" useSubstitutions="0">
        <text-buffer bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferBlendMode="0" bufferNoFill="0" bufferOpacity="1" bufferColor="255,255,255,255" bufferSize="1" bufferDraw="0" bufferJoinStyle="64" bufferSizeUnits="MM"/>
        <background shapeOffsetUnit="MM" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeRotation="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeBlendMode="0" shapeSVGFile="" shapeBorderWidth="0" shapeSizeY="0" shapeOffsetX="0" shapeOffsetY="0" shapeType="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeSizeUnit="Point" shapeOpacity="1" shapeDraw="1" shapeSizeType="0" shapeRadiiUnit="MM" shapeFillColor="255,255,255,255" shapeSizeX="0" shapeJoinStyle="64" shapeBorderWidthUnit="MM" shapeRotationType="0" shapeRadiiX="0" shapeBorderColor="31,120,180,255" shapeRadiiY="0">
          <symbol clip_to_extent="1" alpha="1" force_rhr="0" name="markerSymbol" type="marker">
            <layer enabled="1" locked="0" pass="0" class="SimpleMarker">
              <prop k="angle" v="0"/>
              <prop k="color" v="231,113,72,255"/>
              <prop k="horizontal_anchor_point" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="name" v="circle"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="35,35,35,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0"/>
              <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="scale_method" v="diameter"/>
              <prop k="size" v="2"/>
              <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="size_unit" v="MM"/>
              <prop k="vertical_anchor_point" v="1"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </background>
        <shadow shadowScale="100" shadowOffsetAngle="135" shadowColor="0,0,0,255" shadowOffsetGlobal="1" shadowRadius="0" shadowRadiusAlphaOnly="0" shadowDraw="0" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowBlendMode="6" shadowRadiusUnit="MM" shadowOpacity="0" shadowOffsetUnit="MM" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowUnder="0" shadowOffsetDist="1"/>
        <dd_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </dd_properties>
        <substitutions/>
      </text-style>
      <text-format placeDirectionSymbol="0" plussign="0" useMaxLineLengthForAutoWrap="1" decimals="3" addDirectionSymbol="0" rightDirectionSymbol=">" leftDirectionSymbol="&lt;" autoWrapLength="0" reverseDirectionSymbol="0" wrapChar="" multilineAlign="1" formatNumbers="0"/>
      <placement xOffset="0" placement="1" maxCurvedCharAngleIn="20" geometryGenerator="" dist="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" offsetType="0" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" centroidWhole="0" fitInPolygonOnly="0" geometryGeneratorEnabled="0" quadOffset="4" centroidInside="0" repeatDistanceUnits="MM" preserveRotation="1" yOffset="0" offsetUnits="MapUnit" overrunDistance="0" distUnits="MM" rotationAngle="0" overrunDistanceUnit="MM" distMapUnitScale="3x:0,0,0,0,0,0" geometryGeneratorType="PointGeometry" layerType="PolygonGeometry" priority="5" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" maxCurvedCharAngleOut="-20" repeatDistance="0" placementFlags="10" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0"/>
      <rendering fontLimitPixelSize="0" minFeatureSize="0" fontMinPixelSize="3" displayAll="0" scaleMin="1" scaleMax="5001" labelPerPart="0" obstacle="1" obstacleType="0" upsidedownLabels="0" obstacleFactor="1" scaleVisibility="1" fontMaxPixelSize="10000" mergeLines="0" drawLabels="1" limitNumLabels="0" maxNumLabels="2000" zIndex="-2"/>
      <dd_properties>
        <Option type="Map">
          <Option value="" name="name" type="QString"/>
          <Option name="properties" type="Map">
            <Option name="Hali" type="Map">
              <Option value="true" name="active" type="bool"/>
              <Option value="'Center'" name="expression" type="QString"/>
              <Option value="3" name="type" type="int"/>
            </Option>
            <Option name="PositionX" type="Map">
              <Option value="true" name="active" type="bool"/>
              <Option value="X_LABEL" name="field" type="QString"/>
              <Option value="2" name="type" type="int"/>
            </Option>
            <Option name="PositionY" type="Map">
              <Option value="true" name="active" type="bool"/>
              <Option value="Y_LABEL" name="field" type="QString"/>
              <Option value="2" name="type" type="int"/>
            </Option>
            <Option name="ShapeFillColor" type="Map">
              <Option value="true" name="active" type="bool"/>
              <Option value="if(  ( &quot;TIPORES&quot;  = 'EXPRO'), color_rgb( 255,255,255),color_rgb( 255,255,150))" name="expression" type="QString"/>
              <Option value="3" name="type" type="int"/>
            </Option>
            <Option name="Vali" type="Map">
              <Option value="true" name="active" type="bool"/>
              <Option value="'Center'" name="expression" type="QString"/>
              <Option value="3" name="type" type="int"/>
            </Option>
          </Option>
          <Option value="collection" name="type" type="QString"/>
        </Option>
      </dd_properties>
      <callout type="simple">
        <Option type="Map">
          <Option value="pole_of_inaccessibility" name="anchorPoint" type="QString"/>
          <Option name="ddProperties" type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
          <Option value="false" name="drawToAllParts" type="bool"/>
          <Option value="0" name="enabled" type="QString"/>
          <Option value="&lt;symbol clip_to_extent=&quot;1&quot; alpha=&quot;1&quot; force_rhr=&quot;0&quot; name=&quot;symbol&quot; type=&quot;line&quot;>&lt;layer enabled=&quot;1&quot; locked=&quot;0&quot; pass=&quot;0&quot; class=&quot;SimpleLine&quot;>&lt;prop k=&quot;capstyle&quot; v=&quot;square&quot;/>&lt;prop k=&quot;customdash&quot; v=&quot;5;2&quot;/>&lt;prop k=&quot;customdash_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;customdash_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;draw_inside_polygon&quot; v=&quot;0&quot;/>&lt;prop k=&quot;joinstyle&quot; v=&quot;bevel&quot;/>&lt;prop k=&quot;line_color&quot; v=&quot;60,60,60,255&quot;/>&lt;prop k=&quot;line_style&quot; v=&quot;solid&quot;/>&lt;prop k=&quot;line_width&quot; v=&quot;0.3&quot;/>&lt;prop k=&quot;line_width_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;offset&quot; v=&quot;0&quot;/>&lt;prop k=&quot;offset_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;offset_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;ring_filter&quot; v=&quot;0&quot;/>&lt;prop k=&quot;use_custom_dash&quot; v=&quot;0&quot;/>&lt;prop k=&quot;width_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; name=&quot;name&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; name=&quot;type&quot; type=&quot;QString&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" name="lineSymbol" type="QString"/>
          <Option value="0" name="minLength" type="double"/>
          <Option value="3x:0,0,0,0,0,0" name="minLengthMapUnitScale" type="QString"/>
          <Option value="MM" name="minLengthUnit" type="QString"/>
          <Option value="0" name="offsetFromAnchor" type="double"/>
          <Option value="3x:0,0,0,0,0,0" name="offsetFromAnchorMapUnitScale" type="QString"/>
          <Option value="MM" name="offsetFromAnchorUnit" type="QString"/>
          <Option value="0" name="offsetFromLabel" type="double"/>
          <Option value="3x:0,0,0,0,0,0" name="offsetFromLabelMapUnitScale" type="QString"/>
          <Option value="MM" name="offsetFromLabelUnit" type="QString"/>
        </Option>
      </callout>
    </settings>
  </labeling>
  <customproperties>
    <property value="COALESCE( &quot;SUP_MEDIDA&quot;, '&lt;NULL>' )" key="dualview/previewExpressions"/>
    <property value="0" key="embeddedWidgets/count"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer diagramType="Pie" attributeLegend="1">
    <DiagramCategory rotationOffset="270" scaleBasedVisibility="0" barWidth="5" labelPlacementMethod="XHeight" backgroundColor="#ffffff" diagramOrientation="Up" lineSizeType="MM" lineSizeScale="3x:0,0,0,0,0,0" minimumSize="0" penAlpha="255" backgroundAlpha="255" height="15" penColor="#000000" sizeType="MM" scaleDependency="Area" enabled="0" opacity="1" sizeScale="3x:0,0,0,0,0,0" penWidth="0" width="15" maxScaleDenominator="1e+08" minScaleDenominator="-4.65661e-10">
      <fontProperties style="" description="MS Shell Dlg 2,7.8,-1,5,50,0,0,0,0,0"/>
      <attribute field="" label="" color="#000000"/>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings zIndex="0" priority="0" showAll="1" dist="0" linePlacementFlags="2" obstacle="0" placement="0">
    <properties>
      <Option type="Map">
        <Option value="" name="name" type="QString"/>
        <Option name="properties"/>
        <Option value="collection" name="type" type="QString"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions removeDuplicateNodes="0" geometryPrecision="0">
    <activeChecks/>
    <checkConfiguration type="Map">
      <Option name="QgsGeometryGapCheck" type="Map">
        <Option value="0" name="allowedGapsBuffer" type="double"/>
        <Option value="false" name="allowedGapsEnabled" type="bool"/>
        <Option value="" name="allowedGapsLayer" type="QString"/>
      </Option>
    </checkConfiguration>
  </geometryOptions>
  <fieldConfiguration>
    <field name="no_orden">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="EXPEDIENTE">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="term_munic">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="cod_term_m">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="pedanía">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="pol">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="par">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="subpar">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="RC14">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="dirfinca">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="paraje">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="uso">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="concepto">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="tipopropi">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="supcat">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="calificacion">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="superfpd">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="valorunitpd">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="importepd">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="superfot">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="valorunitot">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="importeot">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="superfsp">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="valorunitsp">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="importesp">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="superfsv">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="valorunitsv">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="importesv">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="TIPORES">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="X_LABEL">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="Y_LABEL">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias field="no_orden" index="0" name=""/>
    <alias field="EXPEDIENTE" index="1" name=""/>
    <alias field="term_munic" index="2" name=""/>
    <alias field="cod_term_m" index="3" name=""/>
    <alias field="pedanía" index="4" name=""/>
    <alias field="pol" index="5" name=""/>
    <alias field="par" index="6" name=""/>
    <alias field="subpar" index="7" name=""/>
    <alias field="RC14" index="8" name=""/>
    <alias field="dirfinca" index="9" name=""/>
    <alias field="paraje" index="10" name=""/>
    <alias field="uso" index="11" name=""/>
    <alias field="concepto" index="12" name=""/>
    <alias field="tipopropi" index="13" name=""/>
    <alias field="supcat" index="14" name=""/>
    <alias field="calificacion" index="15" name=""/>
    <alias field="superfpd" index="16" name=""/>
    <alias field="valorunitpd" index="17" name=""/>
    <alias field="importepd" index="18" name=""/>
    <alias field="superfot" index="19" name=""/>
    <alias field="valorunitot" index="20" name=""/>
    <alias field="importeot" index="21" name=""/>
    <alias field="superfsp" index="22" name=""/>
    <alias field="valorunitsp" index="23" name=""/>
    <alias field="importesp" index="24" name=""/>
    <alias field="superfsv" index="25" name=""/>
    <alias field="valorunitsv" index="26" name=""/>
    <alias field="importesv" index="27" name=""/>
    <alias field="TIPORES" index="28" name=""/>
    <alias field="X_LABEL" index="29" name=""/>
    <alias field="Y_LABEL" index="30" name=""/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default expression="" field="no_orden" applyOnUpdate="0"/>
    <default expression="" field="EXPEDIENTE" applyOnUpdate="0"/>
    <default expression="" field="term_munic" applyOnUpdate="0"/>
    <default expression="" field="cod_term_m" applyOnUpdate="0"/>
    <default expression="" field="pedanía" applyOnUpdate="0"/>
    <default expression="" field="pol" applyOnUpdate="0"/>
    <default expression="" field="par" applyOnUpdate="0"/>
    <default expression="" field="subpar" applyOnUpdate="0"/>
    <default expression="" field="RC14" applyOnUpdate="0"/>
    <default expression="" field="dirfinca" applyOnUpdate="0"/>
    <default expression="" field="paraje" applyOnUpdate="0"/>
    <default expression="" field="uso" applyOnUpdate="0"/>
    <default expression="" field="concepto" applyOnUpdate="0"/>
    <default expression="" field="tipopropi" applyOnUpdate="0"/>
    <default expression="" field="supcat" applyOnUpdate="0"/>
    <default expression="" field="calificacion" applyOnUpdate="0"/>
    <default expression="" field="superfpd" applyOnUpdate="0"/>
    <default expression="" field="valorunitpd" applyOnUpdate="0"/>
    <default expression="" field="importepd" applyOnUpdate="0"/>
    <default expression="" field="superfot" applyOnUpdate="0"/>
    <default expression="" field="valorunitot" applyOnUpdate="0"/>
    <default expression="" field="importeot" applyOnUpdate="0"/>
    <default expression="" field="superfsp" applyOnUpdate="0"/>
    <default expression="" field="valorunitsp" applyOnUpdate="0"/>
    <default expression="" field="importesp" applyOnUpdate="0"/>
    <default expression="" field="superfsv" applyOnUpdate="0"/>
    <default expression="" field="valorunitsv" applyOnUpdate="0"/>
    <default expression="" field="importesv" applyOnUpdate="0"/>
    <default expression="" field="TIPORES" applyOnUpdate="0"/>
    <default expression="" field="X_LABEL" applyOnUpdate="0"/>
    <default expression="" field="Y_LABEL" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint field="no_orden" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="EXPEDIENTE" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="term_munic" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="cod_term_m" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="pedanía" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="pol" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="par" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="subpar" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="RC14" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="dirfinca" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="paraje" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="uso" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="concepto" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="tipopropi" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="supcat" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="calificacion" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="superfpd" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="valorunitpd" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="importepd" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="superfot" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="valorunitot" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="importeot" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="superfsp" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="valorunitsp" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="importesp" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="superfsv" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="valorunitsv" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="importesv" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="TIPORES" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="X_LABEL" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
    <constraint field="Y_LABEL" exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="no_orden" exp="" desc=""/>
    <constraint field="EXPEDIENTE" exp="" desc=""/>
    <constraint field="term_munic" exp="" desc=""/>
    <constraint field="cod_term_m" exp="" desc=""/>
    <constraint field="pedanía" exp="" desc=""/>
    <constraint field="pol" exp="" desc=""/>
    <constraint field="par" exp="" desc=""/>
    <constraint field="subpar" exp="" desc=""/>
    <constraint field="RC14" exp="" desc=""/>
    <constraint field="dirfinca" exp="" desc=""/>
    <constraint field="paraje" exp="" desc=""/>
    <constraint field="uso" exp="" desc=""/>
    <constraint field="concepto" exp="" desc=""/>
    <constraint field="tipopropi" exp="" desc=""/>
    <constraint field="supcat" exp="" desc=""/>
    <constraint field="calificacion" exp="" desc=""/>
    <constraint field="superfpd" exp="" desc=""/>
    <constraint field="valorunitpd" exp="" desc=""/>
    <constraint field="importepd" exp="" desc=""/>
    <constraint field="superfot" exp="" desc=""/>
    <constraint field="valorunitot" exp="" desc=""/>
    <constraint field="importeot" exp="" desc=""/>
    <constraint field="superfsp" exp="" desc=""/>
    <constraint field="valorunitsp" exp="" desc=""/>
    <constraint field="importesp" exp="" desc=""/>
    <constraint field="superfsv" exp="" desc=""/>
    <constraint field="valorunitsv" exp="" desc=""/>
    <constraint field="importesv" exp="" desc=""/>
    <constraint field="TIPORES" exp="" desc=""/>
    <constraint field="X_LABEL" exp="" desc=""/>
    <constraint field="Y_LABEL" exp="" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortExpression="&quot;calificacion&quot;" actionWidgetStyle="dropDown" sortOrder="1">
    <columns>
      <column width="-1" type="actions" hidden="1"/>
      <column width="-1" name="no_orden" type="field" hidden="0"/>
      <column width="-1" name="cod_term_m" type="field" hidden="0"/>
      <column width="-1" name="pol" type="field" hidden="0"/>
      <column width="-1" name="par" type="field" hidden="0"/>
      <column width="-1" name="pedanía" type="field" hidden="0"/>
      <column width="-1" name="subpar" type="field" hidden="0"/>
      <column width="-1" name="RC14" type="field" hidden="0"/>
      <column width="-1" name="dirfinca" type="field" hidden="0"/>
      <column width="-1" name="paraje" type="field" hidden="0"/>
      <column width="-1" name="uso" type="field" hidden="0"/>
      <column width="-1" name="concepto" type="field" hidden="0"/>
      <column width="-1" name="tipopropi" type="field" hidden="0"/>
      <column width="-1" name="supcat" type="field" hidden="0"/>
      <column width="-1" name="calificacion" type="field" hidden="0"/>
      <column width="-1" name="superfpd" type="field" hidden="0"/>
      <column width="-1" name="valorunitpd" type="field" hidden="0"/>
      <column width="-1" name="importepd" type="field" hidden="0"/>
      <column width="-1" name="superfot" type="field" hidden="0"/>
      <column width="-1" name="valorunitot" type="field" hidden="0"/>
      <column width="-1" name="importeot" type="field" hidden="0"/>
      <column width="-1" name="superfsp" type="field" hidden="0"/>
      <column width="-1" name="valorunitsp" type="field" hidden="0"/>
      <column width="-1" name="importesp" type="field" hidden="0"/>
      <column width="-1" name="superfsv" type="field" hidden="0"/>
      <column width="-1" name="valorunitsv" type="field" hidden="0"/>
      <column width="-1" name="importesv" type="field" hidden="0"/>
      <column width="-1" name="TIPORES" type="field" hidden="0"/>
      <column width="-1" name="EXPEDIENTE" type="field" hidden="0"/>
      <column width="-1" name="term_munic" type="field" hidden="0"/>
      <column width="-1" name="X_LABEL" type="field" hidden="0"/>
      <column width="-1" name="Y_LABEL" type="field" hidden="0"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
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
    <field name="BIENES1" editable="1"/>
    <field name="CARRETERA" editable="1"/>
    <field name="COD_PAREXP" editable="1"/>
    <field name="COD_TERM_M" editable="1"/>
    <field name="DATA1" editable="1"/>
    <field name="EXPEDIENTE" editable="1"/>
    <field name="EXPT_EXPRO" editable="1"/>
    <field name="Layer" editable="1"/>
    <field name="NO_ORDEN" editable="1"/>
    <field name="PAR" editable="1"/>
    <field name="PARC_PARTE" editable="1"/>
    <field name="POL" editable="1"/>
    <field name="RC14" editable="1"/>
    <field name="REF_CAT" editable="1"/>
    <field name="SUP_ACTAS" editable="1"/>
    <field name="SUP_CAT" editable="1"/>
    <field name="SUP_MEDIDA" editable="1"/>
    <field name="TERM_MUNI" editable="1"/>
    <field name="TIPO" editable="1"/>
    <field name="TIPORES" editable="1"/>
    <field name="Text" editable="1"/>
    <field name="X_LABEL" editable="1"/>
    <field name="Y_LABEL" editable="1"/>
    <field name="bienes1" editable="1"/>
    <field name="calificacion" editable="1"/>
    <field name="carretera" editable="1"/>
    <field name="cod_parexp" editable="1"/>
    <field name="cod_term_m" editable="1"/>
    <field name="concepto" editable="1"/>
    <field name="data1" editable="1"/>
    <field name="dirfinca" editable="1"/>
    <field name="expt_expro" editable="1"/>
    <field name="fid" editable="1"/>
    <field name="importeot" editable="1"/>
    <field name="importepd" editable="1"/>
    <field name="importesp" editable="1"/>
    <field name="importesv" editable="1"/>
    <field name="layer" editable="1"/>
    <field name="no_orden" editable="1"/>
    <field name="par" editable="1"/>
    <field name="paraje" editable="1"/>
    <field name="parc_parte" editable="1"/>
    <field name="pedanía" editable="1"/>
    <field name="pol" editable="1"/>
    <field name="ref_cat" editable="1"/>
    <field name="subpar" editable="1"/>
    <field name="sup_actas" editable="1"/>
    <field name="sup_cat" editable="1"/>
    <field name="sup_medida" editable="1"/>
    <field name="supcat" editable="1"/>
    <field name="superfot" editable="1"/>
    <field name="superfpd" editable="1"/>
    <field name="superfsp" editable="1"/>
    <field name="superfsv" editable="1"/>
    <field name="term_muni" editable="1"/>
    <field name="term_munic" editable="1"/>
    <field name="text" editable="1"/>
    <field name="tipo" editable="1"/>
    <field name="tipopropi" editable="1"/>
    <field name="uso" editable="1"/>
    <field name="valorunitot" editable="1"/>
    <field name="valorunitpd" editable="1"/>
    <field name="valorunitsp" editable="1"/>
    <field name="valorunitsv" editable="1"/>
    <field name="x_label" editable="1"/>
    <field name="y_label" editable="1"/>
  </editable>
  <labelOnTop>
    <field name="BIENES1" labelOnTop="0"/>
    <field name="CARRETERA" labelOnTop="0"/>
    <field name="COD_PAREXP" labelOnTop="0"/>
    <field name="COD_TERM_M" labelOnTop="0"/>
    <field name="DATA1" labelOnTop="0"/>
    <field name="EXPEDIENTE" labelOnTop="0"/>
    <field name="EXPT_EXPRO" labelOnTop="0"/>
    <field name="Layer" labelOnTop="0"/>
    <field name="NO_ORDEN" labelOnTop="0"/>
    <field name="PAR" labelOnTop="0"/>
    <field name="PARC_PARTE" labelOnTop="0"/>
    <field name="POL" labelOnTop="0"/>
    <field name="RC14" labelOnTop="0"/>
    <field name="REF_CAT" labelOnTop="0"/>
    <field name="SUP_ACTAS" labelOnTop="0"/>
    <field name="SUP_CAT" labelOnTop="0"/>
    <field name="SUP_MEDIDA" labelOnTop="0"/>
    <field name="TERM_MUNI" labelOnTop="0"/>
    <field name="TIPO" labelOnTop="0"/>
    <field name="TIPORES" labelOnTop="0"/>
    <field name="Text" labelOnTop="0"/>
    <field name="X_LABEL" labelOnTop="0"/>
    <field name="Y_LABEL" labelOnTop="0"/>
    <field name="bienes1" labelOnTop="0"/>
    <field name="calificacion" labelOnTop="0"/>
    <field name="carretera" labelOnTop="0"/>
    <field name="cod_parexp" labelOnTop="0"/>
    <field name="cod_term_m" labelOnTop="0"/>
    <field name="concepto" labelOnTop="0"/>
    <field name="data1" labelOnTop="0"/>
    <field name="dirfinca" labelOnTop="0"/>
    <field name="expt_expro" labelOnTop="0"/>
    <field name="fid" labelOnTop="0"/>
    <field name="importeot" labelOnTop="0"/>
    <field name="importepd" labelOnTop="0"/>
    <field name="importesp" labelOnTop="0"/>
    <field name="importesv" labelOnTop="0"/>
    <field name="layer" labelOnTop="0"/>
    <field name="no_orden" labelOnTop="0"/>
    <field name="par" labelOnTop="0"/>
    <field name="paraje" labelOnTop="0"/>
    <field name="parc_parte" labelOnTop="0"/>
    <field name="pedanía" labelOnTop="0"/>
    <field name="pol" labelOnTop="0"/>
    <field name="ref_cat" labelOnTop="0"/>
    <field name="subpar" labelOnTop="0"/>
    <field name="sup_actas" labelOnTop="0"/>
    <field name="sup_cat" labelOnTop="0"/>
    <field name="sup_medida" labelOnTop="0"/>
    <field name="supcat" labelOnTop="0"/>
    <field name="superfot" labelOnTop="0"/>
    <field name="superfpd" labelOnTop="0"/>
    <field name="superfsp" labelOnTop="0"/>
    <field name="superfsv" labelOnTop="0"/>
    <field name="term_muni" labelOnTop="0"/>
    <field name="term_munic" labelOnTop="0"/>
    <field name="text" labelOnTop="0"/>
    <field name="tipo" labelOnTop="0"/>
    <field name="tipopropi" labelOnTop="0"/>
    <field name="uso" labelOnTop="0"/>
    <field name="valorunitot" labelOnTop="0"/>
    <field name="valorunitpd" labelOnTop="0"/>
    <field name="valorunitsp" labelOnTop="0"/>
    <field name="valorunitsv" labelOnTop="0"/>
    <field name="x_label" labelOnTop="0"/>
    <field name="y_label" labelOnTop="0"/>
  </labelOnTop>
  <widgets>
    <widget name="98-054 Elche de la Sierra - Letur (Almazarán)_Apellidos">
      <config/>
    </widget>
    <widget name="98-054 Elche de la Sierra - Letur (Almazarán)_Cultivo/1">
      <config/>
    </widget>
    <widget name="98-054 Elche de la Sierra - Letur (Almazarán)_Cultivo/2">
      <config/>
    </widget>
    <widget name="98-054 Elche de la Sierra - Letur (Almazarán)_Cultivo/3">
      <config/>
    </widget>
    <widget name="98-054 Elche de la Sierra - Letur (Almazarán)_D P">
      <config/>
    </widget>
    <widget name="98-054 Elche de la Sierra - Letur (Almazarán)_J P">
      <config/>
    </widget>
    <widget name="98-054 Elche de la Sierra - Letur (Almazarán)_Jurado">
      <config/>
    </widget>
    <widget name="98-054 Elche de la Sierra - Letur (Almazarán)_Justiprecio">
      <config/>
    </widget>
    <widget name="98-054 Elche de la Sierra - Letur (Almazarán)_Nombre">
      <config/>
    </widget>
    <widget name="98-054 Elche de la Sierra - Letur (Almazarán)_Parcela">
      <config/>
    </widget>
    <widget name="98-054 Elche de la Sierra - Letur (Almazarán)_Pol">
      <config/>
    </widget>
    <widget name="98-054 Elche de la Sierra - Letur (Almazarán)_Total Pts">
      <config/>
    </widget>
    <widget name="98-054 Elche de la Sierra - Letur (Almazarán)_Total m2">
      <config/>
    </widget>
    <widget name="98-054 Elche de la Sierra - Letur (Almazarán)_m2/1">
      <config/>
    </widget>
    <widget name="98-054 Elche de la Sierra - Letur (Almazarán)_m2/2">
      <config/>
    </widget>
    <widget name="98-054 Elche de la Sierra - Letur (Almazarán)_m2/3">
      <config/>
    </widget>
    <widget name="BDEXP_APEL">
      <config/>
    </widget>
    <widget name="BDEXP_APEL_C">
      <config/>
    </widget>
    <widget name="BDEXP_APEL_R">
      <config/>
    </widget>
    <widget name="BDEXP_CARTA">
      <config/>
    </widget>
    <widget name="BDEXP_CITA">
      <config/>
    </widget>
    <widget name="BDEXP_CLAVE">
      <config/>
    </widget>
    <widget name="BDEXP_CP">
      <config/>
    </widget>
    <widget name="BDEXP_CTA">
      <config/>
    </widget>
    <widget name="BDEXP_CULT1">
      <config/>
    </widget>
    <widget name="BDEXP_CULT2">
      <config/>
    </widget>
    <widget name="BDEXP_CULT3">
      <config/>
    </widget>
    <widget name="BDEXP_DEPOSITO">
      <config/>
    </widget>
    <widget name="BDEXP_DG">
      <config/>
    </widget>
    <widget name="BDEXP_DIA_PAGO">
      <config/>
    </widget>
    <widget name="BDEXP_DOMI">
      <config/>
    </widget>
    <widget name="BDEXP_E">
      <config/>
    </widget>
    <widget name="BDEXP_ENTI">
      <config/>
    </widget>
    <widget name="BDEXP_FECHA1">
      <config/>
    </widget>
    <widget name="BDEXP_FICHERO">
      <config/>
    </widget>
    <widget name="BDEXP_FINCA">
      <config/>
    </widget>
    <widget name="BDEXP_FOLIO">
      <config/>
    </widget>
    <widget name="BDEXP_HORA">
      <config/>
    </widget>
    <widget name="BDEXP_INS">
      <config/>
    </widget>
    <widget name="BDEXP_JURADO">
      <config/>
    </widget>
    <widget name="BDEXP_JUSTIPRECI">
      <config/>
    </widget>
    <widget name="BDEXP_LIBRO">
      <config/>
    </widget>
    <widget name="BDEXP_LOC">
      <config/>
    </widget>
    <widget name="BDEXP_M2_1">
      <config/>
    </widget>
    <widget name="BDEXP_M2_2">
      <config/>
    </widget>
    <widget name="BDEXP_M2_3">
      <config/>
    </widget>
    <widget name="BDEXP_N">
      <config/>
    </widget>
    <widget name="BDEXP_NIF">
      <config/>
    </widget>
    <widget name="BDEXP_NIF_C">
      <config/>
    </widget>
    <widget name="BDEXP_NIF_R">
      <config/>
    </widget>
    <widget name="BDEXP_NO">
      <config/>
    </widget>
    <widget name="BDEXP_NOM">
      <config/>
    </widget>
    <widget name="BDEXP_NOM_C">
      <config/>
    </widget>
    <widget name="BDEXP_NOM_R">
      <config/>
    </widget>
    <widget name="BDEXP_O">
      <config/>
    </widget>
    <widget name="BDEXP_OBS">
      <config/>
    </widget>
    <widget name="BDEXP_OFIC">
      <config/>
    </widget>
    <widget name="BDEXP_P1">
      <config/>
    </widget>
    <widget name="BDEXP_P2">
      <config/>
    </widget>
    <widget name="BDEXP_P3">
      <config/>
    </widget>
    <widget name="BDEXP_PAGO">
      <config/>
    </widget>
    <widget name="BDEXP_PAR">
      <config/>
    </widget>
    <widget name="BDEXP_POL">
      <config/>
    </widget>
    <widget name="BDEXP_PRV">
      <config/>
    </widget>
    <widget name="BDEXP_PTSM2_1">
      <config/>
    </widget>
    <widget name="BDEXP_PTSM2_2">
      <config/>
    </widget>
    <widget name="BDEXP_PTSM2_3">
      <config/>
    </widget>
    <widget name="BDEXP_PTSUND_1">
      <config/>
    </widget>
    <widget name="BDEXP_PTSUND_2">
      <config/>
    </widget>
    <widget name="BDEXP_PTSUND_3">
      <config/>
    </widget>
    <widget name="BDEXP_RG">
      <config/>
    </widget>
    <widget name="BDEXP_S">
      <config/>
    </widget>
    <widget name="BDEXP_TIT">
      <config/>
    </widget>
    <widget name="BDEXP_TM">
      <config/>
    </widget>
    <widget name="BDEXP_TOMO">
      <config/>
    </widget>
    <widget name="BDEXP_TOTAL_M2">
      <config/>
    </widget>
    <widget name="BDEXP_TOTAL_PTS">
      <config/>
    </widget>
    <widget name="BDEXP_UND_1">
      <config/>
    </widget>
    <widget name="BDEXP_UND_2">
      <config/>
    </widget>
    <widget name="BDEXP_UND_3">
      <config/>
    </widget>
    <widget name="BD_EXPRAPEL">
      <config/>
    </widget>
    <widget name="BD_EXPRAPEL_C">
      <config/>
    </widget>
    <widget name="BD_EXPRAPEL_R">
      <config/>
    </widget>
    <widget name="BD_EXPRCARTA">
      <config/>
    </widget>
    <widget name="BD_EXPRCITA">
      <config/>
    </widget>
    <widget name="BD_EXPRCLAVE">
      <config/>
    </widget>
    <widget name="BD_EXPRCP">
      <config/>
    </widget>
    <widget name="BD_EXPRCTA">
      <config/>
    </widget>
    <widget name="BD_EXPRCULT1">
      <config/>
    </widget>
    <widget name="BD_EXPRCULT2">
      <config/>
    </widget>
    <widget name="BD_EXPRCULT3">
      <config/>
    </widget>
    <widget name="BD_EXPRDEPOSITO">
      <config/>
    </widget>
    <widget name="BD_EXPRDG">
      <config/>
    </widget>
    <widget name="BD_EXPRDIA_PAGO">
      <config/>
    </widget>
    <widget name="BD_EXPRDOMI">
      <config/>
    </widget>
    <widget name="BD_EXPRE">
      <config/>
    </widget>
    <widget name="BD_EXPRENTI">
      <config/>
    </widget>
    <widget name="BD_EXPRFECHA1">
      <config/>
    </widget>
    <widget name="BD_EXPRFICHERO">
      <config/>
    </widget>
    <widget name="BD_EXPRFINCA">
      <config/>
    </widget>
    <widget name="BD_EXPRFOLIO">
      <config/>
    </widget>
    <widget name="BD_EXPRField66">
      <config/>
    </widget>
    <widget name="BD_EXPRField67">
      <config/>
    </widget>
    <widget name="BD_EXPRField68">
      <config/>
    </widget>
    <widget name="BD_EXPRField69">
      <config/>
    </widget>
    <widget name="BD_EXPRField70">
      <config/>
    </widget>
    <widget name="BD_EXPRField71">
      <config/>
    </widget>
    <widget name="BD_EXPRField72">
      <config/>
    </widget>
    <widget name="BD_EXPRField73">
      <config/>
    </widget>
    <widget name="BD_EXPRField74">
      <config/>
    </widget>
    <widget name="BD_EXPRField75">
      <config/>
    </widget>
    <widget name="BD_EXPRField76">
      <config/>
    </widget>
    <widget name="BD_EXPRField77">
      <config/>
    </widget>
    <widget name="BD_EXPRField78">
      <config/>
    </widget>
    <widget name="BD_EXPRField79">
      <config/>
    </widget>
    <widget name="BD_EXPRField80">
      <config/>
    </widget>
    <widget name="BD_EXPRHORA">
      <config/>
    </widget>
    <widget name="BD_EXPRINS">
      <config/>
    </widget>
    <widget name="BD_EXPRJURADO">
      <config/>
    </widget>
    <widget name="BD_EXPRJUSTIPRECI">
      <config/>
    </widget>
    <widget name="BD_EXPRLIBRO">
      <config/>
    </widget>
    <widget name="BD_EXPRLOC">
      <config/>
    </widget>
    <widget name="BD_EXPRM2_1">
      <config/>
    </widget>
    <widget name="BD_EXPRM2_2">
      <config/>
    </widget>
    <widget name="BD_EXPRM2_3">
      <config/>
    </widget>
    <widget name="BD_EXPRN">
      <config/>
    </widget>
    <widget name="BD_EXPRNIF">
      <config/>
    </widget>
    <widget name="BD_EXPRNIF_C">
      <config/>
    </widget>
    <widget name="BD_EXPRNIF_R">
      <config/>
    </widget>
    <widget name="BD_EXPRNO">
      <config/>
    </widget>
    <widget name="BD_EXPRNOM">
      <config/>
    </widget>
    <widget name="BD_EXPRNOM_C">
      <config/>
    </widget>
    <widget name="BD_EXPRNOM_R">
      <config/>
    </widget>
    <widget name="BD_EXPRO">
      <config/>
    </widget>
    <widget name="BD_EXPROBS">
      <config/>
    </widget>
    <widget name="BD_EXPROFIC">
      <config/>
    </widget>
    <widget name="BD_EXPRP1">
      <config/>
    </widget>
    <widget name="BD_EXPRP2">
      <config/>
    </widget>
    <widget name="BD_EXPRP3">
      <config/>
    </widget>
    <widget name="BD_EXPRPAGO">
      <config/>
    </widget>
    <widget name="BD_EXPRPAR">
      <config/>
    </widget>
    <widget name="BD_EXPRPOL">
      <config/>
    </widget>
    <widget name="BD_EXPRPRV">
      <config/>
    </widget>
    <widget name="BD_EXPRPTSM2_1">
      <config/>
    </widget>
    <widget name="BD_EXPRPTSM2_2">
      <config/>
    </widget>
    <widget name="BD_EXPRPTSM2_3">
      <config/>
    </widget>
    <widget name="BD_EXPRPTSUND_1">
      <config/>
    </widget>
    <widget name="BD_EXPRPTSUND_2">
      <config/>
    </widget>
    <widget name="BD_EXPRPTSUND_3">
      <config/>
    </widget>
    <widget name="BD_EXPRRG">
      <config/>
    </widget>
    <widget name="BD_EXPRS">
      <config/>
    </widget>
    <widget name="BD_EXPRTIT">
      <config/>
    </widget>
    <widget name="BD_EXPRTM">
      <config/>
    </widget>
    <widget name="BD_EXPRTOMO">
      <config/>
    </widget>
    <widget name="BD_EXPRTOTAL_M2">
      <config/>
    </widget>
    <widget name="BD_EXPRTOTAL_PTS">
      <config/>
    </widget>
    <widget name="BD_EXPRUND_1">
      <config/>
    </widget>
    <widget name="BD_EXPRUND_2">
      <config/>
    </widget>
    <widget name="BD_EXPRUND_3">
      <config/>
    </widget>
  </widgets>
  <previewExpression>COALESCE( "SUP_MEDIDA", '&lt;NULL>' )</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>2</layerGeometryType>
</qgis>
