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
    "pie_texto": "",                    # texto fijo a la izquierda del pie/encabezado (p. ej., título corto)
    "comillas": "inglesas",             # inglesas “” | latinas «» | rectas ""
    "modo": "apa",                      # apa | completo
}

# "Trabajo escrito completo": portada institucional completa, índice, número de página
# en el pie, cada sección principal en página nueva.
COMPLETO = {
    "portada": "completa",
    "toc": True,
    "numero_pagina": "abajo-derecha",
    "numerar_portada": False,
    "salto_por_seccion": True,
    "repetir_titulo": False,
}

COMILLAS = {"inglesas": ("\u201c", "\u201d"), "latinas": ("\u00ab", "\u00bb")}
_comillas = COMILLAS["inglesas"]


def tipografia(text):
    """Comillas rectas → tipográficas, sin tocar URLs."""
    if not _comillas:
        return text
    partes = re.split(r"(https?://\S+)", text)
    for k in range(0, len(partes), 2):
        s, out, abierta = partes[k], [], False
        for i, ch in enumerate(s):
            if ch == '"':
                prev = s[i - 1] if i else " "
                abre = prev.isspace() or prev in "([{¿¡—–-/" or (not abierta and i == 0)
                out.append(_comillas[0] if abre else _comillas[1])
                abierta = abre
            else:
                out.append(ch)
        partes[k] = "".join(out)
    return "".join(partes)

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
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]  # entre comillas: siempre texto ("01" no se convierte en 1)
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


def run(text, bold=False, italic=False, size=None, caps=False):
    rpr = ("<w:b/>" if bold else "") + ("<w:i/>" if italic else "") + ("<w:caps/>" if caps else "")
    if size:
        rpr += f'<w:sz w:val="{int(size * 2)}"/><w:szCs w:val="{int(size * 2)}"/>'
    rpr = f"<w:rPr>{rpr}</w:rPr>" if rpr else ""
    return f'<w:r>{rpr}<w:t xml:space="preserve">{escape(tipografia(text))}</w:t></w:r>'


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
        global _comillas
        preset = COMPLETO if str(meta.get("modo", "")).lower() == "completo" else {}
        self.m = {**DEFAULTS, **preset, **meta}
        _comillas = COMILLAS.get(str(self.m["comillas"]).lower())
        self.toc_entries = []
        self.toc_at = None
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
        if level == 2 and re.match(r"(anexo|apéndice|apendice)\s", text.strip().lower()):
            brk = True  # cada anexo en página nueva
        texto = self.number(level, text)
        if level <= 3:
            self.toc_entries.append((level, re.sub(r"[*_`]", "", texto)))
        self.body.append(para(runs(texto), style=f"Heading{level}", page_break=brk))

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
        n = len(header)
        border = '<w:{0} w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        # ancho total = ancho de página menos márgenes; columnas proporcionales al texto más largo
        page_w = 12240 if self.m["papel"] == "carta" else 11906
        total = page_w - 2 * int(float(self.m["margen_cm"]) * CM)
        def col(i):
            return [str(header[i])] + [str(r[i]) for r in data if i < len(r)]
        # peso = lo que pide la palabra más larga (no se corta) o la mitad del texto más largo
        pesos = [max(max(len(w) for c in col(i) for w in (c.split() or [""])) + 2,
                     min(max(len(c) for c in col(i)), 60) / 2) for i in range(n)]
        widths = [int(total * p / sum(pesos)) for p in pesos]
        out = ['<w:tbl><w:tblPr><w:tblStyle w:val="TablaAPA"/>'
               f'<w:tblW w:w="{total}" w:type="dxa"/><w:tblLayout w:type="fixed"/>'
               '<w:tblBorders>' + border.format("top") + border.format("bottom") +
               '</w:tblBorders></w:tblPr><w:tblGrid>' +
               "".join(f'<w:gridCol w:w="{w}"/>' for w in widths) + "</w:tblGrid>"]

        def cell(text, width, bold=False, bottom=False, center=False, keep=True):
            tcpr = f'<w:tcW w:w="{width}" w:type="dxa"/>'
            if bottom:
                tcpr += "<w:tcBorders>" + border.format("bottom") + "</w:tcBorders>"
            # keepNext en todas las filas menos la última: la tabla no se parte entre páginas si cabe en una
            p = para(runs(text, bold=bold), style="CeldaTabla", align="center" if center else None, keep_next=keep)
            return f"<w:tc><w:tcPr>{tcpr}</w:tcPr>{p}</w:tc>"

        out.append('<w:tr><w:trPr><w:cantSplit/><w:tblHeader/></w:trPr>' +
                   "".join(cell(h, widths[i], bottom=True, center=True) for i, h in enumerate(header)) + "</w:tr>")
        for r in data:
            r = (r + [""] * n)[:n]
            out.append("<w:tr><w:trPr><w:cantSplit/></w:trPr>" +
                       "".join(cell(c, widths[i]) for i, c in enumerate(r)) + "</w:tr>")  # también la última: la Nota queda pegada
        out.append("</w:tbl>")
        self.body.append("".join(out))

    def image(self, path, alt, center=False, max_cm=15.0):
        full = os.path.join(self.base, path)
        if not os.path.exists(full):
            self.paragraph(f"[IMAGEN NO ENCONTRADA: {path}]", no_indent=True)
            return
        w, h, kind = image_size(full)
        max_w = max_cm
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
        self.body.append(para(drawing, style="Normal", ind='<w:ind w:firstLine="0"/>', keep_next=True,
                              align="center" if center else None))

    def toc(self):
        self.body.append(para(run("Tabla de Contenidos", bold=True), style="TituloSinNivel", page_break=True))
        self.toc_at = len(self.body)  # se completa en fill_toc() cuando ya se conocen los títulos

    def fill_toc(self):
        """Campo TOC de Word con los títulos ya escritos (Word, LibreOffice y Docs lo muestran;
        Word agrega los números de página al actualizar campos)."""
        if self.toc_at is None:
            return
        entries = self.toc_entries or [(1, "Actualizá el índice: clic derecho → Actualizar campo")]
        begin = ('<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
                 '<w:r><w:instrText xml:space="preserve"> TOC \\o "1-3" \\h \\z \\u </w:instrText></w:r>'
                 '<w:r><w:fldChar w:fldCharType="separate"/></w:r>')
        end = '<w:r><w:fldChar w:fldCharType="end"/></w:r>'
        paras = []
        for k, (lvl, texto) in enumerate(entries):
            content = (begin if k == 0 else "") + run(texto) + '<w:r><w:tab/></w:r>' + \
                      (end if k == len(entries) - 1 else "")
            paras.append(para(content, style=f"TOC{lvl}"))
        self.body[self.toc_at:self.toc_at] = paras

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

    def title_page_completa(self):
        """Portada institucional con los datos del usuario (ver 07-plantillas/mi-perfil.yaml)."""
        m = self.m

        def linea(texto, **kw):
            self.body.append(para(run(str(texto), **kw), style="PortadaCompleta"))

        def vacia(n=1):
            for _ in range(n):
                self.body.append(para("", style="PortadaCompleta"))

        if m.get("logo"):
            self.image(str(m["logo"]), "Logo", center=True, max_cm=4.0)
        for k, kw in (("institucion", {"bold": True, "caps": True}), ("facultad", {}), ("escuela", {}), ("carrera", {})):
            if m.get(k):
                linea(m[k], **kw)
        vacia(2)
        if m.get("curso"):
            linea(m["curso"])
        vacia(2)
        linea(m.get("titulo", "[COMPLETAR: Título]"), bold=True, size=16)
        if m.get("subtitulo"):
            linea(m["subtitulo"], italic=True)
        if m.get("tipo_trabajo"):
            vacia()
            linea(m["tipo_trabajo"])
        vacia(2)
        autores = m.get("autores") or ["[COMPLETAR: Autor]"]
        autores = autores if isinstance(autores, list) else [autores]
        linea("Presentado por:", bold=True)
        for a in autores:
            linea(a)
        if m.get("docente"):
            vacia()
            linea("Docente:", bold=True)
            linea(m["docente"])
        if m.get("grupo"):
            vacia()
            linea(f"Grupo: {m['grupo']}")
        vacia(2)
        lugar_fecha = ", ".join(str(x) for x in (m.get("lugar"), m.get("fecha")) if x)
        if lugar_fecha:
            linea(lugar_fecha)

    # ------------------------------------------------------------ parse body
    def build(self, body):
        if self.m["portada"] == "apa":
            self.title_page()
        elif self.m["portada"] == "completa":
            self.title_page_completa()
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
            style("PortadaCompleta", "Portada completa",
                  '<w:spacing w:before="0" w:after="0" w:line="300" w:lineRule="auto"/><w:ind w:firstLine="0"/><w:jc w:val="center"/>'),
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
        texto = str(self.m.get("pie_texto") or "")
        if pos == "ninguno" and not texto:
            return None, None
        fld = ('<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
               '<w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>1</w:t></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r>')
        if pos == "ninguno":
            fld, pos = "", "abajo-derecha"
        page_w = 12240 if self.m["papel"] == "carta" else 11906
        ancho = page_w - 2 * int(float(self.m["margen_cm"]) * CM)
        if texto:  # texto a la izquierda, número a la derecha
            contenido = run(texto, size=10) + '<w:r><w:tab/></w:r>' + fld
            ppr = f'<w:tabs><w:tab w:val="right" w:pos="{ancho}"/></w:tabs><w:spacing w:line="240" w:lineRule="auto"/>'
        else:
            align = "right" if "derecha" in pos else "center"
            contenido = fld
            ppr = f'<w:spacing w:line="240" w:lineRule="auto"/><w:jc w:val="{align}"/>'
        p = f'<w:p><w:pPr>{ppr}</w:pPr>{contenido}</w:p>'
        ns = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
        kind = "hdr" if pos.startswith("arriba") else "ftr"
        return kind, f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:{kind} {ns}>{p}</w:{kind}>'

    def save(self, out):
        self.fill_toc()
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


def buscar_perfil(carpeta):
    """mi-perfil.yaml en la carpeta del trabajo, sus carpetas superiores o la raíz del kit."""
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    actual = carpeta
    for _ in range(4):
        p = os.path.join(actual, "mi-perfil.yaml")
        if os.path.isfile(p):
            return p
        actual = os.path.dirname(actual)
    p = os.path.join(raiz, "mi-perfil.yaml")
    return p if os.path.isfile(p) else None


def exportar_pdf(docx):
    """PDF con LibreOffice (cualquier sistema) o con Microsoft Word en macOS (actualiza el índice)."""
    import platform
    import shutil
    import subprocess
    docx = os.path.abspath(docx)
    pdf = os.path.splitext(docx)[0] + ".pdf"
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice:
        try:
            subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", os.path.dirname(docx), docx],
                           capture_output=True, timeout=180)
        except subprocess.TimeoutExpired:
            print("LibreOffice no respondió en 3 minutos.", file=sys.stderr)
        if os.path.exists(pdf):
            print(f"PDF: {pdf}")
            return
    if platform.system() == "Darwin" and os.path.isdir("/Applications/Microsoft Word.app"):
        # Word (sandbox) solo puede abrir sin permisos los archivos de su propia carpeta
        cont = os.path.expanduser("~/Library/Containers/com.microsoft.Word/Data/Documents")
        os.makedirs(cont, exist_ok=True)
        tmp_docx = os.path.join(cont, "_md2docx_tmp.docx")
        tmp_pdf = os.path.join(cont, "_md2docx_tmp.pdf")
        sin_aviso = tmp_docx + ".x"
        # copia sin la marca updateFields para que Word no muestre el diálogo; el índice se actualiza por script
        with zipfile.ZipFile(docx) as zin, zipfile.ZipFile(sin_aviso, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.namelist():
                data = zin.read(item)
                if item == "word/settings.xml":
                    data = data.replace(b'<w:updateFields w:val="true"/>', b"")
                zout.writestr(item, data)
        os.replace(sin_aviso, tmp_docx)
        espera = int(os.environ.get("MD2DOCX_PDF_TIMEOUT", "120"))
        script = f'''with timeout of {espera} seconds
tell application "Microsoft Word"
open (POSIX file "{tmp_docx}")
delay 5
set d to document 1
set r to ""
try
set n to count of tables of contents of d
if n > 0 then
update table of contents (table of contents 1 of d)
delay 1
update (table of contents 1 of d)
set r to "indice-actualizado"
end if
on error e
set r to "indice-error: " & e
end try
save as d file name "{tmp_pdf}" file format format PDF
close d saving no
return r
end tell
end timeout'''
        try:
            r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=espera + 30)
        except subprocess.TimeoutExpired:
            # casi siempre es un diálogo de Word esperando respuesta (permisos, activación, recuperar documentos)
            try:
                subprocess.run(["osascript", "-e", 'tell application "Microsoft Word" to close (every document whose name is "_md2docx_tmp.docx") saving no'],
                               capture_output=True, timeout=20)
            except subprocess.TimeoutExpired:
                pass
            print(f"Word no respondió en {espera + 30} s (seguramente hay un diálogo abierto en Word). El .docx está listo: "
                  "abrilo, aceptá actualizar los campos del índice y exportá a PDF desde Word. "
                  "Podés dar más tiempo con MD2DOCX_PDF_TIMEOUT=300.", file=sys.stderr)
            if os.path.exists(tmp_docx):
                os.remove(tmp_docx)
            return
        if "indice-error" in r.stdout:
            print(f"Aviso: Word no actualizó el índice ({r.stdout.strip()})", file=sys.stderr)
        if os.path.exists(tmp_pdf):
            shutil.move(tmp_pdf, pdf)
            os.remove(tmp_docx)
            print(f"PDF: {pdf}")
            return
        print(f"Word no pudo exportar: {r.stderr.strip()}", file=sys.stderr)
    print("Sin LibreOffice ni Word: abrí el .docx y exportá a PDF desde tu procesador de texto.", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description="Markdown → .docx con formato APA 7")
    ap.add_argument("entrada")
    ap.add_argument("-o", "--salida")
    ap.add_argument("--pdf", action="store_true", help="exportar también a PDF (LibreOffice o Word en macOS)")
    args = ap.parse_args()
    with open(args.entrada, encoding="utf-8") as f:
        meta, body = parse_frontmatter(f.read())
    perfil = buscar_perfil(os.path.dirname(os.path.abspath(args.entrada)))
    if perfil:
        with open(perfil, encoding="utf-8") as f:
            datos, _ = parse_frontmatter("---\n" + f.read() + "\n---\n")
        meta = {**datos, **meta}  # lo del trabajo manda sobre el perfil
        print(f"Perfil: {perfil}")
    doc = Doc(meta, os.path.dirname(os.path.abspath(args.entrada)))
    doc.build(body)
    out = args.salida or os.path.splitext(args.entrada)[0] + ".docx"
    doc.save(out)
    print(f"Listo: {out}")
    if args.pdf:
        exportar_pdf(out)


if __name__ == "__main__":
    sys.exit(main())
