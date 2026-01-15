import { Card } from '@/components/common';
import { StatusBadge } from '@/components/common';
import { useAlerts } from '@/hooks/useAlerts';
import { formatRelativeTime } from '@/lib/utils';
import { Bell } from 'lucide-react';

export function AlertsPanel() {
    const { alerts, loading, acknowledgeAlert } = useAlerts({ status: 'active' });

    // Show only active alerts, limit to 5
    const activeAlerts = alerts.slice(0, 5);

    const handleAcknowledge = async (alertId: string) => {
        await acknowledgeAlert(alertId);
    };

    if (loading) {
        return (
            <Card title="Active Alerts" description="System notifications">
                <div className="flex items-center justify-center py-8">
                    <p className="text-white/50">Loading alerts...</p>
                </div>
            </Card>
        );
    }

    return (
        <Card
            title="Active Alerts"
            description="System notifications"
            headerAction={
                <button className="text-sm text-white/50 hover:text-white/70">
                    View all
                </button>
            }
            noPadding
        >
            {activeAlerts.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-center p-6">
                    <Bell className="w-12 h-12 text-white/20 mb-4" />
                    <h3 className="text-lg font-medium text-white/70 mb-2">No Active Alerts</h3>
                    <p className="text-sm text-white/40">
                        All systems running smoothly
                    </p>
                </div>
            ) : (
                <div className="divide-y divide-white/5">
                    {activeAlerts.map((alert) => (
                        <div
                            key={alert.id}
                            className="p-4 hover:bg-white/5 transition-colors"
                        >
                            <div className="flex items-start justify-between gap-3 mb-2">
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-1">
                                        <h4 className="text-sm font-medium text-white/90">
                                            {alert.title}
                                        </h4>
                                        <StatusBadge
                                            variant={alert.severity}
                                            label={alert.severity}
                                            size="sm"
                                        />
                                    </div>
                                    <p className="text-xs text-white/60 mb-2">
                                        {alert.message}
                                    </p>
                                    <span className="text-xs text-white/40">
                                        {formatRelativeTime(alert.created_at)}
                                    </span>
                                </div>
                            </div>
                            <button
                                onClick={() => handleAcknowledge(alert.id)}
                                className="text-xs text-white/50 hover:text-white/70 transition-colors"
                            >
                                Acknowledge
                            </button>
                        </div>
                    ))}
                </div>
            )}
        </Card>
    );
}
