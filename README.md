# MangoSol · Presentación del avance de prefactibilidad

Presentación del avance (secciones I–IV) del curso **Formulación y Evaluación de Proyectos**
(Ingeniería Industrial, UPAO, 2026-20). Sigue el mismo esquema que la presentación de Gestión de la
Calidad del Hotel Río Blanco: reveal.js, con gráficos animados en `anim/`.

## Contenido

| Archivo | Qué es |
| --- | --- |
| `index.html` | Presentación de 22 diapositivas (flechas para avanzar, `F` pantalla completa, `S` notas del expositor) |
| `anim/flujo.html` | Flujograma DOP animado: los lotes de mango recorren la U y se encogen según el balance de materia |
| `anim/peyea.html` | Matriz PEYEA que se dibuja: las cuatro dimensiones como flechas y luego su suma como vector |
| `lib/` | reveal.js 5.1.0, incluido para que funcione sin conexión (las fuentes sí necesitan internet) |

## Cómo verla

**En línea:** https://protocol-pixel.github.io/MangoSol/ (GitHub Pages, rama `main`, carpeta raíz).

**En tu computadora:** las animaciones en `anim/` se cargan como iframes, y algunos navegadores bloquean eso si el archivo se abre
con doble clic. Lo más seguro es levantar un servidor local desde esta carpeta:

```powershell
python -m http.server 8765
```

y abrir `http://localhost:8765`.

## Cómo funcionan las animaciones

- **Entradas:** cada elemento con `data-build-in="rise 3"` aparece en el orden indicado cuando la
  diapositiva está activa (CSS + la clase `present` que pone reveal.js).
- **Contadores:** los números con `class="count"` cuentan desde cero.
- **Gráficos en `anim/`:** son páginas sueltas que se recargan cada vez que se entra a la diapositiva,
  para que se dibujen desde cero.
- **Embudo → brecha:** reveal.js *auto-animate* mueve la cifra «116.6 t» de una diapositiva a la otra.

Las cifras vienen de `../generador/datos.py`, pero se copiaron a mano: si cambia el modelo, hay que
actualizarlas aquí.
