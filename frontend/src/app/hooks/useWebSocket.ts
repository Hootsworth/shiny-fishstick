import { useEffect, useState, useRef } from "react";

export function useWebSocket(url: string) {
  const [messages, setMessages] = useState<string[]>([]);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!url) return;

    const socket = new WebSocket(url);
    socketRef.current = socket;

    socket.onopen = () => {
      console.log("WebSocket connected:", url);
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data && data.message) {
          setMessages((prev) => [...prev, data.message]);
        } else {
          setMessages((prev) => [...prev, event.data]);
        }
      } catch (e) {
        setMessages((prev) => [...prev, event.data]);
      }
    };

    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    socket.onclose = () => {
      console.log("WebSocket closed");
    };

    return () => {
      socket.close();
    };
  }, [url]);

  const clearMessages = () => setMessages([]);
  const addMessage = (msg: string) => setMessages((prev) => [...prev, msg]);

  return { messages, addMessage, clearMessages };
}
