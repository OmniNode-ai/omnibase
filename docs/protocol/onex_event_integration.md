<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 0.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 0.1.0
name: onex_event_integration.md
version: 1.0.0
uuid: 44fa3ee2-83d3-41ca-bb12-1f63f17d1998
author: OmniNode Team
created_at: '2025-05-28T12:40:26.933167'
last_modified_at: '1970-01-01T00:00:00Z'
description: Stamped by MarkdownHandler
state_contract: state_contract://default
lifecycle: active
hash: '0000000000000000000000000000000000000000000000000000000000000000'
entrypoint: markdown://onex_event_integration
namespace: markdown://onex_event_integration
meta_type: tool

<!-- === /OmniNode:Metadata === -->
# ONEX Event Integration Patterns

> **Version:** 1.0.0  
> **Status:** Draft  
> **Last Updated:** 2025-05-25  
> **Purpose:** Integration patterns for ONEX events with external monitoring and observability systems

## Overview

This document provides patterns and guidelines for integrating the ONEX event system with external monitoring, logging, and observability platforms. It covers common integration scenarios and provides implementation examples.

## Integration Architecture

### Event Flow Overview

```
ONEX Nodes → Event Bus → Integration Layer → External Systems
    ↓           ↓              ↓               ↓
  Events    Routing      Transformation    Monitoring
            Filtering    Enrichment        Alerting
            Batching     Format Conversion  Storage
```

### Integration Layer Components

1. **Event Router**: Routes events to appropriate external systems
2. **Event Transformer**: Converts ONEX events to external formats
3. **Event Enricher**: Adds context and metadata for external systems
4. **Event Buffer**: Batches and buffers events for efficient transmission

## Common Integration Patterns

### 1. Observability Platform Integration

#### Prometheus + Grafana

**Event to Metrics Conversion:**

```python
from prometheus_client import Counter, Histogram, Gauge
import time

class PrometheusEventIntegration:
    def __init__(self):
        # Metrics
        self.events_total = Counter(
            'onex_events_total',
            'Total ONEX events',
            ['event_type', 'node_id', 'status']
        )
        
        self.operation_duration = Histogram(
            'onex_operation_duration_seconds',
            'Operation duration',
            ['node_id', 'operation']
        )
        
        self.active_operations = Gauge(
            'onex_active_operations',
            'Active operations',
            ['node_id']
        )
    
    def process_event(self, event: OnexEvent):
        # Convert event to metrics
        if event.event_type == OnexEventTypeEnum.NODE_START:
            self.events_total.labels(
                event_type='node_start',
                node_id=event.node_id,
                status='started'
            ).inc()
            self.active_operations.labels(node_id=event.node_id).inc()
            
        elif event.event_type == OnexEventTypeEnum.NODE_SUCCESS:
            self.events_total.labels(
                event_type='node_success',
                node_id=event.node_id,
                status='success'
            ).inc()
            self.active_operations.labels(node_id=event.node_id).dec()
            
            # Record duration if available
            if 'duration_ms' in event.metadata:
                duration_seconds = event.metadata['duration_ms'] / 1000
                self.operation_duration.labels(
                    node_id=event.node_id,
                    operation=event.metadata.get('operation', 'unknown')
                ).observe(duration_seconds)
```

**Grafana Dashboard Configuration:**

```json
{
  "dashboard": {
    "title": "ONEX System Overview",
    "panels": [
      {
        "title": "Event Rate by Type",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(onex_events_total[5m])",
            "legendFormat": "{{event_type}} - {{node_id}}"
          }
        ]
      },
      {
        "title": "Operation Duration",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(onex_operation_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Active Operations",
        "type": "singlestat",
        "targets": [
          {
            "expr": "sum(onex_active_operations)"
          }
        ]
      }
    ]
  }
}
```

#### Datadog Integration

```python
import datadog
from datadog import statsd

class DatadogEventIntegration:
    def __init__(self, api_key: str, app_key: str):
        datadog.initialize(api_key=api_key, app_key=app_key)
        self.statsd = statsd
    
    def process_event(self, event: OnexEvent):
        # Send metrics
        tags = [
            f"node_id:{event.node_id}",
            f"event_type:{event.event_type}",
            f"correlation_id:{event.correlation_id}"
        ]
        
        self.statsd.increment('onex.events.total', tags=tags)
        
        # Send event to Datadog Events API
        if event.event_type in [OnexEventTypeEnum.NODE_FAILURE]:
            datadog.api.Event.create(
                title=f"ONEX Node Failure: {event.node_id}",
                text=f"Node {event.node_id} failed: {event.metadata.get('error', 'Unknown error')}",
                alert_type='error',
                tags=tags
            )
        
        # Send duration metrics
        if 'duration_ms' in event.metadata:
            self.statsd.histogram(
                'onex.operation.duration',
                event.metadata['duration_ms'],
                tags=tags
            )
```

### 2. Logging Platform Integration

#### ELK Stack (Elasticsearch, Logstash, Kibana)

**Logstash Configuration:**

```ruby
# logstash.conf
input {
  http {
    port => 8080
    codec => json
  }
}

filter {
  if [event_type] {
    mutate {
      add_field => { "[@metadata][index_name]" => "onex-events-%{+YYYY.MM.dd}" }
    }
    
    # Parse timestamp
    date {
      match => [ "timestamp", "ISO8601" ]
    }
    
    # Add computed fields
    if [metadata][duration_ms] {
      ruby {
        code => "event.set('duration_seconds', event.get('[metadata][duration_ms]').to_f / 1000)"
      }
    }
    
    # Categorize events
    if [event_type] == "NODE_FAILURE" {
      mutate {
        add_tag => [ "error", "alert" ]
        add_field => { "severity" => "error" }
      }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "%{[@metadata][index_name]}"
  }
}
```

**Python Integration:**

```python
import requests
import json

class ELKEventIntegration:
    def __init__(self, logstash_url: str):
        self.logstash_url = logstash_url
    
    def process_event(self, event: OnexEvent):
        # Convert to ELK format
        elk_event = {
            "@timestamp": event.timestamp,
            "event_type": event.event_type,
            "node_id": event.node_id,
            "correlation_id": event.correlation_id,
            "metadata": event.metadata,
            "source": "onex",
            "version": "1.0.0"
        }
        
        # Add computed fields
        if 'duration_ms' in event.metadata:
            elk_event['duration_seconds'] = event.metadata['duration_ms'] / 1000
        
        # Send to Logstash
        try:
            response = requests.post(
                self.logstash_url,
                json=elk_event,
                timeout=5
            )
            response.raise_for_status()
        except requests.RequestException as e:
            # Handle error (log, retry, etc.)
            print(f"Failed to send event to ELK: {e}")
```

#### Splunk Integration

```python
import splunklib.client as client

class SplunkEventIntegration:
    def __init__(self, host: str, port: int, username: str, password: str):
        self.service = client.connect(
            host=host,
            port=port,
            username=username,
            password=password
        )
        self.index = self.service.indexes['onex_events']
    
    def process_event(self, event: OnexEvent):
        # Format for Splunk
        splunk_event = {
            "time": event.timestamp,
            "source": "onex",
            "sourcetype": "onex:event",
            "event": {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "node_id": event.node_id,
                "correlation_id": event.correlation_id,
                **event.metadata
            }
        }
        
        # Submit to Splunk
        self.index.submit(json.dumps(splunk_event))
```

### 3. Distributed Tracing Integration

#### Jaeger Integration

```python
from jaeger_client import Config
from opentracing import tracer
import opentracing

class JaegerEventIntegration:
    def __init__(self, service_name: str = "onex"):
        config = Config(
            config={
                'sampler': {'type': 'const', 'param': 1},
                'logging': True,
            },
            service_name=service_name
        )
        self.tracer = config.initialize_tracer()
    
    def process_event(self, event: OnexEvent):
        # Create span from event
        with self.tracer.start_span(
            operation_name=f"onex.{event.event_type.lower()}",
            tags={
                'node.id': event.node_id,
                'event.type': event.event_type,
                'correlation.id': event.correlation_id
            }
        ) as span:
            
            # Add metadata as tags
            for key, value in event.metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    span.set_tag(f"metadata.{key}", value)
            
            # Set span status based on event type
            if event.event_type == OnexEventTypeEnum.NODE_FAILURE:
                span.set_tag('error', True)
                span.log_kv({'event': 'error', 'message': event.metadata.get('error', 'Unknown error')})
```

#### Zipkin Integration

```python
from py_zipkin.zipkin import zipkin_span
import requests

class ZipkinEventIntegration:
    def __init__(self, zipkin_url: str):
        self.zipkin_url = zipkin_url
    
    def http_transport(self, encoded_span):
        requests.post(
            f"{self.zipkin_url}/api/v2/spans",
            data=encoded_span,
            headers={'Content-Type': 'application/json'}
        )
    
    def process_event(self, event: OnexEvent):
        with zipkin_span(
            service_name='onex',
            span_name=f"onex.{event.event_type.lower()}",
            transport_handler=self.http_transport,
            sample_rate=1.0
        ) as span:
            span.add_annotation('event.processed')
            span.add_binary_annotation('node.id', event.node_id)
            span.add_binary_annotation('correlation.id', event.correlation_id)
```

### 4. Alerting Integration

#### PagerDuty Integration

```python
import pypd

class PagerDutyEventIntegration:
    def __init__(self, integration_key: str):
        pypd.api_key = integration_key
        self.integration_key = integration_key
    
    def process_event(self, event: OnexEvent):
        # Only alert on failures
        if event.event_type == OnexEventTypeEnum.NODE_FAILURE:
            incident = pypd.Incident.create(
                title=f"ONEX Node Failure: {event.node_id}",
                service=pypd.Service.find_one(name="ONEX"),
                incident_key=event.correlation_id,
                details={
                    'node_id': event.node_id,
                    'error': event.metadata.get('error', 'Unknown error'),
                    'timestamp': event.timestamp,
                    'correlation_id': event.correlation_id
                }
            )
```

#### Slack Integration

```python
import slack_sdk

class SlackEventIntegration:
    def __init__(self, token: str, channel: str):
        self.client = slack_sdk.WebClient(token=token)
        self.channel = channel
    
    def process_event(self, event: OnexEvent):
        # Send notifications for important events
        if event.event_type in [OnexEventTypeEnum.NODE_FAILURE, OnexEventTypeEnum.NODE_SUCCESS]:
            
            color = "danger" if event.event_type == OnexEventTypeEnum.NODE_FAILURE else "good"
            
            attachment = {
                "color": color,
                "title": f"ONEX Event: {event.event_type}",
                "fields": [
                    {"title": "Node ID", "value": event.node_id, "short": True},
                    {"title": "Correlation ID", "value": event.correlation_id, "short": True},
                    {"title": "Timestamp", "value": event.timestamp, "short": True}
                ]
            }
            
            # Add error details for failures
            if event.event_type == OnexEventTypeEnum.NODE_FAILURE:
                attachment["fields"].append({
                    "title": "Error",
                    "value": event.metadata.get('error', 'Unknown error'),
                    "short": False
                })
            
            self.client.chat_postMessage(
                channel=self.channel,
                text=f"ONEX {event.event_type}",
                attachments=[attachment]
            )
```

## Event Transformation Patterns

### Format Conversion

#### CloudEvents Format

```python
from cloudevents.http import CloudEvent

class CloudEventsTransformer:
    def transform_event(self, event: OnexEvent) -> CloudEvent:
        return CloudEvent({
            "type": f"com.onex.{event.event_type.lower()}",
            "source": f"onex/{event.node_id}",
            "id": event.event_id,
            "time": event.timestamp,
            "datacontenttype": "application/json",
            "data": {
                "correlation_id": event.correlation_id,
                "metadata": event.metadata
            }
        })
```

#### OpenTelemetry Format

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

class OpenTelemetryTransformer:
    def __init__(self):
        trace.set_tracer_provider(TracerProvider())
        tracer = trace.get_tracer(__name__)
        
        jaeger_exporter = JaegerExporter(
            agent_host_name="localhost",
            agent_port=6831,
        )
        
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        self.tracer = tracer
    
    def transform_event(self, event: OnexEvent):
        with self.tracer.start_as_current_span(
            f"onex.{event.event_type.lower()}"
        ) as span:
            span.set_attribute("onex.node_id", event.node_id)
            span.set_attribute("onex.correlation_id", event.correlation_id)
            span.set_attribute("onex.event_type", event.event_type)
            
            # Add metadata as attributes
            for key, value in event.metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    span.set_attribute(f"onex.metadata.{key}", value)
```

## Integration Middleware

### Event Router

```python
from typing import List, Callable
from enum import Enum

class IntegrationType(Enum):
    METRICS = "metrics"
    LOGGING = "logging"
    TRACING = "tracing"
    ALERTING = "alerting"

class EventRouter:
    def __init__(self):
        self.integrations: Dict[IntegrationType, List[Callable]] = {
            IntegrationType.METRICS: [],
            IntegrationType.LOGGING: [],
            IntegrationType.TRACING: [],
            IntegrationType.ALERTING: []
        }
    
    def register_integration(self, integration_type: IntegrationType, handler: Callable):
        self.integrations[integration_type].append(handler)
    
    def route_event(self, event: OnexEvent):
        # Route to all registered integrations
        for integration_type, handlers in self.integrations.items():
            for handler in handlers:
                try:
                    handler(event)
                except Exception as e:
                    # Log error but continue processing
                    print(f"Integration error in {integration_type}: {e}")

# Usage
router = EventRouter()
router.register_integration(IntegrationType.METRICS, prometheus_integration.process_event)
router.register_integration(IntegrationType.LOGGING, elk_integration.process_event)
router.register_integration(IntegrationType.ALERTING, pagerduty_integration.process_event)
```

### Event Buffer

```python
import asyncio
from collections import defaultdict
import time

class EventBuffer:
    def __init__(self, max_size: int = 100, max_age_seconds: int = 30):
        self.max_size = max_size
        self.max_age_seconds = max_age_seconds
        self.buffers = defaultdict(list)
        self.buffer_timestamps = defaultdict(float)
    
    async def add_event(self, integration_type: IntegrationType, event: OnexEvent):
        buffer = self.buffers[integration_type]
        buffer.append(event)
        
        # Set timestamp for first event in buffer
        if len(buffer) == 1:
            self.buffer_timestamps[integration_type] = time.time()
        
        # Flush if buffer is full or old
        if (len(buffer) >= self.max_size or 
            time.time() - self.buffer_timestamps[integration_type] >= self.max_age_seconds):
            await self.flush_buffer(integration_type)
    
    async def flush_buffer(self, integration_type: IntegrationType):
        buffer = self.buffers[integration_type]
        if not buffer:
            return
        
        # Process batch
        await self._process_batch(integration_type, buffer.copy())
        
        # Clear buffer
        buffer.clear()
        del self.buffer_timestamps[integration_type]
    
    async def _process_batch(self, integration_type: IntegrationType, events: List[OnexEvent]):
        # Send batch to appropriate integration
        pass
```

## Configuration Management

### Integration Configuration

```yaml
# integration_config.yaml
integrations:
  prometheus:
    enabled: true
    endpoint: "http://prometheus:9090"
    push_gateway: "http://pushgateway:9091"
    
  datadog:
    enabled: true
    api_key: "${DATADOG_API_KEY}"
    app_key: "${DATADOG_APP_KEY}"
    
  elk:
    enabled: true
    logstash_url: "http://logstash:8080"
    
  jaeger:
    enabled: true
    agent_host: "jaeger"
    agent_port: 6831
    
  pagerduty:
    enabled: true
    integration_key: "${PAGERDUTY_INTEGRATION_KEY}"
    
  slack:
    enabled: true
    token: "${SLACK_TOKEN}"
    channel: "#onex-alerts"

routing:
  rules:
    - event_types: ["NODE_FAILURE"]
      integrations: ["pagerduty", "slack", "elk"]
      
    - event_types: ["NODE_SUCCESS", "NODE_START"]
      integrations: ["prometheus", "elk", "jaeger"]
      
    - event_types: ["TELEMETRY_OPERATION_*"]
      integrations: ["prometheus", "datadog"]

buffering:
  enabled: true
  max_size: 100
  max_age_seconds: 30
```

### Configuration Loader

```python
import yaml
import os
from typing import Dict, Any

class IntegrationConfig:
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Substitute environment variables
        return self._substitute_env_vars(config)
    
    def _substitute_env_vars(self, obj):
        if isinstance(obj, dict):
            return {k: self._substitute_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_env_vars(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith('${') and obj.endswith('}'):
            env_var = obj[2:-1]
            return os.getenv(env_var, obj)
        return obj
    
    def get_integration_config(self, integration_name: str) -> Dict[str, Any]:
        return self.config.get('integrations', {}).get(integration_name, {})
    
    def is_integration_enabled(self, integration_name: str) -> bool:
        return self.get_integration_config(integration_name).get('enabled', False)
```

## Testing Integration

### Integration Test Framework

```python
import pytest
from unittest.mock import Mock, patch

class IntegrationTestFramework:
    def __init__(self):
        self.mock_integrations = {}
    
    def setup_mock_integration(self, integration_type: IntegrationType):
        mock = Mock()
        self.mock_integrations[integration_type] = mock
        return mock
    
    def create_test_event(self, event_type: OnexEventTypeEnum = OnexEventTypeEnum.NODE_SUCCESS) -> OnexEvent:
        return OnexEvent(
            event_type=event_type,
            node_id="test_node",
            correlation_id="test-correlation-id",
            metadata={"test": True}
        )
    
    def assert_integration_called(self, integration_type: IntegrationType, times: int = 1):
        mock = self.mock_integrations[integration_type]
        assert mock.process_event.call_count == times

# Test example
def test_prometheus_integration():
    framework = IntegrationTestFramework()
    prometheus_mock = framework.setup_mock_integration(IntegrationType.METRICS)
    
    event = framework.create_test_event()
    
    # Process event
    router = EventRouter()
    router.register_integration(IntegrationType.METRICS, prometheus_mock.process_event)
    router.route_event(event)
    
    # Assert
    framework.assert_integration_called(IntegrationType.METRICS)
    prometheus_mock.process_event.assert_called_with(event)
```

## Best Practices

### 1. Error Handling

- Implement circuit breakers for external service calls
- Use exponential backoff for retries
- Log integration failures without affecting core functionality
- Provide fallback mechanisms for critical integrations

### 2. Performance

- Use asynchronous processing for non-critical integrations
- Implement batching for high-volume events
- Cache authentication tokens and connections
- Monitor integration performance and latency

### 3. Security

- Store credentials securely (environment variables, secrets management)
- Use TLS for all external communications
- Implement proper authentication and authorization
- Audit integration access and usage

### 4. Monitoring

- Monitor integration health and availability
- Track integration performance metrics
- Alert on integration failures
- Maintain integration SLA dashboards

## References

- **Event Schema**: [ONEX Event Schema Specification](onex_event_schema.md)
- **Performance**: [ONEX Event Performance Guide](onex_event_performance.md)
- **Error Codes**: [ONEX Error Code Taxonomy](onex_error_codes.md)
- **Evolution**: [ONEX Event Schema Evolution](onex_event_schema_evolution.md)

---

**Note**: Integration patterns should be adapted based on specific requirements and external system capabilities. Always test integrations thoroughly before production deployment.
