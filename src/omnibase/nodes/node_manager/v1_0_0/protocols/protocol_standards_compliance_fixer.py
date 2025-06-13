from typing import Protocol, List, Optional
from pathlib import Path

from omnibase.nodes.node_manager.v1_0_0.models.model_standards_fix_result import ModelStandardsFixResult
from omnibase.nodes.node_manager.v1_0_0.models.model_template_validation_result import TemplateValidationResultModel
from omnibase.nodes.node_manager.v1_0_0.enums.enum_fix_operation_type import EnumFixOperationType


class ProtocolStandardsComplianceFixer(Protocol):
    """Protocol for standards compliance fixing with auto-remediation capabilities."""
    
    def fix_standards_violations(
        self,
        target_path: Path,
        dry_run: bool = True,
        fix_types: Optional[List[EnumFixOperationType]] = None,
        create_backups: bool = True
    ) -> ModelStandardsFixResult:
        """
        Fix standards compliance violations in the target path.
        
        Args:
            target_path: Path to file or directory to fix
            dry_run: If True, only report what would be fixed without making changes
            fix_types: Optional list of specific fix types to apply
            create_backups: Whether to create backup files before making changes
            
        Returns:
            ModelStandardsFixResult with details of all fix operations
        """
        ...
    
    def fix_template_artifacts(
        self,
        target_path: Path,
        dry_run: bool = True,
        create_backups: bool = True
    ) -> ModelStandardsFixResult:
        """
        Fix template artifacts (template_node references, etc.) in target path.
        
        Args:
            target_path: Path to file or directory to fix
            dry_run: If True, only report what would be fixed without making changes
            create_backups: Whether to create backup files before making changes
            
        Returns:
            ModelStandardsFixResult with details of template artifact fixes
        """
        ...
    
    def fix_naming_conventions(
        self,
        target_path: Path,
        dry_run: bool = True,
        create_backups: bool = True
    ) -> ModelStandardsFixResult:
        """
        Fix naming convention violations in target path.
        
        Args:
            target_path: Path to file or directory to fix
            dry_run: If True, only report what would be fixed without making changes
            create_backups: Whether to create backup files before making changes
            
        Returns:
            ModelStandardsFixResult with details of naming convention fixes
        """
        ...
    
    def fix_file_organization(
        self,
        target_path: Path,
        dry_run: bool = True,
        create_backups: bool = True
    ) -> ModelStandardsFixResult:
        """
        Fix file organization issues (models in wrong directories, etc.).
        
        Args:
            target_path: Path to file or directory to fix
            dry_run: If True, only report what would be fixed without making changes
            create_backups: Whether to create backup files before making changes
            
        Returns:
            ModelStandardsFixResult with details of file organization fixes
        """
        ...
    
    def validate_and_fix(
        self,
        target_path: Path,
        dry_run: bool = True,
        create_backups: bool = True
    ) -> ModelStandardsFixResult:
        """
        Run validation and automatically fix detected issues.
        
        Args:
            target_path: Path to file or directory to validate and fix
            dry_run: If True, only report what would be fixed without making changes
            create_backups: Whether to create backup files before making changes
            
        Returns:
            ModelStandardsFixResult with details of all validation and fix operations
        """
        ...
    
    def create_backup(self, file_path: Path) -> Optional[Path]:
        """
        Create a backup of the specified file.
        
        Args:
            file_path: Path to file to backup
            
        Returns:
            Path to backup file if successful, None otherwise
        """
        ...
    
    def restore_from_backup(self, backup_path: Path, original_path: Path) -> bool:
        """
        Restore a file from its backup.
        
        Args:
            backup_path: Path to backup file
            original_path: Path where file should be restored
            
        Returns:
            True if restore was successful, False otherwise
        """
        ... 