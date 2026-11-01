from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from docx import Document
from PIL import Image, ImageDraw, ImageFilter
import fitz, random
S="data/samples/"; st=getSampleStyleSheet()
lorem="La conversión de documentos a Markdown debe preservar títulos, listas, tablas y el orden de lectura. "*4
tbl=[["Concepto","Q1","Q2","Total"],["Ventas","1.200","1.500","2.700"],["Costes","800","950","1.750"],["Beneficio","400","550","950"]]
def table():
    t=Table(tbl); t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),.5,colors.black),("BACKGROUND",(0,0),(-1,0),colors.lightgrey)])); return t
SimpleDocTemplate(S+"01_nativo_tablas.pdf",pagesize=A4).build([Paragraph("Informe Anual 2025",st["Title"]),Paragraph("1. Resumen",st["Heading1"]),Paragraph(lorem,st["Normal"]),Paragraph("2. Resultados",st["Heading1"]),table(),Spacer(1,12),Paragraph("2.1 Detalle",st["Heading2"]),Paragraph(lorem,st["Normal"])])
d=Document(); d.add_heading("Contrato de servicios",0); d.add_heading("Cláusula 1",1); d.add_paragraph(lorem); d.add_paragraph("Punto uno",style="List Bullet"); d.add_paragraph("Punto dos",style="List Bullet")
t=d.add_table(rows=4,cols=4); t.style="Table Grid"
for i,r in enumerate(tbl):
    for j,c in enumerate(r): t.cell(i,j).text=c
d.save(S+"02_documento.docx")
# imagen de texto + escaneado
im=Image.new("RGB",(1240,1754),"white"); dr=ImageDraw.Draw(im)
from PIL import ImageFont
f=ImageFont.truetype("arial.ttf",34); fb=ImageFont.truetype("arialbd.ttf",52)
dr.text((100,100),"Factura 2025-0147",font=fb,fill="black")
for k,l in enumerate(["Cliente: Empresa Ejemplo S.L.","Fecha: 14/03/2025","Concepto: Servicios de consultoría","Base imponible: 1.000,00 EUR","IVA 21%: 210,00 EUR","Total: 1.210,00 EUR"]): dr.text((100,240+k*70),l,font=f,fill="black")
im.save(S+"03_imagen_texto.png")
sc=im.rotate(1.2,fillcolor="white").filter(ImageFilter.GaussianBlur(1.2))
px=sc.load()
for _ in range(60000): x,y=random.randrange(1240),random.randrange(1754); v=random.randrange(120,255); px[x,y]=(v,v,v)
sc.convert("L").save(S+"04_foto_escaneada.jpg",quality=60)
pdf=fitz.open(); p=pdf.new_page(width=595,height=842); p.insert_image(p.rect,filename=S+"04_foto_escaneada.jpg"); pdf.save(S+"05_pdf_escaneado.pdf")
