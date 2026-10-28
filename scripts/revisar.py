#!/usr/bin/env python3
"""Revisa un trabajo (.md o .docx) y reporta problemas con severidad.

Comprueba, con código y no "a ojo":
  - citas en el texto sin referencia y referencias que nadie cita (APA 7)
  - años que no coinciden y apellidos casi iguales entre cita y referencia
  - marcadores pendientes: [COMPLETAR], [VERIFICAR], [FUENTE], TODO
  - artefactos de copiar desde una IA (\\%, **, ##)
  - frases típicas de texto generado por IA (lista en 05-redaccion/muletillas-de-ia.md)
  - oraciones demasiado largas y extensión por sección
  - (opcional) cobertura de una rúbrica y extensión según el peso de cada criterio

Sin dependencias. Uso:
    python3 scripts/revisar.py trabajo.md
    python3 scripts/revisar.py trabajo.docx --rubrica rubrica.md --palabras 2500
    python3 scripts/revisar.py trabajo.md -o revision.md

Código de salida 1 si hay hallazgos críticos (útil para automatizar).
"""
import argparse
import os
import re
import sys
import unicodedata
import zipfile
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
YEAR = r"(?:1[5-9]\d\d|20\d\d)[a-z]?|s\.\s?f\.?"
REF_TITLES = ("referencias", "bibliografia", "referencias bibliograficas", "fuentes consultadas")
END_TITLES = ("anexos", "anexo", "apendices", "apendice", "apéndices")
CONNECTORS = {"de", "del", "la", "las", "los", "y", "e", "&", "para", "el", "en"}
QUOTE = re.compile(r'[“"«]([^”"»]+?)[”"»]')
LOCATOR = re.compile(r"\b(p|pp|párr|parr|cap|art|inc)\.\s*\d|secci[oó]n\s|diapositiva\s\d|\d{1,2}:\d{2}", re.I)
PENDING = re.compile(r"\[(?i:COMPLETAR|VERIFICAR|FUENTE|FALTA)[^\]]*\]|\bTODO\b|\bXXX\b")
ARTIFACTS = [(r"\\%", "«\\%» (escape de Markdown/LaTeX)"), (r"\*\*", "«**» (negrita de Markdown sin convertir)"),
             (r"(^|\s)#{1,6}\s", "«#» (título de Markdown sin convertir)"), (r"\\_", "«\\_»")]
TRANSVERSAL = ("ortograf", "redacci", "formato", "apa", "presentaci", "gramat", "estilo", "referencia", "cita")

MULETILLAS = [
    "es importante destacar", "es importante mencionar", "es importante señalar", "es importante resaltar",
    "cabe destacar", "cabe mencionar", "cabe resaltar", "vale la pena mencionar", "en el mundo actual",
    "hoy en día", "en un mundo cada vez más", "en la era digital", "juega un papel crucial",
    "juega un papel fundamental", "desempeña un papel crucial", "de suma importancia", "sin lugar a dudas",
    "no cabe duda", "en conclusión, se puede decir", "a lo largo de la historia", "desde tiempos inmemoriales",
    "un amplio abanico", "una amplia gama", "un sinfín de", "dicho esto", "sumergirse", "adentrarse en",
    "aprovechar al máximo", "a medida que avanzamos", "en el vertiginoso", "el tapiz", "la intersección entre",
    "innegable", "revolucionario", "holístico", "sinergia",
]


# ---------------------------------------------------------------- utilidades
def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9& ]", " ", s).strip()


def words(s):
    return len(re.findall(r"\w+", s))


def lev(a, b):
    if abs(len(a) - len(b)) > 2:
        return 3
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def initials(name):
    return "".join(w[0] for w in name.split() if w[:1].isupper())


def year_of(s):
    m = re.search(YEAR, s)
    return norm(m.group(0)).replace(" ", "") if m else ""


# ---------------------------------------------------------------- lectura
def read_md(path):
    text = open(path, encoding="utf-8").read()
    blocks, buf = [], []
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            blocks.append(("meta", 0, text[3:end]))  # portada: autores, curso, docente…
            text = text[end + 4:]

    def flush():
        if buf:
            blocks.append(("p", 0, " ".join(buf)))
            buf.clear()

    in_refs = False
    for line in text.splitlines():
        s = line.strip()
        m = re.match(r"^(#{1,5})\s+(.*)$", s)
        if m:
            flush()
            blocks.append(("h", len(m.group(1)), m.group(2).strip()))
            in_refs = norm(m.group(2)) in REF_TITLES
        elif in_refs and s:
            blocks.append(("p", 0, s))  # en Referencias cada línea es una entrada
        elif not s or s.startswith("|---") or re.match(r"^\|?\s*:?-{3,}", s):
            flush()
        elif s.startswith(("- ", "* ", "> ")) or re.match(r"^\d+[.)]\s", s) or s.startswith("|"):
            flush()
            blocks.append(("p", 0, re.sub(r"^([-*>]|\d+[.)])\s+", "", s)))
        else:
            buf.append(s)
    flush()
    return blocks


def read_docx(path):
    z = zipfile.ZipFile(path)
    root = ET.fromstring(z.read("word/document.xml"))
    blocks = []
    for p in root.iter(W + "p"):
        style = p.find(f"{W}pPr/{W}pStyle")
        sid = style.get(W + "val") if style is not None else ""
        text = "".join(t.text or "" for t in p.iter(W + "t")).strip()
        if not text or sid in ("Portada",):
            continue
        m = re.search(r"(?:Heading|Ttulo|Titulo|Title)(\d)", sid or "", re.I)
        if m:
            level = int(m.group(1))
            if level >= 4 and "." in text:  # título en línea (APA 4–5)
                head, _, rest = text.partition(".")
                blocks.append(("h", level, head))
                if rest.strip():
                    blocks.append(("p", 0, rest.strip()))
                continue
            blocks.append(("h", level, text))
        else:
            blocks.append(("p", 0, text))
    return blocks


# ---------------------------------------------------------------- análisis
def split_sections(blocks):
    """Devuelve [(titulo, nivel, [parrafos])], referencias, anexos."""
    sections, refs, mode = [], [], "body"
    cur = ["Introducción", 0, []]
    for kind, level, text in blocks:
        if kind == "meta":
            continue
        if kind == "h":
            t = norm(text)
            if t in REF_TITLES:
                mode = "refs"
                continue
            if mode == "refs" and level == 1 and t not in REF_TITLES:
                mode = "end" if any(t.startswith(e) for e in END_TITLES) else "body"
            if any(t.startswith(e) for e in END_TITLES) and level == 1:
                mode = "end"
            if mode == "body":
                if cur[2] or cur[0] != "Introducción":
                    sections.append(tuple(cur))
                cur = [text, level, []]
            continue
        if mode == "body":
            cur[2].append(text)
        elif mode == "refs":
            refs.append(text)
    sections.append(tuple(cur))
    return [s for s in sections if s[2] or s[1]], refs


def parse_refs(refs):
    out = []
    for r in refs:
        m = re.match(r"^(.*?)\s*\((%s)" % YEAR.replace("(?:", "(?:"), r)
        if not m:  # fecha fuera de formato APA, p. ej. "(6 de marzo de 2024)"
            m2 = re.search(r"\(([^)]*?)(%s)\)?" % YEAR, r)
            authors = r[:m2.start()] if m2 else r.split(".")[0]
            year = year_of(m2.group(2)) if m2 else ""
        else:
            authors, year = m.group(1), year_of(m.group(2))
        authors = authors.strip().rstrip(".")
        lead = re.split(r",|\s&\s|\sy\s", authors)[0].strip()
        out.append({"texto": r, "lead": lead, "year": year, "autores": authors, "citada": False})
    return out


PAREN = re.compile(r"\(([^()]*?(?:%s)[^()]*)\)" % YEAR)
NARR = re.compile(r"((?:[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚÑáéíóúñü'’-]*\.?(?:\s+|$))(?:(?:[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚÑáéíóúñü'’-]*|de|del|la|las|los|y|e|&|et al\.)\s+)*)\((%s)[^)]*\)" % YEAR)


def parse_cites(sections):
    cites, aliases = [], {}
    for title, _, paras in sections:
        for p in paras:
            for m in PAREN.finditer(p):
                inner = m.group(1)
                inner = re.sub(r"como se cit[oó] en\s*", "", inner)
                for part in inner.split(";"):
                    part = part.strip()
                    ym = re.search(r",?\s*(%s)" % YEAR, part)
                    if not ym:
                        continue
                    who = part[:ym.start()].strip(" ,")
                    if not who or re.fullmatch(r"[\d\s,.\-–]+", who):
                        continue  # "(2020)" narrativo: lo toma NARR
                    al = re.search(r"\[([^\]]+)\]", who)
                    if al:
                        aliases[norm(al.group(1))] = norm(who[:al.start()])
                        who = who[:al.start()].strip()
                    cites.append({"lead": lead_of(who), "year": year_of(ym.group(1)), "texto": part, "seccion": title})
            for m in NARR.finditer(p):
                who = m.group(1).strip()
                toks = who.split()
                while toks and (toks[0].lower() in CONNECTORS or toks[0] in ("Según", "Como", "Para", "En", "Por", "Sin", "Así", "Además")):
                    toks = toks[1:]
                who = " ".join(toks)
                if not who:
                    continue
                cites.append({"lead": lead_of(who), "year": year_of(m.group(2)), "texto": f"{who} ({m.group(2)})", "seccion": title})
    return cites, aliases


def lead_of(who):
    who = re.sub(r"\bet al\.?", "", who).strip(" ,")
    return re.split(r",|\s&\s|\sy\s", who)[0].strip()


def match(cite, ref, aliases):
    c, r = norm(cite["lead"]), norm(ref["lead"])
    if not c or not r:
        return False
    c = aliases.get(c, c)
    if c == r or r.startswith(c + " ") or c.startswith(r + " ") or r.split()[0] == c.split()[0] \
            or (len(c.split()) == 1 and c in r.split()) or (len(r.split()) == 1 and r in c.split()):
        return True
    return c.upper().replace(" ", "") == initials(ref["autores"]).upper() and len(c) >= 2


def secciones_exigidas(blocks, extra=None):
    req = list(extra or [])
    for kind, _, text in blocks:
        if kind == "meta":
            m = re.search(r"^secciones:\s*\[(.*?)\]", text, re.M)
            if m:
                req += [x.strip().strip('"\'') for x in m.group(1).split(",") if x.strip()]
            else:
                bloque = re.search(r"^secciones:\s*\n((?:\s*-\s*.+\n?)+)", text, re.M)
                if bloque:
                    req += [x.strip().lstrip("-").strip().strip('"\'') for x in bloque.group(1).splitlines() if x.strip()]
    return req


def review(blocks, rubrica=None, palabras=None, es_md=False, secciones=None):
    sections, refs_raw = split_sections(blocks)
    refs = parse_refs(refs_raw)
    cites, aliases = parse_cites(sections)
    H = {"CRÍTICO": [], "IMPORTANTE": [], "MENOR": []}

    # citas ↔ referencias
    vistos = set()
    for c in cites:
        key = (norm(c["lead"]), c["year"])
        if key in vistos:
            continue
        vistos.add(key)
        same_year = [r for r in refs if match(c, r, aliases) and r["year"] == c["year"]]
        if same_year:
            for r in same_year:
                r["citada"] = True
            continue
        other_year = [r for r in refs if match(c, r, aliases)]
        if other_year:
            for r in other_year:
                r["citada"] = True
            H["IMPORTANTE"].append(f"Año distinto: en el texto «{c['texto']}» ({c['seccion']}), en referencias {', '.join(r['year'] or '?' for r in other_year)}.")
            continue
        near = [r for r in refs if lev(norm(c["lead"]), norm(r["lead"])) <= 2 and r["year"] == c["year"]]
        if near:
            for r in near:
                r["citada"] = True
            H["MENOR"].append(f"Apellido casi igual: «{c['lead']}» en el texto vs «{near[0]['lead']}» en referencias. Unificar.")
            continue
        H["CRÍTICO"].append(f"Cita sin referencia: «{c['texto']}» ({c['seccion']}).")
    for r in refs:
        if not r["citada"]:
            H["IMPORTANTE"].append(f"Referencia sin cita en el texto: «{r['texto'][:110]}…»")
    leads = [norm(r["lead"]) for r in refs]
    if leads and leads != sorted(leads):
        H["IMPORTANTE"].append("La lista de referencias no está en orden alfabético.")
    for r in refs:
        if re.search(r"\(\d{1,2} de [a-z]+ de \d{4}\)", r["texto"]):
            H["IMPORTANTE"].append(f"Fecha en formato no APA (usar «(2024, 6 de marzo)»): «{r['texto'][:80]}…»")
        if not r["year"]:
            H["IMPORTANTE"].append(f"Referencia sin año reconocible: «{r['texto'][:80]}…»")

    # pendientes, artefactos, muletillas, oraciones
    body_text = []
    mul_count = {}
    quoted_words = [0]
    long_sent = 0
    for title, _, paras in sections:
        for p in paras:
            body_text.append(p)
            for m in PENDING.finditer(p):
                H["CRÍTICO"].append(f"Pendiente sin resolver «{m.group(0)}» en «{title}».")
            for pat, desc in (ARTIFACTS[:1] if es_md else ARTIFACTS):
                if re.search(pat, p):
                    H["IMPORTANTE"].append(f"Artefacto {desc} en «{title}».")
            for q in QUOTE.finditer(p):
                qw = words(q.group(1))
                if qw < 4:
                    continue  # término entre comillas, no cita
                quoted_words[0] += qw
                antes = re.split(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÑ¿¡])", p[:q.start()])[-1]  # misma oración, antes de la cita
                despues = p[q.end():q.end() + 90]
                cierre = despues.find(")")
                despues = despues[:cierre + 1] if cierre != -1 else despues
                if not (LOCATOR.search(antes) or LOCATOR.search(despues)):
                    H["IMPORTANTE"].append(f"Cita textual sin página o localizador en «{title}»: «{q.group(1)[:60]}…» → agregar (p. X) o (párr. X).")
                if qw >= 40:
                    H["IMPORTANTE"].append(f"Cita textual de {qw} palabras entre comillas en «{title}»: con 40 o más va en bloque, sin comillas.")
            if not re.search(r"m[eé]todo|metodolog|resultado|resumen|abstract|objetivo", norm(title)):
                for s in re.split(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÑ¿¡])", p):
                    dato = re.search(r"\d+(?:[.,]\d+)?\s?%|\b\d{1,3}(?:[ .]\d{3})+\b|\b\d+[.,]\d+\b|\b(?!1[5-9]\d\d\b|20\d\d\b)\d{3,}\b", s)
                    citado = re.search(r"\((?:[^()]*?)(?:%s)" % YEAR, s) or NARR.search(s)
                    propio = re.search(r"encuesta|entrevista|muestra|n\s?=|tabla \d|figura \d|anexo", s, re.I)
                    if dato and not citado and not propio:
                        H["IMPORTANTE"].append(f"Dato sin cita en «{title}»: «{s[:90]}…» → agregar la fuente o quitar el dato.")
            low = " " + p.lower() + " "
            for mm in MULETILLAS:
                n = len(re.findall(r"(?<!\w)" + re.escape(mm) + r"(?!\w)", low))
                if n:
                    mul_count[mm] = mul_count.get(mm, 0) + n
            for s in re.split(r"(?<=[.!?])\s+", p):
                if words(s) > 40:
                    long_sent += 1
    for kind, _, text in blocks:
        if kind == "meta":
            for m in PENDING.finditer(text):
                H["CRÍTICO"].append(f"Pendiente sin resolver «{m.group(0)}» en la portada (encabezado del archivo).")
    for r in refs_raw:
        for m in PENDING.finditer(r):
            H["CRÍTICO"].append(f"Pendiente sin resolver «{m.group(0)}» en Referencias.")
    total = sum(words(p) for p in body_text)
    if mul_count:
        top = sorted(mul_count.items(), key=lambda x: -x[1])
        dens = sum(mul_count.values()) / max(total, 1) * 1000
        sev = "IMPORTANTE" if dens > 4 else "MENOR"
        H[sev].append(f"Frases típicas de IA ({dens:.1f} por cada 1000 palabras): " +
                      ", ".join(f"«{k}» ×{v}" for k, v in top[:12]) + ". Ver 05-redaccion/muletillas-de-ia.md.")
    if total and quoted_words[0] / total > 0.2:
        H["MENOR"].append(f"Citas textuales = {quoted_words[0] / total:.0%} del texto: parafraseá más (ideal < 20 % en ciencias sociales).")
    if long_sent:
        H["MENOR"].append(f"{long_sent} oraciones de más de 40 palabras: partirlas.")

    # extensión por sección
    por_seccion = [(t, lv, sum(words(p) for p in ps)) for t, lv, ps in sections]

    # rúbrica
    rub_rows = []
    if rubrica:
        crits = parse_rubric(rubrica)
        tot_pts = sum(c["pts"] for c in crits) or 1
        objetivo = palabras or total
        for c in crits:
            low = norm(c["criterio"])
            if any(k in low for k in TRANSVERSAL) and not c["seccion"]:
                rub_rows.append((c, "todo el documento", None, None))
                continue
            sec = find_section(c, por_seccion)
            esperado = round(objetivo * c["pts"] / tot_pts)
            if not sec:
                H["CRÍTICO"].append(f"Criterio sin sección que lo cubra: {c['id']} «{c['criterio']}» ({c['pts']} pts).")
                rub_rows.append((c, "—", 0, esperado))
                continue
            got = sec[2]
            rub_rows.append((c, sec[0], got, esperado))
            if esperado and got < 0.6 * esperado:
                H["IMPORTANTE"].append(f"{c['id']} poco desarrollado: «{sec[0]}» tiene {got} palabras y le corresponderían ~{esperado} por su peso ({c['pts']} pts).")
    if palabras and total < 0.9 * palabras:
        H["IMPORTANTE"].append(f"Extensión corta: {total} palabras frente a {palabras} pedidas.")
    if palabras and total > 1.15 * palabras:
        H["MENOR"].append(f"Extensión larga: {total} palabras frente a {palabras} pedidas.")
    titulos = [norm(text) for kind, _, text in blocks if kind == "h"]
    for s in secciones_exigidas(blocks, secciones):
        clave = norm(s)
        if not any(clave in tt or tt in clave for tt in titulos if tt):
            H["CRÍTICO"].append(f"Falta la sección exigida «{s}».")
    stats = {"palabras": total, "citas": len(cites), "referencias": len(refs), "secciones": por_seccion}
    return H, stats, rub_rows


def rubric_lines(path):
    """Filas de la rúbrica como listas de celdas, desde Markdown o desde la primera tabla de un .docx."""
    if path.lower().endswith(".docx"):
        root = ET.fromstring(zipfile.ZipFile(path).read("word/document.xml"))
        for tbl in root.iter(W + "tbl"):
            rows = []
            for tr in tbl.iter(W + "tr"):
                cells = [" ".join("".join(t.text or "" for t in p.iter(W + "t")) for p in tc.iter(W + "p")).strip()
                         for tc in tr.findall(W + "tc")]
                rows.append(cells)
            if len(rows) > 1:
                return rows
        return []
    rows = []
    for line in open(path, encoding="utf-8"):
        s = line.strip()
        if s.startswith("|"):
            rows.append([c.strip() for c in s.strip("|").split("|")])
    return rows


def parse_rubric(path):
    rows, header = [], None
    for cells in rubric_lines(path):
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        if header is None:
            header = [norm(c) for c in cells]
            continue
        d = dict(zip(header, cells))
        crit = next((d[k] for k in d if k.startswith("criterio") or k.startswith("descrip")), cells[1] if len(cells) > 1 else cells[0])
        pts_raw = next((d[k] for k in d if k.startswith(("puntaje", "puntos", "peso", "pts", "valor", "porc"))), "0")
        pts = float(re.sub(r"[^\d.]", "", pts_raw.replace(",", ".")) or 0)
        sec = next((d[k] for k in d if k.startswith(("seccion", "donde"))), "")
        cid = next((d[k] for k in d if k in ("id", "n", "no", "#")), f"C{len(rows) + 1}")
        rows.append({"id": cid or f"C{len(rows) + 1}", "criterio": crit, "pts": pts, "seccion": sec})
    return rows


def find_section(c, por_seccion):
    if c["seccion"]:
        for s in por_seccion:
            if norm(c["seccion"]) in norm(s[0]) or norm(s[0]) in norm(c["seccion"]):
                return s
    cw = {w for w in norm(c["criterio"]).split() if len(w) > 3}
    best, score = None, 0
    for s in por_seccion:
        sw = {w for w in norm(s[0]).split() if len(w) > 3}
        if not sw:
            continue
        sc = len(cw & sw) / len(sw)
        if sc > score:
            best, score = s, sc
    return best if score >= 0.5 else None


def ortografia(blocks, H, idioma="es"):
    """Revisión ortográfica y gramatical con la API pública de LanguageTool (envía el texto a un servicio externo)."""
    import json
    import urllib.parse
    import urllib.request
    texto = "\n\n".join(text for kind, _, text in blocks if kind == "p")
    trozos, actual = [], ""
    for parrafo in texto.split("\n\n"):
        if len(actual) + len(parrafo) > 15000:
            trozos.append(actual)
            actual = ""
        actual += parrafo + "\n\n"
    trozos.append(actual)
    vistos = 0
    for trozo in trozos:
        data = urllib.parse.urlencode({"text": trozo, "language": idioma}).encode()
        req = urllib.request.Request("https://api.languagetool.org/v2/check", data=data,
                                     headers={"User-Agent": "escritura-academica/1.0"})
        try:
            res = json.load(urllib.request.urlopen(req, timeout=60))
        except Exception as e:  # noqa: BLE001
            H["MENOR"].append(f"No se pudo usar LanguageTool ({type(e).__name__}).")
            return
        for m in res.get("matches", []):
            regla = m.get("rule", {}).get("issueType", "")
            frag = trozo[max(0, m["offset"] - 25):m["offset"] + m["length"] + 25].replace("\n", " ")
            sug = ", ".join(r["value"] for r in m.get("replacements", [])[:3])
            sev = "IMPORTANTE" if regla == "misspelling" else "MENOR"
            H[sev].append(f"Ortografía/gramática: {m.get('message')} «…{frag}…»" + (f" → {sug}" if sug else ""))
            vistos += 1
            if vistos >= 60:
                H["MENOR"].append("Más de 60 avisos de LanguageTool: se muestran los primeros 60.")
                return


def compare(prev_path, H):
    """Compara con un reporte anterior de revisar.py: qué se resolvió, qué es nuevo y qué sigue."""
    prev = set()
    for line in open(prev_path, encoding="utf-8"):
        if line.startswith("- ") and not line.startswith("- _"):
            prev.add(line[2:].strip())
    key = lambda s: re.sub(r"\d+([.,]\d+)?", "#", s)  # noqa: E731 — ignora cambios de cantidades
    now = {h for v in H.values() for h in v}
    pk, nk = {key(h): h for h in prev}, {key(h): h for h in now}
    resueltos = {pk[k] for k in pk.keys() - nk.keys()}
    nuevos = {nk[k] for k in nk.keys() - pk.keys()}
    siguen = pk.keys() & nk.keys()
    out = ["## Comparación con la revisión anterior", "",
           f"✅ Resueltos: {len(resueltos)} · 🆕 Nuevos: {len(nuevos)} · ⏳ Siguen: {len(siguen)}", ""]
    if resueltos:
        out += ["**Resueltos**"] + [f"- ~~{h}~~" for h in sorted(resueltos)] + [""]
    if nuevos:
        out += ["**Nuevos**"] + [f"- {h}" for h in sorted(nuevos)] + [""]
    return out


def report(path, H, stats, rub_rows, anterior=None):
    out = [f"# Revisión de `{os.path.basename(path)}`", "",
           f"Cuerpo: **{stats['palabras']} palabras** · {len(stats['secciones'])} secciones · "
           f"{stats['citas']} citas · {stats['referencias']} referencias", ""]
    n = {k: len(v) for k, v in H.items()}
    out.append(f"**Resumen:** {n['CRÍTICO']} críticos · {n['IMPORTANTE']} importantes · {n['MENOR']} menores")
    out.append("")
    for sev, icon in (("CRÍTICO", "🔴"), ("IMPORTANTE", "🟠"), ("MENOR", "🟡")):
        if H[sev]:
            out.append(f"## {icon} {sev.capitalize()}")
            out += [f"- {h}" for h in dict.fromkeys(H[sev])]
            out.append("")
    if anterior:
        out += compare(anterior, H)
    if rub_rows:
        out += ["## Rúbrica", "", "| ID | Criterio | Pts | Sección | Palabras | Esperadas |", "|---|---|---|---|---|---|"]
        for c, sec, got, exp in rub_rows:
            out.append(f"| {c['id']} | {c['criterio'][:60]} | {c['pts']:g} | {sec} | {got if got is not None else '—'} | {exp if exp is not None else '—'} |")
        out.append("")
    out += ["## Extensión por sección", "", "| Sección | Nivel | Palabras |", "|---|---|---|"]
    out += [f"| {t} | {lv} | {w} |" for t, lv, w in stats["secciones"]]
    out += ["", "> Revisión automática: confirma formato y consistencia, no la calidad del argumento ni que las fuentes digan lo que se afirma. Eso lo revisa una persona (o el agente revisor)."]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Revisión automática de un trabajo académico (.md o .docx)")
    ap.add_argument("archivo")
    ap.add_argument("--rubrica", help="Markdown con una tabla (ID | Criterio | Puntaje | Sección) o el .docx del docente (primera tabla)")
    ap.add_argument("--anterior", help="reporte .md de una revisión anterior, para ver qué se resolvió")
    ap.add_argument("--secciones", help="secciones obligatorias separadas por coma (también se leen de 'secciones:' en el encabezado)")
    ap.add_argument("--ortografia", action="store_true",
                    help="revisar ortografía con LanguageTool (ENVÍA el texto a api.languagetool.org)")
    ap.add_argument("--palabras", type=int, help="extensión pedida (palabras del cuerpo)")
    ap.add_argument("-o", "--salida", help="guardar el reporte en este archivo .md")
    a = ap.parse_args()
    es_md = not a.archivo.lower().endswith(".docx")
    blocks = read_md(a.archivo) if es_md else read_docx(a.archivo)
    extra = [s.strip() for s in a.secciones.split(",")] if a.secciones else None
    H, stats, rub = review(blocks, a.rubrica, a.palabras, es_md, extra)
    if a.ortografia:
        ortografia(blocks, H)
    rep = report(a.archivo, H, stats, rub, a.anterior)
    if a.salida:
        os.makedirs(os.path.dirname(os.path.abspath(a.salida)), exist_ok=True)
        open(a.salida, "w", encoding="utf-8").write(rep + "\n")
        print(f"Reporte: {a.salida}")
    print(rep)
    sys.exit(1 if H["CRÍTICO"] else 0)


if __name__ == "__main__":
    main()
