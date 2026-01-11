// Metrics Types
export interface SystemMetric {
    id: string;
    title: string;
    value: number | string;
    unit?: string;
    change?: number;
    changeLabel?: string;
    icon: string;
    type: 'percentage' | 'number' | 'duration' | 'rate';
    color?: 'primary' | 'success' | 'warning' | 'destructive';
}

export interface MetricsData {
    cpu: number;
    memory: number;
    throughput: number;
    activeExecutions: number;
    failureRate: number;
    avgDuration: number;
    totalPipelines: number;
    successRate: number;
}

export interface ChartDataPoint {
    timestamp: string;
    value: number;
    label?: string;
}

export interface MetricsHistory {
    cpu: ChartDataPoint[];
    memory: ChartDataPoint[];
    throughput: ChartDataPoint[];
    executionTime: ChartDataPoint[];
}
