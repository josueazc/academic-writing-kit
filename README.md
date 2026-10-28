# Escritura académica — knowledge base para IA

Base de conocimiento en Markdown + herramientas para que **cualquier IA** convierta un tema o información en bruto en un **trabajo académico completo, citado y formateado en Word**: ensayos, proyectos de investigación, proyectos aplicados, artículos, informes, monografías y TFG/tesis, en **APA 7** (y guía para Vancouver, IEEE, Chicago, MLA).

- Se adapta a **cualquier rúbrica**: la IA la lee y la mapea sobre las estructuras de la base.
- Funciona con Claude, ChatGPT, Gemini, Grok, Perplexity, Copilot, Cursor, Codex, Windsurf, Cline, Aider, DeepSeek, Qwen, Kimi, Le Chat, modelos locales y cualquier agente que lea `AGENTS.md`.
- Genera **.docx** con estilos APA reales (`scripts/md2docx.py`).
- Busca **fuentes reales** en índices con cientos de millones de trabajos y devuelve la referencia APA (`scripts/fuentes.py`).
- **Revisa con código** el trabajo terminado (.md o .docx): citas sin referencia, años y apellidos que no coinciden, pendientes, muletillas de IA y cobertura de la rúbrica según el peso de cada criterio (`scripts/revisar.py`).
- Se instala como **Agent Skill** (`SKILL.md`) en Claude Code, Codex, Cursor, Copilot y otros.
- Es también una **bóveda de Obsidian** (abrí la carpeta con *Open folder as vault*).

## Empezar en 1 minuto

**Con un agente que abre carpetas** (Claude Code, Codex, Cursor, Copilot, Gemini CLI…):
```bash
git clone https://github.com/josueazc/escritura-academica.git
cd escritura-academica
```
Abrí el agente ahí y pedí: *"Leé AGENTS.md. Hacé un ensayo de 5 páginas sobre [tema] con esta información: […]. Generá el .docx."*

**Con un chat** (ChatGPT, Gemini, Grok, Perplexity…): pegá [`PROMPT-UNIVERSAL.md`](PROMPT-UNIVERSAL.md), después tu tema/información y la rúbrica si hay. Para el .docx, subí también `scripts/md2docx.py` (si el chat ejecuta Python) o corrélo vos:
```bash
python3 scripts/md2docx.py trabajo.md
```

**Como Agent Skill** (se carga sola cuando pedís un trabajo académico):
```bash
git clone https://github.com/josueazc/escritura-academica.git ~/.claude/skills/escritura-academica   # Claude Code
```
Otras rutas (Codex, Cursor, Copilot) en [11-integraciones-ia/agentes.md](11-integraciones-ia/agentes.md).

**Revisar antes de entregar:**
```bash
python3 scripts/revisar.py trabajo.docx --rubrica rubrica.md --palabras 2500
```

Guías por herramienta: [11-integraciones-ia/](11-integraciones-ia/README.md).

## Mapa
- [00-indice.md](00-indice.md) — índice completo
- `01-formato/` — APA 7, títulos, tablas y figuras, Word/Docs, **adaptador de rúbricas**, perfiles de universidades (ULACIT, Fidélitas, privadas y públicas de CR) y otros estilos
- `02-citas-y-referencias/` — citas, referencias, errores frecuentes, **dónde buscar fuentes**
- `03-estructuras/` — esqueleto de cada tipo de trabajo
- `04-secciones/` — cómo escribir cada sección
- `05-redaccion/` — estilo, conectores, checklist, integridad e IA
- `06-bloom/` — taxonomía de Bloom revisada
- `07-plantillas/` — brief, plantillas y ejemplo para md2docx
- `08-agentes/` — flujo multiagente y prompts por rol
- `09-analisis/` — lecciones de trabajos reales
- `11-integraciones-ia/` — cómo conectar cada IA
- `scripts/` — md2docx.py, fuentes.py y revisar.py (Python 3, sin dependencias)

## Contribuir
Perfiles de más universidades, estilos y correcciones son bienvenidos: [CONTRIBUTING.md](CONTRIBUTING.md). Licencia CC BY 4.0 ([LICENSE](LICENSE)).

> No contiene trabajos originales ni datos personales de estudiantes; solo reglas y ejemplos anonimizados.
