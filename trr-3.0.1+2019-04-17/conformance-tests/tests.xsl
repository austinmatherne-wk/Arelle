<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet 
  version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:case="http://xbrl.org/2011/conformance-rendering/transforms" 
  xmlns:s="http://xbrl.org/conformance/2008/specifications"
  xmlns:xh="http://www.w3.org/1999/xhtml"
  >

  
<xsl:template match="/">
<xsl:apply-templates select="case:testcase"/>
</xsl:template>  
  
<xsl:template match="case:testcase">
  <html>
    <head>
      <title>
        Conformance test for 
        <xsl:value-of select="@target" />
      </title>
    </head>
    <body>
        
      <h1>
        Conformance test for 
        <xsl:value-of select="@target" />
      </h1>

      <h2>
        Variations
      </h2>
      
      <table border="solid" width="100%">
        <thead>
          <tr>
            <th>Name</th>
            <th>Output Type</th>
            <th>Input</th>
            <th>Expected Output</th>
            <th>Result</th>
          </tr>
        </thead>
        <tbody>
          <xsl:apply-templates select="case:transform" />
        </tbody>
      </table>
    </body>
  </html>
</xsl:template>

<xsl:template match="case:transform">
  <xsl:apply-templates select="case:variation" >
    <xsl:with-param name="name" select="@name" />
    <xsl:with-param name="type" select="@outputType" />
  </xsl:apply-templates>
</xsl:template>
    
<xsl:template match="case:variation">
  <xsl:param name="name">not found</xsl:param>
  <xsl:param name="type">not found</xsl:param>
  <tr>
    <td>
      <xsl:value-of select="$name"/>
    </td>
    <td>
      <xsl:value-of select="$type"/>
    </td>
    <td>
      <xsl:value-of select="@input"/>
    </td>
    <td>
      <xsl:value-of select="@output"/>
    </td>
    <td>
      <xsl:value-of select="@result"/>
    </td>
  </tr>
</xsl:template>


</xsl:stylesheet>
