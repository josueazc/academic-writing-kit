# Escritura académica — knowledge base para IA

Base de conocimiento en Markdown para que **cualquier IA** (Claude, ChatGPT, Gemini, Copilot, Cursor, Codex…) produzca trabajos escritos con el formato correcto: proyectos de colegio, Expotec, ensayos, artículos de divulgación, informes y trabajos universitarios grandes (TFG/tesis) en **APA 7**.

Se construyó analizando 8 trabajos reales (colegio técnico en Costa Rica, 2024–2026) y una rúbrica de especificaciones, más guías oficiales de APA 7, la taxonomía de Bloom revisada y guías de escritura académica.

Es a la vez:
- un **repositorio git** (para versionarlo, compartirlo y aceptar contribuciones), y
- una **bóveda de Obsidian** (abrí esta carpeta con *Open folder as vault*).

## Cómo usarlo

| Situación | Qué hacer |
|---|---|
| IA con acceso a archivos (Claude Code, Codex, Cursor, Copilot) | Abrí la IA dentro de esta carpeta. Lee sola `AGENTS.md` (o `CLAUDE.md` / `GEMINI.md`, que apuntan ahí). |
| Chat web (ChatGPT, Gemini, Claude.ai) | Pegá o adjuntá [`PROMPT-UNIVERSAL.md`](PROMPT-UNIVERSAL.md) y luego tu [brief](07-plantillas/brief-del-trabajo.md) lleno. |
| Proyecto de ChatGPT / Claude Project / Gem | Subí la carpeta completa (o el ZIP) como conocimiento y poné `PROMPT-UNIVERSAL.md` como instrucciones. |
| Varios agentes | Seguí [`08-agentes/flujo-multiagente.md`](08-agentes/flujo-multiagente.md). |

**Regla de oro:** lo que pida el docente (rúbrica, especificaciones) **siempre** gana sobre esta base. La base solo llena los huecos.

## Mapa

- [00-indice.md](00-indice.md) — índice completo (MOC)
- `01-formato/` — página, tipografía, títulos, portada, tablas, figuras, configuración en Word/Docs
- `02-citas-y-referencias/` — APA 7 citas, referencias y errores frecuentes
- `03-estructuras/` — esqueleto de cada tipo de trabajo
- `04-secciones/` — cómo escribir cada sección (objetivos, marco teórico, conclusiones…)
- `05-redaccion/` — estilo académico, conectores, revisión, IA e integridad
- `06-bloom/` — taxonomía de Bloom revisada aplicada a objetivos y a la revisión
- `07-plantillas/` — plantillas listas y el brief del trabajo
- `08-agentes/` — flujo multiagente y prompts por rol
- `09-analisis/` — qué hicieron bien y mal los trabajos analizados
- [10-fuentes.md](10-fuentes.md) — bibliografía de esta base

## Contribuir

Ver [CONTRIBUTING.md](CONTRIBUTING.md). Contenido bajo licencia CC BY 4.0 ([LICENSE](LICENSE)).

> Esta base no contiene los trabajos originales ni datos de estudiantes; solo las reglas que se derivan de ellos.
