import { useEffect, useRef, useState } from "react";

type VideoFeedRef = React.MutableRefObject<((data: Uint8Array) => void) | null>;

export function useWebSocket(url: string, videoFeedRef: VideoFeedRef) {
    const ws = useRef<WebSocket | null>(null);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const [messages, setMessages] = useState<any[]>([]);
    const [sessionId, setSessionId] = useState<string | null>(null);

    useEffect(() => {
        const socket = new WebSocket(url);
        socket.binaryType = "arraybuffer";
        ws.current = socket;

        socket.onmessage = (event) => {
            if (typeof event.data === "string") {
                const parsed = JSON.parse(event.data);
                if (parsed.type === "session") {
                    setSessionId(parsed.session_id);
                } else {
                    setMessages((prev) => [...prev, parsed]);
                }
            } else {
                // Binary video frame — route it to whatever AvatarPlayer
                // registered in videoFeedRef, instead of dropping it.
                const frame = new Uint8Array(event.data as ArrayBuffer);
                videoFeedRef.current?.(frame);
            }
        };

        return () => socket.close();
    }, [url, videoFeedRef]);

    const startRecording = async () => {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const recorder = new MediaRecorder(stream);
        recorder.ondataavailable = (e) => {
            if (e.data.size > 0) ws.current?.send(e.data);
        };
        recorder.start(250); // send chunks every 250ms
        mediaRecorderRef.current = recorder;
    };

    const stopRecording = () => {
        mediaRecorderRef.current?.stop();
        mediaRecorderRef.current?.stream.getTracks().forEach((t) => t.stop());
        ws.current?.send(JSON.stringify({ type: "end_of_turn" }));
    };

    const sendTextMessage = (content: string) => {
        ws.current?.send(JSON.stringify({ type: "chat", content }));
    };

    return { messages, sessionId, startRecording, stopRecording, sendTextMessage };
}
