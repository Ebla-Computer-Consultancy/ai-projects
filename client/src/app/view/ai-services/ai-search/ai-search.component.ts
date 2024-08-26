import { Component, HostListener, inject, OnInit } from '@angular/core';
import { filter, Subject, switchMap } from 'rxjs';
import { AiSearchService } from '../../../services/ai-search.service';
import { FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { SearchResult } from '../../../models/search-result';
import { CommonModule } from '@angular/common';
import { environment } from '../../../../environments/environment.prod';
import { AudioRecorderComponent } from '../../../standalone/audio-recorder/audio-recorder.component';
import { IRecordedAudioOutput } from '../../../interfaces/i-recorded-audio-output';
import { AiSpeechToTextService } from '../../../services/ai-speech-to-text.service';
@Component({
    selector: 'app-ai-search',
    standalone: true,
    imports: [ReactiveFormsModule, CommonModule, AudioRecorderComponent],
    templateUrl: './ai-search.component.html',
    styleUrls: ['./ai-search.component.scss'],
})
export class AiSearchComponent implements OnInit {
    service: AiSearchService = inject(AiSearchService);
    aiSpeechToTextService: AiSpeechToTextService = inject(
        AiSpeechToTextService
    );
    search$: Subject<void> = new Subject<void>();
    control: FormControl = new FormControl('', [Validators.required]);
    results: SearchResult[] = [];
    searchKeyWord = '';
    @HostListener('document:keypress', ['$event'])
    handleKeyboardEvent(event: KeyboardEvent) {
        if (event.key === 'Enter') {
            event.preventDefault();
            this.search$.next();
        }
    }
    constructor() {}

    ngOnInit() {
        this.listenToSearch();
    }

    listenToSearch() {
        this.search$
            .pipe(filter(() => !this.service.loading && !!this.control.valid))
            .pipe(
                switchMap(() => {
                    return this.service.search(this.control.value);
                })
            )
            .subscribe(({ rs }) => {
                this.results = rs;
                this.searchKeyWord = this.control.value;
                this.control.reset();
                this.control.updateValueAndValidity();
            });
    }

    handleSpeechToText(record: IRecordedAudioOutput) {
        const file = new File([record.blob], record.title);
        const formData = new FormData();
        formData.append('file', file);
        this.aiSpeechToTextService
            .transcribe(formData)
            .subscribe((stringText: string) => {
                if (stringText !== 'No speech could be recognized.') {
                    this.control.setValue(stringText);
                    this.search$.next();
                }
            });
    }
    readonly environment = environment;
}
