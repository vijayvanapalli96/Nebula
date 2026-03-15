import React from 'react';
import Sidebar from './Sidebar';

interface DashboardLayoutProps {
  children: React.ReactNode;
  title?: string;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  return (
    <div
      className="flex h-screen overflow-hidden"
      style={{ backgroundColor: 'var(--bg-base)', color: 'var(--text-primary)' }}
    >
      <Sidebar />

      {/* Main content column */}
      <main
        className="flex-1 min-w-0 overflow-y-auto pt-16 md:pt-0"
        style={{ backgroundColor: 'var(--bg-base)' }}
      >
        {children}
      </main>
    </div>
  );
};

export default DashboardLayout;
