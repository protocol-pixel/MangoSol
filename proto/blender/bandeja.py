# Renderiza desde arriba una bandeja real (malla de acero + láminas de mango deshidratado en 3D)
# y la guarda como textura: proto/tex/bandeja_seca.jpg. Usa una escena aparte llamada "Bandeja".
import bpy, bmesh, math, os, random
from mathutils import Vector

TEX = r'C:\Users\Asus\Documents\Formulacion de proyectos\presentacion\proto\tex'
random.seed(11)

if 'Bandeja' in bpy.data.scenes:
    sc = bpy.data.scenes['Bandeja']
    for o in list(sc.collection.objects):
        bpy.data.objects.remove(o, do_unlink=True)
else:
    sc = bpy.data.scenes.new('Bandeja')
C = sc.collection


def ent(n, ident):
    return next(s for s in n.inputs if s.identifier == ident)


def mat(nombre):
    m = bpy.data.materials.get(nombre) or bpy.data.materials.new(nombre)
    try:
        m.use_nodes = True
    except Exception:
        pass
    return m, next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')


inox, b = mat('Bandeja inox')
ent(b, 'Base Color').default_value = (.6, .61, .62, 1); ent(b, 'Metallic').default_value = 1; ent(b, 'Roughness').default_value = .45

# mango deshidratado: color con variación (ruido), translucidez y arrugas por relieve
mango, b = mat('Mango deshidratado')
nt = mango.node_tree
ruido = nt.nodes.new('ShaderNodeTexNoise'); ent(ruido, 'Scale').default_value = 18; ent(ruido, 'Detail').default_value = 8
rampa = nt.nodes.new('ShaderNodeValToRGB')
rampa.color_ramp.elements[0].color = (.36, .08, .01, 1)
rampa.color_ramp.elements[1].color = (.80, .30, .03, 1)
nt.links.new(ruido.outputs['Fac'], rampa.inputs['Fac'])
nt.links.new(rampa.outputs['Color'], ent(b, 'Base Color'))
ent(b, 'Roughness').default_value = .42
try:
    ent(b, 'Subsurface Weight').default_value = .12
    ent(b, 'Subsurface Radius').default_value = (1.0, .35, .08)
    ent(b, 'Subsurface Scale').default_value = .0015
except StopIteration:
    pass
arr = nt.nodes.new('ShaderNodeTexNoise'); ent(arr, 'Scale').default_value = 70; ent(arr, 'Detail').default_value = 6
rel = nt.nodes.new('ShaderNodeBump'); ent(rel, 'Strength').default_value = .55
nt.links.new(arr.outputs['Fac'], ent(rel, 'Height'))
nt.links.new(rel.outputs['Normal'], ent(b, 'Normal'))

fondo, b = mat('Fondo bandeja')
ent(b, 'Base Color').default_value = (.03, .03, .03, 1); ent(b, 'Roughness').default_value = .9


def objeto(nombre, me, m):
    o = bpy.data.objects.new(nombre, me); C.objects.link(o); me.materials.append(m); return o


# fondo oscuro (lo que se ve entre los alambres)
me = bpy.data.meshes.new('fondo'); bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1)
bm.to_mesh(me); bm.free(); o = objeto('Fondo', me, fondo); o.scale = (.5, .7, 1); o.location.z = -.03

# malla de alambre de 3 mm cada 12 mm, en un solo mesh
A, L, PASO, R = .8, 1.2, .012, .0012
me = bpy.data.meshes.new('malla'); bm = bmesh.new()
for k in range(int(A / PASO) + 1):
    x = -A / 2 + k * PASO
    m4 = __import__('mathutils').Matrix
    bmesh.ops.create_cone(bm, cap_ends=False, segments=6, radius1=R, radius2=R, depth=L,
                          matrix=m4.Translation((x, 0, 0)) @ m4.Rotation(math.pi / 2, 4, 'X'))
for k in range(int(L / PASO) + 1):
    y = -L / 2 + k * PASO
    bmesh.ops.create_cone(bm, cap_ends=False, segments=6, radius1=R, radius2=R, depth=A,
                          matrix=m4.Translation((0, y, R * 2)) @ m4.Rotation(math.pi / 2, 4, 'Y'))
bm.to_mesh(me); bm.free(); objeto('Malla', me, inox)
me = bpy.data.meshes.new('borde'); bm = bmesh.new()
for (cx, cy, sx, sy) in [(0, L / 2, A, .02), (0, -L / 2, A, .02), (A / 2, 0, .02, L), (-A / 2, 0, .02, L)]:
    bmesh.ops.create_cube(bm, size=1, matrix=m4.Translation((cx, cy, .004)) @ m4.Diagonal((sx, sy, .012, 1)))
bm.to_mesh(me); bm.free(); objeto('Borde', me, inox)

# láminas: cada una con contorno irregular (ruido en el radio), 6–9 cm de largo y 3–5 cm de ancho
def lamina(largo, ancho):
    me = bpy.data.meshes.new('lamina'); bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=10, radius=1)
    f1, f2, f3 = (random.uniform(0, 6.28) for _ in range(3))
    curva = random.uniform(-.012, .012)
    for v in bm.verts:
        t = math.atan2(v.co.y, v.co.x)
        k = 1 + .14 * math.sin(2 * t + f1) + .07 * math.sin(5 * t + f2) + .04 * math.sin(9 * t + f3)
        x, y = v.co.x * ancho / 2 * k, v.co.y * largo / 2 * k
        v.co = (x, y, v.co.z * .0028 + curva * (y / largo) ** 2 * 4 + .002 * math.sin(x * 90 + f2))
    bm.to_mesh(me); bm.free()
    me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    return me


PX, PY = .062, .088
for i in range(int(A / PX)):
    for j in range(int(L / PY)):
        if random.random() < .08:
            continue
        o = objeto('Lamina', lamina(random.uniform(.06, .09), random.uniform(.03, .05)), mango)
        o.location = (-A / 2 + (i + .5) * PX + random.uniform(-.01, .01),
                      -L / 2 + (j + .5) * PY + random.uniform(-.012, .012), .0095)
        o.rotation_euler = (0, 0, random.uniform(-.45, .45) + (math.pi / 2 if random.random() < .15 else 0))


# cámara ortográfica cenital y luz suave
cam = bpy.data.cameras.new('cam bandeja'); cam.type = 'ORTHO'; cam.ortho_scale = L
co = bpy.data.objects.new('Cam bandeja', cam); C.objects.link(co); co.location = (0, 0, 1)
sc.camera = co
lz = bpy.data.lights.new('luz bandeja', 'AREA'); lz.size = 2.0; lz.energy = 70
lo = bpy.data.objects.new('Luz bandeja', lz); C.objects.link(lo); lo.location = (.3, -.4, 1.4)
lo.rotation_euler = (.25, .18, 0)
w = bpy.data.worlds.get('Mundo bandeja') or bpy.data.worlds.new('Mundo bandeja'); sc.world = w
try:
    w.use_nodes = True
except Exception:
    pass
bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
ent(bg, 'Color').default_value = (.5, .5, .5, 1); ent(bg, 'Strength').default_value = .12

sc.render.engine = 'CYCLES'; sc.cycles.samples = 128; sc.cycles.use_denoising = True
sc.cycles.device = bpy.context.scene.cycles.device
sc.render.resolution_x, sc.render.resolution_y = 1024, 1536
sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 90
try:
    sc.view_settings.view_transform = 'Standard'
except TypeError:
    pass
sc.render.filepath = os.path.join(TEX, 'bandeja_seca.jpg')
bpy.ops.render.render(write_still=True, scene=sc.name)
print('bandeja lista')
