import { useState, useEffect, useRef, useCallback } from "react";
import type { TaskProgress } from "../types";

interface UseWebSocketResult {
  isConnected: boolean;
  progress: TaskProgress | null;
  error: string | null;
  isComplete: boolean;
}

const MAX_BACKOFF = 30000;

export function useWebSocket(url: string | null): UseWebSocketResult {
  const [isConnected, setIsConnected] = useState(false);
  const [progress, setProgress] = useState<TaskProgress | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isComplete, setIsComplete] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const backoffRef = useRef(1000);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = useCallback(() => {
    if (!url) return;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      setError(null);
      backoffRef.current = 1000;
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as TaskProgress;
        setProgress(data);
        if (data.type === "task_completed" || data.type === "task_failed") {
          setIsComplete(true);
        }
      } catch {
        setError("Failed to parse WebSocket message");
      }
    };

    ws.onerror = () => {
      setError("WebSocket error");
    };

    ws.onclose = () => {
      setIsConnected(false);
      wsRef.current = null;
      if (!isComplete) {
        const delay = Math.min(backoffRef.current, MAX_BACKOFF);
        backoffRef.current = delay * 2;
        reconnectTimerRef.current = setTimeout(connect, delay);
      }
    };
  }, [url]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
      if (wsRef.current) {
        wsRef.current.onclose = null;
        wsRef.current.close();
      }
    };
  }, [connect]);

  return { isConnected, progress, error, isComplete };
}
