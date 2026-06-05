-- C3PO Database Initialization Script
-- This script runs automatically when the PostgreSQL container starts

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create extensions for full-text search (optional)
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Grant necessary privileges
GRANT ALL PRIVILEGES ON DATABASE c3po_db TO c3po;

-- Create read-only role for monitoring (optional)
-- CREATE ROLE c3po_readonly WITH LOGIN PASSWORD 'readonly_password';
-- GRANT CONNECT ON DATABASE c3po_db TO c3po_readonly;
-- GRANT USAGE ON SCHEMA public TO c3po_readonly;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO c3po_readonly;

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'C3PO Database initialized successfully!';
END $$;