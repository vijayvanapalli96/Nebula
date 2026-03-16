import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import DashboardLayout from '../components/layout/DashboardLayout';
import StoryCard from '../features/stories/StoryCard';
import { useStoryStore } from '../store/storyStore';
import type { UserStory } from '../types/story';

// ── Section fade-in ───────────────────────────────────────────────────────────
const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (d: number) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.45, ease: 'easeOut' as const, delay: d },
  }),
};

// ── Empty state ───────────────────────────────────────────────────────────────
const EmptyState: React.FC = () => {
  const navigate = useNavigate();
  return (
    <motion.div
      className="flex flex-col items-center justify-center py-24 gap-6 text-center"
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div
        className="w-20 h-20 rounded-full flex items-center justify-center text-4xl"
        style={{
          background: 'radial-gradient(circle, rgba(139,92,246,0.18) 0%, rgba(139,92,246,0.04) 100%)',
          border: '1px solid rgba(139,92,246,0.25)',
        }}
      >
        📖
      </div>
      <div className="space-y-2 max-w-xs">
        <h3 className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>
          No stories yet
        </h3>
        <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
          Pick a world and begin your first adventure.
        </p>
      </div>
      <button
        onClick={() => navigate('/explore')}
        className="px-5 py-2.5 rounded-xl text-sm font-semibold text-white transition-all hover:scale-105 active:scale-95"
        style={{
          background: 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)',
          boxShadow: '0 0 20px rgba(139,92,246,0.35)',
        }}
      >
        Explore Worlds →
      </button>
    </motion.div>
  );
};

// ── Status filter options ──────────────────────────────────────────────────────
type FilterTab = 'all' | 'active' | 'completed';

const filterLabel: Record<FilterTab, string> = {
  all: 'All',
  active: 'In Progress',
  completed: 'Completed',
};

function matchesFilter(story: UserStory, filter: FilterTab): boolean {
  if (filter === 'all') return true;
  if (filter === 'active') {
    return story.status === 'active' || story.status === 'opening_scene_ready';
  }
  return story.status === 'completed';
}

// ── Page ─────────────────────────────────────────────────────────────────────
const MyStoriesPage: React.FC = () => {
  const { userStories, storiesLoading, fetchUserStories } = useStoryStore();
  const [filter, setFilter] = React.useState<FilterTab>('all');

  // Fallback fetch if landing directly
  useEffect(() => {
    fetchUserStories();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const filtered = userStories.filter((s) => matchesFilter(s, filter));

  return (
    <DashboardLayout title="My Stories">
      <div className="px-4 sm:px-6 py-6 sm:py-8 max-w-screen-xl mx-auto space-y-8">

        {/* ── Header ── */}
        <motion.div
          custom={0}
          variants={fadeUp}
          initial="hidden"
          animate="visible"
          className="space-y-1"
        >
          <p className="text-[10px] font-bold tracking-[0.2em] uppercase text-violet-400">
            Your adventures
          </p>
          <h1 className="text-2xl sm:text-3xl font-black" style={{ color: 'var(--text-primary)' }}>
            My Stories
          </h1>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            {userStories.length > 0
              ? `${userStories.length} ${userStories.length === 1 ? 'story' : 'stories'} — sorted by most recent`
              : 'Your stories will appear here once you start one.'}
          </p>
        </motion.div>

        {/* ── Filter tabs ── */}
        {userStories.length > 0 && (
          <motion.div
            custom={0.05}
            variants={fadeUp}
            initial="hidden"
            animate="visible"
            className="flex gap-2"
          >
            {(Object.keys(filterLabel) as FilterTab[]).map((tab) => (
              <button
                key={tab}
                onClick={() => setFilter(tab)}
                className="px-4 py-1.5 rounded-full text-xs font-semibold transition-all"
                style={{
                  backgroundColor: filter === tab ? 'rgba(139,92,246,0.2)' : 'var(--bg-surface)',
                  border: filter === tab ? '1px solid rgba(139,92,246,0.6)' : '1px solid var(--border-color)',
                  color: filter === tab ? '#c4b5fd' : 'var(--text-muted)',
                }}
              >
                {filterLabel[tab]}
                {tab !== 'all' && (
                  <span className="ml-1.5 opacity-70">
                    ({userStories.filter((s) => matchesFilter(s, tab)).length})
                  </span>
                )}
              </button>
            ))}
          </motion.div>
        )}

        {/* ── Grid / Loading / Empty ── */}
        {storiesLoading ? (
          <motion.div
            className="flex items-center justify-center py-24"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <div
              className="w-10 h-10 rounded-full border-2 border-violet-500 border-t-transparent animate-spin"
              style={{ boxShadow: '0 0 16px rgba(139,92,246,0.4)' }}
            />
          </motion.div>
        ) : filtered.length === 0 ? (
          <EmptyState />
        ) : (
          <motion.div
            custom={0.1}
            variants={fadeUp}
            initial="hidden"
            animate="visible"
            className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-6"
          >
            {filtered.map((story, i) => (
              <motion.div
                key={story.story_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: i * 0.05 }}
              >
                <StoryCard story={story} />
              </motion.div>
            ))}
          </motion.div>
        )}

        {/* Bottom spacer */}
        <div className="h-8" />
      </div>
    </DashboardLayout>
  );
};

export default MyStoriesPage;
