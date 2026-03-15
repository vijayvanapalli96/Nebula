import React, { useRef, useCallback } from 'react';
import { motion } from 'framer-motion';
import GenreCard from './GenreCard';
import type { Genre } from '../../types/story';

interface GenreCarouselProps {
  genres: Genre[];
}

const GenreCarousel: React.FC<GenreCarouselProps> = ({ genres }) => {
  const trackRef = useRef<HTMLDivElement>(null);

  const scroll = useCallback((dir: 'left' | 'right') => {
    const el = trackRef.current;
    if (!el) return;
    el.scrollBy({ left: dir === 'left' ? -320 : 320, behavior: 'smooth' });
  }, []);

  return (
    <div className="relative group/carousel">
      {/* Left chevron */}
      <button
        aria-label="Scroll genres left"
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
        {genres.map((genre, i) => (
          <motion.div
            key={genre.id}
            role="listitem"
            style={{ scrollSnapAlign: 'start' }}
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: i * 0.07 }}
          >
            <GenreCard genre={genre} />
          </motion.div>
        ))}
      </div>

      {/* Right chevron */}
      <button
        aria-label="Scroll genres right"
        onClick={() => scroll('right')}
        className="absolute right-0 top-1/2 -translate-y-1/2 z-10 hidden sm:flex items-center justify-center w-10 h-10 rounded-full bg-black/60 backdrop-blur-sm border border-white/10 text-white opacity-0 group-hover/carousel:opacity-100 transition-opacity duration-200 hover:bg-violet-600/60 translate-x-4"
      >
        ›
      </button>
    </div>
  );
};

export default GenreCarousel;
