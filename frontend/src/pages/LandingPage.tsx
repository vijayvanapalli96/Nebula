import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";

// --- Section fade-up helper ------------------------------------------------
const fadeUp = {
  hidden: { opacity: 0, y: 32 },
  visible: (d: number = 0) => ({
    opacity: 1, y: 0,
    transition: { duration: 0.6, ease: "easeOut" as const, delay: d },
  }),
};

// --- Sticky nav -----------------------------------------------------------
const LandingNav: React.FC = () => {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <motion.nav
      initial={{ y: -60, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6 }}
      className="fixed top-0 inset-x-0 z-50 transition-all duration-300"
      style={{
        backgroundColor: scrolled ? "rgba(10,10,15,0.85)" : "transparent",
        backdropFilter: scrolled ? "blur(16px)" : "none",
        borderBottom: scrolled ? "1px solid rgba(255,255,255,0.06)" : "none",
      }}
    >
      <div className="max-w-screen-xl mx-auto flex items-center justify-between px-6 h-16">
        {/* Logo */}
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-violet-600 flex items-center justify-center glow-purple">
            <span className="text-white font-black text-base leading-none select-none">N</span>
          </div>
          <span className="text-lg font-black tracking-tight text-white text-glow">NEBULA</span>
        </div>

        {/* Centre links */}
        <div className="hidden sm:flex items-center gap-8">
          {["Features", "Genres", "How It Works"].map((l) => (
            <a
              key={l}
              href={`#${l.toLowerCase().replace(/ /g, "-")}`}
              className="text-xs font-semibold uppercase tracking-widest text-gray-400 hover:text-white transition"
            >
              {l}
            </a>
          ))}
        </div>

        {/* CTAs */}
        <div className="flex items-center gap-3">
          <Link
            to="/login"
            className="hidden sm:inline-block text-xs font-semibold text-gray-400 hover:text-white transition"
          >
            Sign In
          </Link>
          <motion.div whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.96 }}>
            <Link
              to="/signup"
              className="inline-block px-5 py-2 rounded-xl bg-violet-600 hover:bg-violet-500 text-white text-xs font-bold tracking-wide transition glow-purple"
            >
              Get Started
            </Link>
          </motion.div>
        </div>
      </div>
    </motion.nav>
  );
};

// --- Hero -----------------------------------------------------------------
const HeroSection: React.FC = () => (
  <section
    className="relative min-h-screen flex flex-col items-center justify-center text-center px-6 pt-20 pb-16 overflow-hidden"
    aria-label="Hero"
  >
    {/* Radial gradient bg */}
    <div
      aria-hidden
      className="pointer-events-none absolute inset-0"
      style={{
        background:
          "radial-gradient(ellipse 90% 70% at 50% -5%, rgba(139,92,246,0.22) 0%, transparent 65%), radial-gradient(ellipse 60% 40% at 80% 90%, rgba(59,130,246,0.14) 0%, transparent 60%)",
      }}
    />
    {/* Noise */}
    <div
      aria-hidden
      className="pointer-events-none absolute inset-0 opacity-[0.03]"
      style={{
        backgroundImage:
          "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")",
      }}
    />

    {/* Floating orbs */}
    <div aria-hidden className="pointer-events-none absolute inset-0 overflow-hidden">
      {[
        { w: 320, h: 320, top: "10%", left: "5%",  color: "rgba(139,92,246,0.06)"  },
        { w: 240, h: 240, top: "55%", right: "8%",  color: "rgba(59,130,246,0.07)"  },
        { w: 180, h: 180, top: "25%", right: "20%", color: "rgba(52,211,153,0.05)"  },
      ].map((orb, i) => (
        <motion.div
          key={i}
          animate={{ y: [0, -20, 0], scale: [1, 1.05, 1] }}
          transition={{ duration: 8 + i * 2, repeat: Infinity, ease: "easeInOut" }}
          className="absolute rounded-full blur-3xl"
          style={{ width: orb.w, height: orb.h, top: orb.top, left: (orb as any).left, right: (orb as any).right, backgroundColor: orb.color }}
        />
      ))}
    </div>

    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
      className="relative z-10 space-y-6 max-w-4xl"
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border text-[11px] font-bold tracking-widest uppercase"
        style={{ borderColor: "rgba(139,92,246,0.4)", color: "#a78bfa", backgroundColor: "rgba(139,92,246,0.08)" }}
      >
        <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse" />
        AI Interactive Storytelling
      </motion.div>

      <h1 className="text-4xl sm:text-6xl lg:text-8xl font-black tracking-tight leading-[1.02]">
        <span className="text-white">Your story.</span>
        <br />
        <span
          className="bg-clip-text text-transparent"
          style={{ backgroundImage: "linear-gradient(135deg,#a78bfa 0%,#60a5fa 45%,#34d399 100%)" }}
        >
          Infinite possibilities.
        </span>
      </h1>

      <p className="text-gray-400 text-lg sm:text-xl max-w-2xl mx-auto leading-relaxed">
        Step into AI-powered worlds where every decision reshapes the narrative.
        Choose your genre. Create your character. Live your story.
      </p>

      <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4 pt-2">
        <motion.div whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.96 }}>
          <Link
            to="/signup"
            className="inline-block px-8 py-3.5 rounded-2xl bg-violet-600 hover:bg-violet-500 text-white font-bold text-sm tracking-wide transition glow-purple"
          >
            ? Start Your Journey
          </Link>
        </motion.div>
        <motion.div whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.96 }}>
          <a
            href="#how-it-works"
            className="inline-block px-8 py-3.5 rounded-2xl border text-white font-semibold text-sm tracking-wide transition"
            style={{ borderColor: "rgba(255,255,255,0.12)" }}
            onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "rgba(255,255,255,0.05)")}
            onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "transparent")}
          >
            See How It Works
          </a>
        </motion.div>
      </div>
    </motion.div>

    {/* Scroll hint */}
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 1.4 }}
      className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2"
    >
      <motion.div
        animate={{ y: [0, 8, 0] }}
        transition={{ duration: 1.6, repeat: Infinity }}
        className="w-5 h-8 rounded-full border-2 border-white/20 flex items-start justify-center pt-1.5"
      >
        <div className="w-1 h-1.5 rounded-full bg-white/40" />
      </motion.div>
    </motion.div>
  </section>
);

// --- Stats strip ----------------------------------------------------------
const StatsStrip: React.FC = () => (
  <motion.section
    variants={fadeUp}
    custom={0}
    initial="hidden"
    whileInView="visible"
    viewport={{ once: true, margin: "-60px" }}
    className="py-12 border-y"
    style={{ borderColor: "rgba(255,255,255,0.06)" }}
    aria-label="Platform statistics"
  >
    <div className="max-w-screen-xl mx-auto px-6 flex flex-wrap justify-center gap-10 sm:gap-20">
      {[
        { value: "2M+", label: "Stories Created",  color: "#a78bfa" },
        { value: "6",   label: "Unique Genres",     color: "#60a5fa" },
        { value: "8",   label: "Possible Paths",    color: "#34d399" },
        { value: "98%", label: "Player Satisfaction",color: "#fb923c" },
      ].map(({ value, label, color }) => (
        <div key={label} className="text-center">
          <div className="text-3xl font-black" style={{ color }}>{value}</div>
          <div className="text-[10px] font-bold uppercase tracking-widest mt-1" style={{ color: "rgba(156,163,175,1)" }}>{label}</div>
        </div>
      ))}
    </div>
  </motion.section>
);

// --- Features grid --------------------------------------------------------
const FEATURES = [
  { icon: "??", title: "AI-Powered Narratives",  desc: "GPT-driven stories that adapt to every choice you make � no two playthroughs are ever the same.",     color: "#a78bfa" },
  { icon: "??", title: "Infinite Story Branches", desc: "Your decisions ripple through the world. Betray an ally, reveal a secret � the story remembers.",       color: "#34d399" },
  { icon: "???", title: "6 Immersive Genres",      desc: "From rain-soaked noir to galactic exploration. Every genre is a handcrafted world with its own rules.", color: "#60a5fa" },
  { icon: "??", title: "Save & Continue",         desc: "Your progress is always safe. Pick up exactly where you left off � mid-sentence if you need to.",       color: "#fb923c" },
  { icon: "??", title: "Deep Character Creation", desc: "Choose your archetype, define your motivation, name your hero. The story reacts to who you are.",       color: "#f472b6" },
  { icon: "??", title: "Achievements & Lore",     desc: "Unlock hidden lore, earn badges, and discover secret endings as you explore each narrative thread.",     color: "#fbbf24" },
];

const FeaturesSection: React.FC = () => (
  <section id="features" className="py-24 px-6">
    <div className="max-w-screen-xl mx-auto space-y-14">
      <motion.div
        variants={fadeUp}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
        className="text-center space-y-3"
      >
        <p className="text-xs font-bold uppercase tracking-[0.2em] text-violet-400">Why Nebula</p>
        <h2 className="text-3xl sm:text-4xl font-black text-white">Everything a story deserves</h2>
        <p className="text-gray-400 max-w-lg mx-auto text-sm leading-relaxed">
          Built for immersion. Designed for replayability. Powered by AI that actually listens.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {FEATURES.map(({ icon, title, desc, color }, i) => (
          <motion.div
            key={title}
            variants={fadeUp}
            custom={i * 0.07}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            whileHover={{ y: -4 }}
            className="rounded-2xl p-6 space-y-3 transition-shadow"
            style={{
              backgroundColor: "rgba(255,255,255,0.03)",
              border: "1px solid rgba(255,255,255,0.07)",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.borderColor = `${color}44`)}
            onMouseLeave={(e) => (e.currentTarget.style.borderColor = "rgba(255,255,255,0.07)")}
          >
            <div
              className="w-11 h-11 rounded-xl flex items-center justify-center text-xl"
              style={{ backgroundColor: `${color}15`, border: `1px solid ${color}30` }}
            >
              {icon}
            </div>
            <h3 className="text-sm font-bold text-white">{title}</h3>
            <p className="text-xs text-gray-400 leading-relaxed">{desc}</p>
          </motion.div>
        ))}
      </div>
    </div>
  </section>
);

// --- Genre showcase -------------------------------------------------------
const SHOWCASE_GENRES = [
  { title: "Noir Detective",       tagline: "Solve a crime in a rain-soaked city.",  image: "https://images.unsplash.com/photo-1605806616949-1e87b487fc2f?w=800&q=80", accent: "rgba(234,179,8,0.7)"    },
  { title: "Sci-Fi Exploration",   tagline: "Discover secrets beyond the stars.",    image: "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=800&q=80", accent: "rgba(59,130,246,0.7)"   },
  { title: "Fantasy Kingdom",      tagline: "Magic, politics, and ancient power.",   image: "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=800&q=80", accent: "rgba(168,85,247,0.7)"   },
  { title: "Psychological Thriller",tagline: "Reality may not be what it seems.",   image: "https://images.unsplash.com/photo-1518895312237-a9e23508077d?w=800&q=80", accent: "rgba(239,68,68,0.7)"    },
];

const GenreShowcaseSection: React.FC = () => (
  <section id="genres" className="py-24 px-6" style={{ backgroundColor: "rgba(255,255,255,0.01)" }}>
    <div className="max-w-screen-xl mx-auto space-y-14">
      <motion.div
        variants={fadeUp}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
        className="text-center space-y-3"
      >
        <p className="text-xs font-bold uppercase tracking-[0.2em] text-blue-400">Explore the Worlds</p>
        <h2 className="text-3xl sm:text-4xl font-black text-white">Choose your reality</h2>
        <p className="text-gray-400 max-w-lg mx-auto text-sm leading-relaxed">
          Six handcrafted universes, each with unique rules, tone, and infinite story branches.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {SHOWCASE_GENRES.map(({ title, tagline, image, accent }, i) => (
          <motion.div
            key={title}
            variants={fadeUp}
            custom={i * 0.08}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            whileHover={{ scale: 1.03, y: -6 }}
            transition={{ type: "spring", stiffness: 260, damping: 20 }}
            className="relative rounded-2xl overflow-hidden cursor-pointer card-shadow group"
            style={{ height: 'clamp(200px, 30vw, 280px)' }}
          >
            <img src={image} alt={title} loading="lazy" className="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" />
            <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/30 to-transparent" />
            <motion.div
              className="absolute inset-0 rounded-2xl pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-300"
              style={{ boxShadow: `inset 0 0 0 2px ${accent}, 0 0 30px ${accent}` }}
            />
            <div className="absolute bottom-0 left-0 right-0 p-4">
              <p className="text-xs font-black uppercase tracking-widest text-white">{title}</p>
              <p className="text-[11px] text-gray-300 mt-1">{tagline}</p>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="text-center">
        <Link
          to="/login"
          className="inline-block px-8 py-3 rounded-2xl border text-white text-sm font-semibold tracking-wide transition"
          style={{ borderColor: "rgba(255,255,255,0.12)" }}
          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "rgba(255,255,255,0.05)")}
          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "transparent")}
        >
          Explore All Genres ?
        </Link>
      </div>
    </div>
  </section>
);

// --- How it works ---------------------------------------------------------
const STEPS = [
  { num: "01", title: "Choose Your Genre",    desc: "Pick from 6 cinematic worlds � each with a unique tone, atmosphere, and set of story possibilities.", color: "#a78bfa" },
  { num: "02", title: "Build Your Character", desc: "Name your hero, select your archetype and motivation. The AI will tailor every interaction to who you are.", color: "#60a5fa" },
  { num: "03", title: "Begin Your Adventure", desc: "Dive in and start making choices. Every decision matters. Every path leads somewhere unexpected.", color: "#34d399" },
];

const HowItWorksSection: React.FC = () => (
  <section id="how-it-works" className="py-24 px-6">
    <div className="max-w-screen-xl mx-auto space-y-16">
      <motion.div
        variants={fadeUp}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
        className="text-center space-y-3"
      >
        <p className="text-xs font-bold uppercase tracking-[0.2em] text-emerald-400">Get Started in Minutes</p>
        <h2 className="text-3xl sm:text-4xl font-black text-white">How it works</h2>
      </motion.div>

      <div className="grid sm:grid-cols-3 gap-8 relative">
        {/* Connector line on desktop */}
        <div
          className="hidden sm:block absolute top-8 left-[16%] right-[16%] h-px"
          style={{ backgroundColor: "rgba(255,255,255,0.06)" }}
        />

        {STEPS.map(({ num, title, desc, color }, i) => (
          <motion.div
            key={num}
            variants={fadeUp}
            custom={i * 0.12}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="text-center space-y-4"
          >
            <div
              className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto text-xl font-black"
              style={{ backgroundColor: `${color}15`, border: `1px solid ${color}30`, color }}
            >
              {num}
            </div>
            <h3 className="text-base font-bold text-white">{title}</h3>
            <p className="text-sm text-gray-400 leading-relaxed">{desc}</p>
          </motion.div>
        ))}
      </div>
    </div>
  </section>
);

// --- CTA Banner -----------------------------------------------------------
const CTASection: React.FC = () => (
  <section className="py-24 px-6">
    <motion.div
      variants={fadeUp}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true }}
      className="max-w-3xl mx-auto text-center rounded-3xl py-16 px-8 relative overflow-hidden"
      style={{ backgroundColor: "rgba(139,92,246,0.08)", border: "1px solid rgba(139,92,246,0.2)" }}
    >
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0"
        style={{ background: "radial-gradient(ellipse 80% 60% at 50% 50%, rgba(139,92,246,0.15) 0%, transparent 70%)" }}
      />
      <div className="relative space-y-6">
        <p className="text-xs font-bold uppercase tracking-[0.2em] text-violet-400">Start for Free</p>
        <h2 className="text-2xl sm:text-4xl lg:text-5xl font-black text-white leading-tight">
          Your story is<br />waiting to be told.
        </h2>
        <p className="text-gray-400 text-sm sm:text-base max-w-md mx-auto leading-relaxed">
          No subscription required to start. Pick a genre, name your character, and let the AI weave your world.
        </p>
        <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.96 }}>
          <Link
            to="/signup"
            className="inline-block px-10 py-4 rounded-2xl bg-violet-600 hover:bg-violet-500 text-white font-bold text-sm tracking-wide transition glow-purple"
          >
            ? Begin Your Adventure
          </Link>
        </motion.div>
      </div>
    </motion.div>
  </section>
);

// --- Footer ---------------------------------------------------------------
const LandingFooter: React.FC = () => (
  <footer className="border-t py-12 px-6" style={{ borderColor: "rgba(255,255,255,0.06)" }}>
    <div className="max-w-screen-xl mx-auto">
      <div className="flex flex-col sm:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-xl bg-violet-600 flex items-center justify-center">
            <span className="text-white font-black text-sm leading-none">N</span>
          </div>
          <span className="text-sm font-black tracking-tight text-white">NEBULA</span>
        </div>

        <div className="flex flex-wrap justify-center gap-6">
          {["About", "Features", "Genres", "Blog", "Careers", "Support"].map((l) => (
            <a key={l} href="#" className="text-xs text-gray-500 hover:text-white transition">{l}</a>
          ))}
        </div>

        <p className="text-xs text-gray-600">� 2026 Nebula Inc. All rights reserved.</p>
      </div>
    </div>
  </footer>
);

// --- Page -----------------------------------------------------------------
const LandingPage: React.FC = () => (
  <div className="bg-[#0a0a0f] min-h-screen overflow-x-hidden">
    <LandingNav />
    <HeroSection />
    <StatsStrip />
    <FeaturesSection />
    <GenreShowcaseSection />
    <HowItWorksSection />
    <CTASection />
    <LandingFooter />
  </div>
);

export default LandingPage;
