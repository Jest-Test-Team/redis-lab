# 蜃景交易所 (Mirage Exchange) - 專案結構與架構

## 系統架構圖 (System Architecture)

```mermaid
graph TD
    Client[Next.js Frontend\n(賽博龐克終端)] <-->|WebSocket| Gateway
    
    subgraph Backend Microservices
        Gateway[邊界閘道器 - Go\n(The Vanguard)]
        Sentinel[死間哨兵 - Go\n(Dead Man's Sentinel)]
        Matcher[地獄火撮合引擎 - Rust\n(Hellfire Engine)]
        Identity[身份洗牌矩陣 - Rust\n(Identity Matrix)]
    end

    Gateway -->|gRPC/HTTP| Matcher
    Gateway -->|gRPC/HTTP| Identity
    
    Gateway -.->|Pub/Sub| Redis[(Redis Cluster)]
    Sentinel -.->|Keyspace Notifications| Redis
    Matcher -.->|Lua Scripts / ZSet| Redis
    Identity -.->|Set / Hash| Redis
    ```
    ```plaintext
    mirage-exchange/
├── apps/
│   ├── frontend/         # Next.js: 賽博龐克 UI, WebSocket 客戶端
│   ├── gateway/          # Go: 邊界閘道器 (WebSocket Server, 路由分發)
│   ├── engine/           # Rust: 撮合引擎 (處理 Lua 腳本, ZSet 排行)
│   ├── identity/         # Rust: 身份洗牌矩陣 (動態 Token 生成)
│   └── sentinel/         # Go: 死間哨兵 (監聽 Redis 過期事件, 執行焦土政策)
├── packages/
│   ├── redis-lua/        # 共用的 Redis Lua 腳本 (原子操作核心)
│   ├── proto/            # gRPC Protobuf 定義檔 (微服務通訊)
│   └── types/            # TypeScript 共用型別定義
├── docker-compose.yml    # 本地端 Redis 與微服務一鍵啟動配置
├── README.md             # 專案總說明
└── cursor.plan.md        # AI 輔助開發計畫書
```