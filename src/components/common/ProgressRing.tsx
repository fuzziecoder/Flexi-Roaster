import { cn } from '@/lib/utils';

interface ProgressRingProps {
    value: number;
    size?: number;
    strokeWidth?: number;
    showValue?: boolean;
    label?: string;
    className?: string;
}

export function ProgressRing({
    value,
    size = 80,
    strokeWidth = 8,
    showValue = true,
    label,
    className,
}: ProgressRingProps) {
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const offset = circumference - (value / 100) * circumference;

    return (
        <div className={cn('relative inline-flex items-center justify-center', className)}>
            <svg width={size} height={size} className="transform -rotate-90">
                {/* Background circle */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    strokeWidth={strokeWidth}
                    fill="none"
                    className="stroke-white/10"
                />
                {/* Progress circle */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    strokeWidth={strokeWidth}
                    fill="none"
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                    className="stroke-white/50 transition-all duration-500 ease-out"
                />
            </svg>
            {showValue && (
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-lg font-bold text-white/80">
                        {Math.round(value)}%
                    </span>
                    {label && (
                        <span className="text-xs text-white/40">{label}</span>
                    )}
                </div>
            )}
        </div>
    );
}
