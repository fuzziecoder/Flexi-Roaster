/**
 * Flexible AI Chat Modal
 * Opens as a centered modal with AI assistant functionality
 */
import { useState, useRef, useEffect, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { useFlexibleAI, type Message as AIMessage } from '@/hooks/useFlexibleAI';
import { toast } from '@/components/common';
import {
    Send,
    X,
    Loader2,
    Trash2,
    Bot,
    User,
    Maximize2,
    Minimize2
} from 'lucide-react';

interface FlexibleAIProps {
    collapsed: boolean;
}

// Message bubble component
function MessageBubble({ message }: { message: AIMessage }) {
    const isUser = message.role === 'user';

    return (
        <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
            <div className={`
                w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center
                ${isUser ? 'bg-white/10' : 'bg-gradient-to-br from-white/20 to-white/5'}
            `}>
                {isUser ? (
                    <User className="w-4 h-4 text-white/70" />
                ) : (
                    <img src="/logo.jpg" alt="AI" className="w-6 h-6 rounded-full" />
                )}
            </div>

            <div className={`
                max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed
                ${isUser
                    ? 'bg-white/10 text-white rounded-tr-md'
                    : 'bg-[hsl(var(--surface))] text-white/90 rounded-tl-md border border-white/5'
                }
            `}>
                {message.isThinking ? (
                    <div className="flex items-center gap-2 text-white/50">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Thinking...</span>
                    </div>
                ) : (
                    <div className="whitespace-pre-wrap break-words">
                        {message.content || <span className="text-white/30 italic">No response</span>}
                    </div>
                )}
            </div>
        </div>
    );
}

// Main Modal component
function AIModal({
    isOpen,
    onClose
}: {
    isOpen: boolean;
    onClose: () => void;
}) {
    const [input, setInput] = useState('');
    const [isFullscreen, setIsFullscreen] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    const {
        messages,
        isLoading,
        error,
        sendMessage,
        clearMessages,
        stopGeneration
    } = useFlexibleAI();

    // Auto-scroll
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Focus input
    useEffect(() => {
        if (isOpen && inputRef.current) {
            setTimeout(() => inputRef.current?.focus(), 100);
        }
    }, [isOpen]);

    // Escape to close
    useEffect(() => {
        const handleEsc = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose();
        };
        if (isOpen) {
            window.addEventListener('keydown', handleEsc);
            document.body.style.overflow = 'hidden';
        }
        return () => {
            window.removeEventListener('keydown', handleEsc);
            document.body.style.overflow = '';
        };
    }, [isOpen, onClose]);

    // Handle send message
    const handleSubmit = useCallback(async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage = input.trim();
        setInput('');
        await sendMessage(userMessage);
    }, [input, isLoading, sendMessage]);

    if (!isOpen) return null;

    return createPortal(
        <div
            className="fixed inset-0 z-[9999] flex items-center justify-center"
            style={{ backgroundColor: 'rgba(0, 0, 0, 0.7)' }}
            onClick={onClose}
        >
            <div
                className={`
                    bg-[#0a0a0a] border border-white/10 shadow-2xl
                    flex flex-col overflow-hidden
                    ${isFullscreen
                        ? 'w-full h-full'
                        : 'w-[90%] max-w-2xl h-[80vh] max-h-[600px] rounded-2xl'
                    }
                `}
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="flex items-center justify-between px-5 py-4 border-b border-white/10 bg-[#111]">
                    <div className="flex items-center gap-3">
                        <div className="relative">
                            <img src="/logo.jpg" alt="AI" className="w-8 h-8 rounded-lg" />
                            <div className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-green-500 rounded-full border-2 border-[#111]" />
                        </div>
                        <div>
                            <h2 className="text-lg font-bold text-white zen-dots">Flexible AI</h2>
                            <p className="text-xs text-white/50">Your intelligent assistant</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => setIsFullscreen(!isFullscreen)}
                            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                        >
                            {isFullscreen ? (
                                <Minimize2 className="w-4 h-4 text-white/50" />
                            ) : (
                                <Maximize2 className="w-4 h-4 text-white/50" />
                            )}
                        </button>
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                        >
                            <X className="w-5 h-5 text-white/50" />
                        </button>
                    </div>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-5 bg-[#0a0a0a]">
                    {messages.length === 0 ? (
                        <div className="h-full flex flex-col items-center justify-center text-white/40">
                            <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center mb-4">
                                <Bot className="w-8 h-8" />
                            </div>
                            <h3 className="text-lg font-medium text-white/70 mb-2">How can I help you?</h3>
                            <p className="text-sm text-center max-w-md mb-6">
                                I can create pipelines, list them, and navigate the app.
                            </p>

                            <div className="flex flex-wrap gap-2 justify-center">
                                {[
                                    '✨ Create a test pipeline',
                                    '📋 List my pipelines',
                                    '📊 Go to dashboard'
                                ].map((prompt) => (
                                    <button
                                        key={prompt}
                                        onClick={() => {
                                            setInput(prompt.replace(/^[^\s]+\s/, ''));
                                            inputRef.current?.focus();
                                        }}
                                        className="px-3 py-2 bg-white/5 hover:bg-white/10 text-white/60 hover:text-white text-sm rounded-lg transition-colors"
                                    >
                                        {prompt}
                                    </button>
                                ))}
                            </div>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {messages.map((message) => (
                                <MessageBubble key={message.id} message={message} />
                            ))}
                            <div ref={messagesEndRef} />
                        </div>
                    )}
                </div>

                {/* Error */}
                {error && (
                    <div className="mx-5 mb-2 px-4 py-2 bg-red-500/20 border border-red-500/30 rounded-lg text-sm text-red-400">
                        {error}
                    </div>
                )}

                {/* Input */}
                <div className="p-5 pt-3 border-t border-white/10 bg-[#111]">
                    <form onSubmit={handleSubmit} className="flex gap-3">
                        <input
                            ref={inputRef}
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Ask me anything..."
                            disabled={isLoading}
                            className="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/30 focus:outline-none focus:border-white/30 disabled:opacity-50"
                        />

                        {isLoading ? (
                            <button
                                type="button"
                                onClick={stopGeneration}
                                className="px-4 py-3 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-xl transition-colors flex items-center gap-2"
                            >
                                <X className="w-4 h-4" />
                                Stop
                            </button>
                        ) : (
                            <button
                                type="submit"
                                disabled={!input.trim()}
                                className="px-4 py-3 bg-white/10 hover:bg-white/20 text-white rounded-xl transition-colors disabled:opacity-30 flex items-center gap-2"
                            >
                                <Send className="w-4 h-4" />
                                Send
                            </button>
                        )}

                        {messages.length > 0 && !isLoading && (
                            <button
                                type="button"
                                onClick={() => {
                                    clearMessages();
                                    toast.info('Chat cleared');
                                }}
                                className="p-3 hover:bg-white/10 text-white/50 hover:text-white rounded-xl transition-colors"
                            >
                                <Trash2 className="w-4 h-4" />
                            </button>
                        )}
                    </form>
                </div>
            </div>
        </div>,
        document.body
    );
}

export function FlexibleAI({ collapsed }: FlexibleAIProps) {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <>
            {/* Sidebar Button */}
            <div className={`border-t border-white/10 ${collapsed ? 'px-3 py-2' : ''}`}>
                <button
                    onClick={() => setIsOpen(true)}
                    className={`
                        w-full flex items-center gap-2 transition-colors
                        ${collapsed
                            ? 'p-2 rounded-lg justify-center hover:bg-white/5'
                            : 'px-4 py-3 hover:bg-white/5'
                        }
                        text-white/70 hover:text-white
                    `}
                    title="Open Flexible AI"
                >
                    <div className="relative">
                        <img src="/logo.jpg" alt="AI" className={`rounded ${collapsed ? 'w-5 h-5' : 'w-6 h-6'}`} />
                        <div className="absolute -bottom-0.5 -right-0.5 w-2 h-2 bg-green-500 rounded-full border border-[hsl(var(--card))]" />
                    </div>
                    {!collapsed && (
                        <span className="text-base font-bold text-white zen-dots">Flexible AI</span>
                    )}
                </button>
            </div>

            {/* Modal */}
            <AIModal
                isOpen={isOpen}
                onClose={() => setIsOpen(false)}
            />
        </>
    );
}
