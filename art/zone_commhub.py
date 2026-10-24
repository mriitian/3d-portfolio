"""05 Comm Hub (Contact): a sandstone station with a big dish and a glowing mail sign."""
import math

from blender_lib import Group, P, ring_points, rot, tr
from zone_common import barrel, crate, dish, lamp_post, pad_disc, truss_tower, window


def mail_sign(g, base):
    """A glowing envelope inside a metal frame, readable from both sides."""
    _mail_face(g, base)
    _mail_face(g, base @ rot(0, 0, 180))


def _mail_face(g, base):
    g.metal.box((2.4, 0.22, 1.7), (0, 0, 0), color=P["iron"], base=base, center=True)
    g.g("cyan").box((2.15, 0.06, 1.45), (0, -0.13, 0), base=base, center=True)
    g.g("white").box((1.55, 0.05, 1.0), (0, -0.17, -0.05), base=base, center=True)
    # flap lines: the V from the top corners down to the middle
    g.metal.tube((-0.77, -0.21, 0.45), (0.0, -0.21, -0.02), 0.035, segs=6, color=P["gunmetal"],
                 base=base)
    g.metal.tube((0.77, -0.21, 0.45), (0.0, -0.21, -0.02), 0.035, segs=6, color=P["gunmetal"],
                 base=base)
    g.metal.tube((-0.77, -0.21, -0.55), (-0.2, -0.21, -0.14), 0.025, segs=6,
                 color=P["gunmetal"], base=base)
    g.metal.tube((0.77, -0.21, -0.55), (0.2, -0.21, -0.14), 0.025, segs=6,
                 color=P["gunmetal"], base=base)


def build():
    g = Group("Zone_contact", seed=505)
    pad_disc(g, 6.4, 0.4, P["plaza_dark"])
    pad_disc(g, 5.8, 0.52, P["plaza"])
    g.g("cyan").torus(5.3, 0.05, (0, 0, 0.55), major=72, minor=6)

    # ---- main stone hall with arched, glowing windows
    hy = 1.3
    g.lit.box((5.4, 3.4, 3.6), (0, hy, 0.5), color=P["stone"])
    g.lit.box((5.7, 3.7, 0.28), (0, hy, 4.1), color=P["roof"])
    g.lit.box((5.7, 0.4, 0.5), (0, hy - 1.75, 0.5), color=P["stone_dark"])
    for sx in (-1, 1):
        g.lit.box((0.5, 0.5, 3.9), (sx * 2.75, hy - 1.75, 0.5), color=P["stone_dark"])
    for x in (-1.75, 1.75):
        window(g, (x, hy - 1.74, 2.0), (0.9, 1.5), 0)
        g.metal.torus(0.54, 0.06, (x, hy - 1.86, 2.75), (90, 0, 0), major=24, minor=8, arc=180,
                      color=P["gunmetal"])
    g.metal.box((1.4, 0.3, 2.4), (0, hy - 1.75, 0.5), color=P["iron"])
    g.g("amber").box((1.05, 0.05, 2.0), (0, hy - 1.92, 0.58))
    g.metal.torus(0.62, 0.07, (0, hy - 1.93, 2.55), (90, 0, 0), major=28, minor=8, arc=180,
                  color=P["gunmetal"])
    g.lit.box((1.8, 1.6, 0.18), (0, hy - 2.6, 0.5), color=P["stone_dark"])

    # ---- round tower with balcony and dome
    tx, ty = 3.6, 1.0
    g.lit.cyl(1.15, 1.0, 7.0, (tx, ty, 0.5), segs=32, color=P["stone"])
    g.paint.cyl(1.4, 1.4, 0.24, (tx, ty, 5.0), segs=32, color=P["roof"])
    g.metal.torus(1.4, 0.04, (tx, ty, 5.55), major=48, minor=6, color=P["gunmetal"])
    for i in range(10):
        a = math.radians(i * 36)
        g.metal.tube((tx + math.cos(a) * 1.4, ty + math.sin(a) * 1.4, 5.24),
                     (tx + math.cos(a) * 1.4, ty + math.sin(a) * 1.4, 5.6), 0.03, segs=6)
    g.paint.lathe([(1.25, 7.5), (1.0, 8.0), (0.6, 8.5), (0.0, 9.0)], (tx, ty, 0), segs=32,
                  color=P["roof"], caps=False)
    for z, a in ((2.0, -100), (3.4, -80), (4.2, -110)):
        wx, wy = tx + math.cos(math.radians(a)) * 1.12, ty + math.sin(math.radians(a)) * 1.12
        g.g("amber").box((0.3, 0.06, 0.55), (wx, wy, z), (0, 0, a + 90), center=True)
    g.g("red").ball(0.1, (tx, ty, 9.1), 3)

    # ---- the big dish on the hall roof, with signal arcs
    dbase = tr(-0.6, hy + 0.2, 6.2) @ rot(-48, 0, 25)
    g.metal.cyl(0.7, 0.9, 0.5, (-0.6, hy + 0.2, 4.2), segs=24, color=P["gunmetal"])
    g.metal.cyl(0.26, 0.26, 1.5, (-0.6, hy + 0.2, 4.6), segs=14, color=P["metal"])
    g.metal.box((1.0, 0.5, 0.5), (-0.6, hy + 0.2, 5.9), color=P["gunmetal"])
    dish(g, dbase, 1.05, True, "cyan")
    for i, (rad, z) in enumerate(((0.9, 2.7), (1.5, 3.3), (2.1, 3.9))):
        g.g("cyan").torus(rad, 0.045, (0, 0, z), major=24, minor=6, arc=95, start=-47,
                          base=dbase)

    # ---- envelope sign, mast, props
    mail_sign(g, tr(-4.4, -3.4, 3.2) @ rot(0, 0, 25))
    g.metal.tube((-4.4, -3.4, 0.4), (-4.4, -3.4, 2.4), 0.06, segs=10)
    truss_tower(g, -4.6, 2.9, 9.0, 1.0, 4, platforms=(), yaw=15, lamp_key="red")
    for dz in (6.5, 8.2):
        dish(g, tr(-4.6, 2.9, dz) @ rot(-35, 0, 140), 0.18, False)
    crate(g, 4.6, -3.4, 20, (1.1, 1.1, 1.1), P["orange_deep"], P["cream"])
    crate(g, 3.6, -4.1, -15, (0.8, 0.8, 0.8), P["stone_dark"], P["cyan"])
    barrel(g, 2.7, -4.4)
    g.lit.box((1.6, 0.5, 0.2), (1.2, -3.6, 0.5), color=P["stone_dark"])
    for x, y, a in ring_points(4, 5.5, 45):
        lamp_post(g, x, y, "amber", 2.7)
    return g.build()


# solid parts, as (x, y, radius) in this zone's own frame; the game stops the rover at these
COLLIDERS = [(-1.8, 1.3, 1.8), (0, 1.3, 1.8), (1.8, 1.3, 1.8), (3.6, 1.0, 1.3), (-4.6, 2.9, 0.7), (4.6, -3.4, 0.8), (3.6, -4.1, 0.6), (2.7, -4.4, 0.4)]
