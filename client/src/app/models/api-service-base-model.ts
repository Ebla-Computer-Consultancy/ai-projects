import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment.prod';

export abstract class ApiServiceBaseModel {
    protected abstract http: HttpClient;
    loading: boolean = false;
    constructor(private _baseUrl: string) {}
    get baseUrl() {
        return environment.endpoint + this._baseUrl;
    }
    startLoading() {
        this.loading = true;
    }
    stopLoading() {
        this.loading = false;
    }
}
