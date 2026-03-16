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

/** A single choice inside a Firestore scene document (camelCase from Firestore). */
export interface SceneDocChoice {
  choiceId: string;
  choiceText: string;
  directionHint: string;
  imagePrompt?: string;
  videoPrompt?: string;
  /** Scene ID this choice leads to — null means user hasn't selected/generated the next scene yet. */
  nextSceneId: string | null;
  /** GCS object path — convert to URL with gcsPathToUrl(). */
  imageUrl: string | null;
  /** GCS object path — convert to URL with gcsPathToUrl(). */
  videoUrl: string | null;
}

/** A scene document as stored in Firestore (camelCase keys). */
export interface SceneDoc {
  sceneId: string;
  title: string;
  description: string;
  isRoot?: boolean;
  depth?: number;
  parentSceneId?: string | null;
  nextSceneIds?: string[];
  choices: SceneDocChoice[];
  createdAt?: string;
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
  // Extended fields populated from Firestore subcollections
  root_scene_id: string | null;
  branch_depth: number | null;
  questionnaire_completed: boolean | null;
  custom_input: string | null;
  theme_image_url: string | null;
  questions: Record<string, unknown>[];
  answers: Record<string, unknown>[];
  /** Raw Firestore scene documents. Use buildSceneTimeline() to get the ordered path. */
  scenes: SceneDoc[];
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
