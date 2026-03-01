# Render Private Service 用 Redis 映像（方案 2 極限壓縮）
# 可選：啟用 Keyspace Notifications 以配合 Sentinel（Render 上若不跑 Sentinel 可省略）
FROM redis:7-alpine
CMD ["redis-server", "--notify-keyspace-events", "Ex"]
