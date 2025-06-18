-- cat > database/init.sql << 'EOF'
-- Initialize MediConnect AI Database
\c mediconnect;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Note: Tables will be created by SQLAlchemy when the backend starts
-- Grant permissions to the user
GRANT ALL PRIVILEGES ON DATABASE mediconnect TO mediconnect_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO mediconnect_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mediconnect_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO mediconnect_user;

-- Grant default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO mediconnect_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO mediconnect_user;
-- EOF