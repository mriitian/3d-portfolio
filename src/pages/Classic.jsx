import {
  About,
  Contact,
  Experience,
  Hero,
  Navbar,
  Tech,
  Works,
  StarsCanvas,
} from "../components";
import DeviceNotice from "./DeviceNotice";

const Classic = () => {
  return (
    <div className="relative z-0 bg-primary">
      <div className="bg-hero-pattern bg-cover bg-no-repeat bg-center">
        <Navbar />
        <Hero />
      </div>
      <About />
      <Experience />
      <Tech />
      <Works />
      <div className="relative z-0">
        <StarsCanvas /> {/* background */}
        <Contact /> {/* foreground */}
      </div>
      <DeviceNotice />
    </div>
  );
};

export default Classic;
