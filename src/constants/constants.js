import {
  mobile,
  backend,
  creator,
  web,
  javascript,
  typescript,
  html,
  css,
  reactjs,
  redux,
  tailwind,
  nodejs,
  mongodb,
  git,
  figma,
  racing,
  techfest,
  bizup,
  docker,
  meta,
  starbucks,
  tesla,
  shopify,
  carrent,
  jobit,
  tripguide,
  threejs,
  cafirm,
  promptlib,
  hospi,
  dashboard,
} from "../assets";

export const navLinks = [
  {
    id: "about",
    title: "About",
  },
  {
    id: "work",
    title: "Work",
  },
  {
    id: "contact",
    title: "Contact",
  },
];

const services = [
  {
    title: "Web Developer",
    icon: web,
  },
  {
    title: "Game Developer",
    icon: mobile,
  },
  {
    title: "Backend Developer",
    icon: backend,
  },
  {
    title: "Content Creator",
    icon: creator,
  },
];

const technologies = [
  {
    name: "HTML 5",
    icon: html,
  },
  {
    name: "CSS 3",
    icon: css,
  },
  {
    name: "JavaScript",
    icon: javascript,
  },
  {
    name: "TypeScript",
    icon: typescript,
  },
  {
    name: "React JS",
    icon: reactjs,
  },
  {
    name: "Redux Toolkit",
    icon: redux,
  },
  {
    name: "Tailwind CSS",
    icon: tailwind,
  },
  {
    name: "Node JS",
    icon: nodejs,
  },
  {
    name: "MongoDB",
    icon: mongodb,
  },
  {
    name: "Three JS",
    icon: threejs,
  },
  {
    name: "git",
    icon: git,
  },
  {
    name: "figma",
    icon: figma,
  },
];

const experiences = [
  {
    title: "Content Editor and Analyst",
    company_name: "BIZ-UP",
    icon: bizup,
    iconBg: "#383E56",
    date: "Dec 2023 - Feb 2024",
    points: [
      "Collaborated in a team of 3 alongside managers to streamline the WhatsApp catalogue automation process.",
      "Reduced the processing time from 3 hours to 30 minutes by leveraging JavaScript to automate catalog extraction.",
      "Analyzed 120K+ data points, including CTR, clicks, and viewership using advanced Excel features.",
      "Contributed to the business & operations module by efficiently tagging prices and features of 50+ businesses.",
    ],
  },
  {
    title: "Design and Creatives Coordinator",
    company_name: "Techfest, IIT Bombay",
    icon: techfest,
    iconBg: "#E6DEDD",
    date: "Mar 2023 - Feb 2024",
    points: [
      "Created visually appealing content, generating over 130k+ views on the Techfest Instagram within 2-3 weeks.",
      "Significantly contributed to the design and ideation process for the official website of Techfest 2023.",
      "Designed interactive Competition Cards & Gallery Carousel, visually presenting essential competition details.",
      "Utilized industry-standard software tools like Figma, Dora, and Photoshop to refine the UI of the website.",
      "Produced and edited promotional videos for Techfest 2023, including Theme Guessing, Theme Release, and College Ambassador Program Announcements.",
    ],
  },
  {
    title: "Marketing Trainee",
    company_name: "IIT Bombay Racing Team",
    icon: racing,
    iconBg: "#383E56",
    date: "Feb 2023 - Jan 2024",
    points: [
      "Selected from 30+ candidates after a rigorous selection process including an assignment and interview.",
      "Proficiently created responsive pages for the Achievements and Contact Us pages for the IITB Racing website.",
      "Categorized and databased companies across diverse categories such as F&B, nuts and bolts, and logistics.",
      "Secured first place in the team Presentation Competition, excelling in Presentation & Representation.",
    ],
  },
];

const testimonials = [
  {
    testimonial:
      "I thought it was impossible to make a website as beautiful as our product, but Rick proved me wrong.",
    name: "Sara Lee",
    designation: "CFO",
    company: "Acme Co",
    image: "https://randomuser.me/api/portraits/women/4.jpg",
  },
  {
    testimonial:
      "I've never met a web developer who truly cares about their clients' success like Rick does.",
    name: "Chris Brown",
    designation: "COO",
    company: "DEF Corp",
    image: "https://randomuser.me/api/portraits/men/5.jpg",
  },
  {
    testimonial:
      "After Rick optimized our website, our traffic increased by 50%. We can't thank them enough!",
    name: "Lisa Wang",
    designation: "CTO",
    company: "456 Enterprises",
    image: "https://randomuser.me/api/portraits/women/6.jpg",
  },
];

const projects = [
  {
    name: "CA Firm",
    description:
      "A professional website for a Chartered Accounting (CA) firm, designed with a modern, responsive layout that enhances user experience and engagement.",
    tags: [
      {
        name: "react",
        color: "blue-text-gradient",
      },
      {
        name: "mongodb",
        color: "green-text-gradient",
      },
      {
        name: "django",
        color: "pink-text-gradient",
      },
    ],
    image: cafirm,
    source_code_link: "https://github.com/mriitian/ca-firm",
  },
  {
    name: "AI Prompt Library",
    description:
      "AI Prompt Library platform using Next.js, where users can discover, create, and share AI-powered prompts. The platform features secure Google Auth for easy user sign-in.",
    tags: [
      {
        name: "NextJs",
        color: "blue-text-gradient",
      },
      {
        name: "TailwindCSS",
        color: "green-text-gradient",
      },
      {
        name: "GoogleOauth",
        color: "pink-text-gradient",
      },
    ],
    image: promptlib,
    source_code_link: "https://github.com/mriitian/next-app",
  },
  {
    name: "Admin Dashboard",
    description:
      "An intuitive admin dashboard displaying key metrics such as emails sent, sales obtained, new clients, and recent transactions with visually engaging charts and user-friendly navigation",
    tags: [
      {
        name: "ReactJs",
        color: "blue-text-gradient",
      },
      {
        name: "Nivo Charts",
        color: "green-text-gradient",
      },
      {
        name: "Material UI",
        color: "pink-text-gradient",
      },
    ],
    image: dashboard,
    source_code_link: "https://dashboard-react-1.vercel.app/",
  },
  {
    name: "A Hospital Website",
    description:
      "The hospital website, built using ReactJS with React-Bootstrap, features a clean and modern design, providing a user-friendly interface to navigate the hospital's services and information.",
    tags: [
      {
        name: "ReactJs",
        color: "blue-text-gradient",
      },
      {
        name: "react-bootstrap",
        color: "green-text-gradient",
      },
      {
        name: "RestApi",
        color: "pink-text-gradient",
      },
    ],
    image: hospi,
    source_code_link: "https://github.com/mriitian/Hospital-Website",
  },
];

export { services, technologies, experiences, testimonials, projects };
