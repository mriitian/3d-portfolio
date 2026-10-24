// Shared setup for the Blender-exported models: shadows, glow strength, reflections.

export const prepare = (root, { cast = true, receive = true, fog = true } = {}) => {
  root.traverse((o) => {
    if (!o.isMesh) return;
    const mat = o.material;

    if (mat.name && mat.name.startsWith("Glow_")) {
      // emissive parts: bright enough for the bloom pass to pick up
      mat.emissiveIntensity = 2.6;
      mat.toneMapped = false;
      o.castShadow = false;
      o.receiveShadow = false;
    } else {
      mat.envMapIntensity = 1.0;
      o.castShadow = cast;
      o.receiveShadow = receive;
    }
    if (!fog) {
      // clone so shared materials elsewhere keep their fog
      o.material = mat.clone();
      o.material.fog = false;
    }
  });
  return root;
};
