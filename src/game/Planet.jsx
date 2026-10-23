import React, { forwardRef, useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Stars } from "@react-three/drei";
import { BufferAttribute, Color, IcosahedronGeometry } from "three";
import { R } from "./zones";

// slightly different shade per face, so movement over the ground is readable
const createPlanetGeometry = () => {
  const geometry = new IcosahedronGeometry(R, 4);
  const count = geometry.attributes.position.count;
  const colors = new Float32Array(count * 3);
  const color = new Color();

  for (let face = 0; face < count; face += 3) {
    const noise = Math.abs(Math.sin(face * 12.9898) * 43758.5453) % 1;
    color.setHSL(0.68, 0.14, 0.4 + noise * 0.14);
    for (let corner = 0; corner < 3; corner++) {
      color.toArray(colors, (face + corner) * 3);
    }
  }

  geometry.setAttribute("color", new BufferAttribute(colors, 3));
  return geometry;
};

// a handful of floating rocks and a moon so the sky is not empty
const ROCKS = [
  [-58, 30, 20, 2.2],
  [50, 42, -30, 1.6],
  [-30, -55, 40, 2.6],
  [62, -20, 38, 1.4],
  [10, 66, 36, 2],
  [-66, -8, -30, 1.8],
];

const Planet = forwardRef(function Planet(_, ref) {
  const moon = useRef();
  const rocks = useRef();
  const geometry = useMemo(createPlanetGeometry, []);

  useFrame((_, delta) => {
    moon.current.rotation.y += delta * 0.05;
    rocks.current.rotation.y += delta * 0.01;
  });

  return (
    <>
      <mesh ref={ref} geometry={geometry}>
        <meshStandardMaterial vertexColors flatShading />
      </mesh>

      <group ref={moon}>
        <mesh position={[110, 20, 0]}>
          <icosahedronGeometry args={[6, 1]} />
          <meshStandardMaterial color="#b9bccb" flatShading />
        </mesh>
      </group>

      <group ref={rocks}>
        {ROCKS.map(([x, y, z, size]) => (
          <mesh key={`${x}-${y}-${z}`} position={[x, y, z]}>
            <dodecahedronGeometry args={[size, 0]} />
            <meshStandardMaterial color="#5f6378" flatShading />
          </mesh>
        ))}
      </group>

      <Stars radius={180} depth={60} count={2500} factor={5} saturation={0} fade />
    </>
  );
});

export default Planet;
