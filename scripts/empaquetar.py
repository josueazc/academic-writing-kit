#!/usr/bin/env python3
"""Arma los paquetes para usar el kit desde el navegador (ChatGPT, Claude.ai, Gemini, Copilot…).

Genera en dist/:
  - escritura-academica-skill.zip  → Claude.ai: Configuración › Capacidades › Skills › Subir skill
  - kit-para-chats.zip y kit-para-chats/ → archivos sueltos para un GPT personalizado, un Gem,
    un proyecto o un espacio: instrucciones, generador de Word, revisión y las guías clave
  - md2docx.py → para subir a cualquier chat que ejecute Python

Uso: python3 scripts/empaquetar.py   (GitHub Actions lo corre en cada push y publica los
paquetes en la versión "paquetes" del repositorio).
"""
import os
import shutil
import zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(RAIZ, "dist")
FUERA = {".git", ".github", "tests", "trabajos", "dist", ".obsidian", "__pycache__", ".trash", "evals"}
EXT_FUERA = (".docx", ".pdf", ".pyc")
# Scripts que funcionan sin internet (el Python de los chats no tiene red)
SCRIPTS_CHAT = ["md2docx.py", "revisar.py", "coherencia.py", "apa_referencias.py", "formato_docx.py", "leer_pdf.py"]
GUIAS_CHAT = [
    "07-plantillas/ejemplo-md2docx.md", "07-plantillas/cuestionario-inicial.md",
    "03-estructuras/trabajo-escrito-completo.md", "04-secciones/objetivos.md", "06-bloom/taxonomia-bloom.md",
    "02-citas-y-referencias/tipos-de-citas.md", "02-citas-y-referencias/apa7-referencias.md",
    "08-agentes/prompts/5-revisor.md", "05-redaccion/checklist-revision.md",
]
LEEME = """# Kit de escritura académica para chats

Estos archivos son para usar el kit en ChatGPT, Claude.ai, Gemini, Copilot u otro chat.
Guía paso a paso por herramienta:
https://github.com/josueazc/academic-writing-kit/blob/main/11-integraciones-ia/navegador.md

- INSTRUCCIONES.md: pegalo como instrucciones del GPT, Gem, proyecto o espacio.
- md2docx.py: convierte el trabajo (Markdown) en Word con formato APA 7. No necesita internet.
- revisar.py y sus módulos: revisión de citas, formato y coherencia sin internet.
- El resto: guías que el chat consulta mientras escribe.

Si tu chat no ejecuta Python, convertí el Markdown en Google Colab:
https://colab.research.google.com/github/josueazc/academic-writing-kit/blob/main/colab/kit-academico.ipynb
"""


def incluir(rel):
    partes = rel.split(os.sep)
    return not (set(partes) & FUERA) and not rel.endswith(EXT_FUERA) and partes[-1] not in ("mi-perfil.yaml", ".DS_Store")


def skill_zip():
    out = os.path.join(DIST, "escritura-academica-skill.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for base, dirs, files in os.walk(RAIZ):
            dirs[:] = sorted(d for d in dirs if d not in FUERA)
            for f in sorted(files):
                rel = os.path.relpath(os.path.join(base, f), RAIZ)
                if incluir(rel):
                    z.write(os.path.join(RAIZ, rel), os.path.join("escritura-academica", rel))
    return out


def kit_chats():
    carpeta = os.path.join(DIST, "kit-para-chats")
    os.makedirs(carpeta, exist_ok=True)
    shutil.copy(os.path.join(RAIZ, "PROMPT-UNIVERSAL.md"), os.path.join(carpeta, "INSTRUCCIONES.md"))
    for s in SCRIPTS_CHAT:
        shutil.copy(os.path.join(RAIZ, "scripts", s), carpeta)
    for g in GUIAS_CHAT:
        shutil.copy(os.path.join(RAIZ, g), carpeta)
    with open(os.path.join(carpeta, "LEEME.md"), "w", encoding="utf-8") as f:
        f.write(LEEME)
    out = os.path.join(DIST, "kit-para-chats.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(carpeta)):
            z.write(os.path.join(carpeta, f), f)
    shutil.copy(os.path.join(RAIZ, "scripts", "md2docx.py"), DIST)
    return out


def main():
    shutil.rmtree(DIST, ignore_errors=True)
    os.makedirs(DIST)
    for p in (skill_zip(), kit_chats(), os.path.join(DIST, "md2docx.py")):
        print(f"{os.path.relpath(p, RAIZ)}  ({os.path.getsize(p) // 1024} KB)")


if __name__ == "__main__":
    main()
