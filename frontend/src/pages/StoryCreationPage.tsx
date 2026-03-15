import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Sparkles } from 'lucide-react';

import { useStoryCreationStore } from '../store/storyCreationStore';
import { useThemeStore } from '../store/themeStore';
import { fetchStoryQuestions } from '../api/storyApi';
import StoryLoadingScreen from '../features/storyCreation/StoryLoadingScreen';
import QuestionCard from '../features/storyCreation/QuestionCard';
import CustomStoryInput from '../features/storyCreation/CustomStoryInput';
import type { Genre } from '../types/story';

const StoryCreationPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const genre = (location.state as { genre?: Genre } | null)?.genre ?? null;

  const { isDark } = useThemeStore();
  const {
    questions,
    answers,
    customInput,
    loading,
    setQuestions,
    setAnswer,
    setCustomInput,
    setLoading,
    reset,
  } = useStoryCreationStore();

  // Fetch questions once on mount
  useEffect(() => {
    reset();
    setLoading(true);
    fetchStoryQuestions()
      .then(({ questions }) => setQuestions(questions))
      .finally(() => setLoading(false));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const unansweredCount = questions.filter((q) => !answers[q.id]).length;
  const allAnswered = questions.length > 0 && unansweredCount === 0;

  const handleBegin = () => {
    // Navigate to story player — replace with the real route in the next phase
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen overflow-x-hidden" style={{ backgroundColor: 'var(--bg-base)' }}>
      <AnimatePresence mode="wait">
        {loading ? (
          <StoryLoadingScreen key="loading" />
        ) : (
          <motion.div
            key="questions"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            {/* Ambient top glow */}
            <div
              className="fixed inset-x-0 top-0 h-96 pointer-events-none z-0"
              style={{
                background:
                  'radial-gradient(ellipse 70% 60% at 50% -10%, rgba(139,92,246,0.14) 0%, transparent 70%)',
              }}
            />

            {/* ── Sticky header ── */}
            <header
              className="sticky top-0 z-20 px-4 sm:px-8 h-14 flex items-center justify-between gap-4"
              style={{
                backgroundColor: isDark ? 'rgba(10,10,15,0.88)' : 'rgba(244,243,250,0.92)',
                backdropFilter: 'blur(18px)',
                borderBottom: '1px solid var(--border-color)',
              }}
            >
              {/* Back */}
              <button
                onClick={() => navigate('/dashboard')}
                className="flex items-center gap-2 text-sm font-medium rounded-lg px-2 py-1.5 transition-colors"
                style={{ color: 'var(--text-secondary)' }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.color = 'var(--text-primary)';
                  e.currentTarget.style.backgroundColor = 'var(--sidebar-hover)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.color = 'var(--text-secondary)';
                  e.currentTarget.style.backgroundColor = 'transparent';
                }}
              >
                <ArrowLeft size={15} />
                <span className="hidden sm:inline">Back</span>
              </button>

              {/* Logo */}
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-lg bg-violet-600 flex items-center justify-center glow-purple">
                  <Sparkles size={12} className="text-white" />
                </div>
                <span className="text-sm font-black tracking-tight" style={{ color: 'var(--text-primary)' }}>NEBULA</span>
              </div>

              {/* Genre badge */}
              {genre ? (
                <span
                  className="text-[10px] font-bold tracking-widest uppercase px-3 py-1 rounded-full"
                  style={{
                    backgroundColor: 'rgba(139,92,246,0.12)',
                    border: '1px solid rgba(139,92,246,0.28)',
                    color: '#a78bfa',
                  }}
                >
                  {genre.title}
                </span>
              ) : (
                <div className="w-20" /> /* placeholder to keep logo centred */
              )}
            </header>

            {/* ── Page content ── */}
            <main className="relative z-10 max-w-2xl mx-auto px-4 sm:px-6 pt-10 pb-44 space-y-14">
              {/* Page title */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.55 }}
                className="space-y-2"
              >
                <p className="text-[10px] font-bold tracking-[0.25em] uppercase text-violet-400">
                  Story Creation
                </p>
                <h1
                  className="text-3xl sm:text-4xl font-black leading-tight"
                  style={{
                    backgroundImage: isDark
                      ? 'linear-gradient(135deg, #f0f0f5 0%, #a78bfa 50%, #60a5fa 100%)'
                      : 'linear-gradient(135deg, #1e1b4b 0%, #7c3aed 50%, #1d4ed8 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                  }}
                >
                  Shape your story
                </h1>
                <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                  Answer a few questions and the AI will craft a unique narrative just for you.
                </p>
              </motion.div>

              {/* Questions */}
              <div className="space-y-12">
                {questions.map((question, index) => (
                  <QuestionCard
                    key={question.id}
                    question={question}
                    index={index}
                    selectedAnswer={answers[question.id]}
                    onSelect={setAnswer}
                  />
                ))}
              </div>

              {/* Custom input — only show once questions are loaded */}
              {questions.length > 0 && (
                <CustomStoryInput
                  value={customInput}
                  onChange={setCustomInput}
                  delay={questions.length * 0.13 + 0.2}
                />
              )}
            </main>

            {/* ── Sticky bottom bar ── */}
            <div
              className="fixed bottom-0 inset-x-0 z-20 px-4 sm:px-6 pt-3 pb-5"
              style={{
                backgroundColor: isDark ? 'rgba(10,10,15,0.94)' : 'rgba(244,243,250,0.96)',
                backdropFilter: 'blur(20px)',
                borderTop: '1px solid var(--border-color)',
              }}
            >
              <div className="max-w-2xl mx-auto space-y-3">
                {/* Progress bar — one segment per question */}
                <div className="flex items-center gap-1.5">
                  {questions.map((q) => (
                    <motion.div
                      key={q.id}
                      className="h-1 flex-1 rounded-full"
                      animate={{
                        backgroundColor: answers[q.id]
                          ? '#7c3aed'
                          : isDark ? 'rgba(255,255,255,0.09)' : 'rgba(0,0,0,0.09)',
                      }}
                      transition={{ duration: 0.3 }}
                    />
                  ))}
                </div>

                {/* Begin button */}
                <motion.button
                  onClick={handleBegin}
                  disabled={!allAnswered}
                  whileHover={allAnswered ? { scale: 1.015 } : {}}
                  whileTap={allAnswered ? { scale: 0.985 } : {}}
                  className="w-full py-4 rounded-2xl font-bold text-sm tracking-wide"
                  style={{
                    backgroundColor: allAnswered ? '#7c3aed' : 'var(--input-bg)',
                    color: allAnswered ? '#fff' : 'var(--text-muted)',
                    border: `1.5px solid ${
                      allAnswered ? 'rgba(139,92,246,0.55)' : 'var(--border-color)'
                    }`,
                    boxShadow: allAnswered
                      ? '0 0 28px rgba(124,58,237,0.38), 0 0 56px rgba(124,58,237,0.12)'
                      : 'none',
                    cursor: allAnswered ? 'pointer' : 'not-allowed',
                    transition: 'background-color 0.25s, box-shadow 0.25s, border-color 0.25s, color 0.25s',
                  }}
                >
                  {allAnswered
                    ? '✦ Begin Your Story'
                    : `Answer ${unansweredCount} more question${unansweredCount !== 1 ? 's' : ''} to continue`}
                </motion.button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default StoryCreationPage;
