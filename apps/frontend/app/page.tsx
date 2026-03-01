"use client";

import { motion } from "framer-motion";
import { useWs } from "@/hooks/useWs";

const GATEWAY_WS =
  typeof window !== "undefined"
    ? `ws://${window.location.hostname}:8080/ws`
    : "";

export default function Home() {
  const { connected, virtualId, lastEvent, logs } = useWs(GATEWAY_WS);

  return (
    <main className="min-h-screen p-6 md:p-10">
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="border-b border-terminal-green/30 pb-4 mb-8"
      >
        <h1 className="text-2xl md:text-3xl font-bold glow-green text-terminal-green">
          ［蜃景交易所］ MIRAGE EXCHANGE
        </h1>
        <p className="text-terminal-cyan/80 text-sm mt-1">
          極短線拍賣 · 身份洗牌 · 死間開關 — 研究用雛形
        </p>
      </motion.header>

      <div className="grid gap-6 md:grid-cols-2">
        <motion.section
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="rounded-lg border border-terminal-amber/30 bg-black/40 p-4"
        >
          <h2 className="text-terminal-amber font-mono text-sm mb-2">
            &gt; 連線狀態
          </h2>
          <p className="font-mono text-sm">
            閘道 WebSocket:{" "}
            <span
              className={
                connected ? "text-terminal-green" : "text-terminal-red"
              }
            >
              {connected ? "已連線" : "未連線"}
            </span>
          </p>
          {virtualId && (
            <p className="font-mono text-xs text-terminal-cyan mt-2">
              虛擬 ID: <span className="glow-cyan">{virtualId}</span>
            </p>
          )}
          {lastEvent && (
            <p className="font-mono text-xs text-terminal-amber/80 mt-1 truncate">
              最後事件: {lastEvent.type}
            </p>
          )}
        </motion.section>

        <motion.section
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.15 }}
          className="rounded-lg border border-terminal-cyan/30 bg-black/40 p-4"
        >
          <h2 className="text-terminal-cyan font-mono text-sm mb-2">
            &gt; 即時日誌
          </h2>
          <div className="font-mono text-xs max-h-40 overflow-y-auto space-y-1 text-neutral-400">
            {logs.length === 0 && (
              <span className="text-neutral-600">等待事件…</span>
            )}
            {logs.slice(-8).map((line, i) => (
              <div key={i} className="truncate">
                {line}
              </div>
            ))}
          </div>
        </motion.section>
      </div>

      <motion.footer
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="mt-10 text-center text-neutral-500 text-xs"
      >
        本專案為高併發與分散式系統研究用，請勿用於非法商業用途。
      </motion.footer>
    </main>
  );
}
