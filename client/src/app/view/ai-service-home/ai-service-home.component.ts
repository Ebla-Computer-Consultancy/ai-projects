import { Component, OnInit } from '@angular/core';
import { RouterModule } from '@angular/router';

@Component({
    selector: 'app-ai-service-home',
    standalone: true,
    imports: [RouterModule],
    templateUrl: './ai-service-home.component.html',
    styleUrls: ['./ai-service-home.component.scss'],
})
export class AiServiceHomeComponent implements OnInit {
    services: {
        id: number;
        icon: string;
        title: string;
        route: string;
        description: string;
    }[] = [
        {
            id: 1,
            icon: 'robot-confused-outline',
            title: 'Chat bot',
            route: '/ai-service/ai-chat-bot',
            description:
                'Lorem ipsum dolor sit, amet consectetur adipisicing elit. Aperiam autem amet, rem libero, necessitatibus maiores, possimus adipisci sint quae reiciendis ab impedit quo a! Cum voluptatibus neque libero animi asperiores!',
        },
        {
            id: 2,
            icon: 'magnify',
            title: 'AI Search',
            route: '/ai-service/ai-search',
            description:
                'Lorem ipsum dolor sit, amet consectetur adipisicing elit. Aperiam autem amet, rem libero, necessitatibus maiores, possimus adipisci sint quae reiciendis ab impedit quo a! Cum voluptatibus neque libero animi asperiores!',
        },
        {
            id: 3,
            icon: 'microphone-message',
            title: 'AI Speech to Text',
            route: '/ai-service/ai-speech-to-text',
            description:
                'Lorem ipsum dolor sit, amet consectetur adipisicing elit. Aperiam autem amet, rem libero, necessitatibus maiores, possimus adipisci sint quae reiciendis ab impedit quo a! Cum voluptatibus neque libero animi asperiores!',
        },
    ];
    ngOnInit() {}
}
