import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import type { Database } from '@/lib/supabase';

type Execution = Database['public']['Tables']['executions']['Row'];

export function useRealtimeExecutions() {
    const [executions, setExecutions] = useState<Execution[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Fetch initial data
        const fetchExecutions = async () => {
            const { data, error } = await supabase
                .from('executions')
                .select('*')
                .order('created_at', { ascending: false })
                .limit(50);

            if (error) {
                console.error('Error fetching executions:', error);
            } else {
                setExecutions(data || []);
            }
            setLoading(false);
        };

        fetchExecutions();

        // Subscribe to real-time changes
        const channel = supabase
            .channel('executions-changes')
            .on(
                'postgres_changes',
                {
                    event: '*',
                    schema: 'public',
                    table: 'executions',
                },
                (payload) => {
                    if (payload.eventType === 'INSERT') {
                        setExecutions((prev) => [payload.new as Execution, ...prev]);
                    } else if (payload.eventType === 'UPDATE') {
                        setExecutions((prev) =>
                            prev.map((e) =>
                                e.id === (payload.new as Execution).id ? (payload.new as Execution) : e
                            )
                        );
                    } else if (payload.eventType === 'DELETE') {
                        setExecutions((prev) =>
                            prev.filter((e) => e.id !== (payload.old as Execution).id)
                        );
                    }
                }
            )
            .subscribe();

        return () => {
            supabase.removeChannel(channel);
        };
    }, []);

    return { executions, loading };
}
