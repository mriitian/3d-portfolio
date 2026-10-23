import React from "react";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import {
  experiences,
  projects,
  services,
  technologies,
} from "../constants/constants";
import { github, linkedin } from "../assets";

const journey = [
  { label: "School", sub: "Yavatmal" },
  { label: "IIT Bombay", sub: "Aerospace" },
  { label: "Exploring", sub: "Creativity" },
  { label: "Game Dev", sub: "Now" },
];

const About = ({ color }) => (
  <>
    <p className="text-[20px] font-semibold leading-[30px] text-white">
      From aerospace engineering to game development.
    </p>
    <p className="mt-2 text-[15px] text-secondary">
      Different fields, same curiosity.
    </p>

    <div className="relative mt-10 grid grid-cols-4 gap-2">
      <div
        className="absolute left-[12.5%] right-[12.5%] top-[11px] h-[2px]"
        style={{ background: `linear-gradient(90deg, ${color}, #915eff)` }}
      />
      {journey.map((step, i) => (
        <div key={step.label} className="relative text-center">
          <div
            className="mx-auto h-6 w-6 rounded-full border-2 bg-[#0c0a1f]"
            style={{
              borderColor: color,
              boxShadow: `0 0 16px ${color}`,
              background: i === journey.length - 1 ? color : undefined,
            }}
          />
          <p className="mt-3 text-[14px] font-bold text-white">{step.label}</p>
          <p className="text-[12px] text-secondary">{step.sub}</p>
        </div>
      ))}
    </div>

    <div className="mt-10 grid grid-cols-2 gap-3 md:grid-cols-4">
      {services.map((service) => (
        <div
          key={service.title}
          className="flex flex-col items-center rounded-2xl border border-white/10 bg-white/5 px-3 py-4 text-center"
        >
          <img src={service.icon} alt="" className="h-10 w-10 object-contain" />
          <p className="mt-2 text-[13px] font-semibold text-white">{service.title}</p>
        </div>
      ))}
    </div>
  </>
);

const Projects = ({ color }) => (
  <div className="grid gap-5 md:grid-cols-2">
    {projects.map((project) => (
      <a
        key={project.name}
        href={project.source_code_link}
        target="_blank"
        rel="noopener noreferrer"
        className="group overflow-hidden rounded-2xl border border-white/10 bg-white/5 transition-all duration-300 hover:-translate-y-1"
        style={{ "--accent": color }}
      >
        <div className="h-36 overflow-hidden">
          <img
            src={project.image}
            alt={project.name}
            className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
        </div>
        <div className="p-4">
          <div className="flex items-start justify-between gap-3">
            <h3 className="text-[16px] font-bold text-white">{project.name}</h3>
            <img src={github} alt="GitHub" className="h-5 w-5 shrink-0 opacity-70" />
          </div>
          <p className="mt-1 line-clamp-3 text-[12px] leading-[18px] text-secondary">
            {project.description}
          </p>
          <div className="mt-3 flex flex-wrap gap-x-3 gap-y-1">
            {project.tags.map((tag) => (
              <span key={tag.name} className={`text-[12px] ${tag.color}`}>
                #{tag.name}
              </span>
            ))}
          </div>
        </div>
      </a>
    ))}
  </div>
);

const Skills = ({ color }) => (
  <div className="grid grid-cols-3 gap-4 md:grid-cols-4">
    {technologies.map((tech) => (
      <div
        key={tech.name}
        className="group flex flex-col items-center rounded-2xl border border-white/10 bg-white/5 px-3 py-5 transition-all duration-300 hover:-translate-y-1 hover:bg-white/10"
        style={{ boxShadow: "0 0 0 0 transparent" }}
        onMouseEnter={(e) => (e.currentTarget.style.boxShadow = `0 0 24px ${color}44`)}
        onMouseLeave={(e) => (e.currentTarget.style.boxShadow = "0 0 0 0 transparent")}
      >
        <img src={tech.icon} alt="" className="h-12 w-12 object-contain" />
        <p className="mt-3 text-[13px] font-semibold text-white">{tech.name}</p>
      </div>
    ))}
  </div>
);

const Experience = ({ color }) => (
  <div className="relative space-y-5 pl-8">
    <div
      className="absolute bottom-2 left-[13px] top-2 w-[2px]"
      style={{ background: `linear-gradient(${color}, transparent)` }}
    />
    {experiences.map((exp) => (
      <div key={exp.company_name + exp.title} className="relative">
        <div
          className="absolute -left-[33px] top-3 flex h-7 w-7 items-center justify-center rounded-full border-2"
          style={{ background: exp.iconBg, borderColor: color }}
        >
          <img src={exp.icon} alt="" className="h-[60%] w-[60%] object-contain" />
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <h3 className="text-[16px] font-bold text-white">{exp.title}</h3>
            <span className="text-[12px]" style={{ color }}>
              {exp.date}
            </span>
          </div>
          <p className="text-[13px] font-semibold text-secondary">{exp.company_name}</p>
          <p className="mt-2 line-clamp-2 text-[12px] leading-[18px] text-white-100">
            {exp.points[0]}
          </p>
        </div>
      </div>
    ))}
  </div>
);

const ContactButton = ({ href, icon, title, text, color, external = true }) => (
  <a
    href={href}
    {...(external ? { target: "_blank", rel: "noopener noreferrer" } : {})}
    className="flex items-center gap-4 rounded-2xl border border-white/10 bg-white/5 p-4 transition-all duration-300 hover:-translate-y-1 hover:bg-white/10"
  >
    <span
      className="flex h-12 w-12 items-center justify-center rounded-xl text-[22px]"
      style={{ background: `${color}22` }}
    >
      {icon}
    </span>
    <span>
      <span className="block text-[15px] font-bold text-white">{title}</span>
      <span className="block text-[12px] text-secondary">{text}</span>
    </span>
  </a>
);

const Contact = ({ color }) => (
  <>
    <p className="text-[20px] font-semibold leading-[30px] text-white">
      Let&apos;s create something amazing together.
    </p>
    <div className="mt-8 grid gap-4 md:grid-cols-2">
      <ContactButton
        href="https://www.linkedin.com/in/vedant-parkhe-934b841b9/"
        icon={<img src={linkedin} alt="" className="h-7 w-7 object-contain" />}
        title="LinkedIn"
        text="Say hello"
        color={color}
      />
      <ContactButton
        href="https://github.com/mriitian"
        icon={<img src={github} alt="" className="h-7 w-7 object-contain" />}
        title="GitHub"
        text="See the code"
        color={color}
      />
      <ContactButton
        href="mailto:vedantparkhe2409@gmail.com"
        icon="✉"
        title="Email"
        text="vedantparkhe2409@gmail.com"
        color={color}
        external={false}
      />
    </div>
    <Link
      to="/classic#contact"
      className="mt-6 inline-block text-[13px] text-secondary underline-offset-4 hover:text-white hover:underline"
    >
      Prefer a form? Open the classic contact page →
    </Link>
  </>
);

const CONTENT = {
  about: About,
  projects: Projects,
  skills: Skills,
  experience: Experience,
  contact: Contact,
};

const ZoneCard = ({ zone, onClose }) => {
  const Content = CONTENT[zone.id];

  return (
    <motion.div
      className="fixed inset-0 z-30 flex items-center justify-center bg-black/60 p-6 backdrop-blur-sm"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="w-full max-w-4xl rounded-[28px] p-[1.5px]"
        style={{
          background: `linear-gradient(135deg, ${zone.color}, transparent 55%, #915eff)`,
          boxShadow: `0 0 80px ${zone.color}33`,
        }}
        initial={{ opacity: 0, y: 40, scale: 0.96 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 24, scale: 0.97 }}
        transition={{ type: "spring", duration: 0.5 }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="relative max-h-[84vh] overflow-y-auto rounded-[27px] bg-[#0a091d]/95 p-8">
          <span
            className="pointer-events-none absolute right-8 top-2 select-none text-[120px] font-black leading-none opacity-[0.07]"
            style={{ color: zone.color }}
          >
            0{zone.index}
          </span>

          <button
            onClick={onClose}
            aria-label="Close"
            className="absolute right-5 top-5 flex h-9 w-9 items-center justify-center rounded-full border border-white/15 text-white hover:bg-white/10"
          >
            ✕
          </button>

          <p
            className="text-[12px] font-semibold uppercase tracking-[0.3em]"
            style={{ color: zone.color }}
          >
            {zone.place}
          </p>
          <h2 className="mb-8 mt-1 text-[40px] font-black text-white">{zone.title}</h2>

          <Content color={zone.color} />
        </div>
      </motion.div>
    </motion.div>
  );
};

export default ZoneCard;
