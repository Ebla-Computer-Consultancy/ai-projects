import {
    Component,
    EventEmitter,
    inject,
    Input,
    OnDestroy,
    OnInit,
    Output,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { AiSpeechToTextService } from '../../services/ai-speech-to-text.service';
import {
    SpeechConfig,
    SpeechRecognizer,
    ResultReason,
    AudioConfig,
    AutoDetectSourceLanguageConfig,
} from 'microsoft-cognitiveservices-speech-sdk';
@Component({
    selector: 'audio-recorder',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './audio-recorder.component.html',
    styleUrls: ['./audio-recorder.component.scss'],
})
export class AudioRecorderComponent implements OnInit, OnDestroy {
    @Output() onRecordReady: EventEmitter<string> = new EventEmitter<string>();
    @Output() onStopRecording: EventEmitter<void> = new EventEmitter<void>();
    result = '';
    recognizedText = '';
    @Input() disabled: boolean = false;
    @Input() isProcessing: boolean = false;
    aiSpeechToTextService = inject(AiSpeechToTextService);
    isRecording = false;
    recognizer!: SpeechRecognizer;
    speechConfig!: SpeechConfig;
    stream!: MediaStream;
    constraints = {
        video: false,
        audio: {
            channelCount: 1,
            sampleRate: 16000,
            sampleSize: 16,
            volume: 1,
        },
    };
    constructor() {}
    ngOnInit(): void {
        this.aiSpeechToTextService
            .requestAuthorizationToken()
            .subscribe(({ token, region }) => {
                this.speechConfig = SpeechConfig.fromAuthorizationToken(
                    token,
                    region
                );
            });
    }
    startRecording() {
        if (!this.isRecording) {
            this.isRecording = true;
            navigator.mediaDevices
                .getUserMedia(this.constraints)
                .then((stream) => {
                    this.stream = stream;
                    const audioConfig = AudioConfig.fromStreamInput(stream);
                    const autoDetectSourceLanguageConfig =
                        AutoDetectSourceLanguageConfig.fromLanguages([
                            'ar-QA',
                            'en-US',
                        ]);
                    this.recognizer = SpeechRecognizer.FromConfig(
                        this.speechConfig,
                        autoDetectSourceLanguageConfig,
                        audioConfig
                    );
                    this.recognizedText = '';
                    this.recognizer.recognized = (s, e) => {
                        if (e.result.reason === ResultReason.RecognizedSpeech) {
                            this.recognizedText += e.result.text;
                            this.onRecordReady.emit(this.recognizedText);
                        } else if (e.result.reason === ResultReason.NoMatch) {
                            console.error(
                                'NOMATCH: Speech could not be recognized.'
                            );
                        }
                    };
                    this.recognizer.startContinuousRecognitionAsync();
                });
        }
    }
    stopRecording() {
        if (this.isRecording) {
            this.onStopRecording.emit();
            this.stream.getTracks().forEach((track) => {
                track.stop();
            });
            this.recognizer.stopContinuousRecognitionAsync();
            this.isRecording = false;
        }
    }

    ngOnDestroy(): void {}
}
