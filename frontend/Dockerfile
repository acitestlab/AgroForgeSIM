# -----------------------------
# Build stage
# -----------------------------
FROM node:20.13.1-alpine AS build
WORKDIR /app

# Add a non-root user for the build stage
RUN adduser -D appuser
USER appuser

# Copy package files and install dependencies
COPY package*.json ./
RUN apk update && apk upgrade && npm ci

# Copy source files and build the project
COPY . .
ARG VITE_API_URL=http://localhost:8000/api
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build

# -----------------------------
# Runtime stage (Nginx)
# -----------------------------
FROM nginx:alpine

# Copy build output from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Hardened SPA nginx config with gzip + caching + history fallback
RUN printf '%s\n' \
  'server {' \
  '    listen 8080;' \
  '    server_name _;' \
  '    server_tokens off;' \
  '' \
  '    gzip on;' \
  '    gzip_types text/plain text/css application/javascript application/json image/svg+xml;' \
  '    gzip_min_length 1024;' \
  '' \
  '    root /usr/share/nginx/html;' \
  '    index index.html;' \
  '' \
  '    # Cache immutable assets (Vite hashed files in /assets)' \
  '    location /assets/ {' \
  '        add_header Cache-Control "public, max-age=31536000, immutable";' \
  '        try_files $uri =404;' \
  '    }' \
  '' \
  '    # SPA history fallback' \
  '    location / {' \
  '        try_files $uri /index.html;' \
  '        add_header X-Content-Type-Options "nosniff";' \
  '    }' \
  '}' \
  > /etc/nginx/conf.d/default.conf

# Run as non-root on an unprivileged port
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD wget -qO- http://127.0.0.1:8080/ >/dev/null || exit 1
USER nginx
CMD ["nginx", "-g", "daemon off;"]