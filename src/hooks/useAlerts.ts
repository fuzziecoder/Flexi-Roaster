import { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';
import { useAuth } from './useAuth';
import type { Alert, AlertUpdate, AlertSeverity, AlertStatus } from '@/types/database';

interface AlertFilters {
    severity?: AlertSeverity;
    status?: AlertStatus;
}

export function useAlerts(filters: AlertFilters = {}) {
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const { user } = useAuth();

    // Fetch alerts
    const fetchAlerts = async () => {
        try {
            setLoading(true);
            setError(null);

            let query = supabase
                .from('alerts')
                .select('*')
                .order('created_at', { ascending: false });

            // Apply filters
            if (filters.severity) {
                query = query.eq('severity', filters.severity);
            }
            if (filters.status) {
                query = query.eq('status', filters.status);
            }

            const { data, error: fetchError } = await query;

            if (fetchError) throw fetchError;
            setAlerts(data || []);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    // Acknowledge alert
    const acknowledgeAlert = async (alertId: string) => {
        try {
            if (!user) throw new Error('User not authenticated');

            const updates: AlertUpdate = {
                status: 'acknowledged',
                acknowledged_by: user.id,
                acknowledged_at: new Date().toISOString(),
            };

            const { data, error: updateError } = await supabase
                .from('alerts')
                .update(updates)
                .eq('id', alertId)
                .select()
                .single();

            if (updateError) throw updateError;

            setAlerts(prev => prev.map(a => a.id === alertId ? data : a));
            return { data, error: null };
        } catch (err: any) {
            return { data: null, error: err.message };
        }
    };

    // Resolve alert
    const resolveAlert = async (alertId: string) => {
        try {
            if (!user) throw new Error('User not authenticated');

            const updates: AlertUpdate = {
                status: 'resolved',
                resolved_by: user.id,
                resolved_at: new Date().toISOString(),
            };

            const { data, error: updateError } = await supabase
                .from('alerts')
                .update(updates)
                .eq('id', alertId)
                .select()
                .single();

            if (updateError) throw updateError;

            setAlerts(prev => prev.map(a => a.id === alertId ? data : a));
            return { data, error: null };
        } catch (err: any) {
            return { data: null, error: err.message };
        }
    };

    // Get unread count
    const getUnreadCount = () => {
        return alerts.filter(a => a.status === 'active').length;
    };

    useEffect(() => {
        if (user) {
            fetchAlerts();
        }
    }, [user, JSON.stringify(filters)]);

    return {
        alerts,
        loading,
        error,
        acknowledgeAlert,
        resolveAlert,
        getUnreadCount,
        refetch: fetchAlerts,
    };
}
