"""
API Test Suite for Car Lease LLM API
Tests all endpoints and validates responses
"""
import requests
import json
import time
from pathlib import Path
from typing import Dict, Any

# Configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_PDF_PATH = "contracts"  # Path to your test PDFs


class Colors:
    """Terminal colors for pretty output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str):
    """Print a styled header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")


def test_root_endpoint():
    """Test the root endpoint"""
    print_header("Test 1: Root Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Root endpoint accessible")
            print_info(f"API Name: {data.get('name')}")
            print_info(f"Version: {data.get('version')}")
            print_info(f"Status: {data.get('status')}")
            return True
        else:
            print_error(f"Root endpoint returned status {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Failed to connect to API: {e}")
        return False


def test_health_endpoint():
    """Test the health check endpoint"""
    print_header("Test 2: Health Check Endpoint")
    
    try:
        # Test global health
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print_success("Global health check passed")
        else:
            print_error(f"Global health check failed with status {response.status_code}")
            
        # Test lease service health
        response = requests.get(f"{BASE_URL}/lease/health")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Lease service health check passed")
            print_info(f"Service: {data.get('service')}")
            return True
        else:
            print_error(f"Lease health check failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False


def test_invalid_file_upload():
    """Test uploading an invalid file"""
    print_header("Test 3: Invalid File Upload")
    
    try:
        # Create a fake text file
        files = {'file': ('test.txt', b'This is not a PDF', 'text/plain')}
        response = requests.post(f"{BASE_URL}/lease/extract", files=files)
        
        if response.status_code == 400:
            print_success("API correctly rejected non-PDF file")
            data = response.json()
            print_info(f"Error message: {data.get('detail', {}).get('error')}")
            return True
        else:
            print_warning(f"Expected 400 status but got {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Test failed: {e}")
        return False


def test_valid_pdf_extraction(pdf_path: str = None):
    """Test extracting data from a valid PDF"""
    print_header("Test 4: Valid PDF Extraction")
    
    # Find a test PDF
    if pdf_path is None:
        contracts_dir = Path(TEST_PDF_PATH)
        if contracts_dir.exists():
            pdf_files = list(contracts_dir.glob("*.pdf"))
            if pdf_files:
                pdf_path = pdf_files[0]
                print_info(f"Using test PDF: {pdf_path.name}")
            else:
                print_warning("No PDF files found in contracts directory")
                print_info("Skipping PDF extraction test")
                return None
        else:
            print_warning(f"Contracts directory '{TEST_PDF_PATH}' not found")
            print_info("Skipping PDF extraction test")
            return None
    
    try:
        # Upload PDF
        with open(pdf_path, 'rb') as f:
            files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
            
            print_info("Uploading PDF and processing (this may take 10-30 seconds)...")
            start_time = time.time()
            
            response = requests.post(f"{BASE_URL}/lease/extract", files=files)
            
            elapsed_time = time.time() - start_time
            
        if response.status_code == 200:
            print_success(f"PDF processed successfully in {elapsed_time:.2f} seconds")
            
            data = response.json()
            
            # Validate response structure
            print_info("\nValidating response structure...")
            
            required_fields = ['success', 'metadata', 'extracted_data']
            for field in required_fields:
                if field in data:
                    print_success(f"Field '{field}' present")
                else:
                    print_error(f"Field '{field}' missing")
            
            # Check metadata
            if 'metadata' in data:
                metadata = data['metadata']
                print_info("\nMetadata:")
                print(f"  • Filename: {metadata.get('filename')}")
                print(f"  • File size: {metadata.get('file_size_bytes')} bytes")
                print(f"  • Processing time: {metadata.get('processing_time_seconds')} seconds")
                print(f"  • Text length: {metadata.get('text_length')} characters")
                print(f"  • LLM model: {metadata.get('llm_model')}")
            
            # Check vehicle summary
            if 'vehicle_summary' in data:
                vehicle = data['vehicle_summary']
                print_info("\nVehicle Summary:")
                print(f"  • Car: {vehicle.get('car_name')}")
                print(f"  • VIN: {vehicle.get('vin')}")
                print(f"  • Monthly Payment: {vehicle.get('monthly_payment')}")
                print(f"  • Lease Term: {vehicle.get('lease_term')}")
            
            # Check extracted data structure
            if 'extracted_data' in data:
                extracted = data['extracted_data']
                sections = len(extracted.keys())
                print_success(f"\nExtracted {sections} data sections")
                
                # Count populated fields
                total_fields = 0
                populated_fields = 0
                
                for section, fields in extracted.items():
                    if isinstance(fields, dict):
                        for key, value in fields.items():
                            if isinstance(value, dict):
                                # Nested section (like Payment Details)
                                for subkey, subvalue in value.items():
                                    total_fields += 1
                                    if subvalue != "Information not available":
                                        populated_fields += 1
                            else:
                                total_fields += 1
                                if value != "Information not available":
                                    populated_fields += 1
                
                print_info(f"Populated fields: {populated_fields}/{total_fields} ({populated_fields/total_fields*100:.1f}%)")
            
            # Check warnings
            if 'warnings' in data and data['warnings']:
                print_warning("\nWarnings:")
                for warning in data['warnings']:
                    print(f"  • {warning}")
            
            # Save response to file for inspection
            output_file = "test_output.json"
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            print_info(f"\nFull response saved to: {output_file}")
            
            return True
            
        else:
            print_error(f"PDF extraction failed with status {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_documentation():
    """Test that API documentation is accessible"""
    print_header("Test 5: API Documentation")
    
    try:
        response = requests.get(f"{BASE_URL}/docs")
        
        if response.status_code == 200:
            print_success("API documentation accessible at /docs")
            return True
        else:
            print_error(f"API documentation returned status {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Failed to access documentation: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print_header("CAR LEASE LLM API - TEST SUITE")
    
    print(f"{Colors.BOLD}Testing API at: {BASE_URL}{Colors.END}\n")
    
    results = {
        "Root Endpoint": test_root_endpoint(),
        "Health Check": test_health_endpoint(),
        "Invalid File Upload": test_invalid_file_upload(),
        "Valid PDF Extraction": test_valid_pdf_extraction(),
        "API Documentation": test_api_documentation()
    }
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for result in results.values() if result is True)
    failed = sum(1 for result in results.values() if result is False)
    skipped = sum(1 for result in results.values() if result is None)
    total = len(results)
    
    for test_name, result in results.items():
        if result is True:
            print_success(f"{test_name}: PASSED")
        elif result is False:
            print_error(f"{test_name}: FAILED")
        else:
            print_warning(f"{test_name}: SKIPPED")
    
    print(f"\n{Colors.BOLD}Results: {passed} passed, {failed} failed, {skipped} skipped out of {total} tests{Colors.END}\n")
    
    if failed == 0 and passed > 0:
        print_success("🎉 All tests passed!")
    elif failed > 0:
        print_error("❌ Some tests failed")
    
    return failed == 0


if __name__ == "__main__":
    import sys
    
    print(f"{Colors.BOLD}Car Lease LLM API Test Suite{Colors.END}")
    print(f"Version: 1.0.0\n")
    
    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/", timeout=2)
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to API at {BASE_URL}")
        print_info("Please start the API server first:")
        print_info("  uvicorn app.main:app --reload")
        sys.exit(1)
    
    # Run tests
    success = run_all_tests()
    
    sys.exit(0 if success else 1)
    