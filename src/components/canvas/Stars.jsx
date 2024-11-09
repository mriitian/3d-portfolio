import { useState, useRef, Suspense } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Points, PointMaterial, Preload } from "@react-three/drei";
import * as THREE from "three"; // Using Three.js for randomness and geometry

// Stars Component
const Stars = ({ count = 5000, color = "#f272c8", size = 0.002 }) => {
  const ref = useRef();

  // Generate random positions for the stars
  const positions = new Float32Array(count * 3); // 3 values for each point (x, y, z)
  for (let i = 0; i < count; i++) {
    const [x, y, z] = new THREE.Vector3()
      .randomDirection()
      .multiplyScalar(1.2)
      .toArray();
    positions.set([x, y, z], i * 3);
  }

  useFrame((state, delta) => {
    ref.current.rotation.x -= delta / 10;
    ref.current.rotation.y -= delta / 15;
  });

  return (
    <group rotation={[0, 0, Math.PI / 4]}>
      <Points ref={ref} positions={positions} stride={3}>
        <PointMaterial
          transparent
          color={color}
          size={size}
          sizeAttenuation={true}
          depthWrite={false}
        />
      </Points>
    </group>
  );
};

// Stars Canvas
const StarsCanvas = () => (
  <div className="w-full h-full absolute inset-0 z-[-1]">
    <Canvas camera={{ position: [0, 0, 0.1] }}>
      <Suspense fallback={<div>Loading stars...</div>}>
        <Stars count={5000} color="#f272c8" size={0.002} />
      </Suspense>
      <Preload all />
    </Canvas>
  </div>
);

export default StarsCanvas;
