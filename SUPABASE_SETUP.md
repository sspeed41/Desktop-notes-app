# Supabase Integration Setup Guide

## Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign up/login
2. Click "New Project" 
3. Choose your organization
4. Enter project name: "WiseDesktopNoteApp" (or your preferred name)
5. Enter a strong database password
6. Choose your region (closest to you for better performance)
7. Click "Create new project"

## Step 2: Get Your Credentials

Once your project is created:

1. Go to Settings → API
2. Copy the following values:
   - **Project URL** (something like `https://your-project.supabase.co`)
   - **anon/public key** (starts with `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)
   - **service_role key** (also starts with `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)

## Step 3: Create .env File

Create a `.env` file in your project root with:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE=your_service_role_key_here

# App Configuration  
ORG_ID=your_organization_name
LOG_LEVEL=INFO
```

**Replace the placeholder values with your actual Supabase credentials.**

## Step 4: Setup Database Schema

1. In your Supabase dashboard, go to SQL Editor
2. Copy the contents of `supabase/schema.sql` 
3. Paste it into the SQL Editor
4. Click "Run" to create all tables and sample data

## Step 5: Test Connection

After creating the `.env` file, run:
```bash
python3 run_app.py
```

You should see:
- ✅ Successful database connection (no "offline mode" warning)
- ✅ Loaded tracks, series, and tags from Supabase
- ✅ Application ready to create and sync notes

## Troubleshooting

**Connection Issues:**
- Verify your SUPABASE_URL starts with `https://`
- Check that your keys are copied completely (they're quite long)
- Make sure your `.env` file is in the project root directory

**Schema Issues:** 
- If you get table errors, make sure you ran the full `schema.sql` script
- Check the Supabase dashboard → Database → Tables to verify tables exist

**Permission Issues:**
- The app uses the anon key for regular operations
- Service role key is for admin operations (media uploads, etc.)

## Features Available After Integration

Once connected, you'll have:
- ✅ **Real-time note syncing** across devices
- ✅ **Track/Series/Driver management** 
- ✅ **Tag system** for organizing notes
- ✅ **Media attachments** (images, videos, CSV files)
- ✅ **Session tracking** (Practice, Qualifying, Race)
- ✅ **Offline support** with sync when reconnected
- ✅ **Full racing context** for each note 