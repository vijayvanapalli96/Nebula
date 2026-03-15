import React from 'react';
import { useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import DashboardLayout from '../components/layout/DashboardLayout';

const LABELS: Record<string, string> = {
  '/dashboard/stories':      'My Stories',
  '/dashboard/explore':      'Explore',
  '/dashboard/favorites':    'Favorites',
  '/dashboard/achievements': 'Achievements',
  '/dashboard/settings':     'Settings',
};

const ICONS: Record<string, string> = {
  '/dashboard/stories':      '📖',
  '/dashboard/explore':      '🧭',
  '/dashboard/favorites':    '❤️',
  '/dashboard/achievements': '🏆',
  '/dashboard/settings':     '⚙️',
};

const ComingSoonPage: React.FC = () => {
  const { pathname } = useLocation();
  const label = LABELS[pathname] ?? 'This page';
  const icon  = ICONS[pathname]  ?? '✨';

  return (
    <DashboardLayout title={label}>
      <div className="flex flex-col items-center justify-center h-full min-h-[60vh] text-center px-6 gap-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.85 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, type: 'spring', stiffness: 200 }}
          className="text-6xl"
        >
          {icon}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="space-y-3"
        >
          <h2
            className="text-2xl font-black"
            style={{ color: 'var(--text-primary)' }}
          >
            {label}
          </h2>
          <p
            className="text-sm max-w-xs mx-auto leading-relaxed"
            style={{ color: 'var(--text-secondary)' }}
          >
            This section is currently under construction. Check back soon — it's
            going to be great.
          </p>

          <div
            className="inline-block mt-2 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest border"
            style={{
              color: '#8b5cf6',
              borderColor: 'rgba(139,92,246,0.3)',
              backgroundColor: 'rgba(139,92,246,0.08)',
            }}
          >
            Coming Soon
          </div>
        </motion.div>
      </div>
    </DashboardLayout>
  );
};

export default ComingSoonPage;
