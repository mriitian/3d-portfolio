"""Reusable detail pieces shared by the zone builders."""
import math

from mathutils import Vector

from blender_lib import P, ring_points, rot, tr


def lamp_post(g, x, y, key="amber", h=2.8, base=None):
    """Street lamp: tapered pole, curved arm, hooded head, glowing bulb."""
    b = tr(x, y, 0) if base is None else base @ tr(x, y, 0)
    g.metal.cyl(0.13, 0.13, 0.25, segs=14, color=P["gunmetal"], base=b)
    g.metal.cyl(0.09, 0.06, h, (0, 0, 0.2), segs=12, color=P["gunmetal"], base=b)
    g.metal.tube((0, 0, h + 0.1), (0.35, 0, h + 0.28), 0.045, segs=8, color=P["gunmetal"],
                 base=b)
    g.metal.cyl(0.24, 0.14, 0.16, (0.38, 0, h + 0.16), segs=14, color=P["iron"], base=b)
    g.g(key).ball(0.14, (0.38, 0, h + 0.1), 2, base=b)


def crate(g, x, y, yaw=0.0, size=(0.9, 0.9, 0.9), color=None, band=None):
    g.lit.box(size, (x, y, 0), (0, 0, yaw), color=color or P["stone_dark"])
    if band:
        g.paint.box((size[0] + 0.03, size[1] + 0.03, size[2] * 0.22), (x, y, size[2] * 0.39),
                    (0, 0, yaw), color=band)


def barrel(g, x, y, color=None, h=0.95):
    g.paint.cyl(0.34, 0.34, h, (x, y, 0), segs=18, color=color or P["orange_deep"])
    for z in (0.18, h - 0.2):
        g.metal.cyl(0.355, 0.355, 0.06, (x, y, z), segs=18, color=P["gunmetal"])


def window(g, pos, size, yaw=0.0, key="amber", frame=None, base=None, depth=0.14):
    """A framed glowing window pane, facing local -Y after `yaw`."""
    b = tr(*pos) @ rot(0, 0, yaw)
    if base is not None:
        b = base @ b
    w, h = size
    g.metal.box((w + 0.16, depth, h + 0.16), (0, 0, 0), color=frame or P["iron"], base=b)
    g.g(key).box((w, 0.05, h), (0, -depth / 2 - 0.005, 0.0), base=b)
    # window cross bars
    g.metal.box((0.05, 0.03, h), (0, -depth / 2 - 0.03, 0.0), color=frame or P["iron"], base=b)
    g.metal.box((w, 0.03, 0.05), (0, -depth / 2 - 0.03, h / 2 - 0.02), color=frame or P["iron"],
                base=b)


def railing(g, a, b, height=0.6, posts=4, r=0.035, color=None):
    a, b = Vector(a), Vector(b)
    color = color or P["gunmetal"]
    for i in range(posts + 1):
        p = a.lerp(b, i / posts)
        g.metal.tube((p.x, p.y, p.z), (p.x, p.y, p.z + height), r, segs=6, color=color)
    g.metal.tube((a.x, a.y, a.z + height), (b.x, b.y, b.z + height), r * 1.1, segs=6,
                 color=color)
    g.metal.tube((a.x, a.y, a.z + height * 0.5), (b.x, b.y, b.z + height * 0.5), r * 0.8,
                 segs=6, color=color)


def pipe(g, pts, r=0.1, color=None, joints=True):
    color = color or P["gunmetal"]
    for a, b in zip(pts, pts[1:]):
        g.metal.tube(a, b, r, segs=10, color=color)
    if joints:
        for p in pts[1:-1]:
            g.metal.ball(r * 1.25, p, 2, color=color)


def truss_tower(g, x, y, height, width=1.6, bays=4, color=None, brace=None, yaw=0.0,
                platforms=(), lamp_key="amber"):
    """A lattice gantry: four columns, ring beams, X braces, optional railed platforms."""
    color = color or P["gunmetal"]
    brace = brace or P["orange_deep"]
    h2 = width / 2
    base = tr(x, y, 0) @ rot(0, 0, yaw)
    corners = [(-h2, -h2), (h2, -h2), (h2, h2), (-h2, h2)]
    for cx, cy in corners:
        g.metal.box((0.2, 0.2, height), (cx, cy, 0), color=color, base=base)
    step = height / bays
    levels = [step * i for i in range(bays + 1)]
    for z in levels:
        for i in range(4):
            a, b = corners[i], corners[(i + 1) % 4]
            g.metal.tube((a[0], a[1], z), (b[0], b[1], z), 0.065, segs=8, color=brace, base=base)
    for z0, z1 in zip(levels, levels[1:]):
        for i in range(4):
            a, b = corners[i], corners[(i + 1) % 4]
            g.metal.tube((a[0], a[1], z0), (b[0], b[1], z1), 0.04, segs=6, color=color,
                         base=base)
            g.metal.tube((b[0], b[1], z0), (a[0], a[1], z1), 0.04, segs=6, color=color,
                         base=base)
    for z in platforms:
        g.metal.box((width + 0.7, width + 0.7, 0.12), (0, 0, z), color=P["iron"], base=base)
        for i in range(4):
            a, b = corners[i], corners[(i + 1) % 4]
            ea = (a[0] * 1.22, a[1] * 1.22, z + 0.12)
            eb = (b[0] * 1.22, b[1] * 1.22, z + 0.12)
            railing(g, ea, eb, 0.55, posts=3)
        g.g(lamp_key).ball(0.1, (h2 + 0.25, h2 + 0.25, z + 0.3), 2, base=base)
        g.g(lamp_key).ball(0.1, (-h2 - 0.25, -h2 - 0.25, z + 0.3), 2, base=base)
    g.paint.box((width + 0.3, width + 0.3, 0.2), (0, 0, height), color=P["orange"], base=base)
    g.g("red").ball(0.14, (0, 0, height + 0.34), 3, base=base)
    return base


def smoke_puff(g, x, y, z, r, color=None):
    g.lit.ball(r, (x, y, z), 3, scale=(1.1, 1.0, 0.8), color=color or P["cream"], lump=0.22,
               grad=False, jitter=0.02)


def dish(g, base, scale=1.0, with_feed=True, key="cyan", color=None):
    prof_outer = [(0.0, 0.0), (0.4, 0.04), (0.9, 0.18), (1.5, 0.48), (2.05, 0.92), (2.5, 1.45)]
    prof_inner = [(2.42, 1.47), (1.97, 0.97), (1.42, 0.56), (0.86, 0.28), (0.36, 0.13),
                  (0.0, 0.11)]
    prof = [(r * scale, z * scale) for r, z in prof_outer + prof_inner]
    g.paint.lathe(prof, segs=36, color=color or P["white"], caps=False, base=base)
    g.metal.torus(2.46 * scale, 0.05 * scale, (0, 0, 1.46 * scale), major=48, minor=8,
                  color=P["gunmetal"], base=base)
    if with_feed:
        focus = (0, 0, 1.25 * scale)
        for a in (0, 120, 240):
            rx = math.cos(math.radians(a)) * 2.45 * scale
            ry = math.sin(math.radians(a)) * 2.45 * scale
            g.metal.tube((rx, ry, 1.45 * scale), focus, 0.04 * scale, segs=6,
                         color=P["gunmetal"], base=base)
        g.metal.cyl(0.1 * scale, 0.1 * scale, 0.3 * scale, (0, 0, 1.1 * scale), segs=10,
                    color=P["gunmetal"], base=base)
        g.g(key).ball(0.14 * scale, focus, 3, base=base)


def pad_disc(g, r, h, color, z=0.0, segs=64):
    g.lit.cyl(r, r, h, (0, 0, z), segs=segs, color=color)


def hazard_ring(g, radius, count, z=0.0, w=0.8, d=0.4, h=0.1):
    for i, (x, y, a) in enumerate(ring_points(count, radius)):
        g.paint.box((w, d, h), (x, y, z), (0, 0, a + 90),
                    color=P["orange"] if i % 2 == 0 else P["cream"])
