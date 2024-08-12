import { Component, HostListener, inject, OnInit } from '@angular/core';
import { filter, Subject, switchMap } from 'rxjs';
import { AiSearchService } from '../../../services/ai-search.service';
import { FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { SearchResult } from '../../../models/search-result';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-ai-search',
    standalone: true,
    imports: [ReactiveFormsModule, CommonModule],
    templateUrl: './ai-search.component.html',
    styleUrls: ['./ai-search.component.scss'],
})
export class AiSearchComponent implements OnInit {
    service: AiSearchService = inject(AiSearchService);
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
}
