FROM rust:1.75-bookworm AS build
WORKDIR /app
# 保持與 main.rs 中 include_str! 路徑一致：../../../packages/redis-lua
COPY packages/redis-lua /app/packages/redis-lua
COPY apps/engine /app/engine
WORKDIR /app/engine
RUN cargo build --release

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=build /app/engine/target/release/mirage-engine .
EXPOSE 8081
ENV PORT=8081
CMD ["./mirage-engine"]
