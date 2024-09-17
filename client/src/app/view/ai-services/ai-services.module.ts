import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AiServicesComponent } from './ai-services.component';
import { RouterModule } from '@angular/router';
import { AiChatBotComponent } from './ai-chat-bot/ai-chat-bot.component';
import { AiSearchComponent } from './ai-search/ai-search.component';
@NgModule({
    imports: [
        CommonModule,
        RouterModule.forChild([
            {
                path: '',
                component: AiServicesComponent,
                children: [
                    {
                        path: '',
                        pathMatch: 'full',
                        redirectTo: '/ai-service-home',
                    },
                    {
                        path: 'ai-chat-bot',
                        component: AiChatBotComponent,
                    },
                    {
                        path: 'ai-search',
                        component: AiSearchComponent,
                    },
                ],
            },
        ]),
    ],
    declarations: [AiServicesComponent],
})
export class AiServicesModule {}