import React, { useEffect, useCallback } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useStoryViewerStore } from '../store/storyViewerStore';
import StoryLoadingPage from './StoryLoadingPage';
import SceneTimeline from '../features/story/SceneTimeline';
import type { StoryDetail } from '../types/story';

interface StoryPageLocationState {
  storyDetail?: StoryDetail;
}

// ── helpers ────────────────────────────────────────────────────────────────
const COVER_GRADIENT = 'linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4c1d95 100%)';

function formatRelativeTime(isoDate: string | null | undefined): string {
  if (!isoDate) return '';
  const diff = Date.now() - new Date(isoDate).getTime();
  const minutes = Math.floor(diff / 60_000);
  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

// ── component ───────────────────────────────────────────────────────────────
const StoryPage: React.FC = () => {
  const { storyId } = useParams<{ storyId: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const locationState = location.state as StoryPageLocationState | null;

  const {
    story,
    timeline,
    selectedChoices,
    choicesRevealedForScene,
    localSelectedChoice,
    generatingNextScene,
    loading,
    error,
    loadStory,
    revealChoices,
    selectLocalChoice,
    reset,
  } = useStoryViewerStore();

  useEffect(() => {
    if (!storyId) return;
    const prefetched =
      locationState?.storyDetail?.story_id === storyId ? locationState.storyDetail : null;
    void loadStory(storyId, prefetched);
    return () => reset();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [storyId]);

  const handleChoiceSelect = useCallback(
    (sceneId: string, choiceId: string) => selectLocalChoice(sceneId, choiceId),
    [selectLocalChoice],
  );

  const handleRevealChoices = useCallback(
    (sceneId: string) => revealChoices(sceneId),
    [revealChoices],
  );

  // ── loading state ─────────────────────────────────────────────────────────
  if (loading) {
    const hint = story ?? locationState?.storyDetail;
    return (
      <StoryLoadingPage
        title={hint?.title}
        genre={hint?.genre}
        characterName={hint?.character_name}
      />
    );
  }

  // ── error / not-found state ───────────────────────────────────────────────
  if (error || !story) {
    return (
      <main
        className="min-h-screen flex flex-col items-center justify-center gap-5 px-6"
        style={{ backgroundColor: 'var(--bg-base)' }}
      >
        <div className="text-center space-y-2">
          <p className="text-2xl font-black" style={{ color: 'var(--text-primary)' }}>
            Story not found
          </p>
          {error && (
            <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
              {error}
            </p>
          )}
        </div>
        <button
          onClick={() => navigate('/dashboard')}
          className="text-sm font-semibold transition hover:opacity-80"
          style={{ color: '#a78bfa' }}
        >
          ← Back to Dashboard
        </button>
      </main>
    );
  }

  // ── derived values ────────────────────────────────────────────────────────
  const progress = story.progress ?? 0;
  const lastPlayedLabel = formatRelativeTime(story.last_played_at ?? story.updated_at);
  const hasScenes = timeline.length > 0;
  const coverImage = story.cover_image ?? story.theme_image_url ?? null;

  // ── main render ───────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--bg-base)' }}>
      {/* ── ambient background glow ── */}
      <div
        className="fixed inset-0 pointer-events-none"
        style={{
          background:
            'radial-gradient(ellipse 80% 50% at 50% -20%, rgba(139,92,246,0.12) 0%, transparent 70%)',
          zIndex: 0,
        }}
      />

      {/* ── sticky header + progress bar ── */}
      <header
        className="sticky top-0 z-30 flex items-center justify-between px-5 py-3 backdrop-blur-md border-b"
        style={{
          backgroundColor: 'rgba(10,10,15,0.85)',
          borderColor: 'rgba(255,255,255,0.06)',
        }}
      >
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2 text-sm font-semibold transition hover:opacity-80"
          style={{ color: '#a78bfa' }}
        >
          ← Back
        </button>

        <div className="flex items-center gap-3">
          {lastPlayedLabel && (
            <span className="text-xs hidden sm:block" style={{ color: 'var(--text-muted)' }}>
              {lastPlayedLabel}
            </span>
          )}
          <div className="w-28 h-1.5 rounded-full overflow-hidden" style={{ backgroundColor: 'rgba(255,255,255,0.1)' }}>
            <motion.div
              className="h-full rounded-full"
              style={{ background: 'linear-gradient(90deg, #7c3aed, #a855f7)' }}
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 1.2, ease: 'easeOut' }}
            />
          </div>
          <span className="text-xs font-bold tabular-nums" style={{ color: '#a78bfa' }}>
            {progress}%
          </span>
        </div>
      </header>

      {/* ── hero banner ── */}
      <div className="relative h-56 sm:h-72 overflow-hidden" style={{ zIndex: 1 }}>
        {coverImage ? (
          <img src={coverImage} alt={story.title} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full" style={{ background: COVER_GRADIENT }} />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-[var(--bg-base)] via-black/40 to-transparent" />

        {/* Story meta overlay */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="absolute bottom-6 left-6 right-6"
        >
          {story.genre && (
            <span
              className="inline-block text-[10px] font-bold tracking-widest uppercase px-2.5 py-1 rounded-full mb-2"
              style={{
                backgroundColor: 'rgba(124,58,237,0.25)',
                border: '1px solid rgba(167,139,250,0.3)',
                color: '#c4b5fd',
              }}
            >
              {story.genre}
            </span>
          )}
          <h1 className="text-2xl sm:text-3xl font-black text-white drop-shadow-lg">
            {story.title}
          </h1>
          {(story.character_name || story.archetype) && (
            <p className="text-sm mt-1" style={{ color: 'rgba(196,181,253,0.8)' }}>
              {[story.character_name, story.archetype].filter(Boolean).join(' · ')}
            </p>
          )}
        </motion.div>
      </div>

      {/* ── page body ── */}
      <div className="relative z-10 w-full px-2 sm:px-4 pb-24 pt-8">
        {hasScenes ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            {/* Section label */}
            <div className="flex items-center gap-3 mb-8 max-w-7xl mx-auto px-2 sm:px-4">
              <div className="h-px flex-1" style={{ backgroundColor: 'rgba(255,255,255,0.08)' }} />
              <span
                className="text-[11px] font-bold tracking-widest uppercase"
                style={{ color: 'var(--text-muted)' }}
              >
                Your Journey
              </span>
              <div className="h-px flex-1" style={{ backgroundColor: 'rgba(255,255,255,0.08)' }} />
            </div>

            <SceneTimeline
              timeline={timeline}
              selectedChoices={selectedChoices}
              localSelectedChoices={localSelectedChoice}
              choicesRevealedForScene={choicesRevealedForScene}
              generatingNextScene={generatingNextScene}
              onChoiceSelect={handleChoiceSelect}
              onRevealChoices={handleRevealChoices}
            />
          </motion.div>
        ) : (
          /* ── empty state ── */
          <motion.div
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="flex flex-col items-center justify-center py-24 gap-6 text-center"
          >
            <div
              className="w-20 h-20 rounded-3xl flex items-center justify-center text-4xl"
              style={{
                background: 'linear-gradient(135deg, rgba(124,58,237,0.3), rgba(168,85,247,0.15))',
                border: '1px solid rgba(167,139,250,0.2)',
              }}
            >
              📖
            </div>
            <div className="space-y-2">
              <p className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>
                No scenes yet
              </p>
              <p className="text-sm max-w-xs" style={{ color: 'var(--text-muted)' }}>
                This story hasn't started generating scenes. Come back shortly or continue the
                adventure from the beginning.
              </p>
            </div>
            <button
              onClick={() => navigate('/dashboard')}
              className="px-6 py-2.5 rounded-xl text-sm font-semibold transition hover:opacity-90"
              style={{
                background: 'linear-gradient(135deg, #7c3aed, #a855f7)',
                color: '#fff',
              }}
            >
              Back to Dashboard
            </button>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default StoryPage;
