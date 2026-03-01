"use client";

import { useEffect, useRef, useState } from "react";
import { useTranslations } from "@/contexts/LocaleContext";

export interface WsMessage {
  type: string;
  payload?: unknown;
  ts?: number;
}

const MAX_MESSAGES = 100;

export function useWs(url: string) {
  const t = useTranslations();
  const [connected, setConnected] = useState(false);
  const [virtualId, setVirtualId] = useState<string | null>(null);
  const [lastEvent, setLastEvent] = useState<WsMessage | null>(null);
  const [messages, setMessages] = useState<WsMessage[]>([]);
  const [identityRefreshCount, setIdentityRefreshCount] = useState(0);
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
        addLog(t("logConnected"));
      };

      ws.onclose = () => {
        setConnected(false);
        addLog(t("logDisconnected"));
        reconnectRef.current = setTimeout(connect, 3000);
      };

      ws.onerror = () => addLog(t("logError"));

      ws.onmessage = (event) => {
        try {
          const data: WsMessage = JSON.parse(event.data);
          setLastEvent(data);
          setMessages((prev) => [...prev.slice(-(MAX_MESSAGES - 1)), data]);
          if (data.type === "identity_refreshed" && data.payload && typeof data.payload === "object" && "virtualId" in data.payload) {
            setVirtualId((data.payload as { virtualId: string }).virtualId);
            setIdentityRefreshCount((c) => c + 1);
          }
          addLog(`${t("logEvent")}: ${data.type}`);
        } catch {
          addLog(t("logParseError"));
        }
      };
    };

    connect();
    return () => {
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
      wsRef.current?.close();
      wsRef.current = null;
    };
  }, [url, t]);

  return { connected, virtualId, lastEvent, messages, identityRefreshCount, logs };
}
