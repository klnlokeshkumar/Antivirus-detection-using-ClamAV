import os
import uuid
import time
import aiofiles
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse

from .database import get_collection
from .models import ScanResponse, ScanRecord, ScanStatus, ScanResult, HealthResponse
from .scanner import scanner

router = APIRouter()

# Upload directory
UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=ScanResponse)
async def upload_and_scan(file: UploadFile = File(...)):
    """Upload a file and scan it for malware"""
    
    # Generate unique scan ID
    scan_id = str(uuid.uuid4())
    timestamp = datetime.utcnow()
    
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    # Save file temporarily
    file_path = os.path.join(UPLOAD_DIR, f"{scan_id}_{file.filename}")
    file_size = 0
    
    try:
        # Write file to disk
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            file_size = len(content)
            await f.write(content)
        
        
        # Create initial scan record
        scan_record = ScanRecord(
            scan_id=scan_id,
            filename=file.filename,
            file_size=file_size,
            file_path=file_path,
            status=ScanStatus.SCANNING,
            timestamp=timestamp
        )
        
        # Store in database
        collection = await get_collection()
        collection.insert_one(scan_record.dict())
        
        # Perform scan
        start_time = time.time()
        result, threat_name = await scanner.scan_file(file_path)
        scan_time = time.time() - start_time
        
        # Update scan record
        scan_record.status = ScanStatus.COMPLETED
        scan_record.result = ScanResult(result)
        scan_record.threat_name = threat_name
        scan_record.scan_time = scan_time
        scan_record.clamav_version = await scanner.get_version()
        
        # Update database
        collection.update_one(
            {"scan_id": scan_id},
            {"$set": scan_record.dict()}
        )
        
        # Clean up file after successful scan
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            pass
        
        return ScanResponse(
            scan_id=scan_id,
            filename=file.filename,
            file_size=file_size,
            status=scan_record.status,
            result=scan_record.result,
            threat_name=threat_name,
            scan_time=scan_time,
            timestamp=timestamp
        )
        
    except Exception as e:
        # Update scan record with error
        error_message = str(e)
        collection = await get_collection()
        collection.update_one(
            {"scan_id": scan_id},
            {"$set": {
                "status": ScanStatus.FAILED.value,
                "result": ScanResult.ERROR.value,
                "error_message": error_message
            }}
        )
        
        # Clean up file after error
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as cleanup_error:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scan failed: {error_message}"
        )

@router.get("/scans", response_model=List[ScanResponse])
async def get_scans(limit: int = 50, skip: int = 0):
    """Get all scan results"""
    collection = await get_collection()
    
    cursor = collection.find().sort("timestamp", -1).skip(skip).limit(limit)
    scans = []
    
    for document in cursor:
        # Remove MongoDB's _id field and convert to ScanResponse
        document.pop('_id', None)
        document.pop('file_path', None)  # Don't expose file paths
        document.pop('clamav_version', None)
        document.pop('signature_version', None)
        scans.append(ScanResponse(**document))
    
    return scans

@router.get("/scans/{scan_id}", response_model=ScanResponse)
async def get_scan(scan_id: str):
    """Get specific scan result"""
    collection = await get_collection()
    
    document = collection.find_one({"scan_id": scan_id})
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    # Remove MongoDB's _id field and sensitive data
    document.pop('_id', None)
    document.pop('file_path', None)
    document.pop('clamav_version', None)
    document.pop('signature_version', None)
    
    return ScanResponse(**document)

@router.delete("/scans/{scan_id}")
async def delete_scan(scan_id: str):
    """Delete a scan result"""
    collection = await get_collection()
    
    result = collection.delete_one({"scan_id": scan_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    return {"message": "Scan deleted successfully"}

@router.get("/stats")
async def get_stats():
    """Get scanning statistics"""
    collection = await get_collection()
    
    total_scans = collection.count_documents({})
    clean_files = collection.count_documents({"result": "clean"})
    infected_files = collection.count_documents({"result": "infected"})
    failed_scans = collection.count_documents({"result": "error"})
    
    return {
        "total_scans": total_scans,
        "clean_files": clean_files,
        "infected_files": infected_files,
        "failed_scans": failed_scans
    }