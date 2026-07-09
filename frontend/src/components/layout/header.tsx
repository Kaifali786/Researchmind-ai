import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Sun, Moon, Bell, ChevronDown, LogOut, User, Settings } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useThemeStore } from '@/store/theme-store';
import { useAuthStore } from '@/store/auth-store';
import { Avatar } from '@/components/ui/avatar';
import { cn } from '@/lib/utils';

const Header: React.FC = () => {
  const { theme, toggleTheme } = useThemeStore();
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const [showDropdown, setShowDropdown] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  const notifications = [
    { id: '1', text: 'Document "Quantum ML" processed successfully', time: '2m ago', unread: true },
    { id: '2', text: 'New citation format available: IEEE', time: '1h ago', unread: true },
    { id: '3', text: 'Knowledge graph updated with 12 new connections', time: '3h ago', unread: false },
  ];

  const unreadCount = notifications.filter((n) => n.unread).length;

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-[hsl(var(--border))] bg-[hsl(var(--background))]/80 backdrop-blur-xl px-6">
      {/* Search */}
      <div className="relative max-w-md flex-1">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[hsl(var(--muted-foreground))]" />
        <input
          type="text"
          placeholder="Search papers, notes, conversations..."
          className={cn(
            'h-10 w-full rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--muted))]/50 pl-10 pr-4 text-sm text-[hsl(var(--foreground))]',
            'placeholder:text-[hsl(var(--muted-foreground))]',
            'focus:border-[hsl(var(--primary))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]/20',
            'transition-all duration-200'
          )}
        />
        <kbd className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 hidden rounded-md border border-[hsl(var(--border))] bg-[hsl(var(--muted))] px-1.5 py-0.5 text-[10px] font-mono text-[hsl(var(--muted-foreground))] sm:inline-block">
          ⌘K
        </kbd>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-2">
        {/* Theme Toggle */}
        <motion.button
          onClick={toggleTheme}
          className="relative flex h-9 w-9 items-center justify-center rounded-xl text-[hsl(var(--muted-foreground))] transition-colors hover:bg-[hsl(var(--accent))] hover:text-[hsl(var(--foreground))] cursor-pointer"
          whileTap={{ scale: 0.9 }}
        >
          <AnimatePresence mode="wait">
            {theme === 'dark' ? (
              <motion.div
                key="sun"
                initial={{ rotate: -90, scale: 0 }}
                animate={{ rotate: 0, scale: 1 }}
                exit={{ rotate: 90, scale: 0 }}
                transition={{ duration: 0.2 }}
              >
                <Sun className="h-[18px] w-[18px]" />
              </motion.div>
            ) : (
              <motion.div
                key="moon"
                initial={{ rotate: 90, scale: 0 }}
                animate={{ rotate: 0, scale: 1 }}
                exit={{ rotate: -90, scale: 0 }}
                transition={{ duration: 0.2 }}
              >
                <Moon className="h-[18px] w-[18px]" />
              </motion.div>
            )}
          </AnimatePresence>
        </motion.button>

        {/* Notifications */}
        <div className="relative">
          <motion.button
            onClick={() => { setShowNotifications(!showNotifications); setShowDropdown(false); }}
            className="relative flex h-9 w-9 items-center justify-center rounded-xl text-[hsl(var(--muted-foreground))] transition-colors hover:bg-[hsl(var(--accent))] hover:text-[hsl(var(--foreground))] cursor-pointer"
            whileTap={{ scale: 0.9 }}
          >
            <Bell className="h-[18px] w-[18px]" />
            {unreadCount > 0 && (
              <motion.span
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="absolute right-1 top-1 flex h-4 w-4 items-center justify-center rounded-full bg-[hsl(var(--primary))] text-[9px] font-bold text-white"
              >
                {unreadCount}
              </motion.span>
            )}
          </motion.button>

          <AnimatePresence>
            {showNotifications && (
              <motion.div
                initial={{ opacity: 0, y: 8, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 8, scale: 0.95 }}
                transition={{ duration: 0.15 }}
                className="absolute right-0 top-full mt-2 w-80 rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-1 shadow-xl"
              >
                <div className="px-3 py-2">
                  <h4 className="text-sm font-semibold text-[hsl(var(--foreground))]">Notifications</h4>
                </div>
                <div className="space-y-0.5">
                  {notifications.map((notif) => (
                    <button
                      key={notif.id}
                      className={cn(
                        'w-full rounded-lg px-3 py-2.5 text-left transition-colors hover:bg-[hsl(var(--accent))] cursor-pointer',
                        notif.unread && 'bg-[hsl(var(--primary))]/5'
                      )}
                    >
                      <div className="flex items-start gap-2">
                        {notif.unread && <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-[hsl(var(--primary))]" />}
                        <div className={cn(!notif.unread && 'ml-4')}>
                          <p className="text-sm text-[hsl(var(--foreground))]">{notif.text}</p>
                          <p className="mt-0.5 text-xs text-[hsl(var(--muted-foreground))]">{notif.time}</p>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Separator */}
        <div className="mx-1 h-6 w-px bg-[hsl(var(--border))]" />

        {/* User Menu */}
        <div className="relative">
          <motion.button
            onClick={() => { setShowDropdown(!showDropdown); setShowNotifications(false); }}
            className="flex items-center gap-2 rounded-xl px-2 py-1.5 transition-colors hover:bg-[hsl(var(--accent))] cursor-pointer"
            whileTap={{ scale: 0.97 }}
          >
            <Avatar name={user?.full_name || 'User'} src={user?.avatar_url} size="sm" />
            <span className="hidden text-sm font-medium text-[hsl(var(--foreground))] sm:inline-block">
              {user?.full_name?.split(' ')[0] || 'User'}
            </span>
            <ChevronDown className={cn(
              'h-3.5 w-3.5 text-[hsl(var(--muted-foreground))] transition-transform duration-200',
              showDropdown && 'rotate-180'
            )} />
          </motion.button>

          <AnimatePresence>
            {showDropdown && (
              <motion.div
                initial={{ opacity: 0, y: 8, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 8, scale: 0.95 }}
                transition={{ duration: 0.15 }}
                className="absolute right-0 top-full mt-2 w-56 rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-1 shadow-xl"
              >
                <div className="border-b border-[hsl(var(--border))] px-3 py-2.5 mb-1">
                  <p className="text-sm font-medium text-[hsl(var(--foreground))]">{user?.full_name}</p>
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">{user?.email}</p>
                </div>

                <button
                  onClick={() => { navigate('/settings'); setShowDropdown(false); }}
                  className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-[hsl(var(--foreground))] transition-colors hover:bg-[hsl(var(--accent))] cursor-pointer"
                >
                  <User className="h-4 w-4 text-[hsl(var(--muted-foreground))]" />
                  Profile
                </button>
                <button
                  onClick={() => { navigate('/settings'); setShowDropdown(false); }}
                  className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-[hsl(var(--foreground))] transition-colors hover:bg-[hsl(var(--accent))] cursor-pointer"
                >
                  <Settings className="h-4 w-4 text-[hsl(var(--muted-foreground))]" />
                  Settings
                </button>

                <div className="my-1 h-px bg-[hsl(var(--border))]" />

                <button
                  onClick={() => { logout(); setShowDropdown(false); }}
                  className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-[hsl(var(--destructive))] transition-colors hover:bg-[hsl(var(--destructive))]/10 cursor-pointer"
                >
                  <LogOut className="h-4 w-4" />
                  Sign Out
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Click outside handler overlay */}
      {(showDropdown || showNotifications) && (
        <div
          className="fixed inset-0 z-[-1]"
          onClick={() => { setShowDropdown(false); setShowNotifications(false); }}
        />
      )}
    </header>
  );
};

export { Header };
