FROM node:20-alpine AS build
WORKDIR /app
COPY apps/frontend/package*.json ./
RUN npm ci
COPY apps/frontend/ ./
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=build /app/.next ./.next
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/package.json ./
COPY --from=build /app/next.config.js ./
EXPOSE 3000
ENV NODE_ENV=production
ENV HOSTNAME=0.0.0.0
CMD ["npm", "start"]
