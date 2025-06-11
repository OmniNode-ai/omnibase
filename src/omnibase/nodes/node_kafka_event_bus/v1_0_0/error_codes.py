# AUTO-GENERATED FILE. DO NOT EDIT.
# Generated from contract.yaml
# contract_hash: 65b9c3cff66c3d122a076f5545df3e29b7056e2c1811c330feb68542bd2db7da
# To regenerate: poetry run python src/omnibase/runtimes/onex_runtime/v1_0_0/codegen/contract_to_model.py --contract src/omnibase/nodes/node_kafka_event_bus/v1_0_0/contract.yaml --output-dir src/omnibase/nodes/node_kafka_event_bus/v1_0_0/models

from enum import Enum

class NodeKafkaEventBusNodeErrorCode(Enum):
    BACKEND_UNAVAILABLE = 'BACKEND_UNAVAILABLE'
    CONNECTION_FAILED = 'CONNECTION_FAILED'
    MESSAGE_PUBLISH_FAILED = 'MESSAGE_PUBLISH_FAILED'
    MESSAGE_CONSUME_FAILED = 'MESSAGE_CONSUME_FAILED'
    TIMEOUT_EXCEEDED = 'TIMEOUT_EXCEEDED'
    CONFIGURATION_ERROR = 'CONFIGURATION_ERROR'
    HANDLER_NOT_FOUND = 'HANDLER_NOT_FOUND'
    BOOTSTRAP_FAILED = 'BOOTSTRAP_FAILED'
    INTEGRATION_ERROR = 'INTEGRATION_ERROR'
    RESOURCE_EXHAUSTED = 'RESOURCE_EXHAUSTED'
