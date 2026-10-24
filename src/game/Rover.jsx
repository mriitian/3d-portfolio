import React, { useEffect, useMemo, useRef } from "react";
import { useGLTF } from "@react-three/drei";
import { useFrame, useThree } from "@react-three/fiber";
import { Matrix4, Vector3 } from "three";
import { game } from "./state";
import { prepare } from "./materials";
import { R, SHARDS, ZONES, ZONE_RADIUS } from "./zones";
import obstacleData from "./obstacles.json";

const MAX_SPEED = 14;
const BOOST_SPEED = 26;
const REVERSE_SPEED = 6;
const GROUND_OFFSET = 0.04; // the model's wheels already touch y = 0
const WHEEL_RADIUS = 0.55;
const ROVER_URL = "/game/rover.glb";
const ROVER_RADIUS = 1.45; // the rover is treated as a circle for collisions

// Trees, rocks, lamps and the solid parts of each landmark: [x, y, z, radius] on the planet
// (exported by art/build_world.py). Each is a circle on the surface the rover can't enter.
const OBSTACLES = obstacleData.map(([x, y, z, r]) => ({
  dir: new Vector3(x, y, z).normalize(),
  reach: r + ROVER_RADIUS,
  cosReach: Math.cos((r + ROVER_RADIUS) / R),
}));

useGLTF.preload(ROVER_URL);

const up = new Vector3();
const push = new Vector3();
const axis = new Vector3();
const right = new Vector3();
const back = new Vector3();
const roverWorld = new Vector3();
const camTarget = new Vector3();
const lookTarget = new Vector3();
const camUp = new Vector3(0, 1, 0);
const basis = new Matrix4();

const isDown = (...codes) => codes.some((code) => game.keys.has(code));

const Rover = ({ onNear, onShard }) => {
  const camera = useThree((state) => state.camera);
  const rover = useRef();
  const lastNear = useRef(null);
  const { scene } = useGLTF(ROVER_URL);
  const model = useMemo(() => prepare(scene.clone(true)), [scene]);
  const wheels = useMemo(
    () =>
      ["wheel_FL", "wheel_FR", "wheel_RL", "wheel_RR"]
        .map((name) => model.getObjectByName(name))
        .filter(Boolean),
    [model]
  );

  useEffect(() => {
    const prevent = ["Space", "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"];
    const onDown = (e) => {
      if (prevent.includes(e.code)) e.preventDefault();
      game.keys.add(e.code);
    };
    const onUp = (e) => game.keys.delete(e.code);
    const onBlur = () => game.keys.clear();

    window.addEventListener("keydown", onDown);
    window.addEventListener("keyup", onUp);
    window.addEventListener("blur", onBlur);
    return () => {
      window.removeEventListener("keydown", onDown);
      window.removeEventListener("keyup", onUp);
      window.removeEventListener("blur", onBlur);
    };
  }, []);

  useFrame((_, rawDelta) => {
    const dt = Math.min(rawDelta, 0.05);
    const active = !game.paused;

    const throttle = active
      ? (isDown("KeyW", "ArrowUp") ? 1 : 0) - (isDown("KeyS", "ArrowDown") ? 1 : 0)
      : 0;
    const steer = active
      ? (isDown("KeyA", "ArrowLeft") ? 1 : 0) - (isDown("KeyD", "ArrowRight") ? 1 : 0)
      : 0;
    const top = active && isDown("Space") ? BOOST_SPEED : MAX_SPEED;

    // speed
    if (throttle > 0) {
      game.speed = Math.min(top, game.speed + 20 * dt);
    } else if (throttle < 0) {
      game.speed = Math.max(-REVERSE_SPEED, game.speed - 16 * dt);
    } else {
      game.speed *= Math.exp(-1.8 * dt);
    }
    if (game.speed > top) game.speed -= 30 * dt; // ease back after a boost

    // steer around the local up axis, only while moving
    up.copy(game.pos).normalize();
    const turn = steer * 1.9 * Math.min(1, Math.abs(game.speed) / 5);
    game.fwd.applyAxisAngle(up, turn * dt);

    // drive: rotate the position (and heading) around the planet centre
    axis.crossVectors(up, game.fwd).normalize();
    const angle = (game.speed * dt) / R;
    game.pos.applyAxisAngle(axis, angle);
    game.fwd.applyAxisAngle(axis, angle);

    // collisions: slide along anything solid instead of driving through it
    up.copy(game.pos).normalize();
    let hit = false;
    for (const o of OBSTACLES) {
      const c = up.dot(o.dir);
      if (c < o.cosReach) continue;
      push.copy(up).addScaledVector(o.dir, -c); // points away from the obstacle
      if (push.lengthSq() < 1e-9) continue;
      push.normalize();
      const a = o.reach / R;
      up.copy(o.dir).multiplyScalar(Math.cos(a)).addScaledVector(push, Math.sin(a));
      // only the part of the motion that heads into the obstacle is lost
      const into = Math.max(0, -game.fwd.dot(push) * Math.sign(game.speed));
      game.speed *= 1 - 0.85 * into;
      hit = true;
    }
    if (hit) game.pos.copy(up).multiplyScalar(R);

    // keep the heading tangent to the surface and the position on the sphere
    up.copy(game.pos).normalize();
    game.fwd.addScaledVector(up, -game.fwd.dot(up)).normalize();
    game.pos.copy(up).multiplyScalar(R);

    // place and orient the rover model
    roverWorld.copy(up).multiplyScalar(R + GROUND_OFFSET);
    back.copy(game.fwd).negate();
    right.crossVectors(up, back);
    basis.makeBasis(right, up, back);
    rover.current.position.copy(roverWorld);
    rover.current.quaternion.setFromRotationMatrix(basis);
    game.up.copy(up);
    game.right.copy(right);
    wheels.forEach((wheel) => {
      wheel.rotation.x -= (game.speed * dt) / WHEEL_RADIUS;
    });

    // chase camera
    camTarget.copy(roverWorld).addScaledVector(up, 6.2).addScaledVector(game.fwd, -12.5);
    if (game.snapCamera) {
      camera.position.copy(camTarget);
      camUp.copy(up);
      game.snapCamera = false;
    } else {
      const follow = 1 - Math.exp(-5 * dt);
      camera.position.lerp(camTarget, follow);
      camUp.lerp(up, follow).normalize();
    }
    camera.up.copy(camUp);
    lookTarget.copy(roverWorld).addScaledVector(game.fwd, 3.5).addScaledVector(up, 1.6);
    camera.lookAt(lookTarget);

    // zone proximity
    let near = null;
    for (const zone of ZONES) {
      const arc = R * Math.acos(Math.min(1, up.dot(zone.dir)));
      if (arc < ZONE_RADIUS) near = zone;
    }
    if (near !== lastNear.current) {
      lastNear.current = near;
      onNear(near);
    }

    // shard pickup
    for (let i = 0; i < SHARDS.length; i++) {
      if (game.collected.has(i)) continue;
      const arc = R * Math.acos(Math.min(1, up.dot(SHARDS[i])));
      if (arc < 2.8) {
        game.collected.add(i);
        onShard(game.collected.size);
      }
    }
  });

  return (
    <group ref={rover}>
      <primitive object={model} />
    </group>
  );
};

export default Rover;
