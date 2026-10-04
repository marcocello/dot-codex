FROM node:24-alpine AS build
WORKDIR /app
COPY frontend/app/package*.json ./
RUN npm ci
COPY frontend/app/ ./
RUN npm run build

FROM caddy:2-alpine
COPY deploy/Caddyfile /etc/caddy/Caddyfile
COPY --from=build /app/dist /srv
EXPOSE 80 443
