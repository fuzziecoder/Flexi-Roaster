import { useState } from 'react';
import { Card } from '@/components/common';
import { toast } from '@/components/common/Toast';
import {
    Plug,
    Database,
    Cloud,
    Mail,
    MessageSquare,
    Link2,
    Plus,
    Check,
    Settings,
    ExternalLink,
    Search,
    X,
} from 'lucide-react';

interface Integration {
    id: string;
    name: string;
    description: string;
    icon: React.ElementType;
    category: 'database' | 'cloud' | 'notification' | 'api';
    isConnected: boolean;
    lastSync?: string;
}

// Available integrations - these are configuration options
const availableIntegrations: Integration[] = [
    // Databases
    { id: 'postgresql', name: 'PostgreSQL', description: 'Connect to PostgreSQL databases', icon: Database, category: 'database', isConnected: false },
    { id: 'mysql', name: 'MySQL', description: 'Connect to MySQL databases', icon: Database, category: 'database', isConnected: false },
    { id: 'mongodb', name: 'MongoDB', description: 'Connect to MongoDB clusters', icon: Database, category: 'database', isConnected: false },
    { id: 'supabase', name: 'Supabase', description: 'Connect to Supabase backend', icon: Database, category: 'database', isConnected: false },

    // Cloud Storage
    { id: 'aws-s3', name: 'AWS S3', description: 'Amazon S3 bucket storage', icon: Cloud, category: 'cloud', isConnected: false },
    { id: 'gcs', name: 'Google Cloud Storage', description: 'GCS bucket storage', icon: Cloud, category: 'cloud', isConnected: false },
    { id: 'azure-blob', name: 'Azure Blob', description: 'Azure Blob storage', icon: Cloud, category: 'cloud', isConnected: false },

    // Notifications
    { id: 'slack', name: 'Slack', description: 'Send notifications to Slack', icon: MessageSquare, category: 'notification', isConnected: false },
    { id: 'email', name: 'Email (SMTP)', description: 'Send email notifications', icon: Mail, category: 'notification', isConnected: false },
    { id: 'discord', name: 'Discord', description: 'Send notifications to Discord', icon: MessageSquare, category: 'notification', isConnected: false },

    // APIs
    { id: 'rest-api', name: 'REST API', description: 'Custom REST API endpoints', icon: Link2, category: 'api', isConnected: false },
    { id: 'webhook', name: 'Webhooks', description: 'Outgoing webhook calls', icon: Link2, category: 'api', isConnected: false },
];

const categoryLabels = {
    database: 'Databases',
    cloud: 'Cloud Storage',
    notification: 'Notifications',
    api: 'APIs & Webhooks',
};

// Connection Modal
function ConnectionModal({
    integration,
    onClose,
    onConnect
}: {
    integration: Integration | null;
    onClose: () => void;
    onConnect: (id: string, credentials: Record<string, string>) => void;
}) {
    const [credentials, setCredentials] = useState<Record<string, string>>({});

    if (!integration) return null;

    const getFields = () => {
        switch (integration.category) {
            case 'database':
                return [
                    { key: 'host', label: 'Host', placeholder: 'localhost' },
                    { key: 'port', label: 'Port', placeholder: '5432' },
                    { key: 'database', label: 'Database', placeholder: 'mydb' },
                    { key: 'username', label: 'Username', placeholder: 'user' },
                    { key: 'password', label: 'Password', placeholder: '••••••••', type: 'password' },
                ];
            case 'cloud':
                return [
                    { key: 'accessKey', label: 'Access Key', placeholder: 'AKIA...' },
                    { key: 'secretKey', label: 'Secret Key', placeholder: '••••••••', type: 'password' },
                    { key: 'bucket', label: 'Bucket Name', placeholder: 'my-bucket' },
                    { key: 'region', label: 'Region', placeholder: 'us-east-1' },
                ];
            case 'notification':
                if (integration.id === 'slack') {
                    return [
                        { key: 'webhookUrl', label: 'Webhook URL', placeholder: 'https://hooks.slack.com/...' },
                        { key: 'channel', label: 'Default Channel', placeholder: '#general' },
                    ];
                }
                return [
                    { key: 'host', label: 'SMTP Host', placeholder: 'smtp.gmail.com' },
                    { key: 'port', label: 'Port', placeholder: '587' },
                    { key: 'username', label: 'Username', placeholder: 'email@example.com' },
                    { key: 'password', label: 'Password', placeholder: '••••••••', type: 'password' },
                ];
            case 'api':
                return [
                    { key: 'baseUrl', label: 'Base URL', placeholder: 'https://api.example.com' },
                    { key: 'apiKey', label: 'API Key', placeholder: 'your-api-key', type: 'password' },
                ];
            default:
                return [];
        }
    };

    const fields = getFields();

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        const isValid = fields.every(f => credentials[f.key]);
        if (!isValid) {
            toast.error('Please fill all fields');
            return;
        }
        onConnect(integration.id, credentials);
        setCredentials({});
        onClose();
    };

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-[#1a1a1a] border border-white/10 rounded-xl w-full max-w-md shadow-2xl">
                <div className="flex items-center justify-between p-4 border-b border-white/10">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-white/10">
                            <integration.icon className="w-5 h-5 text-white/60" />
                        </div>
                        <div>
                            <h2 className="text-lg font-semibold text-white">Connect {integration.name}</h2>
                            <p className="text-xs text-white/40">{integration.description}</p>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-1 hover:bg-white/10 rounded">
                        <X className="w-5 h-5 text-white/60" />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-4 space-y-4">
                    {fields.map(field => (
                        <div key={field.key}>
                            <label className="block text-xs text-white/50 mb-1.5">{field.label}</label>
                            <input
                                type={field.type || 'text'}
                                value={credentials[field.key] || ''}
                                onChange={(e) => setCredentials(prev => ({ ...prev, [field.key]: e.target.value }))}
                                placeholder={field.placeholder}
                                className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder-white/30 focus:outline-none focus:border-white/20"
                            />
                        </div>
                    ))}

                    <div className="flex gap-3 pt-2">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 px-4 py-2 border border-white/10 text-white/60 rounded-lg hover:bg-white/5 transition-colors text-sm"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="flex-1 px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/15 transition-colors text-sm font-medium"
                        >
                            Connect
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

// Configuration Modal for connected integrations
function ConfigurationModal({
    integration,
    onClose,
    onDisconnect
}: {
    integration: Integration | null;
    onClose: () => void;
    onDisconnect: (id: string) => void;
}) {
    if (!integration) return null;

    const handleDisconnect = () => {
        onDisconnect(integration.id);
        onClose();
    };

    const getConfigOptions = () => {
        switch (integration.id) {
            case 'supabase':
                return [
                    { label: 'Connection Status', value: 'Active', type: 'status' },
                    { label: 'Database URL', value: 'Connected via app configuration', type: 'readonly' },
                    { label: 'API Key', value: '••••••••••••••••', type: 'readonly' },
                    { label: 'Auto-sync', value: true, type: 'toggle' },
                ];
            default:
                return [
                    { label: 'Connection Status', value: 'Active', type: 'status' },
                    { label: 'Last Sync', value: integration.lastSync ? new Date(integration.lastSync).toLocaleString() : 'Never', type: 'readonly' },
                ];
        }
    };

    const configOptions = getConfigOptions();

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-[#1a1a1a] border border-white/10 rounded-xl w-full max-w-md shadow-2xl">
                <div className="flex items-center justify-between p-4 border-b border-white/10">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-white/10">
                            <integration.icon className="w-5 h-5 text-white/60" />
                        </div>
                        <div>
                            <h2 className="text-lg font-semibold text-white">{integration.name} Settings</h2>
                            <div className="flex items-center gap-1.5 mt-0.5">
                                <div className="w-2 h-2 rounded-full bg-emerald-500" />
                                <span className="text-xs text-emerald-400">Connected</span>
                            </div>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-1 hover:bg-white/10 rounded">
                        <X className="w-5 h-5 text-white/60" />
                    </button>
                </div>

                <div className="p-4 space-y-4">
                    {configOptions.map((option, idx) => (
                        <div key={idx} className="flex items-center justify-between">
                            <span className="text-sm text-white/60">{option.label}</span>
                            {option.type === 'status' ? (
                                <span className="text-sm text-emerald-400 font-medium">{option.value}</span>
                            ) : option.type === 'toggle' ? (
                                <div className="w-10 h-5 bg-emerald-600 rounded-full relative cursor-pointer">
                                    <div className="absolute right-0.5 top-0.5 w-4 h-4 bg-white rounded-full" />
                                </div>
                            ) : (
                                <span className="text-sm text-white/40">{option.value}</span>
                            )}
                        </div>
                    ))}

                    <div className="pt-4 border-t border-white/10">
                        <p className="text-xs text-white/40 mb-3">
                            {integration.id === 'supabase'
                                ? 'Supabase is configured via environment variables in your application settings.'
                                : 'Manage connection settings for this integration.'}
                        </p>
                    </div>

                    <div className="flex gap-3">
                        <button
                            onClick={onClose}
                            className="flex-1 px-4 py-2 border border-white/10 text-white/60 rounded-lg hover:bg-white/5 transition-colors text-sm"
                        >
                            Close
                        </button>
                        {integration.id !== 'supabase' && (
                            <button
                                onClick={handleDisconnect}
                                className="flex-1 px-4 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors text-sm font-medium"
                            >
                                Disconnect
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

function IntegrationCard({
    integration,
    onConnect,
    onConfigure
}: {
    integration: Integration;
    onConnect: (integration: Integration) => void;
    onConfigure: (integration: Integration) => void;
}) {
    const Icon = integration.icon;

    return (
        <div className="p-4 rounded-lg bg-white/[0.02] border border-white/5 hover:border-white/10 transition-all group">
            <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                    <div className={`p-2.5 rounded-lg ${integration.isConnected ? 'bg-white/10' : 'bg-white/5'}`}>
                        <Icon className={`w-5 h-5 ${integration.isConnected ? 'text-white/60' : 'text-white/30'}`} />
                    </div>
                    <div>
                        <h3 className="text-sm font-medium text-white/90">{integration.name}</h3>
                        <p className="text-xs text-white/40">{integration.description}</p>
                    </div>
                </div>
                {integration.isConnected && (
                    <div className="flex items-center gap-1 px-2 py-0.5 bg-white/10 rounded text-[10px] text-white/60">
                        <Check className="w-3 h-3" />
                        Connected
                    </div>
                )}
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-white/5">
                <span className="text-[10px] text-white/30">
                    {integration.isConnected
                        ? integration.lastSync
                            ? `Last sync: ${new Date(integration.lastSync).toLocaleTimeString()}`
                            : 'Connected'
                        : 'Not configured'
                    }
                </span>
                <button
                    onClick={() => integration.isConnected ? onConfigure(integration) : onConnect(integration)}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium transition-colors ${integration.isConnected
                        ? 'bg-white/5 hover:bg-white/10 text-white/60'
                        : 'bg-white/10 hover:bg-white/15 text-white'
                        }`}>
                    {integration.isConnected ? (
                        <>
                            <Settings className="w-3 h-3" />
                            Configure
                        </>
                    ) : (
                        <>
                            <Plus className="w-3 h-3" />
                            Connect
                        </>
                    )}
                </button>
            </div>
        </div>
    );
}

export function IntegrationsPage() {
    const [filter, setFilter] = useState<'all' | 'database' | 'cloud' | 'notification' | 'api'>('all');
    const [search, setSearch] = useState('');
    const [connectingIntegration, setConnectingIntegration] = useState<Integration | null>(null);
    const [configuringIntegration, setConfiguringIntegration] = useState<Integration | null>(null);
    const [integrations, setIntegrations] = useState<Integration[]>(availableIntegrations);

    const handleConnect = (id: string, _credentials: Record<string, string>) => {
        setIntegrations(prev => prev.map(i =>
            i.id === id
                ? { ...i, isConnected: true, lastSync: new Date().toISOString() }
                : i
        ));
        const integration = integrations.find(i => i.id === id);
        toast.success('Connected', `${integration?.name} has been connected`);
    };

    const handleConfigure = (integration: Integration) => {
        setConfiguringIntegration(integration);
    };

    const handleDisconnect = (id: string) => {
        setIntegrations(prev => prev.map(i =>
            i.id === id
                ? { ...i, isConnected: false, lastSync: undefined }
                : i
        ));
        const integration = integrations.find(i => i.id === id);
        toast.info('Disconnected', `${integration?.name} has been disconnected`);
    };

    const filteredIntegrations = integrations.filter(i => {
        const matchesFilter = filter === 'all' || i.category === filter;
        const matchesSearch = i.name.toLowerCase().includes(search.toLowerCase()) ||
            i.description.toLowerCase().includes(search.toLowerCase());
        return matchesFilter && matchesSearch;
    });

    const connectedCount = integrations.filter(i => i.isConnected).length;

    return (
        <div className="space-y-6">
            {/* Connection Modal */}
            <ConnectionModal
                integration={connectingIntegration}
                onClose={() => setConnectingIntegration(null)}
                onConnect={handleConnect}
            />

            {/* Configuration Modal */}
            <ConfigurationModal
                integration={configuringIntegration}
                onClose={() => setConfiguringIntegration(null)}
                onDisconnect={handleDisconnect}
            />

            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">Integrations</h1>
                    <p className="text-white/50 text-sm mt-1">Connect your pipelines to external services and data sources</p>
                </div>
                <button className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/15 text-white rounded-lg transition-colors">
                    <ExternalLink className="w-4 h-4" />
                    <span className="text-sm font-medium">Request Integration</span>
                </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <Card className="p-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-white/5">
                            <Plug className="w-4 h-4 text-white/40" />
                        </div>
                        <div>
                            <p className="text-xl font-bold text-white/90">{integrations.length}</p>
                            <p className="text-xs text-white/40">Available</p>
                        </div>
                    </div>
                </Card>
                <Card className="p-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-white/5">
                            <Check className="w-4 h-4 text-white/40" />
                        </div>
                        <div>
                            <p className="text-xl font-bold text-white/90">{connectedCount}</p>
                            <p className="text-xs text-white/40">Connected</p>
                        </div>
                    </div>
                </Card>
                <Card className="p-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-white/5">
                            <Database className="w-4 h-4 text-white/40" />
                        </div>
                        <div>
                            <p className="text-xl font-bold text-white/90">{integrations.filter(i => i.category === 'database').length}</p>
                            <p className="text-xs text-white/40">Databases</p>
                        </div>
                    </div>
                </Card>
                <Card className="p-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-white/5">
                            <Cloud className="w-4 h-4 text-white/40" />
                        </div>
                        <div>
                            <p className="text-xl font-bold text-white/90">{integrations.filter(i => i.category === 'cloud').length}</p>
                            <p className="text-xs text-white/40">Cloud Storage</p>
                        </div>
                    </div>
                </Card>
            </div>

            {/* Search and Filter */}
            <div className="flex items-center gap-4">
                <div className="relative flex-1 max-w-xs">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                    <input
                        type="text"
                        placeholder="Search integrations..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full pl-9 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder-white/30 focus:outline-none focus:border-white/20"
                    />
                </div>
                <div className="flex items-center gap-2">
                    {(['all', 'database', 'cloud', 'notification', 'api'] as const).map(cat => (
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

            {/* Integrations Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredIntegrations.map(integration => (
                    <IntegrationCard
                        key={integration.id}
                        integration={integration}
                        onConnect={setConnectingIntegration}
                        onConfigure={handleConfigure}
                    />
                ))}
            </div>

            {filteredIntegrations.length === 0 && (
                <Card className="p-12 text-center">
                    <Plug className="w-12 h-12 text-white/20 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-white/60 mb-2">No integrations found</h3>
                    <p className="text-sm text-white/40">Try adjusting your search or filter</p>
                </Card>
            )}
        </div>
    );
}
