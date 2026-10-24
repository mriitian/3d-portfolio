import React, { forwardRef, useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { useGLTF } from "@react-three/drei";
import { prepare } from "./materials";

export const WORLD_URL = "/game/world.glb";

// start downloading as soon as this chunk loads
useGLTF.preload(WORLD_URL);

// where the floating islands hang: x, y, z, which of the modelled variants, size
const ISLANDS = [
  [-58, 30, 20, 0, 1.0],
  [50, 42, -30, 1, 0.9],
  [-30, -55, 40, 2, 1.1],
  [62, -20, 38, 3, 0.8],
  [10, 66, 36, 1, 1.0],
  [-66, -8, -30, 2, 0.9],
];

// Planet, props, moon and floating islands come from the Blender export
// (art/build_world.py). Nodes are wrapped in groups so their own transforms stay intact.
const Planet = forwardRef(function Planet(_, ref) {
  const { nodes } = useGLTF(WORLD_URL);
  const moon = useRef();
  const islands = useRef();

  const scatter = useMemo(
    () => Object.keys(nodes).filter((name) => name.startsWith("Scatter_") && !name.includes("_lit") && !name.includes("_glow") && !name.includes("_paint") && !name.includes("_metal")),
    [nodes]
  );

  useMemo(() => {
    prepare(nodes.Planet, { cast: false });
    prepare(nodes.Road, { cast: false });
    scatter.forEach((name) => prepare(nodes[name]));
    prepare(nodes.Moon, { cast: false });
    for (let i = 0; i < 4; i++) prepare(nodes[`FloatRock_${i}`]);
  }, [nodes, scatter]);

  useFrame((_, delta) => {
    moon.current.rotation.y += delta * 0.05;
    islands.current.rotation.y += delta * 0.01;
  });

  return (
    <>
      <primitive ref={ref} object={nodes.Planet} />
      <primitive object={nodes.Road} />
      {scatter.map((name) => (
        <primitive key={name} object={nodes[name]} />
      ))}

      <group ref={moon}>
        <group position={[110, 20, 0]}>
          <primitive object={nodes.Moon} />
        </group>
      </group>

      <group ref={islands}>
        {ISLANDS.map(([x, y, z, variant, size]) => (
          <group key={`${x}-${y}-${z}`} position={[x, y, z]} scale={size}>
            <primitive object={nodes[`FloatRock_${variant}`].clone(true)} />
          </group>
        ))}
      </group>
    </>
  );
});

export default Planet;
