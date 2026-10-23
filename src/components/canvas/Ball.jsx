import React, { Suspense, useEffect, useMemo, useRef, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { Decal, Float, Preload, useTexture } from "@react-three/drei";
import CanvasLoader from "../Loader";

// grid sizes in CSS px, matching the tailwind breakpoint used by the site (sm = 640px)
const LAYOUTS = {
  desktop: { size: 112, gapX: 40, gapY: 40 },
  mobile: { size: 96, gapX: 16, gapY: 8 },
};

// centred, wrapping grid: returns the container height and each ball's top-left corner
const computeLayout = (width, count) => {
  const { size, gapX, gapY } =
    window.innerWidth >= 640 ? LAYOUTS.desktop : LAYOUTS.mobile;
  const cols = Math.max(1, Math.floor((width + gapX) / (size + gapX)));
  const rows = Math.ceil(count / cols);
  const positions = [];

  for (let i = 0; i < count; i++) {
    const row = Math.floor(i / cols);
    const inRow = Math.min(cols, count - row * cols);
    const rowWidth = inRow * size + (inRow - 1) * gapX;
    const x = (width - rowWidth) / 2 + (i % cols) * (size + gapX);
    positions.push([x, row * (size + gapY)]);
  }

  return { size, positions, height: rows * size + (rows - 1) * gapY };
};

const Ball = ({ imgUrl, position, radius }) => {
  const [decal] = useTexture([imgUrl]);
  const spin = useRef();
  const drag = useRef(null);

  const onPointerDown = (e) => {
    e.stopPropagation();
    e.target.setPointerCapture(e.pointerId);
    drag.current = { x: e.clientX, y: e.clientY };
  };

  const onPointerMove = (e) => {
    if (!drag.current) return;
    spin.current.rotation.y += (e.clientX - drag.current.x) * 0.01;
    spin.current.rotation.x += (e.clientY - drag.current.y) * 0.01;
    drag.current = { x: e.clientX, y: e.clientY };
  };

  const onPointerUp = () => {
    drag.current = null;
  };

  return (
    <group position={position} scale={radius}>
      <Float speed={1.75} rotationIntensity={1} floatIntensity={2}>
        <group ref={spin}>
          <mesh
            castShadow
            receiveShadow
            onPointerDown={onPointerDown}
            onPointerMove={onPointerMove}
            onPointerUp={onPointerUp}
            onPointerOver={() => (document.body.style.cursor = "grab")}
            onPointerOut={() => (document.body.style.cursor = "")}
          >
            <icosahedronGeometry args={[1, 1]} />
            <meshStandardMaterial
              color="#fff8eb"
              polygonOffset
              polygonOffsetFactor={-5}
              flatShading
            />
            <Decal
              map={decal}
              position={[0, 0, 1]}
              rotation={[2 * Math.PI, 0, 6.25]}
              flatShading
            />
          </mesh>
        </group>
      </Float>
    </group>
  );
};

// One canvas for every tech ball (instead of one WebGL context each). It only
// mounts once scrolled near and only renders while on screen.
const BallsCanvas = ({ icons }) => {
  const containerRef = useRef();
  const [width, setWidth] = useState(0);
  const [visible, setVisible] = useState(false);
  const [seen, setSeen] = useState(false);

  useEffect(() => {
    const el = containerRef.current;

    const resize = new ResizeObserver(([entry]) =>
      setWidth(entry.contentRect.width)
    );
    const intersect = new IntersectionObserver(
      ([entry]) => {
        setVisible(entry.isIntersecting);
        if (entry.isIntersecting) setSeen(true);
      },
      { rootMargin: "200px" }
    );

    resize.observe(el);
    intersect.observe(el);
    return () => {
      resize.disconnect();
      intersect.disconnect();
    };
  }, []);

  const layout = useMemo(
    () => (width ? computeLayout(width, icons.length) : null),
    [width, icons.length]
  );

  return (
    <div
      ref={containerRef}
      className="relative w-full"
      style={{ height: layout ? layout.height : 0 }}
    >
      {seen && layout && (
        <Canvas
          orthographic
          camera={{ zoom: 1, position: [0, 0, 100] }}
          frameloop={visible ? "always" : "never"}
          dpr={[1, 2]}
          style={{ position: "absolute", inset: 0, touchAction: "pan-y" }}
        >
          <ambientLight intensity={0.75} />
          <directionalLight position={[0, 0, 0.05]} />
          <Suspense fallback={<CanvasLoader radius={32} />}>
            {icons.map((icon, i) => (
              <Ball
                key={icon}
                imgUrl={icon}
                radius={layout.size * 0.36}
                position={[
                  layout.positions[i][0] - width / 2 + layout.size / 2,
                  layout.height / 2 - layout.positions[i][1] - layout.size / 2,
                  0,
                ]}
              />
            ))}
          </Suspense>
          <Preload all />
        </Canvas>
      )}
    </div>
  );
};

export default BallsCanvas;
