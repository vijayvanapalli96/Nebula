import React from 'react';
import { motion } from 'framer-motion';
import type { SceneDoc } from '../../types/story';
import SceneCard from './SceneCard';

interface SceneTimelineProps {
  timeline: SceneDoc[];
  /** sceneId → choiceId selected from API / Firestore data */
  selectedChoices: Record<string, string>;
  /** sceneId → choiceId selected this session */
  localSelectedChoices: Record<string, string>;
  /** sceneId → true once the unlock button was clicked */
  choicesRevealedForScene: Record<string, boolean>;
  /** True while waiting for next-scene generation */
  generatingNextScene: boolean;
  onChoiceSelect?: (sceneId: string, choiceId: string) => void;
  onRevealChoices?: (sceneId: string) => void;
}

// ── Connector between scenes ──────────────────────────────────────────────────
const TimelineConnector: React.FC<{ choiceLabel: string }> = ({ choiceLabel }) => (
  <motion.div
    className="flex flex-col items-center gap-1 py-1 select-none"
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    transition={{ duration: 0.4 }}
  >
    {/* Top stem */}
    <div
      className="w-px"
      style={{
        height: 24,
        background: 'linear-gradient(180deg, transparent, rgba(139,92,246,0.4))',
      }}
    />

    {/* Choice pill */}
    <div
      className="flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-semibold max-w-[260px]"
      style={{
        backgroundColor: 'rgba(139,92,246,0.1)',
        border: '1px solid rgba(139,92,246,0.25)',
        color: '#a78bfa',
      }}
    >
      {/* Down arrow */}
      <svg width="8" height="9" viewBox="0 0 8 9" fill="none" className="flex-shrink-0">
        <path
          d="M4 0v6.5M1.5 4.5 4 7l2.5-2.5"
          stroke="currentColor"
          strokeWidth="1.4"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      <span className="truncate">{choiceLabel}</span>
    </div>

    {/* Bottom stem */}
    <div
      className="w-px"
      style={{
        height: 24,
        background: 'linear-gradient(180deg, rgba(139,92,246,0.4), transparent)',
      }}
    />
  </motion.div>
);

// ── Empty state ───────────────────────────────────────────────────────────────
const EmptyTimeline: React.FC = () => (
  <motion.div
    className="flex flex-col items-center gap-5 py-20 text-center"
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    transition={{ duration: 0.5 }}
  >
    <div
      className="w-14 h-14 rounded-2xl flex items-center justify-center"
      style={{
        backgroundColor: 'rgba(139,92,246,0.1)',
        border: '1px solid rgba(139,92,246,0.25)',
      }}
    >
      <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
        <path
          d="M11 4v7m0 4h.01"
          stroke="#a78bfa"
          strokeWidth="1.8"
          strokeLinecap="round"
        />
      </svg>
    </div>
    <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
      No scenes available yet.
    </p>
  </motion.div>
);

// ── Timeline ──────────────────────────────────────────────────────────────────
const SceneTimeline: React.FC<SceneTimelineProps> = ({
  timeline,
  selectedChoices,
  localSelectedChoices,
  choicesRevealedForScene,
  generatingNextScene,
  onChoiceSelect,
  onRevealChoices,
}) => {
  if (timeline.length === 0) return <EmptyTimeline />;

  return (
    <div className="flex flex-col">
      {timeline.map((scene, index) => {
        const selectedChoiceId = selectedChoices[scene.sceneId] ?? null;
        const selectedChoice = scene.choices.find((c) => c.choiceId === selectedChoiceId) ?? null;
        const isLast = index === timeline.length - 1;

        return (
          <React.Fragment key={scene.sceneId}>
            <SceneCard
              scene={scene}
              sceneIndex={index}
              selectedChoiceId={selectedChoiceId}
              localSelectedChoiceId={localSelectedChoices[scene.sceneId] ?? null}
              choicesRevealed={choicesRevealedForScene[scene.sceneId] ?? false}
              isLast={isLast}
              generatingNextScene={isLast ? generatingNextScene : false}
              onRevealChoices={() => onRevealChoices?.(scene.sceneId)}
              onChoiceSelect={(choiceId) => onChoiceSelect?.(scene.sceneId, choiceId)}
            />

            {/* Connector shown between scenes — only when a choice links them */}
            {!isLast && selectedChoice && (
              <TimelineConnector
                choiceLabel={
                  selectedChoice.choiceText.length > 50
                    ? selectedChoice.choiceText.slice(0, 47) + '…'
                    : selectedChoice.choiceText
                }
              />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
};

export default SceneTimeline;
