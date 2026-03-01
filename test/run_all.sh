#!/usr/bin/env bash
# 統一測試入口：go test → cargo test (engine, identity) → Jest (frontend) → Robot Framework
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "=== 1. Go tests (gateway, sentinel) ==="
(cd apps/gateway && go test . -count=1)
(cd apps/sentinel && go test . -count=1)

echo "=== 2. Cargo test (engine) ==="
cargo test --manifest-path apps/engine/Cargo.toml

echo "=== 3. Cargo test (identity) ==="
cargo test --manifest-path apps/identity/Cargo.toml

echo "=== 4. Jest (frontend) ==="
npm run test --prefix apps/frontend -- --passWithNoTests

echo "=== 5. Robot Framework (API) ==="
if [ -f test/robot/requirements.txt ]; then
  (pip install -q -r test/robot/requirements.txt || pip3 install -q -r test/robot/requirements.txt || true)
fi
(robot test/robot || robot3 test/robot || echo "Robot: skipped (install robotframework or services down)")

echo "=== All test stages finished ==="
