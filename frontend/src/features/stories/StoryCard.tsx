import React, { memo, useCallback } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import type { Story } from '../../types/story';

interface StoryCardProps {
  story: Story;
}

function formatRelativeTime(isoDate: string): string {
  const diff = Date.now() - new Date(isoDate).getTime();
  const minutes = Math.floor(diff / 60_000);
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

const StoryCard: React.FC<StoryCardProps> = ({ story }) => {
  const navigate = useNavigate();

  const handleClick = useCallback(() => {
    navigate(`/story/${story.id}`);
  }, [navigate, story.id]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        navigate(`/story/${story.id}`);
      }
    },
    [navigate, story.id],
  );

  return (
    <motion.article
      role="button"
      tabIndex={0}
      aria-label={`Continue story: ${story.title}. Genre: ${story.genre}. Progress: ${story.progress}%.`}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      className="relative flex-shrink-0 w-60 sm:w-72 rounded-2xl overflow-hidden cursor-pointer outline-none focus-visible:ring-2 focus-visible:ring-violet-500 card-shadow group"
      whileHover={{ scale: 1.05, y: -6 }}
      whileTap={{ scale: 0.97 }}
      transition={{ type: 'spring', stiffness: 300, damping: 22 }}
      style={{ willChange: 'transform' }}
    >
      {/* ── Cinematic image ── */}
      <div className="relative h-80 sm:h-96 overflow-hidden">
        <motion.img
          src={story.coverImage}
          alt={story.title}
          loading="lazy"
          className="w-full h-full object-cover"
          transition={{ duration: 0.4, ease: 'easeOut' }}
        />
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
      </div>

      {/* ── Card content ── */}
      <div className="absolute bottom-0 left-0 right-0 p-4 space-y-3">
        {/* Genre chip */}
        <span className="inline-block text-[10px] font-bold tracking-widest uppercase px-2 py-1 rounded-full backdrop-blur-sm border border-violet-500/50"
          style={{ backgroundColor: 'rgba(0,0,0,0.45)', color: '#c4b5fd' }}>
          {story.genre}
        </span>

        {/* Title */}
        <h3 className="text-sm font-bold leading-snug line-clamp-2 drop-shadow-lg" style={{ color: '#fff' }}>
          {story.title}
        </h3>

        {/* Progress bar */}
        <div aria-label={`Progress: ${story.progress}%`}>
          <div className="flex justify-between items-center mb-1">
            <span className="text-[10px]" style={{ color: 'rgba(209,213,219,0.85)' }}>Progress</span>
            <span
              className="text-[10px] font-semibold"
              style={{ color: progressColor(story.progress) }}
            >
              {story.progress}%
            </span>
          </div>
          <div className="h-1.5 rounded-full overflow-hidden" style={{ backgroundColor: 'rgba(0,0,0,0.35)' }}>
            <motion.div
              className="h-full rounded-full"
              style={{ backgroundColor: progressColor(story.progress) }}
              initial={{ width: 0 }}
              animate={{ width: `${story.progress}%` }}
              transition={{ duration: 1.2, ease: 'easeOut', delay: 0.2 }}
            />
          </div>
        </div>

        {/* Timestamp */}
        <p className="text-[10px]" style={{ color: 'rgba(156,163,175,0.9)' }}>
          Last played {formatRelativeTime(story.lastPlayed)}
        </p>
      </div>
    </motion.article>
  );
};

export default memo(StoryCard);
