"""01 Launchpad (About): a rocket on a pad with gantries, tanks and a control building."""
import math

from blender_lib import Group, P, ring_points, rot, tr
from zone_common import (barrel, crate, hazard_ring, lamp_post, pad_disc, pipe, railing,
                         smoke_puff, truss_tower, window)


def build():
    g = Group("Zone_about", seed=101)

    # ---- pad: concrete slab, raised ring, hazard stripes, runway lights
    pad_disc(g, 6.4, 0.4, P["plaza_dark"])
    pad_disc(g, 5.7, 0.55, P["plaza"])
    pad_disc(g, 5.55, 0.58, P["stone_dark"])
    hazard_ring(g, 6.0, 32, z=0.0, w=0.62, d=0.42, h=0.46)
    for x, y, a in ring_points(24, 5.0, 7.5):
        g.g("amber").cyl(0.09, 0.09, 0.08, (x, y, 0.58), segs=10)
    g.metal.cyl(2.25, 2.25, 0.62, (0, 0, 0.0), segs=40, color=P["iron"])
    for r in (1.2, 1.7, 2.1):
        g.metal.torus(r, 0.04, (0, 0, 0.64), major=40, minor=6, color=P["gunmetal"])

    # ---- launch table the rocket stands on
    g.metal.lathe([(2.05, 0.55), (2.05, 0.95), (1.7, 1.1), (1.45, 1.1)], segs=40,
                  color=P["gunmetal"], caps=True)
    for x, y, a in ring_points(4, 1.65, 45):
        g.paint.box((0.5, 0.3, 0.8), (x, y, 0.95), (0, 0, a), color=P["orange"])

    # ---- the rocket
    z0 = 1.1
    for x, y, a in ring_points(3, 0.55, 90):
        g.metal.lathe([(0.3, z0 + 0.95), (0.38, z0 + 0.7), (0.55, z0 + 0.15), (0.64, z0 - 0.05)],
                      (x, y, 0), segs=24, color=P["iron"], caps=False)
        g.g("orange").cyl(0.46, 0.46, 0.04, (x, y, z0 + 0.1), segs=20)
    body = [(1.0, z0 + 0.9), (1.2, z0 + 1.3), (1.26, z0 + 1.8), (1.26, z0 + 7.0)]
    g.paint.lathe(body, segs=40, color=P["white"], caps=False)
    g.paint.lathe([(1.26, z0 + 7.0), (1.2, z0 + 7.7), (1.0, z0 + 8.5), (0.7, z0 + 9.3),
                   (0.34, z0 + 9.9), (0.0, z0 + 10.2)], segs=40, color=P["orange"],
                  caps=False)
    for z in (z0 + 2.4, z0 + 4.3, z0 + 6.4):
        g.metal.torus(1.27, 0.045, (0, 0, z), major=48, minor=8, color=P["metal"])
    g.paint.cyl(1.285, 1.285, 0.55, (0, 0, z0 + 2.7), segs=40, color=P["orange"])
    g.paint.cyl(1.285, 1.285, 0.28, (0, 0, z0 + 5.2), segs=40, color=P["navy"])
    g.g("cyan").torus(1.295, 0.025, (0, 0, z0 + 4.8), major=48, minor=6)
    # one big porthole facing the front, with a strip of small cockpit windows beside it
    ax, ay = 0.0, -1.27
    g.metal.torus(0.42, 0.07, (ax, ay, z0 + 6.0), (90, 0, 0), major=32, minor=8,
                  color=P["gunmetal"])
    g.g("cyan").cyl(0.38, 0.38, 0.05, (ax, ay - 0.005, z0 + 6.0), (90, 0, 0), segs=32,
                    center=True)
    for a in range(-125, -54, 14):
        if abs(a + 90) < 12:
            continue
        wx, wy = math.cos(math.radians(a)) * 1.275, math.sin(math.radians(a)) * 1.275
        g.g("amber").box((0.2, 0.05, 0.14), (wx, wy, z0 + 5.45), (0, 0, a + 90), center=True)
    for x, y, a in ring_points(4, 0.0, 45):
        g.paint.prism([(1.2, 0), (2.7, -0.35), (2.55, 0.45), (1.2, 3.1)], 0.16,
                      (0, 0, z0 + 0.7), (90, 0, a), color=P["orange"])
    for side in (-1, 1):
        bx = side * 2.0
        g.paint.cyl(0.52, 0.52, 5.6, (bx, 0, z0 + 0.8), segs=28, color=P["white"])
        g.paint.lathe([(0.52, z0 + 6.4), (0.44, z0 + 6.9), (0.26, z0 + 7.4), (0.0, z0 + 7.7)],
                      (bx, 0, 0), segs=28, color=P["orange"], caps=False)
        g.metal.lathe([(0.3, z0 + 0.95), (0.4, z0 + 0.7), (0.5, z0 + 0.2)], (bx, 0, 0),
                      segs=20, color=P["iron"], caps=False)
        g.g("orange").cyl(0.38, 0.38, 0.04, (bx, 0, z0 + 0.25), segs=20)
        for z in (z0 + 1.6, z0 + 4.6):
            g.metal.box((0.5, 0.55, 0.32), (side * 1.4, 0, z), color=P["gunmetal"])

    # ---- gantry tower + service arm, second shorter tower
    # main gantry stands back-right; its service arm reaches the rocket along the diagonal,
    # between the two boosters
    c45 = math.cos(math.radians(45))
    tx, ty = 3.5, 3.5
    truss_tower(g, tx, ty, 12.2, 1.7, 5, platforms=(3.4, 6.6, 9.8), yaw=45)
    arm_z = z0 + 6.3
    g.metal.box((2.5, 0.62, 0.22), (c45 * 2.55, c45 * 2.55, arm_z), (0, 0, 45), color=P["iron"])
    for off in (-0.31, 0.31):
        ox, oy = -c45 * off, c45 * off
        railing(g, (c45 * 1.4 + ox, c45 * 1.4 + oy, arm_z + 0.22),
                (c45 * 3.7 + ox, c45 * 3.7 + oy, arm_z + 0.22), 0.5, 5)
    g.paint.box((0.25, 0.9, 0.8), (c45 * 1.3, c45 * 1.3, arm_z - 0.3), (0, 0, 45),
                color=P["orange"])
    pipe(g, [(c45 * 3.3, c45 * 3.3, arm_z - 0.5), (c45 * 2.2, c45 * 2.2, arm_z - 0.6),
             (c45 * 1.35, c45 * 1.35, arm_z - 0.7)], 0.07)
    truss_tower(g, -4.9, 1.6, 7.6, 1.3, 3, platforms=(3.6,), yaw=20)

    # ---- fuel spheres on legs, piped to the pad
    for (sx, sy, r) in ((-4.0, -3.4, 1.15), (-2.1, -4.7, 0.95)):
        zc = 2.3 + r * 0.2
        g.metal.ball(r, (sx, sy, zc), 4, color=P["metal"])
        g.metal.torus(r * 1.0, 0.06, (sx, sy, zc), major=48, minor=8, color=P["gunmetal"])
        for x, y, a in ring_points(4, r * 0.8, 45):
            g.metal.tube((sx + x, sy + y, zc - r * 0.6), (sx + x * 1.15, sy + y * 1.15, 0.0),
                         0.07, segs=8, color=P["gunmetal"])
        g.paint.cyl(0.14, 0.14, 0.5, (sx, sy, zc + r - 0.1), segs=12, color=P["orange"])
    pipe(g, [(-3.4, -2.6, 2.0), (-3.0, -1.6, 0.8), (-2.2, -0.8, 0.8), (-1.9, -0.3, 0.8)], 0.11)
    pipe(g, [(-2.1, -3.8, 1.8), (-1.2, -3.0, 0.7), (-1.0, -1.2, 0.7)], 0.09)

    # ---- control building with warm windows
    bx, by, yaw = 2.0, -4.9, 14
    g.lit.box((3.6, 2.4, 2.1), (bx, by, 0.0), (0, 0, yaw), color=P["cream"])
    g.lit.box((3.9, 2.7, 0.22), (bx, by, 2.1), (0, 0, yaw), color=P["roof"])
    g.lit.box((1.4, 1.1, 0.7), (bx - 0.6, by + 0.2, 2.32), (0, 0, yaw), color=P["cream"])
    for dx in (-1.2, 0.0, 1.2):
        window(g, (bx + dx, by - 1.25, 1.2), (0.62, 0.7), yaw, base=None)
    g.lit.box((0.9, 0.12, 1.5), (bx + 1.6, by - 1.22, 0.0), (0, 0, yaw), color=P["navy"])
    g.metal.tube((bx + 1.2, by + 0.3, 2.3), (bx + 1.2, by + 0.3, 4.3), 0.05, segs=8)
    g.metal.tube((bx + 0.7, by + 0.3, 3.7), (bx + 1.7, by + 0.3, 3.7), 0.04, segs=6)
    g.g("red").ball(0.1, (bx + 1.2, by + 0.3, 4.4), 3)
    for dx in (-1.55, 1.55):
        g.lit.cyl(0.22, 0.3, 0.9, (bx + dx, by + 1.25, 0.0), segs=16, color=P["cream"])

    # ---- floodlights, props and steam
    for x, y, a in ring_points(4, 5.3, 45):
        lamp_post(g, x, y, "white", 3.0)
    crate(g, 4.9, -3.2, 25, (1.0, 1.0, 1.0), P["stone_dark"], P["orange"])
    crate(g, 4.1, -4.3, -12, (0.75, 0.75, 0.75), P["stone"], P["orange"])
    barrel(g, 3.3, -5.7)
    barrel(g, 3.9, -5.4, P["cream"])
    for x, y, z, r in ((0.9, -2.0, 0.85, 0.7), (-1.0, -2.2, 0.8, 0.6), (0.2, -2.9, 0.75, 0.8),
                       (-0.5, 2.0, 0.8, 0.55), (1.3, 1.6, 0.8, 0.6)):
        smoke_puff(g, x, y, z, r)
    return g.build()
