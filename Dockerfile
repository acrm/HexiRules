# Use Node.js 18 Alpine as the base image for better security and smaller size
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files for dependency installation
COPY src/infrastructure/ui/hexios/web/package*.json ./

# Install dependencies
RUN npm ci

# Copy the React app source files
COPY src/infrastructure/ui/hexios/web/ ./

# Build the React app
RUN npm run build

# Production stage using Nginx to serve static files
FROM nginx:stable-alpine

# Copy built assets from builder stage to Nginx serve directory
COPY --from=builder /app/dist /usr/share/nginx/html/hexios

# Copy custom Nginx config to serve the app at /hexios path
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]