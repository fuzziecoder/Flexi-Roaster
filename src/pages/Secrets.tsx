import { useState } from 'react';
import { Card } from '@/components/common';
import { toast } from '@/components/common/Toast';
import {
    Key,
    Lock,
    Eye,
    EyeOff,
    Plus,
    Trash2,
    Edit2,
    Copy,
    Check,
    Search,
    Shield,
    X,
} from 'lucide-react';

interface Variable {
    id: string;
    key: string;
    value: string;
    isSecret: boolean;
    description?: string;
    usedBy: string[];
    createdAt: string;
    updatedAt: string;
}

// Add Variable Modal
function AddVariableModal({
    isOpen,
    onClose,
    onSave
}: {
    isOpen: boolean;
    onClose: () => void;
    onSave: (variable: Omit<Variable, 'id' | 'createdAt' | 'updatedAt'>) => void;
}) {
    const [key, setKey] = useState('');
    const [value, setValue] = useState('');
    const [description, setDescription] = useState('');
    const [isSecret, setIsSecret] = useState(false);

    if (!isOpen) return null;

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!key || !value) {
            toast.error('Please fill required fields');
            return;
        }

        if (!/^[A-Z_][A-Z0-9_]*$/.test(key)) {
            toast.error('Key must be UPPER_SNAKE_CASE');
            return;
        }

        onSave({
            key,
            value,
            description,
            isSecret,
            usedBy: [],
        });

        // Reset form
        setKey('');
        setValue('');
        setDescription('');
        setIsSecret(false);
        onClose();
    };

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-[#1a1a1a] border border-white/10 rounded-xl w-full max-w-md shadow-2xl">
                <div className="flex items-center justify-between p-4 border-b border-white/10">
                    <h2 className="text-lg font-semibold text-white">Add Variable</h2>
                    <button onClick={onClose} className="p-1 hover:bg-white/10 rounded">
                        <X className="w-5 h-5 text-white/60" />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-4 space-y-4">
                    <div>
                        <label className="block text-xs text-white/50 mb-1.5">Variable Key *</label>
                        <input
                            type="text"
                            value={key}
                            onChange={(e) => setKey(e.target.value.toUpperCase())}
                            placeholder="e.g., DATABASE_URL"
                            className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white font-mono placeholder-white/30 focus:outline-none focus:border-white/20"
                        />
                        <p className="text-[10px] text-white/30 mt-1">Use UPPER_SNAKE_CASE format</p>
                    </div>

                    <div>
                        <label className="block text-xs text-white/50 mb-1.5">Value *</label>
                        <input
                            type={isSecret ? 'password' : 'text'}
                            value={value}
                            onChange={(e) => setValue(e.target.value)}
                            placeholder="Enter value..."
                            className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white font-mono placeholder-white/30 focus:outline-none focus:border-white/20"
                        />
                    </div>

                    <div>
                        <label className="block text-xs text-white/50 mb-1.5">Description (optional)</label>
                        <input
                            type="text"
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            placeholder="What is this variable used for?"
                            className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder-white/30 focus:outline-none focus:border-white/20"
                        />
                    </div>

                    <div className="flex items-center gap-3 p-3 bg-white/5 rounded-lg">
                        <button
                            type="button"
                            onClick={() => setIsSecret(!isSecret)}
                            className={`relative w-10 h-5 rounded-full transition-colors ${isSecret ? 'bg-white/20' : 'bg-white/10'
                                }`}
                        >
                            <span className={`absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white transition-transform ${isSecret ? 'translate-x-5' : ''
                                }`} />
                        </button>
                        <div className="flex-1">
                            <p className="text-sm text-white/80">Mark as Secret</p>
                            <p className="text-[10px] text-white/40">Value will be encrypted and hidden</p>
                        </div>
                        {isSecret ? (
                            <Lock className="w-4 h-4 text-white/40" />
                        ) : (
                            <Key className="w-4 h-4 text-white/40" />
                        )}
                    </div>

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
                            Add Variable
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

function VariableRow({ variable, onCopy, onDelete }: {
    variable: Variable;
    onCopy: (text: string) => void;
    onDelete: (id: string) => void;
}) {
    const [showValue, setShowValue] = useState(false);
    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        onCopy(variable.key);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const displayValue = variable.isSecret && !showValue
        ? '••••••••••••••••'
        : variable.value;

    return (
        <div className="flex items-center gap-4 p-4 bg-white/[0.02] border border-white/5 rounded-lg hover:border-white/10 transition-all group">
            <div className="p-2 rounded-lg bg-white/5">
                {variable.isSecret ? (
                    <Lock className="w-4 h-4 text-white/40" />
                ) : (
                    <Key className="w-4 h-4 text-white/40" />
                )}
            </div>

            <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                    <code className="text-sm font-mono text-white/90">{variable.key}</code>
                    {variable.isSecret && (
                        <span className="px-1.5 py-0.5 bg-white/10 rounded text-[9px] text-white/50">SECRET</span>
                    )}
                </div>
                <p className="text-xs text-white/40 truncate">{variable.description || 'No description'}</p>
            </div>

            <div className="flex items-center gap-2 font-mono text-xs text-white/50 min-w-[200px]">
                <span className="truncate">{displayValue}</span>
                {variable.isSecret && (
                    <button
                        onClick={() => setShowValue(!showValue)}
                        className="p-1 hover:bg-white/10 rounded"
                    >
                        {showValue ? (
                            <EyeOff className="w-3.5 h-3.5 text-white/40" />
                        ) : (
                            <Eye className="w-3.5 h-3.5 text-white/40" />
                        )}
                    </button>
                )}
            </div>

            <div className="text-xs text-white/30 min-w-[80px]">
                {variable.usedBy.length} pipeline{variable.usedBy.length !== 1 ? 's' : ''}
            </div>

            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                    onClick={handleCopy}
                    className="p-1.5 hover:bg-white/10 rounded"
                    title="Copy key name"
                >
                    {copied ? (
                        <Check className="w-3.5 h-3.5 text-white/60" />
                    ) : (
                        <Copy className="w-3.5 h-3.5 text-white/40" />
                    )}
                </button>
                <button className="p-1.5 hover:bg-white/10 rounded" title="Edit">
                    <Edit2 className="w-3.5 h-3.5 text-white/40" />
                </button>
                <button
                    onClick={() => onDelete(variable.id)}
                    className="p-1.5 hover:bg-white/10 rounded"
                    title="Delete"
                >
                    <Trash2 className="w-3.5 h-3.5 text-white/40" />
                </button>
            </div>
        </div>
    );
}

export function SecretsPage() {
    const [search, setSearch] = useState('');
    const [filter, setFilter] = useState<'all' | 'secrets' | 'variables'>('all');
    const [showAddModal, setShowAddModal] = useState(false);
    const [variables, setVariables] = useState<Variable[]>([]);

    const handleSaveVariable = (variableData: Omit<Variable, 'id' | 'createdAt' | 'updatedAt'>) => {
        const newVariable: Variable = {
            ...variableData,
            id: `var-${Date.now()}`,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
        };
        setVariables(prev => [newVariable, ...prev]);
        toast.success('Variable added', `${variableData.key} has been created`);
    };

    const handleDeleteVariable = (id: string) => {
        setVariables(prev => prev.filter(v => v.id !== id));
        toast.success('Variable deleted');
    };

    const handleCopy = (text: string) => {
        navigator.clipboard.writeText(text);
        toast.info('Copied to clipboard');
    };

    const filteredVariables = variables.filter(v => {
        const matchesFilter = filter === 'all' ||
            (filter === 'secrets' && v.isSecret) ||
            (filter === 'variables' && !v.isSecret);
        const matchesSearch = v.key.toLowerCase().includes(search.toLowerCase()) ||
            (v.description?.toLowerCase().includes(search.toLowerCase()) ?? false);
        return matchesFilter && matchesSearch;
    });

    const secretCount = variables.filter(v => v.isSecret).length;
    const variableCount = variables.filter(v => !v.isSecret).length;

    return (
        <div className="space-y-6">
            {/* Add Variable Modal */}
            <AddVariableModal
                isOpen={showAddModal}
                onClose={() => setShowAddModal(false)}
                onSave={handleSaveVariable}
            />

            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">Variables & Secrets</h1>
                    <p className="text-white/50 text-sm mt-1">Manage environment variables and encrypted secrets for your pipelines</p>
                </div>
                <button
                    onClick={() => setShowAddModal(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/15 text-white rounded-lg transition-colors"
                >
                    <Plus className="w-4 h-4" />
                    <span className="text-sm font-medium">Add Variable</span>
                </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <Card className="p-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-white/5">
                            <Key className="w-4 h-4 text-white/40" />
                        </div>
                        <div>
                            <p className="text-xl font-bold text-white/90">{variables.length}</p>
                            <p className="text-xs text-white/40">Total Variables</p>
                        </div>
                    </div>
                </Card>
                <Card className="p-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-white/5">
                            <Lock className="w-4 h-4 text-white/40" />
                        </div>
                        <div>
                            <p className="text-xl font-bold text-white/90">{secretCount}</p>
                            <p className="text-xs text-white/40">Secrets</p>
                        </div>
                    </div>
                </Card>
                <Card className="p-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-white/5">
                            <Shield className="w-4 h-4 text-white/40" />
                        </div>
                        <div>
                            <p className="text-xl font-bold text-white/90">AES-256</p>
                            <p className="text-xs text-white/40">Encryption</p>
                        </div>
                    </div>
                </Card>
                <Card className="p-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-white/5">
                            <Key className="w-4 h-4 text-white/40" />
                        </div>
                        <div>
                            <p className="text-xl font-bold text-white/90">{variableCount}</p>
                            <p className="text-xs text-white/40">Plain Variables</p>
                        </div>
                    </div>
                </Card>
            </div>

            {/* Warning Banner */}
            <div className="flex items-center gap-3 p-3 bg-white/5 border border-white/10 rounded-lg">
                <Shield className="w-5 h-5 text-white/50 flex-shrink-0" />
                <p className="text-xs text-white/50">
                    Secrets are encrypted at rest and in transit. Never expose secret values in logs or outputs.
                </p>
            </div>

            {/* Search and Filter */}
            <div className="flex items-center gap-4">
                <div className="relative flex-1 max-w-xs">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                    <input
                        type="text"
                        placeholder="Search variables..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full pl-9 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder-white/30 focus:outline-none focus:border-white/20"
                    />
                </div>
                <div className="flex items-center gap-2">
                    {(['all', 'secrets', 'variables'] as const).map(f => (
                        <button
                            key={f}
                            onClick={() => setFilter(f)}
                            className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-colors ${filter === f
                                    ? 'bg-white/10 text-white'
                                    : 'text-white/40 hover:text-white/60 hover:bg-white/5'
                                }`}
                        >
                            {f.charAt(0).toUpperCase() + f.slice(1)}
                        </button>
                    ))}
                </div>
            </div>

            {/* Variables List */}
            {filteredVariables.length > 0 ? (
                <div className="space-y-2">
                    {filteredVariables.map(variable => (
                        <VariableRow
                            key={variable.id}
                            variable={variable}
                            onCopy={handleCopy}
                            onDelete={handleDeleteVariable}
                        />
                    ))}
                </div>
            ) : (
                <Card className="p-12 text-center">
                    <Key className="w-12 h-12 text-white/20 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-white/60 mb-2">No variables yet</h3>
                    <p className="text-sm text-white/40 mb-4">Add your first variable or secret to securely store configuration</p>
                    <button
                        onClick={() => setShowAddModal(true)}
                        className="px-4 py-2 bg-white/10 hover:bg-white/15 text-white rounded-lg transition-colors text-sm"
                    >
                        Add Variable
                    </button>
                </Card>
            )}
        </div>
    );
}
