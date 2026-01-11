import { cn, formatRelativeTime } from '@/lib/utils';
import { Card, StatusBadge } from '@/components/common';
import { useAlertStore } from '@/store';
import { AlertTriangle, Check, Eye, X, Bell } from 'lucide-react';

export function AlertsPanel() {
    const { alerts, acknowledgeAlert } = useAlertStore();
    const activeAlerts = alerts.filter((a) => !a.resolvedAt);

    return (
        <Card
            title="Active Alerts"
            description={`${activeAlerts.length} unresolved`}
            icon={<AlertTriangle size={20} className="text-white/50" />}
            headerAction={
                activeAlerts.length > 0 && (
                    <span className="flex items-center gap-1 px-2 py-1 text-xs font-medium bg-white/10 text-white/70 rounded border border-white/10">
                        <Bell size={12} />
                        {activeAlerts.filter((a) => !a.acknowledged).length} new
                    </span>
                )
            }
            noPadding
        >
            {activeAlerts.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-white/40">
                    <Check size={48} className="text-white/30 mb-3" />
                    <p className="font-medium">All clear!</p>
                    <p className="text-sm">No active alerts at the moment</p>
                </div>
            ) : (
                <div className="divide-y divide-white/5">
                    {activeAlerts.map((alert) => (
                        <div
                            key={alert.id}
                            className={cn(
                                'p-4 transition-colors hover:bg-white/[0.02]',
                                !alert.acknowledged && 'bg-white/[0.02] border-l-2 border-l-white/30'
                            )}
                        >
                            {/* Header */}
                            <div className="flex items-start justify-between gap-2 mb-2">
                                <div className="flex items-center gap-2">
                                    <StatusBadge variant={alert.severity} size="sm" pulse={!alert.acknowledged} />
                                    <h4 className="font-medium text-white/90">{alert.title}</h4>
                                </div>
                                <span className="text-xs text-white/40 flex-shrink-0">
                                    {formatRelativeTime(alert.timestamp)}
                                </span>
                            </div>

                            {/* Message */}
                            <p className="text-sm text-white/50 mb-3">
                                {alert.message}
                            </p>

                            {/* Source */}
                            <div className="flex items-center justify-between">
                                <span className="text-xs text-white/40 font-mono">
                                    Source: {alert.source}
                                </span>

                                {/* Actions */}
                                <div className="flex items-center gap-1">
                                    <button
                                        className={cn(
                                            'flex items-center gap-1 px-2 py-1 text-xs rounded',
                                            'bg-white/5 hover:bg-white/10',
                                            'text-white/50 hover:text-white/70',
                                            'transition-colors'
                                        )}
                                    >
                                        <Eye size={12} />
                                        View
                                    </button>
                                    {!alert.acknowledged && (
                                        <button
                                            onClick={() => acknowledgeAlert(alert.id)}
                                            className={cn(
                                                'flex items-center gap-1 px-2 py-1 text-xs rounded',
                                                'bg-white/10 hover:bg-white/15',
                                                'text-white/70',
                                                'transition-colors'
                                            )}
                                        >
                                            <Check size={12} />
                                            Ack
                                        </button>
                                    )}
                                    <button
                                        className={cn(
                                            'flex items-center gap-1 px-2 py-1 text-xs rounded',
                                            'bg-white/5 hover:bg-white/10',
                                            'text-white/60',
                                            'transition-colors'
                                        )}
                                    >
                                        <X size={12} />
                                        Resolve
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </Card>
    );
}
