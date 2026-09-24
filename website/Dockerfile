# Multi-stage or direct lightweight Nginx alpine image
FROM nginx:alpine

# Labels
LABEL maintainer="DriveForge Team"
LABEL description="DriveForge Web Landing Page - Production Container"

# Remove default nginx html files
RUN rm -rf /usr/share/nginx/html/*

# Copy modular web assets to nginx html directory
COPY . /usr/share/nginx/html

# Overwrite default nginx server configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose standard HTTP port
EXPOSE 80

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget -q -O - http://localhost/ || exit 1

# Start nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
