"""Headless preview renders with a sunset look, so the art can be checked without Blender's UI."""
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
    bg.inputs["Color"].default_value = (0.2, 0.1, 0.26, 1)
    bg.inputs["Strength"].default_value = 1.0
    sc.world = world


def add_lights():
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 4.5
    sun.data.color = (1.0, 0.68, 0.42)
    sun.data.angle = math.radians(3)
    sun.rotation_euler = (math.radians(68), math.radians(8), math.radians(-52))
    bpy.context.scene.collection.objects.link(sun)
    fill = bpy.data.objects.new("Fill", bpy.data.lights.new("Fill", "SUN"))
    fill.data.energy = 0.9
    fill.data.color = (0.55, 0.5, 1.0)
    fill.rotation_euler = (math.radians(75), math.radians(-15), math.radians(140))
    bpy.context.scene.collection.objects.link(fill)


def render(path, cam_pos, target=(0, 0, 0), lens=40, size=(1000, 650)):
    sc = bpy.context.scene
    cam_data = bpy.data.cameras.new("PreviewCam")
    cam_data.lens = lens
    cam = bpy.data.objects.new("PreviewCam", cam_data)
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.location = Vector(cam_pos)
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.resolution_x, sc.render.resolution_y = size
    sc.render.filepath = path
    sc.eevee.taa_render_samples = 24
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)
