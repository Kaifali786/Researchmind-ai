import React from 'react';
import { Outlet } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Sidebar } from '@/components/layout/sidebar';
import { Header } from '@/components/layout/header';
import { useSidebarStore } from '@/store/sidebar-store';

const AppLayout: React.FC = () => {
  const { isCollapsed } = useSidebarStore();

  return (
    <div className="flex min-h-screen bg-[hsl(var(--background))]">
      <Sidebar />

      <motion.div
        className="flex flex-1 flex-col"
        animate={{ marginLeft: isCollapsed ? 72 : 260 }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      >
        <Header />

        <main className="flex-1 overflow-y-auto">
          <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
            <Outlet />
          </div>
        </main>
      </motion.div>
    </div>
  );
};

export { AppLayout };
