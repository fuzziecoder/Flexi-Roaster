import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import type { Database } from '@/lib/supabase';

type Log = Database['public']['Tables']['logs']['Row'];

export function useRealtimeLogs(executionId?: string) {
    const [logs, setLogs] = useState<Log[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Fetch initial data
        const fetchLogs = async () => {
            let query = supabase
                .from('logs')
                .select('*')
                .order('created_at', { ascending: false })
                .limit(100);

            if (executionId) {
                query = query.eq('execution_id', executionId);
            }

            const { data, error } = await query;

            if (error) {
                console.error('Error fetching logs:', error);
            } else {
                setLogs(data || []);
            }
            setLoading(false);
        };

        fetchLogs();

        // Subscribe to real-time changes
        const channel = supabase
            .channel('logs-changes')
            .on(
                'postgres_changes',
                {
                    event: 'INSERT',
                    schema: 'public',
                    table: 'logs',
                    filter: executionId ? `execution_id=eq.${executionId}` : undefined,
                },
                (payload) => {
                    setLogs((prev) => [payload.new as Log, ...prev]);
                }
            )
            .subscribe();

        return () => {
            supabase.removeChannel(channel);
        };
    }, [executionId]);

    return { logs, loading };
}
