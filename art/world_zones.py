"""The five landmark zones. Each is modelled at the origin, +Z up, footprint ~ 6 units."""
import math

from mathutils import Matrix, Vector

from blender_lib import Group, P, ring_points, rot, tr

# ----------------------------------------------------------------- shared ---


def lamp_post(g, x, y, key="orange", h=2.4):
    g.lit.cyl(0.07, 0.09, h, (x, y, 0), segs=5, color=P["metal_dark"])
    g.lit.box((0.34, 0.34, 0.08), (x, y, h), color=P["metal_dark"])
    g.g(key).ball(0.22, (x, y, h + 0.24), 1)


def crate(g, x, y, yaw=0, size=(0.9, 0.9, 0.9), color=None, stripe=None):
    g.lit.box(size, (x, y, 0), (0, 0, yaw), color=color or P["metal"])
    if stripe:
        g.lit.box((size[0] + 0.04, size[1] * 0.28, size[2] + 0.04), (x, y, 0), (0, 0, yaw),
                  color=stripe)


def floodlight(g, x, y, z=2.6, aim=0.0):
    g.lit.cyl(0.07, 0.09, z, (x, y, 0), segs=5, color=P["metal_dark"])
    base = tr(x, y, z) @ rot(0, 0, aim) @ rot(-25, 0, 0)
    g.lit.box((0.6, 0.3, 0.34), (0, 0, 0), color=P["metal_dark"], base=base, center=True)
    g.g("white").box((0.5, 0.05, 0.26), (0, -0.18, 0), base=base, center=True)


def ngon_pad(g, r, h, segs, color, z=0.0):
    g.lit.cyl(r, r, h, (0, 0, z), segs=segs, color=color)


def dish_profile(scale=1.0):
    outer = [(0.0, 0.0), (0.4, 0.04), (0.9, 0.18), (1.5, 0.48), (2.05, 0.92), (2.5, 1.45)]
    inner = [(2.4, 1.47), (1.95, 0.96), (1.4, 0.55), (0.85, 0.27), (0.35, 0.12), (0.0, 0.1)]
    return [(r * scale, z * scale) for r, z in outer + inner]


# ------------------------------------------------------------- 01 launchpad ---


def build_launchpad():
    g = Group("Zone_about", seed=101)
    L = g.lit

    # concrete pad, raised inner disc, hazard stripes and runway lights
    L.cyl(5.9, 5.9, 0.28, segs=18, color=P["slate"])
    L.cyl(5.1, 5.1, 0.38, segs=18, color=P["slate_light"])
    for i, (x, y, a) in enumerate(ring_points(18, 5.5)):
        L.box((0.72, 0.36, 0.42), (x, y, 0), (0, 0, a + 90),
              color=P["orange"] if i % 2 == 0 else P["white"], jitter=0.02)
    for x, y, a in ring_points(9, 4.1, 20):
        g.g("cyan").box((0.3, 0.3, 0.06), (x, y, 0.38), (0, 0, a))
    L.cyl(1.8, 1.8, 0.44, segs=14, color=P["navy"])  # flame pit

    # rocket
    zb = 0.45
    for x, y, a in ring_points(4, 0.62, 45):
        L.cyl(0.42, 0.22, 0.75, (x, y, zb), segs=6, color=P["metal_dark"])
        g.g("orange").cyl(0.26, 0.26, 0.05, (x, y, zb), segs=6)
    L.lathe([(0.0, 1.0), (1.0, 1.0), (1.05, 1.5), (1.05, 5.7), (1.0, 5.7), (0.0, 5.7)],
            segs=14, color=P["white"], caps=False)
    L.lathe([(1.05, 1.5), (1.08, 1.55), (1.08, 5.65), (1.05, 5.7)], segs=14,
            color=P["white"], caps=False, jitter=0.0)
    L.lathe([(0.85, 0.95), (1.08, 1.0), (1.08, 1.7), (1.05, 1.7)], segs=14,
            color=P["metal_dark"], caps=False)
    L.cyl(1.1, 1.1, 0.34, (0, 0, 2.6), segs=14, color=P["orange"], jitter=0.02)
    L.cyl(1.1, 1.1, 0.34, (0, 0, 4.9), segs=14, color=P["cyan"], jitter=0.02)
    L.lathe([(1.05, 5.7), (0.95, 6.4), (0.7, 7.2), (0.38, 7.9), (0.0, 8.4)], segs=14,
            color=P["orange"], caps=False)
    for a, z in ((-90, 4.1), (35, 3.6)):
        ax, ay = math.cos(math.radians(a)) * 1.06, math.sin(math.radians(a)) * 1.06
        L.cyl(0.42, 0.42, 0.06, (ax, ay, z), (90, 0, a + 90), segs=10, color=P["metal_dark"],
              center=True)
        g.g("cyan").cyl(0.3, 0.3, 0.06, (ax * 1.01, ay * 1.01, z), (90, 0, a + 90), segs=10,
                        center=True)
    for _, _, a in ring_points(3, 0.0, 90):
        L.prism([(1.0, 0), (2.5, -0.15), (1.0, 2.9)], 0.16, (0, 0, 1.0), (90, 0, a),
                color=P["orange"], jitter=0.02)

    # launch tower with braces and an umbilical arm
    tx, ty = 3.7, 0.0
    corners = [(-0.6, -0.6), (0.6, -0.6), (0.6, 0.6), (-0.6, 0.6)]
    for cx, cy in corners:
        L.box((0.22, 0.22, 9.2), (tx + cx, ty + cy, 0.3), color=P["metal_dark"])
    levels = [0.9, 2.5, 4.1, 5.7, 7.3, 9.0]
    for z in levels:
        for i in range(4):
            a, b = corners[i], corners[(i + 1) % 4]
            L.tube((tx + a[0], ty + a[1], z), (tx + b[0], ty + b[1], z), 0.08,
                   color=P["orange_deep"])
    for z0, z1 in zip(levels, levels[1:]):
        for i in range(4):
            a, b = corners[i], corners[(i + 1) % 4]
            L.tube((tx + a[0], ty + a[1], z0), (tx + b[0], ty + b[1], z1), 0.05,
                   color=P["metal_dark"])
    L.box((1.7, 1.7, 0.2), (tx, ty, 9.4), color=P["orange"])
    g.g("red").ball(0.22, (tx, ty, 9.8), 1)
    L.box((2.2, 0.34, 0.34), (tx - 1.7, ty, 5.4), color=P["metal"])
    L.box((0.34, 0.5, 0.5), (tx - 2.85, ty, 5.4), color=P["orange"])
    for z in (3.0, 7.0):
        g.g("yellow").box((0.18, 0.18, 0.18), (tx - 0.75, ty - 0.75, z), center=True)

    # fuel tanks + pipes
    for ty2 in (2.3, 0.3):
        L.cyl(0.85, 0.85, 2.3, (-3.7, ty2 + 0.4, 0.3), segs=10, color=P["white"])
        L.ball(0.85, (-3.7, ty2 + 0.4, 2.6), 1, scale=(1, 1, 0.55), color=P["white"])
        L.cyl(0.88, 0.88, 0.3, (-3.7, ty2 + 0.4, 1.2), segs=10, color=P["orange"])
    L.tube((-3.0, 1.4, 0.8), (-1.7, 0.7, 0.45), 0.1, color=P["metal_dark"])
    L.tube((-1.7, 0.7, 0.45), (-1.2, 0.2, 0.45), 0.1, color=P["metal_dark"])

    # control bunker
    L.box((3.0, 1.9, 1.6), (-1.3, -4.1, 0.28), (0, 0, 12), color=P["stone"])
    L.box((3.3, 2.2, 0.22), (-1.3, -4.1, 1.88), (0, 0, 12), color=P["metal_dark"])
    for dx in (-0.8, 0.5):
        g.g("cyan").box((0.7, 0.06, 0.4), (-1.3 + dx, -3.1, 0.9), (0, 0, 12))
    L.box((0.8, 0.1, 1.2), (-2.1, -3.2, 0.28), (0, 0, 12), color=P["navy"])
    L.tube((-0.6, -4.3, 2.1), (-0.6, -4.3, 3.6), 0.05, color=P["metal_dark"])
    g.g("red").ball(0.14, (-0.6, -4.3, 3.7), 1)

    for a in (45, 135, 225, 315):
        x, y = math.cos(math.radians(a)) * 5.0, math.sin(math.radians(a)) * 5.0
        floodlight(g, x, y, 2.6, a - 180)
    crate(g, 4.4, -3.3, 20, (0.9, 0.9, 0.9), P["orange"], P["white"])
    crate(g, 3.5, -4.0, -10, (0.7, 0.7, 0.7), P["cyan"])
    for dx, dy, r in [(0.9, -1.2, 0.6), (-1.0, -1.3, 0.5), (0.2, -1.8, 0.7), (-0.4, 1.7, 0.45),
                      (1.2, 1.2, 0.5)]:
        L.ball(r, (dx, dy, r * 0.45), 1, scale=(1, 1, 0.7), color=P["white"], jitter=0.03,
               noise=0.12)
    return g.build()


# -------------------------------------------------------- 02 creative district ---


def portal(g, x, y, yaw, radius, key):
    L = g.lit
    zc = radius + 0.55
    base = tr(x, y, 0) @ rot(0, 0, yaw)
    L.box((0.9, 0.9, 0.55), (-radius, 0, 0), color=P["slate_light"], base=base)
    L.box((0.9, 0.9, 0.55), (radius, 0, 0), color=P["slate_light"], base=base)
    L.cyl(radius + 0.55, radius + 0.7, 0.12, (0, 0, 0), segs=14, color=P["slate"], base=base)
    ringbase = base @ tr(0, 0, zc) @ rot(90, 0, 0)
    g.g(key).torus(radius, 0.17, major=24, minor=5, base=ringbase)
    L.torus(radius + 0.28, 0.09, major=24, minor=4, color=P["metal"], base=ringbase)
    # the glowing "surface" of the portal, seen from both sides
    g.g(key).cyl(radius - 0.2, radius - 0.2, 0.06, (0, 0, 0), segs=20, center=True,
                 base=ringbase)
    for side in (-1, 1):
        g.g("white").cyl(radius * 0.4, radius * 0.4, 0.04, (0, 0, side * 0.05), segs=16,
                         center=True, base=ringbase)
        g.g("white").torus(radius * 0.66, 0.035, (0, 0, side * 0.045), major=24, minor=4,
                           base=ringbase)


def arcade_cabinet(g, x, y, yaw, accent_key, body):
    L = g.lit
    base = tr(x, y, 0) @ rot(0, 0, yaw)
    L.box((1.15, 0.95, 1.75), (0, 0, 0.3), color=body, base=base)
    L.box((1.2, 1.0, 0.25), (0, 0, 2.05), color=P["navy"], base=base)
    g.g(accent_key).box((1.0, 0.06, 0.18), (0, -0.52, 2.07), base=base)
    L.box((0.95, 0.6, 0.18), (0, -0.5, 1.28), (-18, 0, 0), color=P["slate_light"], base=base)
    g.g("cyan").box((0.8, 0.05, 0.62), (0, -0.49, 1.4), (-12, 0, 0), base=base)
    L.cyl(0.04, 0.04, 0.24, (-0.2, -0.62, 1.38), (-18, 0, 0), segs=5, color=P["metal"],
          base=base)
    g.g("red").ball(0.07, (-0.2, -0.63, 1.64), 0, base=base)
    for i, key in enumerate(("yellow", "orange", "magenta")):
        g.g(key).ball(0.05, (0.0 + i * 0.16, -0.66, 1.36), 0, base=base)


def build_creative_district():
    g = Group("Zone_projects", seed=202)
    L = g.lit
    L.cyl(5.9, 6.0, 0.3, segs=6, color=P["slate"])
    L.cyl(5.2, 5.2, 0.38, segs=6, color=P["slate_light"])
    g.g("magenta").torus(4.7, 0.06, (0, 0, 0.42), major=36, minor=4)
    g.g("cyan").torus(3.7, 0.045, (0, 0, 0.4), major=30, minor=4)

    portal(g, 0.0, -2.8, 0, 2.5, "magenta")
    portal(g, -3.6, 0.9, 32, 2.0, "cyan")
    portal(g, 3.6, 0.9, -32, 2.0, "orange")

    # gamepad centrepiece on a glowing pedestal
    L.cyl(1.05, 1.2, 0.8, (0, 1.8, 0.3), segs=8, color=P["slate"])
    g.g("cyan").torus(1.1, 0.05, (0, 1.8, 1.1), major=18, minor=4)
    pad = tr(0, 1.8, 2.55) @ rot(-22, 0, 0)
    L.box((2.0, 1.05, 0.5), (0, 0, 0), color=P["violet"], base=pad, center=True)
    L.ball(0.62, (-1.05, -0.1, 0), 1, scale=(1.0, 1.25, 0.8), color=P["violet"], base=pad)
    L.ball(0.62, (1.05, -0.1, 0), 1, scale=(1.0, 1.25, 0.8), color=P["violet"], base=pad)
    L.box((0.5, 0.15, 0.06), (-0.75, 0.12, 0.28), color=P["white"], base=pad, center=True)
    L.box((0.15, 0.5, 0.06), (-0.75, 0.12, 0.28), color=P["white"], base=pad, center=True)
    for dx, dy, key in ((0.58, 0.12, "yellow"), (0.9, 0.12, "orange"), (0.74, 0.3, "cyan"),
                        (0.74, -0.06, "magenta")):
        g.g(key).ball(0.1, (dx + 0.15, dy, 0.3), 1, base=pad)
    L.cyl(0.14, 0.14, 0.12, (-0.25, -0.2, 0.25), segs=8, color=P["navy"], base=pad)
    L.cyl(0.14, 0.14, 0.12, (0.25, -0.2, 0.25), segs=8, color=P["navy"], base=pad)

    # arcade cabinets
    arcade_cabinet(g, -2.0, 3.6, 0, "cyan", P["violet"])
    arcade_cabinet(g, 0.0, 4.0, 0, "magenta", P["orange_deep"])
    arcade_cabinet(g, 2.0, 3.6, 0, "orange", P["violet"])

    # neon pylons
    for x, y, key in ((-5.0, -2.6, "cyan"), (5.0, -2.6, "magenta")):
        L.box((0.55, 0.55, 4.6), (x, y, 0.3), color=P["navy"])
        for z in (1.2, 2.3, 3.4):
            g.g(key).box((0.62, 0.62, 0.14), (x, y, z))
        L.box((1.5, 0.2, 0.75), (x, y, 5.0), (0, 0, 0), color=P["navy"])
        g.g(key).box((1.3, 0.22, 0.5), (x, y, 5.07))

    # floating gems
    cols = ["cyan", "magenta", "orange", "yellow", "violet", "cyan"]
    for i, (x, y, a) in enumerate(ring_points(6, 3.4, 15)):
        g.g(cols[i]).ball(0.28, (x, y, 3.3 + (i % 3) * 0.9), 0, scale=(0.8, 0.8, 1.3),
                          rotation=(10 * i, 20 * i, 30 * i))
    for x, y in ((-4.7, 3.2), (4.7, 3.2)):
        lamp_post(g, x, y, "magenta", 2.2)
    return g.build()


# -------------------------------------------------------------- 03 observatory ---


def build_observatory():
    g = Group("Zone_skills", seed=303)
    L = g.lit
    L.cyl(5.6, 5.7, 0.32, segs=14, color=P["slate"])
    L.cyl(4.8, 4.8, 0.5, segs=14, color=P["slate_light"])
    L.cyl(3.4, 3.5, 0.62, segs=14, color=P["stone"], jitter=0.03)

    # tower body + trim
    L.cyl(2.7, 2.6, 2.6, (0, 0, 0.62), segs=12, color=P["stone"], jitter=0.03)
    L.cyl(2.85, 2.85, 0.22, (0, 0, 3.22), segs=12, color=P["violet"], jitter=0.02)
    L.cyl(2.78, 2.78, 0.18, (0, 0, 0.62), segs=12, color=P["violet"], jitter=0.02)
    for x, y, a in ring_points(8, 2.66, 22.5):
        g.g("cyan").box((0.46, 0.1, 0.85), (x, y, 1.55), (0, 0, a + 90))
    L.box((1.0, 0.18, 1.5), (0, -2.66, 0.62), color=P["navy"])
    g.g("cyan").box((0.5, 0.06, 0.12), (0, -2.76, 2.0))

    # dome with a glowing shutter slit
    zd = 3.42
    prof = [(2.7 * math.cos(math.radians(t)), zd + 2.7 * math.sin(math.radians(t)))
            for t in (0, 15, 30, 45, 60, 75, 88)] + [(0.0, zd + 2.74)]
    L.lathe(prof, segs=12, color=P["white"], caps=False, jitter=0.02)
    g.g("cyan").torus(2.76, 0.1, (0, 0, zd), (90, 0, 90), major=20, minor=4, arc=150, start=15)
    L.torus(2.78, 0.16, (0, 0, zd), (90, 0, 90), major=20, minor=4, arc=150, start=15,
            color=P["navy"])
    d = Vector((0, -math.sin(math.radians(50)), math.cos(math.radians(50))))
    start = Vector((0, 0.5, 4.7))
    end = start + d * 3.4
    L.tube(start, end, 0.36, segs=8, color=P["metal"])
    L.tube(start + d * 2.2, end, 0.46, segs=8, color=P["metal_dark"])
    g.g("cyan").cyl(0.34, 0.34, 0.08, tuple(end + d * 0.02), (50, 0, 0), segs=8, center=True)

    # armillary sphere
    ax, ay = 3.9, -2.7
    L.cyl(0.55, 0.7, 1.1, (ax, ay, 0.6), segs=8, color=P["stone"])
    g.g("cyan").ball(0.3, (ax, ay, 2.3), 1)
    for rx, ry in ((0, 0), (90, 0), (60, 60)):
        L.torus(1.0, 0.05, (ax, ay, 2.3), (rx, ry, 0), major=22, minor=4, color=P["yellow"],
                jitter=0.0)

    # constellation
    stars = [(-4.2, 2.6, 4.0, "white"), (-2.6, 3.8, 5.6, "cyan"), (0.2, 4.4, 4.6, "yellow"),
             (2.9, 3.6, 6.1, "white"), (4.5, 1.8, 4.5, "cyan"), (4.9, -0.6, 6.6, "yellow"),
             (-4.8, -1.0, 6.2, "cyan")]
    for i, (x, y, z, key) in enumerate(stars):
        g.g(key).ball(0.3, (x, y, z), 0, scale=(1, 1, 1.15), rotation=(0, 0, 40 * i))
        if i:
            px, py, pz, _ = stars[i - 1]
            g.g("white").tube((px, py, pz), (x, y, z), 0.025, segs=3)

    for x, y in ((-3.6, -3.4), (3.4, 3.7), (-4.5, 2.4)):
        L.box((1.1, 0.4, 0.14), (x, y, 0.32), (0, 0, 30), color=P["rock_light"])
    lamp_post(g, 4.6, 0.2, "cyan", 2.1)
    lamp_post(g, -4.6, -1.6, "cyan", 2.1)
    return g.build()


# ----------------------------------------------------------- 04 space station ---


def build_space_station():
    g = Group("Zone_experience", seed=404)
    L = g.lit
    L.cyl(5.7, 5.8, 0.3, segs=8, color=P["slate"])
    L.cyl(5.0, 5.0, 0.4, segs=8, color=P["slate_light"])
    for x, y, a in ring_points(8, 5.38, 22.5):
        g.g("violet").box((1.0, 0.14, 0.05), (x, y, 0.3), (0, 0, a + 90))

    # tower
    L.lathe([(1.6, 0.4), (1.35, 0.7), (1.0, 1.3), (0.9, 5.0)], segs=10, color=P["white"],
            caps=False)
    L.cyl(1.2, 1.2, 1.3, (0, 0, 5.0), segs=10, color=P["white"], jitter=0.02)
    g.g("cyan").cyl(1.24, 1.24, 0.16, (0, 0, 5.55), segs=10)
    L.cyl(1.25, 1.25, 0.18, (0, 0, 4.9), segs=10, color=P["violet"])
    L.cyl(1.25, 1.25, 0.18, (0, 0, 6.2), segs=10, color=P["violet"])
    L.lathe([(0.8, 6.3), (0.5, 6.7), (0.12, 7.4)], segs=10, color=P["metal"], caps=False)
    L.tube((0, 0, 7.4), (0, 0, 8.5), 0.05, color=P["metal_dark"])
    g.g("red").ball(0.17, (0, 0, 8.6), 1)

    # ring, spokes, windows, pods
    zr = 3.9
    L.torus(4.2, 0.5, (0, 0, zr), major=24, minor=6, color=P["white"], jitter=0.03)
    for a in (0, 90, 180, 270):
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        # box length runs along local X, which the yaw turns radially outwards
        L.box((3.0, 0.34, 0.34), (c * 0.9, s * 0.9, zr - 0.17), (0, 0, a), color=P["metal"])
    for i, (x, y, a) in enumerate(ring_points(20, 4.72, 9)):
        g.g("cyan" if i % 2 == 0 else "violet").box((0.46, 0.1, 0.24), (x, y, zr - 0.12),
                                                      (0, 0, a + 90))
    for x, y, a in ring_points(3, 4.2, 30):
        L.cyl(0.62, 0.62, 1.1, (x, y, zr + 0.4), segs=8, color=P["orange"])
        L.ball(0.62, (x, y, zr + 1.5), 1, scale=(1, 1, 0.5), color=P["orange"])
        g.g("cyan").box((0.5, 0.1, 0.24), (x * 0.99, y * 0.99, zr + 0.9), (0, 0, a + 90))

    # solar wings
    zs = 8.0
    L.tube((-5.2, 0, zs), (5.2, 0, zs), 0.06, color=P["metal_dark"])
    for side in (-1, 1):
        for i in range(3):
            x = side * (1.7 + i * 1.5)
            L.box((1.38, 0.08, 2.5), (x, 0, zs - 1.25), color=P["metal"])
            L.box((1.2, 0.1, 2.3), (x, 0, zs - 1.15), color=P["panel"], jitter=0.05)
            L.box((1.2, 0.12, 0.05), (x, 0, zs - 0.58), color=P["panel_light"])
            L.box((1.2, 0.12, 0.05), (x, 0, zs - 1.5), color=P["panel_light"])
    # docked shuttle
    sa = 40
    sbase = tr(*(Vector((math.cos(math.radians(sa)), math.sin(math.radians(sa)), 0)) * 5.0)) \
        @ tr(0, 0, zr - 0.1) @ rot(0, 0, sa) @ rot(0, 90, 0)
    L.lathe([(0.0, 0.0), (0.45, 0.3), (0.55, 0.9), (0.55, 1.9), (0.35, 2.5), (0.0, 2.8)],
            segs=8, color=P["white"], caps=False, base=sbase)
    L.prism([(0.4, 0.3), (1.3, 0.2), (0.4, 1.7)], 0.1, (0, 0, 0), (0, 0, 0),
            color=P["orange"], base=sbase)
    L.prism([(-0.4, 0.3), (-1.3, 0.2), (-0.4, 1.7)], 0.1, (0, 0, 0), (0, 0, 0),
            color=P["orange"], base=sbase)
    g.g("cyan").ball(0.2, (0, -0.5, 2.0), 1, scale=(1.2, 0.5, 0.7), base=sbase)
    g.g("orange").cyl(0.28, 0.28, 0.06, (0, 0, 0.0), segs=8, base=sbase)

    crate(g, -3.5, -3.7, 15, (1.1, 1.1, 1.1), P["slate_light"], P["violet"])
    crate(g, -2.3, -4.1, -8, (0.8, 0.8, 0.8), P["orange"], P["white"])
    crate(g, 3.5, -3.8, 25, (1.0, 1.0, 1.0), P["white"], P["cyan"])
    for a in (100, 200, 330):
        x, y = math.cos(math.radians(a)) * 4.9, math.sin(math.radians(a)) * 4.9
        lamp_post(g, x, y, "violet", 2.0)
    return g.build()


# ------------------------------------------------------------- 05 comm hub ---


def dish(g, base, scale=1.0, with_feed=True, key="cyan"):
    g.lit.lathe(dish_profile(scale), segs=14, color=P["white"], caps=False, base=base)
    if with_feed:
        focus = Vector((0, 0, 1.2 * scale))
        for a in (0, 120, 240):
            rx = math.cos(math.radians(a)) * 2.4 * scale
            ry = math.sin(math.radians(a)) * 2.4 * scale
            g.lit.tube((rx, ry, 1.4 * scale), focus, 0.04 * scale, segs=3, color=P["metal_dark"],
                       base=base)
        g.g(key).ball(0.18 * scale, tuple(focus), 1, base=base)


def build_comm_hub():
    g = Group("Zone_contact", seed=505)
    L = g.lit
    L.cyl(5.5, 5.6, 0.3, segs=8, color=P["slate"])
    L.cyl(4.9, 4.9, 0.38, segs=8, color=P["slate_light"])
    g.g("cyan").torus(4.6, 0.05, (0, 0, 0.4), major=32, minor=4)

    # main building + roof
    L.cyl(2.5, 2.5, 2.2, (0, 0, 0.3), segs=8, color=P["stone"], jitter=0.03)
    L.cyl(2.6, 2.6, 0.2, (0, 0, 2.5), segs=8, color=P["violet"])
    L.cyl(2.2, 2.2, 0.3, (0, 0, 2.7), segs=8, color=P["metal_dark"])
    for x, y, a in ring_points(8, 2.5, 22.5 + 45):
        if abs(a - 270) % 360 < 30:
            continue
        g.g("cyan").box((0.7, 0.08, 0.5), (x, y, 1.2), (0, 0, a + 90))
    L.box((1.0, 0.14, 1.5), (0, -2.52, 0.3), color=P["navy"])
    g.g("cyan").box((0.7, 0.05, 0.1), (0, -2.6, 1.9))

    # big dish on a pedestal
    L.cyl(0.55, 0.7, 0.5, (0, 0, 3.0), segs=8, color=P["metal_dark"])
    L.cyl(0.28, 0.28, 1.1, (0, 0, 3.4), segs=8, color=P["metal"])
    dbase = tr(0, 0, 4.9) @ rot(-48, 0, 28)
    L.box((0.9, 0.4, 0.5), (0, 0, -0.1), color=P["metal_dark"], base=dbase, center=True)
    dish(g, dbase, 1.0)
    # signal arcs
    for i, (rad, z) in enumerate(((0.9, 2.5), (1.5, 3.0), (2.1, 3.5))):
        g.g("cyan").torus(rad, 0.045, (0, 0, z), major=10, minor=4, arc=95, start=-47,
                          base=dbase)
    # roof dishes
    for x, y, yaw in ((-1.6, 0.8, 200), (1.7, 0.6, -30)):
        L.cyl(0.1, 0.1, 0.5, (x, y, 3.0), segs=5, color=P["metal"])
        dish(g, tr(x, y, 3.5) @ rot(-40, 0, yaw), 0.3, with_feed=False)

    # lattice mast
    mx, my = -3.7, 1.5
    legs = [(0.8, 0), (-0.4, 0.69), (-0.4, -0.69)]
    for lx, ly in legs:
        L.tube((mx + lx, my + ly, 0.3), (mx + lx * 0.2, my + ly * 0.2, 7.0), 0.07,
               color=P["metal_dark"])
    for z, s in ((1.5, 0.82), (3.3, 0.6), (5.1, 0.38)):
        for i in range(3):
            a, b = legs[i], legs[(i + 1) % 3]
            L.tube((mx + a[0] * s, my + a[1] * s, z), (mx + b[0] * s, my + b[1] * s, z), 0.05,
                   color=P["orange_deep"])
    g.g("red").ball(0.2, (mx, my, 7.2), 1)
    L.tube((mx, my, 7.0), (mx, my, 8.4), 0.03, color=P["metal"])

    crate(g, 3.6, -3.0, 20, (1.1, 1.1, 1.1), P["orange"], P["white"])
    crate(g, 4.3, -2.0, -15, (0.8, 0.8, 0.8), P["cyan"], P["white"])
    crate(g, 2.7, -3.9, 5, (0.7, 0.7, 0.7), P["white"], P["orange"])
    L.cyl(0.55, 0.55, 0.45, (-3.2, -3.4, 0.3), segs=10, color=P["metal_dark"])
    L.box((1.5, 1.0, 0.1), (3.9, 2.9, 0.34), (-40, 0, 25), color=P["panel"])
    lamp_post(g, 4.4, 0.4, "cyan", 2.0)
    lamp_post(g, -1.2, -4.4, "cyan", 2.0)
    return g.build()


BUILDERS = [
    ("about", build_launchpad),
    ("projects", build_creative_district),
    ("skills", build_observatory),
    ("experience", build_space_station),
    ("contact", build_comm_hub),
]
