/**
 * 蜃景交易所 — 共用 TypeScript 型別
 * 拍賣狀態、出價、身份 Token、WebSocket 事件
 */

// --- 拍賣 ---
export type AuctionStatus = "open" | "ended";

export interface AuctionMeta {
  auctionId: string;
  status: AuctionStatus;
  endAtMs: number;
  maxBid: number;
  winnerId: string;
}

export interface BidPayload {
  auctionId: string;
  bidderId: string;
  amount: number;
}

export interface LeaderboardEntry {
  bidderId: string;
  amount: number;
  rank: number;
}

// --- 身份 ---
export interface VirtualIdentity {
  virtualId: string;
  expiresAtMs: number;
}

// --- WebSocket 事件 (Gateway → Frontend) ---
export type WsEventType =
  | "auction_created"
  | "auction_updated"
  | "auction_ended"
  | "identity_refreshed"
  | "error";

export interface WsMessage<T = unknown> {
  type: WsEventType;
  payload: T;
  ts: number;
}

export interface WsAuctionCreated {
  auctionId: string;
  endAtMs: number;
}

export interface WsAuctionUpdated {
  auctionId: string;
  maxBid: number;
  leaderId: string;
}

export interface WsAuctionEnded {
  auctionId: string;
  winnerId: string;
  topBid: number;
}

export interface WsIdentityRefreshed {
  virtualId: string;
  expiresAtMs: number;
}
