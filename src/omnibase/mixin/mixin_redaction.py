# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: mixin_redaction.py
# version: 1.0.0
# uuid: 7bacf50d-e858-46e4-9ad5-0f66a25b7356
# author: OmniNode Team
# created_at: 2025-05-26T10:41:44.129572
# last_modified_at: 2025-05-26T16:53:38.721433
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 497493808f9eeb848fc2811128e8610a9aa6ea0fbc1bd334fb574889b9bfbee6
# entrypoint: python@mixin_redaction.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.mixin_redaction
# meta_type: tool
# === /OmniNode:Metadata ===


from typing import Any, Dict, List, Optional, Set


class SensitiveFieldRedactionMixin:
    """
    Pure mixin for sensitive field redaction in Pydantic models.

    Provides automatic redaction of sensitive fields in model_dump() output
    and a dedicated redact() method for explicit redaction.

    Compatible with Pydantic BaseModel inheritance.
    """

    # Default sensitive field patterns
    _DEFAULT_SENSITIVE_PATTERNS = [
        "password",
        "passwd",
        "secret",
        "token",
        "key",
        "credential",
        "auth",
        "api_key",
        "access_key",
        "private_key",
        "cert",
        "certificate",
        "signature",
        "hash",
        "salt",
    ]

    # Default redaction values
    _DEFAULT_REDACTION_VALUES = {
        "string": "[REDACTED]",
        "token": "[MASKED]",
        "secret": "[SECRET]",
        "key": "[KEY_REDACTED]",
        "password": "[PASSWORD_REDACTED]",
        "default": "[SENSITIVE]",
    }

    @classmethod
    def get_sensitive_field_patterns(cls) -> List[str]:
        """
        Get the list of sensitive field patterns for this model.

        Override this method in subclasses to customize sensitive field detection.

        Returns:
            List of lowercase patterns that identify sensitive fields
        """
        return cls._DEFAULT_SENSITIVE_PATTERNS.copy()

    @classmethod
    def get_redaction_values(cls) -> Dict[str, str]:
        """
        Get the redaction values for different field types.

        Override this method in subclasses to customize redaction values.

        Returns:
            Dictionary mapping field types to redaction values
        """
        return cls._DEFAULT_REDACTION_VALUES.copy()

    @classmethod
    def is_sensitive_field(cls, field_name: str) -> bool:
        """
        Check if a field name matches sensitive field patterns.

        Args:
            field_name: Name of the field to check

        Returns:
            True if field is considered sensitive, False otherwise
        """
        field_lower = field_name.lower()
        patterns = cls.get_sensitive_field_patterns()

        return any(pattern in field_lower for pattern in patterns)

    @classmethod
    def get_redaction_value(cls, field_name: str, field_value: Any) -> str:
        """
        Get the appropriate redaction value for a field.

        Args:
            field_name: Name of the field being redacted
            field_value: Original value of the field

        Returns:
            Appropriate redaction string for the field
        """
        redaction_values = cls.get_redaction_values()
        field_lower = field_name.lower()

        # Check for specific field type patterns
        if "password" in field_lower or "passwd" in field_lower:
            return redaction_values.get("password", redaction_values["default"])
        elif "token" in field_lower:
            return redaction_values.get("token", redaction_values["default"])
        elif "secret" in field_lower:
            return redaction_values.get("secret", redaction_values["default"])
        elif "key" in field_lower:
            return redaction_values.get("key", redaction_values["default"])
        else:
            return redaction_values.get("string", redaction_values["default"])

    def redact_sensitive_fields(
        self,
        data: Dict[str, Any],
        additional_sensitive_fields: Optional[Set[str]] = None,
    ) -> Dict[str, Any]:
        """
        Redact sensitive fields in a dictionary.

        Args:
            data: Dictionary to redact sensitive fields from
            additional_sensitive_fields: Additional field names to treat as sensitive

        Returns:
            Dictionary with sensitive fields redacted
        """
        redacted_data = data.copy()
        additional_fields = additional_sensitive_fields or set()

        for field_name, field_value in data.items():
            # Check if field is sensitive by pattern or explicit list
            if self.is_sensitive_field(field_name) or field_name in additional_fields:

                # Only redact non-None values
                if field_value is not None:
                    redacted_data[field_name] = self.get_redaction_value(
                        field_name, field_value
                    )

            # Recursively redact nested dictionaries
            elif isinstance(field_value, dict):
                redacted_data[field_name] = self.redact_sensitive_fields(
                    field_value, additional_sensitive_fields
                )

            # Redact items in lists that are dictionaries
            elif isinstance(field_value, list):
                redacted_list = []
                for item in field_value:
                    if isinstance(item, dict):
                        redacted_list.append(
                            self.redact_sensitive_fields(
                                item, additional_sensitive_fields
                            )
                        )
                    else:
                        redacted_list.append(item)
                redacted_data[field_name] = redacted_list

        return redacted_data

    def redact(
        self, additional_sensitive_fields: Optional[Set[str]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Get a redacted version of the model data.

        Args:
            additional_sensitive_fields: Additional field names to treat as sensitive
            **kwargs: Additional arguments passed to model_dump()

        Returns:
            Dictionary with sensitive fields redacted
        """
        # Get the model data using standard model_dump
        if hasattr(self, "model_dump"):
            data = self.model_dump(**kwargs)  # type: ignore[attr-defined]
        else:
            # Fallback for non-Pydantic models
            data = {
                field: getattr(self, field) for field in getattr(self, "__fields__", {})
            }

        return self.redact_sensitive_fields(data, additional_sensitive_fields)

    def model_dump_redacted(
        self, additional_sensitive_fields: Optional[Set[str]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Convenience method that combines model_dump with redaction.

        Args:
            additional_sensitive_fields: Additional field names to treat as sensitive
            **kwargs: Additional arguments passed to model_dump()

        Returns:
            Dictionary with sensitive fields redacted
        """
        return self.redact(additional_sensitive_fields, **kwargs)
