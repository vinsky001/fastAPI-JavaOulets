import pytest
from app.app import app
from fastapi.testclient import TestClient
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock, MagicMock


def test_list_java_outlets():
    """test listing all JavaHouse Coffee Kenya Outlets"""
    mock_outlets = [
        {
              "id": 1, 
            "name": "Karen Branch",
            "location": "Karen",
            "city": "Nairobi",
            "county": "Nairobi",
            "is_open": 1,
            "street_address": "Karen Road",
            "phone_number": "+254700000001",
            "rating": 4.5,
            "opening_time": "06:00",
            "closing_time": "20:00",
            "last_inspected_at": "2024-01-01"
        },
        {
            "id": 2, 
            "name": "Westlands Branch",
            "location": "Westlands",
            "city": "Nairobi",
            "county": "Nairobi",
            "is_open": 1,
            "street_address": "Westlands Road",
            "phone_number": "+254700000002",
            "rating": 4.7,
            "opening_time": "06:00",
            "closing_time": "20:00",
            "last_inspected_at": "2024-01-01"
        },
    {
            "id": 3, 
            "name": "CBD branch",
            "location": "CBD",
            "city": "Nairobi",
            "county": "Nairobi",
            "is_open": 1,
            "street_address": "CBD Road",
            "phone_number": "+254700000003",
            "rating": 4.6,
            "opening_time": "06:00",
            "closing_time": "20:00",
            "last_inspected_at": "2024-01-01"
        }
    ]
    
    with patch("app.app.run_db_operation", new_callable=AsyncMock) as mock_outlets_operation:
        mock_outlets_operation.return_value = mock_outlets
        
        client = TestClient(app)
        response = client.get("/outlets/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["outlets"]) == 3
        assert data["outlets"][0]["name"] == "Karen Branch"
        assert data["outlets"][1]["name"] == "Westlands Branch"
        assert data["outlets"][2]["name"] == "CBD branch"
        
        

def test_list_java_outlets_empty():
    """test listing all JavaHouse Coffee Kenya Outlets when there are no outlets"""
    with patch("app.app.run_db_operation", new_callable=AsyncMock) as mock_db:
        mock_db.return_value = []
        
        client = TestClient(app)
        response = client.get("/outlets/")
        
        assert response.status_code == 200
        data = response.json()
        assert "outlets" in data
        assert data["outlets"] == []
        assert isinstance(data["outlets"], list)
        
        
def test_java_outlets_db_error():
    """test listing all JavaHouse Coffee Kenya Outlets when there is a DB error"""
    with patch("app.app.run_db_operation", new_callable=AsyncMock) as mock_db:
        mock_db.side_effect = Exception("Database Error")
        
        client = TestClient(app)
        response = client.get("/outlets/")
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str) 
        assert len(data["detail"]) > 0
        
