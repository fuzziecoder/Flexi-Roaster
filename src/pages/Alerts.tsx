import { useState } from 'react';
import { Card } from '@/components/common';
import { StatusBadge } from '@/components/common';
import { Search, CheckCircle, XCircle } from 'lucide-react';
import { useAlerts } from '@/hooks/useAlerts';
import { formatRelativeTime } from '@/lib/utils';
import type { AlertSeverity, AlertStatus } from '@/types/database';

export function AlertsPage() {
    const [searchQuery, setSearchQuery] = useState('');
    const [severityFilter, setSeverityFilter] = useState<AlertSeverity | ''>('');
    const [statusFilter, setStatusFilter] = useState<AlertStatus | ''>('');

    const { alerts, loading, acknowledgeAlert, resolveAlert } = useAlerts({
        severity: severityFilter || undefined,
        status: statusFilter || undefined,
    });

    const filteredAlerts = alerts.filter(alert =>
        alert.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        alert.message.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const handleAcknowledge = async (alertId: string) => {
        await acknowledgeAlert(alertId);
    };

    const handleResolve = async (alertId: string) => {
        await resolveAlert(alertId);
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-white/70">Loading alerts...</div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">Alerts</h1>
                    <p className="text-white/50 mt-1">{filteredAlerts.length} alerts</p>
                </div>
            </div>

            {/* Filters */}
            <div className="flex items-center gap-4">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Search alerts..."
                        className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded text-white placeholder:text-white/40 focus:outline-none focus:border-white/20 transition-colors"
                    />
                </div>
                <select
                    value={severityFilter}
                    onChange={(e) => setSeverityFilter(e.target.value as AlertSeverity | '')}
                    className="px-4 py-2 bg-[hsl(var(--card))] border border-white/10 rounded text-white focus:outline-none focus:border-white/20 transition-colors [&>option]:bg-[hsl(var(--card))] [&>option]:text-white"
                >
                    <option value="">All Severities</option>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                </select>
                <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value as AlertStatus | '')}
                    className="px-4 py-2 bg-[hsl(var(--card))] border border-white/10 rounded text-white focus:outline-none focus:border-white/20 transition-colors [&>option]:bg-[hsl(var(--card))] [&>option]:text-white"
                >
                    <option value="">All Status</option>
                    <option value="active">Active</option>
                    <option value="acknowledged">Acknowledged</option>
                    <option value="resolved">Resolved</option>
                </select>
            </div>

            {/* Alerts List */}
            {filteredAlerts.length === 0 ? (
                <Card className="p-12 text-center">
                    <p className="text-white/50">
                        {searchQuery || severityFilter || statusFilter
                            ? 'No alerts found matching your filters.'
                            : 'No alerts. Everything is running smoothly!'}
                    </p>
                </Card>
            ) : (
                <div className="space-y-3">
                    {filteredAlerts.map((alert) => (
                        <Card key={alert.id} className="p-6 hover:border-white/20 transition-colors">
                            <div className="flex items-start justify-between gap-4">
                                <div className="flex-1">
                                    <div className="flex items-center gap-3 mb-2">
                                        <h3 className="text-lg font-semibold text-white">{alert.title}</h3>
                                        <StatusBadge
                                            variant={alert.severity}
                                            label={alert.severity.charAt(0).toUpperCase() + alert.severity.slice(1)}
                                        />
                                        <StatusBadge
                                            variant="default"
                                            label={alert.status.charAt(0).toUpperCase() + alert.status.slice(1)}
                                            size="sm"
                                        />
                                    </div>
                                    <p className="text-white/70 mb-3">{alert.message}</p>
                                    <div className="flex items-center gap-4 text-sm text-white/50">
                                        <span>Created: {formatRelativeTime(alert.created_at)}</span>
                                        {alert.acknowledged_at && (
                                            <span>Acknowledged: {formatRelativeTime(alert.acknowledged_at)}</span>
                                        )}
                                        {alert.resolved_at && (
                                            <span>Resolved: {formatRelativeTime(alert.resolved_at)}</span>
                                        )}
                                    </div>
                                </div>
                                <div className="flex gap-2">
                                    {alert.status === 'active' && (
                                        <button
                                            onClick={() => handleAcknowledge(alert.id)}
                                            className="flex items-center gap-2 px-3 py-1.5 bg-white/10 hover:bg-white/20 text-white text-sm rounded transition-colors"
                                        >
                                            <CheckCircle className="w-4 h-4" />
                                            Acknowledge
                                        </button>
                                    )}
                                    {(alert.status === 'active' || alert.status === 'acknowledged') && (
                                        <button
                                            onClick={() => handleResolve(alert.id)}
                                            className="flex items-center gap-2 px-3 py-1.5 bg-white/90 hover:bg-white text-black text-sm rounded font-medium transition-colors"
                                        >
                                            <XCircle className="w-4 h-4" />
                                            Resolve
                                        </button>
                                    )}
                                </div>
                            </div>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
}
