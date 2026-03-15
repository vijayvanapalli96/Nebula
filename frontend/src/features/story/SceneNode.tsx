import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import { motion } from 'framer-motion';
import type { SceneNodeData } from '../../store/storySessionStore';

interface SceneNodeProps {
  data: SceneNodeData;
}

const SceneNode: React.FC<SceneNodeProps> = ({ data }) => (
  <motion.div
    className="rounded-2xl px-5 py-4 select-none"
    style={{
      width: 260,
      backgroundColor: 'rgba(139,92,246,0.18)',
      border: '1.5px solid rgba(139,92,246,0.5)',
      boxShadow: '0 0 24px rgba(139,92,246,0.35), inset 0 0 12px rgba(139,92,246,0.08)',
      backdropFilter: 'blur(10px)',
    }}
    initial={{ opacity: 0, scale: 0.85 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ duration: 0.45, ease: 'backOut' }}
  >
    <div
      className="text-[10px] font-bold uppercase tracking-widest mb-2"
      style={{ color: '#a78bfa' }}
    >
      Current Scene
    </div>

    <p
      className="text-sm font-bold leading-snug"
      style={{ color: 'rgba(240,240,255,0.95)' }}
    >
      {data.label}
    </p>

    {data.description && (
      <p
        className="text-[11px] mt-1.5 leading-relaxed line-clamp-3"
        style={{ color: 'rgba(156,163,175,0.8)' }}
      >
        {data.description}
      </p>
    )}

    {/* Outgoing edge handle */}
    <Handle
      type="source"
      position={Position.Bottom}
      style={{ background: 'rgba(139,92,246,0.7)', border: 'none', width: 8, height: 8 }}
    />
  </motion.div>
);

export default memo(SceneNode);
