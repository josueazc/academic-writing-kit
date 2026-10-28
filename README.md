<div align="center">

# ✦ ScholarForge

### *De una idea a un trabajo académico con estructura, evidencia y formato.*

**Base de conocimiento y herramientas para investigar, redactar, citar y revisar con IA.**

APA 7 · Fuentes verificables · Rúbricas · Markdown → Word

[![Pruebas](https://github.com/josueazc/ScholarForge/actions/workflows/pruebas.yml/badge.svg)](https://github.com/josueazc/ScholarForge/actions/workflows/pruebas.yml)
[![Licencia](https://img.shields.io/badge/Licencia-CC_BY_4.0-2563EB?style=flat&logo=creativecommons&logoColor=white)](LICENSE)
[![Contribuciones](https://img.shields.io/badge/PRs-bienvenidos-22C55E?style=flat)](CONTRIBUTING.md)

<br/>

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Markdown](https://img.shields.io/badge/Markdown-181717?style=for-the-badge&logo=markdown&logoColor=white)
![OOXML](https://img.shields.io/badge/OOXML-DOCX-185ABD?style=for-the-badge)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)

![OpenAlex](https://img.shields.io/badge/OpenAlex-Fuentes_académicas-2563EB?style=for-the-badge)
![Crossref](https://img.shields.io/badge/Crossref-DOI_y_referencias-F36F21?style=for-the-badge)
![APA 7](https://img.shields.io/badge/APA-7.ª_edición-334155?style=for-the-badge)

[Empezar](#-empezar) · [Herramientas](#-herramientas) · [Índice completo](00-indice.md) · [Integraciones](11-integraciones-ia/README.md)

</div>

---

## 📚 ¿Qué es ScholarForge?

Una buena idea necesita más que texto para convertirse en un trabajo académico: necesita una pregunta clara, una estructura adecuada, fuentes que se puedan comprobar, citas consistentes y un documento que cumpla la rúbrica.

**ScholarForge reúne ese proceso en un repositorio.** Combina guías en Markdown, instrucciones para agentes de IA y cinco herramientas de Python para pasar de un tema o apuntes en bruto a un documento revisado y formateado en Word.

Podés usarlo con un agente que lea la carpeta, con un chat mediante el prompt universal o como biblioteca de consulta. El contenido y los flujos están orientados principalmente a la escritura académica en español; también incluye una guía para escribir en inglés.

## ✨ Qué podés hacer

| Función | Qué aporta |
| --- | --- |
| 🧭 **Planear un trabajo** | Estructuras para ensayos, investigaciones, revisiones de literatura, artículos IMRyD, estudios de caso, informes y TFG/tesis |
| 📋 **Adaptar una rúbrica** | Convertir criterios, pesos e instrucciones del docente en secciones y requisitos de revisión |
| 🔎 **Buscar bibliografía** | Consultar OpenAlex y Crossref, combinar resultados y eliminar duplicados por DOI |
| 🔗 **Comprobar referencias** | Verificar DOI y URL, contrastar metadatos y señalar referencias que requieren revisión manual |
| ✍️ **Redactar y citar** | Guías por sección, disciplina y tipo de cita, con APA 7 y orientación sobre MLA, Chicago, Vancouver e IEEE |
| 📝 **Generar Word** | Convertir Markdown a `.docx` con portada, estilos de título, márgenes, tablas, figuras y referencias con sangría francesa |
| ✅ **Revisar un borrador** | Detectar citas sin referencia, pendientes, diferencias de año, problemas de extensión y cobertura de la rúbrica |
| 🎓 **Aprender y mejorar** | Prompts de mentoría, revisión por pares, integración de apuntes y respuesta a correcciones |
| 📅 **Organizar entregas** | Crear carpetas de trabajo y consultar fechas, etapas y revisiones pendientes |

## 🧩 Cómo está construido

| Capa | Contenido | Entrada |
| --- | --- | --- |
| **Conocimiento** | Formato, citas, estructuras, redacción, Bloom y convenciones por materia | [00-indice.md](00-indice.md) |
| **Herramientas** | Conversión a Word, fuentes, verificación, revisión y seguimiento | [scripts/README.md](scripts/README.md) |
| **Agentes** | Reglas compartidas y adaptadores para distintas herramientas | [AGENTS.md](AGENTS.md) · [SKILL.md](SKILL.md) |
| **Chats** | Instrucciones compactas para aportar contexto a una conversación | [PROMPT-UNIVERSAL.md](PROMPT-UNIVERSAL.md) |

## 🛠️ Tecnologías

| Tecnología | Para qué se usa |
| --- | --- |
| **Python 3.8+** | Herramientas de línea de comandos, sin dependencias externas |
| **Biblioteca estándar de Python** | HTTP y JSON para fuentes; expresiones regulares para revisión; ZIP y XML para leer y generar documentos |
| **Markdown** | Guías, plantillas, prompts y documentos fuente, con enlaces relativos |
| **Office Open XML / DOCX** | Documentos Word con estilos y formato de página |
| **OpenAlex + Crossref** | Búsqueda de publicaciones y consulta de metadatos bibliográficos y DOI |
| **unittest + GitHub Actions** | Pruebas sin red y comprobación de enlaces internos en CI, con Python 3.9 y 3.12 |

La lectura de las guías y la generación de Word funcionan localmente. La búsqueda de publicaciones y la verificación de DOI/URL necesitan internet. El modelo de IA lo elegís vos.

## 🚀 Empezar

### Con un agente que abre carpetas

```bash
git clone https://github.com/josueazc/ScholarForge.git
cd ScholarForge
```

Abrí la carpeta con tu agente y dale el tema, la información disponible y la consigna:

```text
Leé AGENTS.md. Trabajá en trabajos/ensayo-ia/.
Tema: inteligencia artificial en la educación.
Usá la rúbrica adjunta y los apuntes que te comparto.
Planeá la estructura, buscá fuentes verificables y revisá las referencias.
Generá el documento final con scripts/md2docx.py.
Marcá cualquier dato pendiente como [COMPLETAR] o [VERIFICAR].
```

Las instrucciones priorizan la rúbrica y los requisitos institucionales sobre el formato por defecto. Si no se indica otro formato, usan APA 7 de estudiante.

### Con un chat

Pegá [PROMPT-UNIVERSAL.md](PROMPT-UNIVERSAL.md), seguido de tu tema, apuntes y rúbrica. Si el chat ejecuta Python, compartí también los scripts necesarios; de lo contrario, guardá el Markdown y ejecutá la conversión localmente.

### Como Agent Skill

```bash
# Claude Code: se conserva el identificador de la skill existente
git clone https://github.com/josueazc/ScholarForge.git ~/.claude/skills/escritura-academica
```

Para otros agentes y rutas, consultá [la guía de integración](11-integraciones-ia/agentes.md). También podés abrir la carpeta como una bóveda de Obsidian.

## ⚙️ Herramientas

```bash
# Buscar fuentes en ambos índices y exportar resultados en Markdown
python3 scripts/fuentes.py buscar "inteligencia artificial en educación" --todas --formato md

# Consultar los metadatos de un DOI
python3 scripts/fuentes.py doi <DOI>

# Comprobar las referencias del documento
python3 scripts/verificar_referencias.py trabajo.md

# Revisar citas, pendientes, extensión y rúbrica
python3 scripts/revisar.py trabajo.md --rubrica rubrica.md --palabras 2500

# Generar el Word
python3 scripts/md2docx.py trabajo.md -o final.docx

# Consultar el estado de las entregas
python3 scripts/tareas.py estado
```

El ejemplo [`07-plantillas/ejemplo-md2docx.md`](07-plantillas/ejemplo-md2docx.md) muestra el frontmatter y la sintaxis del documento. Todas las opciones están en [scripts/README.md](scripts/README.md).

## 🗂️ Mapa del repositorio

| Carpeta | Contenido |
| --- | --- |
| `01-formato/` | APA 7, procesadores de texto, rúbricas, perfiles institucionales y otros estilos |
| `02-citas-y-referencias/` | Tipos de citas, referencias por fuente y búsqueda bibliográfica |
| `03-estructuras/` | Estructuras según el tipo de trabajo |
| `04-secciones/` | Objetivos, justificación, marcos, resumen y conclusiones |
| `05-redaccion/` | Estilo, conectores, integridad académica, revisión y escritura en inglés |
| `06-bloom/` | Taxonomía de Bloom para formular objetivos |
| `07-plantillas/` | Brief, plantillas y ejemplo de Markdown a Word |
| `08-agentes/` | Flujo de trabajo y prompts por rol |
| `09-analisis/` | Lecciones y errores de trabajos anteriores, anonimizados |
| `11-integraciones-ia/` | Agentes, chats, modelos locales y herramientas externas |
| `12-materias/` | Convenciones y guías por área de conocimiento |
| `scripts/` | Las cinco herramientas de Python |
| `tests/` | Pruebas automáticas de las herramientas |

Fuentes de la base: [10-fuentes.md](10-fuentes.md). Navegación detallada: [00-indice.md](00-indice.md).

## 🧪 Verificación

```bash
python3 -m unittest discover -s tests -v
```

GitHub Actions ejecuta las pruebas y revisa los enlaces internos en cada push y pull request.

La revisión automática detecta problemas formales y bibliográficos; la calidad del argumento y que cada fuente respalde lo que se afirma requieren lectura humana. Una respuesta válida de un DOI o URL, por sí sola, no valida una afirmación.

## 🛤️ Estado y siguientes pasos

**Disponible:** base de conocimiento, plantillas, instrucciones de agente, prompt universal, búsqueda bibliográfica, verificación de referencias, revisión de documentos y exportación a Word.

**Pendiente:** servidor MCP propio, instalación como plugin con un comando, exportación directa a PDF y LaTeX, búsqueda semántica en bibliotecas y generación de figuras. Hoy el PDF se exporta desde Word, Google Docs o LibreOffice; Pandoc y Overleaf tienen guías de uso.

## 🤝 Contribuir

Son bienvenidas las correcciones, nuevas estructuras y perfiles institucionales. Cada regla nueva necesita una fuente y los ejemplos deben estar anonimizados. Consultá [CONTRIBUTING.md](CONTRIBUTING.md) y la [guía de integridad académica](05-redaccion/integridad-e-ia.md).

## 📄 Licencia

**Creative Commons Attribution 4.0 International (CC BY 4.0).** Podés compartir y adaptar el material con la atribución correspondiente. Ver [LICENSE](LICENSE).

<div align="center">

**ScholarForge — estructura para tus ideas, evidencia para tus argumentos.**

Hecho por [Josué Azofeifa](https://github.com/josueazc) · Costa Rica 🇨🇷

</div>
