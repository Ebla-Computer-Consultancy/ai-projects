import {
    AfterViewInit,
    Component,
    ElementRef,
    EventEmitter,
    inject,
    OnDestroy,
    OnInit,
    Output,
    ViewChild,
} from '@angular/core';
import { TooltipModule } from 'ngx-bootstrap/tooltip';
import { AiAvatarService } from '../../services/ai-avatar.service';
import { StreamResult } from '../../models/stream-result';
import { finalize, from, map, switchMap } from 'rxjs';
import { environment } from '../../../environments/environment.prod';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'ai-avatar',
    standalone: true,
    imports: [TooltipModule, CommonModule],
    templateUrl: './ai-avatar.component.html',
    styleUrls: ['./ai-avatar.component.scss'],
    providers: [],
})
export class AiAvatarComponent implements OnInit, AfterViewInit, OnDestroy {
    @ViewChild('video_ref') video_ref!: ElementRef;
    @Output() onToggle: EventEmitter<boolean> = new EventEmitter<boolean>();
    service = inject(AiAvatarService);
    toggled: boolean = false;
    isProcessing: boolean = false;
    constructor() {}
    STREAM_ID_STORAGE_KEY: string = environment.STREAM_ID_STORAGE_KEY;
    ngOnInit() {
        const streamId = localStorage.getItem(this.STREAM_ID_STORAGE_KEY);
        if (streamId) {
            this.closeStream();
        }
    }
    ngAfterViewInit(): void {}
    closeStream() {
        const streamId = localStorage.getItem(this.STREAM_ID_STORAGE_KEY);

        if (streamId) {
            this.service.closeStream(streamId).subscribe(() => {
                localStorage.removeItem(this.STREAM_ID_STORAGE_KEY);
            });
        }
        this.video_ref.nativeElement.srcObject = null;
    }
    toggleVideo() {
        this.toggled = !this.toggled;
        this.onToggle.emit(this.toggled);
        const streamId = localStorage.getItem(this.STREAM_ID_STORAGE_KEY);
        if (!streamId) {
            this.isProcessing = true;
            this.service
                .startStream()
                .pipe(
                    switchMap((stream: StreamResult) => {
                        const { webrtcData } = stream.data;
                        const { offer, iceServers } = webrtcData;
                        const { id } = stream.data;

                        localStorage.setItem(this.STREAM_ID_STORAGE_KEY, id);

                        const peerConnection = new RTCPeerConnection({
                            iceTransportPolicy: 'relay',
                            iceServers,
                        });
                        peerConnection.onicecandidate = (e) => {
                            console.log('onicecandidate', e);
                            if (!e.candidate) return;
                            this.service
                                .sendCandidate(id, e.candidate)
                                .subscribe();
                        };

                        peerConnection.onicegatheringstatechange = (e) => {
                            console.log('onicegatheringstatechange', e);
                            console.log(
                                'srcObject',
                                this.video_ref.nativeElement.srcObject
                            );

                            const iceGatheringState = (e.target as any)
                                .iceGatheringState;
                            if (
                                iceGatheringState === 'complete' &&
                                this.video_ref.nativeElement.paused &&
                                this.video_ref.nativeElement.srcObject
                            ) {
                                this.video_ref.nativeElement.play();
                            }
                        };

                        peerConnection.ontrack = (e) => {
                            console.log('ontrack', e);
                            const [remoteStream] = e.streams;
                            this.video_ref.nativeElement.srcObject =
                                remoteStream;
                        };
                        return from(
                            peerConnection.setRemoteDescription(
                                new RTCSessionDescription(offer)
                            )
                        )
                            .pipe(
                                switchMap(() => {
                                    return from(peerConnection.createAnswer());
                                })
                            )
                            .pipe(
                                switchMap(
                                    (answer_: RTCSessionDescriptionInit) => {
                                        return from(
                                            peerConnection.setLocalDescription(
                                                answer_
                                            )
                                        ).pipe(
                                            map(() => {
                                                return {
                                                    id,
                                                    answer_,
                                                };
                                            })
                                        );
                                    }
                                )
                            );
                    })
                )
                .pipe(
                    finalize(() => {
                        this.isProcessing = false;
                    }),
                    switchMap(({ id, answer_ }) => {
                        return this.service.sendAnswer(id, answer_);
                    })
                )
                .subscribe();
        } else {
            this.closeStream();
        }
    }
    ngOnDestroy(): void {
        this.closeStream();
    }
}
