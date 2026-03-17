import React from 'react';
import { motion } from 'framer-motion';

interface MediaLoadingBannerProps {
  choiceCount?: number;
}

const MediaLoadingBanner: React.FC<MediaLoadingBannerProps> = ({ choiceCount = 4 }) => (
  <motion.div
    className="px-6 sm:px-10 lg:px-16 pb-14"
    initial={{ opacity: 0, y: 12 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: 8 }}
    transition={{ duration: 0.4 }}
  >
    <div
      className="rounded-2xl p-8 flex flex-col items-center gap-6"
      style={{
        background: 'rgba(0,0,0,0.35)',
        backdropFilter: 'blur(8px)',
        WebkitBackdropFilter: 'blur(8px)',
        border: '1px solid rgba(139,92,246,0.12)',
      }}
    >
      {/* Shimmer placeholder cards */}
      <div
        className="grid gap-3 w-full"
        style={{
          gridTemplateColumns: `repeat(${Math.min(choiceCount, 4)}, minmax(0, 1fr))`,
        }}
      >
        {Array.from({ length: choiceCount }).map((_, i) => (
          <motion.div
            key={i}
            className="rounded-xl"
            style={{
              height: 110,
              background:
                'linear-gradient(90deg, rgba(139,92,246,0.06) 0%, rgba(139,92,246,0.16) 50%, rgba(139,92,246,0.06) 100%)',
              backgroundSize: '200% 100%',
            }}
            animate={{ backgroundPosition: ['200% 0%', '-200% 0%'] }}
            transition={{
              duration: 1.8,
              repeat: Infinity,
              ease: 'linear',
              delay: i * 0.12,
            }}
          />
        ))}
      </div>

      {/* Pulsing dots */}
      <div className="flex items-center gap-2">
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            className="w-1.5 h-1.5 rounded-full"
            style={{ backgroundColor: '#a78bfa' }}
            animate={{ opacity: [0.3, 1, 0.3], scale: [0.8, 1.1, 0.8] }}
            transition={{
              duration: 1.2,
              repeat: Infinity,
              delay: i * 0.2,
              ease: 'easeInOut',
            }}
          />
        ))}
      </div>

      <p className="text-base font-bold tracking-wide" style={{ color: '#a78bfa' }}>
        Loading options…
      </p>
      <p
        className="text-xs tracking-widest -mt-3"
        style={{ color: 'rgba(148,163,184,0.45)' }}
      >
        Crafting your choices
      </p>
    </div>
  </motion.div>
);

export default MediaLoadingBanner;
