"""Shared helpers for building the world in Blender (run with `blender -b -P`).

Models are smooth-shaded, beveled hard-surface and organic shapes painted with per-vertex
colors, with ambient occlusion baked into those colors (see `bake_ao`). Lights and windows
use a few emissive materials. Modelling space is Blender's: +Z up, +Y forward.
"""
import math
import random

import bmesh
import bpy
import numpy as np
from mathutils import Euler, Matrix, Quaternion, Vector, noise
from mathutils.bvhtree import BVHTree

# ---------------------------------------------------------------- palette ---


def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def C(hex_color):
    """'#rrggbb' (sRGB) -> linear rgb tuple, which is what glTF vertex colors expect."""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
    return (_lin(r), _lin(g), _lin(b))


P = {
    # terrain: deep slate-blue rock, teal moss, dark asphalt roads (a cool night palette)
    "earth": C("#2b3558"),
    "earth_dark": C("#1d2540"),
    "earth_light": C("#3a4a78"),
    "cliff": C("#232a47"),
    "sand": C("#2a2f48"),
    "sand_dark": C("#1f2438"),
    "grass": C("#1f6b66"),
    "grass_dark": C("#164d52"),
    "grass_light": C("#2f9a8c"),
    "plaza": C("#39426b"),
    "plaza_dark": C("#282f52"),
    # roads
    "asphalt": C("#262b42"),
    "asphalt_light": C("#2f3550"),
    "pavement": C("#6a7699"),
    "pavement_dark": C("#58648a"),
    "curb": C("#8d9ac0"),
    # structures
    "white": C("#dfe6f7"),
    "cream": C("#9aa8c8"),
    "stone": C("#7f8db0"),
    "stone_dark": C("#566287"),
    "brick": C("#5a4a7a"),
    "roof": C("#1c2142"),
    "metal": C("#9fb0d0"),
    "gunmetal": C("#3a4160"),
    "iron": C("#1f243f"),
    "navy": C("#12152e"),
    "glass": C("#1f3f78"),
    # accents (match the site palette)
    "orange": C("#ff8a3d"),
    "orange_deep": C("#c9501e"),
    "cyan": C("#3ddcff"),
    "blue": C("#3a7bff"),
    "magenta": C("#d95cff"),
    "violet": C("#915eff"),
    "yellow": C("#ffd166"),
    "red": C("#ff4d6d"),
    "panel": C("#2a4cb8"),
    "panel_light": C("#7d98f0"),
    "teal_paint": C("#1f9ec0"),
    "steel_blue": C("#2a5fa8"),
    # nature
    "rock": C("#4a5578"),
    "rock_dark": C("#2f3858"),
    "rock_light": C("#6a78a0"),
    "trunk": C("#3b2f4f"),
    "leaf_green": C("#1d7a68"),
    "leaf_lime": C("#33b08f"),
    "leaf_teal": C("#1f8fb0"),
    "leaf_amber": C("#6c4fd0"),
    "leaf_pink": C("#b44fd0"),
    "mushroom": C("#c04fd0"),
    # character
    "skin": C("#e8b48c"),
    "hair": C("#14101c"),
    "jacket": C("#2f64d8"),
    "pants": C("#242a44"),
}

GLOW_COLORS = {
    "cyan": "#3ddcff",
    "blue": "#3a8bff",
    "orange": "#ff8a3d",
    "amber": "#ffb04a",
    "magenta": "#d95cff",
    "violet": "#915eff",
    "yellow": "#ffd166",
    "white": "#fff6e8",
    "red": "#ff4d6d",
    "green": "#6bff9c",
    "radium": "#7dffb8",
    "halo": "#1d5a48",
    "ice": "#8fd8ff",
}

# ------------------------------------------------------------- materials ---

_materials = {}

SURFACES = {
    # key: (roughness, metallic)
    "lit": (0.85, 0.0),
    "paint": (0.4, 0.2),
    "metal": (0.32, 0.85),
}


def _make_surface(key):
    rough, metal = SURFACES[key]
    mat = bpy.data.materials.new(key.capitalize())
    mat.use_nodes = True
    mat.use_backface_culling = False
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = nodes["Principled BSDF"]
    attr = nodes.new("ShaderNodeVertexColor")
    attr.layer_name = "Col"
    links.new(attr.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    return mat


def _make_glow(name, hex_color):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = False
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    rgb = C(hex_color)
    bsdf.inputs["Base Color"].default_value = (rgb[0] * 0.2, rgb[1] * 0.2, rgb[2] * 0.2, 1)
    bsdf.inputs["Emission Color"].default_value = (*rgb, 1)
    bsdf.inputs["Emission Strength"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.5
    return mat


def material(key):
    if key not in _materials:
        _materials[key] = _make_surface(key) if key in SURFACES else _make_glow(
            "Glow_" + key, GLOW_COLORS[key]
        )
    return _materials[key]


# ---------------------------------------------------------------- helpers ---


def rot(x=0.0, y=0.0, z=0.0):
    """Euler rotation in degrees -> 4x4 matrix."""
    return Euler((math.radians(x), math.radians(y), math.radians(z)), "XYZ").to_matrix().to_4x4()


def tr(x=0.0, y=0.0, z=0.0):
    return Matrix.Translation((x, y, z))


def ring_points(count, radius, start=0.0):
    """Points on a circle: [(x, y, angle_deg)]"""
    out = []
    for i in range(count):
        a = math.radians(start) + (i / count) * math.tau
        out.append((math.cos(a) * radius, math.sin(a) * radius, math.degrees(a)))
    return out


def clamp01(x):
    return max(0.0, min(1.0, x))


def mix(a, b, t):
    t = clamp01(t)
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


# ----------------------------------------------------------- mesh builder ---


class Mesh:
    """A bmesh that collects primitives, all painted with per-vertex colors."""

    def __init__(self, name, mat_key="lit", ao=(0.0, 6.0, 0.86, 1.0), jitter=0.025, seed=1):
        self.name = name
        self.mat_key = mat_key
        self.bm = bmesh.new()
        self.col = self.bm.loops.layers.float_color.new("Col")
        self.ao = ao
        self.jitter = jitter
        self.rng = random.Random(seed)

    # -- internals ---------------------------------------------------------
    @staticmethod
    def _faces_of(verts):
        return list({f for v in verts for f in v.link_faces})

    def _finish(self, faces, color, grad, jitter, base, fix_normals=True):
        bm = self.bm
        new = list(faces)
        if fix_normals:
            bmesh.ops.recalc_face_normals(bm, faces=new)
        grad = self.ao if grad is None else grad
        jit = self.jitter if jitter is None else jitter
        shade = {}
        for f in new:
            for v in f.verts:
                if v not in shade:
                    shade[v] = 1.0 + self.rng.uniform(-jit, jit)
        for f in new:
            for loop in f.loops:
                k = shade[loop.vert]
                if grad:
                    z0, z1, dark, light = grad
                    t = clamp01((loop.vert.co.z - z0) / (z1 - z0))
                    k *= dark + (light - dark) * t
                loop[self.col] = (color[0] * k, color[1] * k, color[2] * k, 1.0)
        if base is not None:
            verts = list({v for f in new for v in f.verts})
            bmesh.ops.transform(bm, matrix=base, verts=verts)

    # -- primitives (pos = bottom centre unless noted) ------------------------
    def box(self, size, pos=(0, 0, 0), rotation=(0, 0, 0), color=None, grad=None,
            jitter=None, base=None, center=False):
        sx, sy, sz = size
        lift = 0.0 if center else sz / 2
        m = tr(*pos) @ rot(*rotation) @ tr(0, 0, lift) @ Matrix.Diagonal((sx, sy, sz, 1.0))
        res = bmesh.ops.create_cube(self.bm, size=1.0, matrix=m, calc_uvs=False)
        self._finish(self._faces_of(res["verts"]), color or P["metal"], grad, jitter, base)

    def cyl(self, r1, r2=None, h=1.0, pos=(0, 0, 0), rotation=(0, 0, 0), segs=20,
            color=None, grad=None, jitter=None, base=None, center=False, caps=True):
        r2 = r1 if r2 is None else r2
        lift = 0.0 if center else h / 2
        m = tr(*pos) @ rot(*rotation) @ tr(0, 0, lift)
        res = bmesh.ops.create_cone(self.bm, cap_ends=caps, cap_tris=False, segments=segs,
                                    radius1=r1, radius2=r2, depth=h, matrix=m, calc_uvs=False)
        self._finish(self._faces_of(res["verts"]), color or P["metal"], grad, jitter, base)

    def ball(self, r, pos=(0, 0, 0), subdiv=3, scale=(1, 1, 1), rotation=(0, 0, 0),
             color=None, grad=None, jitter=None, base=None, lump=0.0, lump_freq=1.3):
        """Icosphere; `lump` adds smooth coherent bumps (rocks, canopies, clouds)."""
        m = tr(*pos) @ rot(*rotation) @ Matrix.Diagonal((*scale, 1.0))
        res = bmesh.ops.create_icosphere(self.bm, subdivisions=subdiv, radius=r, matrix=m,
                                         calc_uvs=False)
        if lump:
            seed = Vector((self.rng.uniform(0, 50), self.rng.uniform(0, 50), self.rng.uniform(0, 50)))
            centre = Vector(pos)
            for v in res["verts"]:
                d = v.co - centre
                n = noise.noise(d.normalized() * lump_freq + seed)
                v.co = centre + d * (1.0 + n * lump)
        self._finish(self._faces_of(res["verts"]), color or P["rock"], grad, jitter, base)

    def lathe(self, profile, pos=(0, 0, 0), rotation=(0, 0, 0), segs=24, color=None,
              grad=None, jitter=None, base=None, caps=True):
        """Revolve [(radius, z), ...] (bottom to top) around Z."""
        bm = self.bm
        made = []
        m = tr(*pos) @ rot(*rotation)
        angles = [(k / segs) * math.tau for k in range(segs)]
        rings = []
        for r, z in profile:
            if abs(r) < 1e-6:
                rings.append([bm.verts.new(m @ Vector((0, 0, z)))])
            else:
                rings.append([bm.verts.new(m @ Vector((r * math.cos(a), r * math.sin(a), z)))
                              for a in angles])
        for i in range(len(rings) - 1):
            a, b = rings[i], rings[i + 1]
            for k in range(segs):
                k2 = (k + 1) % segs
                if len(a) == 1 and len(b) == 1:
                    continue
                if len(a) == 1:
                    made.append(bm.faces.new((a[0], b[k2], b[k])))
                elif len(b) == 1:
                    made.append(bm.faces.new((a[k], a[k2], b[0])))
                else:
                    made.append(bm.faces.new((a[k], a[k2], b[k2], b[k])))
        if caps:
            if len(rings[0]) > 1:
                made.append(bm.faces.new(list(reversed(rings[0]))))
            if len(rings[-1]) > 1:
                made.append(bm.faces.new(rings[-1]))
        self._finish(made, color or P["metal"], grad, jitter, base)

    def prism(self, poly, height, pos=(0, 0, 0), rotation=(0, 0, 0), color=None, grad=None,
              jitter=None, base=None):
        """Extrude a convex 2D polygon [(x, y), ...] (counter-clockwise) up by `height`."""
        bm = self.bm
        m = tr(*pos) @ rot(*rotation)
        low = [bm.verts.new(m @ Vector((x, y, 0))) for x, y in poly]
        high = [bm.verts.new(m @ Vector((x, y, height))) for x, y in poly]
        n = len(poly)
        made = [bm.faces.new(list(reversed(low))), bm.faces.new(high)]
        for i in range(n):
            j = (i + 1) % n
            made.append(bm.faces.new((low[i], low[j], high[j], high[i])))
        self._finish(made, color or P["metal"], grad, jitter, base)

    def torus(self, R, r, pos=(0, 0, 0), rotation=(0, 0, 0), major=40, minor=10, arc=360.0,
              start=0.0, color=None, grad=None, jitter=None, base=None):
        bm = self.bm
        made = []
        m = tr(*pos) @ rot(*rotation)
        full = arc >= 359.9
        steps = major if full else major + 1
        a0, span = math.radians(start), math.radians(arc)
        grid = []
        for i in range(steps):
            a = a0 + (i / major) * span
            row = []
            for j in range(minor):
                b = (j / minor) * math.tau
                rr = R + r * math.cos(b)
                row.append(bm.verts.new(m @ Vector((rr * math.cos(a), rr * math.sin(a),
                                                    r * math.sin(b)))))
            grid.append(row)
        for i in range(major):
            i2 = (i + 1) % steps if full else i + 1
            for j in range(minor):
                j2 = (j + 1) % minor
                made.append(bm.faces.new((grid[i][j], grid[i2][j], grid[i2][j2], grid[i][j2])))
        self._finish(made, color or P["metal"], grad, jitter, base, fix_normals=full)

    def tube(self, a, b, r=0.08, segs=8, color=None, grad=None, jitter=None, base=None):
        """A thin strut between two points."""
        a, b = Vector(a), Vector(b)
        d = b - a
        length = d.length
        if length < 1e-6:
            return
        q = Vector((0, 0, 1)).rotation_difference(d.normalized())
        m = tr(*a) @ q.to_matrix().to_4x4() @ tr(0, 0, length / 2)
        res = bmesh.ops.create_cone(self.bm, cap_ends=True, cap_tris=False, segments=segs,
                                    radius1=r, radius2=r, depth=length, matrix=m,
                                    calc_uvs=False)
        self._finish(self._faces_of(res["verts"]), color or P["gunmetal"], grad, jitter, base)

    def capsule(self, r, length, pos=(0, 0, 0), rotation=(0, 0, 0), segs=16, color=None,
                grad=None, jitter=None, base=None):
        """Pill shape standing on `pos`, total height = length + 2r."""
        prof = [(0.0, 0.0)]
        for t in range(1, 6):
            a = math.radians(90 - t * 15)
            prof.append((r * math.cos(a), r - r * math.sin(a)))
        for t in range(0, 6):
            a = math.radians(t * 15)
            prof.append((r * math.cos(a), r + length + r * math.sin(a)))
        prof.append((0.0, 2 * r + length))
        self.lathe(prof, pos, rotation, segs=segs, color=color, grad=grad, jitter=jitter,
                   base=base, caps=False)

    # -- output ------------------------------------------------------------------
    def to_object(self, parent=None, location=(0, 0, 0), name=None, bevel=0.0,
                  smooth_angle=45.0):
        if not self.bm.faces:
            return None
        me = bpy.data.meshes.new((name or self.name) + "_mesh")
        self.bm.to_mesh(me)
        me.materials.append(material(self.mat_key))
        ob = bpy.data.objects.new(name or self.name, me)
        ob.location = location
        bpy.context.scene.collection.objects.link(ob)
        if parent is not None:
            ob.parent = parent
        finalize(ob, bevel, smooth_angle)
        return ob

    def free(self):
        self.bm.free()


def finalize(ob, bevel=0.0, smooth_angle=45.0):
    """Bevel sharp edges, then shade smooth except across sharp angles."""
    view = bpy.context.view_layer
    view.objects.active = ob
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    if bevel > 0:
        mod = ob.modifiers.new("Bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = "ANGLE"
        mod.angle_limit = math.radians(30)
        mod.harden_normals = False
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(smooth_angle))
    ob.select_set(False)


class Group:
    """One lit mesh, optional paint/metal meshes, and one mesh per glow colour."""

    def __init__(self, name, ao=(0.0, 6.0, 0.86, 1.0), seed=1, bevel=0.035):
        self.name = name
        self.bevel = bevel
        self._seed = seed
        self._ao = ao
        self.lit = Mesh(name + "_lit", "lit", ao=ao, seed=seed)
        self.paint = Mesh(name + "_paint", "paint", ao=ao, seed=seed + 1)
        self.metal = Mesh(name + "_metal", "metal", ao=ao, seed=seed + 2)
        self.glow = {}

    def g(self, key):
        if key not in self.glow:
            self.glow[key] = Mesh(f"{self.name}_glow_{key}", key, ao=False, jitter=0.0,
                                  seed=self._seed)
        return self.glow[key]

    def build(self, location=(0, 0, 0)):
        root = bpy.data.objects.new(self.name, None)
        root.location = location
        bpy.context.scene.collection.objects.link(root)
        for mesh in (self.lit, self.paint, self.metal):
            mesh.to_object(parent=root, bevel=self.bevel)
            mesh.free()
        for mesh in self.glow.values():
            mesh.to_object(parent=root, bevel=0.0)
            mesh.free()
        return root


# ----------------------------------------------------------- baked occlusion ---


def _hemisphere(n):
    """Cosine-weighted directions around +Z."""
    out = []
    for i in range(n):
        u = (i + 0.5) / n
        v, f, k = 0.0, 0.5, i + 1  # radical inverse, base 2
        while k:
            v += f * (k & 1)
            k >>= 1
            f *= 0.5
        r = math.sqrt(u)
        phi = math.tau * v
        out.append(Vector((r * math.cos(phi), r * math.sin(phi), math.sqrt(max(0.0, 1 - u)))))
    return out


def bake_ao(targets, occluders=(), samples=20, max_dist=2.5, floor=0.45, seed=7):
    """Multiply per-vertex ambient occlusion into each target mesh's colors.

    `targets` are mesh objects to darken; `occluders` only block light (e.g. the ground).
    Glow meshes (names containing "_glow_") are left untouched.
    """
    bpy.context.view_layer.update()
    pool = []
    for ob in list(targets) + list(occluders):
        if ob.type == "MESH" and ob not in pool:
            pool.append(ob)

    verts, polys = [], []
    for ob in pool:
        me, mw = ob.data, ob.matrix_world
        base = len(verts)
        verts.extend(mw @ v.co for v in me.vertices)
        polys.extend([base + i for i in p.vertices] for p in me.polygons)
    bvh = BVHTree.FromPolygons(verts, polys)

    rng = random.Random(seed)
    dirs = _hemisphere(samples)
    for ob in targets:
        if ob.type != "MESH" or "_glow_" in ob.name:
            continue
        me, mw = ob.data, ob.matrix_world
        attr = me.color_attributes.get("Col")
        if attr is None:
            continue
        nmat = mw.to_3x3()
        ao = np.ones(len(me.vertices), dtype=np.float32)
        for vi, v in enumerate(me.vertices):
            n = (nmat @ v.normal).normalized()
            p = mw @ v.co + n * 0.02
            q = Vector((0, 0, 1)).rotation_difference(n) @ Quaternion((0, 0, 1), rng.uniform(0, math.tau))
            hits = 0
            for d in dirs:
                if bvh.ray_cast(p, q @ d, max_dist)[0] is not None:
                    hits += 1
            ao[vi] = 1.0 - (hits / samples)
        # soften and lift: `floor` is the darkest allowed multiplier
        factor = floor + (1.0 - floor) * np.sqrt(ao)

        loops = len(me.loops)
        vidx = np.empty(loops, dtype=np.int32)
        me.loops.foreach_get("vertex_index", vidx)
        cols = np.empty(loops * 4, dtype=np.float32)
        attr.data.foreach_get("color", cols)
        cols = cols.reshape(-1, 4)
        cols[:, :3] *= factor[vidx][:, None]
        attr.data.foreach_set("color", cols.ravel())
        me.update()


def glow_color(key):
    return C(GLOW_COLORS[key])
