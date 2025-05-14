from pydantic import BaseModel, RootModel
from typing import Dict, Generic, TypeVar
from foundation.model.model_metadata import MetadataBlockModel

T = TypeVar('T')

class KeyedDataModel(BaseModel, Generic[T]):
    data: Dict[str, T]

class KeyedMetadataBlockModel(KeyedDataModel[MetadataBlockModel]):
    pass 