import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import DashboardLayout from '../components/layout/DashboardLayout';
import StoryCarousel from '../features/stories/StoryCarousel';
import GenreCarousel from '../features/stories/GenreCarousel';
import CreateStoryModal from '../features/stories/CreateStoryModal';
import { useStoryStore } from '../store/storyStore';
import { useStoryThemeStore } from '../store/storyThemeStore';

// ── Quick stat card ────────────────────────────────────────────────────────
const StatCard: React.FC<{ label: string; value: number | string; accent?: string }> = ({
  label,
  value,
  accent = '#8b5cf6',
}) => (
  <div
    className="rounded-2xl px-3 sm:px-5 py-3 sm:py-4 space-y-1"
    style={{
      backgroundColor: 'var(--bg-surface)',
      border: '1px solid var(--border-color)',
    }}
  >
    <p className="text-xl sm:text-2xl font-black" style={{ color: accent }}>
      {value}
    </p>
    <p className="text-xs font-semibold uppercase tracking-widest" style={{ color: 'var(--text-muted)' }}>
      {label}
    </p>
  </div>
);

// ── Section header ─────────────────────────────────────────────────────────
const SectionHeader: React.FC<{
  eyebrow: string;
  title: string;
  eyebrowColor?: string;
  action?: React.ReactNode;
}> = ({ eyebrow, title, eyebrowColor = 'text-violet-400', action }) => (
  <div className="flex items-end justify-between px-1">
    <div>
      <p className={`text-[10px] font-bold tracking-[0.2em] uppercase mb-1 ${eyebrowColor}`}>
        {eyebrow}
      </p>
      <h2 className="text-xl font-black" style={{ color: 'var(--text-primary)' }}>
        {title}
      </h2>
    </div>
    {action}
  </div>
);

// ─── Section fade-in ───────────────────────────────────────────────────────
const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (d: number) => ({
    opacity: 1, y: 0,
    transition: { duration: 0.5, ease: 'easeOut' as const, delay: d },
  }),
};

// ─── Page ─────────────────────────────────────────────────────────────────
const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { userStories, featuredUserStories, fetchUserStories } = useStoryStore();
  const { featuredThemes, themes, fetchThemes } = useStoryThemeStore();

  // Fallback: fetch if the user lands here without going through /loading
  useEffect(() => {
    fetchThemes();
    fetchUserStories();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const hour = new Date().getHours();
  const greeting =
    hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening';

  const inProgress = userStories.filter((s) => s.status === 'active' || s.status === 'opening_scene_ready').length;
  const completed  = userStories.filter((s) => s.status === 'completed').length;

  return (
    <DashboardLayout title="Dashboard">
      <div className="px-4 sm:px-6 py-6 sm:py-8 space-y-10 sm:space-y-12 max-w-screen-xl mx-auto">

        {/* ── Greeting ── */}
        <motion.div
          custom={0}
          variants={fadeUp}
          initial="hidden"
          animate="visible"
          className="space-y-1"
        >
          <p className="text-violet-400 text-sm font-semibold tracking-wide">
            {greeting} 👋
          </p>
          <h2 className="text-xl sm:text-2xl md:text-3xl font-black" style={{ color: 'var(--text-primary)' }}>
            Welcome back, Tarang
          </h2>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            {inProgress > 0
              ? `You have ${inProgress} ${inProgress === 1 ? 'story' : 'stories'} in progress.`
              : userStories.length > 0
              ? 'All caught up! Ready to start a new adventure?'
              : 'Ready to begin your first adventure?'}
          </p>
        </motion.div>

        {/* ── Quick stats ── */}
        <motion.div
          custom={0.1}
          variants={fadeUp}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-3 gap-3 sm:gap-4 w-full max-w-sm"
        >
          <StatCard label="In Progress" value={inProgress} accent="#8b5cf6" />
          <StatCard label="Completed"   value={completed}  accent="#34d399" />
          <StatCard label="Worlds"      value={themes.length} accent="#60a5fa" />
        </motion.div>

        {/* ── Continue Your Stories ── */}
        <motion.section
          custom={0.2}
          variants={fadeUp}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          aria-labelledby="continue-heading"
          className="space-y-4"
        >
          <SectionHeader
            eyebrow="Pick up where you left off"
            title="Continue Your Stories"
            action={
              userStories.length > 4 ? (
                <button
                  onClick={() => navigate('/my-stories')}
                  className="text-xs font-semibold text-violet-400 hover:text-violet-300 transition whitespace-nowrap"
                >
                  View all →
                </button>
              ) : null
            }
          />
          <StoryCarousel stories={featuredUserStories} />
        </motion.section>

        {/* ── Start a New Story ── */}
        <motion.section
          custom={0.3}
          variants={fadeUp}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          aria-labelledby="new-story-heading"
          className="space-y-4"
        >
          <SectionHeader
            eyebrow="Choose your world"
            title="Start a New Story"
            eyebrowColor="text-blue-400"
            action={
              <button
                onClick={() => navigate('/explore')}
                className="text-xs font-semibold text-blue-400 hover:text-blue-300 transition whitespace-nowrap"
              >
                Explore All Worlds →
              </button>
            }
          />
          <GenreCarousel genres={featuredThemes} />
        </motion.section>

        {/* bottom padding */}
        <div className="h-8" />
      </div>

      {/* Global modal */}
      <CreateStoryModal />
    </DashboardLayout>
  );
};

export default DashboardPage;
