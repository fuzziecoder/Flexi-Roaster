/**
 * Flexible AI Hook - Direct Intent Detection for Real Actions
 * Uses keyword detection to execute actual database operations
 */
import { useState, useCallback, useRef } from 'react';
import { supabase } from '@/lib/supabase';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './useAuth';
import { toast } from '@/components/common';

export interface Message {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    isThinking?: boolean;
    timestamp: Date;
}

interface UseFlexibleAIReturn {
    messages: Message[];
    isLoading: boolean;
    error: string | null;
    sendMessage: (content: string) => Promise<void>;
    clearMessages: () => void;
    stopGeneration: () => void;
}

const generateId = () => `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

// Intent patterns for detecting user actions
const INTENTS = {
    CREATE_PIPELINE: /create\s+(a\s+)?(new\s+)?pipeline|make\s+(a\s+)?pipeline/i,
    LIST_PIPELINES: /list\s+(all\s+)?(my\s+)?pipelines|show\s+(my\s+)?pipelines|get\s+pipelines|what\s+pipelines/i,
    NAVIGATE_DASHBOARD: /go\s+to\s+dashboard|open\s+dashboard|show\s+dashboard|navigate.*dashboard/i,
    NAVIGATE_PIPELINES: /go\s+to\s+pipelines|open\s+pipelines\s+page|navigate.*pipelines/i,
    NAVIGATE_EXECUTIONS: /go\s+to\s+executions|open\s+executions|navigate.*executions/i,
    NAVIGATE_SETTINGS: /go\s+to\s+settings|open\s+settings|navigate.*settings/i,
    NAVIGATE_INSIGHTS: /go\s+to\s+(ai\s+)?insights|open\s+insights|navigate.*insights/i,
};

// Extract pipeline name from user input
function extractPipelineName(input: string): string {
    // Look for "called X" or "named X" patterns
    const calledMatch = input.match(/(?:called|named)\s+["']?([^"'\s,]+)["']?/i);
    if (calledMatch) return calledMatch[1];

    // Look for quoted names
    const quotedMatch = input.match(/["']([^"']+)["']/);
    if (quotedMatch) return quotedMatch[1];

    // Generate a default name
    return `Pipeline-${Date.now().toString(36)}`;
}

// Extract stages from user input
function extractStages(input: string): Array<{ id: string; name: string; type: string }> {
    const stages: Array<{ id: string; name: string; type: string }> = [];

    // Look for stage types mentioned
    const lowerInput = input.toLowerCase();

    if (lowerInput.includes('input') || lowerInput.includes('load') || lowerInput.includes('ingest')) {
        stages.push({ id: 'input-1', name: 'Data Input', type: 'input' });
    }
    if (lowerInput.includes('transform') || lowerInput.includes('process') || lowerInput.includes('convert')) {
        stages.push({ id: 'transform-1', name: 'Data Transform', type: 'transform' });
    }
    if (lowerInput.includes('validat') || lowerInput.includes('check') || lowerInput.includes('verify')) {
        stages.push({ id: 'validation-1', name: 'Data Validation', type: 'validation' });
    }
    if (lowerInput.includes('output') || lowerInput.includes('save') || lowerInput.includes('export')) {
        stages.push({ id: 'output-1', name: 'Data Output', type: 'output' });
    }

    // If no specific stages, create default input/output
    if (stages.length === 0) {
        stages.push(
            { id: 'input-1', name: 'Data Input', type: 'input' },
            { id: 'output-1', name: 'Data Output', type: 'output' }
        );
    }

    return stages;
}

export function useFlexibleAI(): UseFlexibleAIReturn {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const abortControllerRef = useRef<AbortController | null>(null);
    const navigate = useNavigate();
    const { user } = useAuth();

    // Create pipeline in database
    const createPipeline = useCallback(async (name: string, stages: Array<{ id: string; name: string; type: string }>) => {
        if (!user) {
            throw new Error('You must be logged in to create pipelines');
        }

        const { data, error: dbError } = await supabase
            .from('pipelines')
            .insert({
                name,
                description: `Created by Flexible AI`,
                config: { stages },
                owner_id: user.id,
                is_active: true,
                version: 1,
                timeout_seconds: 300
            })
            .select()
            .single();

        if (dbError) throw dbError;
        return data;
    }, [user]);

    // List pipelines from database
    const listPipelines = useCallback(async () => {
        const { data, error: dbError } = await supabase
            .from('pipelines')
            .select('id, name, description, is_active, created_at')
            .order('created_at', { ascending: false })
            .limit(10);

        if (dbError) throw dbError;
        return data || [];
    }, []);

    // Generate AI response using NVIDIA API
    const getAIResponse = useCallback(async (userMessage: string): Promise<string> => {
        const apiKey = import.meta.env.VITE_NVIDIA_API_KEY;
        if (!apiKey) {
            return "I'm here to help! What would you like to do?";
        }

        try {
            const response = await fetch('/api/nvidia/v1/chat/completions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: 'deepseek-ai/deepseek-r1',
                    messages: [
                        {
                            role: 'system',
                            content: 'You are Flexible AI, a helpful assistant for FlexiRoaster pipeline automation. Keep responses brief and friendly. Do not simulate or pretend to execute actions - just provide helpful conversation.'
                        },
                        { role: 'user', content: userMessage }
                    ],
                    temperature: 0.7,
                    max_tokens: 500,
                    stream: false
                }),
                signal: abortControllerRef.current?.signal
            });

            if (!response.ok) return '';

            const data = await response.json();
            return data.choices?.[0]?.message?.content || '';
        } catch {
            return '';
        }
    }, []);

    // Send message and handle actions
    const sendMessage = useCallback(async (content: string) => {
        if (!content.trim() || isLoading) return;

        setIsLoading(true);
        setError(null);
        const userInput = content.trim();

        // Add user message
        const userMessage: Message = {
            id: generateId(),
            role: 'user',
            content: userInput,
            timestamp: new Date()
        };
        setMessages(prev => [...prev, userMessage]);

        // Add thinking placeholder
        const assistantId = generateId();
        setMessages(prev => [...prev, {
            id: assistantId,
            role: 'assistant',
            content: '',
            isThinking: true,
            timestamp: new Date()
        }]);

        abortControllerRef.current = new AbortController();

        try {
            let responseContent = '';

            // Check for CREATE PIPELINE intent
            if (INTENTS.CREATE_PIPELINE.test(userInput)) {
                const pipelineName = extractPipelineName(userInput);
                const stages = extractStages(userInput);

                try {
                    const pipeline = await createPipeline(pipelineName, stages);
                    responseContent = `✅ **Pipeline Created Successfully!**

**Name:** ${pipeline.name}
**ID:** \`${pipeline.id}\`
**Stages:** ${stages.map(s => s.name).join(' → ')}
**Status:** Active ✅

Your pipeline is ready! You can view it in the [Pipelines](/pipelines) page.`;
                    toast.success('Pipeline created!', pipeline.name);
                } catch (err) {
                    responseContent = `❌ **Failed to create pipeline**

Error: ${err instanceof Error ? err.message : 'Unknown error'}

Make sure you're logged in and try again.`;
                    toast.error('Failed to create pipeline');
                }
            }
            // Check for LIST PIPELINES intent
            else if (INTENTS.LIST_PIPELINES.test(userInput)) {
                try {
                    const pipelines = await listPipelines();

                    if (pipelines.length === 0) {
                        responseContent = `📋 **No pipelines found**

You don't have any pipelines yet. Would you like me to create one?

Just say: *"Create a pipeline called [name]"*`;
                    } else {
                        responseContent = `📋 **Your Pipelines (${pipelines.length})**

${pipelines.map((p, i) =>
                            `${i + 1}. **${p.name}** ${p.is_active ? '✅' : '⏸️'}
   ${p.description || 'No description'}
   Created: ${new Date(p.created_at).toLocaleDateString()}`
                        ).join('\n\n')}

---
*Click on the Pipelines page to manage them.*`;
                    }
                } catch (err) {
                    responseContent = `❌ **Failed to load pipelines**

Error: ${err instanceof Error ? err.message : 'Unknown error'}`;
                    toast.error('Failed to load pipelines');
                }
            }
            // Check for NAVIGATION intents
            else if (INTENTS.NAVIGATE_DASHBOARD.test(userInput)) {
                navigate('/');
                responseContent = '🧭 **Navigating to Dashboard...**';
                toast.info('Going to Dashboard');
            }
            else if (INTENTS.NAVIGATE_PIPELINES.test(userInput)) {
                navigate('/pipelines');
                responseContent = '🧭 **Navigating to Pipelines...**';
                toast.info('Going to Pipelines');
            }
            else if (INTENTS.NAVIGATE_EXECUTIONS.test(userInput)) {
                navigate('/executions');
                responseContent = '🧭 **Navigating to Executions...**';
                toast.info('Going to Executions');
            }
            else if (INTENTS.NAVIGATE_SETTINGS.test(userInput)) {
                navigate('/settings');
                responseContent = '🧭 **Navigating to Settings...**';
                toast.info('Going to Settings');
            }
            else if (INTENTS.NAVIGATE_INSIGHTS.test(userInput)) {
                navigate('/ai-insights');
                responseContent = '🧭 **Navigating to AI Insights...**';
                toast.info('Going to AI Insights');
            }
            // Default: Get AI response for conversation
            else {
                const aiResponse = await getAIResponse(userInput);
                responseContent = aiResponse || `I can help you with:

• **Create pipelines** - "Create a pipeline called data-sync"
• **List pipelines** - "Show my pipelines"
• **Navigate** - "Go to dashboard", "Open settings"

What would you like to do?`;
            }

            // Update assistant message
            setMessages(prev =>
                prev.map(m =>
                    m.id === assistantId
                        ? { ...m, content: responseContent, isThinking: false }
                        : m
                )
            );

        } catch (err) {
            if (err instanceof Error && err.name === 'AbortError') return;

            console.error('AI Error:', err);
            setError(err instanceof Error ? err.message : 'Request failed');
            setMessages(prev => prev.filter(m => m.id !== assistantId));
        } finally {
            setIsLoading(false);
            abortControllerRef.current = null;
        }
    }, [isLoading, createPipeline, listPipelines, getAIResponse, navigate]);

    const clearMessages = useCallback(() => {
        setMessages([]);
        setError(null);
    }, []);

    const stopGeneration = useCallback(() => {
        abortControllerRef.current?.abort();
    }, []);

    return { messages, isLoading, error, sendMessage, clearMessages, stopGeneration };
}
