import { useState } from 'react';
import { X, Play } from 'lucide-react';
import { usePipelines } from '@/hooks/usePipelines';
import { useExecutions } from '@/hooks/useExecutions';

interface TriggerExecutionModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export function TriggerExecutionModal({ isOpen, onClose }: TriggerExecutionModalProps) {
    const [selectedPipelineId, setSelectedPipelineId] = useState('');
    const [parameters, setParameters] = useState('{}');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);
    const { pipelines } = usePipelines();
    const { triggerExecution } = useExecutions();

    const activePipelines = pipelines.filter(p => p.is_active);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setSuccess(false);

        if (!selectedPipelineId) {
            setError('Please select a pipeline');
            return;
        }

        // Validate JSON parameters
        let metadata = null;
        if (parameters.trim()) {
            try {
                metadata = JSON.parse(parameters);
            } catch (err) {
                setError('Invalid JSON parameters');
                return;
            }
        }

        setLoading(true);

        const { error: triggerError } = await triggerExecution(selectedPipelineId, metadata);

        setLoading(false);

        if (triggerError) {
            setError(triggerError);
        } else {
            setSuccess(true);
            setTimeout(() => {
                setSelectedPipelineId('');
                setParameters('{}');
                setSuccess(false);
                onClose();
            }, 1500);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
            <div className="bg-[hsl(var(--card))] border border-white/10 rounded-lg w-full max-w-lg m-4">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-white/10">
                    <div className="flex items-center gap-3">
                        <Play className="w-5 h-5 text-white/70" />
                        <h2 className="text-xl font-semibold text-white">Trigger Execution</h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-white/5 rounded transition-colors"
                    >
                        <X className="w-5 h-5 text-white/70" />
                    </button>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit} className="p-6 space-y-6">
                    {/* Success Message */}
                    {success && (
                        <div className="p-3 bg-green-500/10 border border-green-500/20 rounded text-green-400 text-sm">
                            ✓ Execution triggered successfully!
                        </div>
                    )}

                    {/* Error Message */}
                    {error && (
                        <div className="p-3 bg-red-500/10 border border-red-500/20 rounded text-red-400 text-sm">
                            {error}
                        </div>
                    )}

                    {/* Pipeline Selection */}
                    <div>
                        <label className="block text-sm font-medium text-white/70 mb-2">
                            Select Pipeline *
                        </label>
                        <select
                            value={selectedPipelineId}
                            onChange={(e) => setSelectedPipelineId(e.target.value)}
                            className="w-full px-4 py-2 bg-[hsl(var(--card))] border border-white/10 rounded text-white focus:outline-none focus:border-white/20 transition-colors [&>option]:bg-[hsl(var(--card))] [&>option]:text-white"
                            required
                        >
                            <option value="">Choose a pipeline...</option>
                            {activePipelines.map(pipeline => (
                                <option key={pipeline.id} value={pipeline.id}>
                                    {pipeline.name}
                                </option>
                            ))}
                        </select>
                        {activePipelines.length === 0 && (
                            <p className="text-xs text-white/40 mt-1">
                                No active pipelines available. Create one first!
                            </p>
                        )}
                    </div>

                    {/* Parameters */}
                    <div>
                        <label className="block text-sm font-medium text-white/70 mb-2">
                            Parameters (JSON)
                        </label>
                        <textarea
                            value={parameters}
                            onChange={(e) => setParameters(e.target.value)}
                            className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded text-white focus:outline-none focus:border-white/20 transition-colors font-mono text-sm resize-none"
                            placeholder='{"key": "value"}'
                            rows={4}
                        />
                        <p className="text-xs text-white/40 mt-1">
                            Optional: Provide execution parameters as JSON
                        </p>
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
                            disabled={loading || activePipelines.length === 0}
                            className="px-4 py-2 bg-white/90 hover:bg-white text-black rounded font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                        >
                            <Play className="w-4 h-4" />
                            {loading ? 'Triggering...' : 'Trigger Execution'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
