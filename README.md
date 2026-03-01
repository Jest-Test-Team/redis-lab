這份文件用於定義專案的精神、技術棧與啟動方式。

```markdown
# 🌆 蜃景交易所 (Mirage Exchange)

> **⚠️ 警告 (Disclaimer):** 本專案為極端高併發與分散式系統的「壓力測試與架構演練」純研究用專案。探討範圍包含瞬時通訊、反追蹤跳板機制與死間開關 (Dead Man's Switch)。請勿用於任何非法商業用途。

蜃景交易所是一個完全匿名、極度短暫、且高度競爭的虛擬情報拍賣平台。系統結合了 Go 的海量連線處理能力、Rust 的極致無延遲運算，以及 Redis 的記憶體級別原子操作。

## 🛠️ 技術棧 (Tech Stack)

* **Frontend (40%):** Next.js, Framer Motion, Tailwind CSS, WebSockets (賽博龐克終端視覺, 即時資料流)
* **Backend (60%):**
  * **Go (Golang):** API Gateway, WebSocket 管理, 背景任務監控。
  * **Rust:** 核心撮合引擎, 身份加密與洗牌, 高頻 API 處理。
* **Database & Message Broker:** Redis (ZSet, Pub/Sub, Streams, Keyspace Notifications, Lua Scripting).

## 🚀 核心機制 (Core Features)

1. **極短線拍賣 (Micro-Auction):** 5 秒內的極限競標，基於 Redis Lua 腳本防禦超賣與資源競爭。
2. **身份洗牌矩陣 (Identity Shuffler):** 連線者每 10 秒自動更換虛擬 ID。
3. **死間開關 (Dead Man's Switch):** 監測連線狀態，觸發「焦土政策」(數據全毀) 或「玉石俱焚」(情報全網廣播)。

## 📦 快速啟動 (Quick Start)

```bash
# 一鍵啟動所有服務（Redis、Gateway、Sentinel、Engine、Identity、Frontend）
docker-compose up -d

# 前端：http://localhost:3000
# 閘道 WebSocket / API：http://localhost:8080
# 撮合引擎 API：http://localhost:8081
# 身份服務 API：http://localhost:8082
```

**環境變數（可選）：**  
`REDIS_ADDR`、`ENGINE_URL`、`IDENTITY_URL`（Gateway）；`DEADMAN_KEY_PREFIX`（Sentinel）；`PORT`（各服務）。

**本雛形對應三大機制：**  
- 極短線拍賣：Engine 透過 Redis Lua 執行 5 秒競標與原子結標。  
- 身份洗牌：Gateway 每 10 秒對 WebSocket 連線推送新虛擬 ID。  
- 死間開關：Sentinel 訂閱 Redis Keyspace 過期事件，觸發焦土邏輯並可 PUBLISH 通知。

## 部署 (Deployment)

支援兩套部署方案，可依需求擇一或並存：

| 方案 | 情境 | 前端 | 後端 | 關鍵環境變數 |
|------|------|------|------|--------------|
| **暗影隧道** | Vercel + 本機，$0 | Vercel | Cloudflare Tunnel → 本機 Gateway/Engine/Identity/Redis | `NEXT_PUBLIC_GATEWAY_WS`、`NEXT_PUBLIC_GATEWAY_API`（Tunnel URL） |
| **極限壓縮** | Vercel + Render，$0 | Vercel（rewrites 隱藏後端） | Render：僅 Gateway 對外，Redis/Engine 內網，Identity 由 Gateway fallback | 前端同源；Render 見根目錄 `render.yaml`。部署前請替換 `apps/frontend/vercel.json` 內 destination 為自己的 Render Gateway URL。 |

- **暗影隧道** 設定步驟：[docs/deploy-shadow-tunnel.md](docs/deploy-shadow-tunnel.md)
- **極限壓縮**：根目錄 `render.yaml` 部署至 Render；Vercel 前端使用同源 `/ws`、`/api`，由 vercel.json rewrites 轉發至 Render Gateway。Render Free Tier 有 750 小時/月與睡眠限制，僅適合展示用。

```