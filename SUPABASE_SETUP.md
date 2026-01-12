# Supabase Setup Guide

## Prerequisites
- Node.js 18+ installed
- Supabase account (sign up at https://supabase.com)

## Step 1: Create Supabase Project

1. Go to https://supabase.com/dashboard
2. Click "New Project"
3. Fill in:
   - **Name**: FlexiRoaster
   - **Database Password**: (choose a strong password)
   - **Region**: (choose closest to you)
4. Wait for project to be created (~2 minutes)

## Step 2: Get Project Credentials

1. In your Supabase project dashboard, go to **Settings** → **API**
2. Copy the following:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: `eyJhbGc...`
   - **service_role key**: `eyJhbGc...` (keep this secret!)

## Step 3: Install Supabase CLI (Optional but Recommended)

```bash
# Install globally
npm install -g supabase

# Verify installation
supabase --version
```

## Step 4: Configure Environment Variables

### Frontend (.env)
```bash
# Copy template
cp .env.supabase.example .env

# Edit .env and add your credentials
VITE_SUPABASE_URL=https://your-project-ref.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
```

### Backend (backend/.env)
```bash
# Copy template
cp backend/.env.supabase.example backend/.env

# Edit backend/.env and add your credentials
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here
DATABASE_URL=postgresql://postgres:your-password@db.your-project-ref.supabase.co:5432/postgres
```

## Step 5: Run Database Migrations

### Option A: Using Supabase Dashboard (Easiest)

1. Go to **SQL Editor** in your Supabase dashboard
2. Click **New Query**
3. Copy contents of `supabase/migrations/20240112_initial_schema.sql`
4. Paste and click **Run**
5. Repeat for `supabase/migrations/20240112_rls_policies.sql`

### Option B: Using Supabase CLI

```bash
# Link to your project
supabase link --project-ref your-project-ref

# Push migrations
supabase db push
```

## Step 6: Verify Database Setup

1. Go to **Table Editor** in Supabase dashboard
2. You should see these tables:
   - user_profiles
   - pipelines
   - pipeline_stages
   - executions
   - execution_stages
   - logs
   - metrics
   - alerts
   - ai_insights

## Step 7: Configure Authentication

1. Go to **Authentication** → **Providers**
2. Enable **Email** provider
3. (Optional) Enable **Google** or **GitHub** OAuth
4. Go to **Authentication** → **URL Configuration**
5. Add your site URL: `http://localhost:5173` (for development)

## Step 8: Test Connection

### Frontend Test
```bash
# Install Supabase client
npm install @supabase/supabase-js

# Start dev server
npm run dev
```

### Backend Test
```bash
# Install Python dependencies
pip install supabase

# Test connection
python -c "from supabase import create_client; print('✅ Supabase connected!')"
```

## Step 9: Enable Realtime (Important!)

1. Go to **Database** → **Replication**
2. Enable replication for these tables:
   - executions
   - logs
   - metrics
   - alerts
   - ai_insights

## Troubleshooting

### Migration Errors
- Make sure you run migrations in order
- Check for syntax errors in SQL
- Verify you have the correct permissions

### Connection Issues
- Double-check your project URL
- Verify API keys are correct
- Ensure no trailing spaces in .env file

### RLS Issues
- Check if RLS is enabled on tables
- Verify policies are created
- Test with authenticated user

## Next Steps

After setup is complete:
1. ✅ Database schema created
2. ✅ RLS policies configured
3. ✅ Environment variables set
4. → Proceed to Phase 4: Frontend Integration
