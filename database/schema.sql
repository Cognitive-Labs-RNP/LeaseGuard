-- LeaseGuard AI database schema
-- Manual setup: create a Supabase project, enable Email auth, then run this SQL in the SQL Editor.

create extension if not exists pgcrypto;

create table if not exists public.properties (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    property_code text not null,
    name text not null,
    address text,
    city text,
    state text,
    zip_code text,
    square_footage numeric,
    status text not null default 'active',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.documents (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    property_id uuid not null references public.properties(id) on delete cascade,
    document_type text not null,
    title text not null,
    storage_path text,
    file_name text,
    mime_type text,
    file_size bigint,
    status text not null default 'uploaded',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.audits (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    property_id uuid not null references public.properties(id) on delete cascade,
    audit_type text not null,
    title text not null,
    status text not null default 'draft',
    summary text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.findings (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    property_id uuid not null references public.properties(id) on delete cascade,
    audit_id uuid references public.audits(id) on delete cascade,
    finding_type text not null,
    title text not null,
    description text,
    amount numeric default 0,
    severity text default 'medium',
    status text not null default 'open',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.risk_scores (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    property_id uuid not null references public.properties(id) on delete cascade,
    score numeric not null,
    risk_level text not null,
    summary text,
    score_at timestamptz not null default now(),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.recovery_records (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    property_id uuid not null references public.properties(id) on delete cascade,
    audit_id uuid references public.audits(id) on delete cascade,
    claim_amount numeric default 0,
    recovered_amount numeric default 0,
    status text not null default 'Detected' check (status in ('Detected', 'Disputed', 'Under Review', 'Recovered', 'Rejected')),
    notes text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.disputes (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    property_id uuid not null references public.properties(id) on delete cascade,
    audit_id uuid references public.audits(id) on delete cascade,
    recovery_id uuid references public.recovery_records(id) on delete set null,
    title text not null,
    dispute_status text not null default 'Draft' check (dispute_status in ('Draft', 'Submitted', 'Under Review', 'Accepted', 'Rejected', 'Recovered')),
    message text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists idx_properties_user_id on public.properties (user_id);
create index if not exists idx_documents_user_id on public.documents (user_id);
create index if not exists idx_documents_property_id on public.documents (property_id);
create index if not exists idx_audits_user_id on public.audits (user_id);
create index if not exists idx_audits_property_id on public.audits (property_id);
create index if not exists idx_findings_user_id on public.findings (user_id);
create index if not exists idx_findings_audit_id on public.findings (audit_id);
create index if not exists idx_risk_scores_property_id on public.risk_scores (property_id);
create index if not exists idx_recovery_records_user_id on public.recovery_records (user_id);
create index if not exists idx_recovery_records_status on public.recovery_records (status);
create index if not exists idx_disputes_user_id on public.disputes (user_id);
create index if not exists idx_disputes_status on public.disputes (dispute_status);

-- Enable Row Level Security (RLS) on all tables
alter table public.properties enable row level security;
alter table public.documents enable row level security;
alter table public.audits enable row level security;
alter table public.findings enable row level security;
alter table public.risk_scores enable row level security;
alter table public.recovery_records enable row level security;
alter table public.disputes enable row level security;

-- Row Level Security (RLS) Policies (allowing authenticated users access to their own data)

-- 1. Properties Policies
drop policy if exists "Users can view own properties" on public.properties;
drop policy if exists "Users can insert own properties" on public.properties;
drop policy if exists "Users can update own properties" on public.properties;
drop policy if exists "Users can delete own properties" on public.properties;

create policy "Users can view own properties" on public.properties for select using (auth.uid() = user_id);
create policy "Users can insert own properties" on public.properties for insert with check (auth.uid() = user_id);
create policy "Users can update own properties" on public.properties for update using (auth.uid() = user_id);
create policy "Users can delete own properties" on public.properties for delete using (auth.uid() = user_id);

-- 2. Documents Policies
drop policy if exists "Users can view own documents" on public.documents;
drop policy if exists "Users can insert own documents" on public.documents;
drop policy if exists "Users can update own documents" on public.documents;
drop policy if exists "Users can delete own documents" on public.documents;

create policy "Users can view own documents" on public.documents for select using (auth.uid() = user_id);
create policy "Users can insert own documents" on public.documents for insert with check (auth.uid() = user_id);
create policy "Users can update own documents" on public.documents for update using (auth.uid() = user_id);
create policy "Users can delete own documents" on public.documents for delete using (auth.uid() = user_id);

-- 3. Audits Policies
drop policy if exists "Users can view own audits" on public.audits;
drop policy if exists "Users can insert own audits" on public.audits;
drop policy if exists "Users can update own audits" on public.audits;

create policy "Users can view own audits" on public.audits for select using (auth.uid() = user_id);
create policy "Users can insert own audits" on public.audits for insert with check (auth.uid() = user_id);
create policy "Users can update own audits" on public.audits for update using (auth.uid() = user_id);

-- 4. Findings Policies
drop policy if exists "Users can view own findings" on public.findings;
drop policy if exists "Users can insert own findings" on public.findings;
drop policy if exists "Users can update own findings" on public.findings;

create policy "Users can view own findings" on public.findings for select using (auth.uid() = user_id);
create policy "Users can insert own findings" on public.findings for insert with check (auth.uid() = user_id);
create policy "Users can update own findings" on public.findings for update using (auth.uid() = user_id);

-- 5. Risk Scores Policies
drop policy if exists "Users can view own risk scores" on public.risk_scores;
drop policy if exists "Users can insert own risk scores" on public.risk_scores;

create policy "Users can view own risk scores" on public.risk_scores for select using (auth.uid() = user_id);
create policy "Users can insert own risk scores" on public.risk_scores for insert with check (auth.uid() = user_id);

-- 6. Recovery Records Policies
drop policy if exists "Users can view own recovery records" on public.recovery_records;
drop policy if exists "Users can insert own recovery records" on public.recovery_records;
drop policy if exists "Users can update own recovery records" on public.recovery_records;

create policy "Users can view own recovery records" on public.recovery_records for select using (auth.uid() = user_id);
create policy "Users can insert own recovery records" on public.recovery_records for insert with check (auth.uid() = user_id);
create policy "Users can update own recovery records" on public.recovery_records for update using (auth.uid() = user_id);

-- 7. Disputes Policies
drop policy if exists "Users can view own disputes" on public.disputes;
drop policy if exists "Users can insert own disputes" on public.disputes;
drop policy if exists "Users can update own disputes" on public.disputes;

create policy "Users can view own disputes" on public.disputes for select using (auth.uid() = user_id);
create policy "Users can insert own disputes" on public.disputes for insert with check (auth.uid() = user_id);
create policy "Users can update own disputes" on public.disputes for update using (auth.uid() = user_id);
