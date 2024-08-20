import { CommonModule, NgOptimizedImage } from '@angular/common';
import { Component, inject, OnInit } from '@angular/core';
import {
    NavigationEnd,
    Router,
    RouterModule,
    RouterOutlet,
} from '@angular/router';
import { filter } from 'rxjs';

@Component({
    selector: 'app-root',
    standalone: true,
    imports: [RouterOutlet, NgOptimizedImage, RouterModule, CommonModule],
    templateUrl: './app.component.html',
    styleUrl: './app.component.scss',
})
export class AppComponent implements OnInit {
    router = inject(Router);
    collapsed: boolean = true;
    activatedRoute!: string;
    navLinks = [
        {
            route: '/',
            title: 'Home',
        },
        {
            route: '/ai-service/ai-search',
            title: 'AI Search',
        },
        {
            route: '/ai-service/ai-chat-bot',
            title: 'Chat Bot',
        },
    ];
    ngOnInit() {
        this.router.events
            .pipe(filter((event) => event instanceof NavigationEnd))
            .subscribe((data) => {
                this.activatedRoute = data.url;
            });
    }
}
