import React, { useMemo, useRef } from "react";
import { Html, useGLTF } from "@react-three/drei";
import { useFrame } from "@react-three/fiber";
import { Quaternion, Vector3 } from "three";
import { R, SHARDS, ZONES } from "./zones";
import { game } from "./state";
import { WORLD_URL } from "./Planet";
import { prepare } from "./materials";

// how high above each landmark its name tag floats
const LABEL_HEIGHT = { about: 15.5, projects: 12.5, skills: 11.5, experience: 10, contact: 11.5 };

// Each landmark is a node in the Blender export, modelled around the origin with +Y up.
const Zone = ({ zone, planetRef }) => {
  const { nodes } = useGLTF(WORLD_URL);
  const model = useMemo(
    () => prepare(nodes[`Zone_${zone.id}`].clone(true)),
    [nodes, zone.id]
  );
  const rotation = useMemo(
    () => new Quaternion().setFromUnitVectors(new Vector3(0, 1, 0), zone.dir),
    [zone]
  );

  return (
    <group quaternion={rotation}>
      <group position={[0, R, 0]}>
        <primitive object={model} />
        <Html
          position={[0, LABEL_HEIGHT[zone.id], 0]}
          center
          occlude={[planetRef]}
          zIndexRange={[10, 0]}
        >
          <div
            className="pointer-events-none select-none whitespace-nowrap rounded-xl border bg-black/65 px-3 py-1.5 text-white backdrop-blur-sm"
            style={{ borderColor: zone.color }}
          >
            <span className="text-[11px] opacity-70">0{zone.index}</span>{" "}
            <span className="text-[14px] font-bold">{zone.title}</span>
            <div className="text-[11px] opacity-70">{zone.place}</div>
          </div>
        </Html>
      </group>
    </group>
  );
};

export const Zones = ({ planetRef }) => (
  <>
    {ZONES.map((zone) => (
      <Zone key={zone.id} zone={zone} planetRef={planetRef} />
    ))}
  </>
);

export const Shards = () => {
  const refs = useRef([]);

  useFrame((state) => {
    const t = state.clock.elapsedTime;
    refs.current.forEach((mesh, i) => {
      if (!mesh) return;
      mesh.visible = !game.collected.has(i);
      mesh.rotation.y = t * 1.5 + i;
      mesh.position.y = R + 1.7 + Math.sin(t * 2 + i) * 0.14;
    });
  });

  return (
    <>
      {SHARDS.map((dir, i) => {
        // park each shard on the planet's surface, then bob it along the local "up"
        const quaternion = new Quaternion().setFromUnitVectors(new Vector3(0, 1, 0), dir);
        return (
          <group key={i} quaternion={quaternion}>
            <mesh ref={(el) => (refs.current[i] = el)} position={[0, R + 1.7, 0]}>
              <octahedronGeometry args={[0.6, 1]} />
              <meshStandardMaterial
                color="#ffd166"
                emissive="#ffb703"
                emissiveIntensity={2.4}
                toneMapped={false}
                roughness={0.3}
              />
            </mesh>
          </group>
        );
      })}
    </>
  );
};
