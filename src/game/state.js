import { Vector3 } from "three";
import { R, SPAWN_DIR } from "./zones";

// Mutable game state shared between the 3D scene and the HUD. It changes every
// frame, so it lives outside React and the HUD reads it directly.
export const game = {
  pos: new Vector3(),
  fwd: new Vector3(),
  speed: 0,
  paused: false,
  snapCamera: true,
  keys: new Set(),
  collected: new Set(),
};

export const resetGame = () => {
  game.pos.copy(SPAWN_DIR).multiplyScalar(R);
  game.fwd.set(0, 0, 1);
  game.speed = 0;
  game.paused = false;
  game.snapCamera = true;
  game.keys.clear();
  game.collected.clear();
};

const side = new Vector3();
const up = new Vector3();

// put the rover a short way from a zone, facing it
export const teleportTo = (zone) => {
  const dir = zone.dir;

  side.set(0, 1, 0).cross(dir);
  if (side.lengthSq() < 1e-4) side.set(1, 0, 0).cross(dir);
  side.normalize();

  const angle = 10 / R;
  game.pos
    .copy(dir)
    .multiplyScalar(Math.cos(angle))
    .addScaledVector(side, Math.sin(angle))
    .normalize()
    .multiplyScalar(R);

  up.copy(game.pos).normalize();
  game.fwd.copy(dir).addScaledVector(up, -dir.dot(up)).normalize();
  game.speed = 0;
  game.snapCamera = true;
};
