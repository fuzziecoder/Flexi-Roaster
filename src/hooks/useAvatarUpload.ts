import { useState } from 'react';
import { supabase } from '@/lib/supabase';
import { useAuth } from './useAuth';

export function useAvatarUpload() {
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const { user } = useAuth();

    const uploadAvatar = async (file: File) => {
        try {
            setUploading(true);
            setError(null);

            if (!user) {
                throw new Error('No user logged in');
            }

            // Validate file type
            if (!file.type.startsWith('image/')) {
                throw new Error('Please upload an image file');
            }

            // Validate file size (max 2MB)
            if (file.size > 2 * 1024 * 1024) {
                throw new Error('File size must be less than 2MB');
            }

            // Create unique filename
            const fileExt = file.name.split('.').pop();
            const fileName = `${user.id}-${Math.random()}.${fileExt}`;
            const filePath = `avatars/${fileName}`;

            // Upload to Supabase Storage
            const { error: uploadError } = await supabase.storage
                .from('avatars')
                .upload(filePath, file, {
                    cacheControl: '3600',
                    upsert: true,
                });

            if (uploadError) {
                throw uploadError;
            }

            // Get public URL
            const { data: { publicUrl } } = supabase.storage
                .from('avatars')
                .getPublicUrl(filePath);

            // Update user metadata
            const { error: updateError } = await supabase.auth.updateUser({
                data: {
                    avatar_url: publicUrl,
                },
            });

            if (updateError) {
                throw updateError;
            }

            return { publicUrl, error: null };
        } catch (err: any) {
            const errorMessage = err.message || 'Failed to upload avatar';
            setError(errorMessage);
            return { publicUrl: null, error: errorMessage };
        } finally {
            setUploading(false);
        }
    };

    const removeAvatar = async () => {
        try {
            setUploading(true);
            setError(null);

            if (!user) {
                throw new Error('No user logged in');
            }

            // Clear avatar_url in user metadata
            const { error: updateError } = await supabase.auth.updateUser({
                data: {
                    avatar_url: null,
                },
            });

            if (updateError) {
                throw updateError;
            }

            return { error: null };
        } catch (err: any) {
            const errorMessage = err.message || 'Failed to remove avatar';
            setError(errorMessage);
            return { error: errorMessage };
        } finally {
            setUploading(false);
        }
    };

    return { uploadAvatar, removeAvatar, uploading, error };
}
