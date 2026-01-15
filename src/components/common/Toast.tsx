/**
 * Toast Notification System
 * Provides accessible toast notifications for app events
 * Styled to match app theme (dark, muted grey tones)
 */
import { create } from 'zustand';
import { useEffect } from 'react';
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react';

// Toast types
export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
    id: string;
    type: ToastType;
    title: string;
    message?: string;
    duration?: number;
}

interface ToastStore {
    toasts: Toast[];
    addToast: (toast: Omit<Toast, 'id'>) => void;
    removeToast: (id: string) => void;
    clearAll: () => void;
}

// Zustand store for toasts
export const useToastStore = create<ToastStore>((set) => ({
    toasts: [],
    addToast: (toast) => {
        const id = `toast_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        set((state) => ({
            toasts: [...state.toasts, { ...toast, id, duration: toast.duration || 4000 }]
        }));
    },
    removeToast: (id) => {
        set((state) => ({
            toasts: state.toasts.filter((t) => t.id !== id)
        }));
    },
    clearAll: () => set({ toasts: [] })
}));

// Helper functions to show toasts
export const toast = {
    success: (title: string, message?: string) => {
        useToastStore.getState().addToast({ type: 'success', title, message });
    },
    error: (title: string, message?: string) => {
        useToastStore.getState().addToast({ type: 'error', title, message, duration: 6000 });
    },
    warning: (title: string, message?: string) => {
        useToastStore.getState().addToast({ type: 'warning', title, message });
    },
    info: (title: string, message?: string) => {
        useToastStore.getState().addToast({ type: 'info', title, message });
    }
};

// Icon mapping - smaller sizes
const iconMap = {
    success: CheckCircle,
    error: XCircle,
    warning: AlertTriangle,
    info: Info
};

// Color mapping - distinct visible colors for each type
const colorMap = {
    success: 'bg-emerald-900/90 border-emerald-700/50 text-white',
    error: 'bg-red-900/90 border-red-700/50 text-white',
    warning: 'bg-amber-900/90 border-amber-700/50 text-white',
    info: 'bg-blue-900/90 border-blue-700/50 text-white'
};

// Icon color mapping - visible icon colors
const iconColorMap = {
    success: 'text-emerald-400',
    error: 'text-red-400',
    warning: 'text-amber-400',
    info: 'text-blue-400'
};

// Individual Toast Component - Compact design
function ToastItem({ toast, onRemove }: { toast: Toast; onRemove: () => void }) {
    const Icon = iconMap[toast.type];

    useEffect(() => {
        const timer = setTimeout(onRemove, toast.duration);
        return () => clearTimeout(timer);
    }, [toast.duration, onRemove]);

    return (
        <div
            className={`
                flex items-center gap-2 px-3 py-2 rounded-lg border shadow-lg
                backdrop-blur-md animate-slide-in text-sm
                ${colorMap[toast.type]}
            `}
            role="alert"
            aria-live="polite"
        >
            <Icon className={`w-4 h-4 flex-shrink-0 ${iconColorMap[toast.type]}`} />
            <div className="flex-1 min-w-0">
                <p className="font-medium text-white/90 text-xs">{toast.title}</p>
                {toast.message && (
                    <p className="text-[10px] mt-0.5 text-white/50 truncate">{toast.message}</p>
                )}
            </div>
            <button
                onClick={onRemove}
                className="p-0.5 hover:bg-white/10 rounded transition-colors flex-shrink-0"
                aria-label="Dismiss notification"
            >
                <X className="w-3 h-3 text-white/40" />
            </button>
        </div>
    );
}

// Toast Container Component - Compact positioning
export function ToastContainer() {
    const { toasts, removeToast } = useToastStore();

    if (toasts.length === 0) return null;

    return (
        <div
            className="fixed bottom-3 right-3 z-[9999] flex flex-col gap-1.5 max-w-xs w-full"
            aria-label="Notifications"
        >
            {toasts.map((t) => (
                <ToastItem
                    key={t.id}
                    toast={t}
                    onRemove={() => removeToast(t.id)}
                />
            ))}
        </div>
    );
}
