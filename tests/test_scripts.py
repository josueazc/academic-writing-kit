"""Pruebas de las herramientas (sin red). Ejecutar: python3 -m unittest discover tests"""
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(RAIZ, "scripts")
EJEMPLO = os.path.join(RAIZ, "07-plantillas", "ejemplo-md2docx.md")
sys.path.insert(0, SCRIPTS)

import revisar  # noqa: E402

ROTO = """# Introducción
En el mundo actual, es importante destacar que la tecnología juega un papel crucial (Castells, 2012).
Según el Tribunal Supremo de Elecciones (2020), el referéndum es clave. Reguillo (2018) plantea algo.
Hoy en día la juventud participa (Instituto Costarricense de Turismo [ICT], 2024) y luego (ICT, 2024).
También (Gómez, 2019; Zumbado et al., 2022) y (Bennet & Segerberg, 2012). Pendiente [VERIFICAR dato].
Castells (2012) habla de "redes de indignación que se forman en internet sin líderes" (Castells, 2012).
# Justificación
Texto corto.
# Referencias
Bennett, W. L., & Segerberg, A. (2012). The logic of connective action. *Information, Communication & Society, 15*(5), 739–768.
Castells, M. (2012). *Redes de indignación y esperanza*. Alianza Editorial.
Alexander Ramírez. (6 de marzo de 2024). Sigue descontento. https://crhoy.com
Instituto Costarricense de Turismo. (2024). *Informe*. https://ict.go.cr
Reguillo, R. (2017). *Paisajes insurrectos*. NED Ediciones.
Tribunal Supremo de Elecciones. (2020). *Referéndum*. https://tse.go.cr
Zumbado, R., Barquero, A., & Hidalgo, O. (2022). Resistencia. *Revista Ciencia y Salud*.
"""


def run(*args):
    return subprocess.run([sys.executable, *args], capture_output=True, text=True, cwd=RAIZ)


class TestMd2Docx(unittest.TestCase):
    def test_genera_docx_valido(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "x.docx")
            r = run(os.path.join(SCRIPTS, "md2docx.py"), EJEMPLO, "-o", out)
            self.assertEqual(r.returncode, 0, r.stderr)
            z = zipfile.ZipFile(out)
            self.assertIn("word/document.xml", z.namelist())
            estilos = z.read("word/styles.xml").decode()
            for s in ("Heading1", "Heading3", "Referencia", "CitaBloque", "BodyText", "Bibliography"):
                self.assertIn(f'w:styleId="{s}"', estilos)
            doc = z.read("word/document.xml").decode()
            self.assertIn("Tabla 1", doc)
            self.assertIn("pageBreakBefore", doc)

    def test_titulos_numerados(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "n.md")
            texto = open(EJEMPLO, encoding="utf-8").read().replace("toc: false", "toc: false\nnumerar_titulos: true")
            open(src, "w", encoding="utf-8").write(texto)
            out = os.path.join(d, "n.docx")
            self.assertEqual(run(os.path.join(SCRIPTS, "md2docx.py"), src, "-o", out).returncode, 0)
            doc = zipfile.ZipFile(out).read("word/document.xml").decode()
            self.assertIn("1. Introducción", doc)
            self.assertIn("1.1 Transferencia", doc)
            self.assertNotIn("1. Resumen", doc)


class TestTrabajoCompleto(unittest.TestCase):
    def test_portada_indice_pie_y_comillas(self):
        md = """---
modo: completo
institucion: Universidad Ejemplo
carrera: Biotecnología
curso: BIO-101 Curso
titulo: Título de Prueba
tipo_trabajo: Proyecto de investigación
autores: ["Ana Pérez — Carné 123"]
docente: Prof. Juan Mora
grupo: "01"
lugar: San José, Costa Rica
fecha: 1 de noviembre de 2026
pie_texto: Prueba
---
# Introducción
Texto con "comillas" y https://ejemplo.com/"x".
# Objetivos
Texto.
# Anexos
## Anexo A Instrumento
Texto.
"""
        with tempfile.TemporaryDirectory() as d:
            src, out = os.path.join(d, "c.md"), os.path.join(d, "c.docx")
            open(src, "w", encoding="utf-8").write(md)
            self.assertEqual(run(os.path.join(SCRIPTS, "md2docx.py"), src, "-o", out).returncode, 0)
            z = zipfile.ZipFile(out)
            doc = z.read("word/document.xml").decode()
            self.assertIn("Universidad Ejemplo", doc)  # en mayúsculas por formato (caps), el texto queda igual
            self.assertIn("Carné 123", doc)
            self.assertIn("Grupo: 01", doc)
            self.assertIn("Presentado por:", doc)
            self.assertIn(" TOC ", doc)
            self.assertIn('w:val="TOC2"', doc)  # el índice ya trae los títulos
            self.assertIn("\u201ccomillas\u201d", doc)
            self.assertIn("word/footer1.xml", z.namelist())
            self.assertIn("Prueba", z.read("word/footer1.xml").decode())
            self.assertIn("<w:titlePg/>", doc)  # portada sin número


class TestRevisar(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.md = os.path.join(self.tmp.name, "roto.md")
        open(self.md, "w", encoding="utf-8").write(ROTO)
        H, self.stats, _ = revisar.review(revisar.read_md(self.md), es_md=True)
        self.todo = "\n".join(h for v in H.values() for h in v)
        self.H = H

    def tearDown(self):
        self.tmp.cleanup()

    def test_cita_sin_referencia(self):
        self.assertIn("Cita sin referencia: «Gómez, 2019»", self.todo)

    def test_siglas_y_narrativas_coinciden(self):
        for ok in ("ICT, 2024", "Tribunal Supremo", "Zumbado", "Castells, 2012»"):
            self.assertNotIn(f"Cita sin referencia: «{ok}", self.todo)

    def test_anio_distinto_y_apellido_parecido(self):
        self.assertIn("Reguillo (2018)", self.todo)
        self.assertIn("Bennet", self.todo)

    def test_pendientes_y_muletillas(self):
        self.assertIn("[VERIFICAR dato]", self.todo)
        self.assertIn("Frases típicas de IA", self.todo)

    def test_cita_textual_sin_pagina(self):
        self.assertIn("Cita textual sin página", self.todo)

    def test_referencias_problematicas(self):
        self.assertIn("Referencia sin cita en el texto: «Alexander Ramírez", self.todo)
        self.assertIn("Fecha en formato no APA", self.todo)

    def test_rubrica(self):
        rub = os.path.join(self.tmp.name, "r.md")
        open(rub, "w", encoding="utf-8").write(
            "| ID | Criterio | Puntaje |\n|---|---|---|\n| C1 | Justificación | 10 |\n| C2 | Marco teórico | 20 |\n")
        H, _, filas = revisar.review(revisar.read_md(self.md), rub, 800, es_md=True)
        todo = "\n".join(h for v in H.values() for h in v)
        self.assertIn("C2 «Marco teórico»", todo)
        self.assertIn("C1 poco desarrollado", todo)

    def test_dato_sin_cita_y_secciones(self):
        md = os.path.join(self.tmp.name, "d.md")
        open(md, "w", encoding="utf-8").write("---\nsecciones: [Introducción, Marco teórico]\n---\n# Introducción\n"
                                              "El 87 % de los jóvenes usa redes. Según INEC (2024), el 40 % trabaja.\n# Referencias\n"
                                              "Instituto Nacional de Estadística y Censos. (2024). *Encuesta*.\n")
        H, _, _ = revisar.review(revisar.read_md(md), es_md=True)
        todo = "\n".join(h for v in H.values() for h in v)
        self.assertIn("Dato sin cita", todo)
        self.assertIn("87 %", todo)
        self.assertNotIn("el 40 %", todo)
        self.assertIn("Falta la sección exigida «Marco teórico»", todo)

    def test_docx_igual_que_md(self):
        out = os.path.join(self.tmp.name, "roto.docx")
        self.assertEqual(run(os.path.join(SCRIPTS, "md2docx.py"), self.md, "-o", out).returncode, 0)
        H, stats, _ = revisar.review(revisar.read_docx(out))
        self.assertEqual(stats["referencias"], self.stats["referencias"])
        self.assertIn("Cita sin referencia: «Gómez, 2019»", "\n".join(H["CRÍTICO"]))


class TestTareas(unittest.TestCase):
    def test_fechas(self):
        import tareas
        self.assertEqual(str(tareas.fecha("15 de mayo de 2026")), "2026-05-15")
        self.assertEqual(str(tareas.fecha("2026-11-01")), "2026-11-01")


if __name__ == "__main__":
    unittest.main()
