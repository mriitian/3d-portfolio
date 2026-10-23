import React, { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Vector3 } from "three";
import { game } from "./state";
import { R, SHARDS, ZONES } from "./zones";

const SIZE = 156;
const ZONE_RANGE = 50; // zones show their exact spot only this close...
const SHARD_RANGE = 22; // ...and shards even closer, so exploring still matters

const clampAcos = (x) => Math.acos(Math.max(-1, Math.min(1, x)));

// Circular scanner. Far zones only show as faint arrows pointing their way.
const Radar = ({ visited }) => {
  const canvasRef = useRef();
  const visitedRef = useRef(visited);
  visitedRef.current = visited;

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    const dpr = window.devicePixelRatio || 1;
    canvas.width = SIZE * dpr;
    canvas.height = SIZE * dpr;
    ctx.scale(dpr, dpr);

    const up = new Vector3();
    const right = new Vector3();
    const t = new Vector3();
    const c = SIZE / 2;
    const radius = c - 8;
    let frame;

    // direction to a point on the planet in the rover's own frame: [right, forward]
    const bearing = (dir) => {
      t.copy(dir).addScaledVector(up, -dir.dot(up));
      if (t.lengthSq() < 1e-6) return [0, 0];
      t.normalize();
      return [t.dot(right), t.dot(game.fwd)];
    };

    const draw = (time) => {
      ctx.clearRect(0, 0, SIZE, SIZE);

      ctx.beginPath();
      ctx.arc(c, c, radius, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(8, 8, 26, 0.72)";
      ctx.fill();
      ctx.strokeStyle = "rgba(145, 94, 255, 0.6)";
      ctx.lineWidth = 2;
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(c, c, radius / 2, 0, Math.PI * 2);
      ctx.strokeStyle = "rgba(145, 94, 255, 0.2)";
      ctx.lineWidth = 1;
      ctx.stroke();

      up.copy(game.pos).normalize();
      right.crossVectors(game.fwd, up);

      // sweep
      const sweep = time / 1200;
      ctx.beginPath();
      ctx.moveTo(c, c);
      ctx.lineTo(c + Math.sin(sweep) * radius, c - Math.cos(sweep) * radius);
      ctx.strokeStyle = "rgba(61, 220, 255, 0.35)";
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // shards
      SHARDS.forEach((dir, i) => {
        if (game.collected.has(i)) return;
        const arc = R * clampAcos(up.dot(dir));
        if (arc > SHARD_RANGE) return;
        const [x, y] = bearing(dir);
        const d = (arc / SHARD_RANGE) * radius;
        ctx.fillStyle = "#ffd166";
        ctx.fillRect(c + x * d - 2, c - y * d - 2, 4, 4);
      });

      // zones
      ZONES.forEach((zone) => {
        const arc = R * clampAcos(up.dot(zone.dir));
        const [x, y] = bearing(zone.dir);
        const seen = visitedRef.current.includes(zone.id);

        if (arc <= ZONE_RANGE) {
          const d = (arc / ZONE_RANGE) * radius;
          const px = c + x * d;
          const py = c - y * d;
          ctx.beginPath();
          ctx.arc(px, py, 7, 0, Math.PI * 2);
          if (seen) {
            ctx.fillStyle = zone.color;
            ctx.fill();
            ctx.fillStyle = "#050816";
            ctx.font = "bold 10px Poppins, sans-serif";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.fillText(String(zone.index), px, py + 0.5);
          } else {
            ctx.strokeStyle = zone.color;
            ctx.globalAlpha = 0.6 + 0.4 * Math.sin(time / 250);
            ctx.lineWidth = 2;
            ctx.stroke();
            ctx.fillStyle = zone.color;
            ctx.font = "bold 10px Poppins, sans-serif";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.fillText("?", px, py + 0.5);
            ctx.globalAlpha = 1;
          }
        } else {
          // out of range: just a faint arrow on the rim
          const a = Math.atan2(x, y);
          const px = c + Math.sin(a) * (radius - 5);
          const py = c - Math.cos(a) * (radius - 5);
          ctx.save();
          ctx.translate(px, py);
          ctx.rotate(a);
          ctx.beginPath();
          ctx.moveTo(0, -4);
          ctx.lineTo(3.5, 3);
          ctx.lineTo(-3.5, 3);
          ctx.closePath();
          ctx.fillStyle = zone.color;
          ctx.globalAlpha = 0.4;
          ctx.fill();
          ctx.restore();
          ctx.globalAlpha = 1;
        }
      });

      // rover
      ctx.beginPath();
      ctx.moveTo(c, c - 7);
      ctx.lineTo(c + 5, c + 6);
      ctx.lineTo(c - 5, c + 6);
      ctx.closePath();
      ctx.fillStyle = "#ffffff";
      ctx.fill();

      frame = requestAnimationFrame(draw);
    };

    frame = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(frame);
  }, []);

  return <canvas ref={canvasRef} style={{ width: SIZE, height: SIZE }} />;
};

const Key = ({ children }) => (
  <kbd className="rounded-md border border-white/25 bg-white/10 px-2 py-0.5 text-[12px] font-semibold text-white">
    {children}
  </kbd>
);

const Panel = ({ className = "", children }) => (
  <div
    className={`rounded-2xl border border-white/10 bg-[#0b0a1e]/70 px-4 py-3 backdrop-blur-md ${className}`}
  >
    {children}
  </div>
);

const Hud = ({ near, visited, shards, onInteract, onJump }) => {
  const [menuOpen, setMenuOpen] = useState(false);
  const allVisited = visited.length === ZONES.length;

  return (
    <div className="pointer-events-none absolute inset-0 z-20 font-[Poppins]">
      {/* top left: title and exits */}
      <div className="pointer-events-auto absolute left-5 top-5">
        <Panel>
          <p className="text-[11px] uppercase tracking-[0.25em] text-secondary">
            Orbital Playground
          </p>
          <p className="text-[15px] font-bold text-white">
            Vedant <span className="text-[#915eff]">Parkhe</span>
          </p>
          <div className="mt-2 flex gap-3 text-[12px]">
            <Link to="/" className="text-secondary hover:text-white">
              ← Home
            </Link>
            <Link to="/classic" className="text-secondary hover:text-white">
              Classic version
            </Link>
          </div>
        </Panel>
      </div>

      {/* top right: mission */}
      <div className="absolute right-5 top-5 w-[230px]">
        <Panel>
          <p className="text-[11px] uppercase tracking-[0.25em] text-secondary">Mission</p>
          <ul className="mt-2 space-y-1">
            {ZONES.map((zone) => {
              const seen = visited.includes(zone.id);
              return (
                <li key={zone.id} className="flex items-center gap-2 text-[13px]">
                  <span
                    className="inline-block h-2.5 w-2.5 rounded-full border"
                    style={{
                      borderColor: zone.color,
                      background: seen ? zone.color : "transparent",
                    }}
                  />
                  <span className={seen ? "text-white" : "text-secondary"}>
                    {seen ? zone.title : "Undiscovered zone"}
                  </span>
                </li>
              );
            })}
          </ul>
          <p className="mt-3 text-[13px] text-[#ffd166]">
            ◆ Orbit shards {shards}/{SHARDS.length}
          </p>
          {allVisited && (
            <p className="mt-2 text-[12px] font-semibold text-[#3ddcff]">
              All zones discovered!
            </p>
          )}
        </Panel>
      </div>

      {/* bottom left: controls + jump menu */}
      <div className="pointer-events-auto absolute bottom-5 left-5 flex flex-col items-start gap-3">
        {menuOpen && (
          <Panel className="w-[230px]">
            <p className="text-[11px] uppercase tracking-[0.25em] text-secondary">Jump to</p>
            <ul className="mt-2 space-y-1">
              {ZONES.map((zone) => (
                <li key={zone.id}>
                  <button
                    onClick={() => {
                      onJump(zone);
                      setMenuOpen(false);
                    }}
                    className="flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left text-[13px] text-white hover:bg-white/10"
                  >
                    <span
                      className="inline-block h-2.5 w-2.5 rounded-full"
                      style={{ background: zone.color }}
                    />
                    {zone.title}
                    <span className="ml-auto text-[11px] text-secondary">{zone.place}</span>
                  </button>
                </li>
              ))}
            </ul>
          </Panel>
        )}
        <button
          onClick={() => setMenuOpen((open) => !open)}
          className="rounded-xl border border-[#915eff]/60 bg-[#0b0a1e]/70 px-4 py-2 text-[13px] font-semibold text-white backdrop-blur-md hover:bg-[#915eff]/30"
        >
          Jump to… {menuOpen ? "▾" : "▸"}
        </button>
        <Panel>
          <div className="space-y-1.5 text-[12px] text-secondary">
            <p className="flex items-center gap-2">
              <span className="flex gap-1">
                <Key>W</Key>
                <Key>A</Key>
                <Key>S</Key>
                <Key>D</Key>
              </span>
              Drive
            </p>
            <p className="flex items-center gap-2">
              <Key>Space</Key> Boost
            </p>
            <p className="flex items-center gap-2">
              <Key>E</Key> Interact · <Key>Esc</Key> Close
            </p>
          </div>
        </Panel>
      </div>

      {/* bottom right: radar */}
      <div className="absolute bottom-5 right-5">
        <Radar visited={visited} />
      </div>

      {/* interaction prompt */}
      {near && (
        <div className="pointer-events-auto absolute bottom-24 left-1/2 -translate-x-1/2">
          <button
            onClick={() => onInteract(near)}
            className="rounded-2xl border px-6 py-3 text-white backdrop-blur-md transition-transform hover:scale-105"
            style={{
              borderColor: near.color,
              background: "rgba(11,10,30,0.8)",
              boxShadow: `0 0 28px ${near.color}55`,
            }}
          >
            <span className="mr-3 rounded-md border border-white/30 bg-white/10 px-2 py-0.5 text-[13px] font-bold">
              E
            </span>
            <span className="text-[15px] font-bold">{near.title}</span>
            <span className="ml-2 text-[12px] text-secondary">{near.place}</span>
          </button>
        </div>
      )}
    </div>
  );
};

export default Hud;
