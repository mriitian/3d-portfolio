"""The planet ground, scattered props, moon, distant ringed planet and floating islands."""
import math
import os
import random

import bmesh
import bpy
from mathutils import Matrix, Vector, kdtree, noise

import preview
from blender_lib import (Group, Mesh, P, bake_ao, mix, rot, tr)
from zone_common import lamp_post

R = 40.0

# Must match src/game/zones.js (id, latitude, longitude in degrees).
ZONE_DEFS = [
    ("about", 8, 28),
    ("projects", 38, 105),
    ("skills", -34, 165),
    ("experience", 30, -115),
    ("contact", -32, -50),
]


def three_to_blender(v):
    """Three.js (x, y, z, y up) direction -> Blender coordinates (x, -z, y)."""
    return Vector((v[0], -v[2], v[1]))


SPAWN = three_to_blender(Vector((1, 0, 0)))


def zone_dirs():
    """Zone directions in Blender space (src/game/zones.js works in three.js space)."""
    out = {}
    for zid, lat, lon in ZONE_DEFS:
        la, lo = math.radians(lat), math.radians(lon)
        out[zid] = three_to_blender(
            Vector((math.cos(la) * math.cos(lo), math.sin(la), math.cos(la) * math.sin(lo))))
    return out


def arc_dist(a, b):
    return R * math.acos(max(-1.0, min(1.0, a.dot(b))))


def smooth(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


# ------------------------------------------------------------- the road ---


def build_path_points(dirs):
    """A meandering loop that visits the spawn -> every zone -> spawn."""
    order = [SPAWN] + [dirs[z] for z in ("about", "projects", "skills", "experience", "contact")]
    order.append(order[0])
    pts = []
    rng = random.Random(5)
    for i in range(len(order) - 1):
        a, b = order[i].normalized(), order[i + 1].normalized()
        length = arc_dist(a, b)
        n = max(2, int(length / 0.45))
        phase = rng.uniform(0, math.tau)
        sway = rng.uniform(1.6, 2.8)
        for k in range(n):
            t = k / n
            p = a.slerp(b, t)
            tangent = (a.slerp(b, min(1.0, t + 0.01)) - p).normalized()
            side = p.cross(tangent).normalized()
            fade = math.sin(math.pi * t)
            offset = side * (math.sin(t * math.pi * 3 + phase) * sway * fade / R)
            p = (p + offset).normalized()
            pts.append((p * R, tangent))
    return pts


# ------------------------------------------------------------ the planet ---


def build_planet(dirs, path_pts):
    noise.seed_set(11)
    rng = random.Random(3)
    m = Mesh("Planet", jitter=0.0, ao=False, seed=3)
    bm = m.bm
    bmesh.ops.create_icosphere(bm, subdivisions=7, radius=R, calc_uvs=False)

    tree = kdtree.KDTree(len(path_pts))
    for i, (p, _) in enumerate(path_pts):
        tree.insert(p, i)
    tree.balance()
    zone_list = list(dirs.values())

    def vertex_color(co):
        c = co.normalized()
        # base terracotta with soft light/dark variation
        col = mix(P["earth"], P["earth_dark"], noise.noise(c * 2.3) * 0.7 + 0.35)
        col = mix(col, P["earth_light"], max(0.0, noise.noise(c * 6.0 + Vector((9, 3, 1)))) * 0.8)
        col = mix(col, P["cliff"], smooth(0.35, 0.7, noise.noise(c * 4.4 + Vector((5, 8, 2)))))
        # green meadows
        grass_mask = smooth(0.0, 0.32, noise.noise(c * 2.9 + Vector((17, 1, 6))))
        grass = mix(P["grass"], P["grass_dark"], noise.noise(c * 9.0) * 0.5 + 0.5)
        grass = mix(grass, P["grass_light"], max(0.0, noise.noise(c * 15.0 + Vector((2, 2, 9)))))
        col = mix(col, grass, grass_mask * 0.95)
        # speckle
        k = 1.0 + noise.noise(c * 40.0) * 0.05
        col = tuple(v * k for v in col)

        # stone plazas under each landmark, with concentric rings
        for zd in zone_list:
            d = arc_dist(c, zd)
            if d < 8.2:
                ring = 0.5 + 0.5 * math.sin(d * 2.6)
                plaza = mix(P["plaza_dark"], P["plaza"], ring)
                col = mix(col, plaza, 1.0 - smooth(6.8, 8.2, d))
        d_spawn = arc_dist(c, SPAWN)
        if d_spawn < 6.5:
            col = mix(col, mix(P["plaza_dark"], P["plaza"], 0.5 + 0.5 * math.sin(d_spawn * 2.6)),
                      1.0 - smooth(5.2, 6.5, d_spawn))

        # the sand road
        d_path = tree.find(co.normalized() * R)[2]
        road = 1.0 - smooth(1.7, 2.4, d_path)
        edge = (1.0 - smooth(2.4, 3.6, d_path)) * 0.55
        sand = mix(P["sand"], P["sand_dark"], noise.noise(c * 30.0) * 0.5 + 0.35)
        col = mix(col, P["sand_dark"], edge)
        col = mix(col, sand, road)
        return col

    cache = {}
    for f in bm.faces:
        for loop in f.loops:
            v = loop.vert
            if v not in cache:
                cache[v] = vertex_color(v.co)
            r = cache[v]
            loop[m.col] = (r[0], r[1], r[2], 1.0)

    obj = m.to_object(name="Planet", bevel=0.0, smooth_angle=180.0)
    m.free()
    _bumpy_normals(obj)
    return obj


def _bumpy_normals(obj):
    """Tilt the vertex normals with noise, so the sphere catches light like rolling terrain."""
    me = obj.data
    normals = []
    eps = 0.9
    for v in me.vertices:
        n = v.co.normalized()
        p = v.co * 0.08
        gx = noise.noise(p + Vector((eps, 0, 0))) - noise.noise(p - Vector((eps, 0, 0)))
        gy = noise.noise(p + Vector((0, eps, 0))) - noise.noise(p - Vector((0, eps, 0)))
        gz = noise.noise(p + Vector((0, 0, eps))) - noise.noise(p - Vector((0, 0, eps)))
        g = Vector((gx, gy, gz))
        g -= n * g.dot(n)  # keep only the tangential part
        fine = Vector((noise.noise(v.co * 0.35 + Vector((3, 1, 7))),
                       noise.noise(v.co * 0.35 + Vector((1, 8, 2))),
                       noise.noise(v.co * 0.35 + Vector((6, 4, 5)))))
        fine -= n * fine.dot(n)
        normals.append((n + g * 0.55 + fine * 0.22).normalized())
    me.normals_split_custom_set_from_vertices(normals)


# --------------------------------------------------------------- props ---


def place(direction, yaw=0.0, scale=1.0, lift=0.0):
    q = Vector((0, 0, 1)).rotation_difference(direction.normalized()).to_matrix().to_4x4()
    return tr(*(direction.normalized() * (R + lift))) @ q @ rot(0, 0, yaw) @ Matrix.Scale(scale, 4)


def round_tree(g, base, leaf):
    g.lit.lathe([(0.42, 0.0), (0.3, 0.5), (0.22, 1.4), (0.2, 2.2)], segs=12, color=P["trunk"],
                base=base, caps=False)
    for x, y, z, r in ((0, 0, 3.0, 1.35), (0.85, 0.3, 3.6, 0.9), (-0.75, -0.4, 3.5, 0.95),
                       (0.1, -0.9, 3.2, 0.8)):
        g.lit.ball(r, (x, y, z), 3, color=leaf, lump=0.2, grad=(2.0, 4.8, 0.78, 1.18), base=base)


def pine_tree(g, base, leaf):
    g.lit.lathe([(0.3, 0.0), (0.2, 1.2)], segs=10, color=P["trunk"], base=base, caps=False)
    for r, z, h in ((1.5, 0.9, 1.9), (1.15, 2.1, 1.8), (0.8, 3.2, 1.7), (0.45, 4.2, 1.5)):
        g.lit.lathe([(r, z), (r * 0.78, z + h * 0.35), (r * 0.42, z + h * 0.72),
                     (0.0, z + h)], segs=18, color=leaf, grad=(0.9, 5.7, 0.8, 1.15), base=base,
                    caps=True)


def bush(g, base, leaf):
    g.lit.ball(0.75, (0, 0, 0.45), 3, scale=(1.2, 1.0, 0.75), color=leaf, lump=0.25, base=base)
    g.lit.ball(0.5, (0.65, 0.2, 0.35), 3, scale=(1, 1, 0.8), color=leaf, lump=0.25, base=base)


def rock(g, base, size, shade):
    g.lit.ball(size, (0, 0, size * 0.32), 3, scale=(1.15, 0.95, 0.7), color=shade, lump=0.34,
               lump_freq=1.7, base=base)


def tuft(g, base):
    for dx, dy, tilt, h in ((0, 0, 0, 0.75), (0.16, 0.05, 14, 0.55), (-0.13, 0.09, -13, 0.6)):
        g.lit.cyl(0.08, 0.0, h, (dx, dy, 0), (tilt, tilt * 0.5, 0), segs=5, color=P["grass_light"],
                  grad=(0, 0.7, 0.7, 1.2), base=base, caps=False)


def mushroom(g, base, cap):
    g.lit.lathe([(0.16, 0.0), (0.11, 0.3), (0.1, 0.6)], segs=10, color=P["cream"], base=base,
                caps=False)
    g.lit.ball(0.42, (0, 0, 0.66), 3, scale=(1, 1, 0.55), color=cap, base=base)


def crystal_cluster(g, base, key):
    glow = g.g(key)
    for dx, dy, tx, ty, h, r in ((0, 0, 0, 0, 2.1, 0.4), (0.55, 0.2, 16, 12, 1.3, 0.3),
                                 (-0.5, 0.1, -15, -10, 1.1, 0.28), (0.1, -0.55, 10, -20, 0.9, 0.24)):
        glow.cyl(r, 0.0, h, (dx, dy, 0.1), (tx, ty, 0), segs=6, base=base)
    g.lit.ball(0.7, (0, 0, 0.12), 3, scale=(1.4, 1.2, 0.5), color=P["rock_dark"], lump=0.3,
               base=base)


def chunk_key(d):
    """Which of six cube faces a direction points at; props are grouped by it so the GPU
    can skip whole chunks that are behind the camera or outside the shadow area."""
    ax = max(range(3), key=lambda i: abs(d[i]))
    return "xyz"[ax] + ("p" if d[ax] >= 0 else "n")


def build_scatter(dirs, path_pts):
    groups = {}

    def G(d):
        key = chunk_key(d)
        if key not in groups:
            groups[key] = Group(f"Scatter_{key}", ao=(0.0, 4.5, 0.9, 1.0),
                                seed=9 + len(groups), bevel=0.0)
        return groups[key]

    rng = random.Random(77)

    path_tree = kdtree.KDTree(len(path_pts))
    for i, (p, _) in enumerate(path_pts):
        path_tree.insert(p, i)
    path_tree.balance()
    zone_list = list(dirs.values())
    placed = []

    def ok(d, min_zone, min_path, min_gap):
        if any(arc_dist(d, z) < min_zone for z in zone_list):
            return False
        if arc_dist(d, SPAWN) < 8:
            return False
        if path_tree.find(d * R)[2] < min_path:
            return False
        return all(arc_dist(d, p) > min_gap for p in placed)

    def sample():
        while True:
            d = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1)))
            if 0.1 < d.length <= 1.0:
                return d.normalized()

    def scatter(count, min_zone, min_path, min_gap, fn, tries=4000):
        n = 0
        while n < count and tries > 0:
            tries -= 1
            d = sample()
            if not ok(d, min_zone, min_path, min_gap):
                continue
            placed.append(d)
            fn(d, G(d))
            n += 1

    leaves = [P["leaf_green"], P["leaf_lime"], P["leaf_teal"], P["leaf_amber"], P["leaf_green"],
              P["leaf_pink"]]
    scatter(38, 11.0, 4.4, 5.5,
            lambda d, g: round_tree(g, place(d, rng.uniform(0, 360), rng.uniform(0.9, 1.4)),
                                 rng.choice(leaves)))
    scatter(34, 11.0, 4.4, 4.6,
            lambda d, g: pine_tree(g, place(d, rng.uniform(0, 360), rng.uniform(0.85, 1.3)),
                                rng.choice([P["leaf_green"], P["leaf_teal"], P["grass_dark"]])))
    scatter(30, 10.0, 3.6, 3.0,
            lambda d, g: bush(g, place(d, rng.uniform(0, 360), rng.uniform(0.8, 1.3)),
                           rng.choice([P["leaf_green"], P["leaf_lime"], P["grass"]])))
    scatter(54, 9.5, 3.4, 3.2,
            lambda d, g: rock(g, place(d, rng.uniform(0, 360)), rng.uniform(0.55, 1.6),
                           rng.choice([P["rock"], P["rock_dark"], P["rock_light"]])))
    scatter(16, 10.0, 4.0, 5.0,
            lambda d, g: crystal_cluster(g, place(d, rng.uniform(0, 360), rng.uniform(0.9, 1.5)),
                                      rng.choice(["cyan", "magenta", "amber", "cyan"])))
    scatter(22, 9.5, 3.6, 2.6,
            lambda d, g: mushroom(g, place(d, rng.uniform(0, 360), rng.uniform(0.9, 1.7)),
                               rng.choice([P["mushroom"], P["leaf_amber"], P["leaf_pink"]])))
    scatter(180, 8.5, 3.0, 1.2,
            lambda d, g: tuft(g, place(d, rng.uniform(0, 360), rng.uniform(0.8, 1.4))), tries=9000)

    # street lamps along the road, alternating sides
    side_sign = 1
    last = None
    for p, tangent in path_pts:
        d = p.normalized()
        if arc_dist(d, SPAWN) < 7 or any(arc_dist(d, z) < 9.0 for z in zone_list):
            continue
        if last is not None and arc_dist(d, last) < 9.5:
            continue
        side = d.cross(tangent).normalized() * side_sign
        lp = (p + side * 3.1).normalized()
        lamp_post(G(lp), 0, 0, "amber", 2.6, base=place(lp, rng.uniform(0, 360)))
        side_sign *= -1
        last = d
    return list(groups.values())


# ------------------------------------------------- moon, sky planet, islands ---


def build_moon():
    noise.seed_set(4)
    m = Mesh("Moon", jitter=0.0, ao=False, seed=2)
    bmesh.ops.create_icosphere(m.bm, subdivisions=6, radius=6.0, calc_uvs=False)
    cr = random.Random(8)
    craters = [(Vector((cr.uniform(-1, 1), cr.uniform(-1, 1), cr.uniform(-1, 1))).normalized(),
                cr.uniform(0.7, 1.5)) for _ in range(14)]
    base = (0.82, 0.78, 0.9)
    cache = {}
    for v in m.bm.verts:
        c = v.co.normalized()
        k = 0.78 + 0.12 * noise.noise(c * 3)
        col = tuple(x * k for x in base)
        depth = 0.0
        for d, rad in craters:
            dd = 6.0 * math.acos(max(-1, min(1, c.dot(d))))
            if dd < rad * 0.75:
                col = tuple(x * 0.55 for x in base)
                depth = max(depth, 0.5 * (1 - dd / (rad * 0.75)))
            elif dd < rad:
                col = tuple(min(1, x * 1.12) for x in base)
        v.co = c * (6.0 - depth * 0.25)
        cache[v] = col
    for f in m.bm.faces:
        for loop in f.loops:
            loop[m.col] = (*cache[loop.vert], 1.0)
    obj = m.to_object(name="Moon", bevel=0.0, smooth_angle=60.0)
    m.free()
    return obj


def build_sky_planet():
    """A big banded ringed planet for the backdrop."""
    noise.seed_set(6)
    g = Group("SkyPlanet", seed=61, bevel=0.0)
    tilt = tr(0, 0, 0) @ rot(62, 0, 18)
    m = g.lit
    bmesh.ops.create_icosphere(m.bm, subdivisions=6, radius=30.0, calc_uvs=False)
    bands = [P["earth_light"], P["orange"], P["leaf_pink"], P["violet"], P["earth_dark"],
             P["sand"]]
    cache = {}
    for v in m.bm.verts:
        c = v.co.normalized()
        t = c.z * 7.0 + noise.noise(c * 2.2) * 1.6
        i = int(math.floor(t)) % len(bands)
        j = (i + 1) % len(bands)
        col = mix(bands[i], bands[j], smooth(0.0, 1.0, t - math.floor(t)))
        k = 0.85 + 0.15 * noise.noise(c * 8)
        cache[v] = tuple(x * k for x in col)
    for f in m.bm.faces:
        for loop in f.loops:
            loop[m.col] = (*cache[loop.vert], 1.0)
    # rings
    for r0, r1, col in ((38, 42, P["sand"]), (43, 50, P["earth_light"]), (51, 53.5, P["sand_dark"])):
        g.paint.lathe([(r0, -0.15), (r1, -0.15), (r1, 0.15), (r0, 0.15)], segs=96, color=col,
                      base=tilt, caps=True, grad=False)
    return g.build()


def build_island(index):
    g = Group(f"FloatRock_{index}", ao=(-4.0, 1.0, 0.7, 1.0), seed=40 + index, bevel=0.0)
    rng = random.Random(40 + index)
    r = 3.0 + index * 0.45
    g.lit.ball(r, (0, 0, 0.2), 4, scale=(1, 1, 0.22), color=P["grass"], lump=0.12, lump_freq=1.0,
               grad=False)
    g.lit.ball(r * 0.97, (0, 0, -0.3), 4, scale=(1, 1, 0.28), color=P["earth"], lump=0.15,
               grad=False)
    for i in range(4):
        a = rng.uniform(0, math.tau)
        d = rng.uniform(0.0, r * 0.5)
        g.lit.ball(1.2 - i * 0.15, (math.cos(a) * d, math.sin(a) * d, -1.5 - i * 0.7), 3,
                   scale=(0.8, 0.8, 1.7), color=P["rock"], lump=0.22, grad=False)
    g.lit.ball(r * 0.7, (0, 0, -1.0), 3, scale=(1, 1, 1.1), color=P["rock_dark"], lump=0.25,
               grad=False)
    if index % 3 == 0:
        round_tree(g, tr(0.6, 0.2, 0.5), P["leaf_pink"])
    elif index % 3 == 1:
        pine_tree(g, tr(-0.4, 0.3, 0.5), P["leaf_teal"])
    else:
        crystal_cluster(g, tr(0.3, -0.3, 0.5), "magenta")
    rock(g, tr(-r * 0.5, -r * 0.3, 0.4), 0.7, P["rock_light"])
    return g.build()


# ------------------------------------------------------------- orchestration ---


def build_all(args):
    dirs = zone_dirs()
    path_pts = build_path_points(dirs)
    t = __import__("time").time()
    planet = build_planet(dirs, path_pts)
    print(f"PLANET built in {__import__('time').time() - t:.1f}s")

    scatter_roots = [g.build() for g in build_scatter(dirs, path_pts)]
    for root in scatter_roots:
        meshes = [ob for ob in root.children_recursive if ob.type == "MESH"]
        bake_ao(meshes, [planet], samples=max(8, args.ao // 2), max_dist=2.2, floor=0.5)
    print(f"SCATTER built in {__import__('time').time() - t:.1f}s")

    roots = [planet, *scatter_roots, build_moon(), build_sky_planet()]
    for i in range(4):
        isl = build_island(i)
        bake_ao([ob for ob in isl.children_recursive if ob.type == "MESH"], [],
                samples=args.ao, max_dist=2.5, floor=0.55)
        roots.append(isl)
    return roots


def render_previews(folder):
    sc = bpy.context.scene
    for ob in bpy.data.objects:
        ob.hide_render = ob.name.startswith(("FloatRock", "SkyPlanet", "Moon"))
    spawn = SPAWN * R
    up = SPAWN
    cam = spawn + up * 7 + Vector((0, -13, 0))
    preview.render(os.path.join(folder, "planet_ground.png"), cam, target=spawn + up * 1.5,
                   lens=32)
    preview.render(os.path.join(folder, "planet_far.png"), (110, -60, 55), lens=50)
    for ob in bpy.data.objects:
        ob.hide_render = False
