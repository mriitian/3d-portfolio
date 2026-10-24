import React, { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Stars, useGLTF } from "@react-three/drei";
import { BackSide, Color, Matrix4, Vector3 } from "three";
import { game } from "./state";
import { WORLD_URL } from "./Planet";
import { prepare } from "./materials";

// The sun's direction in the rover's own frame: x = right, y = up, -z = forward.
export const SUN_LOCAL = new Vector3(0.62, 0.5, -0.22).normalize();

const vertexShader = /* glsl */ `
  varying vec3 vDir;
  void main() {
    vDir = normalize(position);
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

const fragmentShader = /* glsl */ `
  uniform vec3 zenith;
  uniform vec3 mid;
  uniform vec3 horizon;
  uniform vec3 below;
  uniform vec3 sunDir;
  varying vec3 vDir;
  void main() {
    vec3 n = normalize(vDir);
    float y = n.y;
    vec3 col = mix(horizon, mid, smoothstep(0.0, 0.3, y));
    col = mix(col, zenith, smoothstep(0.22, 0.9, y));
    col = mix(col, below, smoothstep(0.0, -0.3, y));
    float s = max(dot(n, normalize(sunDir)), 0.0);
    col += vec3(1.0, 0.62, 0.32) * pow(s, 6.0) * 0.45;
    col += vec3(1.0, 0.75, 0.45) * pow(s, 40.0) * 0.9;
    col += vec3(1.0, 0.92, 0.75) * smoothstep(0.9993, 0.9998, s) * 4.0;
    gl_FragColor = vec4(col, 1.0);
    #include <colorspace_fragment>
  }
`;

export const createSkyUniforms = () => ({
  zenith: { value: new Color("#1d1450") },
  mid: { value: new Color("#b8447f") },
  horizon: { value: new Color("#ff9a4d") },
  below: { value: new Color("#2a1840") },
  sunDir: { value: SUN_LOCAL.clone() },
});

export const SkyMaterial = () => {
  const uniforms = useMemo(createSkyUniforms, []);
  return (
    <shaderMaterial
      uniforms={uniforms}
      vertexShader={vertexShader}
      fragmentShader={fragmentShader}
      side={BackSide}
      depthWrite={false}
      fog={false}
    />
  );
};

const basis = new Matrix4();
const back = new Vector3();

// Everything in the backdrop rides with the camera and turns with the rover, so the
// sunset always looks the same however far around the planet you drive.
const Sky = () => {
  const rig = useRef();
  const { nodes } = useGLTF(WORLD_URL);
  const planet = useMemo(
    () => prepare(nodes.SkyPlanet, { cast: false, receive: false, fog: false }),
    [nodes]
  );

  useFrame(({ camera }) => {
    back.copy(game.fwd).negate();
    basis.makeBasis(game.right, game.up, back);
    rig.current.position.copy(camera.position);
    rig.current.quaternion.setFromRotationMatrix(basis);
  });

  return (
    <group ref={rig}>
      <mesh renderOrder={-10} frustumCulled={false}>
        <sphereGeometry args={[1000, 32, 24]} />
        <SkyMaterial />
      </mesh>
      <Stars radius={800} depth={120} count={3500} factor={7} saturation={0} fade speed={0.3} />
      <group position={[-190, 120, -420]} scale={1.8}>
        <primitive object={planet} />
      </group>
    </group>
  );
};

export default Sky;
