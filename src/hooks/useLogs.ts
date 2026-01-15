import { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';
import { useAuth } from './useAuth';
import type { Log, LogLevel } from '@/types/database';

interface LogFilters {
    executionId?: string;
    level?: LogLevel;
    startDate?: string;
    endDate?: string;
    search?: string;
}

export function useLogs(filters: LogFilters = {}, limit = 100) {
    const [logs, setLogs] = useState<Log[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const { user } = useAuth();

    // Fetch logs with filters
    const fetchLogs = async () => {
        try {
            setLoading(true);
            setError(null);

            let query = supabase
                .from('logs')
                .select('*')
                .order('created_at', { ascending: false })
                .limit(limit);

            // Apply filters
            if (filters.executionId) {
                query = query.eq('execution_id', filters.executionId);
            }
            if (filters.level) {
                query = query.eq('level', filters.level);
            }
            if (filters.startDate) {
                query = query.gte('created_at', filters.startDate);
            }
            if (filters.endDate) {
                query = query.lte('created_at', filters.endDate);
            }
            if (filters.search) {
                query = query.ilike('message', `%${filters.search}%`);
            }

            const { data, error: fetchError } = await query;

            if (fetchError) throw fetchError;
            setLogs(data || []);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    // Export logs as JSON
    const exportLogs = (format: 'json' | 'csv' = 'json') => {
        if (format === 'json') {
            const dataStr = JSON.stringify(logs, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `logs-${new Date().toISOString()}.json`;
            link.click();
        } else {
            // CSV export
            const headers = ['created_at', 'level', 'message', 'execution_id'];
            const csvContent = [
                headers.join(','),
                ...logs.map(log =>
                    headers.map(h => JSON.stringify(log[h as keyof Log] || '')).join(',')
                )
            ].join('\n');

            const dataBlob = new Blob([csvContent], { type: 'text/csv' });
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `logs-${new Date().toISOString()}.csv`;
            link.click();
        }
    };

    useEffect(() => {
        if (user) {
            fetchLogs();
        }
    }, [user, JSON.stringify(filters)]);

    return {
        logs,
        loading,
        error,
        exportLogs,
        refetch: fetchLogs,
    };
}
