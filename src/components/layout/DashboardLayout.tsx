import { useState } from 'react';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import { Outlet } from 'react-router-dom';
import { ToastContainer } from '@/components/common';

export function DashboardLayout() {
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

    return (
        <div className="flex min-h-screen bg-[hsl(var(--background))]">
            <Sidebar collapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} />

            <div className="flex-1 flex flex-col">
                <TopBar />
                <main className="flex-1 overflow-auto p-6">
                    <Outlet />
                </main>
            </div>

            {/* Toast Notifications */}
            <ToastContainer />
        </div>
    );
}

