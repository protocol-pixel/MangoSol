# MangoSol · Presentación del avance de prefactibilidad

Presentación del avance (secciones I–IV) del curso **Formulación y Evaluación de Proyectos**
(Ingeniería Industrial, UPAO, 2026-20), hecha con reveal.js y gráficos animados en `anim/`.

Este repositorio contiene **solo la presentación**. El informe en Word, el modelo de cálculo y los
demás entregables del estudio no están publicados aquí.

## Contenido

| Archivo | Qué es |
| --- | --- |
| `index.html` | Presentación de 22 diapositivas (flechas para avanzar, `F` pantalla completa, `S` notas del expositor) |
| `anim/flujo.html` | Flujograma DOP animado: los lotes de mango recorren la U y se encogen según el balance de materia |
| `anim/peyea.html` | Matriz PEYEA que se dibuja: las cuatro dimensiones como flechas y luego su suma como vector |
| `recorrido.html` | Recorrido 3D en primera persona por la planta en U (teclado y mouse o mando por Bluetooth/USB); se abre desde la diapositiva 20 |
| `lib/` | reveal.js 5.1.0, three.js r128 y las fuentes (Bricolage Grotesque, IBM Plex Sans y Mono en `lib/fonts/`), incluidos para que todo funcione sin conexión |

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
- **Embudo → brecha:** reveal.js *auto-animate* mueve la cifra «116.6» de una diapositiva a la otra.

## De dónde salen las cifras

- **Datos reales del sector:** exportaciones peruanas de mango deshidratado y sus destinos
  ([CIEN-ADEX, 2025](https://cien.adexperu.org.pe/wp-content/uploads/2025/01/NC_Mango_Ene2025_vf.pdf))
  y producción de mango de Piura en 2025 (Dirección Regional de Agricultura de Piura, vía
  [Agraria.pe](https://agraria.pe/noticias/produccion-de-mango-en-piura-crecio-55-81-en-2025-41552)).
- **Precio real de referencia:** en 2024 el Perú exportó 379 mil kg de mango deshidratado por US$ 3.7 M, es
  decir US$ 9.76/kg ([IDEXCAM-CCL, 2025](https://camaralimaplugin.arbitrajeccl.com.pe/wp-content/uploads/2026/03/EXPORTACIONES-PERUANAS-DE-FRUTAS-DESHIDRATADAS-IDEXCAM.DI_.pdf), con datos de SUNAT). El precio de
  MangoSol (US$ 8.50/kg FOB) es una decisión del proyecto y queda 13 % por debajo.
- **Datos simulados con fines académicos:** encuesta a importadores, competidores A, B y C con sus precios y
  parámetros del proceso.
- Los resultados (embudo de mercado, balance de materia, matrices, capacidad) se calcularon en un modelo
  aparte que no forma parte de este repositorio, y **se copiaron a mano** en `index.html`. Si el modelo
  cambia, hay que actualizar las cifras aquí.
