# Orbital Playground art

The 3D world is generated procedurally with Blender's Python API, so every model can be
tweaked in code and re-exported. Style: flat-shaded low poly, per-face vertex colors
(no textures), and a few emissive "glow" materials. Palette matches the site.

| File | What it builds |
|---|---|
| `blender_lib.py` | palette, materials and the vertex-colored primitive builder |
| `world_planet.py` | planet ground (painted road, plazas, craters), trees/rocks/crystals/lamps, moon, floating rocks |
| `world_zones.py` | the five landmarks: Launchpad, Creative District, Observatory, Space Station, Comm Hub |
| `world_rover.py` | the rover (wheels are separate nodes so the game can spin them) |
| `build_world.py` | entry point: builds, previews and exports |
| `preview.py` | headless preview renders |

## Rebuild and export

Needs Blender 4.4 (adjust the path) and Node (for `gltf-transform`).

```bash
BLENDER="/c/Program Files/Blender Foundation/Blender 4.4/blender.exe"

# build everything into a temp folder
"$BLENDER" -b -P art/build_world.py -- --only all --out art/_out

# compress the world (meshopt keeps node names); the rover is small enough to ship as-is
npx @gltf-transform/cli meshopt art/_out/world.glb public/game/world.glb --level high
cp art/_out/rover.glb public/game/rover.glb
```

Add `--preview <folder>` to also render PNG previews, and `--only planet|zones|rover`
to build a single part.

## Keep in sync with the game

- `ZONE_DEFS` in `world_planet.py` must match `src/game/zones.js` (latitude/longitude).
- The planet radius `R = 40` must match `R` in `src/game/zones.js`; the rover drives on a
  perfect sphere of that radius.
- Zone nodes are named `Zone_<id>` and the rover wheels `wheel_FL/FR/RL/RR`; the game
  looks them up by name.
