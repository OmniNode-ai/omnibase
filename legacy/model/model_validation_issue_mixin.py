class ValidationIssueMixin:
    """
    Mixin providing structured error, warning, and failed file reporting for validators.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_error(self, message: str, file: str, type: str = "error", line: int = None, details: dict = None):
        """Append a structured error to self.errors."""
        self.errors.append({
            "message": message,
            "file": file,
            "type": type,
            "line": line,
            "details": details,
        })

    def add_warning(self, message: str, file: str, type: str = "warning", line: int = None, details: dict = None):
        """Append a structured warning to self.warnings."""
        self.warnings.append({
            "message": message,
            "file": file,
            "type": type,
            "line": line,
            "details": details,
        })

    def add_failed_file(self, file: str):
        """Append a file path to self.failed_files."""
        self.failed_files.append(file) 