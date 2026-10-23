import React, { useCallback, useEffect, useRef, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { AnimatePresence } from "framer-motion";
import { game, resetGame, teleportTo } from "../game/state";
import Planet from "../game/Planet";
import Rover from "../game/Rover";
import { Shards, Zones } from "../game/Landmarks";
import Hud from "../game/Hud";
import ZoneCard from "../game/ZoneCard";

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
        dpr={[1, 1.5]}
        camera={{ fov: 55, near: 0.1, far: 500, position: [46, 6, -10] }}
      >
        <color attach="background" args={["#050816"]} />
        <ambientLight intensity={0.55} />
        <hemisphereLight args={["#9ab0ff", "#3a2250", 0.9]} />
        <directionalLight position={[80, 90, 50]} intensity={2.2} />

        <Planet ref={planetRef} />
        <Zones planetRef={planetRef} />
        <Shards />
        <Rover onNear={handleNear} onShard={setShards} />
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
