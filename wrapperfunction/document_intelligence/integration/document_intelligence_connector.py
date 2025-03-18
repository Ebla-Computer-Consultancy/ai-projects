
from fastapi import UploadFile

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult, AnalyzeDocumentRequest
from wrapperfunction.core import config


def analyze_file(
    file: UploadFile | None,
    model_id: str = "prebuilt-layout",
    file_bytes: bytes = None
) -> AnalyzeResult:
    document_intelligence_client = DocumentIntelligenceClient(
        endpoint=config.DOCUMENT_INTELLIGENCE_ENDPOINT,
        credential=AzureKeyCredential(config.DOCUMENT_INTELLIGENCE_API_KEY),
    )
    poller = document_intelligence_client.begin_analyze_document(
        model_id,
        AnalyzeDocumentRequest(bytes_source=file_bytes if file_bytes else file.file.read()),
    )

    return poller.result()
