import React, { memo } from 'react';
import { motion } from 'framer-motion';
import type { SceneDocChoice } from '../../types/story';

interface ChoiceCardProps {
  choice: SceneDocChoice;
  /** This choice was the one selected by the user. */
  isSelected: boolean;
  /** Another choice was selected — this one is dimmed and non-interactive. */
  isLocked: boolean;
  index: number;
  onClick?: () => void;
}

const ChoiceCard: React.FC<ChoiceCardProps> = memo(
  ({ choice, isSelected, isLocked, index, onClick }) => {
    // imageUrl is already a full https:// URL — normalised by storyViewerStore
    const imageUrl = choice.imageUrl;
    const isInteractive = !isLocked && !!onClick;

    const handleKeyDown = (e: React.KeyboardEvent) => {
      if ((e.key === 'Enter' || e.key === ' ') && isInteractive) {
        e.preventDefault();
        onClick?.();
      }
    };

    return (
      <motion.div
        role={isInteractive ? 'button' : 'article'}
        tabIndex={isInteractive ? 0 : -1}
        aria-pressed={isSelected || undefined}
        onClick={isInteractive ? onClick : undefined}
        onKeyDown={handleKeyDown}
        className="relative rounded-2xl overflow-hidden focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500 flex flex-col"
        style={{
          border: isSelected
            ? '2px solid rgba(167,139,250,0.85)'
            : '1px solid rgba(255,255,255,0.09)',
          boxShadow: isSelected
            ? '0 0 36px rgba(139,92,246,0.4), inset 0 0 48px rgba(139,92,246,0.06)'
            : '0 2px 20px rgba(0,0,0,0.45)',
          opacity: isLocked && !isSelected ? 0.35 : 1,
          cursor: isLocked && !isSelected ? 'default' : isInteractive ? 'pointer' : 'default',
          backgroundColor: 'rgba(18,14,38,1)',
        }}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: isLocked && !isSelected ? 0.35 : 1, y: 0 }}
        transition={{ duration: 0.4, delay: index * 0.08 }}
        whileHover={
          isInteractive
            ? {
                scale: 1.03,
                y: -4,
                boxShadow:
                  '0 20px 56px rgba(139,92,246,0.32), 0 0 0 1.5px rgba(167,139,250,0.55)',
              }
            : {}
        }
        whileTap={isInteractive ? { scale: 0.97 } : {}}
      >
        {/* ── Image section ── */}
        <div className="relative w-full overflow-hidden flex-shrink-0" style={{ height: 220 }}>
          {imageUrl ? (
            <img
              src={imageUrl}
              alt={choice.choiceText}
              className="w-full h-full object-cover"
              loading="lazy"
            />
          ) : (
            <div
              className="w-full h-full"
              style={{
                background:
                  'linear-gradient(135deg, rgba(88,28,235,0.35) 0%, rgba(14,11,32,0.95) 100%)',
              }}
            />
          )}
          {/* Fade image edge into card body */}
          <div
            className="absolute bottom-0 left-0 right-0 h-10 pointer-events-none"
            style={{ background: 'linear-gradient(to top, rgba(18,14,38,1) 0%, transparent 100%)' }}
          />
          {/* Selected animated ring */}
          {isSelected && (
            <motion.div
              className="absolute inset-0 pointer-events-none"
              style={{ border: '2px solid rgba(167,139,250,0.45)' }}
              animate={{ opacity: [0.35, 0.85, 0.35] }}
              transition={{ duration: 2.4, repeat: Infinity, ease: 'easeInOut' }}
            />
          )}
        </div>

        {/* ── Text section — always visible ── */}
        <div className="px-5 pt-3 pb-5 space-y-2 flex-1">
          {isSelected && (
            <span
              className="inline-flex items-center gap-1 text-[9px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full"
              style={{
                backgroundColor: 'rgba(139,92,246,0.4)',
                color: '#ede9fe',
                border: '1px solid rgba(167,139,250,0.45)',
              }}
            >
              <span className="w-1.5 h-1.5 rounded-full bg-violet-300 inline-block" />
              Selected
            </span>
          )}
          <p className="text-[15px] sm:text-base font-bold leading-snug text-white">
            {choice.choiceText}
          </p>
          {choice.directionHint && (
            <p
              className="text-xs sm:text-[13px] leading-relaxed"
              style={{ color: 'rgba(203,213,225,0.62)' }}
            >
              {choice.directionHint}
            </p>
          )}
        </div>

        {/* Hover shine overlay */}
        {isInteractive && (
          <motion.div
            className="absolute inset-0 pointer-events-none opacity-0 rounded-2xl"
            style={{
              background:
                'radial-gradient(ellipse at 50% 0%, rgba(167,139,250,0.1) 0%, transparent 60%)',
            }}
            whileHover={{ opacity: 1 }}
            transition={{ duration: 0.2 }}
          />
        )}
      </motion.div>
    );
  },
);

ChoiceCard.displayName = 'ChoiceCard';
export default ChoiceCard;
