# 🦠 ClamAV Antivirus Scanner Project - Simple Overview

## What this Project Actually Does?

This project is like building a virus scanner that runs in containers (like virtual boxes). It's pretty simple - you upload a file, it checks if the file has virus, and tells you the result. That's it!

## The Big Picture (How Everything Works Together)

```
User Upload File → FastAPI (Python Web App) → ClamAV Scanner → Result Back to User
                        ↓
                   MongoDB Database 
                  (Stores scan results)
```

Think of it like this:
- **FastAPI** = The waiter who takes your order
- **ClamAV** = The chef who cooks (scans) your file  
- **MongoDB** = The receipt book that remembers everything
- **Docker** = The restaurant building that contains everything

## My Journey Building This (Step by Step)

### Step 1: Setting up the Basic Structure
First I made the main folders:
```
clamav-task/
├── app/          (where my python code lives)
├── tests/        (test files to check if working)
├── Dockerfile    (recipe to build my app container)
└── docker-compose.yml (connects all containers together)
```

### Step 2: Writing the FastAPI Code
I created a simple web API that can:
- Take file uploads from users
- Send files to ClamAV for scanning  
- Save results in MongoDB database
- Show scan history

The main files I wrote:
- `main.py` - The starting point of my app
- `app/api.py` - All the web routes (like /upload, /scans)
- `app/scanner.py` - Talks to ClamAV scanner
- `app/database.py` - Saves stuff to MongoDB

### Step 3: Docker Setup (The Tricky Part!)
This was confusing at first but basically:

**Dockerfile** = Recipe to build my Python app into a container
- Start with Python 3.11 
- Install my code dependencies
- Copy my app files
- Tell it to run FastAPI server

**docker-compose.yml** = Connects 3 containers together:
1. **clamav** - The virus scanner (port 3310)
2. **mongodb** - Database to store results (port 27017)  
3. **fastapi** - My Python web app (port 8000)

### Step 4: The Health Check Problem (I Got Stuck Here!)
My FastAPI container wasn't starting because it was waiting for ClamAV to be "healthy". But ClamAV health check was failing!

The problem was in docker-compose.yml:
```yaml
# This was wrong:
test: ["CMD", "clamdscan", "--ping"]

# Fixed it to this:
test: ["CMD", "sh", "-c", "clamdtop || nc -z localhost 3310"]
```

Took me while to figure this out because the error messages were confusing.

### Step 5: Testing Everything
Created test files:
- `clean_file.txt` - Normal safe file
- `eicar.txt` - Fake virus file for testing (it's harmless but triggers antivirus)

Made a test script `test_api.py` to check if everything works.

## How the Containers Talk to Each Other

```
    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │   FastAPI App   │    │   ClamAV Daemon │    │    MongoDB      │
    │   (Port 8000)   │    │   (Port 3310)   │    │   (Port 27017)  │
    └─────────────────┘    └─────────────────┘    └─────────────────┘
            │                        │                        │
            │──── Scan File ────────→│                        │
            │←─── Scan Result ───────│                        │
            │                        │                        │
            │──── Save Result ──────────────────────────────→│
            │←─── Confirmation ──────────────────────────────│
```

## What I Learned (The Hard Way)

1. **Docker containers need time to start** - ClamAV takes like 5 minutes first time because it downloads virus definitions
2. **Health checks are important** - If one container isn't healthy, others won't start  
3. **Port mapping matters** - Make sure ports don't conflict
4. **Environment variables** - How containers find each other (like MONGODB_URL=mongodb://mongodb:27017)
5. **Volume mounting** - So data doesn't disappear when containers restart

## Common Problems I Faced

### Problem 1: "ModuleNotFoundError: No module named 'requests'"
**Solution**: Install missing Python packages with `pip install requests`

### Problem 2: FastAPI container not starting  
**Solution**: Fixed ClamAV health check in docker-compose.yml

### Problem 3: "curl -X POST" doesn't work in PowerShell
**Solution**: Use `Invoke-WebRequest` or install real curl with chocolatey

### Problem 4: Files not uploading properly
**Solution**: Make sure test files exist in [`tests`](tests ) folder and use correct file paths

## How to Use This Project

1. **Start everything**: `docker-compose up --build`
2. **Wait for ClamAV to load** (takes few minutes first time)
3. **Test the API**: Go to http://localhost:8000/docs
4. **Upload files**: Use the web interface or curl commands
5. **Check results**: See scan history and statistics

## File Structure Explained

```
clamav-task/
├── app/
│   ├── api.py           # Web routes (/upload, /scans, etc.)
│   ├── scanner.py       # ClamAV communication
│   ├── database.py      # MongoDB operations  
│   └── models.py        # Data structures
├── tests/
│   ├── clean_file.txt   # Safe test file
│   └── eicar.txt        # Virus test file
├── main.py              # App startup
├── Dockerfile           # Build recipe
├── docker-compose.yml   # Container orchestration
├── requirements.txt     # Python dependencies
└── test_api.py          # Automated tests
```

## Technologies Used (and Why)

- **FastAPI** - Modern Python web framework, easy to use, automatic docs
- **ClamAV** - Open source antivirus, reliable, well-known
- **MongoDB** - NoSQL database, good for storing scan results  
- **Docker** - Containerization, makes deployment easier
- **Uvicorn** - ASGI server to run FastAPI

## What Makes This Project Cool

✅ **Containerized** - Everything runs in isolated environments  
✅ **RESTful API** - Standard web API that other apps can use  
✅ **Real virus scanning** - Uses actual ClamAV antivirus engine  
✅ **Persistent storage** - Results saved in database  
✅ **Interactive docs** - Swagger UI for testing  
✅ **Health monitoring** - Containers check if services are running  

