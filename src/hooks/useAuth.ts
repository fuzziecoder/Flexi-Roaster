import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import type { User, Session } from '@supabase/supabase-js';

export function useAuth() {
    const [user, setUser] = useState<User | null>(null);
    const [session, setSession] = useState<Session | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        let isMounted = true;

        const loadingTimeout = window.setTimeout(() => {
            if (isMounted) {
                setLoading(false);
            }
        }, 5000);

        // Get initial session
        supabase.auth
            .getSession()
            .then(({ data: { session } }) => {
                if (!isMounted) return;

                setSession(session);
                setUser(session?.user ?? null);
            })
            .catch(() => {
                if (!isMounted) return;

                setSession(null);
                setUser(null);
            })
            .finally(() => {
                if (isMounted) {
                    window.clearTimeout(loadingTimeout);
                    setLoading(false);
                }
            });

        // Listen for auth changes
        const {
            data: { subscription },
        } = supabase.auth.onAuthStateChange((_event, session) => {
            if (!isMounted) return;

            window.clearTimeout(loadingTimeout);
            setSession(session);
            setUser(session?.user ?? null);
            setLoading(false);
        });

        return () => {
            isMounted = false;
            window.clearTimeout(loadingTimeout);
            subscription.unsubscribe();
        };
    }, []);

    const signIn = async (email: string, password: string) => {
        const { data, error } = await supabase.auth.signInWithPassword({
            email,
            password,
        });
        return { data, error };
    };

    const signUp = async (email: string, password: string, fullName?: string) => {
        const { data, error } = await supabase.auth.signUp({
            email,
            password,
            options: {
                data: {
                    full_name: fullName,
                },
            },
        });
        return { data, error };
    };

    const signOut = async () => {
        const { error } = await supabase.auth.signOut();
        return { error };
    };

    const signInWithGoogle = async () => {
        const { data, error } = await supabase.auth.signInWithOAuth({
            provider: 'google',
            options: {
                redirectTo: `${window.location.origin}/auth/callback`,
            },
        });
        return { data, error };
    };

    const signInWithGitHub = async () => {
        const { data, error } = await supabase.auth.signInWithOAuth({
            provider: 'github',
            options: {
                redirectTo: `${window.location.origin}/auth/callback`,
            },
        });
        return { data, error };
    };

    const updateProfile = async (updates: { full_name?: string; avatar_url?: string | null }) => {
        const { data, error } = await supabase.auth.updateUser({
            data: updates,
        });
        if (!error && data.user) {
            setUser(data.user);
        }
        return { data, error };
    };

    return {
        user,
        session,
        loading,
        signIn,
        signUp,
        signOut,
        signInWithGoogle,
        signInWithGitHub,
        updateProfile,
    };
}
