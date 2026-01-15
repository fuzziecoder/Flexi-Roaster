-- Create FlexiRoaster database if not exists
SELECT 'CREATE DATABASE flexiroaster'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'flexiroaster')\gexec

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE flexiroaster TO airflow;
