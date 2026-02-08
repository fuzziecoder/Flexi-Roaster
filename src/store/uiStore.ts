import { create } from 'zustand';

interface UIState {
    sidebarCollapsed: boolean;
    theme: 'dark' | 'light';
    searchQuery: string;
    activeModal: string | null;

    // Actions
    toggleSidebar: () => void;
    setSidebarCollapsed: (collapsed: boolean) => void;
    setTheme: (theme: 'dark' | 'light') => void;
    setSearchQuery: (query: string) => void;
    openModal: (modal: string) => void;
    closeModal: () => void;
}

export const useUIStore = create<UIState>((set) => ({
    sidebarCollapsed: false,
    theme: 'dark',
    searchQuery: '',
    activeModal: null,

    toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

    setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),

    setTheme: (theme) => set({ theme }),

    setSearchQuery: (searchQuery) => set({ searchQuery }),

    openModal: (activeModal) => set({ activeModal }),

    closeModal: () => set({ activeModal: null }),
}));
