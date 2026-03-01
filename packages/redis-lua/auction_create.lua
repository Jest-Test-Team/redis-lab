-- 建立一場極短線拍賣（5 秒視窗）
-- KEYS[1]: auction:{id} (ZSet)
-- KEYS[2]: auction:{id}:meta (Hash)
-- ARGV[1]: auction_id
-- ARGV[2]: end_at_ts (Unix ms, 通常 now + 5000)
-- ARGV[3]: ttl_sec (key 過期時間，可觸發 Keyspace Notification)
local zkey = KEYS[1]
local metakey = KEYS[2]
local end_at = tonumber(ARGV[2])
local ttl = tonumber(ARGV[3]) or 60

redis.call("DEL", zkey, metakey)
redis.call("HSET", metakey, "status", "open", "end_at", end_at, "max_bid", 0, "winner", "")
redis.call("PEXPIRE", metakey, ttl * 1000)
redis.call("PEXPIRE", zkey, ttl * 1000)
return "ok"
