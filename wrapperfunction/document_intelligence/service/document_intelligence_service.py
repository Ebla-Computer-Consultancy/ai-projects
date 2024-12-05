
import ast
from io import BytesIO
import json
import os
from typing import Optional
import uuid
import zipfile
from fastapi import File, HTTPException, UploadFile
from pypdf import PdfReader, PdfWriter
from wrapperfunction.chatbot.model.chat_payload import ChatPayload
from wrapperfunction.core import config
import wrapperfunction.document_intelligence.integration.document_intelligence_connector as documentintelligenceconnector
import wrapperfunction.chatbot.service.chatbot_service as chatbotservice
import wrapperfunction.chatbot.integration.openai_connector as openaiconnector
import wrapperfunction.admin.integration.storage_connector as storageconnector



def analyze_file(model_id: str, bot_name: str, file: UploadFile = File()):
    try:
        poller_result = documentintelligenceconnector.analyze_file(file, model_id)
        file_result = {"content": poller_result.content, "tables": []}
        for index, table in enumerate(poller_result.tables):
            file_result["tables"].append({"cells": []})
            for cell in table["cells"]:
                file_result["tables"][index]["cells"].append(
                    {"content": cell["content"], "kind": cell.kind}
                )

        return chatbotservice.ask_open_ai_chatbot(
            bot_name=bot_name,
            chat_payload=ChatPayload(
                messages=[
                    {
                        "role": "user",
                        "content": json.dumps(
                            file_result,
                            ensure_ascii=False,
                        ),
                    }
                ]
            ),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

        #   "content": "{'manufacturer':{'producer':'','supplier':'','company-name':'','manufacturer-supplier':'','manufacturers-name-and-Address':''},'trade-name':{'product-name':'','commercial-name':'','brand-name':'','product-identifier':'','proprietary-name':'','common-name':''},'chemical-name':{'substance-name':'','scientific-name':'','iupac-name':'','proper-Chemical-name':'','systematic-name':''},'cas-no':{'cas-registry-number':'','chemical-abstracts-service-number':'','cas-number':'','cas-identification-number':'','cas-rn':''},'state':{'physical-state':'','form':'','appearance':'','condition-Solid-Liquid-Gas':'','state-of-matter':''},'storage-condition':{'storage-requirements':'','storage-guidelines':'','storage-instructions':'','storage-information':'','storage-recommendations':''},'prevention-method':{'preventative-measures':'','safety-precautions':'','preventive-actions':'','hazard-prevention':'','precautionary-measures':''},'control-method':{'control-measures':'','exposure-controls':'','protection-measures':'','control-procedures':'','engineering-controls':''},'classification':{'hazard-classification':'','risk-classification':'','hazard-category':'','hazard-class':'','ghs-classification-globally-harmonized-system':''},'hs-code':{'harmonized-system-code':'','harmonized-tariff-code':'','hts-code':'','customs-code':'','tariff-code':''},'un-no':{'un-number':'','un-identification-number':'','united-nations-number':'','un-id':'','un-hazard-number':''}}"

def get_openai_instruction(prompt):

    try:
        response = openaiconnector.client.chat.completions.create(
            engine=config.OPENAI_CHAT_MODEL,  
            messages=[{"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.5,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error with Azure OpenAI API: {e}"


def detection(text,criteria:Optional[str] = None):
    if not criteria:
        prompt = (
            "The following text is extracted from file. Identify the best practice to split this file. "
            "Return the results as a Python list of page number ranges without any extra text. Example: [[1, 10], [11, 20]].\n\n"
            f"{text}"
        )
    else:
        prompt = (
    f"The following text is extracted from a file. Split the file based on the following criteria: {criteria}. "
    "If splitting based on this criteria is not possible, identify the best practice for splitting the file. "
    "Return the results as a Python list of page number ranges (e.g., [[1, 10], [11, 20]])with no additional text. "
    "If no split is possible, return an empty list `[]` with no additional text.\n\n"
    f"{text}"
)
    try:
        response = openaiconnector.client.chat.completions.create( 
            model=config.OPENAI_CHAT_MODEL, 
            messages=[ 
                {"role": "system", "content": "You are a helpful assistant."}, 
                {"role": "user", "content": prompt} 
            ], 
            max_tokens=200, 
            temperature=0.4, 
        )
        content = response.choices[0].message.content  
        return list(ast.literal_eval(content))
    except Exception as e:
        return f"Error with Azure OpenAI API: {e}"



def auto_split_pdf(pdf, criteria):
    try:
        reader = PdfReader(pdf)
        text_per_page = [page.extract_text() for page in reader.pages]
        full_text = "\n".join(f"Page {i+1}:\n{text}" for i, text in enumerate(text_per_page))

        pages = detection(full_text, criteria)


        pages.append([len(reader.pages) + 1])  
        files = []

        for i in range(len(pages) - 1):
            writer = PdfWriter()

            for j in range(pages[i][0] - 1, pages[i + 1][0] - 1):
                writer.add_page(reader.pages[j])

            output_file_path = f"{i + 1}.pdf"
            with open(output_file_path, "wb") as output_file:
                writer.write(output_file)
            files.append(output_file_path)

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file in files:
                zip_file.write(file, os.path.basename(file))
                os.remove(file) 
        zip_buffer.seek(0)


        container_client = storageconnector.get_blob_service_client(config.SPLITER_CONTAINER_NAME)
        response = container_client.upload_blob(f"{uuid.uuid4()}.zip", zip_buffer, overwrite=True)

        return {"status": "success", "message": "Zip file uploaded successfully", "url": f"{response.url}", "ranges": f"{pages}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
