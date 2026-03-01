FROM rust:1.75-bookworm AS build
WORKDIR /app
COPY apps/identity /app/identity
WORKDIR /app/identity
RUN cargo build --release

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=build /app/identity/target/release/mirage-identity .
EXPOSE 8082
ENV PORT=8082
CMD ["./mirage-identity"]
