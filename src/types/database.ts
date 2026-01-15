// Database Types - Generated from Supabase Schema
export type Json =
    | string
    | number
    | boolean
    | null
    | { [key: string]: Json | undefined }
    | Json[]

export interface Database {
    public: {
        Tables: {
            user_profiles: {
                Row: {
                    id: string
                    email: string
                    full_name: string | null
                    avatar_url: string | null
                    role: 'user' | 'admin'
                    created_at: string
                    updated_at: string
                }
                Insert: {
                    id: string
                    email: string
                    full_name?: string | null
                    avatar_url?: string | null
                    role?: 'user' | 'admin'
                    created_at?: string
                    updated_at?: string
                }
                Update: {
                    id?: string
                    email?: string
                    full_name?: string | null
                    avatar_url?: string | null
                    role?: 'user' | 'admin'
                    created_at?: string
                    updated_at?: string
                }
            }
            pipelines: {
                Row: {
                    id: string
                    name: string
                    description: string | null
                    owner_id: string
                    config: Json
                    is_active: boolean
                    version: number
                    created_at: string
                    updated_at: string
                }
                Insert: {
                    id?: string
                    name: string
                    description?: string | null
                    owner_id: string
                    config: Json
                    is_active?: boolean
                    version?: number
                    created_at?: string
                    updated_at?: string
                }
                Update: {
                    id?: string
                    name?: string
                    description?: string | null
                    owner_id?: string
                    config?: Json
                    is_active?: boolean
                    version?: number
                    created_at?: string
                    updated_at?: string
                }
            }
            pipeline_stages: {
                Row: {
                    id: string
                    pipeline_id: string
                    name: string
                    stage_order: number
                    config: Json
                    created_at: string
                }
                Insert: {
                    id?: string
                    pipeline_id: string
                    name: string
                    stage_order: number
                    config: Json
                    created_at?: string
                }
                Update: {
                    id?: string
                    pipeline_id?: string
                    name?: string
                    stage_order?: number
                    config?: Json
                    created_at?: string
                }
            }
            executions: {
                Row: {
                    id: string
                    pipeline_id: string
                    status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
                    triggered_by: string
                    started_at: string | null
                    completed_at: string | null
                    error_message: string | null
                    metadata: Json | null
                    created_at: string
                }
                Insert: {
                    id?: string
                    pipeline_id: string
                    status?: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
                    triggered_by: string
                    started_at?: string | null
                    completed_at?: string | null
                    error_message?: string | null
                    metadata?: Json | null
                    created_at?: string
                }
                Update: {
                    id?: string
                    pipeline_id?: string
                    status?: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
                    triggered_by?: string
                    started_at?: string | null
                    completed_at?: string | null
                    error_message?: string | null
                    metadata?: Json | null
                    created_at?: string
                }
            }
            execution_stages: {
                Row: {
                    id: string
                    execution_id: string
                    stage_id: string
                    status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped'
                    started_at: string | null
                    completed_at: string | null
                    error_message: string | null
                    output: Json | null
                }
                Insert: {
                    id?: string
                    execution_id: string
                    stage_id: string
                    status?: 'pending' | 'running' | 'completed' | 'failed' | 'skipped'
                    started_at?: string | null
                    completed_at?: string | null
                    error_message?: string | null
                    output?: Json | null
                }
                Update: {
                    id?: string
                    execution_id?: string
                    stage_id?: string
                    status?: 'pending' | 'running' | 'completed' | 'failed' | 'skipped'
                    started_at?: string | null
                    completed_at?: string | null
                    error_message?: string | null
                    output?: Json | null
                }
            }
            logs: {
                Row: {
                    id: string
                    execution_id: string | null
                    level: 'debug' | 'info' | 'warning' | 'error' | 'critical'
                    message: string
                    metadata: Json | null
                    created_at: string
                }
                Insert: {
                    id?: string
                    execution_id?: string | null
                    level: 'debug' | 'info' | 'warning' | 'error' | 'critical'
                    message: string
                    metadata?: Json | null
                    created_at?: string
                }
                Update: {
                    id?: string
                    execution_id?: string | null
                    level?: 'debug' | 'info' | 'warning' | 'error' | 'critical'
                    message?: string
                    metadata?: Json | null
                    created_at?: string
                }
            }
            metrics: {
                Row: {
                    id: string
                    execution_id: string | null
                    metric_name: string
                    metric_value: number
                    unit: string | null
                    tags: Json | null
                    created_at: string
                }
                Insert: {
                    id?: string
                    execution_id?: string | null
                    metric_name: string
                    metric_value: number
                    unit?: string | null
                    tags?: Json | null
                    created_at?: string
                }
                Update: {
                    id?: string
                    execution_id?: string | null
                    metric_name?: string
                    metric_value?: number
                    unit?: string | null
                    tags?: Json | null
                    created_at?: string
                }
            }
            alerts: {
                Row: {
                    id: string
                    execution_id: string | null
                    severity: 'low' | 'medium' | 'high' | 'critical'
                    title: string
                    message: string
                    status: 'active' | 'acknowledged' | 'resolved'
                    acknowledged_by: string | null
                    acknowledged_at: string | null
                    resolved_by: string | null
                    resolved_at: string | null
                    created_at: string
                }
                Insert: {
                    id?: string
                    execution_id?: string | null
                    severity: 'low' | 'medium' | 'high' | 'critical'
                    title: string
                    message: string
                    status?: 'active' | 'acknowledged' | 'resolved'
                    acknowledged_by?: string | null
                    acknowledged_at?: string | null
                    resolved_by?: string | null
                    resolved_at?: string | null
                    created_at?: string
                }
                Update: {
                    id?: string
                    execution_id?: string | null
                    severity?: 'low' | 'medium' | 'high' | 'critical'
                    title?: string
                    message?: string
                    status?: 'active' | 'acknowledged' | 'resolved'
                    acknowledged_by?: string | null
                    acknowledged_at?: string | null
                    resolved_by?: string | null
                    resolved_at?: string | null
                    created_at?: string
                }
            }
            ai_insights: {
                Row: {
                    id: string
                    execution_id: string | null
                    insight_type: 'prediction' | 'anomaly' | 'optimization' | 'recommendation'
                    title: string
                    description: string
                    confidence: number
                    is_dismissed: boolean
                    created_at: string
                }
                Insert: {
                    id?: string
                    execution_id?: string | null
                    insight_type: 'prediction' | 'anomaly' | 'optimization' | 'recommendation'
                    title: string
                    description: string
                    confidence: number
                    is_dismissed?: boolean
                    created_at?: string
                }
                Update: {
                    id?: string
                    execution_id?: string | null
                    insight_type?: 'prediction' | 'anomaly' | 'optimization' | 'recommendation'
                    title?: string
                    description?: string
                    confidence?: number
                    is_dismissed?: boolean
                    created_at?: string
                }
            }
        }
    }
}

// Helper types
export type Pipeline = Database['public']['Tables']['pipelines']['Row']
export type PipelineInsert = Database['public']['Tables']['pipelines']['Insert']
export type PipelineUpdate = Database['public']['Tables']['pipelines']['Update']

export type Execution = Database['public']['Tables']['executions']['Row']
export type ExecutionInsert = Database['public']['Tables']['executions']['Insert']
export type ExecutionUpdate = Database['public']['Tables']['executions']['Update']

export type Log = Database['public']['Tables']['logs']['Row']
export type Alert = Database['public']['Tables']['alerts']['Row']
export type AlertUpdate = Database['public']['Tables']['alerts']['Update']

export type Metric = Database['public']['Tables']['metrics']['Row']
export type AIInsight = Database['public']['Tables']['ai_insights']['Row']

// Enums
export type ExecutionStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
export type LogLevel = 'debug' | 'info' | 'warning' | 'error' | 'critical'
export type AlertSeverity = 'low' | 'medium' | 'high' | 'critical'
export type AlertStatus = 'active' | 'acknowledged' | 'resolved'
