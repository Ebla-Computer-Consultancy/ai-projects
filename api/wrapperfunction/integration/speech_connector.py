import azure.cognitiveservices.speech as speechsdk
import wrapperfunction.core.config as config



def transcribe_audio_file(audio_stream: str):
    speech_config = speechsdk.SpeechConfig(subscription=config.SPEECH_SERVICE_KEY, region=config.SPEECH_APP_REGION)
    speech_config.set_property(property_id=speechsdk.PropertyId.SpeechServiceConnection_LanguageIdMode, value='Continuous')
    # speech_config.speech_recognition_language="ar-QA"
    print("action called")
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