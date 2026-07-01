import { useEffect, useRef } from "react";
import JMuxer from "jmuxer";

type VideoFeedRef = React.MutableRefObject<((data: Uint8Array) => void) | null>;

export default function AvatarPlayer({ videoStreamRef }: { videoStreamRef: VideoFeedRef }) {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (videoRef.current) {
      const jmuxer = new JMuxer({
        node: videoRef.current,
        mode: "video",
        flushingTime: 0,
        fps: 25,
      });
      videoStreamRef.current = (data: Uint8Array) => jmuxer.feed({ video: data });
    }
    return () => {
      videoStreamRef.current = null;
    };
  }, [videoStreamRef]);

  return (
    <div className="relative w-full h-[600px] rounded-2xl bg-white border border-gray-200 shadow-sm flex items-center justify-center overflow-hidden">
      <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover" />
      <div className="absolute top-4 right-4 text-xs font-medium text-blue-600 bg-blue-50 px-3 py-1 rounded-full border border-blue-200">
        Live Stream
      </div>
    </div>
  );
}
