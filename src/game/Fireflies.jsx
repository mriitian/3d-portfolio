import React, { useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import { AdditiveBlending, BufferAttribute, BufferGeometry, Color, ShaderMaterial } from "three";
import { R } from "./zones";

const COUNT = 1500;
const CLUSTERS = 46;

// small deterministic random generator, so the swarm is the same every visit
const mulberry32 = (seed) => () => {
  seed |= 0;
  seed = (seed + 0x6d2b79f5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

const vertexShader = /* glsl */ `
  attribute float aPhase;
  attribute float aSpeed;
  attribute float aSize;
  attribute vec3 aColor;
  uniform float uTime;
  uniform float uScale;
  varying vec3 vColor;
  varying float vGlow;
  void main() {
    float t = uTime * aSpeed + aPhase * 6.2831;
    // a lazy wandering loop around the firefly's home spot
    vec3 drift = vec3(sin(t * 0.9 + aPhase * 11.0),
                      cos(t * 0.7 + aPhase * 7.0),
                      sin(t * 0.8 + aPhase * 5.0)) * 0.9;
    vec4 mv = modelViewMatrix * vec4(position + drift, 1.0);
    gl_Position = projectionMatrix * mv;
    // blink: bright flashes with dim moments between
    float blink = 0.3 + 0.7 * pow(0.5 + 0.5 * sin(t * 1.7 + aPhase * 20.0), 2.0);
    vGlow = blink;
    vColor = aColor;
    gl_PointSize = clamp(aSize * uScale * (0.6 + 0.4 * blink) / -mv.z, 2.0, 46.0);
  }
`;

const fragmentShader = /* glsl */ `
  varying vec3 vColor;
  varying float vGlow;
  void main() {
    float d = length(gl_PointCoord - 0.5);
    if (d > 0.5) discard;
    float core = smoothstep(0.5, 0.0, d);
    vec3 col = vColor * (0.5 + 2.4 * pow(core, 3.0)) * vGlow;
    gl_FragColor = vec4(col, core * vGlow);
    #include <colorspace_fragment>
  }
`;

const PALETTE = [new Color("#d6ff72"), new Color("#78f2ff"), new Color("#ff9ae6")];

// Fireflies spread over the whole planet, drifting and blinking; about half gather in
// small clusters, and the shader does all the movement so it costs almost nothing.
const Fireflies = () => {
  const { geometry, material } = useMemo(() => {
    const rand = mulberry32(2024);
    const dir = () => {
      const z = rand() * 2 - 1;
      const a = rand() * Math.PI * 2;
      const r = Math.sqrt(1 - z * z);
      return [r * Math.cos(a), z, r * Math.sin(a)];
    };
    const centres = Array.from({ length: CLUSTERS }, dir);

    const position = new Float32Array(COUNT * 3);
    const phase = new Float32Array(COUNT);
    const speed = new Float32Array(COUNT);
    const size = new Float32Array(COUNT);
    const colour = new Float32Array(COUNT * 3);

    for (let i = 0; i < COUNT; i++) {
      let d;
      if (i < COUNT * 0.55) {
        const c = centres[i % CLUSTERS];
        const s = 0.1; // spread of a cluster
        d = [c[0] + (rand() - 0.5) * s, c[1] + (rand() - 0.5) * s, c[2] + (rand() - 0.5) * s];
      } else {
        d = dir();
      }
      const len = Math.hypot(d[0], d[1], d[2]);
      const h = R + 0.7 + rand() * 3.6;
      position.set([(d[0] / len) * h, (d[1] / len) * h, (d[2] / len) * h], i * 3);

      phase[i] = rand();
      speed[i] = 0.35 + rand() * 0.5;
      size[i] = 0.24 + rand() * 0.3;
      const pick = rand();
      const col = pick < 0.6 ? PALETTE[0] : pick < 0.88 ? PALETTE[1] : PALETTE[2];
      colour.set([col.r, col.g, col.b], i * 3);
    }

    const geo = new BufferGeometry();
    geo.setAttribute("position", new BufferAttribute(position, 3));
    geo.setAttribute("aPhase", new BufferAttribute(phase, 1));
    geo.setAttribute("aSpeed", new BufferAttribute(speed, 1));
    geo.setAttribute("aSize", new BufferAttribute(size, 1));
    geo.setAttribute("aColor", new BufferAttribute(colour, 3));

    const mat = new ShaderMaterial({
      uniforms: { uTime: { value: 0 }, uScale: { value: 700 } },
      vertexShader,
      fragmentShader,
      transparent: true,
      depthWrite: false,
      blending: AdditiveBlending,
    });
    return { geometry: geo, material: mat };
  }, []);

  useFrame(({ clock, camera, size, viewport }) => {
    material.uniforms.uTime.value = clock.elapsedTime;
    // convert a world-space size into pixels for the current screen and field of view
    material.uniforms.uScale.value =
      (size.height * viewport.dpr) / (2 * Math.tan((camera.fov * Math.PI) / 360));
  });

  return <points geometry={geometry} material={material} frustumCulled={false} />;
};

export default Fireflies;
