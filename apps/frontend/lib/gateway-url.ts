/**
 * Gateway WebSocket / API base URL.
 * - 方案 1 暗影隧道：NEXT_PUBLIC_GATEWAY_WS / NEXT_PUBLIC_GATEWAY_API 設為 Cloudflare Tunnel URL
 * - 方案 2 極限壓縮：同源，使用 /ws 與 /api（Vercel rewrites 轉發至 Render）
 * - 本機開發：localhost 時連 hostname:8080
 */
export function getGatewayWsUrl(): string {
  if (typeof window === "undefined") {
    return process.env.NEXT_PUBLIC_GATEWAY_WS ?? "";
  }
  if (process.env.NEXT_PUBLIC_GATEWAY_WS) {
    return process.env.NEXT_PUBLIC_GATEWAY_WS;
  }
  if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
    return `ws://${window.location.hostname}:8080/ws`;
  }
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}/ws`;
}

export function getGatewayApiUrl(): string {
  if (typeof window === "undefined") {
    return process.env.NEXT_PUBLIC_GATEWAY_API ?? "";
  }
  if (process.env.NEXT_PUBLIC_GATEWAY_API) {
    return process.env.NEXT_PUBLIC_GATEWAY_API.replace(/\/$/, "");
  }
  if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
    return `http://${window.location.hostname}:8080`;
  }
  return window.location.origin;
}
