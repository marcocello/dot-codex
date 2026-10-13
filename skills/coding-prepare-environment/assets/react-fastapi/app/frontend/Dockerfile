FROM node:24-alpine AS build
WORKDIR /app
COPY app/frontend/package*.json ./
RUN npm ci
COPY app/frontend/ ./
RUN npm run build

FROM caddy:2-alpine
COPY deployments/dev/Caddyfile /etc/caddy/Caddyfile
COPY --from=build /app/dist /srv
EXPOSE 80 443
