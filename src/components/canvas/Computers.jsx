import { OrbitControls, Preload } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import { useGLTF } from "@react-three/drei";
import React, { Suspense, useEffect, useState } from "react";
import CanvasLoader from "../Loader";
import useMediaQuery from "../../hooks/useMediaQuery";

const MODEL_URL = "./pc3/pc.glb";

// start fetching the model right away, but only where the canvas is shown
if (window.matchMedia("(min-width: 640px)").matches) {
  useGLTF.preload(MODEL_URL);
}

const Computers = ({ isMobile }) => {
  const computer = useGLTF(MODEL_URL);

  return (
    <mesh>
      <hemisphereLight intensity={0.5} groundColor="black" />
      <pointLight intensity={0.5} />
      <spotLight
        position={[-12, 5, 1]}
        angle={1}
        penumbra={1}
        intensity={500}
        castShadow
        shadow-mapSize={1024}
      />
      <primitive
        object={computer.scene}
        scale={isMobile ? 0.5 : 0.75}
        position={isMobile ? [1, -2.5, 0] : [0, -3.5, -1.5]}
        rotation={[-0.01, -0.2, -0.1]}
      />
    </mesh>
  );
};

const ComputerCanvas = () => {
  const [isMobile, setIsMobile] = useState(false);
  useEffect(() => {
    const mediaQuery = window.matchMedia("(max-width: 500px)");
    setIsMobile(mediaQuery.matches);

    const handleMediaQueryChange = (e) => {
      setIsMobile(e.matches);
    };

    mediaQuery.addEventListener("change", handleMediaQueryChange);

    return () => {
      mediaQuery.removeEventListener("change", handleMediaQueryChange);
    };
  }, []);

  const showCanvas = useMediaQuery("(min-width: 640px)");
  if (!showCanvas) return null;

  return (
    <Canvas
      frameloop="demand"
      shadows
      camera={{ position: [20, 3, 5], fov: 25 }}
      gl={{ preserveDrawingBuffer: true }}
    >
      <Suspense fallback={<CanvasLoader radius={1.3} />}>
        <OrbitControls
          enableZoom={false}
          maxPolarAngle={Math.PI / 2}
          minPolarAngle={Math.PI / 2}
        />
        <Computers isMobile={isMobile} />
      </Suspense>

      <Preload all />
    </Canvas>
  );
};

export default ComputerCanvas;
