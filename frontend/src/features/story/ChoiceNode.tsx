import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import { motion } from 'framer-motion';
import { useStorySessionStore } from '../../store/storySessionStore';
import type { ChoiceNodeData } from '../../store/storySessionStore';

interface ChoiceNodeProps {
  data: ChoiceNodeData;
}

const ChoiceNode: React.FC<ChoiceNodeProps> = ({ data }) => {
  const selectChoice = useStorySessionStore((s) => s.selectChoice);
  const selected = data.selected;

  return (
    <motion.div
      onClick={() => selectChoice(data.choiceId)}
      className="cursor-pointer rounded-2xl px-4 py-3 select-none"
      style={{
        width: 200,
        backgroundColor: selected
          ? 'rgba(139,92,246,0.22)'
          : 'rgba(255,255,255,0.04)',
        border: selected
          ? '1.5px solid rgba(139,92,246,0.7)'
          : '1.5px solid rgba(255,255,255,0.1)',
        boxShadow: selected
          ? '0 0 18px rgba(139,92,246,0.4), inset 0 0 8px rgba(139,92,246,0.12)'
          : '0 2px 12px rgba(0,0,0,0.3)',
        backdropFilter: 'blur(8px)',
        transition: 'all 0.25s ease',
      }}
      whileHover={{ scale: 1.03 }}
      whileTap={{ scale: 0.97 }}
    >
      {/* Incoming edge handle */}
      <Handle
        type="target"
        position={Position.Top}
        style={{ background: 'rgba(139,92,246,0.6)', border: 'none', width: 8, height: 8 }}
      />

      <p
        className="text-xs font-bold leading-snug mb-1"
        style={{ color: selected ? '#c4b5fd' : 'rgba(240,240,255,0.92)' }}
      >
        {data.label}
      </p>

      {data.hint && (
        <p
          className="text-[10px] leading-snug"
          style={{ color: 'rgba(156,163,175,0.75)' }}
        >
          {data.hint}
        </p>
      )}

      {selected && (
        <div
          className="mt-2 flex items-center gap-1 text-[10px] font-semibold"
          style={{ color: '#a78bfa' }}
        >
          <span
            className="inline-block w-1.5 h-1.5 rounded-full bg-violet-400"
            style={{ boxShadow: '0 0 4px #a78bfa' }}
          />
          Selected
        </div>
      )}
    </motion.div>
  );
};

export default memo(ChoiceNode);
