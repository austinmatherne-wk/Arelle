<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet 
  version="2.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:case="http://xbrl.org/2011/conformance-rendering/transforms" 
  xmlns:s="http://xbrl.org/conformance/2008/specifications"
  xmlns:ixt="http://www.xbrl.org/inlineXBRL/transformation/2015-02-26" 
  xmlns:saxon="http://saxon.sf.net/"
  xmlns:xh="http://www.w3.org/1999/xhtml"
  >

<xsl:include href="ixt-reference-transforms.xsl"/>
  
<xsl:template match="/">
<xsl:apply-templates select="case:testcase"/>
</xsl:template>  
  
<xsl:template match="case:testcase">
  <xsl:variable name="root" select="."/>
  <html>
    <head>
      <title>
        Conformance test for <xsl:value-of select="namespace-uri-for-prefix('ixt', .)"/>
      </title>
    </head>
    <body>
        
      <h1>
        Conformance test for <xsl:value-of select="namespace-uri-for-prefix('ixt', .)"/>
      </h1>

      <table border="solid" width="100%">
        <tbody>
          <xsl:for-each select="case:transform">
            <tr><td colspan="4"><br/><h3><xsl:value-of select="@name"/>&#xA0;<small><i>[&#x2192; <xsl:value-of select="@outputType" />]</i></small></h3></td></tr>
            <tr>
              <th>Variation</th>
              <th>Input</th>
              <th>Expected Output</th>
              <th>Result</th>
            </tr>
            <xsl:apply-templates select="case:variation" >
              <xsl:with-param name="name" select="@name" />
            </xsl:apply-templates>
          </xsl:for-each>
        </tbody>
      </table>
    </body>
  </html>
</xsl:template>

<xsl:template match="case:variation">
  <xsl:param name="name">not found</xsl:param>
  <tr>
    <td>
      <xsl:value-of select="@description" />
    </td>
    <td>
      <xsl:value-of select="@input"/>
    </td>
    <td>
<!--
      <xsl:value-of select="@output"/> 
-->
      <xsl:choose>
        <xsl:when test="@result eq 'valid'">
          <xsl:value-of select="@output"/> 
        </xsl:when>
        <xsl:otherwise>
          <span style="background-color: Yellow">INVALID</span>
        </xsl:otherwise>
      </xsl:choose>
    </td>
    <td>
      <xsl:variable name="actualOutput" select="saxon:evaluate(concat($name,'(@input)'))"/>
<!--
      <xsl:choose>
        <xsl:when test="@result eq 'valid' and @output eq $actualOutput">
          <span style="background-color: LightGreen">PASS</span>
        </xsl:when>
        <xsl:when test="@result eq 'invalid'">
          <span style="background-color: LightBlue">SKIPPED</span>
        </xsl:when>
        <xsl:otherwise>
          <span style="background-color: IndianRed">FAIL</span>: <i><xsl:value-of select="$actualOutput"/></i>
        </xsl:otherwise>
      </xsl:choose>
-->
      <span style="background-color: IndianRed">FAIL</span>: <i><xsl:value-of select="$actualOutput"/></i>

    </td>
  </tr>
</xsl:template>


</xsl:stylesheet>
