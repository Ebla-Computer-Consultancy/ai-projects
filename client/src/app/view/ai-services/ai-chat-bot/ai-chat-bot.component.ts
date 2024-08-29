import {
    Component,
    HostListener,
    inject,
    OnInit,
    TemplateRef,
} from '@angular/core';
import { AiChatBotService } from '../../../services/ai-chat-bot.service';
import { FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { filter, Subject, switchMap } from 'rxjs';
import { IChatMessageResult } from '../../../interfaces/i-chat-message-result';
import { CommonModule } from '@angular/common';
import { ICitations, Message } from '../../../models/message';
import { BsModalService, BsModalRef } from 'ngx-bootstrap/modal';
import { AudioRecorderComponent } from '../../../standalone/audio-recorder/audio-recorder.component';
import { AiSpeechToTextService } from '../../../services/ai-speech-to-text.service';
import { IRecordedAudioOutput } from '../../../interfaces/i-recorded-audio-output';
@Component({
    selector: 'app-ai-chat-bot',
    standalone: true,
    imports: [ReactiveFormsModule, CommonModule, AudioRecorderComponent],
    templateUrl: './ai-chat-bot.component.html',
    styleUrls: ['./ai-chat-bot.component.scss'],
    providers: [BsModalService],
})
export class AiChatBotComponent implements OnInit {
    service = inject(AiChatBotService);
    aiSpeechToTextService: AiSpeechToTextService = inject(
        AiSpeechToTextService
    );
    modalService = inject(BsModalService);

    modalRef?: BsModalRef | null;
    control: FormControl = new FormControl('', Validators.required);
    ask$: Subject<void> = new Subject<void>();
    selectedDoc!: ICitations;
    fullScreen: boolean = false;

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

    listenToAskQuestion() {
        this.ask$
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
                    return this.service.askQuestion(this.control.value);
                })
            )
            .subscribe((response: IChatMessageResult) => {
                this.control.reset();
                this.control.updateValueAndValidity();
                this.service.appendMessage(
                    new Message().clone({
                        ...response.message,
                        content: this.formatText(response.message.content),
                    })
                );
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

    handleSpeechToText(record: IRecordedAudioOutput) {
        const file = new File([record.blob], record.title);
        const formData = new FormData();
        formData.append('file', file);
        this.aiSpeechToTextService
            .transcribe(formData)
            .subscribe((stringText: string) => {
                this.control.setValue(stringText);
                this.ask$.next();
            });
    }
    clear() {
        this.control.reset();
        this.control.updateValueAndValidity();
        this.service.resetMessageHistory();
    }
}
