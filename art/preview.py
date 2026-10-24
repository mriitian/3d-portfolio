"""Headless preview renders so the art can be checked without opening Blender."""
import math
import os

import bpy
from mathutils import Vector


def setup_world(sc):
    sc.render.engine = "BLENDER_EEVEE_NEXT"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.render.film_transparent = False
    world = bpy.data.worlds.new("PreviewWorld")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.012, 0.015, 0.05, 1)
    bg.inputs["Strength"].default_value = 1.0
    sc.world = world


def add_lights():
    # warm sun + cool fill + soft sky, to mimic the dusk look used in the game
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 3.0
    sun.data.color = (1.0, 0.82, 0.62)
    sun.rotation_euler = (math.radians(55), math.radians(10), math.radians(-35))
    bpy.context.scene.collection.objects.link(sun)
    fill = bpy.data.objects.new("Fill", bpy.data.lights.new("Fill", "SUN"))
    fill.data.energy = 1.2
    fill.data.color = (0.55, 0.62, 1.0)
    fill.rotation_euler = (math.radians(70), math.radians(-20), math.radians(150))
    bpy.context.scene.collection.objects.link(fill)
    return [sun, fill]


def render(path, cam_pos, target=(0, 0, 0), lens=40, size=(900, 600)):
    sc = bpy.context.scene
    cam_data = bpy.data.cameras.new("PreviewCam")
    cam_data.lens = lens
    cam = bpy.data.objects.new("PreviewCam", cam_data)
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.location = Vector(cam_pos)
    direction = Vector(target) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    sc.render.resolution_x, sc.render.resolution_y = size
    sc.render.filepath = path
    sc.eevee.taa_render_samples = 16
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)
