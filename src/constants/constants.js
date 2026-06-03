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
  mapit,
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
  chatapp,
  snatched,
  unity,
  blender,
  iotron,
  knoxo,
  socgame,
  missminutes,
  creativeportfolio,
  zombiegame,
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
    title: "Game Developer",
    icon: mobile,
  },
  {
    title: "Web Developer",
    icon: web,
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
    name: "Unity",
    icon: unity,
  },
  {
    name: "Blender",
    icon: blender,
  },
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
    title: "Unity Game Developer",
    company_name: "Iotron Technologies",
    icon: iotron,
    iconBg: "#1E1E1E",
    date: "Dec 2024",
    points: [
      "Developed a simulation scene for a Rummy game in Unity, handling card interactions, grouping logic, and validation systems.",
      "Collaborated with a startup team to optimize gameplay mechanics and create a professional card game interface.",
      "Applied Object-Oriented Programming (OOP) and SOLID principles to improve code reusability, scalability, and maintainability.",
      "Strengthened game development workflows by building modular and extensible systems in Unity using C#.",
    ],
  },
  {
    title: "Frontend Developer Intern",
    company_name: "Knoxo",
    icon: knoxo,
    iconBg: "#DDE6ED",
    date: "Apr 2024 - Jun 2024",
    points: [
      "Collaborated in a team of 4 as a Frontend Developer, using React.js to build modern and responsive UI components.",
      "Managed Django database integration and implemented APIs for user authentication and appointment booking systems.",
      "Used Postman for API testing, debugging, and validating backend endpoints during development.",
      "Worked on project structure optimization and loading performance improvements to enhance overall user experience.",
    ],
  },

  // Existing Experiences
  {
    title: "Frontend Developer",
    company_name: "MapIT.ai",
    icon: mapit,
    iconBg: "#DDE6ED",
    date: "Dec 2024 - Mar 2025",
    points: [
      "Collaborated in a team of developers alongside managers to create and improve the UI for Makerspace Inventory.",
      "Used ReactJS and MUI's MediaQuery to make dashboard elements responsive across all screen sizes.",
      "Developed the UI for the Workshops page, handled API calls, integrated backend data, and refined the layout.",
    ],
  },
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
    name: "2D Multiplayer Game",
    description:
      "A Unity-based multiplayer game developed during the Season of Code Program under Web and Coding Club. Implemented real-time networking, multiplayer lobbies, and player synchronization using Unity Gaming Services. Designed polished gameplay systems, smooth scene transitions, and an interactive Main Menu UI while gaining hands-on experience in multiplayer architecture and connection management.",
    tags: [
      {
        name: "Unity",
        color: "blue-text-gradient",
      },
      {
        name: "C#",
        color: "green-text-gradient",
      },
      {
        name: "Unity Gaming Services",
        color: "pink-text-gradient",
      },
      {
        name: "Multiplayer",
        color: "blue-text-gradient",
      },
    ],
    image: socgame,
    source_code_link: "https://github.com/mriitian/2D-Multiplayer",
  },

  {
    name: "Miss Minutes – AI Writing Assistant",
    description:
      "A lightweight and responsive AI-powered writing assistant built using React, TypeScript, XState, ProseMirror, and Google Gemini. Features include a rich text editor, AI-assisted ‘Continue Writing’ functionality with character-by-character typing animation, local document storage, TXT export, and a clean modern UI optimized for seamless writing workflows.",
    tags: [
      {
        name: "React",
        color: "blue-text-gradient",
      },
      {
        name: "TypeScript",
        color: "green-text-gradient",
      },
      {
        name: "Google Gemini",
        color: "pink-text-gradient",
      },
      {
        name: "ProseMirror",
        color: "blue-text-gradient",
      },
      {
        name: "XState",
        color: "green-text-gradient",
      },
    ],
    image: missminutes,
    source_code_link: "https://github.com/mriitian/Miss-Minutes",
  },

  {
    name: "Zombie Survival Game",
    description:
      "A 2D action-survival game inspired by Plants vs Zombies, developed in Unity with multiple gameplay modes, enemy waves, weapon systems, and survival mechanics. Implemented various player weapons, enemy AI behaviors, health systems, and dynamic combat interactions while focusing on engaging gameplay loops, responsive controls, and optimized game architecture.",
    tags: [
      {
        name: "Unity",
        color: "blue-text-gradient",
      },
      {
        name: "C#",
        color: "green-text-gradient",
      },
      {
        name: "Game Development",
        color: "pink-text-gradient",
      },
      {
        name: "2D Game",
        color: "blue-text-gradient",
      },
    ],
    image: zombiegame,
    source_code_link: "https://github.com/mriitian/zombie-survival",
  },

  {
    name: "3D Creative Portfolio",
    description:
      "A creative 3D portfolio hosted on ArtStation showcasing multiple original 3D models, environments, and terrain-based scenes created using Blender and Unity. Explored terrain generation, environmental storytelling, animations, lighting, and AI-assisted workflows to produce visually immersive scenes and stylized renders for creative experimentation and digital world-building.",
    tags: [
      {
        name: "Blender",
        color: "blue-text-gradient",
      },
      {
        name: "Unity",
        color: "green-text-gradient",
      },
      {
        name: "3D Modeling",
        color: "pink-text-gradient",
      },
      {
        name: "Environment Design",
        color: "blue-text-gradient",
      },
    ],
    image: creativeportfolio,
    source_code_link: "https://www.artstation.com/vedantparkhe24",
  },

  // Existing Projects

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
      "An intuitive admin dashboard displaying key metrics such as emails sent, sales obtained, new clients, and recent transactions with visually engaging charts and user-friendly navigation.",
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

  {
    name: "A Dynamic Chatting App",
    description:
      "A Dynamic Chatting application built using ReactJS, NodeJS, Express Server and Socket.io for real-time communication, along with MongoDB for efficient database management.",
    tags: [
      {
        name: "ReactJs",
        color: "blue-text-gradient",
      },
      {
        name: "REST-API",
        color: "green-text-gradient",
      },
      {
        name: "NodeJs",
        color: "pink-text-gradient",
      },
    ],
    image: chatapp,
    source_code_link: "https://github.com/mriitian/X-Chatt",
  },

  {
    name: "Snatched E-commerce Platform",
    description:
      "A full-stack e-commerce web application with user authentication (Google OAuth & JWT), secure session management, product search, dynamic cart, wishlist, and order tracking. Built with a modern Vite + React + ShadCN UI frontend and a Node.js + Express backend integrated with MongoDB.",
    tags: [
      {
        name: "React",
        color: "blue-text-gradient",
      },
      {
        name: "Vite",
        color: "green-text-gradient",
      },
      {
        name: "ShadCN",
        color: "pink-text-gradient",
      },
      {
        name: "Node.js",
        color: "blue-text-gradient",
      },
      {
        name: "Express",
        color: "green-text-gradient",
      },
      {
        name: "MongoDB",
        color: "pink-text-gradient",
      },
      {
        name: "JWT",
        color: "blue-text-gradient",
      },
      {
        name: "Google OAuth",
        color: "green-text-gradient",
      },
    ],
    image: snatched,
    source_code_link: "https://github.com/mriitian/snatched",
  },
];

export { services, technologies, experiences, testimonials, projects };
