import { useState } from 'react';
import { Card } from '@/components/common';
import { StatusBadge } from '@/components/common';
import { Plus, Search, MoreVertical, Trash2, Power } from 'lucide-react';
import { usePipelines } from '@/hooks/usePipelines';
import { CreatePipelineModal } from '@/components/modals';
import { formatRelativeTime } from '@/lib/utils';

export function PipelinesPage() {
    const { pipelines, loading, deletePipeline, togglePipelineStatus } = usePipelines();
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

    const filteredPipelines = pipelines.filter(p =>
        p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.description?.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const handleDelete = async (id: string) => {
        await deletePipeline(id);
        setDeleteConfirm(null);
    };

    const handleToggleStatus = async (id: string, currentStatus: boolean) => {
        await togglePipelineStatus(id, !currentStatus);
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-white/70">Loading pipelines...</div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">Pipelines</h1>
                    <p className="text-white/50 mt-1">{filteredPipelines.length} total pipelines</p>
                </div>
                <button
                    onClick={() => setShowCreateModal(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-white/90 hover:bg-white text-black rounded font-medium transition-colors"
                >
                    <Plus className="w-4 h-4" />
                    Create Pipeline
                </button>
            </div>

            {/* Search */}
            <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
                <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search pipelines..."
                    className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded text-white placeholder:text-white/40 focus:outline-none focus:border-white/20 transition-colors"
                />
            </div>

            {/* Pipelines Grid */}
            {filteredPipelines.length === 0 ? (
                <Card className="p-12 text-center">
                    <p className="text-white/50">
                        {searchQuery ? 'No pipelines found matching your search.' : 'No pipelines yet. Create your first pipeline!'}
                    </p>
                </Card>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {filteredPipelines.map((pipeline) => (
                        <Card key={pipeline.id} className="p-6 hover:border-white/20 transition-colors">
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex-1">
                                    <h3 className="text-lg font-semibold text-white mb-1">{pipeline.name}</h3>
                                    <p className="text-sm text-white/50 line-clamp-2">
                                        {pipeline.description || 'No description'}
                                    </p>
                                </div>
                                <div className="relative group">
                                    <button className="p-2 hover:bg-white/5 rounded transition-colors">
                                        <MoreVertical className="w-4 h-4 text-white/70" />
                                    </button>
                                    {/* Dropdown Menu */}
                                    <div className="absolute right-0 top-full mt-1 w-48 bg-[hsl(var(--card))] border border-white/10 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
                                        <button
                                            onClick={() => handleToggleStatus(pipeline.id, pipeline.is_active)}
                                            className="w-full flex items-center gap-3 px-4 py-2 hover:bg-white/5 text-white text-sm transition-colors"
                                        >
                                            <Power className="w-4 h-4" />
                                            {pipeline.is_active ? 'Deactivate' : 'Activate'}
                                        </button>
                                        <button
                                            onClick={() => setDeleteConfirm(pipeline.id)}
                                            className="w-full flex items-center gap-3 px-4 py-2 hover:bg-white/5 text-red-400 text-sm transition-colors"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                            Delete
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <div className="flex items-center justify-between text-sm">
                                <StatusBadge
                                    variant={pipeline.is_active ? 'success' : 'default'}
                                    label={pipeline.is_active ? 'Active' : 'Inactive'}
                                />
                                <span className="text-white/40">
                                    {formatRelativeTime(pipeline.created_at)}
                                </span>
                            </div>

                            {/* Delete Confirmation */}
                            {deleteConfirm === pipeline.id && (
                                <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded">
                                    <p className="text-sm text-red-400 mb-3">Delete this pipeline?</p>
                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => handleDelete(pipeline.id)}
                                            className="flex-1 px-3 py-1.5 bg-red-500 hover:bg-red-600 text-white text-sm rounded transition-colors"
                                        >
                                            Delete
                                        </button>
                                        <button
                                            onClick={() => setDeleteConfirm(null)}
                                            className="flex-1 px-3 py-1.5 bg-white/10 hover:bg-white/20 text-white text-sm rounded transition-colors"
                                        >
                                            Cancel
                                        </button>
                                    </div>
                                </div>
                            )}
                        </Card>
                    ))}
                </div>
            )}

            {/* Create Pipeline Modal */}
            <CreatePipelineModal
                isOpen={showCreateModal}
                onClose={() => setShowCreateModal(false)}
            />
        </div>
    );
}
