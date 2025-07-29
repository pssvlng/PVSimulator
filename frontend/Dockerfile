# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files from pv-simulator directory
COPY pv-simulator/package*.json ./

# Install dependencies
RUN npm ci

# Copy source code from pv-simulator directory
COPY pv-simulator/ .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built application
COPY --from=builder /app/dist/pv-simulator /usr/share/nginx/html

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
