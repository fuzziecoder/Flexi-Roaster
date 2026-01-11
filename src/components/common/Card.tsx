import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface CardProps {
    title?: string;
    description?: string;
    icon?: ReactNode;
    children: ReactNode;
    className?: string;
    headerAction?: ReactNode;
    noPadding?: boolean;
}

export function Card({
    title,
    description,
    icon,
    children,
    className,
    headerAction,
    noPadding = false,
}: CardProps) {
    return (
        <div
            className={cn(
                'bg-[hsl(var(--card))] rounded-lg border border-white/10',
                'transition-colors duration-200 hover:border-white/20',
                className
            )}
        >
            {(title || headerAction) && (
                <div className="flex items-center justify-between p-4 border-b border-white/10">
                    <div className="flex items-center gap-3">
                        {icon && (
                            <div className="p-2 rounded bg-white/5 text-white/60">
                                {icon}
                            </div>
                        )}
                        <div>
                            {title && <h3 className="font-semibold text-white/90">{title}</h3>}
                            {description && (
                                <p className="text-sm text-white/50">{description}</p>
                            )}
                        </div>
                    </div>
                    {headerAction}
                </div>
            )}
            <div className={cn(!noPadding && 'p-4')}>{children}</div>
        </div>
    );
}
