-- ONEX Development Database Initialization Script
-- This script sets up the basic database structure for ONEX development

-- Create additional databases for testing
CREATE DATABASE onex_test;
CREATE DATABASE onex_integration;

-- Create schemas for different ONEX components
\c onex_dev;

CREATE SCHEMA IF NOT EXISTS onex_core;
CREATE SCHEMA IF NOT EXISTS onex_nodes;
CREATE SCHEMA IF NOT EXISTS onex_scenarios;
CREATE SCHEMA IF NOT EXISTS onex_telemetry;

-- Create basic tables for ONEX metadata and logging
CREATE TABLE IF NOT EXISTS onex_core.node_metadata (
    id SERIAL PRIMARY KEY,
    node_id VARCHAR(255) NOT NULL UNIQUE,
    node_name VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB,
    status VARCHAR(50) DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS onex_core.scenario_executions (
    id SERIAL PRIMARY KEY,
    correlation_id UUID NOT NULL,
    scenario_id VARCHAR(255) NOT NULL,
    node_id VARCHAR(255) NOT NULL,
    dependency_mode VARCHAR(20) NOT NULL DEFAULT 'mock',
    status VARCHAR(50) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    execution_time_ms INTEGER,
    input_data JSONB,
    output_data JSONB,
    error_data JSONB,
    precondition_results JSONB
);

CREATE TABLE IF NOT EXISTS onex_telemetry.structured_logs (
    id SERIAL PRIMARY KEY,
    correlation_id UUID,
    node_id VARCHAR(255),
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    context JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    calling_module VARCHAR(500),
    calling_function VARCHAR(255),
    calling_line INTEGER
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_node_metadata_node_id ON onex_core.node_metadata(node_id);
CREATE INDEX IF NOT EXISTS idx_scenario_executions_correlation_id ON onex_core.scenario_executions(correlation_id);
CREATE INDEX IF NOT EXISTS idx_scenario_executions_node_id ON onex_core.scenario_executions(node_id);
CREATE INDEX IF NOT EXISTS idx_scenario_executions_status ON onex_core.scenario_executions(status);
CREATE INDEX IF NOT EXISTS idx_structured_logs_correlation_id ON onex_telemetry.structured_logs(correlation_id);
CREATE INDEX IF NOT EXISTS idx_structured_logs_node_id ON onex_telemetry.structured_logs(node_id);
CREATE INDEX IF NOT EXISTS idx_structured_logs_level ON onex_telemetry.structured_logs(level);
CREATE INDEX IF NOT EXISTS idx_structured_logs_timestamp ON onex_telemetry.structured_logs(timestamp);

-- Grant permissions to onex_user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA onex_core TO onex_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA onex_nodes TO onex_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA onex_scenarios TO onex_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA onex_telemetry TO onex_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA onex_core TO onex_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA onex_nodes TO onex_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA onex_scenarios TO onex_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA onex_telemetry TO onex_user;

-- Set up the same structure for test databases
\c onex_test;

CREATE SCHEMA IF NOT EXISTS onex_core;
CREATE SCHEMA IF NOT EXISTS onex_nodes;
CREATE SCHEMA IF NOT EXISTS onex_scenarios;
CREATE SCHEMA IF NOT EXISTS onex_telemetry;

-- Copy table structures to test database
CREATE TABLE IF NOT EXISTS onex_core.node_metadata (LIKE onex_dev.onex_core.node_metadata INCLUDING ALL);
CREATE TABLE IF NOT EXISTS onex_core.scenario_executions (LIKE onex_dev.onex_core.scenario_executions INCLUDING ALL);
CREATE TABLE IF NOT EXISTS onex_telemetry.structured_logs (LIKE onex_dev.onex_telemetry.structured_logs INCLUDING ALL);

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA onex_core TO onex_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA onex_nodes TO onex_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA onex_scenarios TO onex_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA onex_telemetry TO onex_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA onex_core TO onex_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA onex_nodes TO onex_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA onex_scenarios TO onex_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA onex_telemetry TO onex_user;

-- Set up the same structure for integration database
\c onex_integration;

CREATE SCHEMA IF NOT EXISTS onex_core;
CREATE SCHEMA IF NOT EXISTS onex_nodes;
CREATE SCHEMA IF NOT EXISTS onex_scenarios;
CREATE SCHEMA IF NOT EXISTS onex_telemetry;

CREATE TABLE IF NOT EXISTS onex_core.node_metadata (LIKE onex_dev.onex_core.node_metadata INCLUDING ALL);
CREATE TABLE IF NOT EXISTS onex_core.scenario_executions (LIKE onex_dev.onex_core.scenario_executions INCLUDING ALL);
CREATE TABLE IF NOT EXISTS onex_telemetry.structured_logs (LIKE onex_dev.onex_telemetry.structured_logs INCLUDING ALL);

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA onex_core TO onex_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA onex_nodes TO onex_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA onex_scenarios TO onex_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA onex_telemetry TO onex_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA onex_core TO onex_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA onex_nodes TO onex_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA onex_scenarios TO onex_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA onex_telemetry TO onex_user; 