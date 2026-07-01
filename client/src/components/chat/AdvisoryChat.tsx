"use client";
import { useState } from "react";

export default function AdvisoryChat({
  messages,
  onSend,
}: {
  messages: any[];
  onSend: (text: string) => void;
}) {
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) return;
    onSend(input.trim());
    setInput("");
  };

  return (
    <div className="flex flex-col h-[600px] bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
      <div className="flex-1 overflow-y-auto space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className="p-3 bg-gray-50 rounded-xl text-gray-800">
            {msg.content}
          </div>
        ))}
      </div>
      <div className="mt-4 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Type a message..."
          className="flex-1 p-4 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none"
        />
        <button
          onClick={handleSend}
          className="bg-blue-600 text-white px-5 rounded-xl hover:bg-blue-700"
        >
          Send
        </button>
      </div>
    </div>
  );
}
