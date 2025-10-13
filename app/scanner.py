import os
import pyclamd
from typing import Tuple, Optional


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
                return True
            else:
                return False
        except Exception as e:
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
                return 'error', "ClamAV connection failed"

        try:
            # Check if file exists and is readable
            if not os.path.exists(file_path):
                return 'error', f"File not found: {file_path}"
            
            if not os.access(file_path, os.R_OK):
                return 'error', f"File not readable: {file_path}"

            result = self.client.scan_file(file_path)
            
            if result is None:
                return 'clean', None
            elif result.get(file_path):
                # Format: ('FOUND', 'THREAT_NAME')
                status, threat = result[file_path]
                if status == 'FOUND':
                    return 'infected', threat
                else:
                    return 'error', f"Unexpected scan status: {status}"
            else:
                return 'clean', None
                
        except Exception as e:
            return 'error', f"Scan exception: {str(e)}"

    async def get_version(self) -> Optional[str]:
        """Get ClamAV version"""
        if not self.client:
            if not await self.connect():
                return None
        
        try:
            return self.client.version()
        except Exception as e:
            return None

    async def ping(self) -> bool:
        """Ping ClamAV daemon"""
        if not self.client:
            if not await self.connect():
                return False
        
        try:
            return self.client.ping()
        except Exception as e:
            return False

# Global scanner instance
scanner = ClamAVScanner()