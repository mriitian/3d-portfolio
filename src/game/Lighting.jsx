import React, { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Environment } from "@react-three/drei";
import { Euler, Matrix4, Vector3 } from "three";
import { game } from "./state";
import { SkyMaterial } from "./Sky";

// Where the light comes from, in the rover's frame (right, up, forward). It is deliberately
// not the sun drawn in the sky: lighting from the side and slightly behind keeps the rover
// and the landmarks facing the camera readable, while the sunset stays ahead.
const LIGHT_RIGHT = 0.55;
const LIGHT_UP = 0.7;
const LIGHT_FWD = -0.3;

const dir = new Vector3();
const back = new Vector3();
const basis = new Matrix4();
const euler = new Euler();

// Golden-hour lighting that stays put relative to the rover: a warm low sun with real
// shadows around the rover, plus sky-coloured fill and reflections that turn with it.
const Lighting = () => {
  const light = useRef();
  const target = useMemo(() => new Vector3(), []);

  useFrame(({ scene }) => {
    dir
      .set(0, 0, 0)
      .addScaledVector(game.right, LIGHT_RIGHT)
      .addScaledVector(game.up, LIGHT_UP)
      .addScaledVector(game.fwd, LIGHT_FWD)
      .normalize();
    light.current.position.copy(game.pos).addScaledVector(dir, 90);
    target.copy(game.pos);
    light.current.target.position.copy(target);
    light.current.target.updateMatrixWorld();

    // keep the reflection map aligned with the sky above the rover
    back.copy(game.fwd).negate();
    basis.makeBasis(game.right, game.up, back);
    scene.environmentRotation.copy(euler.setFromRotationMatrix(basis));
  });

  return (
    <>
      <directionalLight
        ref={light}
        castShadow
        color="#a9c2ff"
        intensity={3.6}
        shadow-mapSize={[2048, 2048]}
        shadow-camera-left={-36}
        shadow-camera-right={36}
        shadow-camera-top={36}
        shadow-camera-bottom={-36}
        shadow-camera-near={1}
        shadow-camera-far={220}
        shadow-bias={-0.0006}
        shadow-normalBias={0.06}
      />
      <hemisphereLight args={["#5a72e0", "#2a2766", 1.7]} />
      <ambientLight intensity={0.5} color="#7f8ee8" />
      <Environment resolution={128} frames={1}>
        <mesh>
          <sphereGeometry args={[100, 32, 24]} />
          <SkyMaterial />
        </mesh>
      </Environment>
    </>
  );
};

export default Lighting;
