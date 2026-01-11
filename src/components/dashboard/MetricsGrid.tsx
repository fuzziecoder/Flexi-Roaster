import { MetricsCard } from './MetricsCard';
import { ProgressRing } from '@/components/common';
import { mockMetrics } from '@/lib/mockData';

export function MetricsGrid() {
    return (
        <div className="space-y-6">
            {/* Primary Metrics Row */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <MetricsCard
                    title="CPU Usage"
                    value={mockMetrics.cpu}
                    unit="%"
                    icon="cpu"
                    type="percentage"
                    showProgress
                    change={5.2}
                    changeLabel="vs last hour"
                />
                <MetricsCard
                    title="Memory Usage"
                    value={mockMetrics.memory}
                    unit="%"
                    icon="memory"
                    type="percentage"
                    showProgress
                    change={-2.1}
                    changeLabel="vs last hour"
                />
                <MetricsCard
                    title="Throughput"
                    value={mockMetrics.throughput}
                    unit="/min"
                    icon="activity"
                    type="rate"
                    change={12.5}
                    changeLabel="vs avg"
                />
                <MetricsCard
                    title="Active Executions"
                    value={mockMetrics.activeExecutions}
                    icon="play"
                    type="number"
                />
            </div>

            {/* Secondary Metrics Row */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <MetricsCard
                    title="Total Pipelines"
                    value={mockMetrics.totalPipelines}
                    icon="pipeline"
                    type="number"
                    change={4}
                    changeLabel="this week"
                />
                <MetricsCard
                    title="Success Rate"
                    value={mockMetrics.successRate}
                    unit="%"
                    icon="check"
                    type="percentage"
                    change={1.2}
                    changeLabel="vs last week"
                />
                <MetricsCard
                    title="Failure Rate"
                    value={mockMetrics.failureRate}
                    unit="%"
                    icon="alert"
                    type="percentage"
                    change={-0.8}
                    changeLabel="vs last week"
                />
                <MetricsCard
                    title="Avg Duration"
                    value="45"
                    unit="s"
                    icon="clock"
                    type="duration"
                    change={-8}
                    changeLabel="improved"
                />
            </div>

            {/* System Health Overview with Progress Rings */}
            <div className="bg-[hsl(var(--card))] rounded-lg border border-white/10 p-6">
                <h3 className="text-lg font-semibold text-white/90 mb-6">System Health Overview</h3>
                <div className="flex flex-wrap justify-around gap-6">
                    <div className="flex flex-col items-center">
                        <ProgressRing value={mockMetrics.cpu} size={100} strokeWidth={10} label="CPU" />
                        <span className="mt-2 text-sm text-white/40">CPU Load</span>
                    </div>
                    <div className="flex flex-col items-center">
                        <ProgressRing value={mockMetrics.memory} size={100} strokeWidth={10} label="MEM" />
                        <span className="mt-2 text-sm text-white/40">Memory</span>
                    </div>
                    <div className="flex flex-col items-center">
                        <ProgressRing value={mockMetrics.successRate} size={100} strokeWidth={10} label="OK" />
                        <span className="mt-2 text-sm text-white/40">Success Rate</span>
                    </div>
                    <div className="flex flex-col items-center">
                        <ProgressRing value={85} size={100} strokeWidth={10} label="UP" />
                        <span className="mt-2 text-sm text-white/40">Uptime</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
