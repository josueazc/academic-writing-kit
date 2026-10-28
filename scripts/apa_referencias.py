#!/usr/bin/env python3
"""Revisa la forma de cada referencia según APA 7 (02-citas-y-referencias/apa7-referencias.md).

No confirma que la fuente exista (eso es verificar_referencias.py) ni que el contenido
sea correcto: solo la sintaxis. Las cursivas se revisan en Markdown (*…*); en .docx se
pierde ese dato al leer el texto y se omite ese chequeo.

Uso directo: python3 scripts/apa_referencias.py trabajo.md
"""
import re
import sys

AUTOR_PERSONA = re.compile(r"^(?:(?:de|del|la|las|los|van|von|der|den|ten|ter|da|das|do|dos|di|du|le|y)\s+)*[A-ZÁÉÍÓÚÑÜ][\wÁÉÍÓÚÑÜáéíóúñü'’ -]+, [A-ZÁÉÍÓÚÑ][a-z]?\.")
FECHA = re.compile(r"\((?:\d{4}[a-z]?(?:[–-]\d{4})?(?:, [^)]+)?|s\. f\.(?:-[a-z])?|en prensa)\)\.")
ARTICULO = re.compile(r"\d+\*?\(\d+[-–]?\d*\)|\*?,\s*\d+\*?,\s*(?:\d+[-–]\d+|e\d+|art)")


def revisar_una(ref, es_md=True):
    """Lista de (severidad, mensaje) para una referencia."""
    out = []
    r = ref.strip()
    corto = r[:70] + ("…" if len(r) > 70 else "")
    m = re.search(r"\(", r)
    autores = r[:m.start()].strip() if m else ""
    if not FECHA.search(r):
        out.append(("IMPORTANTE", f"Fecha fuera de formato APA (va «(2024).», «(2024, 6 de marzo).» o «(s. f.).» después del autor): «{corto}»"))
    if "," in autores and not AUTOR_PERSONA.match(autores) and not re.search(r"\[|\(Ed", autores):
        out.append(("MENOR", f"Autor sin el formato «Apellido, A. A.» (o es un autor corporativo con coma): «{corto}»"))
    if re.search(r"\bet al\.", autores):
        out.append(("IMPORTANTE", f"«et al.» en la lista de referencias: APA 7 escribe hasta 20 autores. «{corto}»"))
    if re.search(r"[A-Z]\., [A-ZÁÉÍÓÚÑ][^,]+, [A-Z]\.(?: [A-Z]\.)?,? y [A-ZÁÉÍÓÚÑ]", autores) or re.search(r"[A-Z]\.,? y [A-ZÁÉÍÓÚÑ][\w-]+, [A-Z]\.", autores):
        out.append(("MENOR", f"Entre autores APA 7 usa «, &» antes del último: «{corto}»"))
    if re.search(r"\b(?:doi:|DOI:|dx\.doi\.org|http://doi\.org)", r):
        out.append(("IMPORTANTE", f"DOI con formato viejo: escribilo como https://doi.org/10.xxxx. «{corto}»"))
    if re.search(r"https://doi\.org/\S+", r) and re.search(r"https?://(?!doi\.org)\S+", r):
        out.append(("MENOR", f"Tiene DOI y además otra URL: con DOI no se pone URL. «{corto}»"))
    if re.search(r"\brecuperado (?:de|el)\b|\bretrieved from\b", r, re.I) and not re.search(r"recuperado el \d", r, re.I):
        out.append(("MENOR", f"«Recuperado de» ya no se usa en APA 7 (solo con fecha de consulta en páginas que cambian). «{corto}»"))
    if re.search(r"https?://\S+\.$", r):
        out.append(("MENOR", f"Punto final después de la URL o el DOI: quitalo. «{corto}»"))
    elif not re.search(r"https?://\S+$", r) and not r.endswith((".", ".*", ")")):
        out.append(("MENOR", f"La referencia no termina en punto. «{corto}»"))
    if ARTICULO.search(r):
        if re.search(r"\bpp?\. \d", r) and not re.search(r"\bEn\b", r):
            out.append(("MENOR", f"En artículos de revista las páginas van sin «pp.»: «{corto}»"))
        if re.search(r"\d-\d", r.split("http")[0]):
            out.append(("MENOR", f"Rango de páginas con guion (-): usá la raya corta (–). «{corto}»"))
    if es_md and "*" not in r and not re.search(r"\[[^\]]*(?:datos|software|video|podcast|post)", r, re.I):
        out.append(("IMPORTANTE", f"Sin cursiva: va en cursiva el libro, informe, página web o la revista y su volumen. «{corto}»"))
    titulo = r[FECHA.search(r).end():].strip() if FECHA.search(r) else ""
    frase = re.sub(r"\*[^*]*\*", "", titulo.split(". ")[0])
    largas = re.findall(r"\b\w{4,}", frase)[1:]
    mayus = [w for w in largas if w[0].isupper()]
    if len(mayus) >= 4 and len(mayus) / max(len(largas), 1) > 0.6:
        out.append(("MENOR", f"Título del artículo o capítulo con Muchas Mayúsculas: APA usa minúscula oracional. «{corto}»"))
    return out


def revisar(refs, H, es_md=True):
    for ref in refs:
        for sev, msg in revisar_una(ref, es_md):
            H[sev].append(msg)


if __name__ == "__main__":
    from revisar import read_docx, read_md, split_sections
    ruta = sys.argv[1]
    md = not ruta.lower().endswith(".docx")
    _, refs = split_sections(read_md(ruta) if md else read_docx(ruta))
    H = {"CRÍTICO": [], "IMPORTANTE": [], "MENOR": []}
    revisar(refs, H, md)
    for sev, hs in H.items():
        for h in hs:
            print(f"[{sev}] {h}")
    print(f"{len(refs)} referencias revisadas.")
