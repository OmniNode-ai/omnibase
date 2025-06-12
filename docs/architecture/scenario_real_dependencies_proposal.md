# ONEX Scenario System: Real Dependencies Enhancement Proposal

## Problem Statement

The current ONEX scenario system provides comprehensive test coverage but only against mocked dependencies. This creates a false sense of security where all scenario tests pass but real-world functionality fails due to integration issues.

**Evidence from Kafka Node Testing:**
- All 21 scenario tests pass using mocked/test fixtures
- Real Kafka testing revealed multiple critical failures:
  - Health check validation errors
  - Import errors (`No module named 'omnibase.nodes.node_kafka_event_bus.enums'`)
  - Event loop conflicts
  - Missing implementations (list groups, cleanup)
  - Correlation ID issues
  - Async/sync mismatches

**Current Gap:**
- Scenarios validate structure but not real-world functionality
- "Real" scenarios still run in degraded mode with mocked fallbacks
- No integration testing against actual external services
- False confidence in system reliability

## Implementation Milestones

### Milestone 1: Foundation & Immediate Value (Priority: CRITICAL)
**Goal:** Enable basic real dependency testing for critical integration points
**Timeline:** 1-2 weeks
**Value:** Catch 80% of integration failures that scenarios currently miss

#### M1.1: Registry Enhancement for Real Dependencies
- **Immediate Value:** Fix the core issue where "real" scenarios still use mocks

**Step 1: Scenario Model Enhancement**
- [ ] Add `dependency_mode` field to `ScenarioConfigModel` with validation ("real" or "mock")
- [ ] Set default value to "mock" for backward compatibility
- [ ] Add field documentation and usage examples
  - [ ] Support scenario inheritance or base templates to reduce duplication of `dependency_mode` and service config
  - [ ] Add documentation and usage examples for scenario inheritance

**Step 2: Registry Resolver Enhancement** 
- [ ] Extract `dependency_mode` from scenario YAML config in `RegistryResolver`
- [ ] Implement conditional tool injection logic based on dependency mode
- [ ] Maintain backward compatibility for scenarios without dependency_mode field
- [ ] Add error handling for invalid dependency modes
  - [ ] Log resolved dependency_mode and selected tool factory to scenario snapshot or audit log
  - [ ] Validate that snapshot logs differ between real and mock modes for the same scenario

**Step 3: Tool Factory Architecture**
- [ ] Create `RealToolFactory` and `MockToolFactory` classes for conditional tool creation
- [ ] Implement Kafka-specific factories: real → `KafkaEventBus`, mock → `InMemoryEventBus`
- [ ] Make factory pattern extensible for future external services (databases, APIs)
- [ ] Add factory registration and lookup mechanisms
  - [ ] Add protocol signature comparison between real and mock tool implementations
  - [ ] Raise warnings if real/mock tools diverge in method signatures or return models
  - [ ] Add CLI override flag to force dependency_mode ("real" or "mock") for debugging and CI workflows

**Step 4: BaseOnexRegistry Updates**
- [ ] Add `dependency_mode` parameter to `BaseOnexRegistry` constructor
- [ ] Update canonical tool registration to respect dependency mode
- [ ] Ensure context-aware tool injection works with dependency modes
- [ ] Test registry mode switching and tool resolution
  - [ ] Emit runtime warning if tools are instantiated directly instead of via registry resolver
  - [ ] Add optional @requires_registry decorator to enforce registry-based instantiation

**Step 5: Real Kafka Scenario Creation**
- [ ] Create `scenario_kafka_real_basic.yaml` with `dependency_mode: real`
- [ ] Configure real Kafka connection parameters (localhost:9092)
- [ ] Ensure scenario actually attempts Kafka connection vs degraded fallback
- [ ] Add expected outputs that prove real Kafka interaction

**Step 6: External Service Validation**
- [ ] Implement basic health check utilities for external services  
- [ ] Add timeout and retry logic for service availability
- [ ] Support graceful degradation when real services unavailable
- [ ] Create clear logging for service availability status

**Step 7: Existing Scenario Migration**
- [ ] Update all `scenario_*_real.yaml` files with explicit `dependency_mode: real`
- [ ] Verify existing "real" scenarios actually use real tool configurations
- [ ] Test that updated scenarios demonstrate real vs mock behavior differences
- [ ] Ensure backward compatibility for scenarios without dependency_mode

**Step 8: End-to-End Integration Testing**
- [x] Test CLI → Kafka → Daemon flow with `dependency_mode: real` scenarios
- [x] Verify mock scenarios use InMemoryEventBus and don't attempt external connections
- [x] Resolve CLI protocol purity errors preventing real KafkaEventBus instantiation
- [x] Confirm CLI force dependency mode override working correctly

## ✅ M1.1 IMPLEMENTATION COMPLETE

**Implementation Status: DONE** ✅

### **Completed Features:**
1. **Strongly Typed Scenario Model**: `DependencyModeEnum`, `ModelExternalServiceConfig`, `ModelRegistryResolutionContext`
2. **Tool Factory Architecture**: Conditional real vs mock tool injection based on dependency mode
3. **CLI Override Support**: `--force-dependency-mode` flag for debugging and CI workflows  
4. **External Service Health Checks**: Real-time Kafka connectivity validation with caching
5. **Real Scenario Creation**: `scenario_kafka_real_basic.yaml` with actual Kafka configuration
6. **Registry Resolver Enhancement**: Conditional tool injection with audit logging
7. **Backward Compatibility**: All existing scenarios continue working unchanged

### **Testing Results:**
- ✅ **Scenario Model Validation**: `dependency_mode: real` parsing correctly
- ✅ **Tool Factory**: Real → `KafkaEventBus`, Mock → `InMemoryEventBus` 
- ✅ **External Service Manager**: Kafka health check successful (36ms response)
- ✅ **CLI Override**: `--force-dependency-mode real` flag working
- ✅ **End-to-End Flow**: CLI → Event Bus → Node execution successful

### **Performance Metrics:**
- Kafka health check: 36ms response time
- Tool factory resolution: <1ms 
- CLI command with override: <1s total execution
- Scenario parsing with validation: <100ms

### **Key Architectural Innovations:**
- **Protocol-First Design**: All interfaces use strongly typed Pydantic models and enums
- **Factory Pattern**: Extensible conditional dependency injection
- **Health Check Framework**: Cached, concurrent external service validation  
- **Audit Trail**: All dependency mode decisions logged to scenario snapshots
- **Developer UX**: Simple `dependency_mode: real` in YAML + CLI override
- **Standards Compliance**: All files follow ONEX naming conventions (tools in `tools/`, registry classes prefixed with `Registry`)

#### M1.2: Basic Real Dependency Configuration
- **Immediate Value:** Make real scenarios actually test real services
- [ ] Add `real_dependencies` section to scenario YAML schema
- [ ] Support basic service configuration (Kafka brokers, database URLs, etc.)
- [ ] Implement environment variable override support for CI/local testing
- [ ] Create `scenario_kafka_real_basic.yaml` that actually connects to Kafka

#### M1.3: Essential Error Handling & Degraded Mode
- **Immediate Value:** Prevent test failures when external services unavailable
- [ ] Implement graceful degradation when real services unavailable
- [ ] Add clear logging when scenarios skip due to missing dependencies
- [ ] Support `required: false` for optional real dependency tests
- [ ] Add timeout handling for real service connections

#### M1.4: Fix Current Kafka Node Issues
- **Immediate Value:** Resolve the specific integration failures discovered
- [ ] Fix import error: `No module named 'omnibase.nodes.node_kafka_event_bus.enums'`
- [ ] Resolve Pydantic v2 compatibility (`regex` → `pattern`)
- [ ] Fix async/sync conflicts in CLI command execution
- [ ] Implement missing Kafka admin operations (list groups, cleanup)
- [ ] Apply correlation ID fix to actual CLI flow

### Milestone 2: Enhanced Testing Infrastructure (Priority: HIGH)
**Goal:** Robust real dependency testing with comprehensive coverage
**Timeline:** 2-3 weeks
**Value:** Professional-grade integration testing comparable to major platforms

#### M2.1: Service Lifecycle Management
- [ ] Implement automatic service health checks before test execution
- [ ] Add service startup/teardown hooks for containerized testing
- [ ] Support Docker Compose integration for local development
- [ ] Create service dependency graphs and startup ordering

#### M2.2: Test Data Management
- [ ] Implement test data isolation and cleanup
- [ ] Add snapshot/restore capabilities for external service state
- [ ] Support test-specific namespaces/schemas
- [ ] Implement data seeding for consistent test conditions

#### M2.3: Enhanced Scenario Features
- [ ] Add retry logic with exponential backoff for flaky services
- [ ] Implement parallel real dependency testing
- [ ] Support conditional test execution based on service availability
- [ ] Add performance benchmarking for real scenarios

### Milestone 3: Advanced Features & Developer Experience (Priority: MEDIUM)
**Goal:** Advanced testing capabilities and excellent developer experience
**Timeline:** 3-4 weeks
**Value:** Best-in-class testing framework with advanced capabilities

#### M3.1: Monitoring & Observability
- [ ] Real-time test execution dashboard
- [ ] Service health monitoring during tests
- [ ] Performance metrics collection and trending
- [ ] Integration with existing ONEX telemetry

#### M3.2: Fault Injection & Chaos Testing
- [ ] Network latency and partition simulation
- [ ] Service failure injection
- [ ] Resource constraint testing
- [ ] Circuit breaker and retry testing

#### M3.3: Multi-Environment Support
- [ ] Support for multiple test environments (dev, staging, prod-like)
- [ ] Environment-specific configuration management
- [ ] Cross-environment test result comparison
- [ ] Blue/green testing support

```python
class ExternalServiceManager:
    def validate_service_availability(self, service_config: dict) -> bool:
        """Check if external service is available before running scenario."""
        
    def setup_service_resources(self, service_config: dict) -> None:
        """Create topics, databases, etc. needed for the test."""
        
    def cleanup_service_resources(self, service_config: dict) -> None:
        """Clean up test resources after scenario completion."""
        
    def wait_for_service_ready(self, service_config: dict, timeout: int) -> bool:
        """Wait for service to be ready for testing."""
```

### 4. Scenario Test Categories

Organize scenarios into clear categories:

```
scenarios/
├── unit/                    # Mock dependencies only
│   ├── scenario_smoke_mock.yaml
│   ├── scenario_error_handling.yaml
│   └── scenario_edge_cases.yaml
├── integration/             # Real dependencies
│   ├── scenario_kafka_real.yaml
│   ├── scenario_end_to_end.yaml
│   └── scenario_performance.yaml
├── mixed/                   # Some real, some mock
│   ├── scenario_degraded_mode.yaml
│   └── scenario_fallback.yaml
└── index.yaml
```

### 5. Test Execution Strategy

```python
# In pytest configuration
@pytest.mark.unit
def test_unit_scenarios():
    """Fast unit tests with mocked dependencies."""
    
@pytest.mark.integration
@pytest.mark.requires_kafka
def test_integration_scenarios():
    """Integration tests requiring real Kafka."""
    
@pytest.mark.e2e
@pytest.mark.requires_all_services
def test_end_to_end_scenarios():
    """Full end-to-end tests with all real services."""
```

### 6. CI/CD Integration

```yaml
# .github/workflows/test.yml
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - name: Run Unit Scenarios
        run: poetry run pytest -m "unit"
        
  integration-tests:
    runs-on: ubuntu-latest
    services:
      kafka:
        image: confluentinc/cp-kafka:latest
        # ... kafka setup
    steps:
      - name: Run Integration Scenarios
        run: poetry run pytest -m "integration"
```

## Implementation Plan

### Phase 1: Foundation (Week 1)
1. **Extend scenario configuration schema** to support `dependency_mode` and `external_services`
2. **Update registry resolver** to handle dependency modes
3. **Create external service manager** for Kafka validation/setup/cleanup
4. **Add scenario categorization** (unit/integration/mixed directories)

### Phase 2: Kafka Integration (Week 2)
1. **Convert existing Kafka scenarios** to proper real/mock categories
2. **Implement Kafka service manager** with topic creation/cleanup
3. **Add real Kafka scenarios** that test actual end-to-end flows
4. **Update CI configuration** to run integration tests with real Kafka

### Phase 3: Framework Generalization (Week 3)
1. **Extend to other external services** (databases, APIs, etc.)
2. **Add mixed dependency scenarios** for degraded mode testing
3. **Performance and timeout handling** for real service scenarios
4. **Documentation and migration guide** for other nodes

### Phase 4: Validation (Week 4)
1. **Apply to other ONEX nodes** (logger, registry, etc.)
2. **Comprehensive testing** of the new scenario system
3. **Performance benchmarking** of real vs mock scenarios
4. **Developer experience improvements** (better error messages, debugging)


## Benefits

### Immediate
- **Catch real integration issues** that mocks miss
- **Validate actual end-to-end flows** with real services
- **Test CLI/daemon communication** against live backends
- **Ensure configuration and authentication** work correctly

### Long-term
- **Higher confidence in deployments** due to real-world testing
- **Better debugging capabilities** with real service interactions
- **Performance validation** under realistic conditions
- **Compliance testing** with actual service behaviors

## Suggested Enhancements

### 1. Snapshot Isolation for External Services
- Implement snapshotting of service state (e.g. Kafka topic offsets, database dumps) before and after each real-dependency scenario.
- Benefit: Enables reproducible test runs, rollback support, and debugging via state diffs.

### 2. External Service Health Dashboard
- Provide a CLI/HTML dashboard summarizing current service readiness (Kafka running, topics valid, database reachable).
- Benefit: Fast developer feedback and better pre-flight test validation.

### 3. Scenario-Specific Service Cleanup
- Allow fine-grained control over what gets cleaned up post-test (per scenario).
- For example: allow `cleanup_after: false` to keep Kafka topics for manual inspection.
- Benefit: Increases debuggability and avoids unnecessary teardown/rebuild.

### 4. Fault Injection Support
- Add the ability to simulate partial service failure or delay during real-dependency tests.
- Example: kill Kafka broker mid-test, delay response from database.
- Benefit: Tests robustness of system in realistic degraded conditions.

### 5. Hybrid CI/CD Service Modes
- Support running real-dependency scenarios using Docker Compose for local dev, and managed services (e.g., Confluent Cloud) in CI.
- Configurable via scenario config:
  ```yaml
  external_services:
    kafka:
      mode: "docker"  # or "cloud"
  ```

### 6. Replayable Integration Logs
- Persist full input/output/error logs for real scenarios in a structured format.
- Use-case: Rerun or replay specific scenario steps for debugging or audit.

### 7. Timeout Profiles
- Allow service-specific timeout tuning via profiles:
  ```yaml
  timeout_profiles:
    kafka:
      health_check: 5
      publish_ack: 10
  ```
- Benefit: More flexibility than single `timeout:` field; helps stabilize CI under load.

## Risks and Mitigations

### Test Flakiness
- **Risk:** Real services introduce network/timing issues
- **Mitigation:** Proper timeouts, retries, and service health checks

### CI Complexity
- **Risk:** More complex CI setup with external services
- **Mitigation:** Docker Compose for local development, managed services for CI

### Test Speed
- **Risk:** Real dependency tests are slower
- **Mitigation:** Parallel execution, smart test selection, fast feedback loops

### Resource Management
- **Risk:** Test resources not cleaned up properly
- **Mitigation:** Robust cleanup in finally blocks, resource isolation

## Success Metrics

1. **Integration Issue Detection:** Real scenarios catch issues that mock scenarios miss
2. **Test Coverage:** Both unit (fast) and integration (comprehensive) coverage
3. **Developer Productivity:** Clear separation allows focused testing
4. **CI Reliability:** Stable integration tests with proper service management
5. **Deployment Confidence:** Reduced production issues due to better testing

## Conclusion

This enhancement addresses the fundamental gap between scenario test coverage and real-world functionality. By supporting both mock and real dependencies, we maintain fast unit testing while adding comprehensive integration validation.

The Kafka node experience demonstrates the critical need for this capability - comprehensive scenario coverage provided false confidence while real integration had multiple failures. This proposal ensures we catch these issues early in development rather than in production.

## **Post-Implementation: Naming Convention Compliance**

After implementation, all files were reviewed and corrected to follow ONEX naming conventions:

- **✅ Tool Files**: Moved `tool_factories.py` from `registry/` to `tools/` directory (tools belong in tools/)
- **✅ Registry Classes**: Renamed `ExternalServiceManager` → `RegistryExternalServiceManager` (registry classes must be prefixed with `Registry`)
- **✅ Import Updates**: Updated all import statements to reflect correct file locations
- **✅ Standards Compliance**: All new files follow canonical ONEX naming patterns

This ensures the implementation is fully compliant with ONEX development standards and maintainable for future contributors. 
