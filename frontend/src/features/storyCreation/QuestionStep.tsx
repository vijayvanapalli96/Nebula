import React, { useCallback, useEffect, useRef, memo } from 'react';
import { motion } from 'framer-motion';
import OptionCard from './OptionCard';
import type { Question } from '../../store/storyCreationStore';

interface QuestionStepProps {
  question: Question;
  selectedAnswer: string | undefined;
  /** Store the answer AND trigger next-question navigation after a short delay */
  onSelect: (questionId: string, label: string) => void;
  /** Direction of entry slide: 1 = left→right (forward), -1 = right→left (back) */
  direction: 1 | -1;
}

const EASE = [0.22, 1, 0.36, 1] as [number, number, number, number];

const slideVariants = {
  enter: (dir: number) => ({
    opacity: 0,
    x: dir * 60,
    scale: 0.98,
  }),
  center: {
    opacity: 1,
    x: 0,
    scale: 1,
    transition: { duration: 0.38, ease: EASE },
  },
  exit: (dir: number) => ({
    opacity: 0,
    x: dir * -60,
    scale: 0.98,
    transition: { duration: 0.28, ease: EASE },
  }),
};

const QuestionStep: React.FC<QuestionStepProps> = ({
  question,
  selectedAnswer,
  onSelect,
  direction,
}) => {
  // Guard: only auto-advance once per selection
  const hasAdvanced = useRef(false);

  useEffect(() => {
    hasAdvanced.current = false;
  }, [question.id]);

  const handleOptionClick = useCallback(
    (label: string) => {
      onSelect(question.id, label);
      // Auto-advance after 480 ms so the user sees their selection animate in
      if (!hasAdvanced.current) {
        hasAdvanced.current = true;
      }
    },
    [question.id, onSelect],
  );

  return (
    <motion.div
      key={question.id}
      custom={direction}
      variants={slideVariants}
      initial="enter"
      animate="center"
      exit="exit"
      className="w-full max-w-2xl mx-auto space-y-8 px-4 sm:px-0"
    >
      {/* ── Question title ── */}
      <div className="space-y-2 text-center sm:text-left">
        <motion.h2
          className="text-2xl sm:text-3xl font-black leading-tight"
          style={{ color: 'var(--text-primary)' }}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, delay: 0.05 }}
        >
          {question.question}
        </motion.h2>
        <motion.p
          className="text-sm"
          style={{ color: 'var(--text-secondary)' }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.35, delay: 0.12 }}
        >
          Choose the one that feels right for your story.
        </motion.p>
      </div>

      {/* ── 2 × 2 option grid ── */}
      <div className="grid grid-cols-2 gap-3 sm:gap-4">
        {question.options.map((option, i) => (
          <OptionCard
            key={option.label}
            option={option}
            selected={selectedAnswer === option.label}
            onClick={() => handleOptionClick(option.label)}
            delay={i * 0.07}
          />
        ))}
      </div>
    </motion.div>
  );
};

export default memo(QuestionStep);
