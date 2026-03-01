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
*(待開發完成後補充 `docker-compose up -d` 等指令)*