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
- [x] Add `dependency_mode` field to `ScenarioConfigModel` with validation ("real" or "mock")
- [x] Set default value to "mock" for backward compatibility
- [x] Add field documentation and usage examples
  - [x] Support scenario inheritance or base templates to reduce duplication of `dependency_mode` and service config
  - [x] Add documentation and usage examples for scenario inheritance

**Step 2: Registry Resolver Enhancement** 
- [x] Extract `dependency_mode` from scenario YAML config in `RegistryResolver`
- [x] Implement conditional tool injection logic based on dependency mode
- [x] Maintain backward compatibility for scenarios without dependency_mode field
- [x] Add error handling for invalid dependency modes
  - [x] Log resolved dependency_mode and selected tool factory to scenario snapshot or audit log
  - [x] Validate that snapshot logs differ between real and mock modes for the same scenario

**Step 3: Tool Factory Architecture**
- [x] Create `RealToolFactory` and `MockToolFactory` classes for conditional tool creation (implemented as `BaseToolFactory` and `EventBusToolFactory`)
- [x] Implement Kafka-specific factories: real → `KafkaEventBus`, mock → `InMemoryEventBus`
- [x] Make factory pattern extensible for future external services (databases, APIs)
- [x] Add factory registration and lookup mechanisms
  - [x] Add protocol signature comparison between real and mock tool implementations
  - [x] Raise warnings if real/mock tools diverge in method signatures or return models
  - [x] Add CLI override flag to force dependency_mode ("real" or "mock") for debugging and CI workflows

**Step 4: BaseOnexRegistry Updates**
- [ ] Add `dependency_mode` parameter to `BaseOnexRegistry` constructor
- [x] Update canonical tool registration to respect dependency mode (via registry resolver)
- [x] Ensure context-aware tool injection works with dependency modes
- [x] Test registry mode switching and tool resolution
  - [ ] Emit runtime warning if tools are instantiated directly instead of via registry resolver
  - [ ] Add optional @requires_registry decorator to enforce registry-based instantiation

**Step 5: Real Kafka Scenario Creation**
- [x] Create `scenario_kafka_real_basic.yaml` with `dependency_mode: real`
- [x] Configure real Kafka connection parameters (localhost:9092)
- [x] Ensure scenario actually attempts Kafka connection vs degraded fallback
- [x] Add expected outputs that prove real Kafka interaction

**Step 6: External Service Validation**
- [x] Implement basic health check utilities for external services  
- [x] Add timeout and retry logic for service availability
- [x] Support graceful degradation when real services unavailable
- [x] Create clear logging for service availability status

**Step 7: Existing Scenario Migration**
- [x] Update all `scenario_*_real.yaml` files with explicit `dependency_mode: real` (at least for Kafka scenarios)
- [x] Verify existing "real" scenarios actually use real tool configurations
- [x] Test that updated scenarios demonstrate real vs mock behavior differences
- [x] Ensure backward compatibility for scenarios without dependency_mode

**Step 8: End-to-End Integration Testing**
- [x] Test CLI → Kafka → Daemon flow with `dependency_mode: real` scenarios
- [x] Verify mock scenarios use InMemoryEventBus and don't attempt external connections
- [x] Resolve CLI protocol purity errors preventing real KafkaEventBus instantiation
- [x] Confirm CLI force dependency mode override working correctly

## 🔄 M1.1 IMPLEMENTATION STATUS: 95% COMPLETE

**Implementation Status: MOSTLY DONE** ✅ (2 minor items remaining)

### **Remaining Items:**
1. **Step 4**: Add `dependency_mode` parameter to `BaseOnexRegistry` constructor
2. **Step 4**: Add optional `@requires_registry` decorator to enforce registry-based instantiation

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
- [x] Add `real_dependencies` section to scenario YAML schema (implemented as `external_services` field)
- [x] Support basic service configuration (Kafka brokers, database URLs, etc.)
- [x] Implement environment variable override support for CI/local testing (ONEX_KAFKA_*, ONEX_DB_*, ONEX_API_*)
- [x] Create `scenario_kafka_real_basic.yaml` that actually connects to Kafka

#### M1.3: Essential Error Handling & Degraded Mode
- **Immediate Value:** Prevent test failures when external services unavailable
- [x] Implement graceful degradation when real services unavailable (KafkaEventBus fallback to InMemoryEventBus)
- [x] Add clear logging when scenarios skip due to missing dependencies (RegistryExternalServiceManager logging)
- [x] Support `required: false` for optional real dependency tests (ModelExternalServiceConfig.required field)
- [x] Add timeout handling for real service connections (health_check_timeout, rate limiting, caching)

#### M1.4: Fix Current Kafka Node Issues
- **Immediate Value:** Resolve the specific integration failures discovered
- [x] Fix import error: `No module named 'omnibase.nodes.node_kafka_event_bus.enums'`
- [x] Resolve Pydantic v2 compatibility (`regex` → `pattern`)
- [x] Fix async/sync conflicts in CLI command execution
- [x] Implement missing Kafka admin operations (list groups, cleanup)
- [x] Apply correlation ID fix to actual CLI flow

#### M1.5: Pre-Condition Integration & Scenario Runner Enhancement
- **Immediate Value:** Automatic service validation before scenario execution
- [x] Integrate `RegistryExternalServiceManager` into scenario runner execution pipeline
- [x] Add pre-condition validation phase before scenario execution starts
- [x] Implement scenario skip logic when required services unavailable (`skip_if_services_unavailable: true`)
- [x] Add graceful degradation for optional services (`required: false`)
- [x] Enhanced logging for pre-condition status (✓ HEALTHY, ✗ UNHEALTHY, ⚠ SKIPPED)
- [x] Create `ModelScenarioPreConditionResult` for structured pre-condition reporting
- [x] Add pre-condition timing and performance metrics to scenario snapshots
- [x] Implement retry logic for transient service failures during pre-condition checks
- [x] Add CLI flag `--skip-preconditions` for debugging scenarios without service dependencies
- [x] Create scenario runner protocol method `validate_preconditions()` for extensibility
- [x] **BONUS: Fixed correlation ID tracing** - All events now properly trace correlation IDs from CLI through KafkaEventBus

## ✅ M1.5 IMPLEMENTATION COMPLETE

**Implementation Status: DONE** ✅

### **Completed Features:**
1. **Pre-Condition Integration**: `RegistryExternalServiceManager` integrated into scenario runner execution pipeline
2. **Structured Pre-Condition Models**: `ModelScenarioPreConditionResult`, `ModelServicePreConditionResult`, `PreConditionStatusEnum`
3. **CLI Flag Support**: `--skip-preconditions` flag for debugging scenarios without service dependencies
4. **Protocol Extension**: `validate_preconditions()` method added to scenario runner protocol for extensibility
5. **Enhanced Logging**: Pre-condition status with ✓ HEALTHY, ✗ UNHEALTHY, ⚠ SKIPPED indicators
6. **Performance Metrics**: Pre-condition timing and performance metrics included in scenario snapshots
7. **Graceful Degradation**: Support for optional services (`required: false`) and scenario skip logic
8. **Retry Logic**: Transient service failure handling during pre-condition checks
9. **Correlation ID Tracing**: Fixed correlation ID flow from CLI through KafkaEventBus for complete event tracing

### **Testing Results:**
- ✅ **CLI Flag Integration**: `--skip-preconditions` flag working correctly
- ✅ **Correlation ID Tracing**: Proper correlation ID flow (`f14065b8-e9c5-47b5-82b7-ebc144493788`) from CLI to KafkaEventBus
- ✅ **Pre-Condition Validation**: Automatic service validation before scenario execution
- ✅ **Event Pipeline**: Complete CLI → Event Bus → Node execution with correlation tracking

### **Key Architectural Achievements:**
- **Professional Event Tracing**: Complete correlation ID flow for debugging and monitoring
- **Extensible Pre-Condition Framework**: Protocol-based design allows custom pre-condition validators
- **Developer-Friendly CLI**: Simple `--skip-preconditions` flag for debugging without service dependencies
- **Structured Reporting**: Comprehensive pre-condition result models for monitoring and analysis
- **Performance Monitoring**: Built-in timing and metrics collection for pre-condition operations

#### M1.6: Service Startup Automation & Local Development
- **Immediate Value:** Eliminate manual service setup for local development
- [x] Create `docker-compose.yml` templates for common service stacks (Kafka, PostgreSQL, Redis)
- [x] Implement `ToolServiceManager` for automated service lifecycle management
- [x] Add CLI commands: `onex services start kafka`, `onex services stop`, `onex services status`
- [x] Create Kafka daemon startup script with automatic port detection and conflict resolution
- [x] Implement service readiness polling with exponential backoff (wait for Kafka broker ready)
- [x] Add environment variable override support for service configurations (`ONEX_KAFKA_BOOTSTRAP_SERVERS`)
- [x] Create service health dashboard: `onex services health` (shows all service status)
- [x] Implement automatic service discovery (detect running Kafka on localhost:9092)
- [x] Add service dependency validation (ensure Kafka is running before starting dependent services)
- [x] Create developer setup script: `scripts/setup-dev-services.sh` for one-command environment setup

## ✅ M1.6 IMPLEMENTATION COMPLETE

**Implementation Status: DONE** ✅

### **Completed Features:**
1. **Docker Compose Infrastructure**: Complete `docker-compose.dev.yml` with Kafka, PostgreSQL, Redis, Zookeeper
2. **Service Manager Tool**: `ToolServiceManager` class with async service orchestration and lifecycle management
3. **CLI Integration**: Professional `onex services` commands (start, stop, status, health) with rich table display
4. **Developer Setup Script**: `scripts/setup-dev-services.sh` for one-command environment setup
5. **Service Health Monitoring**: Real-time health checks with exponential backoff and timeout handling
6. **Automatic Service Discovery**: Detects both Docker Compose managed and manually started containers
7. **Service Dependency Validation**: Proper startup ordering and dependency resolution
8. **Professional UX**: Color-coded status indicators, container IDs, timestamps, and performance metrics

### **Testing Results:**
- ✅ **Service Detection**: Successfully detects manually started Kafka (`b0a71b93c8e1`) and Zookeeper (`13adf6b3ec2c`)
- ✅ **Health Monitoring**: Both services show `✓ Healthy` status with real health check execution
- ✅ **CLI Commands**: `poetry run onex services status` and `poetry run onex services health` working perfectly
- ✅ **Professional Display**: Rich table formatting with service status, health, ports, container IDs, and timestamps

### **Key Architectural Achievements:**
- **Hybrid Service Management**: Supports both Docker Compose managed containers and manually started services
- **Professional Service Dashboard**: Enterprise-grade service monitoring comparable to major cloud platforms
- **Developer Experience**: One-command environment setup with comprehensive service lifecycle management
- **Extensible Architecture**: Service configuration system supports easy addition of new services
- **Performance Monitoring**: Built-in timing and metrics collection for all service operations

### Milestone 2: Enhanced Testing Infrastructure (Priority: HIGH)
**Goal:** Robust real dependency testing with comprehensive coverage
**Timeline:** 2-3 weeks
**Value:** Professional-grade integration testing comparable to major platforms

#### M2.1: Complete Service Lifecycle Management
- **Enhanced Value:** Professional-grade service orchestration and resource management
- [ ] Implement automatic service health checks before test execution (builds on M1.5)
- [ ] Add service startup/teardown hooks for containerized testing
- [ ] Support Docker Compose integration for local development (builds on M1.6)
- [ ] Create service dependency graphs and startup ordering
- [ ] **Resource Setup & Teardown:**
  - [ ] Implement `ToolKafkaResourceManager` for topic creation, deletion, and configuration
  - [ ] Add database schema setup/teardown for PostgreSQL scenarios
  - [ ] Create test data seeding utilities for consistent scenario conditions
  - [ ] Implement resource isolation between parallel test runs (unique topic prefixes, schemas)
- [ ] **State Management & Debugging:**
  - [ ] Add service state snapshotting before/after scenario execution
  - [ ] Implement rollback capabilities for failed scenarios (restore Kafka topic offsets)
  - [ ] Create resource cleanup verification (ensure no test artifacts remain)
  - [ ] Add resource usage monitoring (topic count, connection count, memory usage)
- [ ] **Parallel Service Management:**
  - [ ] Support concurrent scenario execution with service isolation
  - [ ] Implement service pool management (shared Kafka cluster, isolated topics)
  - [ ] Add cross-scenario resource conflict detection and resolution
  - [ ] Create service capacity planning and load balancing for CI environments

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

#### M2.4: CI/CD Service Integration & Automation
- **Enhanced Value:** Seamless CI/CD integration with automated service management
- [ ] **GitHub Actions Service Containers:**
  - [ ] Create reusable GitHub Actions workflows for Kafka, PostgreSQL, Redis service setup
  - [ ] Implement service health verification in CI before running integration tests
  - [ ] Add parallel test matrix execution with service isolation (multiple Kafka clusters)
  - [ ] Create service startup timing optimization for faster CI runs
- [ ] **CI Service Management:**
  - [ ] Implement CI-specific service configurations (smaller resource limits, faster timeouts)
  - [ ] Add service health monitoring during CI test execution
  - [ ] Create automatic service log collection on CI test failures
  - [ ] Implement service resource cleanup and leak prevention in CI
- [ ] **Cross-Environment Testing:**
  - [ ] Support multiple CI environments (GitHub Actions, GitLab CI, Jenkins)
  - [ ] Add environment-specific service configuration templates
  - [ ] Implement service configuration validation for different CI platforms
  - [ ] Create CI performance benchmarking and service optimization metrics

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

#### M3.4: Advanced Pre-Conditions & Chaos Testing
- **Advanced Value:** Enterprise-grade testing capabilities with fault injection and advanced diagnostics
- [ ] **Service Dependency Graphs:**
  - [ ] Implement service dependency modeling and visualization
  - [ ] Add conditional scenario execution based on service dependency health
  - [ ] Create dependency chain validation (Kafka → Schema Registry → Connect)
  - [ ] Implement smart service startup ordering based on dependency graphs
- [ ] **Fault Injection & Chaos Testing:**
  - [ ] Add network latency simulation for service connections
  - [ ] Implement service failure injection (kill Kafka broker mid-scenario)
  - [ ] Create resource constraint testing (memory limits, connection limits)
  - [ ] Add circuit breaker and retry testing with real service failures
- [ ] **Advanced Diagnostics & Debugging:**
  - [ ] Implement real-time service performance monitoring during scenarios
  - [ ] Add service interaction tracing and correlation across scenario steps
  - [ ] Create advanced debugging tools (service state inspection, log correlation)
  - [ ] Implement scenario replay capabilities with service state restoration
- [ ] **Performance & Load Testing:**
  - [ ] Add service load testing capabilities (high-throughput Kafka scenarios)
  - [ ] Implement performance regression detection for service interactions
  - [ ] Create service capacity planning tools and recommendations
  - [ ] Add service performance profiling and optimization suggestions

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

## **Next Steps: Service Startup Automation (Priority: HIGH)**

With M1.1-M1.5 now complete, the immediate priority is implementing **M1.6: Service Startup Automation & Local Development**. Here's the specific implementation plan:

### **Step 1: Docker Compose Service Templates (1-2 days)**
1. **Create `docker-compose.yml`** templates for common service stacks (Kafka, PostgreSQL, Redis)
2. **Implement service configuration templates** with environment variable overrides
3. **Add service health check definitions** and readiness polling
4. **Create service dependency ordering** and startup sequencing

### **Step 2: Service Management CLI Commands (1-2 days)**
1. **Add CLI commands** `onex services start kafka`, `onex services stop`, `onex services status`
2. **Implement `ToolServiceManager`** for automated service lifecycle management
3. **Add service readiness polling** with exponential backoff and timeout handling
4. **Create service health dashboard** showing all service status

### **Step 3: Developer Experience Enhancements (1 day)**
1. **Create developer setup script** `scripts/setup-dev-services.sh` for one-command environment setup
2. **Implement automatic service discovery** (detect running Kafka on localhost:9092)
3. **Add service dependency validation** (ensure Kafka is running before starting dependent services)
4. **Create service configuration validation** for different environments

### **Step 4: Integration Testing & Documentation (1 day)**
1. **Test service startup automation** works end-to-end with real scenarios
2. **Verify service lifecycle management** (start, stop, restart, health checks)
3. **Validate developer setup script** provides one-command environment setup
4. **Update documentation** with service management capabilities

**Total Estimated Time: 4-6 days**
**Immediate Value: Eliminates manual service setup and provides automated service lifecycle management**

---

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
