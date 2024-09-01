import { inject, Injectable } from '@angular/core';
import { ApiServiceBaseModel } from '../models/api-service-base-model';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { finalize, Observable } from 'rxjs';
import { SortType } from '../types/types';
import { IResult } from '../interfaces/i-result';
import { SearchResult } from '../models/search-result';

@Injectable({
    providedIn: 'root',
})
export class AiSearchService extends ApiServiceBaseModel {
    override tag: string = 'website/';
    protected override http: HttpClient = inject(HttpClient);
    constructor() {
        super('speech/search');
    }
    search(
        searchQuery: string,
        sort: SortType = 'date',
        facet: string = ''
    ): Observable<IResult<SearchResult>> {
        this.startLoading();
        return this.http
            .post<{ count: number; rs: any[] }>(
                this.baseUrl,
                {
                    query: searchQuery,
                    sort: sort,
                    facet: facet,
                },
                {
                    headers: new HttpHeaders({
                        // 'x-functions-key':
                        //     environment.functionDefaultKey as string,
                    }),
                }
            )
            .pipe(
                finalize(() => {
                    this.stopLoading();
                })
            );
    }
}
