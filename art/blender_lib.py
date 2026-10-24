"""Shared helpers for building the low-poly world in Blender (run with `blender -b -P`).

Everything is flat-shaded geometry painted with per-face vertex colors, which keeps
the exported files tiny and gives the stylised "game art" look. Glowing parts use a
handful of emissive materials. Modelling space is Blender's: +Z up, +Y forward.
"""
import math
import random

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

# ---------------------------------------------------------------- palette ---


def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def C(hex_color):
    """'#rrggbb' (sRGB) -> linear rgb tuple, which is what glTF vertex colors expect."""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
    return (_lin(r), _lin(g), _lin(b))


P = {
    # world
    "ground_a": C("#454aa6"),
    "ground_b": C("#5556c2"),
    "ground_c": C("#337aab"),
    "ground_d": C("#6a5fd8"),
    "plaza": C("#26264f"),
    "path": C("#f6b06a"),
    "path_edge": C("#cf8449"),
    "crater": C("#2b2d6c"),
    "crater_rim": C("#6a67c9"),
    # structures
    "white": C("#f1effa"),
    "stone": C("#c9c6e6"),
    "metal": C("#aeb3cf"),
    "metal_dark": C("#5d6283"),
    "slate": C("#2c2c4d"),
    "slate_light": C("#3b3b63"),
    "navy": C("#16183a"),
    "glass": C("#244a7a"),
    # accents (match the site palette)
    "orange": C("#ff8a3d"),
    "orange_deep": C("#e2561f"),
    "cyan": C("#3ddcff"),
    "magenta": C("#d95cff"),
    "violet": C("#915eff"),
    "yellow": C("#ffd166"),
    "red": C("#ff4d6d"),
    "panel": C("#2c4fc0"),
    "panel_light": C("#6f8cf0"),
    # nature
    "rock": C("#6e6c97"),
    "rock_dark": C("#4b4a76"),
    "rock_light": C("#9c99c4"),
    "trunk": C("#6b4a5e"),
    "leaf_pink": C("#ff7ad9"),
    "leaf_teal": C("#2fd6b4"),
    "leaf_amber": C("#ffb35c"),
    "leaf_violet": C("#a77bff"),
    "grass": C("#38c9b0"),
    "grass_dark": C("#27957f"),
    "mushroom": C("#ff6b8a"),
}

GLOW_COLORS = {
    "cyan": "#3ddcff",
    "orange": "#ff8a3d",
    "magenta": "#d95cff",
    "violet": "#915eff",
    "yellow": "#ffd166",
    "white": "#f4f1ff",
    "red": "#ff4d6d",
}

# ------------------------------------------------------------- materials ---

_materials = {}


def _make_lit():
    mat = bpy.data.materials.new("Lit")
    mat.use_nodes = True
    mat.use_backface_culling = False
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = nodes["Principled BSDF"]
    attr = nodes.new("ShaderNodeVertexColor")
    attr.layer_name = "Col"
    links.new(attr.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.85
    bsdf.inputs["Metallic"].default_value = 0.0
    return mat


def _make_glow(name, hex_color):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.use_backface_culling = False
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    rgb = C(hex_color)
    bsdf.inputs["Base Color"].default_value = (rgb[0] * 0.25, rgb[1] * 0.25, rgb[2] * 0.25, 1)
    bsdf.inputs["Emission Color"].default_value = (*rgb, 1)
    bsdf.inputs["Emission Strength"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.6
    return mat


def material(key):
    if key not in _materials:
        _materials[key] = _make_lit() if key == "lit" else _make_glow(
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


# ----------------------------------------------------------- mesh builder ---


class Mesh:
    """A bmesh that collects primitives, all painted with per-face vertex colors."""

    def __init__(self, name, mat_key="lit", ao=(0.0, 5.0, 0.7, 1.05), jitter=0.04, seed=1):
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
        for f in new:
            m = 1.0 + self.rng.uniform(-jit, jit)
            for loop in f.loops:
                k = m
                if grad:
                    z0, z1, dark, light = grad
                    t = clamp01((loop.vert.co.z - z0) / (z1 - z0))
                    k *= dark + (light - dark) * t
                loop[self.col] = (color[0] * k, color[1] * k, color[2] * k, 1.0)
        if base is not None:
            verts = list({v for f in new for v in f.verts})
            bmesh.ops.transform(bm, matrix=base, verts=verts)

    @staticmethod
    def _m(pos, rotation, extra=None):
        m = tr(*pos) @ rot(*rotation)
        return m if extra is None else m @ extra

    # -- primitives (pos = bottom centre unless noted) ------------------------
    def box(self, size, pos=(0, 0, 0), rotation=(0, 0, 0), color=None, grad=None,
            jitter=None, base=None, center=False):
        sx, sy, sz = size
        lift = 0.0 if center else sz / 2
        # rotate around `pos` (the bottom centre unless center=True)
        m = tr(*pos) @ rot(*rotation) @ tr(0, 0, lift) @ Matrix.Diagonal((sx, sy, sz, 1.0))
        res = bmesh.ops.create_cube(self.bm, size=1.0, matrix=m, calc_uvs=False)
        self._finish(self._faces_of(res["verts"]), color or P["metal"], grad, jitter, base)

    def cyl(self, r1, r2=None, h=1.0, pos=(0, 0, 0), rotation=(0, 0, 0), segs=8,
            color=None, grad=None, jitter=None, base=None, center=False, caps=True):
        r2 = r1 if r2 is None else r2
        lift = 0.0 if center else h / 2
        m = tr(*pos) @ rot(*rotation) @ tr(0, 0, lift)
        res = bmesh.ops.create_cone(self.bm, cap_ends=caps, cap_tris=False, segments=segs,
                                    radius1=r1, radius2=r2, depth=h, matrix=m, calc_uvs=False)
        self._finish(self._faces_of(res["verts"]), color or P["metal"], grad, jitter, base)

    def ball(self, r, pos=(0, 0, 0), subdiv=1, scale=(1, 1, 1), rotation=(0, 0, 0),
             color=None, grad=None, jitter=None, base=None, noise=0.0):
        m = tr(*pos) @ rot(*rotation) @ Matrix.Diagonal((*scale, 1.0))
        res = bmesh.ops.create_icosphere(self.bm, subdivisions=subdiv, radius=r, matrix=m,
                                         calc_uvs=False)
        if noise:
            centre = Vector(pos)
            for v in res["verts"]:
                v.co += (v.co - centre).normalized() * self.rng.uniform(-noise, noise) * r
        self._finish(self._faces_of(res["verts"]), color or P["rock"], grad, jitter, base)

    def lathe(self, profile, pos=(0, 0, 0), rotation=(0, 0, 0), segs=8, color=None,
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

    def torus(self, R, r, pos=(0, 0, 0), rotation=(0, 0, 0), major=16, minor=6, arc=360.0,
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
        last = major if full else major
        for i in range(major):
            i2 = (i + 1) % steps if full else i + 1
            for j in range(minor):
                j2 = (j + 1) % minor
                made.append(bm.faces.new((grid[i][j], grid[i2][j], grid[i2][j2], grid[i][j2])))
        self._finish(made, color or P["metal"], grad, jitter, base, fix_normals=full)

    def tube(self, a, b, r=0.08, segs=4, color=None, grad=None, jitter=None, base=None):
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
        self._finish(self._faces_of(res["verts"]), color or P["metal_dark"], grad, jitter, base)

    # -- output ------------------------------------------------------------------
    def to_object(self, parent=None, location=(0, 0, 0), name=None):
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
        return ob

    def free(self):
        self.bm.free()


class Group:
    """One lit mesh plus one mesh per glow colour; exported under a shared empty."""

    def __init__(self, name, ao=(0.0, 5.0, 0.7, 1.05), seed=1):
        self.name = name
        self.lit = Mesh(name + "_lit", "lit", ao=ao, seed=seed)
        self.glow = {}
        self._seed = seed
        self._ao = ao

    def g(self, key):
        if key not in self.glow:
            # glow parts are flat colour, no darkening
            self.glow[key] = Mesh(f"{self.name}_glow_{key}", key, ao=False, jitter=0.0,
                                  seed=self._seed)
        return self.glow[key]

    def build(self, location=(0, 0, 0)):
        root = bpy.data.objects.new(self.name, None)
        root.location = location
        bpy.context.scene.collection.objects.link(root)
        self.lit.to_object(parent=root)
        for key, mesh in self.glow.items():
            mesh.to_object(parent=root)
        self.lit.free()
        for mesh in self.glow.values():
            mesh.free()
        return root


def glow_color(key):
    return C(GLOW_COLORS[key])
