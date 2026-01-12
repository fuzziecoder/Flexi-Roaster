-- Complete fix for user_profiles RLS policies
-- Run this in Supabase SQL Editor

-- First, drop all existing policies on user_profiles
DROP POLICY IF EXISTS "Users can view all profiles" ON public.user_profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Users can insert and update own profile" ON public.user_profiles;

-- Create new comprehensive policies
-- Allow users to view all profiles
CREATE POLICY "Users can view all profiles"
ON public.user_profiles
FOR SELECT
USING (auth.role() = 'authenticated');

-- Allow users to insert their own profile
CREATE POLICY "Users can insert own profile"
ON public.user_profiles
FOR INSERT
WITH CHECK (auth.uid() = id);

-- Allow users to update their own profile
CREATE POLICY "Users can update own profile"
ON public.user_profiles
FOR UPDATE
USING (auth.uid() = id)
WITH CHECK (auth.uid() = id);

-- Allow service role full access
CREATE POLICY "Service role has full access"
ON public.user_profiles
FOR ALL
USING (auth.jwt()->>'role' = 'service_role');
