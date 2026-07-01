"use client";
import { useRef } from "react";
import AvatarPlayer from "@/components/avatar/AvatarPlayer";
import AdvisoryChat from "@/components/chat/AdvisoryChat";
import { useWebSocket } from "@/hooks/useWebSocket";

export default function Page() {
  const videoFeedRef = useRef<((data: Uint8Array) => void) | null>(null);
  const { messages, startRecording, stopRecording, sendTextMessage } = useWebSocket(
    "ws://localhost:8000/ws",
    videoFeedRef
  );

  return (
    <div className="min-h-screen p-8 max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">
      <AvatarPlayer videoStreamRef={videoFeedRef} />
      <div className="flex flex-col gap-4">
        <div className="flex gap-3">
          <button
            onClick={startRecording}
            className="bg-blue-600 text-white p-3 rounded-xl shadow-sm hover:bg-blue-700 w-fit"
          >
            Start Voice Chat
          </button>
          <button
            onClick={stopRecording}
            className="bg-gray-200 text-gray-800 p-3 rounded-xl shadow-sm hover:bg-gray-300 w-fit"
          >
            Stop
          </button>
        </div>
        <AdvisoryChat messages={messages} onSend={sendTextMessage} />
      </div>
    </div>
  );
}
