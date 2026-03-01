//! 地獄火撮合引擎 — 拍賣 API、執行 Redis Lua（ZSet 競標/結標）

use axum::{
    extract::Path,
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use std::env;
use std::collections::HashMap;
use tower_http::cors::CorsLayer;

const REDIS_ADDR_DEFAULT: &str = "redis://127.0.0.1:6379/";
const LUA_CREATE: &str = include_str!("../../../packages/redis-lua/auction_create.lua");
const LUA_BID: &str = include_str!("../../../packages/redis-lua/auction_bid.lua");
const LUA_SETTLE: &str = include_str!("../../../packages/redis-lua/auction_settle.lua");

#[derive(Deserialize)]
struct CreateAuctionReq {
    auction_id: String,
    duration_ms: Option<u64>,
}

#[derive(Serialize)]
struct CreateAuctionRes {
    ok: bool,
    error: Option<String>,
    end_at_ms: Option<i64>,
}

#[derive(Deserialize)]
struct BidReq {
    auction_id: String,
    bidder_id: String,
    amount: f64,
}

#[derive(Serialize)]
struct BidRes {
    status: String,
    error: Option<String>,
}

#[derive(Deserialize)]
struct SettleReq {
    auction_id: String,
}

#[derive(Serialize)]
struct SettleRes {
    ok: bool,
    winner_id: Option<String>,
    top_bid: Option<f64>,
    error: Option<String>,
}

#[derive(Serialize)]
struct LeaderboardEntry {
    bidder_id: String,
    amount: f64,
    rank: u32,
}

#[derive(Serialize)]
struct LeaderboardRes {
    entries: Vec<LeaderboardEntry>,
    error: Option<String>,
}

fn redis_client() -> redis::Client {
    let addr = env::var("REDIS_ADDR").unwrap_or_else(|_| REDIS_ADDR_DEFAULT.to_string());
    redis::Client::open(addr).expect("redis client")
}

async fn create_auction(
    Json(req): Json<CreateAuctionReq>,
) -> Json<CreateAuctionRes> {
    let client = redis_client();
    let mut conn = client.get_connection().map_err(|e| e.to_string()).unwrap();
    let duration_ms = req.duration_ms.unwrap_or(5000);
    let end_at_ms = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_millis() as i64
        + duration_ms as i64;
    let zkey = format!("auction:{}", req.auction_id);
    let metakey = format!("auction:{}:meta", req.auction_id);
    let ttl = 60i64;
    let _: () = redis::Script::new(LUA_CREATE)
        .key(&zkey)
        .key(&metakey)
        .arg(&req.auction_id)
        .arg(end_at_ms)
        .arg(ttl)
        .invoke(&mut conn)
        .map_err(|e| e.to_string())
        .unwrap();
    Json(CreateAuctionRes {
        ok: true,
        error: None,
        end_at_ms: Some(end_at_ms),
    })
}

async fn bid(Json(req): Json<BidReq>) -> Json<BidRes> {
    let client = redis_client();
    let mut conn = client.get_connection().map_err(|e| e.to_string()).unwrap();
    let zkey = format!("auction:{}", req.auction_id);
    let metakey = format!("auction:{}:meta", req.auction_id);
    let now = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_millis() as i64;
    let result: String = redis::Script::new(LUA_BID)
        .key(&zkey)
        .key(&metakey)
        .arg(&req.bidder_id)
        .arg(req.amount)
        .arg(now)
        .invoke(&mut conn)
        .unwrap_or_else(|_| "invalid".to_string());
    let status = match result.as_str() {
        "ok" => "ok",
        "outbid" => "outbid",
        "ended" => "ended",
        _ => "invalid",
    };
    if status == "ok" || status == "outbid" {
        let rank: Option<u32> = redis::cmd("ZREVRANK")
            .arg(&zkey)
            .arg(&req.bidder_id)
            .query(&mut conn)
            .ok()
            .and_then(|r: Option<i64>| r.map(|r| (r + 1) as u32));
        let rank = rank.unwrap_or(0);
        let payload: HashMap<&str, serde_json::Value> = [
            ("type", serde_json::json!("bid")),
            ("auction_id", serde_json::json!(req.auction_id)),
            ("bidder_id", serde_json::json!(req.bidder_id)),
            ("amount", serde_json::json!(req.amount)),
            ("rank", serde_json::json!(rank)),
        ]
        .into_iter()
        .collect();
        let channel = format!("mirage:auction:{}", req.auction_id);
        let _: () = redis::cmd("PUBLISH")
            .arg(&channel)
            .arg(serde_json::to_string(&payload).unwrap_or_default())
            .query(&mut conn)
            .unwrap_or(());
    }
    Json(BidRes {
        status: status.to_string(),
        error: None,
    })
}

async fn settle(Json(req): Json<SettleReq>) -> Json<SettleRes> {
    let client = redis_client();
    let mut conn = client.get_connection().map_err(|e| e.to_string()).unwrap();
    let zkey = format!("auction:{}", req.auction_id);
    let metakey = format!("auction:{}:meta", req.auction_id);
    let now = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_millis() as i64;
    let result: Vec<String> = redis::Script::new(LUA_SETTLE)
        .key(&zkey)
        .key(&metakey)
        .arg(now)
        .invoke(&mut conn)
        .unwrap_or_default();
    let winner_id = result.get(0).filter(|s| !s.is_empty()).cloned();
    let top_bid = result.get(1).and_then(|s| s.parse().ok());
    if winner_id.is_some() {
        let payload: HashMap<&str, serde_json::Value> = [
            ("type", serde_json::json!("settled")),
            ("auction_id", serde_json::json!(req.auction_id)),
            ("winner_id", serde_json::json!(winner_id.as_ref().unwrap())),
            ("top_bid", serde_json::json!(top_bid)),
        ]
        .into_iter()
        .collect();
        let channel = format!("mirage:auction:{}", req.auction_id);
        let _: () = redis::cmd("PUBLISH")
            .arg(&channel)
            .arg(serde_json::to_string(&payload).unwrap_or_default())
            .query(&mut conn)
            .unwrap_or(());
    }
    Json(SettleRes {
        ok: winner_id.is_some(),
        winner_id,
        top_bid,
        error: None,
    })
}

async fn leaderboard(Path(id): Path<String>) -> Json<LeaderboardRes> {
    let client = redis_client();
    let mut conn = client.get_connection().map_err(|e| e.to_string()).unwrap();
    let zkey = format!("auction:{}", id);
    let raw: Vec<String> = redis::cmd("ZREVRANGE")
        .arg(&zkey)
        .arg(0)
        .arg(9)
        .arg("WITHSCORES")
        .query(&mut conn)
        .unwrap_or_default();
    let mut entries = Vec::new();
    for (i, chunk) in raw.chunks(2).enumerate() {
        if chunk.len() == 2 {
            let bidder_id = chunk[0].clone();
            let amount: f64 = chunk[1].parse().unwrap_or(0.0);
            entries.push(LeaderboardEntry {
                bidder_id,
                amount,
                rank: (i + 1) as u32,
            });
        }
    }
    Json(LeaderboardRes {
        entries,
        error: None,
    })
}

fn app() -> Router {
    Router::new()
        .route("/auction/create", post(create_auction))
        .route("/auction/bid", post(bid))
        .route("/auction/settle", post(settle))
        .route("/auction/leaderboard/:id", get(leaderboard))
        .layer(CorsLayer::permissive())
}

#[tokio::main]
async fn main() {
    let port = env::var("PORT").unwrap_or_else(|_| "8081".to_string());
    let addr = format!("0.0.0.0:{}", port);
    let listener = tokio::net::TcpListener::bind(&addr).await.unwrap();
    axum::serve(listener, app()).await.unwrap();
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_app_router_builds() {
        let _ = app();
    }
}
