npm run build

# Copy doc assets to the built site
# Astro with hybrid output creates dist/client for static assets
mkdir -p ./dist/client/assets
cp -r ./doc/assets/* ./dist/client/assets/ 2>/dev/null || true

