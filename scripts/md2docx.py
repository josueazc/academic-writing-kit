#!/usr/bin/env python3
"""Convierte un Markdown con frontmatter a .docx con formato APA 7 (o personalizado).

Sin dependencias: solo la biblioteca estándar de Python 3.8+.

Uso:
    python3 scripts/md2docx.py trabajo.md                # crea trabajo.docx
    python3 scripts/md2docx.py trabajo.md -o final.docx

Formato del Markdown: ver scripts/README.md y 07-plantillas/ejemplo-md2docx.md.
"""
import argparse
import os
import re
import struct
import sys
import zipfile
from xml.sax.saxutils import escape

CM = 567  # twips por centímetro

DEFAULTS = {
    "fuente": "Times New Roman",
    "tamano": 12,
    "interlineado": 2.0,
    "alineacion": "izquierda",          # izquierda | justificada
    "margen_cm": 2.54,
    "sangria_cm": 1.27,
    "numero_pagina": "arriba-derecha",  # arriba-derecha | abajo-derecha | abajo-centro | ninguno
    "numerar_portada": True,
    "portada": "apa",                   # apa | ninguna
    "toc": False,
    "repetir_titulo": True,
    "salto_por_seccion": False,         # True = cada título de nivel 1 en página nueva (tesis)
    "numerar_titulos": False,           # True = 1, 1.1, 1.1.1 (ingeniería, informes técnicos, IEEE)
    "papel": "carta",                   # carta | a4
    "idioma": "es-CR",
}

UNNUMBERED = {"resumen", "abstract", "referencias", "bibliografía", "bibliografia", "anexos", "apéndices",
              "apendices", "agradecimientos", "dedicatoria", "tabla de contenidos", "índice", "indice"}

PAGE_BREAK_TITLES = {"resumen", "abstract", "referencias", "bibliografía", "bibliografia",
                     "anexos", "apéndices", "apendices", "tabla de contenidos", "índice"}


# ---------------------------------------------------------------- frontmatter
def parse_frontmatter(text):
    meta = {}
    if not text.startswith("---"):
        return meta, text
    end = text.find("\n---", 3)
    if end == -1:
        return meta, text
    block, body = text[3:end].strip("\n"), text[end + 4:].lstrip("\n")
    key = None
    for line in block.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^\s*-\s+(.*)$", line)
        if m and key:
            if not isinstance(meta.get(key), list):
                meta[key] = []
            meta[key].append(_scalar(m.group(1)))
            continue
        m = re.match(r"^([A-Za-z_áéíóúñ]+)\s*:\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if val.startswith("[") and val.endswith("]"):
                meta[key] = [_scalar(v) for v in val[1:-1].split(",") if v.strip()]
            else:
                meta[key] = _scalar(val) if val else []
    return meta, body


def _scalar(v):
    v = v.strip().strip('"').strip("'")
    low = v.lower()
    if low in ("true", "sí", "si", "yes"):
        return True
    if low in ("false", "no"):
        return False
    try:
        return float(v) if "." in v else int(v)
    except ValueError:
        return v


# ---------------------------------------------------------------- inline runs
INLINE = re.compile(r"(\*\*\*.+?\*\*\*|\*\*.+?\*\*|\*.+?\*|_.+?_|`.+?`|\[[^\]]+\]\([^)]+\))")


def runs(text, bold=False, italic=False):
    out = []
    for part in INLINE.split(text):
        if not part:
            continue
        b, i, t = bold, italic, part
        if part.startswith("***") and part.endswith("***") and len(part) > 6:
            b, i, t = True, True, part[3:-3]
        elif part.startswith("**") and part.endswith("**") and len(part) > 4:
            b, t = True, part[2:-2]
        elif (part.startswith("*") and part.endswith("*") and len(part) > 2) or \
             (part.startswith("_") and part.endswith("_") and len(part) > 2):
            i, t = True, part[1:-1]
        elif part.startswith("`") and part.endswith("`"):
            t = part[1:-1]
        elif part.startswith("[") and re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", part):
            m = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", part)
            t = m.group(1) if m.group(1) == m.group(2) else f"{m.group(1)} ({m.group(2)})"
        out.append(run(t, b, i))
    return "".join(out)


def run(text, bold=False, italic=False):
    rpr = ("<w:b/>" if bold else "") + ("<w:i/>" if italic else "")
    rpr = f"<w:rPr>{rpr}</w:rPr>" if rpr else ""
    return f'<w:r>{rpr}<w:t xml:space="preserve">{escape(text)}</w:t></w:r>'


def para(content, style=None, align=None, ind=None, page_break=False, keep_next=False, spacing=None):
    ppr = ""
    if style:
        ppr += f'<w:pStyle w:val="{style}"/>'
    if keep_next:
        ppr += "<w:keepNext/>"
    if page_break:
        ppr += "<w:pageBreakBefore/>"
    if spacing:
        ppr += spacing
    if ind is not None:
        ppr += ind
    if align:
        ppr += f'<w:jc w:val="{align}"/>'
    return f"<w:p><w:pPr>{ppr}</w:pPr>{content}</w:p>"


# ---------------------------------------------------------------- images
def image_size(path):
    with open(path, "rb") as f:
        data = f.read()
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        w, h = struct.unpack(">II", data[16:24])
        return w, h, "png"
    if data[:2] == b"\xff\xd8":
        i = 2
        while i < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return w, h, "jpeg"
            seg = struct.unpack(">H", data[i + 2:i + 4])[0]
            i += 2 + seg
    raise ValueError(f"Formato de imagen no soportado (usar PNG o JPG): {path}")


# ---------------------------------------------------------------- builder
class Doc:
    def __init__(self, meta, base_dir):
        self.m = {**DEFAULTS, **meta}
        self.base = base_dir
        self.body = []
        self.images = []  # (rid, filename, bytes)
        self.first_body_heading = True
        self.counters = [0, 0, 0, 0, 0]

    # estilos de párrafo
    def ind_first(self):
        return f'<w:ind w:firstLine="{int(self.m["sangria_cm"] * CM)}"/>'

    def align(self):
        return "both" if str(self.m["alineacion"]).startswith("just") else "left"

    def number(self, level, text):
        """Prefijo 1, 1.1, 1.1.1 si numerar_titulos está activo (no numera resumen, referencias, anexos…)."""
        if not self.m["numerar_titulos"] or level > 3 or text.strip().lower() in UNNUMBERED:
            return text
        self.counters[level - 1] += 1
        for k in range(level, len(self.counters)):
            self.counters[k] = 0
        return ".".join(str(c) for c in self.counters[:level]) + ("." if level == 1 else "") + " " + text

    def heading(self, level, text, force_break=False):
        brk = force_break or (self.m["salto_por_seccion"] and level == 1 and not self.first_body_heading)
        if level == 1:
            self.first_body_heading = False
            if text.strip().lower() in PAGE_BREAK_TITLES:
                brk = True
        self.body.append(para(runs(self.number(level, text)), style=f"Heading{level}", page_break=brk))

    def run_in(self, level, title, text):
        """Niveles 4 y 5: título en la misma línea que el párrafo."""
        t = title.rstrip(".") + "."
        r = run(t + " ", bold=True, italic=(level == 5)) + runs(text)
        self.body.append(para(r, style=f"Heading{level}"))

    def paragraph(self, text, no_indent=False):
        ind = '<w:ind w:firstLine="0"/>' if no_indent else None
        self.body.append(para(runs(text), style="Normal", ind=ind))

    def reference(self, text):
        self.body.append(para(runs(text), style="Referencia"))

    def quote(self, text):
        self.body.append(para(runs(text), style="CitaBloque"))

    def list_item(self, text, marker):
        ind = f'<w:ind w:left="{int(self.m["sangria_cm"] * CM)}" w:hanging="{int(0.63 * CM)}"/>'
        self.body.append(para(run(marker + "\t") + runs(text), style="Normal", ind=ind))

    def caption_number(self, text):  # "Tabla 1" / "Figura 1"
        self.body.append(para(runs(text), style="RotuloNumero", keep_next=True))

    def caption_title(self, text):
        self.body.append(para(runs(text), style="RotuloTitulo", keep_next=True))

    def note(self, text):
        self.body.append(para(runs(text), style="NotaTabla"))

    def page_break(self):
        self.body.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')

    def table(self, rows):
        header, data = rows[0], rows[1:]
        border = '<w:{0} w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        out = ['<w:tbl><w:tblPr><w:tblStyle w:val="TablaAPA"/><w:tblW w:w="5000" w:type="pct"/>'
               '<w:tblBorders>' + border.format("top") + border.format("bottom") +
               '</w:tblBorders></w:tblPr><w:tblGrid>' +
               "".join("<w:gridCol/>" for _ in header) + "</w:tblGrid>"]

        def cell(text, bold=False, bottom=False, center=False):
            tcpr = "<w:tcBorders>" + border.format("bottom") + "</w:tcBorders>" if bottom else ""
            p = para(runs(text, bold=bold), style="CeldaTabla", align="center" if center else None)
            return f"<w:tc><w:tcPr>{tcpr}</w:tcPr>{p}</w:tc>"

        out.append('<w:tr><w:trPr><w:tblHeader/></w:trPr>' +
                   "".join(cell(h, bottom=True, center=True) for h in header) + "</w:tr>")
        for r in data:
            r = (r + [""] * len(header))[:len(header)]
            out.append("<w:tr>" + "".join(cell(c) for c in r) + "</w:tr>")
        out.append("</w:tbl>")
        self.body.append("".join(out))

    def image(self, path, alt):
        full = os.path.join(self.base, path)
        if not os.path.exists(full):
            self.paragraph(f"[IMAGEN NO ENCONTRADA: {path}]", no_indent=True)
            return
        w, h, kind = image_size(full)
        max_w = 15.0  # cm
        cw = min(max_w, w / 96 * 2.54)
        ch = cw * h / w
        emu_w, emu_h = int(cw * 360000), int(ch * 360000)
        idx = len(self.images) + 1
        rid = f"rIdImg{idx}"
        name = f"image{idx}.{'png' if kind == 'png' else 'jpeg'}"
        with open(full, "rb") as f:
            self.images.append((rid, name, f.read()))
        drawing = (
            f'<w:r><w:drawing><wp:inline><wp:extent cx="{emu_w}" cy="{emu_h}"/>'
            f'<wp:docPr id="{idx}" name="{escape(alt or name)}"/>'
            '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
            '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            f'<pic:nvPicPr><pic:cNvPr id="{idx}" name="{name}"/><pic:cNvPicPr/></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{emu_w}" cy="{emu_h}"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
            '</a:graphicData></a:graphic></wp:inline></w:drawing></w:r>')
        self.body.append(para(drawing, style="Normal", ind='<w:ind w:firstLine="0"/>', keep_next=True))

    def toc(self):
        self.body.append(para(run("Tabla de Contenidos", bold=True), style="TituloSinNivel", page_break=True))
        fld = ('<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
               '<w:r><w:instrText xml:space="preserve"> TOC \\o "1-3" \\h \\z \\u </w:instrText></w:r>'
               '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
               + run("Clic derecho → Actualizar campo para generar la tabla de contenidos.") +
               '<w:r><w:fldChar w:fldCharType="end"/></w:r>')
        self.body.append(para(fld, style="Normal", ind='<w:ind w:firstLine="0"/>'))

    def title_page(self):
        m = self.m
        lines = []
        for _ in range(3):
            lines.append(para("", style="Portada"))
        lines.append(para(runs(str(m.get("titulo", "[COMPLETAR: Título]")), bold=True), style="Portada"))
        lines.append(para("", style="Portada"))
        autores = m.get("autores") or ["[COMPLETAR: Autor]"]
        if not isinstance(autores, list):
            autores = [autores]
        for a in autores:
            lines.append(para(runs(str(a)), style="Portada"))
        for k in ("afiliacion", "institucion", "curso", "docente", "fecha"):
            v = m.get(k)
            if v:
                for item in (v if isinstance(v, list) else [v]):
                    lines.append(para(runs(str(item)), style="Portada"))
        self.body.extend(lines)

    # ------------------------------------------------------------ parse body
    def build(self, body):
        if self.m["portada"] == "apa":
            self.title_page()
        if self.m["toc"]:
            self.toc()
        lines = body.splitlines()
        i = 0
        section = ""
        started_body = False
        paragraph_buf = []

        def flush():
            if paragraph_buf:
                text = " ".join(s.strip() for s in paragraph_buf)
                if section in ("referencias", "bibliografía", "bibliografia"):
                    self.reference(text)
                elif section in ("resumen", "abstract"):
                    if re.match(r"^\*?(palabras clave|keywords)", text.lower()):
                        self.paragraph(text)
                    else:
                        self.paragraph(text, no_indent=True)
                else:
                    self.paragraph(text)
                paragraph_buf.clear()

        while i < len(lines):
            line = lines[i]
            s = line.strip()
            m = re.match(r"^(#{1,5})\s+(.*)$", s)
            if m:
                flush()
                level, text = len(m.group(1)), m.group(2).strip()
                lower = re.sub(r"[*_]", "", text).strip().lower()
                if level == 1:
                    section = lower
                if level == 1 and not started_body and lower not in ("resumen", "abstract"):
                    started_body = True
                    brk = self.m["portada"] != "ninguna" or self.m["toc"]
                    if self.m["repetir_titulo"] and self.m.get("titulo"):
                        # APA: la primera página del texto repite el título y la introducción no lleva título
                        self.body.append(para(runs(str(self.m["titulo"]), bold=True),
                                              style="TituloSinNivel", page_break=brk))
                        self.first_body_heading = False
                        if lower not in ("introducción", "introduccion") or self.m["numerar_titulos"]:
                            self.heading(1, text)
                    else:
                        self.heading(1, text, force_break=brk)
                    i += 1
                    continue
                if level >= 4:
                    # el texto del párrafo es la siguiente línea no vacía
                    j = i + 1
                    buf = []
                    while j < len(lines) and lines[j].strip() and not lines[j].strip().startswith("#"):
                        buf.append(lines[j].strip())
                        j += 1
                    self.run_in(level, text, " ".join(buf))
                    i = j
                    continue
                self.heading(level, text)
                i += 1
                continue
            if not s:
                flush()
                i += 1
                continue
            if s in ("\\newpage", "<!-- salto -->", "[SALTO]"):
                flush()
                self.page_break()
                i += 1
                continue
            cap = re.match(r"^\*\*((Tabla|Figura|Anexo|Apéndice)\s+[\w.]+)\*\*$", s)
            if cap:
                flush()
                self.caption_number(f"**{cap.group(1)}**")
                nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
                if nxt.startswith("*") and nxt.endswith("*") and not nxt.startswith("**"):
                    self.caption_title(nxt)
                    i += 1
                i += 1
                continue
            if re.match(r"^\*?Nota\.\*?", s):
                flush()
                self.note(s)
                i += 1
                continue
            img = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", s)
            if img:
                flush()
                self.image(img.group(2), img.group(1))
                i += 1
                continue
            if s.startswith("|"):
                flush()
                rows = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                    if not all(re.match(r"^:?-{2,}:?$", c) for c in row if c):
                        rows.append(row)
                    i += 1
                if rows:
                    self.table(rows)
                continue
            if s.startswith(">"):
                flush()
                buf = []
                while i < len(lines) and lines[i].strip().startswith(">"):
                    buf.append(lines[i].strip().lstrip(">").strip())
                    i += 1
                self.quote(" ".join(buf))
                continue
            lm = re.match(r"^([-*+]|\d+[.)])\s+(.*)$", s)
            if lm:
                flush()
                marker = "•" if lm.group(1) in "-*+" else lm.group(1).rstrip(")").rstrip(".") + "."
                self.list_item(lm.group(2), marker)
                i += 1
                continue
            paragraph_buf.append(s)
            if section in ("referencias", "bibliografía", "bibliografia"):
                flush()  # en Referencias cada línea es una entrada
            i += 1
        flush()

    # ------------------------------------------------------------ package
    def styles_xml(self):
        m = self.m
        sz = int(float(m["tamano"]) * 2)
        line = int(240 * float(m["interlineado"]))
        sp = f'<w:spacing w:before="0" w:after="0" w:line="{line}" w:lineRule="auto"/>'
        single = '<w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>'
        font = escape(str(m["fuente"]))
        ind = int(m["sangria_cm"] * CM)
        al = self.align()

        def style(sid, name, ppr="", rpr="", based="Normal", outline=None):
            ol = f'<w:outlineLvl w:val="{outline}"/>' if outline is not None else ""
            return (f'<w:style w:type="paragraph" w:customStyle="1" w:styleId="{sid}"><w:name w:val="{name}"/>'
                    f'<w:basedOn w:val="{based}"/><w:qFormat/><w:pPr>{ppr}{ol}</w:pPr><w:rPr>{rpr}</w:rPr></w:style>')

        heads = [
            style("Heading1", "heading 1", f'<w:keepNext/><w:ind w:firstLine="0"/><w:jc w:val="{"left" if m["numerar_titulos"] else "center"}"/>', "<w:b/>", outline=0),
            style("Heading2", "heading 2", '<w:keepNext/><w:ind w:firstLine="0"/><w:jc w:val="left"/>', "<w:b/>", outline=1),
            style("Heading3", "heading 3", '<w:keepNext/><w:ind w:firstLine="0"/><w:jc w:val="left"/>', "<w:b/><w:i/>", outline=2),
            style("Heading4", "heading 4", f'<w:ind w:firstLine="{ind}"/>', "", outline=3),
            style("Heading5", "heading 5", f'<w:ind w:firstLine="{ind}"/>', "", outline=4),
        ]
        extra = [
            style("Portada", "Portada", '<w:ind w:firstLine="0"/><w:jc w:val="center"/>'),
            style("TituloSinNivel", "Título sin nivel", '<w:ind w:firstLine="0"/><w:jc w:val="center"/>', "<w:b/>"),
            style("Referencia", "Referencia", f'<w:ind w:left="{ind}" w:hanging="{ind}"/><w:jc w:val="left"/>'),
            # nombres que usa Pandoc cuando este .docx se pasa como --reference-doc
            style("BodyText", "Body Text", ""),
            style("FirstParagraph", "First Paragraph", ""),
            style("Bibliography", "Bibliography", f'<w:ind w:left="{ind}" w:hanging="{ind}"/><w:jc w:val="left"/>'),
            style("BlockText", "Block Text", f'<w:ind w:left="{ind}" w:firstLine="0"/>'),
            style("CitaBloque", "Cita en bloque", f'<w:ind w:left="{ind}" w:firstLine="0"/>'),
            style("RotuloNumero", "Rótulo número", '<w:keepNext/><w:ind w:firstLine="0"/><w:jc w:val="left"/>', "<w:b/>"),
            style("RotuloTitulo", "Rótulo título", '<w:keepNext/><w:ind w:firstLine="0"/><w:jc w:val="left"/>', "<w:i/>"),
            style("NotaTabla", "Nota de tabla", '<w:ind w:firstLine="0"/><w:jc w:val="left"/>'),
            style("CeldaTabla", "Celda de tabla", f'{single}<w:ind w:firstLine="0"/><w:jc w:val="left"/>'),
        ]
        toc = [style(f"TOC{n}", f"toc {n}", f'<w:ind w:left="{(n - 1) * 360}" w:firstLine="0"/>'
                     '<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="9350"/></w:tabs>') for n in (1, 2, 3)]
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            f'<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:cs="{font}" w:eastAsia="{font}"/>'
            f'<w:color w:val="000000"/><w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/><w:lang w:val="{m["idioma"]}"/></w:rPr></w:rPrDefault>'
            f'<w:pPrDefault><w:pPr>{sp}</w:pPr></w:pPrDefault></w:docDefaults>'
            '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/>'
            f'<w:pPr>{sp}<w:ind w:firstLine="{ind}"/><w:jc w:val="{al}"/></w:pPr></w:style>'
            + "".join(heads + extra + toc) +
            '<w:style w:type="table" w:styleId="TablaAPA"><w:name w:val="Tabla APA"/>'
            '<w:tblPr><w:tblCellMar><w:left w:w="100" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tblCellMar></w:tblPr></w:style>'
            '</w:styles>')

    def header_footer(self):
        pos = self.m["numero_pagina"]
        if pos == "ninguno":
            return None, None
        align = "right" if "derecha" in pos else "center"
        fld = ('<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
               '<w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>1</w:t></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r>')
        p = f'<w:p><w:pPr><w:spacing w:line="240" w:lineRule="auto"/><w:jc w:val="{align}"/></w:pPr>{fld}</w:p>'
        ns = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
        kind = "hdr" if pos.startswith("arriba") else "ftr"
        return kind, f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:{kind} {ns}>{p}</w:{kind}>'

    def save(self, out):
        m = self.m
        w, h = (12240, 15840) if m["papel"] == "carta" else (11906, 16838)
        mar = int(float(m["margen_cm"]) * CM)
        kind, hf = self.header_footer()
        ref = ""
        if kind:
            tag = "headerReference" if kind == "hdr" else "footerReference"
            ref = f'<w:{tag} w:type="default" r:id="rIdHF"/>'
        title_pg = "" if m["numerar_portada"] or m["portada"] == "ninguna" else "<w:titlePg/>"
        sect = (f'<w:sectPr>{ref}<w:pgSz w:w="{w}" w:h="{h}"/>'
                f'<w:pgMar w:top="{mar}" w:right="{mar}" w:bottom="{mar}" w:left="{mar}" w:header="708" w:footer="708" w:gutter="0"/>'
                f'{title_pg}</w:sectPr>')
        document = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
            'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">'
            f'<w:body>{"".join(self.body)}{sect}</w:body></w:document>')
        rels = ['<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>',
                '<Relationship Id="rIdSettings" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>']
        if kind:
            t = "header" if kind == "hdr" else "footer"
            rels.append(f'<Relationship Id="rIdHF" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/{t}" Target="{t}1.xml"/>')
        for rid, name, _ in self.images:
            rels.append(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{name}"/>')
        ct = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
              '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
              '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
              '<Default Extension="xml" ContentType="application/xml"/>'
              '<Default Extension="png" ContentType="image/png"/><Default Extension="jpeg" ContentType="image/jpeg"/>'
              '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
              '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
              '<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
              '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>')
        if kind:
            t = "header" if kind == "hdr" else "footer"
            ct += f'<Override PartName="/word/{t}1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.{t}+xml"/>'
        ct += "</Types>"
        settings = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                    '<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                    + ('<w:updateFields w:val="true"/>' if m["toc"] else "") +
                    f'<w:defaultTabStop w:val="708"/><w:themeFontLang w:val="{m["idioma"]}"/></w:settings>')
        autores = m.get("autores") or []
        autores = autores if isinstance(autores, list) else [autores]
        core = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
                'xmlns:dc="http://purl.org/dc/elements/1.1/">'
                f'<dc:title>{escape(str(m.get("titulo", "")))}</dc:title>'
                f'<dc:creator>{escape("; ".join(map(str, autores)))}</dc:creator>'
                f'<dc:language>{m["idioma"]}</dc:language></cp:coreProperties>')
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", ct)
            z.writestr("_rels/.rels",
                       '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                       '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                       '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
                       '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
                       '</Relationships>')
            z.writestr("docProps/core.xml", core)
            z.writestr("word/document.xml", document)
            z.writestr("word/styles.xml", self.styles_xml())
            z.writestr("word/settings.xml", settings)
            z.writestr("word/_rels/document.xml.rels",
                       '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                       '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                       + "".join(rels) + "</Relationships>")
            if kind:
                t = "header" if kind == "hdr" else "footer"
                z.writestr(f"word/{t}1.xml", hf)
            for _, name, data in self.images:
                z.writestr(f"word/media/{name}", data)


def main():
    ap = argparse.ArgumentParser(description="Markdown → .docx con formato APA 7")
    ap.add_argument("entrada")
    ap.add_argument("-o", "--salida")
    args = ap.parse_args()
    with open(args.entrada, encoding="utf-8") as f:
        meta, body = parse_frontmatter(f.read())
    doc = Doc(meta, os.path.dirname(os.path.abspath(args.entrada)))
    doc.build(body)
    out = args.salida or os.path.splitext(args.entrada)[0] + ".docx"
    doc.save(out)
    print(f"Listo: {out}")


if __name__ == "__main__":
    sys.exit(main())
