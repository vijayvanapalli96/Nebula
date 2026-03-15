import React, { memo } from 'react';
import { motion } from 'framer-motion';
import { useThemeStore } from '../../store/themeStore';

interface ProgressBarProps {
  /** 0-based index of the current step. */
  current: number;
  /** Total number of steps (questions only, not including custom-input screen). */
  total: number;
  /** If true, show "Final step" label instead of "Question N of M". */
  isFinalStep?: boolean;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ current, total, isFinalStep = false }) => {
  const { isDark } = useThemeStore();
  // Progress as a fraction — custom-input step counts as 100 %
  const fraction = isFinalStep ? 1 : (current + 1) / (total + 1);

  const label = isFinalStep
    ? 'Final step'
    : `Question ${current + 1} of ${total}`;

  return (
    <div className="w-full space-y-2">
      {/* Label row */}
      <div className="flex items-center justify-between">
        <motion.span
          key={label}
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25 }}
          className="text-[10px] font-bold tracking-[0.22em] uppercase"
          style={{ color: '#a78bfa' }}
        >
          {label}
        </motion.span>

        {/* Dot indicators */}
        <div className="flex items-center gap-1.5">
          {Array.from({ length: total }).map((_, i) => (
            <motion.div
              key={i}
              className="rounded-full"
              animate={{
                width:  i === current && !isFinalStep ? 16 : 6,
                height: 6,
                backgroundColor:
                  i < current || isFinalStep
                    ? '#7c3aed'
                    : i === current
                    ? '#a78bfa'
                    : isDark
                    ? 'rgba(255,255,255,0.15)'
                    : 'rgba(0,0,0,0.12)',
              }}
              transition={{ duration: 0.35, ease: 'easeInOut' }}
            />
          ))}
        </div>
      </div>

      {/* Bar track */}
      <div
        className="h-0.5 w-full rounded-full overflow-hidden"
        style={{
          backgroundColor: isDark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.07)',
        }}
      >
        <motion.div
          className="h-full rounded-full"
          style={{
            background: 'linear-gradient(90deg, #7c3aed, #a78bfa)',
            boxShadow: '0 0 8px rgba(139,92,246,0.6)',
          }}
          animate={{ width: `${fraction * 100}%` }}
          transition={{ duration: 0.5, ease: 'easeInOut' }}
        />
      </div>
    </div>
  );
};

export default memo(ProgressBar);
