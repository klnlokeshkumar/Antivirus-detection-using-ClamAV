# ClamAV Containerized Antivirus Scanner

## Features
- File upload and scanning via REST API
- Real-time malware detection using ClamAV
- Scan results stored in MongoDB
- Containerized architecture with Docker Compose

## Architecture
- FastAPI: REST API backend
- ClamAV: Antivirus scanning engine
- MongoDB: NoSQL database for scan results
- Docker: Containerization

## Quick Start
1. Make sure Docker Desktop is running
2. Run the application:

   docker-compose up --build

3. Access the API at `http://localhost:8000`
4. View API docs at `http://localhost:8000/docs`

## API Endpoints
- `POST /upload` - Upload and scan a file
- `GET /scans` - Get all scan results
- `GET /scans/{scan_id}` - Get specific scan result
- `GET /health` - Health check

## Testing
Upload test files to verify malware detection.