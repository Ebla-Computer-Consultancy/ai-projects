import {
    AfterViewInit,
    Component,
    ElementRef,
    inject,
    OnDestroy,
    OnInit,
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
    @ViewChild('videoRef') videoRef!: ElementRef;
    service = inject(AiAvatarService);
    toggled: boolean = false;
    isProcessing: boolean = false;
    constructor() {}
    STREAM_ID_STORAGE_KEY: string = environment.STREAM_ID_STORAGE_KEY;
    ngOnInit() {
        localStorage.removeItem(this.STREAM_ID_STORAGE_KEY);
    }
    ngAfterViewInit(): void {}
    closeStream() {
        this.videoRef.nativeElement.srcObject = null;
        const streamId = localStorage.getItem(this.STREAM_ID_STORAGE_KEY);

        if (streamId) {
            this.service.closeStream(+streamId).subscribe(() => {
                localStorage.removeItem(this.STREAM_ID_STORAGE_KEY);
            });
        }
    }
    renderText(text: string) {
        const streamId = localStorage.getItem(this.STREAM_ID_STORAGE_KEY);
        if (streamId) {
            this.service.renderText(+streamId, text).subscribe();
        }
    }
    toggleVideo() {
        this.toggled = !this.toggled;
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

                        localStorage.setItem(
                            this.STREAM_ID_STORAGE_KEY,
                            JSON.stringify(id)
                        );

                        const peerConnection = new RTCPeerConnection({
                            iceTransportPolicy: 'relay',
                            iceServers,
                        });

                        peerConnection.onicecandidate = async (e) => {
                            if (!e.candidate) return;
                            this.service.sendCandidate(id, e.candidate);
                        };

                        peerConnection.onicegatheringstatechange = (e) => {
                            const iceGatheringState = (e.target as any)
                                .iceGatheringState;
                            if (
                                iceGatheringState === 'complete' &&
                                this.videoRef.nativeElement.paused &&
                                this.videoRef.nativeElement.srcObject
                            ) {
                                this.videoRef.nativeElement.play();
                            }
                        };

                        peerConnection.ontrack = async (event) => {
                            const [remoteStream] = event.streams;
                            this.videoRef.nativeElement.srcObject =
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
                                                    answer_,
                                                    id,
                                                };
                                            })
                                        );
                                    }
                                )
                            );
                    })
                )
                .pipe(
                    switchMap(({ id, answer_ }) => {
                        return this.service.sendAnswer(id, answer_);
                    })
                )
                .pipe(
                    finalize(() => {
                        this.isProcessing = false;
                    })
                )
                .subscribe();
        }
    }
    ngOnDestroy(): void {
        this.closeStream();
    }
}
