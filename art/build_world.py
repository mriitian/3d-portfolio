"""Build the Orbital Playground art in Blender and export it for the web.

Run:  blender -b -P art/build_world.py -- --only all --out OUT_DIR [--preview DIR] [--ao 20]
      --only: all | planet | zones | rover | about | projects | skills | experience | contact

Outputs  world.glb (planet, props, sky objects, one node per zone)
         rover.glb (the rover and driver, wheels as separate nodes)
"""
import argparse
import importlib
import os
import sys
import time

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import preview  # noqa: E402
from blender_lib import Mesh, P, bake_ao, tr  # noqa: E402

ZONE_MODULES = {
    "about": "zone_launchpad",
    "projects": "zone_projects",
    "skills": "zone_observatory",
    "experience": "zone_station",
    "contact": "zone_commhub",
}


def parse():
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ap.add_argument("--preview", default=None)
    ap.add_argument("--ao", type=int, default=20)
    ap.add_argument("--only", default="all")
    return ap.parse_args(argv)


def export(path, roots):
    bpy.ops.object.select_all(action="DESELECT")

    def select(ob):
        ob.select_set(True)
        for child in ob.children:
            select(child)

    for r in roots:
        select(r)
    bpy.ops.export_scene.gltf(
        filepath=path,
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_vertex_color="ACTIVE",
        export_cameras=False,
        export_lights=False,
        export_yup=True,
        export_texcoords=False,
        export_extras=False,
    )
    print("EXPORTED", path, os.path.getsize(path))


def meshes_of(root):
    return [ob for ob in [root, *root.children_recursive] if ob.type == "MESH"]


def write_obstacles(out_dir):
    """Positions of everything solid, in the game's (three.js) coordinates."""
    import json
    import math

    from mathutils import Vector

    import world_planet as wp

    items = []
    for d, r in wp.SOLIDS:
        items.append([round(d.x, 4), round(d.z, 4), round(-d.y, 4), round(r, 2)])
    for zid, lat, lon in wp.ZONE_DEFS:
        la, lo = math.radians(lat), math.radians(lon)
        dir_t = Vector((math.cos(la) * math.cos(lo), math.sin(la), math.cos(la) * math.sin(lo)))
        q = Vector((0, 1, 0)).rotation_difference(dir_t)
        mod = importlib.import_module(ZONE_MODULES[zid])
        for x, y, r in mod.COLLIDERS:
            p = (dir_t * wp.R + q @ Vector((x, 0, -y))).normalized()
            items.append([round(p.x, 4), round(p.y, 4), round(p.z, 4), round(r, 2)])
    path = os.path.join(out_dir, "obstacles.json")
    with open(path, "w") as fh:
        json.dump(items, fh, separators=(",", ":"))
    print("OBSTACLES", len(items), path)


def make_ground(radius, color=None):
    """A flat disc used as an occluder (and preview floor); never exported."""
    disc = Mesh("_ground", ao=False, jitter=0)
    disc.cyl(radius, radius, 0.4, (0, 0, -0.4), segs=64, color=color or P["plaza"])
    ob = disc.to_object()
    disc.free()
    return ob


def build_zone(zid, ground, args):
    mod = importlib.import_module(ZONE_MODULES[zid])
    t = time.time()
    root = mod.build()
    bake_ao(meshes_of(root), [ground], samples=args.ao, max_dist=2.6)
    print(f"ZONE {zid} built in {time.time() - t:.1f}s")
    return root


def preview_zone(root, zid, ground, folder):
    for other in bpy.data.objects:
        if other.type in {"MESH", "EMPTY"} and other.name != "_ground":
            other.hide_render = True
    for ob in [root, *root.children_recursive]:
        ob.hide_render = False
    ground.hide_render = False
    preview.render(os.path.join(folder, f"zone_{zid}.png"), (12, -15, 9), target=(0, 0, 4.2),
                   lens=34)
    preview.render(os.path.join(folder, f"zone_{zid}_b.png"), (-13, 11, 7), target=(0, 0, 3.8),
                   lens=34)
    for other in bpy.data.objects:
        other.hide_render = False


def main():
    args = parse()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    roots = []

    if args.preview:
        os.makedirs(args.preview, exist_ok=True)
        preview.setup_world(bpy.context.scene)
        preview.add_lights()

    zone_ids = list(ZONE_MODULES) if args.only in ("all", "zones") else (
        [args.only] if args.only in ZONE_MODULES else [])
    if zone_ids:
        ground = make_ground(9.0)
        for zid in zone_ids:
            roots.append(build_zone(zid, ground, args))
        if args.preview:
            for zid, root in zip(zone_ids, roots):
                preview_zone(root, zid, ground, args.preview)

    if args.only in ("all", "planet"):
        import world_planet as wp
        roots.extend(wp.build_all(args))
        if args.preview:
            wp.render_previews(args.preview)

    if args.only in ("all", "rover"):
        import world_rover as wr
        rover = wr.build_rover(args)
        if args.preview:
            wr.preview(rover, args.preview)
        if args.out:
            os.makedirs(args.out, exist_ok=True)
            export(os.path.join(args.out, "rover.glb"), [rover])

    if args.out and roots:
        os.makedirs(args.out, exist_ok=True)
        export(os.path.join(args.out, "world.glb"), roots)
        if args.only == "all":
            write_obstacles(args.out)


main()
