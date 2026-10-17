# Funciones comunes para modelar la planta en Blender (se cargan con exec antes de cada escena).
# Coordenadas "del recorrido": x (este), zw (hacia el sur), h (altura). En Blender: (x, -zw, h).
import bpy, bmesh, math, os, random, json
from mathutils import Vector, Matrix

PROTO = r'C:\Users\Asus\Documents\Formulacion de proyectos\presentacion\proto'
TEX = os.path.join(PROTO, 'tex')
COLS = []      # rectángulos sólidos [x0, x1, zw0, zw1] para las colisiones en la web
LUCES = []     # luminarias LED (x, zw) para iluminar el horneado


def limpiar():
    for s in list(bpy.data.scenes):
        if s.name != 'Scene':
            bpy.data.scenes.remove(s)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras, bpy.data.images, bpy.data.textures):
        for x in list(coll):
            if x.users == 0:
                coll.remove(x)
    COLS.clear(); LUCES.clear()


def col():
    return bpy.data.scenes['Scene'].collection


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
    return m, next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')


def mat_color(nombre, rgb, metal=0.0, rough=0.5, emision=None, fuerza=0.0, alfa=1.0):
    m, b = nuevo_mat(nombre)
    entrada(b, 'Base Color').default_value = (*rgb, 1)
    entrada(b, 'Metallic').default_value = metal
    entrada(b, 'Roughness').default_value = rough
    if emision:
        entrada(b, 'Emission Color').default_value = (*emision, 1)
        entrada(b, 'Emission Strength').default_value = fuerza
    if alfa < 1:
        entrada(b, 'Alpha').default_value = alfa
        try:
            m.surface_render_method = 'BLENDED'
        except Exception:
            m.blend_method = 'BLEND'
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


def mat_img(nombre, archivo, rough=.5, emis=0.0):
    m, b = nuevo_mat(nombre)
    t = m.node_tree.nodes.new('ShaderNodeTexImage'); t.image = imagen(archivo)
    m.node_tree.links.new(t.outputs['Color'], entrada(b, 'Base Color'))
    entrada(b, 'Roughness').default_value = rough
    if emis:
        m.node_tree.links.new(t.outputs['Color'], entrada(b, 'Emission Color'))
        entrada(b, 'Emission Strength').default_value = emis
    return m


M = {}


def crear_materiales():
    M.clear()
    M.update({
        'piso': mat_pbr('Piso epoxi', 'piso_epoxi_diff.jpg', 'concrete_floor_painted_rough_2k.jpg', 'concrete_floor_painted_nor_2k.jpg', fuerza_normal=.6),
        'pared': mat_pbr('Pared sanitaria', 'pared_blanca_diff.jpg', 'painted_concrete_rough_1k.jpg', 'painted_concrete_nor_1k.jpg', fuerza_normal=.4),
        'techo': mat_pbr('Techo calamina', 'corrugated_iron_diff_1k.jpg', 'corrugated_iron_rough_1k.jpg', 'corrugated_iron_nor_1k.jpg', metal=.6),
        'inox': mat_color('Acero inoxidable', (.78, .79, .80), metal=1.0, rough=.26),
        'inox_mate': mat_color('Inoxidable satinado', (.70, .71, .72), metal=1.0, rough=.45),
        'junta': mat_color('Junta de panel', (.18, .19, .20), rough=.6),
        'galv': mat_color('Galvanizado', (.62, .64, .66), metal=1.0, rough=.38),
        'viga': mat_color('Viga pintada', (.32, .35, .38), metal=.3, rough=.55),
        'quemador': mat_color('Pintura roja', (.62, .12, .06), metal=.2, rough=.35),
        'gas': mat_color('Tubería de gas', (.85, .66, .05), metal=.2, rough=.4),
        'tablero': mat_color('Tablero RAL 7035', (.74, .75, .73), rough=.45),
        'caucho': mat_color('Caucho', (.03, .03, .03), rough=.8),
        'faja': mat_color('Faja sanitaria', (.12, .13, .14), rough=.55),
        'amarillo': mat_color('Pintura de seguridad', (.95, .72, .02), rough=.5),
        'led': mat_color('Luminaria LED', (1, 1, 1), emision=(1, .97, .92), fuerza=6.0),
        'zocalo': mat_color('Zócalo sanitario', (.28, .30, .30), rough=.4),
        'vidrio': mat_color('Vidrio esmerilado', (.86, .9, .9), rough=.3, alfa=.55),
        'puerta': mat_color('Puerta sanitaria', (.86, .88, .87), rough=.35),
        'hdpe': mat_color('Tabla HDPE', (.93, .93, .9), rough=.6),
        'verde': mat_color('Jaba verde', (.08, .32, .15), rough=.5),
        'azul': mat_color('Jaba azul', (.05, .18, .42), rough=.5),
        'pulpa': mat_color('Pulpa de mango', (.96, .58, .07), rough=.3),
        'piel1': mat_color('Cáscara verde-amarilla', (.55, .62, .12), rough=.35),
        'piel2': mat_color('Cáscara amarilla', (.88, .68, .1), rough=.35),
        'piel3': mat_color('Cáscara roja', (.62, .16, .07), rough=.35),
        'pepa': mat_color('Pepa', (.82, .75, .55), rough=.7),
        'liquido': mat_color('Solución cítrica', (.9, .85, .55), rough=.05, alfa=.75),
        'agua': mat_color('Agua clorada', (.55, .75, .8), rough=.05, alfa=.7),
        'kraft': mat_img('Cartón liso', 'carton_liso.jpg', rough=.8),
        'caja': mat_img('Cartón impreso', 'caja_carton.jpg', rough=.8),
        'bolsa': mat_color('Bolsa PE', (.92, .93, .95), rough=.2, alfa=.6),
        'madera': mat_color('Pallet', (.5, .36, .22), rough=.8),
        'rojo': mat_color('Luz roja', (.8, .05, .04), emision=(1, .1, .05), fuerza=2.0),
        'ambar': mat_color('Luz ámbar', (.8, .5, .02), rough=.3),
        'verde_luz': mat_color('Luz verde', (.1, .8, .2), emision=(.2, 1, .3), fuerza=3.0),
        'seco': mat_color('Mango seco', (.62, .26, .04), rough=.45),
        'bandeja': mat_img('Bandeja con mango seco', 'bandeja_seca.jpg', rough=.55),
    })


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


def _registrar(x0, x1, z0, z1, h0, h1):
    if h0 < 1.7 and h1 > .25:
        COLS.append([round(x0, 3), round(x1, 3), round(z0, 3), round(z1, 3)])


def caja(nombre, x0, x1, zw0, zw1, h0, h1, mat, tile=1.0, solido=False):
    me = bpy.data.meshes.new(nombre)
    ob = bpy.data.objects.new(nombre, me); col().objects.link(ob)
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bm.to_mesh(me); bm.free()
    ob.scale = (x1 - x0, zw1 - zw0, h1 - h0)
    ob.location = W((x0 + x1) / 2, (zw0 + zw1) / 2, (h0 + h1) / 2)
    me.transform(ob.matrix_basis); ob.matrix_basis.identity()
    uv_mundo(ob, tile)
    me.materials.append(mat)
    if solido:
        _registrar(x0, x1, zw0, zw1, h0, h1)
    return ob


def cilindro(nombre, x, zw, h, r, largo, mat, eje='h', seg=24, solido=False, tapa=True):
    """Cilindro centrado en (x, zw, h), con su eje vertical ('h') o a lo largo de 'x' o de 'zw'."""
    me = bpy.data.meshes.new(nombre)
    ob = bpy.data.objects.new(nombre, me); col().objects.link(ob)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=tapa, segments=seg, radius1=r, radius2=r, depth=largo)
    bm.to_mesh(me); bm.free()
    ob.rotation_euler = {'h': (0, 0, 0), 'x': (0, math.pi / 2, 0), 'zw': (math.pi / 2, 0, 0)}[eje]
    ob.location = W(x, zw, h)
    me.transform(ob.matrix_basis); ob.matrix_basis.identity()
    uv_mundo(ob, .5)
    me.materials.append(mat)
    me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    if solido:
        if eje == 'h':
            _registrar(x - r, x + r, zw - r, zw + r, h - largo / 2, h + largo / 2)
        elif eje == 'x':
            _registrar(x - largo / 2, x + largo / 2, zw - r, zw + r, h - r, h + r)
        else:
            _registrar(x - r, x + r, zw - largo / 2, zw + largo / 2, h - r, h + r)
    return ob


def esfera(nombre, x, zw, h, rx, rz, rh, mat, seg=16):
    me = bpy.data.meshes.new(nombre)
    ob = bpy.data.objects.new(nombre, me); col().objects.link(ob)
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=1); bm.to_mesh(me); bm.free()
    ob.scale = (rx, rz, rh); ob.location = W(x, zw, h)
    me.transform(ob.matrix_basis); ob.matrix_basis.identity()
    uv_mundo(ob, .3)
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
    ob = bpy.data.objects.new(nombre, me); col().objects.link(ob)
    ob.rotation_euler = (0, 0, {'-x': -math.pi / 2, '+x': math.pi / 2, '+zw': 0, '-zw': math.pi}[mira])
    ob.location = W(x, zw, h)
    me.materials.append(mat)
    return ob


def muro(nombre, eje, fijo, a, b, huecos=(), alto=4.4, t=.2, ventana=False):
    """Muro con huecos [(centro, ancho)] de 2.7 m. Con ventana=True lleva vidrio esmerilado entre 1.1 y 2.4 m."""
    def tramo(s, e, h0, h1, mat, solido, n=None):
        if e - s < .01:
            return
        if eje == 'x':
            caja(n or nombre, fijo - t / 2, fijo + t / 2, s, e, h0, h1, mat, 2, solido)
        else:
            caja(n or nombre, s, e, fijo - t / 2, fijo + t / 2, h0, h1, mat, 2, solido)
    cur = a
    for c, w in sorted(huecos) + [(1e9, 0)]:
        s, e = c - w / 2, c + w / 2
        fin = min(s, b)
        if ventana:
            tramo(cur, fin, 0, 1.1, M['pared'], True); tramo(cur, fin, 1.1, 2.4, M['vidrio'], False, 'Ventana')
            tramo(cur, fin, 2.4, alto, M['pared'], False)
            for p in [cur + .02, fin - .02]:  # perfiles de la ventana
                tramo(p - .02, p + .02, 1.1, 2.4, M['inox_mate'], False, 'Ventana perfil')
        else:
            tramo(cur, fin, 0, alto, M['pared'], True)
        if c < 1e8:
            tramo(s, e, 2.7, alto, M['pared'], False)
        cur = e


def puerta_cerrada(eje, fijo, centro, ancho, letrero, lado):
    """Hoja de puerta cerrada en un hueco, con letrero encima; 'lado' es hacia dónde mira el letrero."""
    t = .06
    if eje == 'x':
        caja('Puerta', fijo - t / 2, fijo + t / 2, centro - ancho / 2 + .03, centro + ancho / 2 - .03, 0, 2.66, M['puerta'], 1, True)
        caja('Visor', fijo - t / 2 - .005, fijo + t / 2 + .005, centro - .2, centro + .2, 1.4, 1.8, M['vidrio'])
        x = fijo + (.12 if lado == '+x' else -.12)
        plano('Letrero puerta', x, centro, 2.95, 1.3, .325, mat_img('Letrero ' + letrero, letrero, rough=.4), lado)
    else:
        caja('Puerta', centro - ancho / 2 + .03, centro + ancho / 2 - .03, fijo - t / 2, fijo + t / 2, 0, 2.66, M['puerta'], 1, True)
        caja('Visor', centro - .2, centro + .2, fijo - t / 2 - .005, fijo + t / 2 + .005, 1.4, 1.8, M['vidrio'])
        zw = fijo + (.12 if lado == '+zw' else -.12)
        plano('Letrero puerta', centro, zw, 2.95, 1.3, .325, mat_img('Letrero ' + letrero, letrero, rough=.4), lado)


def faja(x0, x1, zw, h=.9, ancho=.6):
    """Faja transportadora sanitaria a lo largo de x, con bastidor, guardas, rodillos y patas."""
    caja('Faja bastidor', x0, x1, zw - ancho / 2, zw + ancho / 2, h - .14, h - .02, M['inox_mate'], 1, True)
    caja('Faja banda', x0 + .05, x1 - .05, zw - ancho / 2 + .04, zw + ancho / 2 - .04, h - .02, h, M['faja'])
    for s in (-1, 1):
        caja('Faja guarda', x0, x1, zw + s * ancho / 2 - .015, zw + s * ancho / 2 + .015, h - .02, h + .06, M['inox'])
    for x in (x0 + .05, x1 - .05):
        cilindro('Faja rodillo', x, zw, h - .05, .055, ancho - .1, M['inox'], eje='zw')
    n = max(2, int((x1 - x0) / 1.4) + 1)
    for i in range(n):
        x = x0 + .1 + i * (x1 - x0 - .2) / (n - 1)
        for s in (-1, 1):
            caja('Faja pata', x - .02, x + .02, zw + s * (ancho / 2 - .05) - .02, zw + s * (ancho / 2 - .05) + .02, 0, h - .14, M['inox_mate'])


def mesa(cx, czw, largo, fondo, h=.9, solido=True):
    caja('Mesa tablero', cx - largo / 2, cx + largo / 2, czw - fondo / 2, czw + fondo / 2, h - .04, h, M['inox'], 1, solido)
    caja('Mesa repisa', cx - largo / 2 + .05, cx + largo / 2 - .05, czw - fondo / 2 + .05, czw + fondo / 2 - .05, .18, .2, M['inox_mate'])
    for sx in (-1, 1):
        for sz in (-1, 1):
            caja('Mesa pata', cx + sx * (largo / 2 - .05) - .02, cx + sx * (largo / 2 - .05) + .02,
                 czw + sz * (fondo / 2 - .05) - .02, czw + sz * (fondo / 2 - .05) + .02, 0, h - .04, M['inox_mate'])


def carro(x, zw, nombre='Carro', solido=True):
    for sx in (-1, 1):
        for sz in (-1, 1):
            caja(nombre + ' poste', x + sx * .42 - .015, x + sx * .42 + .015, zw + sz * .62 - .015, zw + sz * .62 + .015, .12, 1.95, M['inox'])
            cilindro(nombre + ' rueda', x + sx * .38, zw + sz * .55, .055, .055, .03, M['caucho'], eje='x', seg=16)
    for k in range(12):
        h = .25 + k * .14
        caja(nombre + ' bandeja', x - .4, x + .4, zw - .6, zw + .6, h, h + .012, M['bandeja'], 1.2)
        for sx in (-1, 1):
            caja(nombre + ' riel', x + sx * .41 - .01, x + sx * .41 + .01, zw - .6, zw + .6, h - .01, h + .005, M['inox'])
    caja(nombre + ' marco sup', x - .44, x + .44, zw - .64, zw + .64, 1.95, 1.98, M['inox'])
    if solido:
        _registrar(x - .45, x + .45, zw - .65, zw + .65, 0, 2)


def jaba(x, zw, h0=0, mat=None, contenido=None):
    """Jaba plástica de 0.55 × 0.38 × 0.3 m, con contenido opcional ('mango' o 'cascara')."""
    m = mat or M['verde']
    caja('Jaba fondo', x - .275, x + .275, zw - .19, zw + .19, h0, h0 + .02, m)
    for s in (-1, 1):
        caja('Jaba lado', x - .275, x + .275, zw + s * .19 - .012, zw + s * .19 + .012, h0, h0 + .3, m)
        caja('Jaba lado', x + s * .275 - .012, x + s * .275 + .012, zw - .19, zw + .19, h0, h0 + .3, m)
    if contenido == 'mango':
        for i in range(4):
            for j in range(3):
                mango(x - .2 + i * .135 + random.uniform(-.01, .01), zw - .12 + j * .12, h0 + .24 + random.uniform(0, .03))
    elif contenido == 'cascara':
        for _ in range(16):
            cascara(x + random.uniform(-.21, .21), zw + random.uniform(-.13, .13), h0 + .2 + random.uniform(0, .07))
    _registrar(x - .28, x + .28, zw - .2, zw + .2, h0, h0 + .3)


def mango(x, zw, h, rot=None):
    o = esfera('Mango', x, zw, h, .062, .048, .045, random.choice([M['piel1'], M['piel2'], M['piel2'], M['piel3']]), seg=14)
    o.data.transform(Matrix.Translation(-W(x, zw, h)))
    o.data.transform(Matrix.Rotation(rot if rot is not None else random.uniform(0, 6.28), 4, 'Z'))
    o.data.transform(Matrix.Translation(W(x, zw, h)))
    return o


def mitad(x, zw, h):
    """Cachete de mango pelado (pulpa) sobre la mesa."""
    o = esfera('Cachete', x, zw, h, .055, .04, .022, M['pulpa'], seg=14)
    return o


def cascara(x, zw, h):
    me = bpy.data.meshes.new('Cáscara'); bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=5, radius=1)
    for v in list(bm.verts):
        if v.co.z < -.1:
            bm.verts.remove(v)
    for v in bm.verts:
        v.co.x *= .05; v.co.y *= .025; v.co.z *= .012
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('Cáscara', me); col().objects.link(ob)
    ob.rotation_euler = (random.uniform(-.6, .6), random.uniform(-.6, .6), random.uniform(0, 6.28))
    ob.location = W(x, zw, h)
    me.transform(ob.matrix_basis); ob.matrix_basis.identity()
    me.materials.append(random.choice([M['piel1'], M['piel2'], M['piel3']]))
    me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    return ob


def lamina_fresca(x, zw, h):
    o = esfera('Lámina', x, zw, h, .035, .022, .004, M['pulpa'], seg=10)
    o.data.transform(Matrix.Translation(-W(x, zw, h)))
    o.data.transform(Matrix.Rotation(random.uniform(-.5, .5), 4, 'Z'))
    o.data.transform(Matrix.Translation(W(x, zw, h)))
    return o


def caja_carton(x, zw, h0, girar=False):
    """Caja de 10 kg: 0.40 × 0.30 × 0.25 m con la cara impresa hacia +zw (o hacia +x si girar)."""
    ax, az = (.30, .40) if girar else (.40, .30)
    caja('Caja', x - ax / 2, x + ax / 2, zw - az / 2, zw + az / 2, h0, h0 + .25, M['kraft'])
    if girar:
        plano('Caja impresa', x + ax / 2 + .002, zw, h0 + .125, .4, .25, M['caja'], '+x')
    else:
        plano('Caja impresa', x, zw + az / 2 + .002, h0 + .125, .4, .25, M['caja'], '+zw')


def luminaria(x, zw, h=3.9):
    caja('Luminaria', x - .6, x + .6, zw - .09, zw + .09, h - .04, h + .02, M['inox_mate'])
    caja('LED', x - .58, x + .58, zw - .07, zw + .07, h - .045, h - .04, M['led'])
    LUCES.append((x, zw, h))
