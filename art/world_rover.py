"""The rover. Modelled facing +Y (which becomes -Z, the game's forward, after export)."""
import bpy

from blender_lib import Group, Mesh, P, rot, tr

WHEEL_R = 0.5
WHEEL_W = 0.44
AXLE_X = 1.02
AXLE_Y = 0.95
WHEELS = {
    "wheel_FL": (-AXLE_X, AXLE_Y),
    "wheel_FR": (AXLE_X, AXLE_Y),
    "wheel_RL": (-AXLE_X, -AXLE_Y),
    "wheel_RR": (AXLE_X, -AXLE_Y),
}


def side_profile(L, poly, width, z, color, x=0.0, **kw):
    """Extrude a (y, z) profile across the rover's width, centred on x."""
    L.prism(poly, width, (x - width / 2, 0, z), (90, 0, 90), color=color, **kw)


def build_rover():
    g = Group("Rover", ao=(0.0, 2.2, 0.72, 1.08), seed=606)
    L = g.lit

    # undercarriage + axles
    L.box((1.3, 2.5, 0.14), (0, -0.1, 0.4), color=P["navy"])
    for y in (-AXLE_Y, AXLE_Y):
        L.tube((-AXLE_X, y, WHEEL_R), (AXLE_X, y, WHEEL_R), 0.07, segs=5, color=P["metal_dark"])

    # chassis
    L.box((1.62, 2.9, 0.42), (0, -0.05, 0.46), color=P["white"], jitter=0.02)
    L.box((1.66, 2.5, 0.1), (0, -0.05, 0.62), color=P["orange"], jitter=0.02)  # side stripe
    side_profile(L, [(0.55, 0), (1.5, 0), (1.56, 0.24), (1.12, 0.52), (0.55, 0.52)], 1.46,
                 0.88, P["white"], jitter=0.02)  # hood
    g.g("orange").box((1.1, 0.05, 0.08), (0, 1.3, 1.16))  # hood vent

    # cabin with a raked windshield and glass sides
    side_profile(L, [(-0.62, 0), (0.55, 0), (0.12, 0.66), (-0.5, 0.66)], 1.4, 0.88,
                 P["white"], jitter=0.02)
    side_profile(L, [(0.57, 0.04), (0.16, 0.64), (0.06, 0.62), (0.47, 0.02)], 1.2, 0.9,
                 P["glass"], jitter=0.0)
    g.g("cyan").box((1.0, 0.04, 0.05), (0, 0.43, 1.46), (-58, 0, 0))
    for sx in (-0.71, 0.71):
        L.box((0.06, 0.62, 0.32), (sx, -0.1, 1.08), color=P["glass"], jitter=0.0)
    g.g("yellow").box((0.8, 0.14, 0.09), (0, -0.2, 1.57))  # roof light bar
    L.box((0.84, 0.18, 0.05), (0, -0.2, 1.54), color=P["metal_dark"])

    # fenders over the wheels
    for sx in (-1, 1):
        for sy in (-1, 1):
            L.box((0.52, 0.92, 0.09), (sx * AXLE_X, sy * AXLE_Y, 1.0), color=P["orange"],
                  jitter=0.02)
            L.box((0.08, 0.92, 0.26), (sx * (AXLE_X + 0.22), sy * AXLE_Y, 0.78),
                  color=P["orange"], jitter=0.02)

    # roll bar, cargo and antenna
    for sx in (-1, 1):
        L.tube((sx * 0.68, -0.72, 0.9), (sx * 0.68, -0.72, 1.75), 0.05, segs=5,
               color=P["orange_deep"])
        L.tube((sx * 0.68, -0.72, 1.75), (sx * 0.68, -1.35, 1.2), 0.05, segs=5,
               color=P["orange_deep"])
    L.tube((-0.68, -0.72, 1.75), (0.68, -0.72, 1.75), 0.05, segs=5, color=P["orange_deep"])
    L.box((1.3, 0.6, 0.36), (0, -1.05, 0.88), color=P["orange"], jitter=0.03)
    L.box((0.6, 0.5, 0.3), (-0.35, -1.1, 1.24), color=P["cyan"], jitter=0.03)
    L.box((0.5, 0.4, 0.4), (0.4, -1.05, 1.24), color=P["metal"], jitter=0.03)
    L.tube((0.62, -1.38, 0.88), (0.62, -1.38, 2.3), 0.025, segs=4, color=P["metal_dark"])
    g.g("cyan").ball(0.08, (0.62, -1.38, 2.34), 1)

    # bumper and lights
    L.box((1.8, 0.22, 0.24), (0, 1.58, 0.42), color=P["metal_dark"])
    for sx in (-1, 1):
        g.g("white").box((0.32, 0.07, 0.16), (sx * 0.52, 1.56, 0.7))
        g.g("orange").box((0.14, 0.07, 0.1), (sx * 0.8, 1.54, 0.62))
        g.g("red").box((0.28, 0.06, 0.14), (sx * 0.56, -1.53, 0.7))

    root = g.build()

    # wheels: separate nodes with their origin on the axle, so the game can spin them
    for name, (x, y) in WHEELS.items():
        w = Mesh(name, ao=False, jitter=0.03, seed=hash(name) % 1000)
        w.cyl(WHEEL_R, WHEEL_R, WHEEL_W, (0, 0, 0), (0, 90, 0), segs=10, color=P["navy"],
              center=True)
        w.cyl(WHEEL_R * 0.58, WHEEL_R * 0.58, WHEEL_W + 0.04, (0, 0, 0), (0, 90, 0), segs=8,
              color=P["orange"], center=True)
        w.cyl(WHEEL_R * 0.22, WHEEL_R * 0.22, WHEEL_W + 0.1, (0, 0, 0), (0, 90, 0), segs=6,
              color=P["white"], center=True)
        w.to_object(parent=root, location=(x, y, WHEEL_R))
        w.free()
    return root
