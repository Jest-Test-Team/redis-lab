// 死間哨兵 (Dead Man's Sentinel) — 監聽 Redis Keyspace 過期事件，觸發焦土/廣播邏輯
package main

import (
	"context"
	"log"
	"os"
	"strings"
	"time"

	"github.com/redis/go-redis/v9"
)

const (
	redisAddrDefault = "localhost:6379"
	keyPrefixDefault = "mirage:deadman:"
)

func main() {
	redisAddr := getEnv("REDIS_ADDR", redisAddrDefault)
	keyPrefix := getEnv("DEADMAN_KEY_PREFIX", keyPrefixDefault)

	rdb := redis.NewClient(&redis.Options{Addr: redisAddr})
	ctx := context.Background()

	if err := rdb.Ping(ctx).Err(); err != nil {
		log.Fatalf("redis ping: %v", err)
	}

	// 啟用 Keyspace Notifications（過期事件）
	if err := rdb.ConfigSet(ctx, "notify-keyspace-events", "Ex").Err(); err != nil {
		log.Printf("config set notify-keyspace-events: %v (continuing)", err)
	}

	// 訂閱 __keyevent@0__:expired
	channel := "__keyevent@0__:expired"
	sub := rdb.Subscribe(ctx, channel)
	defer sub.Close()

	log.Printf("sentinel listening on %s for channel %s (prefix=%s)", redisAddr, channel, keyPrefix)

	for msg := range sub.Channel() {
		key := msg.Payload
		if !strings.HasPrefix(key, keyPrefix) {
			continue
		}
		log.Printf("[DEADMAN] key expired: %s — triggering scorched earth policy", key)
		// 焦土政策：可在此清空約定 key、通知 Gateway 斷線等
		scorchedEarth(ctx, rdb, key)
	}
}

func scorchedEarth(ctx context.Context, rdb *redis.Client, expiredKey string) {
	// 示範：僅記錄與可選刪除相關 pattern。實際可擴充為清空資料、廣播「玉石俱焚」等
	_ = expiredKey
	pattern := "mirage:deadman:*"
	keys, err := rdb.Keys(ctx, pattern).Result()
	if err != nil {
		log.Printf("keys %s: %v", pattern, err)
		return
	}
	if len(keys) > 0 {
		if err := rdb.Del(ctx, keys...).Err(); err != nil {
			log.Printf("del deadman keys: %v", err)
		}
		log.Printf("scorched earth: removed %d keys", len(keys))
	}
	// 可 PUBLISH mirage:sentinel:scorched 讓 Gateway 廣播給所有客戶端
	_ = rdb.Publish(ctx, "mirage:sentinel:scorched", "triggered at "+time.Now().Format(time.RFC3339))
}

func getEnv(k, d string) string {
	if v := os.Getenv(k); v != "" {
		return v
	}
	return d
}
