// API Service Functions
// Clean API calls for all backend endpoints
import { apiClient } from './api';

// Pipelines API
export const pipelinesApi = {
    getAll: async () => {
        const response = await apiClient.get('/api/pipelines');
        return response.data;
    },

    getById: async (id: string) => {
        const response = await apiClient.get(`/api/pipelines/${id}`);
        return response.data;
    },

    create: async (pipeline: any) => {
        const response = await apiClient.post('/api/pipelines', pipeline);
        return response.data;
    },

    delete: async (id: string) => {
        const response = await apiClient.delete(`/api/pipelines/${id}`);
        return response.data;
    },
};

// Executions API
export const executionsApi = {
    getAll: async (limit = 50, offset = 0) => {
        const response = await apiClient.get('/api/executions', {
            params: { limit, offset }
        });
        return response.data;
    },

    getById: async (id: string) => {
        const response = await apiClient.get(`/api/executions/${id}`);
        return response.data;
    },

    create: async (pipelineId: string, variables?: any) => {
        const response = await apiClient.post('/api/executions', {
            pipeline_id: pipelineId,
            variables
        });
        return response.data;
    },

    getLogs: async (id: string) => {
        const response = await apiClient.get(`/api/executions/${id}/logs`);
        return response.data;
    },
};

// Metrics API
export const metricsApi = {
    getCurrent: async () => {
        const response = await apiClient.get('/api/metrics');
        return response.data;
    },

    getHistory: async (hours = 24) => {
        const response = await apiClient.get('/api/metrics/history', {
            params: { hours }
        });
        return response.data;
    },
};

// AI Insights API
export const aiApi = {
    getInsights: async () => {
        const response = await apiClient.get('/api/ai/insights');
        return response.data;
    },

    getPipelineInsights: async (pipelineId: string) => {
        const response = await apiClient.get(`/api/ai/insights/${pipelineId}`);
        return response.data;
    },
};

// Health Check
export const healthApi = {
    check: async () => {
        const response = await apiClient.get('/health');
        return response.data;
    },
};
