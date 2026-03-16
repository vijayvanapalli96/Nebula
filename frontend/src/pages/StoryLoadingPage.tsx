import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const STORY_HINTS = [
  'Recovering your story…',
  'Rebuilding the world…',
  'Summoning forgotten memories…',
  'Piecing together your journey…',
  'Awakening the narrative…',
  'Restoring your choices…',
  'Traversing the timeline…',
];

interface StoryLoadingPageProps {
  title?: string | null;
  genre?: string | null;
  characterName?: string | null;
}

// ── Glow spinner ──────────────────────────────────────────────────────────────
const GlowSpinner: React.FC = () => (
  <div className="relative w-20 h-20 flex-shrink-0">
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
        className="w-2.5 h-2.5 rounded-full bg-violet-400"
        style={{ boxShadow: '0 0 10px rgba(167,139,250,0.9)' }}
      />
    </div>
  </div>
);

// ── Page ──────────────────────────────────────────────────────────────────────
const StoryLoadingPage: React.FC<StoryLoadingPageProps> = ({ title, genre, characterName }) => {
  const [hintIndex, setHintIndex] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setHintIndex((i) => (i + 1) % STORY_HINTS.length), 2200);
    return () => clearInterval(id);
  }, []);

  return (
    <div
      className="fixed inset-0 flex flex-col items-center justify-center overflow-hidden"
      style={{ backgroundColor: '#0a0a0f' }}
    >
      {/* Ambient glow */}
      <motion.div
        className="absolute inset-0 pointer-events-none"
        animate={{
          background: [
            'radial-gradient(ellipse 80% 70% at 50% 50%, rgba(139,92,246,0.15) 0%, transparent 65%)',
            'radial-gradient(ellipse 80% 70% at 50% 50%, rgba(96,165,250,0.12) 0%, transparent 65%)',
            'radial-gradient(ellipse 80% 70% at 50% 50%, rgba(139,92,246,0.15) 0%, transparent 65%)',
          ],
        }}
        transition={{ duration: 7, repeat: Infinity, ease: 'linear' }}
      />

      {/* Floating orbs */}
      {[
        { s: 320, top: '8%',  left: '5%',  c: 'rgba(139,92,246,0.05)', d: 9  },
        { s: 240, top: '65%', right: '8%', c: 'rgba(59,130,246,0.05)',  d: 12 },
      ].map((o, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full blur-3xl pointer-events-none"
          style={{
            width: o.s,
            height: o.s,
            top: o.top,
            left: (o as { left?: string }).left,
            right: (o as { right?: string }).right,
            backgroundColor: o.c,
          }}
          animate={{ y: [0, -25, 0], scale: [1, 1.06, 1] }}
          transition={{ duration: o.d, repeat: Infinity, ease: 'easeInOut' }}
        />
      ))}

      {/* Core content */}
      <div className="relative z-10 flex flex-col items-center gap-8 text-center px-6 max-w-md">
        <GlowSpinner />

        <div className="space-y-4">
          {title ? (
            <motion.div
              className="space-y-1.5"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              {genre && (
                <p
                  className="text-[10px] font-bold tracking-[0.2em] uppercase"
                  style={{ color: 'rgba(167,139,250,0.7)' }}
                >
                  {genre}
                </p>
              )}
              <h1
                className="text-2xl sm:text-3xl font-black tracking-tight"
                style={{ color: 'var(--text-primary)' }}
              >
                {title}
              </h1>
              {characterName && (
                <p className="text-sm" style={{ color: 'rgba(156,163,175,0.7)' }}>
                  {characterName}
                </p>
              )}
            </motion.div>
          ) : (
            <motion.h1
              className="text-2xl sm:text-3xl font-black tracking-tight"
              style={{
                backgroundImage: 'linear-gradient(135deg, #f0f0f5 0%, #a78bfa 45%, #60a5fa 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              Loading Story
            </motion.h1>
          )}

          {/* Rotating hint */}
          <div className="h-5 overflow-hidden flex items-center justify-center">
            <AnimatePresence mode="wait">
              <motion.p
                key={hintIndex}
                className="text-sm"
                style={{ color: 'rgba(156,163,175,0.8)' }}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -6 }}
                transition={{ duration: 0.3 }}
              >
                {STORY_HINTS[hintIndex]}
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
              transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.22, ease: 'easeInOut' }}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default StoryLoadingPage;
