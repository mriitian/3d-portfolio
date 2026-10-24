import React, { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Stars } from "@react-three/drei";
import { BackSide, Color, Matrix4, Vector3 } from "three";
import { game } from "./state";

// The sun's direction in the rover's own frame: x = right, y = up, -z = forward.
export const SUN_LOCAL = new Vector3(0.5, 0.42, -0.6).normalize(); // the moon

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
    vec3 col = mix(horizon, mid, smoothstep(0.0, 0.07, y));
    col = mix(col, zenith, smoothstep(0.08, 0.75, y));
    col = mix(col, below, smoothstep(0.0, -0.3, y));
    float s = max(dot(n, normalize(sunDir)), 0.0);
    col += vec3(0.45, 0.6, 1.0) * pow(s, 14.0) * 0.16;
    col += vec3(0.7, 0.85, 1.0) * pow(s, 60.0) * 0.5;
    col += vec3(0.85, 0.93, 1.0) * smoothstep(0.9993, 0.9998, s) * 3.0;
    gl_FragColor = vec4(col, 1.0);
    #include <colorspace_fragment>
  }
`;

export const createSkyUniforms = () => ({
  zenith: { value: new Color("#02030c") },
  mid: { value: new Color("#0a1238") },
  horizon: { value: new Color("#16376e") },
  below: { value: new Color("#050818") },
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
    </group>
  );
};

export default Sky;
