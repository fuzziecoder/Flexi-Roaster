import type { ReactNode } from 'react';
import { cn, formatChange } from '@/lib/utils';
import {
    Cpu,
    MemoryStick,
    Activity,
    PlayCircle,
    AlertTriangle,
    Clock,
    GitBranch,
    CheckCircle,
    TrendingUp,
    TrendingDown,
} from 'lucide-react';

interface MetricsCardProps {
    title: string;
    value: string | number;
    unit?: string;
    change?: number;
    changeLabel?: string;
    icon: string;
    type?: 'percentage' | 'number' | 'duration' | 'rate';
    showProgress?: boolean;
    className?: string;
}

const iconMap: Record<string, ReactNode> = {
    cpu: <Cpu size={20} />,
    memory: <MemoryStick size={20} />,
    activity: <Activity size={20} />,
    play: <PlayCircle size={20} />,
    alert: <AlertTriangle size={20} />,
    clock: <Clock size={20} />,
    pipeline: <GitBranch size={20} />,
    check: <CheckCircle size={20} />,
};

export function MetricsCard({
    title,
    value,
    unit,
    change,
    changeLabel,
    icon,
    type = 'number',
    showProgress = false,
    className,
}: MetricsCardProps) {
    const isPositiveChange = change !== undefined && change >= 0;

    return (
        <div
            className={cn(
                'bg-[hsl(var(--card))] rounded-lg border border-white/10 p-4',
                'transition-colors duration-200 hover:border-white/20',
                className
            )}
        >
            <div className="flex items-start justify-between">
                <div className="flex-1">
                    <p className="text-sm font-medium text-white/50 mb-1">
                        {title}
                    </p>
                    <div className="flex items-baseline gap-1">
                        <span className="text-2xl font-bold text-white/90">
                            {value}
                        </span>
                        {unit && (
                            <span className="text-sm text-white/40">{unit}</span>
                        )}
                    </div>

                    {change !== undefined && (
                        <div className="flex items-center gap-1 mt-2">
                            {isPositiveChange ? (
                                <TrendingUp size={14} className="text-white/50" />
                            ) : (
                                <TrendingDown size={14} className="text-white/50" />
                            )}
                            <span className="text-xs font-medium text-white/60">
                                {formatChange(change)}
                            </span>
                            {changeLabel && (
                                <span className="text-xs text-white/40">
                                    {changeLabel}
                                </span>
                            )}
                        </div>
                    )}
                </div>

                <div className="p-3 rounded bg-white/5">
                    <span className="text-white/50">
                        {iconMap[icon] || iconMap.activity}
                    </span>
                </div>
            </div>

            {showProgress && type === 'percentage' && typeof value === 'number' && (
                <div className="mt-4">
                    <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-white/40 rounded-full transition-all duration-500"
                            style={{ width: `${Math.min(value, 100)}%` }}
                        />
                    </div>
                </div>
            )}
        </div>
    );
}
