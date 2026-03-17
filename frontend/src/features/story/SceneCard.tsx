import React, { memo, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { SceneDoc } from '../../types/story';
import ChoiceCard from './ChoiceCard';
import ChoiceUnlockButton from './ChoiceUnlockButton';
import MediaLoadingBanner from './MediaLoadingBanner';

interface SceneCardProps {
  scene: SceneDoc;
  /** 0-based index in the timeline, used for stagger animation and scene number badge. */
  sceneIndex: number;
  /** Choice ID recovered from API / Firestore (nextSceneId was already set). */
  selectedChoiceId: string | null;
  /** Choice ID selected this session before API confirmation. */
  localSelectedChoiceId: string | null;
  /** True once the user has clicked the “Make Your Choice” unlock button. */
  choicesRevealed: boolean;
  /** True when this is the last (unresolved) scene in the timeline. */
  isLast: boolean;
  /** True while waiting for next-scene API response after a local choice. */
  generatingNextScene: boolean;
  /** True while polling GET /story/media for choice images after unlock was clicked. */
  mediaLoading: boolean;
  onRevealChoices: () => void;
  onChoiceSelect?: (choiceId: string) => void;
}

const SceneCard: React.FC<SceneCardProps> = memo(
  ({
    scene,
    sceneIndex,
    selectedChoiceId,
    localSelectedChoiceId,
    choicesRevealed,
    isLast,
    generatingNextScene,
    mediaLoading,
    onRevealChoices,
    onChoiceSelect,
  }) => {
    const videoRef = useRef<HTMLVideoElement>(null);
    const cardRef = useRef<HTMLDivElement>(null);

    // Scroll new scenes into view when they are appended (skip the root/first scene)
    useEffect(() => {
      if (isLast && sceneIndex > 0 && cardRef.current) {
        const timer = setTimeout(() => {
          cardRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 300);
        return () => clearTimeout(timer);
      }
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // API data takes priority; fall back to locally chosen option this session
    const effectiveSelectedChoiceId = selectedChoiceId ?? localSelectedChoiceId;
    const selectedChoice =
      scene.choices.find((c) => c.choiceId === effectiveSelectedChoiceId) ?? null;
    const videoUrl = selectedChoice?.videoUrl ?? null;

    const hasSelection = !!effectiveSelectedChoiceId;
    // Leaf scene with no confirmed selection yet
    const isInteractiveLeaf = isLast && !hasSelection;

    const n = scene.choices.length;
    const gridCols =
      n === 1 ? 'grid-cols-1 max-w-lg'
      : n <= 4 ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4'
      : 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3';

    return (
      <motion.div
        ref={cardRef}
        className="w-full"
        initial={{ opacity: 0, y: 36 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.65, delay: sceneIndex * 0.1 }}
      >
        <div
          className="rounded-3xl overflow-hidden"
          style={{
            background:
              'linear-gradient(160deg, rgba(22,18,50,0.98) 0%, rgba(12,9,28,0.99) 100%)',
            border: '1px solid rgba(139,92,246,0.14)',
            boxShadow:
              '0 8px 64px rgba(0,0,0,0.65), inset 0 1px 0 rgba(255,255,255,0.04)',
          }}
        >
          {/* ── Narrative header ── */}
          <div className="px-6 sm:px-10 lg:px-16 pt-10 sm:pt-14 pb-8 space-y-6">
            {/* Badges */}
            <div className="flex items-center gap-2.5 flex-wrap">
              <span
                className="text-[10px] font-bold tracking-[0.2em] uppercase px-3 py-1 rounded-full"
                style={{
                  backgroundColor: 'rgba(139,92,246,0.14)',
                  color: '#a78bfa',
                  border: '1px solid rgba(139,92,246,0.28)',
                }}
              >
                Scene {String(sceneIndex + 1).padStart(2, '0')}
              </span>
              {scene.isRoot && (
                <span
                  className="text-[10px] font-bold tracking-widest uppercase px-3 py-1 rounded-full"
                  style={{
                    backgroundColor: 'rgba(56,189,248,0.08)',
                    color: '#7dd3fc',
                    border: '1px solid rgba(56,189,248,0.2)',
                  }}
                >
                  Opening
                </span>
              )}
            </div>

            {/* Title */}
            <h2
              className="text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight leading-[1.1]"
              style={{
                backgroundImage:
                  'linear-gradient(130deg, #f1f5f9 0%, #c4b5fd 52%, #818cf8 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
            >
              {scene.title}
            </h2>

            {/* Accent rule */}
            <div className="flex items-center gap-2">
              <div
                className="h-px"
                style={{ width: 48, background: 'linear-gradient(90deg, #8b5cf6, transparent)' }}
              />
              <div
                className="w-1.5 h-1.5 rounded-full"
                style={{ backgroundColor: '#8b5cf6', opacity: 0.7 }}
              />
            </div>

            {/* Description — narrative prose */}
            <p
              className="text-lg sm:text-xl leading-[2] font-light max-w-3xl"
              style={{ color: 'rgba(203,213,225,0.82)' }}
            >
              {scene.description}
            </p>
          </div>

          {/* ── Case B1: leaf, timer running — show unlock button ── */}
          {isInteractiveLeaf && !choicesRevealed && !mediaLoading && (
            <motion.div
              className="px-6 sm:px-10 lg:px-16 pb-14"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.25 }}
            >
              <ChoiceUnlockButton onUnlock={onRevealChoices} />
            </motion.div>
          )}

          {/* ── Case B1.5: leaf, polling for images — show loading banner ── */}
          <AnimatePresence>
            {isInteractiveLeaf && mediaLoading && (
              <MediaLoadingBanner choiceCount={scene.choices.length} />
            )}
          </AnimatePresence>

          {/* ── Cases A / B2 / B3: show choice grid ── */}
          {(hasSelection || choicesRevealed) && (
            <div className="px-6 sm:px-10 lg:px-16 pb-10 space-y-6">
              {/* Section label */}
              <div className="flex items-center gap-3">
                <div className="h-px flex-1" style={{ backgroundColor: 'rgba(255,255,255,0.06)' }} />
                <p
                  className="text-[10px] font-bold uppercase tracking-[0.25em] flex-shrink-0"
                  style={{ color: 'rgba(167,139,250,0.65)' }}
                >
                  {hasSelection ? 'Your choice' : 'Choose your path'}
                </p>
                <div className="h-px flex-1" style={{ backgroundColor: 'rgba(255,255,255,0.06)' }} />
              </div>

              {/* Choice grid */}
              <div className={`grid ${gridCols} gap-4 sm:gap-5 lg:gap-6`}>
                {scene.choices.map((choice, i) => (
                  <ChoiceCard
                    key={choice.choiceId}
                    choice={choice}
                    isSelected={choice.choiceId === effectiveSelectedChoiceId}
                    isLocked={hasSelection && choice.choiceId !== effectiveSelectedChoiceId}
                    index={i}
                    onClick={
                      isInteractiveLeaf && choicesRevealed
                        ? () => onChoiceSelect?.(choice.choiceId)
                        : undefined
                    }
                  />
                ))}
              </div>

              {/* CTA — shown while waiting for user to pick */}
              {isInteractiveLeaf && choicesRevealed && scene.choices.length > 0 && (
                <motion.p
                  className="text-xs text-center pt-1 tracking-widest"
                  style={{ color: 'rgba(148,163,184,0.5)' }}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.7 }}
                >
                  ✦ &nbsp; Select a path to continue your story &nbsp; ✦
                </motion.p>
              )}
            </div>
          )}

          {/* ── Video player — appears once a choice is selected ── */}
          <AnimatePresence>
            {videoUrl && (
              <motion.div
                className="px-6 sm:px-10 lg:px-16 pb-12"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 12 }}
                transition={{ duration: 0.55, ease: 'easeOut' }}
              >
                <div
                  className="rounded-2xl overflow-hidden mx-auto"
                  style={{
                    border: '1px solid rgba(139,92,246,0.22)',
                    boxShadow: '0 8px 48px rgba(0,0,0,0.55)',
                  }}
                >
                  <video
                    ref={videoRef}
                    src={videoUrl}
                    autoPlay
                    muted
                    loop
                    playsInline
                    className="w-full object-cover block"
                    style={{ maxHeight: 500 }}
                  />
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* ── Generating next chapter spinner ── */}
          <AnimatePresence>
            {isLast && !!localSelectedChoiceId && generatingNextScene && (
              <motion.div
                className="px-6 sm:px-10 lg:px-16 pb-14 flex flex-col items-center gap-3"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.45, delay: 0.35 }}
              >
                <div className="flex items-center gap-2">
                  {[0, 1, 2].map((i) => (
                    <motion.div
                      key={i}
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: '#a78bfa' }}
                      animate={{ opacity: [0.3, 1, 0.3], scale: [0.8, 1.2, 0.8] }}
                      transition={{
                        duration: 1.2,
                        repeat: Infinity,
                        delay: i * 0.2,
                        ease: 'easeInOut',
                      }}
                    />
                  ))}
                </div>
                <p
                  className="text-sm font-semibold tracking-wide"
                  style={{ color: '#a78bfa' }}
                >
                  Generating next chapter…
                </p>
                <p
                  className="text-xs tracking-widest"
                  style={{ color: 'rgba(148,163,184,0.45)' }}
                >
                  The story is being written
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    );
  },
);

SceneCard.displayName = 'SceneCard';
export default SceneCard;
