import React from "react";
import { Link, Navigate } from "react-router-dom";
import useMediaQuery from "../hooks/useMediaQuery";
import { SMALL_SCREEN_QUERY } from "../game/device";

const PathCard = ({ to, eyebrow, title, text, cta, accent }) => (
  <Link
    to={to}
    className="group relative block rounded-3xl p-[1.5px] transition-transform duration-300 hover:-translate-y-2"
    style={{
      background: `linear-gradient(135deg, ${accent}, transparent 55%, #915eff)`,
    }}
  >
    <div className="h-full rounded-3xl bg-[#0b0a1e]/95 p-8">
      <p
        className="text-[12px] font-semibold uppercase tracking-[0.25em]"
        style={{ color: accent }}
      >
        {eyebrow}
      </p>
      <h2 className="mt-3 text-white text-[32px] font-black">{title}</h2>
      <p className="mt-3 text-secondary text-[15px] leading-[26px]">{text}</p>
      <span
        className="mt-8 inline-flex items-center gap-2 text-[15px] font-bold text-white"
        style={{ textShadow: `0 0 18px ${accent}` }}
      >
        {cta}
        <span className="transition-transform group-hover:translate-x-1">→</span>
      </span>
    </div>
  </Link>
);

const Landing = () => {
  const isSmall = useMediaQuery(SMALL_SCREEN_QUERY);

  // phones and small screens skip the choice and land on the classic site
  if (isSmall) return <Navigate to="/classic" replace />;

  return (
    <main className="relative min-h-screen overflow-hidden bg-primary">
      <div className="pointer-events-none absolute -top-40 -left-32 h-[480px] w-[480px] rounded-full bg-[#ff8a3d]/20 blur-[140px]" />
      <div className="pointer-events-none absolute -bottom-48 -right-32 h-[560px] w-[560px] rounded-full bg-[#915eff]/30 blur-[160px]" />
      <div className="pointer-events-none absolute top-1/3 right-1/4 h-[260px] w-[260px] rounded-full bg-[#3ddcff]/15 blur-[120px]" />

      <div className="relative mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-10 py-16">
        <p className="text-secondary text-[14px] uppercase tracking-[0.3em]">
          Aerospace Engineer → Game Developer
        </p>
        <h1 className="mt-4 text-white font-black text-[72px] leading-[80px]">
          Vedant <span className="text-[#915eff]">Parkhe</span>
        </h1>
        <p className="mt-4 text-[#dfd9ff] text-[22px] font-medium">
          Same curiosity, different worlds.
        </p>

        <div className="mt-14 grid gap-8 md:grid-cols-2">
          <PathCard
            to="/play"
            accent="#ff8a3d"
            eyebrow="Play mode · best on desktop"
            title="Orbital Playground"
            text="Drive a rover around a tiny planet and discover my work, zone by zone."
            cta="Start exploring"
          />
          <PathCard
            to="/classic"
            accent="#3ddcff"
            eyebrow="Classic mode"
            title="The Portfolio"
            text="The straightforward version: about, experience, projects and contact."
            cta="Take me there"
          />
        </div>
      </div>
    </main>
  );
};

export default Landing;
