"""Build the Orbital Playground art in Blender and export it for the web.

Run:  blender -b -P art/build_world.py -- --out public/game [--preview DIR] [--only zones]

Outputs  world.glb (planet, scatter, moon, floating rocks, one node per zone)
         rover.glb (the rover, wheels as separate nodes)
"""
import argparse
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import preview  # noqa: E402
import world_planet as wp  # noqa: E402
import world_rover as wr  # noqa: E402
import world_zones as wz  # noqa: E402
from blender_lib import Mesh, P  # noqa: E402


def parse():
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ap.add_argument("--preview", default=None)
    ap.add_argument("--only", default="all", choices=["all", "planet", "zones", "rover"])
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


def preview_zone(root, name, folder):
    """Render a zone standing on a flat plaza disc."""
    disc = Mesh("PreviewDisc", ao=False, jitter=0)
    disc.cyl(7.6, 7.6, 0.2, (0, 0, -0.2), segs=24, color=P["plaza"])
    disc_obj = disc.to_object()
    disc.free()
    preview.render(os.path.join(folder, f"zone_{name}.png"), (11, -13, 8.5), target=(0, 0, 3.0),
                   lens=36)
    preview.render(os.path.join(folder, f"zone_{name}_back.png"), (-11, 13, 8.5),
                   target=(0, 0, 3.0), lens=36)
    bpy.data.objects.remove(disc_obj)


def main():
    args = parse()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    dirs = wp.zone_dirs()
    roots = []

    if args.preview:
        os.makedirs(args.preview, exist_ok=True)
        preview.setup_world(bpy.context.scene)
        preview.add_lights()

    if args.only in ("all", "planet"):
        path_pts = wp.build_path_points(dirs)
        roots.append(wp.build_planet(dirs, path_pts))
        roots.append(wp.build_scatter(dirs, path_pts))
        roots.append(wp.build_moon())
        roots.extend(wp.build_floating_rocks())
        if args.preview:
            preview.render(os.path.join(args.preview, "planet_far.png"), (95, -70, 45),
                           lens=55)

    if args.only in ("all", "zones"):
        zone_roots = {}
        for zid, build in wz.BUILDERS:
            zone_roots[zid] = build()
        roots.extend(zone_roots.values())
        if args.preview:
            # park every zone far away except the one being rendered
            for zid, root in zone_roots.items():
                for other in zone_roots.values():
                    other.hide_render = other is not root
                    for child in other.children:
                        child.hide_render = other is not root
                preview_zone(root, zid, args.preview)
            for root in zone_roots.values():
                root.hide_render = False
                for child in root.children:
                    child.hide_render = False

    if args.only in ("all", "rover"):
        rover = wr.build_rover()
        if args.preview:
            for other in roots:
                for ob in [other, *other.children_recursive]:
                    ob.hide_render = True
            disc = Mesh("PreviewDisc", ao=False, jitter=0)
            disc.cyl(4.0, 4.0, 0.2, (0, 0, -0.2), segs=20, color=P["plaza"])
            disc_obj = disc.to_object()
            disc.free()
            preview.render(os.path.join(args.preview, "rover_front.png"), (4.6, 5.2, 2.6),
                           target=(0, 0, 0.9), lens=40)
            preview.render(os.path.join(args.preview, "rover_back.png"), (-4.6, -5.0, 2.8),
                           target=(0, 0, 0.9), lens=40)
            bpy.data.objects.remove(disc_obj)
        if args.out:
            os.makedirs(args.out, exist_ok=True)
            export(os.path.join(args.out, "rover.glb"), [rover])

    if args.out and roots:
        os.makedirs(args.out, exist_ok=True)
        export(os.path.join(args.out, "world.glb"), roots)


main()
