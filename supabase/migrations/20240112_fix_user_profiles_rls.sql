-- Fix RLS policy for user_profiles to allow inserts
-- Run this in Supabase SQL Editor

-- Drop existing policies
DROP POLICY IF EXISTS "Users can update own profile" ON public.user_profiles;

-- Recreate with INSERT permission
CREATE POLICY "Users can insert and update own profile"
ON public.user_profiles
FOR ALL
USING (auth.uid() = id)
WITH CHECK (auth.uid() = id);
