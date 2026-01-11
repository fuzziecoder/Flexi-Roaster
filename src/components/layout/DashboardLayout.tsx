import { cn } from '@/lib/utils';
import { useUIStore } from '@/store';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import { Outlet } from 'react-router-dom';

export function DashboardLayout() {
    const { sidebarCollapsed } = useUIStore();

    return (
        <div className="min-h-screen bg-[hsl(var(--background))]">
            <Sidebar />
            <div className={cn(
                'transition-all duration-300',
                sidebarCollapsed ? 'ml-16' : 'ml-64'
            )}>
                <TopBar />
                <main className="mt-16 p-6">
                    <Outlet />
                </main>
            </div>
        </div>
    );
}
