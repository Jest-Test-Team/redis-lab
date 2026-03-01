import { getGatewayApiUrl } from "./gateway-url";

const api = () => getGatewayApiUrl();

export interface CreateAuctionRes {
  ok: boolean;
  error?: string;
  end_at_ms?: number;
}

export async function createAuction(auctionId: string, durationMs = 5000): Promise<CreateAuctionRes> {
  const res = await fetch(`${api()}/api/auction/create`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ auction_id: auctionId, duration_ms: durationMs }),
  });
  return res.json();
}

export interface BidRes {
  status: string;
  error?: string;
}

export async function bid(auctionId: string, bidderId: string, amount: number): Promise<BidRes> {
  const res = await fetch(`${api()}/api/auction/bid`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ auction_id: auctionId, bidder_id: bidderId, amount }),
  });
  return res.json();
}

export interface SettleRes {
  ok: boolean;
  winner_id?: string;
  top_bid?: number;
  error?: string;
}

export async function settle(auctionId: string): Promise<SettleRes> {
  const res = await fetch(`${api()}/api/auction/settle`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ auction_id: auctionId }),
  });
  return res.json();
}

export interface LeaderboardEntry {
  bidder_id: string;
  amount: number;
  rank: number;
}

export interface LeaderboardRes {
  entries: LeaderboardEntry[];
  error?: string;
}

export async function leaderboard(auctionId: string): Promise<LeaderboardRes> {
  const res = await fetch(`${api()}/api/auction/leaderboard/${encodeURIComponent(auctionId)}`);
  return res.json();
}
