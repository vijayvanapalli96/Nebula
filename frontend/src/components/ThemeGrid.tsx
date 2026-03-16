import React from 'react';
import { motion } from 'framer-motion';
import ThemeCard from './ThemeCard';
import type { Genre } from '../types/story';

interface ThemeGridProps {
  themes: Genre[];
  loading?: boolean;
  /** Card height variant forwarded to ThemeCard */
  cardSize?: 'sm' | 'md' | 'lg';
}

// ── Skeleton card ─────────────────────────────────────────────────────────────
const SkeletonCard: React.FC<{ delay: number }> = ({ delay }) => (
  <motion.div
    className="h-64 rounded-2xl overflow-hidden"
    style={{ backgroundColor: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.06)' }}
    animate={{ opacity: [0.4, 0.7, 0.4] }}
    transition={{ duration: 1.6, repeat: Infinity, delay, ease: 'easeInOut' }}
  >
    {/* Shimmer */}
    <motion.div
      className="h-full w-full"
      style={{
        background:
          'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.05) 50%, transparent 100%)',
        backgroundSize: '200% 100%',
      }}
      animate={{ backgroundPosition: ['200% 0', '-200% 0'] }}
      transition={{ duration: 1.8, repeat: Infinity, delay, ease: 'linear' }}
    />
  </motion.div>
);

// ── Grid ──────────────────────────────────────────────────────────────────────
const ThemeGrid: React.FC<ThemeGridProps> = React.memo(
  ({ themes, loading = false, cardSize = 'md' }) => {
    if (loading) {
      return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-5">
          {Array.from({ length: 8 }).map((_, i) => (
            <SkeletonCard key={i} delay={i * 0.1} />
          ))}
        </div>
      );
    }

    if (themes.length === 0) {
      return (
        <div className="flex flex-col items-center justify-center py-20 gap-3">
          <p className="text-lg font-semibold" style={{ color: 'var(--text-secondary)' }}>
            No worlds found
          </p>
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            Check your connection and try again.
          </p>
        </div>
      );
    }

    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-5">
        {themes.map((theme, i) => (
          <ThemeCard
            key={theme.id}
            theme={theme}
            size={cardSize}
            delay={i * 0.06}
          />
        ))}
      </div>
    );
  },
);

ThemeGrid.displayName = 'ThemeGrid';

export default ThemeGrid;
