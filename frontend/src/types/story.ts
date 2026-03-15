export interface Story {
  id: string;
  title: string;
  genre: string;
  progress: number; // 0–100
  coverImage: string;
  lastPlayed: string; // ISO date string
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
