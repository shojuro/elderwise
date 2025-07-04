import logging
import aiohttp
import asyncio
from typing import List, Dict, Optional, Any
from urllib.parse import urlencode
import json

from src.config.settings import settings
from src.models.medication import Medication, MedicationDetails, DrugInteraction, FoodInteraction

logger = logging.getLogger(__name__)


class RxNormClient:
    """Client for RxNorm and RxImage API integration"""
    
    def __init__(self):
        self.rximage_base_url = settings.rximage_base_url
        self.rxnorm_base_url = settings.rxnorm_base_url
        self.fda_base_url = settings.fda_api_base_url
        self.session = None
        self._timeout = aiohttp.ClientTimeout(total=30)
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self._timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession(timeout=self._timeout)
        return self.session
    
    async def search_by_imprint(
        self, 
        imprint: str, 
        color: Optional[str] = None,
        shape: Optional[str] = None,
        size: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search RxImage API for pills by physical characteristics
        
        Args:
            imprint: Text on the pill
            color: Pill color
            shape: Pill shape
            size: Pill size in mm
            
        Returns:
            List of matching medications from RxImage
        """
        try:
            # Build query parameters
            params = {"imprint": imprint}
            if color:
                params["color"] = self._normalize_color(color)
            if shape:
                params["shape"] = self._normalize_shape(shape)
            if size:
                params["size"] = size
                params["sizeT"] = 2  # Tolerance of 2mm
            
            # Make request to RxImage API
            url = f"{self.rximage_base_url}/rxnav"
            
            session = await self._get_session()
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Parse RxImage response
                    results = []
                    if "nlmRxImages" in data:
                        for image_data in data["nlmRxImages"]:
                            result = {
                                "name": image_data.get("name", ""),
                                "rxcui": image_data.get("rxcui", ""),
                                "ndc": image_data.get("ndc11", ""),
                                "splSetId": image_data.get("splSetId", ""),
                                "imageUrl": image_data.get("imageUrl", ""),
                                "imprint": image_data.get("imprint", ""),
                                "shape": image_data.get("shape", ""),
                                "color": image_data.get("colors", []),
                                "size": image_data.get("size", 0)
                            }
                            results.append(result)
                    
                    logger.info(f"Found {len(results)} medications matching imprint: {imprint}")
                    return results
                else:
                    logger.error(f"RxImage API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error searching RxImage: {e}")
            return []
    
    async def get_medication_details(self, rxcui: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed medication information from RxNorm
        
        Args:
            rxcui: RxNorm Concept Unique Identifier
            
        Returns:
            Detailed medication information
        """
        try:
            # Get all properties from RxNorm
            url = f"{self.rxnorm_base_url}/rxcui/{rxcui}/allinfo.json"
            
            session = await self._get_session()
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if "rxcuiStatusHistory" in data and "attributes" in data["rxcuiStatusHistory"]:
                        attributes = data["rxcuiStatusHistory"]["attributes"]
                        
                        # Extract medication details
                        details = {
                            "rxcui": rxcui,
                            "name": attributes.get("name", ""),
                            "genericName": "",
                            "brandNames": [],
                            "dosageForm": attributes.get("rxtermsDoseForm", ""),
                            "strength": "",
                            "route": attributes.get("route", [])
                        }
                        
                        # Get generic name
                        if "derivedConcepts" in data["rxcuiStatusHistory"]:
                            concepts = data["rxcuiStatusHistory"]["derivedConcepts"]
                            if "ingredientConcept" in concepts:
                                details["genericName"] = concepts["ingredientConcept"][0].get("name", "")
                        
                        # Get brand names
                        if "relatedGroup" in data:
                            concepts = data["relatedGroup"].get("conceptGroup", [])
                            for group in concepts:
                                if group.get("tty") == "BN":  # Brand Name
                                    for concept in group.get("conceptProperties", []):
                                        details["brandNames"].append(concept.get("name", ""))
                        
                        return details
                else:
                    logger.error(f"RxNorm API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting medication details: {e}")
            return None
    
    async def get_fda_label_info(self, rxcui: str) -> Optional[Dict[str, Any]]:
        """
        Get FDA label information including warnings and interactions
        
        Args:
            rxcui: RxNorm Concept Unique Identifier
            
        Returns:
            FDA label information
        """
        try:
            # Search FDA API by rxcui
            params = {
                "search": f"openfda.rxcui:{rxcui}",
                "limit": 1
            }
            
            url = f"{self.fda_base_url}/label.json"
            
            session = await self._get_session()
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if "results" in data and data["results"]:
                        label = data["results"][0]
                        
                        # Extract relevant information
                        info = {
                            "indications": label.get("indications_and_usage", []),
                            "contraindications": label.get("contraindications", []),
                            "warnings": label.get("warnings", []),
                            "adverse_reactions": label.get("adverse_reactions", []),
                            "drug_interactions": label.get("drug_interactions", []),
                            "dosage": label.get("dosage_and_administration", []),
                            "boxed_warning": label.get("boxed_warning", [])
                        }
                        
                        return info
                else:
                    logger.warning(f"FDA API returned status {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting FDA label info: {e}")
            return None
    
    async def build_medication_details(
        self, 
        rximage_result: Dict[str, Any]
    ) -> Optional[MedicationDetails]:
        """
        Build complete medication details from various APIs
        
        Args:
            rximage_result: Result from RxImage search
            
        Returns:
            Complete MedicationDetails object
        """
        try:
            rxcui = rximage_result.get("rxcui")
            if not rxcui:
                return None
            
            # Get RxNorm details
            rxnorm_details = await self.get_medication_details(rxcui)
            
            # Get FDA label info
            fda_info = await self.get_fda_label_info(rxcui)
            
            # Build MedicationDetails object
            medication = MedicationDetails(
                medication_id=rxcui,
                name=rximage_result.get("name", ""),
                generic_name=rxnorm_details.get("genericName", "") if rxnorm_details else "",
                brand_names=rxnorm_details.get("brandNames", []) if rxnorm_details else [],
                shape=rximage_result.get("shape", ""),
                color=", ".join(rximage_result.get("color", [])),
                imprint=rximage_result.get("imprint", ""),
                dosage_forms=[rxnorm_details.get("dosageForm", "")] if rxnorm_details else [],
                strength=self._extract_strength(rximage_result.get("name", "")),
                ndc_code=rximage_result.get("ndc", ""),
                rxcui=rxcui
            )
            
            # Add FDA information if available
            if fda_info:
                # Parse indications
                if fda_info["indications"]:
                    medication.indications = self._parse_fda_text(fda_info["indications"])
                
                # Parse contraindications
                if fda_info["contraindications"]:
                    medication.contraindications = self._parse_fda_text(fda_info["contraindications"])
                
                # Parse warnings
                if fda_info["warnings"]:
                    medication.warnings = self._parse_fda_text(fda_info["warnings"])
                
                # Parse adverse reactions into side effects
                if fda_info["adverse_reactions"]:
                    medication.side_effects = self._parse_side_effects(fda_info["adverse_reactions"])
                
                # Parse drug interactions
                if fda_info["drug_interactions"]:
                    medication.drug_interactions = self._parse_drug_interactions(fda_info["drug_interactions"])
            
            return medication
            
        except Exception as e:
            logger.error(f"Error building medication details: {e}")
            return None
    
    def _normalize_color(self, color: str) -> str:
        """Normalize color name for RxImage API"""
        color_map = {
            "white": "WHITE",
            "blue": "BLUE",
            "pink": "PINK",
            "red": "RED",
            "green": "GREEN",
            "yellow": "YELLOW",
            "orange": "ORANGE",
            "purple": "PURPLE",
            "gray": "GRAY",
            "grey": "GRAY",
            "brown": "BROWN",
            "black": "BLACK"
        }
        return color_map.get(color.lower(), color.upper())
    
    def _normalize_shape(self, shape: str) -> str:
        """Normalize shape name for RxImage API"""
        shape_map = {
            "round": "ROUND",
            "oval": "OVAL",
            "oblong": "OBLONG",
            "capsule": "CAPSULE",
            "square": "SQUARE",
            "rectangle": "RECTANGLE",
            "diamond": "DIAMOND",
            "triangle": "TRIANGLE",
            "pentagon": "PENTAGON",
            "hexagon": "HEXAGON"
        }
        return shape_map.get(shape.lower(), shape.upper())
    
    def _extract_strength(self, name: str) -> str:
        """Extract strength from medication name"""
        import re
        # Look for patterns like "500 mg", "10mg", etc.
        pattern = r'(\d+\.?\d*)\s*(mg|g|mcg|ml|%)'
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            return f"{match.group(1)} {match.group(2)}"
        return ""
    
    def _parse_fda_text(self, text_list: List[str]) -> List[str]:
        """Parse FDA text sections into list of items"""
        if not text_list:
            return []
        
        # Join text and split by common delimiters
        text = " ".join(text_list)
        
        # Remove common FDA formatting
        text = text.replace("INDICATIONS AND USAGE", "")
        text = text.replace("CONTRAINDICATIONS", "")
        text = text.replace("WARNINGS", "")
        
        # Split by bullet points or numbers
        items = []
        import re
        bullets = re.split(r'[•·▪]\s*|\d+\.\s*', text)
        
        for item in bullets:
            item = item.strip()
            if len(item) > 10:  # Filter out very short items
                items.append(item)
        
        return items[:10]  # Limit to 10 items
    
    def _parse_side_effects(self, adverse_reactions: List[str]) -> Dict[str, List[str]]:
        """Parse adverse reactions into categorized side effects"""
        text = " ".join(adverse_reactions) if adverse_reactions else ""
        
        # Simple categorization based on keywords
        side_effects = {
            "common": [],
            "rare": [],
            "severe": []
        }
        
        # Extract side effects (simplified)
        import re
        effects = re.findall(r'(?:may cause|include|such as)\s*([^.]+)', text, re.IGNORECASE)
        
        for effect in effects[:5]:  # Limit to 5 per category
            effect = effect.strip()
            if any(word in effect.lower() for word in ["death", "fatal", "life-threatening"]):
                side_effects["severe"].append(effect)
            elif any(word in effect.lower() for word in ["rare", "uncommon", "infrequent"]):
                side_effects["rare"].append(effect)
            else:
                side_effects["common"].append(effect)
        
        return side_effects
    
    def _parse_drug_interactions(self, interactions_text: List[str]) -> List[DrugInteraction]:
        """Parse drug interactions from FDA text"""
        if not interactions_text:
            return []
        
        text = " ".join(interactions_text)
        interactions = []
        
        # Look for specific drug mentions (simplified)
        import re
        drug_patterns = re.findall(r'with\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)', text, re.IGNORECASE)
        
        for drug in drug_patterns[:5]:  # Limit to 5 interactions
            interaction = DrugInteraction(
                drug_name=drug.strip(),
                severity="moderate",  # Default severity
                description=f"May interact with {drug}",
                management="Monitor closely when used together"
            )
            interactions.append(interaction)
        
        return interactions


# Singleton instance
rxnorm_client = RxNormClient()