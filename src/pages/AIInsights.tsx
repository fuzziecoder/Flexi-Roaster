import { Brain, Lightbulb } from 'lucide-react';
import { Card } from '@/components/common';
import { useAIInsights } from '@/hooks/useAIInsights';

export function AIInsightsPage() {
    const { insights, loading } = useAIInsights();

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-white/50">Loading AI insights...</div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-semibold text-white/90">AI Insights</h1>
                    <p className="text-sm text-white/50 mt-1">
                        AI-powered predictions and recommendations
                    </p>
                </div>
                <div className="flex items-center gap-2 px-3 py-1.5 bg-white/5 rounded-lg border border-white/10">
                    <Brain size={16} className="text-white/70" />
                    <span className="text-sm text-white/70">
                        {insights.length} insights
                    </span>
                </div>
            </div>

            {/* Insights Grid */}
            {insights.length === 0 ? (
                <Card className="p-12 text-center">
                    <Lightbulb className="w-12 h-12 mx-auto text-white/20 mb-4" />
                    <h3 className="text-lg font-medium text-white/70 mb-2">No Insights Yet</h3>
                    <p className="text-sm text-white/40 max-w-md mx-auto">
                        AI insights will appear here once you have pipeline executions.
                        The system will analyze patterns and provide recommendations.
                    </p>
                </Card>
            ) : (
                <div className="grid grid-cols-1 gap-4">
                    {insights.map((insight) => (
                        <Card key={insight.id} className="p-5 hover:border-white/20 transition-colors">
                            <div className="flex items-start gap-4">
                                <div className="p-2 rounded bg-white/10">
                                    <Brain className="w-5 h-5 text-white/70" />
                                </div>
                                <div className="flex-1">
                                    <div className="flex items-center gap-3 mb-2">
                                        <h3 className="font-medium text-white/90">{insight.title}</h3>
                                        <span className="px-2 py-0.5 text-xs rounded bg-white/10 text-white/60">
                                            {insight.insight_type}
                                        </span>
                                        <span className="text-xs text-white/40">
                                            {Math.round(insight.confidence * 100)}% confidence
                                        </span>
                                    </div>
                                    <p className="text-sm text-white/70">{insight.description}</p>
                                </div>
                            </div>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
}
