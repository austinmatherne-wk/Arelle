<?xml version="1.0" encoding="UTF-8"?>
<!--
  Inline XBRL Transformations

  Requires XSLT 2.0 and only tested with the Saxon 8B XSLT engine.
  
  xmlns:ixt="http://www.xbrl.org/inlineXBRL/transformation/2015-02-26" 
  
  NOTE: Scale transform is not applied to numeric values.
        This can be added by wrapping $result as follows:
          <xsl:value-of select="$result"/>
        with:
          <xsl:value-of select="ixt:applyscale(.,$result)"/>
  
  NOTE: Any changes to the ixt namespace needs to be matched in the hardcoded
        namespace string found in the ixt:test() function.

-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0"
  xmlns:ix   ="http://www.xbrl.org/2008/inlineXBRL"
  xmlns:ixt="http://www.xbrl.org/inlineXBRL/transformation/2015-02-26" 
  xmlns:ixh="http://www.xbrl.org/inlineXBRL/transformation/helper-functions"
  xmlns:xhtml="http://www.w3.org/1999/xhtml"
  xmlns:xs="http://www.w3.org/2001/XMLSchema" 
  xmlns:xbrli="http://www.xbrl.org/2003/instance">

  <xsl:output media-type="text/xml" indent="yes"/>

  <!-- ########################################## TRANSFORMATION TEMPLATES -->

  <xsl:template match="
    ix:numerator[ @ix:format ] |
    ix:denominator[ @ix:format ] |
    ix:nonFraction[ @ix:format ] |
    ix:nonNumeric[ @ix:format ]" 
    mode="contentxform">
    <xsl:variable name="ns" select="namespace-uri-for-prefix(substring-before(@ix:format,':'), .)"/>
    <xsl:variable name="lname" select="substring-after(@ix:format,':')"/>
    <xsl:variable name="transform" select="QName($ns, $lname)" as="xs:QName"/>
    <xsl:variable name="input" select="./text()"/>
    <xsl:choose>
      <xsl:when test="$transform eq xs:QName('ixt:booleanfalse')"><xsl:value-of select="ixt:booleanfalse($input)"/></xsl:when>
      <xsl:when test="$transform eq xs:QName('ixt:booleantrue')"><xsl:value-of select="ixt:booleantrue($input)"/></xsl:when>
      <xsl:when test="$transform eq xs:QName('ixt:datedaymonth')"><xsl:value-of select="ixt:datedaymonth($input)"/></xsl:when>
      <xsl:when test="$transform eq xs:QName('ixt:datedaymonthdk')"><xsl:value-of select="ixt:datedaymonthdk($input)"/></xsl:when>
      <xsl:when test="$transform eq xs:QName('ixt:datedaymonthen')"><xsl:value-of select="ixt:datedaymonthen($input)"/></xsl:when>
      <xsl:when test="$transform eq xs:QName('ixt:datedaymonthyear')"><xsl:value-of select="ixt:datedaymonthyear($input)"/></xsl:when>
      <xsl:when test="$transform eq xs:QName('ixt:datedaymonthyeardk')"><xsl:value-of select="ixt:datedaymonthyeardk($input)"/></xsl:when>
      <xsl:when test="$transform eq xs:QName('ixt:datedaymonthyearen')"><xsl:value-of select="ixt:datedaymonthyearen($input)"/></xsl:when>
      <xsl:when test="$transform eq xs:QName('ixt:dateerayearmonthdayjp')"><xsl:value-of select="ixt:dateerayearmonthdayjp($input)"/></xsl:when>
      <xsl:when test="$transform eq xs:QName('ixt:dateerayearmonthjp')"><xsl:value-of select="ixt:dateerayearmonthjp($input)"/></xsl:when>
      <xsl:when test="$transform eq xs:QName('ixt:datemonthday')"><xsl:value-of select="ixt:datemonthday($input)"/></xsl:when>
      <xsl:when test="$transform eq xs:QName('ixt:datemonthdayen')"><xsl:value-of select="ixt:datemonthdayen($input)"/></xsl:when>
      <xsl:when test="$transform eq xs:QName('ixt:datemonthdayyear')"><xsl:value-of select="ixt:datemonthdayyear($input)"/></xsl:when>
      <xsl:when test="$transform eq xs:QName('ixt:datemonthdayyearen')"><xsl:value-of select="ixt:datemonthdayyearen($input)"/></xsl:when>
      <xsl:when test="$transform eq xs:QName('ixt:datemonthyeardk')"><xsl:value-of select="ixt:datemonthyeardk($input)"/></xsl:when>
      <xsl:when test="$transform eq xs:QName('ixt:datemonthyearen')"><xsl:value-of select="ixt:datemonthyearen($input)"/></xsl:when>
      <xsl:when test="$transform eq xs:QName('ixt:dateyearmonthcjk')"><xsl:value-of select="ixt:dateyearmonthcjk($input)"/></xsl:when>
      <xsl:when test="$transform eq xs:QName('ixt:dateyearmonthdaycjk')"><xsl:value-of select="ixt:dateyearmonthdaycjk($input)"/></xsl:when>
      <xsl:when test="$transform eq xs:QName('ixt:dateyearmonthen')"><xsl:value-of select="ixt:dateyearmonthen($input)"/></xsl:when>
      <xsl:when test="$transform eq xs:QName('ixt:nocontent')"><xsl:value-of select="ixt:nocontent($input)"/></xsl:when>
      <xsl:when test="$transform eq xs:QName('ixt:zerodash')"><xsl:value-of select="ixt:zerodash($input)"/></xsl:when>
      <xsl:when test="$transform eq xs:QName('ixt:numcommadecimal')"><xsl:value-of select="ixt:numcommadecimal($input)"/></xsl:when>
      <xsl:when test="$transform eq xs:QName('ixt:numunitdecimal')"><xsl:value-of select="ixt:numunitdecimal($input)"/></xsl:when>
      <xsl:when test="$transform eq xs:QName('ixt:numdotdecimal')"><xsl:value-of select="ixt:numdotdecimal($input)"/></xsl:when>
      <xsl:when test="$transform eq xs:QName('ixt:dateyearmonthday')"><xsl:value-of select="ixt:dateyearmonthday($input)"/></xsl:when>
      <xsl:otherwise>ERROR: unmatched transform '<xsl:value-of select="$transform"/>'</xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
       ===================================
        FORMAT CODE: booleanfalse
       =================================== 
        input:      *
        output:     false
   -->  
  <xsl:function name="ixt:booleanfalse">
    <xsl:param name="input"/>
    <xsl:text>false</xsl:text>
  </xsl:function>

  <!--
       ===================================
        FORMAT CODE: booleantrue
       =================================== 
        input:      *
        output:     true
   -->  
  <xsl:function name="ixt:booleantrue">
    <xsl:param name="input"/>
    <xsl:text>true</xsl:text>
  </xsl:function>

  <!--
       ===================================
        FORMAT CODE: datemonthdayyear
       ===================================
        input:      MM/DD/YY(YY)
        output:     YYYY-MM-DD
    
    No validation is done of the input string.  If an invalid US
    date is supplied, the behaviour is undefined.
    
    e.g. ixt:dateslashus "3/24/08" will output "2008-03-24".
    
    NOTE: If input is only "YY", then "20" is prepended
          (year assumed to be in 21st century)
  -->
  <xsl:function name="ixt:datemonthdayyear">
    <xsl:param name="input"/>
      <xsl:analyze-string select="$input" regex="([0-9]+)(/|\.)([0-9]+)(/|\.)([0-9]+)">
      <xsl:matching-substring>
        <xsl:value-of select="ixh:buildxsddate(regex-group(5), regex-group(1), regex-group(3))"/>
      </xsl:matching-substring>
      </xsl:analyze-string>
  </xsl:function>
  
  <!--
       ===================================
        FORMAT CODE: datedaymonthyear
       ===================================
        input:      DD/MM/YY(YY)
        output:     YYYY-MM-DD
        
        No validation is done of the input string.  If an invalid EU
        date is supplied, the behaviour is undefined.
        
        e.g. ixt:dateslasheu "24/3/08" will output "2008-03-24".
    
    NOTE: If input is only "YY", then "20" is prepended
          (year assumed to be in 21st century)
  -->
  <xsl:function name="ixt:datedaymonthyear">
    <xsl:param name="input"/>
    <xsl:analyze-string select="$input" regex="([0-9]+)(/|\.)([0-9]+)(/|\.)([0-9]+)">
      <xsl:matching-substring>
        <xsl:value-of select="ixh:buildxsddate(regex-group(5), regex-group(3), regex-group(1))"/>
      </xsl:matching-substring>
    </xsl:analyze-string>
  </xsl:function>
  
  <!--
       ===================================
        FORMAT CODE: datedaymonth
       ===================================
        input:      DD/MM
        output:     - -MM-DD
        
        No validation is done of the input string.  If an invalid EU
        date is supplied, the behaviour is undefined.
        
        e.g. ixt:datedaymonth "24/3" will output "- -03-24".
    
    NOTE: If input is only "YY", then "20" is prepended
          (year assumed to be in 21st century)
  -->
  <xsl:function name="ixt:datedaymonth">
    <xsl:param name="input"/>
    <xsl:analyze-string select="$input" regex="([0-9]+)[^0-9]+([0-9]+)">
      <xsl:matching-substring>
        <xsl:value-of select="ixh:buildxsdgmonthdate(regex-group(2), regex-group(1))"/>
      </xsl:matching-substring>
    </xsl:analyze-string>
  </xsl:function>

  <!--
       ===================================
        FORMAT CODE: datemonthday
       ===================================
        input:      MM/DD
        output:     - -MM-DD
        
        No validation is done of the input string.  If an invalid EU
        date is supplied, the behaviour is undefined.
        
        e.g. ixt:datedaymonth "3/24" will output "- -03-24".
    
    NOTE: If input is only "YY", then "20" is prepended
          (year assumed to be in 21st century)
  -->
  <xsl:function name="ixt:datemonthday">
    <xsl:param name="input"/>
    <xsl:analyze-string select="$input" regex="([0-9]+)[^0-9]+([0-9]+)">
      <xsl:matching-substring>
        <xsl:value-of select="ixh:buildxsdgmonthdate(regex-group(1), regex-group(2))"/>
      </xsl:matching-substring>
    </xsl:analyze-string>
  </xsl:function>

  <!-- 
       ===================================
        FORMAT CODE: datemonthdayyearen
       ===================================
        input:      month-full DD, YYYY
        output:     YYYY-MM-DD

        No validation is done of the input string.  If an invalid US
        date is supplied, the behaviour is undefined.
        
        e.g. ixt:datelongus "March 24, 2008" will output "2008-03-24".
        
        NOTE: If input is only "YY", then "20" is prepended
              (year assumed to be in 21st century)
  -->
  <xsl:function name="ixt:datemonthdayyearen">
    <xsl:param name="input"/>
    <xsl:analyze-string select="$input" regex="(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)[^0-9]+([0-9]+)[^0-9]+([0-9]+)">
      <xsl:matching-substring>
        <xsl:value-of select="ixh:buildxsddate(regex-group(3), regex-group(1), regex-group(2))"/>
      </xsl:matching-substring>
    </xsl:analyze-string>
  </xsl:function>

  <!-- 
       ===================================
        FORMAT CODE: datemonthdayen
       ===================================
        input:      month-full DD
        output:     - -MM-DD

        No validation is done of the input string.  If an invalid US
        date is supplied, the behaviour is undefined.
        
        e.g. ixt:datelongus "March 24" will output "- -03-24".
        
        NOTE: If input is only "YY", then "20" is prepended
              (year assumed to be in 21st century)
  -->
  <xsl:function name="ixt:datemonthdayen">
    <xsl:param name="input"/>
    <xsl:analyze-string select="$input" regex="(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)[^0-9]+([0-9]+)">
      <xsl:matching-substring>
        <xsl:value-of select="ixh:buildxsdgmonthdate(regex-group(1), regex-group(2))"/>
      </xsl:matching-substring>
    </xsl:analyze-string>
  </xsl:function>
  
  <!-- 
       ===================================
        FORMAT CODE: datedaymonthyeardk
       ===================================
        input:      DD month-atLeastPartial YY(YY)
        output:     YYYY-MM-DD
      
        No validation is done of the input string.  If an invalid
        date is supplied, the behaviour is undefined.
        
        NOTE: If input is only "YY", then "20" is prepended
              (year assumed to be in 21st century)
  -->
  <xsl:function name="ixt:datedaymonthyeardk">
    <xsl:param name="input"/>
    <xsl:analyze-string select="$input" regex="([0-9]+)[^0-9]+(jan|feb|mar|apr|maj|jun|jul|aug|sep|okt|nov|dec|JAN|FEB|MAR|APR|MAJ|JUN|JUL|AUG|SEP|OKT|NOV|DEC|Jan|Feb|Mar|Apr|Maj|Jun|Jul|Aug|Sep|Okt|Nov|Dec)[^0-9]+([0-9]+)">
      <xsl:matching-substring>
<!--        <xsl:value-of select="ixh:buildxsddate(regex-group(3), regex-group(2), regex-group(1))"/> -->
        <xsl:value-of select="concat(regex-group(3), concat(regex-group(2), regex-group(1)))"/>
      </xsl:matching-substring>
    </xsl:analyze-string>
  </xsl:function>

  <!-- 
       ===================================
        FORMAT CODE: datedaymonthyearen
       ===================================
        input:      DD month-full YY(YY)
        output:     YYYY-MM-DD
      
        No validation is done of the input string.  If an invalid
        date is supplied, the behaviour is undefined.
        
        NOTE: If input is only "YY", then "20" is prepended
              (year assumed to be in 21st century)
  -->
  <xsl:function name="ixt:datedaymonthyearen">
    <xsl:param name="input"/>
    <xsl:analyze-string select="$input" regex="([0-9]+)[^0-9]+(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)[^0-9]+([0-9]+)">
      <xsl:matching-substring>
        <xsl:value-of select="ixh:buildxsddate(regex-group(3), regex-group(2), regex-group(1))"/>
      </xsl:matching-substring>
    </xsl:analyze-string>
  </xsl:function>

  <!-- 
       ===================================
        FORMAT CODE: datemonthyeardk
       ===================================
        input:      month-atLeastPartial YY(YY)
        output:     YYYY-MM
      
        No validation is done of the input string.  If an invalid
        date is supplied, the behaviour is undefined.
        
        NOTE: If input is only "YY", then "20" is prepended
              (year assumed to be in 21st century)
  -->
  <xsl:function name="ixt:datemonthyeardk">
    <xsl:param name="input"/>
    <xsl:analyze-string select="$input" regex="(jan|feb|mar|apr|maj|jun|jul|aug|sep|okt|nov|dec|JAN|FEB|MAR|APR|MAJ|JUN|JUL|AUG|SEP|OKT|NOV|DEC|Jan|Feb|Mar|Apr|Maj|Jun|Jul|Aug|Sep|Okt|Nov|Dec)[^0-9]+([0-9]+)">
      <xsl:matching-substring>
<!--        <xsl:value-of select="ixh:buildxsdgyearmonth(regex-group(2), regex-group(1))"/> -->
        <xsl:value-of select="concat(regex-group(2), regex-group(1))"/>
      </xsl:matching-substring>
    </xsl:analyze-string>
  </xsl:function>

  <!-- 
       ===================================
        FORMAT CODE: datemonthyearen
       ===================================
        input:      month-full YY(YY)
        output:     YYYY-MM
      
        No validation is done of the input string.  If an invalid 
        date is supplied, the behaviour is undefined.
        
        NOTE: If input is only "YY", then "20" is prepended
              (year assumed to be in 21st century)
  -->
  <xsl:function name="ixt:datemonthyearen">
    <xsl:param name="input"/>
    <xsl:analyze-string select="$input" regex="(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)[^0-9]+([0-9]+)">
      <xsl:matching-substring>
        <xsl:value-of select="ixh:buildxsdgyearmonth(regex-group(2), regex-group(1))"/>
      </xsl:matching-substring>
    </xsl:analyze-string>
  </xsl:function>

  <!-- 
       ===================================
        FORMAT CODE: dateyearmonthcjk
       ===================================
        input:      YY(YY)年 MM月
        output:     YYYY-MM
      
        No validation is done of the input string.  If an invalid CJK
        date is supplied, the behaviour is undefined.
        
        e.g. ixt:datelongeu "2008年3月" will output "2008-03".
        
        NOTE: If input is only "YY", then "20" is prepended
              (year assumed to be in 21st century)
  -->
  <xsl:function name="ixt:dateyearmonthcjk">
    <xsl:param name="input"/>
    <xsl:analyze-string select="ixh:full-width-digits-to-normal($input)" regex="([0-9]+)[\s&#xA0;]*年[\s&#xA0;]*([0-9]+)[\s&#xA0;]*月">
      <xsl:matching-substring>
        <xsl:value-of select="ixh:buildxsdgyearmonth(regex-group(1), regex-group(2))"/>
      </xsl:matching-substring>
    </xsl:analyze-string>
  </xsl:function>

  <!-- 
       ===================================
        FORMAT CODE: dateyearmonthdaycjk
       ===================================
        input:      YY(YY)年 MM月 DD日
        output:     YYYY-MM-DD
      
        No validation is done of the input string.  If an invalid CJK
        date is supplied, the behaviour is undefined.
        
        e.g. ixt:datelongeu "2008年3月24日" will output "2008-03-24".
        
        NOTE: If input is only "YY", then "20" is prepended
              (year assumed to be in 21st century)
  -->
  <xsl:function name="ixt:dateyearmonthdaycjk">
    <xsl:param name="input"/>
    <xsl:analyze-string select="ixh:full-width-digits-to-normal($input)" regex="([0-9]+)[\s&#xA0;]*年[\s&#xA0;]*([0-9]+)[\s&#xA0;]*月[\s&#xA0;]*([0-9]+)[\s&#xA0;]*日">
      <xsl:matching-substring>
        <xsl:value-of select="ixh:buildxsddate(regex-group(1), regex-group(2), regex-group(3))"/>
      </xsl:matching-substring>
    </xsl:analyze-string>
  </xsl:function>
  <!-- 
       ===================================
        FORMAT CODE: dateerayearmonthjp
       ===================================
        input:      元号YY年 MM月
        output:     YYYY-MM
      
        No validation is done of the input string.  If an invalid JP
        date is supplied, the behaviour is undefined.
        
        e.g. ixt:dateerayearmonthjp "令和2年2月" will output "2020-02".
        
  -->
  <xsl:function name="ixt:dateerayearmonthjp">
    <xsl:param name="input"/>
    <xsl:analyze-string select="ixh:full-width-digits-to-normal($input)" regex="(明治|明|大正|大|昭和|昭|平成|平|令和|令)[\s&#xA0;]*([0-9]*|元)[\s&#xA0;]*年[\s&#xA0;]*([0-9]*)[\s&#xA0;]*月">
      <xsl:matching-substring>
        <xsl:value-of select="ixh:buildxsdgyearmonth2(regex-group(1), regex-group(2), regex-group(3))"/>
      </xsl:matching-substring>
    </xsl:analyze-string>
  </xsl:function>

  <!-- 
       ===================================
        FORMAT CODE: dateerayearmonthdayjp
       ===================================
        input:      元号YY年 MM月 DD日
        output:     YYYY-MM-DD
      
        No validation is done of the input string.  If an invalid JP
        date is supplied, the behaviour is undefined.
        
        e.g. ixt:dateerayearmonthdayjp "令和2年2月10日" will output "2020-02-10".
        
  -->
  <xsl:function name="ixt:dateerayearmonthdayjp">
    <xsl:param name="input"/>
    <xsl:analyze-string select="ixh:full-width-digits-to-normal($input)" 
                        regex="(明治|明|大正|大|昭和|昭|平成|平|令和|令)[\s&#xA0;]*([0-9]*|元)[\s&#xA0;]*年[\s&#xA0;]*([0-9]*)[\s&#xA0;]*月[\s&#xA0;]*([0-9]*)[\s&#xA0;]*日">
      <xsl:matching-substring>
        <xsl:value-of select="ixh:buildxsdgyearmonthday2(regex-group(1), regex-group(2), regex-group(3), regex-group(4))"/>
      </xsl:matching-substring>
    </xsl:analyze-string>
  </xsl:function>

  <!-- 
       ===================================
        FORMAT CODE: dateyearmonthen
       ===================================
        input:      YY(YY) month-full
        output:     YYYY-MM
      
        No validation is done of the input string.  If an invalid EU
        date is supplied, the behaviour is undefined.
        
        e.g. ixt:datelongeu "2008 March" will output "2008-03".
        
        NOTE: If input is only "YY", then "20" is prepended
              (year assumed to be in 21st century)
  -->
  <xsl:function name="ixt:dateyearmonthen">
    <xsl:param name="input"/>
    <xsl:analyze-string select="$input" regex="([0-9]+)[^0-9]+(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)">
      <xsl:matching-substring>
        <xsl:value-of select="ixh:buildxsdgyearmonth(regex-group(1), regex-group(2))"/>
      </xsl:matching-substring>
    </xsl:analyze-string>
  </xsl:function>

  <!-- 
       ===================================
        FORMAT CODE: datedaymonthdk
       ===================================
        input:      DD month-atLeastPartial
        output:     - -MM-DD
      
        No validation is done of the input string.  If an invalid 
        date is supplied, the behaviour is undefined.
        
        NOTE: If input is only "YY", then "20" is prepended
              (year assumed to be in 21st century)
  -->
  <xsl:function name="ixt:datedaymonthdk">
    <xsl:param name="input"/>
    <xsl:analyze-string select="$input" regex="([0-9]+)[^0-9]+(jan|feb|mar|apr|maj|jun|jul|aug|sep|okt|nov|dec|JAN|FEB|MAR|APR|MAJ|JUN|JUL|AUG|SEP|OKT|NOV|DEC|Jan|Feb|Mar|Apr|Maj|Jun|Jul|Aug|Sep|Okt|Nov|Dec)$">
      <xsl:matching-substring>
<!--        <xsl:value-of select="ixh:buildxsdgmonthdate(regex-group(2), regex-group(1))"/> -->
        <xsl:value-of select="concat(regex-group(2), regex-group(1))"/>
      </xsl:matching-substring>
    </xsl:analyze-string>
  </xsl:function>

  <!-- 
       ===================================
        FORMAT CODE: datedaymonthen
       ===================================
        input:      DD month-full
        output:     - -MM-DD
      
        No validation is done of the input string.  If an invalid 
        date is supplied, the behaviour is undefined.
        
        NOTE: If input is only "YY", then "20" is prepended
              (year assumed to be in 21st century)
  -->
  <xsl:function name="ixt:datedaymonthen">
    <xsl:param name="input"/>
    <xsl:analyze-string select="$input" regex="([0-9]+)[^0-9]+(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)">
      <xsl:matching-substring>
        <xsl:value-of select="ixh:buildxsdgmonthdate(regex-group(2), regex-group(1))"/>
      </xsl:matching-substring>
    </xsl:analyze-string>
  </xsl:function>

  <!--
       ===================================
        FORMAT CODE: nocontent
       =================================== 
        input:      *
        output:     ""
   -->  
  <xsl:function name="ixt:nocontent">
    <xsl:param name="input"/>
    <xsl:text></xsl:text>
  </xsl:function>
  
  <!--
       ===================================
        FORMAT CODE: numcommadecimal
       ===================================
        input:      NN?NNN?NNN,NN
        output:     NNNNNNNN.NN
    
        NOTE: Transform behaviour is undefined if input is not of type ixt:numcommadecimal
  -->
  <xsl:function name="ixt:numcommadecimal">
    <xsl:param name="input"/>
    <xsl:variable name="str1" select="replace($input, '\.', '')"/>
    <xsl:variable name="str2" select="replace($str1, ',', '.')"/>
    <xsl:variable name="str3" select="replace($str2, ' ', '')"/>
    <xsl:variable name="str4" select="replace($str3, '&#xA0;', '')"/>
    <xsl:value-of select="string($str4)"/>
  </xsl:function>
  
  <!--
       ===================================
        FORMAT CODE: zerodash
       =================================== 
        input:      -
        output:     0
        
        NOTE: Transform behaviour is undefined if input is not of type ixt:zerodash
   -->  
  <xsl:function name="ixt:zerodash">
    <xsl:param name="input"/>
    <xsl:value-of select="'0'"/>
  </xsl:function>

  <!--
       ===================================
        FORMAT CODE: numdotdecimal
       =================================== 
        input:      NN?NNN?NNN.NN
        output:     NNNNNNNN.NN

        NOTE: Transform behaviour is undefined if input is not of type ixt:numdotdecimal
   -->  
  <xsl:function name="ixt:numdotdecimal">
    <xsl:param name="input"/>
      <xsl:variable name="str1" select="replace($input, ',', '')"/>
      <xsl:variable name="str2" select="replace($str1, ' ', '')"/>
      <xsl:variable name="str3" select="replace($str2, '&#xA0;', '')"/>
    <xsl:value-of select="string($str3)"/>
  </xsl:function>
  
  <!--
       ===================================
        FORMAT CODE: numunitdecimal
       =================================== 
        input:      NN?NNN?NNN 円 NN 銭
        output:     NNNNNNNN.NN
   -->  
  <xsl:function name="ixt:numunitdecimal">
      <xsl:param name="input"/>
      <xsl:variable name="str1" select="replace($input, ',', '')"/> <!-- remove commas -->
      <xsl:variable name="str2" select="replace($str1, '，', '')"/> <!-- remove full-width commas -->
      <xsl:variable name="str3" select="replace($str2, '\.', '')"/> <!-- remove full stops -->
      <xsl:variable name="str4" select="ixh:full-width-digits-to-normal($str3)"/> 
      <xsl:analyze-string select="$str4" regex="([0-9]+)([^0-9]+)([0-9]+)([^0-9]*)">
      <xsl:matching-substring>
        <xsl:value-of select="concat(regex-group(1), '.', ixh:decimalalignment(regex-group(3)))"/>
      </xsl:matching-substring>
      </xsl:analyze-string>
  </xsl:function>

  <!-- 
       ===================================
        FORMAT CODE: dateyearmonthday
       ===================================
        input:      (Y)Y(YY)*MM*DD
        output:     YYYY-MM-DD
      
        No validation is done of the input string.  If an invalid 
        date is supplied, the behaviour is undefined.
        
        e.g. ixt:dateyearmonthday "2008/3/24" will output "2008-03-24".
        
        NOTE: If input is only "YY", then "20" is prepended
              (year assumed to be in 21st century)
  -->
  <xsl:function name="ixt:dateyearmonthday">
    <xsl:param name="input"/>
    <xsl:analyze-string select="ixh:full-width-digits-to-normal($input)" regex="([0-9０-９]+)[^0-9０-９]+([0-9０-９]+)[^0-9０-９]+([0-9０-９]+)">
      <xsl:matching-substring>
        <xsl:value-of select="ixh:buildxsddate(regex-group(1), regex-group(2), regex-group(3))"/>
      </xsl:matching-substring>
    </xsl:analyze-string>
  </xsl:function>


  
  <!-- ################################################# SUPPORT FUNCTIONS -->
  

  <!--
    =======================================================
    ixh:test(string transform, element context)
    =======================================================
    
    This function checks to see if the given transform exists
    and is in the relevant namespace.  It returns true or false.
  -->
  <xsl:function name="ixh:test">
    <xsl:param name="transform"/>
    <xsl:param name="context"/>
    
    <xsl:choose>
      <xsl:when test="substring-after($context/@ix:format,':') = $transform and
        namespace-uri-for-prefix(substring-before($context/@ix:format,':'),$context)
        = 'http://www.xbrl.org/inlineXBRL/transformation/2015-02-26'">
        <xsl:value-of select="boolean(1)"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="boolean(0)"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:function>
  
  <!--
    =======================================================
    ixh:decimalformat(string result, int count)
    =======================================================
    
    This function produces a formatting string for the format-number() function (XSLT 2.0).
    It is a recursive function which must be "manually" initialized with "0." then the
    recursive function incrementally adds a "zero" character.
    
    e.g. ixh:decimalformat("0.",3) will produce a formatting string "0.000".
    
    Behaviour is undefined if "result" is not initialized as "0." or anything other than a
    non-negative integer value is provided for "count". 
  -->
  <xsl:function name="ixh:decimalformat">
    <xsl:param name="result"/>
    <xsl:param name="count"/>

    <xsl:choose>
      <xsl:when test="$count &lt;= 0 or not($count)">
        <xsl:value-of select="$result"/>
      </xsl:when>
      <xsl:when test="$count > 0">
        <xsl:value-of select="ixh:decimalformat( concat($result, '0'), ceiling($count) - 1)"/>
      </xsl:when>
    </xsl:choose>
  </xsl:function>
  
  <!--
    =======================================================
    ixh:buildxsddate(int year, string month, int day)
    =======================================================
    
    This function takes a year, month, and day and creates an
    XSD format date of the form YYYY-MM-DD.  It will attempt to
    convert a string-format month to the numeric equivalent, will
    assume 21st century ("20" prefix) for 2 digit years, and will
    zero pad any single digit day, month, or year.
  -->
  <xsl:function name="ixh:buildxsddate">
    <xsl:param name="year"/>
    <xsl:param name="month"/>
    <xsl:param name="day"/>
    
    <xsl:variable name="month_adjusted">
      <xsl:value-of select="ixh:monthtonumber($month)"/>
    </xsl:variable>
    
    <xsl:choose>
      <xsl:when test="string-length($year) = 2">20</xsl:when>
      <xsl:when test="string-length($year) = 1">200</xsl:when>
    </xsl:choose>
    <xsl:value-of select="$year"/>
    <xsl:text>-</xsl:text>
    <xsl:if test="string-length($month_adjusted) = 1">0</xsl:if>
    <xsl:value-of select="$month_adjusted"/>
    <xsl:text>-</xsl:text>
    <xsl:if test="string-length($day) = 1">0</xsl:if>
    <xsl:value-of select="$day"/>
  </xsl:function>
  
  <!--
    =======================================================
    ixh:buildxsdgmonthdate(string month, int day)
    =======================================================
    
    This function takes a year, month, and day and creates an
    XSD format date of the form MM-DD.  It will attempt to
    convert a string-format month to the numeric equivalent, will
    assume 21st century ("20" prefix) for 2 digit years, and will
    zero pad any single digit day, month, or year.
  -->
  <xsl:function name="ixh:buildxsdgmonthdate">
    <xsl:param name="month"/>
    <xsl:param name="day"/>
    
    <xsl:variable name="month_adjusted">
      <xsl:value-of select="ixh:monthtonumber($month)"/>
    </xsl:variable>
    
    <xsl:text>--</xsl:text>
    <xsl:if test="string-length($month_adjusted) = 1">0</xsl:if>
    <xsl:value-of select="$month_adjusted"/>
    <xsl:text>-</xsl:text>
    <xsl:if test="string-length($day) = 1">0</xsl:if>
    <xsl:value-of select="$day"/>
  </xsl:function>

  <!--
    =======================================================
    ixh:buildxsdgyearmonth(int year, string month)
    =======================================================
    
    This function takes a year and month and creates an
    XSD format date of the form YYYY-MM.  It will attempt to
    convert a string-format month to the numeric equivalent, will
    assume 21st century ("20" prefix) for 2 digit years, and will
    zero pad any single digit day, month, or year.
  -->
  <xsl:function name="ixh:buildxsdgyearmonth">
    <xsl:param name="year"/>
    <xsl:param name="month"/>
    
    <xsl:variable name="month_adjusted">
      <xsl:value-of select="ixh:monthtonumber($month)"/>
    </xsl:variable>
    
    <xsl:choose>
      <xsl:when test="string-length($year) = 2">20</xsl:when>
      <xsl:when test="string-length($year) = 1">200</xsl:when>
    </xsl:choose>
    <xsl:value-of select="$year"/>
    <xsl:text>-</xsl:text>
    <xsl:if test="string-length($month_adjusted) = 1">0</xsl:if>
    <xsl:value-of select="$month_adjusted"/>
  </xsl:function>
  
  <!--
    =======================================================
    ixh:buildxsdgyearmonth2(string era, string year, int month)
    =======================================================
    
    This function takes a year and month and creates an
    XSD format date of the form YYYY-MM.  It will attempt to
    convert a string-format month to the numeric equivalent, will
    assume 21st century ("20" prefix) for 2 digit years, and will
    zero pad any single digit day, month, or year.
  -->
  <xsl:function name="ixh:buildxsdgyearmonth2">
    <xsl:param name="era"/>
    <xsl:param name="year"/>
    <xsl:param name="month"/>
    
    <xsl:variable name="year_adjusted">
      <xsl:value-of select="ixh:erayeartonumber($era, $year)"/>
    </xsl:variable>
    
    <xsl:value-of select="$year_adjusted"/>
    <xsl:text>-</xsl:text>
    <xsl:if test="string-length($month) = 1">0</xsl:if>
    <xsl:value-of select="$month"/>
  </xsl:function>

  <!--
    =======================================================
    ixh:buildxsdgyearmonthday2(string era, string year, int month, int day)
    =======================================================
    
    This function takes a year and month and creates an
    XSD format date of the form YYYY-MM.  It will attempt to
    convert a string-format month to the numeric equivalent, will
    assume 21st century ("20" prefix) for 2 digit years, and will
    zero pad any single digit day, month, or year.
  -->
  <xsl:function name="ixh:buildxsdgyearmonthday2">
    <xsl:param name="era"/>
    <xsl:param name="year"/>
    <xsl:param name="month"/>
    <xsl:param name="day"/>
    
    <xsl:variable name="year_adjusted">
      <xsl:value-of select="ixh:erayeartonumber($era, $year)"/>
    </xsl:variable>
    
    <xsl:value-of select="$year_adjusted"/>
    <xsl:text>-</xsl:text>
    <xsl:if test="string-length($month) = 1">0</xsl:if>
    <xsl:value-of select="$month"/>
    <xsl:text>-</xsl:text>
    <xsl:if test="string-length($day) = 1">0</xsl:if>
    <xsl:value-of select="$day"/>
  </xsl:function>


  <!--
    =======================================================
    ixh:monthtonumber(string input)
    =======================================================
    
    This function converts capitalized english month names or the three
    letter abbreviations into a two digit month number.
  -->
  <xsl:function name="ixh:monthtonumber">
    <xsl:param name="input"/>

    <xsl:variable name="key">
      <xsl:value-of select="upper-case(substring($input, 1, 3))"/>
    </xsl:variable>
    
    <xsl:choose>
      <xsl:when test="$key = 'JAN'">01</xsl:when>
      <xsl:when test="$key = 'FEB'">02</xsl:when>
      <xsl:when test="$key = 'MAR'">03</xsl:when>
      <xsl:when test="$key = 'APR'">04</xsl:when>
      <xsl:when test="$key = 'MAY'">05</xsl:when>
      <xsl:when test="$key = 'JUN'">06</xsl:when>
      <xsl:when test="$key = 'JUL'">07</xsl:when>
      <xsl:when test="$key = 'AUG'">08</xsl:when>
      <xsl:when test="$key = 'SEP'">09</xsl:when>
      <xsl:when test="$key = 'OCT'">10</xsl:when>
      <xsl:when test="$key = 'NOV'">11</xsl:when>
      <xsl:when test="$key = 'DEC'">12</xsl:when>
      
      <xsl:otherwise><xsl:value-of select="$input"/></xsl:otherwise>
    </xsl:choose>
  </xsl:function>

  <!--
    =======================================================
    ixh:erayeartonumber(string era, string year)
    =======================================================
    
    This function converts Japanese era symbols to years.
  -->
  <xsl:function name="ixh:erayeartonumber">
    <xsl:param name="era"/>
    <xsl:param name="year"/>
    
    <xsl:variable name="year_adjusted">
      <xsl:value-of select="ixh:stringyeartonumber($year)"/>
    </xsl:variable>

    <xsl:choose>
      <xsl:when test="$era='平成'"><xsl:value-of select="$year_adjusted+1988"/></xsl:when>
      <xsl:when test="$era='平'"><xsl:value-of select="$year_adjusted+1988"/></xsl:when>
      <xsl:when test="$era='明治'"><xsl:value-of select="$year_adjusted+1867"/></xsl:when>
      <xsl:when test="$era='明'"><xsl:value-of select="$year_adjusted+1867"/></xsl:when>
      <xsl:when test="$era='大正'"><xsl:value-of select="$year_adjusted+1911"/></xsl:when>
      <xsl:when test="$era='大'"><xsl:value-of select="$year_adjusted+1911"/></xsl:when>
      <xsl:when test="$era='昭和'"><xsl:value-of select="$year_adjusted+1925"/></xsl:when>
      <xsl:when test="$era='昭'"><xsl:value-of select="$year_adjusted+1925"/></xsl:when>
    </xsl:choose>
  </xsl:function>

  <xsl:function name="ixh:stringyeartonumber">
    <xsl:param name="input"/>
    
    <xsl:choose>
      <xsl:when test="$input = '元'">1</xsl:when>
      <xsl:otherwise><xsl:value-of select="ixh:full-width-digits-to-normal($input)"/></xsl:otherwise>
    </xsl:choose>
  </xsl:function>

  <xsl:function name="ixh:full-width-digits-to-normal">
    <xsl:param name="input"/>
    <xsl:value-of select="translate($input,'０１２３４５６７８９','0123456789')"/>
  </xsl:function>

  <!--
    =======================================================
    ixh:applyscale(node node, string initial_value)
    =======================================================
    
    Creates a number formatting string of the format "000.00".
  -->
  
  <xsl:function name="ixh:applyscale">
    <xsl:param name="node"/>
    <xsl:param name="initial_value"/>
    
    <xsl:variable name="scale">
      <xsl:choose>
        <xsl:when test="exists($node/@ix:scale)">
          <xsl:value-of select="number($node/@ix:scale)"/>
        </xsl:when>
        <xsl:otherwise>0</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    
    <xsl:variable name="factor">
      <xsl:value-of select="ixh:power(10, $scale, 1)"/>
    </xsl:variable>
    
    <!-- NOTE: If no @decimals attribute exists, one decimal place is assumed. -->
    <xsl:variable name="decimals">
      <xsl:choose>
        <xsl:when test="exists($node/@decimals)">
          <xsl:value-of select="$node/@decimals"/>
        </xsl:when>
        <xsl:otherwise>0</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    
    <xsl:variable name="sign">
      <xsl:choose>
        <xsl:when test="exists($node/@ix:sign)">-1</xsl:when>
        <xsl:otherwise>1</xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    
    <xsl:variable name="final_value" select="number($sign) * number($initial_value) * number($factor)"/>
    
    <xsl:value-of select="format-number($final_value, ixh:decimalformat('0.', $decimals + $scale))"/>
  </xsl:function>
  <!--
    =======================================================
    ixh:power(float base, int exponent, float result)
    =======================================================
    
    No native way to do "power" operations in XSLT 2.0, so this recursive
    function provides an integer power function, basically looping over\\
    the operation "base * base * base * ... " until the exponent = 0.
    Should also work for "inverses" with negative exponents (untested).
    
    Due to nature of XSLT functions, the "result" variable must be seeded
    with the value "1" when it is first called.
    -->
  <xsl:function name="ixh:power">
    <xsl:param name="base"/>
    <xsl:param name="exponent"/>
    <xsl:param name="result"/>
    
    <xsl:choose>
      <xsl:when test="$exponent = 0">
        <xsl:value-of select="$result"/>
      </xsl:when>
      <xsl:when test="$exponent > 0">
        <xsl:value-of select="ixh:power($base, ceiling($exponent) - 1, $result * $base)"></xsl:value-of>
      </xsl:when>
      <xsl:when test="$exponent &lt; 0">
        <xsl:value-of select="ixh:power($base, floor($exponent) + 1, $result / $base)"></xsl:value-of>
      </xsl:when>
    </xsl:choose>
  </xsl:function>
  
  <!--
    =======================================================
    ixh:decimalalignment(string input)
    =======================================================
    
    This function converts 1-digit numbers to zero-padded 2-digit numbers (e.g. 1 -> 01)
  -->
  <xsl:function name="ixh:decimalalignment">
    <xsl:param name="input"/>
    <xsl:choose>
      <xsl:when test="$input = '1'">01</xsl:when>
      <xsl:when test="$input = '2'">02</xsl:when>
      <xsl:when test="$input = '3'">03</xsl:when>
      <xsl:when test="$input = '4'">04</xsl:when>
      <xsl:when test="$input = '5'">05</xsl:when>
      <xsl:when test="$input = '6'">06</xsl:when>
      <xsl:when test="$input = '7'">07</xsl:when>
      <xsl:when test="$input = '8'">08</xsl:when>
      <xsl:when test="$input = '9'">09</xsl:when>
      <xsl:otherwise><xsl:value-of select="$input"/></xsl:otherwise>
    </xsl:choose>
  </xsl:function>

  <!-- ############################################## GENERAL TEMPLATES -->
  
  <!-- Change default operation on text nodes to "nothing" rather than "print text node" -->
  <xsl:template match="text()"/>
  
  <xsl:template match="xhtml:case">
    <xsl:text>
      
    </xsl:text>
    <xsl:comment><xsl:value-of select="."/></xsl:comment>
    <xsl:text>
    </xsl:text>
  </xsl:template>
  
  <xsl:template match="xhtml:html">
    <xbrli:xbrl
        xmlns:link="http://www.xbrl.org/2003/linkbase"
        xmlns:ref="http://www.xbrl.org/2006/ref"
        xmlns:xbrldt="http://xbrl.org/2005/xbrldt"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
        xmlns:xbrli="http://www.xbrl.org/2003/instance">
        <xsl:apply-templates select="*"/>
    </xbrli:xbrl>
  </xsl:template>
  
  
  <!-- ############################################## InlineXBRL TEMPLATES -->
  
  <xsl:template match="ix:*">
    <xsl:element name="{substring-after(@ix:name,':')}"
      namespace="{namespace-uri-for-prefix(substring-before(@ix:name,':'),.)}">
      <xsl:apply-templates select="@*"/>
      <xsl:apply-templates select="." mode="contentxform"/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="ix:fraction">
    <xsl:element name="{substring-after(@ix:name,':')}"
      namespace="{namespace-uri-for-prefix(substring-before(@ix:name,':'),.)}">
      <xsl:apply-templates select="@*"/>
      <xsl:apply-templates select="*" mode="numdemsearch"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="*" mode="numdemsearch">
    <xsl:apply-templates select="*"/>
  </xsl:template>
  
  <xsl:template match="ix:numerator|ix:denominator" mode="numdemsearch">
    <xsl:element name="{local-name(.)}" namespace="http://www.xbrl.org/2003/instance">
      <xsl:apply-templates select="@*"/>
      <xsl:apply-templates select="." mode="contentxform"/>      
    </xsl:element>  
  </xsl:template>
  
  <!-- TODO: @ix:sign is not currently dealt with, so it is passed through to
              output document.
  -->
  <xsl:template match="@ix:sign">
    <xsl:copy/>
  </xsl:template>
  
  <!-- All non iXBRL namespaced attributes are copied across. -->
  <xsl:template match="@*">
    <xsl:if test="namespace-uri() != 'http://www.xbrl.org/2008/inlineXBRL'">
      <xsl:copy/>
    </xsl:if>
  </xsl:template>
  
</xsl:stylesheet>
