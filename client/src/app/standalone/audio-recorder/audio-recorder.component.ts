import {
    Component,
    EventEmitter,
    Input,
    OnDestroy,
    OnInit,
    Output,
} from '@angular/core';
import { AudioRecordingService } from '../../services/audio-recording.service';
import { DomSanitizer, SafeUrl } from '@angular/platform-browser';
import { IRecordedAudioOutput } from '../../interfaces/i-recorded-audio-output';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'audio-recorder',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './audio-recorder.component.html',
    styleUrls: ['./audio-recorder.component.scss'],
})
export class AudioRecorderComponent implements OnInit, OnDestroy {
    @Output() onRecordReady: EventEmitter<IRecordedAudioOutput> =
        new EventEmitter<IRecordedAudioOutput>();
    @Input() disabled: boolean = false;
    @Input() isProcessing: boolean = false;

    isRecording = false;
    recordedTime!: string;
    blobUrl!: SafeUrl | null;
    record!: IRecordedAudioOutput;

    constructor(
        private audioRecordingService: AudioRecordingService,
        private sanitizer: DomSanitizer
    ) {
        this.audioRecordingService
            .recordingFailed()
            .subscribe(() => (this.isRecording = false));
        this.audioRecordingService
            .getRecordedTime()
            .subscribe((time) => (this.recordedTime = time));
        this.audioRecordingService.getRecordedBlob().subscribe((data) => {
            this.record = data;
            this.onRecordReady.emit(this.record);
            this.blobUrl = this.sanitizer.bypassSecurityTrustUrl(
                URL.createObjectURL(data.blob)
            );
        });
    }
    ngOnInit(): void {}

    startRecording() {
        if (!this.isRecording) {
            this.isRecording = true;
            this.audioRecordingService.startRecording();
        }
    }

    abortRecording() {
        if (this.isRecording) {
            this.isRecording = false;
            this.audioRecordingService.abortRecording();
        }
    }

    stopRecording() {
        if (this.isRecording) {
            this.audioRecordingService.stopRecording();
            this.isRecording = false;
        }
    }

    clearRecordedData() {
        this.blobUrl = null;
    }

    download(): void {
        const url = window.URL.createObjectURL(this.record.blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = this.record.title;
        link.click();
    }

    ngOnDestroy(): void {
        this.abortRecording();
    }
}
