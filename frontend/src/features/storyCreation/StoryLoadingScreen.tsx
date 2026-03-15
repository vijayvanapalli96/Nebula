import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useThemeStore } from '../../store/themeStore';

const HINTS = [
  'Generating story possibilities...',
  'Exploring worlds...',
  'Designing characters...',
  'Weaving narrative threads...',
  'Preparing your journey...',
  'Crafting your universe...',
];

const StoryLoadingScreen: React.FC = () => {
  const { isDark } = useThemeStore();
  const [hintIndex, setHintIndex] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setHintIndex((i) => (i + 1) % HINTS.length), 1800);
    return () => clearInterval(id);
  }, []);

  return (
    <motion.div
      className="fixed inset-0 flex flex-col items-center justify-center overflow-hidden"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.4 }}
      style={{ backgroundColor: 'var(--bg-base)' }}
    >
      {/* Slow-shifting ambient gradient */}
      <motion.div
        className="absolute inset-0 pointer-events-none"
        animate={{
          background: [
            'radial-gradient(ellipse 80% 60% at 50% 40%, rgba(139,92,246,0.18) 0%, transparent 68%)',
            'radial-gradient(ellipse 80% 60% at 50% 40%, rgba(96,165,250,0.14) 0%, transparent 68%)',
            'radial-gradient(ellipse 80% 60% at 50% 40%, rgba(52,211,153,0.12) 0%, transparent 68%)',
            'radial-gradient(ellipse 80% 60% at 50% 40%, rgba(139,92,246,0.18) 0%, transparent 68%)',
          ],
        }}
        transition={{ duration: 9, repeat: Infinity, ease: 'linear' }}
      />

      {/* Floating orbs */}
      {[
        { size: 360, top: '4%',  left: '6%',   color: 'rgba(139,92,246,0.07)', dur: 9  },
        { size: 260, top: '58%', right: '9%',  color: 'rgba(59,130,246,0.07)',  dur: 11 },
        { size: 200, top: '28%', right: '18%', color: 'rgba(52,211,153,0.05)',  dur: 7  },
      ].map((orb, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full blur-3xl pointer-events-none"
          style={{
            width: orb.size,
            height: orb.size,
            top: orb.top,
            left: (orb as any).left,
            right: (orb as any).right,
            backgroundColor: orb.color,
          }}
          animate={{ y: [0, -28, 0], scale: [1, 1.08, 1] }}
          transition={{ duration: orb.dur, repeat: Infinity, ease: 'easeInOut' }}
        />
      ))}

      {/* Core content */}
      <div className="relative z-10 flex flex-col items-center gap-10 px-6 text-center max-w-md">
        {/* Glowing spinner */}
        <div className="relative w-16 h-16">
          <motion.div
            className="absolute inset-0 rounded-full"
            style={{ border: '2px solid rgba(139,92,246,0.2)' }}
          />
          <motion.div
            className="absolute inset-0 rounded-full"
            style={{ borderTop: '2px solid #8b5cf6', borderRight: '2px solid transparent', borderBottom: '2px solid transparent', borderLeft: '2px solid transparent' }}
            animate={{ rotate: 360 }}
            transition={{ duration: 1.1, repeat: Infinity, ease: 'linear' }}
          />
          {/* Inner glow pulse */}
          <motion.div
            className="absolute inset-3 rounded-full"
            style={{ backgroundColor: 'rgba(139,92,246,0.15)' }}
            animate={{ scale: [1, 1.3, 1], opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
          />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-2 h-2 rounded-full bg-violet-400" />
          </div>
        </div>

        {/* Heading + cycling hint */}
        <div className="space-y-3">
          <motion.h1
            className="text-2xl sm:text-3xl font-black tracking-tight"
            style={{
              backgroundImage: isDark
                ? 'linear-gradient(135deg, #f0f0f5 0%, #a78bfa 50%, #60a5fa 100%)'
                : 'linear-gradient(135deg, #1e1b4b 0%, #7c3aed 50%, #1d4ed8 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            Preparing your story world...
          </motion.h1>

          <div className="h-6 flex items-center justify-center">
            <AnimatePresence mode="wait">
              <motion.p
                key={hintIndex}
                className="text-sm font-medium"
                style={{ color: 'var(--text-secondary)' }}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -6 }}
                transition={{ duration: 0.32 }}
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
              transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.22, ease: 'easeInOut' }}
            />
          ))}
        </div>
      </div>
    </motion.div>
  );
};

export default StoryLoadingScreen;
