<?xml-stylesheet type="text/xsl" href="unicode.xsl"?>
<!--
unicode.xml


Copyright David Carlisle 1999-2015

Use and distribution of this code are permitted under the terms of the
W3C Software Notice and License.
http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231.html



This file is a collection of information about how to map 
Unicode entities to LaTeX, and various SGML/XML entity
sets (ISO and MathML). A Unicode character may be mapped
to several entities.

Originally designed by Sebastian Rahtz in conjunction with
Barbara Beeton for the STIX project

Maintained since 1999 by David Carlisle <davidc@nag.co.uk>
on behalf of the W3C math WG.

Thanks to:

Robert Streich 
Nico Poppelier 
Rune Mathisen 
Vidar Gundersen 
John Cowan 
mundie 

for borrowings from their work

-->
<unicode unicode="8.0">
   <entitygroups>
      <group name="predefined">
         <set name="predefined" fpi="-//W3C//ENTITIES Predefined XML//EN"/>
      </group>
      <group name="iso8879">
         <set name="8879-isoamsa" fpi="ISO 8879:1986//ENTITIES Added Math Symbols: Arrow Relations//EN"/>
         <set name="8879-isoamsb" fpi="ISO 8879:1986//ENTITIES Added Math Symbols: Binary Operators//EN"/>
         <set name="8879-isoamsc" fpi="ISO 8879:1986//ENTITIES Added Math Symbols: Delimiters//EN"/>
         <set name="8879-isoamsn" fpi="ISO 8879:1986//ENTITIES Added Math Symbols: Negated Relations//EN"/>
         <set name="8879-isoamso" fpi="ISO 8879:1986//ENTITIES Added Math Symbols: Ordinary//EN"/>
         <set name="8879-isoamsr" fpi="ISO 8879:1986//ENTITIES Added Math Symbols: Relations//EN"/>
         <set name="8879-isobox" fpi="ISO 8879:1986//ENTITIES Box and Line Drawing//EN"/>
         <set name="8879-isocyr1" fpi="ISO 8879:1986//ENTITIES Russian Cyrillic//EN"/>
         <set name="8879-isocyr2" fpi="ISO 8879:1986//ENTITIES Non-Russian Cyrillic//EN"/>
         <set name="8879-isodia" fpi="ISO 8879:1986//ENTITIES Diacritical Marks//EN"/>
         <set name="8879-isogrk1" fpi="ISO 8879:1986//ENTITIES Greek Letters//EN"/>
         <set name="8879-isogrk2" fpi="ISO 8879:1986//ENTITIES Monotoniko Greek//EN"/>
         <set name="8879-isogrk3" fpi="ISO 8879:1986//ENTITIES Greek Symbols//EN"/>
         <set name="8879-isogrk4" fpi="ISO 8879:1986//ENTITIES Alternative Greek Symbols//EN"/>
         <set name="8879-isolat1" fpi="ISO 8879:1986//ENTITIES Added Latin 1//EN"/>
         <set name="8879-isolat2" fpi="ISO 8879:1986//ENTITIES Added Latin 2//EN"/>
         <set name="8879-isonum" fpi="ISO 8879:1986//ENTITIES Numeric and Special Graphic//EN"/>
         <set name="8879-isopub" fpi="ISO 8879:1986//ENTITIES Publishing//EN"/>
         <set name="8879-isotech" fpi="ISO 8879:1986//ENTITIES General Technical//EN"/>
      </group>
      <group name="iso9573-1991">
         <set name="9573-1991-isoamsa" fpi="ISO 9573-13:1991//ENTITIES Added Math Symbols: Arrow Relations //EN"/>
         <set name="9573-1991-isoamsb" fpi="ISO 9573-13:1991//ENTITIES Added Math Symbols: Binary Operators //EN"/>
         <set name="9573-1991-isoamsc" fpi="ISO 9573-13:1991//ENTITIES Added Math Symbols: Delimiters //EN"/>
         <set name="9573-1991-isoamsn" fpi="ISO 9573-13:1991//ENTITIES Added Math Symbols: Negated Relations //EN"/>
         <set name="9573-1991-isoamso" fpi="ISO 9573-13:1991//ENTITIES Added Math Symbols: Ordinary //EN"/>
         <set name="9573-1991-isoamsr" fpi="ISO 9573-13:1991//ENTITIES Added Math Symbols: Relations //EN"/>
         <set name="9573-1991-isogrk3" fpi="ISO 9573-13:1991//ENTITIES Greek Symbols //EN"/>
         <set name="9573-1991-isogrk4" fpi="ISO 9573-13:1991//ENTITIES Alternative Greek Symbols //EN"/>
         <set name="9573-1991-isomfrk" fpi="ISO 9573-13:1991//ENTITIES Math Alphabets: Fraktur //EN"/>
         <set name="9573-1991-isomopf" fpi="ISO 9573-13:1991//ENTITIES Math Alphabets: Open Face //EN"/>
         <set name="9573-1991-isomscr" fpi="ISO 9573-13:1991//ENTITIES Math Alphabets: Script //EN"/>
         <set name="9573-1991-isotech" fpi="ISO 9573-13:1991//ENTITIES General Technical //EN"/>
      </group>
      <group name="iso9573-2003">
         <set name="9573-2003-isobox" fpi="ISO 9573-13:2003//ENTITIES Box and Line Drawing//EN"/>
         <set name="9573-2003-isocyr1" fpi="ISO 9573-13:2003//ENTITIES Russian Cyrillic//EN"/>
         <set name="9573-2003-isocyr2" fpi="ISO 9573-13:2003//ENTITIES Non-Russian Cyrillic//EN"/>
         <set name="9573-2003-isodia" fpi="ISO 9573-13:2003//ENTITIES Diacritical Marks//EN"/>
         <set name="9573-2003-isolat1" fpi="ISO 9573-13:2003//ENTITIES Added Latin 1//EN"/>
         <set name="9573-2003-isolat2" fpi="ISO 9573-13:2003//ENTITIES Added Latin 2//EN"/>
         <set name="9573-2003-isonum" fpi="ISO 9573-13:2003//ENTITIES Numeric and Special Graphic//EN"/>
         <set name="9573-2003-isopub" fpi="ISO 9573-13:2003//ENTITIES Publishing//EN"/>
         <set name="9573-2003-isoamsa" fpi="ISO 9573-13:2003//ENTITIES Added Math Symbols: Arrow Relations//EN"/>
         <set name="9573-2003-isoamsb" fpi="ISO 9573-13:2003//ENTITIES Added Math Symbols: Binary Operators//EN"/>
         <set name="9573-2003-isoamsc" fpi="ISO 9573-13:2003//ENTITIES Added Math Symbols: Delimiters//EN"/>
         <set name="9573-2003-isoamsn" fpi="ISO 9573-13:2003//ENTITIES Added Math Symbols: Negated Relations//EN"/>
         <set name="9573-2003-isoamso" fpi="ISO 9573-13:2003//ENTITIES Added Math Symbols: Ordinary//EN"/>
         <set name="9573-2003-isoamsr" fpi="ISO 9573-13:2003//ENTITIES Added Math Symbols: Relations//EN"/>
         <set name="9573-2003-isogrk1" fpi="ISO 9573-13:2003//ENTITIES Greek Letters//EN"/>
         <set name="9573-2003-isogrk2" fpi="ISO 9573-13:2003//ENTITIES Monotoniko Greek//EN"/>
         <set name="9573-2003-isogrk3" fpi="ISO 9573-13:2003//ENTITIES Greek Symbols//EN"/>
         <set name="9573-2003-isogrk4" fpi="ISO 9573-13:2003//ENTITIES Alternative Greek Symbols//EN"/>
         <set name="9573-2003-isomfrk" fpi="ISO 9573-13:2003//ENTITIES Math Alphabets: Fraktur//EN"/>
         <set name="9573-2003-isomopf" fpi="ISO 9573-13:2003//ENTITIES Math Alphabets: Open Face//EN"/>
         <set name="9573-2003-isomscr" fpi="ISO 9573-13:2003//ENTITIES Math Alphabets: Script//EN"/>
         <set name="9573-2003-isotech" fpi="ISO 9573-13:2003//ENTITIES General Technical//EN"/>
      </group>
      <group name="mathml">
         <set name="9573-2003-isobox" fpi="-//W3C//ENTITIES Box and Line Drawing//EN"/>
         <set name="9573-2003-isocyr1" fpi="-//W3C//ENTITIES Russian Cyrillic//EN"/>
         <set name="9573-2003-isocyr2" fpi="-//W3C//ENTITIES Non-Russian Cyrillic//EN"/>
         <set name="9573-2003-isodia" fpi="-//W3C//ENTITIES Diacritical Marks//EN"/>
         <set name="9573-2003-isolat1" fpi="-//W3C//ENTITIES Added Latin 1//EN"/>
         <set name="9573-2003-isolat2" fpi="-//W3C//ENTITIES Added Latin 2//EN"/>
         <set name="9573-2003-isonum" fpi="-//W3C//ENTITIES Numeric and Special Graphic//EN"/>
         <set name="9573-2003-isopub" fpi="-//W3C//ENTITIES Publishing//EN"/>
         <set name="9573-2003-isoamsa" fpi="-//W3C//ENTITIES Added Math Symbols: Arrow Relations//EN"/>
         <set name="9573-2003-isoamsb" fpi="-//W3C//ENTITIES Added Math Symbols: Binary Operators//EN"/>
         <set name="9573-2003-isoamsc" fpi="-//W3C//ENTITIES Added Math Symbols: Delimiters//EN"/>
         <set name="9573-2003-isoamsn" fpi="-//W3C//ENTITIES Added Math Symbols: Negated Relations//EN"/>
         <set name="9573-2003-isoamso" fpi="-//W3C//ENTITIES Added Math Symbols: Ordinary//EN"/>
         <set name="9573-2003-isoamsr" fpi="-//W3C//ENTITIES Added Math Symbols: Relations//EN"/>
         <set name="9573-2003-isogrk3" fpi="-//W3C//ENTITIES Greek Symbols//EN"/>
         <set name="9573-2003-isomfrk" fpi="-//W3C//ENTITIES Math Alphabets: Fraktur//EN"/>
         <set name="9573-2003-isomopf" fpi="-//W3C//ENTITIES Math Alphabets: Open Face//EN"/>
         <set name="9573-2003-isomscr" fpi="-//W3C//ENTITIES Math Alphabets: Script//EN"/>
         <set name="9573-2003-isotech" fpi="-//W3C//ENTITIES General Technical//EN"/>
         <set name="mmlextra" fpi="-//W3C//ENTITIES Additional MathML Symbols//EN"/>
         <set name="mmlalias" fpi="-//W3C//ENTITIES MathML Aliases//EN"/>
      </group>
      <group name="xhtml1">
         <set name="xhtml1-lat1"/>
         <set name="xhtml1-special"/>
         <set name="xhtml1-symbol"/>
      </group>
      <group name="html5">
         <set name="xhtml1-lat1" fpi="-//W3C//ENTITIES Latin for HTML//EN/"/>
         <set name="xhtml1-special" fpi="-//W3C//ENTITIES Special for HTML//EN/"/>
         <set name="xhtml1-symbol" fpi="-//W3C//ENTITIES Symbol for HTML//EN/"/>
         <set name="html5-uppercase" fpi="-//W3C//ENTITIES uppercase aliases for HTML//EN/"/>
         <set name="predefined" fpi="-//W3C//ENTITIES Predefined XML//EN/"/>
      </group>
      <group name="2007">
         <set name="9573-2003-isobox" fpi="-//W3C//ENTITIES Box and Line Drawing//EN"/>
         <set name="9573-2003-isocyr1" fpi="-//W3C//ENTITIES Russian Cyrillic//EN"/>
         <set name="9573-2003-isocyr2" fpi="-//W3C//ENTITIES Non-Russian Cyrillic//EN"/>
         <set name="9573-2003-isodia" fpi="-//W3C//ENTITIES Diacritical Marks//EN"/>
         <set name="9573-2003-isolat1" fpi="-//W3C//ENTITIES Added Latin 1//EN"/>
         <set name="9573-2003-isolat2" fpi="-//W3C//ENTITIES Added Latin 2//EN"/>
         <set name="9573-2003-isonum" fpi="-//W3C//ENTITIES Numeric and Special Graphic//EN"/>
         <set name="9573-2003-isopub" fpi="-//W3C//ENTITIES Publishing//EN"/>
         <set name="9573-2003-isoamsa" fpi="-//W3C//ENTITIES Added Math Symbols: Arrow Relations//EN"/>
         <set name="9573-2003-isoamsb" fpi="-//W3C//ENTITIES Added Math Symbols: Binary Operators//EN"/>
         <set name="9573-2003-isoamsc" fpi="-//W3C//ENTITIES Added Math Symbols: Delimiters//EN"/>
         <set name="9573-2003-isoamsn" fpi="-//W3C//ENTITIES Added Math Symbols: Negated Relations//EN"/>
         <set name="9573-2003-isoamso" fpi="-//W3C//ENTITIES Added Math Symbols: Ordinary//EN"/>
         <set name="9573-2003-isoamsr" fpi="-//W3C//ENTITIES Added Math Symbols: Relations//EN"/>
         <set name="9573-2003-isogrk1" fpi="-//W3C//ENTITIES Greek Letters//EN"/>
         <set name="9573-2003-isogrk2" fpi="-//W3C//ENTITIES Monotoniko Greek//EN"/>
         <set name="9573-2003-isogrk3" fpi="-//W3C//ENTITIES Greek Symbols//EN"/>
         <set name="9573-2003-isogrk4" fpi="-//W3C//ENTITIES Alternative Greek Symbols//EN"/>
         <set name="9573-2003-isomfrk" fpi="-//W3C//ENTITIES Math Alphabets: Fraktur//EN"/>
         <set name="9573-2003-isomopf" fpi="-//W3C//ENTITIES Math Alphabets: Open Face//EN"/>
         <set name="9573-2003-isomscr" fpi="-//W3C//ENTITIES Math Alphabets: Script//EN"/>
         <set name="9573-2003-isotech" fpi="-//W3C//ENTITIES General Technical//EN"/>
         <set name="mmlextra" fpi="-//W3C//ENTITIES Additional MathML Symbols//EN"/>
         <set name="mmlalias" fpi="-//W3C//ENTITIES MathML Aliases//EN"/>
         <set name="xhtml1-lat1" fpi="-//W3C//ENTITIES Latin for HTML//EN"/>
         <set name="xhtml1-special" fpi="-//W3C//ENTITIES Special for HTML//EN"/>
         <set name="xhtml1-symbol" fpi="-//W3C//ENTITIES Symbol for HTML//EN"/>
         <set name="html5-uppercase" fpi="-//W3C//ENTITIES uppercase aliases for HTML//EN"/>
         <set name="predefined" fpi="-//W3C//ENTITIES Predefined XML//EN/"/>
      </group>
   </entitygroups>
   <mathvariants>
      <mathvariant name="bold" description="Bold (Serif)"/>
      <mathvariant name="italic" description="Italic or Slanted"/>
      <mathvariant name="bold-italic" description="Bold Italic or Slanted"/>
      <mathvariant name="script" description="Script (or Calligraphic)"/>
      <mathvariant name="bold-script" description="Bold Script"/>
      <mathvariant name="fraktur" description="Fraktur"/>
      <mathvariant name="bold-fraktur" description="Bold Fraktur"/>
      <mathvariant name="sans-serif" description="Sans Serif"/>
      <mathvariant name="bold-sans-serif" description="Bold Sans Serif"/>
      <mathvariant name="sans-serif-italic" description="Slanted Sans Serif"/>
      <mathvariant name="sans-serif-bold-italic" description="Slanted Bold Sans Serif"/>
      <mathvariant name="monospace" description="Monospace"/>
      <mathvariant name="double-struck" description="Double Struck (Open Face, Blackboard Bold)"/>
      <mathvariant name="initial" description="Arabic Initial Form"/>
      <mathvariant name="tailed" description="Arabic Tailed Form"/>
      <mathvariant name="looped" description="Arabic Looped Form"/>
      <mathvariant name="stretched" description="Arabic Stretched Form"/>
   </mathvariants>
   <unicodeblocks>
      <block start="00000" end="0007F" name="C0 Controls and Basic Latin"/>
      <block start="00080" end="000FF" name="C1 Controls and Latin-1 Supplement"/>
      <block start="00100" end="0017F" name="Latin Extended-A"/>
      <block start="00180" end="0024F" name="Latin Extended-B"/>
      <block start="00250" end="002AF" name="IPA Extensions"/>
      <block start="002B0" end="002FF" name="Spacing Modifier Letters"/>
      <block start="00300" end="0036F" name="Combining Diacritical Marks"/>
      <block start="00370" end="003FF" name="Greek and Coptic"/>
      <block start="00400" end="004FF" name="Cyrillic"/>
      <block start="00500" end="0052F" name="Cyrillic Supplement"/>
      <block start="00530" end="0058F" name="Armenian"/>
      <block start="00590" end="005FF" name="Hebrew"/>
      <block start="00600" end="006FF" name="Arabic"/>
      <block start="00700" end="0074F" name="Syriac"/>
      <block start="00750" end="0077F" name="Arabic Supplement"/>
      <block start="00780" end="007BF" name="Thaana"/>
      <block start="007C0" end="007FF" name="NKo"/>
      <block start="00800" end="0083F" name="Samaritan"/>
      <block start="00840" end="0085F" name="Mandaic"/>
      <block start="008A0" end="008FF" name="Arabic Extended-A"/>
      <block start="00900" end="0097F" name="Devanagari"/>
      <block start="00980" end="009FF" name="Bengali"/>
      <block start="00A00" end="00A7F" name="Gurmukhi"/>
      <block start="00A80" end="00AFF" name="Gujarati"/>
      <block start="00B00" end="00B7F" name="Oriya"/>
      <block start="00B80" end="00BFF" name="Tamil"/>
      <block start="00C00" end="00C7F" name="Telugu"/>
      <block start="00C80" end="00CFF" name="Kannada"/>
      <block start="00D00" end="00D7F" name="Malayalam"/>
      <block start="00D80" end="00DFF" name="Sinhala"/>
      <block start="00E00" end="00E7F" name="Thai"/>
      <block start="00E80" end="00EFF" name="Lao"/>
      <block start="00F00" end="00FFF" name="Tibetan"/>
      <block start="01000" end="0109F" name="Myanmar"/>
      <block start="010A0" end="010FF" name="Georgian"/>
      <block start="01100" end="011FF" name="Hangul Jamo"/>
      <block start="01200" end="0137F" name="Ethiopic"/>
      <block start="01380" end="0139F" name="Ethiopic Supplement"/>
      <block start="013A0" end="013FF" name="Cherokee"/>
      <block start="01400" end="0167F" name="Unified Canadian Aboriginal Syllabics"/>
      <block start="01680" end="0169F" name="Ogham"/>
      <block start="016A0" end="016FF" name="Runic"/>
      <block start="01700" end="0171F" name="Tagalog"/>
      <block start="01720" end="0173F" name="Hanunoo"/>
      <block start="01740" end="0175F" name="Buhid"/>
      <block start="01760" end="0177F" name="Tagbanwa"/>
      <block start="01780" end="017FF" name="Khmer"/>
      <block start="01800" end="018AF" name="Mongolian"/>
      <block start="018B0" end="018FF" name="Unified Canadian Aboriginal Syllabics Extended"/>
      <block start="01900" end="0194F" name="Limbu"/>
      <block start="01950" end="0197F" name="Tai Le"/>
      <block start="01980" end="019DF" name="New Tai Lue"/>
      <block start="019E0" end="019FF" name="Khmer Symbols"/>
      <block start="01A00" end="01A1F" name="Buginese"/>
      <block start="01A20" end="01AAF" name="Tai Tham"/>
      <block start="01AB0" end="01AFF" name="Combining Diacritical Marks Extended"/>
      <block start="01B00" end="01B7F" name="Balinese"/>
      <block start="01B80" end="01BBF" name="Sundanese"/>
      <block start="01BC0" end="01BFF" name="Batak"/>
      <block start="01C00" end="01C4F" name="Lepcha"/>
      <block start="01C50" end="01C7F" name="Ol Chiki"/>
      <block start="01CC0" end="01CCF" name="Sundanese Supplement"/>
      <block start="01CD0" end="01CFF" name="Vedic Extensions"/>
      <block start="01D00" end="01D7F" name="Phonetic Extensions"/>
      <block start="01D80" end="01DBF" name="Phonetic Extensions Supplement"/>
      <block start="01DC0" end="01DFF" name="Combining Diacritical Marks Supplement"/>
      <block start="01E00" end="01EFF" name="Latin Extended Additional"/>
      <block start="01F00" end="01FFF" name="Greek Extended"/>
      <block start="02000" end="0206F" name="General Punctuation"/>
      <block start="02070" end="0209F" name="Superscripts and Subscripts"/>
      <block start="020A0" end="020CF" name="Currency Symbols"/>
      <block start="020D0" end="020FF" name="Combining Diacritical Marks for Symbols"/>
      <block start="02100" end="0214F" name="Letterlike Symbols"/>
      <block start="02150" end="0218F" name="Number Forms"/>
      <block start="02190" end="021FF" name="Arrows"/>
      <block start="02200" end="022FF" name="Mathematical Operators"/>
      <block start="02300" end="023FF" name="Miscellaneous Technical"/>
      <block start="02400" end="0243F" name="Control Pictures"/>
      <block start="02440" end="0245F" name="Optical Character Recognition"/>
      <block start="02460" end="024FF" name="Enclosed Alphanumerics"/>
      <block start="02500" end="0257F" name="Box Drawing"/>
      <block start="02580" end="0259F" name="Block Elements"/>
      <block start="025A0" end="025FF" name="Geometric Shapes"/>
      <block start="02600" end="026FF" name="Miscellaneous Symbols"/>
      <block start="02700" end="027BF" name="Dingbats"/>
      <block start="027C0" end="027EF" name="Miscellaneous Mathematical Symbols-A"/>
      <block start="027F0" end="027FF" name="Supplemental Arrows-A"/>
      <block start="02800" end="028FF" name="Braille Patterns"/>
      <block start="02900" end="0297F" name="Supplemental Arrows-B"/>
      <block start="02980" end="029FF" name="Miscellaneous Mathematical Symbols-B"/>
      <block start="02A00" end="02AFF" name="Supplemental Mathematical Operators"/>
      <block start="02B00" end="02BFF" name="Miscellaneous Symbols and Arrows"/>
      <block start="02C00" end="02C5F" name="Glagolitic"/>
      <block start="02C60" end="02C7F" name="Latin Extended-C"/>
      <block start="02C80" end="02CFF" name="Coptic"/>
      <block start="02D00" end="02D2F" name="Georgian Supplement"/>
      <block start="02D30" end="02D7F" name="Tifinagh"/>
      <block start="02D80" end="02DDF" name="Ethiopic Extended"/>
      <block start="02DE0" end="02DFF" name="Cyrillic Extended-A"/>
      <block start="02E00" end="02E7F" name="Supplemental Punctuation"/>
      <block start="02E80" end="02EFF" name="CJK Radicals Supplement"/>
      <block start="02F00" end="02FDF" name="Kangxi Radicals"/>
      <block start="02FF0" end="02FFF" name="Ideographic Description Characters"/>
      <block start="03000" end="0303F" name="CJK Symbols and Punctuation"/>
      <block start="03040" end="0309F" name="Hiragana"/>
      <block start="030A0" end="030FF" name="Katakana"/>
      <block start="03100" end="0312F" name="Bopomofo"/>
      <block start="03130" end="0318F" name="Hangul Compatibility Jamo"/>
      <block start="03190" end="0319F" name="Kanbun"/>
      <block start="031A0" end="031BF" name="Bopomofo Extended"/>
      <block start="031C0" end="031EF" name="CJK Strokes"/>
      <block start="031F0" end="031FF" name="Katakana Phonetic Extensions"/>
      <block start="03200" end="032FF" name="Enclosed CJK Letters and Months"/>
      <block start="03300" end="033FF" name="CJK Compatibility"/>
      <block start="03400" end="04DBF" name="CJK Unified Ideographs Extension A"/>
      <block start="04DC0" end="04DFF" name="Yijing Hexagram Symbols"/>
      <block start="04E00" end="09FFF" name="CJK Unified Ideographs"/>
      <block start="0A000" end="0A48F" name="Yi Syllables"/>
      <block start="0A490" end="0A4CF" name="Yi Radicals"/>
      <block start="0A4D0" end="0A4FF" name="Lisu"/>
      <block start="0A500" end="0A63F" name="Vai"/>
      <block start="0A640" end="0A69F" name="Cyrillic Extended-B"/>
      <block start="0A6A0" end="0A6FF" name="Bamum"/>
      <block start="0A700" end="0A71F" name="Modifier Tone Letters"/>
      <block start="0A720" end="0A7FF" name="Latin Extended-D"/>
      <block start="0A800" end="0A82F" name="Syloti Nagri"/>
      <block start="0A830" end="0A83F" name="Common Indic Number Forms"/>
      <block start="0A840" end="0A87F" name="Phags-pa"/>
      <block start="0A880" end="0A8DF" name="Saurashtra"/>
      <block start="0A8E0" end="0A8FF" name="Devanagari Extended"/>
      <block start="0A900" end="0A92F" name="Kayah Li"/>
      <block start="0A930" end="0A95F" name="Rejang"/>
      <block start="0A960" end="0A97F" name="Hangul Jamo Extended-A"/>
      <block start="0A980" end="0A9DF" name="Javanese"/>
      <block start="0A9E0" end="0A9FF" name="Myanmar Extended-B"/>
      <block start="0AA00" end="0AA5F" name="Cham"/>
      <block start="0AA60" end="0AA7F" name="Myanmar Extended-A"/>
      <block start="0AA80" end="0AADF" name="Tai Viet"/>
      <block start="0AAE0" end="0AAFF" name="Meetei Mayek Extensions"/>
      <block start="0AB00" end="0AB2F" name="Ethiopic Extended-A"/>
      <block start="0AB30" end="0AB6F" name="Latin Extended-E"/>
      <block start="0AB70" end="0ABBF" name="Cherokee Supplement"/>
      <block start="0ABC0" end="0ABFF" name="Meetei Mayek"/>
      <block start="0AC00" end="0D7AF" name="Hangul Syllables"/>
      <block start="0D7B0" end="0D7FF" name="Hangul Jamo Extended-B"/>
      <block start="0D800" end="0DB7F" name="High Surrogates"/>
      <block start="0DB80" end="0DBFF" name="High Private Use Surrogates"/>
      <block start="0DC00" end="0DFFF" name="Low Surrogates"/>
      <block start="0E000" end="0F8FF" name="Private Use Area"/>
      <block start="0F900" end="0FAFF" name="CJK Compatibility Ideographs"/>
      <block start="0FB00" end="0FB4F" name="Alphabetic Presentation Forms"/>
      <block start="0FB50" end="0FDFF" name="Arabic Presentation Forms-A"/>
      <block start="0FE00" end="0FE0F" name="Variation Selectors"/>
      <block start="0FE10" end="0FE1F" name="Vertical Forms"/>
      <block start="0FE20" end="0FE2F" name="Combining Half Marks"/>
      <block start="0FE30" end="0FE4F" name="CJK Compatibility Forms"/>
      <block start="0FE50" end="0FE6F" name="Small Form Variants"/>
      <block start="0FE70" end="0FEFF" name="Arabic Presentation Forms-B"/>
      <block start="0FF00" end="0FFEF" name="Halfwidth and Fullwidth Forms"/>
      <block start="0FFF0" end="0FFFF" name="Specials"/>
      <block start="10000" end="1007F" name="Linear B Syllabary"/>
      <block start="10080" end="100FF" name="Linear B Ideograms"/>
      <block start="10100" end="1013F" name="Aegean Numbers"/>
      <block start="10140" end="1018F" name="Ancient Greek Numbers"/>
      <block start="10190" end="101CF" name="Ancient Symbols"/>
      <block start="101D0" end="101FF" name="Phaistos Disc"/>
      <block start="10280" end="1029F" name="Lycian"/>
      <block start="102A0" end="102DF" name="Carian"/>
      <block start="102E0" end="102FF" name="Coptic Epact Numbers"/>
      <block start="10300" end="1032F" name="Old Italic"/>
      <block start="10330" end="1034F" name="Gothic"/>
      <block start="10350" end="1037F" name="Old Permic"/>
      <block start="10380" end="1039F" name="Ugaritic"/>
      <block start="103A0" end="103DF" name="Old Persian"/>
      <block start="10400" end="1044F" name="Deseret"/>
      <block start="10450" end="1047F" name="Shavian"/>
      <block start="10480" end="104AF" name="Osmanya"/>
      <block start="10500" end="1052F" name="Elbasan"/>
      <block start="10530" end="1056F" name="Caucasian Albanian"/>
      <block start="10600" end="1077F" name="Linear A"/>
      <block start="10800" end="1083F" name="Cypriot Syllabary"/>
      <block start="10840" end="1085F" name="Imperial Aramaic"/>
      <block start="10860" end="1087F" name="Palmyrene"/>
      <block start="10880" end="108AF" name="Nabataean"/>
      <block start="108E0" end="108FF" name="Hatran"/>
      <block start="10900" end="1091F" name="Phoenician"/>
      <block start="10920" end="1093F" name="Lydian"/>
      <block start="10980" end="1099F" name="Meroitic Hieroglyphs"/>
      <block start="109A0" end="109FF" name="Meroitic Cursive"/>
      <block start="10A00" end="10A5F" name="Kharoshthi"/>
      <block start="10A60" end="10A7F" name="Old South Arabian"/>
      <block start="10A80" end="10A9F" name="Old North Arabian"/>
      <block start="10AC0" end="10AFF" name="Manichaean"/>
      <block start="10B00" end="10B3F" name="Avestan"/>
      <block start="10B40" end="10B5F" name="Inscriptional Parthian"/>
      <block start="10B60" end="10B7F" name="Inscriptional Pahlavi"/>
      <block start="10B80" end="10BAF" name="Psalter Pahlavi"/>
      <block start="10C00" end="10C4F" name="Old Turkic"/>
      <block start="10C80" end="10CFF" name="Old Hungarian"/>
      <block start="10E60" end="10E7F" name="Rumi Numeral Symbols"/>
      <block start="11000" end="1107F" name="Brahmi"/>
      <block start="11080" end="110CF" name="Kaithi"/>
      <block start="110D0" end="110FF" name="Sora Sompeng"/>
      <block start="11100" end="1114F" name="Chakma"/>
      <block start="11150" end="1117F" name="Mahajani"/>
      <block start="11180" end="111DF" name="Sharada"/>
      <block start="111E0" end="111FF" name="Sinhala Archaic Numbers"/>
      <block start="11200" end="1124F" name="Khojki"/>
      <block start="11280" end="112AF" name="Multani"/>
      <block start="112B0" end="112FF" name="Khudawadi"/>
      <block start="11300" end="1137F" name="Grantha"/>
      <block start="11480" end="114DF" name="Tirhuta"/>
      <block start="11580" end="115FF" name="Siddham"/>
      <block start="11600" end="1165F" name="Modi"/>
      <block start="11680" end="116CF" name="Takri"/>
      <block start="11700" end="1173F" name="Ahom"/>
      <block start="118A0" end="118FF" name="Warang Citi"/>
      <block start="11AC0" end="11AFF" name="Pau Cin Hau"/>
      <block start="12000" end="123FF" name="Cuneiform"/>
      <block start="12400" end="1247F" name="Cuneiform Numbers and Punctuation"/>
      <block start="12480" end="1254F" name="Early Dynastic Cuneiform"/>
      <block start="13000" end="1342F" name="Egyptian Hieroglyphs"/>
      <block start="14400" end="1467F" name="Anatolian Hieroglyphs"/>
      <block start="16800" end="16A3F" name="Bamum Supplement"/>
      <block start="16A40" end="16A6F" name="Mro"/>
      <block start="16AD0" end="16AFF" name="Bassa Vah"/>
      <block start="16B00" end="16B8F" name="Pahawh Hmong"/> 
      <block start="16F00" end="16F9F" name="Miao"/>
      <block start="16AD0" end="16AFF" name="Bassa Vah"/>
      <block start="16B00" end="16B8F" name="Pahawh Hmong"/>
      <block start="16F00" end="16F9F" name="Miao"/>
      <block start="1B000" end="1B0FF" name="Kana Supplement"/>
      <block start="1BC00" end="1BC9F" name="Duployan"/>
      <block start="1BCA0" end="1BCAF" name="Shorthand Format Controls"/>
      <block start="1D000" end="1D0FF" name="Byzantine Musical Symbols"/>
      <block start="1D100" end="1D1FF" name="Musical Symbols"/>
      <block start="1D200" end="1D24F" name="Ancient Greek Musical Notation"/>
      <block start="1D300" end="1D35F" name="Tai Xuan Jing Symbols"/>
      <block start="1D360" end="1D37F" name="Counting Rod Numerals"/>
      <block start="1D400" end="1D7FF" name="Mathematical Alphanumeric Symbols"/>
      <block start="1E800" end="1E8DF" name="Mende Kikakui"/>
      <block start="1EE00" end="1EEFF" name="Arabic Mathematical Alphabetic Symbols"/>
      <block start="1F000" end="1F02F" name="Mahjong Tiles"/>
      <block start="1F030" end="1F09F" name="Domino Tiles"/>
      <block start="1F0A0" end="1F0FF" name="Playing Cards"/>
      <block start="1F100" end="1F1FF" name="Enclosed Alphanumeric Supplement"/>
      <block start="1F200" end="1F2FF" name="Enclosed Ideographic Supplement"/>
      <block start="1F300" end="1F5FF" name="Miscellaneous Symbols And Pictographs"/>
      <block start="1F600" end="1F64F" name="Emoticons"/>
      <block start="1F650" end="1F67F" name="Ornamental Dingbats"/>
      <block start="1F680" end="1F6FF" name="Transport And Map Symbols"/>
      <block start="1F700" end="1F77F" name="Alchemical Symbols"/>
      <block start="1F780" end="1F7FF" name="Geometric Shapes Extended"/>
      <block start="1F800" end="1F8FF" name="Supplemental Arrows-C"/>
      <block start="20000" end="2A6DF" name="CJK Unified Ideographs Extension B"/>
      <block start="2A700" end="2B73F" name="CJK Unified Ideographs Extension C"/>
      <block start="2B740" end="2B81F" name="CJK Unified Ideographs Extension D"/>
      <block start="2F800" end="2FA1F" name="CJK Compatibility Ideographs Supplement"/>
      <block start="E0000" end="E007F" name="Tags"/>
      <block start="E0100" end="E01EF" name="Variation Selectors Supplement"/>
      <block start="F0000" end="FFFFF" name="Supplementary Private Use Area-A"/>
      <block start="100000" end="10FFFF" name="Supplementary Private Use Area-B"/>
   </unicodeblocks>
   <mathclasses>
      <mathclass letter="N" name="Normal - includes all digits and symbols requiring only one form"/>
      <mathclass letter="A" name="Alphabetic "/>
      <mathclass letter="B" name="Binary"/>
      <mathclass letter="C" name="Closing - usually paired with opening delimiter"/>
      <mathclass letter="D" name="Diacritic"/>
      <mathclass letter="F" name="Fence - unpaired delimiter (often used as opening or closing)"/>
      <mathclass letter="G" name="Glyph_Part - piece of large operator"/>
      <mathclass letter="L" name="Large - n-ary or Large operator, often takes limits"/>
      <mathclass letter="O" name="Opening - usually paired with closing delimiter"/>
      <mathclass letter="P" name="Punctuation"/>
      <mathclass letter="R" name="Relation - includes arrows"/>
      <mathclass letter="S" name="Space"/>
      <mathclass letter="U" name="Unary - operators that are only unary"/>
      <mathclass letter="V" name="Vary - operators that can be unary or binary depending on context"/>
      <mathclass letter="X" name="Special - characters not covered by other classes"/>
   </mathclasses>
   <charlist>
      <character id="U00000" dec="0" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="BN" mirror="N" unicode1="NULL"/>
         <description unicode="1.1">NULL</description>
      </character>
      <character id="U00001" dec="1" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="BN" mirror="N" unicode1="START OF HEADING"/>
         <description unicode="1.1">START OF HEADING</description>
      </character>
      <character id="U00002" dec="2" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="BN" mirror="N" unicode1="START OF TEXT"/>
         <description unicode="1.1">START OF TEXT</description>
      </character>
      <character id="U00003" dec="3" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="BN" mirror="N" unicode1="END OF TEXT"/>
         <description unicode="1.1">END OF TEXT</description>
      </character>
      <character id="U00004" dec="4" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="BN" mirror="N" unicode1="END OF TRANSMISSION"/>
         <description unicode="1.1">END OF TRANSMISSION</description>
      </character>
      <character id="U00005" dec="5" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="BN" mirror="N" unicode1="ENQUIRY"/>
         <description unicode="1.1">ENQUIRY</description>
      </character>
      <character id="U00006" dec="6" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="BN" mirror="N" unicode1="ACKNOWLEDGE"/>
         <description unicode="1.1">ACKNOWLEDGE</description>
      </character>
      <character id="U00007" dec="7" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="BN" mirror="N" unicode1="BELL"/>
         <description unicode="1.1">BELL</description>
      </character>
      <character id="U00008" dec="8" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="BN" mirror="N" unicode1="BACKSPACE"/>
         <description unicode="1.1">BACKSPACE</description>
      </character>
      <character id="U00009" dec="9" mode="text" type="other">
         <unicodedata category="Cc" combclass="0" bidi="S" mirror="N" unicode1="CHARACTER TABULATION"/>
         <entity id="Tab" set="mmlextra">
            <desc>tabulator stop; horizontal tabulation</desc>
         </entity>
         <description unicode="1.1">CHARACTER TABULATION</description>
      </character>
      <character id="U0000A" dec="10" mode="text" type="other">
         <unicodedata category="Cc" combclass="0" bidi="B" mirror="N" unicode1="LINE FEED (LF)"/>
         <Wolfram>NewLine</Wolfram>
         <entity id="NewLine" set="mmlextra">
            <desc>force a line break; line feed</desc>
         </entity>
         <description unicode="1.1">LINE FEED (LF)</description>
      </character>
      <character id="U0000B" dec="11" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="S" mirror="N" unicode1="LINE TABULATION"/>
         <description unicode="1.1">LINE TABULATION</description>
      </character>
      <character id="U0000C" dec="12" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="WS" mirror="N" unicode1="FORM FEED (FF)"/>
         <description unicode="1.1">FORM FEED (FF)</description>
      </character>
      <character id="U0000D" dec="13" mode="text" type="other">
         <unicodedata category="Cc" combclass="0" bidi="B" mirror="N" unicode1="CARRIAGE RETURN (CR)"/>
         <description unicode="1.1">CARRIAGE RETURN (CR)</description>
      </character>
      <character id="U0000E" dec="14" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="BN" mirror="N" unicode1="SHIFT OUT"/>
         <description unicode="1.1">SHIFT OUT</description>
      </character>
      <character id="U0000F" dec="15" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="BN" mirror="N" unicode1="SHIFT IN"/>
         <description unicode="1.1">SHIFT IN</description>
      </character>
      <character id="U00010" dec="16" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="BN" mirror="N" unicode1="DATA LINK ESCAPE"/>
         <description unicode="1.1">DATA LINK ESCAPE</description>
      </character>
      <character id="U00011" dec="17" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="BN" mirror="N" unicode1="DEVICE CONTROL ONE"/>
         <description unicode="1.1">DEVICE CONTROL ONE</description>
      </character>
      <character id="U00012" dec="18" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="BN" mirror="N" unicode1="DEVICE CONTROL TWO"/>
         <description unicode="1.1">DEVICE CONTROL TWO</description>
      </character>
      <character id="U00013" dec="19" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="BN" mirror="N" unicode1="DEVICE CONTROL THREE"/>
         <description unicode="1.1">DEVICE CONTROL THREE</description>
      </character>
      <character id="U00014" dec="20" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="BN" mirror="N" unicode1="DEVICE CONTROL FOUR"/>
         <description unicode="1.1">DEVICE CONTROL FOUR</description>
      </character>
      <character id="U00015" dec="21" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="BN" mirror="N" unicode1="NEGATIVE ACKNOWLEDGE"/>
         <description unicode="1.1">NEGATIVE ACKNOWLEDGE</description>
      </character>
      <character id="U00016" dec="22" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="BN" mirror="N" unicode1="SYNCHRONOUS IDLE"/>
         <description unicode="1.1">SYNCHRONOUS IDLE</description>
      </character>
      <character id="U00017" dec="23" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="BN" mirror="N" unicode1="END OF TRANSMISSION BLOCK"/>
         <description unicode="1.1">END OF TRANSMISSION BLOCK</description>
      </character>
      <character id="U00018" dec="24" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="BN" mirror="N" unicode1="CANCEL"/>
         <description unicode="1.1">CANCEL</description>
      </character>
      <character id="U00019" dec="25" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="BN" mirror="N" unicode1="END OF MEDIUM"/>
         <description unicode="1.1">END OF MEDIUM</description>
      </character>
      <character id="U0001A" dec="26" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="BN" mirror="N" unicode1="SUBSTITUTE"/>
         <description unicode="1.1">SUBSTITUTE</description>
      </character>
      <character id="U0001B" dec="27" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="BN" mirror="N" unicode1="ESCAPE"/>
         <description unicode="1.1">ESCAPE</description>
      </character>
      <character id="U0001C" dec="28" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="B" mirror="N" unicode1="INFORMATION SEPARATOR FOUR"/>
         <description unicode="1.1">INFORMATION SEPARATOR FOUR</description>
      </character>
      <character id="U0001D" dec="29" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="B" mirror="N" unicode1="INFORMATION SEPARATOR THREE"/>
         <description unicode="1.1">INFORMATION SEPARATOR THREE</description>
      </character>
      <character id="U0001E" dec="30" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="B" mirror="N" unicode1="INFORMATION SEPARATOR TWO"/>
         <description unicode="1.1">INFORMATION SEPARATOR TWO</description>
      </character>
      <character id="U0001F" dec="31" mode="unknown" type="other">
         <unicodedata category="Cc" combclass="0" bidi="S" mirror="N" unicode1="INFORMATION SEPARATOR ONE"/>
         <description unicode="1.1">INFORMATION SEPARATOR ONE</description>
      </character>
      <character id="U00020" dec="32" mode="text" type="other">
         <unicodedata category="Zs" combclass="0" bidi="WS" mirror="N" mathclass="S"/>
         <latex>\space </latex>
         <description unicode="1.1">SPACE</description>
      </character>
      <character id="U00021" dec="33" mode="text" type="punctuation">
         <unicodedata category="Po" combclass="0" bidi="ON" mirror="N" mathclass="N"/>
         <afii>EE35</afii>
         <latex>!</latex>
         <mathlatex set="unicode-math">\mathexclam</mathlatex>
         <entity id="excl" set="8879-isonum">
            <desc>=exclamation mark</desc>
         </entity>
         <entity id="excl" set="9573-2003-isonum">
            <desc>=exclamation mark</desc>
         </entity>
         <font name="ptmr7t" pos="33"/>
         <operator-dictionary priority="810" form="postfix" lspace="1" rspace="0"/>
         <description unicode="1.1">EXCLAMATION MARK</description>
      </character>
      <character id="U00021-00021" dec="33-33" image="none">
         <unicodedata/>
         <operator-dictionary priority="810" form="postfix" lspace="1" rspace="0"/>
         <description>MULTIPLE CHARACTER OPERATOR: !!</description>
      </character>
      <character id="U00021-0003D" dec="33-61" image="none">
         <unicodedata/>
         <operator-dictionary priority="260" form="infix" lspace="4" rspace="4"/>
         <description>MULTIPLE CHARACTER OPERATOR: !=</description>
      </character>
      <character id="U00022" dec="34" mode="text" type="other">
         <unicodedata category="Po" combclass="0" bidi="ON" mirror="N"/>
         <afii>0022</afii>
         <latex>"</latex>
         <entity id="quot" set="predefined" optional-semi="yes"/>
         <entity id="quot" set="xhtml1-special">
            <desc>quotation mark = APL quote</desc>
         </entity>
         <entity id="quot" set="8879-isonum">
            <desc>=quotation mark</desc>
         </entity>
         <entity id="quot" set="9573-2003-isonum">
            <desc>=quotation mark</desc>
         </entity>
         <entity id="QUOT" set="html5-uppercase" optional-semi="yes">
            <desc>legacy uppercase name</desc>
         </entity>
         <font name="ptmr7t" pos="34"/>
         <operator-dictionary priority="880" form="postfix" lspace="0" rspace="0" accent="true"/>
         <description unicode="1.1">QUOTATION MARK</description>
      </character>
      <character id="U00023" dec="35" mode="text" type="normal">
         <unicodedata category="Po" combclass="0" bidi="ET" mirror="N" mathclass="N"/>
         <afii>0023</afii>
         <latex>\#</latex>
         <mathlatex set="unicode-math">\mathoctothorpe</mathlatex>
         <APS>num</APS>
         <AIP>mesh</AIP>
         <Wolfram>NumberSign</Wolfram>
         <entity id="num" set="8879-isonum">
            <desc>=number sign</desc>
         </entity>
         <entity id="num" set="9573-2003-isonum">
            <desc>=number sign</desc>
         </entity>
         <font name="ptmr7t" pos="35"/>
         <description unicode="1.1">NUMBER SIGN</description>
      </character>
      <character id="U00024" dec="36" mode="mixed" type="normal">
         <unicodedata category="Sc" combclass="0" bidi="ET" mirror="N" mathclass="N"/>
         <afii>00A4</afii>
         <latex>\textdollar </latex>
         <mathlatex>\$</mathlatex>
         <mathlatex set="unicode-math">\mathdollar</mathlatex>
         <Elsevier grid="bhc" ent="">
            <desc>dollar sign</desc>
            <elsrender>\$</elsrender>
         </Elsevier>
         <APS>dollar</APS>
         <AIP>dollar</AIP>
         <entity id="dollar" set="8879-isonum">
            <desc>=dollar sign</desc>
         </entity>
         <entity id="dollar" set="9573-2003-isonum">
            <desc>=dollar sign</desc>
         </entity>
         <font name="ptmr7t" pos="36"/>
         <description unicode="1.1">DOLLAR SIGN</description>
      </character>
      <character id="U00025" dec="37" mode="text" type="normal">
         <unicodedata category="Po" combclass="0" bidi="ET" mirror="N" mathclass="N"/>
         <afii>0025</afii>
         <latex>\%</latex>
         <mathlatex set="unicode-math">\mathpercent</mathlatex>
         <APS>percnt</APS>
         <AIP>percent</AIP>
         <entity id="percnt" set="8879-isonum">
            <desc>=percent sign</desc>
         </entity>
         <entity id="percnt" set="9573-2003-isonum">
            <desc>=percent sign</desc>
         </entity>
         <font name="ptmr7t" pos="37"/>
         <operator-dictionary form="infix" lspace="3" rspace="3" priority="640"/>
         <description unicode="1.1">PERCENT SIGN</description>
      </character>
      <character id="U00026" dec="38" mode="text" type="other">
         <unicodedata category="Po" combclass="0" bidi="ON" mirror="N" mathclass="N"/>
         <afii>0026</afii>
         <latex>\&amp;</latex>
         <mathlatex set="unicode-math">\mathampersand</mathlatex>
         <Elsevier grid="bha" ent="amp">
            <desc>ampersand</desc>
         </Elsevier>
         <APS>amp</APS>
         <AIP>amp</AIP>
         <entity id="amp" set="predefined" optional-semi="yes"/>
         <entity id="AMP" set="html5-uppercase" optional-semi="yes">
            <desc>legacy uppercase name</desc>
         </entity>
         <entity id="amp" set="8879-isonum">
            <desc>=ampersand</desc>
         </entity>
         <entity id="amp" set="9573-2003-isonum">
            <desc>=ampersand</desc>
         </entity>
         <operator-dictionary priority="880" form="postfix" lspace="0" rspace="0"/>
         <description unicode="1.1">AMPERSAND</description>
      </character>
      <character id="U00026-00026" dec="38-38" image="none">
         <unicodedata/>
         <operator-dictionary priority="200" form="infix" lspace="4" rspace="4"/>
         <description>MULTIPLE CHARACTER OPERATOR: &amp;&amp;</description>
      </character>
      <character id="U00027" dec="39" mode="text" type="other">
         <unicodedata category="Po" combclass="0" bidi="ON" mirror="N" unicode1="APOSTROPHE-QUOTE"/>
         <afii>0027</afii>
         <latex>\textquotesingle </latex>
         <entity id="apos" set="predefined"/>
         <entity id="apos" set="8879-isonum">
            <desc>=apostrophe</desc>
         </entity>
         <entity id="apos" set="9573-2003-isonum">
            <desc>=apostrophe</desc>
         </entity>
         <operator-dictionary priority="880" form="postfix" lspace="0" rspace="0" accent="true"/>
         <description unicode="1.1">APOSTROPHE</description>
      </character>
      <character id="U00028" dec="40" mode="text" type="opening">
         <unicodedata category="Ps" combclass="0" bidi="ON" mirror="Y" unicode1="OPENING PARENTHESIS" mathclass="O"/>
         <afii>0028</afii>
         <latex>(</latex>
         <mathlatex set="unicode-math">\lparen</mathlatex>
         <AIP>lpar</AIP>
         <entity id="lpar" set="8879-isonum">
            <desc>O: =left parenthesis</desc>
         </entity>
         <entity id="lpar" set="9573-2003-isonum">
            <desc>O: =left parenthesis</desc>
         </entity>
         <font name="ptmlucrm" pos="132"/>
         <operator-dictionary priority="20" form="prefix" symmetric="true" fence="true" stretchy="true" lspace="0" rspace="0"/>
         <description unicode="1.1">LEFT PARENTHESIS</description>
      </character>
      <character id="U00029" dec="41" mode="text" type="closing">
         <unicodedata category="Pe" combclass="0" bidi="ON" mirror="Y" unicode1="CLOSING PARENTHESIS" mathclass="C"/>
         <afii>0029</afii>
         <latex>)</latex>
         <mathlatex set="unicode-math">\rparen</mathlatex>
         <AIP>rpar</AIP>
         <entity id="rpar" set="8879-isonum">
            <desc>C: =right parenthesis</desc>
         </entity>
         <entity id="rpar" set="9573-2003-isonum">
            <desc>C: =right parenthesis</desc>
         </entity>
         <font name="ptmlucrm" pos="133"/>
         <operator-dictionary priority="20" form="postfix" symmetric="true" fence="true" stretchy="true" lspace="0" rspace="0"/>
         <description unicode="1.1">RIGHT PARENTHESIS</description>
      </character>
      <character id="U0002A" dec="42" mode="math" type="other">
         <unicodedata category="Po" combclass="0" bidi="ON" mirror="N" mathclass="N"/>
         <afii>002A</afii>
         <latex>\ast </latex>
         <Elsevier grid="bl8" ent="">
            <desc>pseudo-superscript asterisk (ASCII *)</desc>
            <elsrender>*</elsrender>
         </Elsevier>
         <APS>ast</APS>
         <entity id="ast" set="8879-isonum">
            <desc>/ast B: =asterisk</desc>
         </entity>
         <entity id="ast" set="9573-2003-isonum">
            <desc>/ast B: =asterisk</desc>
         </entity>
         <entity id="midast" set="9573-1991-isoamsb">
            <desc>/ast B: asterisk</desc>
         </entity>
         <entity id="midast" set="9573-2003-isoamsb">
            <desc>/ast B: asterisk</desc>
         </entity>
         <font name="hlcry" pos="3"/>
         <operator-dictionary priority="390" form="infix" lspace="3" rspace="3"/>
         <description unicode="1.1">ASTERISK</description>
      </character>
      <character id="U0002A-0002A" dec="42-42" image="none">
         <unicodedata/>
         <operator-dictionary priority="780" form="infix" lspace="1" rspace="1"/>
         <description>MULTIPLE CHARACTER OPERATOR: **</description>
      </character>
      <character id="U0002A-0003D" dec="42-61" image="none">
         <unicodedata/>
         <operator-dictionary priority="260" form="infix" lspace="4" rspace="4"/>
         <description>MULTIPLE CHARACTER OPERATOR: *=</description>
      </character>
      <character id="U0002B" dec="43" mode="math" type="binaryop">
         <unicodedata category="Sm" combclass="0" bidi="ES" mirror="N" mathclass="V"/>
         <afii>002B</afii>
         <latex>+</latex>
         <mathlatex set="unicode-math">\mathplus</mathlatex>
         <ACS>plus</ACS>
         <AIP>plus</AIP>
         <entity id="plus" set="8879-isonum">
            <desc>=plus sign B:</desc>
         </entity>
         <entity id="plus" set="9573-2003-isonum">
            <desc>=plus sign B:</desc>
         </entity>
         <font name="hlcry" pos="6"/>
         <operator-dictionary priority="275" form="infix" lspace="4" rspace="4"/>
         <operator-dictionary priority="275" form="prefix" lspace="0" rspace="1"/>
         <description unicode="1.1">PLUS SIGN</description>
      </character>
      <character id="U0002B-0002B" dec="43-43" image="none">
         <unicodedata/>
         <operator-dictionary priority="880" form="postfix" lspace="0" rspace="0"/>
         <description>MULTIPLE CHARACTER OPERATOR: ++</description>
      </character>
      <character id="U0002B-0003D" dec="43-61" image="none">
         <unicodedata/>
         <operator-dictionary priority="260" form="infix" lspace="4" rspace="4"/>
         <description>MULTIPLE CHARACTER OPERATOR: +=</description>
      </character>
      <character id="U0002C" dec="44" mode="text" type="punctuation">
         <unicodedata category="Po" combclass="0" bidi="CS" mirror="N" mathclass="P"/>
         <afii>002C</afii>
         <latex>,</latex>
         <mathlatex set="unicode-math">\mathcomma</mathlatex>
         <entity id="comma" set="8879-isonum">
            <desc>P: =comma</desc>
         </entity>
         <entity id="comma" set="9573-2003-isonum">
            <desc>P: =comma</desc>
         </entity>
         <font name="ptmlucrm" pos="59"/>
         <operator-dictionary priority="40" form="infix" separator="true" lspace="0" rspace="3" linebreakstyle="after"/>
         <description unicode="1.1">COMMA</description>
      </character>
      <character id="U0002D" dec="45" mode="math" type="other">
         <unicodedata category="Pd" combclass="0" bidi="ES" mirror="N" mathclass="N"/>
         <afii>002D</afii>
         <latex>-</latex>
         <AIP>hyphen</AIP>
         <operator-dictionary priority="275" form="infix" lspace="4" rspace="4"/>
         <operator-dictionary priority="275" form="prefix" lspace="0" rspace="1"/>
         <description unicode="1.1">HYPHEN-MINUS</description>
      </character>
      <character id="U0002D-0002D" dec="45-45" image="none">
         <unicodedata/>
         <operator-dictionary priority="880" form="postfix" lspace="0" rspace="0"/>
         <description>MULTIPLE CHARACTER OPERATOR: --</description>
      </character>
      <character id="U0002D-0003D" dec="45-61" image="none">
         <unicodedata/>
         <operator-dictionary priority="260" form="infix" lspace="4" rspace="4"/>
         <description>MULTIPLE CHARACTER OPERATOR: -=</description>
      </character>
      <character id="U0002D-0003E" dec="45-62" image="none">
         <unicodedata/>
         <operator-dictionary priority="90" form="infix" lspace="5" rspace="5"/>
         <description>MULTIPLE CHARACTER OPERATOR: -&gt;</description>
      </character>
      <character id="U0002E" dec="46" mode="text" type="punctuation">
         <unicodedata category="Po" combclass="0" bidi="CS" mirror="N" unicode1="PERIOD" mathclass="P"/>
         <afii>002E</afii>
         <latex>.</latex>
         <mathlatex set="unicode-math">\mathperiod</mathlatex>
         <IEEE>\ldotp</IEEE>
         <entity id="period" set="8879-isonum">
            <desc>=full stop, period</desc>
         </entity>
         <entity id="period" set="9573-2003-isonum">
            <desc>=full stop, period</desc>
         </entity>
         <font name="ptmlucrm" pos="58"/>
         <operator-dictionary priority="390" form="infix" lspace="3" rspace="3"/>
         <description unicode="1.1">FULL STOP</description>
      </character>
      <character id="U0002E-0002E" dec="46-46" image="none">
         <unicodedata/>
         <operator-dictionary priority="100" form="postfix" lspace="0" rspace="0"/>
         <description>MULTIPLE CHARACTER OPERATOR: ..</description>
      </character>
      <character id="U0002E-0002E-0002E" dec="46-46-46" image="none">
         <unicodedata/>
         <operator-dictionary priority="100" form="postfix" lspace="0" rspace="0"/>
         <description>MULTIPLE CHARACTER OPERATOR: ...</description>
      </character>
      <character id="U0002F" dec="47" mode="text" type="other">
         <unicodedata category="Po" combclass="0" bidi="CS" mirror="N" unicode1="SLASH" mathclass="B"/>
         <afii>002F</afii>
         <latex>/</latex>
         <mathlatex set="unicode-math">\mathslash</mathlatex>
         <APS>sol</APS>
         <entity id="sol" set="8879-isonum">
            <desc>=solidus</desc>
         </entity>
         <entity id="sol" set="9573-2003-isonum">
            <desc>=solidus</desc>
         </entity>
         <operator-dictionary priority="660" form="infix" lspace="1" rspace="1"/>
         <description unicode="1.1">SOLIDUS</description>
      </character>
      <character id="U0002F-0002F" dec="47-47" image="none">
         <unicodedata/>
         <operator-dictionary priority="820" form="infix" lspace="1" rspace="1"/>
         <description>MULTIPLE CHARACTER OPERATOR: //</description>
      </character>
      <character id="U0002F-0003D" dec="47-61" image="none">
         <unicodedata/>
         <operator-dictionary priority="260" form="infix" lspace="4" rspace="4"/>
         <description>MULTIPLE CHARACTER OPERATOR: /=</description>
      </character>
      <character id="U00030" dec="48" mode="text" type="other">
         <unicodedata category="Nd" combclass="0" bidi="EN" decimal="0" digit="0" numeric="0" mirror="N" mathclass="N"/>
         <latex>0</latex>
         <description unicode="1.1">DIGIT ZERO</description>
      </character>
      <character id="U00031" dec="49" mode="text" type="other">
         <unicodedata category="Nd" combclass="0" bidi="EN" decimal="1" digit="1" numeric="1" mirror="N" mathclass="N"/>
         <latex>1</latex>
         <description unicode="1.1">DIGIT ONE</description>
      </character>
      <character id="U00032" dec="50" mode="text" type="other">
         <unicodedata category="Nd" combclass="0" bidi="EN" decimal="2" digit="2" numeric="2" mirror="N" mathclass="N"/>
         <latex>2</latex>
         <description unicode="1.1">DIGIT TWO</description>
      </character>
      <character id="U00033" dec="51" mode="text" type="other">
         <unicodedata category="Nd" combclass="0" bidi="EN" decimal="3" digit="3" numeric="3" mirror="N" mathclass="N"/>
         <latex>3</latex>
         <description unicode="1.1">DIGIT THREE</description>
      </character>
      <character id="U00034" dec="52" mode="text" type="other">
         <unicodedata category="Nd" combclass="0" bidi="EN" decimal="4" digit="4" numeric="4" mirror="N" mathclass="N"/>
         <latex>4</latex>
         <description unicode="1.1">DIGIT FOUR</description>
      </character>
      <character id="U00035" dec="53" mode="text" type="other">
         <unicodedata category="Nd" combclass="0" bidi="EN" decimal="5" digit="5" numeric="5" mirror="N" mathclass="N"/>
         <latex>5</latex>
         <description unicode="1.1">DIGIT FIVE</description>
      </character>
      <character id="U00036" dec="54" mode="text" type="other">
         <unicodedata category="Nd" combclass="0" bidi="EN" decimal="6" digit="6" numeric="6" mirror="N" mathclass="N"/>
         <latex>6</latex>
         <description unicode="1.1">DIGIT SIX</description>
      </character>
      <character id="U00037" dec="55" mode="text" type="other">
         <unicodedata category="Nd" combclass="0" bidi="EN" decimal="7" digit="7" numeric="7" mirror="N" mathclass="N"/>
         <latex>7</latex>
         <description unicode="1.1">DIGIT SEVEN</description>
      </character>
      <character id="U00038" dec="56" mode="text" type="other">
         <unicodedata category="Nd" combclass="0" bidi="EN" decimal="8" digit="8" numeric="8" mirror="N" mathclass="N"/>
         <latex>8</latex>
         <description unicode="1.1">DIGIT EIGHT</description>
      </character>
      <character id="U00039" dec="57" mode="text" type="other">
         <unicodedata category="Nd" combclass="0" bidi="EN" decimal="9" digit="9" numeric="9" mirror="N" mathclass="N"/>
         <latex>9</latex>
         <description unicode="1.1">DIGIT NINE</description>
      </character>
      <character id="U0003A" dec="58" mode="text" type="punctuation">
         <unicodedata category="Po" combclass="0" bidi="CS" mirror="N" mathclass="P"/>
         <afii>003A</afii>
         <latex>:</latex>
         <mathlatex set="unicode-math">\mathcolon</mathlatex>
         <AMS>\colon</AMS>
         <IEEE>\colon</IEEE>
         <entity id="colon" set="8879-isonum">
            <desc>/colon P:</desc>
         </entity>
         <entity id="colon" set="9573-2003-isonum">
            <desc>/colon P:</desc>
         </entity>
         <operator-dictionary priority="100" form="infix" lspace="1" rspace="2"/>
         <description unicode="1.1">COLON</description>
      </character>
      <character id="U0003A-0003D" dec="58-61" image="none">
         <unicodedata/>
         <operator-dictionary priority="260" form="infix" lspace="4" rspace="4"/>
         <description>MULTIPLE CHARACTER OPERATOR: :=</description>
      </character>
      <character id="U0003B" dec="59" mode="math" type="punctuation">
         <unicodedata category="Po" combclass="0" bidi="ON" mirror="N" mathclass="P"/>
         <afii>003B</afii>
         <latex>;</latex>
         <mathlatex set="unicode-math">\mathsemicolon</mathlatex>
         <entity id="semi" set="8879-isonum">
            <desc>=semicolon P:</desc>
         </entity>
         <entity id="semi" set="9573-2003-isonum">
            <desc>=semicolon P:</desc>
         </entity>
         <font name="ptmr7t" pos="59"/>
         <operator-dictionary priority="30" form="infix" separator="true" lspace="0" rspace="3" linebreakstyle="after"/>
         <description unicode="1.1">SEMICOLON</description>
      </character>
      <character id="U0003C" dec="60" mode="math" type="relation">
         <unicodedata category="Sm" combclass="0" bidi="ON" mirror="Y" mathclass="R"/>
         <afii>003C</afii>
         <latex>&lt;</latex>
         <mathlatex set="unicode-math">\less</mathlatex>
         <Elsevier grid="bka" ent="lt">
            <desc>less than sign</desc>
         </Elsevier>
         <AMS>\less</AMS>
         <APS>lt</APS>
         <AIP>lt</AIP>
         <entity id="lt" set="predefined" optional-semi="yes"/>
         <entity id="lt" set="xhtml1-special">
            <desc>less-than sign</desc>
         </entity>
         <entity id="lt" set="8879-isonum">
            <desc>=less-than sign R:</desc>
         </entity>
         <entity id="lt" set="9573-2003-isonum">
            <desc>=less-than sign R:</desc>
         </entity>
         <entity id="LT" set="html5-uppercase" optional-semi="yes">
            <desc>legacy uppercase name</desc>
         </entity>
         <font name="ptmlucrm" pos="60"/>
         <operator-dictionary priority="245" form="infix" lspace="5" rspace="5"/>
         <description unicode="1.1">LESS-THAN SIGN</description>
      </character>
      <character id="U0003C-0003D" dec="60-61" image="none">
         <unicodedata/>
         <operator-dictionary priority="241" form="infix" lspace="5" rspace="5"/>
         <description>MULTIPLE CHARACTER OPERATOR: &lt;=</description>
      </character>
      <character id="U0003C-0003E" dec="60-62" image="none">
         <unicodedata/>
         <operator-dictionary priority="780" form="infix" lspace="1" rspace="1"/>
         <description>MULTIPLE CHARACTER OPERATOR: &lt;&gt;</description>
      </character>
      <character id="U0003C-020D2" dec="60-8402" type="other" mode="unknown">
         <unicodedata/>
         <entity id="nvlt" set="9573-1991-isoamsn">
            <desc>not, vert, less-than</desc>
         </entity>
         <entity id="nvlt" set="9573-2003-isoamsn">
            <desc>not, vert, less-than</desc>
         </entity>
         <description unicode="combination">LESS-THAN SIGN with vertical line</description>
      </character>
      <character id="U0003D" dec="61" mode="text" type="relation">
         <unicodedata category="Sm" combclass="0" bidi="ON" mirror="N" mathclass="R"/>
         <afii>003D</afii>
         <latex>=</latex>
         <mathlatex set="unicode-math">\equal</mathlatex>
         <ACS>equals</ACS>
         <AIP>equals</AIP>
         <entity id="equals" set="8879-isonum">
            <desc>=equals sign R:</desc>
         </entity>
         <entity id="equals" set="9573-2003-isonum">
            <desc>=equals sign R:</desc>
         </entity>
         <font name="hlcry" pos="131"/>
         <operator-dictionary priority="260" form="infix" lspace="5" rspace="5"/>
         <description unicode="1.1">EQUALS SIGN</description>
      </character>
      <character id="U0003D-0003D" dec="61-61" image="none">
         <unicodedata/>
         <operator-dictionary priority="260" form="infix" lspace="4" rspace="4"/>
         <description>MULTIPLE CHARACTER OPERATOR: ==</description>
      </character>
      <character id="U0003D-020D2" dec="61-8402" type="other" mode="unknown">
         <unicodedata/>
         <description unicode="combination">EQUALS SIGN with vertical line</description>
      </character>
      <character id="U0003D-020E5" dec="61-8421" mode="math" type="relation">
         <unicodedata/>
         <afii>DB44</afii>
         <entity id="bne" set="STIX"/>
         <entity id="bne" set="9573-1991-isotech">
            <desc>reverse not equal</desc>
         </entity>
         <entity id="bne" set="9573-2003-isotech">
            <desc>reverse not equal</desc>
         </entity>
         <description unicode="combination">EQUALS SIGN with reverse slash</description>
      </character>
      <character id="U0003E" dec="62" mode="math" type="relation">
         <unicodedata category="Sm" combclass="0" bidi="ON" mirror="Y" mathclass="R"/>
         <afii>003E</afii>
         <latex>&gt;</latex>
         <mathlatex set="unicode-math">\greater</mathlatex>
         <Elsevier grid="bma" ent="">
            <desc>greater than sign</desc>
            <elsrender>&gt;</elsrender>
         </Elsevier>
         <AMS>\greater</AMS>
         <APS>gt</APS>
         <AIP>gt</AIP>
         <entity id="gt" set="predefined" optional-semi="yes"/>
         <entity id="gt" set="xhtml1-special">
            <desc>greater-than sign</desc>
         </entity>
         <entity id="gt" set="8879-isonum">
            <desc>=greater-than sign R:</desc>
         </entity>
         <entity id="gt" set="9573-2003-isonum">
            <desc>=greater-than sign R:</desc>
         </entity>
         <entity id="GT" set="html5-uppercase" optional-semi="yes">
            <desc>legacy uppercase name</desc>
         </entity>
         <font name="ptmlucrm" pos="62"/>
         <operator-dictionary priority="243" form="infix" lspace="5" rspace="5"/>
         <description unicode="1.1">GREATER-THAN SIGN</description>
      </character>
      <character id="U0003E-0003D" dec="62-61" image="none">
         <unicodedata/>
         <operator-dictionary priority="243" form="infix" lspace="5" rspace="5"/>
         <description>MULTIPLE CHARACTER OPERATOR: &gt;=</description>
      </character>
      <character id="U0003E-020D2" dec="62-8402" type="other" mode="unknown">
         <unicodedata/>
         <entity id="nvgt" set="9573-1991-isoamsn">
            <desc>not, vert, greater-than</desc>
         </entity>
         <entity id="nvgt" set="9573-2003-isoamsn">
            <desc>not, vert, greater-than</desc>
         </entity>
         <description unicode="combination">GREATER-THAN SIGN with vertical line</description>
      </character>
      <character id="U0003F" dec="63" mode="text" type="punctuation">
         <unicodedata category="Po" combclass="0" bidi="ON" mirror="N" mathclass="P"/>
         <afii>003F</afii>
         <latex>?</latex>
         <mathlatex set="unicode-math">\mathquestion</mathlatex>
         <entity id="quest" set="8879-isonum">
            <desc>=question mark</desc>
         </entity>
         <entity id="quest" set="9573-2003-isonum">
            <desc>=question mark</desc>
         </entity>
         <font name="ptmr7t" pos="63"/>
         <operator-dictionary priority="835" form="infix" lspace="1" rspace="1"/>
         <description unicode="1.1">QUESTION MARK</description>
      </character>
      <character id="U00040" dec="64" mode="text" type="normal">
         <unicodedata category="Po" combclass="0" bidi="ON" mirror="N" mathclass="N"/>
         <afii>0040</afii>
         <latex>@</latex>
         <mathlatex set="unicode-math">\mathatsign</mathlatex>
         <AIP>at</AIP>
         <entity id="commat" set="8879-isonum">
            <desc>=commercial at</desc>
         </entity>
         <entity id="commat" set="9573-2003-isonum">
            <desc>=commercial at</desc>
         </entity>
         <font name="ptmr7t" pos="64"/>
         <operator-dictionary priority="825" form="infix" lspace="1" rspace="1"/>
         <description unicode="1.1">COMMERCIAL AT</description>
      </character>
      <character id="U00041" dec="65" mode="text" type="other">
         <unicodedata category="Lu" combclass="0" bidi="L" mirror="N" lower="0061" mathclass="A"/>
         <latex>A</latex>
         <description unicode="1.1">LATIN CAPITAL LETTER A</description>
      </character>
      <character id="U00042" dec="66" mode="text" type="other">
         <unicodedata category="Lu" combclass="0" bidi="L" mirror="N" lower="0062" mathclass="A"/>
         <latex>B</latex>
         <description unicode="1.1">LATIN CAPITAL LETTER B</description>
      </character>
      <character id="U00043" dec="67" mode="text" type="other">
         <unicodedata category="Lu" combclass="0" bidi="L" mirror="N" lower="0063" mathclass="A"/>
         <latex>C</latex>
         <description unicode="1.1">LATIN CAPITAL LETTER C</description>
      </character>
      <character id="U00044" dec="68" mode="text" type="other">
         <unicodedata category="Lu" combclass="0" bidi="L" mirror="N" lower="0064" mathclass="A"/>
         <latex>D</latex>
         <description unicode="1.1">LATIN CAPITAL LETTER D</description>
      </character>
      <character id="U00045" dec="69" mode="text" type="other">
         <unicodedata category="Lu" combclass="0" bidi="L" mirror="N" lower="0065" mathclass="A"/>
         <latex>E</latex>
         <description unicode="1.1">LATIN CAPITAL LETTER E</description>
      </character>
      <character id="U00046" dec="70" mode="text" type="other">
         <unicodedata category="Lu" combclass="0" bidi="L" mirror="N" lower="0066" mathclass="A"/>
         <latex>F</latex>
         <description unicode="1.1">LATIN CAPITAL LETTER F</description>
      </character>
      <character id="U00047" dec="71" mode="text" type="other">
         <unicodedata category="Lu" combclass="0" bidi="L" mirror="N" lower="0067" mathclass="A"/>
         <latex>G</latex>
         <description unicode="1.1">LATIN CAPITAL LETTER G</description>
      </character>
      <character id="U00048" dec="72" mode="text" type="other">
         <unicodedata category="Lu" combclass="0" bidi="L" mirror="N" lower="0068" mathclass="A"/>
         <latex>H</latex>
         <description unicode="1.1">LATIN CAPITAL LETTER H</description>
      </character>
      <character id="U00049" dec="73" mode="text" type="other">
         <unicodedata category="Lu" combclass="0" bidi="L" mirror="N" lower="0069" mathclass="A"/>
         <latex>I</latex>
         <description unicode="1.1">LATIN CAPITAL LETTER I</description>
      </character>
      <character id="U0004A" dec="74" mode="text" type="other">
         <unicodedata category="Lu" combclass="0" bidi="L" mirror="N" lower="006A" mathclass="A"/>
         <latex>J</latex>
         <description unicode="1.1">LATIN CAPITAL LETTER J</description>
      </character>
      <character id="U0004B" dec="75" mode="text" type="other">
         <unicodedata category="Lu" combclass="0" bidi="L" mirror="N" lower="006B" mathclass="A"/>
         <latex>K</latex>
         <description unicode="1.1">LATIN CAPITAL LETTER K</description>
      </character>
      <character id="U0004C" dec="76" mode="text" type="other">
         <unicodedata category="Lu" combclass="0" bidi="L" mirror="N" lower="006C" mathclass="A"/>
         <afii>004C</afii>
         <latex>L</latex>
         <Elsevier grid="pfl" ent="">
            <desc>capital L  (phonetic symbol)</desc>
            <elsrender>L</elsrender>
         </Elsevier>
         <description unicode="1.1">LATIN CAPITAL LETTER L</description>
      </character>
      <character id="U0004D" dec="77" mode="text" type="other">
         <unicodedata category="Lu" combclass="0" bidi="L" mirror="N" lower="006D" mathclass="A"/>
         <latex>M</latex>
         <description unicode="1.1">LATIN CAPITAL LETTER M</description>
      </character>
      <character id="U0004E" dec="78" mode="text" type="other">
         <unicodedata category="Lu" combclass="0" bidi="L" mirror="N" lower="006E" mathclass="A"/>
         <latex>N</latex>
         <description unicode="1.1">LATIN CAPITAL LETTER N</description>
      </character>
      <character id="U0004F" dec="79" mode="text" type="other">
         <unicodedata category="Lu" combclass="0" bidi="L" mirror="N" lower="006F" mathclass="A"/>
         <latex>O</latex>
         <description unicode="1.1">LATIN CAPITAL LETTER O</description>
      </character>
      <character id="U0005-00072" dec="80-114">
         <description>MULTIPLE CHARACTER OPERATOR: Pr</description>
      </character>
      <character id="U00050" dec="80" mode="text" type="other">
         <unicodedata category="Lu" combclass="0" bidi="L" mirror="N" lower="0070" mathclass="A"/>
         <latex>P</latex>
         <description unicode="1.1">LATIN CAPITAL LETTER P</description>
      </character>
      <character id="U00050-00072" dec="80-114">
         <description>MULTIPLE CHARACTER OPERATOR: Pr</description>
      </character>
      <character id="U00051" dec="81" mode="text" type="other">
         <unicodedata category="Lu" combclass="0" bidi="L" mirror="N" lower="0071" mathclass="A"/>
         <latex>Q</latex>
         <description unicode="1.1">LATIN CAPITAL LETTER Q</description>
      </character>
      <character id="U00052" dec="82" mode="text" type="other">
         <unicodedata category="Lu" combclass="0" bidi="L" mirror="N" lower="0072" mathclass="A"/>
         <latex>R</latex>
         <description unicode="1.1">LATIN CAPITAL LETTER R</description>
      </character>
      <character id="U00053" dec="83" mode="text" type="other">
         <unicodedata category="Lu" combclass="0" bidi="L" mirror="N" lower="0073" mathclass="A"/>
         <latex>S</latex>
         <description unicode="1.1">LATIN CAPITAL LETTER S</description>
      </character>
      <character id="U00054" dec="84" mode="text" type="other">
         <unicodedata category="Lu" combclass="0" bidi="L" mirror="N" lower="0074" mathclass="A"/>
         <latex>T</latex>
         <description unicode="1.1">LATIN CAPITAL LETTER T</description>
      </character>
      <character id="U00055" dec="85" mode="text" type="other">
         <unicodedata category="Lu" combclass="0" bidi="L" mirror="N" lower="0075" mathclass="A"/>
         <latex>U</latex>
         <description unicode="1.1">LATIN CAPITAL LETTER U</description>
      </character>
      <character id="U00056" dec="86" mode="text" type="other">
         <unicodedata category="Lu" combclass="0" bidi="L" mirror="N" lower="0076" mathclass="A"/>
         <latex>V</latex>
         <description unicode="1.1">LATIN CAPITAL LETTER V</description>
      </character>
      <character id="U00057" dec="87" mode="text" type="other">
         <unicodedata category="Lu" combclass="0" bidi="L" mirror="N" lower="0077" mathclass="A"/>
         <latex>W</latex>
         <description unicode="1.1">LATIN CAPITAL LETTER W</description>
      </character>
      <character id="U00058" dec="88" mode="text" type="other">
         <unicodedata category="Lu" combclass="0" bidi="L" mirror="N" lower="0078" mathclass="A"/>
         <latex>X</latex>
         <description unicode="1.1">LATIN CAPITAL LETTER X</description>
      </character>
      <character id="U00059" dec="89" mode="text" type="other">
         <unicodedata category="Lu" combclass="0" bidi="L" mirror="N" lower="0079" mathclass="A"/>
         <latex>Y</latex>
         <description unicode="1.1">LATIN CAPITAL LETTER Y</description>
      </character>
      <character id="U0005A" dec="90" mode="text" type="other">
         <unicodedata category="Lu" combclass="0" bidi="L" mirror="N" lower="007A" mathclass="A"/>
         <latex>Z</latex>
         <description unicode="1.1">LATIN CAPITAL LETTER Z</description>
      </character>
      <character id="U0005B" dec="91" mode="text" type="opening">
         <unicodedata category="Ps" combclass="0" bidi="ON" mirror="Y" unicode1="OPENING SQUARE BRACKET" mathclass="O"/>
         <afii>005B</afii>
         <latex>[</latex>
         <mathlatex set="unicode-math">\lbrack</mathlatex>
         <AMS>\lbrack</AMS>
         <AIP>lsqb</AIP>
         <IEEE>\lbrack</IEEE>
         <entity id="lsqb" set="8879-isonum">
            <desc>/lbrack O: =left square bracket</desc>
         </entity>
         <entity id="lsqb" set="9573-2003-isonum">
            <desc>/lbrack O: =left square bracket</desc>
         </entity>
         <entity id="lbrack" set="mmlalias">
            <desc>alias ISONUM lsqb</desc>
         </entity>
         <font name="ptmlucrm" pos="134"/>
         <operator-dictionary priority="20" form="prefix" symmetric="true" fence="true" stretchy="true" lspace="0" rspace="0"/>
         <description unicode="1.1">LEFT SQUARE BRACKET</description>
      </character>
      <character id="U0005C" dec="92" mode="mixed" type="normal">
         <unicodedata category="Po" combclass="0" bidi="ON" mirror="N" unicode1="BACKSLASH" mathclass="B"/>
         <afii>EE3C</afii>
         <latex>\textbackslash </latex>
         <mathlatex>\backslash </mathlatex>
         <mathlatex set="unicode-math">\backslash</mathlatex>
         <AMS>\backslash</AMS>
         <APS>bsol</APS>
         <AIP>bsol</AIP>
         <IEEE>\backslash</IEEE>
         <entity id="bsol" set="8879-isonum">
            <desc>/backslash =reverse solidus</desc>
         </entity>
         <entity id="bsol" set="9573-2003-isonum">
            <desc>/backslash =reverse solidus</desc>
         </entity>
         <font name="hlcry" pos="110"/>
         <operator-dictionary form="infix" lspace="0" rspace="0" priority="650"/>
         <description unicode="1.1">REVERSE SOLIDUS</description>
      </character>
      <character id="U0005C-02282" dec="92-8834" mode="math" type="relation">
         <unicodedata/>
         <description>REVERSE SOLIDUS, SUBSET OF</description>
      </character>
      <character id="U0005D" dec="93" mode="text" type="closing">
         <unicodedata category="Pe" combclass="0" bidi="ON" mirror="Y" unicode1="CLOSING SQUARE BRACKET" mathclass="C"/>
         <afii>005D</afii>
         <latex>]</latex>
         <mathlatex set="unicode-math">\rbrack</mathlatex>
         <AMS>\rbrack</AMS>
         <AIP>rsqb</AIP>
         <IEEE>\rbrack</IEEE>
         <entity id="rsqb" set="8879-isonum">
            <desc>/rbrack C: =right square bracket</desc>
         </entity>
         <entity id="rsqb" set="9573-2003-isonum">
            <desc>/rbrack C: =right square bracket</desc>
         </entity>
         <entity id="rbrack" set="mmlalias">
            <desc>alias ISONUM rsqb</desc>
         </entity>
         <font name="ptmlucrm" pos="135"/>
         <operator-dictionary priority="20" form="postfix" symmetric="true" fence="true" stretchy="true" lspace="0" rspace="0"/>
         <description unicode="1.1">RIGHT SQUARE BRACKET</description>
      </character>
      <character id="U0005E" dec="94" mode="text" type="other">
         <unicodedata category="Sk" combclass="0" bidi="ON" mirror="N" unicode1="SPACING CIRCUMFLEX" mathclass="N"/>
         <afii>2323</afii>
         <latex>\^{}</latex>
         <AMS>\textasciicircumflex</AMS>
         <entity id="Hat" set="mmlextra">
            <desc>circumflex accent</desc>
         </entity>
         <operator-dictionary priority="880" form="postfix" lspace="0" rspace="0" accent="true" stretchy="true"/>
         <operator-dictionary priority="780" form="infix" lspace="1" rspace="1"/>
         <description unicode="1.1">CIRCUMFLEX ACCENT</description>
      </character>
      <character id="U0005F" dec="95" mode="math" type="other">
         <unicodedata category="Pc" combclass="0" bidi="ON" mirror="N" unicode1="SPACING UNDERSCORE" mathclass="N"/>
         <afii>005F</afii>
         <latex>\_</latex>
         <AIP>lowbar</AIP>
         <entity id="lowbar" set="8879-isonum">
            <desc>=low line</desc>
         </entity>
         <entity id="lowbar" set="9573-2003-isonum">
            <desc>=low line</desc>
         </entity>
         <entity id="UnderBar" set="mmlextra">
            <desc>combining low line</desc>
         </entity>
         <operator-dictionary priority="880" form="postfix" accent="true" stretchy="true" lspace="0" rspace="0"/>
         <operator-dictionary priority="900" form="infix" lspace="1" rspace="1"/>
         <description unicode="1.1">LOW LINE</description>
      </character>
      <character id="U00060" dec="96" mode="text" type="other">
         <unicodedata category="Sk" combclass="0" bidi="ON" mirror="N" unicode1="SPACING GRAVE" mathclass="D"/>
         <afii>0060</afii>
         <latex>\textasciigrave </latex>
         <AMS>\textasciigrave</AMS>
         <entity id="grave" set="8879-isodia">
            <desc>=grave accent</desc>
         </entity>
         <entity id="grave" set="9573-2003-isodia">
            <desc>=grave accent</desc>
         </entity>
         <entity id="DiacriticalGrave" set="mmlalias">
            <desc>alias ISODIA grave</desc>
         </entity>
         <operator-dictionary priority="880" form="postfix" accent="true" lspace="0" rspace="0"/>
         <description unicode="1.1">GRAVE ACCENT</description>
      </character>
      <character id="U00061" dec="97" mode="text" type="other">
         <unicodedata category="Ll" combclass="0" bidi="L" mirror="N" upper="0041" title="0041" mathclass="A"/>
         <latex>a</latex>
         <description unicode="1.1">LATIN SMALL LETTER A</description>
      </character>
      <character id="U00061-00062-00073" dec="97-98-115">
         <description>MULTIPLE CHARACTER OPERATOR: abs</description>
      </character>
      <character id="U00061-0006E-00064" dec="97-110-100">
         <description>MULTIPLE CHARACTER OPERATOR: and</description>
      </character>
      <character id="U00061-00072-00063-00063-0006F-00073" dec="97-114-99-99-111-115">
         <description>MULTIPLE CHARACTER OPERATOR: arccos</description>
      </character>
      <character id="U00061-00072-00063-00063-0006F-00073-00068" dec="97-114-99-99-111-115-104">
         <description>MULTIPLE CHARACTER OPERATOR: arccosh</description>
      </character>
      <character id="U00061-00072-00063-00063-0006F-00074" dec="97-114-99-99-111-116">
         <description>MULTIPLE CHARACTER OPERATOR: arccot</description>
      </character>
      <character id="U00061-00072-00063-00063-0006F-00074-00068" dec="97-114-99-99-111-116-104">
         <description>MULTIPLE CHARACTER OPERATOR: arccoth</description>
      </character>
      <character id="U00061-00072-00063-00063-00073-00063" dec="97-114-99-99-115-99">
         <description>MULTIPLE CHARACTER OPERATOR: arccsc</description>
      </character>
      <character id="U00061-00072-00063-00063-00073-00063-00068" dec="97-114-99-99-115-99-104">
         <description>MULTIPLE CHARACTER OPERATOR: arccsch</description>
      </character>
      <character id="U00061-00072-00063-00073-00065-00063" dec="97-114-99-115-101-99">
         <description>MULTIPLE CHARACTER OPERATOR: arcsec</description>
      </character>
      <character id="U00061-00072-00063-00073-00069-0006E" dec="97-114-99-115-105-110">
         <description>MULTIPLE CHARACTER OPERATOR: arcsin</description>
      </character>
      <character id="U00061-00072-00063-00073-00069-0006E-00068" dec="97-114-99-115-105-110-104">
         <description>MULTIPLE CHARACTER OPERATOR: arcsinh</description>
      </character>
      <character id="U00061-00072-00063-00074-00061-0006E" dec="97-114-99-116-97-110">
         <description>MULTIPLE CHARACTER OPERATOR: arctan</description>
      </character>
      <character id="U00061-00072-00063-00074-00061-0006E-00068" dec="97-114-99-116-97-110-104">
         <description>MULTIPLE CHARACTER OPERATOR: arctanh</description>
      </character>
      <character id="U00061-00072-00067" dec="97-114-103">
         <description>MULTIPLE CHARACTER OPERATOR: arg</description>
      </character>
      <character id="U00062" dec="98" mode="text" type="other">
         <unicodedata category="Ll" combclass="0" bidi="L" mirror="N" upper="0042" title="0042" mathclass="A"/>
         <latex>b</latex>
         <description unicode="1.1">LATIN SMALL LETTER B</description>
      </character>
      <character id="U00063" dec="99" mode="text" type="other">
         <unicodedata category="Ll" combclass="0" bidi="L" mirror="N" upper="0043" title="0043" mathclass="A"/>
         <latex>c</latex>
         <description unicode="1.1">LATIN SMALL LETTER C</description>
      </character>
      <character id="U00063-0006F-00073" dec="99-111-115">
         <description>MULTIPLE CHARACTER OPERATOR: cos</description>
      </character>
      <character id="U00063-0006F-00073-00068" dec="99-111-115-104">
         <description>MULTIPLE CHARACTER OPERATOR: cosh</description>
      </character>
      <character id="U00063-0006F-00074" dec="99-111-116">
         <description>MULTIPLE CHARACTER OPERATOR: cot</description>
      </character>
      <character id="U00063-0006F-00074-00068" dec="99-111-116-104">
         <description>MULTIPLE CHARACTER OPERATOR: coth</description>
      </character>
      <character id="U00063-00073-00063" dec="99-115-99">
         <description>MULTIPLE CHARACTER OPERATOR: csc</description>
      </character>
      <character id="U00063-00073-00063-00068" dec="99-115-99-104">
         <description>MULTIPLE CHARACTER OPERATOR: csch</description>
      </character>
      <character id="U00064" dec="100" mode="text" type="other">
         <unicodedata category="Ll" combclass="0" bidi="L" mirror="N" upper="0044" title="0044" mathclass="A"/>
         <latex>d</latex>
         <description unicode="1.1">LATIN SMALL LETTER D</description>
      </character>
      <character id="U00064-00065-00067" dec="100-101-103">
         <description>MULTIPLE CHARACTER OPERATOR: deg</description>
      </character>
      <character id="U00064-00065-00074" dec="100-101-116">
         <description>MULTIPLE CHARACTER OPERATOR: det</description>
      </character>
      <character id="U00064-00069-0006D" dec="100-105-109">
         <description>MULTIPLE CHARACTER OPERATOR: dim</description>
      </character>
      <character id="U00065" dec="101" mode="text" type="other">
         <unicodedata category="Ll" combclass="0" bidi="L" mirror="N" upper="0045" title="0045" mathclass="A"/>
         <latex>e</latex>
         <description unicode="1.1">LATIN SMALL LETTER E</description>
      </character>
      <character id="U00065-00078-00070" dec="101-120-112">
         <description>MULTIPLE CHARACTER OPERATOR: exp</description>
      </character>
      <character id="U00066" dec="102" mode="text" type="other">
         <unicodedata category="Ll" combclass="0" bidi="L" mirror="N" upper="0046" title="0046" mathclass="A"/>
         <latex>f</latex>
         <description unicode="1.1">LATIN SMALL LETTER F</description>
      </character>
      <character id="U00066-0006A" dec="102-106" mode="text" type="other">
         <latex>fj</latex>
         <entity id="fjlig" set="8879-isopub">
            <desc>small fj ligature</desc>
         </entity>
         <entity id="fjlig" set="9573-2003-isopub">
            <desc>small fj ligature</desc>
         </entity>
         <description unicode="1.1">fj ligature</description>
      </character>
      <character id="U00067" dec="103" mode="text" type="other">
         <unicodedata category="Ll" combclass="0" bidi="L" mirror="N" upper="0047" title="0047" mathclass="A"/>
         <latex>g</latex>
         <description unicode="1.1">LATIN SMALL LETTER G</description>
      </character>
      <character id="U00067-00063-00064" dec="103-99-100">
         <description>MULTIPLE CHARACTER OPERATOR: gcd</description>
      </character>
      <character id="U00068" dec="104" mode="text" type="other">
         <unicodedata category="Ll" combclass="0" bidi="L" mirror="N" upper="0048" title="0048" mathclass="A"/>
         <latex>h</latex>
         <description unicode="1.1">LATIN SMALL LETTER H</description>
      </character>
      <character id="U00068-0006F-0006D" dec="104-111-109">
         <description>MULTIPLE CHARACTER OPERATOR: hom</description>
      </character>
      <character id="U00069" dec="105" mode="text" type="other">
         <unicodedata category="Ll" combclass="0" bidi="L" mirror="N" upper="0049" title="0049" mathclass="A"/>
         <latex>i</latex>
         <description unicode="1.1">LATIN SMALL LETTER I</description>
      </character>
   </charlist>
</unicode>
