-- Create tables for Automated EDA application with Supabase

-- Users table (managed by Supabase Auth, but we'll extend it)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL UNIQUE,
    username TEXT UNIQUE,
    full_name TEXT,
    avatar_url TEXT,
    organization TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Datasets table - stores metadata about uploaded CSV files
CREATE TABLE IF NOT EXISTS public.datasets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    original_file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size_bytes BIGINT,
    row_count INTEGER,
    column_count INTEGER,
    columns JSONB,
    dtypes JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    description TEXT,
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    is_public BOOLEAN DEFAULT FALSE
);

-- Dashboards table - stores generated dashboards
CREATE TABLE IF NOT EXISTS public.dashboards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    dataset_id UUID NOT NULL REFERENCES public.datasets(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    dashboard_type VARCHAR(50), -- 'executive', 'exploratory', 'data_quality'
    html_content TEXT,
    charts_config JSONB,
    ai_insights JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_public BOOLEAN DEFAULT FALSE,
    is_favorite BOOLEAN DEFAULT FALSE
);

-- Analysis Results table - stores analysis history
CREATE TABLE IF NOT EXISTS public.analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    dataset_id UUID NOT NULL REFERENCES public.datasets(id) ON DELETE CASCADE,
    analysis_type VARCHAR(100), -- 'cleaning', 'transformation', 'classification', 'visualization'
    parameters JSONB,
    results JSONB,
    charts JSONB,
    processing_time_ms INTEGER,
    status VARCHAR(20) DEFAULT 'completed', -- 'pending', 'processing', 'completed', 'failed'
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Charts table - stores individual chart configurations
CREATE TABLE IF NOT EXISTS public.charts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dashboard_id UUID REFERENCES public.dashboards(id) ON DELETE CASCADE,
    analysis_id UUID REFERENCES public.analyses(id) ON DELETE CASCADE,
    chart_type VARCHAR(50), -- 'histogram', 'scatter', 'heatmap', 'box', 'bar', etc.
    title TEXT,
    description TEXT,
    chart_config JSONB,
    chart_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sharing/Collaborations table
CREATE TABLE IF NOT EXISTS public.sharing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dashboard_id UUID NOT NULL REFERENCES public.dashboards(id) ON DELETE CASCADE,
    shared_by_user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    shared_with_email TEXT,
    shared_with_user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    access_level VARCHAR(20) DEFAULT 'view', -- 'view', 'comment', 'edit'
    share_token TEXT UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- File Storage Metadata table
CREATE TABLE IF NOT EXISTS public.file_uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size_bytes BIGINT,
    mime_type TEXT,
    storage_path TEXT, -- Path in Supabase Storage
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_datasets_user_id ON public.datasets(user_id);
CREATE INDEX IF NOT EXISTS idx_datasets_created_at ON public.datasets(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_dashboards_user_id ON public.dashboards(user_id);
CREATE INDEX IF NOT EXISTS idx_dashboards_dataset_id ON public.dashboards(dataset_id);
CREATE INDEX IF NOT EXISTS idx_dashboards_created_at ON public.dashboards(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON public.analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_dataset_id ON public.analyses(dataset_id);
CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON public.analyses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_charts_dashboard_id ON public.charts(dashboard_id);
CREATE INDEX IF NOT EXISTS idx_sharing_dashboard_id ON public.sharing(dashboard_id);
CREATE INDEX IF NOT EXISTS idx_file_uploads_user_id ON public.file_uploads(user_id);

-- Enable Row Level Security (RLS)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.datasets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dashboards ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.charts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sharing ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.file_uploads ENABLE ROW LEVEL SECURITY;

-- Create RLS Policies

-- Users policies
CREATE POLICY "Users can view their own profile"
    ON public.users FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
    ON public.users FOR UPDATE
    USING (auth.uid() = id);

-- Datasets policies
CREATE POLICY "Users can view their own datasets"
    ON public.datasets FOR SELECT
    USING (auth.uid() = user_id OR is_public = TRUE);

CREATE POLICY "Users can create datasets"
    ON public.datasets FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own datasets"
    ON public.datasets FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own datasets"
    ON public.datasets FOR DELETE
    USING (auth.uid() = user_id);

-- Dashboards policies
CREATE POLICY "Users can view their own dashboards"
    ON public.dashboards FOR SELECT
    USING (auth.uid() = user_id OR is_public = TRUE);

CREATE POLICY "Users can create dashboards"
    ON public.dashboards FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own dashboards"
    ON public.dashboards FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own dashboards"
    ON public.dashboards FOR DELETE
    USING (auth.uid() = user_id);

-- Analyses policies
CREATE POLICY "Users can view their own analyses"
    ON public.analyses FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create analyses"
    ON public.analyses FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own analyses"
    ON public.analyses FOR UPDATE
    USING (auth.uid() = user_id);

-- Charts policies
CREATE POLICY "Users can view charts in shared dashboards"
    ON public.charts FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.dashboards
            WHERE dashboards.id = charts.dashboard_id
            AND (dashboards.user_id = auth.uid() OR dashboards.is_public = TRUE)
        )
    );

-- File uploads policies
CREATE POLICY "Users can view their own file uploads"
    ON public.file_uploads FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create file uploads"
    ON public.file_uploads FOR INSERT
    WITH CHECK (auth.uid() = user_id);
