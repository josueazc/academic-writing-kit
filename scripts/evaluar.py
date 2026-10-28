#!/usr/bin/env python3
"""Puntaje de 0 a 100 de un trabajo terminado, para comparar IAs, versiones o borradores.

Combina las herramientas del kit:
  - estructura: secciones exigidas presentes (de 'secciones:' en el encabezado o --secciones)
  - citas y referencias: revisar.py (cita↔referencia, años, orden, citas textuales sin página)
  - fuentes reales: verificar_referencias.py (DOI y URL existentes) — con --red
  - afirmaciones respaldadas: verificar_afirmaciones.py (números presentes, evidencia) — con --red
  - pendientes, estilo (muletillas de IA, oraciones largas) y extensión

    python3 scripts/evaluar.py trabajo.md --palabras 2500
    python3 scripts/evaluar.py trabajo.docx --red --secciones "Introducción,Objetivos,Marco teórico,Conclusiones"

El puntaje mide control de calidad, no la calidad de las ideas: un trabajo puede sacar 100
y tener un argumento flojo. Para eso está el revisor (08-agentes/prompts/5-revisor.md).
"""
import argparse
import os
import re
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import revisar  # noqa: E402


def contar(H, patron, sev=None):
    fuentes = [H[sev]] if sev else H.values()
    return sum(1 for v in fuentes for h in v if re.search(patron, h))


def correr(script, archivo):
    r = subprocess.run([sys.executable, os.path.join(AQUI, script), archivo], capture_output=True, text=True,
                       timeout=1200)
    return r.stdout


def main():
    ap = argparse.ArgumentParser(description="Puntaje 0–100 de control de calidad de un trabajo")
    ap.add_argument("archivo")
    ap.add_argument("--palabras", type=int)
    ap.add_argument("--secciones", help="secciones obligatorias separadas por coma")
    ap.add_argument("--rubrica")
    ap.add_argument("--red", action="store_true", help="verificar también fuentes y afirmaciones (internet, más lento)")
    a = ap.parse_args()
    es_md = not a.archivo.lower().endswith(".docx")
    blocks = revisar.read_md(a.archivo) if es_md else revisar.read_docx(a.archivo)
    extra = [s.strip() for s in a.secciones.split(",")] if a.secciones else None
    H, stats, _ = revisar.review(blocks, a.rubrica, a.palabras, es_md, extra)
    filas = []

    exigidas = revisar.secciones_exigidas(blocks, extra)
    faltan = contar(H, r"^Falta la sección")
    estructura = 20 * (1 - faltan / len(exigidas)) if exigidas else 20
    filas.append(("Estructura (secciones exigidas)", estructura, 20,
                  f"{len(exigidas) - faltan}/{len(exigidas)} presentes" if exigidas else "sin lista de secciones: se asume completa"))

    sin_ref = contar(H, r"^Cita sin referencia")
    otros = contar(H, r"^(Año distinto|Referencia sin cita|La lista de referencias|Fecha en formato|Cita textual)")
    citas = max(0, 25 - 6 * sin_ref - 2 * otros)
    filas.append(("Citas y referencias", citas, 25, f"{sin_ref} citas sin referencia, {otros} otros problemas"))

    pend = contar(H, r"^Pendiente sin resolver")
    datos = contar(H, r"^Dato sin cita")
    honestidad = max(0, 15 - 5 * pend - 3 * datos)
    filas.append(("Pendientes y datos sin fuente", honestidad, 15, f"{pend} pendientes, {datos} datos sin cita"))

    mul = next((h for h in H["MENOR"] + H["IMPORTANTE"] if h.startswith("Frases típicas de IA")), "")
    dens = float(re.search(r"\(([\d.]+) por", mul).group(1)) if mul else 0.0
    largas = next((int(re.match(r"(\d+)", h).group(1)) for h in H["MENOR"] if "oraciones de más de 40" in h), 0)
    tasa_largas = largas / max(stats["palabras"] / 100, 1)  # por cada 100 palabras
    estilo = max(0.0, 15 - 2 * dens - 6 * tasa_largas)
    filas.append(("Estilo (muletillas de IA, oraciones largas)", estilo, 15,
                  f"{dens:.1f} muletillas/1000 palabras, {largas} oraciones largas"))

    if a.palabras:
        desvio = abs(stats["palabras"] - a.palabras) / a.palabras
        ext = 10 if desvio <= 0.10 else max(0, 10 - 20 * (desvio - 0.10))
        filas.append(("Extensión", ext, 10, f"{stats['palabras']} de {a.palabras} palabras"))

    if a.red:
        out = correr("verificar_referencias.py", a.archivo)
        m = re.search(r"(\d+) referencias · (\d+) verificadas · (\d+) críticas · (\d+) importantes · (\d+) a mano", out)
        if m:
            tot, ok, crit, imp, mano = map(int, m.groups())
            base = max(tot - mano, 1)
            fuentes = max(0, 10 * ok / base - 5 * crit - 2 * imp)
            filas.append(("Fuentes reales (DOI/URL)", fuentes, 10, f"{ok}/{tot} verificadas, {crit} inexistentes, {mano} a mano"))
        out = correr("verificar_afirmaciones.py", a.archivo)
        m = re.search(r"probable respaldo: (\d+) · 🟡 revisar: (\d+) · 🔴 sin respaldo aparente: (\d+)", out)
        if m:
            pr, rv, sr = map(int, m.groups())
            tot = max(pr + rv + sr, 1)
            afirm = max(0, 5 * (pr + 0.5 * rv) / tot - 3 * sr)
            filas.append(("Afirmaciones respaldadas", afirm, 5, f"{pr} probables, {rv} por revisar, {sr} sin respaldo"))

    obtenido = sum(f[1] for f in filas)
    maximo = sum(f[2] for f in filas)
    puntaje = round(100 * obtenido / maximo)
    print(f"# Evaluación de `{os.path.basename(a.archivo)}`: **{puntaje}/100**\n")
    print("| Criterio | Puntos | Máx. | Detalle |\n|---|---|---|---|")
    for nombre, pts, mx, det in filas:
        print(f"| {nombre} | {pts:.1f} | {mx} | {det} |")
    if not a.red:
        print("\n_Sin --red: no se verificó que las fuentes existan ni que respalden las afirmaciones._")
    print("\n> Mide control de calidad, no la calidad del argumento.")


if __name__ == "__main__":
    main()
