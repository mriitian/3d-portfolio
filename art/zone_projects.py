"""02 Creative District (Projects): a neon arcade studio with a glowing gamepad sign."""
import math

from blender_lib import Group, P, ring_points, rot, tr
from zone_common import crate, lamp_post, pad_disc, window


def arcade_cabinet(g, x, y, body, screen_key, trim_key):
    """An arcade machine facing -Y."""
    b = tr(x, y, 0)
    g.paint.box((1.25, 1.0, 2.0), (0, 0, 0.0), color=body, base=b)
    g.paint.box((1.3, 1.05, 0.34), (0, 0, 2.0), color=P["navy"], base=b)
    g.g(trim_key).box((1.1, 0.06, 0.2), (0, -0.54, 2.07), base=b)
    g.paint.box((1.0, 0.7, 0.16), (0, -0.55, 1.12), (-22, 0, 0), color=P["iron"], base=b)
    g.metal.box((1.0, 0.18, 0.9), (0, -0.46, 1.16), (-12, 0, 0), color=P["gunmetal"], base=b)
    g.g(screen_key).box((0.84, 0.05, 0.7), (0, -0.56, 1.28), (-12, 0, 0), base=b)
    g.metal.tube((-0.22, -0.7, 1.1), (-0.22, -0.78, 1.34), 0.03, segs=8, base=b)
    g.g("red").ball(0.07, (-0.22, -0.8, 1.38), 3, base=b)
    for i, key in enumerate(("yellow", "cyan", "magenta")):
        g.g(key).ball(0.055, (0.08 + i * 0.17, -0.73, 1.26), 3, base=b)
    g.g("amber").box((0.3, 0.04, 0.16), (0.3, -0.52, 0.42), base=b)


def gamepad(g, base):
    """A big glowing gamepad, centred on `base`."""
    gl = g.g("violet")
    gl.box((2.2, 0.28, 1.0), (0, 0, 0), color=None, center=True, base=base)
    for sx in (-1, 1):
        gl.ball(0.62, (sx * 1.15, 0, -0.25), 3, scale=(1.0, 0.45, 1.5), base=base)
    g.g("white").box((0.5, 0.06, 0.14), (-0.78, -0.17, 0.08), center=True, base=base)
    g.g("white").box((0.14, 0.06, 0.5), (-0.78, -0.17, 0.08), center=True, base=base)
    for dx, dz, key in ((0.0, 0.0, "cyan"), (0.3, 0.0, "yellow"), (0.15, 0.2, "orange"),
                        (0.15, -0.2, "magenta")):
        g.g(key).ball(0.1, (0.82 + dx, -0.17, 0.08 + dz), 3, base=base)
    for sx in (-1, 1):
        g.g("white").cyl(0.14, 0.14, 0.05, (sx * 0.3, -0.17, -0.3), (90, 0, 0), segs=20,
                         center=True, base=base)
    g.g("magenta").torus(1.9, 0.045, (0, 0.2, 0), (90, 0, 0), major=64, minor=6, base=base)


def build():
    g = Group("Zone_projects", seed=202)
    pad_disc(g, 6.4, 0.4, P["plaza_dark"])
    pad_disc(g, 5.8, 0.52, P["plaza"])
    g.g("magenta").torus(5.35, 0.05, (0, 0, 0.55), major=72, minor=6)
    g.g("cyan").torus(4.7, 0.04, (0, 0, 0.55), major=72, minor=6)

    # ---- studio building with a display wall and a glowing entrance
    by = 2.3
    g.lit.box((6.6, 3.4, 3.3), (0, by, 0.5), color=P["cream"])
    g.lit.box((7.0, 3.8, 0.3), (0, by, 3.8), color=P["roof"])
    g.paint.box((6.7, 0.25, 0.28), (0, by - 1.8, 3.55), color=P["orange"])
    g.lit.box((6.8, 0.3, 0.5), (0, by - 1.75, 0.2), color=P["stone_dark"])
    keys = ["cyan", "magenta", "blue", "orange", "violet", "cyan", "magenta", "blue"]
    n = 0
    for row, z in enumerate((1.05, 2.45)):
        for x in (-2.55, -1.4, 1.4, 2.55):
            window(g, (x, by - 1.72, z), (0.9, 0.9), 0, keys[n % len(keys)])
            n += 1
    g.metal.box((1.5, 0.3, 2.3), (0, by - 1.75, 0.5), color=P["iron"])
    g.g("amber").box((1.15, 0.05, 1.9), (0, by - 1.92, 0.55))
    g.metal.torus(0.62, 0.07, (0, by - 1.93, 2.35), (90, 0, 0), major=32, minor=8, arc=180,
                  color=P["gunmetal"])
    # roof dome + antenna
    dome = [(1.9 * math.cos(math.radians(t)), 4.1 + 1.9 * math.sin(math.radians(t)))
            for t in range(0, 90, 10)] + [(0.0, 6.0)]
    g.paint.lathe(dome, (0, by, 0), segs=40, color=P["white"], caps=False)
    g.g("cyan").torus(1.92, 0.05, (0, by, 4.25), major=64, minor=6)
    g.metal.tube((0, by, 6.0), (0, by, 7.2), 0.04, segs=8)
    g.g("red").ball(0.1, (0, by, 7.25), 3)
    # towers either side
    for sx in (-1, 1):
        x = sx * 4.1
        g.lit.cyl(1.05, 1.1, 5.2, (x, by, 0.5), segs=28, color=P["cream"])
        g.paint.cyl(1.2, 1.2, 0.22, (x, by, 5.3), segs=28, color=P["orange"])
        g.paint.lathe([(1.15, 5.52), (0.9, 6.0), (0.5, 6.5), (0.0, 6.9)], (x, by, 0), segs=28,
                      color=P["roof"], caps=False)
        for z in (1.6, 3.0, 4.4):
            g.g("amber").box((0.2, 0.06, 0.5), (x, by - 1.07, z), center=True)
    # glowing gamepad sign on a frame
    sign_z = 8.2
    g.metal.tube((-1.1, by - 0.4, 7.2), (-1.1, by - 0.4, sign_z - 0.7), 0.05, segs=8)
    g.metal.tube((1.1, by - 0.4, 7.2), (1.1, by - 0.4, sign_z - 0.7), 0.05, segs=8)
    gamepad(g, tr(0, by - 0.4, sign_z) @ rot(-8, 0, 0))

    # ---- crane
    cx, cy = -5.0, -1.0
    g.paint.box((1.4, 1.4, 0.5), (cx, cy, 0.4), color=P["orange_deep"])
    g.paint.box((0.5, 0.5, 6.2), (cx, cy, 0.9), color=P["orange"])
    g.metal.tube((cx, cy, 7.0), (cx + 5.8, cy, 6.35), 0.1, segs=10, color=P["orange_deep"])
    g.metal.tube((cx, cy, 7.0), (cx - 1.5, cy, 6.8), 0.1, segs=10, color=P["orange_deep"])
    g.metal.tube((cx, cy, 7.1), (cx + 5.6, cy, 6.4), 0.05, segs=6, color=P["gunmetal"])
    g.metal.box((0.7, 0.7, 0.6), (cx - 1.4, cy, 6.3), color=P["iron"])
    g.metal.tube((cx + 4.6, cy, 6.5), (cx + 4.6, cy, 4.5), 0.03, segs=6)
    crate(g, cx + 4.6, cy, 20, (0.8, 0.8, 0.8), P["cream"], P["orange"])
    g.lit.box((0.8, 0.8, 0.8), (cx + 4.6, cy, 3.9), color=P["stone_dark"])
    g.g("red").ball(0.1, (cx, cy, 7.25), 3)

    # ---- arcade cabinets, neon pylons, floating pixels
    arcade_cabinet(g, -1.9, -2.9, P["violet"], "cyan", "magenta")
    arcade_cabinet(g, 0.0, -3.3, P["orange_deep"], "magenta", "yellow")
    arcade_cabinet(g, 1.9, -2.9, P["panel"], "orange", "cyan")
    for sx, key in ((-1, "cyan"), (1, "magenta")):
        x, y = sx * 5.0, -2.4
        g.metal.cyl(0.14, 0.14, 4.6, (x, y, 0.2), segs=14, color=P["gunmetal"])
        for z in (1.0, 2.0, 3.0):
            g.g(key).torus(0.34, 0.04, (x, y, z), major=32, minor=6)
        g.g(key).box((0.9, 0.1, 0.5), (x, y, 4.8), center=True)
    for x, y, z, key, rx in ((-2.6, 0.0, 3.2, "cyan", 20), (2.7, -0.4, 3.6, "magenta", 40),
                             (0.0, -1.0, 3.0, "amber", 12), (-3.6, -1.4, 4.6, "violet", 70)):
        g.g(key).box((0.34, 0.34, 0.34), (x, y, z), (rx, rx * 1.3, rx * 0.6), center=True)
    for x, y, a in ring_points(4, 5.3, 20):
        lamp_post(g, x, y, "magenta", 2.8)
    return g.build()
