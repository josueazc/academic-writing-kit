---
tipo: guia
tema: integraciones
---
# Usar el kit desde el navegador, con el Word ya formateado

El formato del trabajo (portada, índice, número de página, estilos APA 7) lo pone **`md2docx.py`**, no la IA. Por eso el objetivo en cada herramienta es el mismo: que la IA escriba el trabajo en Markdown y lo pase por ese script. Hay tres caminos, del mejor al más simple:

1. **La IA ejecuta Python y tiene el script** (ChatGPT, Claude.ai, Mistral): te entrega el `.docx` listo.
2. **La IA no ejecuta Python** (Gemini, Perplexity, Copilot, DeepSeek…): te entrega el Markdown y lo convertís en **[Google Colab](https://colab.research.google.com/github/josueazc/academic-writing-kit/blob/main/colab/kit-academico.ipynb)** con un clic. Gratis, solo pide una cuenta de Google.
3. **Siempre, al final:** pasá el trabajo (`.md` o `.docx`) por el mismo Colab para **verificar que las fuentes existan**. El Python de los chats no tiene internet y no puede hacerlo.

## Paquetes
Se generan solos en cada actualización del repositorio, en [Releases › paquetes](https://github.com/josueazc/academic-writing-kit/releases/tag/paquetes):

| Archivo | Para |
|---|---|
| `kit-para-chats.zip` | GPT personalizado, proyectos de ChatGPT o Claude, Gems, espacios. Trae `INSTRUCCIONES.md`, `md2docx.py`, la revisión sin internet y las guías clave (17 archivos). |
| `escritura-academica-skill.zip` | Skill de Claude.ai (el kit completo). |
| `md2docx.py` | Subir a cualquier chat que ejecute Python. |

## Herramienta por herramienta
Revisado el 2026-10-28 con la documentación pública de cada una; los menús y lo que incluye cada plan cambian seguido. Si algo no coincide, buscá "instrucciones personalizadas", "archivos" o "ejecutar código".

| Herramienta | ¿Ejecuta Python con tus archivos? | Camino para el Word |
|---|---|---|
| **ChatGPT** | Sí (intérprete de código) | GPT personalizado o proyecto con el paquete → entrega el `.docx` |
| **Claude.ai** | Sí (con "ejecución de código y creación de archivos" activada) | Skill o proyecto → entrega el `.docx` |
| **Mistral Le Chat** | Sí (intérprete de código) | Subí `md2docx.py` al chat → entrega el `.docx` |
| **Gemini** | No de forma confiable con archivos propios | Gem con las instrucciones → Markdown → Colab |
| **Microsoft Copilot** | Limitado | Markdown → Colab → abrí el `.docx` en Word |
| **Perplexity** | No | Espacio con las instrucciones → Markdown → Colab |
| **Grok** | Según la versión | Si ejecuta código, subí `md2docx.py`; si no, Colab |
| **DeepSeek, Qwen, Kimi, Meta AI, Poe** | En general no | Pegá `INSTRUCCIONES.md` → Markdown → Colab |
| **NotebookLM** | No | No sirve para redactar el trabajo; úsalo para estudiar tus fuentes |

### ChatGPT: GPT personalizado (recomendado; se comparte con un enlace)
1. **Explorar GPT › Crear › Configurar.**
2. **Nombre:** «Trabajos académicos APA 7». **Descripción:** «Hace trabajos académicos con fuentes reales y te entrega el Word con formato APA 7».
3. **Instrucciones:** pegá el contenido de `INSTRUCCIONES.md` (cabe en el límite de 8000 caracteres).
4. **Conocimiento:** subí los 17 archivos de `kit-para-chats.zip`, sin el zip.
5. **Capacidades:** activá **Búsqueda web** e **Intérprete de código y análisis de datos**. Sin el intérprete no hay `.docx`.
6. **Iniciadores de conversación:** «Haceme un trabajo escrito completo», «Revisá mi trabajo con el kit».
7. Publicalo como **Cualquiera con el enlace** y compartí ese enlace con quien vaya a usarlo.

Sin GPT: en un **proyecto** subí los mismos archivos y pegá las instrucciones; o en un chat suelto subí `md2docx.py` y pegá `INSTRUCCIONES.md`.

### Claude.ai: skill (recomendado)
1. **Configuración › Capacidades:** activá **Ejecución de código y creación de archivos**.
2. En **Skills**, **Subir skill** y elegí `escritura-academica-skill.zip`.
3. En cualquier chat pedí el trabajo: Claude carga la skill sola, pregunta antes de escribir y entrega el `.docx`.

Alternativa: un **proyecto** con los archivos de `kit-para-chats.zip` como conocimiento y `INSTRUCCIONES.md` como instrucciones del proyecto.

### Gemini: Gem + Colab
1. **Gems › Nuevo Gem:** pegá `INSTRUCCIONES.md` en las instrucciones y subí las guías `.md` del paquete.
2. Pedí el trabajo. Al final te da el Markdown en un bloque de código.
3. Abrí el **Colab**, pegá el texto o subí el archivo y ejecutá todo: se verifican las fuentes y se descarga el `.docx`.

### Cualquier otra IA
Pegá `INSTRUCCIONES.md` al empezar el chat y pedí el trabajo. Si ejecuta Python, subile `md2docx.py`; si no, convertí el Markdown en Colab.

## Qué revisar en el Word que recibís
- Que tenga portada, índice y número de página: si falta todo eso, la IA armó el Word con su propio código en vez de usar `md2docx.py`. Pedile que use el script.
- Al abrirlo, aceptá **actualizar los campos** para que el índice muestre los números de página.
- Pasalo por el Colab para verificar las fuentes antes de entregarlo.
