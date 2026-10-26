<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet 
  version="2.0" 
  xmlns:case="http://xbrl.org/2011/conformance-rendering/transforms" 
  xmlns:ixt="http://www.xbrl.org/inlineXBRL/transformation/2015-02-26"
  xmlns:reg="http://xbrl.org/2008/registry"
  xmlns:xs="http://www.w3.org/2001/XMLSchema"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:func="http://xbrl.org/2008/function"
  
  >
<xsl:output indent="yes"/>
<xsl:param name="result"/>
<xsl:template match="/">
  <case:variations xsi:schemaLocation="http://www.xbrl.org/inlineXBRL/transformation/2015-02-26 ../schema/inlinexbrl-3_0-transformation.xsd http://xbrl.org/2011/conformance-rendering/transforms tests.xsd">
    <xsl:attribute name="result">
      <xsl:value-of select="$result"/>
    </xsl:attribute>
    <xsl:for-each select="case:testcase/case:transform/case:variation[@result=$result]">
      <case:input> 
        <xsl:attribute name="xsi:type">
          <xsl:variable name="transformLocalName" select="substring-after(../@name, ':')"/>
          <xsl:variable name="registryDoc" select="concat('../registry/ixt-', concat($transformLocalName, '.xml'))"/>
          <xsl:value-of select="document($registryDoc)/func:function/func:signature/func:input/@type"/>
        </xsl:attribute>
        <xsl:value-of select="@input"/>
      </case:input> 
    </xsl:for-each>
  </case:variations>
</xsl:template>

</xsl:stylesheet>
