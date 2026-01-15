import { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';
import { useAuth } from './useAuth';
import { toast } from '@/components/common';
import type { Pipeline, PipelineInsert, PipelineUpdate } from '@/types/database';

export function usePipelines() {
    const [pipelines, setPipelines] = useState<Pipeline[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const { user } = useAuth();

    // Fetch pipelines
    const fetchPipelines = async () => {
        try {
            setLoading(true);
            setError(null);

            const { data, error: fetchError } = await supabase
                .from('pipelines')
                .select('*')
                .order('created_at', { ascending: false });

            if (fetchError) throw fetchError;
            setPipelines(data || []);
        } catch (err: any) {
            setError(err.message);
            // Silent fail on network errors - don't spam toasts
            console.warn('Failed to load pipelines:', err.message);
        } finally {
            setLoading(false);
        }
    };

    // Create pipeline
    const createPipeline = async (pipeline: PipelineInsert) => {
        try {
            if (!user) throw new Error('User not authenticated');

            const { data, error: createError } = await supabase
                .from('pipelines')
                .insert({
                    ...pipeline,
                    owner_id: user.id,
                })
                .select()
                .single();

            if (createError) throw createError;

            setPipelines(prev => [data, ...prev]);
            toast.success('Pipeline created', `"${data.name}" has been created successfully`);
            return { data, error: null };
        } catch (err: any) {
            toast.error('Failed to create pipeline', err.message);
            return { data: null, error: err.message };
        }
    };

    // Update pipeline
    const updatePipeline = async (id: string, updates: PipelineUpdate) => {
        try {
            const { data, error: updateError } = await supabase
                .from('pipelines')
                .update(updates)
                .eq('id', id)
                .select()
                .maybeSingle();

            if (updateError) throw updateError;
            if (!data) throw new Error('Pipeline not found');

            setPipelines(prev => prev.map(p => p.id === id ? data : p));
            toast.success('Pipeline updated', `"${data.name}" has been updated`);
            return { data, error: null };
        } catch (err: any) {
            toast.error('Failed to update pipeline', err.message);
            return { data: null, error: err.message };
        }
    };

    // Delete pipeline
    const deletePipeline = async (id: string) => {
        try {
            const pipeline = pipelines.find(p => p.id === id);
            const { error: deleteError } = await supabase
                .from('pipelines')
                .delete()
                .eq('id', id);

            if (deleteError) throw deleteError;

            setPipelines(prev => prev.filter(p => p.id !== id));
            toast.success('Pipeline deleted', pipeline ? `"${pipeline.name}" has been deleted` : undefined);
            return { error: null };
        } catch (err: any) {
            toast.error('Failed to delete pipeline', err.message);
            return { error: err.message };
        }
    };

    // Toggle pipeline active status
    const togglePipelineStatus = async (id: string, isActive: boolean) => {
        const result = await updatePipeline(id, { is_active: isActive });
        if (!result.error) {
            toast.info(`Pipeline ${isActive ? 'activated' : 'deactivated'}`);
        }
        return result;
    };

    useEffect(() => {
        if (user) {
            fetchPipelines();
        }
    }, [user]);

    return {
        pipelines,
        loading,
        error,
        createPipeline,
        updatePipeline,
        deletePipeline,
        togglePipelineStatus,
        refetch: fetchPipelines,
    };
}

