"""The planet ground, scattered props, moon and floating rocks."""
import math
import random

import bmesh
import bpy
from mathutils import Matrix, Vector, kdtree, noise

from blender_lib import Group, Mesh, P, material, rot, tr

R = 40.0

# Must match src/game/zones.js (id, latitude, longitude in degrees).
ZONE_DEFS = [
    ("about", 8, 28),
    ("projects", 38, 105),
    ("skills", -34, 165),
    ("experience", 30, -115),
    ("contact", -32, -50),
]
SPAWN = Vector((1, 0, 0))


def from_latlon(lat, lon):
    la, lo = math.radians(lat), math.radians(lon)
    return Vector((math.cos(la) * math.cos(lo), math.sin(la), math.cos(la) * math.sin(lo))) \
        if False else Vector((math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la)))


def three_to_blender(v):
    """Three.js (x, y, z up=y) direction -> Blender coordinates (x, -z, y)."""
    return Vector((v[0], -v[2], v[1]))


def zone_dirs():
    """Zone directions in *Blender* space. src/game/zones.js uses
    (cos(lat)cos(lon), sin(lat), cos(lat)sin(lon)) in three.js space; glTF export
    maps three (x, y, z) from Blender (x, -z, y), so convert back here."""
    out = {}
    for zid, lat, lon in ZONE_DEFS:
        la, lo = math.radians(lat), math.radians(lon)
        t = Vector((math.cos(la) * math.cos(lo), math.sin(la), math.cos(la) * math.sin(lo)))
        out[zid] = three_to_blender(t)
    return out


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def arc_dist(a, b):
    return R * math.acos(max(-1.0, min(1.0, a.dot(b))))


# ------------------------------------------------------------- the path ---


def build_path_points(dirs):
    """A meandering loop that visits spawn -> every zone -> spawn."""
    order = [three_to_blender(Vector((1, 0, 0)))] + [
        dirs[z] for z in ("about", "projects", "skills", "experience", "contact")
    ]
    order.append(order[0])
    pts = []  # (position on sphere, tangent)
    rng = random.Random(5)
    for i in range(len(order) - 1):
        a, b = order[i].normalized(), order[i + 1].normalized()
        length = arc_dist(a, b)
        n = max(2, int(length / 0.45))
        phase = rng.uniform(0, math.tau)
        sway = rng.uniform(1.4, 2.6)
        for k in range(n):
            t = k / n
            p = a.slerp(b, t)
            tangent = (a.slerp(b, min(1.0, t + 0.01)) - p).normalized()
            side = p.cross(tangent).normalized()
            fade = math.sin(math.pi * t)  # no sway at the zones themselves
            offset = side * (math.sin(t * math.pi * 3 + phase) * sway * fade / R)
            p = (p + offset).normalized()
            pts.append((p * R, tangent))
    return pts


# ------------------------------------------------------------ the planet ---


def build_planet(dirs, path_pts):
    noise.seed_set(11)
    rng = random.Random(3)
    m = Mesh("Planet", jitter=0.0, ao=False, seed=3)
    bmesh.ops.create_icosphere(m.bm, subdivisions=5, radius=R, calc_uvs=False)

    tree = kdtree.KDTree(len(path_pts))
    for i, (p, _) in enumerate(path_pts):
        tree.insert(p, i)
    tree.balance()

    craters = []
    cr = random.Random(21)
    while len(craters) < 9:
        d = Vector((cr.uniform(-1, 1), cr.uniform(-1, 1), cr.uniform(-1, 1)))
        if d.length < 0.1:
            continue
        d.normalize()
        if any(arc_dist(d, zd) < 13 for zd in dirs.values()):
            continue
        if tree.find(d * R)[2] < 7:
            continue
        if arc_dist(d, three_to_blender(SPAWN)) < 12:
            continue
        craters.append((d, cr.uniform(2.4, 4.4)))

    spawn = three_to_blender(SPAWN)
    base_cols = [P["ground_a"], P["ground_b"], P["ground_c"], P["ground_d"]]

    bm = m.bm
    for f in bm.faces:
        c = f.calc_center_median().normalized()
        pos = c * R

        # ground: blend of four tints driven by two noise fields
        n1 = noise.noise(c * 2.4)
        n2 = noise.noise(c * 5.5 + Vector((9, 3, 1)))
        col = mix(base_cols[0], base_cols[1], n1 * 0.5 + 0.5)
        col = mix(col, base_cols[2], max(0.0, n2) * 1.2)
        col = mix(col, base_cols[3], max(0.0, -n1 - 0.25) * 1.4)

        # craters
        for d, rad in craters:
            dd = arc_dist(c, d)
            if dd < rad * 0.72:
                col = P["crater"]
            elif dd < rad:
                col = P["crater_rim"]

        # plazas under each zone
        for zd in dirs.values():
            if arc_dist(c, zd) < 7.4:
                col = P["plaza"]
        if arc_dist(c, spawn) < 5.0:
            col = P["slate_light"]

        # the orange road
        dpath = tree.find(pos)[2]
        if dpath < 2.1:
            col = P["path"]
        elif dpath < 3.4:
            col = mix(col, P["path_edge"], 0.9 if dpath < 2.9 else 0.5)

        k = 1.0 + rng.uniform(-0.05, 0.05)
        for loop in f.loops:
            loop[m.col] = (col[0] * k, col[1] * k, col[2] * k, 1.0)

    obj = m.to_object(name="Planet")
    m.free()
    return obj


# --------------------------------------------------------------- props ---


def place(direction, yaw=0.0, scale=1.0, lift=0.0):
    q = Vector((0, 0, 1)).rotation_difference(direction.normalized()).to_matrix().to_4x4()
    return tr(*(direction.normalized() * (R + lift))) @ q @ rot(0, 0, yaw) @ Matrix.Scale(scale, 4)


def round_tree(g, base, leaf):
    g.lit.cyl(0.2, 0.3, 1.7, segs=6, color=P["trunk"], base=base)
    g.lit.ball(1.15, (0, 0, 2.4), 1, color=leaf, noise=0.12, base=base)
    g.lit.ball(0.8, (0.7, 0.25, 3.1), 1, color=leaf, noise=0.1, base=base)
    g.lit.ball(0.7, (-0.6, -0.3, 3.0), 1, color=leaf, noise=0.1, base=base)


def pine_tree(g, base, leaf):
    g.lit.cyl(0.16, 0.24, 1.1, segs=5, color=P["trunk"], base=base)
    for i, (r, z, h) in enumerate([(1.35, 0.8, 1.6), (1.0, 1.9, 1.5), (0.65, 2.9, 1.4)]):
        g.lit.cyl(r, 0.04, h, (0, 0, z), segs=7, color=leaf, base=base)


def rock(g, base, size, shade):
    g.lit.ball(size, (0, 0, size * 0.35), 1, scale=(1.1, 0.95, 0.72), color=shade,
               noise=0.22, base=base)


def tuft(g, base):
    for dx, dy, tilt, h in [(0, 0, 0, 0.7), (0.14, 0.05, 14, 0.5), (-0.12, 0.08, -12, 0.55)]:
        g.lit.cyl(0.07, 0.0, h, (dx, dy, 0), (tilt, tilt * 0.5, 0), segs=3,
                  color=P["grass"], jitter=0.12, base=base)


def mushroom(g, base, cap):
    g.lit.cyl(0.1, 0.13, 0.55, segs=5, color=P["white"], base=base)
    g.lit.ball(0.4, (0, 0, 0.62), 1, scale=(1, 1, 0.55), color=cap, base=base)


def crystal_cluster(g, base, key):
    glow = g.g(key)
    for dx, dy, tilt_x, tilt_y, h, r in [(0, 0, 0, 0, 1.9, 0.38), (0.5, 0.2, 18, 12, 1.2, 0.28),
                                         (-0.45, 0.1, -16, -10, 1.0, 0.26),
                                         (0.1, -0.5, 10, -20, 0.8, 0.22)]:
        glow.cyl(r, 0.0, h, (dx, dy, 0), (tilt_x, tilt_y, 0), segs=5, base=base)
    g.lit.ball(0.6, (0, 0, 0.1), 1, scale=(1.4, 1.2, 0.5), color=P["rock_dark"], noise=0.2,
               base=base)


def lamp(g, base):
    g.lit.cyl(0.07, 0.09, 1.9, segs=5, color=P["metal_dark"], base=base)
    g.lit.box((0.32, 0.32, 0.08), (0, 0, 1.9), color=P["metal_dark"], base=base)
    g.g("orange").ball(0.24, (0, 0, 2.12), 1, base=base)


def build_scatter(dirs, path_pts):
    g = Group("Scatter", ao=(0.0, 4.5, 0.62, 1.1), seed=9)
    rng = random.Random(77)

    path_tree = kdtree.KDTree(len(path_pts))
    for i, (p, _) in enumerate(path_pts):
        path_tree.insert(p, i)
    path_tree.balance()

    zone_list = list(dirs.values())
    spawn = three_to_blender(SPAWN)
    placed = []

    def ok(d, min_zone, min_path, min_gap):
        if any(arc_dist(d, z) < min_zone for z in zone_list):
            return False
        if arc_dist(d, spawn) < 8:
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
            fn(d)
            n += 1

    leaves = [P["leaf_pink"], P["leaf_teal"], P["leaf_amber"], P["leaf_violet"], P["leaf_pink"]]

    scatter(46, 10.5, 4.2, 5.0,
            lambda d: round_tree(g, place(d, rng.uniform(0, 360), rng.uniform(0.9, 1.5)),
                                 rng.choice(leaves)))
    scatter(40, 10.5, 4.2, 4.2,
            lambda d: pine_tree(g, place(d, rng.uniform(0, 360), rng.uniform(0.9, 1.4)),
                                rng.choice([P["leaf_teal"], P["leaf_violet"], P["grass_dark"]])))
    scatter(60, 9.0, 3.4, 3.0,
            lambda d: rock(g, place(d, rng.uniform(0, 360)), rng.uniform(0.5, 1.5),
                           rng.choice([P["rock"], P["rock_dark"], P["rock_light"]])))
    scatter(20, 9.5, 3.8, 4.5,
            lambda d: crystal_cluster(g, place(d, rng.uniform(0, 360), rng.uniform(0.9, 1.5)),
                                      rng.choice(["cyan", "magenta", "cyan"])))
    scatter(26, 9.0, 3.4, 2.5,
            lambda d: mushroom(g, place(d, rng.uniform(0, 360), rng.uniform(0.8, 1.6)),
                               rng.choice([P["mushroom"], P["leaf_amber"], P["leaf_violet"]])))
    scatter(260, 8.0, 3.0, 1.0,
            lambda d: tuft(g, place(d, rng.uniform(0, 360), rng.uniform(0.8, 1.4))), tries=9000)

    # street lamps: along the road, on alternating sides
    side_sign = 1
    last = None
    for p, tangent in path_pts:
        d = p.normalized()
        if arc_dist(d, spawn) < 6 or any(arc_dist(d, z) < 8.5 for z in zone_list):
            continue
        if last is not None and arc_dist(d, last) < 9.0:
            continue
        side = d.cross(tangent).normalized() * side_sign
        lp = (p + side * 3.0).normalized()
        lamp(g, place(lp, rng.uniform(0, 360)))
        side_sign *= -1
        last = d

    return g.build()


# ------------------------------------------------------ moon + floating rocks ---


def build_moon():
    noise.seed_set(4)
    m = Mesh("Moon", jitter=0.0, ao=False, seed=2)
    bmesh.ops.create_icosphere(m.bm, subdivisions=3, radius=6.0, calc_uvs=False)
    cr = random.Random(8)
    craters = [(Vector((cr.uniform(-1, 1), cr.uniform(-1, 1), cr.uniform(-1, 1))).normalized(),
                cr.uniform(0.7, 1.4)) for _ in range(9)]
    base = (0.78, 0.76, 0.9)
    for f in m.bm.faces:
        c = f.calc_center_median().normalized()
        col = tuple(v * (0.72 + 0.1 * noise.noise(c * 3)) for v in base)
        for d, rad in craters:
            dd = 6.0 * math.acos(max(-1, min(1, c.dot(d))))
            if dd < rad * 0.7:
                col = tuple(v * 0.45 for v in base)
            elif dd < rad:
                col = tuple(min(1, v * 1.15) for v in base)
        for loop in f.loops:
            loop[m.col] = (*col, 1.0)
    obj = m.to_object(name="Moon")
    m.free()
    return obj


def build_floating_rocks():
    objs = []
    for i in range(3):
        g = Group(f"FloatRock_{i}", ao=(-3.0, 1.0, 0.55, 1.1), seed=30 + i)
        rng = random.Random(40 + i)
        top = 2.2 + i * 0.3
        g.lit.cyl(top, top * 0.92, 0.55, (0, 0, 0), segs=9, color=P["ground_b"], jitter=0.06)
        g.lit.cyl(top * 0.9, 0.35, 2.6 + i * 0.5, (0, 0, -2.6 - i * 0.5), segs=7,
                  color=P["rock"], jitter=0.08)
        g.lit.cyl(0.35, 0.05, 1.6, (0.1, 0.1, -4.2 - i * 0.5), segs=5, color=P["rock_dark"])
        if i == 0:
            round_tree(g, tr(0.4, 0.2, 0.55), P["leaf_pink"])
        elif i == 1:
            pine_tree(g, tr(-0.3, 0.1, 0.55), P["leaf_teal"])
        else:
            crystal_cluster(g, tr(0.2, -0.2, 0.55), "magenta")
        objs.append(g.build())
    return objs
