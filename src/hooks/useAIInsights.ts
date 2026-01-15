import { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';
import { useAuth } from './useAuth';
import type { AIInsight } from '@/types/database';

export function useAIInsights() {
    const [insights, setInsights] = useState<AIInsight[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const { user } = useAuth();

    // Fetch AI insights
    const fetchInsights = async () => {
        try {
            setLoading(true);
            setError(null);

            const { data, error: fetchError } = await supabase
                .from('ai_insights')
                .select('*')
                .eq('is_dismissed', false)
                .order('created_at', { ascending: false });

            if (fetchError) throw fetchError;
            setInsights(data || []);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    // Dismiss an insight
    const dismissInsight = async (insightId: string) => {
        try {
            const { error: updateError } = await supabase
                .from('ai_insights')
                .update({ is_dismissed: true })
                .eq('id', insightId);

            if (updateError) throw updateError;

            setInsights(prev => prev.filter(i => i.id !== insightId));
            return { error: null };
        } catch (err: any) {
            return { error: err.message };
        }
    };

    useEffect(() => {
        if (user) {
            fetchInsights();
        }
    }, [user]);

    return {
        insights,
        loading,
        error,
        dismissInsight,
        refetch: fetchInsights,
    };
}
