#!/usr/bin/python3

import os
import glob
import json
import zlib
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
        self.wh = wh
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
    pageTitleLine = None
    pageTitleRegion = None
    pageNumberRegion = None
    #
    currentPage = None
    pagestream = None
    pageHeight = None
    currentPos = None
    #
    def __init__(self):
        self.font1 = EmitPDF.Font()
        #
        ll = XY(0.25,0.5)
        ur = XY(8 - 0.25,11 - 0.5)
        self.contentRegion = RectRegion(ll,ur-ll)
        #
        ll = XY(0.25,0.25)
        ur = XY(8 - 0.25,0.45)
        self.pageTitleRegion = RectRegion(ll,ur-ll)
        #
        ll = XY(0.25,0.475)
        ur = XY(8 - 0.25,0.475)
        self.pageTitleLine = RectRegion(ll,ur-ll)
        #
        ll = XY(8 - 0.5,11 - 0.25)
        ur = XY(8 - 0.25,11 - 0.05)
        self.pageNumberRegion = RectRegion(ll,ur-ll)
        #
        self.currentPage = None
        self.pagestream = None
    def end_page(self,pdfhl):
        if not self.pagestream == None and not self.currentPage == None:
            pdfhl.make_page_content_stream(self.currentPage,data=self.pagestream.data())
        #
        if not self.pagestream == None:
            del self.pagestream
        self.pagestream = None
        #
        if not self.currentPage == None:
            del self.currentPage
        self.currentPage = None
    def new_page(self,pdfhl):
        self.end_page(pdfhl)
        #
        self.currentPage = page = pdfhl.new_page()
        #
        pdfhl.add_page_font_ref(page,self.font1.reg)
        pdfhl.add_page_font_ref(page,self.font1.bold)
        pdfhl.add_page_font_ref(page,self.font1.italic)
        #
        self.pagestream = pdf_module.PDFPageContentWriter()
        #
        self.pageHeight = pdfhl.page_size[1]
        self.currentPos = self.contentRegion.xy
        #
        return page
    def coordxlate(self,xy):
        # PDF coordinate system is bottom-up, we think top down
        return XY(xy.x,self.pageHeight-xy.y)
    def ps(self):
        return self.pagestream

def emit_table_as_pdf(path,table_id,tp):
    emitpdf = EmitPDF()
    #
    pdf = pdf_module.PDFGen()
    pdfhl = pdf_module.PDFGenHL(pdf)
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
    page1 = emitpdf.new_page(pdfhl)
    page1cmd = emitpdf.ps()
    page1cmd.begin_text()
    page1cmd.text_leading(12)
    page1cmd.set_text_font(emitpdf.font1.reg,12)
    page1cmd.text_move_to(288,270)
    page1cmd.fill_color(0,0,0.5)
    page1cmd.text("Hello World. ")
    page1cmd.set_text_font(emitpdf.font1.bold,12)
    page1cmd.fill_color(0,0,1.0)
    page1cmd.text("This is a PDF")
    page1cmd.text_next_line()
    page1cmd.set_text_font(emitpdf.font1.italic,12)
    page1cmd.fill_color(1.0,0,0)
    page1cmd.text("1234ABCD")
    page1cmd.end_text()
    page1cmd.linewidth(2.0)
    page1cmd.stroke_color(0,0.5,0)
    page1cmd.moveto(50,50)
    page1cmd.lineto(100,50)
    page1cmd.lineto(100,100)
    page1cmd.lineto(50,100)
    page1cmd.close_subpath()
    page1cmd.stroke()
    #
    page1cmd.stroke_color(0,0.5,0)
    page1cmd.fill_color(0.5,0,0)
    page1cmd.moveto(150,50)
    page1cmd.lineto(200,50)
    page1cmd.lineto(200,100)
    page1cmd.lineto(150,100)
    page1cmd.close_subpath()
    page1cmd.fill()
    #
    page1cmd.stroke_color(0,0.5,0)
    page1cmd.fill_color(0.5,0,0)
    page1cmd.moveto(250,50)
    page1cmd.lineto(300,50)
    page1cmd.lineto(300,100)
    page1cmd.lineto(250,100)
    page1cmd.close_subpath()
    page1cmd.stroke_and_fill()
    #
    emitpdf.end_page(pdfhl)
    #
    page2 = emitpdf.new_page(pdfhl)
    #
    page2cmd = emitpdf.ps()
    page2cmd.begin_text()
    page2cmd.text_leading(12)
    page2cmd.set_text_font(emitpdf.font1.reg,12)
    page2cmd.text_move_to(288,270)
    page2cmd.fill_color(0,0,0.5)
    page2cmd.text("Page 2")
    page2cmd.end_text()
    page2cmd.linewidth(4.0)
    page2cmd.stroke_color(0,0.5,0)
    page2cmd.fill_color(0.5,0,0)
    page2cmd.moveto(250,50)
    page2cmd.lineto(300,50)
    page2cmd.lineto(300,100)
    page2cmd.lineto(250,100)
    page2cmd.close_subpath()
    page2cmd.stroke_and_fill()
    #
    emitpdf.end_page(pdfhl)
    #
    page1o = pdfhl.get_page(1)
    #
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

