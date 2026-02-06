import pytest
from app.app import app
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timezone


@pytest.fixture
def valid_outlet_payload():
    """Fixture for valid JavaOutletCreate payload"""
    return {
        "name": "Nairobi CBD Outlet",
        "location": "Central Business District",
        "city": "Nairobi",
        "county": "Nairobi",
        "street_address": "Kenyatta Avenue",
        "phone_number": "+254700000001",
        "rating": 4.5,
        "is_open": 1,
        "opening_time": "06:00",
        "closing_time": "20:00",
    }
    
def test_create_java_outlet(valid_outlet_payload):
    """Test creating a new JavaHouse Coffee Kenya Outlet returns HTTP 201 with complete outlet data"""
    created_outlet_response = {
        "id": 1,
        "name": valid_outlet_payload["name"],
        "location": valid_outlet_payload["location"],
        "city": valid_outlet_payload["city"],
        "county": valid_outlet_payload["county"],
        "street_address": valid_outlet_payload["street_address"],
        "phone_number": valid_outlet_payload["phone_number"],
        "rating": valid_outlet_payload["rating"],
        "is_open": valid_outlet_payload["is_open"],
        "opening_time": valid_outlet_payload["opening_time"],
        "closing_time": valid_outlet_payload["closing_time"],
        "last_inspected_at": datetime.now(timezone.utc).isoformat(),
    }
    
    with patch("app.app.run_db_operation", new_callable=AsyncMock) as mock_db:
        mock_db.side_effect = [None, created_outlet_response]
        
        client = TestClient(app)
        response = client.post("/outlets/", json=valid_outlet_payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Nairobi CBD Outlet"
        assert data["city"] == "Nairobi"
        assert data["is_open"] == 1
        assert "last_inspected_at" in data
        assert mock_db.call_count == 2

def test_create_minimal_fields():
    """Test creating outlet with only minimal fields returns HTTP 201"""
    minimal_payload = {
        "name": "Karen Outlet",
        "location": "Karen",
        "city": "Nairobi",
        "county": "Nairobi County",
        "is_open": 1,
    }
    
    created_outlet_response = {
        "id": 2,
        "name": minimal_payload["name"],
        "location": minimal_payload["location"],
        "city": minimal_payload["city"],
        "county": minimal_payload["county"],
        "street_address": None,
        "phone_number": None,
        "rating": None,
        "is_open": minimal_payload["is_open"],
        "opening_time": None,
        "closing_time": None,
        "last_inspected_at": datetime.now(timezone.utc).isoformat(),
    }
    
    with patch("app.app.run_db_operation", new_callable=AsyncMock) as mock_db:
        mock_db.side_effect = [None, created_outlet_response]
        
        client = TestClient(app)
        response = client.post("/outlets/", json=minimal_payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Karen Outlet"
        assert data["location"] == "Karen"
        assert data["city"] == "Nairobi"
        assert data["county"] == "Nairobi County"
        assert data["is_open"] == 1

def test_create_outlet_validation_error_missing_required_field():
    """Test creating outlet with missing required fields returns HTTP 422 validation error"""
    invalid_payload = {
        "name": "Incomplete Outlet",
        # Missing required fields: location, city, county, is_open
    }
    
    client = TestClient(app)
    response = client.post("/outlets/", json=invalid_payload)
    
    assert response.status_code == 422
    data = response.json()    
    assert "detail" in data
    assert len(data["detail"]) > 0

def test_create_outlet_validation_error_invalid_data_type():
    """Test creating outlet with invalid data type for a field returns HTTP 422"""
    invalid_payload = {
        "name": "Test Outlet",
        "location": "Test Location",
        "city": "Nairobi",
        "county": "Nairobi",
        "is_open": "yes",  # Should be an integer not a string
        "rating": "excellent"  # Should be a float not a string
    } 
    
    client = TestClient(app)
    response = client.post("/outlets/", json=invalid_payload)
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    
    error_fields = [error["loc"][1] for error in data["detail"] if "loc" in error]
    
    assert "is_open" in error_fields, "Expected validation error for is_open field"
    assert "rating" in error_fields, "Expected validation error for rating field"

def test_create_outlet_database_error():
    """Test handling when database INSERT operation fails returns HTTP 500"""
    valid_payload = {
        "name": "Test Outlet",
        "location": "Test Location",
        "city": "Nairobi",
        "county": "Nairobi",
        "is_open": 1,
    }
    
    with patch("app.app.run_db_operation", new_callable=AsyncMock) as mock_db:
        mock_db.side_effect = Exception("Database connection failed")
        
        client = TestClient(app)
        response = client.post("/outlets/", json=valid_payload)
        
        assert response.status_code == 500
        data = response.json()
        assert "Error creating a new outlet" in data["detail"]
        assert "Database connection failed" in data["detail"]

def test_create_outlet_retrieve_returns_none():
    """Test handling when SELECT returns None after successful Insert returns HTTP 500"""
    valid_payload = {
        "name": "Test Outlet",
        "location": "Test Location",
        "city": "Nairobi",
        "county": "Nairobi",
        "is_open": 1,
    }
    
    with patch("app.app.run_db_operation", new_callable=AsyncMock) as mock_db:
        mock_db.side_effect = [None, None]
        
        client = TestClient(app)
        response = client.post("/outlets/", json=valid_payload)
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Failed to retrieve created outlet" in data["detail"]

def test_create_outlet_pydantic_validation_error():
    """Test handling when response doesn't match JavaOutlet schema returns HTTP 500"""
    valid_payload = {
        "name": "Test Outlet",
        "location": "Test Location",
        "city": "Nairobi",
        "county": "Nairobi",
        "is_open": 1,
    }
    
    invalid_response = {
        "id": 1,
        "name": "Karen Outlet",
        # Other required fields missing like location, city, county, is_open
    }            
    
    with patch("app.app.run_db_operation", new_callable=AsyncMock) as mock_db:
        mock_db.side_effect = [None, invalid_response]
        
        client = TestClient(app)
        response = client.post("/outlets/", json=valid_payload)
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data

def test_create_outlet_with_special_characters():
    """Test creating with special characters in fields returns HTTP 201"""
    payload = {
        "name": "Java House Café & Restaurant",
        "location": "Kiambu Road, Nairobi (CBD)",
        "city": "Nairobi",
        "county": "Nairobi",
        "street_address": "P.O. Box 123-00100",
        "is_open": 1,
    } 
    
    created_outlet_response = {
        "id": 3,
        "name": payload["name"],
        "location": payload["location"],
        "city": payload["city"],
        "county": payload["county"],
        "street_address": payload["street_address"],
        "phone_number": None,
        "rating": None,
        "is_open": payload["is_open"],
        "opening_time": None,
        "closing_time": None,
        "last_inspected_at": datetime.now(timezone.utc).isoformat(),
    }
    
    with patch("app.app.run_db_operation", new_callable=AsyncMock) as mock_db:
        mock_db.side_effect = [None, created_outlet_response]
        
        client = TestClient(app)
        response = client.post("/outlets/", json=payload) 
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Java House Café & Restaurant" 

def test_create_outlet_with_optional_fields():
    """Test creating outlet with all optional fields returns HTTP 201""" 
    full_payload = {
        "name": "Sarit Centre Mall Outlet",
        "location": "Westlands",
        "city": "Nairobi",
        "county": "Nairobi",
        "street_address": "Westlands Road, Plot 123",
        "phone_number": "+254700000001",
        "rating": 4.8,
        "is_open": 1,
        "opening_time": "05:30",
        "closing_time": "22:00",
    }
    
    created_outlet_response = {
        "id": 4,
        "name": full_payload["name"],
        "location": full_payload["location"],
        "city": full_payload["city"],
        "county": full_payload["county"],
        "street_address": full_payload["street_address"],
        "phone_number": full_payload["phone_number"],
        "rating": full_payload["rating"],
        "is_open": full_payload["is_open"],
        "opening_time": full_payload["opening_time"],
        "closing_time": full_payload["closing_time"],
        "last_inspected_at": datetime.now(timezone.utc).isoformat(),
    }
    
    with patch("app.app.run_db_operation", new_callable=AsyncMock) as mock_db:
        mock_db.side_effect = [None, created_outlet_response]
        
        client = TestClient(app)
        response = client.post("/outlets/", json=full_payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Sarit Centre Mall Outlet"
        assert data["location"] == "Westlands"
        assert data["city"] == "Nairobi"
        assert data["street_address"] == "Westlands Road, Plot 123"
        assert data["phone_number"] == "+254700000001"
        assert float(data["rating"]) == 4.8
        assert data["is_open"] == 1    
        assert data["opening_time"] == "05:30"
        assert data["closing_time"] == "22:00"

def test_create_outlet_is_open_zero():
    """Test creating outlet with is_open set to 0 (Closed) returns HTTP 201"""
    payload = {
        "name": "Closed Outlet",
        "location": "Test Location",
        "city": "Nairobi",
        "county": "Nairobi",
        "is_open": 0,
    }
    
    created_outlet_response = {
        "id": 5,
        "name": payload["name"],
        "location": payload["location"],
        "city": payload["city"],
        "county": payload["county"],
        "street_address": None,
        "phone_number": None,
        "rating": None,
        "is_open": payload["is_open"],
        "opening_time": None,
        "closing_time": None,
        "last_inspected_at": datetime.now(timezone.utc).isoformat(),
    }
    
    with patch("app.app.run_db_operation", new_callable=AsyncMock) as mock_db:
        mock_db.side_effect = [None, created_outlet_response]
        
        client = TestClient(app)
        response = client.post("/outlets/", json=payload)        
        
        assert response.status_code == 201
        data = response.json()
        assert data["is_open"] == 0

def test_create_outlet_with_high_rating():
    """Test creating outlet with maximum rating (5.0) returns HTTP 201"""
    payload = {
        "name": "Top Rated Outlet",
        "location": "Premium Location",
        "city": "Nairobi",
        "county": "Nairobi",
        "is_open": 1,
        "rating": 5.0,
    }
    
    created_outlet_response = {
        "id": 6,
        "name": payload["name"],
        "location": payload["location"],
        "city": payload["city"],
        "county": payload["county"],
        "street_address": None,
        "phone_number": None,
        "rating": payload["rating"],
        "is_open": payload["is_open"],
        "opening_time": None,
        "closing_time": None,
        "last_inspected_at": datetime.now(timezone.utc).isoformat(),
    }
    
    with patch("app.app.run_db_operation", new_callable=AsyncMock) as mock_db:
        mock_db.side_effect = [None, created_outlet_response]
        
        client = TestClient(app)
        response = client.post("/outlets/", json=payload)
        
        assert response.status_code == 201        
        data = response.json()
        assert float(data["rating"]) == 5.0
