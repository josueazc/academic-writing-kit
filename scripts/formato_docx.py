#!/usr/bin/env python3
"""Valida el formato de un .docx hecho en cualquier procesador (Word, Google Docs, LibreOffice).

Lee los estilos y las propiedades directas de cada párrafo y compara con APA 7 de
estudiante (01-formato/apa7-formato-pagina.md) o con lo que pida la rúbrica:
márgenes, tamaño de página, fuente y tamaño, interlineado, espacio entre párrafos,
sangría de primera línea, sangría francesa en referencias, alineación, número de
página, títulos con estilo y espacios o líneas en blanco usados para dar formato.

Uso:
    python3 scripts/formato_docx.py trabajo.docx
    python3 scripts/formato_docx.py trabajo.docx --fuente Arial --tamano 12 --interlineado 1.5 --margen 3 --justificado
Código de salida 1 si hay hallazgos importantes.
"""
import argparse
import re
import sys
import zipfile
from collections import Counter
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
CM = 567  # twips por centímetro
TAMANO_APA = {"times new roman": 12, "calibri": 11, "arial": 11, "georgia": 11, "lucida sans unicode": 10,
              "computer modern": 10, "cmu serif": 10}
REF_TITLES = ("referencias", "bibliografía", "bibliografia", "referencias bibliográficas", "references")


def g(el, path, attr="val"):
    x = el.find(path) if el is not None else None
    return x.get(W + attr) if x is not None and x.get(W + attr) is not None else None


class Estilos:
    def __init__(self, z):
        self.root = ET.fromstring(z.read("word/styles.xml")) if "word/styles.xml" in z.namelist() else ET.Element("x")
        self.by_id = {s.get(W + "styleId"): s for s in self.root.iter(W + "style")}
        self.default_p = next((s.get(W + "styleId") for s in self.root.iter(W + "style")
                               if s.get(W + "type") == "paragraph" and s.get(W + "default") == "1"), None)
        dd = self.root.find(f"{W}docDefaults")
        self.dd_r = dd.find(f"{W}rPrDefault/{W}rPr") if dd is not None else None
        self.dd_p = dd.find(f"{W}pPrDefault/{W}pPr") if dd is not None else None
        self.tema = {}
        if "word/theme/theme1.xml" in z.namelist():
            t = ET.fromstring(z.read("word/theme/theme1.xml"))
            for k, tag in (("minor", "minorFont"), ("major", "majorFont")):
                lat = t.find(f".//{A}{tag}/{A}latin")
                if lat is not None:
                    self.tema[k] = lat.get("typeface")

    def cadena(self, sid):
        out, vistos = [], set()
        while sid and sid in self.by_id and sid not in vistos:
            vistos.add(sid)
            out.append(self.by_id[sid])
            sid = g(self.by_id[sid], f"{W}basedOn")
        return out

    def nombre(self, sid):
        s = self.by_id.get(sid)
        return (g(s, f"{W}name") or sid or "").lower() if s is not None else (sid or "").lower()


def prop(capas, path, attr="val"):
    """Primer valor definido recorriendo las capas de más específica a más general."""
    for c in capas:
        v = g(c, path, attr)
        if v is not None:
            return v
    return None


def fuente(capas, est):
    for c in capas:
        f = c.find(f"{W}rFonts") if c is not None else None
        if f is None:
            continue
        if f.get(W + "ascii"):
            return f.get(W + "ascii")
        th = f.get(W + "asciiTheme")
        if th:
            return est.tema.get("major" if "major" in th else "minor", th)
    return None


def validar(path, fuente_esperada=None, tamano=None, interlineado=2.0, margen=2.54, justificado=False):
    z = zipfile.ZipFile(path)
    est = Estilos(z)
    root = ET.fromstring(z.read("word/document.xml"))
    body = root.find(f"{W}body")
    H = {"CRÍTICO": [], "IMPORTANTE": [], "MENOR": []}
    datos = {}

    # página
    sect = body.find(f"{W}sectPr") if body is not None else None
    if sect is not None:
        mar = sect.find(f"{W}pgMar")
        if mar is not None:
            lados = {k: int(float(mar.get(W + k, 0))) / CM for k in ("top", "right", "bottom", "left")}
            datos["margenes_cm"] = {k: round(v, 2) for k, v in lados.items()}
            malos = [f"{k} {v:.2f}" for k, v in lados.items() if abs(v - margen) > 0.15]
            if malos:
                H["IMPORTANTE"].append(f"Márgenes distintos de {margen} cm: " + ", ".join(malos) + " cm.")
        sz = sect.find(f"{W}pgSz")
        if sz is not None:
            w, h = int(sz.get(W + "w", 0)), int(sz.get(W + "h", 0))
            datos["pagina"] = "carta" if abs(w - 12240) < 60 and abs(h - 15840) < 60 else "A4" if abs(w - 11906) < 60 else f"{w}×{h}"
            if datos["pagina"] not in ("carta", "A4"):
                H["MENOR"].append(f"Tamaño de página poco común ({datos['pagina']} twips): APA usa carta.")
    numeracion = False
    for n in z.namelist():
        if re.match(r"word/(header|footer)\d*\.xml", n):
            x = z.read(n).decode("utf-8", "ignore")
            if re.search(r"\bPAGE\b", x):
                numeracion = True
                datos["numero_pagina"] = "encabezado" if "header" in n else "pie"
    if not numeracion:
        H["IMPORTANTE"].append("No hay número de página (campo PAGE) en el encabezado ni en el pie.")

    # párrafos del cuerpo (fuera de tablas y del índice)
    fuentes, tamanos, lineas, alineaciones = Counter(), Counter(), Counter(), Counter()
    sin_sangria, espacio, sin_estilo_titulo, francesa_mal, vacios_seguidos, tab_inicio = 0, 0, [], 0, 0, 0
    cuerpo, en_refs, vacios, hubo_titulo = 0, False, 0, False
    hijos = list(body) if body is not None else []
    for el in hijos:
        if el.tag != W + "p":
            vacios = 0
            continue
        ppr = el.find(f"{W}pPr")
        sid = g(ppr, f"{W}pStyle") or est.default_p
        cadena = est.cadena(sid)
        nombre = est.nombre(sid)
        capas_p = [ppr] + [s.find(f"{W}pPr") for s in cadena] + [est.dd_p]
        texto = "".join(t.text or "" for t in el.iter(W + "t"))
        if not texto.strip():
            if not el.findall(f".//{W}drawing") and not el.findall(f".//{W}br"):
                vacios += 1
                if vacios == 2 and hubo_titulo:  # en la portada APA sí lleva líneas en blanco
                    vacios_seguidos += 1
            continue
        vacios = 0
        es_titulo = bool(re.search(r"heading|t[ií]tulo|title|toc|portada|caption|epígrafe", nombre)) or prop(capas_p, f"{W}outlineLvl") is not None
        if es_titulo:
            if re.search(r"heading|t[ií]tulo", nombre):
                hubo_titulo = True
                en_refs = texto.strip().lower() in REF_TITLES
            continue
        if re.search(r"r[oó]tulo|nota|celda|cita|bloque|block|list|lista|footnote", nombre):
            continue  # rótulos de tabla, notas, citas en bloque y listas tienen su propio formato
        runs = [r for r in el.iter(W + "r") if (r.find(f"{W}t") is not None and (r.find(f"{W}t").text or "").strip())]
        todo_negrita = runs and all(prop([r.find(f"{W}rPr")] + [s.find(f"{W}rPr") for s in cadena], f"{W}b") not in (None, "0", "false") for r in runs)
        if todo_negrita and len(texto) < 90 and not texto.rstrip().endswith((".", ":")):
            sin_estilo_titulo.append(texto.strip()[:50])
            continue
        cuerpo += 1
        if texto.startswith(("\t", "  ")):
            tab_inicio += 1
        for r in runs:
            capas_r = [r.find(f"{W}rPr")]
            rs = g(r.find(f"{W}rPr"), f"{W}rStyle")
            capas_r += [s.find(f"{W}rPr") for s in est.cadena(rs)] + [s.find(f"{W}rPr") for s in cadena] + [est.dd_r]
            n = len(r.find(f"{W}t").text or "")
            f = fuente(capas_r, est) or "(predeterminada)"
            fuentes[f] += n
            s = prop(capas_r, f"{W}sz")
            tamanos[int(s) / 2 if s else 10.0] += n
        line = prop(capas_p, f"{W}spacing", "line")
        regla = prop(capas_p, f"{W}spacing", "lineRule") or "auto"
        lineas[round(int(line) / 240, 2) if line and regla == "auto" else f"{regla} {line}"] += 1
        antes = int(prop(capas_p, f"{W}spacing", "before") or 0)
        despues = int(prop(capas_p, f"{W}spacing", "after") or 0)
        if antes > 20 or despues > 20:
            espacio += 1
        jc = prop(capas_p, f"{W}jc") or "left"
        alineaciones[jc] += 1
        first = prop(capas_p, f"{W}ind", "firstLine")
        hanging = prop(capas_p, f"{W}ind", "hanging")
        left = prop(capas_p, f"{W}ind", "left") or prop(capas_p, f"{W}ind", "start")
        if en_refs:
            if not hanging or abs(int(hanging) - 720) > 60:
                francesa_mal += 1
        elif not hanging and not (left and int(left) > 0) and (not first or int(first) < 500):
            sin_sangria += 1

    datos.update(parrafos=cuerpo, fuentes=dict(fuentes.most_common(4)), tamanos=dict(tamanos.most_common(3)),
                 interlineado=dict(lineas.most_common(3)), alineacion=dict(alineaciones.most_common(3)))
    if cuerpo:
        total = sum(fuentes.values()) or 1
        principal, n = fuentes.most_common(1)[0]
        esperada = (fuente_esperada or "").lower()
        if esperada and principal.lower() != esperada:
            H["IMPORTANTE"].append(f"Fuente del texto: {principal}; se pidió {fuente_esperada}.")
        elif not esperada and principal.lower() not in TAMANO_APA:
            H["IMPORTANTE"].append(f"Fuente del texto: {principal}, que no es de las aceptadas por APA 7 (Times New Roman 12, Calibri 11, Arial 11, Georgia 11…).")
        if n / total < 0.9:
            H["MENOR"].append("Hay más de una fuente en el texto: " + ", ".join(f"{k} ({v / total:.0%})" for k, v in fuentes.most_common(3)) + ".")
        tam = tamano or TAMANO_APA.get(principal.lower())
        t_principal = tamanos.most_common(1)[0][0]
        if tam and t_principal != tam:
            H["IMPORTANTE"].append(f"Tamaño de letra del texto: {t_principal:g} pt; corresponde {tam:g} pt.")
        l_principal, ln = lineas.most_common(1)[0]
        if l_principal != round(interlineado, 2):
            H["IMPORTANTE"].append(f"Interlineado del texto: {l_principal}; corresponde {interlineado:g}.")
        elif ln / cuerpo < 0.85:
            H["MENOR"].append(f"Interlineado irregular: {dict(lineas.most_common(3))}.")
        if espacio / cuerpo > 0.2:
            H["IMPORTANTE"].append(f"{espacio} párrafos con espacio antes o después: APA usa 0 pt y doble espacio.")
        j = alineaciones.most_common(1)[0][0]
        if justificado and j != "both":
            H["IMPORTANTE"].append("Se pidió texto justificado y el texto no lo está.")
        if not justificado and j == "both":
            H["MENOR"].append("Texto justificado: APA alinea a la izquierda (dejalo si tu institución pide justificado y usá --justificado).")
        if sin_sangria / cuerpo > 0.3:
            H["IMPORTANTE"].append(f"{sin_sangria} de {cuerpo} párrafos sin sangría de primera línea de 1.27 cm (usá el estilo, no Tab).")
    if francesa_mal:
        H["IMPORTANTE"].append(f"{francesa_mal} referencias sin sangría francesa de 1.27 cm.")
    if sin_estilo_titulo:
        H["IMPORTANTE"].append(f"{len(sin_estilo_titulo)} títulos hechos con negrita en vez de estilo Título 1–5 (no entran al índice): «" +
                               "», «".join(sin_estilo_titulo[:4]) + "».")
    if vacios_seguidos:
        H["MENOR"].append(f"{vacios_seguidos} grupos de líneas en blanco usadas para separar: usá salto de página o espaciado del estilo.")
    if tab_inicio:
        H["MENOR"].append(f"{tab_inicio} párrafos empiezan con Tab o espacios: la sangría va en el estilo.")
    return H, datos


def main():
    ap = argparse.ArgumentParser(description="Valida el formato APA 7 (o el de la rúbrica) de un .docx")
    ap.add_argument("archivo")
    ap.add_argument("--fuente", help="fuente pedida (por defecto, cualquiera de las de APA 7)")
    ap.add_argument("--tamano", type=float, help="tamaño pedido en pt (por defecto, el de APA para esa fuente)")
    ap.add_argument("--interlineado", type=float, default=2.0, help="1, 1.5 o 2 (por defecto 2)")
    ap.add_argument("--margen", type=float, default=2.54, help="margen en cm (por defecto 2.54)")
    ap.add_argument("--justificado", action="store_true", help="la institución pide texto justificado")
    a = ap.parse_args()
    H, datos = validar(a.archivo, a.fuente, a.tamano, a.interlineado, a.margen, a.justificado)
    print(f"# Formato de `{a.archivo}`\n")
    for k, v in datos.items():
        print(f"- {k}: {v}")
    print()
    for sev, hs in H.items():
        for h in hs:
            print(f"- [{sev}] {h}")
    if not any(H.values()):
        print("Sin problemas de formato detectados.")
    sys.exit(1 if H["CRÍTICO"] or H["IMPORTANTE"] else 0)


if __name__ == "__main__":
    main()
