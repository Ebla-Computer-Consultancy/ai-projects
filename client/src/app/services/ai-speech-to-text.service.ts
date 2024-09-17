import { HttpClient, HttpHeaders } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { ApiServiceBaseModel } from '../models/api-service-base-model';
import { finalize, Observable } from 'rxjs';
// import { environment } from '../../environments/environment.prod';

@Injectable({
    providedIn: 'root',
})
export class AiSpeechToTextService extends ApiServiceBaseModel {
    protected override http: HttpClient = inject(HttpClient);
    constructor() {
        super('transcribe');
    }
    transcribe(formData: FormData): Observable<string> {
        this.startLoading();
        return this.http
            .post<string>(this.baseUrl, formData, {
                headers: new HttpHeaders({
                    enctype: 'multipart/form-data',
                    // 'x-functions-key': environment.functionDefaultKey as string,
                }),
            })
            .pipe(
                finalize(() => {
                    this.stopLoading();
                })
            );
    }
}