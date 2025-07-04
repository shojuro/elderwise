import logging
from typing import List, Dict, Set, Optional
from datetime import datetime

from src.models.medication import (
    DrugInteraction, FoodInteraction, InteractionCheckResult,
    UserMedication
)
from src.services.medication_db import medication_db_service

logger = logging.getLogger(__name__)


class DrugInteractionService:
    """
    Service for checking drug-drug and drug-food interactions.
    Provides comprehensive interaction checking with severity ratings.
    """
    
    def __init__(self):
        # Critical food interactions that apply to multiple medications
        self.critical_food_interactions = {
            "grapefruit": {
                "affected_drugs": [
                    "statins", "calcium channel blockers", "immunosuppressants",
                    "benzodiazepines", "warfarin", "amiodarone"
                ],
                "severity": "major",
                "description": "Grapefruit can significantly increase drug levels, leading to toxicity"
            },
            "alcohol": {
                "affected_drugs": [
                    "opioids", "benzodiazepines", "sleep medications",
                    "antidepressants", "antihistamines", "muscle relaxants"
                ],
                "severity": "major",
                "description": "Alcohol can cause dangerous sedation and respiratory depression"
            },
            "vitamin_k": {
                "affected_drugs": ["warfarin", "coumadin"],
                "severity": "moderate",
                "description": "Vitamin K can reduce effectiveness of blood thinners"
            },
            "tyramine": {
                "affected_drugs": ["MAO inhibitors"],
                "severity": "major",
                "description": "Can cause dangerous blood pressure spikes"
            }
        }
        
        # Contraindicated drug combinations
        self.contraindicated_combinations = [
            {"drugs": ["opioids", "benzodiazepines"], "reason": "Respiratory depression risk"},
            {"drugs": ["MAO inhibitors", "SSRIs"], "reason": "Serotonin syndrome risk"},
            {"drugs": ["warfarin", "NSAIDs"], "reason": "Increased bleeding risk"},
            {"drugs": ["ACE inhibitors", "potassium supplements"], "reason": "Hyperkalemia risk"}
        ]
    
    async def check_all_interactions(
        self, 
        user_medications: List[UserMedication],
        new_medication: Optional[str] = None
    ) -> InteractionCheckResult:
        """
        Comprehensive interaction check for all user medications
        
        Args:
            user_medications: List of user's current medications
            new_medication: Optional new medication to check
            
        Returns:
            Complete interaction check results
        """
        result = InteractionCheckResult(
            user_id=user_medications[0].user_id if user_medications else "unknown"
        )
        
        # Get all medication names
        medication_names = [med.medication.name for med in user_medications]
        if new_medication:
            medication_names.append(new_medication)
        
        # Check drug-drug interactions
        drug_interactions = await self._check_drug_interactions(medication_names)
        result.drug_interactions = drug_interactions
        
        # Check food interactions
        food_interactions = await self._check_food_interactions(medication_names)
        result.food_interactions = food_interactions
        
        # Check for critical interactions
        result.has_critical_interactions = any(
            interaction.severity in ["major", "contraindicated"]
            for interaction in drug_interactions
        )
        
        # Generate recommendations
        result.recommendations = self._generate_recommendations(
            drug_interactions, food_interactions
        )
        
        return result
    
    async def _check_drug_interactions(
        self, 
        medication_names: List[str]
    ) -> List[DrugInteraction]:
        """Check for drug-drug interactions"""
        interactions = []
        
        # Use medication database service
        db_interactions = await medication_db_service.check_interactions(medication_names)
        
        for interaction_list in db_interactions.values():
            interactions.extend(interaction_list)
        
        # Check contraindicated combinations
        med_names_lower = [name.lower() for name in medication_names]
        
        for combo in self.contraindicated_combinations:
            combo_drugs = combo["drugs"]
            if self._check_drug_class_match(med_names_lower, combo_drugs):
                interactions.append(DrugInteraction(
                    drug_name=" + ".join(combo_drugs),
                    severity="contraindicated",
                    description=combo["reason"],
                    management="Avoid this combination. Consult prescriber immediately."
                ))
        
        return interactions
    
    async def _check_food_interactions(
        self, 
        medication_names: List[str]
    ) -> List[FoodInteraction]:
        """Check for drug-food interactions"""
        interactions = []
        checked_foods = set()
        
        for medication in medication_names:
            # Get specific food interactions from database
            med_food_interactions = await medication_db_service.get_food_interactions(medication)
            interactions.extend(med_food_interactions)
            
            # Check critical food interactions
            med_lower = medication.lower()
            for food, info in self.critical_food_interactions.items():
                if food in checked_foods:
                    continue
                    
                for affected_drug in info["affected_drugs"]:
                    if affected_drug.lower() in med_lower:
                        interactions.append(FoodInteraction(
                            food_item=food.title(),
                            severity=info["severity"],
                            description=info["description"],
                            timing_instructions=self._get_food_timing_instructions(food)
                        ))
                        checked_foods.add(food)
                        break
        
        return interactions
    
    def _check_drug_class_match(
        self, 
        medication_names: List[str], 
        drug_classes: List[str]
    ) -> bool:
        """Check if medications match specified drug classes"""
        matches = 0
        for drug_class in drug_classes:
            for med_name in medication_names:
                if drug_class.lower() in med_name:
                    matches += 1
                    break
        
        return matches >= len(drug_classes)
    
    def _get_food_timing_instructions(self, food: str) -> str:
        """Get timing instructions for food interactions"""
        instructions = {
            "grapefruit": "Avoid grapefruit and grapefruit juice completely while taking this medication",
            "alcohol": "Avoid alcohol completely while taking this medication",
            "vitamin_k": "Maintain consistent intake of vitamin K-rich foods (leafy greens)",
            "tyramine": "Avoid aged cheeses, cured meats, and fermented foods",
            "dairy": "Take medication 1 hour before or 2 hours after dairy products"
        }
        
        return instructions.get(food, "Consult your pharmacist about timing")
    
    def _generate_recommendations(
        self, 
        drug_interactions: List[DrugInteraction],
        food_interactions: List[FoodInteraction]
    ) -> List[str]:
        """Generate safety recommendations based on interactions"""
        recommendations = []
        
        # Check severity levels
        severities = [i.severity for i in drug_interactions]
        
        if "contraindicated" in severities:
            recommendations.append(
                "⚠️ CRITICAL: Contraindicated drug combination detected. "
                "Contact your healthcare provider immediately."
            )
        
        if "major" in severities:
            recommendations.append(
                "⚠️ Major drug interactions detected. "
                "Discuss with your healthcare provider before taking these medications together."
            )
        
        if "moderate" in severities:
            recommendations.append(
                "⚡ Moderate interactions detected. "
                "Your healthcare provider should monitor you closely."
            )
        
        # Food interaction recommendations
        major_food = [f for f in food_interactions if f.severity == "major"]
        if major_food:
            foods = ", ".join([f.food_item for f in major_food])
            recommendations.append(
                f"🍊 Avoid these foods: {foods}"
            )
        
        # General recommendations
        if drug_interactions or food_interactions:
            recommendations.extend([
                "📋 Keep a list of all your medications to show healthcare providers",
                "💊 Take medications exactly as prescribed",
                "📞 Report any unusual symptoms to your healthcare provider"
            ])
        else:
            recommendations.append(
                "✅ No significant interactions detected with current medications"
            )
        
        return recommendations
    
    async def check_elder_specific_concerns(
        self, 
        medications: List[str], 
        user_age: Optional[int] = None
    ) -> List[str]:
        """
        Check for medication concerns specific to elderly patients
        
        Args:
            medications: List of medication names
            user_age: Patient age if available
            
        Returns:
            List of elder-specific warnings
        """
        concerns = []
        
        # Medications requiring special caution in elderly
        elder_caution_meds = {
            "benzodiazepines": "Increased fall risk and confusion",
            "anticholinergics": "Risk of confusion, constipation, and urinary retention",
            "NSAIDs": "Increased risk of GI bleeding and kidney problems",
            "muscle relaxants": "Increased sedation and fall risk",
            "antipsychotics": "Increased risk of stroke in dementia patients"
        }
        
        meds_lower = [med.lower() for med in medications]
        
        for med_class, warning in elder_caution_meds.items():
            for med in meds_lower:
                if med_class.lower() in med:
                    concerns.append(f"⚠️ {med_class.title()}: {warning}")
                    break
        
        # Polypharmacy warning
        if len(medications) >= 5:
            concerns.append(
                "💊 Multiple medications detected. "
                "Regular medication reviews are important to prevent interactions."
            )
        
        # Age-specific warnings
        if user_age and user_age >= 65:
            concerns.append(
                "👴 Age 65+: Start with lower doses and monitor closely for side effects"
            )
        
        return concerns


# Singleton instance
drug_interaction_service = DrugInteractionService()