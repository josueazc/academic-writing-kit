#!/usr/bin/env python3
"""Matriz de lectura: ¿cada fuente respalda la frase que la cita?

Para cada oración con cita del trabajo (.md o .docx):
  1. encuentra la referencia y su DOI;
  2. descarga el resumen (OpenAlex) y, si la fuente es de acceso abierto, el texto
     completo de su página web;
  3. busca en la fuente la oración más parecida a la afirmación (también entre español
     e inglés, comparando raíces de palabras técnicas);
  4. comprueba que los NÚMEROS de la afirmación aparezcan en la fuente.

Resultado: una tabla con la evidencia encontrada y un veredicto preliminar
(probable respaldo / revisar / sin respaldo aparente / no verificable). El veredicto es
una ayuda: la IA o la persona deben leer la evidencia y confirmar cada fila.

    python3 scripts/verificar_afirmaciones.py trabajo.md -o revisiones/matriz-de-lectura.md

Sin dependencias; necesita internet.
"""
import argparse
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from revisar import (NARR, PAREN, YEAR, lead_of, match, norm, parse_refs, read_docx,  # noqa: E402
                     read_md, split_sections, year_of)

UA = "escritura-academica/1.0 (https://github.com/josueazc/escritura-academica)"
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"<>]+", re.I)
VACIAS = set("""el la los las un una unos unas de del al y o u e en con por para que se su sus es son fue
fueron como mas pero sin sobre entre desde hasta este esta estos estas ese esa eso lo le les ya muy
the of and or in on to for with by from as is are was were be been that this these those an a it its
their which also than such into can may not no""".split())
_cache = {}


def get(url, accept="application/json"):
    if url in _cache:
        return _cache[url]
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read().decode("utf-8", "replace")
    _cache[url] = data
    return data


def texto_fuente(doi):
    """Resumen de OpenAlex + texto de la página de acceso abierto (si existe)."""
    try:
        w = json.loads(get("https://api.openalex.org/works/doi:" + urllib.parse.quote(doi, safe="/")))
    except Exception:  # noqa: BLE001
        return "", "sin datos en OpenAlex"
    inv = w.get("abstract_inverted_index") or {}
    resumen = " ".join(k for _, k in sorted((p, k) for k, v in inv.items() for p in v))
    origen = "resumen" if resumen else "sin resumen"
    completo = ""
    loc = w.get("best_oa_location") or {}
    url = loc.get("landing_page_url")
    if url and (w.get("open_access") or {}).get("is_oa"):
        try:
            raw = get(url, accept="text/html")
            raw = re.sub(r"(?is)<(script|style|nav|header|footer)[^>]*>.*?</\1>", " ", raw)
            completo = html.unescape(re.sub(r"<[^>]+>", " ", raw))
            completo = re.sub(r"\s+", " ", completo)[:400000]
            if len(completo) > 3000:
                origen = "resumen + texto completo" if resumen else "texto completo"
        except Exception:  # noqa: BLE001
            pass
    return (resumen + " " + completo).strip(), origen


def raices(s):
    """Raíces de 5 letras de palabras de contenido: permiten comparar español con inglés
    en vocabulario técnico (regulación/regulation → 'regul')."""
    out = set()
    for w in norm(s).split():
        if w in VACIAS or len(w) < 4:
            continue
        out.add(w[:5])
    return out


def numeros(s):
    nums = set()
    for m in re.finditer(r"\d+(?:[.,]\d+)?", s):
        n = m.group(0).replace(",", ".")
        if re.fullmatch(r"(1[5-9]|20)\d\d", n):
            continue  # años: casi siempre son del contexto de la cita
        nums.add(n.rstrip("0").rstrip(".") if "." in n else n)
    return nums


def mejor_evidencia(afirmacion, fuente):
    claims = raices(afirmacion)
    if not claims or not fuente:
        return 0.0, ""
    mejor, frase = 0.0, ""
    for s in re.split(r"(?<=[.!?])\s+", fuente):
        if len(s) < 40 or len(s) > 800:
            continue
        r = raices(s)
        score = len(claims & r) / len(claims)
        if score > mejor:
            mejor, frase = score, s
    return mejor, frase


def oraciones_con_cita(sections):
    for title, _, paras in sections:
        for p in paras:
            for s in re.split(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÑ¿¡])", p):
                cites = []
                for m in PAREN.finditer(s):
                    for part in re.sub(r"como se cit[oó] en\s*", "", m.group(1)).split(";"):
                        ym = re.search(r",?\s*(%s)" % YEAR, part)
                        if ym and part[:ym.start()].strip(" ,"):
                            who = re.sub(r"\[[^\]]+\]", "", part[:ym.start()]).strip(" ,")
                            cites.append((lead_of(who), year_of(ym.group(1))))
                for m in NARR.finditer(s):
                    toks = [t for t in m.group(1).split() if t not in ("Según", "Como", "Para", "En", "Por")]
                    if toks:
                        cites.append((lead_of(" ".join(toks)), year_of(m.group(2))))
                if cites and not re.match(r"\*?Nota\.", s) and "Elaboración propia" not in s:
                    yield title, s, cites


def main():
    ap = argparse.ArgumentParser(description="Matriz de lectura: ¿las fuentes respaldan lo que se afirma?")
    ap.add_argument("archivo")
    ap.add_argument("-o", "--salida")
    a = ap.parse_args()
    blocks = read_md(a.archivo) if not a.archivo.lower().endswith(".docx") else read_docx(a.archivo)
    sections, refs_raw = split_sections(blocks)
    refs = parse_refs(refs_raw)
    for r in refs:
        d = DOI_RE.search(r["texto"])
        r["doi"] = d.group(0).rstrip(".,;)") if d else None
    aliases = {}
    filas, cuenta = [], {"probable respaldo": 0, "revisar": 0, "sin respaldo aparente": 0, "no verificable": 0}
    for title, oracion, cites in oraciones_con_cita(sections):
        limpia = re.sub(r"\([^()]*\d{4}[^()]*\)", "", oracion)
        for lead, year in dict.fromkeys(cites):
            ref = next((r for r in refs if match({"lead": lead}, r, aliases) and r["year"] == year), None)
            if not ref or not ref["doi"]:
                veredicto, evid, origen, faltan = "no verificable", "", "sin DOI (libro, ley, web o fuente primaria): leer y confirmar a mano", set()
            else:
                fuente, origen = texto_fuente(ref["doi"])
                score, evid = mejor_evidencia(limpia, fuente)
                faltan = {n for n in numeros(limpia) if n not in numeros(fuente)}
                # la comparación entre idiomas es aproximada: rojo solo cuando hay una señal objetiva
                if not fuente or not evid:
                    veredicto = "no verificable"
                elif faltan:
                    veredicto = "sin respaldo aparente"
                elif score >= 0.25:
                    veredicto = "probable respaldo"
                else:
                    veredicto = "revisar"
                time.sleep(0.2)
            cuenta[veredicto] += 1
            filas.append((title, oracion, f"{lead} ({year})", veredicto, origen, evid, faltan))
    iconos = {"probable respaldo": "✅", "revisar": "🟡", "sin respaldo aparente": "🔴", "no verificable": "⚪"}
    out = [f"# Matriz de lectura de `{os.path.basename(a.archivo)}`", "",
           " · ".join(f"{iconos[k]} {k}: {v}" for k, v in cuenta.items()), "",
           "Cómo usarla: leé la evidencia de cada fila. Si no respalda la afirmación, corregí la frase, cambiá la "
           "fuente o eliminá el dato. Los números de la afirmación deben aparecer en la fuente.", ""]
    for i, (title, oracion, cita, veredicto, origen, evid, faltan) in enumerate(filas, 1):
        out.append(f"### {i}. {iconos[veredicto]} {veredicto} — {cita} · {title}")
        out.append(f"- **Afirmación:** {oracion}")
        out.append(f"- **Se comparó con:** {origen}")
        if evid:
            out.append(f"- **Evidencia más cercana en la fuente:** «{evid[:500]}»")
        if faltan:
            out.append(f"- **Números que no aparecen en la fuente:** {', '.join(sorted(faltan))}")
        out.append("- **Veredicto de quien revisa:** [ ] respalda · [ ] respalda en parte · [ ] no respalda")
        out.append("")
    out.append("> Coincidencia automática por vocabulario y números: es una alerta, no una prueba. "
               "Un resumen no contiene todo el artículo; lo marcado como «revisar» exige leer la fuente.")
    rep = "\n".join(out)
    if a.salida:
        os.makedirs(os.path.dirname(os.path.abspath(a.salida)), exist_ok=True)
        open(a.salida, "w", encoding="utf-8").write(rep + "\n")
        print(f"Matriz: {a.salida}")
    print("\n".join(out[:3]))
    sys.exit(1 if cuenta["sin respaldo aparente"] else 0)


if __name__ == "__main__":
    main()
