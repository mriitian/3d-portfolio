"""The rover and its driver. Modelled facing +Y (which becomes -Z, the game's forward)."""
import math
import os

import bpy

import preview as pv
from blender_lib import Group, Mesh, P, bake_ao, ring_points, rot, tr

WHEEL_R = 0.53
AXLE_X = 1.08
AXLE_Y = 1.0
WHEELS = {
    "wheel_FL": (-AXLE_X, AXLE_Y),
    "wheel_FR": (AXLE_X, AXLE_Y),
    "wheel_RL": (-AXLE_X, -AXLE_Y),
    "wheel_RR": (AXLE_X, -AXLE_Y),
}


def side_profile(g_mesh, poly, width, z, color, x=0.0):
    """Extrude a (y, z) profile across the rover's width, centred on x."""
    g_mesh.prism(poly, width, (x - width / 2, 0, z), (90, 0, 90), color=color)


def build_wheel(name):
    w = Mesh(name, mat_key="paint", ao=False, jitter=0.02, seed=hash(name) % 1000)
    spin = rot(0, 90, 0)  # axle along X
    tire = [(0.36, -0.25), (0.47, -0.27), (0.53, -0.2), (0.56, -0.08), (0.56, 0.08),
            (0.53, 0.2), (0.47, 0.27), (0.36, 0.25)]
    w.lathe(tire, segs=40, color=P["iron"], base=spin, caps=True)
    for x, y, a in ring_points(20, 0.565):
        w.box((0.13, 0.12, 0.46), (x, y, 0), (0, 0, a + 90), color=P["navy"], base=spin,
              center=True)
    w.cyl(0.36, 0.36, 0.36, (0, 0, 0), segs=32, color=P["metal"], base=spin, center=True)
    w.cyl(0.28, 0.28, 0.4, (0, 0, 0), segs=24, color=P["gunmetal"], base=spin, center=True)
    for x, y, a in ring_points(5, 0.2):
        w.box((0.34, 0.06, 0.42), (x * 0.5, y * 0.5, 0), (0, 0, a), color=P["white"],
              base=spin, center=True)
    w.cyl(0.1, 0.1, 0.46, (0, 0, 0), segs=14, color=P["teal_paint"], base=spin, center=True)
    return w


def build_driver(g):
    skin, jacket, pants = P["skin"], P["jacket"], P["pants"]
    # seat
    g.lit.box((0.95, 0.85, 0.18), (0, -0.28, 0.78), color=P["iron"])
    g.lit.box((0.95, 0.16, 0.85), (0, -0.7, 0.78), (-6, 0, 0), color=P["iron"])
    # legs and boots
    for sx in (-1, 1):
        x = sx * 0.17
        g.paint.tube((x, -0.45, 1.02), (x, 0.12, 1.05), 0.11, segs=14, color=pants)
        g.paint.tube((x, 0.12, 1.05), (x, 0.42, 0.82), 0.095, segs=14, color=pants)
        g.paint.box((0.2, 0.34, 0.14), (x, 0.52, 0.66), color=P["navy"], center=True)
    # torso, jacket collar
    g.paint.capsule(0.27, 0.32, (0, -0.42, 1.0), (8, 0, 0), segs=20, color=jacket)
    g.paint.cyl(0.23, 0.23, 0.07, (0, -0.37, 1.62), segs=20, color=P["white"])
    # arms to the wheel
    for sx in (-1, 1):
        sh = (sx * 0.31, -0.4, 1.5)
        el = (sx * 0.36, -0.02, 1.32)
        hand = (sx * 0.2, 0.28, 1.34)
        g.paint.tube(sh, el, 0.075, segs=12, color=jacket)
        g.paint.tube(el, hand, 0.065, segs=12, color=jacket)
        g.lit.ball(0.075, hand, 3, color=skin)
    # head, hair, face bits
    head = (0, -0.38, 1.9)
    g.lit.ball(0.24, head, 4, color=skin, scale=(1, 1.02, 1.05))
    g.lit.ball(0.255, (0, -0.42, 1.95), 4, color=P["hair"], scale=(1.02, 1.02, 0.9))
    g.lit.ball(0.12, (0, -0.28, 1.97), 3, color=P["hair"], scale=(1.5, 0.9, 0.7))
    for sx in (-1, 1):
        g.lit.ball(0.05, (sx * 0.24, -0.36, 1.88), 2, color=skin)
    # backpack with a glowing emblem
    g.paint.box((0.56, 0.26, 0.74), (0, -0.78, 1.02), color=P["gunmetal"])
    g.paint.box((0.5, 0.22, 0.1), (0, -0.78, 1.76), color=P["steel_blue"])
    g.g("blue").box((0.34, 0.04, 0.34), (0, -0.925, 1.42), center=True)
    g.g("cyan").torus(0.13, 0.025, (0, -0.945, 1.42), (90, 0, 0), major=24, minor=6)
    g.metal.tube((0.2, -0.8, 1.76), (0.2, -0.8, 2.2), 0.02, segs=6)
    g.g("cyan").ball(0.05, (0.2, -0.8, 2.22), 3)
    # steering wheel + dash
    g.paint.box((1.2, 0.34, 0.36), (0, 0.38, 0.94), color=P["gunmetal"])
    g.metal.torus(0.2, 0.03, (0, 0.2, 1.38), (62, 0, 0), major=32, minor=8, color=P["iron"])
    g.metal.tube((0, 0.35, 1.0), (0, 0.22, 1.36), 0.035, segs=8)


def build_rover(args):
    g = Group("Rover", ao=(0.0, 2.4, 0.86, 1.0), seed=606, bevel=0.05)

    # undercarriage, axles, skid plate
    g.metal.box((1.3, 2.6, 0.16), (0, -0.1, 0.36), color=P["iron"])
    for y in (-AXLE_Y, AXLE_Y):
        g.metal.tube((-AXLE_X, y, WHEEL_R), (AXLE_X, y, WHEEL_R), 0.08, segs=10,
                     color=P["gunmetal"])
        g.metal.ball(0.22, (0, y, WHEEL_R), 3, color=P["gunmetal"])

    # tub, side stripes, hood, tail
    g.paint.box((1.64, 3.0, 0.42), (0, -0.05, 0.5), color=P["white"])
    g.paint.box((1.68, 2.2, 0.09), (0, -0.2, 0.7), color=P["teal_paint"])
    side_profile(g.paint, [(0.6, 0), (1.55, 0), (1.62, 0.22), (1.15, 0.5), (0.6, 0.5)], 1.5,
                 0.92, P["white"])
    g.paint.box((1.3, 0.7, 0.3), (0, -1.28, 0.92), color=P["white"])
    g.g("blue").box((0.9, 0.05, 0.07), (0, 1.35, 1.34))
    g.metal.box((0.9, 0.5, 0.06), (0, 1.0, 1.42), (-8, 0, 0), color=P["gunmetal"])  # hood scoop

    # fenders, bumpers, skirts
    for sx in (-1, 1):
        for sy in (-1, 1):
            g.paint.box((0.6, 0.98, 0.1), (sx * AXLE_X, sy * AXLE_Y, 1.0), color=P["teal_paint"])
            g.paint.box((0.09, 0.98, 0.26), (sx * (AXLE_X + 0.26), sy * AXLE_Y, 0.8),
                        color=P["teal_paint"])
    g.metal.box((1.9, 0.24, 0.28), (0, 1.66, 0.42), color=P["gunmetal"])
    g.metal.box((1.9, 0.24, 0.28), (0, -1.66, 0.42), color=P["gunmetal"])
    for sx in (-1, 1):
        g.g("blue").box((0.05, 2.1, 0.06), (sx * 0.86, -0.05, 0.38))  # underglow strips

    # roll cage
    for y, rr in ((-0.8, 0.8), (0.52, 0.72)):
        g.metal.torus(rr, 0.045, (0, y, 0.95), (90, 0, 0), major=36, minor=8, arc=180,
                      color=P["steel_blue"])
    for sx in (-1, 1):
        g.metal.tube((sx * 0.8, -0.8, 1.7), (sx * 0.72, 0.52, 1.68), 0.045, segs=8,
                     color=P["steel_blue"])
    g.metal.tube((-0.75, -0.8, 1.2), (0.75, -0.8, 1.2), 0.035, segs=8, color=P["steel_blue"])
    g.g("white").box((1.0, 0.1, 0.1), (0, 0.55, 1.78), center=True)  # light bar
    g.metal.box((1.06, 0.14, 0.14), (0, 0.55, 1.78), color=P["iron"], center=True)

    # headlights, taillights
    for sx in (-1, 1):
        g.metal.torus(0.17, 0.03, (sx * 0.55, 1.67, 0.74), (90, 0, 0), major=24, minor=6,
                      color=P["gunmetal"])
        g.g("white").cyl(0.15, 0.15, 0.05, (sx * 0.55, 1.665, 0.74), (90, 0, 0), segs=24,
                         center=True)
        g.g("amber").box((0.12, 0.06, 0.1), (sx * 0.82, 1.64, 0.62), center=True)
        g.g("red").box((0.3, 0.06, 0.13), (sx * 0.56, -1.68, 0.74), center=True)

    # rear cargo
    g.metal.box((1.3, 0.8, 0.07), (0, -1.28, 1.09), color=P["gunmetal"])
    g.paint.box((0.55, 0.5, 0.42), (-0.32, -1.3, 1.16), color=P["cyan"])
    g.paint.box((0.5, 0.45, 0.5), (0.35, -1.28, 1.16), color=P["steel_blue"])
    g.paint.cyl(0.2, 0.2, 0.55, (0.05, -1.55, 1.1), segs=18, color=P["white"])
    g.metal.tube((0.62, -1.62, 1.1), (0.62, -1.62, 2.55), 0.022, segs=6)
    g.g("cyan").ball(0.06, (0.62, -1.62, 2.58), 3)

    build_driver(g)
    root = g.build()

    for name, (x, y) in WHEELS.items():
        w = build_wheel(name)
        w.to_object(parent=root, location=(x, y, WHEEL_R), bevel=0.02)
        w.free()

    # soft contact shadows against an imaginary ground
    ground = Mesh("_ground", ao=False, jitter=0)
    ground.cyl(6, 6, 0.4, (0, 0, -0.4), segs=48)
    ground_ob = ground.to_object()
    ground.free()
    meshes = [ob for ob in root.children_recursive if ob.type == "MESH"]
    bake_ao(meshes, [ground_ob], samples=max(12, args.ao), max_dist=1.4, floor=0.5)
    bpy.data.objects.remove(ground_ob)
    return root


def preview(rover, folder):
    for ob in bpy.data.objects:
        ob.hide_render = True
    for ob in [rover, *rover.children_recursive]:
        ob.hide_render = False
    ground = Mesh("_pg", ao=False, jitter=0)
    ground.cyl(5, 5, 0.4, (0, 0, -0.4), segs=48, color=P["sand"])
    gob = ground.to_object()
    ground.free()
    pv.render(os.path.join(folder, "rover_back.png"), (-4.6, -6.2, 3.4), target=(0, 0, 1.0),
              lens=45, size=(1000, 650))
    pv.render(os.path.join(folder, "rover_front.png"), (4.8, 5.6, 2.6), target=(0, 0, 0.9),
              lens=45, size=(1000, 650))
    bpy.data.objects.remove(gob)
    for ob in bpy.data.objects:
        ob.hide_render = False
