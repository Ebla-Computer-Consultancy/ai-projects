import { inject, Injectable } from '@angular/core';
import { ApiServiceBaseModel } from '../models/api-service-base-model';
import { HttpClient } from '@angular/common/http';
import { StreamResult } from '../models/stream-result';

@Injectable({
    providedIn: 'root',
})
export class AiAvatarService extends ApiServiceBaseModel {
    protected override http: HttpClient = inject(HttpClient);
    tag: string = 'common/';
    constructor() {
        super('avatar');
    }

    startStream() {
        return this.http.post<StreamResult>(this.baseUrl + '/start-stream', {});
    }

    sendCandidate(streamId: number, candidate: any) {
        return this.http.post(`${this.baseUrl}/send-candidate/${streamId}`, {
            candidate: candidate,
        });
    }
    sendAnswer(streamId: number, answer: any) {
        return this.http.put(`${this.baseUrl}/send-answer/${streamId}`, {
            answer: answer,
        });
    }
    closeStream(streamId: number) {
        return this.http.delete(`/close-stream/${streamId}`);
    }
    renderText(streamId: number, text: string) {
        return this.http.post(`${this.baseUrl}/render-text/${streamId}`, {
            text,
        });
    }
}
