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
  choices: Choice[];
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
  selectedChoice: string | null;
  graphNodes: Node<GraphNodeData>[];
  graphEdges: Edge[];

  setScene: (scene: Scene) => void;
  selectChoice: (choiceId: string) => void;
  /**
   * Merge media assets from /story/media polling into the current scene's choices.
   * @param assets Record<asset_key, gcs_path | null> e.g. { choice_A_image: "uid/story/.../A/image.png" }
   */
  updateChoiceMedia: (assets: Record<string, string | null>) => void;
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
  selectedChoice: null,
  graphNodes: [],
  graphEdges: [],

  setScene: (scene) => {
    const { nodes, edges } = buildGraph(scene);
    set({ currentScene: scene, selectedChoice: null, graphNodes: nodes, graphEdges: edges });
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

  reset: () => set({ currentScene: null, selectedChoice: null, graphNodes: [], graphEdges: [] }),
}));
