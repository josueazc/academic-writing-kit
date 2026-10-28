---
tipo: guia
tema: formato
nivel: avanzado
---
# Citas automáticas con Pandoc o Quarto (opcional)

`md2docx.py` no necesita instalar nada, pero las referencias las escribís (o las escribe la IA) a mano. Si querés que **las citas y la lista de referencias se generen solas** desde tu biblioteca de Zotero, usá Pandoc o Quarto con archivos CSL (Citation Style Language).

## Pandoc
1. Instalá [Pandoc](https://pandoc.org/installing.html) y [Zotero](https://www.zotero.org) con [Better BibTeX](https://retorque.re/zotero-better-bibtex/).
2. Exportá tu colección de Zotero como `referencias.bib` (o `.json` CSL).
3. Descargá el estilo `apa.csl` del [repositorio oficial de estilos CSL](https://github.com/citation-style-language/styles) (también existen `ieee.csl`, `vancouver.csl`, `modern-language-association.csl`, `chicago-author-date.csl`).
4. En el Markdown, citá con claves:
   ```markdown
   Las redes facilitan la acción conectiva [@bennett2012]. Castells [-@castells2012] lo llama…
   Según @siles2020, …   Varias: [@castells2012; @reguillo2017]   Con página: [@sanchez2015, p. 4]
   ```
5. Generá el Word con el idioma español para "y", "et al." y fechas:
   ```bash
   pandoc trabajo.md --citeproc --bibliography referencias.bib --csl apa.csl \
     -M lang=es-CR -o trabajo.docx
   ```
6. Para que el .docx tenga formato APA (márgenes, doble espacio, títulos), generá una plantilla de estilos con md2docx y pasala como referencia:
   ```bash
   python3 scripts/md2docx.py 07-plantillas/ejemplo-md2docx.md -o plantilla-apa.docx
   pandoc trabajo.md --citeproc --bibliography referencias.bib --csl apa.csl \
     -M lang=es-CR --reference-doc plantilla-apa.docx -o trabajo.docx
   ```
   Pandoc toma los estilos (Normal, Título 1–5) de esa plantilla. La portada se agrega aparte.

## Quarto + apaquarto
[apaquarto](https://github.com/wjschne/apaquarto) (CC0) genera APA 7 completo en .docx, .pdf y .html, con portada, resumen, tablas y figuras:
```bash
quarto use template wjschne/apaquarto
quarto render trabajo.qmd --to apaquarto-docx
```
Ideal para psicología y ciencias sociales con análisis de datos en R o Python dentro del mismo documento.

## Cuándo conviene cada opción
| Opción | Usala cuando |
|---|---|
| `md2docx.py` | Querés cero instalaciones, la IA escribe todo y vos revisás |
| Pandoc + Zotero | Tenés tu biblioteca en Zotero y muchas referencias |
| Quarto + apaquarto | Trabajos con datos, tablas y gráficos generados por código |
| Overleaf | Matemáticas, ingeniería, tesis largas en LaTeX |
