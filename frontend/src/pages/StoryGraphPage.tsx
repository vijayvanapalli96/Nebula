import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ReactFlow,
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  ReactFlowProvider,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { motion } from 'framer-motion';

import { useStorySessionStore } from '../store/storySessionStore';
import SceneNode from '../features/story/SceneNode';
import ChoiceNode from '../features/story/ChoiceNode';

// ── nodeTypes must be defined OUTSIDE the component to avoid re-registration ──
const nodeTypes = {
  sceneNode: SceneNode,
  choiceNode: ChoiceNode,
};

// ── Inner graph (must be inside ReactFlowProvider) ────────────────────────────
const GraphInner: React.FC = () => {
  const { graphNodes, graphEdges, currentScene } = useStorySessionStore();

  const [nodes, setNodes, onNodesChange] = useNodesState(graphNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(graphEdges);

  // Keep local RF state in sync when the Zustand store changes (e.g. selectChoice)
  useEffect(() => { setNodes(graphNodes); }, [graphNodes, setNodes]);
  useEffect(() => { setEdges(graphEdges); }, [graphEdges, setEdges]);

  return (
    // absolute inset-0 gives React Flow explicit pixel dimensions from the
    // positioned flex-1 parent — h-full alone won't work on flex children
    <div style={{ position: 'absolute', inset: 0, backgroundColor: '#0a0a12' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        style={{ width: '100%', height: '100%' }}
        fitView
        fitViewOptions={{ padding: 0.35 }}
        minZoom={0.3}
        maxZoom={2.5}
        proOptions={{ hideAttribution: true }}
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={28}
          size={1}
          color="rgba(139,92,246,0.18)"
        />
        <Controls
          style={{
            background: 'rgba(20,15,35,0.85)',
            border: '1px solid rgba(139,92,246,0.25)',
            borderRadius: 12,
          }}
        />
        <MiniMap
          nodeColor={(n) =>
            n.type === 'sceneNode' ? 'rgba(139,92,246,0.8)' : 'rgba(96,165,250,0.6)'
          }
          maskColor="rgba(10,10,18,0.75)"
          style={{
            background: 'rgba(15,12,25,0.9)',
            border: '1px solid rgba(139,92,246,0.2)',
            borderRadius: 10,
          }}
        />
      </ReactFlow>

      {/* ── Scene title overlay (centred at top) ── */}
      {currentScene && (
        <div
          className="absolute top-4 left-1/2 -translate-x-1/2 pointer-events-none"
          style={{ zIndex: 10 }}
        >
          <motion.div
            className="px-4 py-2 rounded-2xl text-center"
            style={{
              background: 'rgba(15,12,28,0.85)',
              border: '1px solid rgba(139,92,246,0.3)',
              backdropFilter: 'blur(12px)',
            }}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <p className="text-[10px] font-semibold uppercase tracking-widest" style={{ color: '#a78bfa' }}>
              Story Path
            </p>
            <p className="text-sm font-bold mt-0.5" style={{ color: 'rgba(240,240,255,0.9)' }}>
              {currentScene.scene_title}
            </p>
          </motion.div>
        </div>
      )}
    </div>
  );
};

// ── Page wrapper ──────────────────────────────────────────────────────────────
const StoryGraphPage: React.FC = () => {
  const navigate = useNavigate();
  const { currentScene } = useStorySessionStore();

  // Guard: must be in useEffect, never during render
  useEffect(() => {
    if (!currentScene) {
      navigate('/dashboard', { replace: true });
    }
  }, [currentScene, navigate]);

  if (!currentScene) return null;

  return (
    <div className="fixed inset-0 flex flex-col" style={{ backgroundColor: '#0a0a12' }}>
      {/* ── Top bar ── */}
      <motion.div
        className="flex-shrink-0 flex items-center justify-between px-4 py-3"
        style={{
          background: 'rgba(10,10,18,0.9)',
          borderBottom: '1px solid rgba(139,92,246,0.2)',
          backdropFilter: 'blur(12px)',
          zIndex: 20,
        }}
        initial={{ opacity: 0, y: -16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <button
          onClick={() => navigate('/story/scene')}
          className="flex items-center gap-2 text-sm font-medium transition-colors"
          style={{ color: 'rgba(156,163,175,0.8)' }}
          onMouseEnter={(e) => (e.currentTarget.style.color = '#a78bfa')}
          onMouseLeave={(e) => (e.currentTarget.style.color = 'rgba(156,163,175,0.8)')}
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M10 12L6 8l4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Back to Scene
        </button>

        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-violet-500" style={{ boxShadow: '0 0 6px #8b5cf6' }} />
          <span className="text-xs font-semibold" style={{ color: '#a78bfa' }}>Story Graph</span>
        </div>

        <div style={{ width: 96 }} />
      </motion.div>

      {/* ── React Flow canvas ── */}
      <div className="flex-1 relative">
        <ReactFlowProvider>
          <GraphInner />
        </ReactFlowProvider>
      </div>
    </div>
  );
};

export default StoryGraphPage;
