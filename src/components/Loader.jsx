import React, { useEffect, useRef } from "react";
import { Billboard, useProgress } from "@react-three/drei";
import { useFrame, useThree } from "@react-three/fiber";

// In-scene loader: a ring that fills with the load progress around a
// spinning wireframe core. Lives inside the canvas, so it needs no DOM overlay.
const CanvasLoader = ({ radius = 2 }) => {
  const { progress } = useProgress();
  const invalidate = useThree((state) => state.invalidate);
  const core = useRef();

  // keep rendering while loading, even when the canvas uses frameloop="demand"
  useEffect(() => {
    let id;
    const tick = () => {
      invalidate();
      id = requestAnimationFrame(tick);
    };
    tick();
    return () => cancelAnimationFrame(id);
  }, [invalidate]);

  useFrame((_, delta) => {
    core.current.rotation.x += delta * 0.9;
    core.current.rotation.y += delta * 1.3;
  });

  const arc = Math.max(progress / 100, 0.03) * Math.PI * 2;
  const tube = radius * 0.022;

  return (
    <Billboard>
      <mesh>
        <torusGeometry args={[radius, tube * 0.5, 8, 96]} />
        <meshBasicMaterial color="#3b2a6e" toneMapped={false} />
      </mesh>
      <mesh rotation={[0, 0, Math.PI / 2]}>
        <torusGeometry args={[radius, tube, 12, 96, arc]} />
        <meshBasicMaterial color="#915eff" toneMapped={false} />
      </mesh>
      <mesh ref={core} scale={radius * 0.45}>
        <icosahedronGeometry args={[1, 0]} />
        <meshBasicMaterial color="#bf9bff" wireframe toneMapped={false} />
      </mesh>
    </Billboard>
  );
};

export default CanvasLoader;
