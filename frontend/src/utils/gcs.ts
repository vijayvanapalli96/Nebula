/**
 * Utility for converting GCS object paths to publicly accessible URLs.
 *
 * The GCS bucket `nebula-story-images` must have public read access
 * (allUsers Storage Object Viewer) for these URLs to work.
 *
 * GCS path format stored in Firestore / returned by /story/media:
 *   {user_id}/story/{story_id}/scene/{scene_id}/choice/{choice_id}/image.png
 *   {user_id}/story/{story_id}/scene/{scene_id}/choice/{choice_id}/video.mp4
 */

const GCS_BUCKET = 'nebula-story-images';
const GCS_BASE = `https://storage.googleapis.com/${GCS_BUCKET}`;

/**
 * Convert a raw GCS object path to a public https:// URL.
 * Returns null if the path is empty/null.
 * Passes through values that are already full URLs (handles any legacy signed URLs).
 */
export function gcsPathToUrl(path: string | null | undefined): string | null {
  if (!path) return null;
  if (path.startsWith('http://') || path.startsWith('https://')) return path;
  return `${GCS_BASE}/${path}`;
}
