"""
Test script to verify all API endpoints are working

Note: This is a manual test harness that expects a running server at BASE_URL.
We skip this module during automated pytest runs to avoid network and fixture
requirements.
"""
import pytest
pytestmark = pytest.mark.skip("API endpoint script; run manually against a running server.")
import requests
import pandas as pd
import json
import os
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✓ Health check: {response.status_code} - {response.json()}")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_file_list():
    """Test file listing"""
    try:
        response = requests.get(f"{BASE_URL}/api/files/list")
        print(f"✓ File list: {response.status_code}")
        data = response.json()
        print(f"  Found {data.get('uploaded_files_count', 0)} files")
        return True, data
    except Exception as e:
        print(f"✗ File list failed: {e}")
        return False, None

def test_charts(file_id):
    """Test chart generation"""
    try:
        response = requests.get(f"{BASE_URL}/api/charts/{file_id}")
        print(f"✓ Chart generation: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Generated {len(data.get('charts', []))} charts")
            print(f"  Method: {data.get('metadata', {}).get('generation_method', 'unknown')}")
            return True, data
        else:
            print(f"  Error: {response.text}")
            return False, None
    except Exception as e:
        print(f"✗ Chart generation failed: {e}")
        return False, None

def test_dashboard_requirements(file_id):
    """Test dashboard requirements analysis"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/dashboard/analyze-requirements",
            data={"file_id": file_id}
        )
        print(f"✓ Dashboard requirements: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Analysis complete: {data.get('success', False)}")
            return True, data
        else:
            print(f"  Error: {response.text}")
            return False, None
    except Exception as e:
        print(f"✗ Dashboard requirements failed: {e}")
        return False, None

def test_langgraph_dashboard(file_id):
    """Test LangGraph dashboard generation"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/langgraph/dashboard/generate",
            data={
                "file_id": file_id,
                "dashboard_type": "exploratory",
                "user_context": "test dashboard",
                "target_audience": "analyst"
            }
        )
        print(f"✓ LangGraph dashboard: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Success: {data.get('success', False)}")
            print(f"  Charts: {data.get('charts_generated', 0)}")
            print(f"  Insights: {len(data.get('insights', []))}")
            return True, data
        else:
            print(f"  Error: {response.text}")
            return False, None
    except Exception as e:
        print(f"✗ LangGraph dashboard failed: {e}")
        return False, None

def main():
    print("=" * 60)
    print("AUTOMATED EDA API TEST SUITE")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n[1] Testing health endpoint...")
    if not test_health():
        print("\n❌ Server is not running or not responding!")
        print("Please start the server with: python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    # Test 2: File list
    print("\n[2] Testing file list...")
    success, file_data = test_file_list()
    if not success or not file_data:
        print("\n❌ Cannot list files!")
        return
    
    # Get first available file
    uploaded_files = file_data.get('uploaded_files', {})
    if not uploaded_files:
        print("\n⚠ No files uploaded. Please upload a CSV file first.")
        return
    
    file_id = list(uploaded_files.keys())[0]
    filename = uploaded_files[file_id]
    print(f"\n📁 Using file: {filename} (ID: {file_id})")
    
    # Test 3: Chart generation
    print("\n[3] Testing chart generation...")
    test_charts(file_id)
    
    # Test 4: Dashboard requirements
    print("\n[4] Testing dashboard requirements analysis...")
    test_dashboard_requirements(file_id)
    
    # Test 5: LangGraph dashboard
    print("\n[5] Testing LangGraph dashboard generation...")
    test_langgraph_dashboard(file_id)
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
