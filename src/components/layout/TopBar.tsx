import { useState, useRef, useEffect } from 'react';
import { Bell, Search, User, X, AlertTriangle, CheckCircle, Info, Menu } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { Link } from 'react-router-dom';

interface Notification {
    id: string;
    type: 'info' | 'warning' | 'success';
    title: string;
    message: string;
    time: string;
    read: boolean;
}

// Sample notifications - in production, these would come from a store or API
const sampleNotifications: Notification[] = [
    {
        id: '1',
        type: 'success',
        title: 'Pipeline completed',
        message: 'Data sync pipeline finished successfully',
        time: '2 min ago',
        read: false,
    },
    {
        id: '2',
        type: 'warning',
        title: 'High memory usage',
        message: 'Pipeline "Analytics" is using 85% memory',
        time: '15 min ago',
        read: false,
    },
    {
        id: '3',
        type: 'info',
        title: 'Scheduled maintenance',
        message: 'System maintenance planned for tonight',
        time: '1 hour ago',
        read: true,
    },
];

const iconMap = {
    success: CheckCircle,
    warning: AlertTriangle,
    info: Info,
};

const colorMap = {
    success: 'text-emerald-400',
    warning: 'text-amber-400',
    info: 'text-blue-400',
};

interface TopBarProps {
    onToggleSidebar?: () => void;
}

export function TopBar({ onToggleSidebar }: TopBarProps) {
    const { user } = useAuth();
    const [showNotifications, setShowNotifications] = useState(false);
    const [notifications, setNotifications] = useState<Notification[]>(sampleNotifications);
    const dropdownRef = useRef<HTMLDivElement>(null);

    // Get user display info
    const userName = user?.user_metadata?.full_name || user?.email?.split('@')[0] || 'User';
    const userAvatar = user?.user_metadata?.avatar_url;

    const unreadCount = notifications.filter(n => !n.read).length;

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setShowNotifications(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const markAllAsRead = () => {
        setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    };

    const dismissNotification = (id: string) => {
        setNotifications(prev => prev.filter(n => n.id !== id));
    };

    return (
        <header className="h-16 border-b border-white/10 bg-[hsl(var(--card))] flex items-center justify-between px-4 md:px-6 gap-3">
            {/* Mobile Sidebar Toggle */}
            <button
                onClick={onToggleSidebar}
                className="lg:hidden p-2 hover:bg-white/10 rounded-lg transition-colors flex-shrink-0"
                aria-label="Toggle navigation menu"
                id="mobile-sidebar-toggle"
            >
                <Menu className="w-5 h-5 text-white/70" />
            </button>

            {/* Search */}
            <div className="flex-1 max-w-xl">
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
                    <input
                        type="text"
                        placeholder="Search pipelines, executions..."
                        className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder:text-white/40 focus:outline-none focus:border-white/20 transition-colors"
                    />
                </div>
            </div>

            {/* Right Section */}
            <div className="flex items-center gap-4">
                {/* Notifications */}
                <div className="relative" ref={dropdownRef}>
                    <button
                        onClick={() => setShowNotifications(!showNotifications)}
                        className="relative p-2 hover:bg-white/5 rounded-lg transition-colors"
                    >
                        <Bell className="w-5 h-5 text-white/70" />
                        {unreadCount > 0 && (
                            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full"></span>
                        )}
                    </button>

                    {/* Notification Dropdown */}
                    {showNotifications && (
                        <div className="absolute right-0 top-12 w-80 bg-[#1a1a1a] border border-white/10 rounded-xl shadow-2xl z-50 overflow-hidden">
                            {/* Header */}
                            <div className="flex items-center justify-between p-3 border-b border-white/10">
                                <h3 className="text-sm font-semibold text-white">Notifications</h3>
                                {unreadCount > 0 && (
                                    <button
                                        onClick={markAllAsRead}
                                        className="text-xs text-white/40 hover:text-white/60 transition-colors"
                                    >
                                        Mark all as read
                                    </button>
                                )}
                            </div>

                            {/* Notifications List */}
                            <div className="max-h-80 overflow-y-auto">
                                {notifications.length === 0 ? (
                                    <div className="p-6 text-center">
                                        <Bell className="w-8 h-8 text-white/20 mx-auto mb-2" />
                                        <p className="text-sm text-white/40">No notifications</p>
                                    </div>
                                ) : (
                                    notifications.map(notification => {
                                        const Icon = iconMap[notification.type];
                                        return (
                                            <div
                                                key={notification.id}
                                                className={`flex items-start gap-3 p-3 border-b border-white/5 hover:bg-white/5 transition-colors ${!notification.read ? 'bg-white/[0.02]' : ''
                                                    }`}
                                            >
                                                <div className={`mt-0.5 ${colorMap[notification.type]}`}>
                                                    <Icon className="w-4 h-4" />
                                                </div>
                                                <div className="flex-1 min-w-0">
                                                    <p className={`text-sm font-medium ${notification.read ? 'text-white/60' : 'text-white'}`}>
                                                        {notification.title}
                                                    </p>
                                                    <p className="text-xs text-white/40 mt-0.5 truncate">
                                                        {notification.message}
                                                    </p>
                                                    <p className="text-[10px] text-white/30 mt-1">
                                                        {notification.time}
                                                    </p>
                                                </div>
                                                <button
                                                    onClick={() => dismissNotification(notification.id)}
                                                    className="p-1 hover:bg-white/10 rounded transition-colors"
                                                >
                                                    <X className="w-3 h-3 text-white/40" />
                                                </button>
                                            </div>
                                        );
                                    })
                                )}
                            </div>

                            {/* Footer */}
                            <div className="p-2 border-t border-white/10">
                                <Link
                                    to="/alerts"
                                    onClick={() => setShowNotifications(false)}
                                    className="block w-full py-2 text-center text-xs text-white/50 hover:text-white/70 hover:bg-white/5 rounded transition-colors"
                                >
                                    View all alerts
                                </Link>
                            </div>
                        </div>
                    )}
                </div>

                {/* User Profile */}
                <div className="flex items-center gap-3">
                    {userAvatar ? (
                        <img
                            src={userAvatar}
                            alt={userName}
                            className="w-8 h-8 rounded-full"
                        />
                    ) : (
                        <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center">
                            <User className="w-4 h-4 text-white/70" />
                        </div>
                    )}
                    <div className="hidden md:block">
                        <p className="text-sm font-medium text-white">{userName}</p>
                        <p className="text-xs text-white/50">Online</p>
                    </div>
                </div>
            </div>
        </header>
    );
}
