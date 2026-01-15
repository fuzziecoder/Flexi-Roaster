import { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';
import { useAuth } from './useAuth';
import { toast } from '@/components/common';
import type { Execution } from '@/types/database';

interface ExecutionWithPipeline extends Execution {
    pipeline?: {
        name: string;
    };
}

export function useExecutions(limit = 50) {
    const [executions, setExecutions] = useState<ExecutionWithPipeline[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const { user } = useAuth();

    // Fetch executions
    const fetchExecutions = async () => {
        try {
            setLoading(true);
            setError(null);

            const { data, error: fetchError } = await supabase
                .from('executions')
                .select(`
          *,
          pipeline:pipelines(name)
        `)
                .order('created_at', { ascending: false })
                .limit(limit);

            if (fetchError) throw fetchError;
            setExecutions(data || []);
        } catch (err: any) {
            setError(err.message);
            // Silent fail on network errors - don't spam toasts
            console.warn('Failed to load executions:', err.message);
        } finally {
            setLoading(false);
        }
    };

    // Trigger new execution
    const triggerExecution = async (pipelineId: string) => {
        try {
            if (!user) throw new Error('User not authenticated');

            // Note: removed metadata field as it may not exist in all DB schemas
            const executionData = {
                pipeline_id: pipelineId,
                triggered_by: user.id,
                status: 'pending' as const,
            };

            const { data, error: createError } = await supabase
                .from('executions')
                .insert(executionData)
                .select(`
          *,
          pipeline:pipelines(name)
        `)
                .single();

            if (createError) throw createError;

            setExecutions(prev => [data, ...prev]);
            toast.success('Execution started', `Pipeline "${data.pipeline?.name || 'Unknown'}" is now running`);
            return { data, error: null };
        } catch (err: any) {
            toast.error('Failed to start execution', err.message);
            return { data: null, error: err.message };
        }
    };

    // Get execution details with stages
    const getExecutionDetails = async (executionId: string) => {
        try {
            const { data, error: fetchError } = await supabase
                .from('executions')
                .select(`
          *,
          pipeline:pipelines(name, config),
          execution_stages(*)
        `)
                .eq('id', executionId)
                .single();

            if (fetchError) throw fetchError;
            return { data, error: null };
        } catch (err: any) {
            toast.error('Failed to load execution details', err.message);
            return { data: null, error: err.message };
        }
    };

    useEffect(() => {
        if (user) {
            fetchExecutions();
        }
    }, [user]);

    return {
        executions,
        loading,
        error,
        triggerExecution,
        getExecutionDetails,
        refetch: fetchExecutions,
    };
}

