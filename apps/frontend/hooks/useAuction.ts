"use client";

import { useEffect, useState } from "react";
import { leaderboard, type LeaderboardEntry } from "@/lib/gateway-api";
import type { WsMessage } from "./useWs";

const POLL_MS = 400;

export interface SettledEvent {
  winner_id: string;
  top_bid?: number;
}

export function useAuction(
  auctionId: string | null,
  messages: WsMessage[]
) {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [settledEvent, setSettledEvent] = useState<SettledEvent | null>(null);

  useEffect(() => {
    if (!auctionId) {
      setEntries([]);
      setSettledEvent(null);
      return;
    }
    const tick = async () => {
      try {
        const res = await leaderboard(auctionId);
        if (res.entries) setEntries(res.entries);
      } catch {
        setEntries([]);
      }
    };
    tick();
    const id = setInterval(tick, POLL_MS);
    return () => clearInterval(id);
  }, [auctionId]);

  useEffect(() => {
    if (!auctionId) return;
    const last = [...messages].reverse().find((m) => {
      if (m.type !== "settled") return false;
      const p = m.payload as { auction_id?: string };
      return p?.auction_id === auctionId;
    });
    if (last && last.payload && typeof last.payload === "object" && "winner_id" in last.payload) {
      const p = last.payload as { winner_id: string; top_bid?: number };
      setSettledEvent({ winner_id: p.winner_id, top_bid: p.top_bid });
    }
  }, [auctionId, messages]);

  return { entries, settledEvent };
}
