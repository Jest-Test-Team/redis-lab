-- 極短線拍賣：原子結標（防超賣、唯一贏家）
-- KEYS[1]: auction:{id} (ZSet)
-- KEYS[2]: auction:{id}:meta (Hash)
-- ARGV[1]: now_ts (Unix ms)
-- Returns: winner_id or nil, top_bid
local zkey = KEYS[1]
local metakey = KEYS[2]
local now = tonumber(ARGV[1])

local end_at = redis.call("HGET", metakey, "end_at")
if not end_at or tonumber(end_at) > now then
  return redis.error_reply("not yet ended")
end

local status = redis.call("HGET", metakey, "status")
if status == "ended" then
  local w = redis.call("HGET", metakey, "winner")
  local b = redis.call("HGET", metakey, "max_bid")
  return { w, b }
end

local top = redis.call("ZREVRANGE", zkey, 0, 0, "WITHSCORES")
local winner = top[1]
local top_bid = top[2] and tonumber(top[2]) or 0

redis.call("HSET", metakey, "status", "ended", "winner", winner or "", "max_bid", top_bid)
return { winner, tostring(top_bid) }
