import { cn } from '@/lib/utils';
import type { PipelineStatus as PipelineStatusType, LogLevel, AlertSeverity } from '@/types';

type BadgeVariant = PipelineStatusType | LogLevel | AlertSeverity | 'default';

interface StatusBadgeProps {
    variant: BadgeVariant;
    label?: string;
    size?: 'sm' | 'md' | 'lg';
    pulse?: boolean;
    className?: string;
}

// Muted grey styles for all variants
const variantStyles: Record<string, string> = {
    // Pipeline Status - all grey tones
    running: 'bg-white/10 text-white/90 border-white/20',
    completed: 'bg-white/5 text-white/60 border-white/10',
    failed: 'bg-white/10 text-white/70 border-white/20',
    pending: 'bg-white/5 text-white/40 border-white/10',
    paused: 'bg-white/5 text-white/50 border-white/10',

    // Log Levels - subtle grey variations
    info: 'bg-white/10 text-white/80 border-white/20',
    warn: 'bg-white/10 text-white/70 border-white/20',
    error: 'bg-white/15 text-white/90 border-white/25',
    debug: 'bg-white/5 text-white/40 border-white/10',
    success: 'bg-white/5 text-white/60 border-white/10',

    // Alert Severity - grey with opacity variations
    critical: 'bg-white/15 text-white/90 border-white/25',
    high: 'bg-white/10 text-white/80 border-white/20',
    medium: 'bg-white/10 text-white/70 border-white/15',
    low: 'bg-white/5 text-white/50 border-white/10',

    // Default
    default: 'bg-white/5 text-white/50 border-white/10',
};

const sizeStyles = {
    sm: 'px-1.5 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base',
};

const variantLabels: Record<string, string> = {
    running: 'Running',
    completed: 'Completed',
    failed: 'Failed',
    pending: 'Pending',
    paused: 'Paused',
    info: 'INFO',
    warn: 'WARN',
    error: 'ERROR',
    debug: 'DEBUG',
    success: 'SUCCESS',
    critical: 'Critical',
    high: 'High',
    medium: 'Medium',
    low: 'Low',
};

export function StatusBadge({
    variant,
    label,
    size = 'md',
    pulse = false,
    className,
}: StatusBadgeProps) {
    const displayLabel = label || variantLabels[variant] || variant;
    const shouldPulse = pulse || variant === 'running';

    return (
        <span
            className={cn(
                'inline-flex items-center gap-1.5 font-medium rounded border',
                variantStyles[variant] || variantStyles.default,
                sizeStyles[size],
                className
            )}
        >
            {shouldPulse && (
                <span className="w-1.5 h-1.5 rounded-full bg-white/70 animate-pulse" />
            )}
            {displayLabel}
        </span>
    );
}
