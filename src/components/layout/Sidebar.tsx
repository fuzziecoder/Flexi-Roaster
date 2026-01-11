import { Link, useLocation } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { useUIStore } from '@/store';
import {
    LayoutDashboard,
    GitBranch,
    Play,
    Brain,
    FileText,
    AlertTriangle,
    Settings,
    ChevronLeft,
    ChevronRight,
} from 'lucide-react';

interface NavItem {
    id: string;
    label: string;
    icon: React.ReactNode;
    path: string;
    badge?: number;
}

const navItems: NavItem[] = [
    { id: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard size={20} />, path: '/' },
    { id: 'pipelines', label: 'Pipelines', icon: <GitBranch size={20} />, path: '/pipelines' },
    { id: 'executions', label: 'Executions', icon: <Play size={20} />, path: '/executions' },
    { id: 'ai-insights', label: 'AI Insights', icon: <Brain size={20} />, path: '/ai-insights' },
    { id: 'logs', label: 'Logs', icon: <FileText size={20} />, path: '/logs' },
    { id: 'alerts', label: 'Alerts', icon: <AlertTriangle size={20} />, path: '/alerts', badge: 2 },
    { id: 'settings', label: 'Settings', icon: <Settings size={20} />, path: '/settings' },
];

export function Sidebar() {
    const location = useLocation();
    const { sidebarCollapsed, toggleSidebar } = useUIStore();

    return (
        <aside
            className={cn(
                'fixed left-0 top-0 z-40 h-screen bg-[hsl(var(--card))] border-r border-white/10',
                'flex flex-col transition-all duration-300 ease-in-out',
                sidebarCollapsed ? 'w-16' : 'w-64'
            )}
        >
            {/* Logo Section */}
            <div className="flex items-center h-14 px-3 border-b border-white/10">
                <img
                    src="/logo.jpg"
                    alt="FlexiRoaster"
                    className={cn(
                        'transition-all duration-300 rounded-full object-cover',
                        sidebarCollapsed ? 'w-8 h-8' : 'w-9 h-9'
                    )}
                />
                {!sidebarCollapsed && (
                    <span className="ml-2.5 text-sm text-white/90 animate-fade-in" style={{ fontFamily: '"Zen Dots", sans-serif' }}>
                        FlexiRoaster
                    </span>
                )}
            </div>

            {/* Navigation */}
            <nav className="flex-1 py-4 overflow-y-auto">
                <ul className="space-y-1 px-2">
                    {navItems.map((item) => {
                        const isActive = location.pathname === item.path;
                        return (
                            <li key={item.id}>
                                <Link
                                    to={item.path}
                                    className={cn(
                                        'flex items-center gap-3 px-3 py-2.5 rounded transition-all duration-200',
                                        'hover:bg-white/10 group',
                                        isActive && 'bg-white/20 text-white',
                                        !isActive && 'text-white/40'
                                    )}
                                >
                                    <span className={cn(
                                        'transition-colors',
                                        isActive ? 'text-white' : 'text-white/40 group-hover:text-white/70'
                                    )}>
                                        {item.icon}
                                    </span>
                                    {!sidebarCollapsed && (
                                        <span className={cn(
                                            'flex-1 font-medium animate-fade-in',
                                            isActive ? 'text-white' : 'text-white/50'
                                        )}>{item.label}</span>
                                    )}
                                    {!sidebarCollapsed && item.badge && (
                                        <span className="px-2 py-0.5 text-xs font-semibold bg-white/20 text-white/90 rounded-full">
                                            {item.badge}
                                        </span>
                                    )}
                                </Link>
                            </li>
                        );
                    })}
                </ul>
            </nav>

            {/* Collapse Toggle */}
            <div className="p-4 border-t border-white/10">
                <button
                    onClick={toggleSidebar}
                    className={cn(
                        'flex items-center justify-center w-full py-2 rounded',
                        'bg-white/5 hover:bg-white/10',
                        'text-white/50 hover:text-white/70',
                        'transition-all duration-200'
                    )}
                >
                    {sidebarCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
                    {!sidebarCollapsed && <span className="ml-2">Collapse</span>}
                </button>
            </div>
        </aside>
    );
}
