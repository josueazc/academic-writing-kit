#!/usr/bin/env python3
"""Chequeos de coherencia que revisar.py aplica sobre la estructura del trabajo.

Todo es heurístico: da pistas y una matriz para que la persona o el agente revisor
emita el veredicto. Un script no puede decidir si un texto "analiza" o si un método
es adecuado; sí puede señalar dónde mirar.

  - objetivos: cantidad, verbos repetidos, verbos no medibles, nivel de Bloom de cada verbo
  - cobertura: cada objetivo específico aparece en la metodología y en las conclusiones
  - conclusiones: citas, autores o cifras que aparecen por primera vez ahí
  - análisis frente a descripción: densidad de conectores de análisis cuando el verbo pide Analizar o más
  - títulos: saltos de nivel (del 1 al 3) y subsecciones únicas

Uso directo: python3 scripts/coherencia.py trabajo.md
"""
import re
import sys

from revisar import NARR, PAREN, YEAR, lead_of, norm, read_docx, read_md, words  # noqa: F401

# Nivel de Bloom de cada verbo (06-bloom/taxonomia-bloom.md y 04-secciones/objetivos.md).
BLOOM = {
    1: "definir enumerar nombrar reconocer listar citar recordar",
    2: "explicar describir resumir parafrasear ejemplificar interpretar caracterizar identificar reconocer exponer "
       "conocer comprender entender saber aprender",
    3: "aplicar calcular demostrar ejecutar implementar resolver utilizar usar emplear",
    4: "analizar comparar contrastar clasificar diferenciar examinar organizar relacionar categorizar inferir "
       "diagnosticar distinguir explorar",
    5: "evaluar valorar justificar argumentar criticar verificar validar determinar priorizar juzgar medir estimar",
    6: "disenar desarrollar elaborar formular proponer planificar construir producir crear generar",
}
NIVEL = {v: n for n, vs in BLOOM.items() for v in vs.split()}
NOMBRE = {1: "Recordar", 2: "Comprender", 3: "Aplicar", 4: "Analizar", 5: "Evaluar", 6: "Crear"}
NO_MEDIBLES = {"conocer", "comprender", "entender", "saber", "aprender", "concientizar", "mejorar", "investigar", "hacer"}
# Conectores que suelen marcar análisis (relacionar, contrastar, explicar causas, inferir).
ANALISIS = ["porque", "por lo tanto", "por ello", "en consecuencia", "de modo que", "lo que implica", "lo cual",
            "sin embargo", "en cambio", "a diferencia de", "mientras que", "frente a", "no obstante", "aunque",
            "se debe a", "debido a", "esto sugiere", "esto indica", "esto explica", "lo que explica", "evidencia",
            "en contraste", "por el contrario", "a su vez", "es decir", "de ahí", "por esta razón", "dado que",
            "implica", "permite inferir", "se relaciona con", "depende de", "condiciona"]
VACIAS = set("para como sobre entre desde hasta segun mediante principales principal cada estos estas este esta "
             "aquellos tiene tienen asociados asociadas segun hacia trabajo objetivo especifico general".split())


def infinitivo(texto):
    """Primer verbo en infinitivo del texto, normalizado (sin tildes)."""
    for t in norm(re.sub(r"[*_]", "", texto)).split()[:3]:
        if re.fullmatch(r"[a-z]{3,}(ar|er|ir)(se|lo|la|los|las)?", t):
            return re.sub(r"(se|lo|la|los|las)$", "", t) if t not in NIVEL else t
    return ""


def extraer_objetivos(blocks):
    """(general, [específicos]) leídos del encabezado (objetivo_general/objetivos) o del texto."""
    general, especificos = "", []
    for kind, _, text in blocks:
        if kind != "meta":
            continue
        m = re.search(r"^objetivo_general:\s*(.+)$", text, re.M)
        if m:
            general = m.group(1).strip().strip('"\'')
        lista = re.search(r"^objetivos(?:_especificos)?:\s*\n((?:\s*-\s*.+\n?)+)", text, re.M)
        if lista:
            especificos = [x.strip().lstrip("-").strip().strip('"\'') for x in lista.group(1).splitlines() if x.strip()]
    if general and especificos:
        return general, especificos

    modo = None  # "general" | "especificos"
    for kind, _, text in blocks:
        if kind == "meta":
            continue
        t = norm(text)
        if kind == "h" and words(text) > 12:
            kind = "p"  # párrafo con estilo de título por error
        if kind == "h":
            modo = "general" if "objetivo general" in t else "especificos" if "objetivos especificos" in t else None
            continue
        limpio = re.sub(r"^\s*\d+[.)]\s*", "", re.sub(r"[*_]", "", text))
        if not general:
            m = re.search(r"objetivo general\W+(?:es\s+|consiste en\s+|ser[aá]\s+)?(.+)", limpio, re.I)
            if m and infinitivo(m.group(1)):
                general = m.group(1).split(". ")[0].strip()
            elif modo == "general" and infinitivo(limpio):
                general = limpio.strip()
        if modo == "especificos":
            if infinitivo(limpio):
                especificos.append(limpio.strip())
            elif especificos:
                modo = None
            continue
        if re.search(r"objetivos espec[ií]ficos", limpio, re.I) and not especificos:
            modo = "especificos"
    return general, especificos


def agrupar(blocks):
    """Secciones de nivel 1 con todo su contenido (subtítulos incluidos): [(titulo, [textos])]."""
    grupos, actual = [], None
    for kind, level, text in blocks:
        if kind == "meta":
            continue
        if kind == "h" and level <= 1:
            actual = [text, []]
            grupos.append(actual)
        elif actual is not None:
            actual[1].append(text)
    return grupos


def buscar(grupos, *patrones):
    return [g for g in grupos if any(re.search(p, norm(g[0])) for p in patrones)]


def terminos(objetivo):
    return {w for w in norm(re.sub(r"[*_]", "", objetivo)).split()[1:] if len(w) > 4 and w not in VACIAS}


def aparece(n, objetivo, textos):
    """¿El objetivo n se trata en estos textos? Por mención explícita o por sus términos clave."""
    todo = norm(" ".join(textos))
    if re.search(r"objetivo (especifico )?%d\b|oe ?%d\b" % (n, n), todo):
        return True
    clave = terminos(objetivo)
    verbo = infinitivo(objetivo)
    if not clave:
        return False
    hallados = sum(1 for w in clave if w[:6] in todo)
    return hallados / len(clave) >= 0.5 or (verbo and verbo[:5] in todo and hallados / len(clave) >= 0.3)


def citas_de(textos):
    out = set()
    for p in textos:
        for m in PAREN.finditer(p):
            for part in m.group(1).split(";"):
                ym = re.search(r"(%s)" % YEAR, part)
                who = part[:ym.start()].strip(" ,") if ym else ""
                if who and not re.fullmatch(r"[\d\s,.\-–]+", who):
                    out.add((norm(lead_of(who)).split(" ")[0], norm(ym.group(1)).replace(" ", "")))
        for m in NARR.finditer(p):
            who = m.group(1).split()
            while who and who[0] in ("Según", "Como", "Para", "En", "Por", "Además"):
                who = who[1:]
            if who:
                out.add((norm(lead_of(" ".join(who))).split(" ")[0], norm(m.group(2)).replace(" ", "")))
    return out


def cifras_de(texto):
    return {re.sub(r"\s", "", m.group(0)).replace(",", ".") for m in
            re.finditer(r"\d+(?:[.,]\d+)?\s?%|\b\d+[.,]\d+\b|\b(?!1[5-9]\d\d\b|20\d\d\b)\d{2,}\b", texto)}


def densidad_analisis(textos):
    texto = " " + " ".join(textos).lower() + " "
    n = sum(len(re.findall(r"(?<!\w)" + re.escape(c) + r"(?!\w)", texto)) for c in ANALISIS)
    return n / max(words(texto), 1) * 100


def revisar_titulos(blocks, H):
    previo = 0
    hijos = {}
    padre = None
    for kind, level, text in blocks:
        if kind != "h":
            continue
        if words(text) > 25:
            H["IMPORTANTE"].append(f"Párrafo con estilo de título: «{text[:60]}…» (va como texto normal; si no, entra al índice).")
            continue
        if previo and level > previo + 1:
            H["IMPORTANTE"].append(f"Salto de nivel de título: «{text}» es nivel {level} y el anterior era nivel {previo} (no saltes niveles).")
        if level == 1:
            padre = text
        elif level == 2 and padre:
            hijos.setdefault(padre, []).append(text)
        previo = level
    for p, hs in hijos.items():
        if len(hs) == 1:
            H["MENOR"].append(f"«{p}» tiene un solo subtítulo («{hs[0]}»): APA pide al menos dos o ninguno.")


def revisar(blocks, H):
    """Agrega hallazgos a H y devuelve la matriz de coherencia por objetivo."""
    revisar_titulos(blocks, H)
    general, esp = extraer_objetivos(blocks)
    matriz = []
    if not general and not esp:
        if any(kind == "h" and "objetivo" in norm(t) for kind, _, t in blocks):
            H["IMPORTANTE"].append("Hay una sección de objetivos pero no se reconocieron los verbos: escribí cada objetivo empezando con un verbo en infinitivo.")
        return matriz, None

    vg = infinitivo(general)
    ng = NIVEL.get(vg)
    if general and not vg:
        H["IMPORTANTE"].append(f"El objetivo general no empieza con un verbo en infinitivo: «{general[:80]}…».")
    if vg in NO_MEDIBLES:
        H["IMPORTANTE"].append(f"Objetivo general con verbo no medible «{vg}»: usá uno de Analizar, Evaluar o Crear.")
    if esp and not 3 <= len(esp) <= 5:
        H["MENOR"].append(f"Hay {len(esp)} objetivos específicos; lo habitual son 3–5.")
    verbos = [infinitivo(o) for o in esp]
    for v in {v for v in verbos if v and verbos.count(v) > 1}:
        H["IMPORTANTE"].append(f"Verbo repetido entre objetivos específicos: «{v}».")
    if vg and vg in verbos:
        H["MENOR"].append(f"Un objetivo específico repite el verbo del general («{vg}»).")

    grupos = agrupar(blocks)
    metodo = [t for g in buscar(grupos, r"metod", r"procedimiento") for t in [g[0]] + g[1]]
    concl = buscar(grupos, r"^conclusi")
    concl_txt = [t for g in concl for t in [g[0]] + g[1]]
    for i, (o, v) in enumerate(zip(esp, verbos), 1):
        n = NIVEL.get(v)
        if v in NO_MEDIBLES:
            H["IMPORTANTE"].append(f"Objetivo específico {i} con verbo no medible «{v}».")
        if n and ng and n > ng:
            H["MENOR"].append(f"El objetivo específico {i} («{v}», {NOMBRE[n]}) está por encima del general («{vg}», {NOMBRE[ng]}): revisá que ninguno supere al general.")
        en_met = aparece(i, o, metodo) if metodo else None
        en_con = aparece(i, o, concl_txt) if concl_txt else None
        if metodo and not en_met:
            H["IMPORTANTE"].append(f"El objetivo específico {i} no aparece en la metodología: falta su procedimiento.")
        if concl_txt and not en_con:
            H["IMPORTANTE"].append(f"El objetivo específico {i} no tiene conclusión reconocible: organizalas por objetivo.")
        matriz.append({"n": i, "objetivo": o, "verbo": v or "—", "nivel": NOMBRE.get(n, "?"),
                       "metodo": en_met, "conclusion": en_con})

    # conclusiones: información que aparece por primera vez
    if concl:
        resto = [t for g in grupos if g not in concl and not re.search(r"^(referencias|bibliograf|anexo|apendice|recomendac)", norm(g[0]))
                 for t in [g[0]] + g[1]]
        previas = citas_de(resto)
        for autor, anio in sorted(citas_de(concl_txt) - previas):
            H["IMPORTANTE"].append(f"Cita nueva en Conclusiones: «{autor.capitalize()}, {anio}» no aparece antes en el trabajo (las conclusiones no traen fuentes nuevas).")
        nuevas = cifras_de(" ".join(concl_txt)) - cifras_de(" ".join(resto))
        if nuevas:
            H["IMPORTANTE"].append("Cifras que aparecen por primera vez en Conclusiones: " + ", ".join(sorted(nuevas)[:8]) +
                                   ". Una conclusión resume resultados ya presentados, no agrega datos.")

    # análisis frente a descripción
    pista = None
    if ng and ng >= 4:
        cuerpo = [t for g in grupos if not re.search(r"^(resumen|abstract|introduc|objetivo|metod|referencias|bibliograf|anexo|apendice|recomendac)", norm(g[0]))
                  for t in g[1]]
        if words(" ".join(cuerpo)) >= 300:
            pista = densidad_analisis(cuerpo)
            if pista < 0.6:
                H["IMPORTANTE"].append(f"El objetivo general pide «{vg}» ({NOMBRE[ng]}) pero el desarrollo tiene pocos conectores de análisis "
                                       f"({pista:.1f} por cada 100 palabras): puede estar describiendo en vez de analizar. Revisá cada párrafo con 06-bloom.")
    return matriz, {"general": general, "verbo_general": vg, "nivel_general": NOMBRE.get(ng, "?"), "analisis": pista}


def reporte_matriz(matriz, info):
    if not info:
        return []
    out = ["## Matriz de coherencia por objetivo", "",
           f"Objetivo general: «{info['general'][:140]}» · verbo **{info['verbo_general'] or '—'}** ({info['nivel_general']})", ""]
    if info.get("analisis") is not None:
        out += [f"Conectores de análisis en el desarrollo: {info['analisis']:.1f} por cada 100 palabras (menos de 0.6 sugiere texto descriptivo).", ""]
    si = lambda x: "—" if x is None else ("sí" if x else "**no**")  # noqa: E731
    out += ["| # | Objetivo específico | Verbo | Nivel | En metodología | En conclusiones |", "|---|---|---|---|---|---|"]
    out += [f"| {m['n']} | {m['objetivo'][:70]} | {m['verbo']} | {m['nivel']} | {si(m['metodo'])} | {si(m['conclusion'])} |" for m in matriz]
    out += ["", "> Pistas automáticas. El veredicto (¿el método sirve para ese verbo?, ¿la conclusión responde y sale del desarrollo?, "
                "¿los específicos cubren el general?) lo completa el revisor: `08-agentes/prompts/5-revisor.md`.", ""]
    return out


if __name__ == "__main__":
    ruta = sys.argv[1]
    bl = read_docx(ruta) if ruta.lower().endswith(".docx") else read_md(ruta)
    H = {"CRÍTICO": [], "IMPORTANTE": [], "MENOR": []}
    m, info = revisar(bl, H)
    for sev, hs in H.items():
        for h in hs:
            print(f"[{sev}] {h}")
    print("\n".join(reporte_matriz(m, info)))
