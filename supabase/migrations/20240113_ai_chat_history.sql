-- AI Chat History Tables
-- Stores conversations and messages for Flexible AI

-- Conversations table
CREATE TABLE IF NOT EXISTS ai_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    title TEXT DEFAULT 'New Chat',
    message_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Messages table
CREATE TABLE IF NOT EXISTS ai_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES ai_conversations(id) ON DELETE CASCADE NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_ai_conversations_user_id ON ai_conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_conversations_updated_at ON ai_conversations(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_messages_conversation_id ON ai_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_ai_messages_created_at ON ai_messages(created_at);

-- RLS Policies
ALTER TABLE ai_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_messages ENABLE ROW LEVEL SECURITY;

-- Users can only access their own conversations
CREATE POLICY "Users can view own conversations"
    ON ai_conversations FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create own conversations"
    ON ai_conversations FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own conversations"
    ON ai_conversations FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own conversations"
    ON ai_conversations FOR DELETE
    USING (auth.uid() = user_id);

-- Users can access messages in their conversations
CREATE POLICY "Users can view messages in own conversations"
    ON ai_messages FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM ai_conversations 
            WHERE id = ai_messages.conversation_id 
            AND user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create messages in own conversations"
    ON ai_messages FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM ai_conversations 
            WHERE id = ai_messages.conversation_id 
            AND user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete messages in own conversations"
    ON ai_messages FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM ai_conversations 
            WHERE id = ai_messages.conversation_id 
            AND user_id = auth.uid()
        )
    );
