import React, { useRef, useCallback } from 'react';
import { motion } from 'framer-motion';
import StoryCard from './StoryCard';
import type { UserStory } from '../../types/story';

interface StoryCarouselProps {
  stories: UserStory[];
}

const StoryCarousel: React.FC<StoryCarouselProps> = ({ stories }) => {
  const trackRef = useRef<HTMLDivElement>(null);

  const scroll = useCallback((dir: 'left' | 'right') => {
    const el = trackRef.current;
    if (!el) return;
    el.scrollBy({ left: dir === 'left' ? -320 : 320, behavior: 'smooth' });
  }, []);

  if (stories.length === 0) {
    return (
      <p className="text-gray-500 text-sm pl-4">
        No stories yet. Start a new one below!
      </p>
    );
  }

  return (
    <div className="relative group/carousel">
      {/* Left chevron */}
      <button
        aria-label="Scroll left"
        onClick={() => scroll('left')}
        className="absolute left-0 top-1/2 -translate-y-1/2 z-10 hidden sm:flex items-center justify-center w-10 h-10 rounded-full bg-black/60 backdrop-blur-sm border border-white/10 text-white opacity-0 group-hover/carousel:opacity-100 transition-opacity duration-200 hover:bg-violet-600/60 -translate-x-4"
      >
        ‹
      </button>

      {/* Scrollable track */}
      <div
        ref={trackRef}
        role="list"
        className="flex gap-4 overflow-x-auto scrollbar-hide pl-6 pr-4 pt-6 pb-4"
        style={{ scrollSnapType: 'x mandatory' }}
      >
        {stories.map((story) => (
          <motion.div
            key={story.story_id}
            role="listitem"
            style={{ scrollSnapAlign: 'start' }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            <StoryCard story={story} />
          </motion.div>
        ))}
      </div>

      {/* Right chevron */}
      <button
        aria-label="Scroll right"
        onClick={() => scroll('right')}
        className="absolute right-0 top-1/2 -translate-y-1/2 z-10 hidden sm:flex items-center justify-center w-10 h-10 rounded-full bg-black/60 backdrop-blur-sm border border-white/10 text-white opacity-0 group-hover/carousel:opacity-100 transition-opacity duration-200 hover:bg-violet-600/60 translate-x-4"
      >
        ›
      </button>
    </div>
  );
};

export default StoryCarousel;
