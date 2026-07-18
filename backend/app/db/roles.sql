
-- Optional read-only role for the agent.
-- plans the app user doesn't have CREATEROLE, and that shouldn't block
-- the schema/data from being seeded.


DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'analytics_readonly') THEN
      CREATE ROLE analytics_readonly LOGIN PASSWORD 'readonly_pw';
   END IF;
END
$$;

DO $$
BEGIN
   EXECUTE format('GRANT CONNECT ON DATABASE %I TO analytics_readonly', current_database());
END
$$;

GRANT USAGE ON SCHEMA public TO analytics_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO analytics_readonly;