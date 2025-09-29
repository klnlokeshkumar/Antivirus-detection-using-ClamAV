#!/usr/bin/env python3
"""
Simple test script to verify the ClamAV Scanner API
"""
import requests
import json
import time

API_BASE = "http://localhost:8000/api/v1"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{API_BASE}/health")
    if response.status_code == 200:
        health = response.json()
        print(f"✓ Health check passed")
        print(f"  API Status: {health['api_status']}")
        print(f"  ClamAV Status: {health['clamav_status']}")
        print(f"  Database Status: {health['database_status']}")
        if health.get('clamav_version'):
            print(f"  ClamAV Version: {health['clamav_version']}")
        return True
    else:
        print(f"✗ Health check failed: {response.status_code}")
        return False

def test_upload_clean_file():
    """Test uploading a clean file"""
    print("\nTesting clean file upload...")
    try:
        with open("tests/clean_file.txt", "rb") as f:
            files = {"file": ("clean_file.txt", f, "text/plain")}
            response = requests.post(f"{API_BASE}/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Clean file scan completed")
            print(f"  Scan ID: {result['scan_id']}")
            print(f"  Result: {result['result']}")
            print(f"  Scan Time: {result.get('scan_time', 'N/A')}s")
            return result['scan_id']
        else:
            print(f"✗ Clean file scan failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error uploading clean file: {e}")
        return None

def test_upload_eicar_file():
    """Test uploading EICAR test file (should be detected as malware)"""
    print("\nTesting EICAR file upload...")
    try:
        with open("tests/eicar.txt", "rb") as f:
            files = {"file": ("eicar.txt", f, "text/plain")}
            response = requests.post(f"{API_BASE}/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ EICAR file scan completed")
            print(f"  Scan ID: {result['scan_id']}")
            print(f"  Result: {result['result']}")
            print(f"  Threat Name: {result.get('threat_name', 'N/A')}")
            print(f"  Scan Time: {result.get('scan_time', 'N/A')}s")
            return result['scan_id']
        else:
            print(f"✗ EICAR file scan failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error uploading EICAR file: {e}")
        return None

def test_get_scans():
    """Test getting all scans"""
    print("\nTesting get all scans...")
    response = requests.get(f"{API_BASE}/scans")
    if response.status_code == 200:
        scans = response.json()
        print(f"✓ Retrieved {len(scans)} scan results")
        for scan in scans[:3]:  # Show first 3
            print(f"  - {scan['filename']}: {scan['result']} ({scan['status']})")
        return True
    else:
        print(f"✗ Get scans failed: {response.status_code}")
        return False

def test_get_stats():
    """Test getting statistics"""
    print("\nTesting statistics endpoint...")
    response = requests.get(f"{API_BASE}/stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"✓ Statistics retrieved")
        print(f"  Total Scans: {stats['total_scans']}")
        print(f"  Clean Files: {stats['clean_files']}")
        print(f"  Infected Files: {stats['infected_files']}")
        print(f"  Failed Scans: {stats['failed_scans']}")
        return True
    else:
        print(f"✗ Get stats failed: {response.status_code}")
        return False

def main():
    """Run all tests"""
    print("ClamAV Scanner API Test Suite")
    print("=" * 40)
    
    # Test health first
    if not test_health():
        print("Health check failed - stopping tests")
        return
    
    # Wait a moment for services to be ready
    print("\nWaiting for services to be fully ready...")
    time.sleep(2)
    
    # Run tests
    clean_scan_id = test_upload_clean_file()
    eicar_scan_id = test_upload_eicar_file()
    test_get_scans()
    test_get_stats()
    
    print("\n" + "=" * 40)
    print("Test suite completed!")
    
    if clean_scan_id:
        print(f"Clean file scan ID: {clean_scan_id}")
    if eicar_scan_id:
        print(f"EICAR file scan ID: {eicar_scan_id}")

if __name__ == "__main__":
    main()