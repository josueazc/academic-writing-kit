#!/usr/bin/env python3
"""Busca fuentes académicas reales y devuelve referencias APA 7.

Usa APIs abiertas que indexan cientos de millones de trabajos:
  - OpenAlex  (https://openalex.org)    búsqueda por tema
  - Crossref  (https://www.crossref.org) búsqueda y formato APA desde el DOI

Sin dependencias (biblioteca estándar).

Uso:
    python3 scripts/fuentes.py buscar "resistencia antimicrobiana" -n 10
    python3 scripts/fuentes.py buscar "turismo Guanacaste" --desde 2018 --idioma es
    python3 scripts/fuentes.py doi 10.1080/1369118X.2012.670661
    python3 scripts/fuentes.py buscar "participación juvenil" --formato md > fuentes.md

Cada resultado trae DOI y URL para abrirlo y verificarlo. Leer la fuente antes de citarla.
"""
import argparse
import html
import json
import sys
import urllib.parse
import urllib.request

UA = "escritura-academica/1.0 (https://github.com/josueazc/escritura-academica)"


def get(url, accept="application/json"):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


# ------------------------------------------------------------------ APA desde metadatos
def iniciales(nombre):
    partes = [p for p in nombre.replace("-", " - ").split() if p]
    out = []
    for p in partes:
        if p == "-":
            out.append("-")
        elif p[0].isalpha():
            out.append(p[0].upper() + ".")
    return " ".join(out).replace(" - ", "-")


def autor_apa(nombre_completo):
    nombre_completo = nombre_completo.strip()
    if "," in nombre_completo:
        ap, nom = [x.strip() for x in nombre_completo.split(",", 1)]
    else:
        partes = nombre_completo.split()
        if len(partes) == 1:
            return partes[0]
        ap, nom = partes[-1], " ".join(partes[:-1])
    return f"{ap}, {iniciales(nom)}"


def lista_autores(autores):
    a = [autor_apa(x) for x in autores if x]
    if not a:
        return ""
    if len(a) == 1:
        return a[0]
    if len(a) <= 20:
        return ", ".join(a[:-1]) + ", & " + a[-1]
    return ", ".join(a[:19]) + ", . . . " + a[-1]


def apa_desde_openalex(w):
    autores = [x["author"]["display_name"] for x in w.get("authorships", []) if x.get("author")]
    year = w.get("publication_year") or "s. f."
    title = (w.get("display_name") or w.get("title") or "").rstrip(".")
    src = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
    bib = w.get("biblio") or {}
    vol, num = bib.get("volume"), bib.get("issue")
    fp, lp = bib.get("first_page"), bib.get("last_page")
    doi = w.get("doi")
    url = doi or (w.get("primary_location") or {}).get("landing_page_url") or ""
    tipo = w.get("type")
    a = lista_autores(autores)
    head = f"{a} ({year}). " if a else ""
    if tipo in ("article", "review") and src:
        ref = f"{head}{title}. *{src}"
        if vol:
            ref += f", {vol}*"
            if num:
                ref += f"({num})"
        else:
            ref += "*"
        if fp:
            ref += f", {fp}" + (f"–{lp}" if lp and lp != fp else "")
        ref += "."
    else:
        ref = f"{head}*{title}*." + (f" {src}." if src else "")
    if not a:
        ref = f"*{title}*. ({year}). " + (f"{src}." if src else "")
    return (ref + (f" {url}" if url else "")).strip()


# ------------------------------------------------------------------ comandos
def buscar(q, n, desde, idioma, solo_abiertos):
    filtros = []
    if desde:
        filtros.append(f"from_publication_date:{desde}-01-01")
    if idioma:
        filtros.append(f"language:{idioma}")
    if solo_abiertos:
        filtros.append("is_oa:true")
    params = {"search": q, "per-page": str(n), "sort": "relevance_score:desc"}
    if filtros:
        params["filter"] = ",".join(filtros)
    try:
        data = json.loads(get("https://api.openalex.org/works?" + urllib.parse.urlencode(params)))
        res = []
        for w in data.get("results", []):
            res.append({
                "apa": apa_desde_openalex(w),
                "anio": w.get("publication_year"),
                "citas": w.get("cited_by_count"),
                "acceso_abierto": (w.get("open_access") or {}).get("is_oa"),
                "pdf": (w.get("open_access") or {}).get("oa_url"),
                "doi": w.get("doi"),
                "origen": "OpenAlex",
            })
        if res:
            return res
    except Exception as e:  # noqa: BLE001
        print(f"OpenAlex no respondió ({e}); probando Crossref…", file=sys.stderr)
    return buscar_crossref(q, n, desde)


def buscar_crossref(q, n, desde):
    params = {"query": q, "rows": str(n)}
    if desde:
        params["filter"] = f"from-pub-date:{desde}"
    data = json.loads(get("https://api.crossref.org/works?" + urllib.parse.urlencode(params)))
    res = []
    for it in data["message"]["items"]:
        autores = [f'{a.get("family", "")}, {a.get("given", "")}'.strip(", ") for a in it.get("author", [])]
        year = (it.get("issued", {}).get("date-parts") or [[None]])[0][0] or "s. f."
        title = (it.get("title") or [""])[0]
        src = (it.get("container-title") or [""])[0]
        doi = "https://doi.org/" + it["DOI"] if it.get("DOI") else ""
        a = lista_autores(autores)
        ref = f"{a} ({year}). {title}. " + (f"*{src}*. " if src else "") + doi
        res.append({"apa": ref.strip(), "anio": year, "citas": it.get("is-referenced-by-count"),
                    "acceso_abierto": None, "pdf": None, "doi": doi, "origen": "Crossref"})
    return res


def doi_apa(doi):
    doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "").strip()
    url = "https://doi.org/" + urllib.parse.quote(doi, safe="/")
    try:
        return html.unescape(get(url, accept="text/x-bibliography; style=apa; locale=es-ES")).strip()
    except Exception:  # noqa: BLE001
        return html.unescape(get(url, accept="text/x-bibliography; style=apa")).strip()


def main():
    ap = argparse.ArgumentParser(description="Buscar fuentes académicas y obtener referencias APA 7")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("buscar", help="buscar por tema")
    b.add_argument("consulta")
    b.add_argument("-n", type=int, default=10)
    b.add_argument("--desde", type=int, help="año mínimo de publicación")
    b.add_argument("--idioma", help="código ISO: es, en, pt…")
    b.add_argument("--abiertos", action="store_true", help="solo acceso abierto")
    b.add_argument("--formato", choices=["texto", "md", "json"], default="texto")
    d = sub.add_parser("doi", help="referencia APA desde un DOI")
    d.add_argument("doi")
    args = ap.parse_args()

    if args.cmd == "doi":
        print(doi_apa(args.doi))
        return
    res = buscar(args.consulta, args.n, args.desde, args.idioma, args.abiertos)
    if args.formato == "json":
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return
    for i, r in enumerate(res, 1):
        extra = f"citas: {r['citas']}" + (" · acceso abierto" if r["acceso_abierto"] else "")
        if args.formato == "md":
            print(f"### {i}. ({r['anio']}) — {extra}\n- Referencia APA 7: {r['apa']}\n"
                  f"- PDF abierto: {r['pdf'] or 'no'}\n- Verificado por mí: [ ]\n")
        else:
            print(f"{i}. {r['apa']}\n   [{r['origen']} · {extra}]" + (f"\n   PDF: {r['pdf']}" if r["pdf"] else "") + "\n")
    print("Revisá mayúsculas del título y cursivas: los metadatos vienen como los publicó la revista.",
          file=sys.stderr)


if __name__ == "__main__":
    main()
