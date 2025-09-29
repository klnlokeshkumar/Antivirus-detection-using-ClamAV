from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class ScanStatus(str, Enum):
    PENDING = "pending"
    SCANNING = "scanning"
    COMPLETED = "completed"
    FAILED = "failed"

class ScanResult(str, Enum):
    CLEAN = "clean"
    INFECTED = "infected"
    ERROR = "error"

class ScanRequest(BaseModel):
    filename: str
    file_size: int

class ScanResponse(BaseModel):
    scan_id: str
    filename: str
    file_size: int
    status: ScanStatus
    result: Optional[ScanResult] = None
    threat_name: Optional[str] = None
    scan_time: Optional[float] = None
    timestamp: datetime
    error_message: Optional[str] = None

class ScanRecord(BaseModel):
    scan_id: str
    filename: str
    file_size: int
    file_path: str
    status: ScanStatus
    result: Optional[ScanResult] = None
    threat_name: Optional[str] = None
    scan_time: Optional[float] = None
    timestamp: datetime
    error_message: Optional[str] = None
    clamav_version: Optional[str] = None
    signature_version: Optional[str] = None

    class Config:
        use_enum_values = True

class HealthResponse(BaseModel):
    clamav_status: str
    database_status: str
    api_status: str
    clamav_version: Optional[str] = None