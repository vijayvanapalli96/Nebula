import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useStoryStore } from '../store/storyStore';

const StoryPage: React.FC = () => {
  const { storyId } = useParams<{ storyId: string }>();
  const story = useStoryStore((s) => s.stories.find((st) => st.id === storyId));

  if (!story) {
    return (
      <main className="min-h-screen bg-[#0a0a0f] flex flex-col items-center justify-center text-white gap-4">
        <p className="text-gray-400">Story not found.</p>
        <Link to="/" className="text-violet-400 hover:underline text-sm">
          ← Back to Home
        </Link>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#0a0a0f] text-white">
      {/* Hero banner */}
      <div className="relative h-72 sm:h-96 overflow-hidden">
        <img
          src={story.coverImage}
          alt={story.title}
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0f] via-black/50 to-transparent" />
        <Link
          to="/"
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

        <div>
          <div className="flex justify-between text-xs text-gray-400 mb-2">
            <span>Progress</span>
            <span className="text-violet-400">{story.progress}%</span>
          </div>
          <div className="h-2 rounded-full bg-white/10 overflow-hidden">
            <motion.div
              className="h-full rounded-full bg-violet-500"
              initial={{ width: 0 }}
              animate={{ width: `${story.progress}%` }}
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
