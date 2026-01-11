import { MetricsGrid, PipelineStatus, ActivityLog, AIInsights, AlertsPanel } from '@/components/dashboard';

export function Dashboard() {
    return (
        <div className="space-y-6 animate-fade-in">
            {/* Page Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white/90">Dashboard</h1>
                    <p className="text-white/40">
                        Monitor your pipelines and system health
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <div className="flex items-center gap-2 px-3 py-1.5 rounded bg-white/5 border border-white/10">
                        <div className="w-2 h-2 rounded-full bg-white/50 animate-pulse" />
                        <span className="text-sm font-medium text-white/60">All Systems Operational</span>
                    </div>
                </div>
            </div>

            {/* Metrics Section */}
            <MetricsGrid />

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Pipeline Status - Takes 2 columns */}
                <div className="lg:col-span-2">
                    <PipelineStatus />
                </div>

                {/* Alerts Panel */}
                <div>
                    <AlertsPanel />
                </div>
            </div>

            {/* Bottom Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Activity Log */}
                <ActivityLog />

                {/* AI Insights */}
                <AIInsights />
            </div>
        </div>
    );
}
