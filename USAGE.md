# ClamAV Containerized Scanner - Usage Guide

## Overview
This project implements a minimalistic containerized antivirus scanning solution using:
- **ClamAV**: Open-source antivirus engine
- **FastAPI**: Modern Python web framework for the REST API
- **MongoDB**: NoSQL database for storing scan results
- **Docker**: Containerization platform

## Quick Start

### Prerequisites
- Docker Desktop installed and running
- At least 2GB of available RAM (ClamAV signature database is large)

### 1. Start the Application
```bash
docker-compose up --build
```

### 2. Wait for Services to Initialize
- ClamAV takes 2-5 minutes to download and load virus signatures
- Monitor logs for "clamd[1]: Self checking every 600 seconds"
- API will be ready when health check shows all services as "healthy"

### 3. Access the Application
- **API Base URL**: http://localhost:8000
- **Interactive API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Upload and Scan File
```bash
curl -X POST "http://localhost:8000/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@test_file.txt"
```

### Get All Scan Results
```bash
curl -X GET "http://localhost:8000/scans?limit=10&skip=0"
```

### Get Specific Scan Result
```bash
curl -X GET "http://localhost:8000/scans/{scan_id}"
```

### Get Statistics
```bash
curl -X GET "http://localhost:8000/stats"
```

### Health Check
```bash
curl -X GET "http://localhost:8000/health"
```

## Testing

### Run Test Suite
```bash
python test_api.py
```

### Manual Testing Files
- `tests/clean_file.txt` - Should be marked as clean
- `tests/eicar.txt` - Should be detected as malware (EICAR test virus)

### Expected Results
- **Clean File**: `result: "clean", threat_name: null`
- **EICAR File**: `result: "infected", threat_name: "Win.Test.EICAR_HDB-1"`

## Architecture Details

### Services
1. **ClamAV Daemon** (Port 3310)
   - Antivirus scanning engine
   - Automatically updates virus signatures
   - Exposes TCP socket for scanning requests

2. **FastAPI Application** (Port 8000)
   - REST API server
   - Handles file uploads and scanning
   - Stores results in MongoDB

3. **MongoDB** (Port 27017)
   - NoSQL database
   - Stores scan results and metadata
   - Persistent storage with Docker volumes

### File Flow
1. Client uploads file via API
2. File saved temporarily to container
3. ClamAV scans the file
4. Results stored in MongoDB
5. Temporary file deleted
6. Results returned to client

### Data Model
```json
{
  "scan_id": "uuid4-string",
  "filename": "example.txt",
  "file_size": 1024,
  "status": "completed",
  "result": "clean|infected|error",
  "threat_name": "threat-name-if-found",
  "scan_time": 0.123,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Monitoring

### Service Health
Visit http://localhost:8000/health to check:
- API status
- ClamAV daemon status
- Database connectivity
- ClamAV version information

### Logs
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs clamav
docker-compose logs fastapi
docker-compose logs mongodb
```

## Troubleshooting

### Common Issues

**ClamAV taking too long to start:**
- First startup downloads ~200MB of virus signatures
- Allow 5-10 minutes for complete initialization
- Check logs: `docker-compose logs clamav`

**Memory issues:**
- ClamAV requires significant RAM
- Ensure Docker has at least 2GB memory limit
- Monitor with: `docker stats`

**Connection refused errors:**
- Services may not be ready yet
- Use health check endpoint to verify status
- Check service dependencies in docker-compose.yml

**File upload fails:**
- Check file size limits (default: reasonable limits apply)
- Verify uploads directory permissions
- Review API logs for specific errors

### Reset Everything
```bash
# Stop and remove everything
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Start fresh
docker-compose up --build
```

## Development

### Local Development
1. Install Python dependencies: `pip install -r requirements.txt`
2. Start MongoDB and ClamAV separately
3. Set environment variables:
   ```bash
   export MONGODB_URL=mongodb://localhost:27017
   export CLAMAV_HOST=localhost
   export CLAMAV_PORT=3310
   ```
4. Run FastAPI: `uvicorn main:app --reload`

### Environment Variables
- `MONGODB_URL`: MongoDB connection string
- `CLAMAV_HOST`: ClamAV daemon hostname
- `CLAMAV_PORT`: ClamAV daemon port
- `UPLOAD_DIR`: Directory for temporary file storage

## Security Considerations

- Files are scanned in isolated containers
- Temporary files are automatically deleted
- No persistent file storage on the host
- API does not expose internal file paths
- MongoDB runs without external authentication (local development only)

## Production Deployment

For production use, consider:
- Add authentication/authorization
- Use secure MongoDB configuration
- Implement rate limiting
- Add file size restrictions
- Configure HTTPS/TLS
- Set up proper monitoring and alerting
- Use production-grade logging

## Performance

### Expected Performance
- Small files (< 1MB): ~0.1-0.5 seconds
- Large files (10MB+): ~2-5 seconds
- Concurrent scans: Limited by ClamAV daemon capacity

### Scaling
- Multiple FastAPI instances (load balancer required)
- Dedicated ClamAV instances
- MongoDB replica sets
- File storage optimization