import {
    BookOpen,
    GitBranch,
    Play,
    Brain,
    FileText,
    Bell,
    Settings,
    ChevronRight,
    ExternalLink,
    HelpCircle,
    Zap,
    Shield,
    Lightbulb
} from 'lucide-react';
import { Card } from '@/components/common';
import { useNavigate } from 'react-router-dom';

interface DocSectionProps {
    icon: React.ElementType;
    title: string;
    description: string;
    link: string;
    features: string[];
}

function DocSection({ icon: Icon, title, description, link, features }: DocSectionProps) {
    const navigate = useNavigate();

    return (
        <div
            className="cursor-pointer"
            onClick={() => navigate(link)}
        >
            <Card className="p-6 hover:border-white/20 transition-colors">
                <div className="flex items-start gap-4">
                    <div className="p-3 rounded-xl bg-white/5">
                        <Icon className="w-6 h-6 text-white/70" />
                    </div>
                    <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                            <h3 className="text-lg font-semibold text-white">{title}</h3>
                            <ChevronRight className="w-5 h-5 text-white/30" />
                        </div>
                        <p className="text-sm text-white/50 mb-4">{description}</p>
                        <div className="space-y-2">
                            {features.map((feature, i) => (
                                <div key={i} className="flex items-center gap-2 text-sm text-white/60">
                                    <div className="w-1.5 h-1.5 rounded-full bg-white/30" />
                                    {feature}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </Card>
        </div>
    );
}

export function Help() {
    const sections: DocSectionProps[] = [
        {
            icon: GitBranch,
            title: 'Pipelines',
            description: 'Create, manage, and monitor your data pipelines',
            link: '/pipelines',
            features: [
                'Create new pipelines with stages (input, transform, validation, output)',
                'Configure pipeline settings and schedules',
                'Activate/deactivate pipelines',
                'View pipeline configuration and history'
            ]
        },
        {
            icon: Play,
            title: 'Executions',
            description: 'Track and manage pipeline execution runs',
            link: '/executions',
            features: [
                'View real-time execution status and progress',
                'Monitor stage-by-stage completion',
                'Access execution logs and output',
                'Retry failed executions'
            ]
        },
        {
            icon: Brain,
            title: 'AI Insights',
            description: 'Get AI-powered recommendations and predictions',
            link: '/ai-insights',
            features: [
                'Failure predictions based on historical data',
                'Optimization suggestions for performance',
                'Anomaly detection alerts',
                'Cost optimization recommendations'
            ]
        },
        {
            icon: FileText,
            title: 'Logs',
            description: 'View detailed system and execution logs',
            link: '/logs',
            features: [
                'Real-time log streaming',
                'Filter by log level (DEBUG, INFO, WARN, ERROR)',
                'Search across all logs',
                'Export logs for analysis'
            ]
        },
        {
            icon: Bell,
            title: 'Alerts',
            description: 'Monitor and respond to system alerts',
            link: '/alerts',
            features: [
                'View critical, high, medium, and low severity alerts',
                'Acknowledge and resolve alerts',
                'Configure alert thresholds',
                'Set up notification channels'
            ]
        },
        {
            icon: Settings,
            title: 'Settings',
            description: 'Configure your account and preferences',
            link: '/settings',
            features: [
                'Update profile information and avatar',
                'Configure notification preferences',
                'Manage API keys and integrations',
                'Theme and appearance settings'
            ]
        }
    ];

    const quickTips = [
        {
            icon: Zap,
            title: 'Quick Actions',
            tip: 'Use Flexible AI (bottom of sidebar) to create pipelines, list them, or navigate using natural language.'
        },
        {
            icon: Shield,
            title: 'Best Practices',
            tip: 'Always include validation stages in your pipelines to catch data quality issues early.'
        },
        {
            icon: Lightbulb,
            title: 'Pro Tip',
            tip: 'Enable AI Insights notifications to get proactive suggestions for pipeline optimization.'
        }
    ];

    return (
        <div className="space-y-8 animate-fade-in">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white flex items-center gap-3">
                        <BookOpen className="w-7 h-7" />
                        Documentation & Help
                    </h1>
                    <p className="text-white/40 mt-1">
                        Learn how to use FlexiRoaster effectively
                    </p>
                </div>
            </div>

            {/* Quick Tips */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {quickTips.map((tip, i) => (
                    <div key={i} className="p-4 rounded-xl bg-gradient-to-br from-white/[0.03] to-white/[0.01] border border-white/10">
                        <div className="flex items-start gap-3">
                            <div className="p-2 rounded-lg bg-white/5">
                                <tip.icon className="w-5 h-5 text-white/60" />
                            </div>
                            <div>
                                <h4 className="font-medium text-white mb-1">{tip.title}</h4>
                                <p className="text-sm text-white/50">{tip.tip}</p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Getting Started */}
            <Card className="p-5">
                <div className="flex items-start gap-4">
                    <div className="p-2.5 rounded-lg bg-white/5">
                        <HelpCircle className="w-6 h-6 text-white/50" />
                    </div>
                    <div className="flex-1">
                        <h2 className="text-base font-semibold text-white/90 mb-2">Getting Started</h2>
                        <p className="text-xs text-white/50 mb-3">
                            FlexiRoaster is a powerful pipeline automation platform. Here's how to get started:
                        </p>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                            {[
                                { num: 1, title: 'Create a Pipeline', desc: 'Go to Pipelines → Create New → Add stages' },
                                { num: 2, title: 'Run Execution', desc: 'Select your pipeline and click "Execute"' },
                                { num: 3, title: 'Monitor', desc: 'Track progress in Dashboard or Executions' },
                                { num: 4, title: 'Optimize', desc: 'Check AI Insights for recommendations' },
                            ].map((step) => (
                                <div key={step.num} className="flex items-start gap-2 p-3 rounded-lg bg-white/[0.02] border border-white/5">
                                    <span className="w-5 h-5 rounded bg-white/10 flex items-center justify-center text-[10px] font-bold text-white/60 flex-shrink-0">
                                        {step.num}
                                    </span>
                                    <div>
                                        <p className="text-xs font-medium text-white/70">{step.title}</p>
                                        <p className="text-[10px] text-white/40">{step.desc}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </Card>

            {/* Section Documentation */}
            <div>
                <h2 className="text-lg font-semibold text-white mb-4">Section Guide</h2>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {sections.map((section) => (
                        <DocSection key={section.title} {...section} />
                    ))}
                </div>
            </div>

            {/* External Resources */}
            <Card className="p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Additional Resources</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <a
                        href="#"
                        className="flex items-center gap-3 p-4 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                    >
                        <ExternalLink className="w-5 h-5 text-white/50" />
                        <span className="text-white/70">API Documentation</span>
                    </a>
                    <a
                        href="#"
                        className="flex items-center gap-3 p-4 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                    >
                        <ExternalLink className="w-5 h-5 text-white/50" />
                        <span className="text-white/70">Video Tutorials</span>
                    </a>
                    <a
                        href="#"
                        className="flex items-center gap-3 p-4 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                    >
                        <ExternalLink className="w-5 h-5 text-white/50" />
                        <span className="text-white/70">Community Forum</span>
                    </a>
                </div>
            </Card>
        </div>
    );
}
