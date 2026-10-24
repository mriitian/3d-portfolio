"""The road network: a ring road (roundabout) around every site and the spawn, joined by
the routes between them. Asphalt, raised pavements with curbs and a kerb lip, glowing edge
lines and centre dashes, and radium lamps around each ring. Decoration only (the lamps aside)."""
import math
import random

from mathutils import Vector

from blender_lib import Group, P, mix
from zone_common import lamp_post
import world_planet as wp

HALF = 1.9      # half-width of the asphalt
PAVE = 1.0      # width of each pavement
CURB = 0.17     # pavement height
LIP = 0.14      # extra height of the outer kerb
RING_R = 10.2   # centre-line radius of each roundabout, measured along the surface
JOIN = 12.0     # incoming routes end here, where they meet the ring
GAP_HALF = 0.36  # half-width (radians) of the opening cut in a ring for each incoming route


def sweep(mesh, samples, profile, color_fn):
    """Sweep a cross-section [(offset, height), ...] along the samples, making coloured quads."""
    bm = mesh.bm
    grid = []
    for p, side in samples:
        row = []
        for off, h in profile:
            pos = (p * wp.R + side * off).normalized() * (wp.R + h)
            row.append(bm.verts.new(pos))
        grid.append(row)
    for i in range(len(samples) - 1):
        for j in range(len(profile) - 1):
            f = bm.faces.new((grid[i][j], grid[i][j + 1], grid[i + 1][j + 1], grid[i + 1][j]))
            f.normal_update()
            if f.normal.dot(f.calc_center_median()) < 0:
                f.normal_flip()
            col = color_fn(i, j)
            for loop in f.loops:
                loop[mesh.col] = (col[0], col[1], col[2], 1.0)


def side_profile(sign):
    return [(sign * HALF, 0.05), (sign * HALF, CURB), (sign * (HALF + PAVE), CURB),
            (sign * (HALF + PAVE), CURB + LIP), (sign * (HALF + PAVE + 0.16), CURB + LIP),
            (sign * (HALF + PAVE + 0.16), 0.03)]


def pave_color(i, j):
    if j == 0:
        return P["curb"]
    if j == 1:
        return P["pavement"] if (i // 2) % 2 == 0 else P["pavement_dark"]
    if j == 3:
        return P["curb"]
    return P["pavement_dark"]


def runs_of(flags):
    """Index ranges where flags are True."""
    runs, run = [], []
    for i, ok in enumerate(flags):
        if ok:
            run.append(i)
        elif run:
            runs.append(run)
            run = []
    if run:
        runs.append(run)
    return runs


def tangent_basis(d):
    a = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
    e1 = (a - d * a.dot(d)).normalized()
    return e1, d.cross(e1)


def angle_gap(a, b):
    return abs((a - b + math.pi) % math.tau - math.pi)


def route_road(g, samples, rng):
    """One stretch of road between two roundabouts."""
    sweep(g.lit, samples, [(-HALF, 0.05), (HALF, 0.05)],
          lambda i, j: mix(P["asphalt"], P["asphalt_light"], 0.5 + 0.25 * rng.uniform(-1, 1)))
    sweep(g.lit, samples, side_profile(-1), pave_color)
    sweep(g.lit, samples, side_profile(1), pave_color)
    for sign in (-1, 1):
        a, b = sorted((sign * (HALF - 0.19), sign * (HALF - 0.08)))
        sweep(g.g("cyan"), samples, [(a, 0.066), (b, 0.066)], lambda i, j: P["cyan"])
    for start in range(0, len(samples) - 5, 9):
        sweep(g.g("ice"), samples[start:start + 5], [(-0.07, 0.066), (0.07, 0.066)],
              lambda i, j: P["white"])


def build_ring(g, centre, gaps, rng):
    """A roundabout around `centre`, with an opening in its outer pavement at each gap angle."""
    e1, e2 = tangent_basis(centre)
    alpha = RING_R / wp.R
    n = int(math.tau * RING_R / 0.45)
    samples, angles = [], []
    for k in range(n + 1):
        th = math.tau * k / n
        u = e1 * math.cos(th) + e2 * math.sin(th)
        p = centre * math.cos(alpha) + u * math.sin(alpha)
        t = -e1 * math.sin(th) + e2 * math.cos(th)
        t = (t - p * p.dot(t)).normalized()
        side = p.cross(t).normalized()
        samples.append((p, side))
        angles.append(th)

    # which sign of `side` points away from the centre?
    p0, s0 = samples[0]
    outward = 1 if s0.dot((p0 - centre * p0.dot(centre)).normalized()) > 0 else -1

    sweep(g.lit, samples, [(-HALF, 0.05), (HALF, 0.05)],
          lambda i, j: mix(P["asphalt"], P["asphalt_light"], 0.5 + 0.25 * rng.uniform(-1, 1)))
    sweep(g.lit, samples, side_profile(-outward), pave_color)  # inner pavement, unbroken

    # outer pavement and its edge line stop at each opening
    open_flags = [all(angle_gap(th, gp) > GAP_HALF for gp in gaps) for th in angles]
    for run in runs_of(open_flags):
        if len(run) < 2:
            continue
        sub = [samples[i] for i in run]
        sweep(g.lit, sub, side_profile(outward), pave_color)
        a, b = sorted((outward * (HALF - 0.19), outward * (HALF - 0.08)))
        sweep(g.g("cyan"), sub, [(a, 0.066), (b, 0.066)], lambda i, j: P["cyan"])
    a, b = sorted((-outward * (HALF - 0.19), -outward * (HALF - 0.08)))
    sweep(g.g("cyan"), samples, [(a, 0.066), (b, 0.066)], lambda i, j: P["cyan"])
    for start in range(0, len(samples) - 5, 9):
        sweep(g.g("ice"), samples[start:start + 5], [(-0.07, 0.066), (0.07, 0.066)],
              lambda i, j: P["white"])

    # radium lamps just outside the ring, skipping the openings
    lamp_alpha = (RING_R + HALF + PAVE + 1.6) / wp.R
    for k in range(6):
        th = math.tau * (k + 0.5) / 6
        if any(angle_gap(th, gp) < GAP_HALF + 0.2 for gp in gaps):
            continue
        u = e1 * math.cos(th) + e2 * math.sin(th)
        lp = (centre * math.cos(lamp_alpha) + u * math.sin(lamp_alpha)).normalized()
        lamp_post(g, 0, 0, "radium", 2.4, base=wp.place(lp, rng.uniform(0, 360)))
        wp.SOLIDS.append((lp, 0.3))


def build_road(dirs, path_pts):
    rng = random.Random(12)
    centres = [d.normalized() for d in dirs.values()]  # the spawn gets no roundabout
    pts = [p for p, _ in path_pts]
    n = len(pts)

    # routes stop where they meet a roundabout
    keep = [
        all(wp.arc_dist(p.normalized(), c) > JOIN for c in centres)
        and wp.arc_dist(p.normalized(), wp.SPAWN) > 5.2
        for p in pts
    ]
    runs = [r for r in runs_of(keep) if len(r) >= 4]

    g = Group("Road", ao=False, seed=77, bevel=0.0)
    gaps = {i: [] for i in range(len(centres))}

    for run in runs:
        samples = []
        for i in run:
            p = pts[i].normalized()
            t = (pts[(i + 1) % n] - pts[(i - 1) % n]).normalized()
            samples.append((p, p.cross(t).normalized()))
        route_road(g, samples, rng)

        # note the bearing at which this route meets each roundabout it ends at
        for end in (samples[0][0], samples[-1][0]):
            for ci, c in enumerate(centres):
                if wp.arc_dist(end, c) < JOIN + 2.0:
                    e1, e2 = tangent_basis(c)
                    gaps[ci].append(math.atan2(end.dot(e2), end.dot(e1)) % math.tau)

    for ci, c in enumerate(centres):
        build_ring(g, c, gaps[ci], rng)

    return g.build()
