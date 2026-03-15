import React from 'react';
import { motion } from 'framer-motion';
import type { Scene } from '../../store/storySessionStore';

interface SceneDisplayProps {
  scene: Scene;
}

/** Splits description into words and reveals them with a stagger. */
const AnimatedDescription: React.FC<{ text: string }> = ({ text }) => {
  const words = text.split(' ');

  return (
    <motion.p
      className="text-base sm:text-lg leading-8 font-light"
      style={{ color: 'var(--text-secondary)' }}
    >
      {words.map((word, i) => (
        <motion.span
          key={i}
          className="inline-block mr-[0.28em]"
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, delay: 0.5 + i * 0.025, ease: 'easeOut' }}
        >
          {word}
        </motion.span>
      ))}
    </motion.p>
  );
};

const SceneDisplay: React.FC<SceneDisplayProps> = ({ scene }) => (
  <div className="w-full max-w-3xl mx-auto flex flex-col gap-6 px-4">
    {/* ── Scene label badge ── */}
    <motion.div
      className="flex items-center gap-2"
      initial={{ opacity: 0, x: -12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.45 }}
    >
      <span
        className="text-xs font-semibold uppercase tracking-widest px-3 py-1 rounded-full"
        style={{
          backgroundColor: 'rgba(139,92,246,0.15)',
          color: '#a78bfa',
          border: '1px solid rgba(139,92,246,0.3)',
        }}
      >
        Opening Scene
      </span>
      {scene.theme && (
        <span
          className="text-xs font-medium uppercase tracking-widest px-3 py-1 rounded-full"
          style={{
            backgroundColor: 'rgba(96,165,250,0.12)',
            color: '#93c5fd',
            border: '1px solid rgba(96,165,250,0.25)',
          }}
        >
          {scene.theme}
        </span>
      )}
    </motion.div>

    {/* ── Scene title ── */}
    <motion.h1
      className="text-3xl sm:text-5xl font-black tracking-tight leading-tight"
      style={{
        backgroundImage: 'linear-gradient(135deg, var(--text-primary) 0%, #a78bfa 55%, #60a5fa 100%)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        backgroundClip: 'text',
      }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.55, delay: 0.1 }}
    >
      {scene.scene_title}
    </motion.h1>

    {/* ── Divider ── */}
    <motion.div
      className="h-px w-20"
      style={{ backgroundImage: 'linear-gradient(90deg, #8b5cf6, transparent)' }}
      initial={{ scaleX: 0, originX: 0 }}
      animate={{ scaleX: 1 }}
      transition={{ duration: 0.5, delay: 0.4 }}
    />

    {/* ── Description ── */}
    <AnimatedDescription text={scene.scene_description} />
  </div>
);

export default SceneDisplay;
