import React, { memo, useState } from 'react';
import { motion } from 'framer-motion';
import type { QuestionOption } from '../../store/storyCreationStore';

interface OptionCardProps {
  option: QuestionOption;
  selected: boolean;
  onClick: () => void;
  /** Stagger delay for entrance animation */
  delay?: number;
}

const OptionCard: React.FC<OptionCardProps> = ({ option, selected, onClick, delay = 0 }) => {
  const [hovered, setHovered] = useState(false);

  return (
    <motion.button
      onClick={onClick}
      onHoverStart={() => setHovered(true)}
      onHoverEnd={() => setHovered(false)}
      initial={{ opacity: 0, y: 24, scale: 0.96 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      whileTap={{ scale: 0.96 }}
      transition={{ duration: 0.4, ease: 'easeOut', delay }}
      className="relative w-full overflow-hidden rounded-2xl outline-none focus-visible:ring-2 focus-visible:ring-violet-500 cursor-pointer"
      style={{ aspectRatio: '4/3' }}
      aria-pressed={selected}
    >
      {/* ── Image ── */}
      <motion.img
        src={option.image}
        alt={option.label}
        loading="lazy"
        draggable={false}
        className="absolute inset-0 w-full h-full object-cover"
        animate={{ scale: hovered || selected ? 1.08 : 1 }}
        transition={{ duration: 0.45, ease: 'easeOut' }}
      />

      {/* ── Base gradient scrim ── */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/30 to-transparent" />

      {/* ── Hover / selected overlay ── */}
      <motion.div
        className="absolute inset-0"
        animate={{
          backgroundColor: selected
            ? 'rgba(139,92,246,0.28)'
            : hovered
            ? 'rgba(139,92,246,0.12)'
            : 'rgba(0,0,0,0)',
        }}
        transition={{ duration: 0.22 }}
      />

      {/* ── Selected / hover border ring ── */}
      <motion.div
        className="absolute inset-0 rounded-2xl pointer-events-none"
        animate={{
          boxShadow: selected
            ? 'inset 0 0 0 2px rgba(139,92,246,0.9), 0 0 28px rgba(139,92,246,0.35)'
            : hovered
            ? 'inset 0 0 0 1.5px rgba(139,92,246,0.45)'
            : 'inset 0 0 0 1.5px rgba(255,255,255,0.06)',
        }}
        transition={{ duration: 0.22 }}
      />

      {/* ── Selected checkmark ── */}
      {selected && (
        <motion.div
          className="absolute top-3 right-3 w-6 h-6 rounded-full bg-violet-500 flex items-center justify-center"
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: 'spring', stiffness: 420, damping: 22 }}
          style={{ boxShadow: '0 0 12px rgba(139,92,246,0.7)' }}
        >
          <svg width="10" height="8" viewBox="0 0 10 8" fill="none">
            <path
              d="M1 4L3.5 6.5L9 1"
              stroke="white"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </motion.div>
      )}

      {/* ── Label ── */}
      <div className="absolute inset-x-0 bottom-0 p-3 sm:p-4">
        <p
          className="text-sm sm:text-base font-bold leading-snug text-white drop-shadow-lg"
          style={{ textShadow: '0 1px 8px rgba(0,0,0,0.8)' }}
        >
          {option.label}
        </p>
      </div>
    </motion.button>
  );
};

export default memo(OptionCard);
