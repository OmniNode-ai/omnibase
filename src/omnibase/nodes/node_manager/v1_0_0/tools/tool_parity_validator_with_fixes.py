from pathlib import Path
from typing import List, Optional, Dict, Any
import subprocess
import json

from omnibase.enums.log_level import SeverityLevelEnum
from omnibase.nodes.node_logger.protocols.protocol_logger_emit_log_event import ProtocolLoggerEmitLogEvent
from omnibase.nodes.node_manager.v1_0_0.models.model_standards_fix_result import ModelStandardsFixResult
from omnibase.nodes.node_manager.v1_0_0.models.model_validation_result import ModelValidationResult
from omnibase.nodes.node_manager.v1_0_0.tools.tool_standards_compliance_fixer import ToolStandardsComplianceFixer
from omnibase.nodes.node_manager.v1_0_0.tools.tool_file_generator import ToolFileGenerator


class ToolParityValidatorWithFixes:
    """Tool that combines parity validation with automatic standards compliance fixing."""
    
    def __init__(self, logger_tool: ProtocolLoggerEmitLogEvent):
        if logger_tool is None:
            raise RuntimeError("Logger tool must be provided via DI or registry (protocol-pure).")
        self.logger_tool = logger_tool
        self.standards_fixer = ToolStandardsComplianceFixer(logger_tool)
        self.file_generator = ToolFileGenerator(event_bus=None, logger_tool=logger_tool)
    
    def validate_and_fix(
        self,
        target_path: Path,
        fix_mode: bool = False,
        dry_run: bool = True,
        create_backups: bool = True,
        validation_types: Optional[List[str]] = None,
        format_output: str = "detailed"
    ) -> Dict[str, Any]:
        """
        Run parity validation and optionally fix detected issues.
        
        Args:
            target_path: Path to validate and fix
            fix_mode: Whether to attempt fixes for detected issues
            dry_run: If True, only report what would be fixed without making changes
            create_backups: Whether to create backup files before making changes
            validation_types: Optional list of specific validation types to run
            format_output: Output format (summary, detailed, json)
            
        Returns:
            Dictionary containing validation results and fix results
        """
        results = {
            "validation_result": None,
            "fix_result": None,
            "summary": "",
            "success": False
        }
        
        try:
            # Step 1: Run parity validation
            validation_result = self._run_parity_validation(
                target_path, validation_types, format_output
            )
            results["validation_result"] = validation_result
            
            # Step 2: If validation failed and fix_mode is enabled, attempt fixes
            if not validation_result.success and fix_mode:
                fix_result = self.standards_fixer.validate_and_fix(
                    target_path, dry_run, create_backups
                )
                results["fix_result"] = fix_result
                
                # Step 3: Re-run validation after fixes to check improvement
                if not dry_run and fix_result.fixes_successful > 0:
                    post_fix_validation = self._run_parity_validation(
                        target_path, validation_types, format_output
                    )
                    results["post_fix_validation"] = post_fix_validation
                    results["success"] = post_fix_validation.success
                else:
                    results["success"] = fix_result.success
                
                # Generate summary
                if dry_run:
                    results["summary"] = (
                        f"[DRY RUN] Validation found {len(validation_result.errors)} issues. "
                        f"Would attempt to fix {fix_result.total_fixes_attempted} items."
                    )
                else:
                    results["summary"] = (
                        f"Validation found {len(validation_result.errors)} issues. "
                        f"Fixed {fix_result.fixes_successful}/{fix_result.total_fixes_attempted} items."
                    )
            else:
                results["success"] = validation_result.success
                if validation_result.success:
                    results["summary"] = "All parity validation checks passed."
                else:
                    results["summary"] = f"Parity validation failed with {len(validation_result.errors)} issues."
            
            return results
            
        except Exception as e:
            results["summary"] = f"Validation and fix process failed: {str(e)}"
            results["success"] = False
            return results
    
    def fix_specific_issues(
        self,
        target_path: Path,
        issue_types: List[str],
        dry_run: bool = True,
        create_backups: bool = True
    ) -> ModelStandardsFixResult:
        """
        Fix specific types of standards compliance issues.
        
        Args:
            target_path: Path to fix
            issue_types: List of issue types to fix (template_artifacts, naming_conventions, file_organization)
            dry_run: If True, only report what would be fixed without making changes
            create_backups: Whether to create backup files before making changes
            
        Returns:
            ModelStandardsFixResult with details of fix operations
        """
        try:
            if "template_artifacts" in issue_types:
                return self.standards_fixer.fix_template_artifacts(target_path, dry_run, create_backups)
            elif "naming_conventions" in issue_types:
                return self.standards_fixer.fix_naming_conventions(target_path, dry_run, create_backups)
            elif "file_organization" in issue_types:
                return self.standards_fixer.fix_file_organization(target_path, dry_run, create_backups)
            else:
                return self.standards_fixer.fix_standards_violations(target_path, dry_run, None, create_backups)
                
        except Exception as e:
            return ModelStandardsFixResult(
                success=False,
                total_fixes_attempted=0,
                fixes_successful=0,
                fixes_failed=1,
                fixes_skipped=0,
                operations=[],
                errors=[f"Failed to fix specific issues: {str(e)}"],
                warnings=[],
                summary=f"Fix operation failed: {str(e)}",
                dry_run=dry_run
            )
    
    def batch_fix_nodes(
        self,
        nodes_directory: Path,
        dry_run: bool = True,
        create_backups: bool = True,
        node_filter: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run validation and fixes across multiple nodes.
        
        Args:
            nodes_directory: Directory containing nodes to process
            dry_run: If True, only report what would be fixed without making changes
            create_backups: Whether to create backup files before making changes
            node_filter: Optional list of specific node names to process
            
        Returns:
            Dictionary containing batch processing results
        """
        results = {
            "nodes_processed": 0,
            "nodes_successful": 0,
            "nodes_failed": 0,
            "total_fixes": 0,
            "node_results": {},
            "summary": "",
            "success": False
        }
        
        try:
            if not nodes_directory.exists() or not nodes_directory.is_dir():
                results["summary"] = f"Nodes directory not found: {nodes_directory}"
                return results
            
            # Find all node directories
            node_dirs = [d for d in nodes_directory.iterdir() if d.is_dir() and not d.name.startswith('.')]
            
            if node_filter:
                node_dirs = [d for d in node_dirs if d.name in node_filter]
            
            for node_dir in node_dirs:
                try:
                    node_result = self.validate_and_fix(
                        node_dir, fix_mode=True, dry_run=dry_run, create_backups=create_backups
                    )
                    
                    results["node_results"][node_dir.name] = node_result
                    results["nodes_processed"] += 1
                    
                    if node_result["success"]:
                        results["nodes_successful"] += 1
                    else:
                        results["nodes_failed"] += 1
                    
                    if node_result.get("fix_result"):
                        results["total_fixes"] += node_result["fix_result"].fixes_successful
                        
                except Exception as e:
                    results["node_results"][node_dir.name] = {
                        "success": False,
                        "summary": f"Processing failed: {str(e)}"
                    }
                    results["nodes_failed"] += 1
            
            results["success"] = results["nodes_failed"] == 0
            
            if dry_run:
                results["summary"] = (
                    f"[DRY RUN] Processed {results['nodes_processed']} nodes. "
                    f"Would fix {results['total_fixes']} issues across {results['nodes_successful']} nodes."
                )
            else:
                results["summary"] = (
                    f"Processed {results['nodes_processed']} nodes. "
                    f"Fixed {results['total_fixes']} issues. "
                    f"Success: {results['nodes_successful']}, Failed: {results['nodes_failed']}"
                )
            
            return results
            
        except Exception as e:
            results["summary"] = f"Batch processing failed: {str(e)}"
            results["success"] = False
            return results
    
    def _run_parity_validation(
        self,
        target_path: Path,
        validation_types: Optional[List[str]] = None,
        format_output: str = "detailed"
    ) -> ModelValidationResult:
        """Run the existing parity validation."""
        try:
            # Use the existing file generator's parity validation method
            return self.file_generator.run_parity_validation(target_path)
            
        except Exception as e:
            # Fallback to direct subprocess call if file generator method fails
            return self._run_parity_validation_subprocess(target_path, validation_types, format_output)
    
    def _run_parity_validation_subprocess(
        self,
        target_path: Path,
        validation_types: Optional[List[str]] = None,
        format_output: str = "detailed"
    ) -> ModelValidationResult:
        """Run parity validation via subprocess as fallback."""
        try:
            cmd = [
                "poetry", "run", "onex", "run", "parity_validator_node",
                "--args", f'["--nodes-directory", "{target_path}", "--format", "{format_output}"]'
            ]
            
            if validation_types:
                validation_types_str = ",".join(validation_types)
                cmd = [
                    "poetry", "run", "onex", "run", "parity_validator_node",
                    "--args", f'["--nodes-directory", "{target_path}", "--validation-types", "{validation_types_str}", "--format", "{format_output}"]'
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
            
            if result.returncode == 0:
                try:
                    if format_output == "json":
                        validation_data = json.loads(result.stdout)
                        errors = validation_data.get("errors", [])
                        success = len(errors) == 0
                    else:
                        # Parse text output for errors
                        errors = []
                        success = "FAIL" not in result.stdout and "ERROR" not in result.stdout
                        if not success:
                            errors = ["Validation failed - see details for specifics"]
                    
                    return ModelValidationResult(
                        success=success,
                        details=result.stdout,
                        errors=errors,
                        metadata=None
                    )
                except Exception:
                    return ModelValidationResult(
                        success=False,
                        details=result.stdout,
                        errors=["Failed to parse validation output"],
                        metadata=None
                    )
            else:
                return ModelValidationResult(
                    success=False,
                    details=result.stderr,
                    errors=[f"Validation command failed: {result.stderr}"],
                    metadata=None
                )
                
        except Exception as e:
            return ModelValidationResult(
                success=False,
                details=str(e),
                errors=[f"Failed to run parity validation: {str(e)}"],
                metadata=None
            ) 