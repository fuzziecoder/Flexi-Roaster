import { create } from 'zustand';
import type { Alert, Notification } from '@/types/common';
import { mockAlerts, mockNotifications } from '@/lib/mockData';

interface AlertState {
    alerts: Alert[];
    notifications: Notification[];
    unreadCount: number;

    // Actions
    setAlerts: (alerts: Alert[]) => void;
    acknowledgeAlert: (id: string) => void;
    resolveAlert: (id: string) => void;
    addNotification: (notification: Notification) => void;
    markNotificationRead: (id: string) => void;
    markAllRead: () => void;
    clearNotifications: () => void;
}

export const useAlertStore = create<AlertState>((set) => ({
    alerts: mockAlerts,
    notifications: mockNotifications,
    unreadCount: mockNotifications.filter((n) => !n.read).length,

    setAlerts: (alerts) => set({ alerts }),

    acknowledgeAlert: (id) =>
        set((state) => ({
            alerts: state.alerts.map((a) =>
                a.id === id ? { ...a, acknowledged: true } : a
            ),
        })),

    resolveAlert: (id) =>
        set((state) => ({
            alerts: state.alerts.map((a) =>
                a.id === id ? { ...a, resolvedAt: new Date().toISOString() } : a
            ),
        })),

    addNotification: (notification) =>
        set((state) => ({
            notifications: [notification, ...state.notifications],
            unreadCount: state.unreadCount + (notification.read ? 0 : 1),
        })),

    markNotificationRead: (id) =>
        set((state) => {
            const notif = state.notifications.find((n) => n.id === id);
            const wasUnread = notif && !notif.read;
            return {
                notifications: state.notifications.map((n) =>
                    n.id === id ? { ...n, read: true } : n
                ),
                unreadCount: wasUnread ? state.unreadCount - 1 : state.unreadCount,
            };
        }),

    markAllRead: () =>
        set((state) => ({
            notifications: state.notifications.map((n) => ({ ...n, read: true })),
            unreadCount: 0,
        })),

    clearNotifications: () => set({ notifications: [], unreadCount: 0 }),
}));
