from enum import Enum
from typing import List

from wrapperfunction.core import config
from wrapperfunction.core.model.skillset_model import Map, Output


class Skilltype(Enum):
    SplitSkill="#Microsoft.Skills.Text.SplitSkill"
    EmbeddingSkill="#Microsoft.Skills.Text.AzureOpenAIEmbeddingSkill"


class Skill:
    def __init__(self,
                skilltype: Skilltype,
                name: str,
                description: str,
                context: str,
                inputs: List[Map],
                outputs: List[Output],
                ):
        
                    self.skilltype = skilltype
                    self.name = name
                    self.description = description
                    self.context = context
                    self.inputs = inputs
                    self.outputs = outputs
class SplitSkill(Skill):
    def __init__(self, skilltype, name, description, context, inputs, outputs, defaultLanguageCode: str | None = None, textSplitMode: str | None = None, maximumPageLength :int | None = None, pageOverlapLength :int | None = None, unit: str | None = None):
         super().__init__(skilltype, name, description, context, inputs, outputs)
         self.defaultLanguageCode = defaultLanguageCode if defaultLanguageCode is not None else "en"
         self.textSplitMode = textSplitMode if textSplitMode is not None else "pages"
         self.maximumPageLength = maximumPageLength if maximumPageLength is not None else 2000
         self.pageOverlapLength = pageOverlapLength if pageOverlapLength is not None else 500
         self.unit = unit if unit is not None else "characters"
             
    def to_dict(self):
        return{
            "@odata.type": self.skilltype,
            "name": self.name,
            "description": self.description,
            "context": self.context,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "defaultLanguageCode":self.defaultLanguageCode,
            "textSplitMode":self.textSplitMode,
            "maximumPageLength":self.maximumPageLength,
            "pageOverlapLength":self.pageOverlapLength,
        }

class TextEmbeddingSkill(Skill):
    def __init__(self, skilltype, name, description, context, inputs, outputs, resourceUri: str | None = None, deploymentId: str | None = None, apiKey :str | None = None, modelName :str | None = None, dimensions: str | None = None):
         super().__init__(skilltype, name, description, context, inputs, outputs)
         self.resourceUri = resourceUri if resourceUri is not None else config.OPENAI_ENDPOINT
         self.deploymentId = deploymentId if deploymentId is not None else config.OPENAI_EMB_MODEL
         self.apiKey = apiKey if apiKey is not None else config.OPENAI_API_KEY
         self.modelName = modelName if modelName is not None else "text-embedding-3-large"
         self.dimensions = dimensions if dimensions is not None else 3072
             
    def to_dict(self):
        return{
            "@odata.type": self.skilltype,
            "name": self.name,
            "description": self.description,
            "context": self.context,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "resourceUri":self.resourceUri,
            "deploymentId":self.deploymentId,
            "apiKey":self.apiKey,
            "modelName":self.modelName,
            "dimensions":self.dimensions
        }