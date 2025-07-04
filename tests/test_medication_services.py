import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import base64
import json
from datetime import datetime, timedelta

from src.services.vision import VisionService, PillFeatures
from src.services.medication_db import MedicationDatabaseService
from src.services.google_vision_client import GoogleVisionClient
from src.services.rxnorm_client import RxNormClient
from src.models.medication import (
    Medication, MedicationDetails, DrugInteraction, FoodInteraction
)


class TestVisionService:
    """Test vision service for medication identification"""
    
    @pytest.fixture
    def vision_service(self):
        """Create vision service instance"""
        return VisionService(api_key=None)  # Test without API key
    
    @pytest.fixture
    def sample_image_data(self):
        """Create sample base64 image data"""
        # Create a simple 100x100 white image
        from PIL import Image
        import io
        
        img = Image.new('RGB', (100, 100), color='white')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        image_bytes = buffer.getvalue()
        return base64.b64encode(image_bytes).decode('utf-8')
    
    @pytest.mark.asyncio
    async def test_analyze_medication_image_local(self, vision_service, sample_image_data):
        """Test analyzing medication image with local processing"""
        features = await vision_service.analyze_medication_image(sample_image_data)
        
        assert isinstance(features, PillFeatures)
        assert features.shape in ["round", "oval", "oblong", "capsule", "unknown"]
        assert features.color in ["white", "black", "gray", "unknown", "blue", "red", "green", "yellow", "orange", "purple", "pink", "brown"]
        assert features.confidence == 0.7  # Local processing confidence
    
    @pytest.mark.asyncio
    async def test_analyze_medication_image_with_google_vision(self, sample_image_data):
        """Test analyzing medication image with Google Vision API"""
        with patch('src.services.vision.google_vision_client') as mock_client:
            # Mock Google Vision responses
            mock_client.client = Mock()
            mock_client.extract_text = AsyncMock(return_value=["L484", "500MG"])
            mock_client.detect_colors = AsyncMock(return_value=[
                {"name": "white", "score": 0.9}
            ])
            
            vision_service = VisionService(api_key="test_key")
            vision_service.use_google_vision = True
            
            features = await vision_service.analyze_medication_image(sample_image_data)
            
            assert features.imprint == "L484"
            assert features.color == "white"
            assert features.confidence == 0.9  # Google Vision confidence
            
            mock_client.extract_text.assert_called_once()
            mock_client.detect_colors.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_detect_shape(self, vision_service):
        """Test shape detection"""
        from PIL import Image
        
        # Test round shape (square image)
        img = Image.new('RGB', (100, 100), color='white')
        shape = await vision_service._detect_shape(img)
        assert shape == "round"
        
        # Test oval shape (rectangular image)
        img = Image.new('RGB', (150, 100), color='white')
        shape = await vision_service._detect_shape(img)
        assert shape in ["oval", "oblong"]
    
    @pytest.mark.asyncio
    async def test_detect_color(self, vision_service):
        """Test color detection"""
        from PIL import Image
        
        # Test white color
        img = Image.new('RGB', (100, 100), color='white')
        color = await vision_service._detect_color(img)
        assert color == "white"
        
        # Test blue color
        img = Image.new('RGB', (100, 100), color='blue')
        color = await vision_service._detect_color(img)
        assert color == "blue"
    
    def test_validate_image(self, vision_service, sample_image_data):
        """Test image validation"""
        # Valid image
        is_valid, error = vision_service.validate_image(sample_image_data)
        assert is_valid is True
        assert error is None
        
        # Invalid base64
        is_valid, error = vision_service.validate_image("invalid_base64")
        assert is_valid is False
        assert "Invalid image data" in error


class TestMedicationDatabaseService:
    """Test medication database service"""
    
    @pytest.fixture
    def medication_db(self):
        """Create medication database service instance"""
        service = MedicationDatabaseService()
        service.use_real_apis = False  # Use mock data for tests
        return service
    
    @pytest.mark.asyncio
    async def test_identify_by_imprint_mock(self, medication_db):
        """Test identifying medication by imprint using mock data"""
        # Test with known imprint
        results = await medication_db.identify_by_imprint("L484", "oval", "white")
        
        assert len(results) == 1
        assert results[0].name == "Acetaminophen 500 mg"
        assert results[0].imprint == "L484"
        assert results[0].shape == "oval"
        assert results[0].color == "white"
    
    @pytest.mark.asyncio
    async def test_identify_by_imprint_with_api(self):
        """Test identifying medication by imprint using real API"""
        with patch('src.services.medication_db.rxnorm_client') as mock_client:
            # Mock RxImage API response
            mock_client.search_by_imprint = AsyncMock(return_value=[
                {
                    "name": "Acetaminophen 500 mg",
                    "rxcui": "198440",
                    "ndc": "49035-484-01",
                    "shape": "OVAL",
                    "color": ["WHITE"],
                    "imprint": "L484"
                }
            ])
            
            medication_db = MedicationDatabaseService()
            medication_db.use_real_apis = True
            
            async with mock_client:
                results = await medication_db.identify_by_imprint("L484", "oval", "white")
            
            assert len(results) == 1
            assert results[0].medication_id == "198440"
            assert results[0].name == "Acetaminophen 500 mg"
    
    @pytest.mark.asyncio
    async def test_get_medication_details_mock(self, medication_db):
        """Test getting medication details using mock data"""
        details = await medication_db.get_medication_details("med_001")
        
        assert details is not None
        assert details.name == "Acetaminophen 500 mg"
        assert details.generic_name == "acetaminophen"
        assert "Tylenol" in details.brand_names
        assert len(details.warnings) > 0
        assert len(details.side_effects["common"]) > 0
    
    @pytest.mark.asyncio
    async def test_search_by_name(self, medication_db):
        """Test searching medications by name"""
        # Search by generic name
        results = await medication_db.search_by_name("acetaminophen")
        assert len(results) >= 1
        assert any("acetaminophen" in r.generic_name.lower() for r in results)
        
        # Search by brand name
        results = await medication_db.search_by_name("tylenol")
        assert len(results) >= 1
        assert any("Tylenol" in r.brand_names for r in results)
    
    @pytest.mark.asyncio
    async def test_check_interactions(self, medication_db):
        """Test checking drug interactions"""
        interactions = await medication_db.check_interactions([
            "warfarin", "acetaminophen"
        ])
        
        assert len(interactions) > 0
        key = list(interactions.keys())[0]
        assert interactions[key][0].severity == "moderate"
        assert "bleeding" in interactions[key][0].description.lower()
    
    @pytest.mark.asyncio
    async def test_get_food_interactions(self, medication_db):
        """Test getting food interactions"""
        # Test warfarin food interactions
        interactions = await medication_db.get_food_interactions("warfarin")
        assert len(interactions) > 0
        assert any("Vitamin K" in i.food_item for i in interactions)
        
        # Test medication with no interactions
        interactions = await medication_db.get_food_interactions("unknown_med")
        assert len(interactions) == 0
    
    @pytest.mark.asyncio
    async def test_validate_dosage(self, medication_db):
        """Test dosage validation"""
        # Valid dosage
        result = await medication_db.validate_dosage("acetaminophen", "500mg")
        assert result["valid"] is True
        assert result["max_daily"] == 4000
        
        # Excessive dosage
        result = await medication_db.validate_dosage("acetaminophen", "2000mg")
        assert result["valid"] is False
        assert any("Maximum single dose" in w for w in result["warnings"] if w)
    
    def test_extract_strength(self, medication_db):
        """Test strength extraction from medication name"""
        assert medication_db._extract_strength("Acetaminophen 500 mg") == "500 mg"
        assert medication_db._extract_strength("Amoxicillin 250mg") == "250 mg"
        assert medication_db._extract_strength("Insulin 100 units/ml") == "100 units"
        assert medication_db._extract_strength("No strength") == ""


class TestRxNormClient:
    """Test RxNorm API client"""
    
    @pytest.fixture
    def rxnorm_client_instance(self):
        """Create RxNorm client instance"""
        return RxNormClient()
    
    @pytest.mark.asyncio
    async def test_search_by_imprint(self, rxnorm_client_instance):
        """Test searching RxImage API by imprint"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock API response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "nlmRxImages": [{
                    "name": "Acetaminophen 500 mg",
                    "rxcui": "198440",
                    "ndc11": "49035-484-01",
                    "shape": "OVAL",
                    "colors": ["WHITE"],
                    "imprint": "L484",
                    "size": 19
                }]
            })
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with rxnorm_client_instance:
                results = await rxnorm_client_instance.search_by_imprint(
                    "L484", "white", "oval"
                )
            
            assert len(results) == 1
            assert results[0]["rxcui"] == "198440"
            assert results[0]["name"] == "Acetaminophen 500 mg"
    
    @pytest.mark.asyncio
    async def test_get_medication_details(self, rxnorm_client_instance):
        """Test getting medication details from RxNorm"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock API response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "rxcuiStatusHistory": {
                    "attributes": {
                        "name": "Acetaminophen 500 MG Oral Tablet",
                        "rxtermsDoseForm": "Tablet",
                        "route": ["Oral"]
                    }
                }
            })
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with rxnorm_client_instance:
                details = await rxnorm_client_instance.get_medication_details("198440")
            
            assert details is not None
            assert details["name"] == "Acetaminophen 500 MG Oral Tablet"
            assert details["dosageForm"] == "Tablet"
            assert "Oral" in details["route"]
    
    @pytest.mark.asyncio
    async def test_get_fda_label_info(self, rxnorm_client_instance):
        """Test getting FDA label information"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock API response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "results": [{
                    "indications_and_usage": ["For temporary relief of minor aches and pains"],
                    "warnings": ["Liver warning: This product contains acetaminophen"],
                    "adverse_reactions": ["Nausea, vomiting, loss of appetite"],
                    "drug_interactions": ["Warfarin - may increase bleeding risk"]
                }]
            })
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with rxnorm_client_instance:
                info = await rxnorm_client_instance.get_fda_label_info("198440")
            
            assert info is not None
            assert len(info["indications"]) > 0
            assert len(info["warnings"]) > 0
    
    def test_normalize_color(self, rxnorm_client_instance):
        """Test color normalization"""
        assert rxnorm_client_instance._normalize_color("white") == "WHITE"
        assert rxnorm_client_instance._normalize_color("BLUE") == "BLUE"
        assert rxnorm_client_instance._normalize_color("grey") == "GRAY"
    
    def test_normalize_shape(self, rxnorm_client_instance):
        """Test shape normalization"""
        assert rxnorm_client_instance._normalize_shape("round") == "ROUND"
        assert rxnorm_client_instance._normalize_shape("OVAL") == "OVAL"
        assert rxnorm_client_instance._normalize_shape("capsule") == "CAPSULE"


class TestGoogleVisionClient:
    """Test Google Vision API client"""
    
    @pytest.mark.asyncio
    async def test_extract_text(self):
        """Test text extraction with mocked Google Vision"""
        with patch('src.services.google_vision_client.vision') as mock_vision:
            # Create mock client and response
            mock_client = Mock()
            mock_response = Mock()
            mock_text = Mock()
            mock_text.description = "L484"
            mock_response.text_annotations = [
                Mock(description="L484 500MG"),  # Full text
                Mock(description="L484"),
                Mock(description="500MG")
            ]
            mock_client.text_detection.return_value = mock_response
            
            client = GoogleVisionClient()
            client.client = mock_client
            
            # Sample image data
            image_data = base64.b64encode(b"test_image").decode('utf-8')
            
            texts = await client.extract_text(image_data)
            
            assert "L484" in texts
            mock_client.text_detection.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_detect_colors(self):
        """Test color detection with mocked Google Vision"""
        with patch('src.services.google_vision_client.vision') as mock_vision:
            # Create mock client and response
            mock_client = Mock()
            mock_response = Mock()
            mock_color = Mock()
            mock_color.color.red = 255
            mock_color.color.green = 255
            mock_color.color.blue = 255
            mock_color.score = 0.9
            mock_color.pixel_fraction = 0.8
            
            mock_props = Mock()
            mock_props.dominant_colors.colors = [mock_color]
            mock_response.image_properties_annotation = mock_props
            
            mock_client.image_properties.return_value = mock_response
            
            client = GoogleVisionClient()
            client.client = mock_client
            
            # Sample image data
            image_data = base64.b64encode(b"test_image").decode('utf-8')
            
            colors = await client.detect_colors(image_data)
            
            assert len(colors) == 1
            assert colors[0]["name"] == "white"
            assert colors[0]["score"] == 0.9
    
    def test_filter_pill_imprints(self):
        """Test pill imprint filtering"""
        client = GoogleVisionClient()
        
        texts = ["L484", "TABLET", "500MG", "ACETAMINOPHEN", "123", "THIS IS A VERY LONG TEXT"]
        filtered = client._filter_pill_imprints(texts)
        
        assert "L484" in filtered
        assert "500MG" in filtered
        assert "123" in filtered
        assert "THIS IS A VERY LONG TEXT" not in filtered  # Too long
    
    def test_rgb_to_color_name(self):
        """Test RGB to color name conversion"""
        client = GoogleVisionClient()
        
        assert client._rgb_to_color_name(255, 255, 255) == "white"
        assert client._rgb_to_color_name(0, 0, 0) == "black"
        assert client._rgb_to_color_name(255, 0, 0) == "red"
        assert client._rgb_to_color_name(0, 0, 255) == "blue"
        assert client._rgb_to_color_name(0, 255, 0) == "green"


# Integration test
class TestMedicationIdentificationFlow:
    """Test the complete medication identification flow"""
    
    @pytest.mark.asyncio
    async def test_full_identification_flow(self):
        """Test complete flow from image to medication details"""
        # Mock all external services
        with patch('src.services.vision.google_vision_client') as mock_vision_client, \
             patch('src.services.medication_db.rxnorm_client') as mock_rxnorm:
            
            # Setup vision mocks
            mock_vision_client.client = Mock()
            mock_vision_client.extract_text = AsyncMock(return_value=["L484"])
            mock_vision_client.detect_colors = AsyncMock(return_value=[
                {"name": "white", "score": 0.9}
            ])
            
            # Setup RxNorm mocks
            mock_rxnorm.search_by_imprint = AsyncMock(return_value=[{
                "name": "Acetaminophen 500 mg",
                "rxcui": "198440",
                "shape": "OVAL",
                "color": ["WHITE"],
                "imprint": "L484"
            }])
            
            mock_rxnorm.get_medication_details = AsyncMock(return_value={
                "name": "Acetaminophen 500 MG Oral Tablet",
                "genericName": "acetaminophen",
                "brandNames": ["Tylenol"],
                "dosageForm": "Tablet"
            })
            
            mock_rxnorm.get_fda_label_info = AsyncMock(return_value={
                "warnings": ["Liver warning"],
                "indications": ["Pain relief"],
                "drug_interactions": ["Warfarin interaction"]
            })
            
            mock_rxnorm.build_medication_details = AsyncMock(return_value=MedicationDetails(
                medication_id="198440",
                name="Acetaminophen 500 mg",
                generic_name="acetaminophen",
                brand_names=["Tylenol"],
                shape="oval",
                color="white",
                imprint="L484",
                warnings=["Liver warning"]
            ))
            
            # Create services
            vision_service = VisionService(api_key="test_key")
            vision_service.use_google_vision = True
            
            medication_db = MedicationDatabaseService()
            medication_db.use_real_apis = True
            
            # Sample image
            from PIL import Image
            import io
            img = Image.new('RGB', (100, 100), color='white')
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Step 1: Analyze image
            features = await vision_service.analyze_medication_image(image_data)
            assert features.imprint == "L484"
            assert features.color == "white"
            
            # Step 2: Search for medication
            async with mock_rxnorm:
                medications = await medication_db.identify_by_imprint(
                    features.imprint, features.shape, features.color
                )
            
            assert len(medications) == 1
            assert medications[0].name == "Acetaminophen 500 mg"
            
            # Step 3: Get detailed information
            async with mock_rxnorm:
                details = await medication_db.get_medication_details(
                    medications[0].medication_id
                )
            
            assert details is not None
            assert details.generic_name == "acetaminophen"
            assert "Tylenol" in details.brand_names