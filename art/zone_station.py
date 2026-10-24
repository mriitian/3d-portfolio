"""04 Space Station (Experience): a long glass-and-hull module on pylons, with solar wings."""
import math

from blender_lib import Group, P, ring_points, rot, tr
from zone_common import barrel, crate, lamp_post, pad_disc, railing


def solar_wing(g, x, side):
    """A boom with three big panels, reaching sideways from the module."""
    zc = 6.4
    g.metal.tube((x, 0, zc), (x, side * 4.6, zc), 0.07, segs=8, color=P["gunmetal"])
    for i in range(3):
        y = side * (1.7 + i * 1.5)
        g.metal.box((1.5, 1.4, 0.07), (x, y, zc - 0.035), color=P["metal"], center=True)
        g.metal.box((1.34, 1.24, 0.1), (x, y, zc - 0.03), color=P["panel"], center=True)
        for k in (-1, 0, 1):
            g.metal.box((0.03, 1.24, 0.12), (x + k * 0.33, y, zc - 0.03), color=P["panel_light"],
                        center=True)
        g.metal.box((1.34, 0.03, 0.12), (x, y, zc - 0.03), color=P["panel_light"], center=True)


def build():
    g = Group("Zone_experience", seed=404)
    pad_disc(g, 6.4, 0.4, P["plaza_dark"], segs=8)
    pad_disc(g, 5.8, 0.52, P["plaza"], segs=8)
    for x, y, a in ring_points(8, 5.4, 22.5):
        g.g("violet").box((1.1, 0.14, 0.05), (x, y, 0.5), (0, 0, a + 90))
    g.g("violet").torus(3.4, 0.04, (0, 0, 0.55), major=72, minor=6)

    # ---- two pylons carrying the module
    zt = 4.3
    for sx in (-1, 1):
        x = sx * 2.5
        g.metal.cyl(0.85, 0.5, 3.1, (x, 0, 0.5), segs=24, color=P["white"])
        g.metal.cyl(0.95, 0.95, 0.22, (x, 0, 0.5), segs=24, color=P["gunmetal"])
        g.metal.torus(1.25, 0.12, (x, 0, zt), (0, 90, 0), major=40, minor=8, color=P["gunmetal"])
        g.g("cyan").torus(1.25, 0.03, (x, 0, zt), (0, 90, 0), major=40, minor=6)

    # ---- the module: hull, glowing window bands with ribs, docking noses
    L, tube_rot = 4.7, (0, 90, 0)
    g.paint.lathe([(1.15, -3.0), (1.17, -2.9), (1.17, 3.0), (1.15, 3.1)], (0, 0, zt), tube_rot,
                  segs=44, color=P["white"], caps=False)
    for sx in (-1, 1):
        zc = sx * 1.9
        g.g("cyan").lathe([(1.185, zc - 0.78), (1.185, zc + 0.78)], (0, 0, zt), tube_rot, segs=44,
                          caps=False)
        for k in (-1, 0, 1):
            g.metal.torus(1.2, 0.04, (zc + k * 0.85, 0, zt), tube_rot, major=44, minor=6,
                          color=P["gunmetal"])
        # nose
        g.paint.lathe([(1.15, sx * 3.1), (1.0, sx * 3.5), (0.78, sx * 4.2), (0.7, sx * 4.7)],
                      (0, 0, zt), tube_rot, segs=36, color=P["white"], caps=False)
        g.metal.torus(0.74, 0.1, (sx * 4.7, 0, zt), tube_rot, major=36, minor=8,
                      color=P["gunmetal"])
        g.g("orange").lathe([(0.62, sx * 4.72), (0.0, sx * 4.72)], (0, 0, zt), tube_rot,
                            segs=28, caps=False)
    for z in (-0.55, 0.0, 0.55):
        g.paint.torus(1.2, 0.07, (z, 0, zt), tube_rot, major=44, minor=8, color=P["orange"])
    g.paint.cyl(0.35, 0.45, 0.5, (0, 0, zt + 1.1), segs=20, color=P["white"])
    g.metal.cyl(0.18, 0.18, 0.9, (0, 0, zt + 1.55), segs=14, color=P["gunmetal"])
    g.g("red").ball(0.11, (0, 0, zt + 2.5), 3)
    solar_wing(g, -0.4, -1)
    solar_wing(g, -0.4, 1)

    # ---- airlock, stairs, cargo, comms dish
    g.lit.box((1.8, 1.6, 1.6), (0, -3.8, 0.45), color=P["cream"])
    g.paint.box((1.9, 1.7, 0.2), (0, -3.8, 2.05), color=P["orange"])
    g.g("amber").box((0.9, 0.05, 1.0), (0, -4.62, 0.9))
    for i in range(4):
        g.lit.box((1.3, 0.4, 0.14), (0, -4.7 - i * 0.3 + 0.0, 0.45 - 0.0 + i * 0.0), color=P["stone_dark"])
    crate(g, 3.9, -3.3, 15, (1.1, 1.1, 1.1), P["stone_dark"], P["violet"])
    crate(g, 4.9, -2.4, -10, (0.8, 0.8, 0.8), P["orange_deep"], P["cream"])
    crate(g, -4.3, -3.5, 25, (1.0, 1.0, 1.0), P["white"], P["cyan"])
    barrel(g, -3.3, -4.4)
    barrel(g, -2.6, -4.7, P["cream"])
    g.metal.cyl(0.5, 0.6, 0.4, (-4.2, 3.4, 0.5), segs=16, color=P["gunmetal"])
    g.metal.tube((-4.2, 3.4, 0.9), (-4.2, 3.4, 2.1), 0.1, segs=10)
    from zone_common import dish
    dish(g, tr(-4.2, 3.4, 2.2) @ rot(-50, 0, 35), 0.55, True, "violet")
    for x, y, a in ring_points(4, 5.5, 20):
        lamp_post(g, x, y, "violet", 2.6)
    return g.build()
