import React, { useEffect, useState } from 'react';
import { useParams, Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { fetchStoryDetail } from '../api/storyApi';
import type { StoryDetail } from '../types/story';

interface StoryPageLocationState {
  storyDetail?: StoryDetail;
}

function formatRelativeTime(isoDate: string | null): string {
  if (!isoDate) return 'Not played yet';
  const diff = Date.now() - new Date(isoDate).getTime();
  const minutes = Math.floor(diff / 60_000);
  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

const HERO_GRADIENT = 'linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4c1d95 100%)';

const StoryPage: React.FC = () => {
  const { storyId } = useParams<{ storyId: string }>();
  const location = useLocation();
  const locationState = location.state as StoryPageLocationState | null;
  const initialStory =
    locationState?.storyDetail && locationState.storyDetail.story_id === storyId
      ? locationState.storyDetail
      : null;

  const [story, setStory] = useState<StoryDetail | null>(initialStory);
  const [loading, setLoading] = useState<boolean>(Boolean(storyId) && !initialStory);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!storyId) {
      setError('Story ID is missing.');
      setLoading(false);
      return;
    }

    if (initialStory && initialStory.story_id === storyId) {
      setStory(initialStory);
      setError(null);
      setLoading(false);
      return;
    }

    let isMounted = true;
    setLoading(true);
    setError(null);

    void fetchStoryDetail(storyId)
      .then((payload) => {
        if (!isMounted) return;
        setStory(payload);
      })
      .catch((err) => {
        if (!isMounted) return;
        setError(err instanceof Error ? err.message : 'Failed to load story.');
      })
      .finally(() => {
        if (!isMounted) return;
        setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [storyId, initialStory]);

  if (loading) {
    return (
      <main className="min-h-screen bg-[#0a0a0f] flex flex-col items-center justify-center text-white gap-4">
        <div className="w-8 h-8 rounded-full border-2 border-violet-500 border-t-transparent animate-spin" />
        <p className="text-gray-400 text-sm">Loading story…</p>
      </main>
    );
  }

  if (!story || error) {
    return (
      <main className="min-h-screen bg-[#0a0a0f] flex flex-col items-center justify-center text-white gap-4">
        <p className="text-gray-300">Story not found.</p>
        {error ? <p className="text-gray-500 text-sm">{error}</p> : null}
        <Link to="/dashboard" className="text-violet-400 hover:underline text-sm">
          ← Back to Dashboard
        </Link>
      </main>
    );
  }

  const progress = story.progress ?? 0;
  const lastPlayedLabel = formatRelativeTime(story.last_played_at ?? story.updated_at);

  return (
    <main className="min-h-screen bg-[#0a0a0f] text-white">
      {/* Hero banner */}
      <div className="relative h-72 sm:h-96 overflow-hidden">
        {story.cover_image ? (
          <img
            src={story.cover_image}
            alt={story.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full" style={{ background: HERO_GRADIENT }} />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0f] via-black/50 to-transparent" />
        <Link
          to="/dashboard"
          className="absolute top-6 left-6 text-xs font-semibold text-white/70 hover:text-white transition"
        >
          ← Back
        </Link>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-2xl mx-auto px-6 -mt-16 relative z-10 pb-16 space-y-6"
      >
        <span className="inline-block text-[10px] font-bold tracking-widest uppercase px-3 py-1 rounded-full bg-violet-600/20 border border-violet-500/30 text-violet-300">
          {story.genre}
        </span>
        <h1 className="text-3xl sm:text-4xl font-black">{story.title}</h1>
        <p className="text-sm text-violet-200/80">
          {story.character_name} · {story.archetype}
        </p>
        <p className="text-xs text-gray-400">Last played {lastPlayedLabel}</p>

        <div>
          <div className="flex justify-between text-xs text-gray-400 mb-2">
            <span>Progress</span>
            <span className="text-violet-400">{progress}%</span>
          </div>
          <div className="h-2 rounded-full bg-white/10 overflow-hidden">
            <motion.div
              className="h-full rounded-full bg-violet-500"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 1.2, ease: 'easeOut' }}
            />
          </div>
        </div>

        <button className="px-8 py-3 rounded-2xl bg-violet-600 hover:bg-violet-500 font-bold text-sm transition glow-purple">
          ▶ Resume Story
        </button>
      </motion.div>
    </main>
  );
};

export default StoryPage;
