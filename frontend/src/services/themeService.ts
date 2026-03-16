import { fetchStoryThemes } from '../api/storyApi';
import type { Genre } from '../types/story';

/**
 * Loads story themes from the backend API.
 * Throws if the API is unavailable or returns an empty list
 * so the loading page can surface a retry UI.
 */
export async function loadThemes(): Promise<Genre[]> {
  const themes = await fetchStoryThemes();
  if (themes.length === 0) {
    throw new Error('No themes returned from the server.');
  }
  return themes;
}
