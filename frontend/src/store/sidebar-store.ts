import { create } from 'zustand';

interface SidebarState {
  isOpen: boolean;
  isCollapsed: boolean;
  toggle: () => void;
  open: () => void;
  close: () => void;
  toggleCollapse: () => void;
}

export const useSidebarStore = create<SidebarState>((set) => ({
  isOpen: true,
  isCollapsed: localStorage.getItem('sidebar-collapsed') === 'true',

  toggle: () => set((state) => ({ isOpen: !state.isOpen })),
  open: () => set({ isOpen: true }),
  close: () => set({ isOpen: false }),

  toggleCollapse: () =>
    set((state) => {
      const newCollapsed = !state.isCollapsed;
      localStorage.setItem('sidebar-collapsed', String(newCollapsed));
      return { isCollapsed: newCollapsed };
    }),
}));
