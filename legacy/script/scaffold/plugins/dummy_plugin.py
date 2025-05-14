from pathlib import Path
from foundation.protocol.protocol_scaffold_plugin import ProtocolScaffoldPlugin

PLUGIN_NAME = 'dummy'

class DummyPlugin(ProtocolScaffoldPlugin):
    def __init__(self, logger, registry, config=None):
        self.logger = logger
        self.registry = registry
        self.config = config
        self.generated = False
    def generate(self, name: str, output_dir: Path, **kwargs) -> None:
        self.generated = True
        (output_dir / f"{name}.dummy").write_text("dummy content")
    def get_metadata(self):
        return {"type": "dummy", "version": "0.1"}
    def validate(self, output_dir: Path):
        return [] 