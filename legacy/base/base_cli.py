import argparse
import sys


class CLIToolBase:
    """
    Base class for all CLI tools in the foundation project.
    Provides standard argument parsing, help, error handling, and a run() method to override.
    """

    def __init__(self, description: str = "CLI tool"):
        self.parser = argparse.ArgumentParser(description=description)
        self.args = None

    def add_arguments(self):
        """Override to add custom arguments to the parser."""
        pass

    def parse_args(self):
        self.add_arguments()
        self.args = self.parser.parse_args()

    def run(self):
        """Override with the main logic for the CLI tool."""
        raise NotImplementedError("run() must be implemented by subclasses.")

    def execute(self):
        try:
            self.parse_args()
            self.run()
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
