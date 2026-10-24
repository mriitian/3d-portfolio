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
SOLIDS = []  # (direction in Blender space, radius) of props the rover must not drive through

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

        # the road bed (the raised pavements and curbs are modelled separately)
        d_path = tree.find(co.normalized() * R)[2]
        col = mix(col, P["asphalt"], 1.0 - smooth(2.8, 3.4, d_path))
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


def broadleaf(g, base, leaf):
    """A broadleaf tree: flared trunk, two limbs, layered lumpy canopy and glowing fruit."""
    g.lit.lathe([(0.6, 0.0), (0.4, 0.35), (0.27, 1.1), (0.23, 2.1), (0.2, 2.7)], segs=14,
                color=P["trunk"], base=base, caps=False)
    for sx in (-1, 1):
        g.lit.tube((0, 0, 1.9), (sx * 0.95, sx * 0.15, 3.0), 0.1, segs=8, color=P["trunk"],
                   base=base)
    for x, y, z, r in ((0, 0, 3.5, 1.35), (1.0, 0.3, 3.1, 0.95), (-0.95, -0.25, 3.15, 1.0),
                       (0.15, -1.0, 3.6, 0.9), (0.25, 1.0, 3.8, 0.85), (0, 0, 4.5, 0.85)):
        g.lit.ball(r, (x, y, z), 3, color=leaf, lump=0.22, grad=(2.2, 5.4, 0.62, 1.3), base=base)
    for x, y, z in ((1.0, -0.9, 3.2), (-1.1, 0.5, 3.6), (0.3, 1.4, 3.7), (-0.2, -1.4, 3.0)):
        g.g("cyan").ball(0.09, (x, y, z), 2, base=base)


def glow_tree(g, base):
    """A rarer twisted tree with a violet crown hung with glowing orbs."""
    pts = [(0, 0, 0), (0.3, 0.1, 1.2), (-0.2, 0.3, 2.3), (0.2, -0.1, 3.3), (0, 0, 4.2)]
    for a, b in zip(pts, pts[1:]):
        g.lit.tube(a, b, 0.2, segs=10, color=P["trunk"], base=base)
    for x, y, z, r in ((0, 0, 4.6, 1.2), (1.0, 0.4, 4.2, 0.8), (-0.9, -0.3, 4.3, 0.85),
                       (0.1, -0.9, 4.0, 0.7)):
        g.lit.ball(r, (x, y, z), 3, color=P["leaf_amber"], lump=0.25,
                   grad=(3.2, 5.8, 0.7, 1.25), base=base)
    for i in range(7):
        a = i * 0.9
        g.g("violet").ball(0.1, (math.cos(a) * 1.4, math.sin(a) * 1.4, 3.6 + (i % 3) * 0.5), 2,
                           base=base)


def conifer(g, base, leaf):
    """A tall tiered conifer, frosted toward the tip."""
    g.lit.lathe([(0.34, 0.0), (0.24, 0.5), (0.2, 1.4)], segs=10, color=P["trunk"], base=base,
                caps=False)
    tiers = [(1.65, 0.9, 1.5), (1.4, 1.9, 1.45), (1.15, 2.9, 1.4), (0.9, 3.8, 1.3),
             (0.65, 4.65, 1.2), (0.4, 5.4, 1.1)]
    for i, (r, z, h) in enumerate(tiers):
        col = mix(leaf, P["leaf_teal"], i / len(tiers) * 0.7)
        g.lit.lathe([(r, z), (r * 0.9, z + h * 0.18), (r * 0.62, z + h * 0.5),
                     (r * 0.28, z + h * 0.8), (0.0, z + h)], segs=22, color=col,
                    grad=(0.9, 6.5, 0.6, 1.3), base=base, caps=True)
    g.g("ice").ball(0.1, (0, 0, 6.55), 2, base=base)


def bush(g, base, leaf):
    for x, y, z, r in ((0, 0, 0.5, 0.8), (0.7, 0.25, 0.4, 0.55), (-0.6, -0.3, 0.42, 0.6)):
        g.lit.ball(r, (x, y, z), 3, scale=(1.2, 1, 0.8), color=leaf, lump=0.28,
                   grad=(0, 1.3, 0.6, 1.25), base=base)
    for x, y, z in ((0.5, -0.6, 0.7), (-0.4, 0.6, 0.8), (0.1, 0.1, 1.05)):
        g.g("magenta").ball(0.07, (x, y, z), 2, base=base)


def rock(g, base, size, shade):
    g.lit.ball(size, (0, 0, size * 0.3), 3, scale=(1.2, 1.0, 0.72), color=shade, lump=0.42,
               lump_freq=1.9, grad=(0, size * 1.2, 0.7, 1.15), base=base)
    if size > 0.9:  # a mossy cap on the bigger ones
        g.lit.ball(size * 0.75, (0, 0, size * 0.5), 3, scale=(1.0, 0.85, 0.4),
                   color=P["grass_dark"], lump=0.3, base=base)


def tuft(g, base, glow=False):
    for dx, dy, tilt, h in ((0, 0, 0, 0.75), (0.16, 0.05, 14, 0.55), (-0.13, 0.09, -13, 0.6)):
        g.lit.cyl(0.08, 0.0, h, (dx, dy, 0), (tilt, tilt * 0.5, 0), segs=5,
                  color=P["grass_light"], grad=(0, 0.7, 0.7, 1.2), base=base, caps=False)
    if glow:
        g.g("cyan").ball(0.05, (0, 0, 0.8), 2, base=base)


def mushroom(g, base, key):
    """Bioluminescent mushroom: pale stem, glowing cap."""
    g.lit.lathe([(0.15, 0.0), (0.1, 0.3), (0.09, 0.6)], segs=10, color=P["pavement"],
                base=base, caps=False)
    g.g(key).ball(0.42, (0, 0, 0.66), 3, scale=(1, 1, 0.5), base=base)


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
        if arc_dist(d, SPAWN) < 9.5:
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

    leaves = [P["leaf_green"], P["leaf_lime"], P["leaf_teal"], P["leaf_green"], P["leaf_pink"]]
    solids = []

    def tree_fn(d, g):
        s = rng.uniform(0.9, 1.4)
        b = place(d, rng.uniform(0, 360), s)
        if rng.random() < 0.25:
            glow_tree(g, b)
        else:
            broadleaf(g, b, rng.choice(leaves))
        solids.append((d, 0.6 * s))

    def pine_fn(d, g):
        s = rng.uniform(0.85, 1.3)
        conifer(g, place(d, rng.uniform(0, 360), s),
                rng.choice([P["leaf_green"], P["grass_dark"], P["leaf_teal"]]))
        solids.append((d, 1.0 * s))

    def bush_fn(d, g):
        s = rng.uniform(0.8, 1.3)
        bush(g, place(d, rng.uniform(0, 360), s),
             rng.choice([P["leaf_green"], P["leaf_lime"], P["grass"]]))
        solids.append((d, 0.9 * s))

    def rock_fn(d, g):
        size = rng.uniform(0.55, 1.6)
        rock(g, place(d, rng.uniform(0, 360)), size,
             rng.choice([P["rock"], P["rock_dark"], P["rock_light"]]))
        solids.append((d, size * 1.1))

    def crystal_fn(d, g):
        s = rng.uniform(0.9, 1.5)
        crystal_cluster(g, place(d, rng.uniform(0, 360), s),
                        rng.choice(["cyan", "magenta", "violet", "cyan", "blue"]))
        solids.append((d, 0.85 * s))

    def mushroom_fn(d, g):
        mushroom(g, place(d, rng.uniform(0, 360), rng.uniform(0.9, 1.7)),
                 rng.choice(["magenta", "cyan", "violet"]))

    def tuft_fn(d, g):
        tuft(g, place(d, rng.uniform(0, 360), rng.uniform(0.8, 1.4)), glow=rng.random() < 0.25)

    scatter(34, 16.0, 4.4, 5.5, tree_fn)
    scatter(34, 16.0, 4.4, 4.6, pine_fn)
    scatter(30, 15.0, 3.6, 3.0, bush_fn)
    scatter(54, 15.0, 3.4, 3.2, rock_fn)
    scatter(16, 15.0, 4.0, 5.0, crystal_fn)
    scatter(22, 15.0, 3.6, 2.6, mushroom_fn)
    scatter(180, 14.5, 3.0, 1.2, tuft_fn, tries=9000)

    # street lamps along the road, alternating sides
    side_sign = 1
    last = None
    for p, tangent in path_pts:
        d = p.normalized()
        if arc_dist(d, SPAWN) < 9 or any(arc_dist(d, z) < 17.0 for z in zone_list):
            continue
        if last is not None and arc_dist(d, last) < 8.5:
            continue
        side = d.cross(tangent).normalized() * side_sign
        lp = (p + side * 3.6).normalized()
        lamp_post(G(lp), 0, 0, "radium", 2.4, base=place(lp, rng.uniform(0, 360)))
        solids.append((lp, 0.3))
        side_sign *= -1
        last = d
    SOLIDS[:] = solids
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
        broadleaf(g, tr(0.6, 0.2, 0.5), P["leaf_pink"])
    elif index % 3 == 1:
        conifer(g, tr(-0.4, 0.3, 0.5), P["leaf_teal"])
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

    from world_road import build_road

    roots = [planet, *scatter_roots, build_road(dirs, path_pts), build_moon()]
    for i in range(4):
        isl = build_island(i)
        bake_ao([ob for ob in isl.children_recursive if ob.type == "MESH"], [],
                samples=args.ao, max_dist=2.5, floor=0.55)
        roots.append(isl)
    return roots


def render_previews(folder):
    sc = bpy.context.scene
    for ob in bpy.data.objects:
        ob.hide_render = ob.name.startswith(("FloatRock", "Moon"))
    spawn = SPAWN * R
    up = SPAWN
    cam = spawn + up * 7 + Vector((0, -13, 0))
    preview.render(os.path.join(folder, "planet_ground.png"), cam, target=spawn + up * 1.5,
                   lens=32)
    preview.render(os.path.join(folder, "planet_far.png"), (110, -60, 55), lens=50)
    for ob in bpy.data.objects:
        ob.hide_render = False
