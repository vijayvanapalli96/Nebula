import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  BookOpen,
  Compass,
  Heart,
  Trophy,
  Settings,
  Sun,
  Moon,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  LogOut,
} from 'lucide-react';
import { useThemeStore } from '../../store/themeStore';

// --- Nav items config ------------------------------------------------------

interface NavItem {
  id: string;
  label: string;
  icon: React.ElementType;
  href: string;
  end?: boolean;
}

const MAIN_NAV: NavItem[] = [
  { id: 'dashboard',    label: 'Dashboard',    icon: LayoutDashboard, href: '/dashboard',              end: true },
  { id: 'stories',      label: 'My Stories',   icon: BookOpen,        href: '/dashboard/stories'                },
  { id: 'explore',      label: 'Explore',      icon: Compass,         href: '/dashboard/explore'                },
  { id: 'favorites',    label: 'Favorites',    icon: Heart,           href: '/dashboard/favorites'              },
  { id: 'achievements', label: 'Achievements', icon: Trophy,          href: '/dashboard/achievements'           },
];

const ACCOUNT_NAV: NavItem[] = [
  { id: 'settings', label: 'Settings', icon: Settings, href: '/dashboard/settings' },
];

// --- Tooltip wrapper -------------------------------------------------------

const Tooltip: React.FC<{ label: string; show: boolean }> = ({ label, show }) =>
  show ? (
    <div
      className="absolute left-full top-1/2 -translate-y-1/2 ml-3 px-2.5 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap z-50 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-150"
      style={{
        backgroundColor: 'var(--bg-elevated)',
        color: 'var(--text-primary)',
        border: '1px solid var(--border-color)',
        boxShadow: '0 4px 16px rgba(0,0,0,0.3)',
      }}
    >
      {label}
    </div>
  ) : null;

// --- NavItem Row -----------------------------------------------------------

interface NavRowProps {
  item: NavItem;
  isOpen: boolean;
  pathname: string;
}

const NavRow: React.FC<NavRowProps> = ({ item, isOpen, pathname }) => {
  const isActive = item.end
    ? pathname === item.href
    : pathname.startsWith(item.href);

  return (
    <div className="relative group">
      <NavLink
        to={item.href}
        end={item.end}
        className={`sidebar-nav-item ${isActive ? 'active' : ''}`}
        aria-current={isActive ? 'page' : undefined}
      >
        {isActive && (
          <motion.span
            layoutId="nav-active-pill"
            className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 rounded-r-full bg-violet-500"
          />
        )}

        <item.icon size={18} className="flex-shrink-0" />

        <AnimatePresence>
          {isOpen && (
            <motion.span
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }}
              className="text-sm font-medium whitespace-nowrap"
            >
              {item.label}
            </motion.span>
          )}
        </AnimatePresence>
      </NavLink>

      <Tooltip label={item.label} show={!isOpen} />
    </div>
  );
};

// --- Shared sidebar inner content -----------------------------------------

interface SidebarContentProps {
  isOpen: boolean;
  isMobile: boolean;
  onToggle: () => void;
  onClose: () => void;
  isDark: boolean;
  toggleTheme: () => void;
  pathname: string;
}

const SidebarContent: React.FC<SidebarContentProps> = ({
  isOpen, isMobile, onToggle, onClose, isDark, toggleTheme, pathname,
}) => {
  const labelVisible = isOpen || isMobile;

  return (
    <>
      {/* Logo + toggle */}
      <div
        className="flex items-center h-16 px-4 gap-3 flex-shrink-0"
        style={{ borderBottom: '1px solid var(--border-color)' }}
      >
        <div className="w-8 h-8 rounded-xl bg-violet-600 flex items-center justify-center flex-shrink-0 glow-purple">
          <Sparkles size={15} className="text-white" />
        </div>

        <AnimatePresence>
          {labelVisible && (
            <motion.span
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              transition={{ duration: 0.18 }}
              className="flex-1 text-base font-black tracking-tight"
              style={{ color: 'var(--text-primary)' }}
            >
              NEBULA
            </motion.span>
          )}
        </AnimatePresence>

        <button
          onClick={isMobile ? onClose : onToggle}
          aria-label={isMobile ? 'Close menu' : isOpen ? 'Collapse sidebar' : 'Expand sidebar'}
          className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 transition-colors ml-auto"
          style={{ color: 'var(--text-muted)' }}
          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--sidebar-hover)')}
          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
        >
          {isMobile || isOpen ? <ChevronLeft size={14} /> : <ChevronRight size={14} />}
        </button>
      </div>

      {/* Main nav */}
      <nav role="navigation" className="flex-1 overflow-y-auto py-3 px-2 space-y-0.5 scrollbar-hide">
        {labelVisible && (
          <p className="text-[9px] font-bold uppercase tracking-widest px-3 pt-1 pb-2" style={{ color: 'var(--text-muted)' }}>
            Main
          </p>
        )}

        {MAIN_NAV.map((item) => (
          <NavRow key={item.id} item={item} isOpen={labelVisible} pathname={pathname} />
        ))}

        <div className="py-2 px-1">
          <div className="h-px" style={{ backgroundColor: 'var(--border-color)' }} />
        </div>

        {labelVisible && (
          <p className="text-[9px] font-bold uppercase tracking-widest px-3 pb-2" style={{ color: 'var(--text-muted)' }}>
            Account
          </p>
        )}

        {ACCOUNT_NAV.map((item) => (
          <NavRow key={item.id} item={item} isOpen={labelVisible} pathname={pathname} />
        ))}
      </nav>

      {/* Bottom: theme + user */}
      <div className="flex-shrink-0 px-2 py-3 space-y-1" style={{ borderTop: '1px solid var(--border-color)' }}>
        <div className="relative group">
          <button
            onClick={toggleTheme}
            aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
            className={`sidebar-nav-item w-full ${!labelVisible ? 'justify-center' : ''}`}
          >
            <motion.span
              key={isDark ? 'sun' : 'moon'}
              initial={{ rotate: 90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              transition={{ duration: 0.25 }}
              className="flex-shrink-0 flex items-center justify-center"
            >
              {isDark ? <Sun size={18} /> : <Moon size={18} />}
            </motion.span>
            <AnimatePresence>
              {labelVisible && (
                <motion.span
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.15 }}
                  className="text-sm font-medium whitespace-nowrap"
                >
                  {isDark ? 'Light Mode' : 'Dark Mode'}
                </motion.span>
              )}
            </AnimatePresence>
          </button>
          <Tooltip label={isDark ? 'Light Mode' : 'Dark Mode'} show={!labelVisible} />
        </div>

        <div
          className={`flex items-center rounded-xl transition-colors cursor-pointer ${
            labelVisible ? 'gap-3 px-3 py-2.5' : 'justify-center py-2.5'
          }`}
          style={{ color: 'var(--text-secondary)' }}
          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--sidebar-hover)')}
          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
        >
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-blue-500 flex items-center justify-center flex-shrink-0">
            <span className="text-xs font-bold text-white">T</span>
          </div>
          <AnimatePresence>
            {labelVisible && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.15 }}
                className="flex-1 min-w-0"
              >
                <p className="text-xs font-semibold leading-tight truncate" style={{ color: 'var(--text-primary)' }}>
                  Tarang
                </p>
                <p className="text-[10px] truncate" style={{ color: 'var(--text-muted)' }}>
                  tarang@nebula.ai
                </p>
              </motion.div>
            )}
          </AnimatePresence>
          {labelVisible && (
            <LogOut size={14} className="flex-shrink-0" style={{ color: 'var(--text-muted)' }} />
          )}
        </div>
      </div>
    </>
  );
};

// --- Sidebar --------------------------------------------------------------

const Sidebar: React.FC = () => {
  const [isOpen, setIsOpen] = useState(true);
  const [mobileOpen, setMobileOpen] = useState(false);
  const { isDark, toggleTheme } = useThemeStore();
  const { pathname } = useLocation();

  // Close drawer on route change
  useEffect(() => { setMobileOpen(false); }, [pathname]);

  // Close drawer on Escape
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') setMobileOpen(false); };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, []);

  const sharedProps = { isDark, toggleTheme, pathname };

  return (
    <>
      {/* -- Desktop sidebar (md+) -- */}
      <motion.aside
        animate={{ width: isOpen ? 240 : 72 }}
        transition={{ duration: 0.28, ease: [0.4, 0, 0.2, 1] }}
        className="relative hidden md:flex flex-col h-full flex-shrink-0 z-20"
        style={{
          backgroundColor: 'var(--sidebar-bg)',
          borderRight: '1px solid var(--border-color)',
          overflow: 'hidden',
        }}
        aria-label="Dashboard navigation"
      >
        <SidebarContent
          {...sharedProps}
          isOpen={isOpen}
          isMobile={false}
          onToggle={() => setIsOpen((o) => !o)}
          onClose={() => setMobileOpen(false)}
        />
      </motion.aside>

      {/* -- Mobile: hamburger button (< md) -- */}
      <button
        onClick={() => setMobileOpen(true)}
        aria-label="Open menu"
        className="md:hidden fixed top-4 left-4 z-30 w-10 h-10 flex items-center justify-center rounded-xl shadow-lg"
        style={{
          backgroundColor: 'var(--sidebar-bg)',
          border: '1px solid var(--border-color)',
          color: 'var(--text-primary)',
        }}
      >
        <svg width="18" height="14" viewBox="0 0 18 14" fill="none">
          <path d="M1 1h16M1 7h16M1 13h16" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
        </svg>
      </button>

      {/* -- Mobile: backdrop -- */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            key="mob-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="md:hidden fixed inset-0 z-40 bg-black/60 backdrop-blur-sm"
            onClick={() => setMobileOpen(false)}
            aria-hidden="true"
          />
        )}
      </AnimatePresence>

      {/* -- Mobile: slide-in drawer -- */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.aside
            key="mob-drawer"
            initial={{ x: -280 }}
            animate={{ x: 0 }}
            exit={{ x: -280 }}
            transition={{ duration: 0.28, ease: [0.4, 0, 0.2, 1] }}
            className="md:hidden fixed top-0 left-0 h-full z-50 flex flex-col w-64"
            style={{
              backgroundColor: 'var(--sidebar-bg)',
              borderRight: '1px solid var(--border-color)',
            }}
            aria-label="Dashboard navigation"
          >
            <SidebarContent
              {...sharedProps}
              isOpen={true}
              isMobile={true}
              onToggle={() => setIsOpen((o) => !o)}
              onClose={() => setMobileOpen(false)}
            />
          </motion.aside>
        )}
      </AnimatePresence>
    </>
  );
};

export default Sidebar;
