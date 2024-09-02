import { Component, HostListener, inject, OnInit } from '@angular/core';
import { filter, Subject, switchMap, tap } from 'rxjs';
import { AiSearchService } from '../../../services/ai-search.service';
import { FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { SearchResult } from '../../../models/search-result';
import { CommonModule } from '@angular/common';
import { environment } from '../../../../environments/environment.prod';
import { AudioRecorderComponent } from '../../../standalone/audio-recorder/audio-recorder.component';
import { IRecordedAudioOutput } from '../../../interfaces/i-recorded-audio-output';
import { AiSpeechToTextService } from '../../../services/ai-speech-to-text.service';
import { LoadingComponent } from '../../../standalone/loading/loading.component';
import { PaginationModule } from 'ngx-bootstrap/pagination';
@Component({
    selector: 'app-ai-search',
    standalone: true,
    imports: [
        ReactiveFormsModule,
        CommonModule,
        AudioRecorderComponent,
        LoadingComponent,
        PaginationModule,
    ],
    templateUrl: './ai-search.component.html',
    styleUrls: ['./ai-search.component.scss'],
})
export class AiSearchComponent implements OnInit {
    service: AiSearchService = inject(AiSearchService);
    aiSpeechToTextService: AiSpeechToTextService = inject(
        AiSpeechToTextService
    );
    search$: Subject<number> = new Subject<number>();
    control: FormControl = new FormControl('', [Validators.required]);
    results: SearchResult[] = [];
    total_count: number = 0;
    currentPage: number = 1;
    searchKeyWord = '';
    @HostListener('document:keypress', ['$event'])
    handleKeyboardEvent(event: KeyboardEvent) {
        if (event.key === 'Enter') {
            event.preventDefault();
            this.search$.next(1);
        }
    }
    constructor() {}

    ngOnInit() {
        this.listenToSearch();
    }

    listenToSearch() {
        this.search$
            .pipe(
                filter(
                    () =>
                        !this.service.loading &&
                        (!!this.control.valid || !!this.searchKeyWord)
                )
            )
            .pipe(
                tap(() => {
                    if (!this.control.value) {
                        this.control.setValue(this.searchKeyWord);
                    }
                })
            )
            .pipe(
                switchMap((page: number) => {
                    return this.service.search(this.control.value, 10, page);
                })
            )
            .subscribe(({ rs, total_count }) => {
                this.results = rs;
                this.total_count = total_count;
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
                    this.search$.next(1);
                }
            });
    }
    readonly environment = environment;
}
