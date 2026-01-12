import { Bell, Search, User } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';

export function TopBar() {
    const { user } = useAuth();

    // Get user display info
    const userName = user?.user_metadata?.full_name || user?.email?.split('@')[0] || 'User';
    const userAvatar = user?.user_metadata?.avatar_url;

    return (
        <header className="h-16 border-b border-white/10 bg-[hsl(var(--card))] flex items-center justify-between px-6">
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
                <button className="relative p-2 hover:bg-white/5 rounded-lg transition-colors">
                    <Bell className="w-5 h-5 text-white/70" />
                    <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full"></span>
                </button>

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
