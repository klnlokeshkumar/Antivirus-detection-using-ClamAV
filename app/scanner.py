import os
import pyclamd
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class ClamAVScanner:
    def __init__(self):
        self.host = os.getenv("CLAMAV_HOST", "localhost")
        self.port = int(os.getenv("CLAMAV_PORT", "3310"))
        self.client = None

    async def connect(self) -> bool:
        """Connect to ClamAV daemon"""
        try:
            self.client = pyclamd.ClamdNetworkSocket(self.host, self.port)
            # Test connection
            if self.client.ping():
                logger.info(f"Connected to ClamAV at {self.host}:{self.port}")
                return True
            else:
                logger.error("ClamAV daemon is not responding")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to ClamAV: {e}")
            return False

    async def scan_file(self, file_path: str) -> Tuple[str, Optional[str]]:
        """
        Scan a file with ClamAV
        Returns: (result, threat_name)
        - result: 'clean', 'infected', or 'error'
        - threat_name: name of detected threat or None
        """
        if not self.client:
            if not await self.connect():
                logger.error(f"Cannot connect to ClamAV daemon for scanning {file_path}")
                return 'error', "ClamAV connection failed"

        try:
            # Check if file exists and is readable
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return 'error', f"File not found: {file_path}"
            
            if not os.access(file_path, os.R_OK):
                logger.error(f"File not readable: {file_path}")
                return 'error', f"File not readable: {file_path}"

            logger.info(f"Scanning file: {file_path}")
            result = self.client.scan_file(file_path)
            logger.info(f"ClamAV scan result for {file_path}: {result}")
            
            if result is None:
                logger.info(f"File {file_path} is clean")
                return 'clean', None
            elif result.get(file_path):
                # Format: ('FOUND', 'THREAT_NAME')
                status, threat = result[file_path]
                logger.info(f"ClamAV returned status: {status}, threat: {threat}")
                if status == 'FOUND':
                    return 'infected', threat
                else:
                    return 'error', f"Unexpected scan status: {status}"
            else:
                logger.info(f"File {file_path} is clean (empty result)")
                return 'clean', None
                
        except Exception as e:
            logger.error(f"Exception during scan of {file_path}: {type(e).__name__}: {e}")
            return 'error', f"Scan exception: {str(e)}"

    async def get_version(self) -> Optional[str]:
        """Get ClamAV version"""
        if not self.client:
            if not await self.connect():
                return None
        
        try:
            return self.client.version()
        except Exception as e:
            logger.error(f"Error getting ClamAV version: {e}")
            return None

    async def ping(self) -> bool:
        """Ping ClamAV daemon"""
        if not self.client:
            if not await self.connect():
                return False
        
        try:
            return self.client.ping()
        except Exception as e:
            logger.error(f"Error pinging ClamAV: {e}")
            return False

# Global scanner instance
scanner = ClamAVScanner()