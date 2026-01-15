/**
 * Chat History Hook
 * Persists Flexible AI conversations to Supabase
 */
import { useState, useEffect, useCallback } from 'react';
import { supabase } from '@/lib/supabase';
import { useAuth } from '@/hooks/useAuth';

export interface ChatConversation {
    id: string;
    title: string;
    created_at: string;
    updated_at: string;
    message_count: number;
}

export interface ChatMessage {
    id: string;
    conversation_id: string;
    role: 'user' | 'assistant';
    content: string;
    created_at: string;
}

interface UseChatHistoryReturn {
    conversations: ChatConversation[];
    currentConversation: ChatConversation | null;
    messages: ChatMessage[];
    isLoading: boolean;
    createConversation: () => Promise<string | null>;
    selectConversation: (id: string) => Promise<void>;
    addMessage: (role: 'user' | 'assistant', content: string) => Promise<void>;
    deleteConversation: (id: string) => Promise<void>;
    updateConversationTitle: (id: string, title: string) => Promise<void>;
    refreshConversations: () => Promise<void>;
}

export function useChatHistory(): UseChatHistoryReturn {
    const { user } = useAuth();
    const [conversations, setConversations] = useState<ChatConversation[]>([]);
    const [currentConversation, setCurrentConversation] = useState<ChatConversation | null>(null);
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    // Load conversations on mount
    useEffect(() => {
        if (user) {
            refreshConversations();
        }
    }, [user]);

    // Refresh conversations list
    const refreshConversations = useCallback(async () => {
        if (!user) return;

        try {
            const { data, error } = await supabase
                .from('ai_conversations')
                .select('*')
                .eq('user_id', user.id)
                .order('updated_at', { ascending: false })
                .limit(50);

            if (error) throw error;
            setConversations(data || []);
        } catch (err) {
            console.error('Failed to load conversations:', err);
        }
    }, [user]);

    // Create new conversation
    const createConversation = useCallback(async (): Promise<string | null> => {
        if (!user) return null;

        try {
            const { data, error } = await supabase
                .from('ai_conversations')
                .insert({
                    user_id: user.id,
                    title: 'New Chat',
                    message_count: 0
                })
                .select()
                .single();

            if (error) throw error;

            setCurrentConversation(data);
            setMessages([]);
            await refreshConversations();
            return data.id;
        } catch (err) {
            console.error('Failed to create conversation:', err);
            return null;
        }
    }, [user, refreshConversations]);

    // Select and load a conversation
    const selectConversation = useCallback(async (id: string) => {
        setIsLoading(true);
        try {
            // Get conversation
            const { data: conv, error: convError } = await supabase
                .from('ai_conversations')
                .select('*')
                .eq('id', id)
                .single();

            if (convError) throw convError;
            setCurrentConversation(conv);

            // Get messages
            const { data: msgs, error: msgsError } = await supabase
                .from('ai_messages')
                .select('*')
                .eq('conversation_id', id)
                .order('created_at', { ascending: true });

            if (msgsError) throw msgsError;
            setMessages(msgs || []);
        } catch (err) {
            console.error('Failed to load conversation:', err);
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Add message to current conversation
    const addMessage = useCallback(async (role: 'user' | 'assistant', content: string) => {
        if (!currentConversation) return;

        try {
            const { data, error } = await supabase
                .from('ai_messages')
                .insert({
                    conversation_id: currentConversation.id,
                    role,
                    content
                })
                .select()
                .single();

            if (error) throw error;

            setMessages(prev => [...prev, data]);

            // Update conversation
            const newTitle = messages.length === 0 && role === 'user'
                ? content.slice(0, 50) + (content.length > 50 ? '...' : '')
                : currentConversation.title;

            await supabase
                .from('ai_conversations')
                .update({
                    updated_at: new Date().toISOString(),
                    message_count: messages.length + 1,
                    title: newTitle
                })
                .eq('id', currentConversation.id);

            if (newTitle !== currentConversation.title) {
                setCurrentConversation(prev => prev ? { ...prev, title: newTitle } : null);
            }

            await refreshConversations();
        } catch (err) {
            console.error('Failed to add message:', err);
        }
    }, [currentConversation, messages.length, refreshConversations]);

    // Delete conversation
    const deleteConversation = useCallback(async (id: string) => {
        try {
            // Messages will be cascade deleted
            const { error } = await supabase
                .from('ai_conversations')
                .delete()
                .eq('id', id);

            if (error) throw error;

            if (currentConversation?.id === id) {
                setCurrentConversation(null);
                setMessages([]);
            }

            await refreshConversations();
        } catch (err) {
            console.error('Failed to delete conversation:', err);
        }
    }, [currentConversation, refreshConversations]);

    // Update conversation title
    const updateConversationTitle = useCallback(async (id: string, title: string) => {
        try {
            const { error } = await supabase
                .from('ai_conversations')
                .update({ title })
                .eq('id', id);

            if (error) throw error;

            if (currentConversation?.id === id) {
                setCurrentConversation(prev => prev ? { ...prev, title } : null);
            }

            await refreshConversations();
        } catch (err) {
            console.error('Failed to update title:', err);
        }
    }, [currentConversation, refreshConversations]);

    return {
        conversations,
        currentConversation,
        messages,
        isLoading,
        createConversation,
        selectConversation,
        addMessage,
        deleteConversation,
        updateConversationTitle,
        refreshConversations
    };
}
