from datetime import datetime
from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field
from bson import ObjectId


class DrugInteraction(BaseModel):
    drug_name: str
    severity: Literal["minor", "moderate", "major", "contraindicated"]
    description: str
    management: str
    
    
class FoodInteraction(BaseModel):
    food_item: str
    severity: Literal["minor", "moderate", "major"]
    description: str
    timing_instructions: Optional[str] = None


class Medication(BaseModel):
    medication_id: str = Field(default_factory=lambda: str(ObjectId()))
    name: str
    generic_name: str
    brand_names: List[str] = Field(default_factory=list)
    shape: Optional[str] = None
    color: Optional[str] = None
    imprint: Optional[str] = None
    dosage_forms: List[str] = Field(default_factory=list)
    strength: str
    manufacturer: Optional[str] = None
    ndc_code: Optional[str] = None  # National Drug Code
    rxcui: Optional[str] = None  # RxNorm Concept Unique Identifier
    
    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }


class MedicationDetails(Medication):
    indications: List[str] = Field(default_factory=list)
    contraindications: List[str] = Field(default_factory=list)
    side_effects: Dict[str, List[str]] = Field(
        default_factory=lambda: {
            "common": [],
            "rare": [],
            "severe": []
        }
    )
    drug_interactions: List[DrugInteraction] = Field(default_factory=list)
    food_interactions: List[FoodInteraction] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    pregnancy_category: Optional[str] = None
    storage_instructions: Optional[str] = None
    administration_instructions: List[str] = Field(default_factory=list)


class MedicationImage(BaseModel):
    user_id: str
    image_id: str = Field(default_factory=lambda: str(ObjectId()))
    image_data: str  # base64 encoded
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    image_metadata: Dict[str, any] = Field(default_factory=dict)
    identified_medications: List[Medication] = Field(default_factory=list)
    confidence_scores: Dict[str, float] = Field(default_factory=dict)
    processing_status: Literal["pending", "processing", "completed", "failed"] = "pending"
    error_message: Optional[str] = None
    
    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }


class UserMedication(BaseModel):
    user_medication_id: str = Field(default_factory=lambda: str(ObjectId()))
    user_id: str
    medication: Medication
    dosage: str
    frequency: str
    times: List[str] = Field(default_factory=list)  # ["08:00", "20:00"]
    start_date: datetime
    end_date: Optional[datetime] = None
    prescribed_by: Optional[str] = None
    pharmacy: Optional[str] = None
    refills_remaining: Optional[int] = None
    notes: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }


class MedicationReminder(BaseModel):
    reminder_id: str = Field(default_factory=lambda: str(ObjectId()))
    user_id: str
    user_medication_id: str
    medication_name: str
    dosage: str
    scheduled_time: datetime
    actual_taken_time: Optional[datetime] = None
    status: Literal["pending", "taken", "missed", "skipped"] = "pending"
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }


class MedicationAdherence(BaseModel):
    user_id: str
    medication_name: str
    period_start: datetime
    period_end: datetime
    total_doses: int
    taken_doses: int
    missed_doses: int
    skipped_doses: int
    adherence_percentage: float
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class InteractionCheck(BaseModel):
    user_id: str
    medications: List[str]  # List of medication names or IDs
    check_food_interactions: bool = True
    include_inactive_medications: bool = False
    

class InteractionCheckResult(BaseModel):
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    drug_interactions: List[DrugInteraction] = Field(default_factory=list)
    food_interactions: List[FoodInteraction] = Field(default_factory=list)
    has_critical_interactions: bool = False
    recommendations: List[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }