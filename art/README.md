# Orbital Playground art

The 3D world is generated procedurally with Blender's Python API, so every model can be
tweaked in code and re-exported. Style: smooth, beveled stylised models painted with
per-vertex colours (no textures), soft ambient occlusion baked into those colours, and a few
emissive "glow" materials (the game adds bloom to them). Palette matches the site: warm
terracotta ground, sandstone buildings, orange/cyan/magenta/violet accents.

| File | What it builds |
|---|---|
| `blender_lib.py` | palette, materials, the vertex-coloured primitive builder, bevel/smooth, AO baking |
| `zone_common.py` | shared detail pieces: lamp posts, windows, railings, trusses, pipes, dishes |
| `zone_launchpad.py` | 01 About: rocket, boosters, gantry towers, fuel spheres, control building |
| `zone_projects.py` | 02 Projects: arcade studio, display wall, crane, neon gamepad sign |
| `zone_observatory.py` | 03 Skills: domed observatory with a glowing orb, holo panels, constellation |
| `zone_station.py` | 04 Experience: long glass-tube module on pylons, solar wings |
| `zone_commhub.py` | 05 Contact: sandstone hall, dish, tower, glowing mail sign |
| `world_planet.py` | the planet (painted terrain + road), props, moon, sky planet, floating islands |
| `world_rover.py` | the rover, its driver and four separate wheel nodes |
| `build_world.py` | entry point: builds, bakes AO, previews and exports |
| `preview.py` | headless preview renders |

## Rebuild and export

Needs Blender 4.4 (adjust the path) and Node (for `gltf-transform`).

```bash
BLENDER="/c/Program Files/Blender Foundation/Blender 4.4/blender.exe"

# build everything into a temp folder (about a minute)
"$BLENDER" -b -P art/build_world.py -- --only all --out art/_out --ao 16

# compress; meshopt keeps node names
npx @gltf-transform/cli meshopt art/_out/world.glb public/game/world.glb --level high
npx @gltf-transform/cli meshopt art/_out/rover.glb public/game/rover.glb --level high
```

Useful flags: `--preview <folder>` also renders PNG previews; `--only about|projects|skills|
experience|contact|planet|rover` builds one part; `--ao N` sets the occlusion ray count.

## Keep in sync with the game

- `ZONE_DEFS` in `world_planet.py` must match `src/game/zones.js` (latitude/longitude).
- The planet radius `R = 40` must match `R` in `src/game/zones.js`; the rover drives on a
  perfect sphere of that radius.
- Zone nodes are `Zone_<id>`, scatter chunks `Scatter_xp/xn/yp/yn/zp/zn`, floating islands
  `FloatRock_0..3`, wheels `wheel_FL/FR/RL/RR`. The game looks them up by name.
- Glow materials are named `Glow_<colour>`; `src/game/materials.js` boosts them for bloom.
