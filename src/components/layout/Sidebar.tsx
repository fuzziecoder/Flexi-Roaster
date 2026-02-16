import { NavLink, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { FlexibleAI } from '@/components/ai';
import {
    LayoutDashboard,
    GitBranch,
    Play,
    Calendar,
    Plug,
    KeyRound,
    LayoutTemplate,
    Sparkles,
    ScrollText,
    Bell,
    Cog,
    ChevronLeft,
    ChevronRight,
    CircleHelp,
    LogOut,
    User,
} from 'lucide-react';

interface SidebarProps {
    collapsed: boolean;
    onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
    const [showProfileMenu, setShowProfileMenu] = useState(false);
    const { user, signOut } = useAuth();
    const navigate = useNavigate();

    const handleSignOut = async () => {
        await signOut();
        navigate('/login');
    };

    const handleSettings = () => {
        setShowProfileMenu(false);
        navigate('/settings');
    };

    // Get user display info
    const userEmail = user?.email || 'user@example.com';
    const userName = user?.user_metadata?.full_name || user?.email?.split('@')[0] || 'User';
    const userAvatar = user?.user_metadata?.avatar_url;

    const navItems = [
        { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
        { to: '/pipelines', icon: GitBranch, label: 'Pipelines' },
        { to: '/executions', icon: Play, label: 'Executions' },
        { to: '/schedules', icon: Calendar, label: 'Schedules' },
        { to: '/integrations', icon: Plug, label: 'Integrations' },
        { to: '/secrets', icon: KeyRound, label: 'Secrets' },
        { to: '/templates', icon: LayoutTemplate, label: 'Templates' },
        { to: '/ai-insights', icon: Sparkles, label: 'AI Insights' },
        { to: '/logs', icon: ScrollText, label: 'Logs' },
        { to: '/alerts', icon: Bell, label: 'Alerts' },
        { to: '/settings', icon: Cog, label: 'Settings' },
        { to: '/help', icon: CircleHelp, label: 'Help & Docs' },
    ];

    return (
        <>
            {/* Mobile Overlay */}
            {!collapsed && (
                <div
                    className="fixed inset-0 bg-black/50 z-40 lg:hidden"
                    onClick={onToggle}
                />
            )}

            {/* Sidebar */}
            <aside
                className={`
          fixed lg:sticky top-0 left-0 h-screen
          bg-[hsl(var(--card))] border-r border-white/10
          transition-all duration-300 ease-in-out z-50
          ${collapsed ? '-translate-x-full lg:translate-x-0 lg:w-20' : 'translate-x-0 w-64'}
        `}
            >
                <div className="flex flex-col h-full">
                    {/* Logo */}
                    <div className="h-16 flex items-center justify-between px-4 border-b border-white/10">
                        {!collapsed && (
                            <div className="flex items-center gap-2">
                                <img src="/logo.jpg" alt="Logo" className="w-8 h-8 rounded" />
                                <span className="text-xl font-bold text-white zen-dots">FlexiRoaster</span>
                            </div>
                        )}
                        <button
                            onClick={onToggle}
                            className="p-2 hover:bg-white/5 rounded transition-colors"
                            aria-label="Toggle sidebar"
                        >
                            {collapsed ? (
                                <ChevronRight className="w-5 h-5 text-white/70" />
                            ) : (
                                <ChevronLeft className="w-5 h-5 text-white/70" />
                            )}
                        </button>
                    </div>

                    {/* Navigation */}
                    <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
                        {navItems.map((item) => (
                            <NavLink
                                key={item.to}
                                to={item.to}
                                onClick={() => {
                                    // Auto-close sidebar on mobile when a nav item is clicked
                                    if (window.innerWidth < 1024) {
                                        onToggle();
                                    }
                                }}
                                className={({ isActive }) =>
                                    `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all
                  ${isActive
                                        ? 'bg-white/10 text-white'
                                        : 'text-white/70 hover:bg-white/5 hover:text-white'
                                    }
                  ${collapsed ? 'justify-center' : ''}`
                                }
                                title={collapsed ? item.label : undefined}
                            >
                                <item.icon className="w-5 h-5 flex-shrink-0" />
                                {!collapsed && <span className="text-sm font-medium">{item.label}</span>}
                            </NavLink>
                        ))}
                    </nav>

                    {/* Flexible AI */}
                    <FlexibleAI collapsed={collapsed} />

                    {/* User Profile */}
                    <div className="relative border-t border-white/10 p-3">
                        <button
                            onClick={() => setShowProfileMenu(!showProfileMenu)}
                            className={`w-full flex items-center gap-3 p-2 rounded-lg hover:bg-white/5 transition-colors ${collapsed ? 'justify-center' : ''
                                }`}
                        >
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
                            {!collapsed && (
                                <div className="flex-1 text-left overflow-hidden">
                                    <p className="text-sm font-medium text-white truncate">{userName}</p>
                                    <p className="text-xs text-white/50 truncate">{userEmail}</p>
                                </div>
                            )}
                        </button>

                        {/* Profile Dropdown */}
                        {showProfileMenu && (
                            <div className="absolute bottom-full left-3 right-3 mb-2 bg-[hsl(var(--card))] border border-white/10 rounded-lg shadow-lg overflow-hidden">
                                <button
                                    onClick={handleSettings}
                                    className="w-full flex items-center gap-3 px-4 py-3 hover:bg-white/5 transition-colors text-left"
                                >
                                    <Cog className="w-4 h-4 text-white/70" />
                                    <span className="text-sm text-white">Settings</span>
                                </button>
                                <button
                                    onClick={() => {
                                        setShowProfileMenu(false);
                                        // Add help functionality later
                                    }}
                                    className="w-full flex items-center gap-3 px-4 py-3 hover:bg-white/5 transition-colors text-left"
                                >
                                    <CircleHelp className="w-4 h-4 text-white/70" />
                                    <span className="text-sm text-white">Help</span>
                                </button>
                                <div className="border-t border-white/10"></div>
                                <button
                                    onClick={handleSignOut}
                                    className="w-full flex items-center gap-3 px-4 py-3 hover:bg-white/5 transition-colors text-left text-red-400"
                                >
                                    <LogOut className="w-4 h-4" />
                                    <span className="text-sm">Sign Out</span>
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </aside>
        </>
    );
}
