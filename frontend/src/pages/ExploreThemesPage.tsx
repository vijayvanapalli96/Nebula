import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import DashboardLayout from '../components/layout/DashboardLayout';
import ThemeGrid from '../components/ThemeGrid';
import { useStoryThemeStore } from '../store/storyThemeStore';

const ExploreThemesPage: React.FC = () => {
  const { themes, loading, fetchThemes } = useStoryThemeStore();

  // Fetch if navigated directly (store not populated yet)
  useEffect(() => {
    fetchThemes();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <DashboardLayout>
      <div className="min-h-full">
        {/* ── Cinematic hero header ── */}
        <div className="relative px-6 pt-10 pb-12 overflow-hidden">
          {/* Ambient glow behind the header */}
          <div
            className="absolute inset-0 pointer-events-none"
            style={{
              background:
                'radial-gradient(ellipse 70% 80% at 50% 0%, rgba(139,92,246,0.12) 0%, transparent 70%)',
            }}
          />

          <div className="relative z-10 max-w-4xl">
            <motion.div
              className="flex items-center gap-2 mb-4"
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.45 }}
            >
              <span
                className="text-xs font-semibold tracking-widest uppercase"
                style={{ color: 'rgba(139,92,246,0.85)' }}
              >
                Story Worlds
              </span>
            </motion.div>

            <motion.h1
              className="text-4xl sm:text-5xl font-black tracking-tight mb-3"
              style={{ color: 'var(--text-primary)' }}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.05 }}
            >
              Explore All Worlds
            </motion.h1>

            <motion.p
              className="text-base sm:text-lg max-w-xl"
              style={{ color: 'var(--text-secondary)' }}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.12 }}
            >
              Find your next narrative adventure. Every world holds a story waiting for you.
            </motion.p>

            {/* Theme count badge */}
            {!loading && themes.length > 0 && (
              <motion.div
                className="mt-4 inline-flex items-center gap-2 px-3 py-1.5 rounded-full"
                style={{
                  backgroundColor: 'rgba(139,92,246,0.1)',
                  border: '1px solid rgba(139,92,246,0.2)',
                }}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3, delay: 0.25 }}
              >
                <div
                  className="w-1.5 h-1.5 rounded-full bg-violet-400"
                  style={{ boxShadow: '0 0 6px rgba(167,139,250,0.8)' }}
                />
                <span
                  className="text-xs font-semibold"
                  style={{ color: 'rgba(167,139,250,0.9)' }}
                >
                  {themes.length} worlds available
                </span>
              </motion.div>
            )}
          </div>
        </div>

        {/* ── Theme grid ── */}
        <div className="px-6 pb-16">
          <ThemeGrid themes={themes} loading={loading} cardSize="md" />
        </div>
      </div>
    </DashboardLayout>
  );
};

export default ExploreThemesPage;
