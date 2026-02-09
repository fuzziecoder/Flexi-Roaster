import { create } from 'zustand';

// Helper to get initial theme from localStorage
function getInitialTheme(): 'dark' | 'light' {
    try {
        const saved = localStorage.getItem('flexi-theme');
        if (saved === 'light' || saved === 'dark') return saved;
    } catch {}
    return 'dark';
}

// Apply theme class to document
function applyThemeToDocument(theme: 'dark' | 'light') {
    const root = document.documentElement;
    if (theme === 'light') {
        root.classList.add('light');
        root.classList.remove('dark');
    } else {
        root.classList.add('dark');
        root.classList.remove('light');
    }
    try {
        localStorage.setItem('flexi-theme', theme);
    } catch {}
}

interface UIState {
    sidebarCollapsed: boolean;
    theme: 'dark' | 'light';
    searchQuery: string;
    activeModal: string | null;

    // Actions
    toggleSidebar: () => void;
    setSidebarCollapsed: (collapsed: boolean) => void;
    setTheme: (theme: 'dark' | 'light') => void;
    toggleTheme: () => void;
    setSearchQuery: (query: string) => void;
    openModal: (modal: string) => void;
    closeModal: () => void;
}

// Apply initial theme immediately
const initialTheme = getInitialTheme();
applyThemeToDocument(initialTheme);

export const useUIStore = create<UIState>((set, get) => ({
    sidebarCollapsed: false,
    theme: initialTheme,
    searchQuery: '',
    activeModal: null,

    toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

    setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),

    setTheme: (theme) => {
        applyThemeToDocument(theme);
        set({ theme });
    },

    toggleTheme: () => {
        const newTheme = get().theme === 'dark' ? 'light' : 'dark';
        applyThemeToDocument(newTheme);
        set({ theme: newTheme });
    },

    setSearchQuery: (searchQuery) => set({ searchQuery }),

    openModal: (activeModal) => set({ activeModal }),

    closeModal: () => set({ activeModal: null }),
}));
