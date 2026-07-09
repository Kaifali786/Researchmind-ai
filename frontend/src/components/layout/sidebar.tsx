import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  FileText,
  MessageSquare,
  GitCompareArrows,
  Quote,
  Share2,
  BookOpen,
  BarChart3,
  Settings,
  ChevronLeft,
  LogOut,
  Sparkles,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useSidebarStore } from '@/store/sidebar-store';
import { useAuthStore } from '@/store/auth-store';
import { Avatar } from '@/components/ui/avatar';
import { Tooltip } from '@/components/ui/tooltip';

interface NavItemConfig {
  label: string;
  href: string;
  icon: React.ElementType;
  badge?: number;
}

const navItems: NavItemConfig[] = [
  { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { label: 'Documents', href: '/documents', icon: FileText },
  { label: 'Chat', href: '/chat', icon: MessageSquare, badge: 3 },
  { label: 'Compare', href: '/compare', icon: GitCompareArrows },
  { label: 'Citations', href: '/citations', icon: Quote },
  { label: 'Knowledge Graph', href: '/knowledge-graph', icon: Share2 },
  { label: 'Notebook', href: '/notebook', icon: BookOpen },
  { label: 'Analytics', href: '/analytics', icon: BarChart3 },
];

const Sidebar: React.FC = () => {
  const { isCollapsed, toggleCollapse } = useSidebarStore();
  const { user, logout } = useAuthStore();
  const location = useLocation();

  return (
    <motion.aside
      className={cn(
        'fixed left-0 top-0 z-40 flex h-screen flex-col border-r border-[hsl(var(--sidebar-border))] bg-[hsl(var(--sidebar-bg))]',
        'dark:bg-[hsl(var(--sidebar-bg))]/80 dark:backdrop-blur-xl dark:backdrop-saturate-150'
      )}
      animate={{ width: isCollapsed ? 72 : 260 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
    >
      {/* Brand Header */}
      <div className="flex h-16 items-center justify-between border-b border-[hsl(var(--sidebar-border))] px-4">
        <NavLink to="/dashboard" className="flex items-center gap-3 overflow-hidden">
          <motion.div
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-blue-600 shadow-lg shadow-indigo-500/25"
            whileHover={{ scale: 1.05, rotate: 5 }}
            whileTap={{ scale: 0.95 }}
          >
            <Sparkles className="h-5 w-5 text-white" />
          </motion.div>
          <AnimatePresence>
            {!isCollapsed && (
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                transition={{ duration: 0.2 }}
                className="flex flex-col"
              >
                <span className="text-sm font-bold tracking-tight gradient-text">
                  ResearchMind
                </span>
                <span className="text-[10px] font-medium text-[hsl(var(--muted-foreground))]">
                  AI Research Assistant
                </span>
              </motion.div>
            )}
          </AnimatePresence>
        </NavLink>

        <AnimatePresence>
          {!isCollapsed && (
            <motion.button
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={toggleCollapse}
              className="flex h-7 w-7 items-center justify-center rounded-lg text-[hsl(var(--muted-foreground))] transition-colors hover:bg-[hsl(var(--accent))] hover:text-[hsl(var(--foreground))] cursor-pointer"
            >
              <ChevronLeft className="h-4 w-4" />
            </motion.button>
          )}
        </AnimatePresence>
      </div>

      {/* Expand button when collapsed */}
      {isCollapsed && (
        <div className="flex justify-center py-2">
          <motion.button
            onClick={toggleCollapse}
            className="flex h-7 w-7 items-center justify-center rounded-lg text-[hsl(var(--muted-foreground))] transition-colors hover:bg-[hsl(var(--accent))] hover:text-[hsl(var(--foreground))] cursor-pointer"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            <ChevronLeft className="h-4 w-4 rotate-180" />
          </motion.button>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto overflow-x-hidden px-3 py-4">
        <div className="space-y-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.href || location.pathname.startsWith(item.href + '/');
            const Icon = item.icon;

            const linkContent = (
              <NavLink
                key={item.href}
                to={item.href}
                className={cn(
                  'group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200',
                  isActive
                    ? 'text-[hsl(var(--primary))]'
                    : 'text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] hover:bg-[hsl(var(--accent))]',
                  isCollapsed && 'justify-center px-2'
                )}
              >
                {/* Active indicator */}
                {isActive && (
                  <motion.div
                    layoutId="sidebar-active-indicator"
                    className="absolute inset-0 rounded-xl bg-[hsl(var(--primary))]/10 dark:bg-[hsl(var(--primary))]/15 border border-[hsl(var(--primary))]/20"
                    transition={{ type: 'spring', stiffness: 350, damping: 30 }}
                  />
                )}

                {/* Active left accent bar */}
                {isActive && (
                  <motion.div
                    layoutId="sidebar-active-bar"
                    className="absolute left-0 top-1/2 -translate-y-1/2 h-6 w-[3px] rounded-full bg-[hsl(var(--primary))]"
                    transition={{ type: 'spring', stiffness: 350, damping: 30 }}
                  />
                )}

                <Icon className={cn(
                  'h-[18px] w-[18px] shrink-0 relative z-10 transition-transform duration-200',
                  isActive && 'text-[hsl(var(--primary))]',
                  !isActive && 'group-hover:scale-110'
                )} />

                <AnimatePresence>
                  {!isCollapsed && (
                    <motion.span
                      initial={{ opacity: 0, x: -8 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -8 }}
                      transition={{ duration: 0.15 }}
                      className="relative z-10 truncate"
                    >
                      {item.label}
                    </motion.span>
                  )}
                </AnimatePresence>

                {/* Badge */}
                {item.badge && !isCollapsed && (
                  <motion.span
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="relative z-10 ml-auto flex h-5 min-w-5 items-center justify-center rounded-full bg-[hsl(var(--primary))] px-1.5 text-[10px] font-bold text-white"
                  >
                    {item.badge}
                  </motion.span>
                )}
                {item.badge && isCollapsed && (
                  <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-[hsl(var(--primary))]" />
                )}
              </NavLink>
            );

            if (isCollapsed) {
              return (
                <Tooltip key={item.href} content={item.label} side="right">
                  {linkContent}
                </Tooltip>
              );
            }
            return <React.Fragment key={item.href}>{linkContent}</React.Fragment>;
          })}
        </div>
      </nav>

      {/* Settings link */}
      <div className="border-t border-[hsl(var(--sidebar-border))] px-3 py-2">
        {(() => {
          const isSettingsActive = location.pathname === '/settings';
          const settingsLink = (
            <NavLink
              to="/settings"
              className={cn(
                'group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200',
                isSettingsActive
                  ? 'text-[hsl(var(--primary))] bg-[hsl(var(--primary))]/10'
                  : 'text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] hover:bg-[hsl(var(--accent))]',
                isCollapsed && 'justify-center px-2'
              )}
            >
              <Settings className={cn('h-[18px] w-[18px] shrink-0 transition-transform duration-500', !isSettingsActive && 'group-hover:rotate-90')} />
              <AnimatePresence>
                {!isCollapsed && (
                  <motion.span
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -8 }}
                    transition={{ duration: 0.15 }}
                  >
                    Settings
                  </motion.span>
                )}
              </AnimatePresence>
            </NavLink>
          );

          return isCollapsed ? (
            <Tooltip content="Settings" side="right">
              {settingsLink}
            </Tooltip>
          ) : settingsLink;
        })()}
      </div>

      {/* User Profile Section */}
      <div className="border-t border-[hsl(var(--sidebar-border))] p-3">
        <div
          className={cn(
            'flex items-center gap-3 rounded-xl p-2 transition-colors hover:bg-[hsl(var(--accent))]',
            isCollapsed && 'justify-center'
          )}
        >
          <Avatar
            name={user?.full_name || 'User'}
            src={user?.avatar_url}
            size="sm"
          />
          <AnimatePresence>
            {!isCollapsed && (
              <motion.div
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -8 }}
                transition={{ duration: 0.15 }}
                className="flex-1 overflow-hidden"
              >
                <p className="truncate text-sm font-medium text-[hsl(var(--foreground))]">
                  {user?.full_name || 'User'}
                </p>
                <p className="truncate text-xs text-[hsl(var(--muted-foreground))]">
                  {user?.email || 'user@example.com'}
                </p>
              </motion.div>
            )}
          </AnimatePresence>
          <AnimatePresence>
            {!isCollapsed && (
              <motion.button
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={logout}
                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-[hsl(var(--muted-foreground))] transition-colors hover:bg-[hsl(var(--destructive))]/10 hover:text-[hsl(var(--destructive))] cursor-pointer"
                title="Logout"
              >
                <LogOut className="h-4 w-4" />
              </motion.button>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.aside>
  );
};

export { Sidebar };
