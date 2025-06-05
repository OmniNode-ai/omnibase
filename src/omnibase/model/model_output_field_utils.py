from typing import Any, Type, TypeVar
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

def make_output_field(field_value: Any, output_field_model_cls: Type[T]) -> T:
    """
    Converts/wraps any field_value (dict, Pydantic model, etc.) into the canonical output field model.
    Args:
        field_value: The value to wrap (dict, model, etc.)
        output_field_model_cls: The canonical output field model class for the node
    Returns:
        An instance of output_field_model_cls
    Raises:
        ValueError: If the value cannot be converted to the output field model
    """
    if isinstance(field_value, output_field_model_cls):
        return field_value
    if isinstance(field_value, BaseModel):
        # Try to convert via dict
        return output_field_model_cls(**field_value.model_dump())
    if isinstance(field_value, dict):
        return output_field_model_cls(**field_value)
    # Fallback: wrap in 'data' field if model supports it
    try:
        return output_field_model_cls(data=field_value)
    except Exception as e:
        raise ValueError(f"Cannot convert {field_value!r} to {output_field_model_cls.__name__}: {e}") 