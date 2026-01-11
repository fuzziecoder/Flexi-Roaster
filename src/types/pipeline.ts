// Pipeline Types
export type PipelineStatus = 'running' | 'completed' | 'failed' | 'pending' | 'paused';

export interface Pipeline {
    id: string;
    name: string;
    description: string;
    status: PipelineStatus;
    progress: number;
    lastExecution: string;
    nextExecution?: string;
    stages: PipelineStage[];
    createdAt: string;
    updatedAt: string;
}

export interface PipelineStage {
    id: string;
    name: string;
    type: string;
    status: PipelineStatus;
    duration?: number;
    error?: string;
}

export interface PipelineExecution {
    id: string;
    pipelineId: string;
    pipelineName: string;
    status: PipelineStatus;
    startTime: string;
    endTime?: string;
    duration?: number;
    stagesCompleted: number;
    totalStages: number;
    error?: string;
}
