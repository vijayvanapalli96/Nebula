import React, { useCallback, useEffect, useId } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useStoryStore } from '../../store/storyStore';
import type { Archetype, Motivation } from '../../types/story';

const ARCHETYPES: Archetype[] = [
  'The Detective',
  'The Rebel',
  'The Scholar',
  'The Outlaw',
  'The Wanderer',
  'The Hero',
];

const MOTIVATIONS: Motivation[] = [
  'Seek Justice',
  'Uncover the Truth',
  'Protect the Innocent',
  'Pursue Power',
  'Find Redemption',
  'Survive at All Costs',
];

const backdropVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
};

const panelVariants = {
  hidden: { opacity: 0, scale: 0.92, y: 40 },
  visible: { opacity: 1, scale: 1, y: 0, transition: { type: 'spring' as const, stiffness: 300, damping: 28 } },
  exit: { opacity: 0, scale: 0.92, y: 24, transition: { duration: 0.2 } },
};

const CreateStoryModal: React.FC = () => {
  const { isModalOpen, selectedGenre, newStoryForm, closeModal, updateForm } =
    useStoryStore();

  const titleId = useId();
  const nameId = useId();
  const archetypeId = useId();
  const motivationId = useId();

  // Close on Escape key
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') closeModal();
    };
    if (isModalOpen) document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [isModalOpen, closeModal]);

  // Prevent body scroll when open
  useEffect(() => {
    document.body.style.overflow = isModalOpen ? 'hidden' : '';
    return () => { document.body.style.overflow = ''; };
  }, [isModalOpen]);

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      if (!newStoryForm.characterName.trim()) return;
      // In a real app: dispatch to backend / router
      alert(
        `Generating story for "${newStoryForm.characterName}" (${newStoryForm.archetype || 'no archetype'}) — ${selectedGenre?.title}`,
      );
      closeModal();
    },
    [newStoryForm, selectedGenre, closeModal],
  );

  return (
    <AnimatePresence>
      {isModalOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            key="backdrop"
            className="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm"
            variants={backdropVariants}
            initial="hidden"
            animate="visible"
            exit="hidden"
            transition={{ duration: 0.25 }}
            onClick={closeModal}
            aria-hidden="true"
          />

          {/* Modal panel */}
          <motion.div
            key="panel"
            role="dialog"
            aria-modal="true"
            aria-labelledby={titleId}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
            variants={panelVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
          >
            <div
              className="relative w-full max-w-md rounded-3xl overflow-hidden card-shadow max-h-[90dvh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Genre hero image header */}
              {selectedGenre && (
                <div className="relative h-40 overflow-hidden">
                  <img
                    src={selectedGenre.image}
                    alt={selectedGenre.title}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-b from-black/30 to-black/80" />
                  <div className="absolute bottom-4 left-5">
                    <span className="text-[10px] font-bold tracking-widest uppercase text-violet-300">
                      {selectedGenre.title}
                    </span>
                    <p className="text-white/80 text-xs mt-0.5">{selectedGenre.tagline}</p>
                  </div>
                </div>
              )}

              {/* Form body */}
              <div
                className="rounded-b-3xl p-6 space-y-5"
                style={{
                  backgroundColor: 'var(--bg-card)',
                  borderLeft: '1px solid var(--border-color)',
                  borderRight: '1px solid var(--border-color)',
                  borderBottom: '1px solid var(--border-color)',
                }}
              >
                <h2
                  id={titleId}
                  className="text-lg font-bold text-glow"
                  style={{ color: 'var(--text-primary)' }}
                >
                  Create Your Character
                </h2>

                <form onSubmit={handleSubmit} className="space-y-4" noValidate>
                  {/* Character name */}
                  <div className="space-y-1.5">
                    <label
                      htmlFor={nameId}
                      className="block text-xs font-semibold uppercase tracking-wider"
                      style={{ color: 'var(--text-secondary)' }}
                    >
                      Character Name <span className="text-red-400">*</span>
                    </label>
                    <input
                      id={nameId}
                      type="text"
                      required
                      placeholder="e.g. Detective Marlowe…"
                      value={newStoryForm.characterName}
                      onChange={(e) => updateForm({ characterName: e.target.value })}
                      className="w-full rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 transition"
                      style={{
                        backgroundColor: 'var(--input-bg)',
                        border: '1px solid var(--border-color)',
                        color: 'var(--text-primary)',
                      }}
                    />
                  </div>

                  {/* Archetype */}
                  <div className="space-y-1.5">
                    <label
                      htmlFor={archetypeId}
                      className="block text-xs font-semibold uppercase tracking-wider"
                      style={{ color: 'var(--text-secondary)' }}
                    >
                      Archetype
                    </label>
                    <select
                      id={archetypeId}
                      value={newStoryForm.archetype}
                      onChange={(e) =>
                        updateForm({ archetype: e.target.value as Archetype | '' })
                      }
                      className="w-full rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 transition appearance-none"
                      style={{
                        backgroundColor: 'var(--bg-elevated)',
                        border: '1px solid var(--border-color)',
                        color: 'var(--text-primary)',
                      }}
                    >
                      <option value="" style={{ backgroundColor: 'var(--bg-elevated)' }}>
                        — Choose archetype —
                      </option>
                      {ARCHETYPES.map((a) => (
                        <option key={a} value={a} style={{ backgroundColor: 'var(--bg-elevated)' }}>
                          {a}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Motivation */}
                  <div className="space-y-1.5">
                    <label
                      htmlFor={motivationId}
                      className="block text-xs font-semibold uppercase tracking-wider"
                      style={{ color: 'var(--text-secondary)' }}
                    >
                      Motivation
                    </label>
                    <select
                      id={motivationId}
                      value={newStoryForm.motivation}
                      onChange={(e) =>
                        updateForm({ motivation: e.target.value as Motivation | '' })
                      }
                      className="w-full rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 transition appearance-none"
                      style={{
                        backgroundColor: 'var(--bg-elevated)',
                        border: '1px solid var(--border-color)',
                        color: 'var(--text-primary)',
                      }}
                    >
                      <option value="" style={{ backgroundColor: 'var(--bg-elevated)' }}>
                        — Choose motivation —
                      </option>
                      {MOTIVATIONS.map((m) => (
                        <option key={m} value={m} style={{ backgroundColor: 'var(--bg-elevated)' }}>
                          {m}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-3 pt-2">
                    <button
                      type="button"
                      onClick={closeModal}
                      className="flex-1 px-4 py-2.5 rounded-xl text-sm transition"
                      style={{
                        border: '1px solid var(--border-color)',
                        color: 'var(--text-secondary)',
                        backgroundColor: 'transparent',
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--sidebar-hover)')}
                      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                    >
                      Cancel
                    </button>
                    <motion.button
                      type="submit"
                      whileHover={{ scale: 1.03 }}
                      whileTap={{ scale: 0.97 }}
                      disabled={!newStoryForm.characterName.trim()}
                      className="flex-1 px-4 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold text-sm transition glow-purple"
                    >
                      ✦ Generate Story
                    </motion.button>
                  </div>
                </form>
              </div>

              {/* Close button */}
              <button
                aria-label="Close modal"
                onClick={closeModal}
                className="absolute top-3 right-3 w-8 h-8 flex items-center justify-center rounded-full bg-black/50 text-white/60 hover:text-white hover:bg-black/80 transition"
              >
                ✕
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default CreateStoryModal;
