import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import type { Genre } from '../types/story';

interface ThemeCardProps {
  theme: Genre;
  onClick?: () => void;
  /** Visual size variant – controls card height */
  size?: 'sm' | 'md' | 'lg';
  /** Delay for stagger entrance animation */
  delay?: number;
}

const HEIGHT: Record<NonNullable<ThemeCardProps['size']>, string> = {
  sm: 'h-52',
  md: 'h-64',
  lg: 'h-80',
};

const ThemeCard: React.FC<ThemeCardProps> = React.memo(
  ({ theme, onClick, size = 'md', delay = 0 }) => {
    const navigate = useNavigate();

    const handleClick = () => {
      if (onClick) {
        onClick();
      } else {
        navigate('/story/create', { state: { genre: theme } });
      }
    };

    return (
      <motion.article
        className={`relative ${HEIGHT[size]} rounded-2xl overflow-hidden cursor-pointer group`}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay, ease: 'easeOut' }}
        whileHover={{ scale: 1.025, y: -4 }}
        onClick={handleClick}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && handleClick()}
        aria-label={`Start a story in ${theme.title}`}
        style={{
          border: '1px solid rgba(255,255,255,0.07)',
          boxShadow: '0 4px 24px rgba(0,0,0,0.35)',
        }}
      >
        {/* Background image */}
        {theme.image && (
          <motion.div
            className="absolute inset-0 bg-cover bg-center"
            style={{ backgroundImage: `url(${theme.image})` }}
            whileHover={{ scale: 1.08 }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
          />
        )}

        {/* Gradient scrim */}
        <div
          className="absolute inset-0"
          style={{
            background: `linear-gradient(
              to top,
              rgba(0,0,0,0.88) 0%,
              rgba(0,0,0,0.45) 45%,
              rgba(0,0,0,0.12) 100%
            )`,
          }}
        />

        {/* Accent glow on hover */}
        <motion.div
          className="absolute inset-0 rounded-2xl pointer-events-none"
          style={{
            border: `1.5px solid ${theme.accentColor ?? 'rgba(139,92,246,0.6)'}`,
            opacity: 0,
          }}
          whileHover={{ opacity: 1 }}
          transition={{ duration: 0.25 }}
        />

        {/* Top accent badge */}
        <div className="absolute top-3 right-3">
          <div
            className="w-2 h-2 rounded-full"
            style={{
              backgroundColor: theme.accentColor ?? '#8b5cf6',
              boxShadow: `0 0 8px ${theme.accentColor ?? '#8b5cf6'}`,
            }}
          />
        </div>

        {/* Bottom text content */}
        <div className="absolute bottom-0 left-0 right-0 p-4 space-y-1">
          <h3
            className="font-bold text-base sm:text-lg leading-tight text-white line-clamp-1"
            style={{ textShadow: '0 2px 8px rgba(0,0,0,0.7)' }}
          >
            {theme.title}
          </h3>

          {/* Tagline slides up on hover */}
          <motion.p
            className="text-xs sm:text-sm font-medium line-clamp-2 leading-snug"
            style={{ color: 'rgba(209,213,219,0.85)' }}
            initial={{ opacity: 0, y: 6 }}
            whileHover={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25 }}
          >
            {theme.tagline}
          </motion.p>

          {/* CTA on hover */}
          <motion.div
            className="flex items-center gap-1 pt-0.5"
            initial={{ opacity: 0 }}
            whileHover={{ opacity: 1 }}
            transition={{ duration: 0.25, delay: 0.05 }}
          >
            <span
              className="text-xs font-semibold tracking-wide"
              style={{ color: theme.accentColor ?? '#a78bfa' }}
            >
              Enter World →
            </span>
          </motion.div>
        </div>
      </motion.article>
    );
  },
);

ThemeCard.displayName = 'ThemeCard';

export default ThemeCard;
