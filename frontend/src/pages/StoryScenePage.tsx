import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

import { useStorySessionStore } from '../store/storySessionStore';
import SceneDisplay from '../features/story/SceneDisplay';
import { fetchSceneMedia } from '../api/storyApi';
import { gcsPathToUrl } from '../utils/gcs';

const StoryScenePage: React.FC = () => {
  const navigate = useNavigate();
  const { currentScene, updateChoiceMedia, isGenerating, error, continueStory } = useStorySessionStore();

  // Guard: if no scene loaded, go back to dashboard
  useEffect(() => {
    if (!currentScene) {
      navigate('/dashboard', { replace: true });
    }
  }, [currentScene, navigate]);

  const [mediaLoading, setMediaLoading] = useState(false);
  const [mediaLoaded, setMediaLoaded] = useState(false);

  const startMediaPolling = async () => {
    if (!currentScene?.story_id || mediaLoading || mediaLoaded) return;
    setMediaLoading(true);
    try {
      const items = await fetchSceneMedia(currentScene.story_id, 'scene_001');
      const assets: Record<string, string | null> = {};
      for (const item of items) {
        assets[`choice_${item.choice_id}_image`] = item.image_url ?? null;
        assets[`choice_${item.choice_id}_video`] = item.video_url ?? null;
      }
      updateChoiceMedia(assets);
      setMediaLoaded(true);
    } catch {
      // Silently ignore errors — user can retry
    } finally {
      setMediaLoading(false);
    }
  };

  if (!currentScene) return null;

  const handleChoiceSelect = (choiceId: string) => {
    if (isGenerating) return;
    continueStory(choiceId);
  };

  return (
    <div
      className="fixed inset-0 flex flex-col overflow-hidden"
      style={{ backgroundColor: 'var(--bg-base)' }}
    >
      {/* ── Ambient background ── */}
      <motion.div
        className="absolute inset-0 pointer-events-none"
        animate={{
          background: [
            'radial-gradient(ellipse 90% 65% at 50% 20%, rgba(139,92,246,0.1) 0%, transparent 60%)',
            'radial-gradient(ellipse 90% 65% at 50% 20%, rgba(96,165,250,0.08) 0%, transparent 60%)',
            'radial-gradient(ellipse 90% 65% at 50% 20%, rgba(139,92,246,0.1) 0%, transparent 60%)',
          ],
        }}
        transition={{ duration: 10, repeat: Infinity, ease: 'linear' }}
      />

      {/* ── Top bar ── */}
      <motion.header
        className="flex-shrink-0 flex items-center justify-between px-6 py-4"
        style={{
          borderBottom: '1px solid var(--border-color)',
          backdropFilter: 'blur(8px)',
          zIndex: 10,
        }}
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2 text-sm font-medium transition-colors"
          style={{ color: 'var(--text-muted)' }}
          onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--text-primary)')}
          onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-muted)')}
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path
              d="M10 12L6 8l4-4"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          Dashboard
        </button>

        {/* Scene depth indicator */}
        <div className="flex items-center gap-2">
          {currentScene.depth !== undefined && currentScene.depth > 0 && (
            <span
              className="text-[10px] font-bold tracking-widest uppercase px-3 py-1 rounded-full"
              style={{
                backgroundColor: 'rgba(52,211,153,0.12)',
                border: '1px solid rgba(52,211,153,0.3)',
                color: '#6ee7b7',
              }}
            >
              Scene {(currentScene.depth ?? 0) + 1}
            </span>
          )}
        </div>

        {/* Floating "View Story Path" button */}
        <motion.button
          onClick={() => navigate('/story/graph')}
          className="flex items-center gap-2 text-xs font-semibold px-4 py-2 rounded-full"
          style={{
            background: 'rgba(139,92,246,0.15)',
            border: '1px solid rgba(139,92,246,0.35)',
            color: '#a78bfa',
          }}
          whileHover={{ scale: 1.04, backgroundColor: 'rgba(139,92,246,0.25)' }}
          whileTap={{ scale: 0.96 }}
        >
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <circle cx="7" cy="2.5" r="1.5" fill="currentColor" />
            <circle cx="2.5" cy="10.5" r="1.5" fill="currentColor" />
            <circle cx="11.5" cy="10.5" r="1.5" fill="currentColor" />
            <line x1="7" y1="4" x2="2.5" y2="9" stroke="currentColor" strokeWidth="1.2" />
            <line x1="7" y1="4" x2="11.5" y2="9" stroke="currentColor" strokeWidth="1.2" />
          </svg>
          View Story Path
        </motion.button>
      </motion.header>

      {/* ── Main content ── */}
      <div className="flex-1 overflow-y-auto">
        <div className="min-h-full flex flex-col items-center justify-center py-16 px-4">
          {/* ── Generating overlay ── */}
          <AnimatePresence>
            {isGenerating && (
              <motion.div
                className="fixed inset-0 z-50 flex flex-col items-center justify-center"
                style={{ backgroundColor: 'rgba(10, 10, 15, 0.85)', backdropFilter: 'blur(8px)' }}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <motion.div
                  className="w-16 h-16 rounded-full"
                  style={{
                    border: '3px solid transparent',
                    borderTopColor: '#8b5cf6',
                    borderRightColor: 'rgba(139,92,246,0.3)',
                  }}
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1.2, repeat: Infinity, ease: 'linear' }}
                />
                <motion.p
                  className="mt-6 text-sm font-medium"
                  style={{ color: '#a78bfa' }}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.3 }}
                >
                  Generating next scene...
                </motion.p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* ── Error message ── */}
          {error && (
            <motion.div
              className="w-full max-w-3xl mb-6 px-4 py-3 rounded-xl text-sm"
              style={{
                backgroundColor: 'rgba(239,68,68,0.12)',
                border: '1px solid rgba(239,68,68,0.3)',
                color: '#fca5a5',
              }}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              {error}
            </motion.div>
          )}

          <SceneDisplay scene={currentScene} />

          {/* ── Choices ── */}
          {currentScene.choices.length > 0 && (
            <motion.div
              className="w-full max-w-3xl mt-12 px-4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.2, duration: 0.5 }}
            >
              <div className="flex items-center justify-between mb-4">
                <p
                  className="text-xs font-semibold uppercase tracking-widest"
                  style={{ color: 'var(--text-muted)' }}
                >
                  Your Choices
                </p>
                {!mediaLoaded && (
                  <button
                    onClick={startMediaPolling}
                    disabled={mediaLoading}
                    className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg transition-opacity"
                    style={{
                      background: 'rgba(139,92,246,0.15)',
                      border: '1px solid rgba(139,92,246,0.3)',
                      color: '#a78bfa',
                      opacity: mediaLoading ? 0.6 : 1,
                    }}
                  >
                    {mediaLoading ? (
                      <>
                        <svg className="animate-spin" width="12" height="12" viewBox="0 0 12 12" fill="none">
                          <circle cx="6" cy="6" r="4.5" stroke="currentColor" strokeWidth="1.5" strokeDasharray="14 6" />
                        </svg>
                        Generating…
                      </>
                    ) : 'Load Images'}
                  </button>
                )}
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {currentScene.choices.map((choice, i) => (
                  <motion.button
                    key={choice.choice_id}
                    onClick={() => handleChoiceSelect(choice.choice_id)}
                    disabled={isGenerating}
                    className="rounded-xl overflow-hidden text-sm text-left transition-all"
                    style={{
                      backgroundColor: 'var(--bg-card)',
                      border: '1px solid var(--border-color)',
                      cursor: isGenerating ? 'not-allowed' : 'pointer',
                      opacity: isGenerating ? 0.5 : 1,
                    }}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 1.3 + i * 0.07 }}
                    whileHover={!isGenerating ? {
                      scale: 1.02,
                      borderColor: 'rgba(139,92,246,0.5)',
                      boxShadow: '0 0 20px rgba(139,92,246,0.15)',
                    } : {}}
                    whileTap={!isGenerating ? { scale: 0.98 } : {}}
                  >
                    {/* Choice image thumbnail — shown once GCS path arrives via polling */}
                    {gcsPathToUrl(choice.image_url) && (
                      <img
                        src={gcsPathToUrl(choice.image_url)!}
                        alt={choice.choice_text}
                        className="w-full h-24 object-cover"
                        loading="lazy"
                      />
                    )}
                    <div className="px-4 py-3">
                      <p
                        className="font-semibold leading-snug"
                        style={{ color: 'var(--text-primary)' }}
                      >
                        {choice.choice_text}
                      </p>
                      {choice.direction_hint && (
                        <p
                          className="text-xs mt-1"
                          style={{ color: 'var(--text-muted)' }}
                        >
                          {choice.direction_hint}
                        </p>
                      )}
                    </div>
                  </motion.button>
                ))}
              </div>
            </motion.div>
          )}

          {/* ── CTA ── */}
          <motion.div
            className="mt-10"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.5 }}
          >
            <motion.button
              onClick={() => navigate('/story/graph')}
              className="flex items-center gap-3 px-8 py-3.5 rounded-2xl text-sm font-bold"
              style={{
                backgroundImage: 'linear-gradient(135deg, #7c3aed, #4f46e5)',
                color: '#fff',
                boxShadow: '0 4px 24px rgba(139,92,246,0.4)',
              }}
              whileHover={{ scale: 1.04, boxShadow: '0 6px 32px rgba(139,92,246,0.55)' }}
              whileTap={{ scale: 0.97 }}
            >
              Explore Story Path
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path
                  d="M6 4l4 4-4 4"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </motion.button>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default StoryScenePage;
