import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useStoryThemeStore } from '../store/storyThemeStore';
import { useStoryStore } from '../store/storyStore';

const HINTS = [
  'Exploring narrative universes…',
  'Discovering hidden worlds…',
  'Building cinematic experiences…',
  'Loading creative possibilities…',
  'Unlocking story dimensions…',
  'Preparing your adventure…',
];

// ── Glowing spinner (reused pattern) ─────────────────────────────────────────
const GlowSpinner: React.FC = () => (
  <div className="relative w-24 h-24 flex-shrink-0">
    <div
      className="absolute inset-0 rounded-full"
      style={{ border: '2px solid rgba(139,92,246,0.15)' }}
    />
    <motion.div
      className="absolute inset-0 rounded-full"
      style={{
        border: '2px solid transparent',
        borderTopColor: '#8b5cf6',
        borderRightColor: 'rgba(139,92,246,0.3)',
      }}
      animate={{ rotate: 360 }}
      transition={{ duration: 1.4, repeat: Infinity, ease: 'linear' }}
    />
    <motion.div
      className="absolute inset-3 rounded-full"
      style={{
        border: '2px solid transparent',
        borderBottomColor: '#60a5fa',
        borderLeftColor: 'rgba(96,165,250,0.3)',
      }}
      animate={{ rotate: -360 }}
      transition={{ duration: 2.1, repeat: Infinity, ease: 'linear' }}
    />
    <motion.div
      className="absolute inset-6 rounded-full"
      style={{ backgroundColor: 'rgba(139,92,246,0.25)' }}
      animate={{ scale: [1, 1.35, 1], opacity: [0.6, 1, 0.6] }}
      transition={{ duration: 1.8, repeat: Infinity, ease: 'easeInOut' }}
    />
    <div className="absolute inset-0 flex items-center justify-center">
      <div
        className="w-3 h-3 rounded-full bg-violet-400"
        style={{ boxShadow: '0 0 12px rgba(167,139,250,0.9)' }}
      />
    </div>
  </div>
);

// ── Particle ──────────────────────────────────────────────────────────────────
const Particle: React.FC<{ i: number }> = ({ i }) => {
  const angle = (i / 20) * Math.PI * 2;
  const r = 120 + (i % 5) * 28;
  const x = Math.cos(angle) * r;
  const y = Math.sin(angle) * r;
  const size = 2 + (i % 3);
  const delay = (i / 20) * 3.5;
  return (
    <motion.div
      className="absolute rounded-full"
      style={{
        width: size,
        height: size,
        left: `calc(50% + ${x}px)`,
        top: `calc(50% + ${y}px)`,
        backgroundColor: i % 3 === 0 ? '#8b5cf6' : i % 3 === 1 ? '#60a5fa' : '#34d399',
        boxShadow: `0 0 ${size * 3}px currentColor`,
      }}
      animate={{ opacity: [0, 1, 0], scale: [0.5, 1.2, 0.5] }}
      transition={{ duration: 2.8, repeat: Infinity, delay, ease: 'easeInOut' }}
    />
  );
};

// ── Page ──────────────────────────────────────────────────────────────────────
const ThemeLoadingPage: React.FC = () => {
  const navigate = useNavigate();
  const { fetchThemes, loading, error } = useStoryThemeStore();
  const { fetchUserStories } = useStoryStore();
  const [hintIndex, setHintIndex] = useState(0);

  // Rotate hints every 2 s
  useEffect(() => {
    const id = setInterval(() => setHintIndex((i) => (i + 1) % HINTS.length), 2000);
    return () => clearInterval(id);
  }, []);

  // Kick off both fetches in parallel on mount
  useEffect(() => {
    Promise.all([fetchThemes(), fetchUserStories().catch(() => { /* stories failure is non-fatal */ })])
      .then(() => navigate('/dashboard', { replace: true }))
      .catch(() => {
        // error is already written to the store by fetchThemes;
        // the retry UI below will surface it.
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div
      className="fixed inset-0 flex flex-col items-center justify-center overflow-hidden"
      style={{ backgroundColor: '#0a0a0f' }}
    >
      {/* Animated ambient background */}
      <motion.div
        className="absolute inset-0 pointer-events-none"
        animate={{
          background: [
            'radial-gradient(ellipse 80% 70% at 50% 50%, rgba(139,92,246,0.18) 0%, transparent 65%)',
            'radial-gradient(ellipse 80% 70% at 50% 50%, rgba(96,165,250,0.14) 0%, transparent 65%)',
            'radial-gradient(ellipse 80% 70% at 50% 50%, rgba(52,211,153,0.12) 0%, transparent 65%)',
            'radial-gradient(ellipse 80% 70% at 50% 50%, rgba(139,92,246,0.18) 0%, transparent 65%)',
          ],
        }}
        transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
      />

      {/* Floating orbs */}
      {[
        { s: 400, top: '5%',  left: '3%',   c: 'rgba(139,92,246,0.06)', d: 10 },
        { s: 280, top: '60%', right: '5%',  c: 'rgba(59,130,246,0.06)',  d: 13 },
        { s: 220, top: '20%', right: '15%', c: 'rgba(52,211,153,0.05)',  d: 8  },
      ].map((o, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full blur-3xl pointer-events-none"
          style={{
            width: o.s, height: o.s,
            top: o.top,
            left: (o as { left?: string }).left,
            right: (o as { right?: string }).right,
            backgroundColor: o.c,
          }}
          animate={{ y: [0, -30, 0], scale: [1, 1.07, 1] }}
          transition={{ duration: o.d, repeat: Infinity, ease: 'easeInOut' }}
        />
      ))}

      {/* Particles */}
      <div className="absolute inset-0 pointer-events-none">
        {Array.from({ length: 20 }).map((_, i) => (
          <Particle key={i} i={i} />
        ))}
      </div>

      {/* Core content */}
      <div className="relative z-10 flex flex-col items-center gap-10 text-center px-6 max-w-lg">
        <GlowSpinner />

        <div className="space-y-4">
          <motion.h1
            className="text-3xl sm:text-4xl font-black tracking-tight"
            style={{
              backgroundImage:
                'linear-gradient(135deg, #f0f0f5 0%, #a78bfa 45%, #60a5fa 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.15 }}
          >
            Preparing Your Story Worlds
          </motion.h1>

          <div className="h-6 overflow-hidden flex items-center justify-center">
            <AnimatePresence mode="wait">
              <motion.p
                key={hintIndex}
                className="text-sm font-medium"
                style={{ color: 'rgba(156,163,175,0.9)' }}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.3 }}
              >
                {HINTS[hintIndex]}
              </motion.p>
            </AnimatePresence>
          </div>
        </div>

        {/* Bouncing dots */}
        <div className="flex items-center gap-2">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className="w-1.5 h-1.5 rounded-full bg-violet-500"
              animate={{ scale: [1, 1.7, 1], opacity: [0.35, 1, 0.35] }}
              transition={{
                duration: 1.2,
                repeat: Infinity,
                delay: i * 0.22,
                ease: 'easeInOut',
              }}
            />
          ))}
        </div>

        {/* Error state */}
        {error && !loading && (
          <motion.div
            className="mt-4 px-5 py-3 rounded-xl text-sm text-red-300 space-y-3"
            style={{
              backgroundColor: 'rgba(239,68,68,0.1)',
              border: '1px solid rgba(239,68,68,0.25)',
            }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <p>{error}</p>
            <button
              onClick={() =>
                Promise.all([fetchThemes(), fetchUserStories().catch(() => {})])
                  .then(() => navigate('/dashboard', { replace: true }))
                  .catch(() => {})
              }
              className="text-xs font-semibold text-red-400 underline underline-offset-2"
            >
              Retry
            </button>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default ThemeLoadingPage;
