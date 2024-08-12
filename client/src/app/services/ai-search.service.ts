import { inject, Injectable } from '@angular/core';
import { ApiServiceBaseModel } from '../models/api-service-base-model';
import { HttpClient, HttpParams } from '@angular/common/http';
import { finalize, Observable } from 'rxjs';
import { SortType } from '../types/types';
import { IResult } from '../interfaces/i-result';
import { SearchResult } from '../models/search-result';

@Injectable({
    providedIn: 'root',
})
export class AiSearchService extends ApiServiceBaseModel {
    protected override http: HttpClient = inject(HttpClient);
    constructor() {
        super('search-action');
    }
    search(
        searchQuery: string,
        sort: SortType = 'date',
        facet: string = ''
    ): Observable<IResult<SearchResult>> {
        this.startLoading();
        return this.http
            .post<{ count: number; rs: any[] }>(this.baseUrl, {
                query: searchQuery,
                sort: sort,
                facet: facet,
            })
            .pipe(
                finalize(() => {
                    this.stopLoading();
                })
            );
    }
}
