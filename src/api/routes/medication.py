from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta
import base64

from src.models.medication import (
    Medication, MedicationDetails, MedicationImage,
    UserMedication, MedicationReminder, InteractionCheck,
    InteractionCheckResult, MedicationAdherence
)
from src.services.vision import vision_service
from src.services.medication_db import medication_db_service
from src.services.drug_interactions import drug_interaction_service
from src.memory.storage import MemoryStorage

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize storage
storage = MemoryStorage()


class MedicationIdentifyRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    image_data: str = Field(..., description="Base64 encoded image data")
    save_to_profile: bool = Field(False, description="Save medication to user profile")


class MedicationIdentifyResponse(BaseModel):
    success: bool
    medications: List[Medication]
    confidence_scores: Dict[str, float]
    pill_features: Dict[str, Any]
    warnings: List[str]


class AddMedicationRequest(BaseModel):
    user_id: str
    medication_id: str
    dosage: str
    frequency: str
    times: List[str]
    prescribed_by: Optional[str] = None
    pharmacy: Optional[str] = None
    notes: Optional[str] = None


class MedicationReminderRequest(BaseModel):
    user_id: str
    user_medication_id: str
    reminder_times: List[str]


@router.post("/identify", response_model=MedicationIdentifyResponse)
async def identify_medication(
    request: MedicationIdentifyRequest,
    background_tasks: BackgroundTasks
):
    """
    Identify medication from an image
    
    This endpoint:
    1. Validates the image
    2. Extracts pill features (shape, color, imprint)
    3. Searches medication database
    4. Returns possible matches with confidence scores
    """
    try:
        # Validate image
        is_valid, error_msg = vision_service.validate_image(request.image_data)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Enhance image for better recognition
        enhanced_image = await vision_service.enhance_image(request.image_data)
        
        # Extract pill features
        logger.info(f"Analyzing medication image for user {request.user_id}")
        pill_features = await vision_service.analyze_medication_image(enhanced_image)
        
        # Search for medications based on features
        medications = []
        confidence_scores = {}
        
        if pill_features.imprint:
            # Search by imprint first (most reliable)
            found_meds = await medication_db_service.identify_by_imprint(
                imprint=pill_features.imprint,
                shape=pill_features.shape,
                color=pill_features.color
            )
            
            for med in found_meds:
                medications.append(med)
                # Calculate confidence based on feature matches
                confidence = pill_features.confidence
                if med.shape == pill_features.shape:
                    confidence += 0.1
                if med.color == pill_features.color:
                    confidence += 0.1
                confidence_scores[med.medication_id] = min(confidence, 1.0)
        
        # Store the image analysis in background
        background_tasks.add_task(
            store_medication_image,
            user_id=request.user_id,
            image_data=request.image_data,
            pill_features=pill_features,
            identified_medications=medications
        )
        
        # Generate warnings for elder users
        warnings = []
        if medications:
            # Check if any identified medications require special care
            for med in medications:
                if any(term in med.name.lower() for term in ["opioid", "narcotic", "benzodiazepine"]):
                    warnings.append("⚠️ This medication requires special care. Keep in a secure location.")
                if "anticoagulant" in med.name.lower() or "warfarin" in med.name.lower():
                    warnings.append("⚠️ Blood thinner detected. Regular monitoring required.")
        else:
            warnings.append("Could not identify medication. Please consult your pharmacist.")
        
        # Add general advice
        warnings.append("Always verify medication identity with your pharmacist before taking.")
        
        return MedicationIdentifyResponse(
            success=len(medications) > 0,
            medications=medications,
            confidence_scores=confidence_scores,
            pill_features={
                "shape": pill_features.shape,
                "color": pill_features.color,
                "imprint": pill_features.imprint,
                "size_estimate": pill_features.size_estimate
            },
            warnings=warnings
        )
        
    except Exception as e:
        logger.error(f"Error identifying medication: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{medication_id}", response_model=MedicationDetails)
async def get_medication_details(medication_id: str):
    """Get detailed information about a medication"""
    try:
        details = await medication_db_service.get_medication_details(medication_id)
        
        if not details:
            raise HTTPException(status_code=404, detail="Medication not found")
        
        return details
        
    except Exception as e:
        logger.error(f"Error getting medication details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/user/add")
async def add_user_medication(request: AddMedicationRequest):
    """Add a medication to user's profile"""
    try:
        # Get medication details
        medication = await medication_db_service.get_medication_details(request.medication_id)
        if not medication:
            raise HTTPException(status_code=404, detail="Medication not found")
        
        # Create user medication record
        user_medication = UserMedication(
            user_id=request.user_id,
            medication=Medication(
                medication_id=medication.medication_id,
                name=medication.name,
                generic_name=medication.generic_name,
                brand_names=medication.brand_names,
                shape=medication.shape,
                color=medication.color,
                imprint=medication.imprint,
                dosage_forms=medication.dosage_forms,
                strength=medication.strength,
                manufacturer=medication.manufacturer
            ),
            dosage=request.dosage,
            frequency=request.frequency,
            times=request.times,
            prescribed_by=request.prescribed_by,
            pharmacy=request.pharmacy,
            notes=request.notes,
            start_date=datetime.utcnow()
        )
        
        # Store in database (mock for now)
        # In production, save to MongoDB
        logger.info(f"Added medication {medication.name} for user {request.user_id}")
        
        # Check for interactions with existing medications
        interaction_result = await check_medication_interactions(
            InteractionCheck(
                user_id=request.user_id,
                medications=[medication.name]
            )
        )
        
        return {
            "success": True,
            "user_medication_id": user_medication.user_medication_id,
            "medication_name": medication.name,
            "interaction_warnings": interaction_result.recommendations
        }
        
    except Exception as e:
        logger.error(f"Error adding user medication: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/medications")
async def get_user_medications(user_id: str, include_inactive: bool = False):
    """Get all medications for a user"""
    try:
        # Mock implementation - in production, query from database
        mock_medications = [
            UserMedication(
                user_id=user_id,
                medication=Medication(
                    medication_id="med_001",
                    name="Acetaminophen",
                    generic_name="acetaminophen",
                    brand_names=["Tylenol"],
                    strength="500 mg"
                ),
                dosage="500mg",
                frequency="Every 6 hours as needed",
                times=["08:00", "14:00", "20:00"],
                start_date=datetime.utcnow() - timedelta(days=30),
                is_active=True
            )
        ]
        
        if include_inactive:
            return mock_medications
        else:
            return [med for med in mock_medications if med.is_active]
            
    except Exception as e:
        logger.error(f"Error getting user medications: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interactions/check", response_model=InteractionCheckResult)
async def check_medication_interactions(request: InteractionCheck):
    """Check for drug-drug and drug-food interactions"""
    try:
        # Get user's current medications
        user_medications = await get_user_medications(request.user_id)
        
        # Check interactions
        result = await drug_interaction_service.check_all_interactions(
            user_medications=user_medications,
            new_medication=request.medications[0] if request.medications else None
        )
        
        # Add elder-specific concerns
        if request.user_id:
            # Get user age from profile (mock for now)
            user_age = 75  # Mock age
            elder_concerns = await drug_interaction_service.check_elder_specific_concerns(
                medications=request.medications,
                user_age=user_age
            )
            result.recommendations.extend(elder_concerns)
        
        return result
        
    except Exception as e:
        logger.error(f"Error checking interactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reminders")
async def create_medication_reminder(request: MedicationReminderRequest):
    """Create medication reminders for a user"""
    try:
        # Create reminders for each time
        reminders = []
        for time_str in request.reminder_times:
            # Parse time and create reminder
            hour, minute = map(int, time_str.split(':'))
            reminder_time = datetime.utcnow().replace(hour=hour, minute=minute, second=0)
            
            # If time has passed today, schedule for tomorrow
            if reminder_time < datetime.utcnow():
                reminder_time += timedelta(days=1)
            
            reminder = MedicationReminder(
                user_id=request.user_id,
                user_medication_id=request.user_medication_id,
                medication_name="Mock Medication",  # Get from database in production
                dosage="Mock Dosage",
                scheduled_time=reminder_time
            )
            reminders.append(reminder)
        
        # In production, save to database and schedule notifications
        logger.info(f"Created {len(reminders)} reminders for user {request.user_id}")
        
        return {
            "success": True,
            "reminders_created": len(reminders),
            "next_reminder": min(r.scheduled_time for r in reminders).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating reminders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/adherence/{user_id}")
async def get_medication_adherence(
    user_id: str,
    days: int = 30
):
    """Get medication adherence statistics for a user"""
    try:
        # Mock implementation
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        adherence = MedicationAdherence(
            user_id=user_id,
            medication_name="All Medications",
            period_start=start_date,
            period_end=end_date,
            total_doses=90,  # 3 times daily for 30 days
            taken_doses=85,
            missed_doses=5,
            skipped_doses=0,
            adherence_percentage=94.4
        )
        
        return {
            "adherence": adherence,
            "trend": "improving",
            "recommendations": [
                "Great job maintaining your medication schedule!",
                "Consider setting reminders for evening doses"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting adherence data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reminder/{reminder_id}/taken")
async def mark_medication_taken(reminder_id: str, notes: Optional[str] = None):
    """Mark a medication reminder as taken"""
    try:
        # In production, update the reminder in database
        logger.info(f"Marked reminder {reminder_id} as taken")
        
        return {
            "success": True,
            "reminder_id": reminder_id,
            "status": "taken",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error marking medication taken: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Background task functions
async def store_medication_image(
    user_id: str,
    image_data: str,
    pill_features: Any,
    identified_medications: List[Medication]
):
    """Store medication image analysis for future reference"""
    try:
        medication_image = MedicationImage(
            user_id=user_id,
            image_data=image_data,
            identified_medications=identified_medications,
            confidence_scores={
                med.medication_id: 0.85 for med in identified_medications
            },
            processing_status="completed",
            image_metadata={
                "shape": pill_features.shape,
                "color": pill_features.color,
                "imprint": pill_features.imprint
            }
        )
        
        # In production, save to database
        logger.info(f"Stored medication image analysis for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error storing medication image: {e}")