import React, { Suspense, useCallback, useEffect, useRef, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { Bloom, EffectComposer, ToneMapping, Vignette } from "@react-three/postprocessing";
import { ToneMappingMode } from "postprocessing";
import { AnimatePresence } from "framer-motion";
import { game, resetGame, teleportTo } from "../game/state";
import Planet from "../game/Planet";
import Rover from "../game/Rover";
import { Shards, Zones } from "../game/Landmarks";
import Hud from "../game/Hud";
import Lighting from "../game/Lighting";
import Sky from "../game/Sky";
import ZoneCard from "../game/ZoneCard";
import CanvasLoader from "../components/Loader";

const PlayGame = () => {
  const planetRef = useRef();
  const [near, setNear] = useState(null);
  const [open, setOpen] = useState(null);
  const [visited, setVisited] = useState([]);
  const [shards, setShards] = useState(0);

  const nearRef = useRef(null);
  const openRef = useRef(null);
  nearRef.current = near;
  openRef.current = open;

  useEffect(() => {
    resetGame();
  }, []);

  // the rover stands still while a card is open
  useEffect(() => {
    game.paused = open !== null;
  }, [open]);

  useEffect(() => {
    const onKey = (e) => {
      if (e.code === "KeyE" && nearRef.current && !openRef.current) {
        setOpen(nearRef.current);
      } else if (e.code === "Escape") {
        setOpen(null);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const handleNear = useCallback((zone) => {
    setNear(zone);
    if (zone) {
      setVisited((prev) => (prev.includes(zone.id) ? prev : [...prev, zone.id]));
    }
  }, []);

  const handleJump = useCallback((zone) => {
    teleportTo(zone);
    setOpen(null);
  }, []);

  return (
    <div className="fixed inset-0 bg-[#050816]">
      <Canvas
        shadows
        dpr={[1, 1.5]}
        camera={{ fov: 55, near: 0.1, far: 1800, position: [46, 6, -10] }}
        gl={{ antialias: false, powerPreference: "high-performance" }}
      >
        <color attach="background" args={["#2a1840"]} />
        <fog attach="fog" args={["#6b3f6e", 90, 380]} />

        <Suspense fallback={<CanvasLoader radius={6} />}>
          <Lighting />
          <Sky />
          <Planet ref={planetRef} />
          <Zones planetRef={planetRef} />
          <Shards />
          <Rover onNear={handleNear} onShard={setShards} />
        </Suspense>

        <EffectComposer multisampling={4}>
          <Bloom
            mipmapBlur
            intensity={0.85}
            luminanceThreshold={0.9}
            luminanceSmoothing={0.25}
          />
          <Vignette eskil={false} offset={0.25} darkness={0.55} />
          <ToneMapping mode={ToneMappingMode.ACES_FILMIC} />
        </EffectComposer>
      </Canvas>

      <Hud
        near={near}
        visited={visited}
        shards={shards}
        onInteract={setOpen}
        onJump={handleJump}
      />

      <AnimatePresence>
        {open && <ZoneCard key={open.id} zone={open} onClose={() => setOpen(null)} />}
      </AnimatePresence>
    </div>
  );
};

export default PlayGame;
