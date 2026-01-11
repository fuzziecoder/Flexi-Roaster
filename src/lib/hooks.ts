// React Query Hooks for API Integration
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { pipelinesApi, executionsApi, metricsApi, aiApi } from './apiService';

// Pipelines Hooks
export const usePipelines = () => {
    return useQuery({
        queryKey: ['pipelines'],
        queryFn: pipelinesApi.getAll,
        refetchInterval: 30000, // Refetch every 30 seconds
    });
};

export const usePipeline = (id: string) => {
    return useQuery({
        queryKey: ['pipeline', id],
        queryFn: () => pipelinesApi.getById(id),
        enabled: !!id,
    });
};

export const useCreatePipeline = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: pipelinesApi.create,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['pipelines'] });
        },
    });
};

export const useDeletePipeline = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: pipelinesApi.delete,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['pipelines'] });
        },
    });
};

// Executions Hooks
export const useExecutions = (limit = 50, offset = 0) => {
    return useQuery({
        queryKey: ['executions', limit, offset],
        queryFn: () => executionsApi.getAll(limit, offset),
        refetchInterval: 5000, // Refetch every 5 seconds for real-time updates
    });
};

export const useExecution = (id: string) => {
    return useQuery({
        queryKey: ['execution', id],
        queryFn: () => executionsApi.getById(id),
        enabled: !!id,
        refetchInterval: 2000, // Refetch every 2 seconds while running
    });
};

export const useCreateExecution = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ pipelineId, variables }: { pipelineId: string; variables?: any }) =>
            executionsApi.create(pipelineId, variables),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['executions'] });
        },
    });
};

export const useExecutionLogs = (id: string) => {
    return useQuery({
        queryKey: ['execution-logs', id],
        queryFn: () => executionsApi.getLogs(id),
        enabled: !!id,
        refetchInterval: 3000,
    });
};

// Metrics Hooks
export const useMetrics = () => {
    return useQuery({
        queryKey: ['metrics'],
        queryFn: metricsApi.getCurrent,
        refetchInterval: 10000, // Refetch every 10 seconds
    });
};

export const useMetricsHistory = (hours = 24) => {
    return useQuery({
        queryKey: ['metrics-history', hours],
        queryFn: () => metricsApi.getHistory(hours),
        refetchInterval: 60000, // Refetch every minute
    });
};

// AI Insights Hooks
export const useAIInsights = () => {
    return useQuery({
        queryKey: ['ai-insights'],
        queryFn: aiApi.getInsights,
        refetchInterval: 30000, // Refetch every 30 seconds
    });
};

export const usePipelineAIInsights = (pipelineId: string) => {
    return useQuery({
        queryKey: ['ai-insights', pipelineId],
        queryFn: () => aiApi.getPipelineInsights(pipelineId),
        enabled: !!pipelineId,
        refetchInterval: 30000,
    });
};
