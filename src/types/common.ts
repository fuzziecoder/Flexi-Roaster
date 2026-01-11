// Common Types
export type LogLevel = 'info' | 'warn' | 'error' | 'debug' | 'success';
export type AlertSeverity = 'critical' | 'high' | 'medium' | 'low';

export interface LogEntry {
    id: string;
    timestamp: string;
    level: LogLevel;
    service: string;
    message: string;
    details?: Record<string, unknown>;
}

export interface Alert {
    id: string;
    title: string;
    message: string;
    severity: AlertSeverity;
    source: string;
    timestamp: string;
    acknowledged: boolean;
    resolvedAt?: string;
}

export interface AIInsight {
    id: string;
    type: 'prediction' | 'optimization' | 'anomaly' | 'recommendation';
    title: string;
    description: string;
    confidence: number;
    impact: 'high' | 'medium' | 'low';
    timestamp: string;
    actionable: boolean;
    action?: string;
}

export interface Notification {
    id: string;
    title: string;
    message: string;
    type: 'info' | 'success' | 'warning' | 'error';
    read: boolean;
    timestamp: string;
}

export interface NavItem {
    id: string;
    label: string;
    icon: string;
    path: string;
    badge?: number;
}
