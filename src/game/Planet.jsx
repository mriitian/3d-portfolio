import React, { forwardRef, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Stars, useGLTF } from "@react-three/drei";

export const WORLD_URL = "/game/world.glb";

// start downloading as soon as this chunk loads
useGLTF.preload(WORLD_URL);

// where the floating rocks hang, and which of the three modelled variants each uses
const ROCKS = [
  [-58, 30, 20, 0, 1],
  [50, 42, -30, 1, 0.8],
  [-30, -55, 40, 2, 1.1],
  [62, -20, 38, 0, 0.7],
  [10, 66, 36, 1, 1],
  [-66, -8, -30, 2, 0.9],
];

// Planet, props, moon and floating rocks all come from the Blender export
// (art/build_world.py). Nodes are wrapped in groups so their own transforms stay intact.
const Planet = forwardRef(function Planet(_, ref) {
  const { nodes } = useGLTF(WORLD_URL);
  const moon = useRef();
  const rocks = useRef();

  useFrame((_, delta) => {
    moon.current.rotation.y += delta * 0.05;
    rocks.current.rotation.y += delta * 0.01;
  });

  return (
    <>
      <primitive ref={ref} object={nodes.Planet} />
      <primitive object={nodes.Scatter} />

      <group ref={moon}>
        <group position={[110, 20, 0]}>
          <primitive object={nodes.Moon} />
        </group>
      </group>

      <group ref={rocks}>
        {ROCKS.map(([x, y, z, variant, size]) => (
          <group key={`${x}-${y}-${z}`} position={[x, y, z]} scale={size}>
            <primitive object={nodes[`FloatRock_${variant}`].clone(true)} />
          </group>
        ))}
      </group>

      <Stars radius={180} depth={60} count={2500} factor={5} saturation={0} fade />
    </>
  );
});

export default Planet;
