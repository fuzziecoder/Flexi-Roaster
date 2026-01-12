import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
    throw new Error('Missing Supabase environment variables');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
    auth: {
        autoRefreshToken: true,
        persistSession: true,
        detectSessionInUrl: true
    },
    realtime: {
        params: {
            eventsPerSecond: 10
        }
    }
});

// Database types (will be auto-generated later)
export type Database = {
    public: {
        Tables: {
            user_profiles: {
                Row: {
                    id: string;
                    full_name: string | null;
                    avatar_url: string | null;
                    role: 'admin' | 'user' | 'viewer';
                    created_at: string;
                    updated_at: string;
                };
                Insert: {
                    id: string;
                    full_name?: string | null;
                    avatar_url?: string | null;
                    role?: 'admin' | 'user' | 'viewer';
                };
                Update: {
                    full_name?: string | null;
                    avatar_url?: string | null;
                    role?: 'admin' | 'user' | 'viewer';
                };
            };
            pipelines: {
                Row: {
                    id: string;
                    name: string;
                    description: string | null;
                    owner_id: string | null;
                    definition: any;
                    version: number;
                    is_active: boolean;
                    schedule_cron: string | null;
                    timeout_seconds: number;
                    tags: string[] | null;
                    created_at: string;
                    updated_at: string;
                };
            };
            executions: {
                Row: {
                    id: string;
                    pipeline_id: string | null;
                    status: 'pending' | 'queued' | 'running' | 'completed' | 'failed' | 'cancelled';
                    started_at: string | null;
                    completed_at: string | null;
                    duration_seconds: number | null;
                    triggered_by: string | null;
                    trigger_type: 'manual' | 'scheduled' | 'webhook' | 'api';
                    error_message: string | null;
                    context: any;
                    created_at: string;
                };
            };
            logs: {
                Row: {
                    id: number;
                    level: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR' | 'SUCCESS';
                    service: string | null;
                    pipeline_id: string | null;
                    execution_id: string | null;
                    stage_id: string | null;
                    message: string;
                    metadata: any;
                    created_at: string;
                };
            };
            alerts: {
                Row: {
                    id: string;
                    severity: 'critical' | 'high' | 'medium' | 'low';
                    title: string;
                    message: string;
                    source: string | null;
                    pipeline_id: string | null;
                    execution_id: string | null;
                    status: 'open' | 'acknowledged' | 'resolved';
                    acknowledged_by: string | null;
                    acknowledged_at: string | null;
                    resolved_by: string | null;
                    resolved_at: string | null;
                    metadata: any;
                    created_at: string;
                };
            };
            metrics: {
                Row: {
                    id: number;
                    metric_name: string;
                    metric_type: 'counter' | 'gauge' | 'histogram';
                    value: number;
                    tags: any;
                    created_at: string;
                };
            };
            ai_insights: {
                Row: {
                    id: string;
                    insight_type: 'failure_prediction' | 'anomaly' | 'optimization' | 'cost';
                    pipeline_id: string | null;
                    execution_id: string | null;
                    severity: 'critical' | 'high' | 'medium' | 'low' | 'info' | null;
                    title: string;
                    description: string | null;
                    recommendation: string | null;
                    confidence: number | null;
                    metadata: any;
                    is_dismissed: boolean;
                    created_at: string;
                };
            };
        };
    };
};
