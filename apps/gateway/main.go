// 邊界閘道器 (The Vanguard) — WebSocket 服務、轉發拍賣/身份、Redis Pub/Sub
package main

import (
	"context"
	"crypto/rand"
	"encoding/base64"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
	"github.com/redis/go-redis/v9"
)

const (
	engineURLDefault   = "http://localhost:8081"
	identityURLDefault = "http://localhost:8082"
	redisAddrDefault   = "localhost:6379"
	identityRotateSec  = 10
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool { return true }, // 在 main() 依 CORS_ORIGINS 覆寫
}

type connState struct {
	connID     string
	virtualID  string
	lastRotate time.Time
	mu         sync.Mutex
}

type hub struct {
	clients   map[*websocket.Conn]*connState
	broadcast chan []byte
	register  chan *websocket.Conn
	unregister chan *websocket.Conn
	mu        sync.RWMutex
}

func newHub() *hub {
	return &hub{
		clients:    make(map[*websocket.Conn]*connState),
		broadcast:  make(chan []byte, 256),
		register:   make(chan *websocket.Conn),
		unregister: make(chan *websocket.Conn),
	}
}

func (h *hub) run(ctx context.Context) {
	for {
		select {
		case <-ctx.Done():
			return
		case c := <-h.register:
			h.mu.Lock()
			h.clients[c] = &connState{connID: c.RemoteAddr().String(), lastRotate: time.Now()}
			h.mu.Unlock()
		case c := <-h.unregister:
			h.mu.Lock()
			delete(h.clients, c)
			h.mu.Unlock()
		case msg := <-h.broadcast:
			h.mu.RLock()
			for conn := range h.clients {
				_ = conn.WriteMessage(websocket.TextMessage, msg)
			}
			h.mu.RUnlock()
		}
	}
}

func (h *hub) broadcastAuction(event string, payload interface{}) {
	body := map[string]interface{}{
		"type": event,
		"payload": payload,
		"ts": time.Now().UnixMilli(),
	}
	b, _ := json.Marshal(body)
	select {
	case h.broadcast <- b:
	default:
	}
}

func main() {
	engineURL := getEnv("ENGINE_URL", engineURLDefault)
	if engineURL != "" && !strings.HasPrefix(engineURL, "http://") && !strings.HasPrefix(engineURL, "https://") {
		engineURL = "http://" + engineURL
	}
	identityURL := getEnv("IDENTITY_URL", identityURLDefault)
	redisAddr := getEnv("REDIS_ADDR", redisAddrDefault)

	var rdb *redis.Client
	if strings.HasPrefix(redisAddr, "redis://") {
		opt, err := redis.ParseURL(redisAddr)
		if err != nil {
			log.Fatalf("redis parse URL: %v", err)
		}
		rdb = redis.NewClient(opt)
	} else {
		rdb = redis.NewClient(&redis.Options{Addr: redisAddr})
	}
	ctx := context.Background()
	if err := rdb.Ping(ctx).Err(); err != nil {
		log.Printf("redis ping: %v (continuing)", err)
	}

	h := newHub()
	go h.run(ctx)

	// Redis Pub/Sub：轉發拍賣事件到 WebSocket
	go func() {
		sub := rdb.Subscribe(ctx, "mirage:auction:*")
		ch := sub.Channel()
		for msg := range ch {
			h.broadcast <- []byte(msg.Payload)
		}
	}()

	r := gin.Default()
	// CORS：允許前端網域（mirage-exchange.dennisleehappy.org）與本機開發
	corsOrigins := getEnv("CORS_ORIGINS", "https://mirage-exchange.dennisleehappy.org,http://localhost:3000,http://127.0.0.1:3000")
	allowedOrigins := make(map[string]struct{})
	for _, o := range strings.Split(corsOrigins, ",") {
		if s := strings.TrimSpace(o); s != "" {
			allowedOrigins[s] = struct{}{}
		}
	}
	upgrader.CheckOrigin = func(r *http.Request) bool {
		origin := r.Header.Get("Origin")
		_, ok := allowedOrigins[origin]
		return ok || origin == ""
	}
	r.Use(func(c *gin.Context) {
		origin := c.GetHeader("Origin")
		if _, ok := allowedOrigins[origin]; ok {
			c.Header("Access-Control-Allow-Origin", origin)
		}
		c.Header("Access-Control-Allow-Credentials", "true")
		c.Header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Content-Type, Authorization")
		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(http.StatusNoContent)
			return
		}
		c.Next()
	})
	r.GET("/ws", func(c *gin.Context) {
		conn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
		if err != nil {
			return
		}
		h.register <- conn
		defer func() { h.unregister <- conn }()

		// 每 10 秒刷新虛擬 ID（可呼叫 identity 服務取得新 token，此處簡化為廣播事件）
		ticker := time.NewTicker(identityRotateSec * time.Second)
		defer ticker.Stop()
		go func() {
			for range ticker.C {
				h.mu.RLock()
				st, ok := h.clients[conn]
				h.mu.RUnlock()
				if !ok {
					return
				}
				st.mu.Lock()
				st.virtualID = "vid_" + time.Now().Format("150405.000")
				st.lastRotate = time.Now()
				v := st.virtualID
				st.mu.Unlock()
				payload := map[string]interface{}{
					"type": "identity_refreshed",
					"payload": map[string]interface{}{
						"virtualId":   v,
						"expiresAtMs": time.Now().Add(identityRotateSec * time.Second).UnixMilli(),
					},
					"ts": time.Now().UnixMilli(),
				}
				b, _ := json.Marshal(payload)
				_ = conn.WriteMessage(websocket.TextMessage, b)
			}
		}()

		for {
			_, message, err := conn.ReadMessage()
			if err != nil {
				break
			}
			// 可根據 message 轉發到 engine（下單等）
			_ = message
		}
	})

	// HTTP 代理：轉發到 Engine / Identity（前端也可直連，這裡提供統一入口）
	r.POST("/api/auction/create", proxyCreateAuction(engineURL))
	r.POST("/api/auction/bid", proxyBid(engineURL))
	r.POST("/api/auction/settle", proxySettle(engineURL))
	r.GET("/api/auction/leaderboard/:id", proxyLeaderboard(engineURL))
	if identityURL == "" {
		r.GET("/api/identity/token", localIdentityToken())
	} else {
		r.GET("/api/identity/token", proxyGetToken(identityURL))
	}

	port := getEnv("PORT", "8080")
	if err := r.Run(":" + port); err != nil {
		log.Fatal(err)
	}
}

func getEnv(k, d string) string {
	if v := os.Getenv(k); v != "" {
		return v
	}
	return d
}

// localIdentityToken 在未設定 IDENTITY_URL 時由 Gateway 直接產生虛擬 ID（方案 2 極限壓縮用）
func localIdentityToken() gin.HandlerFunc {
	return func(c *gin.Context) {
		b := make([]byte, 6)
		if _, err := rand.Read(b); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "rand failed"})
			return
		}
		virtualID := "vid_" + base64.URLEncoding.EncodeToString(b)[:8]
		expiresAtMs := time.Now().Add(identityRotateSec * time.Second).UnixMilli()
		c.JSON(http.StatusOK, gin.H{"virtualId": virtualID, "expiresAtMs": expiresAtMs})
	}
}

func proxyCreateAuction(base string) gin.HandlerFunc {
	return proxyPOST(base + "/auction/create")
}
func proxyBid(base string) gin.HandlerFunc {
	return proxyPOST(base + "/auction/bid")
}
func proxySettle(base string) gin.HandlerFunc {
	return proxyPOST(base + "/auction/settle")
}
func proxyGetToken(base string) gin.HandlerFunc {
	return proxyGET(base + "/identity/token")
}

func proxyPOST(url string) gin.HandlerFunc {
	client := &http.Client{Timeout: 10 * time.Second}
	return func(c *gin.Context) {
		req, err := http.NewRequestWithContext(c.Request.Context(), http.MethodPost, url, c.Request.Body)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		req.Header.Set("Content-Type", "application/json")
		resp, err := client.Do(req)
		if err != nil {
			c.JSON(http.StatusBadGateway, gin.H{"error": err.Error()})
			return
		}
		defer resp.Body.Close()
		c.DataFromReader(resp.StatusCode, resp.ContentLength, resp.Header.Get("Content-Type"), resp.Body, nil)
	}
}

func proxyGET(url string) gin.HandlerFunc {
	client := &http.Client{Timeout: 5 * time.Second}
	return func(c *gin.Context) {
		req, err := http.NewRequestWithContext(c.Request.Context(), http.MethodGet, url, nil)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		resp, err := client.Do(req)
		if err != nil {
			c.JSON(http.StatusOK, gin.H{"virtualId": "vid_local", "expiresAtMs": time.Now().Add(10 * time.Second).UnixMilli()})
			return
		}
		defer resp.Body.Close()
		c.DataFromReader(resp.StatusCode, resp.ContentLength, resp.Header.Get("Content-Type"), resp.Body, nil)
	}
}

func proxyLeaderboard(base string) gin.HandlerFunc {
	return func(c *gin.Context) {
		id := c.Param("id")
		_ = base
		c.JSON(http.StatusOK, gin.H{"auctionId": id, "entries": []interface{}{}})
	}
}
