import { useState } from 'react';
import { X, Plus, Trash2 } from 'lucide-react';
import { usePipelines } from '@/hooks/usePipelines';

interface CreatePipelineModalProps {
    isOpen: boolean;
    onClose: () => void;
}

interface Stage {
    name: string;
    order: number;
}

export function CreatePipelineModal({ isOpen, onClose }: CreatePipelineModalProps) {
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [stages, setStages] = useState<Stage[]>([{ name: '', order: 0 }]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const { createPipeline } = usePipelines();

    const handleAddStage = () => {
        setStages([...stages, { name: '', order: stages.length }]);
    };

    const handleRemoveStage = (index: number) => {
        setStages(stages.filter((_, i) => i !== index));
    };

    const handleStageChange = (index: number, value: string) => {
        const newStages = [...stages];
        newStages[index].name = value;
        setStages(newStages);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        // Validation
        if (!name.trim()) {
            setError('Pipeline name is required');
            return;
        }

        const validStages = stages.filter(s => s.name.trim());
        if (validStages.length === 0) {
            setError('At least one stage is required');
            return;
        }

        setLoading(true);

        const { error: createError } = await createPipeline({
            name: name.trim(),
            description: description.trim() || null,
            config: {
                stages: validStages.map((s, i) => ({
                    name: s.name.trim(),
                    order: i,
                })),
            },
        } as any);

        setLoading(false);

        if (createError) {
            setError(createError);
        } else {
            // Reset form
            setName('');
            setDescription('');
            setStages([{ name: '', order: 0 }]);
            onClose();
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
            <div className="bg-[hsl(var(--card))] border border-white/10 rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto m-4">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-white/10">
                    <h2 className="text-xl font-semibold text-white">Create New Pipeline</h2>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-white/5 rounded transition-colors"
                    >
                        <X className="w-5 h-5 text-white/70" />
                    </button>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit} className="p-6 space-y-6">
                    {/* Error Message */}
                    {error && (
                        <div className="p-3 bg-red-500/10 border border-red-500/20 rounded text-red-400 text-sm">
                            {error}
                        </div>
                    )}

                    {/* Pipeline Name */}
                    <div>
                        <label className="block text-sm font-medium text-white/70 mb-2">
                            Pipeline Name *
                        </label>
                        <input
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded text-white focus:outline-none focus:border-white/20 transition-colors"
                            placeholder="My Data Pipeline"
                            required
                        />
                    </div>

                    {/* Description */}
                    <div>
                        <label className="block text-sm font-medium text-white/70 mb-2">
                            Description
                        </label>
                        <textarea
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded text-white focus:outline-none focus:border-white/20 transition-colors resize-none"
                            placeholder="Describe what this pipeline does..."
                            rows={3}
                        />
                    </div>

                    {/* Stages */}
                    <div>
                        <div className="flex items-center justify-between mb-3">
                            <label className="block text-sm font-medium text-white/70">
                                Pipeline Stages *
                            </label>
                            <button
                                type="button"
                                onClick={handleAddStage}
                                className="flex items-center gap-2 px-3 py-1.5 bg-white/10 hover:bg-white/20 text-white text-sm rounded transition-colors"
                            >
                                <Plus className="w-4 h-4" />
                                Add Stage
                            </button>
                        </div>

                        <div className="space-y-3">
                            {stages.map((stage, index) => (
                                <div key={index} className="flex items-center gap-3">
                                    <span className="text-white/50 text-sm w-8">{index + 1}.</span>
                                    <input
                                        type="text"
                                        value={stage.name}
                                        onChange={(e) => handleStageChange(index, e.target.value)}
                                        className="flex-1 px-4 py-2 bg-white/5 border border-white/10 rounded text-white focus:outline-none focus:border-white/20 transition-colors"
                                        placeholder={`Stage ${index + 1} name`}
                                    />
                                    {stages.length > 1 && (
                                        <button
                                            type="button"
                                            onClick={() => handleRemoveStage(index)}
                                            className="p-2 hover:bg-red-500/10 text-red-400 rounded transition-colors"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center justify-end gap-3 pt-4 border-t border-white/10">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="px-4 py-2 bg-white/90 hover:bg-white text-black rounded font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? 'Creating...' : 'Create Pipeline'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
