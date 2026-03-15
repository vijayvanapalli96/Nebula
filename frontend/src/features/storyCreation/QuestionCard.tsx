import React from 'react';
import { motion } from 'framer-motion';
import OptionButton from './OptionButton';
import type { Question } from '../../store/storyCreationStore';

interface QuestionCardProps {
  question: Question;
  index: number;
  selectedAnswer: string | undefined;
  onSelect: (questionId: string, option: string) => void;
}

const QuestionCard: React.FC<QuestionCardProps> = ({
  question,
  index,
  selectedAnswer,
  onSelect,
}) => (
  <motion.div
    initial={{ opacity: 0, y: 32 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5, ease: 'easeOut', delay: index * 0.13 }}
    className="space-y-5"
  >
    {/* Question header */}
    <div className="flex items-start gap-4">
      {/* Number badge */}
      <span
        className="flex-shrink-0 w-8 h-8 rounded-xl flex items-center justify-center text-[11px] font-black mt-0.5"
        style={{
          backgroundColor: 'rgba(139,92,246,0.14)',
          border: '1px solid rgba(139,92,246,0.28)',
          color: '#a78bfa',
        }}
      >
        {String(index + 1).padStart(2, '0')}
      </span>

      <h3
        className="text-lg sm:text-xl font-bold leading-snug"
        style={{ color: 'var(--text-primary)' }}
      >
        {question.question}
      </h3>
    </div>

    {/* Options — 2 cols on sm+, 1 col on mobile */}
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pl-12">
      {question.options.map((option) => (
        <OptionButton
          key={option}
          label={option}
          selected={selectedAnswer === option}
          onClick={() => onSelect(question.id, option)}
        />
      ))}
    </div>
  </motion.div>
);

export default QuestionCard;
