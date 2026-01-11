import { create } from 'zustand';
import type { Pipeline, PipelineExecution } from '@/types/pipeline';
import { mockPipelines, mockExecutions } from '@/lib/mockData';

interface PipelineState {
    pipelines: Pipeline[];
    executions: PipelineExecution[];
    selectedPipelineId: string | null;
    isLoading: boolean;
    error: string | null;

    // Actions
    setPipelines: (pipelines: Pipeline[]) => void;
    setExecutions: (executions: PipelineExecution[]) => void;
    selectPipeline: (id: string | null) => void;
    updatePipelineStatus: (id: string, status: Pipeline['status'], progress: number) => void;
    setLoading: (loading: boolean) => void;
    setError: (error: string | null) => void;
}

export const usePipelineStore = create<PipelineState>((set) => ({
    pipelines: mockPipelines,
    executions: mockExecutions,
    selectedPipelineId: null,
    isLoading: false,
    error: null,

    setPipelines: (pipelines) => set({ pipelines }),

    setExecutions: (executions) => set({ executions }),

    selectPipeline: (id) => set({ selectedPipelineId: id }),

    updatePipelineStatus: (id, status, progress) =>
        set((state) => ({
            pipelines: state.pipelines.map((p) =>
                p.id === id ? { ...p, status, progress } : p
            ),
        })),

    setLoading: (isLoading) => set({ isLoading }),

    setError: (error) => set({ error }),
}));
