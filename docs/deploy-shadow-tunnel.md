# 方案 1：暗影隧道（Vercel + Cloudflare Tunnel + 本機）

前端架在 Vercel，後端與 Redis 全跑在本機；透過 Cloudflare Tunnel 將本機 Gateway 暴露為公開網址，供 Vercel 上的前端連線。成本 $0，適合高併發測試與展示。

**缺點：** 電腦關機即無法連線。

## 步驟

### 1. 本機啟動後端

在專案根目錄執行：

```bash
docker-compose up -d
# 或分別啟動：Redis、Gateway、Engine、Identity（Sentinel 可選）
```

確認 Gateway 在 `http://localhost:8080` 可連（含 `/ws` WebSocket）。

### 2. 安裝並啟動 Cloudflare Tunnel

- 安裝 [cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/)。
- 執行（取得臨時公開網域）：

```bash
cloudflared tunnel --url http://localhost:8080
```

終端會顯示一行如：`https://xxxx-xx-xx-xx-xx.trycloudflare.com`，即為 Tunnel URL。

### 3. 設定 Vercel 環境變數

在 Vercel 專案 **Settings → Environment Variables** 新增：

| 變數 | 值 | 說明 |
|------|-----|------|
| `NEXT_PUBLIC_GATEWAY_WS` | `wss://xxxx.trycloudflare.com/ws` | 將 `https` 改為 `wss`，路徑為 `/ws` |
| `NEXT_PUBLIC_GATEWAY_API` | `https://xxxx.trycloudflare.com` | 同網域，用於 API 請求（若有） |

使用上述 Tunnel 網域替換 `xxxx.trycloudflare.com`。儲存後重新部署前端。

### 4. 部署前端

將 `apps/frontend` 部署至 Vercel（或連結 Monorepo 後指定 Root Directory 為 `apps/frontend`）。部署完成後，前端會透過 Tunnel 連到本機 Gateway。

## 注意

- Tunnel 臨時網域重開 `cloudflared` 會變更，需重新設定 Vercel 環境變數並重新部署。
- 若需固定網域，可改用 Cloudflare Named Tunnel 與自訂網域。
