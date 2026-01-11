import { useState } from 'react';
import { cn } from '@/lib/utils';
import { useUIStore, useAlertStore } from '@/store';
import { formatRelativeTime } from '@/lib/utils';
import {
    Search,
    Bell,
    User,
    ChevronDown,
    LogOut,
    Settings,
    HelpCircle,
} from 'lucide-react';

export function TopBar() {
    const { sidebarCollapsed, searchQuery, setSearchQuery } = useUIStore();
    const { notifications, unreadCount, markNotificationRead, markAllRead } = useAlertStore();
    const [showNotifications, setShowNotifications] = useState(false);
    const [showUserMenu, setShowUserMenu] = useState(false);

    return (
        <header
            className={cn(
                'fixed top-0 right-0 z-30 h-16 bg-[hsl(var(--card))] border-b border-white/10',
                'flex items-center justify-between px-6 transition-all duration-300',
                sidebarCollapsed ? 'left-16' : 'left-64'
            )}
        >
            {/* Search */}
            <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" size={18} />
                <input
                    type="text"
                    placeholder="Search pipelines, logs, alerts..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className={cn(
                        'w-full pl-10 pr-4 py-2 rounded',
                        'bg-white/5 border border-white/10',
                        'text-white/90 placeholder:text-white/30',
                        'focus:outline-none focus:border-white/30',
                        'transition-all duration-200'
                    )}
                />
                <kbd className="absolute right-3 top-1/2 -translate-y-1/2 hidden sm:inline-flex items-center gap-1 px-2 py-0.5 text-xs text-white/30 bg-white/5 rounded">
                    ⌘K
                </kbd>
            </div>

            {/* Right Section */}
            <div className="flex items-center gap-4 ml-6">
                {/* Notifications */}
                <div className="relative">
                    <button
                        onClick={() => setShowNotifications(!showNotifications)}
                        className={cn(
                            'relative p-2 rounded transition-colors',
                            'hover:bg-white/10 text-white/50 hover:text-white/70'
                        )}
                    >
                        <Bell size={20} />
                        {unreadCount > 0 && (
                            <span className="absolute -top-1 -right-1 w-5 h-5 flex items-center justify-center text-xs font-bold bg-white/30 text-white rounded-full">
                                {unreadCount}
                            </span>
                        )}
                    </button>

                    {/* Notifications Dropdown */}
                    {showNotifications && (
                        <div className={cn(
                            'absolute right-0 top-12 w-80 bg-[hsl(var(--card))] rounded shadow-xl',
                            'border border-white/10 animate-slide-in overflow-hidden'
                        )}>
                            <div className="flex items-center justify-between p-4 border-b border-white/10">
                                <h3 className="font-semibold text-white/90">Notifications</h3>
                                <button
                                    onClick={markAllRead}
                                    className="text-xs text-white/50 hover:text-white/70"
                                >
                                    Mark all read
                                </button>
                            </div>
                            <div className="max-h-80 overflow-y-auto">
                                {notifications.length === 0 ? (
                                    <p className="p-4 text-center text-white/40">
                                        No notifications
                                    </p>
                                ) : (
                                    notifications.slice(0, 5).map((notif) => (
                                        <div
                                            key={notif.id}
                                            onClick={() => markNotificationRead(notif.id)}
                                            className={cn(
                                                'flex items-start gap-3 p-4 border-b border-white/5 cursor-pointer',
                                                'hover:bg-white/5 transition-colors',
                                                !notif.read && 'bg-white/[0.02]'
                                            )}
                                        >
                                            <div className="w-2 h-2 rounded-full mt-2 flex-shrink-0 bg-white/40" />
                                            <div className="flex-1 min-w-0">
                                                <p className="font-medium text-white/80 truncate">{notif.title}</p>
                                                <p className="text-sm text-white/40 truncate">{notif.message}</p>
                                                <p className="text-xs text-white/30 mt-1">
                                                    {formatRelativeTime(notif.timestamp)}
                                                </p>
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                    )}
                </div>

                {/* User Menu */}
                <div className="relative">
                    <button
                        onClick={() => setShowUserMenu(!showUserMenu)}
                        className={cn(
                            'flex items-center gap-2 p-2 rounded transition-colors',
                            'hover:bg-white/10'
                        )}
                    >
                        <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                            <User size={16} className="text-white/70" />
                        </div>
                        <span className="hidden sm:block text-white/80 font-medium">Admin</span>
                        <ChevronDown size={16} className="text-white/40" />
                    </button>

                    {/* User Dropdown */}
                    {showUserMenu && (
                        <div className={cn(
                            'absolute right-0 top-12 w-48 bg-[hsl(var(--card))] rounded shadow-xl',
                            'border border-white/10 animate-slide-in overflow-hidden'
                        )}>
                            <div className="p-3 border-b border-white/10">
                                <p className="font-medium text-white/80">Admin User</p>
                                <p className="text-sm text-white/40">admin@flexiroaster.io</p>
                            </div>
                            <div className="py-2">
                                <button className="flex items-center gap-3 w-full px-4 py-2 text-white/50 hover:bg-white/5 hover:text-white/70 transition-colors">
                                    <Settings size={16} />
                                    Settings
                                </button>
                                <button className="flex items-center gap-3 w-full px-4 py-2 text-white/50 hover:bg-white/5 hover:text-white/70 transition-colors">
                                    <HelpCircle size={16} />
                                    Help
                                </button>
                                <button className="flex items-center gap-3 w-full px-4 py-2 text-white/50 hover:bg-white/5 transition-colors">
                                    <LogOut size={16} />
                                    Sign out
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </header>
    );
}
