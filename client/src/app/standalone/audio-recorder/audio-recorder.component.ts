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
    @Input() disabled: boolean = true;
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
                this.disabled = false;
            });
    }
    startRecording() {
        if (!this.isRecording) {
            this.isRecording = true;
            navigator.mediaDevices
                .getUserMedia(this.constraints)
                .then((stream) => {
                    try {
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
                        this.recognizer.recognizing = (s, e) => {
                            this.isProcessing = true;
                            if (e.result.text) {
                                this.onRecordReady.emit(e.result.text);
                            }
                        };
                        this.recognizedText = '';
                        this.recognizer.recognized = (s, e) => {
                            this.isProcessing = false;
                            if (e.result.text) {
                                this.recognizedText += ' ' + e.result.text;
                            }
                            this.onRecordReady.emit(this.recognizedText);
                        };

                        this.recognizer.startContinuousRecognitionAsync();
                    } catch {
                        this.isRecording = false;
                        this.stream.getTracks().forEach((track) => {
                            track.stop();
                        });
                    }
                });
        }
    }
    stopRecording() {
        if (this.isRecording) {
            this.onStopRecording.emit();
            this.recognizer.stopContinuousRecognitionAsync();
            this.isRecording = false;
        }
    }

    ngOnDestroy(): void {}
}
