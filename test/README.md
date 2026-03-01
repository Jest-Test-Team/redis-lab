# 統一測試套件

本目錄協調蜃景交易所各 app 的測試：Jest（frontend）、Robot Framework（API 整合）、go test（gateway、sentinel）、cargo test（engine、identity）。

## 環境需求

- **Node.js** 18+（frontend Jest）
- **Go** 1.21+（gateway、sentinel）
- **Rust** 1.70+（engine、identity）
- **Python** 3.9+ 與 pip（Robot Framework）
- **Redis**（可選）：Robot 的 engine/identity 用例及整合測試若需真實服務，請先啟動 Redis 與對應服務。

## 執行方式

### 一鍵執行全部（建議）

從專案根目錄執行：

```bash
./test/run_all.sh
```

或：

```bash
chmod +x test/run_all.sh && test/run_all.sh
```

任一階段失敗會回傳非零，適合 CI。

### 分開執行

1. **Go 測試（gateway、sentinel）**
   ```bash
   go test ./apps/gateway/... ./apps/sentinel/...
   ```

2. **Rust 測試（engine、identity）**
   ```bash
   cargo test --manifest-path apps/engine/Cargo.toml
   cargo test --manifest-path apps/identity/Cargo.toml
   ```

3. **Frontend Jest**
   ```bash
   npm run test --prefix apps/frontend
   ```

4. **Robot Framework（需先安裝依賴；可選先啟動 Gateway/Engine/Identity）**
   ```bash
   pip install -r test/robot/requirements.txt
   robot test/robot
   ```
   可透過環境變數覆寫 URL：例如 `GATEWAY_URL=http://localhost:8080`（若 Robot 支援從變數讀取）。

## 目錄結構

- `test/README.md` — 本說明
- `test/run_all.sh` — 依序執行 go test、cargo test、Jest、Robot
- `test/robot/` — Robot Framework 用例與變數
