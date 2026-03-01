//! 身份洗牌矩陣 — 發放/刷新虛擬 ID（Token），寫入 Redis Set/Hash

use axum::{
    routing::get,
    Json, Router,
};
use redis::Commands;
use serde::Serialize;
use std::env;
use std::time::{SystemTime, UNIX_EPOCH};
use tower_http::cors::CorsLayer;
use uuid::Uuid;

const REDIS_ADDR_DEFAULT: &str = "redis://127.0.0.1:6379/";
const TOKEN_TTL_SEC: i64 = 15;

#[derive(Serialize)]
struct TokenRes {
    virtual_id: String,
    expires_at_ms: i64,
    error: Option<String>,
}

fn redis_client() -> redis::Client {
    let addr = env::var("REDIS_ADDR").unwrap_or_else(|_| REDIS_ADDR_DEFAULT.to_string());
    redis::Client::open(addr).expect("redis client")
}

fn now_ms() -> i64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_millis() as i64
}

async fn get_token() -> Json<TokenRes> {
    let client = redis_client();
    let mut conn = client.get_connection().ok().unwrap();
    let virtual_id = format!("vid_{}", Uuid::new_v4().simple());
    let expires_at_ms = now_ms() + TOKEN_TTL_SEC as i64 * 1000;
    let key = format!("identity:token:{}", virtual_id);
    let _: () = conn.set_ex(&key, "1", TOKEN_TTL_SEC as u64).unwrap_or(());
    Json(TokenRes {
        virtual_id: virtual_id.clone(),
        expires_at_ms,
        error: None,
    })
}

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/identity/token", get(get_token))
        .layer(CorsLayer::permissive());

    let port = env::var("PORT").unwrap_or_else(|_| "8082".to_string());
    let addr = format!("0.0.0.0:{}", port);
    let listener = tokio::net::TcpListener::bind(&addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
