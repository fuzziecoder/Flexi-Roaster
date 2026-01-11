import { useAlertStore } from '@/store';
import { AlertTriangle, CheckCircle } from 'lucide-react';

export function AlertsPage() {
    const { alerts, acknowledgeAlert, resolveAlert } = useAlertStore();

    const getSeverityColor = (severity: string) => {
        switch (severity) {
            case 'critical':
                return 'bg-white/20 text-white/90 border-white/30';
            case 'high':
                return 'bg-white/15 text-white/80 border-white/20';
            case 'medium':
                return 'bg-white/10 text-white/70 border-white/15';
            default:
                return 'bg-white/5 text-white/60 border-white/10';
        }
    };

    const activeAlerts = alerts.filter((a) => !a.resolvedAt);
    const resolvedAlerts = alerts.filter((a) => a.resolvedAt);

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-semibold text-white/90">Alerts</h1>
                    <p className="text-sm text-white/50 mt-1">System alerts and notifications</p>
                </div>
                <div className="flex items-center gap-2 px-3 py-1.5 bg-white/5 rounded-lg border border-white/10">
                    <AlertTriangle size={16} className="text-white/70" />
                    <span className="text-sm text-white/70">{activeAlerts.length} active</span>
                </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-[hsl(var(--card))] border border-white/10 rounded-lg p-4">
                    <div className="text-xs text-white/50 mb-1">Active Alerts</div>
                    <div className="text-2xl font-semibold text-white/90">{activeAlerts.length}</div>
                </div>
                <div className="bg-[hsl(var(--card))] border border-white/10 rounded-lg p-4">
                    <div className="text-xs text-white/50 mb-1">Resolved Today</div>
                    <div className="text-2xl font-semibold text-white/90">{resolvedAlerts.length}</div>
                </div>
                <div className="bg-[hsl(var(--card))] border border-white/10 rounded-lg p-4">
                    <div className="text-xs text-white/50 mb-1">Acknowledged</div>
                    <div className="text-2xl font-semibold text-white/90">
                        {alerts.filter((a) => a.acknowledged).length}
                    </div>
                </div>
            </div>

            {/* Active Alerts */}
            <div className="bg-[hsl(var(--card))] border border-white/10 rounded-lg">
                <div className="p-4 border-b border-white/10">
                    <h2 className="text-sm font-medium text-white/90">Active Alerts</h2>
                </div>

                <div className="divide-y divide-white/10">
                    {activeAlerts.length === 0 ? (
                        <div className="p-8 text-center">
                            <CheckCircle size={48} className="mx-auto text-white/20 mb-4" />
                            <p className="text-white/50">No active alerts</p>
                        </div>
                    ) : (
                        activeAlerts.map((alert) => (
                            <div key={alert.id} className="p-4">
                                <div className="flex items-start justify-between gap-4">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-3 mb-2">
                                            <span
                                                className={`px-2 py-0.5 text-xs rounded border ${getSeverityColor(
                                                    alert.severity
                                                )}`}
                                            >
                                                {alert.severity.toUpperCase()}
                                            </span>
                                            <span className="font-medium text-white/90">{alert.title}</span>
                                        </div>
                                        <p className="text-sm text-white/70 mb-3">{alert.message}</p>
                                        <div className="text-xs text-white/40">
                                            {new Date(alert.timestamp).toLocaleString()}
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-2">
                                        {!alert.acknowledged && (
                                            <button
                                                onClick={() => acknowledgeAlert(alert.id)}
                                                className="px-3 py-1.5 text-xs bg-white/10 hover:bg-white/20 text-white/90 rounded border border-white/20 transition-colors"
                                            >
                                                Acknowledge
                                            </button>
                                        )}
                                        <button
                                            onClick={() => resolveAlert(alert.id)}
                                            className="px-3 py-1.5 text-xs bg-white/10 hover:bg-white/20 text-white/90 rounded border border-white/20 transition-colors"
                                        >
                                            Resolve
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* Resolved Alerts */}
            {resolvedAlerts.length > 0 && (
                <div className="bg-[hsl(var(--card))] border border-white/10 rounded-lg">
                    <div className="p-4 border-b border-white/10">
                        <h2 className="text-sm font-medium text-white/90">Resolved Alerts</h2>
                    </div>

                    <div className="divide-y divide-white/10 max-h-96 overflow-y-auto">
                        {resolvedAlerts.map((alert) => (
                            <div key={alert.id} className="p-4 opacity-50">
                                <div className="flex items-center gap-3">
                                    <CheckCircle size={16} className="text-white/50" />
                                    <div className="flex-1">
                                        <div className="text-sm text-white/70">{alert.title}</div>
                                        <div className="text-xs text-white/40 mt-1">
                                            Resolved: {new Date(alert.resolvedAt!).toLocaleString()}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
