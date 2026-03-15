import React, { memo } from 'react';
import { motion } from 'framer-motion';

interface CustomStoryInputProps {
  value: string;
  onChange: (value: string) => void;
  delay?: number;
}

const MAX_CHARS = 300;

const CustomStoryInput: React.FC<CustomStoryInputProps> = ({
  value,
  onChange,
  delay = 0.4,
}) => (
  <motion.div
    initial={{ opacity: 0, y: 24 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5, ease: 'easeOut', delay }}
    className="space-y-4"
  >
    {/* Divider */}
    <div
      className="h-px"
      style={{ backgroundColor: 'var(--border-color)' }}
    />

    <div className="space-y-1">
      <p className="text-[10px] font-bold tracking-[0.22em] uppercase text-blue-400">
        Optional
      </p>
      <h3 className="text-lg sm:text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
        Add something unique to your story
      </h3>
      <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
        A character idea, a twist, a world detail — the AI will weave it into your narrative.
      </p>
    </div>

    <div className="relative">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value.slice(0, MAX_CHARS))}
        placeholder="Example: A mysterious traveler who appears in every chapter..."
        rows={4}
        className="w-full rounded-2xl px-5 py-4 text-sm resize-none outline-none"
        style={{
          backgroundColor: 'var(--input-bg)',
          border: '1.5px solid var(--border-color)',
          color: 'var(--text-primary)',
          caretColor: '#8b5cf6',
          transition: 'border-color 0.18s, box-shadow 0.18s',
        }}
        onFocus={(e) => {
          e.currentTarget.style.borderColor = 'rgba(139,92,246,0.55)';
          e.currentTarget.style.boxShadow = '0 0 0 3px rgba(139,92,246,0.1)';
        }}
        onBlur={(e) => {
          e.currentTarget.style.borderColor = 'var(--border-color)';
          e.currentTarget.style.boxShadow = 'none';
        }}
      />
      {/* Char counter */}
      <span
        className="absolute bottom-3 right-4 text-[10px] font-medium tabular-nums"
        style={{
          color: value.length > MAX_CHARS * 0.85 ? '#f87171' : 'rgba(107,114,128,0.7)',
          transition: 'color 0.2s',
        }}
      >
        {value.length}/{MAX_CHARS}
      </span>
    </div>
  </motion.div>
);

export default memo(CustomStoryInput);
