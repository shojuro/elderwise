import logging
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import aiohttp
import json

from src.models.medication import (
    Medication, MedicationDetails, DrugInteraction, 
    FoodInteraction, UserMedication
)
from src.services.rxnorm_client import rxnorm_client
from src.config.settings import settings

logger = logging.getLogger(__name__)


class MedicationDatabaseService:
    """
    Service for looking up medication information from various sources.
    Integrates with RxImage, RxNorm, and FDA APIs.
    """
    
    def __init__(self):
        self.use_real_apis = bool(settings.rximage_base_url and settings.rxnorm_base_url)
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = timedelta(hours=24)
        
        # Initialize mock database for fallback
        self._init_mock_database()
        
        if self.use_real_apis:
            logger.info("Medication service using real APIs (RxImage, RxNorm, FDA)")
        else:
            logger.info("Medication service using mock data")
    
    def _init_mock_database(self):
        """Initialize mock medication data for testing/fallback"""
        self.mock_medications = {
            "L484": MedicationDetails(
                medication_id="med_001",
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
                contraindications=["Severe liver disease", "Allergy to acetaminophen"],
                side_effects={
                    "common": ["Nausea", "Stomach pain"],
                    "rare": ["Skin rash", "Itching"],
                    "severe": ["Liver damage (with overdose)", "Severe skin reactions"]
                },
                drug_interactions=[
                    DrugInteraction(
                        drug_name="Warfarin",
                        severity="moderate",
                        description="May increase bleeding risk",
                        management="Monitor INR closely"
                    )
                ],
                food_interactions=[],
                warnings=["Do not exceed 4000mg per day", "Avoid alcohol"],
                storage_instructions="Store at room temperature"
            ),
            "TEVA 3109": MedicationDetails(
                medication_id="med_002",
                name="Amoxicillin 500 mg",
                generic_name="amoxicillin",
                brand_names=["Amoxil", "Trimox"],
                shape="capsule",
                color="pink",
                imprint="TEVA 3109",
                dosage_forms=["capsule"],
                strength="500 mg",
                manufacturer="Teva Pharmaceuticals",
                indications=["Bacterial infections"],
                contraindications=["Allergy to penicillin"],
                side_effects={
                    "common": ["Diarrhea", "Nausea", "Vomiting"],
                    "rare": ["Yeast infections", "Dizziness"],
                    "severe": ["Severe allergic reactions", "C. difficile colitis"]
                },
                drug_interactions=[
                    DrugInteraction(
                        drug_name="Methotrexate",
                        severity="major",
                        description="May increase methotrexate toxicity",
                        management="Monitor for toxicity"
                    )
                ],
                food_interactions=[
                    FoodInteraction(
                        food_item="Grapefruit",
                        severity="minor",
                        description="May slightly reduce absorption",
                        timing_instructions="Take 1 hour before or 2 hours after meals"
                    )
                ],
                warnings=["Complete the full course", "May cause allergic reactions"],
                storage_instructions="Store in a cool, dry place"
            ),
            "M367": MedicationDetails(
                medication_id="med_003",
                name="Hydrocodone/Acetaminophen 10mg/325mg",
                generic_name="hydrocodone/acetaminophen",
                brand_names=["Norco", "Vicodin"],
                shape="oblong",
                color="white",
                imprint="M367",
                dosage_forms=["tablet"],
                strength="10mg/325mg",
                manufacturer="Mallinckrodt Pharmaceuticals",
                indications=["Moderate to severe pain"],
                contraindications=["Respiratory depression", "Acute asthma"],
                side_effects={
                    "common": ["Drowsiness", "Dizziness", "Constipation", "Nausea"],
                    "rare": ["Mood changes", "Difficulty urinating"],
                    "severe": ["Respiratory depression", "Addiction", "Overdose"]
                },
                drug_interactions=[
                    DrugInteraction(
                        drug_name="Benzodiazepines",
                        severity="contraindicated",
                        description="Risk of profound sedation, respiratory depression, coma, and death",
                        management="Avoid concurrent use"
                    ),
                    DrugInteraction(
                        drug_name="Alcohol",
                        severity="contraindicated",
                        description="Increased risk of respiratory depression",
                        management="Avoid alcohol completely"
                    )
                ],
                food_interactions=[
                    FoodInteraction(
                        food_item="Grapefruit",
                        severity="moderate",
                        description="May increase drug levels",
                        timing_instructions="Avoid grapefruit products"
                    )
                ],
                warnings=[
                    "High risk of addiction",
                    "May cause respiratory depression",
                    "Do not drive or operate machinery"
                ],
                storage_instructions="Store in locked cabinet"
            )
        }
    
    async def identify_by_imprint(self, imprint: str, shape: Optional[str] = None, 
                                 color: Optional[str] = None) -> List[Medication]:
        """
        Identify medication by imprint code, shape, and color
        
        Args:
            imprint: Text imprinted on the pill
            shape: Shape of the pill
            color: Color of the pill
            
        Returns:
            List of possible medications
        """
        # Check cache first
        cache_key = f"imprint_{imprint}_{shape}_{color}"
        if cache_key in self.cache:
            cache_time, cached_result = self.cache[cache_key]
            if datetime.utcnow() - cache_time < self.cache_ttl:
                return cached_result
        
        results = []
        
        if self.use_real_apis:
            try:
                # Use RxNorm client to search RxImage API
                async with rxnorm_client:
                    rximage_results = await rxnorm_client.search_by_imprint(
                        imprint=imprint,
                        color=color,
                        shape=shape
                    )
                    
                    # Convert RxImage results to Medication objects
                    for rx_result in rximage_results:
                        medication = Medication(
                            medication_id=rx_result.get("rxcui", ""),
                            name=rx_result.get("name", ""),
                            generic_name="",  # Will be filled by get_medication_details
                            brand_names=[],
                            shape=rx_result.get("shape", ""),
                            color=rx_result.get("color", ""),
                            imprint=rx_result.get("imprint", ""),
                            dosage_forms=[],
                            strength=self._extract_strength(rx_result.get("name", "")),
                            manufacturer="",
                            ndc_code=rx_result.get("ndc", ""),
                            rxcui=rx_result.get("rxcui", "")
                        )
                        results.append(medication)
                    
                    logger.info(f"Found {len(results)} medications from RxImage API")
                    
            except Exception as e:
                logger.error(f"Error calling RxImage API: {e}")
                # Fall back to mock data
                results = await self._search_mock_database(imprint, shape, color)
        else:
            # Use mock data
            results = await self._search_mock_database(imprint, shape, color)
        
        # Cache results
        self.cache[cache_key] = (datetime.utcnow(), results)
        
        return results
    
    async def _search_mock_database(self, imprint: str, shape: Optional[str], 
                                   color: Optional[str]) -> List[Medication]:
        """Search mock database for testing"""
        results = []
        
        # Search by imprint in mock database
        if imprint.upper() in self.mock_medications:
            med_details = self.mock_medications[imprint.upper()]
            
            # Check if shape and color match
            shape_match = shape is None or med_details.shape.lower() == shape.lower()
            color_match = color is None or med_details.color.lower() == color.lower()
            
            if shape_match and color_match:
                medication = Medication(
                    medication_id=med_details.medication_id,
                    name=med_details.name,
                    generic_name=med_details.generic_name,
                    brand_names=med_details.brand_names,
                    shape=med_details.shape,
                    color=med_details.color,
                    imprint=med_details.imprint,
                    dosage_forms=med_details.dosage_forms,
                    strength=med_details.strength,
                    manufacturer=med_details.manufacturer
                )
                results.append(medication)
        
        return results
    
    async def get_medication_details(self, medication_id: str) -> Optional[MedicationDetails]:
        """
        Get detailed information about a medication
        
        Args:
            medication_id: Medication identifier (rxcui for real APIs, or mock ID)
            
        Returns:
            Detailed medication information
        """
        # Check cache
        cache_key = f"details_{medication_id}"
        if cache_key in self.cache:
            cache_time, cached_result = self.cache[cache_key]
            if datetime.utcnow() - cache_time < self.cache_ttl:
                return cached_result
        
        result = None
        
        if self.use_real_apis and medication_id.isdigit():  # RxCUI should be numeric
            try:
                # Build complete medication details from APIs
                async with rxnorm_client:
                    # First, get basic info from RxNorm
                    rxnorm_details = await rxnorm_client.get_medication_details(medication_id)
                    
                    if rxnorm_details:
                        # Create a basic rximage result to build from
                        rximage_result = {
                            "rxcui": medication_id,
                            "name": rxnorm_details.get("name", ""),
                            "shape": "",
                            "color": "",
                            "imprint": "",
                            "ndc": ""
                        }
                        
                        # Build complete details
                        result = await rxnorm_client.build_medication_details(rximage_result)
                        
                        logger.info(f"Retrieved medication details from APIs for rxcui: {medication_id}")
                    
            except Exception as e:
                logger.error(f"Error getting medication details from APIs: {e}")
                # Fall back to mock data
                result = self._get_mock_medication_details(medication_id)
        else:
            # Use mock data
            result = self._get_mock_medication_details(medication_id)
        
        # Cache result
        if result:
            self.cache[cache_key] = (datetime.utcnow(), result)
        
        return result
    
    def _get_mock_medication_details(self, medication_id: str) -> Optional[MedicationDetails]:
        """Get medication details from mock database"""
        for med in self.mock_medications.values():
            if med.medication_id == medication_id:
                return med
        return None
    
    async def search_by_name(self, name: str) -> List[Medication]:
        """
        Search medications by name (brand or generic)
        
        Args:
            name: Medication name to search
            
        Returns:
            List of matching medications
        """
        results = []
        name_lower = name.lower()
        
        if self.use_real_apis:
            try:
                # Search RxNorm by name
                async with rxnorm_client:
                    # This would need to be implemented in rxnorm_client
                    # For now, fall back to mock
                    logger.warning("Search by name not yet implemented for real APIs")
                    results = await self._search_mock_by_name(name_lower)
            except Exception as e:
                logger.error(f"Error searching by name: {e}")
                results = await self._search_mock_by_name(name_lower)
        else:
            results = await self._search_mock_by_name(name_lower)
        
        return results
    
    async def _search_mock_by_name(self, name_lower: str) -> List[Medication]:
        """Search mock database by name"""
        results = []
        
        for med_details in self.mock_medications.values():
            if (name_lower in med_details.name.lower() or 
                name_lower in med_details.generic_name.lower() or
                any(name_lower in brand.lower() for brand in med_details.brand_names)):
                
                medication = Medication(
                    medication_id=med_details.medication_id,
                    name=med_details.name,
                    generic_name=med_details.generic_name,
                    brand_names=med_details.brand_names,
                    shape=med_details.shape,
                    color=med_details.color,
                    imprint=med_details.imprint,
                    dosage_forms=med_details.dosage_forms,
                    strength=med_details.strength,
                    manufacturer=med_details.manufacturer
                )
                results.append(medication)
        
        return results
    
    async def check_interactions(self, medication_names: List[str]) -> Dict[str, List[DrugInteraction]]:
        """
        Check for drug-drug interactions between medications
        
        Args:
            medication_names: List of medication names to check
            
        Returns:
            Dictionary of interactions keyed by medication pair
        """
        # For now, use the mock implementation
        # Real API integration would require more complex logic
        interactions = {}
        
        # Mock implementation with some common interactions
        interaction_database = {
            ("warfarin", "acetaminophen"): DrugInteraction(
                drug_name="Warfarin + Acetaminophen",
                severity="moderate",
                description="Increased risk of bleeding",
                management="Monitor INR more frequently"
            ),
            ("methotrexate", "amoxicillin"): DrugInteraction(
                drug_name="Methotrexate + Amoxicillin",
                severity="major",
                description="Increased methotrexate toxicity",
                management="Monitor for signs of toxicity"
            ),
            ("hydrocodone", "alprazolam"): DrugInteraction(
                drug_name="Hydrocodone + Benzodiazepines",
                severity="contraindicated",
                description="Risk of respiratory depression and death",
                management="Avoid concurrent use"
            )
        }
        
        # Check all pairs
        for i in range(len(medication_names)):
            for j in range(i + 1, len(medication_names)):
                med1 = medication_names[i].lower()
                med2 = medication_names[j].lower()
                
                # Check both directions
                key1 = (med1, med2)
                key2 = (med2, med1)
                
                for key in [key1, key2]:
                    if key in interaction_database:
                        interaction_key = f"{medication_names[i]} + {medication_names[j]}"
                        if interaction_key not in interactions:
                            interactions[interaction_key] = []
                        interactions[interaction_key].append(interaction_database[key])
        
        return interactions
    
    async def get_food_interactions(self, medication_name: str) -> List[FoodInteraction]:
        """
        Get food interactions for a medication
        
        Args:
            medication_name: Name of the medication
            
        Returns:
            List of food interactions
        """
        # Mock implementation
        food_interactions = {
            "warfarin": [
                FoodInteraction(
                    food_item="Vitamin K-rich foods",
                    severity="moderate",
                    description="May reduce effectiveness",
                    timing_instructions="Maintain consistent intake"
                ),
                FoodInteraction(
                    food_item="Grapefruit",
                    severity="moderate",
                    description="May increase drug levels",
                    timing_instructions="Avoid grapefruit"
                )
            ],
            "statins": [
                FoodInteraction(
                    food_item="Grapefruit",
                    severity="major",
                    description="Can cause dangerous increase in drug levels",
                    timing_instructions="Avoid grapefruit completely"
                )
            ],
            "antibiotics": [
                FoodInteraction(
                    food_item="Dairy products",
                    severity="minor",
                    description="May reduce absorption",
                    timing_instructions="Take 2 hours before or after dairy"
                )
            ]
        }
        
        name_lower = medication_name.lower()
        
        # Check specific medications
        for med_key, interactions in food_interactions.items():
            if med_key in name_lower:
                return interactions
        
        # Check mock database
        for med in self.mock_medications.values():
            if (name_lower in med.name.lower() or 
                name_lower in med.generic_name.lower()):
                return med.food_interactions
        
        return []
    
    async def validate_dosage(self, medication_name: str, dosage: str) -> Dict[str, Any]:
        """
        Validate if a dosage is within safe ranges
        
        Args:
            medication_name: Name of medication
            dosage: Dosage to validate
            
        Returns:
            Validation result with warnings if applicable
        """
        # Mock implementation with common dosage ranges
        dosage_ranges = {
            "acetaminophen": {
                "max_single": 1000,  # mg
                "max_daily": 4000,   # mg
                "usual_single": 500  # mg
            },
            "ibuprofen": {
                "max_single": 800,
                "max_daily": 3200,
                "usual_single": 400
            }
        }
        
        name_lower = medication_name.lower()
        
        # Extract numeric dosage
        try:
            import re
            dosage_match = re.search(r'(\d+)', dosage)
            if dosage_match:
                dosage_mg = int(dosage_match.group(1))
                
                for med_name, ranges in dosage_ranges.items():
                    if med_name in name_lower:
                        return {
                            "valid": dosage_mg <= ranges["max_single"],
                            "warnings": [
                                f"Maximum single dose is {ranges['max_single']}mg" 
                                if dosage_mg > ranges["max_single"] else None,
                                f"Usual dose is {ranges['usual_single']}mg"
                                if dosage_mg > ranges["usual_single"] else None
                            ],
                            "max_daily": ranges["max_daily"]
                        }
        except:
            pass
        
        return {
            "valid": True,
            "warnings": [],
            "note": "Unable to validate dosage automatically"
        }
    
    def _extract_strength(self, name: str) -> str:
        """Extract strength from medication name"""
        import re
        # Look for patterns like "500 mg", "10mg", etc.
        pattern = r'(\d+\.?\d*)\s*(mg|g|mcg|ml|%)'
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            return f"{match.group(1)} {match.group(2)}"
        return ""


# Singleton instance
medication_db_service = MedicationDatabaseService()