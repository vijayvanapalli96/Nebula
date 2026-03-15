import React, { memo } from 'react';
import { motion } from 'framer-motion';

interface OptionButtonProps {
  label: string;
  selected: boolean;
  onClick: () => void;
}

const OptionButton: React.FC<OptionButtonProps> = ({ label, selected, onClick }) => (
  <motion.button
    onClick={onClick}
    whileTap={{ scale: 0.97 }}
    transition={{ type: 'spring', stiffness: 400, damping: 26 }}
    className="relative w-full text-left px-5 py-4 rounded-2xl text-sm font-semibold outline-none focus-visible:ring-2 focus-visible:ring-violet-500"
    style={{
      backgroundColor: selected ? 'rgba(139,92,246,0.18)' : 'var(--input-bg)',
      border: `1.5px solid ${selected ? 'rgba(139,92,246,0.75)' : 'var(--border-color)'}`,
      color: selected ? '#ddd6fe' : 'var(--text-secondary)',
      boxShadow: selected
        ? '0 0 22px rgba(139,92,246,0.22), 0 0 44px rgba(139,92,246,0.08)'
        : 'none',
      transition: 'background-color 0.18s, border-color 0.18s, box-shadow 0.18s, color 0.18s',
    }}
    onMouseEnter={(e) => {
      if (!selected) {
        e.currentTarget.style.borderColor = 'rgba(139,92,246,0.4)';
        e.currentTarget.style.backgroundColor = 'rgba(139,92,246,0.08)';
        e.currentTarget.style.color = 'var(--text-primary)';
      }
    }}
    onMouseLeave={(e) => {
      if (!selected) {
        e.currentTarget.style.borderColor = 'var(--border-color)';
        e.currentTarget.style.backgroundColor = 'var(--input-bg)';
        e.currentTarget.style.color = 'var(--text-secondary)';
      }
    }}
  >
    {/* Selected dot indicator */}
    {selected && (
      <motion.span
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="absolute right-4 top-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-violet-400"
        style={{ boxShadow: '0 0 8px rgba(167,139,250,0.8)' }}
      />
    )}
    {label}
  </motion.button>
);

export default memo(OptionButton);
