import { Vector3 } from "three";

// planet radius in world units; everything is placed on this sphere
export const R = 40;
// how close (along the surface) the rover must be to interact with a zone
export const ZONE_RADIUS = 7;

const rad = (deg) => (deg * Math.PI) / 180;
const fromLatLon = (lat, lon) =>
  new Vector3(
    Math.cos(rad(lat)) * Math.cos(rad(lon)),
    Math.sin(rad(lat)),
    Math.cos(rad(lat)) * Math.sin(rad(lon))
  );

export const SPAWN_DIR = new Vector3(1, 0, 0);

export const ZONES = [
  { id: "about", title: "About Me", place: "Launchpad", color: "#ff8a3d", lat: 8, lon: 28 },
  { id: "projects", title: "Projects", place: "Creative District", color: "#d95cff", lat: 38, lon: 105 },
  { id: "skills", title: "Skills", place: "Observatory", color: "#3ddcff", lat: -34, lon: 165 },
  { id: "experience", title: "Experience", place: "Space Station", color: "#915eff", lat: 30, lon: -115 },
  { id: "contact", title: "Contact", place: "Comm Hub", color: "#edebff", lat: -32, lon: -50 },
].map((zone, i) => ({ ...zone, index: i + 1, dir: fromLatLon(zone.lat, zone.lon) }));

export const SHARD_COUNT = 12;

// collectibles spread evenly over the planet, kept clear of the zones and spawn
const GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5));
export const SHARDS = (() => {
  const candidates = 70;
  const out = [];

  for (let i = 0; i < candidates && out.length < SHARD_COUNT; i++) {
    const y = 1 - (i / (candidates - 1)) * 2;
    const ring = Math.sqrt(1 - y * y);
    const theta = GOLDEN_ANGLE * i;
    const dir = new Vector3(Math.cos(theta) * ring, y, Math.sin(theta) * ring);

    const clearOfZones = ZONES.every(
      (zone) => Math.acos(Math.min(1, dir.dot(zone.dir))) * R > 12
    );
    const clearOfSpawn = Math.acos(Math.min(1, dir.dot(SPAWN_DIR))) * R > 8;

    if (clearOfZones && clearOfSpawn) out.push(dir);
  }

  return out;
})();

// distance along the surface between a unit direction and another
export const arcDistance = (a, b) =>
  R * Math.acos(Math.max(-1, Math.min(1, a.dot(b))));
