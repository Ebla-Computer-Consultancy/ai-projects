import { Routes } from '@angular/router';
import { AiServiceHomeComponent } from './view/ai-service-home/ai-service-home.component';

export const routes: Routes = [
    {
        path: '',
        pathMatch: 'full',
        redirectTo: '/ai-service-home',
    },
    {
        path: 'ai-service-home',
        component: AiServiceHomeComponent,
    },
    {
        path: 'ai-service',
        loadChildren: () =>
            import('./view/ai-services/ai-services.module').then(
                (m) => m.AiServicesModule
            ),
    },
];
