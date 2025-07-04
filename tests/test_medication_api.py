import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import base64
import json
from datetime import datetime

from src.api.main import app
from src.models.medication import (
    Medication, MedicationDetails, DrugInteraction, 
    FoodInteraction, UserMedication
)
from src.services.vision import PillFeatures


class TestMedicationAPI:
    """Test medication-related API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_image_data(self):
        """Create sample base64 image data"""
        from PIL import Image
        import io
        
        img = Image.new('RGB', (100, 100), color='white')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        image_bytes = buffer.getvalue()
        return base64.b64encode(image_bytes).decode('utf-8')
    
    @pytest.fixture
    def mock_medication_response(self):
        """Create mock medication response"""
        return Medication(
            medication_id="198440",
            name="Acetaminophen 500 mg",
            generic_name="acetaminophen",
            brand_names=["Tylenol"],
            shape="oval",
            color="white",
            imprint="L484",
            dosage_forms=["tablet"],
            strength="500 mg",
            manufacturer="Kroger Company"
        )
    
    @pytest.fixture
    def mock_medication_details(self):
        """Create mock medication details"""
        return MedicationDetails(
            medication_id="198440",
            name="Acetaminophen 500 mg",
            generic_name="acetaminophen",
            brand_names=["Tylenol"],
            shape="oval",
            color="white",
            imprint="L484",
            dosage_forms=["tablet"],
            strength="500 mg",
            manufacturer="Kroger Company",
            indications=["Pain relief", "Fever reduction"],
            contraindications=["Severe liver disease"],
            side_effects={
                "common": ["Nausea"],
                "rare": ["Skin rash"],
                "severe": ["Liver damage"]
            },
            warnings=["Do not exceed 4000mg per day"],
            drug_interactions=[
                DrugInteraction(
                    drug_name="Warfarin",
                    severity="moderate",
                    description="May increase bleeding risk",
                    management="Monitor INR"
                )
            ],
            food_interactions=[],
            storage_instructions="Store at room temperature"
        )
    
    def test_identify_medication_by_photo(self, client, sample_image_data, mock_medication_response):
        """Test POST /medications/identify endpoint"""
        with patch('src.services.vision.vision_service') as mock_vision, \
             patch('src.services.medication_db.medication_db_service') as mock_db:
            
            # Mock vision service
            mock_features = PillFeatures(
                shape="oval",
                color="white",
                imprint="L484",
                confidence=0.9
            )
            mock_vision.analyze_medication_image = AsyncMock(return_value=mock_features)
            
            # Mock medication database
            mock_db.identify_by_imprint = AsyncMock(return_value=[mock_medication_response])
            
            # Make request
            response = client.post(
                "/medications/identify",
                json={"image": sample_image_data}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "success"
            assert len(data["medications"]) == 1
            assert data["medications"][0]["name"] == "Acetaminophen 500 mg"
            assert data["medications"][0]["imprint"] == "L484"
            assert data["confidence"] == 0.9
    
    def test_identify_medication_no_results(self, client, sample_image_data):
        """Test medication identification with no results"""
        with patch('src.services.vision.vision_service') as mock_vision, \
             patch('src.services.medication_db.medication_db_service') as mock_db:
            
            # Mock vision service
            mock_features = PillFeatures(
                shape="unknown",
                color="unknown",
                imprint=None,
                confidence=0.3
            )
            mock_vision.analyze_medication_image = AsyncMock(return_value=mock_features)
            
            # Mock medication database - no results
            mock_db.identify_by_imprint = AsyncMock(return_value=[])
            
            # Make request
            response = client.post(
                "/medications/identify",
                json={"image": sample_image_data}
            )
            
            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "No medications found matching the image"
    
    def test_get_medication_details(self, client, mock_medication_details):
        """Test GET /medications/{medication_id} endpoint"""
        with patch('src.services.medication_db.medication_db_service') as mock_db:
            # Mock database response
            mock_db.get_medication_details = AsyncMock(return_value=mock_medication_details)
            
            # Make request
            response = client.get("/medications/198440")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["name"] == "Acetaminophen 500 mg"
            assert data["generic_name"] == "acetaminophen"
            assert "Tylenol" in data["brand_names"]
            assert len(data["warnings"]) > 0
            assert len(data["drug_interactions"]) > 0
    
    def test_get_medication_details_not_found(self, client):
        """Test getting details for non-existent medication"""
        with patch('src.services.medication_db.medication_db_service') as mock_db:
            # Mock database response - not found
            mock_db.get_medication_details = AsyncMock(return_value=None)
            
            # Make request
            response = client.get("/medications/999999")
            
            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Medication not found"
    
    def test_search_medications(self, client, mock_medication_response):
        """Test GET /medications/search endpoint"""
        with patch('src.services.medication_db.medication_db_service') as mock_db:
            # Mock database response
            mock_db.search_by_name = AsyncMock(return_value=[mock_medication_response])
            
            # Make request
            response = client.get("/medications/search?name=tylenol")
            
            assert response.status_code == 200
            data = response.json()
            
            assert len(data) == 1
            assert data[0]["name"] == "Acetaminophen 500 mg"
            assert "Tylenol" in data[0]["brand_names"]
    
    def test_add_user_medication(self, client):
        """Test POST /medications/user endpoint"""
        with patch('src.utils.database.get_mongo_collection') as mock_get_collection:
            # Mock MongoDB collection
            mock_collection = Mock()
            mock_collection.insert_one = AsyncMock(return_value=Mock(inserted_id="med_user_001"))
            mock_get_collection.return_value = mock_collection
            
            # Request data
            medication_data = {
                "user_id": "user123",
                "medication_id": "198440",
                "name": "Acetaminophen 500 mg",
                "dosage": "500mg",
                "frequency": "Every 6 hours as needed",
                "purpose": "Pain relief"
            }
            
            # Make request
            response = client.post("/medications/user", json=medication_data)
            
            assert response.status_code == 201
            data = response.json()
            
            assert data["status"] == "success"
            assert "id" in data
            
            # Verify MongoDB call
            mock_collection.insert_one.assert_called_once()
            call_args = mock_collection.insert_one.call_args[0][0]
            assert call_args["user_id"] == "user123"
            assert call_args["medication_id"] == "198440"
    
    def test_get_user_medications(self, client):
        """Test GET /medications/user/{user_id} endpoint"""
        with patch('src.utils.database.get_mongo_collection') as mock_get_collection:
            # Mock MongoDB collection
            mock_collection = Mock()
            mock_cursor = Mock()
            mock_cursor.to_list = AsyncMock(return_value=[
                {
                    "_id": "med_user_001",
                    "user_id": "user123",
                    "medication_id": "198440",
                    "name": "Acetaminophen 500 mg",
                    "dosage": "500mg",
                    "frequency": "Every 6 hours",
                    "active": True,
                    "created_at": datetime.utcnow()
                }
            ])
            mock_collection.find.return_value = mock_cursor
            mock_get_collection.return_value = mock_collection
            
            # Make request
            response = client.get("/medications/user/user123")
            
            assert response.status_code == 200
            data = response.json()
            
            assert len(data) == 1
            assert data[0]["name"] == "Acetaminophen 500 mg"
            assert data[0]["active"] is True
    
    def test_check_interactions(self, client):
        """Test POST /medications/interactions endpoint"""
        with patch('src.services.medication_db.medication_db_service') as mock_db:
            # Mock interaction response
            mock_interactions = {
                "Warfarin + Acetaminophen": [
                    DrugInteraction(
                        drug_name="Warfarin + Acetaminophen",
                        severity="moderate",
                        description="May increase bleeding risk",
                        management="Monitor INR"
                    )
                ]
            }
            mock_db.check_interactions = AsyncMock(return_value=mock_interactions)
            
            # Request data
            interaction_data = {
                "medications": ["warfarin", "acetaminophen"]
            }
            
            # Make request
            response = client.post("/medications/interactions", json=interaction_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert "Warfarin + Acetaminophen" in data
            assert data["Warfarin + Acetaminophen"][0]["severity"] == "moderate"
    
    def test_validate_dosage(self, client):
        """Test POST /medications/validate-dosage endpoint"""
        with patch('src.services.medication_db.medication_db_service') as mock_db:
            # Mock validation response
            mock_validation = {
                "valid": True,
                "warnings": ["Usual dose is 500mg"],
                "max_daily": 4000
            }
            mock_db.validate_dosage = AsyncMock(return_value=mock_validation)
            
            # Request data
            dosage_data = {
                "medication_name": "acetaminophen",
                "dosage": "1000mg"
            }
            
            # Make request
            response = client.post("/medications/validate-dosage", json=dosage_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["valid"] is True
            assert data["max_daily"] == 4000
            assert len(data["warnings"]) > 0
    
    def test_update_user_medication(self, client):
        """Test PUT /medications/user/{medication_user_id} endpoint"""
        with patch('src.utils.database.get_mongo_collection') as mock_get_collection:
            # Mock MongoDB collection
            mock_collection = Mock()
            mock_collection.update_one = AsyncMock(return_value=Mock(modified_count=1))
            mock_get_collection.return_value = mock_collection
            
            # Update data
            update_data = {
                "frequency": "Every 8 hours",
                "notes": "Take with food"
            }
            
            # Make request
            response = client.put("/medications/user/med_user_001", json=update_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "success"
            
            # Verify MongoDB call
            mock_collection.update_one.assert_called_once()
    
    def test_delete_user_medication(self, client):
        """Test DELETE /medications/user/{medication_user_id} endpoint"""
        with patch('src.utils.database.get_mongo_collection') as mock_get_collection:
            # Mock MongoDB collection
            mock_collection = Mock()
            mock_collection.update_one = AsyncMock(return_value=Mock(modified_count=1))
            mock_get_collection.return_value = mock_collection
            
            # Make request (soft delete)
            response = client.delete("/medications/user/med_user_001")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "success"
            
            # Verify MongoDB call for soft delete
            mock_collection.update_one.assert_called_once()
            call_args = mock_collection.update_one.call_args[0]
            assert call_args[1]["$set"]["active"] is False
    
    def test_get_medication_history(self, client):
        """Test GET /medications/user/{user_id}/history endpoint"""
        with patch('src.utils.database.get_mongo_collection') as mock_get_collection:
            # Mock MongoDB collection
            mock_collection = Mock()
            mock_cursor = Mock()
            mock_cursor.to_list = AsyncMock(return_value=[
                {
                    "_id": "med_user_001",
                    "user_id": "user123",
                    "medication_id": "198440",
                    "name": "Acetaminophen 500 mg",
                    "start_date": datetime.utcnow(),
                    "end_date": datetime.utcnow(),
                    "active": False
                }
            ])
            mock_collection.find.return_value = mock_cursor
            mock_get_collection.return_value = mock_collection
            
            # Make request
            response = client.get("/medications/user/user123/history")
            
            assert response.status_code == 200
            data = response.json()
            
            assert len(data) == 1
            assert data[0]["active"] is False


class TestMedicationErrorHandling:
    """Test error handling in medication endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_identify_medication_invalid_image(self, client):
        """Test medication identification with invalid image"""
        response = client.post(
            "/medications/identify",
            json={"image": "invalid_base64_data"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid image" in data["detail"]
    
    def test_identify_medication_missing_image(self, client):
        """Test medication identification without image"""
        response = client.post(
            "/medications/identify",
            json={}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_search_medications_empty_query(self, client):
        """Test searching medications with empty query"""
        response = client.get("/medications/search?name=")
        
        assert response.status_code == 422  # Validation error
    
    def test_add_user_medication_invalid_data(self, client):
        """Test adding user medication with invalid data"""
        response = client.post(
            "/medications/user",
            json={
                "user_id": "user123"
                # Missing required fields
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_check_interactions_single_medication(self, client):
        """Test interaction check with single medication"""
        response = client.post(
            "/medications/interactions",
            json={"medications": ["acetaminophen"]}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "at least 2 medications" in data["detail"].lower()