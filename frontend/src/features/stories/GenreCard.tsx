import React, { memo, useCallback, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { useStoryCreationStore } from "../../store/storyCreationStore";
import type { Genre } from "../../types/story";

interface Props {
  genre: Genre;
}

const GenreCard: React.FC<Props> = ({ genre }) => {
  const navigate = useNavigate();
  const setSelectedGenre = useStoryCreationStore((s) => s.setSelectedGenre);
  const [hovered, setHovered] = useState(false);

  const handleClick = useCallback(() => {
    setSelectedGenre(genre);
    navigate('/story/create', { state: { genre } });
  }, [setSelectedGenre, navigate, genre]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        setSelectedGenre(genre);
        navigate('/story/create', { state: { genre } });
      }
    },
    [setSelectedGenre, navigate, genre],
  );

  return (
    <motion.article
      role="button"
      tabIndex={0}
      aria-label={`Start a new ${genre.title} story. ${genre.tagline}`}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      onHoverStart={() => setHovered(true)}
      onHoverEnd={() => setHovered(false)}
      className="relative flex-shrink-0 w-68 sm:w-80 rounded-2xl overflow-hidden cursor-pointer outline-none focus-visible:ring-2 focus-visible:ring-violet-500 card-shadow"
      style={{ height: "420px", willChange: "transform" }}
      whileHover={{ scale: 1.04, y: -8 }}
      whileTap={{ scale: 0.97 }}
      transition={{ type: "spring", stiffness: 280, damping: 22 }}
    >
      <div className="absolute inset-0 overflow-hidden">
        <motion.img
          src={genre.image}
          alt={genre.title}
          loading="lazy"
          className="w-full h-full object-cover"
          animate={{ scale: hovered ? 1.1 : 1 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
        />
      </div>

      <div className="absolute inset-0 bg-gradient-to-t from-black/95 via-black/40 to-black/10" />

      <motion.div
        className="absolute inset-0 rounded-2xl pointer-events-none"
        animate={{ opacity: hovered ? 1 : 0 }}
        transition={{ duration: 0.3 }}
        style={{
          boxShadow: `inset 0 0 0 2px ${genre.accentColor}, 0 0 50px ${genre.accentColor}`,
        }}
      />

      <div className="absolute inset-x-0 bottom-0 p-5">
        <h3 className="text-sm font-black text-white uppercase tracking-[0.15em] drop-shadow-lg">
          {genre.title}
        </h3>
        <p className="text-xs text-gray-300 mt-1.5 leading-relaxed">{genre.tagline}</p>

        <AnimatePresence>
          {hovered && (
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 8 }}
              transition={{ duration: 0.25 }}
              className="mt-3 space-y-2"
            >
              {genre.description.split("\n").map((line, i) => (
                <p key={i} className="text-xs text-white/70 leading-relaxed">{line}</p>
              ))}
              <div
                className="mt-3 inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-white uppercase tracking-wider"
                style={{ backgroundColor: genre.accentColor }}
              >
                <span>Start This Story</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.article>
  );
};

export default memo(GenreCard);
