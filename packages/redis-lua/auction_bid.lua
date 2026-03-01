-- 極短線拍賣：原子出價
-- KEYS[1]: auction:{id} (ZSet, score=出價金額, member=bidder_id)
-- KEYS[2]: auction:{id}:meta (Hash: status, end_at, max_bid, winner)
-- ARGV[1]: bidder_id
-- ARGV[2]: bid_amount (number as string)
-- ARGV[3]: now_ts (Unix ms)
-- Returns: "ok" | "ended" | "outbid" (當前為最高價時回傳 "ok")
local zkey = KEYS[1]
local metakey = KEYS[2]
local bidder = ARGV[1]
local amount = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

if not amount or amount <= 0 then
  return redis.error_reply("invalid amount")
end

local status = redis.call("HGET", metakey, "status")
local end_at = redis.call("HGET", metakey, "end_at")
if status == "ended" or (end_at and tonumber(end_at) <= now) then
  return "ended"
end

redis.call("ZADD", zkey, amount, bidder)
local rank = redis.call("ZRANK", zkey, bidder)
local max_score = redis.call("ZREVRANGE", zkey, 0, 0, "WITHSCORES")
local is_leader = (max_score[1] == bidder)

if is_leader then
  redis.call("HSET", metakey, "max_bid", amount, "winner", bidder)
end

return is_leader and "ok" or "outbid"
