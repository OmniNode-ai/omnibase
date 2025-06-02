# ONEX Registry Node: Proxy Tool Invocation API

## Purpose
Enable clients (CLI, agents, nodes) to invoke a tool by name via the registry node. The registry node will:
- Look up the tool in its registry (`ToolCollection`)
- Route the invocation to the correct node(s) that registered the tool
- Return the result (or error) to the caller

---

## API Design

### Input Model
```python
from omnibase.enums import OnexStatusEnum
from omnibase.enums import OnexErrorCodeEnum  # Canonical error code enum

class ToolProxyInvocationRequest(BaseModel):
    tool_name: str
    arguments: dict  # Strongly-typed if tool contracts are available
    correlation_id: Optional[str] = None
    timeout_ms: Optional[int] = 5000
    # Milestone 1: node_selection_policy stub (e.g., "first", "round_robin", "least_loaded")
    node_selection_policy: Optional[str] = None  # Default: "first" if not specified
    # Milestone 2: trusted_only flag stub
    trusted_only: Optional[bool] = False
    # Future: tool version support
    tool_version: Optional[str] = None
```

### Output Model
```python
from omnibase.enums import OnexStatusEnum
from omnibase.enums import OnexErrorCodeEnum

class ToolProxyInvocationError(BaseModel):
    error_code: OnexErrorCodeEnum  # Use canonical error code enum, not string
    error_type: Optional[str] = None  # e.g., "validation", "timeout", "internal"
    message: str
    details: Optional[dict] = None

class ToolProxyInvocationResponse(BaseModel):
    tool_name: str
    result: Any  # Strongly-typed if available
    status: OnexStatusEnum  # Use canonical status enum
    error: Optional[ToolProxyInvocationError] = None
    correlation_id: Optional[str] = None
```

### Registry Node API Method
```python
def proxy_invoke_tool(self, request: ToolProxyInvocationRequest) -> ToolProxyInvocationResponse:
    # 1. Look up tool in self.registry_state.tools
    # 2. Find the node(s) that registered this tool
    # 3. Route the invocation (emit event or call directly if local)
    # 4. Wait for response (with timeout)
    # 5. Return ToolProxyInvocationResponse
```

### Event Bus Protocol
- Registry node emits a `TOOL_PROXY_INVOKE` event to the target node(s)
- Target node responds with a `TOOL_PROXY_RESULT` event
- Registry node collects the result and returns it to the original caller

**Event Types:**
- `TOOL_PROXY_INVOKE`
- `TOOL_PROXY_RESULT`

## Event Payload Specification

### TOOL_PROXY_INVOKE
```python
class ToolProxyInvokeEvent(OnexEvent):
    tool_name: str
    arguments: dict
    correlation_id: str
    timeout_ms: int
    origin_node_id: str
    request_ts: str  # ISO 8601 timestamp
    tool_version: Optional[str] = None
```

### TOOL_PROXY_RESULT
```python
class ToolProxyResultEvent(OnexEvent):
    tool_name: str
    correlation_id: str
    result: Any
    status: OnexStatusEnum  # Use canonical status enum
    error: Optional[ToolProxyInvocationError]
    response_ts: str  # ISO 8601 timestamp
```

**Note:** All protocol-facing models must use the strongest possible typing, including enums for status and error codes, per project standards. See OnexErrorCodeEnum and OnexStatusEnum in `omnibase.enums`.

---

## Routing Logic
- If multiple nodes register the same tool, use a policy (`node_selection_policy`). Supported: `"first"` (Milestone 1; default), `"round_robin"`, `"least_loaded"` (stubbed).
- If multiple nodes register the tool and no policy is specified, default to `"first"` and emit a warning-level log.
- If the tool is not found, return an error response.
- [ ] If timeout_ms is exceeded, return a TOOL_TIMEOUT error response and discard late responses.

## Security/Validation
- Validate that the tool exists and arguments match the contract signature if available. (Milestone 1)
- Optionally enforce permissions or trust state.
- If `trusted_only: Optional[bool] = False` is set on the request, only nodes with verified trust state are eligible targets. (Stub for Milestone 2)
- Log and reject invocations to unregistered or expired tools.

## Tool Introspection and Metadata (stub for Milestone 2)
- [ ] Add `ToolDescribeRequest` API method to return metadata for a tool, including argument schema, description, version, trust flags, etc.
- [ ] CLI command: `onex describe-tool <tool_name>` to fetch this information interactively.

## Tool Registration Health & Expiry (stub for Milestone 2)
- [ ] Allow tool registration to specify `registration_ttl` (time-to-live)
- [ ] Registry node should support optional heartbeat-based re-registration
- [ ] Expired or stale tool registrations are purged automatically and events emitted

## Usage Examples
- CLI: `onex proxy-invoke --tool <tool_name> --args '{"foo": 1}'`
- Python: `NodeRegistryNode().proxy_invoke_tool(ToolProxyInvocationRequest(...))`

## Extensibility
- Can be extended for streaming, async, or batch invocations.
- Can add support for tool versioning, node selection policies, etc.
- Add support for correlation tracing: each request/response pair should emit `TOOL_PROXY_INVOKE` and `TOOL_PROXY_RESULT` events with the same `correlation_id`. (Milestone 1)
- Future: Add `ToolProxyInvocationBatchRequest` to support batch or parallel invocations across tool variants.
- Add support for `tool_version: Optional[str] = None` in request model to support explicit version routing. (stub for Milestone 2)
- All protocol-facing models must use canonical enums and models for status, error codes, and other fixed sets. See `omnibase.enums.OnexErrorCodeEnum` and `omnibase.enums.OnexStatusEnum`.

---

## Testing and Simulation
- [ ] Include local test harness that registers fake tools and validates proxy routing behavior.
- [ ] Simulate multiple tool registrants to test routing policy logic, timeouts, and failover handling.
- [ ] Emit structured logs for all tool proxy request/response operations.
- [ ] CLI support for `--dry-run` to simulate a proxy invocation without sending it
- [ ] Add CLI `--verbose` flag to emit full event payloads during simulation

---

## Error Granularity
For `ToolProxyInvocationResponse.error`, use a structured error object with a canonical error code enum for programmatic handling of different failure modes:
```python
from omnibase.enums import OnexErrorCodeEnum
class ToolProxyInvocationError(BaseModel):
    error_code: OnexErrorCodeEnum  # e.g., OnexErrorCodeEnum.TOOL_NOT_FOUND, OnexErrorCodeEnum.INVALID_ARGUMENTS, ...
    error_type: Optional[str] = None  # e.g., "validation", "timeout", "internal"
    message: str
    details: Optional[dict] = None
```
**Rationale:** Enables robust error handling, diagnostics, and future internationalization. All error codes must use the canonical enum, not raw strings.

---

## Asynchronous Invocation
- **Milestone 1:** Synchronous wait with timeout is used for proxy invocation.
- **Future:** The API is designed for async/streaming. Consider making `proxy_invoke_tool` an `async def` method, or supporting callback/event-driven completion (e.g., emit a `TOOL_PROXY_RESULT` event to a callback address or correlation ID).
- For batch/streaming, return a handle or job ID for polling or subscription.
- **Design Note:** Document that the API is sync for now, but will become async in the future.

---

## Trusted_Only Logic (Future)
- When `trusted_only=True`, the registry will need to determine node trust, likely via a `trust_state` field in node metadata or by querying a dedicated `trust_node` or `identity_node`.
- For now, this is a filter on the registry's view of node trust; actual trust evaluation logic is deferred.
- Emit a warning if `trusted_only=True` is requested but no trust evaluation is available.

---

## Additional Innovation Ideas
- **Tool Versioning:** Allow invocation of a specific version of a tool, or default to the latest.
- **Multi-Target Invocation:** Support invoking all nodes that provide a tool (e.g., for distributed processing or redundancy).
- **Invocation Auditing:** Log all proxy invocations and results for traceability and debugging.
- **Timeout/Fallback Policy:** Allow the caller to specify fallback behavior if the primary node fails (e.g., try next node, return error, escalate).
- **Schema Validation:** Validate arguments against the tool's contract/schema before routing.
- **Security/Authorization:** In the future, add an optional `auth_token` or `caller_identity` field for access control.
- **Batch Invocation Semantics:** Define aggregation policy for future `ToolProxyInvocationBatchRequest` (e.g., ordered list of results, merged dict, short-circuit on error)

---

**Status:** Design phase partially complete. Routing policy, security flag, error structure (with canonical enums), async/streaming, and test stubs drafted. Initial implementation to begin in Milestone 1; future milestones will address trust, versioning, and advanced routing.