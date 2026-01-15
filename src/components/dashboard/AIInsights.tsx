import { Card } from '@/components/common';
import { Lightbulb, TrendingUp, AlertTriangle, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';

export function AIInsights() {
    // TODO: Replace with real AI insights from backend
    // For now, show empty state
    const insights: any[] = [];

    return (
        <Card
            title="AI Insights"
            headerAction={
                <button className="text-sm text-white/50 hover:text-white/70">
                    View all
                </button>
            }
        >
            {insights.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                    <Lightbulb className="w-12 h-12 text-white/20 mb-4" />
                    <h3 className="text-lg font-medium text-white/70 mb-2">No Insights Yet</h3>
                    <p className="text-sm text-white/40 max-w-sm">
                        AI insights will appear here once you have pipeline executions.
                        The system will analyze patterns and provide recommendations.
                    </p>
                </div>
            ) : (
                <div className="space-y-3">
                    {insights.map((insight: any) => (
                        <div
                            key={insight.id}
                            className={cn(
                                'p-3 rounded border transition-colors',
                                'bg-white/5 border-white/10',
                                'hover:bg-white/10'
                            )}
                        >
                            <div className="flex items-start gap-3">
                                <div className={cn(
                                    'p-2 rounded',
                                    insight.type === 'optimization' && 'bg-white/10',
                                    insight.type === 'prediction' && 'bg-white/10',
                                    insight.type === 'anomaly' && 'bg-white/15'
                                )}>
                                    {insight.type === 'optimization' && <TrendingUp className="w-4 h-4 text-white/70" />}
                                    {insight.type === 'prediction' && <Zap className="w-4 h-4 text-white/70" />}
                                    {insight.type === 'anomaly' && <AlertTriangle className="w-4 h-4 text-white/90" />}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <h4 className="text-sm font-medium text-white/90 mb-1">
                                        {insight.title}
                                    </h4>
                                    <p className="text-xs text-white/60 mb-2">
                                        {insight.description}
                                    </p>
                                    <div className="flex items-center gap-2">
                                        <span className="text-xs text-white/40">
                                            Confidence: {Math.round(insight.confidence * 100)}%
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </Card>
    );
}
