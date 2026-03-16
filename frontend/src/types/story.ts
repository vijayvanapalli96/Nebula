export interface Story {
  id: string;
  title: string;
  genre: string;
  progress: number; // 0–100
  coverImage: string;
  lastPlayed: string; // ISO date string
}

/** Shape returned by GET /stories/me */
export interface UserStory {
  story_id: string;
  session_id: string;
  title: string;
  genre: string;
  character_name: string;
  archetype: string;
  last_scene_id: string | null;
  updated_at: string;
  choices_available: number;
  progress: number | null;
  cover_image: string | null;
  last_played_at: string | null;
  status: string | null;
  theme_id: string | null;
  theme_title: string | null;
  theme_description: string | null;
}

/** Shape returned by GET /story/{user_id}/{story_id} */
export interface StoryDetail {
  story_id: string;
  user_id: string;
  session_id: string;
  title: string;
  genre: string;
  character_name: string;
  archetype: string;
  last_scene_id: string | null;
  updated_at: string;
  choices_available: number;
  progress: number | null;
  cover_image: string | null;
  last_played_at: string | null;
  status: string | null;
  theme_id: string | null;
  theme_title: string | null;
  theme_category: string | null;
  theme_description: string | null;
  question_count: number | null;
  questions_generated: string[];
  created_at: string | null;
}

export interface Genre {
  id: string;
  title: string;
  tagline: string;
  description: string;
  image: string;
  accentColor: string; // for the glow tint
}

export type Archetype =
  | 'The Detective'
  | 'The Rebel'
  | 'The Scholar'
  | 'The Outlaw'
  | 'The Wanderer'
  | 'The Hero';

export type Motivation =
  | 'Seek Justice'
  | 'Uncover the Truth'
  | 'Protect the Innocent'
  | 'Pursue Power'
  | 'Find Redemption'
  | 'Survive at All Costs';

export interface NewStoryForm {
  characterName: string;
  archetype: Archetype | '';
  motivation: Motivation | '';
}
