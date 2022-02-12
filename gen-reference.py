#!/usr/bin/python3

import os
import re
import glob
import json
import zlib
import math
import struct
import pathlib

import ttf_module
import pdf_module
import html_module
import common_json_help_module
import table_presentation_module

def emit_table_as_text(path,table_id,tp):
    #
    f = open(path,"w",encoding="UTF-8")
    f.write("\n")
    #
    f.write(tp.display.header+"\n")
    f.write(("="*len(tp.display.header))+"\n")
    f.write("\n")
    #
    if not tp.description == None:
        f.write(tp.description+"\n")
        f.write("\n")
    #
    if not tp.display.disptable == None:
        desci = 0
        for ci in range(len(tp.display.colsiz)):
            if not tp.display.colhdr[ci] == None and not tp.display.coldesc[ci] == None:
                x = tp.display.colhdr[ci] + ": " + tp.display.coldesc[ci]
                f.write(" - "+x+"\n")
                desci = desci + 1
        if desci > 0:
            f.write("\n")
        #
        for ci in range(len(tp.display.colsiz)):
            if ci > 0:
                f.write(" | ")
            x = ""
            if not tp.display.colhdr[ci] == None:
                x = tp.display.colhdr[ci]
            x = (x + (" "*tp.display.colsiz[ci]))[0:tp.display.colsiz[ci]]
            f.write(x)
        f.write("\n")
        #
        for ci in range(len(tp.display.colsiz)):
            if ci > 0:
                f.write("=|=")
            x = "="*tp.display.colsiz[ci]
            f.write(x)
        f.write("\n")
        #
        if len(tp.display.disptable) > 0:
            for row in tp.display.disptable:
                columns = row.get("columns")
                if not columns == None:
                    # NTS: array of arrays, because column values can have newlines
                    coltext = [ ]
                    collines = 1
                    # first pass: grab each column value, split by newline, stuff into coltext
                    for coli in range(len(columns)):
                        col = columns[coli]
                        val = col.get("value")
                        if val == None:
                            val = ""
                        #
                        vallines = val.split('\n')
                        coltext.append(vallines)
                        # how many vertical lines will this column need?
                        # to render correctly, all columns will be printed with this many vertical lines.
                        if collines < len(vallines):
                            collines = len(vallines)
                    # second pass: draw the columns, multiple lines if needed
                    for collc in range(collines):
                        show_sources = False
                        if collc == 0 and row.get("same key") == True:
                            show_sources = True
                        #
                        for coli in range(len(columns)):
                            if coli > 0:
                                f.write(" | ")
                            #
                            val = ""
                            cola = coltext[coli]
                            if collc < len(cola):
                                val = cola[collc]
                                if val == None:
                                    val = ""
                            #
                            x = (val + (" "*tp.display.colsiz[coli]))[0:tp.display.colsiz[coli]]
                            #
                            if not show_sources == True and coli == len(columns) - 1:
                                x = x.rstrip()
                            #
                            f.write(x)
                        #
                        if show_sources == True:
                            sia = row.get("source index")
                            if not sia == None:
                                for si in sia:
                                    f.write(" [*"+str(si)+"]")
                        #
                        f.write("\n")
                    # Problem: If any column has multiple lines, the per-line text format becomes confusing, and lines are needed to visually separate them
                    if tp.display.columns_have_newlines == True:
                        for ci in range(len(tp.display.colsiz)):
                            if ci > 0:
                                f.write("-+-")
                            x = "-"*tp.display.colsiz[ci]
                            f.write(x)
                        f.write("\n")
            #
            f.write("\n")
    #
    if not tp.sources == None:
        f.write("Sources\n")
        f.write("=======\n")
        for sii in range(len(tp.sources)):
            sobj = tp.sources[sii]
            if not int(sobj.get("source index")) == sii:
                raise Exception("source index is wrong")
            head = "  [*"+str(sii)+"] "
            f.write(head)
            if "book" in sobj:
                book = sobj["book"]
            elif "website" in sobj:
                book = sobj["website"]
            else:
                book = None

            if not book == None:
                where = sobj.get("where")
                citation = sobj.get("citation")
                if not citation == None:
                    x = ""
                    title = citation.get("title")
                    if not title == None:
                        if not x == "":
                            x = x + ", "
                        x = x + title
                    author = citation.get("author")
                    if not author == None:
                        if not x == "":
                            x = x + ", "
                        x = x + author
                    publisher = citation.get("publisher")
                    if not publisher == None:
                        if not x == "":
                            x = x + ", "
                        x = x + publisher
                    year = citation.get("year")
                    if not year == None:
                        if not x == "":
                            x = x + ", "
                        x = x + str(year)
                    if not x == "":
                        f.write(x+"\n")
                    #
                    url = citation.get("url")
                    if not url == None:
                        f.write(" "*len(head))
                        f.write("URL: "+url+"\n")
                if not where == None:
                    x = ""
                    for whi in where:
                        y = ""
                        if "path" in whi:
                            if not y == "":
                                y = y + ", "
                            y = y + whi["path"]
                        if "title" in whi:
                            if not y == "":
                                y = y + ", "
                            y = y + whi["title"]
                        if not y == "":
                            if not x == "":
                                x = x + " => "
                            x = x + y
                    if not x == "":
                        f.write(" "*len(head))
                        f.write(x+"\n")
            #
            f.write("\n")
    #
    if not tp.notes == None and len(tp.notes) > 0:
        f.write("Notes\n")
        f.write("-----\n")
        for note in tp.notes:
            f.write(" * "+note+"\n")
        f.write("\n")
    #
    f.close()

def emit_table_as_html(path,table_id,tp):
    #
    title = tp.display.header
    #
    f = open(path,"w",encoding="UTF-8")
    f.write("<!DOCTYPE HTML>\n")
    f.write("<html>")
    #
    f.write("<head>")
    f.write("<meta charset=\"utf-8\">")
    f.write("<title>"+html_module.html_escape(title)+"</title>")
    f.write("</head>")
    #
    f.write("<body>");
    f.write("<h2><span style=\"border-bottom: double;\">"+html_module.html_escape(title)+"</span></h2>")
    #
    if not tp.description == None:
        f.write("<p>"+html_module.html_escape(tp.description)+"</p>")
    #
    if not tp.display.disptable == None:
        desci = 0
        for ci in range(len(tp.display.colsiz)):
            if not tp.display.colhdr[ci] == None and not tp.display.coldesc[ci] == None:
                if desci == 0:
                    f.write("<table>")
                f.write("<tr style=\"font-size: 0.9em;\">")
                f.write("<td style=\"font-weight: 700; padding-right: 1em; white-space: pre; text-align: left;\">"+html_module.html_escape(tp.display.colhdr[ci])+":</td>")
                f.write("<td style=\"text-align: left;\">"+html_module.html_escape(tp.display.coldesc[ci])+"</td>")
                f.write("</tr>")
                desci = desci + 1
        if desci > 0:
            f.write("</table><br>")
        #
        f.write("<table style=\"border: 1px solid black; border-spacing: 0px;\">")
        #
        f.write("<tr style=\"background-color: rgb(224,224,224);\">")
        for ci in range(len(tp.display.colsiz)):
            x = ""
            if not tp.display.colhdr[ci] == None:
                x = tp.display.colhdr[ci]
            #
            if ci == len(tp.display.colsiz)-1:
                style = ""
            else:
                style = "border-right: 1px solid black;"
            #
            style = style + " padding: 0.2em; padding-right: 1em;"
            style = style + " border-bottom: 1px solid black; font-size: 0.9em; text-align: left;"
            #
            f.write("<th style=\""+style.strip()+"\">"+html_module.html_escape(x)+"</th>")
        f.write("</tr>")
        #
        if len(tp.display.disptable) > 0:
            for rowidx in range(len(tp.display.disptable)):
                row = tp.display.disptable[rowidx]
                columns = row.get("columns")
                if not columns == None:
                    f.write("<tr valign=\"top\">")
                    show_sources = False
                    # HTML can handle multi-line just fine for us
                    for coli in range(len(columns)):
                        #
                        col = columns[coli]
                        val = col.get("value")
                        if val == None:
                            val = ""
                        #
                        if row.get("same key") == True:
                            show_sources = True
                        #
                        f.write("<td style=\"")
                        f.write("white-space: pre; padding: 0.2em; padding-right: 1em; font-size: 0.9em; text-align: left;")
                        if not coli == len(columns)-1:
                            f.write(" border-right: 1px solid black;")
                        if not rowidx == len(tp.display.disptable)-1:
                            f.write(" border-bottom: 1px solid black;")
                        f.write("\">")
                        #
                        f.write(html_module.html_escape(val))
                        #
                        if coli == len(columns)-1 and show_sources == True:
                            sia = row.get("source index")
                            if not sia == None:
                                for si in sia:
                                    f.write(" <a style=\"text-decoration: none;\" href=\"#"+table_id+"_source_"+str(si)+"\"><sup style=\"color: rgb(0,0,192);\"><i>[*"+str(si)+"]</i></sup></a>")
                        #
                        f.write("</td>")
                    #
                    f.write("</tr>")
            #
            f.write("\n")
        #
        f.write("</table>")
    #
    if not tp.sources == None:
        f.write("<p><span style=\"border-bottom: solid; border-bottom-width: thin;\">Sources</span></p>\n")
        f.write("<table style=\"font-size: 0.8em;\">")
        for sii in range(len(tp.sources)):
            f.write("<tr valign=\"top\">")
            sobj = tp.sources[sii]
            if not int(sobj.get("source index")) == sii:
                raise Exception("source index is wrong")
            #
            f.write("<td style=\"padding-left: 2em; padding-bottom: 1em;\" id=\""+table_id+"_source_"+str(sii)+"\"><sup style=\"color: rgb(0,0,192);\"><i>[*"+str(sii)+"]</i></sup></td>")
            #
            if "book" in sobj:
                book = sobj["book"]
            elif "website" in sobj:
                book = sobj["website"]
            else:
                book = None

            f.write("<td style=\"padding-bottom: 1em;\">")
            if not book == None:
                where = sobj.get("where")
                citation = sobj.get("citation")
                if not citation == None:
                    x = ""
                    title = citation.get("title")
                    if not title == None:
                        if not x == "":
                            x = x + ", "
                        x = x + title
                    author = citation.get("author")
                    if not author == None:
                        if not x == "":
                            x = x + ", "
                        x = x + author
                    publisher = citation.get("publisher")
                    if not publisher == None:
                        if not x == "":
                            x = x + ", "
                        x = x + publisher
                    year = citation.get("year")
                    if not year == None:
                        if not x == "":
                            x = x + ", "
                        x = x + str(year)
                    if not x == "":
                        f.write(html_module.html_escape(x)+"<br>")
                    #
                    url = citation.get("url")
                    if not url == None:
                        f.write("URL: <a href=\""+url+"\" target=\"_blank\">"+html_module.html_escape(url)+"</a><br>")
                if not where == None:
                    x = ""
                    for whi in where:
                        y = ""
                        if "path" in whi:
                            if not y == "":
                                y = y + ", "
                            y = y + whi["path"]
                        if "title" in whi:
                            if not y == "":
                                y = y + ", "
                            y = y + whi["title"]
                        if not y == "":
                            if not x == "":
                                x = x + " => "
                            x = x + y
                    if not x == "":
                        f.write(html_module.html_escape(x)+"<br>")
            f.write("</td>")
            #
            f.write("</tr>")
        #
        f.write("</table>")
    #
    if not tp.notes == None and len(tp.notes) > 0:
        f.write("<p><span style=\"border-bottom: solid; border-bottom-width: thin;\">Notes</span></p>")
        f.write("<ul style=\"font-size: 0.8em;\">")
        for note in tp.notes:
            f.write("<li>"+html_module.html_escape(note)+"</li>")
        f.write("</ul>")
    #
    f.write("</body>");
    #
    f.write("</html>")
    f.close()

class XY:
    x = None
    y = None
    def __init__(self,x=0,y=0):
        self.x = x
        self.y = y
    def __str__(self):
        return "["+str(self.x)+","+str(self.y)+"]"
    def __sub__(self,other):
        return XY(self.x-other.x,self.y-other.y)
    def __add__(self,other):
        return XY(self.x+other.x,self.y+other.y)
class WH:
    w = None
    h = None
    def __init__(self,w=0,h=0):
        self.w = w
        self.h = h
    def __str__(self):
        return "["+str(self.w)+"x"+str(self.h)+"]"
    def __sub__(self,other):
        return XY(self.w-other.w,self.h-other.h)
    def __add__(self,other):
        return XY(self.w+other.w,self.h+other.h)
class RectRegion:
    xy = None
    wh = None
    def __init__(self,xy=XY(),wh=WH()):
        self.xy = xy
        if type(wh) == WH:
            self.wh = wh
        elif type(wh) == XY:
            self.wh = WH(wh.x,wh.y)
        else:
            raise Exception("RectRegion wh param invalid")
    def __str__(self):
        return "[xy="+str(self.xy)+",wh="+str(self.wh)+"]"

class EmitPDF:
    class Font:
        reg = None
        bold = None
        italic = None
    #
    font1 = None
    contentRegion = None
    pageTitleRegion = None
    pageNumberRegion = None
    #
    currentTitle = None
    currentPage = None
    pagestream = None
    pageHeight = None
    currentPos = None
    currentDPI = None
    pdfhl = None
    #
    def __init__(self):
        self.font1 = EmitPDF.Font()
        #
        ll = XY(0.25,0.5)
        ur = XY(8 - 0.25,11 - 0.25)
        self.contentRegion = RectRegion(ll,ur-ll)
        #
        ll = XY(0.25,0.25)
        ur = XY(8 - 0.25,0.45)
        self.pageTitleRegion = RectRegion(ll,ur-ll)
        # y coord is ignored
        ll = XY(0.25,0)
        ur = XY(8 - 0.25,0)
        self.pageTitleLine = RectRegion(ll,ur-ll)
        #
        ll = XY(8 - 0.5,11 - (10/72) - 0.10)
        ur = XY(8 - 0.10,11 - 0.05)
        self.pageNumberRegion = RectRegion(ll,ur-ll)
        #
        self.currentPage = None
        self.pagestream = None
        #
        self.pdfhl = None
    def setpdfhl(self,pdfhl):
        self.pdfhl = pdfhl
    def end_page(self):
        if not self.pagestream == None and not self.currentPage == None:
            self.pdfhl.make_page_content_stream(self.currentPage,data=self.pagestream.data())
        #
        if not self.pagestream == None:
            del self.pagestream
        self.pagestream = None
        #
        if not self.currentPage == None:
            del self.currentPage
        self.currentPage = None
    def new_page(self):
        self.end_page()
        #
        self.currentPage = page = self.pdfhl.new_page()
        #
        self.pdfhl.add_page_font_ref(page,self.font1.reg)
        self.pdfhl.add_page_font_ref(page,self.font1.bold)
        self.pdfhl.add_page_font_ref(page,self.font1.italic)
        #
        ps = self.pagestream = pdf_module.PDFPageContentWriter(self.pdfhl)
        #
        self.currentDPI = self.pdfhl.page_dpi
        self.pageHeight = self.pdfhl.page_size[1]
        # DEBUG: Draw a dark red box around the content region-----------------------------
        if False:
            ps.stroke_color(0.5,0,0)
            p = self.coordxlate(XY(self.contentRegion.xy.x,self.contentRegion.xy.y))
            ps.moveto(p.x,p.y)
            p = self.coordxlate(XY(self.contentRegion.xy.x+self.contentRegion.wh.w,self.contentRegion.xy.y))
            ps.lineto(p.x,p.y)
            p = self.coordxlate(XY(self.contentRegion.xy.x+self.contentRegion.wh.w,self.contentRegion.xy.y+self.contentRegion.wh.h))
            ps.lineto(p.x,p.y)
            p = self.coordxlate(XY(self.contentRegion.xy.x,self.contentRegion.xy.y+self.contentRegion.wh.h))
            ps.lineto(p.x,p.y)
            ps.close_subpath()
            ps.stroke()
        # END DEBUG------------------------------------------------------------------------
        # title
        self.move_to(self.pageTitleRegion.xy)
        self.layout_text_begin()
        ps.set_text_font(self.font1.italic,10)
        ps.fill_color(0,0,0)
        self.layout_text(self.currentTitle,overflow="stop")
        self.newline(y=(self.layoutVadj.y*5)/4) # from baseline to below text
        self.layout_text_end()
        vadj = XY(0,self.currentPos.y)
        #
        p = self.coordxlate(self.pageTitleLine.xy + vadj)
        p2 = self.coordxlate(self.pageTitleLine.xy + vadj + XY(self.pageTitleLine.wh.w,0))
        ps.stroke_color(0,0,0)
        ps.linewidth(0.5)
        ps.moveto(p.x,p.y)
        ps.lineto(p2.x,p2.y)
        ps.stroke()
        # page number (top)
        vadj = XY(0,10/self.currentDPI) # remember that text is rendered from a baseline, not from the top
        ps.begin_text()
        ps.set_text_font(self.font1.italic,10)
        ptxt = str(self.currentPage.index)
        pw = ps.text_width(ptxt) # get text width to right-justify
        ps.fill_color(0,0,0)
        p = self.coordxlate(XY(self.pageTitleRegion.xy.x+self.pageTitleRegion.wh.w-pw,self.pageTitleRegion.xy.y)+vadj)
        ps.text_move_to(p.x,p.y) # right justify
        ps.text(ptxt)
        ps.end_text()
        # page number (bottom)
        vadj = XY(0,10/self.currentDPI) # remember that text is rendered from a baseline, not from the top
        ps.begin_text()
        ps.set_text_font(self.font1.italic,10)
        ptxt = str(self.currentPage.index)
        pw = ps.text_width(ptxt) # get text width to right-justify
        ps.fill_color(0,0,0)
        p = self.coordxlate(XY(self.pageNumberRegion.xy.x+self.pageNumberRegion.wh.w-pw,self.pageNumberRegion.xy.y)+vadj)
        ps.text_move_to(p.x,p.y) # right justify
        ps.text(ptxt)
        ps.end_text()
        #
        self.move_to(self.contentRegion.xy)
        #
        return page
    def coordxlateunscaled(self,xy):
        # PDF coordinate system is bottom-up, we think top down
        return XY(xy.x,self.pageHeight-xy.y)
    def coordxlate(self,xy):
        tx = self.coordxlateunscaled(xy)
        return XY(tx.x*self.currentDPI,tx.y*self.currentDPI)
    def ps(self):
        return self.pagestream
    def dpi(self):
        return self.currentDPI
    def set_title(self,title):
        self.currentTitle = title
    def content_end(self):
        return XY(self.contentRegion.xy.x + self.contentRegion.wh.w,self.contentRegion.xy.y + self.contentRegion.wh.h)
    def newline(self,*,x=0,y=0):
        self.currentPos.x = self.contentRegion.xy.x + x
        self.currentPos.y = self.currentPos.y + y
    def tchr_classify(self,c):
        if c == '\n' or c == '\t' or c == ' ':
            return "w"
        return "c"
    def split_text(self,text):
        e = [ ]
        w = ""
        cls = None
        for c in text:
            ncls = self.tchr_classify(c)
            if not cls == ncls or c == '\n':
                cls = ncls
                if not w == "":
                    e.append(w)
                    w = ""
            #
            w = w + c
        if not w == "":
            e.append(w)
        return e
    def layout_text_begin(self):
        if not self.pagestream.intxt:
            self.pagestream.begin_text()
        self.layoutStarted = True
        self.layoutWritten = 0
        self.layoutLineTextBuf = ""
        self.layoutStartedAt = XY(self.currentPos.x,self.currentPos.y)
        self.layoutMaxEnd = XY(self.currentPos.x,self.currentPos.y)
        self.layoutVadj = XY(0,0)
    def layout_text_end(self):
        if len(self.layoutLineTextBuf) > 0:
            self.pagestream.text(self.layoutLineTextBuf)
            self.layoutLineTextBuf = ""
        self.pagestream.end_text()
        self.layoutStarted = False
    def move_to(self,xy=None,*,x=None,y=None):
        if not xy == None:
            if not type(xy) == XY:
                raise Exception("move_to() without XY object");
            self.currentPos = XY(xy.x,xy.y)
        if not x == None:
            self.currentPos.x = x
        if not y == None:
            self.currentPos.y = y
    def layout_span_page(self):
        savedFont = self.pagestream.currentFont
        savedFontSize = self.pagestream.currentFontSize
        self.end_page()
        self.new_page()
        if not savedFont == None and not savedFontSize == None:
            self.layout_text_begin()
            self.pagestream.set_text_font(savedFont,savedFontSize)
            self.pagestream.text_leading(self.pagestream.currentFontSize)
            self.pagestream.fill_color(0,0,0)
            self.layoutVadj = XY(0,self.pagestream.currentFontSize/self.currentDPI)
            #
            tp = self.coordxlate(self.currentPos+self.layoutVadj)
            self.pagestream.text_move_to(tp.x,tp.y)
    def layout_text_flush(self):
        if len(self.layoutLineTextBuf) > 0:
            self.pagestream.text(self.layoutLineTextBuf)
            self.layoutLineTextBuf = ""
    def layout_text(self,text,*,overflow="wrap",pagespan=False):
        stop_xy = self.content_end()
        elements = self.split_text(text)
        #
        if self.layoutWritten == 0:
            self.pagestream.text_leading(self.pagestream.currentFontSize)
            self.layoutVadj = XY(0,self.pagestream.currentFontSize/self.currentDPI)
            self.layoutWritten = 1
            #
            tp = self.coordxlate(self.currentPos+self.layoutVadj)
            self.pagestream.text_move_to(tp.x,tp.y)
            #
            if pagespan == True:
                if (self.currentPos+self.layoutVadj).y > (self.contentRegion.xy.y+self.contentRegion.wh.h):
                    self.layout_span_page()
        #
        for elem in elements:
            ew = self.pagestream.text_width(elem)
            fx = self.currentPos.x + ew
            if fx > stop_xy.x or elem == "\n":
                if overflow == "stop" and not elem == "\n":
                    break
                #
                if len(self.layoutLineTextBuf) > 0:
                    self.pagestream.text(self.layoutLineTextBuf)
                    self.layoutLineTextBuf = ""
                #
                if self.layoutMaxEnd.x < self.currentPos.x:
                    self.layoutMaxEnd.x = self.currentPos.x
                #
                self.pagestream.text_next_line()
                self.newline(y=(self.pagestream.currentFontSize/self.currentDPI))
                #
                if self.layoutMaxEnd.y < self.currentPos.y:
                    self.layoutMaxEnd.y = self.currentPos.y
            #
            if not elem == "\n":
                if pagespan == True:
                    if (self.currentPos+self.layoutVadj).y > (self.contentRegion.xy.y+self.contentRegion.wh.h):
                        self.layout_span_page()
                #
                self.layoutLineTextBuf = self.layoutLineTextBuf + elem
                self.currentPos.x = self.currentPos.x + ew
                #
                if self.layoutMaxEnd.x < self.currentPos.x:
                    self.layoutMaxEnd.x = self.currentPos.x

def emit_table_as_pdf(path,table_id,tp):
    emitpdf = EmitPDF()
    #
    pdf = pdf_module.PDFGen()
    pdfhl = pdf_module.PDFGenHL(pdf)
    emitpdf.setpdfhl(pdfhl)
    # -- font 1: regular
    emitpdf.font1.reg = pdfhl.add_font({
        pdf_module.PDFName("Subtype"): pdf_module.PDFName("TrueType"),
        pdf_module.PDFName("Name"): pdf_module.PDFName("F1"),
        pdf_module.PDFName("Encoding"): pdf_module.PDFName("WinAnsiEncoding"),
        pdf_module.PDFName("BaseFont"): pdf_module.PDFName("ABCDEE+Ubuntu")
    },
    desc={
    },
    ttffile="ttf/Ubuntu-R.ttf")
    # -- font 1: bold
    emitpdf.font1.bold = pdfhl.add_font({
        pdf_module.PDFName("Subtype"): pdf_module.PDFName("TrueType"),
        pdf_module.PDFName("Name"): pdf_module.PDFName("F2"),
        pdf_module.PDFName("Encoding"): pdf_module.PDFName("WinAnsiEncoding"),
        pdf_module.PDFName("BaseFont"): pdf_module.PDFName("ABCDEE+Ubuntu")
    },
    desc={
    },
    ttffile="ttf/Ubuntu-B.ttf")
    # -- font 1: italic
    emitpdf.font1.italic = pdfhl.add_font({
        pdf_module.PDFName("Subtype"): pdf_module.PDFName("TrueType"),
        pdf_module.PDFName("Name"): pdf_module.PDFName("F3"),
        pdf_module.PDFName("Encoding"): pdf_module.PDFName("WinAnsiEncoding"),
        pdf_module.PDFName("BaseFont"): pdf_module.PDFName("ABCDEE+Ubuntu")
    },
    desc={
    },
    ttffile="ttf/Ubuntu-RI.ttf")
    # -------------- END FONTS
    emitpdf.set_title(tp.display.header)
    page1 = emitpdf.new_page()
    ps = emitpdf.ps()
    # header
    emitpdf.newline(y=16/emitpdf.currentDPI)
    #
    vadj = XY(0,16/emitpdf.currentDPI) # remember that text is rendered from a baseline, not from the top
    emitpdf.layout_text_begin()
    ps.set_text_font(emitpdf.font1.bold,16)
    ps.fill_color(0,0,0)
    emitpdf.layout_text(tp.display.header,overflow="stop")
    emitpdf.layout_text_end()
    emitpdf.newline(y=emitpdf.layoutVadj.y)
    emitpdf.newline(y=16/emitpdf.currentDPI/5) # 1/5th the font size
    hdrlinew = emitpdf.layoutMaxEnd.x - emitpdf.layoutStartedAt.x
    #
    p = emitpdf.coordxlate(emitpdf.currentPos)
    ps.stroke_color(0,0,0)
    ps.linewidth(0.5)
    ps.moveto(p.x,p.y)
    lt = emitpdf.contentRegion.wh.w
    l = hdrlinew
    if l > lt:
        l = lt
    p2 = emitpdf.coordxlate(emitpdf.currentPos+XY(l,0))
    ps.lineto(p2.x,p2.y)
    ps.stroke()
    #
    emitpdf.newline(y=10/emitpdf.currentDPI)
    #
    if not tp.description == None:
        emitpdf.layout_text_begin()
        ps.set_text_font(emitpdf.font1.reg,10)
        emitpdf.layout_text(tp.description,pagespan=True)
        emitpdf.layout_text("\n\n")
        emitpdf.layout_text_end()
    #
    if not tp.display.disptable == None:
        desci = 0
        for ci in range(len(tp.display.colsiz)):
            if not tp.display.colhdr[ci] == None and not tp.display.coldesc[ci] == None:
                emitpdf.layout_text_begin()
                #
                ps.set_text_font(emitpdf.font1.bold,8)
                emitpdf.layout_text(tp.display.colhdr[ci],pagespan=True)
                emitpdf.layout_text_flush()
                #
                ps.set_text_font(emitpdf.font1.reg,8)
                emitpdf.layout_text(": "+tp.display.coldesc[ci],pagespan=True)
                emitpdf.layout_text("\n",pagespan=True)
                #
                emitpdf.layout_text_end()
                emitpdf.newline(y=2/emitpdf.currentDPI)
                #
                desci = desci + 1
        if desci > 0:
            emitpdf.newline(y=10/emitpdf.currentDPI)
        #
        fontSize = 10
        while True:
            dpiwidths = [ ]
            dpiposx = [ ]
            dpitexx = [ ]
            dpiposw = [ ]
            dpitexw = [ ]
            for ci in range(len(tp.display.colsiz)):
                x = ""
                if not tp.display.colhdr[ci] == None:
                    x = tp.display.colhdr[ci]
                lines = x.split('\n')
                mw = 0
                for line in lines:
                    lw = pdfhl.fontwidth(emitpdf.font1.reg,fontSize,line)
                    if mw < lw:
                        mw = lw
                dpiwidths.append(mw)
                dpiposx.append(None)
                dpitexx.append(None)
                dpiposw.append(None)
                dpitexw.append(None)
            #
            for rowidx in range(len(tp.display.disptable)):
                row = tp.display.disptable[rowidx]
                columns = row.get("columns")
                if not columns == None:
                    for coli in range(len(columns)):
                        col = columns[coli]
                        val = col.get("value")
                        if val == None:
                            val = ""
                        lines = val.split('\n')
                        for line in lines:
                            lw = pdfhl.fontwidth(emitpdf.font1.reg,fontSize,line)
                            if dpiwidths[coli] < lw:
                                dpiwidths[coli] = lw
            # decide where to layout the tables
            hcols = 1
            hcolw = 0
            hxpad = 0.05
            hipad = 0.4
            hx = 0
            for ci in range(len(tp.display.colsiz)):
                dpiposx[ci] = hx
                dpitexx[ci] = hxpad + hx
                dpiposw[ci] = hxpad + dpiwidths[ci] + hxpad
                dpitexw[ci] = dpiwidths[ci]
                hx = dpiposx[ci] + dpiposw[ci]
            #
            maxw = emitpdf.contentRegion.wh.w
            if hx > maxw:
                fontSize = fontSize - 1
                if fontSize <= 4:
                    raise Exception("Cannot fit tables")
                continue
            else:
                hcols = math.floor(maxw / (hx + hipad))
                if hcols < 1:
                    hcols = 1
                hcolw = hx + hipad
                hcoltw = (hx + hipad) * hcols
                break
        # determine table pos, make new page to ensure enough room
        tablepos = XY(emitpdf.contentRegion.xy.x,emitpdf.currentPos.y)
        if (tablepos.y+((fontSize*6)/emitpdf.currentDPI)) > (emitpdf.contentRegion.xy.y+emitpdf.contentRegion.wh.h):
            page1 = emitpdf.new_page()
            ps = emitpdf.ps()
            tablepos = XY(emitpdf.contentRegion.xy.x,emitpdf.currentPos.y)
        # draw table row by row
        drawcol = 0
        drawrowtop = 0
        drawrowcount = 0
        rowh = ((5.0/4.0)*fontSize)/emitpdf.currentDPI
        rowidx = 0
        while rowidx < len(tp.display.disptable):
            row = tp.display.disptable[rowidx]
            columns = row.get("columns")
            #
            if drawrowcount == 0:
                emitpdf.move_to(XY(tablepos.x+(hcolw*drawcol),tablepos.y))
                drawrowtop = emitpdf.currentPos.y
                ps.fill_color(0.8,0.8,0.8)
                p = emitpdf.coordxlate(emitpdf.currentPos)
                ps.moveto(p.x,p.y)
                p = emitpdf.coordxlate(XY(emitpdf.currentPos.x+hx,emitpdf.currentPos.y))
                ps.lineto(p.x,p.y)
                p = emitpdf.coordxlate(XY(emitpdf.currentPos.x+hx,emitpdf.currentPos.y+rowh))
                ps.lineto(p.x,p.y)
                p = emitpdf.coordxlate(XY(emitpdf.currentPos.x,emitpdf.currentPos.y+rowh))
                ps.lineto(p.x,p.y)
                ps.close_subpath()
                ps.fill()
                #
                ps.stroke_color(0,0,0)
                ps.linewidth(0.5)
                p = emitpdf.coordxlate(emitpdf.currentPos)
                ps.moveto(p.x,p.y)
                p = emitpdf.coordxlate(XY(emitpdf.currentPos.x+hx,emitpdf.currentPos.y))
                ps.lineto(p.x,p.y)
                ps.stroke()
                p = emitpdf.coordxlate(emitpdf.currentPos+XY(0,rowh))
                ps.moveto(p.x,p.y)
                p = emitpdf.coordxlate(XY(emitpdf.currentPos.x+hx,emitpdf.currentPos.y+rowh))
                ps.lineto(p.x,p.y)
                ps.stroke()
                #
                for coli in range(len(columns)):
                    val = tp.display.colhdr[coli]
                    if val == None:
                        val = ""
                    # 
                    ps.fill_color(0,0,0)
                    emitpdf.currentPos.x = tablepos.x+(hcolw*drawcol) + dpiposx[coli] + hxpad
                    emitpdf.layout_text_begin()
                    ps.set_text_font(emitpdf.font1.reg,fontSize)
                    emitpdf.layout_text(val)
                    emitpdf.layout_text_end()
                #
                emitpdf.newline(y=rowh)
            #
            maxlines = 1
            colvals = [ ]
            for coli in range(len(columns)):
                col = columns[coli]
                val = col.get("value")
                if val == None:
                    val = ""
                #
                vallines = val.split('\n')
                if maxlines < len(vallines):
                    maxlines = len(vallines)
                #
                colvals.append(vallines)
            #
            if (emitpdf.currentPos.y+((rowh*maxlines)/emitpdf.currentDPI)) > (emitpdf.contentRegion.xy.y+emitpdf.contentRegion.wh.h):
                if drawrowcount > 0:
                    for coli in range(len(columns)):
                        x = tablepos.x+(hcolw*drawcol) + dpiposx[coli]
                        ps.stroke_color(0,0,0)
                        ps.linewidth(0.5)
                        p = emitpdf.coordxlate(XY(x,drawrowtop))
                        ps.moveto(p.x,p.y)
                        p = emitpdf.coordxlate(XY(x,emitpdf.currentPos.y))
                        ps.lineto(p.x,p.y)
                        ps.stroke()
                    #
                    x = tablepos.x+(hcolw*drawcol)+hx
                    ps.stroke_color(0,0,0)
                    ps.linewidth(0.5)
                    p = emitpdf.coordxlate(XY(x,drawrowtop))
                    ps.moveto(p.x,p.y)
                    p = emitpdf.coordxlate(XY(x,emitpdf.currentPos.y))
                    ps.lineto(p.x,p.y)
                    ps.stroke()
                #
                drawrowcount = 0
                drawcol = drawcol + 1
                if drawcol >= hcols:
                    drawcol = 0
                    page1 = emitpdf.new_page()
                    ps = emitpdf.ps()
                    tablepos = XY(emitpdf.contentRegion.xy.x,emitpdf.currentPos.y)
                #
                pdf.currentPos = XY(tablepos.x,tablepos.y)
                continue
            #
            show_sources = False
            if row.get("same key") == True:
                show_sources = True
            #
            coltop = XY(emitpdf.currentPos.x,emitpdf.currentPos.y)
            for coli in range(len(columns)):
                colv = colvals[coli]
                #
                ps.fill_color(0,0,0)
                tx = emitpdf.currentPos.x = tablepos.x+(hcolw*drawcol) + dpiposx[coli] + hxpad
                emitpdf.currentPos.y = coltop.y
                emitpdf.layout_text_begin()
                ps.set_text_font(emitpdf.font1.reg,fontSize)
                for line in colv:
                    emitpdf.currentPos.x = tx
                    emitpdf.layout_text(line)
                    emitpdf.layout_text_flush()
                    ps.text_next_line()
                emitpdf.layout_text_end()
                #
                if show_sources == True and coli == len(columns)-1:
                    sia = row.get("source index")
                    if not sia == None and len(sia) > 0:
                        ps.fill_color(0,0,0.75)
                        emitpdf.currentPos.x = coltop.x + dpiposx[coli] + hxpad + pdfhl.fontwidth(emitpdf.font1.reg,fontSize,colvals[coli][0])
                        emitpdf.currentPos.y = coltop.y
                        emitpdf.layout_text_begin()
                        ps.set_text_font(emitpdf.font1.italic,5)
                        for si in sia:
                            refmark = " [*"+str(si)+"]"
                            emitpdf.layout_text(refmark)
                        emitpdf.layout_text_end()
                        ps.fill_color(0,0,0)
            #
            emitpdf.currentPos.x = coltop.x
            emitpdf.currentPos.y = coltop.y + rowh
            if maxlines > 1:
                emitpdf.currentPos.y = emitpdf.currentPos.y + ((maxlines - 1) * (fontSize/emitpdf.currentDPI))
            #
            ps.stroke_color(0,0,0)
            ps.linewidth(0.5)
            p = emitpdf.coordxlate(emitpdf.currentPos+XY(hcolw*drawcol,0))
            ps.moveto(p.x,p.y)
            p = emitpdf.coordxlate(XY(emitpdf.currentPos.x+(hcolw*drawcol)+hx,emitpdf.currentPos.y))
            ps.lineto(p.x,p.y)
            ps.stroke()
            #
            drawrowcount = drawrowcount + 1
            rowidx = rowidx + 1
        #
        if drawrowcount > 0:
            for coli in range(len(columns)):
                x = tablepos.x+(hcolw*drawcol) + dpiposx[coli]
                ps.stroke_color(0,0,0)
                ps.linewidth(0.5)
                p = emitpdf.coordxlate(XY(x,drawrowtop))
                ps.moveto(p.x,p.y)
                p = emitpdf.coordxlate(XY(x,emitpdf.currentPos.y))
                ps.lineto(p.x,p.y)
                ps.stroke()
            #
            x = tablepos.x+(hcolw*drawcol)+hx
            ps.stroke_color(0,0,0)
            ps.linewidth(0.5)
            p = emitpdf.coordxlate(XY(x,drawrowtop))
            ps.moveto(p.x,p.y)
            p = emitpdf.coordxlate(XY(x,emitpdf.currentPos.y))
            ps.lineto(p.x,p.y)
            ps.stroke()
        #
        emitpdf.newline(y=(8+2)/emitpdf.currentDPI)
    #
    if not tp.sources == None:
        ps.fill_color(0,0,0)
        emitpdf.layout_text_begin()
        ps.set_text_font(emitpdf.font1.reg,10)
        emitpdf.layout_text("Sources\n",pagespan=True)
        emitpdf.layout_text_end()
        emitpdf.newline(y=10/emitpdf.currentDPI/5) # 1/5th the font size
        hdrlinew = emitpdf.layoutMaxEnd.x - emitpdf.layoutStartedAt.x
        #
        p = emitpdf.coordxlate(emitpdf.currentPos)
        ps.stroke_color(0,0,0)
        ps.linewidth(0.5)
        ps.moveto(p.x,p.y)
        lt = emitpdf.contentRegion.wh.w
        l = hdrlinew
        if l > lt:
            l = lt
        p2 = emitpdf.coordxlate(emitpdf.currentPos+XY(l,0))
        ps.lineto(p2.x,p2.y)
        ps.stroke()
        #
        emitpdf.newline(y=5/emitpdf.currentDPI)
        #
        for sii in range(len(tp.sources)):
            sobj = tp.sources[sii]
            if not int(sobj.get("source index")) == sii:
                raise Exception("source index is wrong")
            #
            emitpdf.currentPos.x = emitpdf.currentPos.x + 0.1
            nPos = emitpdf.currentPos.x + 0.3
            emitpdf.layout_text_begin()
            #
            refmark = "[*"+str(sii)+"]"
            ps.set_text_font(emitpdf.font1.italic,8)
            ps.fill_color(0,0,0.75)
            emitpdf.layout_text(refmark,pagespan=True)
            emitpdf.layout_text_end()
            ps.fill_color(0,0,0)
            #
            if "book" in sobj:
                book = sobj["book"]
            elif "website" in sobj:
                book = sobj["website"]
            else:
                book = None

            emit = False
            if not book == None:
                where = sobj.get("where")
                citation = sobj.get("citation")
                if not citation == None:
                    x = ""
                    title = citation.get("title")
                    if not title == None:
                        if not x == "":
                            x = x + ", "
                        x = x + title
                    author = citation.get("author")
                    if not author == None:
                        if not x == "":
                            x = x + ", "
                        x = x + author
                    publisher = citation.get("publisher")
                    if not publisher == None:
                        if not x == "":
                            x = x + ", "
                        x = x + publisher
                    year = citation.get("year")
                    if not year == None:
                        if not x == "":
                            x = x + ", "
                        x = x + str(year)
                    if not x == "":
                        #
                        if emit == False:
                            emit = True
                        else:
                            emitpdf.newline(y=4/emitpdf.currentDPI)
                        #
                        emitpdf.currentPos.x = nPos
                        emitpdf.layout_text_begin()
                        ps.set_text_font(emitpdf.font1.reg,8)
                        ps.fill_color(0,0,0)
                        emitpdf.layout_text(x+"\n",pagespan=True)
                        emitpdf.layout_text_end()
                        emit = True
                    #
                    url = citation.get("url")
                    if not url == None: # TODO: I know PDF allows this... how do you make it clickable so that it loads the web address?
                        #
                        if emit == False:
                            emit = True
                        else:
                            emitpdf.newline(y=4/emitpdf.currentDPI)
                        #
                        emitpdf.currentPos.x = nPos
                        emitpdf.layout_text_begin()
                        ps.set_text_font(emitpdf.font1.reg,8)
                        ps.fill_color(0,0,0)
                        emitpdf.layout_text("URL: ",pagespan=True)
                        emitpdf.layout_text(url+"\n",pagespan=True)
                        emitpdf.layout_text_end()
                if not where == None:
                    x = ""
                    for whi in where:
                        y = ""
                        if "path" in whi:
                            if not y == "":
                                y = y + ", "
                            y = y + whi["path"]
                        if "title" in whi:
                            if not y == "":
                                y = y + ", "
                            y = y + whi["title"]
                        if not y == "":
                            if not x == "":
                                x = x + " => "
                            x = x + y
                    if not x == "":
                        #
                        if emit == False:
                            emit = True
                        else:
                            emitpdf.newline(y=4/emitpdf.currentDPI)
                        #
                        emitpdf.currentPos.x = nPos
                        emitpdf.layout_text_begin()
                        ps.set_text_font(emitpdf.font1.italic,8)
                        ps.fill_color(0,0,0)
                        emitpdf.layout_text(x+"\n",pagespan=True)
                        emitpdf.layout_text_end()
            #
            emitpdf.newline(y=(8+2)/emitpdf.currentDPI)
        #
        emitpdf.newline(y=2/emitpdf.currentDPI)
    #
    if not tp.notes == None and len(tp.notes) > 0:
        emitpdf.layout_text_begin()
        ps.set_text_font(emitpdf.font1.reg,10)
        emitpdf.layout_text("Notes\n",pagespan=True)
        emitpdf.layout_text_end()
        emitpdf.newline(y=10/emitpdf.currentDPI/5) # 1/5th the font size
        hdrlinew = emitpdf.layoutMaxEnd.x - emitpdf.layoutStartedAt.x
        #
        p = emitpdf.coordxlate(emitpdf.currentPos)
        ps.stroke_color(0,0,0)
        ps.linewidth(0.5)
        ps.moveto(p.x,p.y)
        lt = emitpdf.contentRegion.wh.w
        l = hdrlinew
        if l > lt:
            l = lt
        p2 = emitpdf.coordxlate(emitpdf.currentPos+XY(l,0))
        ps.lineto(p2.x,p2.y)
        ps.stroke()
        #
        emitpdf.newline(y=5/emitpdf.currentDPI)
        for note in tp.notes:
            emitpdf.currentPos.x = emitpdf.currentPos.x + 0.1
            ps.fill_color(0.25,0.25,0.25)
            cx = 0.0
            cy = (8/emitpdf.currentDPI)*0.5*(5.0/4.0)
            cw = (8/emitpdf.currentDPI)*0.4
            ch = (8/emitpdf.currentDPI)*0.4
            #
            p = emitpdf.coordxlate(XY(emitpdf.currentPos.x+cx-(cw/2.0),emitpdf.currentPos.y+cy-(cw/2.0)))
            ps.moveto(p.x,p.y)
            p = emitpdf.coordxlate(XY(emitpdf.currentPos.x+cx+(cw/2.0),emitpdf.currentPos.y+cy-(cw/2.0)))
            ps.lineto(p.x,p.y)
            p = emitpdf.coordxlate(XY(emitpdf.currentPos.x+cx+(cw/2.0),emitpdf.currentPos.y+cy+(cw/2.0)))
            ps.lineto(p.x,p.y)
            p = emitpdf.coordxlate(XY(emitpdf.currentPos.x+cx-(cw/2.0),emitpdf.currentPos.y+cy+(cw/2.0)))
            ps.lineto(p.x,p.y)
            #
            ps.close_subpath()
            ps.fill()
            #
            emitpdf.currentPos.x = emitpdf.currentPos.x + 0.1
            emitpdf.layout_text_begin()
            ps.set_text_font(emitpdf.font1.reg,8)
            emitpdf.layout_text(note+"\n",pagespan=True)
            emitpdf.layout_text_end()
        #
        emitpdf.newline(y=5/emitpdf.currentDPI)
    #
    emitpdf.end_page()
    pdfhl.finish()
    f = open(path,"wb")
    pdf.write_file(f)
    f.close()

os.system("rm -Rf reference/text/tables; mkdir -p reference/text/tables")
os.system("rm -Rf reference/html/tables; mkdir -p reference/html/tables")
os.system("rm -Rf reference/pdf/tables; mkdir -p reference/pdf/tables")

tables_json = common_json_help_module.load_json("compiled/tables.json")

tables = tables_json.get("tables")
if not tables == None:
    for table_id in tables:
        tp = table_presentation_module.TablePresentation(tables[table_id])
        emit_table_as_text("reference/text/tables/"+table_id+".txt",table_id,tp)
        emit_table_as_html("reference/html/tables/"+table_id+".htm",table_id,tp)
        emit_table_as_pdf("reference/pdf/tables/"+table_id+".pdf",table_id,tp)

