#!/usr/bin/env python3
"""Lee un PDF de un trabajo y lo convierte en los bloques que usa revisar.py.

Sin dependencias de Python: usa `pdftotext` (poppler) si está instalado y, en macOS,
PDFKit mediante `swift`. Un PDF no guarda estilos, así que los títulos se deducen
(nombres de sección conocidos y líneas cortas sin punto final) y se pierden las
cursivas: con un PDF, revisar.py no revisa cursivas ni formato de página.

Uso directo (muestra el Markdown reconstruido): python3 scripts/leer_pdf.py trabajo.pdf
"""
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata

SWIFT = """import PDFKit
let d = PDFDocument(url: URL(fileURLWithPath: CommandLine.arguments[1]))!
for i in 0..<d.pageCount { print(d.page(at: i)!.string ?? ""); print("\\u{0C}") }
"""
NIVEL1 = {"resumen", "abstract", "introduccion", "planteamiento del problema", "justificacion", "antecedentes",
          "objetivos", "marco teorico", "marco conceptual", "marco metodologico", "metodologia", "metodo",
          "desarrollo", "resultados", "resultados y analisis", "analisis de resultados", "discusion",
          "conclusiones", "conclusion", "recomendaciones", "referencias", "bibliografia",
          "referencias bibliograficas", "anexos", "apendices", "tabla de contenidos", "indice"}
REF = {"referencias", "bibliografia", "referencias bibliograficas"}


def _norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9 ]", "", "".join(c for c in s if unicodedata.category(c) != "Mn")).strip()


def texto_pdf(path):
    """Texto por páginas (separadas por \\f). Lanza RuntimeError si no hay con qué extraerlo."""
    if shutil.which("pdftotext"):
        r = subprocess.run(["pdftotext", "-enc", "UTF-8", path, "-"], capture_output=True, text=True, timeout=120)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout
    if platform.system() == "Darwin" and shutil.which("swift"):
        with tempfile.NamedTemporaryFile("w", suffix=".swift", delete=False) as f:
            f.write(SWIFT)
        try:
            r = subprocess.run(["swift", f.name, os.path.abspath(path)], capture_output=True, text=True, timeout=300)
        finally:
            os.remove(f.name)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout
    raise RuntimeError("No se pudo extraer el texto del PDF: instalá poppler (pdftotext) o revisá el .docx o el .md.")


def bloques(texto):
    """[(tipo, nivel, texto)] como read_md: 'meta' (portada e índice), 'h' y 'p'."""
    paginas = [[l.strip() for l in p.splitlines() if l.strip() and not re.fullmatch(r"\d{1,3}", l.strip())]
               for p in texto.split("\f")]
    largos = sorted(len(l) for p in paginas for l in p) or [80]
    ancho = largos[int(len(largos) * 0.75)]  # largo típico de una línea llena
    out, buf = [], []
    en_refs = False

    def flush():
        if buf:
            out.append(("p", 0, re.sub(r"(https?://\S+-) (\S)", r"\1\2", " ".join(buf))))
            buf.clear()

    for pag in paginas:
        if pag is paginas[0] and not any(_norm(l) in NIVEL1 - {"tabla de contenidos", "indice"} for l in pag):
            out.append(("meta", 0, "\n".join(pag)))  # portada (en APA la introducción no lleva título)
            continue
        if any(re.search(r"\.{5,}\s*\d+$", l) for l in pag[:4]) or (pag and _norm(pag[0]) in ("tabla de contenidos", "indice")):
            out.append(("meta", 0, "\n".join(pag)))  # índice
            continue
        for i, l in enumerate(pag):
            n = _norm(l)
            sig = pag[i + 1] if i + 1 < len(pag) else ""
            if n in NIVEL1:
                flush()
                en_refs = n in REF
                out.append(("h", 1, l))
                continue
            corta = len(l) < 0.6 * ancho and len(l.split()) <= 10
            if (not en_refs and corta and l[:1].isupper() and not re.search(r"[.,;:)]$", l)
                    and not re.match(r"(Tabla|Figura|Nota)\b", l) and (not sig or sig[:1].isupper() or sig[:1].isdigit())):
                flush()
                out.append(("h", 2, l))
                continue
            if en_refs:
                completa = buf and re.search(r"\((\d{4}|s\. ?f\.)", " ".join(buf))
                autor = re.match(r"^(?:(?:de|van|von|ten|der|la)\s)*[A-ZÁÉÍÓÚÑ][\w'’ -]+, [A-Z]\.", l) \
                    or re.match(r"^[A-ZÁÉÍÓÚÑ][^.()]+\.\s\((\d{4}|s\. ?f\.)", l)
                editores = re.search(r"\(Eds?\.\)", l) or re.search(r"\b(?:En|In)\s+(?:[A-Z]\.\s?)+$", buf[-1] if buf else "")
                if completa and autor and not editores:  # los editores de un capítulo no abren otra referencia
                    flush()
                buf.append(l)
                continue
            if re.match(r"^\d+\.\s", l):
                flush()
            buf.append(l)
            if len(l) < 0.85 * ancho and re.search(r"[.?!:]$", l):
                flush()
        flush()
    return out


def leer(path):
    return bloques(texto_pdf(path))


if __name__ == "__main__":
    for tipo, nivel, t in leer(sys.argv[1]):
        print(("#" * nivel + " " + t) if tipo == "h" else ("[portada/índice] " + t[:80].replace("\n", " ") if tipo == "meta" else t), end="\n\n")
