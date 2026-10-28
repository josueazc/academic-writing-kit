#!/usr/bin/env python3
"""Genera figuras (gráficos) listas para insertar con md2docx, con estilo académico sobrio.

Requiere matplotlib (`pip install matplotlib`): es la única herramienta del kit con una
dependencia, porque dibujar gráficos legibles sin ella no vale la pena.

    python3 scripts/figuras.py barras --datos "Sí:70.7,No:29.3" --titulo "¿Sabe qué es la turistificación?" \
        --eje-y "Porcentaje" -o figuras/fig1.png --nota "Elaboración propia con datos de la encuesta (n = 249)."
    python3 scripts/figuras.py pastel --datos "Nacionales:30.5,Extranjeros:28.1,No sabe:41.4" -o figuras/fig2.png
    python3 scripts/figuras.py lineas --csv datos.csv --x anio --y valor -o figuras/fig3.png
    python3 scripts/figuras.py barras-h --csv respuestas.csv --x opcion --y cantidad -o figuras/fig4.png

Imprime el bloque Markdown (Figura N + título + imagen + nota) para pegar en el trabajo.
Los datos los pone quien investiga: nunca inventes valores para "rellenar" un gráfico.
"""
import argparse
import csv
import os
import sys


def cargar(a):
    if a.datos:
        pares = [p.split(":") for p in a.datos.split(",")]
        return [p[0].strip() for p in pares], [float(p[1].replace(" ", "")) for p in pares]
    with open(a.csv, encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    return [r[a.x] for r in filas], [float(r[a.y].replace(",", ".")) for r in filas]


def main():
    ap = argparse.ArgumentParser(description="Gráficos académicos para md2docx")
    ap.add_argument("tipo", choices=["barras", "barras-h", "pastel", "lineas"])
    ap.add_argument("--datos", help='"Etiqueta:valor,Etiqueta:valor"')
    ap.add_argument("--csv")
    ap.add_argument("--x", help="columna de etiquetas (CSV)")
    ap.add_argument("--y", help="columna de valores (CSV)")
    ap.add_argument("--titulo", default="[COMPLETAR: título de la figura]")
    ap.add_argument("--eje-x", default="")
    ap.add_argument("--eje-y", default="")
    ap.add_argument("--nota", default="[COMPLETAR: fuente de los datos]")
    ap.add_argument("--numero", type=int, default=1)
    ap.add_argument("-o", "--salida", required=True)
    a = ap.parse_args()
    if not (a.datos or (a.csv and a.x and a.y)):
        ap.error("usá --datos o --csv con --x y --y")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("Falta matplotlib. Instalalo con:  python3 -m pip install matplotlib", file=sys.stderr)
        sys.exit(2)

    etiquetas, valores = cargar(a)
    plt.rcParams.update({"font.family": "serif", "font.size": 11, "axes.spines.top": False,
                         "axes.spines.right": False})
    fig, ax = plt.subplots(figsize=(6.4, 4.0), dpi=200)
    grises = ["#4d4d4d", "#8c8c8c", "#bfbfbf", "#d9d9d9", "#262626", "#a6a6a6"]
    if a.tipo == "barras":
        barras = ax.bar(etiquetas, valores, color=grises[0])
        ax.bar_label(barras, fmt="%g", padding=2)
    elif a.tipo == "barras-h":
        barras = ax.barh(etiquetas, valores, color=grises[0])
        ax.bar_label(barras, fmt="%g", padding=2)
        ax.invert_yaxis()
    elif a.tipo == "pastel":
        ax.pie(valores, labels=etiquetas, autopct="%1.1f %%", colors=grises[:len(valores)],
               wedgeprops={"edgecolor": "white"}, textprops={"fontsize": 10})
        ax.axis("equal")
    else:
        ax.plot(etiquetas, valores, marker="o", color=grises[0])
    if a.tipo != "pastel":
        ax.set_xlabel(a.eje_x)
        ax.set_ylabel(a.eje_y)
    fig.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(a.salida)), exist_ok=True)
    fig.savefig(a.salida)
    print(f"**Figura {a.numero}**\n*{a.titulo}*\n\n![{a.titulo}]({a.salida})\n\n*Nota.* {a.nota}")


if __name__ == "__main__":
    main()
