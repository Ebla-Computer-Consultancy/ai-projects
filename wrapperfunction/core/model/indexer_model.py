
from enum import Enum
from typing import List
from pydantic import BaseModel

class ParsingModeKeys(Enum):
    DEFAULT = "default"
    TEXT = "text"
    JSON = "json"
    JSONArray = "jsonArray"
    JSONLines = "jsonLines"
    delimitedText = "delimitedText"
    

class DataToExtractKeys(Enum):
    ALL_METADATA = "allMetadata"
    STORAGE_METADATA = "storageMetadata"
    CONTENT_AND_METADATA = "contentAndMetadata"
    
class ImageActionKeys(Enum):
    GenerateNormalizedImages = "generateNormalizedImages"
    GenerateNormalizedImagePerPage = "generateNormalizedImagePerPage"
    
    
class IndexerParamtersConfig(BaseModel):
    def __init__(self,dataToExtract: str = DataToExtractKeys.CONTENT_AND_METADATA.value,
        parsingMode: str = ParsingModeKeys.DEFAULT.value,imageAction: str |None = None):
        self.dataToExtract = dataToExtract
        self.parsingMode = parsingMode
        self.imageAction = imageAction
    
    def to_dict(self):
        if self.imageAction is not None:
            return {
                "dataToExtract":self.dataToExtract,
                "parsingMode":self.parsingMode,
                "imageAction": self.imageAction
            }
        return{
            "dataToExtract":self.dataToExtract,
                "parsingMode":self.parsingMode
        }
class IndexerParameters(BaseModel):
    batchSize: int | None = None
    maxFailedItems: int | None = None
    maxFailedItemsPerBatch: int | None = None
    base64EncodeKeys: bool | None = None
    configuration: dict = IndexerParamtersConfig().to_dict()
    
class IndexerFieldMapping(BaseModel):
    sourceFieldName: str = "metadata_storage_name"
    targetFieldName: str = "title"
    mappingFunction: str | None = None

class Indexer:
    def __init__(self,
                 name: str, 
                 dataSourceName: str, 
                 skillsetName: str, 
                 targetIndexName: str,
                 outputFieldMappings:list = [],
                 parameters: IndexerParameters | None = None, 
                 fieldMappings: List[IndexerFieldMapping] | None = None, 
                 description: str | None = None
                 ): 
        self.name = name
        self.description = description
        self.dataSourceName = dataSourceName
        self.skillsetName = skillsetName
        self.targetIndexName = targetIndexName
        self.parameters = parameters if parameters is not None else IndexerParameters()
        self.fieldMappings = fieldMappings if fieldMappings is not None else [IndexerFieldMapping()]
        self.outputFieldMappings = outputFieldMappings
        
    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "dataSourceName": self.dataSourceName,
            "skillsetName": self.skillsetName,
            "targetIndexName": self.targetIndexName,
            "disabled": None,
            "schedule": None,
            "parameters": self.parameters,
            "fieldMappings": self.fieldMappings,
            "outputFieldMappings": self.outputFieldMappings,
            "encryptionKey": None
        }