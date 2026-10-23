import React, { useMemo } from "react";
import { Html } from "@react-three/drei";
import { Quaternion, Vector3 } from "three";
import { R, SHARDS, ZONES, ZONE_RADIUS } from "./zones";
import { game } from "./state";
import { useFrame } from "@react-three/fiber";

const grey = "#9ea3b8";
const dark = "#5c6078";

const Part = ({ position, rotation, children, color = grey }) => (
  <mesh position={position} rotation={rotation}>
    {children}
    <meshStandardMaterial color={color} flatShading />
  </mesh>
);

// Greybox landmarks: simple primitives that stand in for the final art.
// Each is built around local +y, which points away from the planet.
const Launchpad = ({ color }) => (
  <>
    <Part position={[0, 0.2, 0]} color={dark}>
      <cylinderGeometry args={[2.6, 2.8, 0.4, 12]} />
    </Part>
    <Part position={[0, 3.2, 0]}>
      <cylinderGeometry args={[0.9, 0.9, 5.6, 10]} />
    </Part>
    <Part position={[0, 6.9, 0]} color={color}>
      <coneGeometry args={[0.9, 1.9, 10]} />
    </Part>
    <Part position={[-1.1, 1.2, 0]} color={dark}>
      <boxGeometry args={[0.2, 2, 1.2]} />
    </Part>
    <Part position={[1.1, 1.2, 0]} color={dark}>
      <boxGeometry args={[0.2, 2, 1.2]} />
    </Part>
    <Part position={[3.6, 3, 0]} color={dark}>
      <boxGeometry args={[0.8, 6, 0.8]} />
    </Part>
  </>
);

const CreativeDistrict = ({ color }) => (
  <>
    <Part position={[0, 0.15, 0]} color={dark}>
      <cylinderGeometry args={[5, 5.2, 0.3, 14]} />
    </Part>
    {[-3.4, 0, 3.4].map((x, i) => (
      <group key={x} position={[x, 2.4, i === 1 ? -1 : 0.6]} rotation={[0, (i - 1) * 0.5, 0]}>
        <mesh>
          <torusGeometry args={[1.9 + (i === 1 ? 0.5 : 0), 0.22, 8, 24]} />
          <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.7} flatShading />
        </mesh>
        <mesh>
          <circleGeometry args={[1.7 + (i === 1 ? 0.5 : 0), 24]} />
          <meshBasicMaterial color={color} transparent opacity={0.18} />
        </mesh>
      </group>
    ))}
  </>
);

const Observatory = ({ color }) => (
  <>
    <Part position={[0, 0.9, 0]} color={dark}>
      <cylinderGeometry args={[3, 3.2, 1.8, 12]} />
    </Part>
    <Part position={[0, 1.8, 0]}>
      <sphereGeometry args={[2.8, 12, 8, 0, Math.PI * 2, 0, Math.PI / 2]} />
    </Part>
    <Part position={[0.9, 3.5, 0.4]} color={dark}>
      <boxGeometry args={[0.5, 1.6, 2.2]} />
    </Part>
    {[0, 1, 2, 3, 4, 5].map((i) => {
      const a = (i / 6) * Math.PI * 2;
      return (
        <mesh key={i} position={[Math.cos(a) * 4.6, 4 + (i % 3) * 1.1, Math.sin(a) * 4.6]}>
          <octahedronGeometry args={[0.32, 0]} />
          <meshStandardMaterial color={color} emissive={color} emissiveIntensity={1} flatShading />
        </mesh>
      );
    })}
  </>
);

const SpaceStation = ({ color }) => (
  <>
    <Part position={[0, 1.6, 0]}>
      <cylinderGeometry args={[1.2, 1.4, 3.2, 10]} />
    </Part>
    <mesh position={[0, 4.4, 0]} rotation={[Math.PI / 2, 0, 0]}>
      <torusGeometry args={[3.6, 0.38, 6, 18]} />
      <meshStandardMaterial color={color} flatShading />
    </mesh>
    <Part position={[0, 4.4, 0]}>
      <cylinderGeometry args={[0.9, 0.9, 1.2, 8]} />
    </Part>
    <Part position={[-5.4, 4.4, 0]} color={dark}>
      <boxGeometry args={[3, 0.12, 1.6]} />
    </Part>
    <Part position={[5.4, 4.4, 0]} color={dark}>
      <boxGeometry args={[3, 0.12, 1.6]} />
    </Part>
  </>
);

const CommHub = ({ color }) => (
  <>
    <Part position={[0, 0.6, 0]} color={dark}>
      <boxGeometry args={[3.4, 1.2, 3.4]} />
    </Part>
    <Part position={[0, 2.4, 0]}>
      <cylinderGeometry args={[0.28, 0.28, 3.2, 8]} />
    </Part>
    <group position={[0, 4.2, 0]} rotation={[0.5, 0.6, 0]}>
      <mesh>
        <coneGeometry args={[2.2, 1.1, 20, 1, true]} />
        <meshStandardMaterial color={grey} flatShading side={2} />
      </mesh>
      <mesh position={[0, 0.7, 0]}>
        <sphereGeometry args={[0.25, 8, 6]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={1} />
      </mesh>
    </group>
  </>
);

const LANDMARKS = {
  about: Launchpad,
  projects: CreativeDistrict,
  skills: Observatory,
  experience: SpaceStation,
  contact: CommHub,
};

const Zone = ({ zone, planetRef }) => {
  const rotation = useMemo(
    () => new Quaternion().setFromUnitVectors(new Vector3(0, 1, 0), zone.dir),
    [zone]
  );
  const Landmark = LANDMARKS[zone.id];
  const inner = (ZONE_RADIUS - 0.7) / R;
  const outer = ZONE_RADIUS / R;

  return (
    <group quaternion={rotation}>
      {/* glowing ground ring that follows the planet's curvature */}
      <mesh>
        <sphereGeometry args={[R + 0.08, 48, 1, 0, Math.PI * 2, inner, outer - inner]} />
        <meshBasicMaterial color={zone.color} transparent opacity={0.55} />
      </mesh>

      <group position={[0, R, 0]}>
        <Landmark color={zone.color} />
        <Html position={[0, 9.5, 0]} center occlude={[planetRef]} zIndexRange={[10, 0]}>
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
  const refs = React.useRef([]);

  useFrame((state) => {
    const t = state.clock.elapsedTime;
    refs.current.forEach((mesh, i) => {
      if (!mesh) return;
      mesh.visible = !game.collected.has(i);
      mesh.rotation.y = t * 1.5 + i;
    });
  });

  return (
    <>
      {SHARDS.map((dir, i) => (
        <mesh
          key={i}
          ref={(el) => (refs.current[i] = el)}
          position={dir.clone().multiplyScalar(R + 1.3)}
        >
          <octahedronGeometry args={[0.55, 0]} />
          <meshStandardMaterial color="#ffd166" emissive="#ffb703" emissiveIntensity={1.2} flatShading />
        </mesh>
      ))}
    </>
  );
};
