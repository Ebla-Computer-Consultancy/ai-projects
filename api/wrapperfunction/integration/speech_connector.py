import os
from dotenv import load_dotenv
import azure.cognitiveservices.speech as SpeechSDK

load_dotenv()
region = os.getenv("APP_REGION")
speech_service_key = os.getenv("SPEECH_SERVICE_KEY")
speech_config = SpeechSDK.SpeechConfig(subscription=speech_service_key, region=region)

def transcribe_audio_file(audio_stream: str):
    audio_input = SpeechSDK.AudioConfig(filename=audio_stream)

    auto_detect_source_language_config = (
        SpeechSDK.languageconfig.AutoDetectSourceLanguageConfig(
            languages=["en-GB", "ar-QA", "es-ES"]
        )
    )
    speech_recognizer = SpeechSDK.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_input,
        auto_detect_source_language_config=auto_detect_source_language_config,
    )

    result = speech_recognizer.recognize_once_async().get()
    if result.reason == SpeechSDK.ResultReason.RecognizedSpeech:
        return result.text
    elif result.reason == SpeechSDK.ResultReason.NoMatch:
        return "No speech could be recognized."
    elif result.reason == SpeechSDK.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        if cancellation_details.reason == SpeechSDK.CancellationReason.Error:
            return f"Transcription canceled: {cancellation_details.reason}. Error details: {cancellation_details.error_details}"
        return f"Transcription canceled: {cancellation_details.reason}"