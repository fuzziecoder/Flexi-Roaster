import { useState } from 'react';
import { Card } from '@/components/common';
import { useNavigate } from 'react-router-dom';
import {
    LayoutTemplate,
    Play,
    Star,
    Users,
    Clock,
    GitBranch,
    Search,
    Download,
    Zap,
    Database,
    Brain,
    FileText,
    BarChart3,
    Mail,
} from 'lucide-react';

interface Template {
    id: string;
    name: string;
    description: string;
    icon: React.ElementType;
    category: 'data' | 'ai' | 'integration' | 'reporting' | 'automation';
    stages: number;
    isOfficial: boolean;
}

// Static template catalog - not user data, just available templates
const templatesCatalog: Template[] = [
    { id: 'tpl-001', name: 'ETL Data Pipeline', description: 'Extract, Transform, Load data from multiple sources to a data warehouse', icon: Database, category: 'data', stages: 4, isOfficial: true },
    { id: 'tpl-002', name: 'ML Model Training', description: 'Complete pipeline for training and deploying ML models', icon: Brain, category: 'ai', stages: 5, isOfficial: true },
    { id: 'tpl-003', name: 'Daily Report Generator', description: 'Generate and email daily business reports automatically', icon: FileText, category: 'reporting', stages: 3, isOfficial: true },
    { id: 'tpl-004', name: 'API Data Sync', description: 'Sync data between APIs and databases periodically', icon: Zap, category: 'integration', stages: 4, isOfficial: true },
    { id: 'tpl-005', name: 'Log Analyzer', description: 'Process and analyze application logs for insights', icon: BarChart3, category: 'data', stages: 3, isOfficial: true },
    { id: 'tpl-006', name: 'Email Notifications', description: 'Send email notifications based on triggers and events', icon: Mail, category: 'automation', stages: 2, isOfficial: true },
];

const categoryLabels = {
    data: 'Data Processing',
    ai: 'AI & ML',
    integration: 'Integrations',
    reporting: 'Reporting',
    automation: 'Automation',
};

function TemplateCard({ template }: { template: Template }) {
    const navigate = useNavigate();
    const Icon = template.icon;

    return (
        <div className="p-4 rounded-lg bg-white/[0.02] border border-white/5 hover:border-white/10 transition-all group">
            <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-lg bg-white/10">
                        <Icon className="w-5 h-5 text-white/60" />
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <h3 className="text-sm font-medium text-white/90">{template.name}</h3>
                            {template.isOfficial && (
                                <span className="px-1.5 py-0.5 bg-white/10 rounded text-[9px] text-white/50">OFFICIAL</span>
                            )}
                        </div>
                        <p className="text-xs text-white/40">{categoryLabels[template.category]}</p>
                    </div>
                </div>
            </div>

            <p className="text-xs text-white/50 mb-4 line-clamp-2">{template.description}</p>

            <div className="flex items-center gap-4 text-[10px] text-white/40 mb-4">
                <div className="flex items-center gap-1">
                    <GitBranch className="w-3 h-3" />
                    {template.stages} stages
                </div>
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-white/5">
                <span className="text-[10px] text-white/30">FlexiRoaster</span>
                <button
                    onClick={() => navigate('/pipelines')}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-white/10 hover:bg-white/15 rounded text-xs font-medium text-white transition-colors"
                >
                    <Play className="w-3 h-3" />
                    Use Template
                </button>
            </div>
        </div>
    );
}

export function TemplatesPage() {
    const navigate = useNavigate();
    const [filter, setFilter] = useState<'all' | 'data' | 'ai' | 'integration' | 'reporting' | 'automation'>('all');
    const [search, setSearch] = useState('');

    const filteredTemplates = templatesCatalog.filter(t => {
        const matchesFilter = filter === 'all' || t.category === filter;
        const matchesSearch = t.name.toLowerCase().includes(search.toLowerCase()) ||
            t.description.toLowerCase().includes(search.toLowerCase());
        return matchesFilter && matchesSearch;
    });

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">Templates</h1>
                    <p className="text-white/50 text-sm mt-1">Pre-built pipeline templates to get you started quickly</p>
                </div>
                <button className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/15 text-white rounded-lg transition-colors">
                    <Download className="w-4 h-4" />
                    <span className="text-sm font-medium">Import Template</span>
                </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <Card className="p-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-white/5">
                            <LayoutTemplate className="w-4 h-4 text-white/40" />
                        </div>
                        <div>
                            <p className="text-xl font-bold text-white/90">{templatesCatalog.length}</p>
                            <p className="text-xs text-white/40">Templates</p>
                        </div>
                    </div>
                </Card>
                <Card className="p-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-white/5">
                            <Star className="w-4 h-4 text-white/40" />
                        </div>
                        <div>
                            <p className="text-xl font-bold text-white/90">{templatesCatalog.filter(t => t.isOfficial).length}</p>
                            <p className="text-xs text-white/40">Official</p>
                        </div>
                    </div>
                </Card>
                <Card className="p-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-white/5">
                            <Users className="w-4 h-4 text-white/40" />
                        </div>
                        <div>
                            <p className="text-xl font-bold text-white/90">Free</p>
                            <p className="text-xs text-white/40">All Templates</p>
                        </div>
                    </div>
                </Card>
                <Card className="p-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-white/5">
                            <Clock className="w-4 h-4 text-white/40" />
                        </div>
                        <div>
                            <p className="text-xl font-bold text-white/90">~5min</p>
                            <p className="text-xs text-white/40">Avg Setup</p>
                        </div>
                    </div>
                </Card>
            </div>

            {/* Quick Start Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div
                    className="p-4 rounded-lg border border-dashed border-white/10 bg-[hsl(var(--card))] cursor-pointer hover:bg-white/[0.02] transition-colors"
                    onClick={() => navigate('/pipelines')}
                >
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-white/5">
                            <Zap className="w-5 h-5 text-white/40" />
                        </div>
                        <div>
                            <h3 className="text-sm font-medium text-white/80">Quick Start</h3>
                            <p className="text-xs text-white/40">Create a simple data pipeline</p>
                        </div>
                    </div>
                </div>
                <div
                    className="p-4 rounded-lg border border-dashed border-white/10 bg-[hsl(var(--card))] cursor-pointer hover:bg-white/[0.02] transition-colors"
                    onClick={() => navigate('/pipelines')}
                >
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-white/5">
                            <Brain className="w-5 h-5 text-white/40" />
                        </div>
                        <div>
                            <h3 className="text-sm font-medium text-white/80">AI Starter</h3>
                            <p className="text-xs text-white/40">ML training pipeline template</p>
                        </div>
                    </div>
                </div>
                <div
                    className="p-4 rounded-lg border border-dashed border-white/10 bg-[hsl(var(--card))] cursor-pointer hover:bg-white/[0.02] transition-colors"
                    onClick={() => navigate('/pipelines')}
                >
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-white/5">
                            <Database className="w-5 h-5 text-white/40" />
                        </div>
                        <div>
                            <h3 className="text-sm font-medium text-white/80">ETL Starter</h3>
                            <p className="text-xs text-white/40">Basic ETL pipeline setup</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Search and Filter */}
            <div className="flex items-center gap-4">
                <div className="relative flex-1 max-w-xs">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                    <input
                        type="text"
                        placeholder="Search templates..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full pl-9 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder-white/30 focus:outline-none focus:border-white/20"
                    />
                </div>
                <div className="flex items-center gap-2 flex-wrap">
                    {(['all', 'data', 'ai', 'integration', 'reporting', 'automation'] as const).map(cat => (
                        <button
                            key={cat}
                            onClick={() => setFilter(cat)}
                            className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-colors ${filter === cat
                                ? 'bg-white/10 text-white'
                                : 'text-white/40 hover:text-white/60 hover:bg-white/5'
                                }`}
                        >
                            {cat === 'all' ? 'All' : categoryLabels[cat]}
                        </button>
                    ))}
                </div>
            </div>

            {/* Templates Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredTemplates.map(template => (
                    <TemplateCard key={template.id} template={template} />
                ))}
            </div>

            {filteredTemplates.length === 0 && (
                <Card className="p-12 text-center">
                    <LayoutTemplate className="w-12 h-12 text-white/20 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-white/60 mb-2">No templates found</h3>
                    <p className="text-sm text-white/40">Try adjusting your search or filter</p>
                </Card>
            )}
        </div>
    );
}
