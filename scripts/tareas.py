#!/usr/bin/env python3
"""Organiza los trabajos en curso y muestra qué se entrega primero.

Cada trabajo vive en trabajos/<nombre>/ con brief.md, rubrica.md, revisiones/ y el borrador.
(La carpeta trabajos/ está en .gitignore: no se publica.)

    python3 scripts/tareas.py nueva ensayo-ia --fecha 2026-11-15 --tipo ensayo --tema "IA en la educación" --materia Educación
    python3 scripts/tareas.py estado
"""
import argparse
import datetime as dt
import os
import re
import shutil

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRABAJOS = os.path.join(BASE, "trabajos")
MESES = {m: i for i, m in enumerate(["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                                      "septiembre", "octubre", "noviembre", "diciembre"], 1)}


def leer_campo(texto, campo):
    m = re.search(rf"^{campo}:(.*)$", texto, re.M)
    return m.group(1).split("#")[0].strip().strip('"') if m else ""


def fecha(valor):
    valor = valor.strip().lower()
    try:
        return dt.date.fromisoformat(valor)
    except ValueError:
        pass
    m = re.match(r"(\d{1,2}) de ([a-záéíóú]+) de (\d{4})", valor)
    if m and m.group(2) in MESES:
        return dt.date(int(m.group(3)), MESES[m.group(2)], int(m.group(1)))
    return None


def nueva(a):
    destino = os.path.join(TRABAJOS, a.nombre)
    if os.path.exists(destino):
        raise SystemExit(f"Ya existe: {destino}")
    os.makedirs(os.path.join(destino, "revisiones"))
    plantilla = open(os.path.join(BASE, "07-plantillas", "brief-del-trabajo.md"), encoding="utf-8").read()
    for campo, valor in (("tipo_de_trabajo", a.tipo), ("fecha_de_entrega", a.fecha), ("tema", a.tema),
                         ("materia_o_area", a.materia)):
        if valor:
            plantilla = re.sub(rf"^{campo}:(\s*)(#.*)?$",
                               lambda m, c=campo, v=valor: f"{c}:{m.group(1) or ' '}{v}  {m.group(2) or ''}".rstrip(),
                               plantilla, flags=re.M)
    open(os.path.join(destino, "brief.md"), "w", encoding="utf-8").write(plantilla)
    open(os.path.join(destino, "rubrica.md"), "w", encoding="utf-8").write(
        "| ID | Criterio | Puntaje | Sección |\n|---|---|---|---|\n")
    shutil.copy(os.path.join(BASE, "07-plantillas", "ejemplo-md2docx.md"), os.path.join(destino, "ejemplo-formato.md"))
    print(f"Creado {destino}\n  brief.md · rubrica.md · revisiones/ · ejemplo-formato.md")
    print(f"Siguiente: abrí la IA en {BASE} y pedí que trabaje en trabajos/{a.nombre}/")


def estado(_):
    if not os.path.isdir(TRABAJOS):
        print("No hay trabajos. Creá uno con: python3 scripts/tareas.py nueva <nombre> --fecha AAAA-MM-DD")
        return
    hoy = dt.date.today()
    filas = []
    for nombre in sorted(os.listdir(TRABAJOS)):
        carpeta = os.path.join(TRABAJOS, nombre)
        brief = os.path.join(carpeta, "brief.md")
        if not os.path.isfile(brief):
            continue
        texto = open(brief, encoding="utf-8").read()
        f = fecha(leer_campo(texto, "fecha_de_entrega"))
        archivos = os.listdir(carpeta)
        docx = [x for x in archivos if x.endswith(".docx")]
        revs = sorted(os.listdir(os.path.join(carpeta, "revisiones"))) if os.path.isdir(os.path.join(carpeta, "revisiones")) else []
        criticos = "?"
        if revs:
            m = re.search(r"(\d+) críticos", open(os.path.join(carpeta, "revisiones", revs[-1]), encoding="utf-8").read())
            criticos = m.group(1) if m else "?"
        if os.path.exists(os.path.join(carpeta, "ENTREGADO")):
            etapa = "entregado"
        elif docx:
            etapa = "documento generado"
        elif any(x.startswith(("borrador", "trabajo")) and x.endswith(".md") for x in archivos):
            etapa = "redactando"
        elif "esquema.md" in archivos:
            etapa = "planificado"
        else:
            etapa = "sin empezar"
        filas.append((f or dt.date.max, nombre, leer_campo(texto, "tipo_de_trabajo"), etapa, criticos, f))
    filas.sort()
    print(f"{'Entrega':<12} {'Días':>5}  {'Trabajo':<28} {'Tipo':<22} {'Etapa':<20} Críticos")
    for _, nombre, tipo, etapa, criticos, f in filas:
        dias = (f - hoy).days if f else None
        alerta = " ⚠️" if dias is not None and dias <= 3 and etapa != "entregado" else ""
        print(f"{(f.isoformat() if f else 'sin fecha'):<12} {(dias if dias is not None else '-'):>5}  "
              f"{nombre:<28} {tipo[:22]:<22} {etapa:<20} {criticos}{alerta}")
    print("\nMarcá un trabajo como entregado creando un archivo vacío ENTREGADO en su carpeta.")


def main():
    ap = argparse.ArgumentParser(description="Seguimiento de trabajos y entregas")
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("nueva", help="crear la carpeta de un trabajo")
    n.add_argument("nombre")
    n.add_argument("--fecha", default="", help="AAAA-MM-DD o '15 de mayo de 2026'")
    n.add_argument("--tipo", default="")
    n.add_argument("--tema", default="")
    n.add_argument("--materia", default="")
    n.set_defaults(fn=nueva)
    e = sub.add_parser("estado", help="listar trabajos por fecha de entrega")
    e.set_defaults(fn=estado)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
