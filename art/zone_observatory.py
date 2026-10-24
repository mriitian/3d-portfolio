"""03 Observatory (Skills): a domed building with a glowing energy orb and holo panels."""
import math

import bmesh
from mathutils import Vector

from blender_lib import Group, P, ring_points, rot, tr
from zone_common import crate, lamp_post, pad_disc, window


def holo_panel(g, x, y, yaw, key, rows=3):
    b = tr(x, y, 0) @ rot(0, 0, yaw)
    g.metal.cyl(0.07, 0.09, 1.2, (0, 0, 0), segs=12, color=P["gunmetal"], base=b)
    g.metal.box((1.5, 0.12, 1.6), (0, 0, 1.2), color=P["iron"], base=b)
    g.g(key).box((1.34, 0.05, 1.44), (0, -0.085, 1.2), base=b)
    for i in range(rows):
        g.g("white").box((0.9, 0.04, 0.1), (0.0, -0.12, 1.45 + 0.0 - i * 0.28), base=b)
    g.g("white").ball(0.13, (-0.45, -0.12, 2.08), 3, base=b)


def build():
    g = Group("Zone_skills", seed=303)
    pad_disc(g, 6.4, 0.4, P["plaza_dark"])
    pad_disc(g, 5.7, 0.55, P["plaza"])
    pad_disc(g, 4.6, 0.7, P["stone_dark"])
    g.g("cyan").torus(4.2, 0.07, (0, 0, 0.72), major=72, minor=8)
    g.g("cyan").torus(3.65, 0.04, (0, 0, 0.72), major=72, minor=6)
    for x, y, a in ring_points(12, 5.2):
        g.g("amber").cyl(0.08, 0.08, 0.08, (x, y, 0.55), segs=10)

    # ---- drum + dome with an open slit and a glowing orb inside
    zd = 3.6
    g.lit.cyl(3.15, 3.05, 3.0, (0, 0, 0.7), segs=40, color=P["cream"])
    g.paint.cyl(3.25, 3.25, 0.28, (0, 0, 0.7), segs=40, color=P["stone_dark"])
    g.paint.cyl(3.28, 3.28, 0.24, (0, 0, 3.4), segs=40, color=P["violet"])
    for x, y, a in ring_points(10, 3.1, 18):
        if abs(((a + 360) % 360) - 270) < 25:
            continue
        window(g, (x * 1.0, y * 1.0, 1.9), (0.5, 0.95), a - 90)
    g.metal.box((1.3, 0.3, 1.9), (0, -3.1, 0.7), color=P["iron"])
    g.g("amber").box((0.95, 0.05, 1.55), (0, -3.27, 0.78))
    g.lit.box((2.0, 1.2, 0.18), (0, -3.5, 0.5), color=P["stone_dark"])

    # dome with a round window cut into its front, trimmed with a metal ring
    prof = [(3.1 * math.cos(math.radians(t)), zd + 3.1 * math.sin(math.radians(t)))
            for t in range(0, 90, 5)] + [(0.0, zd + 3.1)]
    before = set(g.paint.bm.faces)
    g.paint.lathe(prof, segs=96, color=P["white"], caps=False)
    shell = [f for f in g.paint.bm.faces if f not in before]
    look = Vector((0, -math.cos(math.radians(32)), math.sin(math.radians(32))))
    hole = math.radians(25)
    doomed = []
    for f in shell:
        c = f.calc_center_median() - Vector((0, 0, zd))
        if c.length > 1e-6 and math.acos(max(-1, min(1, c.normalized().dot(look)))) < hole:
            doomed.append(f)
    bmesh.ops.delete(g.paint.bm, geom=doomed, context="FACES")
    before_in = set(g.lit.bm.faces)
    g.lit.lathe([(2.95 * math.cos(math.radians(t)), zd + 2.95 * math.sin(math.radians(t)))
                 for t in range(0, 90, 5)] + [(0.0, zd + 2.95)], segs=96, color=P["navy"],
                caps=False)
    inner = []
    for f in g.lit.bm.faces:
        if f in before_in:
            continue
        c = f.calc_center_median() - Vector((0, 0, zd))
        if c.length > 1e-6 and math.acos(max(-1, min(1, c.normalized().dot(look)))) < hole + 0.1:
            inner.append(f)
    bmesh.ops.delete(g.lit.bm, geom=inner, context="FACES")
    ring_c = Vector((0, 0, zd)) + look * (3.1 * math.cos(hole))
    ring_q = Vector((0, 0, 1)).rotation_difference(look).to_matrix().to_4x4()
    ring_base = tr(*ring_c) @ ring_q
    g.metal.torus(3.1 * math.sin(hole) + 0.04, 0.12, (0, 0, 0), major=56, minor=10,
                  color=P["gunmetal"], base=ring_base)
    g.g("cyan").torus(3.1 * math.sin(hole) - 0.08, 0.035, (0, 0, 0.05), major=56, minor=6,
                      base=ring_base)
    # the energy orb seen through the window, wrapped in rings
    orb = (0, 0, zd + 1.35)
    g.g("blue").ball(1.25, orb, 4)
    g.g("white").ball(0.7, orb, 3)
    g.g("cyan").torus(1.75, 0.05, orb, (70, 0, 0), major=64, minor=6)
    g.g("cyan").torus(1.55, 0.04, orb, (0, 65, 25), major=64, minor=6)
    g.metal.cyl(1.0, 1.2, 0.6, (0, 0, zd - 0.05), segs=28, color=P["gunmetal"])
    g.metal.tube((0, 0, zd + 3.1), (0, 0, zd + 4.4), 0.05, segs=8)
    g.g("red").ball(0.1, (0, 0, zd + 4.45), 3)

    # ---- outbuildings, panels, constellation
    for sx in (-1, 1):
        x, y = sx * 4.7, 1.8
        g.lit.cyl(1.0, 1.05, 1.9, (x, y, 0.55), segs=24, color=P["cream"])
        g.paint.lathe([(1.1 * math.cos(math.radians(t)), 2.45 + 1.1 * math.sin(math.radians(t)))
                       for t in range(0, 90, 15)] + [(0, 3.55)], (x, y, 0), segs=24,
                      color=P["white"], caps=False)
        g.g("amber").box((0.3, 0.06, 0.5), (x, y - 1.02, 1.5), center=True)
    holo_panel(g, -3.3, -4.4, -22, "cyan")
    holo_panel(g, 0.0, -5.3, 0, "blue")
    holo_panel(g, 3.3, -4.4, 22, "cyan")

    stars = [(-4.6, 2.4, 7.2, "white"), (-2.9, 3.4, 8.6, "cyan"), (-0.3, 4.0, 9.4, "yellow"),
             (2.7, 3.4, 8.4, "white"), (4.8, 1.8, 7.3, "cyan"), (5.2, -1.0, 8.6, "yellow"),
             (-5.0, -1.0, 8.4, "cyan")]
    for i, (x, y, z, key) in enumerate(stars):
        g.g(key).ball(0.22, (x, y, z), 3, scale=(1, 1, 1.2), rotation=(0, 0, 40 * i))
        g.g(key).ball(0.34, (x, y, z), 2)
        if i:
            px, py, pz, _ = stars[i - 1]
            g.g("white").tube((px, py, pz), (x, y, z), 0.02, segs=4)
    crate(g, 4.9, -2.6, 15, (0.9, 0.9, 0.9), P["stone_dark"], P["cyan"])
    for x, y, a in ring_points(4, 5.5, 45):
        lamp_post(g, x, y, "cyan", 2.6)
    return g.build()


# solid parts, as (x, y, radius) in this zone's own frame; the game stops the rover at these
COLLIDERS = [(0, 0, 3.4), (-4.7, 1.8, 1.15), (4.7, 1.8, 1.15), (0, -5.3, 0.8)]
