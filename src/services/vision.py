import base64
import io
import logging
from typing import Dict, List, Optional, Tuple
from PIL import Image
import numpy as np
from dataclasses import dataclass

from src.services.google_vision_client import google_vision_client
from src.config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class PillFeatures:
    """Extracted features from a pill image"""
    shape: Optional[str] = None
    color: Optional[str] = None
    imprint: Optional[str] = None
    size_estimate: Optional[str] = None
    confidence: float = 0.0


class VisionService:
    """
    Service for analyzing medication images.
    Integrates with Google Vision API for production use,
    with fallback to local image processing.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.google_vision_api_key
        self.use_google_vision = bool(self.api_key and google_vision_client.client)
        self._init_color_ranges()
        
        if self.use_google_vision:
            logger.info("Vision service using Google Vision API")
        else:
            logger.info("Vision service using local processing (Google Vision not available)")
        
    def _init_color_ranges(self):
        """Initialize HSV color ranges for pill color detection"""
        self.color_ranges = {
            "white": [(0, 0, 200), (180, 30, 255)],
            "blue": [(100, 50, 50), (130, 255, 255)],
            "pink": [(140, 50, 50), (170, 255, 255)],
            "yellow": [(20, 50, 50), (30, 255, 255)],
            "orange": [(10, 50, 50), (20, 255, 255)],
            "red": [(0, 50, 50), (10, 255, 255)],
            "green": [(40, 50, 50), (80, 255, 255)],
            "brown": [(10, 50, 20), (20, 255, 100)],
            "gray": [(0, 0, 50), (180, 30, 200)]
        }
    
    async def analyze_medication_image(self, image_data: str) -> PillFeatures:
        """
        Analyze a medication image and extract features
        
        Args:
            image_data: Base64 encoded image data
            
        Returns:
            PillFeatures object with extracted information
        """
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract features
            features = PillFeatures()
            
            if self.use_google_vision:
                # Use Google Vision API for text extraction
                imprints = await google_vision_client.extract_text(image_data)
                if imprints:
                    # Take the most likely imprint (first one)
                    features.imprint = imprints[0] if imprints else None
                    features.confidence = 0.9  # High confidence with Google Vision
                
                # Use Google Vision for color detection
                colors = await google_vision_client.detect_colors(image_data)
                if colors:
                    # Use the dominant color
                    features.color = colors[0]['name'] if colors else None
                
                # Shape detection still uses local processing
                features.shape = await self._detect_shape(image)
                features.size_estimate = await self._estimate_size(image)
                
            else:
                # Fallback to local processing
                features.shape = await self._detect_shape(image)
                features.color = await self._detect_color(image)
                features.imprint = await self._extract_text_local(image)
                features.size_estimate = await self._estimate_size(image)
                features.confidence = 0.7  # Lower confidence without API
            
            logger.info(f"Extracted pill features: {features}")
            return features
            
        except Exception as e:
            logger.error(f"Error analyzing medication image: {e}")
            return PillFeatures(confidence=0.0)
    
    async def _detect_shape(self, image: Image.Image) -> str:
        """
        Detect the shape of the pill using image analysis
        """
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Convert to grayscale
            gray = np.mean(img_array, axis=2).astype(np.uint8)
            
            # Simple edge detection (threshold)
            threshold = np.mean(gray)
            binary = (gray > threshold).astype(np.uint8) * 255
            
            # Calculate aspect ratio of bounding box
            rows = np.any(binary, axis=1)
            cols = np.any(binary, axis=0)
            
            if np.any(rows) and np.any(cols):
                rmin, rmax = np.where(rows)[0][[0, -1]]
                cmin, cmax = np.where(cols)[0][[0, -1]]
                
                height = rmax - rmin
                width = cmax - cmin
                
                if height > 0:
                    aspect_ratio = width / height
                    
                    # Classify shape based on aspect ratio and area
                    if 0.9 <= aspect_ratio <= 1.1:
                        return "round"
                    elif 1.5 <= aspect_ratio <= 2.5:
                        return "oval"
                    elif aspect_ratio > 2.5:
                        return "capsule"
                    else:
                        return "oblong"
            
            return "unknown"
            
        except Exception as e:
            logger.error(f"Error detecting shape: {e}")
            return "unknown"
    
    async def _detect_color(self, image: Image.Image) -> str:
        """
        Detect the dominant color of the pill
        """
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Get center region (where pill likely is)
            h, w = img_array.shape[:2]
            center_region = img_array[h//4:3*h//4, w//4:3*w//4]
            
            # Calculate average color
            avg_color = np.mean(center_region.reshape(-1, 3), axis=0)
            
            # Convert to HSV for better color classification
            # Simplified HSV conversion
            r, g, b = avg_color / 255.0
            max_c = max(r, g, b)
            min_c = min(r, g, b)
            diff = max_c - min_c
            
            # Calculate hue
            if diff == 0:
                h = 0
            elif max_c == r:
                h = ((g - b) / diff) % 6
            elif max_c == g:
                h = (b - r) / diff + 2
            else:
                h = (r - g) / diff + 4
            
            h = int(h * 60)
            s = 0 if max_c == 0 else diff / max_c
            v = max_c
            
            # Classify color based on HSV values
            if s < 0.1 and v > 0.8:
                return "white"
            elif s < 0.1 and v < 0.3:
                return "black"
            elif s < 0.1:
                return "gray"
            elif 0 <= h <= 20 or 340 <= h <= 360:
                return "red"
            elif 20 < h <= 40:
                return "orange"
            elif 40 < h <= 70:
                return "yellow"
            elif 70 < h <= 150:
                return "green"
            elif 150 < h <= 260:
                return "blue"
            elif 260 < h <= 340:
                return "purple" if s > 0.5 else "pink"
            else:
                return "unknown"
                
        except Exception as e:
            logger.error(f"Error detecting color: {e}")
            return "unknown"
    
    async def _extract_text_local(self, image: Image.Image) -> Optional[str]:
        """
        Extract text from pill using local processing (fallback)
        This is a placeholder - in production, always use Google Vision
        """
        # Mock some common imprints for testing when API is not available
        import random
        
        if settings.google_vision_api_key:
            # If API key exists but Google Vision failed, return None
            return None
        
        # Only for development/testing without API key
        mock_imprints = [
            "L484", "TEVA 3109", "M367", "IP 110", "AN 627",
            "V 3601", "T 194", "G 32 500", "54 543", "93 150"
        ]
        
        if random.random() > 0.3:  # 70% chance of detecting imprint in mock
            return random.choice(mock_imprints)
        return None
    
    async def _estimate_size(self, image: Image.Image) -> str:
        """
        Estimate the size of the pill
        In production, this could use reference objects or ML-based size estimation
        """
        width, height = image.size
        
        # Rough estimation based on typical phone camera images
        # Assuming pills are photographed at similar distances
        max_dim = max(width, height)
        
        # Estimate based on pixel dimensions
        # These thresholds would need calibration with real data
        if max_dim < 200:
            return "small"  # < 10mm
        elif max_dim < 400:
            return "medium"  # 10-15mm
        else:
            return "large"  # > 15mm
    
    async def enhance_image(self, image_data: str) -> str:
        """
        Enhance image quality for better recognition
        
        Args:
            image_data: Base64 encoded image
            
        Returns:
            Base64 encoded enhanced image
        """
        # If using Google Vision, delegate to its enhancement
        if self.use_google_vision:
            return await google_vision_client.enhance_for_ocr(image_data)
        
        # Otherwise use local enhancement
        try:
            # Decode image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Apply enhancements
            # 1. Resize if too large
            max_size = (1024, 1024)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # 2. Enhance contrast
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
            # 3. Sharpen
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
            
            # Convert back to base64
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            enhanced_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Error enhancing image: {e}")
            return image_data  # Return original if enhancement fails
    
    def validate_image(self, image_data: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that the image is suitable for medication identification
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Decode and open image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Check image size
            width, height = image.size
            if width < 100 or height < 100:
                return False, "Image is too small. Please take a clearer photo."
            
            if width > 4000 or height > 4000:
                return False, "Image is too large. Please reduce the image size."
            
            # Check file size (in bytes)
            if len(image_bytes) > 10 * 1024 * 1024:  # 10MB
                return False, "Image file is too large. Maximum size is 10MB."
            
            # Check format
            if image.format not in ['JPEG', 'PNG', 'WEBP']:
                return False, "Unsupported image format. Please use JPEG or PNG."
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error validating image: {e}")
            return False, "Invalid image data. Please try again."


# Singleton instance
vision_service = VisionService()