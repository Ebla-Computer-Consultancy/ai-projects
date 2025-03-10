from fastapi import HTTPException
from fastapi.responses import JSONResponse
import requests
import azure.cognitiveservices.speech as speechsdk
import wrapperfunction.core.config as config
from azure.identity import ClientSecretCredential

def transcribe_audio_file(audio_stream: str):
    speech_config = speechsdk.SpeechConfig(
        subscription=config.SPEECH_SERVICE_KEY, region=config.SPEECH_SERVICE_REGION
    )
    # speech_config.set_property(property_id=speechsdk.PropertyId.SpeechServiceConnection_LanguageIdMode, value='Continuous')
    # speech_config.speech_recognition_language="ar-QA"
    audio_input = speechsdk.AudioConfig(filename=audio_stream)

    auto_detect_source_language_config = (
        speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
            languages=["en-GB", "ar-QA", "es-ES", "fr-FR", "de-DE"]
        )
    )

    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_input,
        auto_detect_source_language_config=auto_detect_source_language_config,
    )

    result = speech_recognizer.recognize_once_async().get()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        return "No speech could be recognized."
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            return f"Transcription canceled: {cancellation_details.reason}. Error details: {cancellation_details.error_details}"
        return f"Transcription canceled: {cancellation_details.reason}"

def get_speech_token():
    speech_key = config.SPEECH_SERVICE_KEY
    speech_region = config.SPEECH_SERVICE_REGION

    if (
        speech_key == "paste-your-speech-key-here"
        or speech_region == "paste-your-speech-region-here"
    ):
        raise HTTPException(
            status_code=400,
            detail="You forgot to add your speech key or region to the .env file.",
        )

    headers = {
        "Ocp-Apim-Subscription-Key": speech_key,
        "Content-Type": "application/x-www-form-urlencoded",
        # "Authorization": f"Bearer {get_speech_entra_access_token()}",
    }

    try:
        response = requests.post(
            f"https://{speech_region}.api.cognitive.microsoft.com/sts/v1.0/issueToken",
            headers=headers,
        )
        response.raise_for_status()
        return JSONResponse(content={"token": response.text, "region": speech_region})
    except Exception as e:
        raise HTTPException(
            status_code=401, detail=str(e)
        )

def get_private_access_token():
    tenant_id = config.TENANT_ID
    client_id = config.CLIENT_ID
    client_secret = config.CLIENT_SECRET_VALUE
    speech_custom_domain_name = config.SPEECH_CUSTOM_DOMAIN_NAME
    resource_id = config.SPEECH_RESOURCE_ID

    try:
        credential = ClientSecretCredential(tenant_id, client_id, client_secret)
        token = credential.get_token("https://cognitiveservices.azure.com/.default").token
        
        authorization_token = f"aad#{resource_id}#{token}"
        endpoint = f"wss://{speech_custom_domain_name}.cognitiveservices.azure.com/stt/speech/recognition/conversation/cognitiveservices/v1"
        
        return {"token": authorization_token, "endpoint": endpoint}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))