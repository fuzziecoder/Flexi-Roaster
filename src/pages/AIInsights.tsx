import { useAIInsights } from '@/lib/hooks';
import { Brain, AlertTriangle, TrendingUp, Lightbulb, Target } from 'lucide-react';

export function AIInsightsPage() {
    const { data: insightsData, isLoading, error } = useAIInsights();

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-white/50">Loading AI insights...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-red-400">Error loading insights. Make sure backend is running.</div>
            </div>
        );
    }

    const insights = insightsData?.insights || [];

    const getSeverityColor = (severity: string) => {
        switch (severity) {
            case 'high':
                return 'bg-white/20 text-white/90';
            case 'medium':
                return 'bg-white/10 text-white/70';
            default:
                return 'bg-white/5 text-white/50';
        }
    };

    const getTypeIcon = (type: string) => {
        switch (type) {
            case 'prediction':
                return <Brain size={20} />;
            case 'performance':
                return <TrendingUp size={20} />;
            case 'optimization':
                return <Lightbulb size={20} />;
            case 'success':
                return <Target size={20} />;
            default:
                return <AlertTriangle size={20} />;
        }
    };

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
                        {insights.length} insights generated
                    </span>
                </div>
            </div>

            {/* Insights Grid */}
            {insights.length === 0 ? (
                <div className="bg-[hsl(var(--card))] border border-white/10 rounded-lg p-12 text-center">
                    <Brain size={48} className="mx-auto text-white/20 mb-4" />
                    <h3 className="text-lg font-medium text-white/70 mb-2">No Insights Yet</h3>
                    <p className="text-sm text-white/50">
                        Execute some pipelines to generate AI insights
                    </p>
                </div>
            ) : (
                <div className="grid grid-cols-1 gap-4">
                    {insights.map((insight: any, index: number) => (
                        <div
                            key={index}
                            className="bg-[hsl(var(--card))] border border-white/10 rounded-lg p-5 hover:border-white/20 transition-colors"
                        >
                            <div className="flex items-start gap-4">
                                <div className={`p-2 rounded ${getSeverityColor(insight.severity)}`}>
                                    {getTypeIcon(insight.type)}
                                </div>

                                <div className="flex-1">
                                    <div className="flex items-center gap-3 mb-2">
                                        <h3 className="font-medium text-white/90">{insight.title}</h3>
                                        <span
                                            className={`px-2 py-0.5 text-xs rounded ${getSeverityColor(
                                                insight.severity
                                            )}`}
                                        >
                                            {insight.severity.toUpperCase()}
                                        </span>
                                        <span className="text-xs text-white/40">
                                            {Math.round(insight.confidence * 100)}% confidence
                                        </span>
                                    </div>

                                    <p className="text-sm text-white/70 mb-3">{insight.message}</p>

                                    <div className="flex items-center gap-2 text-xs text-white/50">
                                        <Lightbulb size={14} />
                                        <span className="font-medium">Recommendation:</span>
                                        <span>{insight.recommendation}</span>
                                    </div>

                                    {insight.pipeline_id && (
                                        <div className="mt-3 pt-3 border-t border-white/10">
                                            <span className="text-xs text-white/40">
                                                Pipeline: {insight.pipeline_id}
                                            </span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
