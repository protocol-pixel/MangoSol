# Áreas 4 (pelado), 5B (túnel), 6 (selección final) y 7 (envasado) en versión realista.
# En Blender:  exec(open(r'...\proto\blender\escena_areas.py', encoding='utf-8').read())
import os
exec(open(os.path.join(r'C:\Users\Asus\Documents\Formulacion de proyectos\presentacion\proto\blender', 'utilidades.py'), encoding='utf-8').read())
limpiar()
crear_materiales()
random.seed(5)

# ---------------- piso, techo y vigas ----------------
me = bpy.data.meshes.new('Piso')
rects = [(23, 40, 0, 8), (13, 40, 8, 16)]  # áreas 4+5B (norte) y 7+6+5B (sur)
vs, fs = [], []
for x0, x1, z0, z1 in rects:
    k = len(vs)
    vs += [tuple(W(x0, z0, 0)), tuple(W(x1, z0, 0)), tuple(W(x1, z1, 0)), tuple(W(x0, z1, 0))]
    fs.append((k, k + 3, k + 2, k + 1))
me.from_pydata(vs, [], fs)
piso = bpy.data.objects.new('Piso', me); col().objects.link(piso)
uv_mundo(piso, 4); me.materials.append(M['piso'])
caja('Techo', 12.8, 40.2, -.2, 16.2, 4.4, 4.45, M['techo'], 1.5)
for zw in [1, 5, 9, 13]:
    x0 = 23 if zw < 8 else 13
    caja('Viga', x0, 40, zw - .08, zw + .08, 4.02, 4.04, M['viga'])
    caja('Viga', x0, 40, zw - .006, zw + .006, 4.04, 4.38, M['viga'])
    caja('Viga', x0, 40, zw - .08, zw + .08, 4.38, 4.4, M['viga'])

# ---------------- muros: puertas abiertas en el flujo, cerradas hacia áreas no modeladas ----------------
muro('Muro', 'zw', 0, 23, 40, [(30, 2)])                 # norte: salida de cáscara (cerrada)
puerta_cerrada('zw', 0, 30, 2, 'p_residuos.jpg', '+zw')
muro('Muro', 'x', 23, 0, 8, [(6.2, 3)])                  # área 4 ← área 3 (cerrada)
puerta_cerrada('x', 23, 6.2, 3, 'p_area3.jpg', '+x')
muro('Muro', 'zw', 8, 23, 33, ventana=True)              # 4 | 6: zona sucia y limpia separadas por vidrio
muro('Muro', 'zw', 8, 13, 23, ventana=True)              # 7 | 2 y 3
muro('Muro', 'x', 33, 0, 16, [(6.2, 3), (14.2, 3)])      # 4 → 5B → 6 (abiertas)
muro('Muro', 'x', 40, 0, 16, [(14.6, 2.4)])              # 5B → 5A (cerrada)
puerta_cerrada('x', 40, 14.6, 2.4, 'p_solar.jpg', '-x')
muro('Muro', 'x', 23, 8, 16, [(14.2, 3)])                # 6 → 7 (abierta)
muro('Muro', 'x', 13, 8, 16, [(14.2, 3)])                # 7 → 8 (cerrada)
puerta_cerrada('x', 13, 14.2, 3, 'p_area8.jpg', '+x')
muro('Muro', 'zw', 16, 13, 40, [(14.5, 1.6), (19.5, 1.8)])  # sur: laboratorio y vestuarios (cerradas)
puerta_cerrada('zw', 16, 14.5, 1.6, 'p_lab.jpg', '-zw')
puerta_cerrada('zw', 16, 19.5, 1.8, 'p_ves.jpg', '-zw')
for (x0, x1, z0, z1) in [(23.1, 32.9, .1, .14), (13.1, 39.9, 15.86, 15.9), (33.1, 33.14, 0, 16), (39.86, 39.9, 0, 16), (23.14, 23.18, 0, 8)]:
    caja('Zócalo', x0, x1, z0, z1, 0, .12, M['zocalo'])

# letreros de área
plano('Letrero área 4', 28, .12, 3.2, 3.6, .7, mat_img('Letrero 4', 'area4.jpg', .4), '+zw')
plano('Letrero área 6', 28, 15.88, 3.2, 3.6, .7, mat_img('Letrero 6', 'area6.jpg', .4), '-zw')
plano('Letrero área 7', 17, 15.88, 3.45, 3.0, .586, mat_img('Letrero 7', 'area7.jpg', .4), '-zw')
plano('EPP', 13.12, 10.2, 1.7, .75, .5, mat_img('EPP', 'epp.jpg', .4), '+x')

# luminarias
for x in [25, 28.5, 31.5]:
    for zw in [2.2, 5.6, 10.4, 13.8]:
        luminaria(x, zw)
for x in [15, 18, 21]:
    for zw in [10.4, 13.8]:
        luminaria(x, zw)
for zw in [2.5, 6.5, 10.5, 14.5]:
    for x in [34.5, 38.5]:
        luminaria(x, zw)

# ---------------- área 4: pelado, laminado y pretratamiento ----------------
faja(23.6, 32.6, 6.4)
for i in range(46):  # láminas frescas sobre la faja
    if random.random() < .8:
        lamina_fresca(23.9 + i * .19, 6.4 + random.uniform(-.18, .18), .905)
for cx in (24.6, 27.4):
    mesa(cx, 1.7, 2.4, 1.0)
    for k in range(3):  # puesto de trabajo: tabla, cuchillo, mangos, cachetes y cáscara
        px = cx - .8 + k * .8
        caja('Tabla HDPE', px - .2, px + .2, 1.75, 2.05, .9, .915, M['hdpe'])
        caja('Cuchillo hoja', px + .05, px + .2, 1.85, 1.87, .915, .918, M['inox'])
        caja('Cuchillo mango', px + .2, px + .3, 1.845, 1.875, .915, .93, M['caucho'])
        mango(px - .1, 1.4, .945); mango(px + .05, 1.35, .945)
        mitad(px - .07, 1.92, .935); mitad(px + .08, 2.0, .935)
        cascara(px + .25, 1.45, .92)
    jaba(cx - .6, 2.75, 0, M['verde'], 'cascara')
    jaba(cx + .6, 2.75, 0, M['azul'], 'mango')
for zw in (1.2, 3.0):  # rebanadoras semiautomáticas
    caja('Rebanadora', 31.5, 32.4, zw - .4, zw + .4, 0, 1.0, M['inox'], 1, True)
    caja('Rebanadora tolva', 31.65, 32.25, zw - .25, zw + .25, 1.0, 1.35, M['inox_mate'])
    caja('Rebanadora salida', 31.3, 31.5, zw - .2, zw + .2, .7, .76, M['inox'])
    caja('Rebanadora tablero', 32.4, 32.44, zw - .15, zw + .15, .7, .95, M['tablero'])
for x in (25.2, 27.6):  # tinas de pretratamiento (ácido cítrico y ascórbico)
    cilindro('Tina', x, 4.5, .4, .46, .8, M['inox'], solido=True, tapa=False)   # 500 L, abierta
    cilindro('Tina fondo', x, 4.5, .01, .46, .02, M['inox'])
    cilindro('Solución', x, 4.5, .7, .45, .01, M['liquido'])
    cilindro('Tina borde', x, 4.5, .8, .48, .03, M['inox'], tapa=False)
caja('Lavamanos', 23.15, 23.7, 3.6, 4.4, .75, .95, M['inox'], 1, True)
cilindro('Grifo', 23.25, 4.0, 1.05, .015, .2, M['inox'])
caja('Pedal', 23.3, 23.5, 3.9, 4.1, 0, .05, M['inox_mate'])

# ---------------- área 5B: túnel de secado (igual al prototipo anterior) ----------------
X0, X1, Z0, Z1, HT = 34.6, 39.4, 1.0, 12.8, 2.8
for args in [(X0, X0 + .1, Z0, Z1, 0, HT), (X1 - .1, X1, Z0, Z1, 0, HT), (X0, X1, Z0, Z0 + .1, 0, HT)]:
    caja('Túnel', *args, M['inox'], 1.2, True)
caja('Túnel techo', X0, X1, Z0, Z1, HT - .1, HT, M['inox'], 1.2)
caja('Túnel piso', X0 + .1, X1 - .1, Z0 + .1, Z1, 0, .02, M['inox_mate'], 1)
for zw in [z / 10 for z in range(22, 128, 12)]:
    caja('Junta', X0 - .004, X0, zw - .01, zw + .01, 0, HT, M['junta'])
    caja('Junta', X1, X1 + .004, zw - .01, zw + .01, 0, HT, M['junta'])
caja('Marco', X0, X1, Z1 - .02, Z1 + .08, HT - .35, HT, M['inox'])
caja('Marco', X0, X0 + .2, Z1 - .02, Z1 + .08, 0, HT, M['inox'], 1, True)
caja('Marco', X1 - .2, X1, Z1 - .02, Z1 + .08, 0, HT, M['inox'], 1, True)
caja('Puerta túnel', X0 - .09, X0 - .01, Z1 + .08, Z1 + 2.35, .05, HT - .4, M['inox'], 1.2, True)
caja('Puerta túnel', X1 + .01, X1 + .09, Z1 + .08, Z1 + 2.35, .05, HT - .4, M['inox'], 1.2, True)
caja('Sello', X0 + .2, X1 - .2, Z1 + .08, Z1 + .1, HT - .37, HT - .35, M['caucho'])
caja('Quemador', 35.4, 38.6, 1.3, 3.1, HT, HT + .8, M['quemador'])
cilindro('Quemador', 37, 3.27, HT + .4, .22, .35, M['quemador'], eje='zw')
for x in [35.6, 38.4]:
    cilindro('Ventilador', x, 5.0, HT + .275, .45, .55, M['galv'])
    cilindro('Rejilla', x, 5.0, HT + .56, .43, .02, M['junta'])
cilindro('Ducto', 37, 7.45, HT + .32, .28, 8.7, M['galv'], eje='zw')
for zw in [4.5, 7.5, 10.5]:
    caja('Abrazadera', 36.68, 37.32, zw - .03, zw + .03, HT, HT + .62, M['viga'])
cilindro('Gas', 33.25, 2.0, (HT + .5) / 2, .03, HT + .5, M['gas'], solido=True)
cilindro('Gas', 34.3, 2.0, HT + .5, .03, 2.1, M['gas'], eje='x')
caja('Tablero túnel', 34.25, 34.6, 9.4, 10.4, 1.0, 1.9, M['tablero'], 1, True)
plano('Pantalla túnel', 34.245, 9.9, 1.6, .5, .31, mat_img('Pantalla túnel', 'pantalla_tunel.jpg', .2, 1.5), '-x')
plano('Letrero PCC 1', X0 - .015, 11.6, 1.75, 1.0, .5, mat_img('PCC 1', 'letrero_pcc1.jpg', .35), '-x')
plano('Letrero área 5B', 37, Z1 + .09, 3.15, 3.0, .586, mat_img('Letrero 5B', 'area5b.jpg', .4), '+zw')
for zw in [11.6, 10.2, 8.8, 7.4, 6.0, 4.6, 3.2, 1.8]:
    for x in (35.9, 38.1):
        carro(x, zw)
carro(38.4, 14.0, 'Carro afuera')
for (x0, x1, z0, z1) in [(X0, X1, 15.3, 15.38), (X0, X0 + .08, Z1 + .1, 15.38), (X1 - .08, X1, Z1 + .1, 15.38)]:
    caja('Franja amarilla', x0, x1, z0, z1, 0, .002, M['amarillo'])

# ---------------- área 6: enfriado (acondicionado 24 h) y selección final ----------------
for x in (24.6, 26.6, 28.6):
    carro(x, 8.95)
mesa(26.2, 11.4, 2.4, 1.0)
for i in range(18):
    o = lamina_fresca(25.2 + (i % 9) * .22, 11.2 + (i // 9) * .3, .905)
    o.data.materials[0] = M['seco']  # láminas secas sobre la mesa de selección
faja(23.6, 32.6, 14.4)
for i in range(40):  # producto seco en la faja
    if random.random() < .75:
        o = lamina_fresca(23.9 + i * .22, 14.4 + random.uniform(-.17, .17), .905)
        o.data.materials[0] = M['seco']
# detector de metales (PCC 2): arco sobre la faja, pantalla y torre de luces
caja('Detector', 30.35, 31.05, 13.95, 14.05, .7, 1.45, M['tablero'], 1, True)
caja('Detector', 30.35, 31.05, 14.75, 14.85, .7, 1.45, M['tablero'], 1, True)
caja('Detector', 30.35, 31.05, 13.95, 14.85, 1.2, 1.45, M['tablero'])
caja('Detector panel', 30.45, 30.95, 13.75, 13.95, 1.0, 1.4, M['tablero'])
plano('Pantalla detector', 30.7, 13.745, 1.25, .32, .2, mat_img('Pantalla detector', 'pantalla_detector.jpg', .2, 1.5), '-zw')
cilindro('Torre', 30.95, 13.85, 1.6, .02, .3, M['inox'])
for k, m in enumerate([M['rojo'], M['ambar'], M['verde_luz']]):
    cilindro('Baliza', 30.95, 13.85, 1.78 + k * .09, .045, .085, m)
caja('Bandeja rechazo', 31.15, 31.55, 14.95, 15.35, .5, .7, M['quemador'], 1, True)
plano('Letrero PCC 2', 30.7, 15.88, 2.0, 1.0, .5, mat_img('PCC 2', 'letrero_pcc2.jpg', .35), '-zw')

# ---------------- área 7: envasado ----------------
faja(13.6, 22.6, 14.4)
caja('Selladora', 19.6, 20.6, 13.85, 14.95, .76, 1.45, M['inox'], 1, True)
caja('Selladora túnel', 19.55, 20.65, 14.05, 14.75, .9, 1.25, M['junta'])
plano('Pantalla selladora', 20.1, 13.845, 1.3, .3, .19, mat_img('Pantalla selladora', 'pantalla_selladora.jpg', .2, 1.5), '-zw')
for i in range(12):  # bolsas selladas que salen de la selladora
    x = 15.0 + i * .38
    if x < 19.4:
        caja('Bolsa', x - .14, x + .14, 14.25, 14.55, .9, .96, M['bolsa'])
mesa(17.0, 10.0, 2.4, 1.0)
caja('Balanza', 16.0, 16.45, 9.75, 10.2, .9, .96, M['inox'])
plano('Display balanza', 16.225, 9.745, .95, .2, .05, mat_img('Display', 'pantalla_selladora.jpg', .2, 1.5), '-zw')
caja_carton(17.2, 10.0, .9)
caja('Bolsa abierta', 17.0, 17.4, 9.85, 10.15, 1.15, 1.32, M['bolsa'])
for i in range(3):
    cilindro('Rollo bolsas', 18.2 + i * .14, 10.2, .96, .06, .3, M['bolsa'], eje='zw')
mesa(21.0, 10.0, 2.4, 1.0)
for i in range(4):
    caja_carton(20.2 + i * .45, 10.0, .9)
# pallet con cajas terminadas (5 niveles) junto a la puerta del almacén
caja('Pallet', 13.4, 14.6, 9.0, 10.2, 0, .14, M['madera'], 1, True)
for lv in range(5):
    for i in range(3):
        for j in range(3):
            caja_carton(13.6 + i * .4, 9.25 + j * .4 + (.0 if lv % 2 else .02), .14 + lv * .25)
COLS.append([13.4, 14.6, 9.0, 10.2])
cilindro('Pediluvio', 19.5, 15.55, .03, .5, .06, M['agua'])

# ---------------- iluminación para el horneado y cámara de referencia ----------------
sc = bpy.data.scenes['Scene']
w = sc.world or bpy.data.worlds.new('Mundo'); sc.world = w
try:
    w.use_nodes = True
except Exception:
    pass
nt = w.node_tree
env = next((n for n in nt.nodes if n.type == 'TEX_ENVIRONMENT'), None) or nt.nodes.new('ShaderNodeTexEnvironment')
env.image = bpy.data.images.load(os.path.join(TEX, 'empty_warehouse_01_1k.hdr'), check_existing=True)
bg = next(n for n in nt.nodes if n.type == 'BACKGROUND')
nt.links.new(env.outputs['Color'], entrada(bg, 'Color')); entrada(bg, 'Strength').default_value = .1
for (x, zw, h) in LUCES:
    L = bpy.data.lights.new('LED', 'AREA'); L.shape = 'RECTANGLE'; L.size, L.size_y = 1.16, .14
    L.energy = 110; L.color = (1, .96, .9)
    o = bpy.data.objects.new('Luz LED', L); col().objects.link(o); o.location = W(x, zw, h - .06)
cam = bpy.data.cameras.new('Cámara'); cam.lens = 22
co = bpy.data.objects.new('Cámara', cam); col().objects.link(co)
co.location = W(23.8, 5.6, 1.65)
co.rotation_euler = (W(30, 2.5, 1.0) - co.location).to_track_quat('-Z', 'Y').to_euler()
sc.camera = co

json.dump({'cols': COLS}, open(os.path.join(PROTO, 'colisiones.json'), 'w'))
print('objetos:', len(bpy.data.objects), 'colisiones:', len(COLS), 'luces:', len(LUCES))
