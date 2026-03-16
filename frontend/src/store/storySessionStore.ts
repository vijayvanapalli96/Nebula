import { create } from 'zustand';
import type { Node, Edge } from '@xyflow/react';

// ── Domain types ────────────────────────────────────────────────────────────

export interface Choice {
  choice_id: string;
  choice_text: string;
  direction_hint: string;
  /** GCS object path — convert to URL with gcsPathToUrl() from utils/gcs.ts */
  image_url?: string | null;
  /** GCS object path — convert to URL with gcsPathToUrl() from utils/gcs.ts */
  video_url?: string | null;
}

export interface Scene {
  story_id: string;
  theme: string;
  character_name: string;
  scene_title: string;
  scene_description: string;
  summary?: string;
  choices: Choice[];
  // Fields populated by continuation responses
  scene_id?: string;
  parent_scene_id?: string;
  depth?: number;
  media_request_id?: string | null;
}

// ── Graph node/edge data types ───────────────────────────────────────────────

export interface SceneNodeData extends Record<string, unknown> {
  label: string;
  description?: string;
  type: 'scene';
}

export interface ChoiceNodeData extends Record<string, unknown> {
  label: string;
  hint: string;
  choiceId: string;
  type: 'choice';
  selected: boolean;
}

export type GraphNodeData = SceneNodeData | ChoiceNodeData;

// ── Store ────────────────────────────────────────────────────────────────────

interface StorySessionState {
  currentScene: Scene | null;
  sceneHistory: Scene[];
  selectedChoice: string | null;
  isGenerating: boolean;
  error: string | null;
  graphNodes: Node<GraphNodeData>[];
  graphEdges: Edge[];

  setScene: (scene: Scene) => void;
  selectChoice: (choiceId: string) => void;
  /**
   * Merge media assets from /story/media polling into the current scene's choices.
   * @param assets Record<asset_key, gcs_path | null> e.g. { choice_A_image: "uid/story/.../A/image.png" }
   */
  updateChoiceMedia: (assets: Record<string, string | null>) => void;
  continueStory: (choiceId: string) => Promise<void>;
  setGenerating: (value: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

/** Builds a React Flow graph from a scene's choices. */
function buildGraph(scene: Scene): {
  nodes: Node<GraphNodeData>[];
  edges: Edge[];
} {
  const sceneNode: Node<SceneNodeData> = {
    id: 'scene-root',
    type: 'sceneNode',
    position: { x: 0, y: 0 },
    data: {
      label: scene.scene_title,
      description: scene.scene_description.slice(0, 120) + '…',
      type: 'scene',
    },
  };

  const COLS = 3;
  const CARD_W = 200;
  const H_GAP = 40;
  const V_GAP = 120;

  const choiceNodes: Node<ChoiceNodeData>[] = scene.choices.map((c, i) => ({
    id: `choice-${c.choice_id}`,
    type: 'choiceNode',
    position: {
      x: (i - (Math.min(scene.choices.length, COLS) - 1) / 2) * (CARD_W + H_GAP),
      y: V_GAP,
    },
    data: {
      label: c.choice_text,
      hint: c.direction_hint,
      choiceId: c.choice_id,
      type: 'choice',
      selected: false,
    },
  }));

  const edges: Edge[] = scene.choices.map((c) => ({
    id: `edge-root-${c.choice_id}`,
    source: 'scene-root',
    target: `choice-${c.choice_id}`,
    type: 'smoothstep',
    animated: true,
    style: { stroke: 'rgba(139,92,246,0.5)', strokeWidth: 2 },
  }));

  return { nodes: [sceneNode, ...choiceNodes], edges };
}

export const useStorySessionStore = create<StorySessionState>((set, get) => ({
  currentScene: null,
  sceneHistory: [],
  selectedChoice: null,
  isGenerating: false,
  error: null,
  graphNodes: [],
  graphEdges: [],

  setScene: (scene) => {
    const { nodes, edges } = buildGraph(scene);
    set((state) => ({
      currentScene: scene,
      selectedChoice: null,
      graphNodes: nodes,
      graphEdges: edges,
      sceneHistory: [...state.sceneHistory, scene],
      error: null,
    }));
  },

  selectChoice: (choiceId) => {
    const nodes = get().graphNodes.map((n) => {
      if (n.data.type === 'choice') {
        return {
          ...n,
          data: { ...n.data, selected: n.data.choiceId === choiceId },
        };
      }
      return n;
    });
    set({ selectedChoice: choiceId, graphNodes: nodes });
  },

  updateChoiceMedia: (assets) =>
    set((state) => {
      if (!state.currentScene) return state;
      const choices = state.currentScene.choices.map((c) => {
        const imgPath = assets[`choice_${c.choice_id}_image`];
        const vidPath = assets[`choice_${c.choice_id}_video`];
        return {
          ...c,
          ...(imgPath !== undefined ? { image_url: imgPath } : {}),
          ...(vidPath !== undefined ? { video_url: vidPath } : {}),
        };
      });
      return { currentScene: { ...state.currentScene, choices } };
    }),

  continueStory: async (choiceId: string) => {
    const { currentScene } = get();
    if (!currentScene) return;

    set({ isGenerating: true, error: null, selectedChoice: choiceId });

    try {
      const { fetchContinuationScene } = await import('../api/storyApi');

      // Determine current scene id — opening scene is always "scene_001"
      const currentSceneId = currentScene.scene_id ?? 'scene_001';
      // For parent scene, use the parent if this is a continuation, otherwise empty
      const previousSceneId = currentScene.parent_scene_id ?? '';

      const response = await fetchContinuationScene({
        story_id: currentScene.story_id,
        previous_scene_id: previousSceneId,
        current_scene_id: currentSceneId,
        choice_id: choiceId,
      });

      // Map the continuation response to our Scene type
      const nextScene: Scene = {
        story_id: response.story_id,
        theme: currentScene.theme,
        character_name: currentScene.character_name,
        scene_title: response.scene_title,
        scene_description: response.scene_description,
        summary: response.summary,
        choices: response.choices.map((c) => ({
          choice_id: c.choice_id,
          choice_text: c.choice_text,
          direction_hint: c.direction_hint,
        })),
        scene_id: response.scene_id,
        parent_scene_id: response.parent_scene_id,
        depth: response.depth,
        media_request_id: response.media_request_id,
      };

      get().setScene(nextScene);
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Failed to continue story.' });
    } finally {
      set({ isGenerating: false });
    }
  },

  setGenerating: (value) => set({ isGenerating: value }),
  setError: (error) => set({ error }),

  reset: () => set({
    currentScene: null,
    sceneHistory: [],
    selectedChoice: null,
    isGenerating: false,
    error: null,
    graphNodes: [],
    graphEdges: [],
  }),
}));
