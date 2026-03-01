"use client";

import { motion, AnimatePresence } from "framer-motion";
import type { LeaderboardEntry } from "@/lib/gateway-api";

interface OrderBookWaterfallProps {
  entries: LeaderboardEntry[];
  maxRows?: number;
}

export function OrderBookWaterfall({ entries, maxRows = 12 }: OrderBookWaterfallProps) {
  const list = entries.slice(0, maxRows);

  return (
    <ul className="font-mono text-[10px] text-white/80 overflow-y-auto space-y-0.5 max-h-48 list-none p-0 m-0">
      <AnimatePresence mode="popLayout" initial={false}>
        {list.map((entry, index) => (
          <motion.li
            key={`${entry.bidder_id}-${entry.amount}-${entry.rank}`}
            layout
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, x: -8 }}
            transition={{ duration: 0.15 }}
            className="flex justify-between items-center py-1 px-2 rounded border border-transparent hover:border-nothing-border"
          >
            <span className="text-nothing-muted w-6">#{entry.rank}</span>
            <span className="truncate flex-1 mx-2" title={entry.bidder_id}>
              {entry.bidder_id}
            </span>
            <span className="text-terminal-cyan tabular-nums">{entry.amount.toFixed(2)}</span>
          </motion.li>
        ))}
      </AnimatePresence>
    </ul>
  );
}
