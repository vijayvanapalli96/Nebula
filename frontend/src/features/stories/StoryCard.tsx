import React, { memo, useCallback, useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { fetchStoryDetail } from '../../api/storyApi';
import type { UserStory } from '../../types/story';

interface StoryCardProps {
  story: UserStory;
}

function formatRelativeTime(isoDate: string | null): string {
  if (!isoDate) return 'Not played yet';
  const diff = Date.now() - new Date(isoDate).getTime();
  const minutes = Math.floor(diff / 60_000);
  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

const progressColor = (pct: number): string => {
  if (pct >= 75) return '#a78bfa'; // violet
  if (pct >= 40) return '#60a5fa'; // blue
  return '#34d399'; // emerald
};

const statusBadge = (status: string | null) => {
  switch (status) {
    case 'opening_scene_ready':
    case 'active':
      return { label: 'Active', color: '#60a5fa' };
    case 'completed':
      return { label: 'Completed', color: '#34d399' };
    case 'generating_opening_scene':
      return { label: 'Generating…', color: '#fbbf24' };
    default:
      return null;
  }
};

// Gradient fallback when no cover image is available
const COVER_GRADIENTS = [
  'linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4c1d95 100%)',
  'linear-gradient(135deg, #0c1445 0%, #1e3a5f 50%, #0f4c75 100%)',
  'linear-gradient(135deg, #064e3b 0%, #065f46 50%, #0f766e 100%)',
  'linear-gradient(135deg, #1a0533 0%, #2d1b69 50%, #4a044e 100%)',
];

function coverGradient(storyId: string): string {
  const hash = storyId.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0);
  return COVER_GRADIENTS[hash % COVER_GRADIENTS.length];
}

const StoryCard: React.FC<StoryCardProps> = ({ story }) => {
  const navigate = useNavigate();
  const [isOpening, setIsOpening] = useState(false);
  const progress = story.progress ?? 0;
  const badge = statusBadge(story.status);
  const timeLabel = formatRelativeTime(story.last_played_at ?? story.updated_at);

  const openStory = useCallback(async () => {
    if (isOpening) return;

    setIsOpening(true);
    try {
      const storyDetail = await fetchStoryDetail(story.story_id);
      navigate(`/story/${story.story_id}`, { state: { storyDetail } });
    } catch (error) {
      console.error('Failed to load story detail before navigation.', error);
      navigate(`/story/${story.story_id}`);
    } finally {
      setIsOpening(false);
    }
  }, [isOpening, navigate, story.story_id]);

  const handleClick = useCallback(() => {
    void openStory();
  }, [openStory]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        void openStory();
      }
    },
    [openStory],
  );

  return (
    <motion.article
      role="button"
      tabIndex={0}
      aria-busy={isOpening}
      aria-label={`Continue story: ${story.title}. Genre: ${story.genre}. Progress: ${progress}%.`}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      className={`relative flex-shrink-0 w-60 sm:w-72 rounded-2xl overflow-hidden cursor-pointer outline-none focus-visible:ring-2 focus-visible:ring-violet-500 card-shadow group ${
        isOpening ? 'opacity-80 pointer-events-none' : ''
      }`}
      whileHover={{ scale: 1.05, y: -6 }}
      whileTap={{ scale: 0.97 }}
      transition={{ type: 'spring', stiffness: 300, damping: 22 }}
      style={{ willChange: 'transform' }}
    >
      {/* ── Cinematic image / gradient fallback ── */}
      <div className="relative h-80 sm:h-96 overflow-hidden">
        {story.cover_image ? (
          <motion.img
            src={story.cover_image}
            alt={story.title}
            loading="lazy"
            className="w-full h-full object-cover"
            transition={{ duration: 0.4, ease: 'easeOut' }}
          />
        ) : (
          <div
            className="w-full h-full"
            style={{ background: coverGradient(story.story_id) }}
          />
        )}
        {/* dark gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent" />

        {/* glow border on hover */}
        <motion.div
          className="absolute inset-0 rounded-2xl pointer-events-none"
          initial={{ opacity: 0 }}
          whileHover={{ opacity: 1 }}
          transition={{ duration: 0.25 }}
          style={{
            boxShadow: 'inset 0 0 0 2px rgba(139,92,246,0.8), 0 0 30px rgba(139,92,246,0.4)',
          }}
        />

        {/* Status badge (top-right) */}
        {badge && (
          <div
            className="absolute top-3 right-3 text-[9px] font-bold tracking-widest uppercase px-2 py-0.5 rounded-full backdrop-blur-sm"
            style={{
              backgroundColor: 'rgba(0,0,0,0.55)',
              border: `1px solid ${badge.color}55`,
              color: badge.color,
            }}
          >
            {badge.label}
          </div>
        )}
      </div>

      {/* ── Card content ── */}
      <div className="absolute bottom-0 left-0 right-0 p-4 space-y-3">
        {/* Genre chip */}
        <span
          className="inline-block text-[10px] font-bold tracking-widest uppercase px-2 py-1 rounded-full backdrop-blur-sm border border-violet-500/50"
          style={{ backgroundColor: 'rgba(0,0,0,0.45)', color: '#c4b5fd' }}
        >
          {story.genre}
        </span>

        {/* Title */}
        <h3 className="text-sm font-bold leading-snug line-clamp-2 drop-shadow-lg" style={{ color: '#fff' }}>
          {story.title}
        </h3>

        {/* Character name or theme description as subtitle */}
        {story.character_name && story.character_name !== 'Unknown' ? (
          <p className="text-[10px]" style={{ color: 'rgba(196,181,253,0.8)' }}>
            {story.character_name}
          </p>
        ) : story.theme_description ? (
          <p className="text-[10px] line-clamp-2" style={{ color: 'rgba(156,163,175,0.75)' }}>
            {story.theme_description}
          </p>
        ) : null}

        {/* Progress bar */}
        <div aria-label={`Progress: ${progress}%`}>
          <div className="flex justify-between items-center mb-1">
            <span className="text-[10px]" style={{ color: 'rgba(209,213,219,0.85)' }}>Progress</span>
            <span
              className="text-[10px] font-semibold"
              style={{ color: progressColor(progress) }}
            >
              {progress}%
            </span>
          </div>
          <div className="h-1.5 rounded-full overflow-hidden" style={{ backgroundColor: 'rgba(0,0,0,0.35)' }}>
            <motion.div
              className="h-full rounded-full"
              style={{ backgroundColor: progressColor(progress) }}
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 1.2, ease: 'easeOut', delay: 0.2 }}
            />
          </div>
        </div>

        {/* Timestamp */}
        <p className="text-[10px]" style={{ color: 'rgba(156,163,175,0.9)' }}>
          Last played {timeLabel}
        </p>
      </div>
    </motion.article>
  );
};

export default memo(StoryCard);
