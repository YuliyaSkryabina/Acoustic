<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.28" styleCategories="AllStyleCategories">
  <renderer-v2 attr="level_dba" forceraster="0" graduatedMode="0" type="graduatedSymbol" enableorderby="0" symbollevels="0">
    <ranges>
      <range symbol="0" lower="0" upper="35" label="до 35 дБА" render="true"/>
      <range symbol="1" lower="35" upper="40" label="35–40 дБА" render="true"/>
      <range symbol="2" lower="40" upper="45" label="40–45 дБА" render="true"/>
      <range symbol="3" lower="45" upper="50" label="45–50 дБА" render="true"/>
      <range symbol="4" lower="50" upper="55" label="50–55 дБА (ПДУ ночь)" render="true"/>
      <range symbol="5" lower="55" upper="60" label="55–60 дБА (ПДУ день)" render="true"/>
      <range symbol="6" lower="60" upper="65" label="60–65 дБА" render="true"/>
      <range symbol="7" lower="65" upper="70" label="65–70 дБА" render="true"/>
      <range symbol="8" lower="70" upper="80" label="70–80 дБА" render="true"/>
      <range symbol="9" lower="80" upper="999" label="свыше 80 дБА" render="true"/>
    </ranges>
    <symbols>
      <symbol name="0" type="line" force_rhr="0" alpha="0.8">
        <layer class="SimpleLine">
          <prop k="line_color" v="33,150,243,204"/>
          <prop k="line_width" v="0.5"/>
          <prop k="line_style" v="solid"/>
        </layer>
      </symbol>
      <symbol name="1" type="line" force_rhr="0" alpha="0.8">
        <layer class="SimpleLine">
          <prop k="line_color" v="66,165,245,204"/>
          <prop k="line_width" v="0.5"/>
        </layer>
      </symbol>
      <symbol name="2" type="line" force_rhr="0" alpha="0.8">
        <layer class="SimpleLine">
          <prop k="line_color" v="76,175,80,204"/>
          <prop k="line_width" v="0.7"/>
        </layer>
      </symbol>
      <symbol name="3" type="line" force_rhr="0" alpha="0.8">
        <layer class="SimpleLine">
          <prop k="line_color" v="139,195,74,204"/>
          <prop k="line_width" v="0.7"/>
        </layer>
      </symbol>
      <symbol name="4" type="line" force_rhr="0" alpha="0.9">
        <layer class="SimpleLine">
          <prop k="line_color" v="205,220,57,230"/>
          <prop k="line_width" v="1.0"/>
        </layer>
      </symbol>
      <symbol name="5" type="line" force_rhr="0" alpha="0.9">
        <layer class="SimpleLine">
          <prop k="line_color" v="255,193,7,230"/>
          <prop k="line_width" v="1.2"/>
        </layer>
      </symbol>
      <symbol name="6" type="line" force_rhr="0" alpha="0.9">
        <layer class="SimpleLine">
          <prop k="line_color" v="255,112,67,230"/>
          <prop k="line_width" v="1.5"/>
        </layer>
      </symbol>
      <symbol name="7" type="line" force_rhr="0" alpha="1.0">
        <layer class="SimpleLine">
          <prop k="line_color" v="244,67,54,255"/>
          <prop k="line_width" v="1.5"/>
        </layer>
      </symbol>
      <symbol name="8" type="line" force_rhr="0" alpha="1.0">
        <layer class="SimpleLine">
          <prop k="line_color" v="183,28,28,255"/>
          <prop k="line_width" v="2.0"/>
        </layer>
      </symbol>
      <symbol name="9" type="line" force_rhr="0" alpha="1.0">
        <layer class="SimpleLine">
          <prop k="line_color" v="74,20,140,255"/>
          <prop k="line_width" v="2.5"/>
        </layer>
      </symbol>
    </symbols>
    <source-symbol>
      <symbol name="0" type="line"/>
    </source-symbol>
    <colorramp name="[source]" type="gradient">
      <prop k="color1" v="33,150,243,255"/>
      <prop k="color2" v="183,28,28,255"/>
    </colorramp>
    <labelformat format="%1 дБА" trimtrailingzeroes="true" decimalplaces="0"/>
  </renderer-v2>
  <labeling type="simple">
    <settings calloutType="simple">
      <text-style fontFamily="Arial" fontSize="8" textColor="50,50,50,255"/>
      <placement placement="2"/>
    </settings>
  </labeling>
</qgis>
