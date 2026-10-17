# Reconstruye las áreas 4–7, precalcula la luz (lightmaps) de piso, muros y techo, y exporta proto/areas.glb.
import bpy, os
import numpy as np

BL = r'C:\Users\Asus\Documents\Formulacion de proyectos\presentacion\proto\blender'
exec(open(os.path.join(BL, 'escena_planta.py'), encoding='utf-8').read())

sc = bpy.data.scenes['Scene']
bpy.context.window.scene = sc
vl = bpy.context.view_layer


def unir(cond, nombre):
    obs = [o for o in sc.objects if o.type == 'MESH' and cond(o)]
    for o in sc.objects:
        o.select_set(False)
    for o in obs:
        o.select_set(True)
    vl.objects.active = obs[0]
    if len(obs) > 1:
        bpy.ops.object.join()
    ob = vl.objects.active
    ob.name = nombre; ob.data.name = nombre
    return ob


HORNEADO = {'Piso': 4096, 'Muros': 4096, 'Techo': 1024, 'Suelo': 2048}
unir(lambda o: o.name.startswith(('Muro', 'Zócalo')), 'Muros')
unir(lambda o: o.name.startswith('Techo'), 'Techo')
# los planos con imagen (letreros, logos, pantallas) quedan aparte: al unirlos se perdían sus coordenadas UV
PLANOS = ('Letrero', 'Fachada', 'Logo', 'Pantalla', 'EPP', 'Indicador', 'Termómetro', 'Caja impresa', 'Display')
unir(lambda o: o.name not in HORNEADO and not o.name.startswith(PLANOS), 'Equipos')
SOLO_EXPORTAR = globals().get('SOLO_EXPORTAR', False)  # True: reutiliza los lightmaps ya horneados

sc.render.engine = 'CYCLES'
sc.cycles.device = 'GPU'
sc.cycles.samples = 256
sc.cycles.use_denoising = True
sc.render.bake.margin = 8
ESCALA = .35  # se guarda a 0.35× para no saturar; en three.js lightMapIntensity = 1/0.35
for nombre, res in HORNEADO.items():
    ob = sc.objects[nombre]; me = ob.data
    if 'luz' not in me.uv_layers:
        me.uv_layers.new(name='luz')
    for o in sc.objects:
        o.select_set(False)
    ob.select_set(True); vl.objects.active = ob
    me.uv_layers.active = me.uv_layers['luz']
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.lightmap_pack(PREF_CONTEXT='ALL_FACES', PREF_MARGIN_DIV=0.2)
    bpy.ops.object.mode_set(mode='OBJECT')
    img = bpy.data.images.new('luz_' + nombre, res, res, float_buffer=True)
    nodos = []
    for slot in ob.material_slots:
        nt = slot.material.node_tree
        n = nt.nodes.new('ShaderNodeTexImage'); n.image = img
        nt.nodes.active = n; nodos.append((nt, n))
    if SOLO_EXPORTAR:
        for nt, n in nodos:
            nt.nodes.remove(n)
        me.uv_layers.active = me.uv_layers[0]
        continue
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT', 'INDIRECT'}, uv_layer='luz', use_clear=True)
    px = np.array(img.pixels[:], dtype=np.float32).reshape(-1, 4)
    px[:, :3] = np.clip(px[:, :3] * ESCALA, 0, 1) ** (1 / 2.2)
    out = bpy.data.images.new('luz8_' + nombre, res, res)
    out.pixels.foreach_set(px.ravel())
    out.filepath_raw = os.path.join(PROTO, 'tex', f'planta_luz_{nombre.lower()}.jpg')
    out.file_format = 'JPEG'; out.save()
    for nt, n in nodos:
        nt.nodes.remove(n)
    me.uv_layers.active = me.uv_layers[0]
    print('horneado', nombre)

for o in sc.objects:
    o.select_set(o.type == 'MESH')
destino = os.path.join(PROTO, 'planta.glb')
bpy.ops.export_scene.gltf(filepath=destino + '.tmp.glb', export_format='GLB', use_selection=True,
                          export_lights=False, export_cameras=False, export_texcoords=True, export_normals=True,
                          export_image_format='JPEG')
os.replace(destino + '.tmp.glb', destino)  # el archivo final aparece solo cuando la exportación terminó
print('exportado', round(os.path.getsize(destino) / 1e6, 1), 'MB')
