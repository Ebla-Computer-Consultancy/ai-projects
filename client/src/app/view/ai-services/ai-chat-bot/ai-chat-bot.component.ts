import {
    AfterViewInit,
    Component,
    ElementRef,
    HostListener,
    inject,
    OnInit,
    TemplateRef,
    ViewChild,
} from '@angular/core';
import { AiChatBotService } from '../../../services/ai-chat-bot.service';
import { FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { filter, Subject, Subscription, switchMap, takeUntil } from 'rxjs';
import { IChatMessageResult } from '../../../interfaces/i-chat-message-result';
import { CommonModule } from '@angular/common';
import { ICitations, Message } from '../../../models/message';
import { BsModalService, BsModalRef } from 'ngx-bootstrap/modal';
import { AudioRecorderComponent } from '../../../standalone/audio-recorder/audio-recorder.component';
import { AiSpeechToTextService } from '../../../services/ai-speech-to-text.service';
import { LoadingComponent } from '../../../standalone/loading/loading.component';
import { TextWriterAnimatorDirective } from '../../../directives/text-writer-animator.directive';
import { formateString, isRTL } from '../../../utils';
import { StopProcessingBtnComponent } from '../../../standalone/stop-processing-btn/stop-processing-btn.component';

@Component({
    selector: 'app-ai-chat-bot',
    standalone: true,
    imports: [
        ReactiveFormsModule,
        CommonModule,
        AudioRecorderComponent,
        LoadingComponent,
        TextWriterAnimatorDirective,
        StopProcessingBtnComponent,
    ],
    templateUrl: './ai-chat-bot.component.html',
    styleUrls: ['./ai-chat-bot.component.scss'],
    providers: [BsModalService],
})
export class AiChatBotComponent implements OnInit, AfterViewInit {
    @ViewChild('chat_container') chat_container!: ElementRef;
    @ViewChild('chat_body') chat_body!: ElementRef;
    service = inject(AiChatBotService);
    aiSpeechToTextService: AiSpeechToTextService = inject(
        AiSpeechToTextService
    );
    modalService = inject(BsModalService);
    stopProcessing$: Subject<void> = new Subject<void>();
    modalRef?: BsModalRef | null;
    control: FormControl = new FormControl('', Validators.required);
    ask$: Subject<void> = new Subject<void>();
    selectedDoc!: ICitations;
    fullScreen: boolean = false;
    animating: boolean = false;
    subscription!: Subscription;
    readonly isRTL = isRTL;
    @HostListener('document:keypress', ['$event'])
    handleKeyboardEvent(event: KeyboardEvent) {
        if (event.key === 'Enter') {
            event.preventDefault();
            this.ask$.next();
        }
    }
    constructor() {}

    ngOnInit() {
        this.listenToAskQuestion();
    }
    ngAfterViewInit() {
        this.scrollToMessage();
    }
    scrollToMessage() {
        this.chat_body &&
            this.chat_container &&
            this.chat_container.nativeElement.lastElementChild &&
            (this.chat_body.nativeElement.scrollTop =
                this.chat_body?.nativeElement.scrollHeight -
                this.chat_container.nativeElement.lastElementChild
                    .scrollHeight -
                20);
    }
    listenToAskQuestion() {
        this.subscription = this.ask$
            .pipe(
                filter(
                    () =>
                        !this.service.loading &&
                        this.control.valid &&
                        !!this.control.value.trim()
                )
            )
            .pipe(
                switchMap(() => {
                    setTimeout(() => {
                        this.scrollToMessage();
                    }, 200);
                    return this.service
                        .askQuestion(this.control.value)
                        .pipe(takeUntil(this.stopProcessing$));
                })
            )
            .subscribe((response: IChatMessageResult) => {
                formateString(this.formatText(response.message.content));
                this.control.reset();
                this.control.updateValueAndValidity();
                this.service.appendMessage(
                    new Message().clone({
                        ...response.message,
                        content: this.formatText(response.message.content),
                    })
                );
                setTimeout(() => {
                    this.scrollToMessage();
                }, 200);
            });
    }
    openDocModal(template: TemplateRef<void>, link: ICitations) {
        this.selectedDoc = link;
        this.modalRef = this.modalService.show(template, {
            class: 'modal-lg',
        });
    }
    formatText(text: string) {
        let formattedText = text.replace(
            /\*\*(.*?)\*\*/g,
            '<strong>$1</strong>'
        );

        // Replace text between [ and ] with <a> tags
        formattedText = formattedText.replace(
            /\[(.*?)\]/g,
            '<pre class="d-inline"><small class="px-1 text-primary">$1<i class="mdi mdi-link-variant"></i></small></pre>'
        );
        // text = text.replace(/\./g, '.<br>')

        // Return the formatted text
        return formattedText.trim();
    }
    stopAnimation() {
        this.stopProcessing$.next();
        if (
            this.service.messageHistory[this.service.messageHistory.length - 1]
                .role == 'assistant'
        ) {
            this.service.messageHistory[
                this.service.messageHistory.length - 1
            ].content =
                this.chat_container.nativeElement.lastElementChild.children[0].children[0].innerHTML;
        }
    }
    handleSpeechToText(result: string) {
        this.control.setValue(result);
    }
    stopRecording() {
        this.ask$.next();
    }
    clear() {
        this.control.reset();
        this.control.updateValueAndValidity();
        this.service.resetMessageHistory();
    }
}
