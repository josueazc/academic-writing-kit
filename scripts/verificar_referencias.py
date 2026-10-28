#!/usr/bin/env python3
"""Verifica que las referencias de un trabajo existan de verdad.

Para cada entrada de la lista de Referencias (.md o .docx):
  - con DOI: consulta Crossref; avisa si el DOI no existe o si apunta a otro
    trabajo (título o año distintos). Es la mejor defensa contra referencias
    inventadas por una IA.
  - con URL: comprueba que la página responda (404 = enlace roto).
  - sin DOI ni URL: busca la referencia en Crossref y sugiere el DOI si la
    encuentra; si no, la marca para verificar a mano (libros y documentos
    locales a menudo no están en Crossref: eso no significa que sean falsos).

Sin dependencias. Necesita internet.
    python3 scripts/verificar_referencias.py trabajo.md
    python3 scripts/verificar_referencias.py trabajo.docx -o revisiones/referencias.md
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from revisar import norm, read_docx, read_md, split_sections  # noqa: E402

UA = "escritura-academica/1.0 (https://github.com/josueazc/academic-writing-kit)"
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"<>]+", re.I)
URL_RE = re.compile(r"https?://[^\s<>\"]+")
YEAR_RE = re.compile(r"\((\d{4})")


def http(url, accept="application/json", method="GET"):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept}, method=method)
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.status, r.read().decode("utf-8", "replace") if method == "GET" else ""


def anio_crossref(msg):
    """Año más temprano entre las fechas de Crossref (issued a veces es la fecha de registro)."""
    anios = []
    for k in ("published-print", "published-online", "published", "issued", "created"):
        parts = (msg.get(k) or {}).get("date-parts") or [[None]]
        if parts[0] and parts[0][0]:
            anios.append(int(parts[0][0]))
    return min(anios) if anios else None


def tokens(s):
    return {w for w in norm(s).split() if len(w) > 3}


def similar(a, b):
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / min(len(ta), len(tb))


def titulo_de(ref):
    m = re.search(r"\)\.\s*(.+?)(?:\.\s|\?\s|\.$|$)", ref)
    return (m.group(1) if m else ref)[:250].strip("*_ ")


def check_doi(doi, ref):
    doi = doi.rstrip(".,;)")
    try:
        _, body = http("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            # puede ser un DOI de DataCite (datasets, Zenodo): probar el resolvedor
            try:
                http("https://doi.org/" + doi, accept="text/html", method="HEAD")
                return "ok", f"DOI válido fuera de Crossref ({doi})."
            except Exception:  # noqa: BLE001
                return "critico", f"El DOI {doi} no existe. Posible referencia inventada o DOI mal copiado."
        return "aviso", f"No se pudo consultar el DOI {doi} (HTTP {e.code})."
    except Exception as e:  # noqa: BLE001
        return "aviso", f"No se pudo consultar el DOI {doi} ({e})."
    msg = json.loads(body)["message"]
    real_title = (msg.get("title") or [""])[0]
    real_year = anio_crossref(msg)
    sim = similar(titulo_de(ref), real_title)
    ym = YEAR_RE.search(ref)
    year_ok = not ym or not real_year or abs(int(ym.group(1)) - int(real_year)) <= 1
    if sim < 0.35:
        return "importante", f"El DOI {doi} existe pero corresponde a otro trabajo: «{real_title}» ({real_year})."
    if not year_ok:
        return "importante", f"Año distinto: la referencia dice {ym.group(1)} y el DOI {doi} es de {real_year}."
    return "ok", f"DOI verificado: «{real_title[:80]}»."


def check_url(url):
    url = url.rstrip(".,;)")
    try:
        status, _ = http(url, accept="text/html,*/*", method="HEAD")
        return "ok", f"URL responde ({status})."
    except urllib.error.HTTPError as e:
        if e.code in (403, 405, 429, 503):
            try:
                status, _ = http(url, accept="text/html,*/*")
                return "ok", f"URL responde ({status})."
            except urllib.error.HTTPError as e2:
                if e2.code == 404:
                    return "importante", f"Enlace roto (404): {url}"
                return "aviso", f"El sitio no permite comprobarlo automáticamente (HTTP {e2.code}): {url}"
            except Exception:  # noqa: BLE001
                return "aviso", f"No se pudo comprobar: {url}"
        if e.code in (404, 410):
            return "importante", f"Enlace roto ({e.code}): {url}"
        return "aviso", f"HTTP {e.code} en {url}"
    except Exception as e:  # noqa: BLE001
        return "aviso", f"No se pudo abrir {url} ({type(e).__name__})."


def search_crossref(ref):
    q = urllib.parse.urlencode({"query.bibliographic": ref[:300], "rows": "1"})
    try:
        _, body = http("https://api.crossref.org/works?" + q)
    except Exception:  # noqa: BLE001
        return "aviso", "No se pudo consultar Crossref."
    items = json.loads(body)["message"]["items"]
    if items:
        it = items[0]
        title = (it.get("title") or [""])[0]
        apellidos = {norm(x.get("family", "")) for x in it.get("author", [])}
        primer = norm(re.split(r"[,(]", ref)[0])
        anio = anio_crossref(it)
        ym = YEAR_RE.search(ref)
        mismo_autor = any(a and a.split()[0] in primer.split() for a in apellidos)
        mismo_anio = not ym or (anio and abs(int(ym.group(1)) - int(anio)) <= 1)
        if similar(titulo_de(ref), title) >= 0.6 and mismo_autor and mismo_anio:
            return "menor", f"Encontrada en Crossref; agregá su DOI: https://doi.org/{it['DOI']}"
    return "manual", "No está en Crossref (normal en libros, leyes, sitios web y documentos locales): verificala a mano."


def main():
    ap = argparse.ArgumentParser(description="Verifica que las referencias existan (DOI, URL, Crossref)")
    ap.add_argument("archivo")
    ap.add_argument("-o", "--salida")
    a = ap.parse_args()
    blocks = read_md(a.archivo) if not a.archivo.lower().endswith(".docx") else read_docx(a.archivo)
    _, refs = split_sections(blocks)
    if not refs:
        print("No se encontró una sección «Referencias».")
        sys.exit(2)
    out = {"critico": [], "importante": [], "menor": [], "manual": [], "aviso": [], "ok": []}
    for ref in refs:
        if not re.search(r"\(\d{4}|\(s\.\s?f\.|\(en prensa", ref):
            continue  # continuación de la entrada anterior (p. ej., URL en otra línea)
        doi = DOI_RE.search(ref)
        if doi:
            sev, msg = check_doi(doi.group(0), ref)
        else:
            url = URL_RE.search(ref)
            sev, msg = check_url(url.group(0)) if url else search_crossref(ref)
        out[sev].append((ref, msg))
        time.sleep(0.3)  # cortesía con las APIs
    labels = [("critico", "🔴 Crítico (probablemente no existe)"), ("importante", "🟠 Importante"),
              ("menor", "🟡 Menor"), ("manual", "⚪ Verificar a mano"), ("aviso", "ℹ️ No comprobables automáticamente"),
              ("ok", "✅ Verificadas")]
    total = sum(len(v) for v in out.values())
    lines = [f"# Verificación de referencias de `{os.path.basename(a.archivo)}`", "",
             f"{total} referencias · {len(out['ok'])} verificadas · {len(out['critico'])} críticas · "
             f"{len(out['importante'])} importantes · {len(out['manual'])} a mano", ""]
    for k, title in labels:
        if out[k]:
            lines.append(f"## {title}")
            for ref, msg in out[k]:
                lines.append(f"- {msg}\n  - _{ref[:140]}{'…' if len(ref) > 140 else ''}_")
            lines.append("")
    lines.append("> Que una referencia exista no prueba que diga lo que el texto afirma: leé la fuente.")
    rep = "\n".join(lines)
    if a.salida:
        os.makedirs(os.path.dirname(os.path.abspath(a.salida)), exist_ok=True)
        open(a.salida, "w", encoding="utf-8").write(rep + "\n")
    print(rep)
    sys.exit(1 if out["critico"] else 0)


if __name__ == "__main__":
    main()
