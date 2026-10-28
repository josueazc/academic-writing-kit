---
tipo: checklist
tema: revision
---
# Checklist de revisión antes de entregar

Usalo en tres pasadas: **contenido → citas → formato**. Antes, corré `python3 scripts/revisar.py trabajo.md` (o el .docx): verifica automáticamente citas↔referencias, pendientes, artefactos, muletillas de IA y cobertura de la rúbrica. Lo que queda abajo es lo que un script no puede juzgar.

## 1. Rúbrica y estructura
- [ ] Están todas las secciones que pide la rúbrica, en su orden.
- [ ] Conteos de palabras pedidos (justificación, conclusiones…) cumplidos.
- [ ] Coherencia: problema → pregunta → objetivos → metodología → conclusiones → recomendaciones (un hilo por objetivo).
- [ ] Objetivos con verbos medibles y sin repetir ([Bloom](../06-bloom/taxonomia-bloom.md)).
- [ ] Conclusiones sin información nueva; recomendaciones dirigidas a actores concretos.

## 2. Redacción
- [ ] Registro académico; sin coloquialismos ni primera persona mezclada.
- [ ] Párrafos de 4–8 oraciones; sin oraciones de más de 40 palabras.
- [ ] Ortografía y tildes revisadas (corrector + lectura en voz alta).
- [ ] Siglas definidas la primera vez.
- [ ] Ningún párrafo termina sin punto; ninguna sección quedó a medias.
- [ ] Abstract revisado en inglés.

## 3. Citas y referencias
- [ ] Cada cita tiene referencia y cada referencia tiene cita.
- [ ] Apellido y año idénticos en cita y referencia.
- [ ] Citas textuales con página o párrafo.
- [ ] 3+ autores con "et al." desde la primera cita.
- [ ] Lista en orden alfabético, sangría francesa, doble espacio.
- [ ] URLs/DOI funcionan y corresponden a la referencia (`python3 scripts/verificar_referencias.py trabajo.md`).
- [ ] Ninguna fuente sin verificar (sobre todo si una IA la sugirió).

## 4. Formato
- [ ] Fuente, tamaño, interlineado, alineación y márgenes según rúbrica o APA.
- [ ] Títulos con estilos Título 1–3 y niveles consistentes.
- [ ] Portada completa según APA o la plantilla de la institución.
- [ ] Tabla de contenidos automática y actualizada.
- [ ] Numeración de páginas correcta.
- [ ] Tablas y figuras: número en negrita, título en cursiva, nota, mencionadas en el texto.
- [ ] Referencias antes de anexos.
- [ ] Sin artefactos (`\%`, `**`, `#`, resaltados, comentarios).
- [ ] PDF exportado y revisado página por página (sin páginas en blanco ni figuras perdidas).

## 5. Integridad
- [ ] El texto pasa una revisión de similitud razonable (paráfrasis reales).
- [ ] Uso de IA declarado si el docente lo exige ([integridad-e-ia.md](integridad-e-ia.md)).
