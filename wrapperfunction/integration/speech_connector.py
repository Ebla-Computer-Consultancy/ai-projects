from fastapi import HTTPException
from fastapi.responses import JSONResponse
import requests
import azure.cognitiveservices.speech as speechsdk
import wrapperfunction.core.config as config


def transcribe_audio_file(audio_stream: str):
    speech_config = speechsdk.SpeechConfig(
        subscription=config.SPEECH_SERVICE_KEY, region=config.SPEECH_SERVICE_REGION
    )
    # speech_config.set_property(property_id=speechsdk.PropertyId.SpeechServiceConnection_LanguageIdMode, value='Continuous')
    # speech_config.speech_recognition_language="ar-QA"
    audio_input = speechsdk.AudioConfig(filename=audio_stream)

    auto_detect_source_language_config = (
        speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
            languages=["en-GB", "ar-QA", "es-ES"]
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
    }

    try:
        response = requests.post(
            f"https://{speech_region}.api.cognitive.microsoft.com/sts/v1.0/issueToken",
            headers=headers,
        )
        response.raise_for_status()
        return JSONResponse(content={"token": response.text, "region": speech_region})
    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code=401, detail="There was an error authorizing your speech key."
        )
