# Texturas propias para las áreas 4, 5B, 6 y 7 (se corre con Python normal, no dentro de Blender).
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = r'C:\Users\Asus\Documents\Formulacion de proyectos\presentacion\proto\tex' + '\\'
OSC, CRE, NAR = (19, 32, 26), (243, 237, 226), (240, 160, 48)


def F(tam, estilo='bold'):
    archivo = {'bold': 'arialbd.ttf', 'reg': 'arial.ttf', 'black': 'ariblk.ttf'}[estilo]
    try:
        return ImageFont.truetype(r'C:\Windows\Fonts' + '\\' + archivo, tam)
    except OSError:
        return ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf', tam)


def mango_laminas(d, cx, cy, rx, ry, color, ang=-14):
    """El mango en láminas de la marca, dibujado a una tinta."""
    capa = Image.new('L', (int(rx * 2.6), int(ry * 2.6)), 0)
    g = ImageDraw.Draw(capa)
    w, h = capa.size
    g.ellipse([w / 2 - rx, h / 2 - ry, w / 2 + rx, h / 2 + ry], fill=255)
    rayas = Image.new('L', capa.size, 0); gr = ImageDraw.Draw(rayas)
    paso = ry * 2 / 11
    for i, off in enumerate([0, 6, -4, 8, -3, 5, -7, 3, -5, 7, 0]):
        y0 = h / 2 - ry + i * paso
        gr.rectangle([0, y0, w, y0 + paso * .74], fill=255)
    from PIL import ImageChops
    m = ImageChops.multiply(capa, rayas).rotate(ang, resample=Image.BICUBIC)
    d._image.paste(color, (int(cx - w / 2), int(cy - h / 2)), m)


# ---------- caja de cartón de 10 kg (cara lateral impresa a una tinta) ----------
kraft = (176, 134, 88)
im = Image.new('RGB', (1024, 640), kraft)
px = im.load()
import random
random.seed(3)
for y in range(0, 640, 2):  # fibra del cartón
    for x in range(0, 1024, 3):
        v = random.randint(-9, 9)
        r, g, b = px[x, y]; px[x, y] = (r + v, g + v, b + v)
im = im.filter(ImageFilter.GaussianBlur(.6))
d = ImageDraw.Draw(im)
tinta = (38, 52, 44)
mango_laminas(d, 200, 300, 110, 130, tinta)
d.text((360, 200), 'MangoSol', font=F(118, 'black'), fill=tinta)
d.text((366, 360), 'Mango deshidratado sin azúcar ni sulfitos', font=F(31), fill=tinta)
d.text((366, 415), 'Dried mango slices · Product of Peru', font=F(31, 'reg'), fill=tinta)
d.rectangle([366, 480, 960, 545], outline=tinta, width=4)
d.text((386, 493), 'NETO 10 kg   LOTE 2026-11-0457', font=F(34), fill=tinta)
d.text((40, 590), 'Sol de Tambogrande S.A.C. · Sullana, Piura', font=F(28, 'reg'), fill=tinta)
im.save(OUT + 'caja_carton.jpg', quality=90)
Image.new('RGB', (64, 64), kraft).save(OUT + 'carton_liso.jpg', quality=90)


# ---------- letreros de área (identidad de la marca) ----------
def letrero_area(archivo, num, titulo, zona):
    im = Image.new('RGB', (2048, 400), OSC); d = ImageDraw.Draw(im)
    d.text((70, 200), num, font=F(240, 'black'), fill=NAR, anchor='lm')
    x = 130 + d.textlength(num, font=F(240, 'black'))
    t = 96
    while d.textlength(titulo, font=F(t)) > 2048 - x - 60:
        t -= 4
    d.text((x, 165), titulo, font=F(t), fill=CRE, anchor='lm')
    d.text((x + 4, 290), zona, font=F(56, 'reg'), fill=(174, 185, 176), anchor='lm')
    im.save(OUT + archivo, quality=92)


letrero_area('area4.jpg', '4', 'PELADO, LAMINADO Y PRETRATAMIENTO', 'Zona sucia · cofia, mascarilla y guantes')
letrero_area('area5b.jpg', '5B', 'TÚNEL DE SECADO (GLP)', 'Secado final · 60–65 °C · 8 a 10 h')
letrero_area('area6.jpg', '6', 'ENFRIADO Y SELECCIÓN FINAL', 'Zona limpia · acondicionado 24 h')
letrero_area('area7.jpg', '7', 'ENVASADO', 'Zona limpia · cajas de 10 kg')

# ---------- PCC 2 ----------
im = Image.new('RGB', (1024, 512), (245, 196, 0)); d = ImageDraw.Draw(im)
d.rectangle([14, 14, 1009, 497], outline=(20, 20, 20), width=14)
d.text((512, 150), 'PCC 2', font=F(170), fill=(20, 20, 20), anchor='mm')
d.text((512, 300), 'DETECTOR DE METALES · Fe 1.5 mm', font=F(56), fill=(20, 20, 20), anchor='mm')
d.text((512, 390), 'Producto rechazado: separar, revisar y registrar', font=F(36, 'reg'), fill=(20, 20, 20), anchor='mm')
im.save(OUT + 'letrero_pcc2.jpg', quality=92)


# ---------- letreros de puertas cerradas (señalética sanitaria) ----------
def puerta(archivo, texto, sub=''):
    im = Image.new('RGB', (1024, 256), (246, 246, 242)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 1023, 255], outline=OSC, width=10)
    d.text((512, 105 if sub else 128), texto, font=F(78), fill=OSC, anchor='mm')
    if sub:
        d.text((512, 190), sub, font=F(44, 'reg'), fill=(80, 90, 84), anchor='mm')
    im.save(OUT + archivo, quality=92)


puerta('p_area3.jpg', '3 · SELECCIÓN Y LAVADO', 'Zona sucia')
puerta('p_area8.jpg', '8 · ALMACÉN Y DESPACHO', 'Producto terminado')
puerta('p_lab.jpg', 'LABORATORIO DE CALIDAD', 'Humedad · aw · color')
puerta('p_ves.jpg', 'VESTUARIOS', 'Filtro sanitario · pediluvio')
puerta('p_residuos.jpg', 'SALIDA DE CÁSCARA Y PEPA', 'Hacia residuos orgánicos')
puerta('p_solar.jpg', '5A · PRESECADO SOLAR', 'Exterior')

# obligatorio (azul): EPP en zona limpia
im = Image.new('RGB', (768, 512), (255, 255, 255)); d = ImageDraw.Draw(im)
d.rectangle([0, 0, 767, 150], fill=(0, 92, 170))
d.text((384, 75), 'ZONA LIMPIA', font=F(84), fill=(255, 255, 255), anchor='mm')
for i, t in enumerate(['Cofia y mascarilla', 'Guantes y mandil', 'Lavarse las manos']):
    d.ellipse([60, 190 + i * 100, 140, 270 + i * 100], fill=(0, 92, 170))
    d.text((180, 230 + i * 100), t, font=F(54), fill=(20, 20, 20), anchor='lm')
im.save(OUT + 'epp.jpg', quality=92)


# ---------- pantallas ----------
def pantalla(archivo, lineas, verde=True):
    im = Image.new('RGB', (512, 320), (8, 18, 14)); d = ImageDraw.Draw(im)
    for i, (a, b) in enumerate(lineas):
        y = 28 + i * 66
        d.text((24, y), a, font=F(28 if i == 0 else 26, 'bold' if i == 0 else 'reg'), fill=(120, 230, 160) if i == 0 else (150, 190, 170))
        if b:
            d.text((488, y - 8), b, font=F(40), fill=(240, 250, 240), anchor='ra')
    im.save(OUT + archivo, quality=92)


pantalla('pantalla_detector.jpg', [('DETECTOR · PCC 2', ''), ('Estado', 'OK'), ('Fe', '1.5 mm'), ('Rechazos hoy', '2')])
pantalla('pantalla_selladora.jpg', [('SELLADORA DE BANDA', ''), ('Temperatura', '165 °C'), ('Velocidad', '8 m/min'), ('Cajas hoy', '64')])

letrero_area('area1.jpg', '1', 'RECEPCIÓN Y PESADO', 'Zona sucia · 9,000 kg/día de mango fresco')
letrero_area('area2.jpg', '2', 'ALMACÉN DE MATERIA PRIMA', 'Cámara fría · 12 a 14 °C')
letrero_area('area3.jpg', '3', 'SELECCIÓN Y LAVADO', 'Zona sucia · agua clorada a 100 ppm')
letrero_area('area8.jpg', '8', 'ALMACÉN DE PRODUCTO TERMINADO', 'Zona limpia · despacho en contenedor a Paita')
puerta('p_oficinas.jpg', 'OFICINAS', 'Administración y comercial')
pantalla('pantalla_camara.jpg', [('CÁMARA DE MP', ''), ('Temperatura', '13.0 °C'), ('Humedad rel.', '88 %'), ('Jabas', '412')])


def logo_decal(archivo, fondo, tinta, ancho=2048, alto=600):
    im = Image.new('RGB', (ancho, alto), fondo); d = ImageDraw.Draw(im)
    mango_laminas(d, 300, alto // 2, 190, 225, (240, 160, 48))
    d.text((560, alto // 2 - 60), 'MangoSol', font=F(250, 'black'), fill=tinta, anchor='lm')
    d.text((570, alto // 2 + 140), 'Sol de Tambogrande S.A.C. · Sullana, Piura', font=F(70, 'reg'), fill=tinta, anchor='lm')
    im.save(OUT + archivo, quality=92)


logo_decal('logo_camion.jpg', (244, 244, 240), OSC)
logo_decal('logo_contenedor.jpg', (24, 74, 120), CRE)
# fachada: letrero de la empresa sobre el ingreso de camiones
im = Image.new('RGB', (2048, 512), OSC); d = ImageDraw.Draw(im)
mango_laminas(d, 230, 256, 150, 178, NAR)
d.text((440, 200), 'SOL DE TAMBOGRANDE S.A.C.', font=F(120, 'black'), fill=CRE, anchor='lm')
d.text((446, 360), 'MangoSol · planta de mango deshidratado', font=F(64, 'reg'), fill=(174, 185, 176), anchor='lm')
im.save(OUT + 'fachada.jpg', quality=92)
print('ok')
