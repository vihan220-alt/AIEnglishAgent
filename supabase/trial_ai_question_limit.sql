-- Run once in the Supabase SQL Editor to persist the 20-question trial limit.
alter table public.users
    add column if not exists trial_ai_questions_used integer not null default 0;

grant select, update on public.users to anon, authenticated;
