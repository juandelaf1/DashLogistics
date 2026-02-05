# Supabase Setup (MVP)

This document describes minimal steps to use Supabase for the app database.

Options:

1) Use Supabase managed service (recommended)
   - Create a project at https://app.supabase.com
   - Copy `SUPABASE_URL` and `SUPABASE_KEY` (service role or anon key depending on needs)
   - Set `DATABASE_URL` in your `.env` to the provided Postgres connection string OR set `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
   - Run migrations or let the app create tables on first run (depending on your preference)

2) Self-host Postgres via Docker (local dev)
   - `docker-compose -f docker-compose.supabase.yml up -d`
   - Update `.env` (or use `.env.local`) with `DATABASE_URL=postgresql://postgres:admin@localhost:5432/shipping_db`
   - Start the app

Notes and tips:
- Use `psql` or a GUI (pgAdmin, TablePlus) to inspect tables created by the ETL.
- When using managed Supabase, store `SUPABASE_KEY` in CI secrets and use `DATABASE_URL` in the app's environment for production deployments.
- If you want, I can add migration tooling (Alembic) and initial migration files to manage DB schema changes explicitly.
