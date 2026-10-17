# Escena realista del área 5B (túnel de secado) para el prototipo del recorrido.
# Se ejecuta dentro de Blender:  exec(open(r'...\proto\blender\escena_tunel.py', encoding='utf-8').read())
# Coordenadas "del recorrido": x (este), zw (hacia el sur), h (altura). En Blender: (x, -zw, h).
import bpy, bmesh, math, os, random
from mathutils import Vector

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if '__file__' in dir() else \
    r'C:\Users\Asus\Documents\Formulacion de proyectos\presentacion\proto'
TEX = os.path.join(RAIZ, 'tex')
random.seed(5)

# ---------------- limpiar la escena (sin reiniciar Blender) ----------------
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras, bpy.data.images, bpy.data.node_groups):
    for x in list(coll):
        if x.users == 0:
            coll.remove(x)
col = bpy.context.scene.collection


def W(x, zw, h):
    return Vector((x, -zw, h))


# ---------------- materiales ----------------
def entrada(nodo, ident):
    return next(s for s in nodo.inputs if s.identifier == ident)


def nuevo_mat(nombre):
    m = bpy.data.materials.new(nombre)
    try:
        m.use_nodes = True
    except Exception:
        pass
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    return m, b


def mat_color(nombre, rgb, metal=0.0, rough=0.5, emision=None, fuerza=0.0):
    m, b = nuevo_mat(nombre)
    entrada(b, 'Base Color').default_value = (*rgb, 1)
    entrada(b, 'Metallic').default_value = metal
    entrada(b, 'Roughness').default_value = rough
    if emision:
        entrada(b, 'Emission Color').default_value = (*emision, 1)
        entrada(b, 'Emission Strength').default_value = fuerza
    return m


def imagen(archivo, color=True):
    im = bpy.data.images.load(os.path.join(TEX, archivo), check_existing=True)
    if not color:
        im.colorspace_settings.name = 'Non-Color'
    return im


def mat_pbr(nombre, diff, rough=None, nor=None, metal=0.0, fuerza_normal=1.0):
    m, b = nuevo_mat(nombre)
    nt = m.node_tree
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = imagen(diff)
    nt.links.new(t.outputs['Color'], entrada(b, 'Base Color'))
    if rough:
        r = nt.nodes.new('ShaderNodeTexImage'); r.image = imagen(rough, False)
        nt.links.new(r.outputs['Color'], entrada(b, 'Roughness'))
    if nor:
        n = nt.nodes.new('ShaderNodeTexImage'); n.image = imagen(nor, False)
        nm = nt.nodes.new('ShaderNodeNormalMap'); entrada(nm, 'Strength').default_value = fuerza_normal
        nt.links.new(n.outputs['Color'], entrada(nm, 'Color'))
        nt.links.new(nm.outputs['Normal'], entrada(b, 'Normal'))
    entrada(b, 'Metallic').default_value = metal
    return m


M = {
    'piso': mat_pbr('Piso epoxi', 'piso_epoxi_diff.jpg', 'concrete_floor_painted_rough_2k.jpg', 'concrete_floor_painted_nor_2k.jpg', fuerza_normal=.6),
    'pared': mat_pbr('Pared sanitaria', 'pared_blanca_diff.jpg', 'painted_concrete_rough_1k.jpg', 'painted_concrete_nor_1k.jpg', fuerza_normal=.4),
    'techo': mat_pbr('Techo calamina', 'corrugated_iron_diff_1k.jpg', 'corrugated_iron_rough_1k.jpg', 'corrugated_iron_nor_1k.jpg', metal=.6),
    'inox': mat_color('Acero inoxidable', (.78, .79, .80), metal=1.0, rough=.26),
    'inox_mate': mat_color('Inoxidable satinado', (.70, .71, .72), metal=1.0, rough=.45),
    'junta': mat_color('Junta de panel', (.18, .19, .20), rough=.6),
    'galv': mat_color('Galvanizado', (.62, .64, .66), metal=1.0, rough=.38),
    'viga': mat_color('Viga pintada', (.32, .35, .38), metal=.3, rough=.55),
    'quemador': mat_color('Quemador (pintura)', (.62, .12, .06), metal=.2, rough=.35),
    'gas': mat_color('Tubería de gas', (.85, .66, .05), metal=.2, rough=.4),
    'tablero': mat_color('Tablero RAL 7035', (.74, .75, .73), rough=.45),
    'caucho': mat_color('Caucho', (.03, .03, .03), rough=.8),
    'amarillo': mat_color('Pintura de seguridad', (.95, .72, .02), rough=.5),
    'led': mat_color('Luminaria LED', (1, 1, 1), emision=(1, .97, .92), fuerza=6.0),
    'zocalo': mat_color('Zócalo sanitario', (.28, .30, .30), rough=.4),
}


def mat_img(nombre, archivo, rough=.5, emis=0.0):
    m, b = nuevo_mat(nombre)
    t = m.node_tree.nodes.new('ShaderNodeTexImage'); t.image = imagen(archivo)
    m.node_tree.links.new(t.outputs['Color'], entrada(b, 'Base Color'))
    entrada(b, 'Roughness').default_value = rough
    if emis:
        m.node_tree.links.new(t.outputs['Color'], entrada(b, 'Emission Color'))
        entrada(b, 'Emission Strength').default_value = emis
    return m


M['pcc'] = mat_img('Letrero PCC 1', 'letrero_pcc1.jpg', rough=.35)
M['pantalla'] = mat_img('Pantalla del túnel', 'pantalla_tunel.jpg', rough=.2, emis=1.5)
M['bandeja'] = mat_img('Bandeja con mango seco', 'bandeja_seca.jpg', rough=.55)


# ---------------- geometría ----------------
def uv_mundo(ob, tile):
    """UV por proyección según la normal dominante, en metros / tile (texturas a escala real)."""
    me = ob.data
    bm = bmesh.new(); bm.from_mesh(me)
    uv = bm.loops.layers.uv.verify()
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for lp in f.loops:
            p = lp.vert.co
            u, v = ((p.y, p.z) if ax == 0 else (p.x, p.z) if ax == 1 else (p.x, p.y))
            lp[uv].uv = (u / tile, v / tile)
    bm.to_mesh(me); bm.free()


def caja(nombre, x0, x1, zw0, zw1, h0, h1, mat, tile=1.0, padre=None):
    me = bpy.data.meshes.new(nombre)
    ob = bpy.data.objects.new(nombre, me); col.objects.link(ob)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    bm.to_mesh(me); bm.free()
    ob.scale = (x1 - x0, zw1 - zw0, h1 - h0)
    ob.location = W((x0 + x1) / 2, (zw0 + zw1) / 2, (h0 + h1) / 2)
    # aplicar escala para que las normales y UV sean correctas
    me.transform(ob.matrix_basis); ob.matrix_basis.identity()
    uv_mundo(ob, tile)
    me.materials.append(mat)
    if padre:
        ob.parent = padre
    return ob


def cilindro(nombre, x, zw, h, r, largo, mat, eje='h', seg=24):
    """Cilindro centrado en (x, zw, h), con su eje vertical ('h') o a lo largo de 'x' o de 'zw'."""
    me = bpy.data.meshes.new(nombre)
    ob = bpy.data.objects.new(nombre, me); col.objects.link(ob)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=largo)
    bm.to_mesh(me); bm.free()
    ob.rotation_euler = {'h': (0, 0, 0), 'x': (0, math.pi / 2, 0), 'zw': (math.pi / 2, 0, 0)}[eje]
    ob.location = W(x, zw, h)
    me.transform(ob.matrix_basis); ob.matrix_basis.identity()
    uv_mundo(ob, .5)
    me.materials.append(mat)
    me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    return ob


def plano(nombre, x, zw, h, ancho, alto, mat, mira='-x'):
    """Plano vertical con la imagen derecha mirando hacia 'mira' ('-x', '+x', '+zw', '-zw')."""
    me = bpy.data.meshes.new(nombre)
    a, b = ancho / 2, alto / 2
    me.from_pydata([(-a, 0, -b), (a, 0, -b), (a, 0, b), (-a, 0, b)], [], [(0, 1, 2, 3)])
    uvl = me.uv_layers.new()
    for i, (u, v) in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uvl.data[i].uv = (u, v)
    ob = bpy.data.objects.new(nombre, me); col.objects.link(ob)
    rot = {'-x': -math.pi / 2, '+x': math.pi / 2, '+zw': 0, '-zw': math.pi}[mira]
    ob.rotation_euler = (0, 0, rot)
    ob.location = W(x, zw, h)
    me.materials.append(mat)
    return ob


def muro(nombre, eje_fijo, fijo, a, b, huecos, alto=4.4, t=.2):
    """Muro con huecos de puerta [(centro, ancho)] de 2.7 m de alto y dintel encima."""
    cur = a
    for c, w in sorted(huecos) + [(b + 1e9, 0)]:
        s, e = c - w / 2, c + w / 2
        fin = min(s, b)
        if fin - cur > .01:
            if eje_fijo == 'x':
                caja(nombre, fijo - t / 2, fijo + t / 2, cur, fin, 0, alto, M['pared'], 2)
            else:
                caja(nombre, cur, fin, fijo - t / 2, fijo + t / 2, 0, alto, M['pared'], 2)
        if e < b + 1e8:
            if eje_fijo == 'x':
                caja(nombre + ' dintel', fijo - t / 2, fijo + t / 2, s, e, 2.7, alto, M['pared'], 2)
            else:
                caja(nombre + ' dintel', s, e, fijo - t / 2, fijo + t / 2, 2.7, alto, M['pared'], 2)
        cur = e


# ---------------- nave del área 5B (x 33–40, zw 0–16) ----------------
caja('Piso', 33, 40, -0.5, 16.5, -.02, 0, M['piso'], 4)
muro('Muro oeste', 'x', 33, 0, 16, [(6.2, 3), (14.2, 3)])
muro('Muro este', 'x', 40, 0, 16, [(14.6, 2.4)])
muro('Muro norte', 'zw', 0, 33, 40, [])
muro('Muro sur', 'zw', 16, 33, 40, [])
for nombre, (x0, x1, z0, z1) in {'Zócalo O': (33.1, 33.14, 0, 16), 'Zócalo E': (39.86, 39.9, 0, 16)}.items():
    caja(nombre, x0, x1, z0, z1, 0, .12, M['zocalo'])
caja('Techo', 32.8, 40.2, -.2, 16.2, 4.4, 4.45, M['techo'], 1.5)
for zw in [1, 5, 9, 13]:  # vigas I del techo
    caja('Viga ala inf', 33, 40, zw - .08, zw + .08, 4.02, 4.04, M['viga'])
    caja('Viga alma', 33, 40, zw - .006, zw + .006, 4.04, 4.38, M['viga'])
    caja('Viga ala sup', 33, 40, zw - .08, zw + .08, 4.38, 4.4, M['viga'])
for zw in [2.5, 6.5, 10.5, 14.5]:  # luminarias LED lineales
    for x in [34.5, 38.5]:
        caja('Luminaria', x - .6, x + .6, zw - .09, zw + .09, 3.86, 3.92, M['inox_mate'])
        caja('LED', x - .58, x + .58, zw - .07, zw + .07, 3.855, 3.86, M['led'])

# ---------------- túnel de secado: paneles de inoxidable con juntas ----------------
X0, X1, Z0, Z1, HT = 34.6, 39.4, 1.0, 12.8, 2.8
caja('Túnel pared O', X0, X0 + .1, Z0, Z1, 0, HT, M['inox'], 1.2)
caja('Túnel pared E', X1 - .1, X1, Z0, Z1, 0, HT, M['inox'], 1.2)
caja('Túnel techo', X0, X1, Z0, Z1, HT - .1, HT, M['inox'], 1.2)
caja('Túnel fondo', X0, X1, Z0, Z0 + .1, 0, HT, M['inox'], 1.2)
caja('Túnel piso', X0 + .1, X1 - .1, Z0 + .1, Z1, 0, .02, M['inox_mate'], 1)
for zw in [z / 10 for z in range(22, 128, 12)]:  # juntas verticales cada 1.2 m
    caja('Junta O', X0 - .004, X0, zw - .01, zw + .01, 0, HT, M['junta'])
    caja('Junta E', X1, X1 + .004, zw - .01, zw + .01, 0, HT, M['junta'])
caja('Marco sup', X0, X1, Z1 - .02, Z1 + .08, HT - .35, HT, M['inox'])
caja('Marco O', X0, X0 + .2, Z1 - .02, Z1 + .08, 0, HT, M['inox'])
caja('Marco E', X1 - .2, X1, Z1 - .02, Z1 + .08, 0, HT, M['inox'])
# puertas abiertas a 90° hacia afuera, pegadas a los costados
caja('Puerta O', X0 - .09, X0 - .01, Z1 + .08, Z1 + 2.35, .05, HT - .4, M['inox'], 1.2)
caja('Puerta E', X1 + .01, X1 + .09, Z1 + .08, Z1 + 2.35, .05, HT - .4, M['inox'], 1.2)
for x in [X0 - .12, X1 + .12]:
    cilindro('Manija', x, Z1 + 2.1, 1.2, .015, .6, M['inox'])
# sello de silicona en el marco
caja('Sello', X0 + .2, X1 - .2, Z1 + .08, Z1 + .1, HT - .37, HT - .35, M['caucho'])

# ---------------- quemador GLP, ventiladores y ductos sobre el túnel ----------------
caja('Quemador carcasa', 35.4, 38.6, 1.3, 3.1, HT, HT + .8, M['quemador'])
cilindro('Quemador', 37, 3.27, HT + .4, .22, .35, M['quemador'], eje='zw')
for x in [35.6, 38.4]:
    cilindro('Ventilador', x, 5.0, HT + .275, .45, .55, M['galv'])
    cilindro('Rejilla', x, 5.0, HT + .56, .43, .02, M['junta'])
cilindro('Ducto', 37, 7.45, HT + .32, .28, 8.7, M['galv'], eje='zw')  # a lo largo del túnel
for zw in [4.5, 7.5, 10.5]:
    caja('Abrazadera', 36.68, 37.32, zw - .03, zw + .03, HT, HT + .62, M['viga'])
# tren de gas: tubería amarilla desde el muro oeste al quemador
cilindro('Gas vertical', 33.2, 2.0, (HT + .5) / 2, .03, HT + .5, M['gas'])
cilindro('Gas horizontal', 34.3, 2.0, HT + .5, .03, 2.2, M['gas'], eje='x')
caja('Válvula', 33.14, 33.26, 1.92, 2.08, 1.3, 1.45, M['quemador'])

# ---------------- tablero de control y letrero PCC 1 ----------------
caja('Tablero', 34.25, 34.6, 9.4, 10.4, 1.0, 1.9, M['tablero'])
plano('Pantalla', 34.245, 9.9, 1.6, .5, .31, M['pantalla'], mira='-x')
for zw, c in [(9.65, (.1, .7, .2)), (10.15, (.8, .1, .1))]:
    cilindro('Botón', 34.23, zw, 1.22, .03, .04, mat_color('Botón', c, rough=.3), eje='x')
plano('Letrero PCC 1', X0 - .015, 11.6, 1.75, 1.0, .5, M['pcc'], mira='-x')

# ---------------- carros de secado con bandejas ----------------
def carro(x, zw, nombre='Carro'):
    piezas = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            piezas.append(caja(nombre + ' poste', x + sx * .42 - .015, x + sx * .42 + .015, zw + sz * .62 - .015, zw + sz * .62 + .015, .12, 1.95, M['inox']))
            piezas.append(cilindro(nombre + ' rueda', x + sx * .38, zw + sz * .55, .055, .055, .03, M['caucho'], eje='x', seg=16))
    for k in range(12):
        h = .25 + k * .14
        piezas.append(caja(nombre + ' bandeja', x - .4, x + .4, zw - .6, zw + .6, h, h + .012, M['bandeja'], 1.2))
        for sx in (-1, 1):
            piezas.append(caja(nombre + ' riel', x + sx * .41 - .01, x + sx * .41 + .01, zw - .6, zw + .6, h - .01, h + .005, M['inox']))
    piezas.append(caja(nombre + ' marco sup', x - .44, x + .44, zw - .64, zw + .64, 1.95, 1.98, M['inox']))
    return piezas


for zw in [11.6, 10.2, 8.8, 7.4, 6.0, 4.6, 3.2, 1.8]:
    for x in (35.9, 38.1):
        carro(x, zw)
carro(38.4, 14.0, 'Carro afuera')

# ---------------- señalización de piso y canaleta ----------------
for (x0, x1, z0, z1) in [(X0, X1, 15.3, 15.38), (X0, X0 + .08, Z1 + .1, 15.38), (X1 - .08, X1, Z1 + .1, 15.38)]:
    caja('Franja amarilla', x0, x1, z0, z1, 0, .002, M['amarillo'])
caja('Canaleta', 33.6, 39.8, 15.8, 15.95, -.001, .001, M['inox_mate'])

# ---------------- iluminación y cámara (para el render de referencia) ----------------
w = bpy.context.scene.world or bpy.data.worlds.new('Mundo')
bpy.context.scene.world = w
try:
    w.use_nodes = True
except Exception:
    pass
nt = w.node_tree
if nt is None:
    w.use_nodes = True; nt = w.node_tree
env = nt.nodes.new('ShaderNodeTexEnvironment')
env.image = bpy.data.images.load(os.path.join(TEX, 'empty_warehouse_01_1k.hdr'), check_existing=True)
bg = next(n for n in nt.nodes if n.type == 'BACKGROUND')
nt.links.new(env.outputs['Color'], entrada(bg, 'Color'))
entrada(bg, 'Strength').default_value = .25
for zw in [2.5, 6.5, 10.5, 14.5]:
    for x in [34.5, 38.5]:
        L = bpy.data.lights.new('LED', 'AREA'); L.shape = 'RECTANGLE'; L.size, L.size_y = 1.16, .14
        L.energy = 260; L.color = (1, .96, .9)
        o = bpy.data.objects.new('Luz LED', L); col.objects.link(o); o.location = W(x, zw, 3.84)
cam = bpy.data.cameras.new('Cámara'); cam.lens = 22
co = bpy.data.objects.new('Cámara', cam); col.objects.link(co)
co.location = W(36.4, 15.75, 1.65)
dir_ = (W(37.6, 9.0, 1.25) - co.location)
co.rotation_euler = dir_.to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = co
print('objetos:', len(bpy.data.objects))
