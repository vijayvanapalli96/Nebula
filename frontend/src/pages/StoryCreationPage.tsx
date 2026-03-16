import React, { useEffect, useRef, useCallback, useMemo } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Sparkles } from 'lucide-react';

import { useStoryCreationStore } from '../store/storyCreationStore';
import { useThemeStore } from '../store/themeStore';
import { fetchStoryQuestions } from '../api/storyApi';
import type { StoryOpeningRequest } from '../api/storyApi';
import StoryLoadingScreen from '../features/storyCreation/StoryLoadingScreen';
import QuestionStep from '../features/storyCreation/QuestionStep';
import ProgressBar from '../features/storyCreation/ProgressBar';
import CustomStoryInput from '../features/storyCreation/CustomStoryInput';
import type { Genre } from '../types/story';

// ── slide direction tracker ─────────────────────────────────────────────────
type Direction = 1 | -1;

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
    selectedGenre,
    currentQuestionIndex,
    setQuestions,
    setAnswer,
    setCustomInput,
    setLoading,
    setStoryId,
    nextQuestion,
    previousQuestion,
    reset,
  } = useStoryCreationStore();

  // Track slide direction for AnimatePresence
  const directionRef = useRef<Direction>(1);

  // Fetch questions on mount
  useEffect(() => {
    const themeId = genre?.id ?? selectedGenre?.id ?? '';
    reset();
    setLoading(true);
    fetchStoryQuestions(themeId)
      .then(({ questions, storyId }) => {
        setQuestions(questions);
        setStoryId(storyId);
      })
      .finally(() => setLoading(false));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const totalQuestions = questions.length;
  const isCustomInputStep = currentQuestionIndex >= totalQuestions && totalQuestions > 0;
  const currentQuestion = !isCustomInputStep ? questions[currentQuestionIndex] : null;

  const allAnswered = useMemo(
    () => totalQuestions > 0 && questions.every((q) => answers[q.id] !== undefined),
    [totalQuestions, questions, answers],
  );

  // Called when user selects an option — store answer then auto-advance
  const handleSelect = useCallback(
    (questionId: string, label: string) => {
      setAnswer(questionId, label);
      // Advance after a short delay so the selection glow animates in first
      setTimeout(() => {
        directionRef.current = 1;
        nextQuestion();
      }, 480);
    },
    [setAnswer, nextQuestion],
  );

  const handleBack = useCallback(() => {
    if (currentQuestionIndex === 0) {
      navigate('/dashboard');
    } else {
      directionRef.current = -1;
      previousQuestion();
    }
  }, [currentQuestionIndex, navigate, previousQuestion]);

  const handleBegin = () => {
    const theme = selectedGenre?.title ?? genre?.title ?? 'Adventure';
    const character_name = customInput.trim() || 'The Protagonist';
    const payload: StoryOpeningRequest = {
      theme,
      character_name,
      answers: questions.map((q) => ({
        question: q.question,
        answer: answers[q.id] ?? '',
      })),
    };
    const storyId = useStoryCreationStore.getState().storyId;
    navigate('/story/generating', { state: { payload, storyId } });
  };

  const headerBg = isDark ? 'rgba(10,10,15,0.88)' : 'rgba(244,243,250,0.92)';
  const bottomBg = isDark ? 'rgba(10,10,15,0.94)' : 'rgba(244,243,250,0.96)';

  return (
    <div
      className="min-h-screen overflow-x-hidden flex flex-col"
      style={{ backgroundColor: 'var(--bg-base)' }}
    >
      <AnimatePresence mode="wait">
        {/* ─────────────── LOADING ─────────────── */}
        {loading && <StoryLoadingScreen key="loading" />}

        {/* ─────────────── QUESTION FLOW ─────────────── */}
        {!loading && questions.length > 0 && (
          <motion.div
            key="flow"
            className="flex flex-col min-h-screen"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4 }}
          >
            {/* Ambient glow */}
            <div
              className="fixed inset-x-0 top-0 h-96 pointer-events-none z-0"
              style={{
                background:
                  'radial-gradient(ellipse 70% 60% at 50% -10%, rgba(139,92,246,0.13) 0%, transparent 70%)',
              }}
            />

            {/* ── Sticky header ── */}
            <header
              className="sticky top-0 z-20 px-4 sm:px-8 h-14 flex items-center justify-between gap-4 flex-shrink-0"
              style={{
                backgroundColor: headerBg,
                backdropFilter: 'blur(18px)',
                borderBottom: '1px solid var(--border-color)',
              }}
            >
              <button
                onClick={handleBack}
                className="flex items-center gap-2 text-sm font-medium rounded-lg px-2 py-1.5"
                style={{ color: 'var(--text-secondary)', transition: 'color 0.15s, background 0.15s' }}
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
                <span className="hidden sm:inline">
                  {currentQuestionIndex === 0 ? 'Back' : 'Previous'}
                </span>
              </button>

              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-lg bg-violet-600 flex items-center justify-center">
                  <Sparkles size={12} className="text-white" />
                </div>
                <span className="text-sm font-black tracking-tight" style={{ color: 'var(--text-primary)' }}>
                  NEBULA
                </span>
              </div>

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
                <div className="w-20" />
              )}
            </header>

            {/* ── Main area ── */}
            <main className="relative z-10 flex-1 flex flex-col items-center justify-center px-4 sm:px-6 py-10">
              {/* Progress bar */}
              <div className="w-full max-w-2xl mb-10">
                <ProgressBar
                  current={isCustomInputStep ? totalQuestions - 1 : currentQuestionIndex}
                  total={totalQuestions}
                  isFinalStep={isCustomInputStep}
                />
              </div>

              {/* Animated step */}
              <div className="w-full max-w-2xl">
                <AnimatePresence mode="wait" custom={directionRef.current}>
                  {currentQuestion && (
                    <QuestionStep
                      key={currentQuestion.id}
                      question={currentQuestion}
                      selectedAnswer={answers[currentQuestion.id]}
                      onSelect={handleSelect}
                      direction={directionRef.current}
                    />
                  )}

                  {isCustomInputStep && (
                    <motion.div
                      key="custom-input"
                      custom={directionRef.current}
                      initial={{ opacity: 0, x: directionRef.current * 60, scale: 0.98 }}
                      animate={{ opacity: 1, x: 0, scale: 1, transition: { duration: 0.38, ease: [0.22, 1, 0.36, 1] as const } }}
                      exit={{ opacity: 0, x: directionRef.current * -60, scale: 0.98, transition: { duration: 0.28 } }}
                      className="w-full"
                    >
                      <CustomStoryInput value={customInput} onChange={setCustomInput} delay={0} />
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* Begin button — shown only on final step */}
              {isCustomInputStep && (
                <motion.div
                  className="w-full max-w-2xl mt-10"
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: 0.2 }}
                >
                  <motion.button
                    onClick={handleBegin}
                    disabled={!allAnswered}
                    whileHover={allAnswered ? { scale: 1.015 } : {}}
                    whileTap={allAnswered ? { scale: 0.985 } : {}}
                    className="w-full py-4 rounded-2xl font-bold text-sm tracking-wide"
                    style={{
                      backgroundColor: allAnswered ? '#7c3aed' : 'var(--input-bg)',
                      color: allAnswered ? '#fff' : 'var(--text-muted)',
                      border: `1.5px solid ${allAnswered ? 'rgba(139,92,246,0.55)' : 'var(--border-color)'}`,
                      boxShadow: allAnswered
                        ? '0 0 28px rgba(124,58,237,0.38), 0 0 56px rgba(124,58,237,0.12)'
                        : 'none',
                      cursor: allAnswered ? 'pointer' : 'not-allowed',
                      transition: 'background-color 0.25s, box-shadow 0.25s, border-color 0.25s, color 0.25s',
                    }}
                  >
                    ✦ Begin Your Story
                  </motion.button>
                </motion.div>
              )}
            </main>

            {/* ── Sticky bottom segment strip (question steps only) ── */}
            {!isCustomInputStep && (
              <div
                className="sticky bottom-0 z-20 px-4 sm:px-8 pt-3 pb-5 flex-shrink-0"
                style={{
                  backgroundColor: bottomBg,
                  backdropFilter: 'blur(20px)',
                  borderTop: '1px solid var(--border-color)',
                }}
              >
                <div className="max-w-2xl mx-auto flex items-center gap-1.5">
                  {questions.map((q, i) => (
                    <motion.div
                      key={q.id}
                      className="h-1 flex-1 rounded-full"
                      animate={{
                        backgroundColor:
                          i < currentQuestionIndex
                            ? '#7c3aed'
                            : i === currentQuestionIndex
                            ? '#a78bfa'
                            : isDark
                            ? 'rgba(255,255,255,0.09)'
                            : 'rgba(0,0,0,0.09)',
                      }}
                      transition={{ duration: 0.3 }}
                    />
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default StoryCreationPage;
