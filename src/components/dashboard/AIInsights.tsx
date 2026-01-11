import { cn, formatRelativeTime } from '@/lib/utils';
import { Card } from '@/components/common';
import { mockAIInsights } from '@/lib/mockData';
import type { AIInsight } from '@/types';
import {
    Brain,
    TrendingUp,
    AlertTriangle,
    Lightbulb,
    ArrowRight,
    Sparkles,
} from 'lucide-react';

const typeIcons: Record<AIInsight['type'], React.ReactNode> = {
    prediction: <TrendingUp size={18} />,
    optimization: <Lightbulb size={18} />,
    anomaly: <AlertTriangle size={18} />,
    recommendation: <Sparkles size={18} />,
};

export function AIInsights() {
    return (
        <Card
            title="AI Insights"
            description="Intelligent recommendations"
            icon={<Brain size={20} className="text-white/60" />}
            headerAction={
                <button className="text-sm text-white/50 hover:text-white/70">
                    View all
                </button>
            }
            noPadding
        >
            <div className="divide-y divide-white/5">
                {mockAIInsights.map((insight) => (
                    <div
                        key={insight.id}
                        className="p-4 transition-colors hover:bg-white/[0.02] cursor-pointer group"
                    >
                        {/* Header */}
                        <div className="flex items-start gap-3 mb-2">
                            <div className="p-2 rounded bg-white/5">
                                <span className="text-white/50">{typeIcons[insight.type]}</span>
                            </div>
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 flex-wrap">
                                    <h4 className="font-medium text-white/90">{insight.title}</h4>
                                    <span className="px-2 py-0.5 text-xs rounded bg-white/5 text-white/50 border border-white/10">
                                        {insight.impact} impact
                                    </span>
                                </div>
                                <p className="text-xs text-white/40 mt-0.5">
                                    {formatRelativeTime(insight.timestamp)}
                                </p>
                            </div>

                            {/* Confidence */}
                            <div className="flex flex-col items-end">
                                <span className="text-sm font-medium text-white/70">
                                    {Math.round(insight.confidence * 100)}%
                                </span>
                                <span className="text-xs text-white/40">
                                    confidence
                                </span>
                            </div>
                        </div>

                        {/* Description */}
                        <p className="text-sm text-white/50 mb-3 line-clamp-2">
                            {insight.description}
                        </p>

                        {/* Action Button */}
                        {insight.actionable && insight.action && (
                            <button
                                className={cn(
                                    'flex items-center gap-2 px-3 py-1.5 rounded text-sm font-medium',
                                    'bg-white/5 text-white/70 border border-white/10',
                                    'hover:bg-white/10 hover:text-white/90',
                                    'transition-all duration-200 group-hover:translate-x-1'
                                )}
                            >
                                {insight.action}
                                <ArrowRight size={14} />
                            </button>
                        )}
                    </div>
                ))}
            </div>
        </Card>
    );
}
