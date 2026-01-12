import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '@/lib/supabase';

export function AuthCallback() {
    const navigate = useNavigate();

    useEffect(() => {
        // Handle the OAuth callback
        supabase.auth.getSession().then(({ data: { session } }) => {
            if (session) {
                // Successfully authenticated, redirect to dashboard
                navigate('/', { replace: true });
            } else {
                // No session, redirect to login
                navigate('/login', { replace: true });
            }
        });
    }, [navigate]);

    return (
        <div className="min-h-screen flex items-center justify-center" style={{ background: 'hsl(var(--background))' }}>
            <div className="text-center">
                <div className="w-16 h-16 border-4 border-white/20 border-t-white rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-white/70">Completing sign in...</p>
            </div>
        </div>
    );
}
