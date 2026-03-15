import React from 'react';
import { Bell, Search } from 'lucide-react';

interface TopBarProps {
  title: string;
}

const TopBar: React.FC<TopBarProps> = ({ title }) => {
  return (
    <header
      className="flex items-center h-16 px-6 gap-4 flex-shrink-0"
      style={{
        backgroundColor: 'var(--bg-surface)',
        borderBottom: '1px solid var(--border-color)',
      }}
    >
      {/* Page title */}
      <h1
        className="text-sm font-bold flex-shrink-0 tracking-tight"
        style={{ color: 'var(--text-primary)' }}
      >
        {title}
      </h1>

      {/* Search */}
      <div
        className="flex items-center gap-2 px-3 py-2 rounded-xl flex-1 max-w-xs mx-4"
        style={{
          backgroundColor: 'var(--input-bg)',
          border: '1px solid var(--border-color)',
        }}
      >
        <Search size={14} style={{ color: 'var(--text-muted)' }} />
        <input
          type="search"
          placeholder="Search stories, genres…"
          aria-label="Search"
          className="bg-transparent text-sm outline-none w-full placeholder-shown:text-muted"
          style={{ color: 'var(--text-primary)' }}
        />
      </div>

      {/* Right cluster */}
      <div className="flex items-center gap-3 ml-auto">
        {/* Notifications */}
        <button
          aria-label="Notifications"
          className="relative w-9 h-9 rounded-xl flex items-center justify-center transition-colors"
          style={{ color: 'var(--text-secondary)' }}
          onMouseEnter={(e) =>
            (e.currentTarget.style.backgroundColor = 'var(--sidebar-hover)')
          }
          onMouseLeave={(e) =>
            (e.currentTarget.style.backgroundColor = 'transparent')
          }
        >
          <Bell size={18} />
          {/* Unread badge */}
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-violet-500" />
        </button>

        {/* User avatar */}
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-blue-500 flex items-center justify-center cursor-pointer">
          <span className="text-xs font-bold text-white select-none">T</span>
        </div>
      </div>
    </header>
  );
};

export default TopBar;
