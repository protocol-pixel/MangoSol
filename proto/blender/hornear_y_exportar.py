# Precalcula la iluminación (lightmaps) del piso, muros y techo con Cycles y exporta la escena a glTF.
# Correr después de escena_tunel.py, en la escena "Scene".
import bpy, os
import numpy as np

PROTO = r'C:\Users\Asus\Documents\Formulacion de proyectos\presentacion\proto'
sc = bpy.data.scenes['Scene']
bpy.context.window.scene = sc
vl = bpy.context.view_layer


def unir(prefijos, nombre):
    obs = [o for o in sc.objects if o.type == 'MESH' and any(o.name.startswith(p) for p in prefijos)]
    for o in sc.objects:
        o.select_set(False)
    for o in obs:
        o.select_set(True)
    vl.objects.active = obs[0]
    bpy.ops.object.join()
    vl.objects.active.name = nombre
    return vl.objects.active


# 1) menos objetos = menos llamadas de dibujo en el navegador
unir(['Muro', 'Zócalo'], 'Muros')
unir(['Carro'], 'Carros')
unir(['Viga'], 'Vigas')
unir(['Luminaria'], 'Luminarias')
unir(['Túnel', 'Junta', 'Marco', 'Puerta', 'Sello', 'Manija'], 'Tunel')
unir(['Quemador', 'Ventilador', 'Rejilla', 'Ducto', 'Abrazadera', 'Gas', 'Válvula'], 'Equipos techo')
unir(['Tablero', 'Botón'], 'Tablero')

# 2) segundo mapa UV para la luz y horneado difuso (solo luz, sin color propio)
sc.render.engine = 'CYCLES'
sc.cycles.samples = 384
sc.cycles.use_denoising = True
sc.render.bake.margin = 8
hornear = {'Piso': 2048, 'Muros': 2048, 'Techo': 1024}
for nombre, res in hornear.items():
    ob = sc.objects[nombre]
    me = ob.data
    if 'luz' not in me.uv_layers:
        me.uv_layers.new(name='luz')
    for o in sc.objects:
        o.select_set(False)
    ob.select_set(True); vl.objects.active = ob
    me.uv_layers.active = me.uv_layers['luz']
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.lightmap_pack(PREF_CONTEXT='ALL_FACES', PREF_MARGIN_DIV=0.3)
    bpy.ops.object.mode_set(mode='OBJECT')
    img = bpy.data.images.new('luz_' + nombre, res, res, float_buffer=True)
    nodos = []
    for slot in ob.material_slots:  # nodo de imagen activo en cada material: ahí escribe el horneado
        nt = slot.material.node_tree
        n = nt.nodes.new('ShaderNodeTexImage'); n.image = img
        nt.nodes.active = n; nodos.append((nt, n))
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT', 'INDIRECT'}, uv_layer='luz', use_clear=True)
    # guardar en 8 bits a la mitad de intensidad (en three.js se multiplica por 2)
    px = np.array(img.pixels[:], dtype=np.float32).reshape(-1, 4)
    px[:, :3] = np.clip(px[:, :3] * .5, 0, 1) ** (1 / 2.2)
    out = bpy.data.images.new('luz8_' + nombre, res, res)
    out.pixels.foreach_set(px.ravel())
    out.filepath_raw = os.path.join(PROTO, 'tex', f'luz_{nombre.lower()}.jpg')
    out.file_format = 'JPEG'
    out.save()
    for nt, n in nodos:
        nt.nodes.remove(n)
    me.uv_layers.active = me.uv_layers[0]
    print('horneado', nombre)

# 3) exportar (sin luces ni cámara; las luces se recrean en three.js)
for o in sc.objects:
    o.select_set(o.type == 'MESH')
bpy.ops.export_scene.gltf(filepath=os.path.join(PROTO, 'tunel.glb'), export_format='GLB', use_selection=True,
                          export_lights=False, export_cameras=False, export_texcoords=True, export_normals=True,
                          export_image_format='JPEG')
print('exportado', round(os.path.getsize(os.path.join(PROTO, 'tunel.glb')) / 1e6, 1), 'MB')
