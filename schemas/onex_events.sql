-- Canonical ONEX event store schema for Postgres
-- Stores all emitted events for durability and audit

CREATE TABLE IF NOT EXISTS onex_events (
    event_id UUID PRIMARY KEY, -- Unique event identifier
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL, -- Event timestamp (UTC)
    node_id TEXT NOT NULL, -- ID of the node emitting the event
    event_type TEXT NOT NULL, -- Type of event emitted (e.g., NODE_START, NODE_SUCCESS, NODE_FAILURE)
    metadata JSONB -- Optional event metadata or payload
);

-- Index for fast lookup by node_id and event_type
CREATE INDEX IF NOT EXISTS idx_onex_events_node_id ON onex_events(node_id);
CREATE INDEX IF NOT EXISTS idx_onex_events_event_type ON onex_events(event_type); 