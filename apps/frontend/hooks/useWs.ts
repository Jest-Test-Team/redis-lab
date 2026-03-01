"use client";

import { useEffect, useRef, useState } from "react";

interface WsMessage {
  type: string;
  payload?: unknown;
  ts?: number;
}

export function useWs(url: string) {
  const [connected, setConnected] = useState(false);
  const [virtualId, setVirtualId] = useState<string | null>(null);
  const [lastEvent, setLastEvent] = useState<WsMessage | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectRef = useRef<ReturnType<typeof setTimeout>>();

  const addLog = (msg: string) => {
    setLogs((prev) => [...prev.slice(-50), `[${new Date().toISOString().slice(11, 23)}] ${msg}`]);
  };

  useEffect(() => {
    if (!url) return;

    const connect = () => {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        addLog("WebSocket 已連線");
      };

      ws.onclose = () => {
        setConnected(false);
        addLog("WebSocket 已斷線");
        reconnectRef.current = setTimeout(connect, 3000);
      };

      ws.onerror = () => addLog("WebSocket 錯誤");

      ws.onmessage = (event) => {
        try {
          const data: WsMessage = JSON.parse(event.data);
          setLastEvent(data);
          if (data.type === "identity_refreshed" && data.payload && typeof data.payload === "object" && "virtualId" in data.payload) {
            setVirtualId((data.payload as { virtualId: string }).virtualId);
          }
          addLog(`事件: ${data.type}`);
        } catch {
          addLog("無法解析訊息");
        }
      };
    };

    connect();
    return () => {
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
      wsRef.current?.close();
      wsRef.current = null;
    };
  }, [url]);

  return { connected, virtualId, lastEvent, logs };
}
