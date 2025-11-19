# HexiRules Docker Deployment

This directory contains Docker configuration files for deploying the HexiRules application.

## Components

1. **Backend API Server** (`Dockerfile.server`)
   - Python FastAPI server
   - Serves API endpoints for world management, simulation, etc.
   - Runs on port 8000

2. **Frontend Web UI** (`Dockerfile.web`)
   - React-based web UI
   - Built with Vite and served by Nginx
   - Runs on port 80
   - Mounted at `/hexios/` path
   - Proxies API requests to the backend

## Deployment Instructions

### Prerequisites

- Docker and Docker Compose installed
- Git repository cloned

### Building and Running

1. Navigate to the repository root:
   ```bash
   cd /path/to/HexiRules
   ```

2. Build and start the containers:
   ```bash
   cd docker
   docker-compose up -d
   ```

3. Access the application:
   - Frontend: http://localhost/hexios/
   - API: http://localhost:8000/

### Stopping the Services

```bash
cd docker
docker-compose down
```

## Data Persistence

- World data is stored in the `/app/data` directory inside the container
- This directory is mapped to `../data` in the host for persistence

## Configuration

You can modify environment variables in the `docker-compose.yml` file to change:
- Port mappings
- Host settings
- Volume mounts for data persistence

## Troubleshooting

If you encounter issues:

1. Check container logs:
   ```bash
   docker-compose logs api
   docker-compose logs web
   ```

2. Verify network connectivity:
   ```bash
   docker network inspect docker_default
   ```

3. For API issues, access the health endpoint:
   ```bash
   curl http://localhost:8000/health
   ```

## Development

For development purposes, you can modify the docker-compose.yml to mount source code directories as volumes for live code changes.