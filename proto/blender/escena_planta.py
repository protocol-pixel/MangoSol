# Planta completa en versión realista: camión de mango → áreas 1 a 8 → contenedor a Paita.
# En Blender:  exec(open(r'...\proto\blender\escena_planta.py', encoding='utf-8').read())
import os
exec(open(os.path.join(r'C:\Users\Asus\Documents\Formulacion de proyectos\presentacion\proto\blender', 'utilidades.py'), encoding='utf-8').read())
limpiar()
crear_materiales()
random.seed(5)
M['asfalto'] = mat_pbr('Asfalto', 'asphalt_02_diff_1k.jpg', 'asphalt_02_rough_1k.jpg', 'asphalt_02_nor_1k.jpg', fuerza_normal=.7)
M['arena'] = mat_pbr('Terreno', 'dense_sand_diff_1k.jpg', 'dense_sand_rough_1k.jpg', 'dense_sand_nor_1k.jpg', fuerza_normal=.8)
M['pintura_blanca'] = mat_color('Pintura blanca', (.9, .9, .88), metal=.2, rough=.35)
M['contenedor'] = mat_pbr('Contenedor azul', 'corrugated_iron_rough_1k.jpg', None, 'corrugated_iron_nor_1k.jpg', fuerza_normal=1.0)
entrada(next(n for n in M['contenedor'].node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), 'Metallic').default_value = .4
# el contenedor es azul liso con relieve corrugado: se reemplaza el color de la textura por azul
nt = M['contenedor'].node_tree; bs = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
for l in list(nt.links):
    if l.to_socket == entrada(bs, 'Base Color'):
        nt.links.remove(l)
entrada(bs, 'Base Color').default_value = (.04, .17, .34, 1)
M['vidrio_oscuro'] = mat_color('Vidrio de cabina', (.05, .07, .08), metal=.3, rough=.05)
M['cortina'] = mat_color('Cortina de PVC', (.8, .86, .88), rough=.15, alfa=.35)
M['film'] = mat_color('Film strech', (.9, .92, .94), rough=.1, alfa=.35)


def suelo_poligonos(nombre, rects, mat, tile, h=0.0):
    me = bpy.data.meshes.new(nombre); vs, fs = [], []
    for x0, x1, z0, z1 in rects:
        k = len(vs)
        vs += [tuple(W(x0, z0, h)), tuple(W(x1, z0, h)), tuple(W(x1, z1, h)), tuple(W(x0, z1, h))]
        fs.append((k, k + 3, k + 2, k + 1))
    me.from_pydata(vs, [], fs)
    ob = bpy.data.objects.new(nombre, me); col().objects.link(ob)
    uv_mundo(ob, tile); me.materials.append(mat)
    return ob


# ---------------- pisos, patio, terreno, techo ----------------
suelo_poligonos('Piso', [(0, 40, 0, 8), (0, 40, 8, 16)], M['piso'], 4)
suelo_poligonos('Suelo', [(-16, 16, -20, -.1), (-16, -.1, -.1, 18)], M['asfalto'], 5, .003)   # patio de maniobras
suelo_poligonos('Terreno', [(-60, 90, -70, 60)], M['arena'], 6, -.02)
caja('Techo', -.2, 40.2, -.2, 16.2, 4.4, 4.5, M['techo'], 1.5)
for zw in [1, 5, 9, 13]:
    caja('Viga', 0, 40, zw - .08, zw + .08, 4.02, 4.04, M['viga'])
    caja('Viga', 0, 40, zw - .006, zw + .006, 4.04, 4.38, M['viga'])
    caja('Viga', 0, 40, zw - .08, zw + .08, 4.38, 4.4, M['viga'])

# ---------------- muros: el flujo va por puertas abiertas; lo demás, cerrado ----------------
muro('Muro', 'zw', 0, 0, 40, [(3.5, 4), (30, 2)])                 # norte: ingreso de camiones (abierto) y cáscara
puerta_cerrada('zw', 0, 30, 2, 'p_residuos.jpg', '+zw')
muro('Muro', 'x', 0, 0, 16, [(12, 3.5)])                          # oeste: andén de despacho (abierto)
muro('Muro', 'zw', 16, 0, 40, [(4.5, 1.8), (14.5, 1.6), (19.5, 1.8)])  # sur: oficinas, laboratorio, vestuarios
puerta_cerrada('zw', 16, 4.5, 1.8, 'p_oficinas.jpg', '-zw')
puerta_cerrada('zw', 16, 14.5, 1.6, 'p_lab.jpg', '-zw')
puerta_cerrada('zw', 16, 19.5, 1.8, 'p_ves.jpg', '-zw')
muro('Muro', 'x', 40, 0, 16, [(14.6, 2.4)])                       # este: presecado solar
puerta_cerrada('x', 40, 14.6, 2.4, 'p_solar.jpg', '-x')
for x in (7, 15, 23):                                             # 1 → 2 → 3 → 4
    muro('Muro', 'x', x, 0, 8, [(6.2, 3)])
muro('Muro', 'x', 33, 0, 16, [(6.2, 3), (14.2, 3)])               # 4 → 5B → 6
muro('Muro', 'x', 23, 8, 16, [(14.2, 3)])                         # 6 → 7
muro('Muro', 'x', 13, 8, 16, [(14.2, 3)])                         # 7 → 8
muro('Muro', 'zw', 8, 0, 33, ventana=True)                        # zona sucia | zona limpia: vidrio
for (x0, x1, z0, z1) in [(.1, 39.9, .1, .14), (.1, 39.9, 15.86, 15.9), (.1, .14, 0, 16), (39.86, 39.9, 0, 16)]:
    caja('Zócalo', x0, x1, z0, z1, 0, .12, M['zocalo'])
# cortinas de PVC en el ingreso y en la cámara fría (se atraviesan caminando)
def cortina(eje, fijo, a, b, alto=2.7):
    n = int((b - a) / .2)
    for i in range(n):
        c = a + .1 + i * (b - a - .2) / max(1, n - 1)
        if eje == 'zw':
            caja('Cortina', c - .095, c + .095, fijo - .005, fijo + .005, .05, alto, M['cortina'])
        else:
            caja('Cortina', fijo - .005, fijo + .005, c - .095, c + .095, .05, alto, M['cortina'])
cortina('zw', .12, 1.55, 5.45)
cortina('x', 7.12, 4.75, 7.65)
cortina('x', 14.88, 4.75, 7.65)

# letreros
plano('Fachada', 10.5, -.11, 3.35, 5.2, 1.3, mat_img('Fachada', 'fachada.jpg', .4), '-zw')
plano('Letrero área 1', .12, 3.6, 3.2, 3.0, .586, mat_img('Letrero 1', 'area1.jpg', .4), '+x')
plano('Letrero área 2', 11, .12, 3.2, 3.0, .586, mat_img('Letrero 2', 'area2.jpg', .4), '+zw')
plano('Letrero área 3', 19, .12, 3.2, 3.0, .586, mat_img('Letrero 3', 'area3.jpg', .4), '+zw')
plano('Letrero área 4', 28, .12, 3.2, 3.6, .7, mat_img('Letrero 4', 'area4.jpg', .4), '+zw')
plano('Letrero área 6', 28, 15.88, 3.2, 3.6, .7, mat_img('Letrero 6', 'area6.jpg', .4), '-zw')
plano('Letrero área 7', 17, 15.88, 3.45, 3.0, .586, mat_img('Letrero 7', 'area7.jpg', .4), '-zw')
plano('Letrero área 8', 9.4, 15.88, 3.3, 3.2, .625, mat_img('Letrero 8', 'area8.jpg', .4), '-zw')
plano('EPP', 13.12, 10.2, 1.7, .75, .5, mat_img('EPP', 'epp.jpg', .4), '+x')

# luminarias
for xs, zs in [((2, 5), (2.2, 5.6)), ((9, 13), (2.2, 5.6)), ((17, 21), (2.2, 5.6)), ((25, 28.5, 31.5), (2.2, 5.6, 10.4, 13.8)),
               ((15, 18, 21), (10.4, 13.8)), ((2.5, 6.5, 10.5), (10.4, 13.8)), ((34.5, 38.5), (2.5, 6.5, 10.5, 14.5))]:
    for x in xs:
        for zw in zs:
            luminaria(x, zw)

# ---------------- exterior: camión de mango fresco en el ingreso ----------------
def rueda(x, zw, h=.5, r=.5):
    cilindro('Llanta', x, zw, h, r, .3, M['caucho'], eje='x', seg=28)
    cilindro('Aro', x + (.16 if x > 3.5 else -.16), zw, h, r * .55, .02, M['inox_mate'], eje='x', seg=20)


TX0, TX1, TZ0, TZ1 = 2.3, 4.7, -7.8, -.9   # furgón (atrás pegado al ingreso)
caja('Chasis', 2.6, 4.4, -10.4, -.9, .7, 1.0, M['viga'])
caja('Furgón piso', TX0, TX1, TZ0, TZ1, 1.0, 1.12, M['madera'])
for s in (TX0, TX1 - .05):
    caja('Furgón lado', s, s + .05, TZ0, TZ1, 1.12, 3.5, M['pintura_blanca'], 1, True)
caja('Furgón frente', TX0, TX1, TZ0, TZ0 + .05, 1.12, 3.5, M['pintura_blanca'], 1, True)
caja('Furgón techo', TX0, TX1, TZ0, TZ1, 3.5, 3.56, M['pintura_blanca'])
for x0, x1 in ((TX0 - .05, TX0), (TX1, TX1 + .05)):  # puertas traseras abiertas contra los lados
    caja('Puerta furgón', x0, x1, TZ1 - 1.2, TZ1, 1.15, 3.45, M['pintura_blanca'], 1, True)
plano('Logo camión', TX0 - .01, (TZ0 + TZ1) / 2, 2.35, 6.0, 1.76, mat_img('Logo camión', 'logo_camion.jpg', .5), '-x')
plano('Logo camión', TX1 + .01, (TZ0 + TZ1) / 2, 2.35, 6.0, 1.76, mat_img('Logo camión 2', 'logo_camion.jpg', .5), '+x')
for k in range(6):  # jabas de mango apiladas en el furgón (cinco de alto)
    for i in range(4):
        zj = TZ1 - .35 - k * .45
        for lv in range(5):
            jaba(2.65 + i * .58, zj, 1.12 + lv * .3, M['verde'] if (k + i + lv) % 3 else M['azul'], 'mango' if lv == 4 else None)
COLS.append([TX0, TX1, TZ0, TZ1])
caja('Cabina', 2.35, 4.65, -10.4, -8.0, .8, 3.0, M['pintura_blanca'], 1, True)
caja('Parabrisas', 2.45, 4.55, -10.42, -10.4, 1.9, 2.8, M['vidrio_oscuro'])
for x in (2.33, 4.67):
    caja('Ventana cabina', x - .01, x + .01, -9.9, -8.8, 1.9, 2.7, M['vidrio_oscuro'])
caja('Parachoques', 2.3, 4.7, -10.55, -10.4, .55, .8, M['viga'])
for x in (2.55, 4.45):
    caja('Faro', x - .12, x + .12, -10.43, -10.41, 1.05, 1.2, M['led'])
for zw in (-9.4, -3.2, -1.9):
    rueda(2.45, zw); rueda(4.55, zw)
caja('Parrilla', 2.75, 4.25, -10.43, -10.41, 1.0, 1.6, M['junta'])
for x, s in ((2.35, -1), (4.65, 1)):
    caja('Espejo brazo', x + s * .02, x + s * .25, -10.25, -10.21, 2.4, 2.43, M['viga'])
    caja('Espejo', x + s * .22, x + s * .3, -10.3, -10.16, 2.0, 2.45, M['viga'])
    caja('Puerta cabina', x - .006, x + .006, -9.05, -9.03, .95, 2.85, M['junta'])
    caja('Peldaño', x - s * .02, x + s * .14, -9.7, -9.2, .55, .6, M['inox_mate'])
cilindro('Tanque', 2.42, -7.0, .78, .24, .9, M['inox_mate'], eje='zw')
caja('Deflector', 2.4, 4.6, -9.6, -8.0, 3.0, 3.35, M['pintura_blanca'])
for i in range(3):  # jabas ya descargadas sobre un pallet, listas para pesar
    for lv in range(3):
        jaba(2.4 + i * .58, 1.55, lv * .3 + .14, M['verde'], 'mango' if lv == 2 else None)
caja('Pallet', 1.9, 4.2, 1.3, 1.8, 0, .14, M['madera'])

# ---------------- área 1: recepción y pesado ----------------
caja('Balanza', 4.3, 5.8, 2.5, 4.0, 0, .08, M['inox_mate'])
caja('Balanza poste', 6.0, 6.1, 3.1, 3.2, 0, 1.25, M['inox'], 1, True)
caja('Balanza indicador', 5.95, 6.15, 2.95, 3.35, 1.25, 1.5, M['tablero'])
plano('Indicador', 5.94, 3.15, 1.39, .3, .16, mat_img('Indicador', 'pantalla_camara.jpg', .2, 1.5), '-x')
for lv in range(4):  # pallet sobre la balanza
    for i in range(2):
        for j in range(3):
            jaba(4.75 + i * .58, 2.85 + j * .4, .22 + lv * .3, M['azul'], 'mango' if lv == 3 else None)
caja('Pallet', 4.4, 5.7, 2.6, 3.9, .08, .22, M['madera'])
for zw0 in (5.2, 6.6):  # pallets en espera
    caja('Pallet', .4, 1.7, zw0 - .6, zw0 + .6, 0, .14, M['madera'])
    for lv in range(4):
        for i in range(2):
            for j in range(3):
                jaba(.75 + i * .58, zw0 - .4 + j * .4, .14 + lv * .3, M['verde'], 'mango' if lv == 3 else None)
mesa(5.6, 7.4, 1.4, .6)
caja('Tablilla', 5.3, 5.62, 7.25, 7.5, .9, .91, M['hdpe'])
caja('Transpaleta', 3.0, 3.6, 5.6, 6.9, 0, .1, M['amarillo'])
caja('Transpaleta mango', 3.27, 3.33, 6.9, 7.0, .1, 1.1, M['amarillo'])

# ---------------- área 2: cámara de materia prima (12–14 °C) ----------------
for zw0 in (.8, 3.2):
    for x0 in (7.8, 11.3):
        for lv, h in enumerate((0, 1.1, 2.2)):
            caja('Estante', x0, x0 + 3.0, zw0 - .45, zw0 + .45, h + .9, h + .95, M['galv'])
        for dx in (0, 1.5, 3.0):
            caja('Estante poste', x0 + dx - .03, x0 + dx + .03, zw0 - .45, zw0 - .39, 0, 3.2, M['galv'])
            caja('Estante poste', x0 + dx - .03, x0 + dx + .03, zw0 + .39, zw0 + .45, 0, 3.2, M['galv'])
        for h in (0, .95, 2.05):
            for i in range(5):
                jaba(x0 + .32 + i * .59, zw0, h + (.0 if h == 0 else .0), M['azul'] if i % 2 else M['verde'], 'mango')
        _registrar(x0, x0 + 3.0, zw0 - .45, zw0 + .45, 0, 3.2)
caja('Evaporador', 9.6, 12.4, .12, .75, 3.0, 3.7, M['tablero'])
for x in (10.3, 11.7):
    cilindro('Ventilador evaporador', x, .76, 3.35, .28, .02, M['junta'], eje='zw')
plano('Termómetro', 14.88, 3.0, 1.6, .4, .25, mat_img('Termómetro', 'pantalla_camara.jpg', .2, 1.5), '-x')

# ---------------- área 3: selección y lavado ----------------
faja(15.6, 22.6, 6.4)
for i in range(18):
    if random.random() < .85:
        mango(15.9 + i * .37, 6.4 + random.uniform(-.15, .15), .95)
caja('Lavadora', 19.0, 21.9, 5.75, 7.05, 0, 1.05, M['inox'], 1, True)
caja('Agua', 19.05, 21.85, 5.8, 7.0, 1.0, 1.01, M['agua'])
for x in (19.4, 20.4, 21.4):  # barras de aspersión
    caja('Aspersor', x - .02, x + .02, 5.75, 7.05, 1.45, 1.49, M['inox'])
    caja('Aspersor', x - .02, x + .02, 5.75, 5.79, 1.05, 1.49, M['inox'])
for i in range(8):
    mango(19.2 + i * .35, 6.4 + random.uniform(-.3, .3), 1.03)
caja('Descarte', 16.9, 17.5, 7.0, 7.6, 0, .75, M['quemador'], 1, True)
for i in range(5):
    mango(17.0 + random.uniform(0, .4), 7.1 + random.uniform(0, .4), .72)
mesa(17.5, 2.0, 2.4, 1.0)
for i in range(6):
    mango(16.6 + i * .35, 2.0 + random.uniform(-.2, .2), .945)
jaba(15.7, 4.9, 0, M['azul'], 'mango'); jaba(15.7, 4.9, .3, M['azul'], 'mango')

# ---------------- área 4: pelado, laminado y pretratamiento ----------------
faja(23.6, 32.6, 6.4)
for i in range(46):
    if random.random() < .8:
        lamina_fresca(23.9 + i * .19, 6.4 + random.uniform(-.18, .18), .905)
for cx in (24.6, 27.4):
    mesa(cx, 1.7, 2.4, 1.0)
    for k in range(3):
        px = cx - .8 + k * .8
        caja('Tabla HDPE', px - .2, px + .2, 1.75, 2.05, .9, .915, M['hdpe'])
        caja('Cuchillo hoja', px + .05, px + .2, 1.85, 1.87, .915, .918, M['inox'])
        caja('Cuchillo mango', px + .2, px + .3, 1.845, 1.875, .915, .93, M['caucho'])
        mango(px - .1, 1.4, .945); mango(px + .05, 1.35, .945)
        mitad(px - .07, 1.92, .935); mitad(px + .08, 2.0, .935)
        cascara(px + .25, 1.45, .92)
    jaba(cx - .6, 2.75, 0, M['verde'], 'cascara')
    jaba(cx + .6, 2.75, 0, M['azul'], 'mango')
for zw in (1.2, 3.0):
    caja('Rebanadora', 31.5, 32.4, zw - .4, zw + .4, 0, 1.0, M['inox'], 1, True)
    caja('Rebanadora tolva', 31.65, 32.25, zw - .25, zw + .25, 1.0, 1.35, M['inox_mate'])
    caja('Rebanadora salida', 31.3, 31.5, zw - .2, zw + .2, .7, .76, M['inox'])
    caja('Rebanadora tablero', 32.4, 32.44, zw - .15, zw + .15, .7, .95, M['tablero'])
for x in (25.2, 27.6):
    cilindro('Tina', x, 4.5, .4, .46, .8, M['inox'], solido=True, tapa=False)
    cilindro('Tina fondo', x, 4.5, .01, .46, .02, M['inox'])
    cilindro('Solución', x, 4.5, .7, .45, .01, M['liquido'])
    cilindro('Tina borde', x, 4.5, .8, .48, .03, M['inox'], tapa=False)
caja('Lavamanos', 23.15, 23.7, 3.6, 4.4, .75, .95, M['inox'], 1, True)
cilindro('Grifo', 23.25, 4.0, 1.05, .015, .2, M['inox'])

# ---------------- área 5B: túnel de secado ----------------
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
caja('Quemador', 35.4, 38.6, 1.3, 3.1, HT, HT + .8, M['quemador'])
cilindro('Quemador', 37, 3.27, HT + .4, .22, .35, M['quemador'], eje='zw')
for x in [35.6, 38.4]:
    cilindro('Ventilador', x, 5.0, HT + .275, .45, .55, M['galv'])
cilindro('Ducto', 37, 7.45, HT + .32, .28, 8.7, M['galv'], eje='zw')
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

# ---------------- área 6: enfriado y selección final (PCC 2) ----------------
for x in (24.6, 26.6, 28.6):
    carro(x, 8.95)
mesa(26.2, 11.4, 2.4, 1.0)
for i in range(18):
    lamina_fresca(25.2 + (i % 9) * .22, 11.2 + (i // 9) * .3, .905).data.materials[0] = M['seco']
faja(23.6, 32.6, 14.4)
for i in range(40):
    if random.random() < .75:
        lamina_fresca(23.9 + i * .22, 14.4 + random.uniform(-.17, .17), .905).data.materials[0] = M['seco']
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
for i in range(12):
    x = 15.0 + i * .38
    if x < 19.4:
        caja('Bolsa', x - .14, x + .14, 14.25, 14.55, .9, .96, M['bolsa'])
mesa(17.0, 10.0, 2.4, 1.0)
caja('Balanza mesa', 16.0, 16.45, 9.75, 10.2, .9, .96, M['inox'])
caja_carton(17.2, 10.0, .9)
mesa(21.0, 10.0, 2.4, 1.0)
for i in range(4):
    caja_carton(20.2 + i * .45, 10.0, .9)
cilindro('Pediluvio', 19.5, 15.55, .03, .5, .06, M['agua'])


# ---------------- área 8: almacén de producto terminado y despacho ----------------
def pallet_cajas(cx, czw, niveles=5, film=True):
    caja('Pallet', cx - .6, cx + .6, czw - .6, czw + .6, 0, .14, M['madera'], 1, True)
    for lv in range(niveles):
        for i in range(3):
            for j in range(3):
                caja_carton(cx - .4 + i * .4, czw - .4 + j * .4 + .05, .14 + lv * .25)
    if film:
        caja('Film', cx - .62, cx + .62, czw - .62, czw + .62, .14, .14 + niveles * .25 + .02, M['film'])


for x in (1.0, 2.4, 3.8, 5.2, 6.6, 8.0, 9.4):
    pallet_cajas(x, 9.0)
for x in (6.6, 8.0, 9.4):
    pallet_cajas(x, 10.45, 4)
caja('Transpaleta', 3.2, 3.8, 12.3, 13.6, 0, .1, M['amarillo'])
caja('Transpaleta mango', 3.47, 3.53, 13.6, 13.7, .1, 1.1, M['amarillo'])
pallet_cajas(3.5, 12.6, 4)
for zw in (10.3, 13.7):  # topes del andén
    caja('Tope', -.25, -.1, zw - .2, zw + .2, .2, .55, M['caucho'], 1, True)
caja('Sello andén', -.3, -.1, 10.15, 10.3, 0, 2.8, M['caucho'])
caja('Sello andén', -.3, -.1, 13.7, 13.85, 0, 2.8, M['caucho'])
caja('Sello andén', -.3, -.1, 10.15, 13.85, 2.65, 2.8, M['caucho'])

# ---------------- exterior: contenedor de 20 pies hacia Paita ----------------
CX0, CX1, CZ0, CZ1, CH = -6.46, -.4, 10.78, 13.22, 2.59
caja('Contenedor piso', CX0, CX1, CZ0, CZ1, 0, .15, M['madera'])
caja('Contenedor lado', CX0, CX1, CZ0, CZ0 + .05, 0, CH, M['contenedor'], 1.2, True)
caja('Contenedor lado', CX0, CX1, CZ1 - .05, CZ1, 0, CH, M['contenedor'], 1.2, True)
caja('Contenedor fondo', CX0, CX0 + .05, CZ0, CZ1, 0, CH, M['contenedor'], 1.2, True)
caja('Contenedor techo', CX0, CX1, CZ0, CZ1, CH - .05, CH, M['contenedor'], 1.2)
for x0, x1 in ((CX1 - 1.22, CX1),):  # puertas abiertas 270°, pegadas a los lados
    caja('Puerta contenedor', x0, x1, CZ0 - .08, CZ0 - .03, .05, CH - .1, M['contenedor'], 1.2, True)
    caja('Puerta contenedor', x0, x1, CZ1 + .03, CZ1 + .08, .05, CH - .1, M['contenedor'], 1.2, True)
plano('Logo contenedor', (CX0 + CX1) / 2, CZ0 - .01, 1.45, 4.6, 1.35, mat_img('Logo contenedor', 'logo_contenedor.jpg', .5), '-zw')
plano('Logo contenedor', (CX0 + CX1) / 2, CZ1 + .01, 1.45, 4.6, 1.35, mat_img('Logo contenedor 2', 'logo_contenedor.jpg', .5), '+zw')
for x in (-5.7, -4.4):  # dos pallets ya cargados al fondo
    caja('Pallet', x - .6, x + .6, 11.4, 12.6, .15, .29, M['madera'])
    for lv in range(5):
        for i in range(3):
            for j in range(3):
                caja('Caja', x - .55 + i * .37, x - .2 + i * .37, 11.45 + j * .38, 11.8 + j * .38, .29 + lv * .25, .53 + lv * .25, M['kraft'])

# ---------------- cielo, sol y luces para el horneado ----------------
sc = bpy.data.scenes['Scene']
w = sc.world or bpy.data.worlds.new('Mundo'); sc.world = w
try:
    w.use_nodes = True
except Exception:
    pass
nt = w.node_tree
env = next((n for n in nt.nodes if n.type == 'TEX_ENVIRONMENT'), None) or nt.nodes.new('ShaderNodeTexEnvironment')
env.image = bpy.data.images.load(os.path.join(TEX, 'cielo_1k.hdr'), check_existing=True)
bg = next(n for n in nt.nodes if n.type == 'BACKGROUND')
nt.links.new(env.outputs['Color'], entrada(bg, 'Color')); entrada(bg, 'Strength').default_value = .6
sol = bpy.data.lights.new('Sol', 'SUN'); sol.energy = 4.0; sol.angle = math.radians(1.5); sol.color = (1, .97, .92)
so = bpy.data.objects.new('Sol', sol); col().objects.link(so)
so.rotation_euler = (math.radians(35), math.radians(-20), math.radians(30))
for (x, zw, h) in LUCES:
    L = bpy.data.lights.new('LED', 'AREA'); L.shape = 'RECTANGLE'; L.size, L.size_y = 1.16, .14
    L.energy = 110; L.color = (1, .96, .9)
    o = bpy.data.objects.new('Luz LED', L); col().objects.link(o); o.location = W(x, zw, h - .06)
cam = bpy.data.cameras.new('Cámara'); cam.lens = 22
co = bpy.data.objects.new('Cámara', cam); col().objects.link(co)
co.location = W(-1.5, -14.5, 1.65)
co.rotation_euler = (W(3.5, -2.0, 2.0) - co.location).to_track_quat('-Z', 'Y').to_euler()
sc.camera = co

json.dump({'cols': COLS}, open(os.path.join(PROTO, 'colisiones.json'), 'w'))
print('objetos:', len(bpy.data.objects), 'colisiones:', len(COLS), 'luces:', len(LUCES))
