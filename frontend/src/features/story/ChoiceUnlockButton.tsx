import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface ChoiceUnlockButtonProps {
  /** Called once the countdown reaches 0 and the user clicks the button. */
  onUnlock: () => void;
}

const ChoiceUnlockButton: React.FC<ChoiceUnlockButtonProps> = ({ onUnlock }) => {
  const [countdown, setCountdown] = useState(10);
  const isReady = countdown === 0;

  useEffect(() => {
    if (isReady) return;
    const timer = setInterval(() => {
      setCountdown((c) => {
        if (c <= 1) {
          clearInterval(timer);
          return 0;
        }
        return c - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [isReady]);

  return (
    <div className="flex flex-col items-center gap-4 py-4">
      {/* Subtitle */}
      <p
        className="text-xs tracking-[0.2em] uppercase"
        style={{ color: 'rgba(148,163,184,0.45)' }}
      >
        {isReady ? 'Your fate awaits' : 'Take a moment to decide…'}
      </p>

      {/* Button */}
      <motion.button
        onClick={isReady ? onUnlock : undefined}
        disabled={!isReady}
        className="relative px-10 py-4 rounded-2xl text-sm font-bold tracking-widest uppercase transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500"
        style={{
          background: isReady
            ? 'linear-gradient(135deg, #7c3aed 0%, #a855f7 100%)'
            : 'rgba(139,92,246,0.10)',
          color: isReady ? '#fff' : 'rgba(167,139,250,0.45)',
          border: isReady
            ? '1px solid rgba(167,139,250,0.6)'
            : '1px solid rgba(139,92,246,0.22)',
          cursor: isReady ? 'pointer' : 'not-allowed',
        }}
        animate={
          isReady
            ? {
                boxShadow: [
                  '0 0 18px rgba(139,92,246,0.3)',
                  '0 0 40px rgba(139,92,246,0.65)',
                  '0 0 18px rgba(139,92,246,0.3)',
                ],
              }
            : { boxShadow: '0 0 0px rgba(139,92,246,0)' }
        }
        transition={
          isReady
            ? { duration: 1.8, repeat: Infinity, ease: 'easeInOut' }
            : { duration: 0 }
        }
        whileHover={isReady ? { scale: 1.04, y: -2 } : {}}
        whileTap={isReady ? { scale: 0.97 } : {}}
      >
        {isReady ? 'Make Your Choice  ✦' : `Make Your Choice  (${countdown}s)`}
      </motion.button>

      {/* Countdown progress ring */}
      {!isReady && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex items-center gap-1.5"
        >
          {Array.from({ length: 10 }).map((_, i) => (
            <motion.div
              key={i}
              className="rounded-full"
              style={{
                width: 5,
                height: 5,
                backgroundColor:
                  i < 10 - countdown
                    ? '#a78bfa'
                    : 'rgba(139,92,246,0.18)',
              }}
              animate={{ scale: i === 10 - countdown - 1 ? [1, 1.4, 1] : 1 }}
              transition={{ duration: 0.4 }}
            />
          ))}
        </motion.div>
      )}
    </div>
  );
};

export default ChoiceUnlockButton;
