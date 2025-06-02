from pathlib import Path
from typing import Callable, Optional
from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevel
from omnibase.fixtures.mocks.dummy_schema_loader import DummySchemaLoader
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_factory import get_event_bus
from omnibase.protocol.protocol_file_io import ProtocolFileIO
from omnibase.runtimes.onex_runtime.v1_0_0.telemetry import get_correlation_id_from_state, telemetry
from omnibase.utils.real_file_io import RealFileIO
from omnibase.mixin.event_driven_node_mixin import EventDrivenNodeMixin
from .helpers.stamper_engine import StamperEngine
from .introspection import StamperNodeIntrospection
from .models.state import StamperInputState, StamperOutputState, create_stamper_input_state, create_stamper_output_state
from omnibase.protocol.protocol_event_bus_types import ProtocolEventBus
_COMPONENT_NAME = Path(__file__).stem


class StamperNode(EventDrivenNodeMixin):

    def __init__(self, event_bus: Optional[ProtocolEventBus]=None, **kwargs):
        super().__init__(node_id='stamper_node', event_bus=event_bus, **kwargs)
        self.event_bus = event_bus or InMemoryEventBus()

    @telemetry(node_name='stamper_node', operation='run')
    def run(self, input_state: StamperInputState, handler_registry:
        Optional[FileTypeHandlerRegistry]=None, file_io: Optional[
        ProtocolFileIO]=None, event_bus: Optional[ProtocolEventBus]=None,
        **kwargs) ->'OnexResultModel':
        """
        Run the stamper node and return the canonical OnexResultModel.
        """
        correlation_id = getattr(input_state, 'correlation_id', None)
        self.emit_node_start({'input_state': input_state.model_dump()},
            correlation_id=correlation_id)
        try:
            engine = StamperEngine(schema_loader=DummySchemaLoader(),
                file_io=file_io, handler_registry=handler_registry,
                event_bus=event_bus or self.event_bus)
            result = engine.stamp_file(Path(input_state.file_path), author=
                input_state.author, discover_functions=getattr(input_state,
                'discover_functions', False))
            self.emit_node_success({'input_state': input_state.model_dump(),
                'output_state': result.model_dump() if hasattr(result,
                'model_dump') else {}}, correlation_id=correlation_id)
            return result
        except Exception as e:
            self.emit_node_failure({'input_state': input_state.model_dump(),
                'error': str(e)}, correlation_id=correlation_id)
            raise


def run_stamper_node(input_state: StamperInputState, event_bus: Optional[
    ProtocolEventBus]=None, handler_registry: Optional[
    FileTypeHandlerRegistry]=None, file_io: Optional[ProtocolFileIO]=None,
    **kwargs) ->'OnexResultModel':
    """
    Run the stamper node and return the canonical OnexResultModel.
    """
    if event_bus is None:
        event_bus = get_event_bus(mode="bind")  # Publisher
    node = StamperNode(event_bus=event_bus)
    return node.run(input_state, handler_registry=handler_registry, file_io
        =file_io, event_bus=event_bus, **kwargs)


def run_canary_preflight(canary_config_path=
    'src/omnibase/nodes/stamper_node/v1_0_0/node_tests/fixtures/stamper_canaries.yaml'
    ) ->bool:
    """
    Run the stamper and parity validator on all Canary files. Abort if any fail.
    Returns True if all Canaries pass, False otherwise.
    """
    import yaml
    import subprocess
    from pathlib import Path
    from omnibase.core.core_structured_logging import emit_log_event
    from omnibase.enums import LogLevel
    if not Path(canary_config_path).exists():
        emit_log_event(LogLevel.ERROR,
            f'Canary config file not found: {canary_config_path}', node_id=
            _COMPONENT_NAME, event_bus=self._event_bus)
        return False
    with open(canary_config_path, 'r') as f:
        config = yaml.safe_load(f)
    canaries = config.get('canaries', {})
    all_passed = True
    for ext, file_path in canaries.items():
        if not file_path or not Path(file_path).exists():
            emit_log_event(LogLevel.WARNING,
                f'No Canary file for {ext} or file does not exist: {file_path}'
                , node_id=_COMPONENT_NAME, event_bus=self._event_bus)
            continue
        emit_log_event(LogLevel.INFO,
            f'[CANARY] Stamping Canary file for {ext}: {file_path}',
            node_id=_COMPONENT_NAME, event_bus=self._event_bus)
        try:
            result = subprocess.run(['python', __file__, file_path,
                '--author', 'CanaryCheck'], capture_output=True, text=True,
                check=True)
            emit_log_event(LogLevel.INFO,
                f"""[CANARY] Stamper output for {file_path}:
{result.stdout}"""
                , node_id=_COMPONENT_NAME, event_bus=self._event_bus)
        except subprocess.CalledProcessError as e:
            emit_log_event(LogLevel.ERROR,
                f'[CANARY] Stamper failed for {file_path}: {e.stderr}',
                node_id=_COMPONENT_NAME, event_bus=self._event_bus)
            all_passed = False
            continue
        try:
            validator_result = subprocess.run(['poetry', 'run', 'onex',
                'run', 'parity_validator_node',
                '--args=["--nodes-directory","src/omnibase/nodes/stamper_node/v1_0_0/node_tests/fixtures","--verbose"]'
                ], capture_output=True, text=True, check=True)
            emit_log_event(LogLevel.INFO,
                f"""[CANARY] Parity validator output for {file_path}:
{validator_result.stdout}"""
                , node_id=_COMPONENT_NAME, event_bus=self._event_bus)
            if ('FAIL' in validator_result.stdout or 'ERROR' in
                validator_result.stdout):
                emit_log_event(LogLevel.ERROR,
                    f'[CANARY] Parity validator failed for {file_path}',
                    node_id=_COMPONENT_NAME, event_bus=self._event_bus)
                all_passed = False
        except subprocess.CalledProcessError as e:
            emit_log_event(LogLevel.ERROR,
                f'[CANARY] Parity validator failed for {file_path}: {e.stderr}'
                , node_id=_COMPONENT_NAME, event_bus=self._event_bus)
            all_passed = False
    return all_passed


def main() ->None:
    """CLI entrypoint for standalone execution."""
    import argparse
    import uuid
    parser = argparse.ArgumentParser(description='ONEX Stamper Node CLI')
    parser.add_argument('file_path', type=str, nargs='?', help=
        'Path to file to stamp')
    parser.add_argument('--author', type=str, default='OmniNode Team', help
        ='Author name')
    parser.add_argument('--correlation-id', type=str, help=
        'Correlation ID for request tracking')
    parser.add_argument('--introspect', action='store_true', help=
        'Enable introspection')
    parser.add_argument('--discover-functions', action='store_true', help=
        'Discover and include function tools in metadata (unified tools approach)'
        )
    parser.add_argument('--skip-canary-check', action='store_true', help=
        'Skip Canary preflight check (for testing only)')
    args = parser.parse_args()
    if args.introspect:
        StamperNodeIntrospection.handle_introspect_command()
        return
    if (not args.skip_canary_check and args.file_path and not args.
        file_path.startswith(
        'src/omnibase/nodes/stamper_node/v1_0_0/node_tests/fixtures/')):
        if not run_canary_preflight():
            emit_log_event(LogLevel.ERROR,
                '[CANARY] Preflight check failed. Aborting batch stamping.',
                node_id=_COMPONENT_NAME, event_bus=self._event_bus)
            exit(2)
    if not args.file_path:
        parser.error('file_path is required when not using --introspect')
    correlation_id = args.correlation_id or str(uuid.uuid4())
    input_state = create_stamper_input_state(file_path=args.file_path,
        author=args.author, correlation_id=correlation_id,
        discover_functions=args.discover_functions)
    event_bus = InMemoryEventBus()
    handler_registry = FileTypeHandlerRegistry(event_bus=event_bus)
    handler_registry.register_all_handlers()
    output = run_stamper_node(input_state, correlation_id=correlation_id,
        handler_registry=handler_registry, file_io=RealFileIO(), event_bus=event_bus)
    emit_log_event(LogLevel.INFO, output.model_dump_json(indent=2),
        node_id=_COMPONENT_NAME, event_bus=event_bus)


def get_introspection() ->dict:
    """Get introspection data for the stamper node."""
    return StamperNodeIntrospection.get_introspection_response().model_dump()


if __name__ == '__main__':
    main()
