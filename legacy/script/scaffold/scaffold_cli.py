import argparse
from pathlib import Path
import sys
from typing import Optional
from foundation.registry.registry_scaffold_plugin import ScaffoldPluginRegistry
from foundation.protocol.protocol_scaffold_plugin import ProtocolScaffoldPlugin
import importlib
import pkgutil

PLUGINS_PACKAGE = 'foundation.script.scaffold.plugins'
PLUGINS_PATH = Path(__file__).parent / 'plugins'

class SimpleLogger:
    def info(self, msg):
        print(f"[INFO] {msg}")
    def error(self, msg):
        print(f"[ERROR] {msg}", file=sys.stderr)

def create_scaffold_plugin_registry(logger, config=None):
    """
    Factory for creating and populating the scaffold plugin registry.
    Handles all dynamic plugin discovery and registration.
    """
    registry = ScaffoldPluginRegistry(logger=logger, config=config)
    for finder, name, ispkg in pkgutil.iter_modules([str(PLUGINS_PATH)]):
        module_name = f"{PLUGINS_PACKAGE}.{name}"
        try:
            module = importlib.import_module(module_name)
            plugin_cls = None
            plugin_name = None
            for attr in dir(module):
                obj = getattr(module, attr)
                if (
                    isinstance(obj, type)
                    and issubclass(obj, ProtocolScaffoldPlugin)
                    and hasattr(module, 'PLUGIN_NAME')
                ):
                    plugin_cls = obj
                    plugin_name = getattr(module, 'PLUGIN_NAME')
                    break
            if plugin_cls and plugin_name:
                registry.register_plugin(plugin_name, plugin_cls(logger, registry))
                logger.info(f"Discovered and registered plugin: {plugin_name}")
        except Exception as e:
            logger.error(f"Failed to import plugin {module_name}: {e}")
    return registry

def main():
    logger = SimpleLogger()
    registry = create_scaffold_plugin_registry(logger)

    parser = argparse.ArgumentParser(
        description="OmniNode Scaffold Generator CLI (plugin-based, dynamic discovery)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Scaffold commands")

    # 'new' command
    new_parser = subparsers.add_parser("new", help="Create a new scaffold")
    new_parser.add_argument("type", type=str, help="Type of scaffold (e.g., container)")
    new_parser.add_argument("name", type=str, help="Name of the scaffolded entity")
    new_parser.add_argument(
        "--output", type=str, default=".", help="Output directory (default: current)"
    )
    new_parser.add_argument(
        "--extra", nargs=argparse.REMAINDER, help="Extra plugin-specific arguments"
    )

    args = parser.parse_args()

    if not args.command:
        logger.info("Available scaffold types:")
        for t in registry.list_plugins().keys():
            logger.info(f"  - {t}")
        parser.print_help()
        sys.exit(0)

    if args.command == "new":
        plugin: Optional[ProtocolScaffoldPlugin] = registry.get_plugin(args.type)
        if not plugin:
            logger.error(f"No scaffold plugin registered for type: {args.type}")
            logger.info("Available types:")
            for t in registry.list_plugins().keys():
                logger.info(f"  - {t}")
            sys.exit(1)
        output_dir = Path(args.output).resolve()
        extra_kwargs = {}
        if args.extra:
            # Parse --key value pairs from --extra
            for i in range(0, len(args.extra), 2):
                if i+1 < len(args.extra):
                    key = args.extra[i].lstrip('-')
                    value = args.extra[i+1]
                    extra_kwargs[key] = value
        try:
            plugin.generate(args.name, output_dir, **extra_kwargs)
            logger.info(f"Scaffold '{args.type}' named '{args.name}' created at {output_dir}")
        except Exception as e:
            logger.error(f"Failed to generate scaffold: {e}")
            sys.exit(2)

if __name__ == "__main__":
    main() 