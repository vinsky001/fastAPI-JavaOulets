import pytest
from fastapi.testclient import TestClient
from app.app import app
from unittest.mock import patch, AsyncMock, MagicMock
from sqlalchemy import text
from fastapi import HTTPException
from httpx import AsyncClient
import json


@pytest.fixture
def client():
    """Create a test client for the FASTAPI app."""
    return TestClient(app)


@pytest.fixture
def async_client():
    """Create an async test client for the FASTAPI api"""
    return AsyncClient(app=app, base_url="http://test")  


class TestGetOutlet:
    """Test suite for the get_outlet endpoint"""
    
    # Successful get outlet by id
    
    def test_get_outlet_by_basic(self, client):
        """Test successful retrieval of outlet with basic data"""
        with patch("app.app.run_db_operation") as mock_db:
           
            mock_outlet_data = {
                'id': 1,
                'name': 'Downtown Branch',
                'location': 'Nairobi',
                'city': 'Nairobi',
                'county': 'Nairobi County',
                'is_open': True,
                'opening_time': '06:00',
                'closing_time': '22:00',
            }
            mock_db.return_value = mock_outlet_data
            response = client.get("/outlets/1")
            
            assert response.status_code == 200
            assert response.json()["id"] == 1
            assert response.json()['name'] == 'Downtown Branch'  
            assert response.json()['location'] == 'Nairobi'
            assert response.json()['city'] == 'Nairobi'
            assert response.json()['county'] == 'Nairobi County'
            assert response.json()['is_open'] == True
            assert response.json()['opening_time'] == '06:00'
            assert response.json()['closing_time'] == '22:00'
            
            
            
    def test_get_outlet_success_all_fields(self, client):
        """Test successful retrieval of outlet with all fields"""
        with patch("app.app.run_db_operation") as mock_db:
            mock_outlet_data = {
                'id': 5,
                'name': 'Airport Branch',
                'location': 'Jomo Kenyatta International Airport',
                'city': 'Nairobi',
                'county': 'Nairobi County',
                'street_address': 'Terminal 1A, Nairobi',
                'phone_number': '+254722999888',
                'rating': 4.5,
                'is_open': True,
                'opening_time': '06:00',
                'closing_time': '23:00',
                'last_inspected_at': '2024-01-15T10:30:00',
            }
            
            mock_db.return_value = mock_outlet_data
            response = client.get("/outlets/5")  
            
            assert response.status_code == 200
            data = response.json()
            assert data['id'] == 5
            assert data['name'] == 'Airport Branch'
            assert data['location'] == 'Jomo Kenyatta International Airport'  
            assert data['city'] == 'Nairobi'
            assert data['county'] == 'Nairobi County'
            assert data['street_address'] == 'Terminal 1A, Nairobi'
            assert data['phone_number'] == '+254722999888'
            assert data['rating'] == 4.5
            assert data['is_open'] == True
            assert data['opening_time'] == '06:00'
            assert data['closing_time'] == '23:00'
            
            
            
    def test_get_out_different_ids(self, client):
        """Test retrieval of different outlets with different IDs."""
        test_case = [
            (1, 'Downtown'),
            (2, 'Westlands'),
            (10, 'Mombasa'),
            (999, 'Remote Branch')
        ]
        
        for outlet_id, name in test_case:
            with patch("app.app.run_db_operation") as mock_db:
                mock_outlet_data = {
                    'id': outlet_id,
                    'name': name,
                    'location': f'Location {outlet_id}',
                    'city': f'City {outlet_id}',
                    'county': f'County {outlet_id}',
                    'is_open': True,
                }
                
                mock_db.return_value = mock_outlet_data
                response = client.get(f"/outlets/{outlet_id}")  
                
                assert response.status_code == 200
                assert response.json()['id'] == outlet_id
                assert response.json()['name'] == name
                
    # Not found cases            
                
    def test_get_outlet_not_found_nonexistent_id(self, client):
        """Test retrieving an outlet that does not exist"""
        with patch("app.app.run_db_operation") as mock_db:
            mock_db.return_value = None
            
            response = client.get("/outlets/999990")
            
            assert response.status_code == 404  
    
    # Invalid Input cases
    
    def test_get_outlet_invalid_id_string(self, client):
        """Test with non integer id path"""     
        response = client.get("/outlets/abc/")
        assert response.status_code == 422
        
    def test_get_outlet_invalid_id_float(self, client):
        """Test with float ID in path"""
        response = client.get("/outlets/4.4/")
        assert response.status_code == 422
        
    def test_get_outlet_invalid_id_special_chars(self, client):
        """Test with special characters in path"""
        response = client.get("/outlets/1@#$%/")
        assert response.status_code == 422
        
    def test_get_outlet_empty_id(self, client):
        """Test with an empty ID in path"""
        response = client.get("/outlets//")     
        assert response.status_code in [404, 405]
        
    
    # Database Error case handling    
    
    def test_get_outlet_database_connection_error(self, client):
        """Test handling database connection errors"""
        with patch("app.app.run_db_operation") as mock_db:
            mock_db.side_effect = Exception("Database connection Error")
            
            response = client.get("/outlets/1/")
            
            assert response.status_code == 500  
            assert 'Database connection Error' in response.json()['detail'] 
            
    def test_get_outlet_database_query_error(self, client):
        """Test handling database query error"""
        with patch("app.app.run_db_operation") as mock_db:  
            mock_db.side_effect = Exception("SQL syntax error")
            
            response = client.get("/outlets/1/")
            
            assert response.status_code == 500
            assert 'SQL syntax error' in response.json()['detail']
            
    def test_get_outlet_database_timeout(self, client):
        """Test handling database timeout"""
        with patch("app.app.run_db_operation") as mock_db:
            mock_db.side_effect = TimeoutError("Database query Timeout")
            
            response = client.get("/outlets/3/")
            
            assert response.status_code == 500  
            
    def test_get_outlet_database_access_denied(self, client):
        """Test handling database permission errors"""
        with patch("app.app.run_db_operation") as mock_db:
            mock_db.side_effect = Exception("Access denied to table")
            
            response = client.get("/outlets/1/")
            
            assert response.status_code == 500
            assert 'Access denied to table' in response.json()['detail']
            
            
    
    # Data Mapping Cases
    
    def test_get_outlet_data_dict_conversion(self, client):
        """Test proper conversion of database mapping to dict"""
        with patch("app.app.run_db_operation") as mock_db:
            # Simulate RowMapping object with correct field names
            mock_mapping = MagicMock()  
            mock_mapping.__iter__ = lambda self: iter({
                'id': 1,
                'name': 'Test Outlet',
                'location': 'Test Location',
                'city': 'Test City',
                'county': 'Test County',
                'is_open': True,
            }.items())
            mock_db.return_value = mock_mapping
            
            response = client.get("/outlets/1/")
            
            assert response.status_code == 200
            
            
            
    def test_get_outlet_missing_optional_fields(self, client):
        """Test handling when optional fields are missing from database"""
        with patch("app.app.run_db_operation") as mock_db:
            # Only required fields - optional fields omitted
            mock_outlet_data = {
                'id': 1,
                'name': 'Minimal Outlet',
                'location': 'Test Location',
                'city': 'Test City',
                'county': 'Test County',
                'is_open': False,
                # Optional fields intentionally omitted
            }
            mock_db.return_value = mock_outlet_data       
            
            response = client.get("/outlets/1/")
            
            assert response.status_code == 200
            
            
            
    # Concurrency request cases
    
    def test_get_outlet_concurrent_requests(self, client):
        """Test handling of concurrent request for same outlet"""
        with patch("app.app.run_db_operation") as mock_db:
            mock_outlet_data = {
                'id': 1,
                'name': 'Popular Outlet',
                'location': 'Nairobi',
                'city': 'Nairobi',
                'county': 'Nairobi County',
                'is_open': True,
            }
            mock_db.return_value = mock_outlet_data
            # Simulate multiple concurrent requests
            responses = [client.get("/outlets/1/") for _ in range(5)] 
            
            for response in responses:
                assert response.status_code == 200                            
                assert response.json()['id'] == 1
                
                   
    # Response format cases
    
    def test_get_outlet_response_is_json(self, client):
        """Testing that the response is a valid json object"""
        with patch("app.app.run_db_operation") as mock_db:
            mock_outlet_data = {
                'id': 1,
                'name': 'Test Outlet',
                'location': 'Test Location',
                'city': 'Test City',
                'county': 'Test County',
                'is_open': True,
            }
            mock_db.return_value = mock_outlet_data
            
            response = client.get("/outlets/1/")
            
            assert response.status_code == 200
            # Should be a valid json and parsable
            data = response.json()
            assert isinstance(data, dict)  
            
    
    def test_get_outlet_response_content_type(self, client):
        """Test that response has the correct content type"""
        with patch("app.app.run_db_operation") as mock_db:
            mock_outlet_data = {
                'id': 1,
                'name': 'Test Outlet',
                'location': 'Test Location',
                'city': 'Test City',
                'county': 'Test County',
                'is_open': True,
            }
            mock_db.return_value = mock_outlet_data
            
            response = client.get("/outlets/1/")
            
            assert 'application/json' in response.headers.get('content-type', '')  
            
    
    def test_get_outlet_response_includes_all_fields(self, client):
        """Test that response includes all expected fields."""
        with patch("app.app.run_db_operation") as mock_db:
            mock_outlet_data = {
                'id': 1,
                'name': 'Test Outlet',
                'location': 'Test Location',
                'city': 'Test City',
                'county': 'Test County',
                'street_address': '123 Test St',
                'phone_number': '+254712345678',
                'rating': 4.0,
                'is_open': True,
                'opening_time': '08:00',
                'closing_time': '18:00',
            } 
            mock_db.return_value = mock_outlet_data
            
            response = client.get("/outlets/1/")
            
            assert response.status_code == 200
            data = response.json()
            for key in mock_outlet_data.keys():
                assert key in data
                
    
    # Edge cases
    
    def test_get_outlet_very_large_id(self, client):
        """Test with very large integer ID."""
        with patch('app.app.run_db_operation') as mock_db:
            large_id = 2**31 - 1
            mock_outlet_data = {
                'id': large_id,
                'name': 'Large ID Outlet',
                'location': 'Test Location',
                'city': 'Test City',
                'county': 'Test County',
                'is_open': True,
            }
            mock_db.return_value = mock_outlet_data
            
            response = client.get(f"/outlets/{large_id}/")
            
            assert response.status_code == 200
            assert response.json()['id'] == large_id
            
    def test_get_outlet_special_characters_in_response(self, client): 
        """Test handling of special characters in outlet data"""
        with patch("app.app.run_db_operation") as mock_db:
            mock_outlet_data = {
                'id': 1,
                'name': 'Café Java House™',
                'location': 'Nairobi, Kenya 🇰🇪',
                'city': 'Nairobi',
                'county': 'Nairobi County',
                'street_address': '123 "Main" Street & Co.',
                'is_open': True,
            } 
            mock_db.return_value = mock_outlet_data
            
            response = client.get("/outlets/1/")  
            
            assert response.status_code == 200 
            data = response.json()
            assert 'Café' in data['name']
            assert '🇰🇪' in data['location']
            
    def test_get_outlet_minimum_length_fields(self, client):
        """Test handling of fields at minimum length constraints"""
        with patch("app.app.run_db_operation") as mock_db:
            # Note: name, location, city, county have min_length=2
            mock_outlet_data = {
                'id': 1,
                'name': 'AB',  # 
                'location': 'CD',  
                'city': 'EF',  
                'county': 'GH',  
                'is_open': True,
            }
            mock_db.return_value = mock_outlet_data
            
            response = client.get("/outlets/1/")  
            
            assert response.status_code == 200


    # HTTP Method Cases
    
    def test_get_outlet_post_method_not_allowed(self, client):
        """Test that POST method is not allowed."""
        response = client.post("/outlets/1/")
        
        assert response.status_code == 405  
    
    def test_get_outlet_put_method_not_allowed(self, client):
        """Test that PUT method is not allowed."""
        response = client.put("/outlets/1/")
        
        assert response.status_code == 405
    
    def test_get_outlet_delete_method_not_allowed(self, client):
        """Test that DELETE method is not allowed."""
        response = client.delete("/outlets/1/")
        
        assert response.status_code == 405
    
    def test_get_outlet_patch_method_not_allowed(self, client):
        """Test that PATCH method is not allowed."""
        response = client.patch("/outlets/1/")
        
        assert response.status_code == 405  
        
        
    # Integration-like Cases
    
    def test_get_outlet_db_operation_called_correctly(self, client):
        """Test that run_db_operation is called with correct parameters."""
        with patch('app.app.run_db_operation') as mock_db:
            mock_outlet_data = {
                'id': 42,
                'name': 'Test Outlet',
                'location': 'Test Location',
                'city': 'Test City',
                'county': 'Test County',
                'is_open': True,
            }
            mock_db.return_value = mock_outlet_data
            
            response = client.get("/outlets/42/")
            
            # Verify the function was called
            assert mock_db.called
            assert response.status_code == 200
    
    def test_get_outlet_exception_not_caught_as_500(self, client):
        """Test that HTTPException is raised correctly without being caught as 500."""
        with patch('app.app.run_db_operation') as mock_db:
            mock_db.return_value = None
            
            response = client.get("/outlets/1/")
            
            # Should be 404, not caught and converted to 500
            assert response.status_code == 404
            assert response.json()['detail'] == 'Outlet not found'


class TestGetOutletIntegration:
    """Integration tests for get_outlet endpoint."""
    
    def test_get_outlet_full_workflow(self, client):
        """Test complete workflow of getting an outlet."""
        with patch('app.app.run_db_operation') as mock_db:
            # Setup
            outlet_id = 1
            expected_data = {
                'id': outlet_id,
                'name': 'Main Branch',
                'location': 'Nairobi',
                'city': 'Nairobi',
                'county': 'Nairobi County',
                'street_address': '123 Main St',
                'phone_number': '+254712345678',
                'is_open': True,
                'opening_time': '06:00',
                'closing_time': '23:00',
            }
            mock_db.return_value = expected_data
            
            # Execute
            response = client.get(f"/outlets/{outlet_id}/")
            
            # Verify
            assert response.status_code == 200
            data = response.json()
            assert data['id'] == outlet_id
            assert data['name'] == expected_data['name']
            assert data['location'] == expected_data['location']
            assert data['city'] == expected_data['city']
            assert data['county'] == expected_data['county']
            assert data['is_open'] == expected_data['is_open']