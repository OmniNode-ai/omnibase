# Node-specific constants for node_kafka_event_bus
# Only include values unique to this node. All generic/shared constants are in src/omnibase/constants.py

PROTOCOL_KAFKA = "kafka"
DEBUG_ENTERED_RUN = "[DEBUG] Entered NodeKafkaEventBus.run()"
NODE_KAFKA_EVENT_BUS_SUCCESS_MSG = "NodeKafkaEventBus ran successfully."
NODE_KAFKA_EVENT_BUS_SUCCESS_EVENT_MSG = "NodeKafkaEventBus ran successfully (event-driven)"
NODE_KAFKA_EVENT_BUS_ID = "node_kafka_event_bus"
INPUT_VALIDATION_SUCCEEDED_MSG = "Input validation succeeded"
INPUT_REQUIRED_FIELD_ERROR_TEMPLATE = "Input should have required field '{missing_field}'"
INPUT_MISSING_REQUIRED_FIELD_ERROR = "Input is missing a required field"
